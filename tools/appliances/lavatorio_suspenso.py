"""Lavatório suspenso de louça: cuba oval com mesa traseira, espelho de fixação com parafusos, misturador monocomando de alavanca,
válvula de escoamento com tampão e ladrão, sifão de copo cromado, registros de ângulo com flexíveis e semicoluna opcional."""

from _sanitarios import *

LIP = 0.005  # the rounded lip of the bowl
DEPTH = 0.13  # from under the lip to the bowl's floor
# Outer outline drawn in below the rim (the apron curving under): (depth below the rim, inset of the sides and the front).
APRON = [(0.0, 0.004), (-LIP, 0.0), (-0.06, 0.0), (-0.09, 0.008), (-0.11, 0.02), (-0.125, 0.033), (-LIP - DEPTH, 0.048)]


def inset_at(dz):
    for (z0, s0), (z1, s1) in zip(APRON, APRON[1:]):
        if z1 <= dz <= z0:
            return s0 + (s1 - s0) * (dz - z0) / (z1 - z0)
    return APRON[-1][1]


def build():
    c = Component("Lavatório suspenso", "plumbing", "lavatorio-suspenso", "Plumbing")
    L = c.param("Largura", 0.45)
    D = c.param("Profundidade", 0.35)
    A = c.param("Altura", 0.82)
    S = c.param("Semicoluna", 0, "Number")  # 1: with the half pedestal that hides the trap
    lever = c.angle("AnguloAlavanca", 0, open_at=25)
    c.type("Lavatório suspenso 45 cm", "Lavatório de louça fixado na parede")
    c.type("Lavatório suspenso 55 cm", "Lavatório de louça fixado na parede", Largura=0.55, Profundidade=0.42)
    c.type("Lavatório suspenso c/ semicoluna 45 cm", "Lavatório de louça fixado na parede, com semicoluna que esconde o sifão", Semicoluna=1)
    c.mep = {"Fixture": {"drain_units": 1, "supply_weight": 0.3, "hot_water": True}}
    c.connector("Esgoto", "Sanitary", 0, V(D) / 2, 0.55, "Back", 0.04)
    c.connector("Água fria", "ColdWater", -0.1, V(D) / 2, 0.6, "Back", 0.02)
    c.connector("Água quente", "HotWater", 0.1, V(D) / 2, 0.6, "Back", 0.02)
    c.preview_base = 0.3
    c.preview_size = (0.5, 0.4, 0.62)

    yw = V(D) / 2  # the wall

    def z(d):
        return V(A) + d

    # --- outlines: the body (straight back on the wall) and the bowl's cavity, from its rim to its floor ---
    cy_o = yw - 0.1

    def outer(s):
        return contour(0, cy_o, V(L) / 2 - s, V(D) - 0.1 - s, 0.1, 2.3, 6)

    cy_i = (yw - 0.1 - V(D) / 2 + 0.035) / 2
    rx_i, ry_i = V(L) / 2 - 0.045, (V(D) - 0.135) / 2
    rx_f, ry_f, cy_f = rx_i * 0.45, ry_i * 0.5, cy_i + 0.008

    def cavity(phi, grow=0.0):
        k, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        return contour(0, lerp(cy_i, cy_f, s), rx_f + (rx_i - rx_f) * k + grow, ry_f + (ry_i - ry_f) * k + grow, None, 2.2)

    def dz_of(phi):
        return -LIP - DEPTH * math.sin(math.radians(phi))

    # --- coarse stand-ins (the old body, the half pedestal) ---
    ring_a = spread(90, 450, 24)[:-1]
    loft_x(c, "Corpo simplificado", [(z(-0.15), outer(0.03)(ring_a)), (A, outer(0)(ring_a))], "Louça", COARSE, in_plan=True)

    # --- the basin: two lofted halves between the body's outline and the bowl's cavity ---
    phis = [90, 82, 72, 60, 46, 31, 16, 0]
    levels = [(z(dz_of(f)), outer(inset_at(dz_of(f))), cavity(f)) for f in phis] + [(A, outer(inset_at(0.0)), cavity(0, 0.004))]
    shell_halves(c, "Lavatório", levels, "Louça", n=14)
    zf = z(-LIP - DEPTH)  # the bowl's floor
    c.profile("Fundo da cuba", "Plan", oval(0, cy_f, rx_f + 0.004, ry_f + 0.004, n=40), zf - 0.015, 0.015, "Louça")
    # The overflow, in the front of the bowl just under the rim.
    f_l = 14
    y_l = lerp(cy_i, cy_f, math.sin(math.radians(f_l))) - (ry_f + (ry_i - ry_f) * math.cos(math.radians(f_l)))
    c.profile("Ladrão", "Front", oval(0, z(dz_of(f_l)), 0.013, 0.0045, n=16), y_l - 0.0025, 0.003, "Plástico preto", FINE)

    # --- back plate on the wall, below the basin, with its two fixing bolts ---
    xa, xb, xc, xd = V(L) / 2 - 0.03, V(L) / 2 - 0.036, V(L) / 2 - 0.062, V(L) / 2 - 0.095
    plate = [(xa, z(-0.02)), (xb, z(-0.125)), (xc, z(-0.172)), (xd, z(-0.19))]
    c.profile("Espelho de fixação", "Front", plate + [(-x, zz) for x, zz in reversed(plate)], yw - 0.025, 0.025, "Louça")
    for side, sx in (("esquerdo", -1), ("direito", 1)):
        x = (V(L) / 2 - 0.088) * sx
        c.cyl_y(f"Arruela do parafuso {side}", x, z(-0.162), yw - 0.027, 0.014, 0.002, "Plástico cinza claro", FINE)
        c.rev(f"Capa do parafuso {side}", "Plan", [(x, yw - 0.027), (x + 0.0105, yw - 0.027), (x + 0.0105, yw - 0.033, 0.008), (x, yw - 0.038)],
              z(-0.162), x, "Cromado", detail=FINE)

    # --- mixer on the deck, pop-up waste ---
    mixer(c, "do misturador", 0, yw - 0.055, A, lever, reach=0.11, height=0.1)
    popup_drain(c, "de escoamento", 0, cy_f, zf)

    # --- drain under the bowl: waste body, nut, bottle trap to the wall ---
    c.cyl("Corpo da válvula", 0, cy_f, z(-0.19), 0.017, zf - 0.015 - z(-0.19), "Cromado")
    c.cyl("Porca da válvula", 0, cy_f, zf - 0.03, 0.03, 0.013, "Cromado", FINE)
    c.cyl("Arruela da válvula", 0, cy_f, zf - 0.017, 0.033, 0.002, "Borracha", FINE)
    bottle_trap(c, 0, cy_f, z(-0.19), 0.55, yw)

    # --- supply: angle valves on the wall, braided hoses up into the deck ---
    for name, x in (("fria", -0.1), ("quente", 0.1)):
        yo, zo = angle_valve_ext(c, "registro", x, yw, 0.6, suffix=name)
        xe = 0.012 if x > 0 else -0.012
        hose(c, f"Flexível {name}", x, zo, xe, z(-0.137), yo)
        c.cyl(f"Porca do flexível {name}", xe, yo, z(-0.157), 0.0085, 0.02, "Cromado", FINE)

    # --- half pedestal (semicoluna): shrinks into the deck when the type has none ---
    k = f"max(0.005, {S})"
    g = scaled(k, (0, yw - 0.05, z(-0.07)))
    wt, dt = V(L) * 0.3, V(D) * 0.6 + 0.075

    def col(wf, df, n=24):
        pts = contour(0, yw - 0.03, wt * wf, dt * df - 0.03, 0.028, 2.4, 8)(spread(90, 450, n)[:-1])
        return g.plan(pts)

    secs = [(z(-0.46), col(0.78, 0.82)), (z(-0.448), col(0.82, 0.86)), (z(-0.3), col(0.9, 0.93)), (z(-0.18), col(0.97, 0.98)),
            (z(-0.136), col(1.0, 1.0))]
    for i in range(len(secs) - 1):
        (z0, a), (z1, b) = secs[i], secs[i + 1]
        blend(c, f"Semicoluna {i + 1}", "Plan", a, b, g.z(z0), g.l(V(z1) - V(z0)), "Louça")
    (z0, a), (z1, b) = secs[0], secs[-1]
    blend(c, "Semicoluna simplificada", "Plan", col(0.8, 0.84, 12), col(1.0, 1.0, 12), g.z(z0), g.l(V(z1) - V(z0)), "Louça", COARSE)

    # --- plan symbol ---
    c.profile("Planta – contorno", "Plan", outer(0)(ring_a), A, 0.002, "Louça")
    c.profile("Planta – cuba", "Plan", cavity(0)(spread(90, 450, 32)[:-1]), A, 0.002, "Louça")
    for name in ("Planta – contorno", "Planta – cuba"):
        c.plan_only(name)
    return c
