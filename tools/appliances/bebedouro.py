"""Bebedouro: a wall-hung stainless steel drinking fountain with two basins, a standard one and an accessible one
(NBR 9050: spout at 0,90 m, free knee space 0,73 m high under it), plus a cup filler.

Wall fixture: the wall is y = 0, the front -Y; on the floor, centred on X.
"""

from kit import *


def build():
    c = Component("Bebedouro", "plumbing", "bebedouro", "Plumbing")
    c.type("Bebedouro de pressão duplo acessível", "Bebedouro de pressão de aço inox de parede com duas cubas: uma a 1,00 m e outra "
           "acessível a 0,90 m com vão livre de 0,73 m, válvulas de jato e torneira para copo; água gelada (NBR 9050)")
    c.mep = {"Fixture": {"drain_units": 1, "supply_weight": 0.1, "hot_water": False}}
    c.connector("Água fria", "ColdWater", 0, 0, 0.6, "Back", 0.02)
    c.connector("Esgoto", "Sanitary", 0, 0, 0.45, "Back", 0.04)
    c.connector("Alimentação", "Power", 0.25, 0, 0.3, "Back")
    c.preview_size = (0.9, 0.5, 1.1)

    c.box("Bebedouro simplificado", -0.42, -0.45, 0.73, 0.84, 0.45, 0.32, "Inox escovado", detail=COARSE, in_plan=True)
    # Accessible basin at the left (top 0,90 m), standard basin at the right (top 1,00 m), the refrigeration box under the right.
    for name, x0, z in (("acessível", -0.42, 0.9), ("padrão", 0.0, 1.0)):
        c.box(f"Gabinete {name}", x0, -0.42, z - 0.12, 0.42, 0.42, 0.12, "Inox escovado", in_plan=True)
        c.box(f"Cuba {name}", x0 + 0.04, -0.38, z - 0.035, 0.34, 0.32, 0.036, "Inox escovado")
        c.rev(f"Ralo {name}", "Front", [(x0 + 0.21, z - 0.035), (x0 + 0.23, z - 0.035), (x0 + 0.23, z - 0.033), (x0 + 0.21, z - 0.033)], -0.22,
              x0 + 0.21, "Cromado", detail=FINE)
        c.cyl(f"Bico {name}", x0 + 0.21, -0.3, z - 0.035, 0.012, 0.05, "Cromado")
        c.box(f"Botão {name}", x0 + 0.15, -0.432, z - 0.08, 0.12, 0.012, 0.04, "Cromado")
    c.box("Unidade de refrigeração", 0.04, -0.36, 0.25, 0.34, 0.33, 0.6, "Inox escovado")
    c.box("Grade de ventilação", 0.08, -0.362, 0.32, 0.26, 0.002, 0.2, "Tela perfurada", detail=FINE)
    c.cyl("Torneira para copo", 0.33, -0.35, 1.0, 0.012, 0.12, "Cromado")
    c.box("Placa de fixação", -0.4, -0.01, 0.7, 0.8, 0.01, 0.36, "Inox escovado", detail=FINE)
    c.cyl("Sifão", -0.21, -0.12, 0.45, 0.016, 0.33, "Cromado", detail=FINE)
    return c
