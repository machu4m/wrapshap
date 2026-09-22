#!/usr/bin/env python3
"""
build_mat.py - Wrapshap screen-protector application mat.

A counter mat for fitting a screen protector: the phone goes in the guide, the
dark work zone makes dust visible against the glass, and the steps run around
it. Yellow-dominant and matte - flat process colour throughout, no gradients,
no gloss, and a texture held at low contrast so the surface stays calm to work
on.

    1:1    400 x 400 mm
    16:9   600 x 337.5 mm

Both: 3 mm bleed, 12 mm safe area, 4/0 CMYK, rounded cut line on a spot
separation, all type outlined.
"""
from __future__ import annotations

import os
import random
import sys

from reportlab.lib.colors import CMYKColor
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typeset as T
from brand import (BLACK, DIELINE, F_BLACK, F_BOLD, F_MED, F_SEMI, F_XBOLD,
                   GOLD, GOLD_DEEP, PAPER, REG, YELLOW, fit, logo, text, wrap)
from texture import fine_spray, paint_marks

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   os.pardir, "print"))

# --------------------------------------------------------------------------- #
# Geometry - millimetres
# --------------------------------------------------------------------------- #
BLEED = 3.0
SLUG = 10.0                 # marks margin outside the bleed
SAFE = 12.0
CORNER = 14.0               # cut radius on the finished mat
SEED = 20250922

# --------------------------------------------------------------------------- #
# Matte tonal set. The ground is the brand yellow; the texture sits one and two
# steps deeper in the same hue, so it reads as a surface rather than as pattern.
# --------------------------------------------------------------------------- #
TEX_1 = CMYKColor(0.00, 0.21, 1.00, 0.00)
TEX_2 = CMYKColor(0.00, 0.27, 1.00, 0.00)
ZONE_LINE = CMYKColor(0.00, 0.16, 1.00, 0.00)     # guides inside the work zone
ZONE_DIM = CMYKColor(0.00, 0.20, 1.00, 0.55)      # secondary marks on black

LOGO = logo()

TAG = "STAY WRAPPED.  STAY PROTECTED."
SUB = "Invisible protection. Made for your device."

STEPS = [
    ("CLEAN",  "Wipe the screen with the alcohol pad, then dry it."),
    ("DUST",   "Lift every last speck with the dust sticker."),
    ("ALIGN",  "Line the protector up with the speaker cut-out."),
    ("DROP",   "Release it from the centre and let it settle."),
    ("SMOOTH", "Push any bubbles outward from the middle."),
]


# --------------------------------------------------------------------------- #
# Ground
# --------------------------------------------------------------------------- #
def draw_ground(c, w, h, rng, clear):
    """Flat yellow flood plus a quiet tonal texture."""
    c.setFillColor(YELLOW)
    c.rect(-BLEED * mm, -BLEED * mm, (w + 2 * BLEED) * mm, (h + 2 * BLEED) * mm,
           stroke=0, fill=1)
    x0, y0 = -BLEED * mm, -BLEED * mm
    W, H = (w + 2 * BLEED) * mm, (h + 2 * BLEED) * mm
    paint_marks(c, x0, y0, W, H, rng, 12, 4.0, 9.0, [TEX_1], avoid=clear,
                droplets=False)
    paint_marks(c, x0, y0, W, H, rng, 18, 2.0, 5.0, [TEX_1, TEX_2], avoid=clear)
    fine_spray(c, x0, y0, W, H, rng, 130, [TEX_2, TEX_1], lo=0.4, hi=1.2)


