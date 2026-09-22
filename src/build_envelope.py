#!/usr/bin/env python3
"""
build_envelope.py - Wrapshap phone-case mailer: print-ready die layout.

Produces a single-page CMYK document at the flat (unfolded) blank size with
3 mm bleed, a spot-colour dieline/crease/glue set, crop and registration marks
and a colour bar. All type is converted to outlines.

    Finished envelope   123 x 205 mm  (spec 20.5 x 12.3 cm, portrait)
    Construction        side-seam pocket mailer, top seal flap
    Stock               100 gsm wood-free
    Printing            4/0 process (CMYK), one side
    Finishing           die cut + side/bottom pasting

Output: Wrapshap_Envelope_Dieline_PRINT.ai (+ .pdf proof, + .png preview)
"""
from __future__ import annotations

import math
import os
import random
import sys

from reportlab.lib.colors import CMYKColor, CMYKColorSep
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typeset as T

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.abspath(os.path.join(HERE, os.pardir, "print"))

# --------------------------------------------------------------------------- #
# Geometry - all values in millimetres
# --------------------------------------------------------------------------- #
ENV_W, ENV_H = 123.0, 205.0      # finished envelope
SEAL = 45.0                      # top seal flap depth
SIDE = 13.0                      # side glue flaps (carried on the front panel)
BLEED = 3.0
SLUG = 11.0                      # marks / colour-bar margin outside the bleed

BLANK_W = SIDE + ENV_W + SIDE    # 149.0
BLANK_H = ENV_H + ENV_H + SEAL   # 455.0
MARGIN = BLEED + SLUG            # 14.0
PAGE_W = BLANK_W + 2 * MARGIN
PAGE_H = BLANK_H + 2 * MARGIN

# Blank-local y bands, measured from the bottom of the blank.
# The blank folds so that the back panel swings behind the front panel and the
# seal flap then wraps forward over the top of the front - which is why the
# seal flap sits at the bottom of the flat layout and the back panel artwork
# is set 180 degrees round (see draw_back_panel).
SEAL_Y0, SEAL_Y1 = 0.0, SEAL                      # 0   -> 45
BACK_Y0, BACK_Y1 = SEAL, SEAL + ENV_H             # 45  -> 250
FRNT_Y0, FRNT_Y1 = SEAL + ENV_H, BLANK_H          # 250 -> 455
PANEL_X0, PANEL_X1 = SIDE, SIDE + ENV_W           # 13  -> 136

FLAP_R = 16.0        # radius on the free corners of the seal flap
CHAMFER = 7.0        # 45 deg relief on the glue flaps
NOTCH_R = 11.0       # thumb notch on the front panel opening edge

# The closed flap covers the top SEAL mm of the front panel, so live artwork
# has to stay below this line.
FRONT_VISIBLE_TOP = FRNT_Y1 - SEAL                # 410

# --------------------------------------------------------------------------- #
# Palette - process CMYK, black and yellow only. Total area coverage is kept
# at or under 200% so it dries cleanly on uncoated 100 gsm wood-free.
# --------------------------------------------------------------------------- #
BLACK = CMYKColor(0.40, 0.30, 0.30, 1.00)      # rich black, TAC 200%
YELLOW = CMYKColor(0.00, 0.16, 1.00, 0.00)     # brand golden yellow
GOLD = CMYKColor(0.00, 0.32, 1.00, 0.02)       # amber, logo shadow + accents
GOLD_DEEP = CMYKColor(0.00, 0.42, 1.00, 0.14)
SPLAT_MID = CMYKColor(0.00, 0.26, 1.00, 0.55)  # mid splatter on black
SPLAT_DARK = CMYKColor(0.00, 0.22, 1.00, 0.78) # low-contrast splatter, TAC 200%
PAPER = CMYKColor(0, 0, 0, 0)                  # unprinted stock = the white type

# Spot channels for the finishing department. These are separations, not
# process build-ups, so the die house can pull them as their own plates.
DIELINE = CMYKColorSep(0.00, 1.00, 0.00, 0.00, spotName="Dieline")
CREASE = CMYKColorSep(1.00, 0.00, 0.00, 0.00, spotName="Crease")
GLUE = CMYKColorSep(0.55, 0.00, 1.00, 0.00, spotName="Glue")

