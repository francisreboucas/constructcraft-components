"""Carregador veicular (wallbox): a wall charger for electric cars with a tethered Type 2 cable coiled on its holder.

Dedicated outlet of 7,4 kVA (NBR 5410): ConstructCraft puts its base at the outlets' height (0,30 m), where the
conduit's box is; the charger stands above it, its bottom 0,70 m higher (1,00 m from the floor), and a conduit rises
from the box to it. The wall is y = 0, the front -Y.
"""

from kit import *


def build():
    c = Component("Carregador veicular (wallbox)", "electrical", "carregador-veicular", "Electrical")
    c.type("Carregador veicular 7,4 kW", "Carregador veicular de parede (wallbox) monofásico de 7,4 kW (32 A, 230 V), cabo "
           "Tipo 2 de 5 m enrolado no suporte; circuito exclusivo com DR tipo A e DPS (NBR 5410, NBR 17019)")
    c.mep = {"Device": {"device": "DedicatedOutlet", "power": 7400}}
    c.connector("Alimentação", "Power", 0, 0, 0.0, "Down")
    c.material("Vidro preto", (14, 15, 18), "Glass", "Glossy")
    c.material("LED azul", (60, 150, 240), "Glass", "Glossy")
    c.preview_size = (0.5, 0.2, 1.05)

    w, d, h, z0 = 0.24, 0.11, 0.36, 0.7
    c.box("Carregador simplificado", -w / 2, -d, z0, w, d, h, "Plástico cinza claro", detail=COARSE, in_plan=True)
    # Body: a rounded shell on a back plate, a black glass front with a status light bar.
    c.box("Placa de fixação", -w / 2 + 0.01, -0.012, z0 + 0.01, w - 0.02, 0.012, h - 0.02, "Plástico cinza", detail=FINE)
    c.profile("Corpo", "Front", rrect(-w / 2, z0, w / 2, z0 + h, 0.04), -d, d - 0.012, "Branco", in_plan=True)
    c.profile("Frente de vidro", "Front", rrect(-w / 2 + 0.018, z0 + 0.06, w / 2 - 0.018, z0 + h - 0.03, 0.025), -d - 0.004, 0.005,
              "Vidro preto")
    c.box("Barra de status", -0.05, -d - 0.0045, z0 + h - 0.08, 0.1, 0.001, 0.008, "LED azul", detail=FINE)
    c.cyl_y("Botão", 0, z0 + 0.1, -d - 0.006, 0.012, 0.003, "Plástico cinza", detail=FINE)
    # Cable gland at the bottom and the cable down, round the holder at the right.
    c.cyl("Prensa-cabo", 0.06, -d / 2, z0 - 0.02, 0.014, 0.02, "Plástico preto", detail=FINE)
    xh, zh = w / 2 + 0.13, z0 + 0.18
    c.cyl_y("Suporte do cabo - base", xh, zh, -0.012, 0.04, 0.012, "Plástico cinza")
    c.cyl_y("Suporte do cabo - cubo", xh, zh, -0.07, 0.03, 0.058, "Plástico cinza")
    for k, r in enumerate((0.1, 0.112, 0.124)):
        c.rev(f"Cabo enrolado {k + 1}", "Plan", [(f"{xh} + {r - 0.009}", -0.05 - 0.02 * k), (f"{xh} + {r + 0.009}", -0.05 - 0.02 * k),
                                                  (f"{xh} + {r + 0.009}", -0.032 - 0.02 * k), (f"{xh} + {r - 0.009}", -0.032 - 0.02 * k)],
              zh, xh, "Borracha")
    c.box("Cabo - trecho até o suporte", 0.054, -d / 2 - 0.009, z0 - 0.06, 0.018, 0.018, 0.045, "Borracha")
    c.cyl_y("Cabo - curva", 0.11, z0 - 0.06, -d / 2 - 0.009, 0.06, 0.018, "Borracha", detail=FINE)
    # Type 2 plug in its holster, under the holder.
    c.box("Coldre do conector", xh - 0.035, -0.06, zh - 0.27, 0.07, 0.06, 0.08, "Plástico cinza")
    c.cyl("Conector Tipo 2", xh, -0.04, zh - 0.21, 0.026, 0.11, "Plástico preto")
    # Conduit from the outlet box (z = 0) up into the charger.
    c.box("Caixa 4x2", -0.03, -0.004, -0.06, 0.06, 0.004, 0.12, "Branco", detail=FINE)
    c.cyl("Eletroduto aparente", 0, -0.02, 0.06, 0.0125, z0 - 0.06, "Plástico cinza claro")
    c.cyl_y("Abraçadeira", 0, z0 * 0.5, -0.034, 0.015, 0.03, "Aço galvanizado", detail=FINE)
    return c
