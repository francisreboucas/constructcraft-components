"""Armário de vestiário: a steel locker of 1 to 4 columns, each with four ventilated doors with a hasp for a padlock.

Against a wall: the back at y = 0, the doors towards -Y; centred on X. `Colunas` from 1 to 4 (the columns a type
does not have shrink away inside the first one).
"""

from kit import *
from _mobilia import EPS, Grp
from _escritorio import declare


def build():
    c = Component("Armário de vestiário", "furniture", "armario-vestiario")
    N = c.param("Colunas", 2, "Number")
    D = c.param("Profundidade", 0.4)
    H = c.param("Altura", 1.95)
    desc = "Armário roupeiro de aço para vestiário com quatro portas por coluna, venezianas de ventilação, porta-cadeado e base"
    c.type("Armário de vestiário 2 colunas, 8 portas", desc)
    c.type("Armário de vestiário 1 coluna, 4 portas", desc, Colunas=1)
    c.type("Armário de vestiário 3 colunas, 12 portas", desc, Colunas=3)
    c.type("Armário de vestiário 4 colunas, 16 portas", desc, Colunas=4)
    declare(c, "Aço pintado cinza claro")
    c.preview_size = (1.3, 0.5, 2.0)

    st = "Aço pintado cinza claro"
    cw = 0.3  # column width
    W = f"{N}*{cw}"
    xl = f"-{W}/2"
    zb = 0.1  # base
    c.box("Armário simplificado", xl, f"-{D}", 0, W, D, H, st, detail=COARSE, in_plan=True)
    c.box("Base", f"{xl} + 0.01", f"-{D} + 0.02", 0, f"{W} - 0.02", f"{D} - 0.03", zb, "Aço pintado cinza")
    c.box("Corpo", xl, f"-{D}", zb, W, D, f"{H} - {zb}", st, in_plan=True)
    hd = f"({H} - {zb} - 0.02)/4"  # door height
    for col in range(4):
        k = f"min(1, max({EPS}, {N} - {col}))"
        g = Grp(c, k, (0, f"-{D}/2", f"{H}/2"))
        x0 = f"{xl} + {col}*{cw}"
        for row in range(4):
            z0 = f"{zb} + 0.01 + {row}*{hd}"
            tag = f"Porta {col + 1}.{row + 1}"
            g.box(tag, f"{x0} + 0.005", f"-{D} - 0.012", f"{z0} + 0.005", cw - 0.01, 0.012, f"{hd} - 0.01", st)
            for v in range(4):
                g.box(f"{tag} - veneziana {v + 1}", f"{x0} + 0.09", f"-{D} - 0.016", f"{z0} + {hd} - 0.08 + {v * 0.012}", 0.12, 0.004, 0.005,
                      "Aço pintado cinza", detail=FINE)
            g.box(f"{tag} - porta-cadeado", f"{x0} + {cw - 0.05}", f"-{D} - 0.03", f"{z0} + {hd}/2 - 0.02", 0.02, 0.018, 0.04,
                  "Aço galvanizado", detail=FINE)
            g.box(f"{tag} - etiqueta", f"{x0} + 0.11", f"-{D} - 0.0125", f"{z0} + {hd} - 0.13", 0.08, 0.001, 0.03, "Branco", detail=FINE)
    return c