# --------------------------------------------------------------------------- #
# Type
# --------------------------------------------------------------------------- #
F_BLACK = T.Face(os.path.join(FONTS, "Montserrat-Black.ttf"))
F_XBOLD = T.Face(os.path.join(FONTS, "Montserrat-ExtraBold.ttf"))
F_BOLD = T.Face(os.path.join(FONTS, "Montserrat-Bold.ttf"))
F_SEMI = T.Face(os.path.join(FONTS, "Montserrat-SemiBold.ttf"))
F_MED = T.Face(os.path.join(FONTS, "Montserrat-Medium.ttf"))
AR_BOLD = T.Face(os.path.join(FONTS, "Cairo-Bold.ttf"))
AR_SEMI = T.Face(os.path.join(FONTS, "Cairo-SemiBold.ttf"))

AR = dict(direction="rtl", script="arab", language="ar")


def fit(face, text, target_mm, tracking_em=0.0, **kw):
    """Point size at which `text` sets to exactly `target_mm` wide.

    Tracking is expressed as a fraction of the em so the solve stays linear.
    """
    probe = T.layout(face, text, 100.0, tracking=0.0, **kw)
    gaps = max(len(probe.glyphs) - 1, 0)
    per_pt = probe.width / 100.0 + tracking_em * gaps
    return (target_mm * mm) / per_pt


def text(c, face, s, size, x, y, colour, align="left", tracking_em=0.0, **kw):
    """Draw a line of outlined type. Coordinates in points, size in points."""
    run = T.layout(face, s, size, tracking=tracking_em * size, **kw)
    path = T.run_path(c, run, x, y, align=align)
    c.setFillColor(colour)
    c.drawPath(path, stroke=0, fill=1)
    return run.width


# --------------------------------------------------------------------------- #
# Paint splatter - the brand texture, built as real vector contours
# --------------------------------------------------------------------------- #
def _closed_spline(c, pts):
    """A closed Catmull-Rom spline through `pts`, emitted as cubic beziers."""
    p = c.beginPath()
    n = len(pts)
    p.moveTo(*pts[0])
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        b1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        b2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        p.curveTo(b1[0], b1[1], b2[0], b2[1], p2[0], p2[1])
    p.close()
    return p


def blob(c, cx, cy, r, rng, lobes=11, rough=0.42, stretch=1.0, angle=0.0):
    """One organic paint mark: a circle pushed around by random radii."""
    pts = []
    for i in range(lobes):
        a = 2 * math.pi * i / lobes
        rr = r * (1.0 - rough + rng.random() * rough * 2.0)
        px, py = math.cos(a) * rr * stretch, math.sin(a) * rr
        ca, sa = math.cos(angle), math.sin(angle)
        pts.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
    return _closed_spline(c, pts)


def paint_marks(c, x0, y0, w, h, rng, count, r_lo, r_hi, colours,
                avoid=None, streaks=True, droplets=True):
    """Thrown paint: a main mark, a few flung streaks, a ring of droplets.

    `avoid` is a list of rects in points that the mark centres stay out of,
    so the texture never builds up behind the type.
    """
    keep_clear = avoid or []
    for _ in range(count):
        cx = cy = 0.0
        for _try in range(40):
            cx = x0 + rng.random() * w
            cy = y0 + rng.random() * h
            if not any(r[0] < cx < r[2] and r[1] < cy < r[3] for r in keep_clear):
                break
        r = (r_lo + rng.random() * (r_hi - r_lo)) * mm
        c.setFillColor(rng.choice(colours))
        c.drawPath(blob(c, cx, cy, r, rng, lobes=15, rough=0.38,
                        stretch=1.0 + rng.random() * 0.8,
                        angle=rng.random() * math.pi), stroke=0, fill=1)
        if streaks:
            for _ in range(rng.randint(1, 3)):
                a_ = rng.random() * 2 * math.pi
                d = r * (1.0 + rng.random() * 1.8)
                c.drawPath(blob(c, cx + math.cos(a_) * d, cy + math.sin(a_) * d,
                                r * 0.22, rng, lobes=9, rough=0.45,
                                stretch=3.0 + rng.random() * 3.0, angle=a_),
                           stroke=0, fill=1)
        if droplets:
            for _ in range(rng.randint(5, 14)):
                a_ = rng.random() * 2 * math.pi
                d = r * (1.2 + rng.random() * 3.0)
                dr = r * (0.05 + rng.random() * 0.16)
                c.drawPath(blob(c, cx + math.cos(a_) * d, cy + math.sin(a_) * d,
                                dr, rng, lobes=7, rough=0.30), stroke=0, fill=1)


