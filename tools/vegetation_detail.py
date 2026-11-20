"""The detailed plants of tools/vegetation.py: what the medium and fine detail levels draw.

The coarse level keeps the light low-poly silhouettes of vegetation.py; these meshes are the real look: branches by
space colonization ending in twigs, sprays of single leaves (each a folded tetrahedron of four vertices), five-petal flowers, palm fronds with leaflets or fans, conifer whorls with needle tufts, multi-stem shrubs
and grass blades. Every plant comes from a fixed seed.
"""

from __future__ import annotations

import math
import random

from vegetation import UP, Mesh, add, bounds, colonize, cross, dot, loft, mul, perpendicular, pipe_radii, sub, tube, unit

GOLDEN = math.radians(137.5)


# --- leaves, sprays, flowers ------------------------------------------------------------------

def leaf(mesh: Mesh, base, d, n, ln, w, fold=0.25, curl=0.0):
    """A leaf from `base` along the unit `d`, its face towards `n`: a folded tetrahedron (four vertices, four faces).

    The two upper faces meet along the midrib, base to tip; `fold` drops the edges, `curl` bends the tip down.
    """
    side = unit(cross(n, d))
    up = cross(d, side)
    tip = add(add(base, mul(d, ln)), mul(up, -curl * ln))
    mid = add(add(base, mul(d, ln * 0.42)), mul(up, -(curl * 0.3 * ln + max(fold, 0.06) * w * 0.5)))
    l, r = add(mid, mul(side, w / 2)), add(mid, mul(side, -w / 2 * 0.96))
    r = add(r, mul(up, -0.02 * w))  # a hair lower: the solid is never flat
    b, t, L, R = (mesh.vertex(p) for p in (base, tip, l, r))
    faces = [[b, L, t], [b, t, R], [b, R, L], [L, R, t]]
    v = mesh.vertices
    vol = sum(dot(v[f[0]], cross(v[f[1]], v[f[2]])) for f in faces)
    mesh.faces += faces if vol > 0 else [f[::-1] for f in faces]


def flower(mesh: Mesh, center, n, size, petals=4, rnd=None, cup=0.35):
    """A flower facing `n`: `petals` leaves round its center, cupped up by `cup`."""
    a0 = rnd.uniform(0, 2 * math.pi) if rnd else 0.0
    e1 = perpendicular(n)
    e2 = cross(n, e1)
    for k in range(petals):
        a = a0 + 2 * math.pi * k / petals
        d = unit(add(add(mul(e1, math.cos(a)), mul(e2, math.sin(a))), mul(n, cup)))
        leaf(mesh, center, d, n, size, size * 0.7, fold=0.1)


def spray(wood, leaves, p, d, ln, rnd, *, count=9, leaf_len=0.15, leaf_w=0.07, twig=0.0, droop=0.25, face_up=0.6,
          curl=0.15, blooms=None, bloom_share=0.0, bloom_size=0.06, petals=4):
    """A twig from `p` along `d`, `ln` long, with `count` leaves alternating along it and one at the tip."""
    d = unit(d)
    pts = []
    for i in range(4):
        t = i / 3
        pts.append(add(add(p, mul(d, ln * t)), mul(UP, -droop * ln * t * t)))
    if twig > 0 and wood is not None:
        tube(wood, pts, [twig, twig * 0.75, twig * 0.5, twig * 0.3], 4)
    ref = perpendicular(d)
    for i in range(count):
        t = 0.25 + 0.75 * i / max(count - 1, 1)
        k = min(2, int(t * 3))
        q = add(pts[k], mul(sub(pts[min(k + 1, 3)], pts[k]), t * 3 - k))
        a = GOLDEN * i + rnd.uniform(-0.3, 0.3)
        out = unit(add(mul(ref, math.cos(a)), mul(cross(d, ref), math.sin(a))))
        ld = unit(add(mul(d, 0.8), out))
        if i == count - 1:
            ld = d
        n = unit(add(mul(UP, face_up), add(mul(out, 1 - face_up), (rnd.uniform(-.2, .2), rnd.uniform(-.2, .2), 0))))
        if abs(dot(n, ld)) > 0.95:
            n = perpendicular(ld)
        s = rnd.uniform(0.8, 1.15)
        if blooms is not None and rnd.random() < bloom_share:
            flower(blooms, q, unit(add(n, mul(ld, 0.5))), bloom_size * s, petals, rnd)
        else:
            leaf(leaves, q, ld, n, leaf_len * s, leaf_w * s, curl=curl)


