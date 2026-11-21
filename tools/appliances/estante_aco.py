"""Estante de aço: a slotted-angle steel shelving unit with five shelves, for stores, archives and stockrooms.

Against a wall: the back at y = 0, the front -Y; centred on X.
"""

from kit import *
from _escritorio import declare


def build():
    c = Component("Estante de aço", "furniture", "estante-aco")
    W = c.param("Largura", 0.92)
    D = c.param("Profundidade", 0.3)
    H = c.param("Altura", 1.98)
    desc = "Estante de aço com colunas de cantoneira perfurada, cinco bandejas reforçadas e sapatas plásticas, carga de 50 kg por bandeja"
    c.type("Estante de aço 92 x 30 x 198 cm", desc)
    c.type("Estante de aço 92 x 40 x 198 cm", desc, Profundidade=0.4)
    c.type("Estante de aço 92 x 60 x 198 cm", desc + "; para depósito", Profundidade=0.6)
    declare(c, "Aço pintado cinza claro")
    c.preview_size = (1.0, 0.6, 2.0)

    st = "Aço pintado cinza claro"
    xl = f"-{W}/2"
    a = 0.035  # angle flange
    c.box("Estante simplificada", xl, f"-{D}", 0, W, D, H, st, detail=COARSE, in_plan=True)
    for name, x, y in (("frontal esquerda", xl, f"-{D}"), ("frontal direita", f"{W}/2 - {a}", f"-{D}"),
                       ("traseira esquerda", xl, f"-{a}"), ("traseira direita", f"{W}/2 - {a}", f"-{a}")):
        c.box(f"Coluna {name} - aba 1", x, y, 0.01, a, 0.002, f"{H} - 0.01", st, in_plan=True)
        c.box(f"Coluna {name} - aba 2", x, y, 0.01, 0.002, a, f"{H} - 0.01", st)
        c.box(f"Sapata {name}", x, y, 0, a, a, 0.01, "Plástico preto", detail=FINE)
    for k in range(5):
        z = f"0.08 + {k}*({H} - 0.1)/4"
        c.box(f"Bandeja {k + 1}", xl, f"-{D}", z, W, D, 0.002, st)
        c.box(f"Bandeja {k + 1} - dobra frontal", xl, f"-{D}", f"{z} - 0.03", W, 0.002, 0.03, st)
        c.box(f"Bandeja {k + 1} - dobra traseira", xl, -0.002, f"{z} - 0.03", W, 0.002, 0.03, st, detail=FINE)
        c.box(f"Bandeja {k + 1} - reforço", f"{xl} + {a}", f"-{D}/2 - 0.015", f"{z} - 0.025", f"{W} - {2 * a}", 0.03, 0.025, st, detail=FINE)
    # Diagonal braces at the back (an X).
    c.profile("Contraventamento 1", "Front", [(f"{xl} + {a}", 0.1), (f"{xl} + {a} + 0.02", 0.1), (f"{W}/2 - {a}", f"{H}/2"),
                                               (f"{W}/2 - {a} - 0.02", f"{H}/2")], -0.004, 0.002, st, detail=FINE)
    c.profile("Contraventamento 2", "Front", [(f"{W}/2 - {a} - 0.02", 0.1), (f"{W}/2 - {a}", 0.1), (f"{xl} + {a} + 0.02", f"{H}/2"),
                                               (f"{xl} + {a}", f"{H}/2")], -0.006, 0.002, st, detail=FINE)
    return c
