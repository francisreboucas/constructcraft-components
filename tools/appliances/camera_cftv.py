"""Câmera de CFTV: a bullet security camera on a wall bracket, aimed down and forward.

Wall device: the wall is y = 0, the front -Y; the instance parameter Elevacao is the height of the bracket's centre.
"""

import math

from kit import *


def build():
    c = Component("Câmera de CFTV", "electrical", "camera-cftv", "Electrical")
    E = c.param("Elevacao", 2.6, "Length", True)
    c.type("Câmera bullet de CFTV", "Câmera de segurança tipo bullet IP com infravermelho, caixa de passagem e suporte de parede "
           "articulado; inclinada 20° para baixo")
    c.material("Lente", (16, 18, 26), "Glass", "Glossy")
    c.preview_size = (0.15, 0.35, 0.2)
    c.preview_base = 2.45

    def z(d):
        return f"{E} + {d}"

    c.box("Câmera simplificada", -0.04, -0.3, z(-0.05), 0.08, 0.3, 0.1, "Branco", detail=COARSE, in_plan=True)
    c.cyl_y("Caixa de passagem", 0, E, -0.035, 0.05, 0.035, "Branco")
    c.cyl_y("Braço do suporte", 0, E, -0.11, 0.012, 0.08, "Branco")
    c.rev("Articulação", "Front", [(0, z(-0.02)), (0.02, z(-0.02)), (0.022, z(0.0), 0.03), (0.02, z(0.02)), (0, z(0.02))], -0.115, 0,
          "Branco", detail=FINE)
    # The body: a cylinder along the view, tilted 20° down, with its sun shield.
    a = 20

    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))

    def tilt(s, n):  # (y, z) of the point s along the camera's axis (forward and down) and n across it (up), from the joint
        return (-0.115 - s * ca - n * sa, z(-s * sa + n * ca))

    pts = [tilt(0.02, -0.035), tilt(0.2, -0.035), tilt(0.2, 0.035), tilt(0.02, 0.035)]
    c.profile("Corpo da câmera", "Side", pts, -0.035, 0.07, "Branco", in_plan=True)
    c.profile("Para-sol", "Side", [tilt(0.04, 0.035), tilt(0.24, 0.035), tilt(0.24, 0.042), tilt(0.04, 0.042)], -0.042, 0.084, "Branco")
    c.profile("Lente", "Side", [tilt(0.2, -0.026), tilt(0.205, -0.026), tilt(0.205, 0.026), tilt(0.2, 0.026)], -0.026, 0.052, "Lente")
    c.profile("Infravermelho", "Side", [tilt(0.2, -0.032), tilt(0.203, -0.032), tilt(0.203, -0.028), tilt(0.2, -0.028)], -0.03, 0.06,
              "Plástico fumê", detail=FINE)
    return c