def ellipsoid_area(a, b, c):
    """Surface of an ellipsoid (Thomsen's approximation)."""
    q = 1.6075
    return 4 * math.pi * (((a * b) ** q + (a * c) ** q + (b * c) ** q) / 3) ** (1 / q)


def budget(area, ln, w, cover, cap):
    """How many leaves of ln x w cover `area` `cover` times over, and their size: past `cap` leaves they grow instead."""
    n = cover * area / (0.5 * ln * w)
    k = max(1.0, math.sqrt(n / cap))
    return int(min(n, cap)), ln * k, w * k


# --- trees -------------------------------------------------------------------------------------

def fine_tree(seed, height, crown, clear, trunk, *, points=600, leaf_len=0.16, leaf_w=0.07, per=9, cover=2.2, cap=2800,
              flowers=0.0, bloom_size=0.05, flat=1.0, droop=0.25, sprays=None):
    """A broadleaf tree: branches down to twigs, leaf sprays at the tips; returns wood, leaves and blooms."""
    rnd = random.Random(seed * 7 + 1)
    R, Hc = crown / 2, height - clear
    center = (0.0, 0.0, clear + Hc * 0.55)
    radii = (R * 0.85, R * 0.85, Hc / 2 * 0.85 * flat)
    nodes, parents = colonize(rnd, clear + Hc * 0.1, center, radii, points=points, step=max(radii) / 10)
    rr, children = pipe_radii(parents, trunk / 2, exponent=2.0)
    n_leaves, leaf_len, leaf_w = budget(ellipsoid_area(R, R, Hc / 2 * flat), leaf_len, leaf_w, cover, cap)
    sprays = n_leaves // per
    bloom_size *= max(1.0, leaf_len / 0.12) ** 0.5
    wood, leaves, bloom = Mesh(), Mesh(), Mesh()
    # Every branch as tubes, the thickest child continuing each path.
    stack, done = [[0]], []
    while stack:
        chain = stack.pop()
        node = chain[-1]
        while children[node]:
            kids = sorted(children[node], key=lambda c: -rr[c])
            for c in kids[1:]:
                stack.append([node, c])
            chain.append(kids[0])
            node = kids[0]
        if len(chain) > 1:
            done.append(chain)
    for chain in done:
        # The thin end of a path is left to the twigs and the leaves that hide it.
        while len(chain) > 2 and rr[chain[-1]] < 0.012:
            chain = chain[:-1]
        if len(chain) < 2 or rr[chain[0]] < 0.012:
            continue
        rs = [rr[i] for i in chain]
        sides = 8 if rs[0] > trunk * 0.3 else 5 if rs[0] > 0.03 else 4
        tube(wood, [nodes[i] for i in chain], rs, sides)
    step = max(radii) / 10
    # Leaf sprays around the thin branches: each hangs on a twig from a branch node, outwards from the trunk.
    thin = [i for i in range(len(nodes)) if rr[i] < max(0.025, trunk * 0.08) and nodes[i][2] > clear + Hc * 0.15]
    for _ in range(sprays):
        i = thin[rnd.randrange(len(thin))]
        p0 = nodes[i]
        out = unit(add(sub(p0, (0.0, 0.0, p0[2] * 0.6)), (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.6, 0.9))))
        p = add(p0, mul(out, step * rnd.uniform(0.2, 0.9)))
        tube(wood, [p0, p], [0.006, 0.003], 4)
        d = unit(add(out, (rnd.uniform(-.5, .5), rnd.uniform(-.5, .5), rnd.uniform(-.2, .4))))
        spray(None, leaves, p, d, step * rnd.uniform(0.8, 1.2), rnd, count=per, leaf_len=leaf_len, leaf_w=leaf_w, droop=droop,
              blooms=bloom, bloom_share=flowers, bloom_size=bloom_size, petals=1)
    # Fit like the coarse tree: the crown sized to the species, the trunk bending towards it.
    crown_meshes = [m for m in (leaves, bloom) if m.vertices]
    lo, hi = bounds(crown_meshes)
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    kxy = crown / max(hi[0] - lo[0], hi[1] - lo[1])
    kz = height / hi[2]

    def place(p):
        w = min(1.0, max(0.0, p[2] / clear)) ** 2
        return ((p[0] - cx * w) * kxy, (p[1] - cy * w) * kxy, p[2] * kz)

    for m in (wood, leaves, bloom):
        m.transform(place)
    return wood, leaves, bloom


