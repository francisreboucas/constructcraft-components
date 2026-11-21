"""Exaustor de banheiro: a ceiling extract fan with a square grille, the fan body and duct above the ceiling.

Ceiling device: the ceiling is z = 0 (place it with the base offset at the ceiling height); the grille hangs below it.
"""

from kit import *


def build():
    c = Component("Exaustor de banheiro", "furniture", "exaustor-banheiro", "Furniture")
    S = c.param("Largura", 0.25)
    c.type("Exaustor de teto 150 m³/h", "Exaustor axial de teto para banheiros sem janela, 150 m³/h, grelha quadrada e duto de "
           "100 mm até a fachada ou o shaft; acionado com a luz ou por sensor de umidade")
    c.preview_size = (0.3, 0.3, 0.35)
    c.preview_base = -0.02

    c.box("Exaustor simplificado", f"-{S}/2", f"-{S}/2", -0.02, S, S, 0.2, "Branco", detail=COARSE, in_plan=True)
    c.profile("Grelha - moldura", "Plan", rrect(f"-{S}/2", f"-{S}/2", f"{S}/2", f"{S}/2", 0.015), -0.015, 0.015, "Branco", in_plan=True)
    for k in range(7):
        y = f"-{S}/2 + 0.03 + {k}*({S} - 0.06)/6"
        c.box(f"Grelha - aleta {k + 1}", f"-{S}/2 + 0.025", f"{y} - 0.004", -0.018, f"{S} - 0.05", 0.008, 0.004, "Plástico cinza claro",
              detail=FINE)
    c.box("Caixa do ventilador", f"-{S}/2 + 0.02", f"-{S}/2 + 0.02", 0, f"{S} - 0.04", f"{S} - 0.04", 0.12, "Plástico cinza claro")
    c.cyl("Colarinho", 0, 0, 0.12, 0.052, 0.04, "Plástico cinza claro")
    c.cyl("Duto flexível", 0, 0, 0.16, 0.05, 0.14, "Alumínio anodizado")
    return c