# --------------------------------------------------------------------------- #
# Work zone
# --------------------------------------------------------------------------- #
def draw_phone_guide(c, cx, cy, gw=82.0, gh=168.0):
    """Device outline, corner brackets and the work-from-the-centre arrows."""
    x, y = (cx - gw / 2) * mm, (cy - gh / 2) * mm
    W, H = gw * mm, gh * mm

    c.saveState()
    c.setStrokeColor(ZONE_LINE)
    c.setLineWidth(0.5 * mm)
    c.setDash(2.6 * mm, 2.2 * mm)
    c.roundRect(x, y, W, H, 9 * mm, stroke=1, fill=0)
    c.setDash()

    # Corner brackets, stood off the outline so both stay readable.
    arm, off, lw = 15.0 * mm, 3.4 * mm, 1.3 * mm
    c.setLineWidth(lw)
    c.setLineCap(0)
    for sx, px in ((1, x - off), (-1, x + W + off)):
        for sy, py in ((1, y - off), (-1, y + H + off)):
            c.line(px, py, px + sx * arm, py)
            c.line(px, py, px, py + sy * arm)

    # Centre mark and the four push-out arrows.
    c.setFillColor(ZONE_DIM)
    c.setStrokeColor(ZONE_DIM)
    c.circle(x + W / 2, y + H / 2, 2.0 * mm, stroke=0, fill=1)
    c.setLineWidth(1.3 * mm)
    for dx, dy, reach in ((1, 0, gw * 0.24), (-1, 0, gw * 0.24),
                          (0, 1, gh * 0.15), (0, -1, gh * 0.15)):
        sx, sy = x + W / 2, y + H / 2
        r0, r1 = 5.0 * mm, reach * mm
        ex, ey = sx + dx * r1, sy + dy * r1
        c.line(sx + dx * r0, sy + dy * r0, ex - dx * 3.0 * mm, ey - dy * 3.0 * mm)
        head = c.beginPath()                       # solid arrowhead
        head.moveTo(ex, ey)
        head.lineTo(ex - dx * 4.4 * mm - dy * 2.4 * mm,
                    ey - dy * 4.4 * mm - dx * 2.4 * mm)
        head.lineTo(ex - dx * 4.4 * mm + dy * 2.4 * mm,
                    ey - dy * 4.4 * mm + dx * 2.4 * mm)
        head.close()
        c.drawPath(head, stroke=0, fill=1)
    c.restoreState()


def draw_kit_tray(c, x, y, w, row_h, gap, labels):
    """Dashed drop zones for the kit, stacked in the order the steps use them."""
    for i, lab in enumerate(reversed(list(labels))):
        ry = y + i * (row_h + gap)
        c.saveState()
        c.setStrokeColor(ZONE_DIM)
        c.setLineWidth(0.4 * mm)
        c.setDash(2.2 * mm, 2.0 * mm)
        c.roundRect(x * mm, ry * mm, w * mm, row_h * mm, 4 * mm, stroke=1, fill=0)
        c.setDash()
        c.restoreState()
        text(c, F_BOLD, lab, fit(F_BOLD, lab, min(w - 10, 46), 0.08),
             (x + w / 2) * mm, (ry + row_h / 2 - 1.4) * mm, ZONE_DIM,
             align="center", tracking_em=0.08)


def draw_workzone(c, x, y, w, h, guide_cx=None, kit=None, guide=(82.0, 168.0)):
    """The dark fitting surface: dust shows against black, not against yellow."""
    c.setFillColor(BLACK)
    c.roundRect(x * mm, y * mm, w * mm, h * mm, 9 * mm, stroke=0, fill=1)

    c.saveState()                                   # inner hairline
    c.setStrokeColor(ZONE_DIM)
    c.setLineWidth(0.3 * mm)
    c.roundRect((x + 6) * mm, (y + 6) * mm, (w - 12) * mm, (h - 12) * mm,
                5 * mm, stroke=1, fill=0)
    c.restoreState()

    lab = "PLACE DEVICE FACE UP"
    text(c, F_XBOLD, lab, fit(F_XBOLD, lab, min(w * 0.42, 72), 0.16),
         (x + w / 2 if guide_cx is None else guide_cx) * mm,
         (y + h - 15.5) * mm, PAPER, align="center", tracking_em=0.16)

    text(c, F_SEMI, "DUST-FREE ZONE", fit(F_SEMI, "DUST-FREE ZONE", 34, 0.14),
         (x + 13) * mm, (y + 12) * mm, ZONE_DIM, tracking_em=0.14)

    draw_phone_guide(c, x + w / 2 if guide_cx is None else guide_cx,
                     y + h / 2 - 4, *guide)
    if kit:
        draw_kit_tray(c, **kit)


# --------------------------------------------------------------------------- #
# Steps
# --------------------------------------------------------------------------- #
def step_badge(c, cx, cy, r, n):
    c.setFillColor(BLACK)
    c.circle(cx * mm, cy * mm, r * mm, stroke=0, fill=1)
    text(c, F_BLACK, str(n), r * 1.30 * mm, cx * mm,
         (cy - r * 0.36) * mm, YELLOW, align="center")


