"""Pictograms and arrows of the floor markings, drawn with shapely and encoded as figures.

Every figure is designed in its own units and written as integers (see
fonte.py for the encoding); the scripts of tools/site/ scale them.

- Arrows ("seta_*") follow the shapes of the Brazilian lane-use arrows
  (Manual Brasileiro de Sinalização de Trânsito, Volume IV, sinalização
  horizontal) as a driver sees them: drawn here undistorted, 10 units long
  (x 100), the stem 1.2 wide, the head 3.6 wide and 3 long, with the stem on
  x = 0 and the arrow from y = 0 to y <= 1000. The scripts stretch them along
  the direction of travel.
- The International Symbol of Access ("cadeirante") and the bicycle
  ("bicicleta") are drawn on a 100 unit grid (x 10) and centred on the origin.
"""

from __future__ import annotations

import math

from shapely.affinity import scale, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from fonte import encode_shape, polygons

S = 0.6  # half the stem's width
HW = 1.8  # half the head's width
HL = 3.0  # length of the head
RI = 1.0  # inner radius of the bends
RO = RI + 2 * S


def head(tip: tuple[float, float], direction: tuple[float, float]) -> Polygon:
    dx, dy = direction
    bx, by = tip[0] - dx * HL, tip[1] - dy * HL
    return Polygon([tip, (bx - dy * HW, by + dx * HW), (bx + dy * HW, by - dx * HW)])


def sector(cx: float, cy: float, r0: float, r1: float, a0: float, a1: float, n: int = 28) -> Polygon:
    """An annulus sector from a0 to a1 degrees (counter-clockwise)."""
    outer = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)), cy + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return Polygon(outer + inner)


def turn_right(at: float) -> Polygon:
    """A branch leaving the stem at height `at` and turning to the right, with its head."""
    cx, cy = S + RI, at
    arm_end = cx + 0.9
    mid = cy + RI + S
    return unary_union([
        sector(cx, cy, RI, RO, 90, 180),
        box(cx - 0.01, cy + RI, arm_end, cy + RO),
        head((arm_end + HL, mid), (1, 0)),
    ])


def mirror(shape):
    return scale(shape, -1, 1, origin=(0, 0))


def arrows() -> dict:
    stem = lambda top: box(-S, 0, S, top)  # noqa: E731
    straight = unary_union([stem(10 - HL + 0.01), head((0, 10), (0, 1))])
    right = unary_union([stem(5.4), turn_right(5.4)])
    straight_right = unary_union([straight, turn_right(2.6)])
    both = unary_union([stem(4.6), turn_right(4.6), mirror(turn_right(4.6))])
    cx = -(S + RI)
    u_turn = unary_union([
        stem(6.2),
        sector(cx, 6.2, RI, RO, 0, 180),
        box(cx - RO, 5.2, cx - RI, 6.21),
        head((cx - RI - S, 5.2 - HL), (0, -1)),
    ])
    shapes = {
        "seta_frente": straight,
        "seta_direita": right,
        "seta_esquerda": mirror(right),
        "seta_frente_direita": straight_right,
        "seta_frente_esquerda": mirror(straight_right),
        "seta_direita_esquerda": both,
        "seta_retorno": u_turn,
    }
    return {k: encode_shape(polygons(v, 100)) for k, v in shapes.items()}


def stroke(points, width: float, round_caps: bool = True):
    return LineString(points).buffer(width / 2, cap_style="round" if round_caps else "flat", join_style="round", quad_segs=10)


def arc(cx, cy, r, a0, a1, width, n=48):
    pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return LineString(pts).buffer(width / 2, cap_style="flat", join_style="round", quad_segs=10)


def centred(shape):
    x0, y0, x1, y1 = shape.bounds
    return translate(shape, -(x0 + x1) / 2, -(y0 + y1) / 2)


def wheelchair():
    """The International Symbol of Access (ISO 7001 PI PF 006), facing right."""
    return centred(unary_union([
        Point(44, 88).buffer(8.5, quad_segs=16),
        stroke([(41.5, 74), (44, 47)], 10.5),
        stroke([(43, 64), (63, 64)], 8),
        stroke([(44, 46.5), (67, 46.5)], 10.5),
        stroke([(67, 46.5), (76.5, 21)], 9.5),
        stroke([(76.5, 21), (84, 21)], 7),
        arc(42, 33, 24.5, 78, 345, 7.5),
    ]))


def bicycle():
    """A bicycle seen from its left side, facing right (the cycle lane pictogram)."""
    w = 3.6
    rear, front, crank, seat, headset = (21, 26), (79, 26), (45, 26), (39, 54), (70, 56)
    return centred(unary_union([
        Point(*rear).buffer(18.5, quad_segs=24).difference(Point(*rear).buffer(14.5, quad_segs=24)),
        Point(*front).buffer(18.5, quad_segs=24).difference(Point(*front).buffer(14.5, quad_segs=24)),
        stroke([rear, crank, seat, rear], w),
        stroke([seat, headset, crank], w),
        stroke([headset, front], w),
        stroke([headset, (68, 64), (76, 66.5)], w),
        stroke([seat, (37.5, 61)], w),
        stroke([(31, 62.5), (44, 62.5)], 4.6),
        Point(*crank).buffer(4.2, quad_segs=12),
        stroke([(45, 26), (49.5, 19.5)], 3.2),
    ]))


def pictograms() -> dict:
    return {
        "cadeirante": encode_shape(polygons(wheelchair(), 10)),
        "bicicleta": encode_shape(polygons(bicycle(), 10)),
    }


def all_figures() -> dict:
    return {**arrows(), **pictograms()}