def fine_spray(c, x0, y0, w, h, rng, count, colours, lo=0.25, hi=1.0):
    """Loose overspray that ties the larger marks together."""
    for _ in range(count):
        cx = x0 + rng.random() * w
        cy = y0 + rng.random() * h
        r = (lo + rng.random() * (hi - lo)) * mm
        c.setFillColor(rng.choice(colours))
        c.drawPath(blob(c, cx, cy, r, rng, lobes=7, rough=0.34), stroke=0, fill=1)


# --------------------------------------------------------------------------- #
# Brand marks
# --------------------------------------------------------------------------- #
def draw_logo(c, cx_mm, baseline_mm, width_mm, shadow=True):
    """The Wrapshap wordmark: arched, yellow, with a black keyline and a drop.

    Built from outlines rather than placed art so the file stays self-contained.
    Swap this function for a placed vector if the official logo file is to hand.
    """
    word = "Wrapshap"
    tracking_em = -0.012
    size = fit(F_BLACK, word, width_mm, tracking_em)
    run = T.layout(F_BLACK, word, size, tracking=tracking_em * size)
    radius = width_mm * 2.15 * mm            # gentle convex-up arch
    placer = T.arch_placer(cx_mm * mm, baseline_mm * mm, radius, run)
    path = T.run_path(c, run, cx_mm * mm, baseline_mm * mm, align="center",
                      placer=placer)

    keyline = width_mm * 0.024 * mm          # scales with the mark
    if shadow:
        c.saveState()
        c.translate(keyline * 0.55, -keyline * 0.55)
        c.setStrokeColor(GOLD_DEEP)
        c.setFillColor(GOLD_DEEP)
        c.setLineWidth(keyline)
        c.setLineJoin(1)
        c.drawPath(path, stroke=1, fill=1)
        c.restoreState()

    c.saveState()
    c.setLineJoin(1)
    c.setStrokeColor(BLACK)
    c.setFillColor(BLACK)
    c.setLineWidth(keyline)
    c.drawPath(path, stroke=1, fill=1)

    c.setStrokeColor(YELLOW)
    c.setFillColor(YELLOW)
    c.setLineWidth(keyline * 0.14)
    c.drawPath(path, stroke=1, fill=1)
    c.restoreState()


def draw_phone(c, cx_mm, cy_mm, h_mm, colour=YELLOW):
    """Outline phone mark, echoing the icon on the reference pack."""
    w = h_mm * 0.52
    x, y = (cx_mm - w / 2) * mm, (cy_mm - h_mm / 2) * mm
    W, H = w * mm, h_mm * mm
    lw = h_mm * 0.030 * mm
    c.saveState()
    c.setStrokeColor(colour)
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.roundRect(x, y, W, H, h_mm * 0.115 * mm, stroke=1, fill=0)
    # earpiece slot
    c.setLineWidth(h_mm * 0.022 * mm)
    c.line(x + W * 0.36, y + H - h_mm * 0.062 * mm,
           x + W * 0.64, y + H - h_mm * 0.062 * mm)
    # home indicator
    c.setFillColor(colour)
    c.circle(x + W / 2, y + h_mm * 0.072 * mm, h_mm * 0.024 * mm, stroke=0, fill=1)
    c.restoreState()


