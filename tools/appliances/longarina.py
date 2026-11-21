"""Longarina: a waiting-room bench of moulded seats on a steel beam with two T-legs (clinics, offices, terminals).

The seats face -Y; centred on X. `Lugares` from 2 to 5 (the seats a type does not have shrink into the beam).
"""

from kit import *
from _mobilia import EPS, Grp
from _escritorio import declare


def build():
    c = Component("Longarina", "furniture", "longarina")
    N = c.param("Lugares", 3, "Number")
    desc = "Longarina de espera com assentos e encostos de polipropileno sobre viga de aço e dois pés em T, com braços nas pontas"
    c.type("Longarina 3 lugares", desc)
    c.type("Longarina 2 lugares", desc, Lugares=2)
    c.type("Longarina 4 lugares", desc, Lugares=4)
    c.type("Longarina 5 lugares", desc, Lugares=5)
    declare(c, "Tecido estofado preto")
    c.preview_size = (2.4, 0.7, 0.9)

    p = 0.52  # seat pitch
    L = f"{N}*{p}"
    xl = f"-{L}/2"
    c.box("Longarina simplificada", xl, -0.3, 0, L, 0.6, 0.85, "Plástico preto", detail=COARSE, in_plan=True)
    c.box("Viga", f"{xl} + 0.05", -0.03, 0.36, f"{L} - 0.1", 0.06, 0.05, "Aço pintado preto")
    for side, x in (("esquerdo", f"{xl} + 0.15"), ("direito", f"-{xl} - 0.17")):
        c.box(f"Pé {side} - coluna", x, -0.02, 0.03, 0.02, 0.04, 0.33, "Aço pintado preto")
        c.box(f"Pé {side} - base", f"{x} - 0.01", -0.28, 0, 0.04, 0.56, 0.03, "Aço pintado preto")
    for k in range(5):
        x0 = f"{xl} + {k}*{p} + 0.03"
        kk = f"min(1, max({EPS}, {N} - {k}))"
        g = Grp(c, kk, (0, 0, 0.385))
        g.box(f"Assento {k + 1}", x0, -0.27, 0.41, p - 0.06, 0.44, 0.04, "Plástico preto", in_plan=True)
        g.box(f"Estofado {k + 1}", f"{x0} + 0.02", -0.25, 0.45, p - 0.1, 0.38, 0.02, "Tecido estofado preto", detail=FINE)
        g.box(f"Encosto {k + 1}", x0, 0.16, 0.52, p - 0.06, 0.03, 0.33, "Plástico preto")
        g.box(f"Suporte do encosto {k + 1}", f"{x0} + {p / 2 - 0.05}", 0.03, 0.4, 0.04, 0.14, 0.04, "Aço pintado preto")
        g.box(f"Haste do encosto {k + 1}", f"{x0} + {p / 2 - 0.05}", 0.16, 0.42, 0.04, 0.02, 0.15, "Aço pintado preto")
    for side, x in (("esquerdo", f"{xl} - 0.01"), ("direito", f"-{xl} - 0.03")):
        c.box(f"Braço {side}", x, -0.22, 0.6, 0.04, 0.34, 0.03, "Plástico preto")
        c.box(f"Haste do braço {side}", x, -0.05, 0.39, 0.04, 0.03, 0.21, "Aço pintado preto")
    return c
