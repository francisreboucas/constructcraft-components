"""Padrão de entrada de energia: the utility service entrance at the property line, a galvanized steel pole with the
service-drop insulator at the top, the meter box with its viewing window and the main breaker, the conduit, the
grounding rod and its inspection box.

On the ground, at the boundary: the pole at the origin, the meter box on its street side (towards -Y). Heights follow
the usual utility standards (meter window between 1,20 and 1,60 m).
"""

from kit import *


def build():
    c = Component("Padrão de entrada de energia", "electrical", "padrao-entrada", "Electrical")
    H = c.param("AlturaPoste", 6.0)
    c.type("Padrão de entrada monofásico", "Padrão de entrada de energia monofásico em poste de aço galvanizado de 6 m acima do "
           "solo, armação secundária com isolador roldana, caixa de medição de policarbonato com visor e disjuntor geral, "
           "eletroduto de descida e haste de aterramento com caixa de inspeção; confira o padrão da concessionária local")
    c.type("Padrão de entrada monofásico 7 m", "Padrão de entrada monofásico com poste de 7 m acima do solo, para travessia de rua "
           "mais alta", AlturaPoste=7.0)
    c.material("Policarbonato cinza", (196, 200, 202), "Plastic", "Satin")
    c.preview_size = (0.8, 0.6, 6.4)

    r = 0.05  # pole radius (4")
    c.cyl("Poste simplificado", 0, 0, 0, r, H, "Aço galvanizado", detail=COARSE, in_plan=True)
    c.box("Caixa de medição simplificada", -0.18, -0.25, 1.15, 0.36, 0.2, 0.55, "Policarbonato cinza", detail=COARSE)
    c.cyl("Poste", 0, 0, 0, r, H, "Aço galvanizado", in_plan=True)
    c.cyl("Base de concreto", 0, 0, 0, 0.15, 0.08, "Concreto")
    c.cyl("Tampa do poste", 0, 0, H, r + 0.006, 0.02, "Aço galvanizado", detail=FINE)
    # The service-drop insulator on a secondary rack near the top, and the cable to it.
    zr = f"{H} - 0.25"
    c.box("Armação secundária", -0.03, -0.12, zr, 0.06, 0.07, 0.16, "Aço galvanizado")
    c.cyl("Isolador roldana", 0, -0.14, f"{zr} + 0.03", 0.04, 0.09, "Louça")
    c.rev("Isolador roldana - gola", "Front", [(0, f"{zr} + 0.06"), (0.028, f"{zr} + 0.06"), (0.028, f"{zr} + 0.09"), (0, f"{zr} + 0.09")], -0.14,
          0, "Louça", detail=FINE)
    c.cyl_y("Ramal de ligação", 0, f"{zr} + 0.075", -1.2, 0.007, 1.06, "Borracha")
    # The weather head and the conduit down the pole into the meter box.
    c.cyl("Eletroduto de entrada", 0.0, -0.075, 1.7, 0.019, f"{H} - 0.55 - 1.7", "Aço galvanizado")
    c.rev("Curva de entrada", "Front", [(0, f"{H} - 0.55"), (0.026, f"{H} - 0.55"), (0.026, f"{H} - 0.45"), (0, f"{H} - 0.42")], -0.075, 0,
          "Aço galvanizado")
    for k, z in enumerate((2.2, 3.2, 4.2, f"{H} - 0.7"), 1):
        c.cyl(f"Abraçadeira {k}", 0, -0.04, z, 0.075, 0.025, "Aço galvanizado", detail=FINE)
    # Meter box: body, the window over the meter, the breaker door below it, the seal.
    c.box("Caixa de medição", -0.17, -0.27, 1.15, 0.34, 0.17, 0.55, "Policarbonato cinza", in_plan=True)
    c.box("Caixa de medição - suporte", -0.04, -0.1, 1.25, 0.08, 0.06, 0.35, "Aço galvanizado", detail=FINE)
    c.box("Visor", -0.11, -0.275, 1.4, 0.22, 0.006, 0.22, "Plástico translúcido")
    c.box("Medidor", -0.08, -0.24, 1.43, 0.16, 0.03, 0.16, "Plástico preto")
    c.box("Visor do medidor", -0.04, -0.245, 1.52, 0.08, 0.005, 0.03, "Visor LCD", detail=FINE)
    c.box("Porta do disjuntor", -0.11, -0.275, 1.2, 0.22, 0.006, 0.14, "Policarbonato cinza")
    c.box("Disjuntor geral", -0.02, -0.2, 1.23, 0.036, 0.06, 0.08, "Branco", detail=FINE)
    c.cyl_y("Lacre", 0.12, 1.55, -0.28, 0.008, 0.006, "Plástico vermelho", detail=FINE)
    # Down to the house: conduit from the box into the ground.
    c.cyl("Eletroduto de saída", 0.1, -0.18, -0.3, 0.019, 1.45, "Plástico cinza")
    # Grounding: an inspection box with the rod's head at the foot of the pole.
    c.box("Caixa de inspeção do aterramento", 0.2, -0.45, -0.3, 0.3, 0.3, 0.32, "Concreto")
    c.box("Tampa da caixa de inspeção", 0.21, -0.44, 0.02, 0.28, 0.28, 0.015, "Ferro fundido")
    c.cyl("Haste de aterramento", 0.35, -0.3, -2.4, 0.008, 2.4, "Cobre")
    c.cyl("Condutor de aterramento", 0.0, -0.1, -0.3, 0.004, 1.6, "Cobre", detail=FINE)
    return c
