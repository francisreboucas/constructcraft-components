"""Carro SUV: a compact sport utility vehicle of generic design (no brand, logo or real model).

4,45 m long, 1,84 m wide (2,04 m over the mirrors), 1,68 m high, wheelbase 2,66 m, 215/60 R17
tyres, higher ground clearance and roof rails. The body is lofted by `_carro` (see carro_hatch.py).
"""

from kit import FULL, Component
from _carro import BLACK, Car, build_car, shapes_mesh
from _moto import base as mb


def roof_rails(c, s, body, cab):
    """Two rails along the roof, on posts at their ends."""
    top = cab.indices(lambda p, nn: nn[1] > 0.9, 0)
    for side, sg in (("esquerda", 1), ("direita", -1)):
        x = sg * (cab.half - 0.14)
        pts = [cab.point(x, i) for i in range(top[0] + 2, top[1] - 1)]
        pts = [(p[0], p[1], p[2] + 0.05) for p in pts]
        posts = [mb.cyl((p[0], p[1], p[2] - 0.06), p, 0.014, 10) for p in (pts[0], pts[-1])]
        m = shapes_mesh(mb.tube(pts, 0.014, n=10), *posts)
        c._add(f"Rack de teto {side}", m.shape(), BLACK, FULL, False, False)


SPEC = Car(
    paint="Pintura azul metálica",
    WB=2.66, OF=0.88, OR=0.91, W=1.84,
    RT=0.345, TW=0.215, rim=0.216,
    gc=0.205, gc_front=0.25, gc_rear=0.26, z_front_bottom=0.33, z_rear_bottom=0.4,
    round_front=0.12, round_rear=0.06,
    top=[(2.24, 0.6), (2.25, 0.85), (2.22, 1.02), (2.12, 1.09), (1.8, 1.1), (0.6, 1.07), (-0.6, 1.04), (-1.1, 1.03),
         (-1.22, 1.02), (-1.6, 0.97), (-2.0, 0.92), (-2.17, 0.86), (-2.21, 0.74), (-2.215, 0.52)],
    z_belt=1.06,
    glass=[(2.12, 1.06), (2.09, 1.16), (1.95, 1.48), (1.7, 1.63), (1.0, 1.66), (0.0, 1.67), (-0.4, 1.645), (-0.7, 1.53), (-1.2, 1.06)],
    cabin_inset=0.05, tumble=0.1, yB=-0.12, y_glass_rear=1.45,
    head_z=(0.74, 0.84), head_w=0.42, grille_z=(0.56, 0.72), grille_w=0.42, plate_front_z=(0.42, 0.53),
    tail_z=(0.9, 1.05), tail_w=0.32, plate_rear_z=(0.66, 0.8),
    door_gaps=[-1.05, -0.13, 0.85], handles=[-0.3, 0.6], y_mirror=-1.08,
    z_floor=0.42, y_seat_front=-0.05, y_seat_rear=0.85, y_dash=-0.85,
    extras=roof_rails,
)


def build():
    c = Component("Carro SUV", "vehicles", "carro-suv", "Generic")
    c.type("Carro SUV compacto", "Utilitário esportivo (SUV) compacto, de desenho genérico: 4,45 m de comprimento, "
           "1,84 m de largura (2,04 m nos retrovisores), 1,72 m de altura com o rack de teto, entre-eixos de 2,66 m, "
           "pneus 215/60 R17, vão livre maior; a frente para -Y, a origem no chão no meio do entre-eixos")
    build_car(c, SPEC)
    c.preview_size = (2.04, 4.45, 1.72)
    return c
