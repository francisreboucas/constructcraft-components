"""Bidê de louça de piso: bacia oval rasa sobre pedestal, mesa traseira com misturador monocomando de alavanca,
válvula de escoamento com tampão, registros de ângulo com flexíveis e parafusos de fixação no piso."""

from _sanitarios import *


# (distance outwards from the floor's outline, height below the rim) around the bowl's wall.
INNER = catmull([(0, -0.15), (0.007, -0.135), (0.018, -0.105), (0.03, -0.07), (0.041, -0.038), (0.049, -0.016), (0.055, -0.005),
                 (0.061, -0.001)], 3)
TOP = [(0.064, 0), (0.084, 0), (0.093, -0.003), (0.098, -0.009)]
OUTER = catmull([(0.1, -0.02), (0.099, -0.05), (0.094, -0.09), (0.085, -0.13), (0.072, -0.168), (0.06, -0.195), (0.055, -0.21)], 3)
RIM = 0.1  # the rim's outer edge, out of the floor's outline
MID = 0.075  # the middle of the rim's top, where the back deck starts


def build():
    c = Component("Bidê", "plumbing", "bide", "Plumbing")
    L = c.param("Largura", 0.36)
    D = c.param("Profundidade", 0.53)
    A = c.param("Altura", 0.4)
    lever = c.angle("AnguloAlavanca", 0, open_at=25)
    c.type("Bidê", "Bidê de louça")
    c.type("Bidê compacto", "Bidê de louça de dimensões reduzidas", Largura=0.34, Profundidade=0.49, Altura=0.39)
    c.mep = {"Fixture": {"drain_units": 1, "supply_weight": 0.1, "hot_water": True}}
    c.connector("Esgoto", "Sanitary", 0, V(D) / 2 - 0.2, 0, "Down", 0.04)
    c.connector("Água fria", "ColdWater", -0.1, V(D) / 2, 0.2, "Back", 0.02)
    c.connector("Água quente", "HotWater", 0.1, V(D) / 2, 0.2, "Back", 0.02)

    yw = V(D) / 2  # the wall
    b_out = (V(D) - 0.13) / 2  # half length of the bowl's outline
    cy = -V(D) / 2 + b_out  # the bowl's center
    a0, b0 = V(L) / 2 - RIM, b_out - RIM  # the floor's outline

    def z(d):
        return V(A) + d

    # --- coarse stand-ins (the old pieces) ---
    c.box("Pé simplificado", -0.11, -V(D) / 2 + 0.12, 0, 0.22, V(D) - 0.2, 0.2, "Louça", COARSE)
    c.cyl("Bacia simplificada", 0, -V(D) / 2 + V(L) / 2, 0.2, V(L) / 2, V(A) - 0.2, "Louça", COARSE, in_plan=True)
    c.box("Corpo simplificado", -V(L) / 2, -V(D) / 2 + V(L) / 2, 0.2, L, V(D) - V(L) / 2 - 0.01, V(A) - 0.2, "Louça", COARSE, in_plan=True)

    # --- the bowl: its wall carried around the floor, hollow by construction; the floor ---
    section = [(0, -0.21)] + INNER + TOP + OUTER
    ring(c, "Bacia", 0, cy, a0, b0, A, section, "Louça")
    c.profile("Fundo da bacia", "Plan", oval(0, cy, a0 + 0.003, b0 + 0.003, n=40), z(-0.21), 0.061, "Louça")

    # --- the deck at the back, flush with the rim; its edge towards the bowl runs inside the rim ---
    ta = 12.0  # where the deck leaves the rim's outline (degrees from the side)
    arc_mid = soval(0, cy, a0 + MID, b0 + MID, [180 - ta + (2 * ta - 180) * i / 16 for i in range(17)])  # left to right by the back

    def deck(inset, back_inset=0.0):
        right_out = soval(0, cy, V(L) / 2 - inset, b_out - inset, [ta])[0]
        left_out = soval(0, cy, V(L) / 2 - inset, b_out - inset, [180 - ta])[0]
        xb, yb_ = V(L) / 2 - 0.05 - inset, yw - 0.012 - back_inset
        rc = 0.035
        corner_r = arc(xb - rc, yb_ - rc, rc, 0, 90, n=4)
        corner_l = arc(-xb + rc, yb_ - rc, rc, 90, 180, n=4)
        return [arc_mid[-1], right_out] + corner_r + corner_l + [left_out] + arc_mid[:-1]

    loft_x(c, "Mesa traseira", [(z(-0.06), deck(0.012, 0.004)), (z(-0.008), deck(0)), (z(0), deck(0.005, 0.004))], "Louça")

    # --- plan symbol: the outline (bowl and deck) and the bowl's opening ---
    outline = deck(0)[1:-len(arc_mid) + 1][:-1] + soval(0, cy, V(L) / 2, b_out, spread(180 - ta, 360 + ta, 40))[:-1]
    c.profile("Planta – contorno", "Plan", outline, A, 0.002, "Louça")
    c.profile("Planta – bacia", "Plan", oval(0, cy, a0 + 0.062, b0 + 0.062, n=48), A, 0.002, "Louça")
    for name in ("Planta – contorno", "Planta – bacia"):
        c.plan_only(name)

    # --- pedestal and the body under the deck ---
    def ped(rx, front, back, power=2.6):
        y0, y1 = cy - b0 + front, yw - back
        return oval(0, (y0 + y1) / 2, rx, (y1 - y0) / 2, n=40, power=power)

    loft_x(c, "Pedestal", [
        (0, ped(0.118, -0.02, 0.09)),
        (0.012, ped(0.118, -0.02, 0.09)),
        (0.045, ped(0.104, 0.0, 0.1)),
        (0.12, ped(0.1, 0.0, 0.1, 2.6)),
        (z(-0.205), ped(0.13, -0.052, 0.09, 2.2)),
    ], "Louça")
    yr0 = cy + b0 + 0.045
    loft_x(c, "Corpo traseiro", [
        (z(-0.215), oval(0, (yr0 + yw - 0.09) / 2, 0.128, (yw - 0.09 - yr0) / 2, n=40, power=3)),
        (z(-0.055), oval(0, (yr0 + yw - 0.09) / 2, V(L) / 2 - 0.045, (yw - 0.09 - yr0) / 2, n=40, power=3)),
    ], "Louça")

    # --- floor bolts ---
    yb_bolt = cy + 0.07
    for side, x in (("esquerdo", -0.122), ("direito", 0.122)):
        c.cyl(f"Orelha de fixação {side}", x, yb_bolt, 0, 0.024, 0.012, "Louça")
        c.rev(f"Capa do parafuso {side}", "Front", [(x, 0.012), (V(x) + 0.013, 0.012), (V(x) + 0.012, 0.02, 0.012), (x, 0.026)],
              yb_bolt, x, "Branco", detail=FINE)

    # --- mixer on the deck, pop-up waste in the floor and its lift rod ---
    ym = cy + b0 + 0.062 + 0.062  # behind the opening
    mixer(c, "do misturador", 0, ym, A, lever, reach=0.1, height=0.088)
    popup_drain(c, "de escoamento", 0, cy - 0.02, z(-0.149))
    c.cyl("Haste do tampão", 0, ym + 0.042, z(-0.01), 0.0035, 0.045, "Cromado", FINE)
    c.rev("Puxador do tampão", "Front", [(0, z(0.033)), (0.006, z(0.033)), (0.008, z(0.04), 0.008), (0.006, z(0.047)), (0, z(0.048))],
          ym + 0.042, 0, "Cromado", detail=FINE)
    c.cyl("Canopla da haste", 0, ym + 0.042, A, 0.009, 0.003, "Cromado", FINE)

    # --- supply: angle valves on the wall, braided hoses up into the deck ---
    for name, x in (("fria", -0.1), ("quente", 0.1)):
        yo, zo = angle_valve_ext(c, "registro", x, yw, 0.2, suffix=name)
        hose(c, f"Flexível {name}", x, zo, 0.012 if x > 0 else -0.012, z(-0.055), yo)
        c.cyl(f"Porca do flexível {name}", 0.012 if x > 0 else -0.012, yo, z(-0.075), 0.0085, 0.02, "Cromado", FINE)
    return c
