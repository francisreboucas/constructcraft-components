"""Luminária de embutir no piso: an in-ground LED uplight, its stainless ring and tempered glass flush with the paving,
the body in a buried sleeve. For façades, trees and walkways (drive-over class).

The paving is z = 0, the body below it. No device data (see balizador_jardim); the power is in the description.
"""

from kit import *
import _luminarias as lu


def build():
    c = Component("Luminária de embutir no piso", "lighting", "embutido-piso", "Lighting")
    D = c.param("Diametro", 0.12)
    H = c.param("Profundidade", 0.12)
    lu.materiais(c)
    desc = "Luminária LED de embutir no piso com aro de aço inox e vidro temperado, 7 W, facho de 30°, IP67, suporta pisoteio"
    c.type("Embutido de piso Ø12 cm", desc)
    c.type("Embutido de piso Ø18 cm", desc.replace("7 W", "15 W"), Diametro=0.18, Profundidade=0.15)
    c.preview_size = (0.25, 0.25, 0.2)
    c.preview_base = -0.1

    r = f"{D}/2"
    c.cyl("Embutido simplificado", 0, 0, f"-{H}", f"{r} + 0.01", H, "Inox escovado", detail=COARSE, in_plan=True)
    c.rev("Aro de inox", "Front", [(f"{r} - 0.012", 0), (f"{r} + 0.012", 0), (f"{r} + 0.012", 0.003), (f"{r} + 0.008", 0.005),
                                   (f"{r} - 0.012", 0.005)], 0, 0, "Inox escovado", in_plan=True)
    c.cyl("Vidro", 0, 0, -0.002, f"{r} - 0.012", 0.006, lu.DIFUSOR)
    c.cyl("Refletor", 0, 0, -0.03, f"{r} - 0.016", 0.026, "Alumínio anodizado", detail=FINE)
    c.cyl("LED", 0, 0, -0.031, f"{r}*0.35", 0.003, lu.LED, detail=FINE)
    c.cyl("Corpo", 0, 0, f"-{H}", f"{r} - 0.01", f"{H} - 0.03", "Alumínio fundido")
    c.cyl("Caixa de embutir", 0, 0, f"-{H} - 0.02", f"{r} + 0.006", f"{H} + 0.018", "Plástico preto")
    c.cyl("Prensa-cabo", f"{r}*0.4", 0, f"-{H} - 0.04", 0.007, 0.02, "Plástico preto", detail=FINE)
    return c
