"""Shared helpers of the sanitary ware modules (bacias, bidê, mictório, lavatórios, banheira).

Not a component module: `make.py` only takes the .py files of tools/appliances.
Besides the kit's shapes these write the engine's `Sweep` (a closed section
carried along a path) and `Blend` (a loft between two outlines) pieces, and
profile points with Bézier handles.

Hollow ceramic is built here WITHOUT voids wherever something has to be seen
inside it (water, drains, overflows): a void cuts every solid it overlaps, so
bowls are `ring`s, sections swept around a closed path, hollow by construction.
"""

from __future__ import annotations

import math

from kit import *  # noqa: F401,F403
from kit import e, p, lift, FULL, FINE, COARSE


# --- points ------------------------------------------------------------------

def bez(u, v, u1, v1, u2, v2) -> dict:
    """A point whose segment to the next is a cubic Bézier with these two handles."""
    return {"u": e(u), "v": e(v), "bezier": {"u1": e(u1), "v1": e(v1), "u2": e(u2), "v2": e(v2)}}


def P(points) -> list[dict]:
    """Profile points from (u, v), (u, v, radius) or ready dicts."""
    out = []
    for pt in points:
        if isinstance(pt, dict):
            out.append(pt)
            continue
        d = {"u": e(pt[0]), "v": e(pt[1])}
        if len(pt) > 2 and pt[2] not in (None, "", 0):
            d["radius"] = e(pt[2])
        out.append(d)
    return out


def add(base, d) -> str:
    """base + d, for a numeric d (an expression that reads well)."""
    if isinstance(d, str):
        return f"{p(base)} + {p(d)}"
    if abs(d) < 5e-7:
        return e(base)
    if isinstance(base, (int, float)):
        return e(base + d)
    return f"{p(base)} + {e(d)}" if d > 0 else f"{p(base)} - {e(-d)}"


def mul(base, k) -> str:
    """base * k, for a numeric k."""
    if isinstance(base, (int, float)):
        return e(base * k)
    return f"{p(base)}*({k:.5f})"


# --- shapes the kit does not have ---------------------------------------------

def sweep(c, name, plane, path, offset, section, material, detail=FULL, in_plan=False, void=False):
    """A closed `section` (u to the left of the path, v along the plane's normal) carried along `path`."""
    shape = {"Sweep": {"plane": plane, "path": P(path), "offset": e(offset), "profile": P(section)}}
    c._add(name, shape, material, detail, in_plan, void)


def blend(c, name, plane, bottom, top, offset, depth, material, detail=FULL, in_plan=False, void=False):
    """A loft from the `bottom` outline at `offset` to the `top` outline `depth` farther along the plane's normal."""
    shape = {"Blend": {"plane": plane, "bottom": P(bottom), "top": P(top), "offset": e(offset), "depth": e(depth)}}
    c._add(name, shape, material, detail, in_plan, void)


def circle(r, n=12) -> list[tuple]:
    """A circular section of radius r, as a polygon."""
    return [(mul(r, math.cos(2 * math.pi * i / n)), mul(r, math.sin(2 * math.pi * i / n))) for i in range(n)]


def tube(c, name, plane, path, offset, radius, material, detail=FULL, in_plan=False, void=False, n=12):
    """A round tube along a path drawn on a plane."""
    sweep(c, name, plane, path, offset, circle(radius, n), material, detail, in_plan, void)


# --- outlines ------------------------------------------------------------------