# --------------------------------------------------------------------------- #
# "This device belongs to" - bilingual write-on block
# --------------------------------------------------------------------------- #
def draw_belongs_to(c, x_mm, y_mm, w_mm, h_mm):
    """Yellow write-on panel, English and Arabic.

    This block inverts the palette deliberately: a pen will not show on a
    flood-black ground, so the fields sit on solid yellow with black rules.
    The heading spans the panel and the two fields run the full width under
    it, which leaves a rule long enough to actually write a name on.
    """
    c.setFillColor(YELLOW)
    c.roundRect(x_mm * mm, y_mm * mm, w_mm * mm, h_mm * mm, 3.4 * mm,
                stroke=0, fill=1)

    pad = 5.0
    lx, rx = x_mm + pad, x_mm + w_mm - pad
    live = rx - lx

    # --- heading ----------------------------------------------------------- #
    head = min(fit(F_XBOLD, "THIS DEVICE BELONGS TO", live * 0.60, 0.015), 9.4)
    text(c, F_XBOLD, "THIS DEVICE BELONGS TO", head, lx * mm,
         (y_mm + h_mm - 7.6) * mm, BLACK, tracking_em=0.015)
    text(c, AR_BOLD, "هذا الجهاز ملك لـ", head * 1.05, rx * mm,
         (y_mm + h_mm - 7.6) * mm, BLACK, align="right", **AR)

    c.setStrokeColor(BLACK)
    c.setLineWidth(0.25 * mm)
    c.line(lx * mm, (y_mm + h_mm - 11.2) * mm, rx * mm, (y_mm + h_mm - 11.2) * mm)

    # --- fields ------------------------------------------------------------- #
    lab = head * 0.86
    for i, (en_lab, ar_lab) in enumerate((("Name", "الاسم"), ("Number", "الرقم"))):
        fy = y_mm + h_mm - (18.2 + i * 8.0)
        en_w = text(c, F_BOLD, en_lab, lab, lx * mm, fy * mm, BLACK)
        gap = 1.6 * mm
        ar_w = text(c, AR_SEMI, ar_lab, lab, lx * mm + en_w + gap, fy * mm,
                    BLACK, **AR)
        c.saveState()
        c.setStrokeColor(BLACK)
        c.setLineWidth(0.22 * mm)
        c.setLineCap(1)
        c.setDash(0.22 * mm, 1.6 * mm)
        c.line(lx * mm + en_w + ar_w + gap * 2.4, (fy - 0.9) * mm,
               rx * mm, (fy - 0.9) * mm)
        c.restoreState()


# --------------------------------------------------------------------------- #
# Panels
# --------------------------------------------------------------------------- #
TAG_1 = "STAY WRAPPED."
TAG_2 = "STAY PROTECTED."
TAG_SUB = "Invisible protection. Made for your device."

CX = PANEL_X0 + ENV_W / 2.0          # 74.5, the centre line of every panel
CONTENT_W = 103.0                    # live area width, 10 mm clear of trim


def draw_ground(c, rng):
    """Flood the whole bleed area and lay the splatter texture over it.

    Flooding the full bleed box rather than an outset of the die means every
    cut edge stays covered whatever tolerance the die house runs to.
    """
    x0, y0 = -BLEED * mm, -BLEED * mm
    w = (BLANK_W + 2 * BLEED) * mm
    h = (BLANK_H + 2 * BLEED) * mm
    c.setFillColor(BLACK)
    c.rect(x0, y0, w, h, stroke=0, fill=1)

    # Keep the largest marks clear of the front-panel headline stack.
    clear = [
        (6 * mm, 336 * mm, 143 * mm, 404 * mm),     # front headline + wordmark
        (38 * mm, 286 * mm, 111 * mm, 330 * mm),    # front device mark
        (18 * mm, 100 * mm, 131 * mm, 165 * mm),    # back wordmark + strapline
    ]
    paint_marks(c, x0, y0, w, h, rng, 26, 3.4, 7.0,
                [SPLAT_DARK, SPLAT_DARK, SPLAT_MID], avoid=clear)
    paint_marks(c, x0, y0, w, h, rng, 34, 1.2, 3.0,
                [SPLAT_DARK, SPLAT_MID], streaks=False)
    fine_spray(c, x0, y0, w, h, rng, 240, [SPLAT_DARK, SPLAT_DARK, SPLAT_MID])
    fine_spray(c, x0, y0, w, h, rng, 18, [GOLD], lo=0.22, hi=0.5)


