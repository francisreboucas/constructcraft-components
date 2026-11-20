#!/usr/bin/env python3
"""Generate the planting sources (sources/planting/*.json).

    python tools/vegetation.py      then  python tools/build.py

Plants are fixed meshes, one per type, sized to the species (height and crown
width of a mature plant), at two detail levels:

- coarse (plans, site plans, distant views): tools/vegetation_coarse.py, a light
  silhouette that still reads as a plant: a trunk forking into its limbs, a crown
  of leaf clusters in two tones spread over the crown's envelope, serrated palm
  fronds and notched fans, conifer whorls of pads, shrubs with a few flowers;
- medium and fine: tools/vegetation_detail.py, the detailed plant: branches by
  space colonization (Runions, Lane and Prusinkiewicz, 2007) with pipe-model
  thickness, sprays of single leaves whose number and size come from the
  crown's area, flowers, palm leaflets and fans, needle tufts, grass blades.

Lawns, planting beds and planters with walls are parametric pieces. This module
holds the shared mesh primitives, the materials and the species.

Every plant comes from a fixed seed, so running this again gives the same files.
"""

from __future__ import annotations

import json
import math
import random
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sources" / "planting"

MATERIALS = {
    "Folhagem": [78, 122, 58],
    "Folhagem escura": [46, 92, 56],
    "Folhagem clara": [118, 158, 70],
    "Folhagem sombra": [30, 66, 42],
    "Floração amarela": [232, 190, 40],
    "Casca de árvore": [102, 78, 58],
    "Estipe de palmeira": [150, 140, 122],
    "Palmito": [104, 140, 76],
    "Terracota": [176, 98, 66],
    "Terra vegetal": [74, 56, 42],
    "Floração rosa": [222, 122, 172],
    "Floração vermelha": [192, 36, 42],
    "Floração laranja": [234, 102, 38],
    "Floração azul": [94, 114, 206],
    "Floração branca": [242, 242, 236],
    "Folhagem arroxeada": [116, 64, 82],
    "Pluma de capim": [204, 170, 158],
    "Grama": [96, 146, 62],
    "Concreto aparente": [172, 170, 164],
    "Reboco pintado": [228, 224, 214],
    "Casca de pinus": [124, 82, 52],
    "Seixo branco": [224, 222, 214],
    "Fibra de vidro grafite": [62, 64, 68],
}


# --- vectors -----------------------------------------------------------------------

def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def length(a):
    return math.sqrt(dot(a, a))


def unit(a):
    n = length(a)
    return mul(a, 1 / n) if n > 1e-12 else a


def perpendicular(t):
    """A unit vector perpendicular to `t`."""
    u = cross(t, (0, 0, 1))
    if length(u) < 1e-6:
        u = cross(t, (1, 0, 0))
    return unit(u)


UP = (0.0, 0.0, 1.0)


# --- meshes ------------------------------------------------------------------------

class Mesh:
    """Vertices and polygon faces, each face counter-clockwise seen from outside."""

    def __init__(self):
        self.vertices: list[tuple] = []
        self.faces: list[list[int]] = []

    def vertex(self, p) -> int:
        self.vertices.append(tuple(p))
        return len(self.vertices) - 1

    def face(self, idx: list[int], outward):
        """Add a face, flipped if needed so that its normal agrees with `outward`."""
        pts = [self.vertices[i] for i in idx]
        n = (0.0, 0.0, 0.0)
        for a, b in zip(pts, pts[1:] + pts[:1]):  # Newell's normal
            n = add(n, ((a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1])))
        if dot(n, outward) < 0:
            idx = idx[::-1]
        self.faces.append(idx)

    def centroid(self, idx):
        pts = [self.vertices[i] for i in idx]
        return mul(tuple(map(sum, zip(*pts))), 1 / len(pts))

    def transform(self, fn):
        self.vertices = [fn(p) for p in self.vertices]

    def shape(self) -> dict:
        return {"Mesh": {"vertices": [[round(c, 3) + 0.0 for c in p] for p in self.vertices], "faces": self.faces}}


def tube(mesh: Mesh, path, radii, sides=6):
    """A closed tube along `path` (points) with a radius at each point."""
    rings = []
    normal = None
    for i, p in enumerate(path):
        t = unit(sub(path[min(i + 1, len(path) - 1)], path[max(i - 1, 0)]))
        # Parallel transport keeps the rings from twisting along the tube.
        normal = perpendicular(t) if normal is None else unit(sub(normal, mul(t, dot(normal, t))))
        binormal = cross(t, normal)
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            ring.append(mesh.vertex(add(p, add(mul(normal, math.cos(a) * radii[i]), mul(binormal, math.sin(a) * radii[i])))))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k in range(sides):
            idx = [rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]]
            axis = mul(add(path[i], path[i + 1]), 0.5)
            mesh.face(idx, sub(mesh.centroid(idx), axis))
    mesh.face(list(rings[0]), sub(path[0], path[1]))
    mesh.face(list(rings[-1]), sub(path[-1], path[-2]))