def draw_steps_row(c, x, y, total_w, n_cols=5):
    """Steps side by side - used on the square mat."""
    col = total_w / n_cols
    for i, (title, body) in enumerate(STEPS):
        cx = x + col * (i + 0.5)
        step_badge(c, cx, y, 6.8, i + 1)
        text(c, F_XBOLD, title, fit(F_XBOLD, title, min(col - 12, 40), 0.09),
             cx * mm, (y - 16.0) * mm, BLACK, align="center", tracking_em=0.09)
        size = 9.5
        for j, line in enumerate(wrap(F_MED, body, size, col - 13)):
            text(c, F_MED, line, size, cx * mm, (y - 23.5 - j * 4.6) * mm,
                 BLACK, align="center")


def draw_steps_stack(c, x, y, w, pitch):
    """Steps stacked - used on the widescreen mat."""
    for i, (title, body) in enumerate(STEPS):
        ry = y - i * pitch
        step_badge(c, x + 6.4, ry - 2.2, 6.4, i + 1)
        tx = x + 17.5
        text(c, F_XBOLD, title, fit(F_XBOLD, title, 34, 0.09), tx * mm,
             ry * mm, BLACK, tracking_em=0.09)
        size = 10.5
        for j, line in enumerate(wrap(F_MED, body, size, w - 19)):
            text(c, F_MED, line, size, tx * mm, (ry - 7.0 - j * 5.0) * mm, BLACK)


# --------------------------------------------------------------------------- #
# Layouts
# --------------------------------------------------------------------------- #
def layout_square(c, w, h, rng):
    """400 x 400. Wordmark over a centred work zone, steps across the foot."""
    logo_w = 180.0
    logo_y = 316.0
    draw_ground(c, w, h, rng, clear=[
        ((w - logo_w) / 2 * mm, logo_y * mm,
         (w + logo_w) / 2 * mm, (logo_y + LOGO.height_for(logo_w)) * mm),
        (110 * mm, 296 * mm, 290 * mm, 312 * mm),      # strapline
        (0 * mm, 28 * mm, w * mm, 74 * mm),            # step row
    ])

    LOGO.draw_flat(c, (w - logo_w) / 2 * mm, logo_y * mm, logo_w * mm, BLACK)
    text(c, F_BLACK, TAG, fit(F_BLACK, TAG, 152, 0.05), w / 2 * mm, 302 * mm,
         BLACK, align="center", tracking_em=0.05)

    draw_workzone(c, 105, 84, 190, 208, guide=(84.0, 160.0))
    draw_steps_row(c, 0, 62, w)

    text(c, F_MED, SUB, fit(F_MED, SUB, 96, 0.02), w / 2 * mm, 17 * mm,
         BLACK, align="center", tracking_em=0.02)


def layout_wide(c, w, h, rng):
    """600 x 337.5. Brand and steps down the left, work zone on the right."""
    logo_w = 175.0
    logo_y = 256.0
    draw_ground(c, w, h, rng, clear=[
        (30 * mm, logo_y * mm,
         (30 + logo_w) * mm, (logo_y + LOGO.height_for(logo_w)) * mm),
        (28 * mm, 236 * mm, 212 * mm, 252 * mm),       # strapline
        (28 * mm, 54 * mm, 236 * mm, 214 * mm),        # step stack
    ])

    LOGO.draw_flat(c, 30 * mm, logo_y * mm, logo_w * mm, BLACK)
    text(c, F_BLACK, TAG, fit(F_BLACK, TAG, 176, 0.05), 30 * mm, 242 * mm,
         BLACK, tracking_em=0.05)

    draw_steps_stack(c, 30, 208, 200, pitch=31)

    c.setStrokeColor(GOLD_DEEP)
    c.setLineWidth(0.6 * mm)
    c.line(30 * mm, 46 * mm, 230 * mm, 46 * mm)
    text(c, F_MED, SUB, fit(F_MED, SUB, 110, 0.02), 30 * mm, 33 * mm, BLACK,
         tracking_em=0.02)

    draw_workzone(c, 262, 30, 308, 277.5, guide_cx=360, guide=(82.0, 168.0),
                  kit=dict(x=448, y=78, w=104, row_h=44, gap=16,
                           labels=("ALCOHOL WIPE", "DUST STICKER", "PROTECTOR")))
    text(c, F_XBOLD, "FITTING KIT", fit(F_XBOLD, "FITTING KIT", 42, 0.16),
         500 * mm, 256 * mm, PAPER, align="center", tracking_em=0.16)