# --- conifers ------------------------------------------------------------------------------------

def fine_pine(seed, height, crown, clear, trunk, *, whorl=0.7, arms=5):
    """A pine: a tapering trunk, whorls of branches that droop and turn up, needle tufts along them."""
    rnd = random.Random(seed * 7 + 2)
    R = crown / 2
    wood, leaves = Mesh(), Mesh()
    tube(wood, [(0, 0, 0), (0, 0, height * 0.5), (0, 0, height * 0.97)], [trunk / 2, trunk * 0.3, 0.02], 9)
    z = clear
    while z < height * 0.95:
        t = (z - clear) / (height - clear)
        reach = R * (1 - t) ** 0.9 + 0.25
        spin = rnd.uniform(0, 2 * math.pi)
        n_arms = arms if t < 0.85 else 3
        for j in range(n_arms):
            a = spin + 2 * math.pi * j / n_arms + rnd.uniform(-0.25, 0.25)
            d = (math.cos(a), math.sin(a), 0.0)
            L = reach * rnd.uniform(0.85, 1.05)
            pts = [(0, 0, z)]
            for s in range(1, 5):
                u = s / 4
                pts.append(add((d[0] * L * u, d[1] * L * u, z), (0, 0, L * (0.08 * u - 0.22 * u * u + 0.2 * u ** 3))))
            r0 = max(0.012, trunk * 0.18 * (1 - t))
            tube(wood, pts, [r0, r0 * 0.7, r0 * 0.5, r0 * 0.35, r0 * 0.2], 5)
            # Needle tufts along the outer two thirds of the branch, and side sprays.
            for s in range(1, 5):
                for q in range(2):
                    base = add(pts[s], mul(sub(pts[min(s + 1, 4)], pts[s]), q / 2))
                    side = unit(cross(d, UP)) if q % 2 else unit(cross(UP, d))
                    tuft(leaves, base, unit(add(add(d, mul(side, 0.6)), (0, 0, 0.25))), rnd, 0.3 * (1 - 0.3 * t))
            tuft(leaves, pts[-1], unit(add(d, (0, 0, 0.4))), rnd, 0.32)
            # Side branchlets off the outer half, each ending in tufts.
            for s in (3,):
                for sgn in (-1, 1):
                    sd = unit(add(d, mul(cross(UP, d), sgn * 1.1)))
                    q0 = pts[s]
                    ql = L * 0.28 * (1 - 0.4 * t)
                    q1 = add(q0, add(mul(sd, ql), (0, 0, ql * 0.15)))
                    tube(wood, [q0, q1], [r0 * 0.25, 0.004], 4)
                    for u in (1.0,):
                        tuft(leaves, add(q0, mul(sub(q1, q0), u)), unit(add(sd, (0, 0, 0.35))), rnd, 0.28 * (1 - 0.3 * t))
        z += whorl * rnd.uniform(0.85, 1.15)
    for q in range(4):
        tuft(leaves, (0, 0, height * 0.95 + q * 0.04), unit((rnd.uniform(-.3, .3), rnd.uniform(-.3, .3), 1)), rnd, 0.2)
    return wood, leaves


