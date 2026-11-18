"""Gabinete de banheiro com cuba: móvel de duas portas sobre pés, tampo de louça com cuba integrada, misturador,
válvula click, sifão, registros de ângulo e flexíveis, e o que se guarda dentro."""

from _banheiro import *
from louca import ring, oval, smooth, tube, mixer, popup_drain, angle_valve

MDF, LOUCA, ALU, CHROME = "MDF branco", "Louça", "Alumínio anodizado", "Cromado"

# The bowl's wall: (distance outwards from the floor's outline, height from the top), inner face, top, outer face.
INNER = smooth([(0, -0.15), (0.012, -0.136), (0.03, -0.1), (0.045, -0.055), (0.055, -0.02), (0.06, -0.005), (0.062, 0)], 3)
OUTER = [(0.078, 0), (0.078, -0.016), (0.072, -0.05), (0.058, -0.1), (0.038, -0.14), (0.014, -0.162), (0, -0.165)]
HOLE = 0.07  # the deck's opening, out of the floor's outline: inside the wall's top
B0 = 0.1  # the floor's half depth
POWER = 2.5  # a rounded rectangle


def build():
    c = Component("Gabinete de banheiro com cuba", "plumbing", "gabinete-banheiro", "Plumbing")
    W = c.param("Largura", 0.6)
    P = c.param("Profundidade", 0.46)
    A = c.param("Altura", 0.85)
    G = c.angle("AnguloPortas", 0, open_at=95)
    L = c.angle("AnguloAlavanca", 0, open_at=25)
    c.material(MDF, (240, 240, 235), "Wood", "Satin")
    c.material("Papel", (238, 232, 214), "Generic", "Matte")
    desc = "Gabinete de banheiro de duas portas sobre pés, com tampo de louça e cuba integrada"
    c.type("Gabinete com cuba 60 cm", desc, Largura=0.6)
    c.type("Gabinete com cuba 80 cm", desc, Largura=0.8)
    c.mep = {"Fixture": {"drain_units": 1, "supply_weight": 0.3, "hot_water": True}}
    yw = f"({P}/2)"  # the wall
    c.connector("Esgoto", "Sanitary", 0, yw, 0.5, "Back", 0.04)
    c.connector("Água fria", "ColdWater", -0.1, yw, 0.6, "Back", 0.02)
    c.connector("Água quente", "HotWater", 0.1, yw, 0.6, "Back", 0.02)

    T, TD = 0.018, 0.018
    xL, xR = f"(-{W}/2)", f"({W}/2)"
    yF = f"(-{P}/2)"
    yD = f"({yF} + {TD})"  # back face of the doors
    yC = f"({yD} + 0.002)"  # front edge of the carcass
    zP = 0.15  # top of the feet, bottom of the carcass
    zS = f"({A} - 0.03)"  # under the top's apron: top of the carcass
    a0 = f"(0.25*{W} + 0.012)"  # the bowl floor's half width
    cy = -0.02  # the bowl's center
    zf = f"({A} - 0.15)"  # the bowl's floor

    def z(dz):
        return add(A, dz)

    # --- coarse stand-ins ---
    c.box("Gabinete simplificado", xL, yF, 0, W, P, zS, MDF, COARSE, in_plan=True)
    c.box("Tampo simplificado", f"{xL} - 0.003", f"{yF} - 0.008", zS, f"{W} + 0.006", f"{P} + 0.008", 0.03, LOUCA, COARSE, in_plan=True)

    # --- the top: a deck round an opening, the bowl's wall swept round its floor, aprons ---
    xs0, xs1, ys0, ys1, rc = f"({xL} - 0.003)", f"({xR} + 0.003)", f"({yF} - 0.008)", yw, 0.02
    hole_l = oval(0, cy, add(a0, HOLE), B0 + HOLE, n=24, power=POWER, start=270, turn=-180)
    hole_r = oval(0, cy, add(a0, HOLE), B0 + HOLE, n=24, power=POWER, start=90, turn=-180)
    corner_l = [(add(xs0, rc * (1 - k1)), add(ys0, rc * (1 - k2))) for k1, k2 in ((1, 0), (0.866, 0.5), (0.5, 0.866), (0, 1))]
    corner_r = [(add(xs1, -rc * (1 - k1)), add(ys0, rc * (1 - k2))) for k1, k2 in ((0, 1), (0.5, 0.866), (0.866, 0.5), (1, 0))]
    c.extrusion("Tampo - lado esquerdo", [(0, ys1), (xs0, ys1)] + corner_l + [(0, ys0)] + hole_l, z(-0.015), 0.015, LOUCA)
    c.extrusion("Tampo - lado direito", [(0, ys0)] + corner_r + [(xs1, ys1), (0, ys1)] + hole_r, z(-0.015), 0.015, LOUCA)
    # the deck is two pieces meeting at x = 0: plans draw its outline instead, without the seam
    c.profile("Contorno do tampo", "Plan", [(xs1, ys1), (xs0, ys1), (xs0, f"{ys0} + {rc}", rc), (f"{xs0} + {rc}", ys0),
                                            (f"{xs1} - {rc}", ys0, rc), (xs1, f"{ys0} + {rc}")], z(-0.015), 0.015, LOUCA)
    c.plan_only("Contorno do tampo")
    c.profile("Testeira do tampo", "Side", [(f"{ys0} + 0.025", z(-0.03)), (f"{ys0} + 0.025", z(-0.014)), (f"{ys0} + 0.004", z(-0.014)),
                                            (ys0, z(-0.018)), (ys0, z(-0.026)), (f"{ys0} + 0.004", z(-0.03))], f"{xs0} + 0.004", f"{W} - 0.002", LOUCA)
    for nm, x0 in (("esquerda", xs0), ("direita", f"{xs1} - 0.012")):
        c.box(f"Aba lateral {nm} do tampo", x0, f"{ys0} + 0.02", z(-0.03), 0.012, f"{P} - 0.012", 0.016, LOUCA)
    section = INNER + OUTER
    ring(c, "Cuba", 0, cy, a0, B0, A, section, LOUCA, n=64, in_plan=True, power=POWER)
    c.profile("Fundo da cuba", "Plan", oval(0, cy, add(a0, 0.003), B0 + 0.003, n=40, power=POWER), z(-0.165), 0.015, LOUCA)
    c.box("Ladrão da cuba", -0.02, f"{cy} - {B0} - 0.048", z(-0.05), 0.04, 0.006, 0.01, "Plástico cinza", FINE)
    popup_drain(c, "da cuba", 0, cy, zf)
    c.box("Silicone de vedação do tampo", f"{xL} + 0.004", f"{yw} - 0.004", z(0), f"{W} - 0.008", 0.004, 0.003, "Borracha cinza", FINE)

    # --- the mixer on the deck behind the bowl, its shank under the deck ---
    ym = f"({yw} - 0.045)"
    mixer(c, "do misturador", 0, ym, A, L, reach=0.115, height=0.105)
    c.cyl("Haste roscada do misturador", 0, ym, z(-0.07), 0.017, 0.055, "Latão", FINE)
    c.cyl("Porca de fixação do misturador", 0, ym, z(-0.042), 0.026, 0.012, "Latão", FINE)
    c.cyl("Arruela do misturador", 0, ym, z(-0.03), 0.028, 0.004, "Borracha", FINE)
    for nm, s in (("indicador frio", -1), ("indicador quente", 1)):
        c.box(f"Misturador - {nm}", 0.012 * s - 0.002, f"{ym} - 0.0215", z(0.088), 0.004, 0.001, 0.004, "Plástico azul" if s < 0 else "Plástico vermelho", FINE)

    # --- waste: valve body, tailpiece, bottle trap, arm into the wall ---
    c.cyl("Corpo da válvula", 0, cy, z(-0.215), 0.02, 0.052, CHROME)
    c.cyl("Porca da válvula", 0, cy, z(-0.19), 0.029, 0.012, CHROME, FINE)
    c.cyl("Tubo de descida", 0, cy, 0.56, 0.016, f"{A} - 0.215 - 0.56", CHROME)
    c.cyl("Porca de descida", 0, cy, 0.545, 0.024, 0.02, CHROME, FINE)
    c.rev("Copo do sifão", "Front", [(0, 0.43), (0.028, 0.43, 0.02), (0.04, 0.445), (0.04, 0.53), (0.028, 0.545), (0, 0.545)], cy, 0, CHROME)
    c.rev("Tampa de limpeza do sifão", "Front", [(0, 0.418), (0.02, 0.418), (0.02, 0.432), (0, 0.432)], cy, 0, CHROME, detail=FINE)
    c.cyl_y("Braço do sifão", 0, 0.5, cy, 0.016, f"{yw} - {cy} - 0.01", CHROME)
    c.cyl_y("Porca do braço do sifão", 0, 0.5, cy + 0.035, 0.023, 0.02, CHROME, FINE)
    c.rev("Canopla do esgoto", "Plan", [(0, f"{yw} - 0.012"), (0.03, f"{yw} - 0.008", 0.03), (0.032, yw), (0, yw)], 0.5, 0, CHROME)

    # --- angle valves on the wall, braided hoses up to the mixer ---
    for nm, s in (("frio", -1), ("quente", 1)):
        xv = 0.1 * s
        yo, zo = angle_valve(c, "registro", xv, yw, 0.6, suffix=nm)
        xt, r = 0.008 * s, 0.046
        tube(c, f"Flexível {nm}", "Front", [
            (xv, zo), (xv, 0.655, r * s), (xv - r * s, 0.655 + r, -r * s), (xt, 0.655 + 2 * r), (xt, z(-0.085)),
        ], yo, 0.0055, "Inox escovado", n=10)
        c.cyl(f"Porca superior do flexível {nm}", xt, yo, z(-0.098), 0.0085, 0.016, CHROME, FINE)

    # --- carcass on four feet: open at the back for the plumbing ---
    hs = f"({zS} - {zP})"
    c.box("Lateral esquerda", xL, yC, zP, T, f"{yw} - {yC}", hs, MDF, in_plan=True)
    c.box("Lateral direita", f"{xR} - {T}", yC, zP, T, f"{yw} - {yC}", hs, MDF, in_plan=True)
    c.box("Base", f"{xL} + {T}", yC, zP, f"{W} - 2*{T}", f"{yw} - {yC}", T, MDF)
    c.box("Travessa superior frontal", f"{xL} + {T}", yC, f"{zS} - {T}", f"{W} - 2*{T}", 0.08, T, MDF)
    c.box("Travessa traseira de fixação", f"{xL} + {T}", f"{yw} - {T}", f"{zS} - 0.1", f"{W} - 2*{T}", T, 0.1, MDF)
    c.box("Travessa traseira inferior", f"{xL} + {T}", f"{yw} - {T}", f"{zP} + {T}", f"{W} - 2*{T}", T, 0.08, MDF)
    c.box("Fita de borda da base", f"{xL} + {T}", f"{yC} - 0.0005", zP, f"{W} - 2*{T}", 0.0005, T, "Laminado branco", FINE)
    for i, x in enumerate((f"{xL} + {T} + 0.06", f"{xR} - {T} - 0.06"), 1):
        c.cyl_y(f"Parafuso de fixação na parede {i}", x, f"{zS} - 0.07", f"{yw} - {T} - 0.002", 0.0045, 0.002, "Aço galvanizado", FINE)
    for nm, x, y in (("frontal esquerdo", f"{xL} + 0.04", f"{yF} + 0.06"), ("frontal direito", f"{xR} - 0.04", f"{yF} + 0.06"),
                     ("traseiro esquerdo", f"{xL} + 0.04", f"{yw} - 0.05"), ("traseiro direito", f"{xR} - 0.04", f"{yw} - 0.05")):
        c.rev(f"Pé {nm}", "Front", [(x, 0.008), (add(x, 0.012), 0.008), (add(x, 0.016), zP - 0.004), (x, zP - 0.004)], y, x, ALU, in_plan=False)
        c.cyl(f"Sapata do pé {nm}", x, y, 0, 0.013, 0.008, "Plástico preto", FINE)
        c.cyl(f"Base de fixação do pé {nm}", x, y, zP - 0.004, 0.022, 0.004, ALU, FINE)

    # --- two doors ---
    wd = f"({W}/2 - 0.0015)"
    zd, hd = f"{zP} + 0.002", f"({zS} - {zP} - 0.004)"
    for i, side, hx, xi in ((1, "left", f"({xL} + 0.0015)", f"({xL} + {T})"), (2, "right", f"({xR} - 0.0015)", f"({xR} - {T})")):
        c.door_box(f"Porta {i}", (hx, yD), G, 0, wd, 0, TD, zd, hd, MDF, side=side, in_plan=True)
        g = Grp(c)
        hinge(g, f"Dobradiça superior da porta {i}", side, hx, yD, xi, f"{zS} - 0.09", G)
        hinge(g, f"Dobradiça inferior da porta {i}", side, hx, yD, xi, f"{zP} + 0.1", G)
        pull(g, f"Puxador da porta {i}", side, hx, yD, f"{wd} - 0.035", f"{zS} - 0.13", 0.16, G)
        g.door_box(f"Batente da porta {i}", (hx, yD), G, f"{wd} - 0.03", f"{wd} - 0.022", -0.002, 0, f"{zP} + {T} + 0.005", 0.008, "Plástico translúcido", side=side, detail=FINE)

    # --- what is kept inside: toilet paper and cleaning bottles, clear of the trap and the hoses ---
    zi = f"({zP} + {T})"
    xr = f"({xL} + {T} + 0.075)"
    for k in range(2):
        z0 = f"{zi} + {k * 0.101}"
        c.cyl(f"Rolo de papel higiênico {k + 1}", xr, f"{yF} + 0.12", z0, 0.055, 0.1, "Papel", FINE)
        c.cyl(f"Tubo do rolo {k + 1}", xr, f"{yF} + 0.12", f"{z0} + 0.0005", 0.022, 0.1, "Madeira clara", FINE)
    c.cyl("Rolo de papel higiênico 3", f"{xr} + 0.002", f"{yF} + 0.235", zi, 0.055, 0.1, "Papel", FINE)
    xb = f"({xR} - {T} - 0.06)"
    for j, (dy, r, h, mat) in enumerate(((0.1, 0.035, 0.22, "Plástico azul"), (0.2, 0.04, 0.17, "Branco")), 1):
        c.rev(f"Frasco de limpeza {j}", "Front", [(xb, zi), (add(xb, r), zi), (add(xb, r), f"{zi} + {h * 0.8:.3f}"), (add(xb, r * 0.4), f"{zi} + {h:.3f}"), (xb, f"{zi} + {h:.3f}")],
              f"{yF} + {dy}", xb, mat, detail=FINE)
        c.cyl(f"Tampa do frasco de limpeza {j}", xb, f"{yF} + {dy}", f"{zi} + {h:.3f}", r * 0.45, 0.03, "Plástico vermelho" if j == 1 else "Plástico verde", FINE)
    return c
