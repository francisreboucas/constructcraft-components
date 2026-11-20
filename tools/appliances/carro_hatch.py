"""Carro hatch: a compact five-door hatchback of generic design (no brand, logo or real model).

3,90 m long, 1,72 m wide (1,92 m over the mirrors), 1,48 m high, wheelbase 2,50 m, 185/65 R15
tyres. The body is lofted by `_carro` from the profiles below (meters; front towards -Y,
origin on the ground in the middle of the wheelbase).
"""

from kit import Component
from _carro import Car, build_car

SPEC = Car(
    paint="Pintura prata metálica",
    WB=2.50, OF=0.78, OR=0.62, W=1.72,
    RT=0.31, TW=0.185, rim=0.1905,
    gc=0.155, gc_front=0.19, gc_rear=0.2, z_front_bottom=0.27, z_rear_bottom=0.33,
    round_front=0.12, round_rear=0.06,
    # the lower body's top, from the rear bumper over the tailgate's foot, the belt and the hood to the front face
    top=[(1.87, 0.52), (1.88, 0.72), (1.85, 0.9), (1.76, 0.98), (1.5, 0.99), (0.6, 0.965), (-0.6, 0.935), (-1.0, 0.92),
         (-1.12, 0.905), (-1.5, 0.84), (-1.82, 0.775), (-1.97, 0.725), (-2.025, 0.63), (-2.035, 0.45)],
    # the cabin: from the rear glass' foot over the roof to the windshield's foot
    z_belt=0.95,
    glass=[(1.78, 0.95), (1.74, 1.05), (1.56, 1.3), (1.32, 1.43), (0.8, 1.47), (0.0, 1.475), (-0.3, 1.45), (-0.56, 1.34), (-1.06, 0.95)],
    cabin_inset=0.04, tumble=0.12, yB=-0.05, y_glass_rear=1.22,
    head_z=(0.63, 0.72), head_w=0.36, grille_z=(0.53, 0.61), grille_w=0.36, plate_front_z=(0.39, 0.49),
    tail_z=(0.78, 0.95), tail_w=0.3, plate_rear_z=(0.55, 0.68),
    door_gaps=[-0.92, -0.06, 0.82], handles=[-0.22, 0.62], y_mirror=-0.95,
    z_floor=0.3, y_seat_front=0.0, y_seat_rear=0.85, y_dash=-0.75,
)


def build():
    c = Component("Carro hatch", "vehicles", "carro-hatch", "Generic")
    c.type("Carro hatch compacto", "Automóvel hatch compacto de cinco portas, de desenho genérico: 3,90 m de comprimento, "
           "1,72 m de largura (1,92 m nos retrovisores), 1,48 m de altura, entre-eixos de 2,50 m, pneus 185/65 R15; "
           "a frente para -Y, a origem no chão no meio do entre-eixos; para estudos de vagas, garagens e fachadas")
    build_car(c, SPEC)
    c.preview_size = (1.92, 3.9, 1.48)
    return c
