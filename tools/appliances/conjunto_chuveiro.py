"""Conjunto de chuveiro: a wall single-lever shower mixer, a wall arm with a round rain head, and a hand shower on a slide
bar fed by a hose from the mixer's outlet. The wall is y = 0, the pieces stand out towards -Y."""

from _sanitarios import *


def wall_rose(c, name, x, z, r=0.025, depth=0.01, detail=FULL):
    c.rev(name, "Plan", [(x, -depth), (add(x, r - 0.004), -depth, 0.004), (add(x, r), -depth + 0.004), (add(x, r), 0), (x, 0)], z, x, "Cromado",
          detail=detail)


def build():
    c = Component("Conjunto de chuveiro", "plumbing", "conjunto-chuveiro", "Plumbing")
    H = c.param("AlturaChuveiro", 2.2)
    R = c.param("AlturaRegistro", 1.1)
    B = c.param("Braco", 0.4)
    D = c.param("DiametroDucha", 0.25)
    desc = ("Conjunto de chuveiro de parede: misturador monocomando de embutir com desviador, braço de parede com ducha de teto "
            "redonda e ducha manual em barra deslizante com flexível, metais cromados; para aquecimento a gás ou solar")
    c.type("Conjunto de chuveiro ducha Ø25", desc)
    c.type("Conjunto de chuveiro ducha Ø30", desc, DiametroDucha=0.3, Braco=0.45)
    c.mep = {"Fixture": {"drain_units": 2, "supply_weight": 0.4, "hot_water": True}}
    c.connector("Água fria", "ColdWater", -0.05, 0, R, "Back", 0.02)
    c.connector("Água quente", "HotWater", 0.05, 0, R, "Back", 0.02)
    c.preview_size = (0.7, 0.6, 2.3)

    def h(d):
        return add(H, d)

    def r_(d):
        return add(R, d)

    c.box("Chuveiro simplificado", -0.13, f"-{B} - 0.13", h(-0.01), 0.26, f"{B} + 0.13", 0.03, "Cromado", detail=COARSE, in_plan=True)
    c.box("Registro simplificado", -0.08, -0.06, r_(-0.08), 0.16, 0.06, 0.16, "Cromado", detail=COARSE)

    # --- mixer: a round escutcheon, the cartridge body, the lever and the diverter knob ---
    wall_rose(c, "Espelho do misturador", 0, R, r=0.08, depth=0.008)
    c.cyl_y("Corpo do misturador", 0, R, -0.05, 0.026, 0.042, "Cromado")
    c.box("Alavanca do misturador", -0.009, -0.078, r_(-0.1), 0.018, 0.028, 0.11, "Cromado")
    c.cyl_y("Cubo da alavanca", 0, R, -0.078, 0.02, 0.03, "Cromado")
    c.cyl_y("Desviador", 0, r_(0.12), -0.03, 0.016, 0.03, "Cromado", FINE)
    wall_rose(c, "Espelho do desviador", 0, r_(0.12), r=0.028, depth=0.006, detail=FINE)
    c.box("Indicador quente/frio", -0.03, -0.0085, r_(0.05), 0.06, 0.001, 0.004, "Plástico vermelho", FINE)

    # --- the wall arm and the rain head ---
    za = h(0.09)  # height of the arm
    wall_rose(c, "Canopla do braço", 0, za, r=0.03, depth=0.012)
    c.cyl_y("Braço", 0, za, f"-{B}", 0.011, f"{B} - 0.012", "Cromado")
    c.cyl("Descida do braço", 0, f"-{B}", h(0.03), 0.011, 0.06, "Cromado")
    c.rev("Articulação", "Front", [(0, h(0.015)), (0.016, h(0.015)), (0.018, h(0.03), 0.02), (0.012, h(0.04)), (0, h(0.04))], f"-{B}", 0,
          "Cromado", detail=FINE)
    c.rev("Ducha de teto", "Front", [(0, h(0.0)), (f"{D}/2 - 0.004", h(0.0)), (f"{D}/2", h(0.004)), (f"{D}/2", h(0.008)),
                                     (f"{D}/2 - 0.03", h(0.016)), (0, h(0.018))], f"-{B}", 0, "Cromado", in_plan=True)
    c.cyl("Placa de jatos", 0, f"-{B}", h(-0.001), f"{D}/2 - 0.015", 0.001, "Borracha cinza", FINE)

    # --- hand shower on a slide bar at the right ---
    xb = 0.32
    zb0, zb1 = r_(-0.05), r_(0.75)
    for name, zz in (("inferior", zb0), ("superior", zb1)):
        wall_rose(c, f"Suporte {name} da barra", xb, zz, r=0.02, depth=0.01, detail=FULL)
        c.cyl_y(f"Braço {name} da barra", xb, zz, -0.045, 0.008, 0.035, "Cromado")
    c.cyl("Barra deslizante", xb, -0.045, zb0, 0.0125, f"{zb1} - ({zb0})", "Cromado")
    zs = r_(0.55)
    c.box("Cursor da barra", xb - 0.02, -0.065, zs, 0.04, 0.04, 0.05, "Cromado")
    # Handle tilted forward, its head facing down and forward.
    c.cyl("Cabo da ducha manual", xb, -0.09, r_(0.38), 0.014, 0.2, "Cromado")
    c.cyl_y("Ducha manual", xb, r_(0.62), -0.115, 0.055, 0.03, "Cromado")
    c.cyl_y("Face da ducha manual", xb, r_(0.62), -0.117, 0.045, 0.002, "Borracha cinza", FINE)
    # Wall outlet (saída de água) beside the mixer and the hose sagging to the handle.
    xo = 0.12
    wall_rose(c, "Saída de água", xo, r_(-0.02), r=0.025, depth=0.03)
    path = [(x, r_(dz)) for x, dz in smooth([(xo, -0.03), (0.15, -0.3), (0.22, -0.42), (0.29, -0.33), (xb - 0.004, -0.05)], 4)]
    path.append((xb, r_(0.38)))
    tube(c, "Flexível", "Front", path, -0.07, 0.008, "Inox escovado", FINE, n=10)
    return c