def tuft(mesh, base, d, rnd, ln, n=6, spread=0.65):
    """A tuft of needles from `base` around the direction `d`."""
    e1 = perpendicular(d)
    e2 = cross(d, e1)
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.2, 0.2)
        nd = unit(add(d, add(mul(e1, math.cos(a) * spread), mul(e2, math.sin(a) * spread))))
        leaf(mesh, base, nd, perpendicular(nd), ln * rnd.uniform(0.8, 1.1), 0.03, fold=0.0)


def fine_column(seed, height, crown, clear, trunk, *, leaf_len=0.12, cover=2.0, cap=3600):
    """A columnar conifer (cypress, thuja): short ascending branches and dense fans of scale-leaf sprays."""
    rnd = random.Random(seed * 7 + 3)
    R = crown / 2
    n, leaf_len, _ = budget(ellipsoid_area(R, R, (height - clear) / 2) * 0.85, leaf_len, leaf_len * 0.45, cover, cap)
    sprays = n // 6
    wood, leaves = Mesh(), Mesh()
    tube(wood, [(0, 0, 0), (0, 0, height * 0.6), (0, 0, height * 0.95)], [trunk / 2, trunk * 0.3, 0.015], 7)

    def radius(z):
        t = (z - clear) / (height - clear)
        return R * max(0.08, math.sin(math.pi * min(1.0, 0.18 + t * 0.9)) ** 0.7 * (1 - 0.45 * t))

    for k in range(28):  # a few visible branches
        z = clear + (height - clear) * rnd.uniform(0.05, 0.85)
        a = rnd.uniform(0, 2 * math.pi)
        r = radius(z) * 0.75
        tube(wood, [(0, 0, z), (math.cos(a) * r, math.sin(a) * r, z + r * 0.8)], [0.02, 0.006], 4)
    for k in range(sprays):
        z = clear + (height - clear) * (rnd.random() ** 0.9)
        a = GOLDEN * k
        r = radius(z) * rnd.uniform(0.78, 1.0)
        p = (math.cos(a) * r, math.sin(a) * r, z)
        out = unit((math.cos(a), math.sin(a), 0.0))
        d = unit(add(mul(out, 0.45), (0, 0, 1)))
        for j in range(6):
            b = (j - 2.5) * 0.35
            side = cross(UP, out)
            ld = unit(add(d, mul(side, b)))
            leaf(leaves, add(p, mul(ld, -0.02)), ld, out, leaf_len * rnd.uniform(0.85, 1.15), leaf_len * 0.45, fold=0.15)
    return wood, leaves


# --- palms ------------------------------------------------------------------------------------------

def ringed_trunk(wood, height, stem, lean, rings=0.09, base_flare=1.35):
    n = max(12, int(height / rings))
    path, radii = [], []
    for i in range(n + 1):
        t = i / n
        z = height * t
        path.append((lean * height * t ** 1.6, 0.0, z))
        r = stem / 2 * ((base_flare - 0.25) * (1 - t) ** 6 + 1.1 - 0.25 * t)
        if 0 < i < n:
            r *= 1.0 + (0.035 if i % 2 else -0.01)
        radii.append(r)
    tube(wood, path, radii, 10)
    return path[-1]


