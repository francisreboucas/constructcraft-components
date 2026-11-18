"""Hollow shells with straight sides and rounded corners (bathtub, laundry sink).

Not a component module (make.py skips files starting with "_"). A shell is a
stack of `Blend`s between "annulus" outlines: a rounded-rectangle hole inside a
rounded-rectangle edge, joined by a zero-width slit at the back (+y), so each
level is one closed outline. Every level may have its own hole, so a basin can
slope more at one end than at the other (a bathtub's backrest), and nothing is
cut by a void.
"""

from __future__ import annotations

import math

from louca import blend, add, mul
from kit import e, p


def mid(a, b) -> str:
    return f"({p(a)} + {p(b)}) / 2"


def corners(rect, clockwise=False, n=8) -> list[tuple]:
    """The rounded rectangle `rect` as a polygon (n segments per corner), from the middle of its back side.

    Counter-clockwise (towards -x first) or clockwise (towards +x first); the
    start point is left out.
    """
    x0, y0, x1, y1, r = rect
    # Corner centers and the angle each quarter starts at, counter-clockwise from the back.
    quarters = [((f"{p(x0)} + {p(r)}", f"{p(y1)} - {p(r)}"), 90), ((f"{p(x0)} + {p(r)}", f"{p(y0)} + {p(r)}"), 180),
                ((f"{p(x1)} - {p(r)}", f"{p(y0)} + {p(r)}"), 270), ((f"{p(x1)} - {p(r)}", f"{p(y1)} - {p(r)}"), 0)]
    pts = []
    for (cx, cy), a0 in quarters:
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n)
            pts.append((add(cx, mul(r, math.cos(t))) if abs(math.cos(t)) > 1e-9 else e(cx),
                        add(cy, mul(r, math.sin(t))) if abs(math.sin(t)) > 1e-9 else e(cy)))
    if clockwise:
        pts.reverse()
    return pts


def annulus(inner, outer, xs=None) -> list[tuple]:
    """One closed outline: the rounded rectangle `outer` with the hole `inner`.

    `inner` and `outer` are (x0, y0, x1, y1, r) with x0 < x1, y0 < y1. The
    outline runs down a slit at x = `xs` (default: the middle of the hole) on
    the back, clockwise around the hole, back up the slit and counter-clockwise
    around the edge. Stacked levels must share `xs`, or the slit twists.
    """
    xm = xs if xs is not None else mid(inner[0], inner[2])
    y1, Y1 = inner[3], outer[3]
    return [(xm, Y1), (xm, y1)] + corners(inner, clockwise=True) + [(xm, y1), (xm, Y1)] + corners(outer)


def grow(rect, d):
    """The rounded rectangle `rect` offset outwards by the number d."""
    x0, y0, x1, y1, r = rect
    return (add(x0, -d), add(y0, -d), add(x1, d), add(y1, d), add(r, d))


def shell(c, name, levels, thickness, material, detail="mf", in_plan=False, xs=None):
    """A hollow wall through `levels` [(z, inner rect), …], `thickness` thick outwards.

    Each pair of levels is one Blend named "<name> <i>".
    """
    for i in range(len(levels) - 1):
        (z0, a), (z1, b) = levels[i], levels[i + 1]
        blend(c, f"{name} {i + 1}", "Plan", annulus(a, grow(a, thickness), xs), annulus(b, grow(b, thickness), xs),
              z0, f"{p(z1)} - {p(z0)}", material, detail, in_plan and i == len(levels) - 2)
