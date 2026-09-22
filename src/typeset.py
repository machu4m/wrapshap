"""
typeset.py - HarfBuzz-shaped text drawn as true vector outlines on a ReportLab canvas.

Every piece of type on the envelope is emitted as outlines rather than as embedded
font text. A production file with no font dependency opens, previews and separates
identically on any RIP, which is what a printer expects to receive.

Latin is shaped with Montserrat, Arabic with Cairo; HarfBuzz handles the Arabic
joining forms and the right-to-left ordering.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import uharfbuzz as hb
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont


# --------------------------------------------------------------------------- #
# Font handling
# --------------------------------------------------------------------------- #

class Face:
    """A font file wrapped for both shaping (HarfBuzz) and outlines (fontTools)."""

    def __init__(self, path: str):
        self.path = path
        blob = hb.Blob.from_file_path(path)
        self.hb_face = hb.Face(blob)
        self.hb_font = hb.Font(self.hb_face)
        self.upem = float(self.hb_face.upem)
        self.tt = TTFont(path, lazy=True)
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def shape(self, text, direction="ltr", script="latn", language="en", features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction = direction
        buf.script = script
        buf.language = language
        hb.shape(self.hb_font, buf, features or {})
        return [
            (self.order[i.codepoint], p.x_offset, p.y_offset, p.x_advance)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)
        ]


@dataclass
class Glyph:
    """One positioned glyph, in output units (points), relative to the run origin."""
    name: str
    x: float
    y: float


@dataclass
class Run:
    """A shaped, measured line of type ready to be drawn."""
    face: Face
    glyphs: list
    width: float
    size: float

    @property
    def scale(self) -> float:
        return self.size / self.face.upem


def layout(face: Face, text: str, size: float, tracking: float = 0.0,
           direction: str = "ltr", script: str = "latn", language: str = "en",
           features=None) -> Run:
    """Shape `text` and lay it out on a baseline starting at x=0.

    `tracking` is extra letterspacing in output units (points), applied per glyph.
    """
    shaped = face.shape(text, direction, script, language, features)
    scale = size / face.upem
    glyphs, pen_x = [], 0.0
    for name, dx, dy, adv in shaped:
        glyphs.append(Glyph(name, pen_x + dx * scale, dy * scale))
        pen_x += adv * scale + tracking
    width = pen_x - tracking if shaped else 0.0
    return Run(face, glyphs, width, size)


def measure(face: Face, text: str, size: float, **kw) -> float:
    return layout(face, text, size, **kw).width


# --------------------------------------------------------------------------- #
# Outline extraction
# --------------------------------------------------------------------------- #

class _OutlinePen(BasePen):
    """Streams glyph contours into a ReportLab path, applying an affine transform.

    BasePen already decomposes TrueType quadratics into cubics and resolves
    composite glyphs through the glyph set, so only the four primitives remain.
    """

    def __init__(self, glyphset, path, transform: Transform):
        super().__init__(glyphset)
        self.path = path
        self.t = transform

    def _moveTo(self, pt):
        self.path.moveTo(*self.t.transformPoint(pt))

    def _lineTo(self, pt):
        self.path.lineTo(*self.t.transformPoint(pt))

    def _curveToOne(self, p1, p2, p3):
        a = self.t.transformPoint(p1)
        b = self.t.transformPoint(p2)
        c = self.t.transformPoint(p3)
        self.path.curveTo(a[0], a[1], b[0], b[1], c[0], c[1])

    def _closePath(self):
        self.path.close()


def run_path(canvas, run: Run, x: float, y: float, align: str = "left",
             placer: Callable[[Glyph, Run], Transform] | None = None):
    """Build a single ReportLab path holding every glyph of `run` as outlines.

    Keeping a line in one path means a stroked outline pass can be laid down
    under one fill pass, so adjacent letters share a clean common edge.

    `placer` overrides positioning (used for the arched logo); it receives each
    glyph and returns the em-space -> page-space transform for it.
    """
    ox = x - {"left": 0.0, "center": run.width / 2.0, "right": run.width}[align]
    path = canvas.beginPath()
    for g in run.glyphs:
        if placer is not None:
            t = placer(g, run)
        else:
            t = Transform().translate(ox + g.x, y + g.y).scale(run.scale)
        pen = _OutlinePen(run.face.glyphset, path, t)
        run.face.glyphset[g.name].draw(pen)
    return path


def arch_placer(cx: float, cy: float, radius: float, run: Run) -> Callable:
    """Place glyphs along a convex-up circular arc centred on (cx, cy).

    Larger `radius` flattens the arch. Each glyph is rotated to sit normal to
    the curve, the way a set arched wordmark behaves.
    """
    import math

    def place(g: Glyph, r: Run) -> Transform:
        # Advance-width centre of this glyph, measured from the middle of the line.
        adv_mid = g.x + _glyph_halfwidth(r, g)
        theta = (adv_mid - r.width / 2.0) / radius
        px = cx + radius * math.sin(theta)
        py = cy - radius * (1.0 - math.cos(theta))
        return (Transform()
                .translate(px, py + g.y)
                .rotate(-theta)
                .translate(-_glyph_halfwidth(r, g), 0)
                .scale(r.scale))

    return place


def _glyph_halfwidth(run: Run, g: Glyph) -> float:
    """Half the on-line width this glyph occupies, used to pivot it on the arc."""
    idx = run.glyphs.index(g)
    nxt = run.glyphs[idx + 1].x if idx + 1 < len(run.glyphs) else run.width
    return (nxt - g.x) / 2.0
