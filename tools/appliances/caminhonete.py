"""Caminhonete: a mid-size double-cab pickup of generic design (no brand, logo or real model).

5,30 m long, 1,86 m wide (2,06 m over the mirrors), 1,82 m high, wheelbase 3,10 m, 245/70 R16
tyres; the bed is closed by a tonneau cover (capota marítima). The body is lofted by `_carro`
(see carro_hatch.py); here the lower body runs at the bed rails' height to the tailgate.
"""

from kit import FINE, FULL, Component
from _carro import BLACK, CHROME, Car, build_car, shapes_mesh
from _moto import base as mb


def bed(c, s, body, cab):
    """The tonneau cover over the bed, the rail caps and the rear step."""
    y0, y1, zt = s.bed_y0, s.yR - 0.07, s.bed_z
    w = s.W / 2 - 0.075
    cover = shapes_mesh(mb.box((0, (y0 + y1) / 2, zt + 0.012), (2 * w, y1 - y0, 0.024)))
    c._add("Capota marítima", cover.shape(), BLACK, FULL, False, False)
    caps = shapes_mesh(*[mb.box((sg * (w + 0.03), (y0 + y1) / 2, zt + 0.006), (0.05, y1 - y0, 0.012)) for sg in (1, -1)])
    c._add("Proteção das bordas da caçamba", caps.shape(), BLACK, FINE, False, False)
    step = shapes_mesh(mb.box((0, s.yR + 0.03, s.z_rear_bottom + 0.06), (1.2, 0.1, 0.05)))
    c._add("Estribo traseiro", step.shape(), CHROME, FULL, False, False)


SPEC = Car(
    paint="Pintura vermelha automotiva",
    WB=3.10, OF=0.95, OR=1.25, W=1.86,
    RT=0.375, TW=0.245, rim=0.2032,
    gc=0.22, gc_front=0.27, gc_rear=0.3, z_front_bottom=0.38, z_rear_bottom=0.5,
    round_front=0.12, round_rear=0.03,
    bed_y0=0.86, bed_z=1.15,
    top=[(2.8, 0.66), (2.81, 0.9), (2.79, 1.08), (2.72, 1.15), (2.2, 1.155), (-0.6, 1.13), (-1.2, 1.12),
         (-1.35, 1.11), (-1.8, 1.08), (-2.3, 1.05), (-2.45, 0.98), (-2.5, 0.85), (-2.505, 0.6)],
    z_belt=1.13,
    glass=[(0.78, 1.12), (0.78, 1.2), (0.76, 1.58), (0.65, 1.77), (0.2, 1.8), (-0.4, 1.8), (-0.7, 1.77), (-0.95, 1.62), (-1.38, 1.12)],
    cabin_inset=0.05, tumble=0.1, yB=-0.3, y_glass_rear=0.6,
    head_z=(0.86, 0.98), head_w=0.42, grille_z=(0.62, 0.84), grille_w=0.45, plate_front_z=(0.45, 0.57),
    tail_z=(0.8, 1.1), tail_w=0.1, plate_rear_z=(0.7, 0.84),
    door_gaps=[-1.25, -0.31, 0.72], handles=[-0.48, 0.48], y_mirror=-1.25,
    z_floor=0.5, y_seat_front=-0.2, y_seat_rear=0.5, y_dash=-1.02,
    extras=bed,
)


def build():
    c = Component("Caminhonete cabine dupla", "vehicles", "caminhonete", "Generic")
    c.type("Caminhonete média cabine dupla", "Picape média de cabine dupla, de desenho genérico: 5,30 m de comprimento, "
           "1,86 m de largura (2,06 m nos retrovisores), 1,82 m de altura, entre-eixos de 3,10 m, pneus 245/70 R16, "
           "caçamba com capota marítima; a frente para -Y, a origem no chão no meio do entre-eixos")
    build_car(c, SPEC)
    c.preview_size = (2.06, 5.3, 1.82)
    return c
