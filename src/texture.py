"""
texture.py - the Wrapshap paint-splatter texture, built as real vector contours.

Marks are grown from a seeded RNG, so a given seed always lays down the same
scatter and a rebuild is repeatable.
"""
from __future__ import annotations

import math

from reportlab.lib.units import mm


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
