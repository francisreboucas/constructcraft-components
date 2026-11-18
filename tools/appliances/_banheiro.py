"""Shared helpers of the bathroom accessory modules (box, gabinete, espelheira, ducha, toalheiro).

Not a component module: make.py skips files starting with `_`.
"""

from __future__ import annotations

import math

from kit import *  # noqa: F401,F403
from kit import e, p, swing, FULL, FINE, COARSE
from louca import sweep, blend, circle, oval, add, mul

EPS = 0.001  # scale of a collapsed group: its pieces shrink into a point hidden inside a solid


class Grp:
    """Pieces scaled by `k` about the point `h`.

    k = 1 leaves the pieces as they are; k = EPS shrinks them into `h`, a
    point inside a solid that stays: that is how the parts a type does not
    have disappear (a piece cannot have zero size). Without `k` the pieces
    are written as they are.
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

    def _maps(self, plane):
        return {"Plan": (self.x, self.y, self.z), "Front": (self.x, self.z, self.y), "Side": (self.y, self.z, self.x)}[plane]

    def _pts(self, plane, pts):
        fu, fv, _ = self._maps(plane)
        return [(fu(q[0]), fv(q[1])) + ((self.l(q[2]),) if len(q) > 2 and q[2] not in (None, "", 0) else ()) for q in pts]

    def box(self, name, x, y, z, w, d, h, mat, **kw):
        self.c.box(name, self.x(x), self.y(y), self.z(z), self.l(w), self.l(d), self.l(h), mat, **kw)

    def cyl(self, name, x, y, z, r, h, mat, **kw):
        self.c.cyl(name, self.x(x), self.y(y), self.z(z), self.l(r), self.l(h), mat, **kw)

    def cyl_x(self, name, y, z, x, r, length, mat, **kw):
        self.c.cyl_x(name, self.y(y), self.z(z), self.x(x), self.l(r), self.l(length), mat, **kw)

    def cyl_y(self, name, x, z, y, r, length, mat, **kw):
        self.c.cyl_y(name, self.x(x), self.z(z), self.y(y), self.l(r), self.l(length), mat, **kw)

    def door_box(self, name, hinge, angle, a0, a1, b0, b1, z, height, mat, side="left", **kw):
        hg = (self.x(hinge[0]), self.y(hinge[1]))
        self.c.door_box(name, hg, angle, self.l(a0), self.l(a1), self.l(b0), self.l(b1), self.z(z), self.l(height), mat, side=side, **kw)

    def door_cyl(self, name, hinge, angle, a, b, z, r, height, mat, side="left", **kw):
        """A vertical cylinder that swings with a door: axis at (a, b) of the door."""
        cx, cy = swing((self.x(hinge[0]), self.y(hinge[1])), angle, self.l(a), self.l(b), side)
        self.c.cyl(name, cx, cy, self.z(z), self.l(r), self.l(height), mat, **kw)

    def profile(self, name, plane, pts, offset, depth, mat, **kw):
        _, _, fo = self._maps(plane)
        self.c.profile(name, plane, self._pts(plane, pts), fo(offset), self.l(depth), mat, **kw)

    def rev(self, name, plane, pts, offset, axis, mat, **kw):
        fu, _, fo = self._maps(plane)
        self.c.rev(name, plane, self._pts(plane, pts), fo(offset), fu(axis), mat, **kw)

    def sweep(self, name, plane, path, offset, section, mat, **kw):
        _, _, fo = self._maps(plane)
        sec = [(self.l(u), self.l(v)) for u, v in section]
        sweep(self.c, name, plane, self._pts(plane, path), fo(offset), sec, mat, **kw)

    def tube(self, name, plane, path, offset, radius, mat, n=12, **kw):
        self.sweep(name, plane, path, offset, circle(radius, n), mat, **kw)

    def blend(self, name, plane, bottom, top, offset, depth, mat, **kw):
        _, _, fo = self._maps(plane)
        blend(self.c, name, plane, self._pts(plane, bottom), self._pts(plane, top), fo(offset), self.l(depth), mat, **kw)


def hinge(g, name, side, hx, hy, xi, zc, A, steel="Aço galvanizado"):
    """A cup hinge (as in armario_aereo): the cup on the door (swings), the arm and its plate on the side panel.

    `hx`, `hy`: the door's hinge axis; `xi`: inner face of the panel that carries
    the hinge; `zc`: height of its center.
    """
    s = 1 if side == "left" else -1
    g.door_box(f"{name} - caneca", (hx, hy), A, 0.005, 0.04, -0.003, 0, f"{zc} - 0.025", 0.05, steel, side=side, detail=FINE)
    x0 = xi if s > 0 else f"{xi} - 0.012"
    g.box(f"{name} - braço", x0, f"{hy} + 0.0035", f"{zc} - 0.01", 0.012, 0.055, 0.02, steel, detail=FINE)
    x0 = xi if s > 0 else f"{xi} - 0.004"
    g.box(f"{name} - calço", x0, f"{hy} + 0.022", f"{zc} - 0.0225", 0.004, 0.05, 0.045, steel, detail=FINE)


def pull(g, name, side, hx, hy, a, zc, length, A, td=0.018, mat="Inox escovado"):
    """A vertical bar pull on a door (as in armario_aereo): a round bar on two posts, centered at `zc`."""
    g.door_cyl(f"{name} - barra", (hx, hy), A, a, td + 0.026, f"{zc} - {p(length)}/2", 0.005, length, mat, side=side)
    for i, dz in enumerate((f"- {p(length)}/2 + 0.02", f"+ {p(length)}/2 - 0.028"), 1):
        g.door_box(f"{name} - pino {i}", (hx, hy), A, f"{p(a)} - 0.004", f"{p(a)} + 0.004", td, td + 0.026, f"{zc} {dz}", 0.008, mat, side=side, detail=FINE)


def circ(cu, cv, r, n=16) -> list[tuple]:
    """A circle of radius r centered at (cu, cv), as a polygon of n points (for blends: same count on both ends)."""
    return [(add(cu, mul(r, math.cos(2 * math.pi * i / n))) if abs(math.cos(2 * math.pi * i / n)) > 1e-9 else e(cu),
             add(cv, mul(r, math.sin(2 * math.pi * i / n))) if abs(math.sin(2 * math.pi * i / n)) > 1e-9 else e(cv)) for i in range(n)]


def loop_path(cu, cv, ru, rv, n=48) -> list[tuple]:
    """A closed path round an ellipse of a plane, for a swept ring: the seam at the top overlaps itself by 2 mm."""
    pts = oval(cu, cv, ru, rv, n=n, start=90.0)
    top = pts[0][1]
    return [(add(cu, 0.001), top)] + pts + [pts[0], (add(cu, -0.001), top)]