def loft(mesh: Mesh, sections):
    """A closed solid through `sections` (lists of points, the same count each);
    a section of a single point closes the end in a tip."""
    # A thin solid has faces almost edge-on to any "from the inside out" test,
    # so the faces are wound consistently from the ring order instead and the
    # whole solid is flipped if its volume comes out negative.
    rings = [[mesh.vertex(p) for p in s] for s in sections]
    faces = []
    for a, b in zip(rings, rings[1:]):
        n = len(a)
        for k in range(n):
            if len(b) == 1:
                faces.append([a[k], a[(k + 1) % n], b[0]])
            else:  # two triangles: the sections twist, so a quad would not be planar
                faces += [[a[k], a[(k + 1) % n], b[(k + 1) % n]], [a[k], b[(k + 1) % n], b[k]]]
    if len(rings[0]) > 2:
        faces.append(rings[0][::-1])
    if len(rings[-1]) > 2:
        faces.append(list(rings[-1]))
    v = mesh.vertices
    volume = sum(dot(v[f[0]], cross(v[f[i]], v[f[i + 1]])) for f in faces for i in range(1, len(f) - 1))
    mesh.faces += [f[::-1] for f in faces] if volume < 0 else faces


def bounds(meshes):
    pts = [p for m in meshes for p in m.vertices]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


# --- trees: space colonization -------------------------------------------------------

def colonize(rnd, trunk_top, center, radii, points=260, step=None, influence=None, kill=None, tropism=0.15):
    """Grow a branch skeleton from a trunk up to `trunk_top` into the ellipsoid
    `center`/`radii`. Returns node positions and parents (-1 for the root)."""
    step = step or max(radii) / 5
    influence = influence or max(radii) * 1.2
    kill = kill or step * 1.6
    attractors = []
    while len(attractors) < points:
        p = (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))
        if dot(p, p) <= 1:
            attractors.append(add(center, (p[0] * radii[0], p[1] * radii[1], p[2] * radii[2])))
    nodes, parents = [(0.0, 0.0, 0.0)], [-1]
    segments = max(2, round(trunk_top / step))
    for k in range(1, segments + 1):
        nodes.append((0.0, 0.0, trunk_top * k / segments))
        parents.append(k - 1)
    for _ in range(80):
        pull: dict[int, tuple] = {}
        for a in attractors:
            best, dist = -1, influence
            for i, n in enumerate(nodes):
                d = length(sub(a, n))
                if d < dist:
                    best, dist = i, d
            if best >= 0:
                pull[best] = add(pull.get(best, (0.0, 0.0, 0.0)), unit(sub(a, nodes[best])))
        if not pull:
            break
        grown = []
        for i, d in sorted(pull.items()):
            p = add(nodes[i], mul(unit(add(unit(d), mul(UP, tropism))), step))
            if all(length(sub(p, nodes[j])) > step * 0.3 for j in range(len(nodes)) if parents[j] == i):
                nodes.append(p)
                parents.append(i)
                grown.append(p)
        if not grown:
            break
        attractors = [a for a in attractors if all(length(sub(a, g)) > kill for g in grown)]
        if not attractors:
            break
    return nodes, parents


def pipe_radii(parents, trunk_radius, tip=1.0, exponent=2.5):
    """Branch radii by the pipe model, the root scaled to `trunk_radius`."""
    r = [0.0] * len(parents)
    children = [[] for _ in parents]
    for i, p in enumerate(parents):
        if p >= 0:
            children[p].append(i)
    for i in range(len(parents) - 1, -1, -1):  # children always come after their parent
        r[i] = tip if not children[i] else sum(r[c] ** exponent for c in children[i]) ** (1 / exponent)
    k = trunk_radius / r[0]
    return [x * k for x in r], children


# --- sources -------------------------------------------------------------------------
# The engine keeps one definition per component and its types differ only in
# parameter values, so each species, with its own mesh, is its own component.

COARSE = {"coarse": True, "medium": False, "fine": False}
DETAILED = {"coarse": False, "medium": True, "fine": True}


def item(name, material, mesh, in_plan, detail=None):
    """A mesh piece; `detail` COARSE or DETAILED (None: every level)."""
    it = {"name": name, "material": material, "in_plan": in_plan, "shape": mesh.shape()}
    if detail:
        it["detail"] = detail
    return it


def seed(name):
    return zlib.crc32(name.encode("utf-8"))


def source(component, type_name, description, items, params=None, types=None):
    used = list(dict.fromkeys(i["material"] for i in items))
    return {
        "component": component,
        "def": {"kind": "Generic", "params": params or [], "items": items},
        "types": types or [{"name": type_name, "values": {}, "info": {"description": description}}],
        "materials": [{"name": n, "color": MATERIALS[n]} for n in used],
    }


def moved(mesh, d):
    mesh.transform(lambda p: add(p, d))
    return mesh


def merged(meshes):
    out = Mesh()
    for m in meshes:
        base = len(out.vertices)
        out.vertices += m.vertices
        out.faces += [[i + base for i in f] for f in m.faces]
    return out


SHADE = {"Folhagem": "Folhagem escura", "Folhagem escura": "Folhagem sombra", "Folhagem clara": "Folhagem",
         "Folhagem arroxeada": "Folhagem arroxeada"}


