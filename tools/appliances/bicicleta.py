"""Bicicleta: an urban bicycle of generic design (no brand, logo or real model), 26" wheels.

1,78 m long, 0,62 m wide at the handlebar, 1,05 m high; diamond steel frame, rigid fork, flat
handlebar, single chainring, kickstand. Front towards -Y, the wheels on the ground (z = 0), the
origin in the middle of the wheelbase; the drivetrain on the right (-X).
"""

from __future__ import annotations

import math

from kit import ALL, COARSE, FINE, FULL, Component
from _carro import shapes_mesh
from _moto import base as mb
from _moto.base import v_add, v_mul, v_norm, v_sub

FRAME = "Pintura verde-água"
TYRE, RIM, CHROME, BLACK, LEATHER = "Borracha", "Alumínio polido", "Cromado", "Plástico preto", "Couro preto"

WB = 1.06
R_WHEEL = 0.335  # 26 x 1.95: the tyre's outer radius
RA = (0.0, WB / 2, R_WHEEL)  # rear axle
FA = (0.0, -WB / 2, R_WHEEL)  # front axle
BB = (0.0, 0.11, 0.3)  # bottom bracket
ST = (0.0, 0.3, 0.86)  # top of the seat tube
HT_TOP, HT_BOT = (0.0, -0.39, 0.88), (0.0, -0.44, 0.7)


def wheel(c, name, axle):
    rt, rr = R_WHEEL - 0.025, 0.025
    tyre = mb.lathe([(rt + rr * math.cos(2 * math.pi * k / 16), rr * math.sin(2 * math.pi * k / 16)) for k in range(16)],
                    axle, (1, 0, 0), n=48, closed=True)
    c._add(f"Pneu {name}", shapes_mesh(tyre).shape(), TYRE, FULL, True, False)
    rim = mb.lathe([(0.272, -0.011), (0.29, -0.012), (0.29, 0.012), (0.272, 0.011)], axle, (1, 0, 0), n=48, closed=True)
    hub = mb.lathe([(0, -0.05), (0.012, -0.05), (0.012, -0.035), (0.025, -0.034), (0.025, -0.028), (0.014, -0.026), (0.014, 0.026),
                    (0.025, 0.028), (0.025, 0.034), (0.012, 0.035), (0.012, 0.05), (0, 0.05)], axle, (1, 0, 0), n=20)
    c._add(f"Aro e cubo {name}", shapes_mesh(rim, hub).shape(), RIM, FULL, False, False)
    spokes = []
    for k in range(32):
        a = 2 * math.pi * k / 32
        side = 0.031 if k % 2 else -0.031
        b = a + (0.35 if k % 4 < 2 else -0.35)  # tangential lacing
        p0 = v_add(axle, (side, 0.024 * math.cos(b), 0.024 * math.sin(b)))
        p1 = v_add(axle, (0.0, 0.274 * math.cos(a), 0.274 * math.sin(a)))
        spokes.append(mb.cyl(p0, p1, 0.0012, 4))
    c._add(f"Raios {name}", shapes_mesh(*spokes).shape(), CHROME, FINE, False, False)
    c.cyl_x(f"Roda simplificada {name}", axle[1], axle[2], -0.025, R_WHEEL, 0.05, TYRE, detail=COARSE)


