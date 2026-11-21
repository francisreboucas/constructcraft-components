"""Pessoa em cadeira de rodas: a generic figure in a manual folding wheelchair, with the NBR 9050 reference module
(0,80 x 1,20 m) drawn in plan around it."""

from __future__ import annotations

import math

from kit import COARSE, FINE, FULL, Component
from _carro import shapes_mesh
from _moto import base as mb
from _pessoa import add_figure, declare

MATERIALS = {"skin": "Pele morena", "hair": "Cabelo castanho", "top": "Tecido azul-marinho", "bottom": "Jeans", "shoes": "Couro preto"}
FRAME, SEAT, TYRE, RIM = "Alumínio anodizado", "Tecido cinza-chumbo", "Borracha", "Alumínio polido"

YA = 0.1  # rear axle, behind the origin
R_WHEEL = 0.3  # 24" rear wheels
XW = 0.31  # rear wheels' mid planes
SEAT_Z = 0.48


def build():
    c = Component("Pessoa em cadeira de rodas", "people", "cadeirante", "Generic")
    declare(c, {**MATERIALS, "seat": SEAT})
    c.material("Alumínio polido", (214, 217, 221), "Metal", "Polished")
    c.type("Pessoa em cadeira de rodas", "Figura genérica de pessoa em cadeira de rodas manual dobrável (rodas aro 24, 0,66 m de "
           "largura, 1,05 m de comprimento), com o módulo de referência de 0,80 x 1,20 m da NBR 9050 desenhado em planta; para "
           "verificar circulação, áreas de manobra e aproximação (a frente para -Y)")
    c.preview_size = (0.8, 1.2, 1.3)

    add_figure(c, MATERIALS, H=1.70, pose="wheel", sleeves="long", hair="short")

    # --- wheelchair ------------------------------------------------------------------------------------------------
    wheels, rims, frame, spokes = [], [], [], []
    for s in (-1, 1):
        x = s * XW
        axle = (x, YA, R_WHEEL)
        wheels.append(mb.lathe([(R_WHEEL - 0.02 + 0.02 * math.cos(2 * math.pi * k / 12), 0.016 * math.sin(2 * math.pi * k / 12))
                                for k in range(12)], axle, (1, 0, 0), n=40, closed=True))
        rims.append(mb.lathe([(0.25, -0.01), (0.27, -0.01), (0.27, 0.01), (0.25, 0.01)], axle, (1, 0, 0), n=40, closed=True))
        # Push rim, outboard of the wheel, on three standoffs.
        xr = x + s * 0.035
        rims.append(mb.lathe([(0.265 + 0.007 * math.cos(2 * math.pi * k / 8), 0.007 * math.sin(2 * math.pi * k / 8)) for k in range(8)],
                             (xr, YA, R_WHEEL), (1, 0, 0), n=36, closed=True))
        rims.append(mb.cyl((x - s * 0.04, YA, R_WHEEL), (xr, YA, R_WHEEL), 0.02, 16))
        for k in range(18):
            a = 2 * math.pi * k / 18
            spokes.append(mb.cyl((x + (0.012 if k % 2 else -0.012), YA, R_WHEEL),
                                 (x, YA + 0.25 * math.cos(a), R_WHEEL + 0.25 * math.sin(a)), 0.0015, 4))
        # Side frame: from the front caster up to the seat rail, down the back to the axle plate, the backrest upright
        # with its push handle, the footrest hanger.
        xs = s * 0.235
        frame.append(mb.tube([(xs, -0.3, 0.2), (xs, -0.28, SEAT_Z - 0.03), (xs, 0.12, SEAT_Z - 0.03)], 0.012, smooth=2))
        frame.append(mb.tube([(xs, 0.12, SEAT_Z - 0.03), (xs, 0.16, 0.92), (xs, 0.25, 0.94)], 0.012, smooth=3))
        frame.append(mb.tube([(xs, -0.28, SEAT_Z - 0.06), (xs, -0.42, 0.14)], 0.011))
        frame.append(mb.tube([(xs, -0.3, 0.2), (xs, 0.12, 0.26), (xs, YA, R_WHEEL)], 0.011))
        frame.append(mb.box((xs + s * 0.02, YA, R_WHEEL), (0.045, 0.08, 0.06)))
        frame.append(mb.cyl((xs, 0.25, 0.94), (xs, 0.33, 0.95), 0.016, 12))  # handle grip
        # Front caster: fork stem, fork and a small wheel.
        cx = s * 0.235
        frame.append(mb.cyl((cx, -0.3, 0.2), (cx, -0.3, 0.13), 0.012, 12))
        frame.append(mb.box((cx, -0.32, 0.1), (0.03, 0.03, 0.06)))
        wheels.append(mb.lathe([(0.0, -0.012), (0.075, -0.012), (0.075, 0.012), (0.0, 0.012)], (cx, -0.34, 0.075), (1, 0, 0), n=24))
        # Footplate.
        frame.append(mb.box((s * 0.12, -0.45, 0.13), (0.2, 0.13, 0.012)))
    # Cross brace under the seat.
    frame.append(mb.tube([(-0.235, -0.1, SEAT_Z - 0.04), (0.235, 0.1, 0.27)], 0.009))
    frame.append(mb.tube([(0.235, -0.1, SEAT_Z - 0.04), (-0.235, 0.1, 0.27)], 0.009))
    c._add("Cadeira - pneus e rodízios", shapes_mesh(*wheels).shape(), TYRE, FULL, True, False)
    c._add("Cadeira - aros", shapes_mesh(*rims).shape(), RIM, FULL, False, False)
    c._add("Cadeira - raios", shapes_mesh(*spokes).shape(), RIM, FINE, False, False)
    c._add("Cadeira - quadro", shapes_mesh(*frame).shape(), FRAME, FULL, True, False)
    seat = [mb.box((0, -0.08, SEAT_Z - 0.02), (0.44, 0.42, 0.012)), mb.box((0, 0.15, 0.7), (0.44, 0.015, 0.4),
                                                                          ((1, 0, 0), (0, math.cos(0.1), -math.sin(0.1)), (0, math.sin(0.1), math.cos(0.1))))]
    c._add("Cadeira - assento e encosto", shapes_mesh(*seat).shape(), SEAT, FULL, False, False)
    # Coarse stand-ins of the chair.
    simple = [mb.disc_x(s * XW - 0.02, s * XW + 0.02, YA, R_WHEEL, R_WHEEL, 12) for s in (-1, 1)]
    simple.append(mb.box((0, -0.08, SEAT_Z - 0.03), (0.47, 0.44, 0.04)))
    simple.append(mb.box((0, 0.15, 0.7), (0.47, 0.03, 0.42)))
    c._add("Cadeira simplificada", shapes_mesh(*simple).shape(), FRAME, COARSE, True, False)

    # --- the NBR 9050 reference module, a plan symbol: 0,80 x 1,20 m around the chair ----------------------------------
    y0, y1 = -0.62, 0.58
    for name, x, y, w, d in (("frente", -0.4, y0, 0.8, 0.01), ("trás", -0.4, y1 - 0.01, 0.8, 0.01),
                             ("esquerda", -0.4, y0, 0.01, 1.2), ("direita", 0.39, y0, 0.01, 1.2)):
        c.box(f"Módulo de referência - {name}", x, y, 0, w, d, 0.001, FRAME)
        c.plan_only(f"Módulo de referência - {name}")
    return c
