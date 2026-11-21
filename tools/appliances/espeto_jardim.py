"""Espeto de jardim: a spike-mounted LED spotlight aimed up at a tree, a wall or a plant, with an anti-glare snoot.

On the ground at the origin, the spike driven into the soil; `Inclinacao` is the beam's angle above the horizon, aimed
towards +Y (the object it lights). No device data (see balizador_jardim); the power is in the description.
"""

from kit import *
import _luminarias as lu


def build():
    c = Component("Espeto de jardim", "lighting", "espeto-jardim", "Lighting")
    A = c.param("Inclinacao", 60, "Angle")
    lu.materiais(c)
    desc = "Espeto de jardim de alumínio com projetor LED de 7 W, facho de 24°, aleta antiofuscamento e articulação, IP65"
    c.type("Espeto de jardim 60°", desc)
    c.type("Espeto de jardim 30°", desc + "; para fachadas e muros", Inclinacao=30)
    c.type("Espeto de jardim 85°", desc + "; para árvores e palmeiras", Inclinacao=85)
    c.preview_size = (0.2, 0.3, 0.35)

    c.box("Espeto simplificado", -0.04, -0.06, 0, 0.08, 0.16, 0.22, "Aço pintado preto", detail=COARSE, in_plan=True)
    # Spike (below ground) and the stem with the knuckle.
    c.rev("Espeto", "Front", [(0, -0.2), (0.012, -0.03), (0.016, 0), (0, 0)], 0, 0, "Plástico preto")
    c.cyl("Haste", 0, 0, 0, 0.012, 0.09, "Aço pintado preto")
    zk = 0.1
    c.cyl_x("Articulação", 0, zk, -0.018, 0.016, 0.036, "Aço pintado preto")
    # The spot: a cylinder along its axis, tilted A above the horizon towards +Y, its glass and snoot at the front.
    ca, sa = f"cos({A})", f"sin({A})"

    def pt(s, n):  # (y, z) of the point s along the beam and n across it (above), from the knuckle
        return (f"({s})*{ca} - ({n})*{sa}", f"{zk} + ({s})*{sa} + ({n})*{ca}")

    def slab(name, s0, s1, n0, n1, x, w, mat, **kw):
        c.profile(name, "Side", [pt(s0, n0), pt(s1, n0), pt(s1, n1), pt(s0, n1)], x, w, mat, **kw)

    slab("Corpo do projetor", -0.04, 0.08, -0.034, 0.034, -0.034, 0.068, "Aço pintado preto", in_plan=True)
    for k in range(3):
        s = -0.036 + 0.014 * k
        slab(f"Aleta de dissipação {k + 1}", s, f"{s} + 0.005", -0.037, 0.037, -0.037, 0.074, "Aço pintado preto", detail=FINE)
    slab("Vidro", 0.08, 0.084, -0.028, 0.028, -0.028, 0.056, lu.DIFUSOR)
    slab("Aleta antiofuscamento", 0.08, 0.115, 0.03, 0.034, -0.034, 0.068, "Aço pintado preto")
    slab("LED", 0.074, 0.078, -0.012, 0.012, -0.012, 0.024, lu.LED, detail=FINE)
    c.cyl("Cabo", 0.03, 0.0, -0.05, 0.004, 0.08, "Borracha", detail=FINE)
    return c
