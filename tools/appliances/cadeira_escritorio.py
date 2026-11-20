"""Cadeira de escritório giratória: an operator's swivel chair of generic design.

Five-star nylon base on twin-wheel casters, gas lift, synchro mechanism, an upholstered seat with a waterfall front, an
upholstered backrest with lumbar support on a steel bar, and T-armrests. 0,66 m across the base, seat 0,48 m high,
1,05 m high; the front towards -Y, the origin on the floor at the column.
"""

from __future__ import annotations

import math

from kit import ALL, COARSE, FINE, FULL, Component
from _carro import shapes_mesh, slab
from _escritorio import declare
from _moto import base as mb

FABRIC, PLASTIC, CHROME = "Tecido estofado preto", "Plástico preto", "Cromado"


def squircle(u, v, s=0.75):
    """The square [-1, 1]² eased towards a disc (rounded corners)."""
    return u * math.sqrt(1 - s * v * v / 2), v * math.sqrt(1 - s * u * u / 2)


def cushion(frame, thick, n=14, wall=0.4, crown=0.0):
    """A cushion over the surface frame(u, v) -> (point, normal), u, v in [-1, 1]: full `thick` inside, `wall` of it at the edge."""
    top, bot = [], []
    for i in range(n + 1):
        v = -1 + 2 * i / n
        rt, rb = [], []
        for j in range(n + 1):
            u = -1 + 2 * j / n
            pt, nn = frame(u, v)
            rr = (u ** 4 + v ** 4) ** 0.25
            h = thick * (wall + (1 - wall) * math.sqrt(max(0.0, 1 - min(1.0, rr) ** 8))) + crown * (1 - u * u) * (1 - v * v)
            rb.append(pt)
            rt.append(mb.v_add(pt, mb.v_mul(nn, h)))
        top.append(rt)
        bot.append(rb)
    return slab(top, bot)