def coarse(parts, leaf_mat="Folhagem", bloom_mat="Floração amarela", *, wood_mat="Casca de árvore", wood_name="Tronco",
           leaf_name="Copa", green_mat="Palmito", offset=None):
    """The coarse pieces of a plant from vegetation_coarse's dict of meshes: light and shade tones, blooms, wood."""
    out = []
    for key, name, mat, plan in (("wood", wood_name, wood_mat, False), ("green", "Palmito", green_mat, False),
                                 ("light", leaf_name, leaf_mat, True), ("shade", f"{leaf_name} - sombra", SHADE[leaf_mat], True),
                                 ("bloom", "Floração", bloom_mat, True)):
        m = parts.get(key)
        if m is not None and m.vertices:
            if offset:
                moved(m, offset)
            out.append(item(name, mat, m, plan, COARSE))
    return out


def detailed(items, wood=None, leaves=None, blooms=None, *, wood_mat="Casca de árvore", leaf_mat="Folhagem",
             bloom_mat="Floração amarela", wood_name="Galhos", leaf_name="Folhas", bloom_name="Flores"):
    """Append the medium/fine pieces of a plant to `items`."""
    for name, mat, mesh, plan in ((wood_name, wood_mat, wood, False), (leaf_name, leaf_mat, leaves, True),
                                  (bloom_name, bloom_mat, blooms, True)):
        if mesh is not None and mesh.vertices:
            items.append(item(name, mat, mesh, plan, DETAILED))
    return items


import vegetation_coarse as VC  # noqa: E402  (it imports this module's primitives)


def trees():
    import vegetation_detail as D
    # file, species, height, crown, clear trunk, trunk diameter, foliage, share of flowering clumps, detailed look
    for file, name, H, C, F, T, mat, fl, look in [
        ("ipe-amarelo", "Ipê-amarelo", 8.0, 6.0, 2.2, 0.3, "Folhagem", 0.55,
         dict(flowers=0.85, leaf_len=0.12, leaf_w=0.05, bloom_size=0.14, bloom="Floração amarela")),
        ("reseda", "Resedá", 5.0, 4.0, 1.8, 0.2, "Folhagem", 0.0,
         dict(flowers=0.4, leaf_len=0.1, leaf_w=0.05, bloom_size=0.09, bloom="Floração rosa")),
        ("pau-brasil", "Pau-brasil", 10.0, 7.0, 2.5, 0.35, "Folhagem escura", 0.0,
         dict(leaf_len=0.12, leaf_w=0.05, per=10)),
        ("oiti", "Oiti", 10.0, 10.0, 2.2, 0.4, "Folhagem escura", 0.0, dict(leaf_len=0.19, leaf_w=0.08)),
        ("mangueira", "Mangueira", 12.0, 12.0, 2.0, 0.6, "Folhagem escura", 0.0,
         dict(leaf_len=0.32, leaf_w=0.07, per=8, droop=0.35)),
        ("sibipiruna", "Sibipiruna", 15.0, 12.0, 3.0, 0.5, "Folhagem", 0.0,
         dict(leaf_len=0.12, leaf_w=0.05, per=10, flowers=0.12, bloom_size=0.06, bloom="Floração amarela", flat=0.8)),
    ]:
        look = dict(look)
        bmat = look.pop("bloom", "Floração amarela")
        shape = {"ipe-amarelo": "vase", "oiti": "dome", "mangueira": "dome", "sibipiruna": "umbrella"}.get(file, "round")
        bloom_share = fl or (0.25 if look.get("flowers") else 0.0)
        items = coarse(VC.tree(seed(name), H, C, F, T, shape=shape, flowers=bloom_share), mat, bmat)
        fw, fl_, fb = D.fine_tree(seed(name), H, C, F, T, **look)
        detailed(items, fw, fl_, fb, leaf_mat=mat, bloom_mat=bmat)
        yield file, source(name, f"{name} {H:g} m", f"Árvore de copa arredondada, {H:g} m de altura, copa Ø{C:g} m", items)


def conifers():
    import vegetation_detail as D
    for file, name, H, C, F, T, make, fine in [
        ("tuia-holandesa", "Tuia-holandesa", 4.0, 1.2, 0.15, 0.1, VC.column,
         lambda s: D.fine_column(s, 4.0, 1.2, 0.15, 0.1, leaf_len=0.09)),
        ("cipreste-italiano", "Cipreste-italiano", 8.0, 1.6, 0.3, 0.2, VC.column,
         lambda s: D.fine_column(s, 8.0, 1.6, 0.3, 0.2, leaf_len=0.12)),
        ("pinheiro", "Pinheiro", 12.0, 5.0, 1.8, 0.4, VC.pine, lambda s: D.fine_pine(s, 12.0, 5.0, 1.8, 0.4)),
    ]:
        leaf_mat = "Folhagem clara" if file == "tuia-holandesa" else "Folhagem escura"
        items = coarse(make(seed(name), H, C, F, T), leaf_mat)
        fw, fl = fine(seed(name))
        detailed(items, fw, fl, leaf_mat=leaf_mat, leaf_name="Folhagem")
        yield file, source(name, f"{name} {H:g} m", f"Conífera, {H:g} m de altura, copa Ø{C:g} m", items)