def draw_front_panel(c):
    """The face of the envelope. Live artwork stops below the closed flap."""
    # Wordmark
    draw_logo(c, CX, 382.0, 90.0)

    # Headline - both lines set from the longer one so the stack is even.
    size = fit(F_BLACK, TAG_2, CONTENT_W, -0.015)
    for line, base in ((TAG_1, 358.0), (TAG_2, 346.0)):
        text(c, F_BLACK, line, size, CX * mm, base * mm, PAPER,
             align="center", tracking_em=-0.015)

    # Supporting line
    text(c, F_MED, TAG_SUB, fit(F_MED, TAG_SUB, 88.0, 0.012),
         CX * mm, 334.0 * mm, PAPER, align="center", tracking_em=0.012)

    draw_phone(c, CX, 309.0, 28.0)
    draw_belongs_to(c, CX - CONTENT_W / 2, 256.0, CONTENT_W, 31.0)


def draw_back_panel(c):
    """The reverse.

    The back swings behind the front on the bottom fold, so anything set
    upright in the flat blank would read upside down on the finished job.
    The frame below is rotated to compensate; inside it, y runs up the
    finished envelope as you would expect.
    """
    c.saveState()
    c.translate(CX * mm, ((BACK_Y0 + BACK_Y1) / 2.0) * mm)
    c.rotate(180)
    c.translate(-(ENV_W / 2.0) * mm, -(ENV_H / 2.0) * mm)

    cx = ENV_W / 2.0
    draw_logo(c, cx, 124.0, 74.0)

    joined = TAG_1 + "  " + TAG_2
    text(c, F_BOLD, joined, fit(F_BOLD, joined, 92.0, 0.06),
         cx * mm, 107.0 * mm, YELLOW, align="center", tracking_em=0.06)

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5 * mm)
    c.setLineCap(1)
    c.line((cx - 16) * mm, 56.0 * mm, (cx + 16) * mm, 56.0 * mm)

    text(c, F_MED, TAG_SUB, fit(F_MED, TAG_SUB, 80.0, 0.01),
         cx * mm, 46.0 * mm, PAPER, align="center", tracking_em=0.01)
    c.restoreState()


def draw_seal_flap(c):
    """Texture only, plus a hairline that reads as a seal cue near the edge."""
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.4 * mm)
    c.setLineCap(1)
    c.setDash(1.6 * mm, 1.8 * mm)
    c.line((PANEL_X0 + 14) * mm, 9.0 * mm, (PANEL_X1 - 14) * mm, 9.0 * mm)
    c.setDash()


# --------------------------------------------------------------------------- #
# Dieline, creases and glue - drawn in spot separations for the die house
# --------------------------------------------------------------------------- #
K = 0.5523         # circle-to-bezier constant


def die_outline(c):
    """The cutting contour of the flat blank, traced as one closed path."""
    M = mm
    r, ch, nr = FLAP_R, CHAMFER, NOTCH_R
    x0, x1 = PANEL_X0, PANEL_X1
    bx0, bx1 = 0.0, BLANK_W
    top, fold = BLANK_H, FRNT_Y0

    p = c.beginPath()
    p.moveTo((x0 + r) * M, 0)                                   # seal flap edge
    p.lineTo((x1 - r) * M, 0)
    p.curveTo((x1 - r + r * K) * M, 0, x1 * M, (r - r * K) * M, x1 * M, r * M)
    p.lineTo(x1 * M, fold * M)
    p.lineTo(bx1 * M, (fold + ch) * M)                          # glue flap relief
    p.lineTo(bx1 * M, (top - ch) * M)
    p.lineTo((bx1 - ch) * M, top * M)
    p.lineTo((CX + nr) * M, top * M)                            # thumb notch
    p.curveTo((CX + nr) * M, (top - nr * K) * M,
              (CX + nr * K) * M, (top - nr) * M, CX * M, (top - nr) * M)
    p.curveTo((CX - nr * K) * M, (top - nr) * M,
              (CX - nr) * M, (top - nr * K) * M, (CX - nr) * M, top * M)
    p.lineTo(ch * M, top * M)
    p.lineTo(bx0 * M, (top - ch) * M)
    p.lineTo(bx0 * M, (fold + ch) * M)
    p.lineTo(x0 * M, fold * M)
    p.lineTo(x0 * M, r * M)
    p.curveTo(x0 * M, (r - r * K) * M, (x0 + r - r * K) * M, 0, (x0 + r) * M, 0)
    p.close()
    return p