# --------------------------------------------------------------------------- #
# Marks
# --------------------------------------------------------------------------- #
def draw_marks(c, w, h, spec):
    """Rounded cut line on the Dieline separation, crop marks and a job slug."""
    c.saveState()
    c.setStrokeOverprint(True)
    c.setStrokeColor(DIELINE)
    c.setLineWidth(0.25 * mm)
    c.roundRect(0, 0, w * mm, h * mm, CORNER * mm, stroke=1, fill=0)

    c.setStrokeColor(REG)
    gap, ln = BLEED + 1.0, 6.0
    for bx in (0.0, w):
        for by in (0.0, h):
            sx = -1 if bx == 0 else 1
            sy = -1 if by == 0 else 1
            c.line((bx + sx * gap) * mm, by * mm, (bx + sx * (gap + ln)) * mm, by * mm)
            c.line(bx * mm, (by + sy * gap) * mm, bx * mm, (by + sy * (gap + ln)) * mm)
    c.restoreState()

    text(c, F_SEMI, spec, min(fit(F_SEMI, spec, w * 0.92, 0.02), 6.0),
         0, (-BLEED - 6.4) * mm, CMYKColor(0, 0, 0, 1), tracking_em=0.02)


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build(path, w, h, layout, spec, title):
    off = BLEED + SLUG
    c = rl_canvas.Canvas(path, pagesize=((w + 2 * off) * mm, (h + 2 * off) * mm),
                         pageCompression=1)
    c.setTitle(title)
    c.setAuthor("Wrapshap")
    c.setSubject(spec)
    c.setCreator("Wrapshap artwork build")

    c.saveState()
    c.translate(off * mm, off * mm)

    c.saveState()
    clip = c.beginPath()
    clip.rect(-BLEED * mm, -BLEED * mm, (w + 2 * BLEED) * mm, (h + 2 * BLEED) * mm)
    c.clipPath(clip, stroke=0, fill=0)
    layout(c, w, h, random.Random(SEED))
    c.restoreState()

    draw_marks(c, w, h, spec)
    c.restoreState()
    c.showPage()
    c.save()
    return path


MATS = [
    ("Wrapshap_Mat_1x1_400x400mm", 400.0, 400.0, layout_square,
     "WRAPSHAP  /  SCREEN PROTECTOR APPLICATION MAT  /  1:1  /  400 x 400 mm  /  "
     "4-0 CMYK  /  MATTE  /  BLEED 3 mm  /  SAFE 12 mm  /  R14 CUT  /  TYPE OUTLINED"),
    ("Wrapshap_Mat_16x9_600x337mm", 600.0, 337.5, layout_wide,
     "WRAPSHAP  /  SCREEN PROTECTOR APPLICATION MAT  /  16:9  /  600 x 337.5 mm  /  "
     "4-0 CMYK  /  MATTE  /  BLEED 3 mm  /  SAFE 12 mm  /  R14 CUT  /  TYPE OUTLINED"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    from build_envelope import finalize

    made = []
    for name, w, h, layout, spec in MATS:
        tmp = os.path.join(OUT, "_tmp_mat.pdf")
        ai = os.path.join(OUT, name + "_PRINT.ai")
        build(tmp, w, h, layout, spec, "Wrapshap Application Mat - " + name)
        off = BLEED + SLUG
        finalize(tmp, ai,
                 trim_mm=(off, off, off + w, off + h),
                 bleed_mm=(off - BLEED, off - BLEED, off + w + BLEED, off + h + BLEED))
        os.remove(tmp)
        with open(ai, "rb") as a, open(ai[:-3] + ".pdf", "wb") as b:
            b.write(a.read())
        print("%9d bytes  %s" % (os.path.getsize(ai), os.path.basename(ai)))
        made.append(ai)

    try:
        import pymupdf
        for ai in made:
            out = ai[:-3] + "_PROOF.png"
            pymupdf.open(ai)[0].get_pixmap(dpi=110).save(out)
            print("%9d bytes  %s" % (os.path.getsize(out), os.path.basename(out)))
    except ImportError:
        print("  (pymupdf not installed - skipping PNG proofs)")
    return made


if __name__ == "__main__":
    main()