def oval(cx, cy, rx, ry, n=48, power=2.0, ry_back=None, start=0.0, turn=360.0, close=True) -> list[tuple]:
    """A (super)ellipse as a polygon, counter-clockwise from the angle `start`.

    `power` 2 is an ellipse, more squares it. `ry_back` is the semi-axis of
    the half towards +y when it differs (an egg). With `turn` under 360 the
    points are those of an open arc, both ends included.
    """
    pts = []
    count = n if turn >= 360 and close else n + 1
    for i in range(count):
        t = math.radians(start + turn * i / n)
        co, si = math.cos(t), math.sin(t)
        kx = math.copysign(abs(co) ** (2 / power), co)
        ky = math.copysign(abs(si) ** (2 / power), si)
        r_y = ry_back if (ry_back is not None and ky > 0) else ry
        pts.append((add(cx, mul(rx, kx)) if abs(kx) > 1e-9 else e(cx), add(cy, mul(r_y, ky)) if abs(ky) > 1e-9 else e(cy)))
    return pts


def smooth(points, per=4) -> list[tuple]:
    """A numeric polyline through `points`, rounded (Catmull-Rom), ends kept."""
    n = len(points)
    if n < 3:
        return list(points)
    out = []
    for i in range(n - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, n - 1)]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                       + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t3)
                for j in (0, 1)
            ))
    out.append(tuple(points[-1]))
    return out


def ring(c, name, cx, cy, rx, ry, zbase, section, material, n=64, detail=FULL, in_plan=False, void=False, ry_back=None, power=2.0):
    """A hollow piece: `section` carried around the oval of center (cx, cy) and semi-axes rx, ry.

    `section` is [(d, dz), …]: d the distance OUTWARDS from the oval (the
    oval itself is the piece's hole when no d is negative) and dz the height
    above `zbase`. The seam is at the back (+y) and overlaps itself by 2 mm.
    """
    loop = oval(cx, cy, rx, ry, n=n, power=power, ry_back=ry_back, start=90.0)
    top_y = loop[0][1]
    path = [(add(cx, 0.001), top_y)] + loop + [loop[0], (add(cx, -0.001), top_y)]
    sweep(c, name, "Plan", path, zbase, [(-d if not isinstance(d, str) else f"-({d})", dz) for d, dz in section],
          material, detail, in_plan, void)


def half_ring(c, name, cx, cy, rx, ry, zbase, section, material, n=40, detail=FULL, in_plan=False, void=False, power=2.0):
    """`section` carried around the front half (from +x by -y to -x... run counter-clockwise from -x to +x) of an oval.

    The path runs counter-clockwise from (cx - rx, cy) by the front (-y) to
    (cx + rx, cy); d is outwards as in `ring`. The ends are flat, facing +y.
    """
    arc = oval(cx, cy, rx, ry, n=n, power=power, start=180.0, turn=180.0)
    path = [(arc[0][0], add(cy, 0.002))] + arc + [(arc[-1][0], add(cy, 0.002))]
    sweep(c, name, "Plan", path, zbase, [(-d if not isinstance(d, str) else f"-({d})", dz) for d, dz in section],
          material, detail, in_plan, void)


def loft(c, name, sections, material, detail=FULL, in_plan=False, void=False):
    """Blends stacked through `sections` [(z, outline), …] (plan outlines with as many points)."""
    for i in range(len(sections) - 1):
        (z0, a), (z1, b) = sections[i], sections[i + 1]
        label = name if len(sections) == 2 else f"{name} {i + 1}"
        blend(c, label, "Plan", a, b, z0, f"{p(z1)} - {p(z0)}", material, detail, in_plan, void)


# --- pieces that turn about a hinge along X -----------------------------------------

def hinged_slices(c, name, hinge, angle, xs, backs, fronts, t0, t1, material, detail=FULL, start=1):
    """A flat slab of curved outline that lifts about a back hinge along X (a seat, a lid).

    It is cut in slices along X: slice i runs from xs[i] to xs[i + 1], and at
    xs[i] the slab spans backs[i]..fronts[i] forward of the hinge (`r` of
    `lift`) and t0..t1 above it. Each slice is a loft between its two end
    sections, so the outline comes out as a polygon through the given points.
    """
    def quad(i):
        return [lift(hinge, angle, r, t) for r, t in ((backs[i], t0), (backs[i], t1), (fronts[i], t1), (fronts[i], t0))]

    for i in range(len(xs) - 1):
        blend(c, f"{name} {start + i}", "Side", quad(i), quad(i + 1), xs[i], f"{p(xs[i + 1])} - {p(xs[i])}", material, detail)