def fine_palm(seed, height, crown, stem, *, fronds=16, droop=0.7, lean=0.0, shaft=False, rise=(60, -10), leaflets=58,
              plumose=False, fan=False):
    """A palm: a ringed stem, a crownshaft or not, pinnate fronds with leaflets (or fan leaves)."""
    rnd = random.Random(seed * 7 + 4)
    wood, leaves, green = Mesh(), Mesh(), Mesh()
    R = crown / 2
    L = R * 1.1
    h = height - L * 0.3
    top = ringed_trunk(wood, h, stem, lean, rings=0.12 if fan else 0.09, base_flare=1.2 if fan else 1.3)
    if shaft:
        tube(green, [add(top, (0, 0, -0.05)), add(top, (0, 0, h * 0.1))], [stem / 2 * 1.12, stem / 2 * 0.95], 12)
        top = add(top, (0, 0, h * 0.1))
    for k in range(fronds):
        az = GOLDEN * k + rnd.uniform(-0.1, 0.1)
        frac = k / max(fronds - 1, 1)
        el = math.radians(rise[0] + (rise[1] - rise[0]) * (rnd.random() * 0.4 + frac * 0.6))
        d = (math.cos(az), math.sin(az), 0.0)
        side = (-math.sin(az), math.cos(az), 0.0)
        Lk = L * rnd.uniform(0.85, 1.05)

        def spine(t):
            return add(top, mul(add(mul(d, math.cos(el) * t), mul(UP, math.sin(el) * t - droop * t * t)), Lk))

        def tangent(t):
            return unit(add(mul(d, math.cos(el)), mul(UP, math.sin(el) - 2 * droop * t)))

        if fan:
            # Petiole to the hastula, then a fan of folded segments with drooping tips.
            pet = [spine(t * 0.45) for t in (0, 0.33, 0.66, 1.0)]
            tube(green, pet, [0.04, 0.03, 0.025, 0.02], 5)
            c = pet[-1]
            tg = tangent(0.45)
            nrm = unit(cross(side, tg))
            for j in range(17):
                a = math.radians(-95 + 190 * j / 16)
                sd = unit(add(add(mul(tg, math.cos(a)), mul(side, math.sin(a))), mul(nrm, 0.15)))
                leaf(leaves, c, sd, nrm, Lk * 0.55 * rnd.uniform(0.9, 1.05), 0.2, fold=0.35, curl=0.3)
            continue
        steps = 10
        pts = [spine(i / steps) for i in range(steps + 1)]
        tube(green, pts, [0.025 * (1 - 0.85 * i / steps) + 0.004 for i in range(steps + 1)], 5)
        for j in range(leaflets):
            t = 0.12 + 0.86 * j / (leaflets - 1)
            s = spine(t)
            tg = tangent(t)
            nrm = unit(cross(side, tg))
            nrm = nrm if nrm[2] >= 0 else mul(nrm, -1)
            lf = Lk * 0.42 * (0.35 + 0.65 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.7)
            for sgn in (1, -1):
                tilt = (0.5 if (j % 3 == 0) else -0.35 if (j % 3 == 1) else 0.0) if plumose else (0.25 if j % 2 else -0.45)
                ld = unit(add(add(mul(side, sgn), mul(tg, 0.55)), mul(nrm, tilt)))
                leaf(leaves, s, ld, nrm, lf * rnd.uniform(0.9, 1.05), lf * 0.1 + 0.025, fold=0.5, curl=0.45)
    lo, hi = bounds([leaves])
    kxy = crown / max(hi[0] - lo[0], hi[1] - lo[1])
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    for m in (leaves, green):
        m.transform(lambda p: (top[0] + (p[0] - cx) * kxy, top[1] + (p[1] - cy) * kxy, top[2] + (p[2] - top[2]) * kxy))
    meshes = [m for m in (wood, leaves, green) if m.vertices]
    kz = height / bounds(meshes)[1][2]
    for m in meshes:
        m.transform(lambda p: (p[0], p[1], p[2] * kz))
    return wood, leaves, green


# --- shrubs, grasses, ground covers ---------------------------------------------------------------

