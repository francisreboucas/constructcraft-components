"""Helpers of the detailed sanitary ware modules (bacia com válvula, bidê, mictório, lavatórios).

Not a component module: make.py skips files starting with `_`. It adds to the
`louca` package (which it imports) what these modules share:

- `X`, an expression that is a linear combination of parameters plus a
  constant. It is a `str` (so the kit and louca take it as an expression) and
  it adds, subtracts and scales like a number, so outlines can be computed
  point by point and stay correct for every type.
- Smooth curves through such points (Catmull-Rom, cubic Bézier samples): the
  engine draws straight segments between profile points, it has no Bézier
  handles (ccad 0.12 drops them; `flatten_beziers` samples a helper's).
- `contour` outlines and `shell_halves`, hollow basins lofted in two halves so
  the cavity can have any outline at each height (a `ring`'s is an offset).
- Fittings: an angle valve with an extension, a bottle trap, flexible hoses.
"""

from __future__ import annotations

import math
import re

from louca import *  # noqa: F401,F403
from louca import sweep, blend, tube, add, mul, circle
from kit import e, p, FULL, FINE, COARSE, ALL

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _num(v: float) -> str:
    text = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


class X(str):
    """An affine expression: sum of coefficient * parameter, plus a constant."""

    terms: dict
    c: float

    def __new__(cls, terms=None, c=0.0):
        terms = {k: float(v) for k, v in (terms or {}).items() if abs(v) > 1e-9}
        c = 0.0 if abs(c) < 5e-7 else float(c)
        parts = []
        for name, k in terms.items():
            mag = abs(k)
            body = name if abs(mag - 1) < 1e-9 else f"{_num(mag)}*{name}"
            parts.append(("-" if k < 0 else "+", body))
        if c or not parts:
            parts.append(("-" if c < 0 else "+", _num(abs(c))))
        text = ""
        for i, (sign, body) in enumerate(parts):
            if i == 0:
                text = body if sign == "+" else f"-{body}"
            else:
                text += f" {sign} {body}"
        obj = super().__new__(cls, text)
        obj.terms, obj.c = terms, c
        return obj

    # arithmetic -------------------------------------------------------------
    def __add__(self, other):
        o = V(other)
        terms = dict(self.terms)
        for k, v in o.terms.items():
            terms[k] = terms.get(k, 0.0) + v
        return X(terms, self.c + o.c)

    __radd__ = __add__

    def __neg__(self):
        return X({k: -v for k, v in self.terms.items()}, -self.c)

    def __sub__(self, other):
        return self + (-V(other))

    def __rsub__(self, other):
        return V(other) + (-self)

    def __mul__(self, k):
        if isinstance(k, X) or isinstance(k, str):
            o = V(k)
            if o.terms and self.terms:
                raise ValueError("X * X is not affine")
            if not o.terms:
                k = o.c
            else:
                return o * self.c
        return X({n: v * k for n, v in self.terms.items()}, self.c * k)

    __rmul__ = __mul__

    def __truediv__(self, k):
        return self * (1.0 / k)

    def __hash__(self):
        return str.__hash__(self)

    def __eq__(self, other):
        return str.__eq__(self, other)

    def value(self, values: dict) -> float:
        return self.c + sum(k * values[n] for n, k in self.terms.items())


def V(v) -> X:
    """A number, a parameter name or an X as an X."""
    if isinstance(v, X):
        return v
    if isinstance(v, (int, float)):
        return X(None, v)
    if isinstance(v, str) and _NAME.match(v):
        return X({v: 1.0})
    raise ValueError(f"not an affine expression: {v!r}")


def lerp(a, b, t):
    return V(a) * (1 - t) + V(b) * t


# --- curves -------------------------------------------------------------------

def catmull(points, per=4) -> list[tuple]:
    """A polyline through `points` (tuples of numbers or X), rounded (Catmull-Rom), ends kept."""
    n = len(points)
    if n < 3:
        return list(points)
    out = []
    dims = len(points[0])
    for i in range(n - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, n - 1)]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            w0 = 0.5 * (-t + 2 * t2 - t3)
            w1 = 0.5 * (2 - 5 * t2 + 3 * t3)
            w2 = 0.5 * (t + 4 * t2 - 3 * t3)
            w3 = 0.5 * (-t2 + t3)
            out.append(tuple(V(p0[j]) * w0 + V(p1[j]) * w1 + V(p2[j]) * w2 + V(p3[j]) * w3 for j in range(dims)))
    out.append(tuple(V(q) for q in points[-1]))
    return out


