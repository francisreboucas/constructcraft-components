"""Shared pieces of the window components (not a component: no `build()`).

Frame of a wall-hosted window: x along the wall from the opening's center, y
across the wall (-y is the exterior, where the sill overhangs; +y the room), z
up from the sill. `WallThickness` is the host wall's thickness.
"""

from kit import *

ALU = "Alumínio anodizado"
GLASS = "Vidro"
RUBBER = "Borracha"
STONE = "Granito"
NUM = (int, float)


def plus(*terms):
    """The sum of numbers and expressions, as a number or a parenthesized expression."""
    if all(isinstance(t, NUM) for t in terms):
        return sum(terms)
    return "(" + " + ".join(p(t) for t in terms) + ")"


def minus(a, b):
    if isinstance(a, NUM) and isinstance(b, NUM):
        return a - b
    return f"({p(a)} - {p(b)})"


def times(a, b):
    if isinstance(a, NUM) and isinstance(b, NUM):
        return a * b
    return f"({p(a)}*{p(b)})"


def stone(c):
    c.material(STONE, (70, 70, 75), "Generic", "Polished")


# --- fixed frames --------------------------------------------------------------

def ring(c, name, x0, x1, z0, z1, section, material, detail=FULL, sides="lrbt"):
    """A rectangular frame x0..x1, z0..z1 of one section, the four members meeting like a miter.

    `section` is an outline [(a, y), …]: `a` is the distance from the frame's
    outer edge inwards, y is across the wall. Stiles and rails run the whole
    length and share the corners.
    """
    if "l" in sides:
        c.profile(f"{name} montante esquerdo", "Plan", [(plus(x0, a), y) for a, y in section], z0, minus(z1, z0), material, detail)
    if "r" in sides:
        c.profile(f"{name} montante direito", "Plan", [(minus(x1, a), y) for a, y in reversed(section)], z0, minus(z1, z0), material, detail)
    if "b" in sides:
        c.profile(f"{name} travessa inferior", "Side", [(y, plus(z0, a)) for a, y in reversed(section)], x0, minus(x1, x0), material, detail)
    if "t" in sides:
        c.profile(f"{name} travessa superior", "Side", [(y, minus(z1, a)) for a, y in section], x0, minus(x1, x0), material, detail)


def box_ring(c, name, x0, x1, z0, z1, a0, a1, y0, y1, material, detail=FULL, sides="lrbt"):
    """A rectangular frame of rectangular section a0..a1 (from the outer edge inwards), y0..y1, butt joints."""
    w, d = minus(a1, a0), minus(y1, y0)
    hz = minus(minus(z1, z0), times(2, a0))
    wx = minus(minus(x1, x0), times(2, a1))
    if "l" in sides:
        c.box(f"{name} esquerdo", plus(x0, a0), y0, plus(z0, a0), w, d, hz, material, detail)
    if "r" in sides:
        c.box(f"{name} direito", minus(x1, a1), y0, plus(z0, a0), w, d, hz, material, detail)
    if "b" in sides:
        c.box(f"{name} inferior", plus(x0, a1), y0, plus(z0, a0), wx, d, w, material, detail)
    if "t" in sides:
        c.box(f"{name} superior", plus(x0, a1), y0, minus(z1, a1), wx, d, w, material, detail)


def peitoril(c, L, yext, yint, inner=STONE, coarse=True):
    """The stone sill: a nose with a drip groove outside, a ramp up to the frame's
    exterior face `yext`, and a stool from the frame's interior face `yint` to a
    rounded nose in the room."""
    W = "(-WallThickness/2)"
    I = "(WallThickness/2)"
    xl, wl = f"(-{L}/2 - 0.03)", f"({L} + 0.06)"
    if coarse:
        c.box("Peitoril simplificado", xl, f"{W} - 0.03", -0.02, wl, "WallThickness + 0.03", 0.02, STONE, COARSE)
    c.profile("Peitoril externo", "Side", [
        (f"{W} + 0.01", -0.02), (f"{W} - 0.014", -0.02), (f"{W} - 0.014", -0.015), (f"{W} - 0.02", -0.015),
        (f"{W} - 0.02", -0.02), (f"{W} - 0.03", -0.02), (f"{W} - 0.03", 0.0), (f"{W} + 0.01", 0.004),
    ], xl, wl, STONE)
    yr = f"max({p(yext)}, {W} + 0.012)"
    c.profile("Peitoril rampa", "Side", [(f"{W} + 0.0095", 0), (yr, 0), (yr, 0.012), (f"{W} + 0.0095", 0.004)],
              f"(-{L}/2 + 0.0005)", f"({L} - 0.001)", STONE)
    yi = f"min({p(yint)}, {I} - 0.002)"
    c.box("Peitoril interno", f"(-{L}/2 + 0.0005)", yi, 0, f"({L} - 0.001)", f"({I} + 0.001 - {yi})", 0.005, inner)
    c.profile("Peitoril interno bocel", "Side", [
        (I, -0.022), (f"{I} + 0.014", -0.022, 0.008), (f"{I} + 0.022", -0.014), (f"{I} + 0.022", -0.003, 0.008),
        (f"{I} + 0.014", 0.005), (I, 0.005),
    ], xl, wl, inner)


