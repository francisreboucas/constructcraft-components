"""Gôndola: a double-sided steel shop shelving module, a perforated central back, a base deck and four shelves each side
with price strips. Place modules end to end for a run. The shelves fronts face ±Y.
"""

from kit import *
from _escritorio import declare


def build():
    c = Component("Gôndola", "furniture", "gondola")
    W = c.param("Largura", 1.0)
    D = c.param("Profundidade", 0.9)
    H = c.param("Altura", 1.6)
    desc = "Gôndola dupla de aço pintado com costas perfuradas, base e quatro prateleiras de cada lado com porta-etiquetas de preço"
    c.type("Gôndola dupla 1,0 x 1,6 m", desc)
    c.type("Gôndola dupla 1,0 x 2,0 m", desc, Altura=2.0)
    c.type("Gôndola dupla 1,2 x 1,6 m", desc, Largura=1.2)
    declare(c, "Aço pintado cinza claro")
    c.preview_size = (1.1, 1.0, 1.8)

    st = "Aço pintado cinza claro"
    xl = f"-{W}/2"
    c.box("Gôndola simplificada", xl, f"-{D}/2", 0, W, D, H, st, detail=COARSE, in_plan=True)
    for side, x in (("esquerda", xl), ("direita", f"{W}/2 - 0.03")):
        c.box(f"Coluna {side}", x, -0.03, 0, 0.03, 0.06, H, st)
        c.box(f"Pé {side}", x, f"-{D}/2", 0, 0.03, D, 0.12, st)
    c.box("Costas perfuradas", f"{xl} + 0.03", -0.01, 0.12, f"{W} - 0.06", 0.02, f"{H} - 0.12", "Tela perfurada")
    c.box("Travessa superior", f"{xl} + 0.03", -0.02, f"{H} - 0.04", f"{W} - 0.06", 0.04, 0.04, st)
    for s, nm in ((-1, "frente"), (1, "verso")):
        y0 = f"{s}*0.02" if s > 0 else f"-{D}/2"
        dep = f"{D}/2 - 0.02"
        c.box(f"Base - {nm}", f"{xl} + 0.03", y0, 0.12, f"{W} - 0.06", dep, 0.02, st, in_plan=True)
        c.box(f"Rodapé - {nm}", f"{xl} + 0.03", f"{s}*{D}/2 - {0.02 if s > 0 else 0}", 0.0, f"{W} - 0.06", 0.02, 0.12, st)
        for k in range(1, 5):
            z = f"0.12 + {k}*({H} - 0.25)/4.6"
            dk = f"({dep})*(1 - 0.12*{k})"  # the upper shelves are shallower
            yk = y0 if s > 0 else f"-0.02 - {dk}"
            c.box(f"Prateleira {k} - {nm}", f"{xl} + 0.03", yk, z, f"{W} - 0.06", dk, 0.02, st)
            yf = f"0.02 + {dk}" if s > 0 else f"-0.02 - {dk} - 0.004"
            c.box(f"Porta-etiqueta {k} - {nm}", f"{xl} + 0.03", yf, f"{z} - 0.02", f"{W} - 0.06", 0.004, 0.04, "Plástico translúcido",
                  detail=FINE)
    return c