def palms():
    import vegetation_detail as D
    for file, name, H, C, Dm, kw, fine in [
        ("palmeira-imperial", "Palmeira-imperial", 15.0, 6.0, 0.45, {"fronds": 18, "shaft": True, "droop": 0.6},
         {"fronds": 16, "shaft": True, "droop": 0.6, "leaflets": 34}),
        ("jeriva", "Jerivá", 8.0, 5.0, 0.3, {"fronds": 14, "droop": 0.8, "lean": 0.03},
         {"fronds": 15, "droop": 0.85, "lean": 0.03, "leaflets": 32, "plumose": True}),
        ("palmeira-real-australiana", "Palmeira-real-australiana", 10.0, 4.0, 0.25,
         {"fronds": 12, "shaft": True, "droop": 0.55}, {"fronds": 12, "shaft": True, "droop": 0.55, "leaflets": 30}),
        ("washingtonia", "Washingtonia", 12.0, 4.0, 0.6, {"fronds": 18, "droop": 0.35, "rise": (35, -45), "fan": True},
         {"fronds": 18, "droop": 0.3, "rise": (55, -35), "fan": True}),
    ]:
        items = coarse(VC.palm(seed(name), H, C, Dm, **kw), "Folhagem", wood_mat="Estipe de palmeira", wood_name="Estipe",
                       leaf_name="Folhas")
        fw, fl, fg = D.fine_palm(seed(name), H, C, Dm, **fine)
        detailed(items, fw, fl, None, wood_mat="Estipe de palmeira", wood_name="Estipe detalhado", leaf_name="Folíolos")
        if fg.vertices:
            items.append(item("Ráquis e palmito", "Palmito", fg, False, DETAILED))
        yield file, source(name, f"{name} {H:g} m", f"Palmeira de estipe único, {H:g} m de altura, copa Ø{C:g} m", items)


def shrubs():
    import vegetation_detail as D
    for file, name, H, C, n, j, mat, fine in [  # n: coarse clusters, j: coarse flowers
        ("buxinho", "Buxinho", 0.5, 0.5, 0, 0, "Folhagem escura",
         dict(leaf_len=0.03, leaf_w=0.018, topiary=True, stems=4, cover=2.6)),
        ("ixora", "Ixora", 0.8, 0.8, 11, 14, "Folhagem",
         dict(leaf_len=0.07, leaf_w=0.03, umbels=16, flower_size=0.012, bloom="Floração vermelha")),
        ("pingo-de-ouro", "Pingo-de-ouro", 1.0, 1.0, 13, 0, "Folhagem clara", dict(leaf_len=0.045, leaf_w=0.025)),
        ("hibisco", "Hibisco", 1.8, 1.5, 16, 12, "Folhagem",
         dict(leaf_len=0.1, leaf_w=0.07, flowers=26, flower_size=0.065, bloom="Floração vermelha", stems=9)),
    ]:
        fine = dict(fine)
        bmat = fine.pop("bloom", "Floração vermelha")
        parts = VC.shrub(seed(name), H, C, clusters=n or 12, flowers=j, topiary=file == "buxinho", stems=0 if file == "buxinho" else 4)
        items = coarse(parts, mat, bmat, wood_name="Caules simplificados", leaf_name="Folhagem")
        fw, fl, fb = D.fine_shrub(seed(name), H, C, **fine)
        detailed(items, fw, fl, fb, leaf_mat=mat, bloom_mat=bmat, wood_name="Caules", leaf_name="Folhas")
        yield file, source(name, f"{name} Ø{C * 100:g}", f"Arbusto de canteiro ou cerca viva, {H:g} m de altura, Ø{C:g} m",
                           items)


def pots():
    import vegetation_detail as D
    for DV, HV, DP, HP in [(0.4, 0.4, 0.5, 0.6), (0.6, 0.55, 0.8, 1.0), (0.8, 0.7, 1.1, 1.4)]:
        size = f"Ø{DV * 100:g}"
        pot = {"Revolution": {"plane": "Front", "offset": "0", "axis": "0", "angle": "360", "points": [
            {"u": "0", "v": "0", "radius": ""}, {"u": f"{DV * 0.38:g}", "v": "0", "radius": ""},
            {"u": f"{DV / 2:g}", "v": f"{HV:g}", "radius": ""}, {"u": "0", "v": f"{HV:g}", "radius": ""}]}}
        soil = {"Cylinder": {"x": "0", "y": "0", "z": f"{HV:g}", "radius": f"{DV / 2 - 0.02:g}", "height": "0.01"}}
        items = [
            {"name": "Vaso", "material": "Terracota", "in_plan": True, "shape": pot},
            {"name": "Terra", "material": "Terra vegetal", "in_plan": False, "shape": soil},
        ] + coarse(VC.shrub(seed(f"Vaso {size}"), HP - HV * 0.9, DP, z0=HV * 0.9, clusters=10), "Folhagem", leaf_name="Planta")
        fw, fl, _ = D.fine_shrub(seed(f"Vaso {size}"), HP - HV * 0.9, DP, z0=HV, leaf_len=0.11, leaf_w=0.05,
                                 stems=6)
        detailed(items, fw, fl, None, wood_name="Caules")
        yield f"vaso-planta-{DV * 100:g}", source(f"Vaso com planta {size}", f"Vaso {size}",
                                                  "Vaso de terracota com planta ornamental", items)


# --- grasses and ground covers ---------------------------------------------------------------