def fine_shrub(seed, height, width, *, z0=0.0, stems=7, leaf_len=0.06, leaf_w=0.03, topiary=False, cover=2.0, cap=3000,
               flowers=0, flower_size=0.05, umbels=0, petals=5, leaves_n=None):
    """A shrub: stems from the base fanning out, leaf sprays filling an ellipsoid (a clipped shell for topiary)."""
    rnd = random.Random(seed * 7 + 5)
    R, H = width / 2, height
    wood, leaves, bloom = Mesh(), Mesh(), Mesh()
    c = (0.0, 0.0, z0 + H * 0.55)
    rad = (R, R, H * 0.45)
    leaves_n, leaf_len, leaf_w = budget(ellipsoid_area(*rad), leaf_len, leaf_w, cover, cap)
    for k in range(stems):
        a = 2 * math.pi * k / stems + rnd.uniform(-0.3, 0.3)
        r = R * rnd.uniform(0.3, 0.6)
        top = (math.cos(a) * r, math.sin(a) * r, z0 + H * rnd.uniform(0.6, 0.85))
        mid = (top[0] * 0.4, top[1] * 0.4, z0 + H * 0.3)
        tube(wood, [(math.cos(a) * 0.02, math.sin(a) * 0.02, z0), mid, top], [0.012 * width + 0.006, 0.008 * width + 0.004, 0.003], 5)
    per = 6
    count = leaves_n // per
    for k in range(count):
        while True:
            u = (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))
            q = dot(u, u)
            if q <= 1 and (q >= (0.75 if topiary else 0.25)):
                break
        p = (c[0] + u[0] * rad[0], c[1] + u[1] * rad[1], c[2] + u[2] * rad[2])
        if p[2] < z0 + 0.02:
            continue
        out = unit(u) if q > 1e-6 else UP
        d = unit(add(out, (rnd.uniform(-.5, .5), rnd.uniform(-.5, .5), 0.4)))
        spray(None, leaves, p, d, leaf_len * 2.2, rnd, count=per, leaf_len=leaf_len, leaf_w=leaf_w, droop=0.1, face_up=0.4,
              curl=0.1)
    for k in range(flowers):
        u = unit((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.2, 1)))
        p = (c[0] + u[0] * rad[0] * 1.0, c[1] + u[1] * rad[1], c[2] + u[2] * rad[2])
        flower(bloom, p, unit(add(u, (0, 0, 0.3))), flower_size * rnd.uniform(0.85, 1.1), petals, rnd)
    for k in range(umbels):
        u = unit((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.0, 1)))
        p = (c[0] + u[0] * rad[0], c[1] + u[1] * rad[1], c[2] + u[2] * rad[2])
        umbel(bloom, p, u, rnd, flower_size, 14)
    return wood, leaves, bloom


def umbel(mesh, p, n, rnd, size, florets=14, radius=None):
    """A rounded head of small four-petal florets around `p`, facing `n` (ixora, agapanthus)."""
    radius = radius or size * 1.6
    for k in range(florets):
        a = GOLDEN * k
        z = 1 - (k + 0.5) / florets
        r = math.sqrt(max(0.0, 1 - z * z))
        e1 = perpendicular(n)
        e2 = cross(n, e1)
        dvec = unit(add(add(mul(e1, r * math.cos(a)), mul(e2, r * math.sin(a))), mul(n, z)))
        flower(mesh, add(p, mul(dvec, radius)), dvec, size, 3, rnd, cup=0.2)


def grass(seed, height, width, *, blades=60, blade_w=0.012, arch=0.6, stiff=False, z0=0.0):
    """A tuft of grass blades: each a thin tapering strip lofted along an arching curve."""
    rnd = random.Random(seed * 7 + 6)
    m = Mesh()
    for k in range(blades):
        a = GOLDEN * k + rnd.uniform(-0.2, 0.2)
        out = (math.cos(a), math.sin(a), 0.0)
        side = (-math.sin(a), math.cos(a), 0.0)
        base = (out[0] * width * 0.08 * rnd.random(), out[1] * width * 0.08 * rnd.random(), z0)
        lean = rnd.uniform(0.15, 0.55) if not stiff else rnd.uniform(0.05, 0.25)
        L = height * rnd.uniform(0.75, 1.15) * (1.15 if not stiff else 1.0)
        bend = arch * rnd.uniform(0.6, 1.2)
        sections = []
        n = 4
        for i in range(n + 1):
            t = i / n
            s = add(base, add(mul(out, L * (lean * t + bend * t ** 3 / 3) * 0.9), (0, 0, L * t * (1 - 0.45 * bend * t * t))))
            if i == n:
                sections.append([s])
                break
            w = blade_w * (1 - t) ** 0.6 + 0.001
            sections.append([add(s, mul(side, w)), add(s, (0, 0, 0.002 * (1 - t) + 0.0005)), add(s, mul(side, -w))])
        loft(m, sections)
    lo, hi = bounds([m])
    kz = height / (hi[2] - z0)
    kxy = width / max(hi[0] - lo[0], hi[1] - lo[1])
    m.transform(lambda p: (p[0] * kxy, p[1] * kxy, z0 + (p[2] - z0) * kz))
    return m

