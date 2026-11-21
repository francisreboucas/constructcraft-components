"""Generic human figures for scale: smooth mannequins on a posed skeleton, dressed in simple clothes.

Not a component module. The body parts are blended into one continuous surface (tools/appliances/_manequim.py), and
each garment is meshed as its own closed solid. A figure is built twice: a fine surface for the medium and fine levels
(the head finer still), a coarse one for the coarse level.

The figure faces -Y with its feet on z = 0 and its origin between the feet (sitting: under the hips). No real person
is depicted: the faces are featureless, the bodies average adult or child proportions.
"""

from __future__ import annotations

import math

from kit import COARSE, FULL

HREF = 1.70  # the joints below are those of a 1,70 m adult; other heights scale them

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


def build_mannequin(H=1.70, *, pose="stand", female=False, child=False, sleeves="short", hair="short", skirt=False, h=0.015):
    """A smooth mannequin: the body parts blended into one surface, meshed per garment (skin, hair, top, bottom, shoes)."""
    import numpy as np
    from _manequim import Body, garment_meshes

    k = H / HREF
    j = pose_joints(pose, female)
    px, py, pz = j["pelvis"]
    lean = math.radians(j["lean"])
    hk = 1.22 if child else 1.0

    def body(p):  # a point of the standing torso placed in the pose and scaled
        x, y, z = p
        dz = z - 0.9
        return (k * (px + x), k * (py + y * math.cos(lean) - dz * math.sin(lean)), k * (pz + y * math.sin(lean) + dz * math.cos(lean)))

    def J(name):
        x, y, z = j[name]
        return (k * x, k * y, k * z)

    b = Body(blend=0.03 * k)
    top = "top"
    lower = "top" if skirt else "bottom"
    # Torso: hips, waist, chest and shoulders as blended ellipsoids.
    if female:
        torso = [(lower, 0.9, 0.0, (0.18, 0.12, 0.13)), (top, 1.06, -0.004, (0.135, 0.092, 0.11)),
                 (top, 1.24, -0.018, (0.16, 0.12, 0.13)), (top, 1.39, 0.006, (0.165, 0.085, 0.07))]
    else:
        torso = [(lower, 0.9, 0.006, (0.172, 0.115, 0.13)), (top, 1.06, -0.004, (0.15, 0.098, 0.11)),
                 (top, 1.25, -0.01, (0.175, 0.115, 0.14)), (top, 1.39, 0.008, (0.185, 0.092, 0.07))]
    if child:
        torso = [(g, z, y, (r[0] * 0.92, r[1] * 0.95, r[2])) for g, z, y, r in torso]
    for g, z, y, r in torso:
        b.ellipsoid(g, body((0.0, y, z)), tuple(v * k for v in r), blend=0.06 * k)
    if skirt:
        b.cone(top, body((0.0, 0.0, 0.98)), body((0.0, 0.01, 0.44)), 0.16 * k, 0.215 * k, blend=0.04 * k, zmin=body((0, 0, 0.5))[2])
    # Neck and head, the hair over the top and back of it.
    b.cone("skin", body((0.0, 0.015, 1.44)), body((0.0, 0.01, 1.56)), 0.055 * k, 0.05 * k)
    hc = body((0.0, 0.0, 1.6 + 0.03 * (hk - 1)))
    hr = (0.077 * k * hk, 0.094 * k * hk, 0.114 * k * hk)
    b.ellipsoid("head", hc, hr, blend=0.02 * k)
    b.ellipsoid("hair", (hc[0], hc[1] + 0.022 * k, hc[2] + 0.03 * k), (hr[0] * 1.07, hr[1] * 1.0, hr[2] * 0.93), blend=0.01 * k)
    if hair == "long":
        b.cone("hair", (hc[0], hc[1] + hr[1] * 0.55, hc[2]), (hc[0], hc[1] + hr[1] * 0.75, hc[2] - hr[2] * 1.6),
               hr[0] * 0.95, hr[0] * 0.75, blend=0.02 * k)
    elif hair == "bun":
        b.ellipsoid("hair", (hc[0], hc[1] + hr[1] * 0.85, hc[2] + hr[2] * 0.45), (0.042 * k,) * 3, blend=0.015 * k)
    # Legs and feet.
    for sd in ("L", "R"):
        hip, knee, ankle = J(f"hip{sd}"), J(f"knee{sd}"), J(f"ankle{sd}")
        leg = "skin" if skirt else lower
        b.cone(leg, hip, knee, 0.078 * k, 0.052 * k)
        b.cone(leg, knee, ankle, 0.05 * k, 0.034 * k)
        fd = np.asarray(j[f"foot{sd}"], float)
        fd = fd / np.linalg.norm(fd)
        side = np.cross(fd, (0, 0, 1))
        side = side / np.linalg.norm(side) if np.linalg.norm(side) > 1e-6 else np.array([1.0, 0, 0])
        up = np.cross(side, fd)
        c = np.asarray(ankle) + fd * 0.07 * k - up * 0.045 * k
        on_floor = ankle[2] < 0.12 * k and abs(fd[2]) < 0.3
        b.ellipsoid("shoes", tuple(c), (0.048 * k, 0.13 * k, 0.05 * k), basis=(side, fd, up), floor=0.0 if on_floor else None,
                    blend=0.02 * k)
    # Arms and hands.
    for sd in ("L", "R"):
        sh, el, wr, ha = J(f"shoulder{sd}"), J(f"elbow{sd}"), J(f"wrist{sd}"), J(f"hand{sd}")
        inward = np.array([-np.sign(sh[0]) * 0.015 * k, 0.0, -0.012 * k])
        sh = tuple(np.asarray(sh) + inward)
        if sleeves == "long":
            b.cone(top, sh, el, 0.05 * k, 0.04 * k)
            b.cone(top, el, wr, 0.039 * k, 0.03 * k)
        else:
            mid = tuple(np.asarray(sh) + 0.42 * (np.asarray(el) - np.asarray(sh)))
            b.cone(top, sh, mid, 0.056 * k, 0.05 * k)
            b.cone("skin", sh, el, 0.044 * k, 0.036 * k)
            b.cone("skin", el, wr, 0.035 * k, 0.026 * k)
        d = np.asarray(ha) - np.asarray(wr)
        d = d / np.linalg.norm(d)
        e1 = np.cross((0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0), d)
        e1 = e1 / np.linalg.norm(e1)
        e2 = np.cross(d, e1)
        hcn = tuple(np.asarray(wr) + d * 0.08 * k)
        b.ellipsoid("skin", hcn, (0.024 * k, 0.045 * k, 0.09 * k), basis=(e1, e2, d), blend=0.015 * k)
    return garment_meshes(b, h, finer={"head": h * 0.5, "hair": h * 0.5})


def add_figure(c, materials: dict, *, prefix="", **kw):
    """Add a mannequin to the component: a fine surface for medium/fine, a coarse one for the coarse level. `materials`
    maps the garments (skin, hair, top, bottom, shoes) to material names."""
    kw.pop("n", None)
    names = {"skin": "Pele", "head": "Cabeça", "hair": "Cabelo", "top": "Roupa - parte de cima", "bottom": "Roupa - parte de baixo", "shoes": "Calçados"}
    for level, h, detail in (("", 0.018, FULL), (" simplificada", 0.05, COARSE)):
        parts = build_mannequin(h=h * kw.get("H", HREF) / HREF, **kw)
        for key, mesh in parts.items():
            if mesh.v:
                mat = materials["skin" if key == "head" else key]
                c._add(f"{prefix}{names[key]}{level}", mesh.shape(), mat, detail, key in ("top", "hair", "bottom"), False)


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
