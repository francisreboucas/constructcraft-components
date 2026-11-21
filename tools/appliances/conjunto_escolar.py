"""Conjunto escolar: a student's desk and chair of steel tube with a laminated top and a polypropylene seat and back,
with the bookrack under the top. The sizes follow the FNDE/ABNT size classes (NBR 14006).

The desk is centred on the origin; the chair stands at -Y, facing the desk (+Y).
"""

from kit import *


def build():
    c = Component("Conjunto escolar", "furniture", "conjunto-escolar")
    H = c.param("AlturaMesa", 0.76)
    S = c.param("AlturaAssento", 0.46)
    desc = "Conjunto escolar (mesa e cadeira) de tubo de aço com tampo de MDF revestido de laminado, porta-livros, assento e encosto de polipropileno"
    c.type("Conjunto escolar CJA-06 (adulto)", desc + "; tamanho 6, para alunos de 1,59 a 1,88 m (NBR 14006)")
    c.type("Conjunto escolar CJA-04", desc + "; tamanho 4, para alunos de 1,33 a 1,59 m", AlturaMesa=0.64, AlturaAssento=0.38)
    c.type("Conjunto escolar CJA-03", desc + "; tamanho 3, para alunos de 1,19 a 1,42 m", AlturaMesa=0.59, AlturaAssento=0.35)
    c.preview_size = (0.7, 1.1, 0.9)

    tube = "Aço pintado cinza"
    c.box("Conjunto simplificado", -0.3, -0.75, 0, 0.6, 1.05, H, "Laminado branco", detail=COARSE, in_plan=True)
    # Desk: top 60 x 45 cm on four legs, the bookrack under it.
    c.box("Tampo", -0.3, -0.15, f"{H} - 0.022", 0.6, 0.45, 0.022, "Laminado branco", in_plan=True)
    c.box("Fita de borda", -0.3, -0.152, f"{H} - 0.022", 0.6, 0.002, 0.022, "Plástico azul", detail=FINE)
    for k, (x, y) in enumerate(((-0.28, -0.13), (0.26, -0.13), (-0.28, 0.27), (0.26, 0.27))):
        c.box(f"Pé da mesa {k + 1}", x, y, 0, 0.02, 0.02, f"{H} - 0.022", tube)
    c.box("Porta-livros", -0.27, 0.0, f"{H} - 0.16", 0.54, 0.28, 0.003, tube)
    c.box("Travessa da mesa", -0.27, 0.27, 0.12, 0.54, 0.02, 0.02, tube)
    for side, x in (("esquerda", -0.28), ("direita", 0.26)):
        c.box(f"Travessa lateral {side}", x, -0.13, 0.12, 0.02, 0.4, 0.02, tube)
    # Chair at -Y, facing the desk (+Y).
    yc = -0.5  # centre of the seat
    c.box("Assento", -0.2, f"{yc} - 0.2", f"{S} - 0.02", 0.4, 0.4, 0.02, "Plástico azul", in_plan=True)
    c.box("Encosto", -0.19, f"{yc} - 0.22", f"{S} + 0.15", 0.38, 0.02, 0.22, "Plástico azul")
    for k, (x, y) in enumerate(((-0.18, -0.67), (0.16, -0.67), (-0.18, -0.35), (0.16, -0.35))):
        back = y < -0.6
        c.box(f"Pé da cadeira {k + 1}", x, y, 0, 0.02, 0.02, f"{S} + {0.36 if back else -0.02}", tube)
    c.box("Travessa da cadeira", -0.17, -0.67, 0.15, 0.34, 0.02, 0.02, tube)
    return c
