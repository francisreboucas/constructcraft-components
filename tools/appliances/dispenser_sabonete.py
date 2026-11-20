"""Dispenser de sabonete líquido: a wall dispenser with a smoked window, a push button and a refill reservoir."""

from kit import *
from louca import add


def build():
    c = Component("Dispenser de sabonete líquido", "furniture", "dispenser-sabonete", "Furniture")
    E = c.param("Elevacao", 1.0, "Length", True)
    c.type("Dispenser de sabonete 800 ml", "Dispenser de parede para sabonete líquido ou álcool em gel, 800 ml, de plástico ABS "
           "branco com visor fumê e botão de pressão; Elevacao é a altura da base (NBR 9050: comando entre 0,80 m e 1,20 m)")
    c.preview_size = (0.12, 0.12, 0.22)
    c.preview_base = 0.95

    def z(d):
        return add(E, d)

    w, d, hh = 0.115, 0.105, 0.21
    c.box("Dispenser simplificado", -w / 2, -d, E, w, d, hh, "Branco", detail=COARSE, in_plan=True)
    c.box("Placa de fixação", -w / 2 + 0.004, -0.008, z(0.004), w - 0.008, 0.008, hh - 0.008, "Plástico cinza claro", detail=FINE)
    # Cover: a side profile rounded at the top front and tapering to the button at the bottom.
    c.profile("Tampa", "Side", [(-0.008, z(0.0)), (-0.008, z(hh)), (-d + 0.02, z(hh), 0.02), (-d, z(hh - 0.02)), (-d, z(0.07)), (-d + 0.03, z(0.0), -0.05)],
              -w / 2, w, "Branco", in_plan=True)
    c.box("Visor", -0.03, -d - 0.0015, z(0.1), 0.06, 0.002, 0.07, "Plástico fumê")
    c.profile("Botão", "Side", [(-d + 0.024, z(0.004)), (-d + 0.002, z(0.04)), (-d - 0.004, z(0.068)), (-d + 0.01, z(0.07)), (-d + 0.03, z(0.02))],
              -0.035, 0.07, "Plástico cinza claro")
    c.cyl("Bico", 0, -0.045, z(-0.006), 0.006, 0.008, "Plástico cinza claro", detail=FINE)
    c.box("Fechadura da tampa", -0.006, -0.012, z(hh), 0.012, 0.004, 0.003, "Plástico cinza", detail=FINE)
    return c
