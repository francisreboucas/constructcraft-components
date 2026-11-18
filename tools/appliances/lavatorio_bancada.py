"""Lavatório com bancada: bancada de granito com saia e rodabanca sobre mãos-francesas, cuba oval de louça de embutir,
misturador monocomando de alavanca, válvula de escoamento com tampão e ladrão, sifão de copo cromado com saída para baixo,
registros de ângulo com flexíveis."""

from _sanitarios import *

T = 0.02  # thickness of the granite
WALL = 0.012  # thickness of the bowl's wall
# The bowl (cuba oval de embutir): its flange on the countertop, its opening and its floor (half sizes).
FX, FY = 0.235, 0.17  # flange
OX, OY = 0.2, 0.135  # opening, inside the flange's lip
BX, BY = 0.085, 0.06  # floor
SKIRT = 0.022  # straight part under the flange
DEPTH = 0.135  # from the skirt to the floor


def build():
    c = Component("Lavatório com bancada", "plumbing", "lavatorio-bancada", "Plumbing")
    L = c.param("Largura", 0.8)
    D = c.param("Profundidade", 0.5)
    A = c.param("Altura", 0.85)
    lever = c.angle("AnguloAlavanca", 0, open_at=25)
    desc = "Cuba de embutir em bancada de granito"
    c.type("Lavatório bancada 80x50", desc, Largura=0.8)
    c.type("Lavatório bancada 100x50", desc, Largura=1.0)
    c.type("Lavatório bancada 120x55", desc, Largura=1.2, Profundidade=0.55)
    c.mep = {"Fixture": {"drain_units": 1, "supply_weight": 0.3, "hot_water": True}}
    c.connector("Esgoto", "Sanitary", 0, V(D) / 2 - 0.1, 0.5, "Down", 0.04)
    c.connector("Água fria", "ColdWater", -0.1, V(D) / 2, 0.6, "Back", 0.02)
    c.connector("Água quente", "HotWater", 0.1, V(D) / 2, 0.6, "Back", 0.02)
    c.material("Granito", (70, 70, 75), "Generic", "Polished")
    c.preview_base = 0.3
    c.preview_size = (0.9, 0.55, 0.65)

    yw = V(D) / 2  # the wall
    yc = yw - T - 0.085 - FY  # the bowl's center: the mixer stands between it and the backsplash
    ym = yw - T - 0.0425  # the mixer
    zb = V(A) - SKIRT - DEPTH  # the bowl's floor

    def z(d):
        return V(A) + d

    # --- coarse stand-in of the bowl ---
    c.profile("Cuba simplificada", "Plan", oval(0, yc, FX - 0.02, FY - 0.02, n=24), zb - WALL, V(A) - zb + WALL - T, "Louça", COARSE)

    # --- countertop, front skirt, backsplash ---
    def oval_c(rx, ry, cy, p=2.2):
        return contour(0, cy, rx, ry, None, p)

    c.box("Bancada simplificada", -V(L) / 2, -V(D) / 2, z(-T), L, D, T, "Granito", COARSE, in_plan=True)
    # The slab in two halves, each with half of the bowl's hole (just outside the bowl's skirt): no void,
    # whose cut faces would coincide with the bowl's.
    hole = oval_c(OX + WALL + 0.001, OY + WALL + 0.001, yc)(spread(270, 90, 28))
    half = [(0, yw), (-V(L) / 2, yw), (-V(L) / 2, -V(D) / 2), (0, -V(D) / 2)] + hole
    c.profile("Bancada – metade esquerda", "Plan", half, z(-T), T, "Granito")
    c.profile("Bancada – metade direita", "Plan", [(-x, y) for x, y in reversed(half)], z(-T), T, "Granito")
    c.profile("Planta – bancada", "Plan", rect(-V(L) / 2, -V(D) / 2, V(L) / 2, yw), A, 0.002, "Granito")
    c.plan_only("Planta – bancada")
    c.box("Saia frontal", -V(L) / 2, -V(D) / 2, z(-T - 0.08), L, T, 0.08, "Granito", ALL)
    c.box("Rodabanca", -V(L) / 2, yw - T, A, L, T, 0.08, "Granito", ALL, in_plan=True)

    # --- the bowl: flange on the stone, straight skirt through it, then the bowl to its floor ---

    flange = [
        (A, oval_c(FX, FY, yc), oval_c(OX, OY, yc)),
        (z(0.005), oval_c(FX - 0.002, FY - 0.002, yc), oval_c(OX + 0.001, OY + 0.001, yc)),
        (z(0.009), oval_c(FX - 0.01, FY - 0.01, yc), oval_c(OX + 0.005, OY + 0.005, yc)),
    ]
    shell_halves(c, "Borda da cuba", flange, "Louça", n=14)
    cyf = yc + 0.01  # the floor sits a little back

    def bowl(phi, grow):
        k, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        return oval_c(BX + (OX - BX) * k + grow, BY + (OY - BY) * k + grow, lerp(yc, cyf, s))

    def zp(phi):
        return z(-SKIRT - DEPTH * math.sin(math.radians(phi)))

    phis = [90, 80, 68, 54, 38, 22, 8, 0]
    body = [(zp(f), bowl(f, WALL), bowl(f, 0)) for f in phis] + [(A, oval_c(OX + WALL, OY + WALL, yc), oval_c(OX, OY, yc))]
    shell_halves(c, "Cuba", body, "Louça", n=14)
    c.profile("Fundo da cuba", "Plan", oval(0, cyf, BX + 0.004, BY + 0.004, n=40), zb - WALL, WALL, "Louça")
    f_l = 14
    y_l = lerp(yc, cyf, math.sin(math.radians(f_l))) - (BY + (OY - BY) * math.cos(math.radians(f_l)))
    c.profile("Ladrão", "Front", oval(0, zp(f_l), 0.013, 0.0045, n=16), y_l - 0.0025, 0.003, "Plástico preto", FINE)

    # --- mixer on the stone, pop-up waste ---
    mixer(c, "do misturador", 0, ym, A, lever, reach=0.14, height=0.13)
    popup_drain(c, "de escoamento", 0, cyf, zb)
    c.cyl("Haste roscada do misturador", 0, ym, z(-T - 0.06), 0.016, 0.06, "Latão", FINE)
    c.cyl("Porca de fixação do misturador", 0, ym, z(-T - 0.014), 0.026, 0.012, "Latão", FINE)
    c.cyl("Arruela do misturador", 0, ym, z(-T - 0.002), 0.03, 0.002, "Borracha", FINE)

    # --- drain: waste body, nut, bottle trap with its outlet turning down ---
    zt = zb - WALL - 0.045  # the trap's tail starts under the waste nut
    c.cyl("Corpo da válvula", 0, cyf, zt, 0.017, zb - WALL - zt, "Cromado")
    c.cyl("Porca da válvula", 0, cyf, zb - WALL - 0.016, 0.03, 0.013, "Cromado", FINE)
    c.cyl("Arruela da válvula", 0, cyf, zb - WALL - 0.003, 0.033, 0.003, "Borracha", FINE)
    bottle_trap(c, 0, cyf, zt, 0.56, yw, outlet_down=0.5, y_down=V(D) / 2 - 0.1)

    # --- supply: angle valves on the wall, braided hoses up to the mixer's tails ---
    for name, x in (("fria", -0.1), ("quente", 0.1)):
        yo, zo = angle_valve_ext(c, "registro", x, yw, 0.6, reach=yw - ym, suffix=name)
        hose(c, f"Flexível {name}", x, zo, 0.007 if x > 0 else -0.007, z(-T - 0.06), ym, radius=0.005)

    # --- two steel brackets (mãos-francesas) under the countertop ---
    arm = V(D) * 0.6
    for side, sx in (("esquerda", -1), ("direita", 1)):
        x0 = (V(L) / 2 - 0.12) * sx - 0.0125
        c.box(f"Mão-francesa {side} – montante", x0, yw - 0.004, z(-T - 0.3), 0.025, 0.004, 0.3, "Aço pintado branco")
        c.box(f"Mão-francesa {side} – braço", x0, yw - arm, z(-T - 0.004), 0.025, arm - 0.004, 0.004, "Aço pintado branco")
        brace = [(yw - 0.004, z(-T - 0.27)), (yw - 0.004, z(-T - 0.24)), (yw - arm + 0.06, z(-T - 0.004)), (yw - arm + 0.03, z(-T - 0.004))]
        c.profile(f"Mão-francesa {side} – diagonal", "Side", brace, x0 + 0.009, 0.007, "Aço pintado branco")
        for i, zz in enumerate((-T - 0.05, -T - 0.25), 1):
            c.cyl_y(f"Parafuso da mão-francesa {side} {i}", x0 + 0.0125, z(zz), yw - 0.007, 0.005, 0.003, "Aço galvanizado", FINE)

    # --- plan symbol of the bowl ---
    c.profile("Planta – borda da cuba", "Plan", oval_c(FX, FY, yc)(spread(90, 450, 48)[:-1]), A, 0.002, "Louça")
    c.profile("Planta – cuba", "Plan", oval_c(OX, OY, yc)(spread(90, 450, 48)[:-1]), A, 0.002, "Louça")
    for name in ("Planta – borda da cuba", "Planta – cuba"):
        c.plan_only(name)
    return c