def plumes(seed_, height, count, size=0.05):
    """Arching flower stems of an ornamental grass ending in feathery plumes."""
    import vegetation_detail as D
    rnd = random.Random(seed_)
    stems, heads = Mesh(), Mesh()
    for k in range(count):
        a = D.GOLDEN * k
        out = (math.cos(a), math.sin(a), 0.0)
        lean = rnd.uniform(0.15, 0.35)
        L = height * rnd.uniform(0.9, 1.1)
        path = [add(mul(out, L * lean * t * t), (0, 0, L * t)) for t in (0, 0.33, 0.66, 0.8, 1.0)]
        tube(stems, path[:4], [0.003, 0.0025, 0.002, 0.0015], 3)
        axis = unit(sub(path[4], path[3]))
        for i in range(26):
            t = i / 25
            p = add(path[3], mul(sub(path[4], path[3]), t))
            d = unit(add(axis, (rnd.uniform(-.5, .5), rnd.uniform(-.5, .5), rnd.uniform(-.2, .2))))
            D.leaf(heads, p, d, perpendicular(d), size * (1.2 - 0.6 * t), 0.012, fold=0.0, curl=0.2)
    return stems, heads


def flower_stalks(seed_, height, count, spread, size, petals, umbel=False, umbel_r=0.07, florets=30):
    """Upright flower stalks topped by a flower (moreia) or a round umbel (agapanto)."""
    import vegetation_detail as D
    rnd = random.Random(seed_)
    stalks, blooms = Mesh(), Mesh()
    for k in range(count):
        a = D.GOLDEN * k + 0.4
        r = spread * rnd.uniform(0.2, 1.0)
        top = (math.cos(a) * r, math.sin(a) * r, height * rnd.uniform(0.85, 1.05))
        tube(stalks, [(math.cos(a) * 0.02, math.sin(a) * 0.02, 0.0), top], [0.004, 0.003], 4)
        if umbel:
            D.umbel(blooms, add(top, (0, 0, umbel_r * 0.8)), UP, rnd, size, florets, radius=umbel_r)
        else:
            D.flower(blooms, top, unit((math.cos(a) * 0.3, math.sin(a) * 0.3, 1.0)), size, petals, rnd, cup=0.15)
    return stalks, blooms


def grasses():
    import vegetation_detail as D
    name = "Capim-do-texas"  # arching purple blades and pinkish plumes
    items = [item("Touceira", "Folhagem arroxeada", D.grass(seed(name), 0.8, 0.8, blades=14, blade_w=0.03, arch=0.7), True, COARSE)]
    st, hd = plumes(seed(name) + 1, 1.05, 22)
    detailed(items, None, D.grass(seed(name), 0.8, 0.9, blades=170, blade_w=0.006, arch=0.75), None, leaf_mat="Folhagem arroxeada",
             leaf_name="Lâminas")
    items += [item("Hastes florais", "Pluma de capim", st, False, DETAILED), item("Plumas", "Pluma de capim", hd, True, DETAILED)]
    yield "capim-do-texas", source(name, f"{name} Ø90", "Gramínea ornamental de folhas arroxeadas e plumas, 1 m de altura, "
                                   "touceira Ø0,9 m", items)

    name = "Moreia"  # stiff upright strap leaves, white flowers on thin stalks
    items = [item("Touceira", "Folhagem escura", D.grass(seed(name), 0.6, 0.6, blades=12, blade_w=0.025, arch=0.2, stiff=True), True,
                  COARSE)]
    st, fl = flower_stalks(seed(name) + 1, 0.75, 9, 0.18, 0.035, 3)
    detailed(items, None, D.grass(seed(name), 0.6, 0.65, blades=70, blade_w=0.011, arch=0.25, stiff=True), fl,
             leaf_mat="Folhagem escura", bloom_mat="Floração branca", leaf_name="Folhas")
    items.append(item("Hastes florais", "Folhagem", st, False, DETAILED))
    yield "moreia", source(name, f"{name} Ø60", "Moreia (Dietes), touceira de folhas eretas com flores brancas, 0,75 m de altura, "
                           "Ø0,6 m", items)

    name = "Agapanto"  # arching strap leaves and blue round umbels on tall stalks
    items = [item("Touceira", "Folhagem", D.grass(seed(name), 0.45, 0.6, blades=12, blade_w=0.03, arch=0.8), True, COARSE)]
    st, um = flower_stalks(seed(name) + 1, 0.85, 6, 0.12, 0.02, 4, True, 0.07, 34)
    detailed(items, None, D.grass(seed(name), 0.45, 0.65, blades=48, blade_w=0.016, arch=0.85), um, leaf_mat="Folhagem",
             bloom_mat="Floração azul", leaf_name="Folhas")
    items.append(item("Hastes florais", "Folhagem", st, False, DETAILED))
    yield "agapanto", source(name, f"{name} Ø60", "Agapanto, touceira de folhas em fita com umbelas azuis, 0,9 m de altura, Ø0,6 m",
                             items)