# --- moving sashes -------------------------------------------------------------

def tilt_pt(hinge, angle, s, t):
    """Side (y, z) of a point of a sash turning about a horizontal axis `hinge` = (y, z).

    Closed, `s` runs up from the axis and `t` out of it towards the exterior
    (-y). `angle` swings what is below the axis outwards (and what is above it
    into the room).
    """
    hy, hz = p(hinge[0]), p(hinge[1])
    s, t, g = p(s), p(t), p(angle)
    return (f"{hy} - {t}*cos({g}) + {s}*sin({g})", f"{hz} + {s}*cos({g}) + {t}*sin({g})")


def tilt_prof(c, name, hinge, angle, x, width, points, material, detail=FULL):
    """An outline [(s, t), …] of a tilting sash (see `tilt_pt`), extruded from x along the wall."""
    c.profile(name, "Side", [tilt_pt(hinge, angle, s, t) for s, t in points], x, width, material, detail)


def tilt_box(c, name, hinge, angle, x, width, s0, s1, t0, t1, material, detail=FULL):
    tilt_prof(c, name, hinge, angle, x, width, [(s0, t0), (s0, t1), (s1, t1), (s1, t0)], material, detail)


def swing_pt(hinge, angle, a, b, side="left"):
    """Plan (x, y) of a point of a leaf hinged on a vertical axis `hinge` = (x, y), opening into the room (+y).

    Closed, `a` runs from the hinge along the leaf (to +x for a hinge on the
    `left`, to -x on the `right`) and `b` towards the room (+y).
    """
    hx, hy = p(hinge[0]), p(hinge[1])
    a, b, g = p(a), p(b), p(angle)
    sa, sb = ("+", "-") if side == "left" else ("-", "+")
    return (f"{hx} {sa} {a}*cos({g}) {sb} {b}*sin({g})", f"{hy} + {a}*sin({g}) + {b}*cos({g})")


def swing_box(c, name, hinge, angle, a0, a1, b0, b1, z, height, material, side="left", detail=FULL):
    pts = [swing_pt(hinge, angle, a, b, side) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
    c.profile(name, "Plan", pts, z, height, material, detail)


def swing_prof(c, name, hinge, angle, points, z, height, material, side="left", detail=FULL):
    """An outline [(a, b), …] or [(a, b, radius), …] of a swinging leaf, extruded up from z."""
    pts = [swing_pt(hinge, angle, q[0], q[1], side) + tuple(q[2:]) for q in points]
    c.profile(name, "Plan", pts, z, height, material, detail)


def tilt_ring(c, name, hinge, angle, x0, x1, s0, s1, a0, a1, t0, t1, material, detail=FULL, sides="lrbt"):
    """A rectangular frame of a tilting sash: section a0..a1 from its outer edge (x0..x1, s0..s1) inwards, t0..t1."""
    w = minus(a1, a0)
    wx = minus(minus(x1, x0), times(2, a1))
    if "l" in sides:
        tilt_box(c, f"{name} esquerdo", hinge, angle, plus(x0, a0), w, plus(s0, a0), minus(s1, a0), t0, t1, material, detail)
    if "r" in sides:
        tilt_box(c, f"{name} direito", hinge, angle, minus(x1, a1), w, plus(s0, a0), minus(s1, a0), t0, t1, material, detail)
    if "b" in sides:
        tilt_box(c, f"{name} inferior", hinge, angle, plus(x0, a1), wx, plus(s0, a0), plus(s0, a1), t0, t1, material, detail)
    if "t" in sides:
        tilt_box(c, f"{name} superior", hinge, angle, plus(x0, a1), wx, minus(s1, a1), minus(s1, a0), t0, t1, material, detail)


def old_frame(c, L, H, depth, material, y0=None):
    """The coarse stand-in of the frame: four bars 4 cm wide, `depth` across the wall."""
    y0 = -depth / 2 if y0 is None else y0
    c.box("Marco simplificado esquerdo", f"(-{L}/2)", y0, 0, 0.04, depth, H, material, COARSE)
    c.box("Marco simplificado direito", f"({L}/2 - 0.04)", y0, 0, 0.04, depth, H, material, COARSE)
    c.box("Marco simplificado inferior", f"(-{L}/2 + 0.04)", y0, 0, f"({L} - 0.08)", depth, 0.04, material, COARSE)
    c.box("Marco simplificado superior", f"(-{L}/2 + 0.04)", y0, f"({H} - 0.04)", f"({L} - 0.08)", depth, 0.04, material, COARSE)


def opening_param(c, name, kind, opened):
    """An instance parameter that opens a sash, closed (0) by default.

    Hosted windows take no instance values yet (`component_params_set` refuses
    them), so make.py cannot render an open pose: set the environment variable
    JANELAS_ABERTAS=1 to preview the component with `opened` as the default
    (never commit a source made that way).
    """
    import os
    return c.param(name, opened if os.environ.get("JANELAS_ABERTAS") else 0.0, kind, True)