def hatch(c, x0, y0, x1, y1, colour, spacing=2.2, lw=0.15):
    """45 degree fill used to flag the pasting areas."""
    c.saveState()
    clip = c.beginPath()
    clip.rect(x0 * mm, y0 * mm, (x1 - x0) * mm, (y1 - y0) * mm)
    c.clipPath(clip, stroke=0, fill=0)
    c.setStrokeColor(colour)
    c.setLineWidth(lw * mm)
    n = int(((x1 - x0) + (y1 - y0)) / spacing) + 2
    for i in range(-n, n + 1):
        xx = x0 + i * spacing
        c.line(xx * mm, y0 * mm, (xx + (y1 - y0)) * mm, y1 * mm)
    c.restoreState()


def draw_dieline(c):
    c.saveState()
    c.setStrokeOverprint(True)
    c.setFillOverprint(True)

    # Pasting areas first, so the cut and crease rules sit on top of them.
    for gx0, gx1 in ((0.0, PANEL_X0), (PANEL_X1, BLANK_W)):
        hatch(c, gx0, FRNT_Y0 + CHAMFER, gx1, BLANK_H - CHAMFER, GLUE)
    hatch(c, PANEL_X0 + 10, 4.0, PANEL_X1 - 10, 13.0, GLUE)

    for gx in (PANEL_X0 / 2, BLANK_W - PANEL_X0 / 2):
        c.saveState()
        c.translate((gx - 1.2) * mm, 340 * mm)
        c.rotate(90)
        text(c, F_BOLD, "GLUE", 6.5, 0, 0, GLUE, align="center", tracking_em=0.10)
        c.restoreState()
    text(c, F_BOLD, "SEAL GUM  (INSIDE FACE)", 6.5, CX * mm, 15.5 * mm, GLUE,
         align="center", tracking_em=0.10)

    # Creases
    c.setStrokeColor(CREASE)
    c.setLineWidth(0.25 * mm)
    c.setDash(2.4 * mm, 1.6 * mm)
    c.line(PANEL_X0 * mm, SEAL * mm, PANEL_X1 * mm, SEAL * mm)
    c.line(PANEL_X0 * mm, FRNT_Y0 * mm, PANEL_X1 * mm, FRNT_Y0 * mm)
    c.line(PANEL_X0 * mm, FRNT_Y0 * mm, PANEL_X0 * mm, BLANK_H * mm)
    c.line(PANEL_X1 * mm, FRNT_Y0 * mm, PANEL_X1 * mm, BLANK_H * mm)
    c.setDash()

    # Cut
    c.setStrokeColor(DIELINE)
    c.setLineWidth(0.25 * mm)
    c.drawPath(die_outline(c), stroke=1, fill=0)
    c.restoreState()


# --------------------------------------------------------------------------- #
# Press marks, colour bar and slug
# --------------------------------------------------------------------------- #
REG = CMYKColor(1, 1, 1, 1)        # registration black - prints on every plate