def seat_nodes(alpha):
    """Fractions of the half width where a seat is sliced: fine near the opening's ends (|s| = alpha)."""
    inner = [alpha * math.sin(math.radians(a)) for a in (-90, -67.5, -45, -22.5, 0, 22.5, 45, 67.5, 90)]
    side = [alpha + (1 - alpha) * k for k in (0.4, 0.7, 0.9, 0.985)]
    return [-s for s in reversed(side)] + inner + side


def seat_and_lid(c, hinge, seat_angle, lid_angle, cy, a, b, alpha, bi, seat_t=(-0.010, 0.010), lid_t=(0.012, 0.026),
                 seat_material="Branco", lid_material="Branco"):
    """An oval seat ring and its lid, both lifting about `hinge` (y, z).

    The outline is the ellipse of center (0, cy) and semi-axes a (x), b (y);
    the seat's opening the ellipse of semi-axes alpha * a and bi.
    """
    hy = hinge[0]
    nodes = seat_nodes(alpha)
    xs = [mul(a, s) for s in nodes]
    out = [math.sqrt(max(0.0, 1 - s * s)) for s in nodes]
    inn = [math.sqrt(max(0.0, 1 - (s / alpha) ** 2)) if abs(s) < alpha - 1e-9 else 0.0 for s in nodes]
    r_center = f"{p(hy)} - {p(cy)}"  # the ellipse's center, forward of the hinge
    front = [add(r_center, mul(b, k)) for k in out]
    back = [add(r_center, mul(b, -k)) for k in out]
    in_front = [add(r_center, mul(bi, k)) for k in inn]
    in_back = [add(r_center, mul(bi, -k)) for k in inn]
    lo = next(i for i, s in enumerate(nodes) if abs(s + alpha) < 1e-9)
    hi = next(i for i, s in enumerate(nodes) if abs(s - alpha) < 1e-9)
    # The seat: whole slices beside the opening, a front and a back one across it.
    hinged_slices(c, "Assento – lateral esquerda", hinge, seat_angle, xs[: lo + 1], back[: lo + 1], front[: lo + 1], *seat_t, seat_material)
    hinged_slices(c, "Assento – frente", hinge, seat_angle, xs[lo: hi + 1], in_front[lo: hi + 1], front[lo: hi + 1], *seat_t, seat_material)
    hinged_slices(c, "Assento – fundo", hinge, seat_angle, xs[lo: hi + 1], back[lo: hi + 1], in_back[lo: hi + 1], *seat_t, seat_material)
    hinged_slices(c, "Assento – lateral direita", hinge, seat_angle, xs[hi:], back[hi:], front[hi:], *seat_t, seat_material)
    hinged_slices(c, "Tampa", hinge, lid_angle, xs, back, front, *lid_t, lid_material)


# --- fittings ------------------------------------------------------------------------

def angle_valve(c, name, x, yw, z, suffix="", up=True):
    """An angle stop valve on the wall (y = yw) at (x, z): escutcheon, body, handle and outlet.

    Returns (y, z) of the outlet's end, where the hose starts.
    """
    s = f" {suffix}" if suffix else ""
    c.cyl_y(f"Canopla do {name}{s}", x, z, add(yw, -0.007), 0.026, 0.007, "Cromado")
    c.cyl_y(f"Corpo do {name}{s}", x, z, add(yw, -0.052), 0.0105, 0.045, "Cromado")
    c.cyl_y(f"Volante do {name}{s}", x, z, add(yw, -0.072), 0.015, 0.018, "Cromado", FINE)
    c.box(f"Borboleta do {name}{s}", add(x, -0.004), add(yw, -0.082), add(z, -0.019), 0.008, 0.011, 0.038, "Cromado", FINE)
    zo = add(z, 0.008) if up else add(z, -0.03)
    c.cyl(f"Saída do {name}{s}", x, add(yw, -0.034), zo, 0.008, 0.022, "Cromado", FINE)
    zn = add(z, 0.026) if up else add(z, -0.038)
    c.cyl(f"Porca do {name}{s}", x, add(yw, -0.034), zn, 0.0115, 0.012, "Latão", FINE)
    return add(yw, -0.034), (add(z, 0.038) if up else add(z, -0.038))


