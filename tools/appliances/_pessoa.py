"""Generic human figures for scale: a posed skeleton dressed in simple clothes.

Not a component module. A figure is built twice: smooth for the medium and fine levels, low-poly for the coarse one.
The figure faces -Y with its feet on z = 0 and its origin between the feet (sitting: under the hips). No real person
is depicted: the faces are featureless, the bodies average adult or child proportions.
"""

from __future__ import annotations

import math

from kit import COARSE, FULL
from _carro import shapes_mesh
from _moto import base as mb
from _moto.base import Mesh, v_add, v_len, v_mul, v_norm, v_sub

HREF = 1.70  # the joints below are those of a 1,70 m adult; other heights scale them

# Torso rings of a standing adult: z, half width, half depth, y offset (front is -y).
TORSO_M = [(0.80, 0.12, 0.09, 0.0), (0.86, 0.165, 0.11, 0.005), (0.93, 0.172, 0.112, 0.01), (1.00, 0.155, 0.1, 0.0),
           (1.06, 0.148, 0.097, -0.004), (1.15, 0.158, 0.105, -0.01), (1.25, 0.172, 0.115, -0.01), (1.34, 0.183, 0.108, 0.0),
           (1.40, 0.182, 0.094, 0.01), (1.45, 0.13, 0.075, 0.015), (1.49, 0.058, 0.055, 0.015)]
TORSO_F = [(0.80, 0.125, 0.09, 0.0), (0.86, 0.178, 0.112, 0.008), (0.93, 0.18, 0.112, 0.012), (1.00, 0.148, 0.095, 0.0),
           (1.06, 0.128, 0.088, -0.004), (1.15, 0.14, 0.1, -0.012), (1.24, 0.158, 0.122, -0.022), (1.33, 0.162, 0.108, -0.006),
           (1.40, 0.165, 0.09, 0.008), (1.45, 0.12, 0.072, 0.014), (1.49, 0.055, 0.052, 0.015)]
BELT = 1.0  # z of the waistband on a standing adult: below it the bottom garment


def pose_joints(pose: str, female=False):
    """Joint positions of a 1,70 m adult in `pose`: 'stand', 'walk', 'sit' (seat at 0,45 m) or 'wheel' (seat at 0,48 m)."""
    sh = 0.17 if female else 0.185
    j = {"pelvis": (0.0, 0.0, 0.9), "lean": 0.0}
    for s, x in (("L", 1), ("R", -1)):
        j[f"hip{s}"] = (x * 0.088, 0.0, 0.9)
        j[f"knee{s}"] = (x * 0.092, -0.01, 0.49)
        j[f"ankle{s}"] = (x * 0.098, 0.02, 0.085)
        j[f"foot{s}"] = (0.0, -1.0, 0.0)  # the foot's direction
        j[f"shoulder{s}"] = (x * sh, 0.01, 1.415)
        j[f"elbow{s}"] = (x * (sh + 0.03), 0.035, 1.13)
        j[f"wrist{s}"] = (x * (sh + 0.035), 0.005, 0.865)
        j[f"hand{s}"] = (x * (sh + 0.035), -0.005, 0.69)
    if pose == "walk":
        j.update(kneeL=(0.092, -0.17, 0.5), ankleL=(0.098, -0.29, 0.115), footL=(0.0, -1.0, 0.25),
                 kneeR=(-0.092, 0.1, 0.47), ankleR=(-0.098, 0.27, 0.16), footR=(0.0, -0.8, -0.6),
                 elbowR=(-sh - 0.025, -0.11, 1.14), wristR=(-sh - 0.03, -0.22, 0.92), handR=(-sh - 0.03, -0.3, 0.77),
                 elbowL=(sh + 0.025, 0.13, 1.14), wristL=(sh + 0.03, 0.19, 0.88), handL=(sh + 0.03, 0.22, 0.71))
    elif pose in ("sit", "wheel"):
        seat = 0.45 if pose == "sit" else 0.48
        zh = seat + 0.085
        j["pelvis"] = (0.0, 0.07, zh)
        j["lean"] = -6.0 if pose == "sit" else -4.0
        for s, x in (("L", 1), ("R", -1)):
            j[f"hip{s}"] = (x * 0.09, 0.07, zh)
            j[f"knee{s}"] = (x * 0.1, -0.36, zh - 0.01)
            j[f"ankle{s}"] = (x * 0.11, -0.42 if pose == "sit" else -0.46, 0.085 if pose == "sit" else 0.16)
            j[f"foot{s}"] = (0.0, -1.0, 0.0 if pose == "sit" else -0.25)
        dz = zh - 0.9
        for s, x in (("L", 1), ("R", -1)):
            j[f"shoulder{s}"] = (x * sh, 0.11, 1.415 + dz)
            if pose == "sit":  # forearms on the thighs, hands near the knees
                j[f"elbow{s}"] = (x * (sh + 0.02), 0.1, 0.79 + dz + 0.03)
                j[f"wrist{s}"] = (x * 0.15, -0.16, zh + 0.12)
                j[f"hand{s}"] = (x * 0.13, -0.32, zh + 0.1)
            else:  # hands on the push rims
                j[f"elbow{s}"] = (x * (sh + 0.06), 0.16, 0.79 + dz + 0.05)
                j[f"wrist{s}"] = (x * 0.27, 0.06, zh + 0.12)
                j[f"hand{s}"] = (x * 0.285, -0.08, zh + 0.07)
    return j