def draw_marks(c):
    """Crop marks, registration targets, colour bar and job slug.

    Everything here sits outside the bleed box and is trimmed away.
    """
    c.saveState()
    c.setStrokeOverprint(True)
    c.setStrokeColor(REG)
    c.setLineWidth(0.25 * mm)
    gap, ln = BLEED + 1.0, 6.0
    for bx in (0.0, BLANK_W):
        for by in (0.0, BLANK_H):
            sx = -1 if bx == 0 else 1
            sy = -1 if by == 0 else 1
            c.line((bx + sx * gap) * mm, by * mm, (bx + sx * (gap + ln)) * mm, by * mm)
            c.line(bx * mm, (by + sy * gap) * mm, bx * mm, (by + sy * (gap + ln)) * mm)

    # Registration targets
    # Left, right and foot only - the head margin carries the job slug.
    for tx, ty in ((-SLUG / 2 - BLEED, BLANK_H / 2),
                   (BLANK_W + SLUG / 2 + BLEED, BLANK_H / 2),
                   (BLANK_W / 2, -SLUG / 2 - BLEED)):
        c.setLineWidth(0.2 * mm)
        c.circle(tx * mm, ty * mm, 2.2 * mm, stroke=1, fill=0)
        c.line((tx - 3.4) * mm, ty * mm, (tx + 3.4) * mm, ty * mm)
        c.line(tx * mm, (ty - 3.4) * mm, tx * mm, (ty + 3.4) * mm)
    c.restoreState()

    # Colour bar
    bar = [("C", CMYKColor(1, 0, 0, 0)), ("M", CMYKColor(0, 1, 0, 0)),
           ("Y", CMYKColor(0, 0, 1, 0)), ("K", CMYKColor(0, 0, 0, 1)),
           ("C50", CMYKColor(.5, 0, 0, 0)), ("M50", CMYKColor(0, .5, 0, 0)),
           ("Y50", CMYKColor(0, 0, .5, 0)), ("K50", CMYKColor(0, 0, 0, .5)),
           ("RICH K", BLACK), ("YELLOW", YELLOW), ("GOLD", GOLD),
           ("SPLAT", SPLAT_DARK), ("DIE", DIELINE), ("CREASE", CREASE),
           ("GLUE", GLUE)]
    pw, ph, y = 8.2, 5.0, -SLUG - BLEED + 3.0
    for i, (lab, col) in enumerate(bar):
        x = 1.0 + i * (pw + 1.2)
        c.setFillColor(col)
        c.rect(x * mm, y * mm, pw * mm, ph * mm, stroke=0, fill=1)
        text(c, F_SEMI, lab, 4.2, (x + pw / 2) * mm, (y - 2.6) * mm,
             CMYKColor(0, 0, 0, 1), align="center")

    slug = ("WRAPSHAP  /  PHONE CASE MAILER  /  FINISHED 123 x 205 mm  /  "
            "FLAT 149 x 455 mm  /  100 gsm WOOD-FREE  /  4-0 CMYK  /  "
            "BLEED 3 mm  /  DIE CUT + PASTED  /  TYPE OUTLINED")
    text(c, F_SEMI, slug, min(fit(F_SEMI, slug, BLANK_W, 0.02), 6.0),
         0, (BLANK_H + BLEED + 4.0) * mm, CMYKColor(0, 0, 0, 1), tracking_em=0.02)


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
SEED = 20250922          # fixed so every rebuild produces identical splatter

META = dict(
    title="Wrapshap Phone Case Mailer - 123 x 205 mm - Die Cut + Pasted",
    author="Wrapshap",
    subject="100 gsm wood-free / 4-0 CMYK / bleed 3 mm / dieline on spot separations",
)


def _bleed_clip(c, x, y, w, h):
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0, fill=0)


def build_dieline_sheet(path):
    """The production file: full flat blank, bleed, dieline, marks."""
    c = rl_canvas.Canvas(path, pagesize=(PAGE_W * mm, PAGE_H * mm),
                         pageCompression=1)
    c.setTitle(META["title"])
    c.setAuthor(META["author"])
    c.setSubject(META["subject"])
    c.setCreator("Wrapshap artwork build")

    c.saveState()
    c.translate(MARGIN * mm, MARGIN * mm)          # origin = blank bottom-left

    c.saveState()
    _bleed_clip(c, -BLEED * mm, -BLEED * mm,
                (BLANK_W + 2 * BLEED) * mm, (BLANK_H + 2 * BLEED) * mm)
    draw_ground(c, random.Random(SEED))
    draw_seal_flap(c)
    draw_back_panel(c)
    draw_front_panel(c)
    c.restoreState()

    draw_dieline(c)
    draw_marks(c)
    c.restoreState()

    c.showPage()
    c.save()
    return path