def ground_covers():
    import vegetation_detail as D

    def slab(h):  # each covers a 1 x 1 m square from its centre: place several to fill a bed
        return {"Box": {"x": "-0.5", "y": "-0.5", "z": "0", "width": "1", "depth": "1", "height": f"{h:g}"}}

    name = "Forração de grama-amendoim"
    rnd = random.Random(seed(name))
    leaves, blooms = Mesh(), Mesh()
    for k in range(2600):
        p = (rnd.uniform(-0.48, 0.48), rnd.uniform(-0.48, 0.48), rnd.uniform(0.02, 0.11))
        a = rnd.uniform(0, 2 * math.pi)
        d = (math.cos(a), math.sin(a), rnd.uniform(-0.1, 0.3))
        D.leaf(leaves, p, unit(d), unit((rnd.uniform(-.3, .3), rnd.uniform(-.3, .3), 1)), 0.04, 0.03, fold=0.2)
    for k in range(45):
        p = (rnd.uniform(-0.46, 0.46), rnd.uniform(-0.46, 0.46), rnd.uniform(0.1, 0.14))
        D.flower(blooms, p, UP, 0.012, 4, rnd, cup=0.3)
    items = [{"name": "Forração simplificada", "material": "Folhagem clara", "in_plan": True, "shape": slab(0.1), "detail": COARSE}]
    detailed(items, None, leaves, blooms, leaf_mat="Folhagem clara", bloom_mat="Floração amarela")
    yield "forracao-grama-amendoim", source(name, "Grama-amendoim 1x1 m", "Forração de grama-amendoim (Arachis repens) com flores "
                                            "amarelas, 12 cm de altura, em placa de 1 x 1 m (repita para cobrir o canteiro)", items)

    name = "Forração de grama-preta"
    tufts = []
    rnd = random.Random(seed(name))
    for i in range(7):
        for j in range(7):
            x = -0.43 + i * 0.143 + rnd.uniform(-0.03, 0.03)
            y = -0.43 + j * 0.143 + rnd.uniform(-0.03, 0.03)
            tufts.append(moved(D.grass(seed(name) + i * 7 + j, 0.18, 0.2, blades=18, blade_w=0.0035, arch=1.2), (x, y, 0)))
    items = [{"name": "Forração simplificada", "material": "Folhagem escura", "in_plan": True, "shape": slab(0.15), "detail": COARSE}]
    detailed(items, None, merged(tufts), None, leaf_mat="Folhagem escura", leaf_name="Touceiras")
    yield "forracao-grama-preta", source(name, "Grama-preta 1x1 m", "Forração de grama-preta (Ophiopogon) em touceiras, 20 cm de "
                                         "altura, em placa de 1 x 1 m (repita para cobrir o canteiro)", items)


# --- lawns, beds, large planters -----------------------------------------------------------------

def P(name, value, kind="Length"):
    return {"name": name, "value": value, "kind": kind, "instance": False}


def T(name, description, **values):
    return {"name": name, "values": values, "info": {"description": description}}


def box(name, material, x, y, z, w, d, h, in_plan=False):
    def s(v):
        return v if isinstance(v, str) else f"{v:g}"
    return {"name": name, "material": material, "in_plan": in_plan,
            "shape": {"Box": {"x": s(x), "y": s(y), "z": s(z), "width": s(w), "depth": s(d), "height": s(h)}}}


