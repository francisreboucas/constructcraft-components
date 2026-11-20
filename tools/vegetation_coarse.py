"""The coarse plants of tools/vegetation.py: light silhouettes that still read as plants.

What the coarse detail level (plans, site plans, distant views) draws: a trunk that forks into its main limbs, a crown
of many leaf clusters spread over the crown's envelope with gaps between them (the limbs show through), the clusters
in two tones (light on top, shade below and inside), palm fronds with a serrated edge and fan leaves with a notched
rim, conifer whorls of flattened pads, shrubs of clusters with a few flowers. A few hundred to two thousand faces per
plant. Each function returns a dict of meshes by role: wood, light, shade, bloom, green.
"""

from __future__ import annotations

import math
import random

from vegetation import UP, Mesh, add, bounds, cross, loft, mul, perpendicular, sub, tube, unit

GOLDEN = math.pi * (3 - math.sqrt(5))


def _ico(level):
    t = (1 + math.sqrt(5)) / 2
    verts = [unit(v) for v in [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t),
                               (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2),
             (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5),
             (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(level):
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
        faces = out
    return verts, faces


ICO = {k: _ico(k) for k in (0, 1, 2)}


def cluster(mesh: Mesh, center, radii, rnd, jitter=0.18, level=1, flat=0.6, lumps=0.0):
    """A leaf cluster: an icosphere to `radii`, its underside flattened by `flat`, its vertices jittered (and lumpy)."""
    verts, faces = ICO[level]
    base = len(mesh.vertices)
    phase = (rnd.uniform(0, 6.3), rnd.uniform(0, 6.3), rnd.uniform(0, 6.3))
    for v in verts:
        k = 1 + rnd.uniform(-jitter, jitter)
        if lumps:
            k += lumps * math.sin(3 * v[0] + phase[0]) * math.sin(3 * v[1] + phase[1]) * math.sin(3 * v[2] + phase[2]) * 2
        z = v[2] * (flat if v[2] < 0 else 1.0)
        mesh.vertex(add(center, (v[0] * radii[0] * k, v[1] * radii[1] * k, z * radii[2] * k)))
    for f in faces:
        idx = [base + i for i in f]
        mesh.face(idx, sub(mesh.centroid(idx), center))


def _fit_z(meshes, height):
    hi = bounds([m for m in meshes if m.vertices])[1][2]
    k = height / hi
    for m in meshes:
        m.transform(lambda p: (p[0], p[1], p[2] * k))


# --- trees ----------------------------------------------------------------------------------------

SHAPES = {
    # crown centre height (share of the crown), vertical radius (share of the half crown height), how far the
    # clusters reach below the centre (-1 = to the bottom), limb spread
    "round": (0.55, 1.0, -0.75, 0.55),
    "dome": (0.52, 0.95, -0.35, 0.65),  # dense, low and wide, close to the ground (mangueira, oiti)
    "vase": (0.6, 1.0, -0.45, 0.75),  # open, rising limbs (ipê)
    "umbrella": (0.62, 0.75, -0.25, 0.85),  # wide and flat-topped (sibipiruna)
}


def tree(seed, height, crown, clear, trunk, *, shape="round", flowers=0.0, clusters=None, limbs=5):
    rnd = random.Random(seed * 13 + 1)
    out = {k: Mesh() for k in ("wood", "light", "shade", "bloom")}
    R = crown / 2
    Hc = height - clear
    zc_share, kz, reach_down, spread = SHAPES[shape]
    zc = clear + Hc * zc_share
    rz = Hc / 2 * kz
    # Trunk and limbs: the trunk rises to the fork, each limb curves out and up into the crown.
    fork = clear + Hc * 0.12
    tube(out["wood"], [(0, 0, 0), (0, 0, fork * 0.5), (0, 0, fork)], [trunk / 2 * 1.15, trunk / 2, trunk / 2 * 0.85], 7)
    tips = []
    for k in range(limbs):
        a = 2 * math.pi * k / limbs + rnd.uniform(-0.35, 0.35)
        d = (math.cos(a), math.sin(a), 0.0)
        r_end = R * spread * rnd.uniform(0.75, 1.0)
        z_end = zc + rz * rnd.uniform(0.0, 0.45)
        mid = add(mul(d, r_end * 0.45), (0, 0, fork + (z_end - fork) * 0.55))
        end = add(mul(d, r_end), (0, 0, z_end))
        r0 = trunk / 2 * 0.6
        tube(out["wood"], [(0, 0, fork - 0.05), mid, end], [r0, r0 * 0.6, r0 * 0.25], 5)
        tips.append(end)
        # Two branchlets off each limb.
        for s in (-1, 1):
            b0 = add(mid, mul(sub(end, mid), 0.35))
            side = unit(add(d, mul(cross(UP, d), s * 1.2)))
            b1 = add(b0, add(mul(side, R * 0.35), (0, 0, rz * 0.25)))
            tube(out["wood"], [b0, b1], [r0 * 0.3, r0 * 0.12], 4)
            tips.append(b1)
    # Leaf clusters over the envelope (a Fibonacci spiral on the ellipsoid), with gaps, plus a few on the limb tips.
    n = clusters or max(18, min(34, round(12 + R * 2.6)))
    rc = R * 0.42 * (22 / n) ** 0.5
    pts = []
    for i in range(n):
        zz = 1 - 2 * (i + 0.5) / n
        if zz < reach_down:
            continue
        rr = math.sqrt(1 - zz * zz)
        a = GOLDEN * i
        pts.append((math.cos(a) * rr * R * 0.78, math.sin(a) * rr * R * 0.78, zc + zz * rz * 0.8))
    pts += [add(t, (0, 0, rc * 0.2)) for t in tips[::2]]
    n_bloom = round(len(pts) * flowers)
    order = list(range(len(pts)))
    rnd.shuffle(order)
    blooming = set(order[:n_bloom])
    for i, p in enumerate(pts):
        r = rc * rnd.uniform(0.8, 1.15)
        high = (p[2] - zc) / rz
        target = out["bloom"] if i in blooming else out["light"] if high > -0.15 else out["shade"]
        cluster(target, p, (r, r, r * 0.8), rnd, jitter=0.16, lumps=0.05)
    # A core in shade so that the crown is never see-through.
    cluster(out["shade"], (0, 0, zc), (R * 0.55, R * 0.55, rz * 0.5), rnd, jitter=0.12)
    lo, hi = bounds([out[k] for k in ("light", "shade", "bloom") if out[k].vertices])
    kxy = crown / max(hi[0] - lo[0], hi[1] - lo[1])
    kzz = height / hi[2]
    for m in out.values():
        m.transform(lambda p: (p[0] * kxy, p[1] * kxy, p[2] * kzz))
    return out


# --- conifers --------------------------------------------------------------------------------------

def pine(seed, height, crown, clear, trunk, *, whorls=11, arms=5):
    """Whorls of flattened, drooping pads on a tapering trunk, narrowing to a pointed top."""
    rnd = random.Random(seed * 13 + 2)
    out = {k: Mesh() for k in ("wood", "light", "shade")}
    R = crown / 2
    tube(out["wood"], [(0, 0, 0), (0, 0, height * 0.6), (0, 0, height * 0.96)], [trunk / 2, trunk * 0.3, 0.03], 7)
    for w in range(whorls):
        t = w / (whorls - 1)
        z = clear + (height - clear) * 0.88 * t
        reach = R * (1 - 0.85 * t) + 0.2
        spin = rnd.uniform(0, 2 * math.pi)
        n = arms if t < 0.8 else 3
        for j in range(n):
            a = spin + 2 * math.pi * j / n
            d = (math.cos(a), math.sin(a), 0.0)
            end = add(mul(d, reach), (0, 0, z - reach * 0.12))
            tube(out["wood"], [(0, 0, z), end], [max(0.02, trunk * 0.15 * (1 - t)), 0.01], 4)
            c = add(mul(d, reach * 0.6), (0, 0, z - reach * 0.06))
            pad = (reach * 0.62, reach * 0.62, max(0.2, reach * 0.24))
            # Pads point along their branch: stretch them radially.
            target = out["light"] if w % 2 else out["shade"]
            m = Mesh()
            cluster(m, (0, 0, 0), (pad[0], pad[1] * 0.6, pad[2]), rnd, jitter=0.2, flat=0.5)
            ca, sa = math.cos(a), math.sin(a)
            base = len(target.vertices)
            target.vertices += [add(c, (x * ca - y * sa, x * sa + y * ca, zz)) for x, y, zz in m.vertices]
            target.faces += [[i + base for i in f] for f in m.faces]
    cluster(out["light"], (0, 0, height * 0.93), (0.25, 0.25, height * 0.07), rnd, jitter=0.1, flat=1.0)
    _fit_z(list(out.values()), height)
    return out


def column(seed, height, crown, clear, trunk, *, clusters=22):
    """A columnar conifer: clusters on a spindle-shaped envelope, two tones, a dense core."""
    rnd = random.Random(seed * 13 + 3)
    out = {k: Mesh() for k in ("wood", "light", "shade")}
    R = crown / 2
    tube(out["wood"], [(0, 0, 0), (0, 0, clear + 0.3)], [trunk / 2, trunk * 0.4], 6)

    def radius(z):
        t = (z - clear) / (height - clear)
        return R * max(0.12, math.sin(math.pi * min(1.0, 0.15 + t * 0.92)) ** 0.75 * (1 - 0.4 * t))

    core_n = 6
    for i in range(core_n):
        t = (i + 0.5) / core_n
        z = clear + (height - clear) * t
        r = radius(z) * 0.75
        cluster(out["shade"], (0, 0, z), (r, r, (height - clear) / core_n * 0.8), rnd, jitter=0.1)
    for i in range(clusters):
        t = (i + 0.5) / clusters
        z = clear + (height - clear) * (0.06 + 0.9 * t)
        a = GOLDEN * i * 2
        r = radius(z)
        p = (math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, z)
        rr = r * 0.55
        cluster(out["light"] if i % 3 else out["shade"], p, (rr, rr, rr * 1.4), rnd, jitter=0.15)
    _fit_z(list(out.values()), height)
    return out


# --- palms --------------------------------------------------------------------------------------------

def palm(seed, height, crown, stem, *, fronds=16, droop=0.7, lean=0.0, shaft=False, rise=(60, -10), fan=False, frond_w=0.2):
    """A palm: a tapering stem with a flared base, pinnate fronds with a serrated edge or fan leaves with a notched rim."""
    rnd = random.Random(seed * 13 + 4)
    out = {k: Mesh() for k in ("wood", "light", "shade", "green")}
    R = crown / 2
    L = R * 1.08
    h = height - L * 0.3
    ts = [i / 8 for i in range(9)]
    path = [(lean * h * t ** 1.6, 0.0, h * t) for t in ts]
    tube(out["wood"], path, [stem / 2 * (1.0 + 0.35 * (1 - t) ** 5 + 0.1 * (1 - t)) for t in ts], 9)
    top = path[-1]
    if shaft:
        tube(out["green"], [add(top, (0, 0, -0.05)), add(top, (0, 0, h * 0.1))], [stem / 2 * 1.1, stem / 2 * 0.92], 9)
        top = add(top, (0, 0, h * 0.1))
    for k in range(fronds):
        az = 2 * math.pi * k / fronds * 2.0 + rnd.uniform(-0.15, 0.15)
        frac = k / max(fronds - 1, 1)
        el = math.radians(rise[0] + (rise[1] - rise[0]) * (rnd.random() * 0.4 + frac * 0.6))
        d = (math.cos(az), math.sin(az), 0.0)
        side = (-math.sin(az), math.cos(az), 0.0)
        Lk = L * rnd.uniform(0.88, 1.05)
        target = out["light"] if frac < 0.6 else out["shade"]
        if fan:
            # Petiole, then a fan: a solid from the hastula to a notched rim, slightly cupped.
            c = add(top, mul(add(mul(d, math.cos(el)), mul(UP, math.sin(el))), Lk * 0.4))
            tube(out["green"], [top, c], [0.035, 0.02], 4)
            tg = unit(add(mul(d, math.cos(el)), mul(UP, math.sin(el) - 0.3)))
            nrm = unit(cross(side, tg))
            nrm = nrm if nrm[2] >= 0 else mul(nrm, -1)
            m = 14

            def rim(rad, notch):
                up_, dn = [], []
                for j in range(m + 1):
                    a = math.radians(-100 + 200 * j / m)
                    rr = rad * (1 - notch if j % 2 else 1)
                    dirv = add(mul(tg, math.cos(a)), mul(side, math.sin(a)))
                    sag = -0.35 * rad * abs(math.sin(a)) ** 2 - 0.15 * rad
                    p = add(add(c, mul(dirv, rr)), mul(nrm, sag * (rr / rad)))
                    up_.append(add(p, mul(nrm, 0.01)))
                    dn.append(add(p, mul(nrm, -0.01)))
                return up_ + dn[::-1]

            loft(target, [rim(Lk * 0.08, 0.0), rim(Lk * 0.35, 0.05), rim(Lk * 0.6, 0.28)])
            continue
        sections = []
        steps = 14
        for i in range(steps + 1):
            t = i / steps
            s = add(top, mul(add(mul(d, math.cos(el) * t), mul(UP, math.sin(el) * t - droop * t * t)), Lk))
            if i == steps:
                sections.append([s])
                continue
            tang = unit(add(mul(d, math.cos(el)), mul(UP, math.sin(el) - 2 * droop * t)))
            nrm = unit(cross(side, tang))
            nrm = nrm if nrm[2] >= 0 else mul(nrm, -1)
            w = Lk * frond_w * (0.2 + 0.8 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.6)
            if i % 2:  # the notches between leaflets
                w *= 0.55
            th = max(0.012, w * 0.06)
            fold = w * 0.4
            sections.append([add(s, mul(nrm, th)), add(add(s, mul(side, w)), mul(nrm, -fold)), add(s, mul(nrm, -th)),
                             add(add(s, mul(side, -w)), mul(nrm, -fold))])
        loft(target, sections)
    lo, hi = bounds([out["light"], out["shade"]])
    k = crown / max(hi[0] - lo[0], hi[1] - lo[1])
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    for key in ("light", "shade", "green"):
        if key == "green" and not fan:
            continue
        out[key].transform(lambda p: (top[0] + (p[0] - cx) * k, top[1] + (p[1] - cy) * k, top[2] + (p[2] - top[2]) * k))
    _fit_z([m for m in out.values() if m.vertices], height)
    return out


# --- shrubs -----------------------------------------------------------------------------------------

def shrub(seed, height, width, *, z0=0.0, clusters=12, flowers=0, topiary=False, stems=0):
    """A shrub: clusters on a dome, a shaded core, a few flowers; a clipped ball for topiary."""
    rnd = random.Random(seed * 13 + 5)
    out = {k: Mesh() for k in ("wood", "light", "shade", "bloom")}
    R, H = width / 2, height
    c = (0.0, 0.0, z0 + H * 0.5)
    if topiary:
        cluster(out["light"], c, (R, R, H / 2), rnd, jitter=0.04, level=2, flat=0.9, lumps=0.03)
        return out
    cluster(out["shade"], add(c, (0, 0, -H * 0.05)), (R * 0.7, R * 0.7, H * 0.4), rnd, jitter=0.12, flat=0.7)
    for k in range(stems):
        a = 2 * math.pi * k / max(stems, 1)
        tube(out["wood"], [(0, 0, z0), (math.cos(a) * R * 0.3, math.sin(a) * R * 0.3, z0 + H * 0.35)], [0.015, 0.008], 4)
    for i in range(clusters):
        zz = 1 - 1.6 * (i + 0.5) / clusters  # from the top to a bit below the middle
        rr = math.sqrt(max(0.0, 1 - zz * zz))
        a = GOLDEN * i
        p = (c[0] + math.cos(a) * rr * R * 0.72, c[1] + math.sin(a) * rr * R * 0.72, c[2] + zz * H * 0.36)
        r = R * 0.42 * (12 / clusters) ** 0.5 * rnd.uniform(0.85, 1.15)
        cluster(out["light"] if zz > -0.2 else out["shade"], p, (r, r, r * 0.85), rnd, jitter=0.16)
    for i in range(flowers):
        zz = rnd.uniform(-0.1, 0.95)
        a = rnd.uniform(0, 2 * math.pi)
        rr = math.sqrt(max(0.0, 1 - zz * zz))
        p = (math.cos(a) * rr * R * 1.0, math.sin(a) * rr * R * 1.0, c[2] + zz * H * 0.48)
        r = max(0.02, R * 0.09)
        cluster(out["bloom"], p, (r, r, r * 0.6), rnd, jitter=0.1, level=0)
    lo, hi = bounds([out[k] for k in ("light", "shade") if out[k].vertices])
    kxy = width / max(hi[0] - lo[0], hi[1] - lo[1])
    base = min(lo[2], z0 + 0.02 * H)  # the lowest cluster rests on z0
    kz = H / (hi[2] - base)
    for m in out.values():
        m.transform(lambda p: (p[0] * kxy, p[1] * kxy, z0 + max(0.0, p[2] - base) * kz))
    return out
