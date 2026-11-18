"""Tanque de lavar roupa de louça com coluna: cuba oca com esfregador nervurado, borda larga, válvula,
coluna aberta atrás com sifão e braço até a parede, torneira de parede com bico para mangueira."""

import math

from louca import *
from _casco import shell, annulus

DEPTH = 0.29  # inner depth of the bowl
# (height above the bowl's floor, inset of the walls from the opening)
PROFILE = [(-0.015, 0.052), (0.0, 0.05), (0.008, 0.037), (0.02, 0.029), (0.04, 0.023), (DEPTH - 0.006, 0.0), (DEPTH, -0.006)]


def inset_at(v):
    """The walls' inset at the height v above the floor (linear between the levels)."""
    for (v0, a0), (v1, a1) in zip(PROFILE, PROFILE[1:]):
        if v0 <= v <= v1:
            return a0 + (a1 - a0) * (v - v0) / (v1 - v0)
    return PROFILE[-1][1]


def u_outline(Y, w, front, t, rc, n=6):
    """A U open at the back (y = Y - 0.004), front at Y - `front`: half width w, wall t, front corners rc."""
    yb = add(Y, -0.004)
    pts = []

    def arc(cx, cyd, r, a0, a1):
        out = []
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / n)
            out.append((e(cx + r * math.cos(a)), add(Y, -(cyd) + r * math.sin(a))))
        return out

    # Outer edge from the back left, round the front, to the back right; then the inner edge back.
    pts.append((e(-w), yb))
    pts += arc(-w + rc, front - rc, rc, 180, 270)
    pts += arc(w - rc, front - rc, rc, 270, 360)
    pts.append((e(w), yb))
    pts.append((e(w - t), yb))
    pts += arc(w - rc, front - rc, rc - t, 360, 270)
    pts += arc(-w + rc, front - rc, rc - t, 270, 180)
    pts.append((e(-w + t), yb))
    return pts