def beds():
    desc = "Gramado em placas (grama-esmeralda) sobre o terreno, 3 cm de espessura"
    yield "gramado", source("Gramado", "", "", [box("Gramado", "Grama", "-Largura/2", "-Profundidade/2", 0, "Largura", "Profundidade",
                                                     0.03, True)],
                            [P("Largura", 5.0), P("Profundidade", 5.0)],
                            [T("Gramado 5x5 m", desc), T("Gramado 10x10 m", desc, Largura=10, Profundidade=10),
                             T("Gramado 2x2 m", desc, Largura=2, Profundidade=2)])

    c, h = 0.08, 0.06  # the curb: width, height above the ground
    items = [
        box("Meio-fio frontal", "Concreto aparente", "-Largura/2", "-Profundidade/2", 0, "Largura", c, h, True),
        box("Meio-fio traseiro", "Concreto aparente", "-Largura/2", f"Profundidade/2 - {c}", 0, "Largura", c, h, True),
        box("Meio-fio esquerdo", "Concreto aparente", "-Largura/2", f"-Profundidade/2 + {c}", 0, c, f"Profundidade - {2 * c}", h, True),
        box("Meio-fio direito", "Concreto aparente", f"Largura/2 - {c}", f"-Profundidade/2 + {c}", 0, c, f"Profundidade - {2 * c}", h,
            True),
        box("Cobertura de casca de pinus", "Casca de pinus", f"-Largura/2 + {c}", f"-Profundidade/2 + {c}", 0, f"Largura - {2 * c}",
            f"Profundidade - {2 * c}", 0.035),
    ]
    desc = "Canteiro no nível do terreno com meio-fio de concreto pré-moldado e cobertura de casca de pinus, para receber plantas"
    yield "canteiro-meio-fio", source("Canteiro com meio-fio", "", "", items, [P("Largura", 2.0), P("Profundidade", 1.0)],
                                      [T("Canteiro com meio-fio 2,0x1,0 m", desc),
                                       T("Canteiro com meio-fio 3,0x1,2 m", desc, Largura=3.0, Profundidade=1.2),
                                       T("Canteiro com meio-fio 1,0x1,0 m", desc, Largura=1.0, Profundidade=1.0)])

    t, cap = 0.14, 0.03
    hw = f"Altura - {cap}"
    items = [
        box("Parede frontal", "Reboco pintado", "-Largura/2", "-Profundidade/2", 0, "Largura", t, hw, True),
        box("Parede traseira", "Reboco pintado", "-Largura/2", f"Profundidade/2 - {t}", 0, "Largura", t, hw, True),
        box("Parede esquerda", "Reboco pintado", "-Largura/2", f"-Profundidade/2 + {t}", 0, t, f"Profundidade - {2 * t}", hw, True),
        box("Parede direita", "Reboco pintado", f"Largura/2 - {t}", f"-Profundidade/2 + {t}", 0, t, f"Profundidade - {2 * t}", hw, True),
        box("Pingadeira frontal", "Concreto aparente", "-Largura/2 - 0.02", "-Profundidade/2 - 0.02", hw, "Largura + 0.04", t + 0.02, cap),
        box("Pingadeira traseira", "Concreto aparente", "-Largura/2 - 0.02", f"Profundidade/2 - {t}", hw, "Largura + 0.04", t + 0.02, cap),
        box("Pingadeira esquerda", "Concreto aparente", "-Largura/2 - 0.02", f"-Profundidade/2 + {t}", hw, t + 0.02,
            f"Profundidade - {2 * t}", cap),
        box("Pingadeira direita", "Concreto aparente", f"Largura/2 - {t}", f"-Profundidade/2 + {t}", hw, t + 0.02,
            f"Profundidade - {2 * t}", cap),
        box("Terra", "Terra vegetal", f"-Largura/2 + {t}", f"-Profundidade/2 + {t}", 0, f"Largura - {2 * t}", f"Profundidade - {2 * t}",
            "Altura - 0.06"),
    ]
    desc = "Canteiro elevado de alvenaria rebocada e pintada com pingadeira de concreto, cheio de terra vegetal"
    yield "canteiro-elevado", source("Canteiro elevado", "", "", items, [P("Largura", 2.0), P("Profundidade", 0.8), P("Altura", 0.45)],
                                     [T("Canteiro elevado 2,0x0,8 m", desc),
                                      T("Canteiro elevado 3,0x1,0 m", desc, Largura=3.0, Profundidade=1.0, Altura=0.6),
                                      T("Canteiro elevado 1,2x1,2 m", desc, Largura=1.2, Profundidade=1.2)])

    ring = {"Revolution": {"plane": "Front", "offset": "0", "axis": "0", "angle": "360", "points": [
        {"u": "Diametro/2 - 0.08", "v": "0"}, {"u": "Diametro/2", "v": "0"}, {"u": "Diametro/2", "v": "0.05"},
        {"u": "Diametro/2 - 0.01", "v": "0.06"}, {"u": "Diametro/2 - 0.07", "v": "0.06"}, {"u": "Diametro/2 - 0.08", "v": "0.05"}]}}
    gravel = {"Cylinder": {"x": "0", "y": "0", "z": "0", "radius": "Diametro/2 - 0.08", "height": "0.035"}}
    items = [{"name": "Borda de concreto", "material": "Concreto aparente", "in_plan": True, "shape": ring},
             {"name": "Seixo", "material": "Seixo branco", "in_plan": False, "shape": gravel}]
    desc = "Canteiro redondo com borda de concreto e cobertura de seixo branco, para uma árvore ou um grupo de plantas"
    yield "canteiro-redondo", source("Canteiro redondo", "", "", items, [P("Diametro", 1.5)],
                                     [T("Canteiro redondo Ø1,5 m", desc), T("Canteiro redondo Ø1,0 m", desc, Diametro=1.0),
                                      T("Canteiro redondo Ø2,0 m", desc, Diametro=2.0)])


