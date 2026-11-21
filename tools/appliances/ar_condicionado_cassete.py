"""Ar-condicionado cassete: the indoor unit of a 4-way ceiling cassette, the body above the ceiling, the grille below.

Ceiling device: the ceiling is z = 0 (place it with the base offset at the ceiling height); the body rises above it
into the plenum, the panel hangs a few centimetres below.
"""

from kit import *


def build():
    c = Component("Ar-condicionado cassete", "furniture", "ar-condicionado-cassete", "Furniture")
    P = c.param("Painel", 0.95)
    C = c.param("Corpo", 0.84)
    H = c.param("AlturaCorpo", 0.25)
    desc = "Unidade interna de ar-condicionado tipo cassete de 4 vias, corpo embutido no forro e painel com grelha de retorno e aletas"
    c.type("Ar-condicionado cassete 36.000 BTU/h", desc)
    c.type("Ar-condicionado cassete 18.000 BTU/h", desc, Painel=0.62, Corpo=0.57, AlturaCorpo=0.26)
    c.preview_size = (1.0, 1.0, 0.35)
    c.preview_base = -0.05

    pt = 0.035  # panel thickness below the ceiling
    c.box("Cassete simplificado", f"-{P}/2", f"-{P}/2", -pt, P, P, f"{pt} + {H}", "Branco", detail=COARSE, in_plan=True)
    c.box("Corpo", f"-{C}/2", f"-{C}/2", 0, C, C, H, "Aço galvanizado")
    c.profile("Painel", "Plan", rrect(f"-{P}/2", f"-{P}/2", f"{P}/2", f"{P}/2", 0.03), -pt, pt, "Branco", in_plan=True)
    # Return grille in the middle, four supply slots with their louvres around it.
    g = f"{P}*0.36"
    c.box("Grelha de retorno", f"-{g}", f"-{g}", f"-{pt} - 0.002", f"2*{g}", f"2*{g}", 0.002, "Plástico cinza claro")
    for k in range(9):
        y = f"-{g} + ({k} + 0.5)*2*{g}/9"
        c.box(f"Grelha - barra {k + 1}", f"-{g}", f"{y} - 0.002", f"-{pt} - 0.004", f"2*{g}", 0.004, 0.002, "Branco", detail=FINE)
    s0, s1 = f"{P}*0.39", f"{P}*0.45"
    for name, x, y, w, d in (("frontal", f"-{g}", f"-{s1}", f"2*{g}", f"{s1} - {s0}"), ("traseira", f"-{g}", s0, f"2*{g}", f"{s1} - {s0}"),
                             ("esquerda", f"-{s1}", f"-{g}", f"{s1} - {s0}", f"2*{g}"), ("direita", s0, f"-{g}", f"{s1} - {s0}", f"2*{g}")):
        c.box(f"Saída de ar {name}", x, y, f"-{pt} - 0.001", w, d, 0.001, "Plástico cinza")
        c.box(f"Aleta {name}", x, y, f"-{pt} - 0.008", w, d, 0.004, "Branco", detail=FINE)
    # Refrigerant lines and drain out of one side of the body.
    c.cyl_x("Linha de líquido", f"{C}/4", f"{H} - 0.05", f"{C}/2", 0.005, 0.3, "Cobre")
    c.cyl_x("Linha de sucção", f"{C}/4 + 0.04", f"{H} - 0.05", f"{C}/2", 0.008, 0.3, "Borracha")
    c.cyl_x("Dreno", f"-{C}/4", f"{H} - 0.08", f"{C}/2", 0.012, 0.3, "PVC")
    return c
