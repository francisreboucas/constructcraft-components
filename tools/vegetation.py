#!/usr/bin/env python3
"""Generate the planting sources (sources/planting/*.json).

    python tools/vegetation.py      then  python tools/build.py

Plants are fixed meshes, one per type, sized to the species (height and crown
width of a mature plant), at two detail levels: the coarse level is a light
low-poly silhouette (the functions below), the medium and fine levels the
detailed plant of tools/vegetation_detail.py (branches down to twigs, sprays of
single leaves, flowers, palm leaflets and fans, needle tufts, grass blades),
with the number and size of the leaves worked out from the crown's area.
Lawns, planting beds and planters with walls are parametric pieces.

- Trees grow their branches by space colonization (Runions, Lane and
  Prusinkiewicz, "Modeling trees with a space colonization algorithm", 2007):
  attraction points fill the crown envelope and the branch tips grow towards
  them. Branch thickness follows the pipe model (the cross-section below a
  fork matches those above it, r^n = sum of the children's r^n), and the
  branch tips gather into foliage clumps, jittered icospheres.
- Palms have a leaning, tapering stem and arching fronds lofted along a
  curved spine with a V-folded section.
- Conifers stack drooping tiers with a jagged rim; columnar ones and shrubs
  are clusters of clumps.

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


def _icosphere():
    t = (1 + math.sqrt(5)) / 2
    verts = [unit(v) for v in [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t),
                               (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2),
             (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5),
             (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    mids: dict = {}

    def mid(a, b):
        key = (min(a, b), max(a, b))
        if key not in mids:
            verts.append(unit(mul(add(verts[a], verts[b]), 0.5)))
            mids[key] = len(verts) - 1
        return mids[key]

    out = []
    for a, b, c in faces:
        ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
        out += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
    return verts, out


ICO_VERTS, ICO_FACES = _icosphere()  # 42 vertices, 80 faces


def clump(mesh: Mesh, center, radii, rnd: random.Random, jitter=0.12):
    """A foliage clump: an icosphere stretched to `radii`, its vertices jittered."""
    base = len(mesh.vertices)
    for v in ICO_VERTS:
        k = 1 + rnd.uniform(-jitter, jitter)
        mesh.vertex(add(center, (v[0] * radii[0] * k, v[1] * radii[1] * k, v[2] * radii[2] * k)))
    for f in ICO_FACES:
        idx = [base + i for i in f]
        mesh.face(idx, sub(mesh.centroid(idx), center))


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


def fit(meshes, width, height, z0=0.0):
    """Scale and move `meshes` to `width` (largest plan side) by `height`, centered, from `z0` up."""
    lo, hi = bounds(meshes)
    kxy = width / max(hi[0] - lo[0], hi[1] - lo[1])
    kz = height / (hi[2] - lo[2])
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    for m in meshes:
        m.transform(lambda p: ((p[0] - cx) * kxy, (p[1] - cy) * kxy, z0 + (p[2] - lo[2]) * kz))


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


def chains(children, radii, min_radius):
    """Paths of nodes to draw as tubes: each fork continues along its thickest
    child and starts new paths at the others; thin twigs are left out."""
    out, stack = [], [[0]]
    while stack:
        chain = stack.pop()
        node = chain[-1]
        while True:
            kids = sorted((c for c in children[node] if radii[c] >= min_radius), key=lambda c: -radii[c])
            if not kids:
                break
            for c in kids[1:]:
                stack.append([node, c])
            chain.append(kids[0])
            node = kids[0]
        if len(chain) > 1:
            out.append(chain)
    return out


def kmeans(points, k, rnd, rounds=12):
    """Cluster `points` into `k` groups (farthest-point start); returns the groups."""
    centers = [points[rnd.randrange(len(points))]]
    while len(centers) < min(k, len(points)):
        centers.append(max(points, key=lambda p: min(length(sub(p, c)) for c in centers)))
    for _ in range(rounds):
        groups = [[] for _ in centers]
        for p in points:
            groups[min(range(len(centers)), key=lambda i: length(sub(p, centers[i])))].append(p)
        centers = [mul(tuple(map(sum, zip(*g))), 1 / len(g)) if g else c for g, c in zip(groups, centers)]
    return [(c, g) for c, g in zip(centers, groups) if g]


def tree(seed, height, crown, clear, trunk, *, flowers=0.0, clumps=None, flat=1.0, jitter=0.14):
    """A broadleaf tree: `height` and `crown` width, `clear` trunk height, `trunk` diameter."""
    rnd = random.Random(seed)
    R, Hc = crown / 2, height - clear
    center = (0.0, 0.0, clear + Hc * 0.55)
    radii = (R * 0.8, R * 0.8, Hc / 2 * 0.8 * flat)
    nodes, parents = colonize(rnd, clear + Hc * 0.1, center, radii)
    radii_n, children = pipe_radii(parents, trunk / 2)
    wood = Mesh()
    for chain in chains(children, radii_n, max(0.015, trunk * 0.09)):
        rs = [radii_n[i] for i in chain]
        tube(wood, [nodes[i] for i in chain], rs, 7 if rs[0] > trunk * 0.3 else 5)
    tips = [nodes[i] for i in range(len(nodes)) if not children[i]]
    k = clumps or max(7, min(16, round(5 + R * 1.4)))
    leaves, bloom = Mesh(), Mesh()
    groups = kmeans(tips, k, rnd)
    for n, (c, g) in enumerate(groups):
        spread = math.sqrt(sum(dot(sub(p, c), sub(p, c)) for p in g) / len(g))
        r = max(R * 0.3, min(R * 0.5, spread * 1.2 + R * 0.12))
        target = bloom if n < round(len(groups) * flowers) else leaves
        clump(target, c, (r, r, r * 0.85 * flat), rnd, jitter)
    clump(leaves, (center[0], center[1], center[2]), (R * 0.55, R * 0.55, Hc * 0.35 * flat), rnd, jitter)
    # Center the crown on the trunk base and size it to the species: the crown
    # moves whole, the trunk bends towards it from the ground.
    crown_meshes = [m for m in (leaves, bloom) if m.vertices]
    lo, hi = bounds(crown_meshes)
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    kxy = crown / max(hi[0] - lo[0], hi[1] - lo[1])
    kz = height / hi[2]

    def place(p, bend=True):
        w = min(1.0, max(0.0, p[2] / clear)) ** 2 if bend else 1.0
        return ((p[0] - cx * w) * kxy, (p[1] - cy * w) * kxy, p[2] * kz)

    wood.transform(place)
    for m in crown_meshes:
        m.transform(lambda p: place(p, False))
    return wood, leaves, bloom


def conifer(seed, height, crown, clear, trunk, *, tiers=6, points=9, droop=0.35):
    """A conifer of drooping tiers, each a cone with a jagged rim."""
    rnd = random.Random(seed)
    R, Hc = crown / 2, height - clear
    wood, leaves = Mesh(), Mesh()
    tube(wood, [(0, 0, 0), (0, 0, clear + Hc * 0.4)], [trunk / 2, trunk * 0.35], 7)
    for i in range(tiers):
        t = i / (tiers - 1)
        base = clear + Hc * 0.78 * t
        top = height if i == tiers - 1 else base + Hc * 0.34
        r = R * (1 - 0.78 * t)
        spin = rnd.uniform(0, 2 * math.pi)
        rim = []
        for k in range(points * 2):
            a = spin + math.pi * k / points
            rr = r * (1.0 if k % 2 == 0 else 0.72) * rnd.uniform(0.92, 1.05)
            z = base - (droop * rr * 0.35 if k % 2 == 0 else 0) + rnd.uniform(-0.03, 0.03) * r
            rim.append(leaves.vertex((math.cos(a) * rr, math.sin(a) * rr, z)))
        apex = leaves.vertex((0, 0, top))
        under = leaves.vertex((0, 0, base + (top - base) * 0.12))
        n = len(rim)
        for k in range(n):
            a, b = rim[k], rim[(k + 1) % n]
            side = [a, b, apex]
            mid = leaves.centroid(side)
            leaves.face(side, (mid[0], mid[1], 0.3 * r))
            leaves.face([a, b, under], (0, 0, -1))
    fit([wood, leaves], crown, height)
    return wood, leaves


def column(seed, height, crown, clear, trunk, *, clumps=6, jitter=0.1):
    """A columnar conifer (cypress, thuja): stacked clumps narrowing to the top."""
    rnd = random.Random(seed)
    R, Hc = crown / 2, height - clear
    wood, leaves = Mesh(), Mesh()
    tube(wood, [(0, 0, 0), (0, 0, clear + Hc * 0.3)], [trunk / 2, trunk * 0.4], 6)
    for i in range(clumps):
        t = i / (clumps - 1)
        r = R * (1 - 0.6 * t ** 1.5)
        z = clear + Hc * (0.12 + 0.76 * t)
        off = (rnd.uniform(-0.08, 0.08) * R, rnd.uniform(-0.08, 0.08) * R, 0)
        clump(leaves, add((0, 0, z), off), (r, r, Hc / clumps * 0.95), rnd, jitter)
    fit([wood, leaves], crown, height)
    return wood, leaves


def shrub(seed, height, width, *, clumps=5, jitter=0.12, z0=0.0):
    """A shrub: a core clump with others around and above it, from `z0` up."""
    rnd = random.Random(seed)
    R = width / 2
    leaves = Mesh()
    clump(leaves, (0, 0, height * 0.5), (R * 0.75, R * 0.75, height * 0.45), rnd, jitter)
    for k in range(clumps - 1):
        a = 2 * math.pi * k / (clumps - 1) + rnd.uniform(-0.3, 0.3)
        d = R * rnd.uniform(0.4, 0.5)
        r = R * rnd.uniform(0.45, 0.55)
        clump(leaves, (math.cos(a) * d, math.sin(a) * d, height * rnd.uniform(0.35, 0.6)), (r, r, r * 0.9), rnd, jitter)
    fit([leaves], width, height, z0)
    return leaves


# --- palms -------------------------------------------------------------------------

def palm(seed, height, crown, stem, *, fronds=16, droop=0.7, lean=0.0, shaft=False, frond_w=0.12, rise=(60, -10)):
    rnd = random.Random(seed)
    R = crown / 2
    L = R * 1.05  # frond length
    h = height - L * 0.35
    wood, leaves, green = Mesh(), Mesh(), Mesh()
    ts = [i / 7 for i in range(8)]
    path = [(lean * h * t ** 1.6, 0.0, h * t) for t in ts]
    tube(wood, path, [stem / 2 * ((1.35 if t == 0 else 1.15) - 0.25 * t) for t in ts], 9)
    top = path[-1]
    if shaft:  # the green crownshaft of royal palms
        tube(green, [add(top, (0, 0, -h * 0.02)), add(top, (0, 0, h * 0.1))], [stem / 2 * 1.08, stem / 2 * 0.9], 9)
        top = add(top, (0, 0, h * 0.1))
    for k in range(fronds):
        az = 2 * math.pi * k / fronds * 2.0 + rnd.uniform(-0.15, 0.15)  # two turns around the stem
        frac = k / max(fronds - 1, 1)
        el = math.radians(rise[0] + (rise[1] - rise[0]) * (rnd.random() * 0.5 + frac * 0.5))
        d = (math.cos(az), math.sin(az), 0.0)
        side = (-math.sin(az), math.cos(az), 0.0)
        Lk = L * rnd.uniform(0.85, 1.05)
        sections = []
        steps = 9
        for i in range(steps + 1):
            t = i / steps
            s = add(top, mul(add(mul(d, math.cos(el) * t), mul(UP, math.sin(el) * t - droop * t * t)), Lk))
            if i == steps:
                sections.append([s])
                continue
            tang = unit(add(mul(d, math.cos(el)), mul(UP, math.sin(el) - 2 * droop * t)))
            nrm = unit(cross(side, tang))
            nrm = nrm if nrm[2] >= 0 else mul(nrm, -1)
            w = Lk * frond_w * (0.15 + 0.85 * math.sin(math.pi * min(1.0, t * 1.15)) ** 0.6)
            th = max(0.01, w * 0.05)
            fold = w * 0.35  # leaflets hang below the rachis: a V section
            sections.append([
                add(s, mul(nrm, th)),
                add(add(s, mul(side, w)), mul(nrm, -fold)),
                add(s, mul(nrm, -th)),
                add(add(s, mul(side, -w)), mul(nrm, -fold)),
            ])
        loft(leaves, sections)
    # Size the crown to the species about the top of the stem, then the whole
    # palm to its height; the stem's base stays at the origin.
    lo, hi = bounds([leaves])
    k = crown / max(hi[0] - lo[0], hi[1] - lo[1])
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    leaves.transform(lambda p: (top[0] + (p[0] - cx) * k, top[1] + (p[1] - cy) * k, top[2] + (p[2] - top[2]) * k))
    meshes = [m for m in (wood, leaves, green) if m.vertices]
    kz = height / bounds(meshes)[1][2]
    for m in meshes:
        m.transform(lambda p: (p[0], p[1], p[2] * kz))
    return wood, leaves, green


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


def detailed(items, wood=None, leaves=None, blooms=None, *, wood_mat="Casca de árvore", leaf_mat="Folhagem",
             bloom_mat="Floração amarela", wood_name="Galhos", leaf_name="Folhas", bloom_name="Flores"):
    """Append the medium/fine pieces of a plant to `items`."""
    for name, mat, mesh, plan in ((wood_name, wood_mat, wood, False), (leaf_name, leaf_mat, leaves, True),
                                  (bloom_name, bloom_mat, blooms, True)):
        if mesh is not None and mesh.vertices:
            items.append(item(name, mat, mesh, plan, DETAILED))
    return items


def trees():
    import vegetation_detail as D
    # file, species, height, crown, clear trunk, trunk diameter, foliage, share of flowering clumps, detailed look
    for file, name, H, C, F, T, mat, fl, look in [
        ("ipe-amarelo", "Ipê-amarelo", 8.0, 6.0, 2.2, 0.3, "Folhagem", 0.75,
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
        wood, leaves, bloom = tree(seed(name), H, C, F, T, flowers=fl)
        items = [item("Tronco", "Casca de árvore", wood, False, COARSE), item("Copa", mat, leaves, True, COARSE)]
        if bloom.vertices:
            items.append(item("Floração", "Floração amarela", bloom, True, COARSE))
        look = dict(look)
        bmat = look.pop("bloom", "Floração amarela")
        fw, fl_, fb = D.fine_tree(seed(name), H, C, F, T, **look)
        detailed(items, fw, fl_, fb, leaf_mat=mat, bloom_mat=bmat)
        yield file, source(name, f"{name} {H:g} m", f"Árvore de copa arredondada, {H:g} m de altura, copa Ø{C:g} m", items)


def conifers():
    import vegetation_detail as D
    for file, name, H, C, F, T, make, fine in [
        ("tuia-holandesa", "Tuia-holandesa", 4.0, 1.2, 0.15, 0.1, column,
         lambda s: D.fine_column(s, 4.0, 1.2, 0.15, 0.1, leaf_len=0.09)),
        ("cipreste-italiano", "Cipreste-italiano", 8.0, 1.6, 0.3, 0.2, column,
         lambda s: D.fine_column(s, 8.0, 1.6, 0.3, 0.2, leaf_len=0.12)),
        ("pinheiro", "Pinheiro", 12.0, 5.0, 1.8, 0.4, conifer, lambda s: D.fine_pine(s, 12.0, 5.0, 1.8, 0.4)),
    ]:
        wood, leaves = make(seed(name), H, C, F, T)
        items = [item("Tronco", "Casca de árvore", wood, False, COARSE), item("Copa", "Folhagem escura", leaves, True, COARSE)]
        fw, fl = fine(seed(name))
        leaf_mat = "Folhagem clara" if file == "tuia-holandesa" else "Folhagem escura"
        detailed(items, fw, fl, leaf_mat=leaf_mat, leaf_name="Folhagem")
        yield file, source(name, f"{name} {H:g} m", f"Conífera, {H:g} m de altura, copa Ø{C:g} m", items)


def palms():
    import vegetation_detail as D
    for file, name, H, C, Dm, kw, fine in [
        ("palmeira-imperial", "Palmeira-imperial", 15.0, 6.0, 0.45, {"fronds": 16, "shaft": True, "droop": 0.6},
         {"fronds": 16, "shaft": True, "droop": 0.6, "leaflets": 34}),
        ("jeriva", "Jerivá", 8.0, 5.0, 0.3, {"fronds": 14, "droop": 0.8, "lean": 0.03},
         {"fronds": 15, "droop": 0.85, "lean": 0.03, "leaflets": 32, "plumose": True}),
        ("palmeira-real-australiana", "Palmeira-real-australiana", 10.0, 4.0, 0.25,
         {"fronds": 12, "shaft": True, "droop": 0.55}, {"fronds": 12, "shaft": True, "droop": 0.55, "leaflets": 30}),
        ("washingtonia", "Washingtonia", 12.0, 4.0, 0.6, {"fronds": 22, "droop": 0.35, "frond_w": 0.3, "rise": (55, -35)},
         {"fronds": 18, "droop": 0.3, "rise": (55, -35), "fan": True}),
    ]:
        wood, leaves, green = palm(seed(name), H, C, Dm, **kw)
        items = [item("Estipe", "Estipe de palmeira", wood, False, COARSE)]
        if green.vertices:
            items.append(item("Palmito", "Palmito", green, False, COARSE))
        items.append(item("Folhas", "Folhagem", leaves, True, COARSE))
        fw, fl, fg = D.fine_palm(seed(name), H, C, Dm, **fine)
        detailed(items, fw, fl, None, wood_mat="Estipe de palmeira", wood_name="Estipe detalhado", leaf_name="Folíolos")
        if fg.vertices:
            items.append(item("Ráquis e palmito", "Palmito", fg, False, DETAILED))
        yield file, source(name, f"{name} {H:g} m", f"Palmeira de estipe único, {H:g} m de altura, copa Ø{C:g} m", items)


def shrubs():
    import vegetation_detail as D
    for file, name, H, C, n, j, mat, fine in [
        ("buxinho", "Buxinho", 0.5, 0.5, 3, 0.04, "Folhagem escura",
         dict(leaf_len=0.03, leaf_w=0.018, topiary=True, stems=4, cover=2.6)),
        ("ixora", "Ixora", 0.8, 0.8, 5, 0.1, "Folhagem",
         dict(leaf_len=0.07, leaf_w=0.03, umbels=16, flower_size=0.012, bloom="Floração vermelha")),
        ("pingo-de-ouro", "Pingo-de-ouro", 1.0, 1.0, 6, 0.12, "Folhagem clara", dict(leaf_len=0.045, leaf_w=0.025)),
        ("hibisco", "Hibisco", 1.8, 1.5, 7, 0.15, "Folhagem",
         dict(leaf_len=0.1, leaf_w=0.07, flowers=26, flower_size=0.065, bloom="Floração vermelha", stems=9)),
    ]:
        items = [item("Folhagem", mat, shrub(seed(name), H, C, clumps=n, jitter=j), True, COARSE)]
        fine = dict(fine)
        bmat = fine.pop("bloom", "Floração vermelha")
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
        plant = shrub(seed(f"Vaso {size}"), HP, DP, clumps=5, jitter=0.12, z0=HV * 0.9)
        items = [
            {"name": "Vaso", "material": "Terracota", "in_plan": True, "shape": pot},
            {"name": "Terra", "material": "Terra vegetal", "in_plan": False, "shape": soil},
            item("Planta", "Folhagem", plant, True, COARSE),
        ]
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
    items.append(item("Planta", "Folhagem clara", shrub(seed(name), 1.0, 1.0, clumps=6, jitter=0.12, z0=h - 0.06), True, COARSE))
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
    wood, leaves, _ = tree(seed(name), 2.4, 1.6, 0.9, 0.08)
    items += [item("Tronco", "Casca de árvore", moved(wood, (0, 0, zt)), False, COARSE),
              item("Copa", "Folhagem", moved(leaves, (0, 0, zt)), True, COARSE)]
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
    coarse, fine_w, fine_l, fine_b = [], [], [], []
    for k, x in enumerate((-0.37, 0.0, 0.37)):
        coarse.append(moved(shrub(seed(name) + k, 0.45, 0.4, clumps=4, jitter=0.1, z0=Hh - 0.05), (x, 0, 0)))
        fw, fl, fb = D.fine_shrub(seed(name) + k, 0.4, 0.38, z0=Hh - 0.04, leaf_len=0.045, leaf_w=0.022, stems=4, cap=900, umbels=7,
                                  flower_size=0.01)
        fine_w.append(moved(fw, (x, 0, 0)))
        fine_l.append(moved(fl, (x, 0, 0)))
        fine_b.append(moved(fb, (x, 0, 0)))
    items.append(item("Plantas", "Folhagem", merged(coarse), True, COARSE))
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
