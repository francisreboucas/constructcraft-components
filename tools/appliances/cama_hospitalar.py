"""Cama hospitalar: a manual hospital bed with a raisable backrest, side rails, head and foot boards, four castors with
brakes and an IV pole. The head is at +Y; centred on the origin. `AnguloEncosto` raises the backrest.
"""

from kit import *
from _escritorio import declare


def build():
    c = Component("Cama hospitalar", "furniture", "cama-hospitalar")
    A = c.angle("AnguloEncosto", 0, open_at=45)
    c.type("Cama hospitalar Fowler", "Cama hospitalar de aço pintado tipo Fowler com cabeceira e peseira removíveis, grades laterais "
           "basculantes, colchão de espuma D33, rodízios de 5\" com freio e suporte de soro; 2,10 x 1,00 m")
    declare(c, "Aço pintado cinza claro")
    c.material("Colchão hospitalar", (120, 170, 200), "Generic", "Satin")
    c.preview_size = (1.1, 2.2, 1.6)

    st = "Aço pintado cinza claro"
    L, W = 2.1, 1.0
    zf = 0.5  # top of the spring frame
    c.box("Cama simplificada", -W / 2, -L / 2, 0, W, L, zf + 0.15, "Colchão hospitalar", detail=COARSE, in_plan=True)
    # Base frame on castors, the platform.
    for k, (x, y) in enumerate(((-0.42, -0.95), (0.42, -0.95), (-0.42, 0.95), (0.42, 0.95))):
        c.cyl(f"Rodízio {k + 1} - garfo", x, y, 0.07, 0.02, 0.06, "Plástico preto")
        c.cyl_x(f"Rodízio {k + 1}", y, 0.063, x - 0.015, 0.063, 0.03, "Borracha")
        c.box(f"Coluna {k + 1}", x - 0.02, y - 0.02, 0.13, 0.04, 0.04, zf - 0.17, st)
    for side, x in (("esquerda", -0.44), ("direita", 0.4)):
        c.box(f"Longarina {side}", x, -L / 2 + 0.05, zf - 0.06, 0.04, L - 0.1, 0.05, st)
        c.box(f"Longarina inferior {side}", x, -0.95, 0.2, 0.04, 1.9, 0.04, st)
    # Mattress: the foot and seat sections fixed, the back section turning about its lower edge (y = 0.15).
    mt = 0.12
    c.box("Colchão - pés e assento", -0.45, -L / 2 + 0.05, zf, 0.9, 1.15, mt, "Colchão hospitalar", in_plan=True)
    hinge = (0.15, zf)
    pts = [lift(hinge, f"-{A}", r, t) for r, t in ((0.0, 0.0), (-0.85, 0.0), (-0.85, mt), (0.0, mt))]
    c.profile("Colchão - encosto", "Side", pts, -0.45, 0.9, "Colchão hospitalar", in_plan=True)
    c.profile("Estrado do encosto", "Side", [lift(hinge, f"-{A}", r, t) for r, t in ((0.0, -0.02), (-0.85, -0.02), (-0.85, 0.0), (0.0, 0.0))], -0.43,
              0.86, st)
    # Head and foot boards.
    c.box("Cabeceira", -W / 2, L / 2 - 0.04, 0.2, W, 0.04, 0.85, "Plástico cinza claro")
    c.box("Peseira", -W / 2, -L / 2, 0.2, W, 0.04, 0.6, "Plástico cinza claro")
    # Side rails: two bars on posts along each side.
    for side, x in (("esquerda", -W / 2), ("direita", W / 2 - 0.025)):
        for k, z in enumerate((zf + mt + 0.1, zf + mt + 0.28)):
            c.box(f"Grade {side} - barra {k + 1}", x, -0.55, z, 0.025, 1.3, 0.025, st)
        for k, y in enumerate((-0.5, 0.1, 0.65)):
            c.box(f"Grade {side} - poste {k + 1}", x, y, zf, 0.025, 0.025, mt + 0.3, st, detail=FINE)
    # IV pole at the head, left.
    c.cyl("Suporte de soro", -0.44, 0.98, zf, 0.012, 1.4, "Inox escovado")
    for k in range(4):
        c.box(f"Gancho de soro {k + 1}", -0.44 - 0.06 + 0.04 * (k % 2), 0.98 - 0.003, zf + 1.38, 0.08 if k < 2 else 0.006, 0.006, 0.006,
              "Inox escovado", detail=FINE)
    c.box("Manivela", -0.03, -L / 2 - 0.08, 0.3, 0.06, 0.08, 0.06, "Cromado", detail=FINE)
    return c
