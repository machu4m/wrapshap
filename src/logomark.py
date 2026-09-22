"""
logomark.py - the supplied Wrapshap wordmark, traced to vector.

The brand mark arrives as a bitmap. Placing a raster in a print file caps the
artwork at whatever resolution the file happens to be, so it is traced once to
bezier contours and drawn as vector from then on - identical shape, no
resolution ceiling, and recolourable.

The wordmark is a three-layer sticker: an outer keyline, a light gap, and the
letter cores. Those layers are recovered from the nesting depth of the traced
contours, which is what makes `draw_full` able to recolour each one.
"""
from __future__ import annotations

import math

import numpy as np
import potrace
from PIL import Image
from reportlab.pdfgen.canvas import FILL_EVEN_ODD


def _flatten(curve, steps=10):
    """A traced contour as a closed polyline, for containment testing."""
    pts = [(curve.start_point.x, curve.start_point.y)]
    cur = pts[0]
    for seg in curve:
        if seg.is_corner:
            pts.append((seg.c.x, seg.c.y))
            pts.append((seg.end_point.x, seg.end_point.y))
        else:
            p0 = cur
            p1 = (seg.c1.x, seg.c1.y)
            p2 = (seg.c2.x, seg.c2.y)
            p3 = (seg.end_point.x, seg.end_point.y)
            for i in range(1, steps + 1):
                t = i / steps
                u = 1 - t
                pts.append((
                    u**3 * p0[0] + 3 * u*u*t * p1[0] + 3 * u*t*t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u*u*t * p1[1] + 3 * u*t*t * p2[1] + t**3 * p3[1],
                ))
        cur = (seg.end_point.x, seg.end_point.y)
    return pts


def _interior_point(poly):
    """A point strictly inside `poly`.

    Taken at the lowest vertex, which is always a convex corner, stepped a
    little way along the bisector of its two edges. Centroids are not safe
    here - the wordmark's contours are long and concave.
    """
    i = min(range(len(poly)), key=lambda k: (poly[k][1], poly[k][0]))
    v = poly[i]
    a, b = poly[(i - 1) % len(poly)], poly[(i + 1) % len(poly)]
    out = []
    for n in (a, b):
        dx, dy = n[0] - v[0], n[1] - v[1]
        d = math.hypot(dx, dy) or 1.0
        out.append((dx / d, dy / d))
    bx = out[0][0] + out[1][0]
    by = out[0][1] + out[1][1]
    d = math.hypot(bx, by)
    if d < 1e-9:                       # degenerate spike - nudge straight up
        return (v[0], v[1] + 1e-3)
    return (v[0] + bx / d * 1e-3, v[1] + by / d * 1e-3)


def _contains(poly, pt):
    """Even-odd ray cast."""
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xx = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if xx > x:
                inside = not inside
    return inside


class LogoMark:
    """A traced wordmark, normalised so that x runs 0..1 across the ink."""

    def __init__(self, png_path: str, threshold: int = 128):
        img = Image.open(png_path)
        if img.mode in ("RGBA", "LA"):
            flat = Image.new("RGB", img.size, (255, 255, 255))
            flat.paste(img, mask=img.getchannel("A"))
            img = flat
        ink = np.array(img.convert("L")) < threshold

        # potrace.Bitmap inverts whatever it is handed, so the mask goes in
        # negated to come back out the right way round.
        path = potrace.Bitmap(~ink).trace(turdsize=2, alphamax=1.0,
                                          opttolerance=0.2)
        self.curves = list(path)
        polys = [_flatten(c) for c in self.curves]

        # Nesting depth: even depth is ink, odd depth is a hole. Depth 0 is the
        # outer keyline shell, 1 the gap around each letter, 2 the letter core,
        # 3 the counters and the star cut-outs.
        probes = [_interior_point(p) for p in polys]
        self.depth = [
            sum(1 for j, q in enumerate(polys) if j != i and _contains(q, probes[i]))
            for i in range(len(polys))
        ]

        xs = [p[0] for poly in polys for p in poly]
        ys = [p[1] for poly in polys for p in poly]
        self.x0, self.x1 = min(xs), max(xs)
        self.y0, self.y1 = min(ys), max(ys)
        self.aspect = (self.y1 - self.y0) / (self.x1 - self.x0)

    # ------------------------------------------------------------------ #
    def _emit(self, c, levels, x, y, w):
        """Build a ReportLab path from the contours at the given depths.

        The bitmap runs y-down and PDF runs y-up, so y is flipped here.
        """
        s = w / (self.x1 - self.x0)
        ox, oy = self.x0, self.y1

        def T(px, py):
            return (x + (px - ox) * s, y + (oy - py) * s)

        p = c.beginPath()
        for curve, d in zip(self.curves, self.depth):
            if d not in levels:
                continue
            p.moveTo(*T(curve.start_point.x, curve.start_point.y))
            for seg in curve:
                if seg.is_corner:
                    p.lineTo(*T(seg.c.x, seg.c.y))
                    p.lineTo(*T(seg.end_point.x, seg.end_point.y))
                else:
                    a = T(seg.c1.x, seg.c1.y)
                    b = T(seg.c2.x, seg.c2.y)
                    e = T(seg.end_point.x, seg.end_point.y)
                    p.curveTo(a[0], a[1], b[0], b[1], e[0], e[1])
            p.close()
        return p

    def height_for(self, w: float) -> float:
        return w * self.aspect

    def draw_flat(self, c, x, y, w, colour):
        """One-colour wordmark. Gaps and counters drop out to the ground."""
        c.setFillColor(colour)
        c.drawPath(self._emit(c, {0, 1, 2, 3, 4, 5}, x, y, w),
                   stroke=0, fill=1, fillMode=FILL_EVEN_ODD)

    def draw_full(self, c, x, y, w, keyline, gap, fill):
        """The three-layer sticker treatment, each layer recoloured."""
        c.setFillColor(gap)                            # solid silhouette
        c.drawPath(self._emit(c, {0}, x, y, w), stroke=0, fill=1,
                   fillMode=FILL_EVEN_ODD)
        c.setFillColor(keyline)                        # outer ring
        c.drawPath(self._emit(c, {0, 1}, x, y, w), stroke=0, fill=1,
                   fillMode=FILL_EVEN_ODD)
        c.setFillColor(fill)                           # letter cores
        c.drawPath(self._emit(c, {2, 3}, x, y, w), stroke=0, fill=1,
                   fillMode=FILL_EVEN_ODD)
