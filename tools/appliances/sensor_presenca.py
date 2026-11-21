"""Sensor de presença de teto: a ceiling PIR occupancy sensor with a 360° lens dome.

Ceiling device: the ceiling is z = 0 and the sensor hangs below it; place it with the base offset at the ceiling height.
"""

from kit import *


def build():
    c = Component("Sensor de presença de teto", "electrical", "sensor-presenca", "Electrical")
    c.type("Sensor de presença 360°", "Sensor de presença infravermelho passivo de sobrepor no teto, 360°, alcance de 6 m de "
           "diâmetro a 2,5 m de altura, com fotocélula e temporizador; comanda a iluminação do ambiente")
    c.preview_size = (0.12, 0.12, 0.06)
    c.preview_base = -0.06

    c.cyl("Sensor simplificado", 0, 0, -0.045, 0.055, 0.045, "Branco", detail=COARSE, in_plan=True)
    c.rev("Base", "Front", [(0, 0), (0.055, 0), (0.055, -0.004), (0.05, -0.022), (0, -0.022)], 0, 0, "Branco", in_plan=True)
    c.rev("Lente", "Front", [(0, -0.022), (0.03, -0.022), (0.03, -0.028), (0.026, -0.04, 0.03), (0, -0.046)], 0, 0, "Plástico translúcido")
    for k in range(3):
        c.cyl(f"Ajuste {k + 1}", f"0.04*cos({120 * k})", f"0.04*sin({120 * k})", -0.0225, 0.004, 0.001, "Plástico cinza", detail=FINE)
    return c