def build():
    c = Component("Bicicleta", "vehicles", "bicicleta", "Generic")
    c.material(FRAME, (52, 150, 140), "Metal", "Glossy")
    for name, spec in (("Alumínio polido", ((214, 217, 221), "Metal", "Polished", 0)), ("Couro preto", ((28, 23, 21), "Generic", "Satin", 0))):
        c.material(name, *spec)
    c.type("Bicicleta urbana aro 26", "Bicicleta urbana de desenho genérico, aro 26, quadro diamante de aço, garfo rígido, guidão reto, "
           "coroa única e descanso lateral: 1,78 m de comprimento, 0,62 m de largura no guidão, 1,05 m de altura; para "
           "bicicletários, garagens e estudos de vagas (a frente para -Y, a origem no chão no meio do entre-eixos)")
    c.preview_size = (0.62, 1.78, 1.05)

    # --- frame ---------------------------------------------------------------------------------------------
    r = 0.016
    tubes = [mb.tube([BB, ST], r), mb.tube([v_add(ST, (0, -0.02, -0.04)), v_add(HT_TOP, (0, 0, -0.03))], 0.014),
             mb.tube([BB, v_add(HT_BOT, (0, 0, 0.03))], 0.018), mb.cyl(HT_BOT, HT_TOP, 0.019)]
    for sx in (-1, 1):
        tubes.append(mb.tube([v_add(BB, (sx * 0.02, 0.02, 0)), v_add(RA, (sx * 0.065, 0, 0))], 0.009))
        tubes.append(mb.tube([v_add(ST, (sx * 0.015, 0.0, -0.05)), v_add(RA, (sx * 0.065, 0, 0.01))], 0.008))
        tubes.append(mb.tube([v_add(HT_BOT, (sx * 0.02, 0, 0)), v_add(HT_BOT, (sx * 0.055, -0.03, -0.1)), v_add(FA, (sx * 0.05, -0.04, 0.02)),
                              v_add(FA, (sx * 0.05, 0, 0))], 0.011, smooth=3))
    c._add("Quadro e garfo", shapes_mesh(*tubes).shape(), FRAME, ALL, True, False)

    # --- wheels ----------------------------------------------------------------------------------------------
    wheel(c, "dianteira", FA)
    wheel(c, "traseira", RA)

    # --- cockpit: steerer, stem, handlebar, grips, brake levers --------------------------------------------------
    d = v_norm(v_sub(HT_TOP, HT_BOT))
    top = v_add(HT_TOP, v_mul(d, 0.08))
    bar_c = v_add(top, (0, -0.08, 0.03))
    cock = [mb.cyl(HT_TOP, top, 0.014), mb.tube([top, bar_c], 0.016),
            mb.tube([(-0.3, bar_c[1] + 0.04, bar_c[2]), (-0.12, bar_c[1], bar_c[2]), (0.12, bar_c[1], bar_c[2]), (0.3, bar_c[1] + 0.04, bar_c[2])], 0.011)]
    c._add("Guidão e mesa", shapes_mesh(*cock).shape(), CHROME, FULL, True, False)
    grips = [mb.cyl((sx * 0.19, bar_c[1] + 0.024, bar_c[2]), (sx * 0.31, bar_c[1] + 0.042, bar_c[2]), 0.016, 12) for sx in (-1, 1)]
    levers = [mb.box((sx * 0.17, bar_c[1] - 0.05, bar_c[2] - 0.005), (0.09, 0.012, 0.02)) for sx in (-1, 1)]
    c._add("Manoplas e manetes", shapes_mesh(*grips, *levers).shape(), BLACK, FULL, False, False)

    # --- seat --------------------------------------------------------------------------------------------------
    post_top = v_add(ST, v_mul(v_norm(v_sub(ST, BB)), 0.12))
    c._add("Canote", shapes_mesh(mb.tube([ST, post_top], 0.0135)).shape(), CHROME, FULL, False, False)
    outline = [(0.0, -0.15), (0.035, -0.12), (0.05, -0.02), (0.09, 0.06), (0.1, 0.1), (0.07, 0.13), (0.0, 0.135),
               (-0.07, 0.13), (-0.1, 0.1), (-0.09, 0.06), (-0.05, -0.02), (-0.035, -0.12)]
    saddle = mb.prism(outline, (0.0, post_top[1] - 0.02, post_top[2]), (1, 0, 0), (0, 1, 0), (0, 0, 1), 0.0, 0.055)
    c._add("Selim", shapes_mesh(saddle).shape(), LEATHER, ALL, True, False)

    # --- drivetrain (right side, -X) -----------------------------------------------------------------------------
    xd = -0.055
    ring = mb.lathe([(0.075, -0.003), (0.095, -0.003), (0.095, 0.003), (0.075, 0.003)], (xd, BB[1], BB[2]), (1, 0, 0), n=40, closed=True)
    cog = mb.lathe([(0.02, -0.004), (0.04, -0.004), (0.04, 0.004), (0.02, 0.004)], (xd, RA[1], RA[2]), (1, 0, 0), n=24, closed=True)
    axle = mb.disc_x(-0.075, 0.075, BB[1], BB[2], 0.012)
    cranks = [mb.box(v_add(BB, (sx * 0.075, sx * 0.0, -sx * 0.085)), (0.012, 0.03, 0.18)) for sx in (-1, 1)]
    pedals = [mb.box(v_add(BB, (sx * 0.12, 0.0, -sx * 0.17)), (0.09, 0.06, 0.02)) for sx in (-1, 1)]
    c._add("Pedivela e coroa", shapes_mesh(ring, cog, axle, *cranks).shape(), CHROME, FULL, False, False)
    c._add("Pedais", shapes_mesh(*pedals).shape(), BLACK, FULL, False, False)
    # The chain: the two straight runs between the chainring and the cog, as thin bands.
    chain = []
    for zf, zr in ((0.093, 0.038), (-0.093, -0.038)):
        a, b = (xd, BB[1], BB[2] + zf), (xd, RA[1], RA[2] + zr)
        chain.append(mb.box(v_mul(v_add(a, b), 0.5), (0.007, math.dist(a, b), 0.009),
                            ((1, 0, 0), v_norm(v_sub(b, a)), mb.v_cross((1, 0, 0), v_norm(v_sub(b, a))))))
    c._add("Corrente", shapes_mesh(*chain).shape(), "Ferro fundido", FINE, False, False)

    # --- kickstand (left side) -------------------------------------------------------------------------------------
    k0 = v_add(BB, (0.03, 0.1, 0.0))
    stand = mb.tube([k0, (0.16, 0.42, 0.012)], 0.008)
    c._add("Descanso", shapes_mesh(stand).shape(), BLACK, FULL, False, False)
    return c
