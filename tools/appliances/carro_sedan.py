"""Carro sedã: a mid-size four-door sedan of generic design (no brand, logo or real model).

4,60 m long, 1,78 m wide (1,98 m over the mirrors), 1,46 m high, wheelbase 2,70 m, 205/55 R16
tyres, a separate trunk. The body is lofted by `_carro` (see carro_hatch.py).
"""

from kit import Component
from _carro import Car, build_car

SPEC = Car(
    paint="Pintura grafite metálica",
    WB=2.70, OF=0.92, OR=0.98, W=1.78,
    RT=0.316, TW=0.205, rim=0.2032,
    gc=0.15, gc_front=0.18, gc_rear=0.2, z_front_bottom=0.26, z_rear_bottom=0.34,
    round_front=0.13, round_rear=0.08,
    top=[(2.33, 0.54), (2.34, 0.78), (2.31, 0.94), (2.22, 1.0), (1.9, 1.02), (1.5, 1.0), (0.6, 0.96), (-0.6, 0.93), (-1.1, 0.915),
         (-1.25, 0.9), (-1.7, 0.82), (-2.1, 0.75), (-2.24, 0.7), (-2.27, 0.6), (-2.275, 0.44)],
    z_belt=0.95,
    glass=[(1.62, 0.97), (1.5, 1.05), (1.2, 1.3), (0.85, 1.43), (0.3, 1.46), (-0.2, 1.455), (-0.5, 1.42), (-0.75, 1.3), (-1.2, 0.95)],
    cabin_inset=0.04, tumble=0.12, yB=-0.12, y_glass_rear=1.15,
    head_z=(0.62, 0.71), head_w=0.4, grille_z=(0.5, 0.6), grille_w=0.4, plate_front_z=(0.37, 0.47),
    tail_z=(0.8, 0.94), tail_w=0.36, plate_rear_z=(0.58, 0.72),
    door_gaps=[-1.0, -0.13, 0.86], handles=[-0.3, 0.6], y_mirror=-1.08,
    z_floor=0.3, y_seat_front=-0.05, y_seat_rear=0.85, y_dash=-0.85,
)


def build():
    c = Component("Carro sedã", "vehicles", "carro-sedan", "Generic")
    c.type("Carro sedã médio", "Automóvel sedã médio de quatro portas, de desenho genérico: 4,60 m de comprimento, "
           "1,78 m de largura (1,98 m nos retrovisores), 1,46 m de altura, entre-eixos de 2,70 m, pneus 205/55 R16, "
           "porta-malas separado; a frente para -Y, a origem no chão no meio do entre-eixos")
    build_car(c, SPEC)
    c.preview_size = (1.98, 4.6, 1.46)
    return c