def mixer(c, name, x, y, z, lever_angle, reach=0.115, height=0.105, suffix=""):
    """A single-lever basin mixer standing on (x, y, z), spout towards the front (-y).

    Returns (y, z) of the aerator's outlet.
    """
    s = f" {suffix}" if suffix else ""

    def xs(d):
        return add(x, d)

    def zs(d):
        return add(z, d)

    c.rev(f"Base {name}{s}", "Front", [(x, z), (xs(0.027), z), (xs(0.027), zs(0.003)), (xs(0.023), zs(0.009)), (x, zs(0.009))], y, x, "Cromado")
    c.rev(f"Corpo {name}{s}", "Front", [
        (x, zs(0.009)), (xs(0.0215), zs(0.009)), (xs(0.0195), zs(height - 0.006)), (xs(0.0165), zs(height)), (x, zs(height)),
    ], y, x, "Cromado")
    # The spout: a flat oval section rising slightly to the front.
    z0, z1 = zs(height * 0.52), zs(height * 0.52 + 0.022)
    sweep(c, f"Bica {name}{s}", "Side", [(add(y, -0.008), z0), (add(y, -reach - 0.012), z1)], x,
          [(-0.0105, -0.006), (-0.0105, 0.006), (-0.006, 0.0125), (0.006, 0.0125), (0.0105, 0.006), (0.0105, -0.006), (0.006, -0.0125), (-0.006, -0.0125)],
          "Cromado")
    ya = add(y, -reach)
    c.cyl(f"Arejador {name}{s}", x, ya, add(z1, -0.021), 0.0105, 0.012, "Cromado", FINE)
    c.cyl(f"Tela do arejador {name}{s}", x, ya, add(z1, -0.0225), 0.008, 0.002, "Plástico cinza", FINE)
    # The lever, lifting about a pivot on the top of the body.
    hinge = (add(y, 0.006), zs(height + 0.004))
    c.rev(f"Cúpula {name}{s}", "Front", [(x, zs(height)), (xs(0.0165), zs(height)), (xs(0.0165), zs(height + 0.004), 0.02), (x, zs(height + 0.013))], y, x, "Cromado")
    c.profile(f"Alavanca {name}{s}", "Side", [lift(hinge, lever_angle, r, t) for r, t in
                                              ((-0.012, 0.004), (-0.012, 0.014), (0.03, 0.016), (0.1, 0.012), (0.1, 0.006), (0.03, 0.006))],
              xs(-0.011), 0.022, "Cromado")
    return ya, add(z1, -0.0225)


def popup_drain(c, name, x, y, z, suffix="", radius=0.031):
    """A pop-up waste standing on a basin's floor at (x, y, z): flange and plug."""
    s = f" {suffix}" if suffix else ""
    c.rev(f"Válvula {name}{s}", "Front", [(x, z), (add(x, radius), z), (add(x, radius), add(z, 0.002)), (add(x, radius - 0.006), add(z, 0.004)), (x, add(z, 0.004))],
          y, x, "Cromado", in_plan=True)
    c.rev(f"Tampão {name}{s}", "Front", [(x, add(z, 0.004)), (add(x, radius - 0.01), add(z, 0.004)), (add(x, radius - 0.01), add(z, 0.006), 0.05), (x, add(z, 0.0095))],
          y, x, "Cromado", detail=FINE)