class Figure:
    """Meshes of one figure at one resolution, by garment."""

    def __init__(self):
        self.parts: dict[str, Mesh] = {}

    def add(self, key, *shapes_or_meshes):
        m = self.parts.setdefault(key, Mesh())
        for s in shapes_or_meshes:
            m.extend(s if isinstance(s, Mesh) else shapes_mesh(s))


def segment(p0, p1, radii, n):
    """A tapered limb from p0 to p1 through the radii [(t, r), …] (t from 0 to 1), closed at both ends."""
    L = v_len(v_sub(p1, p0))
    prof = [(0.0, 0.0)] + [(r, t * L) for t, r in radii] + [(0.0, L)]
    return mb.lathe(prof, p0, v_sub(p1, p0), n=n)


def ellipsoid(center, radii, n, z_cut=None, ref_up=(0, 0, 1)):
    """An ellipsoid; with z_cut (-1..1) only the part above that height (a hair cap)."""
    rings = max(4, n // 2)
    lo = -math.pi / 2 if z_cut is None else math.asin(max(-1.0, min(1.0, z_cut)))
    prof = []
    for i in range(rings + 1):
        a = lo + (math.pi / 2 - lo) * i / rings
        prof.append((math.cos(a), math.sin(a)))
    if z_cut is None:
        prof[0] = (0.0, -1.0)
    prof[-1] = (0.0, 1.0)
    m = shapes_mesh(mb.lathe(prof, (0, 0, 0), (0, 0, 1), n=n))
    m.v = [(center[0] + x * radii[0], center[1] + y * radii[1], center[2] + z * radii[2]) for x, y, z in m.v]
    return m


def loft_rings(rings, n):
    """A closed solid through elliptic rings [(center, half x, half y), …] lying flat (normal +z)."""
    m = Mesh()
    rows = []
    for c, a, b in rings:
        rows.append([m.vtx((c[0] + a * math.cos(2 * math.pi * k / n), c[1] + b * math.sin(2 * math.pi * k / n), c[2])) for k in range(n)])
    mb._rows_faces(m, rows, False, True)
    m.poly(list(reversed(rows[0])))
    m.poly(list(rows[-1]))
    m.orient(0)
    return m


def build_figure(H=1.70, *, pose="stand", female=False, child=False, sleeves="short", hair="short", skirt=False, n=16):
    """The meshes of a figure: keys skin, hair, top, bottom, shoes."""
    k = H / HREF
    j = pose_joints(pose, female)
    fig = Figure()
    n_ring = max(8, n + 4)
    head_k = 1.22 if child else 1.0  # children have larger heads for their height
    torso = TORSO_F if female else TORSO_M
    if child:  # a slimmer, straighter torso
        torso = [(z, a * 0.92, b * 0.95, y) for z, a, b, y in TORSO_M]
    px, py, pz = j["pelvis"]
    lean = math.radians(j["lean"])

    def body(p):  # a torso point of the standing body (about the pelvis at z 0,9) placed in the pose, then scaled
        x, y, z = p
        dz, dy = z - 0.9, y
        y2 = dy * math.cos(lean) - dz * math.sin(lean)
        z2 = dy * math.sin(lean) + dz * math.cos(lean)
        return (k * (px + x), k * (py + y2), k * (pz + z2))

    def J(name):
        x, y, z = j[name]
        return (k * x, k * y, k * z)

    # Torso in two garments, split at the belt.
    rings = [(body((0.0, y, z)), a * k, b * k) for z, a, b, y in torso]
    below = [r for r, t in zip(rings, torso) if t[0] <= BELT]
    above = [r for r, t in zip(rings, torso) if t[0] >= BELT]
    fig.add("bottom" if not skirt else "top", loft_rings(below, n_ring))
    fig.add("top", loft_rings(above, n_ring))
    if skirt:  # a dress: the skirt flares from the waist to just below the knees
        sk = [(body((0.0, 0.0, z)), a * k, b * k) for z, a, b in ((1.0, 0.152, 0.1), (0.9, 0.2, 0.14), (0.7, 0.23, 0.17), (0.48, 0.25, 0.19))]
        fig.add("top", loft_rings(sk, n_ring))
    # Neck and head.
    neck0 = body((0.0, 0.015, 1.46))
    neck1 = body((0.0, 0.012, 1.55))
    fig.add("skin", segment(neck0, neck1, [(0, 0.052 * k), (1, 0.05 * k)], n))
    hc = body((0.0, 0.0, 1.6 + 0.03 * (head_k - 1)))
    hr = (0.077 * k * head_k, 0.094 * k * head_k, 0.115 * k * head_k)
    fig.add("skin", ellipsoid(hc, hr, n))
    if n >= 12:  # a hint of a nose and ears in the smooth figure
        fig.add("skin", segment(v_add(hc, (0, -hr[1] * 0.9, -hr[2] * 0.12)), v_add(hc, (0, -hr[1] * 1.08, -hr[2] * 0.2)),
                                [(0, 0.012 * k), (1, 0.006 * k)], 8))
        for s in (1, -1):
            fig.add("skin", ellipsoid(v_add(hc, (s * hr[0] * 0.97, 0.005 * k, -0.005 * k)), (0.012 * k, 0.022 * k, 0.03 * k), 8))
    # Hair: a cap over the top and back of the head, longer for long hair.
    cap = ellipsoid(v_add(hc, (0, 0.008 * k, 0.012 * k)), (hr[0] * 1.08, hr[1] * 1.08, hr[2] * 1.06), n, z_cut=-0.05)
    # The hairline: the front of the cap rises above the forehead, the sides above the ears.
    cap.v = [(x, y, z) if y > hc[1] + hr[1] * 0.1 else (x, y, max(z, hc[2] + hr[2] * (0.2 + 0.45 * min(1.0, (hc[1] + hr[1] * 0.1 - y) / hr[1])))) for x, y, z in cap.v]
    fig.add("hair", cap)
    if hair == "long":
        back = [(v_add(hc, (0, hr[1] * 0.55, hr[2] * 0.2)), hr[0] * 1.05, hr[1] * 0.45),
                (v_add(hc, (0, hr[1] * 0.6, -hr[2] * 0.6)), hr[0] * 1.0, hr[1] * 0.42),
                (v_add(hc, (0, hr[1] * 0.75, -hr[2] * 1.5)), hr[0] * 1.15, hr[1] * 0.3)]
        back = [((c[0], c[1], c[2]), a, b) for c, a, b in reversed(back)]
        fig.add("hair", loft_rings(back, n_ring))
    elif hair == "bun":
        fig.add("hair", ellipsoid(v_add(hc, (0, hr[1] * 0.75, hr[2] * 0.55)), (0.04 * k, 0.04 * k, 0.04 * k), n))
    # Legs.
    for s in ("L", "R"):
        hip, knee, ankle = J(f"hip{s}"), J(f"knee{s}"), J(f"ankle{s}")
        leg_key = "skin" if skirt else "bottom"
        thigh_key = "skin" if skirt else "bottom"
        fig.add(thigh_key, segment(hip, knee, [(0, 0.078 * k), (0.5, 0.068 * k), (1, 0.054 * k)], n))
        fig.add(leg_key, ellipsoid(knee, (0.054 * k,) * 3, n))
        fig.add(leg_key, segment(knee, ankle, [(0, 0.052 * k), (0.3, 0.054 * k), (1, 0.038 * k)], n))
        # Shoe: a rounded sole and upper along the foot's direction.
        fd = v_norm(j[f"foot{s}"])
        side = v_norm(mb.v_cross(fd, (0, 0, 1))) if abs(fd[2]) < 0.99 else (1, 0, 0)
        up = mb.v_cross(side, fd)
        heel = v_add(ankle, v_add(v_mul(fd, -0.045 * k), v_mul(up, -0.06 * k)))
        outline = [(0.045 * k * math.cos(t), 0.13 * k + 0.13 * k * math.sin(t) * (1.0 if math.sin(t) > 0 else 0.75))
                   for t in [2 * math.pi * i / 20 for i in range(20)]]
        outline = [(u, v * 1.0) for u, v in outline]
        fig.add("shoes", mb.prism(outline, heel, side, fd, up, 0.0, 0.075 * k))
    # Arms.
    for s in ("L", "R"):
        sh, el, wr, ha = J(f"shoulder{s}"), J(f"elbow{s}"), J(f"wrist{s}"), J(f"hand{s}")
        fig.add("top", ellipsoid(v_add(sh, (-0.012 * k if sh[0] > 0 else 0.012 * k, 0, -0.005 * k)), (0.05 * k, 0.05 * k, 0.046 * k), n))
        if sleeves == "long":
            fig.add("top", segment(sh, el, [(0, 0.05 * k), (1, 0.04 * k)], n), ellipsoid(el, (0.04 * k,) * 3, n),
                    segment(el, wr, [(0, 0.039 * k), (1, 0.031 * k)], n))
        else:
            mid = v_add(sh, v_mul(v_sub(el, sh), 0.45))
            fig.add("top", segment(sh, mid, [(0, 0.054 * k), (1, 0.05 * k)], n))
            fig.add("skin", segment(mid, el, [(0, 0.043 * k), (1, 0.037 * k)], n), ellipsoid(el, (0.037 * k,) * 3, n),
                    segment(el, wr, [(0, 0.036 * k), (1, 0.027 * k)], n))
        # Hand: a flattened mitten, its palm towards the body.
        hand = ellipsoid((0, 0, 0), (0.026 * k, 0.045 * k, 0.095 * k), n)
        d = v_norm(v_sub(ha, wr))
        c = v_add(wr, v_mul(d, 0.085 * k))
        e3 = d
        e1 = v_norm(mb.v_cross((0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0), e3))
        e2 = mb.v_cross(e3, e1)
        hand.v = [v_add(c, v_add(v_add(v_mul(e1, x), v_mul(e2, y)), v_mul(e3, z))) for x, y, z in hand.v]
        fig.add("skin", hand)
    return fig.parts


def add_figure(c, materials: dict, *, prefix="", **kw):
    """Add a figure to the component: smooth pieces for medium/fine, a low-poly one for coarse. `materials` maps the
    garments (skin, hair, top, bottom, shoes) to material names."""
    names = {"skin": "Pele", "hair": "Cabelo", "top": "Roupa - parte de cima", "bottom": "Roupa - parte de baixo", "shoes": "Calçados"}
    for level, n, detail in (("", 16, FULL), (" simplificada", 6, COARSE)):
        parts = build_figure(n=n, **kw)
        for key, mesh in parts.items():
            if mesh.v:
                c._add(f"{prefix}{names[key]}{level}", mesh.shape(), materials[key], detail, key in ("top", "hair", "bottom"), False)


# Materials of the figures (the same name means the same material in every component).
PEOPLE = {
    "Pele clara": ((226, 184, 152), "Generic", "Satin", 0),
    "Pele morena": ((172, 118, 82), "Generic", "Satin", 0),
    "Pele negra": ((104, 68, 46), "Generic", "Satin", 0),
    "Cabelo preto": ((30, 26, 24), "Generic", "Satin", 0),
    "Cabelo castanho": ((86, 58, 38), "Generic", "Satin", 0),
    "Cabelo grisalho": ((168, 166, 160), "Generic", "Satin", 0),
    "Tecido azul-marinho": ((36, 48, 80), "Generic", "Matte", 0),
    "Jeans": ((66, 88, 124), "Generic", "Matte", 0),
    "Tecido branco": ((236, 236, 232), "Generic", "Matte", 0),
    "Tecido vermelho": ((168, 46, 48), "Generic", "Matte", 0),
    "Tecido verde-oliva": ((98, 106, 66), "Generic", "Matte", 0),
    "Tecido mostarda": ((204, 150, 48), "Generic", "Matte", 0),
    "Tecido cinza-chumbo": ((70, 72, 76), "Generic", "Matte", 0),
    "Couro preto": ((28, 23, 21), "Generic", "Satin", 0),
}


def declare(c, materials: dict):
    for name in dict.fromkeys(materials.values()):
        if name in PEOPLE:
            c.material(name, *PEOPLE[name])
