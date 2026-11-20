"""Papeleira: a wall toilet-roll holder of chromed brass, an open arm on a round rose, with the roll on it."""

from kit import *
from louca import add
from _acessorios import rose


def build():
    c = Component("Papeleira", "furniture", "papeleira", "Furniture")
    E = c.param("Elevacao", 0.6, "Length", True)
    c.type("Papeleira de parede", "Papeleira de parede de braço aberto, latão cromado, com rolo de papel higiênico; "
           "Elevacao é a altura do eixo do rolo (NBR 9050: entre 0,50 m e 0,60 m, ao alcance da bacia)")
    c.material("Papel higiênico", (246, 246, 242), "Generic", "Matte")
    c.preview_size = (0.2, 0.15, 0.15)
    c.preview_base = 0.5

    def z(d):
        return add(E, d)

    c.box("Papeleira simplificada", -0.02, -0.13, z(-0.06), 0.16, 0.13, 0.12, "Papel higiênico", detail=COARSE, in_plan=True)
    rose(c, "Canopla", -0.01, E, r=0.026, depth=0.014)
    c.cyl_y("Braço", -0.01, E, -0.075, 0.009, 0.062, "Cromado")
    c.cyl("Cotovelo", -0.01, -0.075, z(-0.0095), 0.0095, 0.019, "Cromado", detail=FINE)
    c.cyl_x("Haste", -0.075, E, -0.01, 0.0085, 0.15, "Cromado")
    c.cyl_x("Ponteira", -0.075, E, 0.14, 0.0105, 0.008, "Cromado", detail=FINE)
    # The roll: 10 cm wide, 11 cm across, on a cardboard core.
    c.cyl_x("Rolo de papel", -0.075, E, 0.015, 0.055, 0.1, "Papel higiênico", in_plan=True)
    c.cyl_x("Tubete do rolo", -0.075, E, 0.0145, 0.022, 0.101, "Papel kraft", detail=FINE)
    c.box("Ponta solta do papel", 0.015, -0.13, z(-0.12), 0.1, 0.0008, 0.12, "Papel higiênico", detail=FINE)
    c.material("Papel kraft", (176, 140, 92), "Generic", "Matte")
    return c
