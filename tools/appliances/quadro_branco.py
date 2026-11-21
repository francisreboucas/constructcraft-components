"""Quadro branco: a wall whiteboard with an aluminium frame and a marker tray.

Wall item: the wall is y = 0, the front -Y; the instance parameter Elevacao is the height of its bottom edge.
"""

from kit import *


def build():
    c = Component("Quadro branco", "furniture", "quadro-branco")
    W = c.param("Largura", 2.0)
    H = c.param("Altura", 1.2)
    E = c.param("Elevacao", 0.9, "Length", True)
    desc = "Quadro branco de laminado melamínico brilhante com moldura de alumínio anodizado e porta-pincel"
    c.type("Quadro branco 200 x 120 cm", desc)
    c.type("Quadro branco 120 x 90 cm", desc, Largura=1.2, Altura=0.9)
    c.type("Quadro branco 300 x 120 cm", desc + "; para salas de aula", Largura=3.0)
    c.material("Laminado branco brilhante", (246, 247, 246), "Plastic", "Glossy")
    c.preview_size = (2.2, 0.2, 1.3)
    c.preview_base = 0.85

    xl = f"-{W}/2"
    f = 0.025
    c.box("Quadro simplificado", xl, -0.02, E, W, 0.02, H, "Laminado branco brilhante", detail=COARSE, in_plan=True)
    c.box("Superfície", f"{xl} + {f}", -0.014, f"{E} + {f}", f"{W} - {2 * f}", 0.014, f"{H} - {2 * f}", "Laminado branco brilhante",
          in_plan=True)
    for name, x, z, w, h in (("inferior", xl, E, W, f), ("superior", xl, f"{E} + {H} - {f}", W, f), ("esquerda", xl, f"{E} + {f}", f, f"{H} - {2 * f}"),
                             ("direita", f"{W}/2 - {f}", f"{E} + {f}", f, f"{H} - {2 * f}")):
        c.box(f"Moldura {name}", x, -0.02, z, w, 0.02, h, "Alumínio anodizado")
    c.profile("Porta-pincel", "Side", [(-0.02, f"{E} - 0.005"), (-0.075, f"{E} - 0.005"), (-0.075, f"{E} + 0.015"), (-0.068, f"{E} + 0.015"),
                                       (-0.068, f"{E} + 0.002"), (-0.02, f"{E} + 0.002")], f"-{W}*0.3", f"{W}*0.6", "Alumínio anodizado")
    for k, (x, mat) in enumerate(((-0.1, "Plástico azul"), (-0.05, "Plástico vermelho"), (0.0, "Plástico preto"))):
        c.cyl_x(f"Pincel {k + 1}", -0.045, f"{E} + 0.012", x, 0.009, 0.13, mat, detail=FINE)
    c.box("Apagador", 0.18, -0.065, f"{E} + 0.002", 0.13, 0.04, 0.03, "Plástico cinza", detail=FINE)
    return c