def planters():
    import vegetation_detail as D
    a, h, w = 0.8, 0.8, 0.05  # square concrete planter with a shrub
    items = [
        box("Vaso - face frontal", "Concreto aparente", -a / 2, -a / 2, 0, a, w, h, True),
        box("Vaso - face traseira", "Concreto aparente", -a / 2, a / 2 - w, 0, a, w, h, True),
        box("Vaso - face esquerda", "Concreto aparente", -a / 2, -a / 2 + w, 0, w, a - 2 * w, h, True),
        box("Vaso - face direita", "Concreto aparente", a / 2 - w, -a / 2 + w, 0, w, a - 2 * w, h, True),
        box("Terra", "Terra vegetal", -a / 2 + w, -a / 2 + w, 0, a - 2 * w, a - 2 * w, h - 0.05),
    ]
    name = "Vaso de concreto com arbusto"
    items += coarse(VC.shrub(seed(name), 1.0, 1.0, z0=h - 0.14, clusters=12), "Folhagem clara", leaf_name="Planta")
    fw, fl, _ = D.fine_shrub(seed(name), 1.0, 1.0, z0=h - 0.05, leaf_len=0.045, leaf_w=0.024)
    detailed(items, fw, fl, None, leaf_mat="Folhagem clara", wood_name="Caules")
    yield "vaso-concreto-quadrado", source(name, "Vaso de concreto 80x80", "Vaso quadrado de concreto aparente 80 x 80 x 80 cm com "
                                           "arbusto de pingo-de-ouro", items)

    Dv, Hv = 1.0, 0.9  # round fibreglass planter with a small tree
    pot = {"Revolution": {"plane": "Front", "offset": "0", "axis": "0", "angle": "360", "points": [
        {"u": "0", "v": "0"}, {"u": f"{Dv * 0.4:g}", "v": "0"}, {"u": f"{Dv / 2:g}", "v": f"{Hv - 0.03:g}"},
        {"u": f"{Dv / 2:g}", "v": f"{Hv:g}"}, {"u": f"{Dv / 2 - 0.03:g}", "v": f"{Hv:g}"}, {"u": f"{Dv / 2 - 0.035:g}", "v": f"{Hv - 0.05:g}"},
        {"u": "0", "v": f"{Hv - 0.05:g}"}]}}
    name = "Vaso de fibra com árvore"
    soil = {"Cylinder": {"x": "0", "y": "0", "z": f"{Hv - 0.05:g}", "radius": f"{Dv / 2 - 0.04:g}", "height": "0.005"}}
    items = [{"name": "Vaso", "material": "Fibra de vidro grafite", "in_plan": True, "shape": pot},
             {"name": "Terra", "material": "Terra vegetal", "in_plan": False, "shape": soil}]
    zt = Hv - 0.05
    items += coarse(VC.tree(seed(name), 2.4, 1.6, 0.9, 0.08, clusters=18, limbs=4), "Folhagem", offset=(0, 0, zt))
    fw, fl, _ = D.fine_tree(seed(name), 2.4, 1.6, 0.9, 0.08, points=380, leaf_len=0.07, leaf_w=0.03, per=9)
    detailed(items, moved(fw, (0, 0, zt)), moved(fl, (0, 0, zt)), None, leaf_mat="Folhagem")
    yield "vaso-fibra-arvore", source(name, "Vaso de fibra Ø100 com árvore", "Vaso redondo de fibra de vidro grafite Ø1,0 m x 0,9 m "
                                      "com árvore ornamental de pequeno porte (3,3 m de altura total)", items)

    L, B, Hh, w = 1.2, 0.4, 0.4, 0.035  # rectangular planter with three flowering shrubs
    items = [
        box("Jardineira - face frontal", "Fibra de vidro grafite", -L / 2, -B / 2, 0, L, w, Hh, True),
        box("Jardineira - face traseira", "Fibra de vidro grafite", -L / 2, B / 2 - w, 0, L, w, Hh, True),
        box("Jardineira - face esquerda", "Fibra de vidro grafite", -L / 2, -B / 2 + w, 0, w, B - 2 * w, Hh, True),
        box("Jardineira - face direita", "Fibra de vidro grafite", L / 2 - w, -B / 2 + w, 0, w, B - 2 * w, Hh, True),
        box("Terra", "Terra vegetal", -L / 2 + w, -B / 2 + w, 0, L - 2 * w, B - 2 * w, Hh - 0.04),
    ]
    name = "Jardineira com flores"
    c_light, c_shade, c_bloom, fine_w, fine_l, fine_b = [], [], [], [], [], []
    for k, x in enumerate((-0.37, 0.0, 0.37)):
        parts = VC.shrub(seed(name) + k, 0.45, 0.4, z0=Hh - 0.05, clusters=8, flowers=6)
        c_light.append(moved(parts["light"], (x, 0, 0)))
        c_shade.append(moved(parts["shade"], (x, 0, 0)))
        c_bloom.append(moved(parts["bloom"], (x, 0, 0)))
        fw, fl, fb = D.fine_shrub(seed(name) + k, 0.4, 0.38, z0=Hh - 0.04, leaf_len=0.045, leaf_w=0.022, stems=4, cap=900, umbels=7,
                                  flower_size=0.01)
        fine_w.append(moved(fw, (x, 0, 0)))
        fine_l.append(moved(fl, (x, 0, 0)))
        fine_b.append(moved(fb, (x, 0, 0)))
    items += coarse({"light": merged(c_light), "shade": merged(c_shade), "bloom": merged(c_bloom)}, "Folhagem", "Floração laranja",
                    leaf_name="Plantas")
    detailed(items, merged(fine_w), merged(fine_l), merged(fine_b), bloom_mat="Floração laranja", wood_name="Caules")
    yield "jardineira-flores", source(name, "Jardineira 120x40", "Jardineira retangular de fibra de vidro grafite 120 x 40 x 40 cm "
                                      "com três ixoras floridas", items)


def dumps(src) -> str:
    """JSON with two-space indents, number lists kept on one line."""
    text = json.dumps(src, ensure_ascii=False, indent=2)
    return re.sub(r"\[\s+(-?[\d.e-]+(?:,\s+-?[\d.e-]+)*)\s+\]", lambda m: "[" + re.sub(r",\s+", ", ", m.group(1)) + "]",
                  text) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):  # the folder is all generated
        old.unlink()
    for make in (trees, conifers, palms, shrubs, pots, grasses, ground_covers, beds, planters):
        for file, src in make():
            (OUT / f"{file}.json").write_text(dumps(src), encoding="utf-8", newline="\n")
            print(f"sources/planting/{file}.json")


if __name__ == "__main__":
    main()
