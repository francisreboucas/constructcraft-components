"""Shared helpers of the furniture modules poltrona, mesa_centro, comoda, beliche and ventilador_teto.

Not a component module: make.py skips the files whose name starts with `_`.
"""

from __future__ import annotations

from kit import *  # noqa: F401,F403
from kit import e, p, lift, FULL
from louca import sweep, blend  # noqa: F401  (the engine's Sweep and Blend pieces)

EPS = 0.005  # scale of a collapsed group: its pieces shrink into a point hidden inside a solid


def turned(c, name, cx, cy, profile, material, detail=FULL, in_plan=False):
    """A turned piece about the vertical axis at (cx, cy): profile = [(radius, z), …] from bottom to top."""
    pts = [(cx, profile[0][1])] + [(f"{p(cx)} + {p(r)}", z) for r, z in profile] + [(cx, profile[-1][1])]
    c.rev(name, "Front", pts, cy, cx, material, detail=detail, in_plan=in_plan)


def reverse(pts):
    """The same closed outline run the other way, each arc kept on its segment."""
    q = list(reversed(pts))
    n = len(q)
    out = []
    for i in range(n):
        nxt = q[(i + 1) % n]
        rad = nxt[2] if len(nxt) > 2 else None
        out.append((q[i][0], q[i][1], rad) if rad not in (None, "", 0) else (q[i][0], q[i][1]))
    return out


def tilted(hinge, angle, pts):
    """Side outline given in (r forward, t up) about `hinge`, tilted back by `angle` (see kit.lift).

    The mapping mirrors the outline, so it comes out reversed to stay counter-clockwise.
    """
    out = []
    for q in pts:
        y, z = lift(hinge, angle, q[0], q[1])
        out.append((y, z, q[2]) if len(q) > 2 and q[2] not in (None, "", 0) else (y, z))
    return reverse(out)


def at(base, d):
    """`base` moved by the number or expression `d`."""
    if isinstance(d, str):
        return f"{p(base)} + {p(d)}"
    if abs(d) < 5e-7:
        return e(base)
    if isinstance(base, (int, float)):
        return e(base + d)
    return f"{p(base)} + {e(d)}" if d > 0 else f"{p(base)} - {e(-d)}"


def polar(angle, r, s=0):
    """(x, y) of the point r along and s across the direction `angle` (degrees, from +x towards +y)."""
    a = p(angle)
    return (f"{p(r)}*cos({a}) - {p(s)}*sin({a})", f"{p(r)}*sin({a}) + {p(s)}*cos({a})")


class Grp:
    """Pieces scaled by `k` about the point `h` (see estante.Grp).

    k = 1 leaves the pieces as they are; k = EPS shrinks them into `h`, a point
    inside a solid: that is how the parts a type does not have disappear (a
    piece cannot have zero size). Without `k` the pieces are written as they are.
    """

    def __init__(self, c, k=None, h=(0, 0, 0)):
        self.c, self.k, self.h = c, k, h

    def _at(self, i, v):
        return e(v) if self.k is None else f"{p(self.h[i])} + {p(self.k)}*({e(v)} - {p(self.h[i])})"

    def x(self, v):
        return self._at(0, v)

    def y(self, v):
        return self._at(1, v)

    def z(self, v):
        return self._at(2, v)

    def l(self, v):
        return e(v) if self.k is None else f"{p(self.k)}*{p(v)}"

    def box(self, name, x, y, z, w, d, h, mat, **kw):
        self.c.box(name, self.x(x), self.y(y), self.z(z), self.l(w), self.l(d), self.l(h), mat, **kw)

    def cyl(self, name, x, y, z, r, h, mat, **kw):
        self.c.cyl(name, self.x(x), self.y(y), self.z(z), self.l(r), self.l(h), mat, **kw)

    def cyl_x(self, name, y, z, x, r, length, mat, **kw):
        self.c.cyl_x(name, self.y(y), self.z(z), self.x(x), self.l(r), self.l(length), mat, **kw)

    def cyl_y(self, name, x, z, y, r, length, mat, **kw):
        self.c.cyl_y(name, self.x(x), self.z(z), self.y(y), self.l(r), self.l(length), mat, **kw)

    def _map(self, plane, pts):
        fu, fv = {"Plan": (self.x, self.y), "Front": (self.x, self.z), "Side": (self.y, self.z)}[plane]
        return [(fu(q[0]), fv(q[1])) + ((self.l(q[2]),) if len(q) > 2 and q[2] not in (None, "", 0) else ()) for q in pts]

    def _off(self, plane):
        return {"Plan": self.z, "Front": self.y, "Side": self.x}[plane]

    def profile(self, name, plane, pts, offset, depth, mat, **kw):
        self.c.profile(name, plane, self._map(plane, pts), self._off(plane)(offset), self.l(depth), mat, **kw)

    def rev(self, name, plane, pts, offset, axis, mat, **kw):
        fu = {"Plan": self.x, "Front": self.x, "Side": self.y}[plane]
        self.c.rev(name, plane, self._map(plane, pts), self._off(plane)(offset), fu(axis), mat, **kw)
