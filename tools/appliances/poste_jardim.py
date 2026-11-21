"""Poste de jardim: a garden lamp post with a lantern head (or a globe), a fluted column on a square base.

On the ground, centred on the origin. No device data (see balizador_jardim); the power is in the description.
"""

from kit import *
from _mobilia import EPS, Grp
import _luminarias as lu


def build():
    c = Component("Poste de jardim", "lighting", "poste-jardim", "Lighting")
    H = c.param("Altura", 2.5)
    G = c.param("Globo", 0, "Number")
    lu.materiais(c)
    desc = "Poste de jardim de alumínio fundido pintado de preto, base quadrada chumbada, coluna canelada e cabeça"
    c.type("Poste de jardim com lanterna 2,5 m", desc + " de lanterna com vidro, LED 15 W")
    c.type("Poste de jardim com globo 2,5 m", desc + " de globo de policarbonato leitoso Ø30 cm, LED 15 W", Globo=1)
    c.type("Poste de jardim com lanterna 3,0 m", desc + " de lanterna com vidro, LED 20 W", Altura=3.0)
    c.preview_size = (0.4, 0.4, 3.0)

    kl = f"min(1, max({EPS}, 1 - {G}))"  # the lantern, or…
    kg = f"min(1, max({EPS}, {G}))"  # …the globe
    top = f"{H} - 0.45"  # top of the column
    c.cyl("Poste simplificado", 0, 0, 0, 0.06, H, "Aço pintado preto", detail=COARSE, in_plan=True)
    c.box("Base", -0.12, -0.12, 0, 0.24, 0.24, 0.05, "Aço pintado preto", in_plan=True)
    c.rev("Pé da coluna", "Front", [(0, 0.05), (0.09, 0.05), (0.09, 0.08), (0.075, 0.1), (0.055, 0.16), (0.045, 0.3), (0, 0.3)], 0, 0, "Aço pintado preto")
    c.rev("Coluna", "Front", [(0, 0.3), (0.042, 0.3), (0.034, top), (0, top)], 0, 0, "Aço pintado preto")
    for k in range(8):
        c.box(f"Canelura {k + 1}", f"0.038*cos({45 * k}) - 0.003", f"0.038*sin({45 * k}) - 0.003", 0.35, 0.006, 0.006, f"{top} - 0.4",
              "Aço pintado preto", detail=FINE)
    c.rev("Capitel", "Front", [(0, top), (0.06, top), (0.06, f"{top} + 0.04"), (0, f"{top} + 0.04")], 0, 0, "Aço pintado preto")
    zl = f"{top} + 0.04"
    # Lantern: a tapered glass box under a pyramid roof with a finial.
    gl = Grp(c, kl, (0, 0, f"{top} + 0.02"))
    gl.profile("Lanterna - vidro", "Plan", rect(-0.09, -0.09, 0.09, 0.09), zl, 0.28, lu.DIFUSOR)
    for k, (x, y) in enumerate(((-0.1, -0.1), (0.085, -0.1), (-0.1, 0.085), (0.085, 0.085))):
        gl.box(f"Lanterna - montante {k + 1}", x, y, zl, 0.015, 0.015, 0.3, "Aço pintado preto")
    gl.box("Lanterna - base", -0.11, -0.11, zl, 0.22, 0.22, 0.02, "Aço pintado preto")
    gl.box("Lanterna - beiral", -0.13, -0.13, f"{zl} + 0.3", 0.26, 0.26, 0.02, "Aço pintado preto")
    gl.rev("Lanterna - telhado", "Front", [(0, f"{zl} + 0.32"), (0.13, f"{zl} + 0.32"), (0, f"{zl} + 0.42")], 0, 0, "Aço pintado preto")
    gl.cyl("Lanterna - LED", 0, 0, f"{zl} + 0.05", 0.03, 0.14, lu.LED)
    # Globe: a milky sphere on a collar.
    gg = Grp(c, kg, (0, 0, f"{top} + 0.02"))
    gg.cyl("Globo - colar", 0, 0, zl, 0.07, 0.04, "Aço pintado preto")
    pts = [(0, f"{zl} + 0.04")] + [(f"0.15*sin({a})", f"{zl} + 0.19 - 0.15*cos({a})") for a in range(20, 181, 20)]
    gg.rev("Globo", "Front", pts, 0, 0, lu.DIFUSOR)
    return c
