"""Moto custom: a custom (cruiser) motorcycle of generic design, 1600 cm3 air-cooled V-twin.

Double-cradle tube frame, raked telescopic fork, wire-spoke wheels (21" front, wide 16" rear),
teardrop tank, solo seat, dual exhausts, pulled-back handlebar. No brand, logo or real model.

The parts live in the `_moto` package (make.py skips it): `base` (hardpoints, materials, mesh
kernel, moving-parts script), `chassi` (frame, front end, swingarm, wheels, brakes, belt, stand),
`motor` (engine, gearbox, primary, intake, exhaust) and `carroceria` (tank, seat, fenders, lights,
controls, handlebar, cables); `preview.py` renders it from any side. The steering (AnguloGuidao)
and the side stand (Descanso) are instance parameters, built by the component's Lua script piece.
"""

from __future__ import annotations

import importlib

from _moto import base
from _moto.base import HP, MotoComponent

PARTS = ("chassi", "motor", "carroceria")


def build(parts=None):
    c = MotoComponent("Moto custom", "vehicles", "moto-custom", "Generic")
    c.angle("AnguloGuidao", 0, open_at=25)
    c.param("Descanso", 0, "Number", True)
    c.open_pose["Descanso"] = 1
    c.type("Moto custom 1600", "Motocicleta custom (cruiser) genérica, motor V2 1600 cm³ arrefecido a ar, transmissão "
           "final por correia; 2,39 m de comprimento, 0,85 m de largura nos retrovisores, entre-eixos 1,665 m, rodas raiadas "
           "21\" e 16\", assento a 0,68 m; guidão (AnguloGuidao) e descanso lateral (Descanso) móveis")
    base.declare_materials(c)
    # make.py aims its cameras at this box: the whole bike, mirrors included (x +-0.424, y -1.189..1.198, z 0..1.394)
    c.preview_size = (0.85, 2.39, 1.40)
    c.preview_base = 0.0
    for name in parts or PARTS:
        try:
            module = importlib.import_module(f"_moto.{name}")
        except ModuleNotFoundError as err:
            if err.name == f"_moto.{name}":
                continue
            raise
        module.add(c, HP)
    return c
