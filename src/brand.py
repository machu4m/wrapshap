"""
brand.py - the Wrapshap palette, type and drawing helpers shared by every
product in this repo.

Colours are process CMYK throughout, chosen so that no area exceeds 200% total
ink - which is what uncoated stock and dye-sub substrates will take without
set-off. Nothing here is RGB and nothing is a gradient: the brand prints matte
and flat.
"""
from __future__ import annotations

import os

from reportlab.lib.colors import CMYKColor, CMYKColorSep
from reportlab.lib.units import mm

import typeset as T

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
LOGO_MONO = os.path.join(HERE, "logo", "wrapshap-wordmark-mono.png")

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




_LOGO = None


def logo():
    """The supplied wordmark, traced once per process and shared.

    Tracing costs about a second, so it is deferred until something actually
    asks for the mark.
    """
    global _LOGO
    if _LOGO is None:
        from logomark import LogoMark
        _LOGO = LogoMark(LOGO_MONO)
    return _LOGO


def wrap(face, s, size, max_mm, tracking_em=0.0, **kw):
    """Greedy word wrap, measured on the real shaped widths."""
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if cur and T.layout(face, trial, size,
                            tracking=tracking_em * size, **kw).width > max_mm * mm:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


REG = CMYKColor(1, 1, 1, 1)        # registration black - prints on every plate
