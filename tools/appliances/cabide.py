"""Cabide: a double wall hook of chromed brass for towels and robes."""

from kit import *
from louca import add, smooth, tube
from _acessorios import rose


def build():
    c = Component("Cabide", "furniture", "cabide", "Furniture")
    E = c.param("Elevacao", 1.7, "Length", True)
    c.type("Cabide duplo de parede", "Cabide duplo de parede para toalhas e roupões, latão cromado, fixação oculta; Elevacao é a "
           "altura da canopla")
    c.preview_size = (0.06, 0.08, 0.1)
    c.preview_base = 1.6

    def z(d):
        return add(E, d)

    c.box("Cabide simplificado", -0.02, -0.07, z(-0.02), 0.04, 0.07, 0.07, "Cromado", detail=COARSE, in_plan=True)
    rose(c, "Canopla", 0, E, r=0.02, depth=0.012)
    # Two hooks out of the rose: a long upper one and a short lower one, each curling up at the tip.
    for name, pts, r in (("superior", [(-0.008, 0.006), (-0.035, 0.004), (-0.056, 0.012), (-0.064, 0.03), (-0.06, 0.044)], 0.0065),
                         ("inferior", [(-0.008, -0.006), (-0.022, -0.016), (-0.036, -0.014), (-0.042, -0.002), (-0.04, 0.008)], 0.0055)):
        tube(c, f"Gancho {name}", "Side", [(y, z(h)) for y, h in smooth(pts, 6)], 0, r, "Cromado", n=16)
        ye, ze = pts[-1]
        c.cyl(f"Ponteira {name}", 0, ye, z(ze - 0.003), r + 0.0012, 0.005, "Cromado", detail=FINE)
    return c
