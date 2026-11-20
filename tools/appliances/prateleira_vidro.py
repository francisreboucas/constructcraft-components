"""Prateleira de vidro: a tempered glass bathroom shelf on two chromed brackets, with a front rail."""

from kit import *
from louca import add
from _acessorios import rose


def build():
    c = Component("Prateleira de vidro", "furniture", "prateleira-vidro", "Furniture")
    W = c.param("Largura", 0.6)
    D = c.param("Profundidade", 0.12)
    E = c.param("Elevacao", 1.2, "Length", True)
    desc = "Prateleira de banheiro de vidro temperado de 8 mm com bordas lapidadas, suportes e grade frontal de latão cromado"
    c.type("Prateleira de vidro 60 cm", desc)
    c.type("Prateleira de vidro 40 cm", desc, Largura=0.4)
    c.type("Prateleira de vidro 80 cm", desc, Largura=0.8, Profundidade=0.14)
    c.preview_base = 1.1

    def z(d):
        return add(E, d)

    c.box("Prateleira simplificada", f"-{W}/2", f"-{D}", E, W, D, 0.008, "Vidro temperado", detail=COARSE, in_plan=True)
    c.profile("Vidro", "Plan", rrect(f"-{W}/2", f"-{D}", f"{W}/2", -0.004, 0.01), E, 0.008, "Vidro temperado", in_plan=True)
    xs = f"({W}/2 - 0.06)"
    for name, s in (("esquerdo", "-"), ("direito", "")):
        x = f"{s}{xs}"
        rose(c, f"Canopla do suporte {name}", x, z(-0.012), r=0.02, depth=0.01)
        # A clamp under and over the glass, and a post of the front rail.
        c.box(f"Suporte {name}", f"{x} - 0.008", f"-{D} + 0.03", z(-0.022), 0.016, f"{D} - 0.04", 0.02, "Cromado")
        c.box(f"Presilha {name}", f"{x} - 0.012", f"-{D} + 0.032", z(-0.004), 0.024, 0.03, 0.016, "Cromado", detail=FINE)
        c.cyl(f"Haste da grade {name}", x, f"-{D} + 0.012", z(0.008), 0.004, 0.04, "Cromado")
    c.cyl_x("Grade frontal", f"-{D} + 0.012", z(0.048), f"-{xs} - 0.02", 0.005, f"2*{xs} + 0.04", "Cromado")
    return c
