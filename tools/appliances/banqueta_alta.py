"""Banqueta alta: a bar stool with a round upholstered seat, four splayed steel legs and a footrest ring."""

from kit import *
from _escritorio import declare


def build():
    c = Component("Banqueta alta", "furniture", "banqueta-alta")
    H = c.param("AlturaAssento", 0.75)
    desc = "Banqueta de aço pintado com assento redondo estofado Ø36 cm, quatro pés abertos e aro de apoio para os pés"
    c.type("Banqueta alta 75 cm (balcão)", desc + "; para bancadas a 1,05 m")
    c.type("Banqueta alta 65 cm (cozinha)", desc + "; para bancadas a 0,90 m", AlturaAssento=0.65)
    declare(c, "Tecido estofado preto")
    c.preview_size = (0.5, 0.5, 0.8)

    c.cyl("Banqueta simplificada", 0, 0, 0, 0.2, H, "Aço pintado preto", detail=COARSE, in_plan=True)
    c.rev("Assento", "Front", [(0, f"{H} - 0.05"), (0.17, f"{H} - 0.05"), (0.18, f"{H} - 0.02", 0.03), (0.16, H), (0, f"{H} + 0.005")], 0, 0,
          "Tecido estofado preto", in_plan=True)
    c.cyl("Base do assento", 0, 0, f"{H} - 0.07", 0.15, 0.02, "Aço pintado preto")
    for k in range(4):
        a = 45 + 90 * k
        bot = (f"0.15*cos({a})", f"0.15*sin({a})")
        # A glide under each leg.
        c.profile(f"Pé {k + 1}", "Plan", [(f"{bot[0]} - 0.01", f"{bot[1]} - 0.01"), (f"{bot[0]} + 0.01", f"{bot[1]} - 0.01"),
                                          (f"{bot[0]} + 0.01", f"{bot[1]} + 0.01"), (f"{bot[0]} - 0.01", f"{bot[1]} + 0.01")], 0, 0.01,
                  "Plástico preto", detail=FINE)
        c.box(f"Haste {k + 1}", f"0.15*cos({a}) - 0.01", f"0.15*sin({a}) - 0.01", 0, 0.02, 0.02, f"{H} - 0.07", "Aço pintado preto")
    c.rev("Aro de apoio dos pés", "Front", [(0.17, 0.27), (0.19, 0.27), (0.19, 0.29), (0.17, 0.29)], 0, 0, "Aço pintado preto")
    return c