def build_front_panel_sheet(path):
    """Front panel alone at trim + bleed - for mockups and single-panel repro."""
    c = rl_canvas.Canvas(path,
                         pagesize=((ENV_W + 2 * BLEED) * mm, (ENV_H + 2 * BLEED) * mm),
                         pageCompression=1)
    c.setTitle("Wrapshap Mailer - Front Panel 123 x 205 mm")
    c.setAuthor(META["author"])
    c.saveState()
    # Same seed and same offset as the die sheet, so the texture matches exactly.
    c.translate((BLEED - PANEL_X0) * mm, (BLEED - FRNT_Y0) * mm)
    _bleed_clip(c, (PANEL_X0 - BLEED) * mm, (FRNT_Y0 - BLEED) * mm,
                (ENV_W + 2 * BLEED) * mm, (ENV_H + 2 * BLEED) * mm)
    draw_ground(c, random.Random(SEED))
    draw_front_panel(c)
    c.restoreState()
    c.showPage()
    c.save()
    return path


def finalize(src, dst, trim_mm, bleed_mm):
    """Stamp the real TrimBox/BleedBox/ArtBox and the document metadata.

    ReportLab can only anchor those boxes at the page origin, so they are
    written here instead. Nothing else in the file is touched.
    """
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject

    from pypdf.generic import NameObject

    w = PdfWriter(clone_from=PdfReader(src))
    page = w.pages[0]
    # Every glyph is already an outline, so the default font resource is dead
    # weight that would show up in preflight as a non-embedded font.
    res = page.get("/Resources")
    if res is not None and "/Font" in res:
        del res[NameObject("/Font")]
    page.trimbox = RectangleObject([v * mm for v in trim_mm])
    page.artbox = RectangleObject([v * mm for v in trim_mm])
    page.bleedbox = RectangleObject([v * mm for v in bleed_mm])
    w.add_metadata({
        "/Title": META["title"],
        "/Author": META["author"],
        "/Subject": META["subject"],
        "/Keywords": "envelope, dieline, CMYK, spot, Wrapshap",
    })
    with open(dst, "wb") as fh:
        w.write(fh)
    return dst


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp.pdf")

    die_ai = os.path.join(OUT, "Wrapshap_Envelope_Dieline_PRINT.ai")
    build_dieline_sheet(tmp)
    finalize(tmp,
             die_ai,
             trim_mm=(MARGIN, MARGIN, MARGIN + BLANK_W, MARGIN + BLANK_H),
             bleed_mm=(MARGIN - BLEED, MARGIN - BLEED,
                       MARGIN + BLANK_W + BLEED, MARGIN + BLANK_H + BLEED))

    front_ai = os.path.join(OUT, "Wrapshap_Envelope_FrontPanel.ai")
    build_front_panel_sheet(tmp)
    finalize(tmp, front_ai,
             trim_mm=(BLEED, BLEED, BLEED + ENV_W, BLEED + ENV_H),
             bleed_mm=(0, 0, ENV_W + 2 * BLEED, ENV_H + 2 * BLEED))

    os.remove(tmp)
    for src in (die_ai, front_ai):
        with open(src, "rb") as a, open(src[:-3] + ".pdf", "wb") as b:
            b.write(a.read())
        print("%9d bytes  %s" % (os.path.getsize(src), os.path.basename(src)))

    render_proofs(((die_ai, 120), (front_ai, 200)))
    return die_ai, front_ai


def render_proofs(jobs):
    """Flat PNG proofs for sign-off. Screen approximations, not colour proofs."""
    try:
        import pymupdf
    except ImportError:
        print("  (pymupdf not installed - skipping PNG proofs)")
        return
    for path, dpi in jobs:
        out = path[:-3] + "_PROOF.png"
        pymupdf.open(path)[0].get_pixmap(dpi=dpi).save(out)
        print("%9d bytes  %s" % (os.path.getsize(out), os.path.basename(out)))


if __name__ == "__main__":
    main()
