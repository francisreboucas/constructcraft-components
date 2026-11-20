"""Misturador gourmet de cozinha: a single-lever kitchen mixer with a tall arched spout and a pull-out spray head.

It stands on a countertop: the origin is the mixer's axis on the stone, the instance parameter Elevacao the height of
the countertop. The spout points to -Y (the sink in front of the wall).
"""

from _sanitarios import *


def build():
    c = Component("Misturador gourmet de cozinha", "plumbing", "misturador-cozinha", "Plumbing")
    E = c.param("Elevacao", 0.9, "Length", True)
    c.type("Misturador gourmet bica alta", "Misturador monocomando de cozinha, de mesa, com bica alta em arco e ducha "
           "extraível de dois jatos, latão cromado; Elevacao é a altura da bancada")
    c.mep = {"Fixture": {"drain_units": 0, "supply_weight": 0.7, "hot_water": True}}
    c.connector("Água fria", "ColdWater", -0.01, 0, add(E, -0.3), "Down", 0.0125)
    c.connector("Água quente", "HotWater", 0.01, 0, add(E, -0.3), "Down", 0.0125)
    c.preview_size = (0.25, 0.3, 1.4)

    def z(d):
        return add(E, d)

    c.cyl("Misturador simplificado", 0, 0, E, 0.03, 0.45, "Cromado", detail=COARSE, in_plan=True)

    # Body: base, a column with the lever, the swivel ring.
    c.rev("Base", "Front", [(0, E), (0.032, E), (0.032, z(0.004)), (0.028, z(0.012)), (0, z(0.012))], 0, 0, "Cromado", in_plan=True)
    c.rev("Corpo", "Front", [(0, z(0.012)), (0.026, z(0.012)), (0.026, z(0.14)), (0.022, z(0.15)), (0, z(0.15))], 0, 0, "Cromado")
    c.rev("Anel giratório", "Front", [(0, z(0.15)), (0.019, z(0.15)), (0.019, z(0.17)), (0, z(0.17))], 0, 0, "Inox escovado", detail=FINE)
    c.cyl_x("Alavanca - cubo", 0, z(0.1), 0.024, 0.014, 0.016, "Cromado")
    c.box("Alavanca", 0.036, -0.006, z(0.094), 0.075, 0.012, 0.012, "Cromado")

    # Spout: a tube rising from the ring and arching forward.
    r = 0.105
    up = 0.42
    pts = [(0.0, 0.17), (0.0, up - r)]
    for k in range(1, 9):
        a = math.pi * k / 8
        pts.append((-r + r * math.cos(a), up - r + r * math.sin(a)))
    pts.append((-2 * r, up - r - 0.04))
    tube(c, "Bica", "Side", [(y, z(h)) for y, h in pts], 0, 0.013, "Cromado", n=16)
    # Pull-out spray head hanging from the end of the arch.
    yh = -2 * r
    c.rev("Ducha extraível", "Front", [(0, z(up - r - 0.04)), (0.016, z(up - r - 0.04)), (0.022, z(up - r - 0.1)), (0.024, z(up - r - 0.13)),
                                       (0, z(up - r - 0.13))], yh, 0, "Cromado")
    c.cyl("Face da ducha", 0, yh, z(up - r - 0.132), 0.02, 0.002, "Plástico preto", FINE)
    c.box("Botão de jato", -0.006, yh - 0.024, z(up - r - 0.075), 0.012, 0.004, 0.018, "Plástico preto", FINE)

    # Under the countertop: threaded shank, nut, two braided hoses.
    c.cyl("Haste de fixação", 0, 0, z(-0.07), 0.017, 0.07, "Latão", FINE)
    c.cyl("Porca de fixação", 0, 0, z(-0.045), 0.028, 0.014, "Latão", FINE)
    for name, x in (("fria", -0.01), ("quente", 0.01)):
        c.cyl(f"Flexível {name}", x, 0, z(-0.3), 0.005, 0.23, "Inox escovado", FINE)
    return c
