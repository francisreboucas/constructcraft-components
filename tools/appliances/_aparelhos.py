"""Shared helpers of cooktop_4_bocas, purificador_agua, depurador_ar, tanquinho and aquecedor_gas.

Shapes the kit has no helper for (Blend, Sweep) and a few small compound pieces.
"""

from __future__ import annotations

import math

import kit
from kit import FINE, FULL, disc, e, p


def num(v: float) -> str:
    """A number safe to paste inside an expression."""
    text = f"{v:.5f}".rstrip("0").rstrip(".")
    if text in ("", "-0"):
        text = "0"
    return f"({text})" if text.startswith("-") else text


def blend(c, name, bottom, top, z, height, material, detail=FULL, in_plan=False, void=False):
    """A solid joining the plan outline `bottom` at z to `top` at z + height."""
    shape = {"Blend": {"plane": "Plan", "bottom": kit._points(bottom), "top": kit._points(top), "offset": e(z), "depth": e(height)}}
    c._add(name, shape, material, detail, in_plan, void)


def sweep(c, name, plane, path, offset, section, material, detail=FULL, in_plan=False, void=False):
    """A closed `section` (u to the left of the path, v along the plane's normal) carried along `path`."""
    shape = {"Sweep": {"plane": plane, "path": kit._points(path), "offset": e(offset), "profile": kit._points(section)}}
    c._add(name, shape, material, detail, in_plan, void)


def tube(c, name, plane, path, offset, radius, material, detail=FULL, in_plan=False):
    """A round tube of `radius` along `path` (points of the plane, with optional bend radii)."""
    sweep(c, name, plane, path, offset, disc(0, 0, radius), material, detail, in_plan)


def sphere(c, name, x, y, z, r, material, detail=FINE):
    """A ball centered at (x, y, z)."""
    c.rev(name, "Front", [(x, f"{p(z)} - {p(r)}", r), (x, f"{p(z)} + {p(r)}")], y, x, material, detail=detail)


def ring_rrect_hole(u0, v0, u1, v1, r, cu, cv, rh):
    """Plan outline of a rounded rectangle with a round hole (center cu, cv; radius rh), reached by a slit at the front.

    The slit has no width: the outline goes in along it, round the hole the
    other way and back out.
    """
    r_ = p(r)
    return [
        (cu, v0),
        (f"{p(u1)} - {r_}", v0, r),
        (u1, f"{p(v0)} + {r_}"),
        (u1, f"{p(v1)} - {r_}", r),
        (f"{p(u1)} - {r_}", v1),
        (f"{p(u0)} + {r_}", v1, r),
        (u0, f"{p(v1)} - {r_}"),
        (u0, f"{p(v0)} + {r_}", r),
        (f"{p(u0)} + {r_}", v0),
        (cu, v0),
        (cu, f"{p(cv)} - {p(rh)}", f"-{p(rh)}"),
        (cu, f"{p(cv)} + {p(rh)}", f"-{p(rh)}"),
        (cu, f"{p(cv)} - {p(rh)}"),
    ]


def side_swing(hinge, angle, a, b) -> tuple[str, str]:
    """Plan (x, y) of a door on a right side face, hinged at its back edge.

    Closed, the door lies in the plane x = hinge x: `a` runs from the hinge
    towards the front (-y) and `b` out of the side (+x). `angle` swings its
    front edge out to the right.
    """
    hx, hy = p(hinge[0]), p(hinge[1])
    a, b, g = p(a), p(b), p(angle)
    return (f"{hx} + {b}*cos({g}) + {a}*sin({g})", f"{hy} + {b}*sin({g}) - {a}*cos({g})")


def side_door_box(c, name, hinge, angle, a0, a1, b0, b1, z, height, material, detail=FULL, in_plan=False):
    """A box of a right side door (see `side_swing`), from z to z + height."""
    pts = [side_swing(hinge, angle, a, b) for a, b in ((a0, b0), (a0, b1), (a1, b1), (a1, b0))]
    c.profile(name, "Plan", pts, z, height, material, detail=detail, in_plan=in_plan)


def ring_points(n, radius, phase=0.0):
    """Unit offsets (dx, dy) of n points on a circle of `radius` (a number)."""
    out = []
    for i in range(n):
        a = math.radians(phase + 360 * i / n)
        out.append((radius * math.cos(a), radius * math.sin(a)))
    return out
