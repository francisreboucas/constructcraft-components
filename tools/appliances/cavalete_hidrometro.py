"""Cavalete com hidrômetro: the water service entrance at the property line, in its concrete box with a steel door.

The box stands on the ground against the boundary wall (y = 0 is its back), the door towards -Y. The supply comes
from below at the left and leaves through the wall at the right.
"""

from kit import *


def build():
    c = Component("Cavalete com hidrômetro", "plumbing", "cavalete-hidrometro", "Plumbing")
    A = c.angle("AnguloPorta", 0, open_at=110)
    c.type("Cavalete com hidrômetro DN 20", "Cavalete de PVC DN 20 (3/4\") com registro de esfera, hidrômetro de 1,5 m³/h e "
           "tubete, em abrigo de concreto com porta de chapa e visor, no muro de divisa, conforme o padrão da concessionária")
    c.mep = {"Fixture": {"drain_units": 0, "supply_weight": 0, "hot_water": False}}
    c.connector("Rede pública", "ColdWater", -0.17, -0.18, 0.0, "Down", 0.025)
    c.connector("Alimentação do imóvel", "ColdWater", 0.17, 0.0, 0.42, "Back", 0.025)
    c.material("Vidro do hidrômetro", (200, 220, 230), "Glass", "Polished", 0.5)
    c.material("PVC marrom", (120, 70, 46), "Plastic", "Satin")
    c.preview_size = (0.7, 0.4, 0.8)

    w, d, h, t = 0.6, 0.35, 0.8, 0.05
    c.box("Abrigo simplificado", -w / 2, -d, 0, w, d, h, "Concreto", detail=COARSE, in_plan=True)
    c.box("Abrigo - fundo", -w / 2, -t, 0, w, t, h, "Concreto")
    c.box("Abrigo - lateral esquerda", -w / 2, -d, 0, t, d - t, h, "Concreto", in_plan=True)
    c.box("Abrigo - lateral direita", w / 2 - t, -d, 0, t, d - t, h, "Concreto", in_plan=True)
    c.box("Abrigo - topo", -w / 2, -d, h - t, w, d - t, t, "Concreto")
    c.box("Abrigo - base", -w / 2 + t, -d, 0, w - 2 * t, d - t, 0.06, "Concreto")
    # Door: steel sheet hinged at the left with a reading window.
    hinge = (-w / 2 + t, -d)
    dw = w - 2 * t
    c.door_box("Porta", hinge, A, 0, dw, 0, 0.004, 0.08, h - t - 0.1, "Aço pintado cinza")
    c.door_box("Visor da porta", hinge, A, dw * 0.35, dw * 0.65, 0.004, 0.006, 0.42, 0.12, "Vidro do hidrômetro", detail=FINE)
    c.door_box("Fecho da porta", hinge, A, dw - 0.05, dw - 0.02, 0.004, 0.02, 0.36, 0.05, "Aço galvanizado", detail=FINE)
    # The cavalete: riser from the ground at the left, across at the meter height, down and out at the right.
    y = -0.18
    zm = 0.42
    c.cyl("Tubo de entrada", -0.17, y, 0.0, 0.0125, zm, "PVC marrom")
    c.cyl_x("Tubo horizontal", y, zm, -0.17, 0.0125, 0.34, "PVC marrom")
    c.cyl_y("Saída para o imóvel", 0.17, zm, y, 0.0125, -y, "PVC marrom")
    for x in (-0.17, 0.17):
        c.rev(f"Joelho {'esquerdo' if x < 0 else 'direito'}", "Front", [(x, zm - 0.02), (x + 0.018, zm - 0.02), (x + 0.018, zm + 0.02), (x, zm + 0.02)],
              y, x, "PVC marrom", detail=FINE)
    # Ball valve and the meter.
    c.cyl_x("Registro - corpo", y, zm, -0.13, 0.02, 0.05, "Latão")
    c.box("Registro - alavanca", -0.115, y - 0.06, zm + 0.015, 0.02, 0.06, 0.008, "Plástico vermelho")
    c.cyl_x("Hidrômetro - porcas", y, zm, -0.06, 0.018, 0.13, "Latão")
    c.cyl("Hidrômetro - corpo", 0.005, y, zm - 0.035, 0.045, 0.07, "Latão")
    c.cyl("Hidrômetro - mostrador", 0.005, y, zm + 0.035, 0.04, 0.012, "Vidro do hidrômetro")
    c.cyl("Hidrômetro - tampa", 0.005, y, zm + 0.047, 0.042, 0.006, "Plástico azul", detail=FINE)
    return c
