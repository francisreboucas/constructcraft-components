"""Videoporteiro: an outdoor video door-phone panel with a camera, a speaker grille and a call button, under a rain hood.

Wall device: the wall is y = 0, the front -Y; the instance parameter Elevacao is the height of the panel's centre
(1,40 m is usual; 1,00 to 1,20 m within reach from a wheelchair, NBR 9050).
"""

from kit import *


def build():
    c = Component("Videoporteiro", "electrical", "porteiro-eletronico", "Electrical")
    E = c.param("Elevacao", 1.4, "Length", True)
    c.type("Videoporteiro de sobrepor", "Módulo externo de videoporteiro de sobrepor em alumínio escovado, com câmera, alto-falante, "
           "microfone, botão de chamada iluminado e chapéu contra chuva; a central fica dentro do imóvel")
    c.material("Lente", (16, 18, 26), "Glass", "Glossy")
    c.material("LED azul", (60, 150, 240), "Glass", "Glossy")
    c.preview_size = (0.15, 0.08, 0.25)
    c.preview_base = 1.25

    def z(d):
        return f"{E} + {d}"

    w, d, h = 0.1, 0.035, 0.2
    c.box("Videoporteiro simplificado", -w / 2, -d, z(-h / 2), w, d, h, "Alumínio anodizado", detail=COARSE, in_plan=True)
    c.profile("Corpo", "Front", rrect(-w / 2, z(-h / 2), w / 2, z(h / 2), 0.008), -d, d, "Alumínio anodizado", in_plan=True)
    c.profile("Chapéu", "Side", [(f"-{d} - 0.02", z(h / 2 + 0.002)), (0, z(h / 2 + 0.002)), (0, z(h / 2 + 0.012)), (f"-{d} - 0.02", z(h / 2 + 0.006))],
              -w / 2 - 0.006, w + 0.012, "Alumínio anodizado")
    c.cyl_y("Moldura da câmera", 0, z(0.055), f"-{d} - 0.004", 0.018, 0.004, "Plástico preto")
    c.cyl_y("Câmera", 0, z(0.055), f"-{d} - 0.006", 0.007, 0.002, "Lente", detail=FINE)
    for k in range(5):
        c.box(f"Grade do alto-falante {k + 1}", -0.025, f"-{d} - 0.001", z(-0.005 - 0.008 * k), 0.05, 0.001, 0.003, "Plástico preto",
              detail=FINE)
    c.cyl_y("Botão de chamada - anel", 0, z(-0.065), f"-{d} - 0.004", 0.017, 0.004, "LED azul")
    c.cyl_y("Botão de chamada", 0, z(-0.065), f"-{d} - 0.007", 0.013, 0.004, "Inox escovado")
    return c