def build():
    c = Component("Tanque de lavar roupa", "plumbing", "tanque", "Plumbing")
    L = c.param("Largura", 0.6)
    P = c.param("Profundidade", 0.55)
    A = c.param("Altura", 0.9)
    c.type("Tanque 40 L", "Tanque de louça com coluna")
    c.type("Tanque 60 L", "Tanque de louça com coluna", Largura=0.75, Profundidade=0.6)
    c.mep = {"Fixture": {"drain_units": 3, "supply_weight": 0.7, "hot_water": False}}

    x0, x1, y0, y1 = f"-{L} / 2", f"{L} / 2", f"-{P} / 2", f"{P} / 2"
    RS, RB = 0.04, 0.06  # rim at the front and sides, at the back
    RC = 0.07  # corner radius of the bowl's opening
    ZF = add(A, -DEPTH)  # the bowl's floor
    ox0, ox1, oy0, oy1 = add(x0, RS), add(x1, -RS), add(y0, RS), add(y1, -RB)

    def opening(d):
        return (add(ox0, d), add(oy0, d), add(ox1, -d), add(oy1, -d), e(RC - d))

    def z(v):
        return add(ZF, v)

    LOUCA = "Louça"
    zb = z(-0.015)  # underside of the bowl

    # --- coarse stand-ins ---
    c.box("Tanque simplificado", x0, y0, add(A, -0.32), L, P, 0.32, LOUCA, COARSE, in_plan=True)
    c.box("Coluna simplificada", -0.12, add(y1, -0.215), 0, 0.24, 0.211, add(A, -0.32), LOUCA, COARSE)

    # --- the bowl: a hollow ceramic shell, a wide rim and a back skirt to the wall ---
    shell(c, "Cuba", [(z(v), opening(a)) for v, a in PROFILE], 0.015, LOUCA)
    fl = opening(0.051)
    c.profile("Fundo da cuba", "Plan", rrect(*fl[:4], fl[4]), zb, 0.015, LOUCA)
    c.profile("Borda", "Plan", annulus(opening(-0.006), (x0, y0, x1, y1, 0.035)), add(A, -0.035), 0.035, LOUCA)
    c.box("Encosto traseiro", add(x0, 0.03), add(y1, -0.048), add(A, -0.2), f"{L} - 0.06", 0.046, 0.166, LOUCA)
    # Plan symbol: the outline, the bowl and the washboard's edge.
    c.profile("Símbolo - contorno", "Plan", rrect(x0, y0, x1, y1, 0.035), A, 0.001, LOUCA)
    c.plan_only("Símbolo - contorno")
    top = opening(-0.006)
    c.profile("Símbolo - cuba", "Plan", rrect(*top[:4], top[4]), A, 0.001, LOUCA)
    c.plan_only("Símbolo - cuba")

    # --- washboard: a ribbed slab sloping from the front rim into the bowl ---
    yf_, yb_ = 0.0, 0.175  # from the opening's front edge
    zt_, zl_ = -0.012, -0.135  # from the rim
    dy, dz = yb_ - yf_, zl_ - zt_
    ln = math.hypot(dy, dz)
    ny, nz = -dz / ln, dy / ln  # the slab's upward normal
    ribs = 11
    top_pts = []
    for k in range(ribs + 1):
        s = k / ribs
        top_pts.append((yf_ + dy * s, zt_ + dz * s))
        if k < ribs:
            sm = (k + 0.5) / ribs
            top_pts.append((yf_ + dy * sm + 0.006 * ny, zt_ + dz * sm + 0.006 * nz))
    th = 0.025
    bottom = [(yb_ - th * ny, zl_ - th * nz), (yf_ + 0.004, zt_ - th / nz)]
    section = [(add(oy0, yy), add(A, zz)) for yy, zz in top_pts + bottom]
    v_low = DEPTH + zl_ - th * nz  # the slab's lowest point, above the floor
    half = f"({p(ox1)} - {p(ox0)}) / 2"
    c.profile("Esfregador", "Side", section, add(f"-{half}", 0.003), f"2 * {half} - 0.006", LOUCA, in_plan=False)
    # Its back wall, down to the floor, following the bowl's walls.
    wall = []
    vs = [v for v, _ in PROFILE if 0 <= v < v_low] + [v_low]
    for v in vs:
        wall.append((f"-{half} + {e(inset_at(v) - 0.002)}", z(v)))
    for v in reversed(vs):
        wall.append((f"{half} - {e(inset_at(v) - 0.002)}", z(v)))
    c.profile("Parede do esfregador", "Front", wall, add(oy0, yb_ - th * ny - 0.012), 0.012, LOUCA)
    sx0, sy0, sx1, _, sr = opening(-0.006)
    c.profile("Símbolo - esfregador", "Plan", [
        (sx0, add(oy0, yb_)), (sx0, add(sy0, sr), sr), (add(sx0, sr), sy0), (add(sx1, f"-{p(sr)}"), sy0, sr), (sx1, add(sy0, sr)), (sx1, add(oy0, yb_)),
    ], A, 0.001, LOUCA)
    c.plan_only("Símbolo - esfregador")

    # --- drain: strainer valve on the floor, tailpiece, bottle trap and arm to the wall ---
    yd = add(y1, -0.15)
    c.rev("Válvula", "Front", [(0, ZF), (0.036, ZF), (0.036, z(0.002)), (0.03, z(0.004)), (0, z(0.004))], yd, 0, "Cromado", in_plan=True)
    for i, r in enumerate((0.009, 0.016, 0.023), 1):
        c.rev(f"Grelha da válvula {i}", "Front", rect(r - 0.0018, z(0.0035), r + 0.0018, z(0.0045)), yd, 0, "Plástico preto", detail=FINE)
    c.cyl("Corpo da válvula", 0, yd, add(zb, -0.035), 0.03, 0.035, "Cromado")
    c.cyl("Porca da válvula", 0, yd, add(zb, -0.03), 0.038, 0.014, "Cromado", FINE)
    zs = 0.45  # the arm to the wall
    c.cyl("Tubo de descida", 0, yd, 0.5, 0.016, f"{p(zb)} - 0.535", "Branco")
    c.cyl("Porca do tubo de descida", 0, yd, add(zb, -0.055), 0.022, 0.02, "Branco", FINE)
    c.rev("Copo do sifão", "Front", [(0, 0.37), (0.026, 0.37, 0.02), (0.038, 0.385), (0.038, 0.48), (0.028, 0.497), (0, 0.497)], yd, 0, "Branco")
    c.cyl("Porca do sifão", 0, yd, 0.49, 0.028, 0.018, "Branco", FINE)
    c.cyl_y("Braço do sifão", 0, zs, yd, 0.02, f"{p(y1)} - {p(yd)}", "Branco")
    c.cyl_y("Porca do braço do sifão", 0, zs, add(yd, 0.035), 0.026, 0.02, "Branco", FINE)
    c.cyl_y("Canopla do esgoto", 0, zs, add(y1, -0.006), 0.04, 0.006, "Branco", FINE)
    c.connector("Esgoto", "Sanitary", 0, y1, zs, "Back", 0.04)
    # Overflow slots high on the back wall.
    for i in range(3):
        c.box(f"Ladrão {i + 1}", add(-0.025, 0.02 * i), add(oy1, -0.004), add(A, -0.075), 0.01, 0.006, 0.022, "Plástico preto", FINE)

    # --- column: open at the back, hiding the trap ---
    Y = y1
    loft(c, "Coluna", [
        (0, u_outline(Y, 0.115, 0.195, 0.016, 0.05)),
        (0.02, u_outline(Y, 0.105, 0.19, 0.016, 0.05)),
        (0.06, u_outline(Y, 0.1, 0.185, 0.016, 0.05)),
        (add(zb, 0.004), u_outline(Y, 0.13, 0.22, 0.016, 0.06)),
    ], LOUCA, in_plan=False)

    # --- wall fixing: bolts through the back rim ---
    for side, x in (("esquerdo", add(x0, 0.09)), ("direito", add(x1, -0.09))):
        c.cyl(f"Parafuso de fixação {side}", x, add(y1, -0.03), add(A, -0.004), 0.006, 0.008, "Aço galvanizado", FINE)
        c.rev(f"Capa do parafuso {side}", "Front", [(x, A), (add(x, 0.012), A), (add(x, 0.011), add(A, 0.006), 0.012), (x, add(A, 0.01))],
              add(y1, -0.03), x, "Branco", detail=FINE)

    # --- wall tap with a hose nozzle ---
    zr = add(A, 0.2)
    c.connector("Água fria", "ColdWater", 0, y1, zr, "Back", 0.02)
    c.cyl_y("Canopla da torneira", 0, zr, add(y1, -0.007), 0.03, 0.007, "Cromado")
    c.rev("Corpo da torneira", "Plan", [(0, add(y1, -0.07)), (0.015, add(y1, -0.07)), (0.017, add(y1, -0.055)), (0.017, add(y1, -0.007)), (0, add(y1, -0.007))],
          zr, 0, "Cromado")
    c.cyl("Castelo da torneira", 0, add(y1, -0.045), zr, 0.013, 0.035, "Cromado")
    c.cyl("Volante da torneira", 0, add(y1, -0.045), add(zr, 0.035), 0.016, 0.012, "Cromado", FINE)
    c.box("Alavanca da torneira", -0.005, add(y1, -0.12), add(zr, 0.04), 0.01, 0.08, 0.008, "Cromado")
    c.cyl_y("Ponta da alavanca", 0, add(zr, 0.044), add(y1, -0.128), 0.007, 0.01, "Cromado", FINE)
    tube(c, "Bica da torneira", "Side", [(add(y1, -0.065), zr), (add(y1, -0.1), zr, 0.03), (add(y1, -0.13), add(zr, -0.03)), (add(y1, -0.13), add(zr, -0.06))],
         0, 0.0105, "Cromado", in_plan=True)
    c.cyl("Bico para mangueira", 0, add(y1, -0.13), add(zr, -0.1), 0.0095, 0.04, "Cromado", FINE)
    for i in range(4):
        c.cyl(f"Rosca do bico {i + 1}", 0, add(y1, -0.13), add(zr, -0.095 + 0.009 * i), 0.011, 0.004, "Cromado", FINE)
    c.cyl("Arejador da torneira", 0, add(y1, -0.13), add(zr, -0.103), 0.008, 0.003, "Plástico cinza", FINE)
    return c