def build():
    c = Component("Cadeira de escritório giratória", "furniture", "cadeira-escritorio")
    declare(c, FABRIC)
    c.type("Cadeira giratória operativa", "Cadeira de escritório giratória de desenho genérico: base de cinco pás de náilon com "
           "rodízios duplos, pistão a gás, mecanismo sincronizado, assento e encosto estofados com apoio lombar e braços em T; "
           "0,66 m de diâmetro na base, assento a 0,48 m, 1,05 m de altura (a frente para -Y)")
    c.preview_size = (0.66, 0.66, 1.05)

    # --- coarse stand-ins ----------------------------------------------------------------------------------------
    c.cyl("Base simplificada", 0, 0, 0, 0.33, 0.12, PLASTIC, detail=COARSE, in_plan=True)
    c.cyl("Coluna simplificada", 0, 0, 0.12, 0.03, 0.3, PLASTIC, detail=COARSE)
    c.box("Assento simplificado", -0.25, -0.26, 0.42, 0.5, 0.48, 0.07, FABRIC, detail=COARSE, in_plan=True)
    c.box("Encosto simplificado", -0.23, 0.2, 0.58, 0.46, 0.07, 0.48, FABRIC, detail=COARSE)

    # --- five-star base ---------------------------------------------------------------------------------------------
    arms, tips, casters, wheels = [], [], [], []
    for k in range(5):
        a = math.radians(-90 + 72 * k)
        d = (math.cos(a), math.sin(a), 0.0)
        s = (-math.sin(a), math.cos(a), 0.0)
        # The arm: a ribbed section that thins and drops towards the tip.
        sec = [(-0.022, -0.012), (0.022, -0.012), (0.019, 0.01), (0.006, 0.02), (-0.006, 0.02), (-0.019, 0.01)]
        path = [(0.035 * d[0], 0.035 * d[1], 0.12), (0.17 * d[0], 0.17 * d[1], 0.112), (0.3 * d[0], 0.3 * d[1], 0.095)]
        arms.append(mb.sweep(path, sec, up=s, scale=[1.0, 0.9, 0.75]))
        tip = (0.3 * d[0], 0.3 * d[1], 0.0)
        tips.append(mb.cyl(mb.v_add(tip, (0, 0, 0.078)), mb.v_add(tip, (0, 0, 0.108)), 0.02, 20))
        # Twin-wheel caster: stem, hood and two wheels on an axle across the arm.
        ctr = mb.v_add(tip, mb.v_mul(d, 0.022))
        casters.append(mb.cyl(mb.v_add(tip, (0, 0, 0.06)), mb.v_add(tip, (0, 0, 0.08)), 0.008, 12))
        casters.append(mb.box(mb.v_add(ctr, (0, 0, 0.046)), (0.05, 0.016, 0.03), (d, s, (0, 0, 1))))
        for side in (-1, 1):
            o = mb.v_add((ctr[0], ctr[1], 0.025), mb.v_mul(s, side * 0.016))
            wheels.append(mb.cyl(mb.v_sub(o, mb.v_mul(s, 0.007)), mb.v_add(o, mb.v_mul(s, 0.007)), 0.025, 24))
    hub = mb.lathe([(0, 0.1), (0.05, 0.1), (0.052, 0.13), (0.035, 0.145), (0, 0.145)], (0, 0, 0), (0, 0, 1), n=40)
    c._add("Base de cinco pás", shapes_mesh(hub, *arms, *tips).shape(), PLASTIC, FULL, True, False)
    c._add("Rodízios - carenagens", shapes_mesh(*casters).shape(), PLASTIC, FULL, False, False)
    c._add("Rodízios - rodas", shapes_mesh(*wheels).shape(), "Borracha", FULL, False, False)

    # --- gas lift and mechanism ---------------------------------------------------------------------------------------
    cover = mb.lathe([(0, 0.14), (0.03, 0.14), (0.03, 0.2), (0.027, 0.205), (0.027, 0.26), (0.024, 0.265), (0.024, 0.31), (0, 0.31)],
                     (0, 0, 0), (0, 0, 1), n=32)
    c._add("Capa telescópica do pistão", shapes_mesh(cover).shape(), PLASTIC, FULL, False, False)
    c._add("Pistão a gás", shapes_mesh(mb.cyl((0, 0, 0.3), (0, 0, 0.4), 0.014, 20)).shape(), CHROME, FULL, False, False)
    mech = [mb.box((0, 0.0, 0.405), (0.2, 0.24, 0.035)), mb.box((0, 0.02, 0.385), (0.1, 0.12, 0.02))]
    lever = [mb.tube([(-0.09, -0.02, 0.4), (-0.2, -0.04, 0.395), (-0.24, -0.08, 0.39)], 0.006, smooth=3),
             mb.sphere((-0.245, -0.085, 0.39), 0.013, 8)]
    knob = mb.lathe([(0, 0), (0.025, 0), (0.025, 0.03), (0, 0.035)], (0, -0.08, 0.385), (0, -1, 0), n=20)
    c._add("Mecanismo", shapes_mesh(*mech).shape(), "Aço pintado preto", FULL, False, False)
    c._add("Alavanca e manípulo", shapes_mesh(*lever, knob).shape(), PLASTIC, FINE, False, False)

    # --- seat: a plastic shell and the cushion with a waterfall front ---------------------------------------------------
    def seat_frame(z0, half_w, half_d, yc):
        def f(u, v):
            x, y = squircle(u, v)
            y = yc + y * half_d
            # The front (v -> -1) curls down: the waterfall edge.
            fall = max(0.0, -v - 0.55) ** 2 * 0.12
            return (x * half_w, y, z0 + 0.012 * (1 - u * u) * 0 - fall), (0.0, 0.0, 1.0)
        return f

    shell = cushion(seat_frame(0.425, 0.245, 0.235, -0.02), 0.018, wall=1.0)
    seat = cushion(seat_frame(0.443, 0.25, 0.24, -0.02), 0.06, wall=0.45, crown=0.008)
    c._add("Assento - concha", shell.shape(), PLASTIC, FULL, False, False)
    c._add("Assento - estofado", seat.shape(), FABRIC, ALL, True, False)

    # --- backrest: curved in plan, with a lumbar bulge, reclined ----------------------------------------------------------
    zb0, zb1 = 0.6, 1.05

    def back_frame(off):
        def f(u, v):
            x, t = squircle(u, v, 0.6)
            z = zb0 + (t + 1) / 2 * (zb1 - zb0)
            half = 0.22 + 0.02 * math.sin(math.pi * (t + 1) / 2)  # wider at the shoulders
            xx = x * half
            lumbar = 0.025 * math.exp(-((z - 0.72) / 0.08) ** 2)
            y = 0.2 + (z - zb0) * 0.2 - 0.6 * xx * xx - lumbar + off
            n = mb.v_norm((1.2 * xx, -1.0, 0.2))  # roughly the inward (towards -Y) normal
            return (xx, y, z), n
        return f

    bshell = cushion(back_frame(0.0), 0.016, wall=1.0)
    back = cushion(back_frame(-0.016), 0.05, wall=0.45, crown=0.006)
    c._add("Encosto - concha", bshell.shape(), PLASTIC, FULL, False, False)
    c._add("Encosto - estofado", back.shape(), FABRIC, ALL, False, False)

    # The steel bar from the mechanism to the back of the shell.
    bar = mb.sweep(mb.catmull([(0, 0.1, 0.405), (0, 0.235, 0.41), (0, 0.255, 0.5), (0, 0.212, 0.62), (0, 0.205, 0.7), (0, 0.22, 0.78)], 4),
                   [(-0.03, -0.007), (0.03, -0.007), (0.03, 0.007), (-0.03, 0.007)], up=(1, 0, 0))
    c._add("Lâmina do encosto", shapes_mesh(bar).shape(), "Aço pintado preto", FULL, False, False)

    # --- T-armrests --------------------------------------------------------------------------------------------------------
    supports, pads = [], []
    for sx in (-1, 1):
        x = sx * 0.275
        supports.append(mb.sweep(mb.catmull([(sx * 0.09, 0.02, 0.4), (sx * 0.2, 0.02, 0.4), (x, 0.03, 0.45), (x, 0.04, 0.66)], 4),
                                 [(-0.03, -0.008), (0.03, -0.008), (0.03, 0.008), (-0.03, 0.008)], up=(0, 1, 0)))
        pads.append(mb.prism(mb.rrect2(0.075, 0.25, 0.03, 4), (x, 0.0, 0.66), (1, 0, 0), (0, 1, 0), (0, 0, 1), 0.0, 0.028))
    c._add("Braços - suportes", shapes_mesh(*supports).shape(), PLASTIC, FULL, False, False)
    c._add("Braços - apoios", shapes_mesh(*pads).shape(), "Borracha", FULL, True, False)
    return c