def bezier(p0, p1, p2, p3, n=8, first=True) -> list[tuple]:
    """Points of the cubic Bézier p0 -> p3 with handles p1, p2 (tuples of numbers or X)."""
    out = []
    for i in range(0 if first else 1, n + 1):
        t = i / n
        w = ((1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3)
        out.append(tuple(V(p0[j]) * w[0] + V(p1[j]) * w[1] + V(p2[j]) * w[2] + V(p3[j]) * w[3] for j in range(len(p0))))
    return out


def arc(cu, cv, r, a0, a1, n=8) -> list[tuple]:
    """Points of the circular arc of center (cu, cv), radius r, from angle a0 to a1 (degrees)."""
    return [(V(cu) + V(r) * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             V(cv) + V(r) * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def soval(cx, cy, rx, ry, angles, power=2.0, ry_back=None) -> list[tuple]:
    """Points of a superellipse at the given angles (degrees, 0 = +x, 90 = +y)."""
    pts = []
    for a in angles:
        t = math.radians(a)
        co, si = math.cos(t), math.sin(t)
        kx = math.copysign(abs(co) ** (2 / power), co) if abs(co) > 1e-12 else 0.0
        ky = math.copysign(abs(si) ** (2 / power), si) if abs(si) > 1e-12 else 0.0
        r_y = ry_back if (ry_back is not None and ky > 0) else ry
        pts.append((V(cx) + V(rx) * kx, V(cy) + V(r_y) * ky))
    return pts


def angle_for_x(frac, power=2.0) -> float:
    """The superellipse angle (0..90) whose point has x = frac * rx."""
    frac = min(max(frac, 0.0), 1.0)
    return math.degrees(math.acos(frac ** (power / 2)))


def contour(cx, cy, rx, ry_front, ry_back=None, p_front=2.0, p_back=None):
    """A plan outline as a function of angles (degrees): a superellipse whose front (-y) and back halves may differ.

    Returns f(angles) -> points. With `ry_back`/`p_back` the half towards +y has its own semi-axis and power
    (a large power and the back on the wall gives a basin's straight back with rounded corners).
    """
    def f(angles):
        pts = []
        for a in angles:
            t = math.radians(a)
            co, si = math.cos(t), math.sin(t)
            back = si > 1e-12
            pw = p_back if (back and p_back) else p_front
            kx = math.copysign(abs(co) ** (2 / pw), co) if abs(co) > 1e-12 else 0.0
            ky = math.copysign(abs(si) ** (2 / pw), si) if abs(si) > 1e-12 else 0.0
            ry = ry_back if (back and ry_back is not None) else ry_front
            pts.append((V(cx) + V(rx) * kx, V(cy) + V(ry) * ky))
        return pts
    return f


def spread(a0, a1, n):
    return [a0 + (a1 - a0) * i / n for i in range(n + 1)]


def flatten_beziers(c, n=8):
    """Replace the Bézier points of the component's sweeps, profiles and revolutions by polylines through the curve.

    ccad 0.12 ignores a point's `bezier` handles (the segment comes out straight), so a shared helper's
    curves (the trapway bulges of `louca.bacia`) are sampled here, as expressions.
    """
    def expand(points):
        out = []
        for i, q in enumerate(points):
            b = q.get("bezier")
            if not b or i + 1 >= len(points):
                out.append({k: v for k, v in q.items() if k != "bezier"})
                continue
            nxt = points[i + 1]
            ctrl = ((q["u"], q["v"]), (b["u1"], b["v1"]), (b["u2"], b["v2"]), (nxt["u"], nxt["v"]))
            for k in range(n):
                t = k / n
                w = ((1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3)
                pt = {}
                for j, key in enumerate(("u", "v")):
                    pt[key] = " + ".join(f"{wk:.6f}*{p(cp[j])}" for wk, cp in zip(w, ctrl) if wk > 1e-9)
                out.append(pt)
        return out

    for item in c.items:
        shape = item["shape"]
        kind = next(iter(shape))
        body = shape[kind]
        keys = {"Sweep": ("path", "profile"), "Profile": ("points",), "Revolution": ("points",)}.get(kind, ())
        for key in keys:
            if any("bezier" in q for q in body[key]):
                body[key] = expand(body[key])


# --- shapes -------------------------------------------------------------------

def shell_halves(c, name, levels, material, detail=FULL, n=14, names=("esquerda", "direita")):
    """A hollow basin as two lofted halves, so its cavity may have any outline at each height (a ring's is an offset).

    `levels` = [(z, outer, inner), …] from the top down or the bottom up, where `outer` and `inner` are
    `contour` functions: the solid lies between them. Each half runs from the back (+y) by its side to
    the front; they meet on x = 0.
    """
    sides = (
        (names[0], spread(90, 270, 2 * n), spread(270, 90, 2 * n)),
        (names[1], spread(90, -90, 2 * n), spread(-90, 90, 2 * n)),
    )
    for label, out_a, in_a in sides:
        secs = [(z, outer(out_a) + inner(in_a)) for z, outer, inner in levels]
        loft_x(c, f"{name} – metade {label}", secs, material, detail)


def scaled(k, h):
    """A mapper of points/lengths about the point h = (x, y, z) by the factor expression k (a part a type may not have)."""
    def at(i, v):
        return f"{p(h[i])} + {k}*({e(V(v) - V(h[i]))})"

    class S:
        def x(self, v):
            return at(0, v)

        def y(self, v):
            return at(1, v)

        def z(self, v):
            return at(2, v)

        def l(self, v):
            return f"{k}*({e(v)})"

        def plan(self, pts):
            return [(self.x(a), self.y(b)) for a, b in pts]

    return S()

def loft_x(c, name, sections, material, detail=FULL, in_plan=False, void=False):
    """`louca.loft` for sections whose z are X/numbers: blends stacked through [(z, outline), …]."""
    for i in range(len(sections) - 1):
        (z0, a), (z1, b) = sections[i], sections[i + 1]
        label = name if len(sections) == 2 else f"{name} {i + 1}"
        blend(c, label, "Plan", a, b, z0, V(z1) - V(z0), material, detail, in_plan, void)


def side_loft(c, name, sections, material, detail=FULL, in_plan=False):
    """Blends stacked along X through [(x, outline in (y, z)), …] on the Side plane."""
    for i in range(len(sections) - 1):
        (x0, a), (x1, b) = sections[i], sections[i + 1]
        label = name if len(sections) == 2 else f"{name} {i + 1}"
        blend(c, label, "Side", a, b, x0, V(x1) - V(x0), material, detail, in_plan)


# --- fittings -------------------------------------------------------------------

def angle_valve_ext(c, name, x, yw, z, reach=0.034, suffix="", detail_body=FULL):
    """An angle stop valve on the wall (y = yw) at (x, z), its outlet `reach` out of the wall, pointing up.

    Escutcheon, threaded nipple, body, handle with its wings, outlet and nut.
    Returns (y, z) of the outlet's end, where the hose starts.
    """
    s = f" {suffix}" if suffix else ""
    yo = V(yw) - reach
    c.cyl_y(f"Canopla do {name}{s}", x, z, V(yw) - 0.007, 0.026, 0.007, "Cromado")
    c.cyl_y(f"Niple do {name}{s}", x, z, yo + 0.01, 0.0085, V(yw) - yo - 0.017, "Cromado", FINE)
    c.cyl_y(f"Corpo do {name}{s}", x, z, yo - 0.013, 0.0115, 0.026, "Cromado", detail_body)
    c.cyl_y(f"Haste do {name}{s}", x, z, yo - 0.03, 0.006, 0.018, "Cromado", FINE)
    c.cyl_y(f"Volante do {name}{s}", x, z, yo - 0.042, 0.015, 0.014, "Cromado", FINE)
    c.box(f"Borboleta do {name}{s}", V(x) - 0.004, yo - 0.05, V(z) - 0.019, 0.008, 0.01, 0.038, "Cromado", FINE)
    c.cyl(f"Saída do {name}{s}", x, yo, V(z) + 0.008, 0.008, 0.022, "Cromado", FINE)
    c.cyl(f"Porca do {name}{s}", x, yo, V(z) + 0.026, 0.0115, 0.012, "Cromado", FINE)
    return yo, V(z) + 0.038


def hose(c, name, x0, z0, x1, z1, y, radius=0.0055, material="Inox escovado", detail=FINE, n=10):
    """A braided hose in the Front plane at y: up from (x0, z0), an S bend, up into (x1, z1)."""
    zm0 = lerp(z0, z1, 0.3)
    zm1 = lerp(z0, z1, 0.7)
    pts = [(V(x0), V(z0))] + bezier((x0, zm0), (x0, lerp(z0, z1, 0.55)), (x1, lerp(z0, z1, 0.45)), (x1, zm1), n=n) + [(V(x1), V(z1))]
    tube(c, name, "Front", pts, y, radius, material, detail, n=10)


def bottle_trap(c, x, y, z_tail_top, z_arm, yw, material="Cromado", suffix="", r_cup=0.032, outlet_down=None, y_down=None):
    """A bottle trap (sifão de copo) under a drain at (x, y): tail from z_tail_top, cup around z_arm, arm to the wall.

    `outlet_down`: when given (a z), the arm turns down into a pipe at y = `y_down` (by default
    2 cm off the wall) that ends at that z, instead of entering the wall. Returns (y, z) where
    the arm or the down pipe ends.
    """
    s = f" {suffix}" if suffix else ""
    zc0, zc1 = V(z_arm) - 0.07, V(z_arm) + 0.045  # the cup
    c.cyl(f"Tubo do sifão{s}", x, y, zc1 - 0.004, 0.016, V(z_tail_top) - zc1 + 0.004, material)
    c.cyl(f"Porca do tubo do sifão{s}", x, y, zc1 - 0.008, 0.022, 0.018, material, FINE)
    c.rev(f"Copo do sifão{s}", "Front", [
        (x, zc0 + 0.004), (V(x) + r_cup - 0.006, zc0 + 0.004), (V(x) + r_cup, zc0 + 0.012), (V(x) + r_cup, zc1 - 0.012),
        (V(x) + r_cup - 0.008, zc1), (x, zc1)], y, x, material)
    c.rev(f"Tampa do copo{s}", "Front", [(x, zc0), (V(x) + r_cup - 0.004, zc0), (V(x) + r_cup - 0.002, zc0 + 0.006), (x, zc0 + 0.006)],
          y, x, material, detail=FINE)
    c.rev(f"Anel do copo{s}", "Front", [(x, zc1 - 0.016), (V(x) + r_cup + 0.0015, zc1 - 0.016), (V(x) + r_cup + 0.0015, zc1 - 0.01), (x, zc1 - 0.01)],
          y, x, material, detail=FINE)
    y_cup_back = V(y) + r_cup - 0.004
    if outlet_down is None:
        c.cyl_y(f"Braço do sifão{s}", x, z_arm, y_cup_back, 0.016, V(yw) - y_cup_back - 0.002, material)
        c.cyl_y(f"Porca do braço do sifão{s}", x, z_arm, y_cup_back + 0.002, 0.021, 0.016, material, FINE)
        c.cyl_y(f"Canopla do sifão{s}", x, z_arm, V(yw) - 0.008, 0.036, 0.008, material, FINE)
        return V(yw), V(z_arm)
    yp = V(y_down) if y_down is not None else V(yw) - 0.02  # the down pipe's axis
    yd = yp - 0.025
    c.cyl_y(f"Braço do sifão{s}", x, z_arm, y_cup_back, 0.016, yd - y_cup_back, material)
    c.cyl_y(f"Porca do braço do sifão{s}", x, z_arm, y_cup_back + 0.002, 0.021, 0.016, material, FINE)
    tube(c, f"Curva do sifão{s}", "Side", arc(yd, V(z_arm) - 0.025, 0.025, 90, 0, n=6), x, 0.016, material, n=12)
    c.cyl(f"Tubo de saída do sifão{s}", x, yp, outlet_down, 0.016, V(z_arm) - 0.025 - V(outlet_down), material)
    return yp, V(outlet_down)
