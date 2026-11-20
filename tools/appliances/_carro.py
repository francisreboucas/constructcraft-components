"""Shared builder of the passenger cars (carro_hatch, carro_sedan, carro_suv, caminhonete).

The body is not drawn piece by piece: it is lofted, as a mesh, from two side profiles
(y, z) carried across the width (x):

* the lower body: bumpers, hood, sills, the wheel arches, the trunk or the tailgate;
* the cabin (greenhouse): from the beltline up, over the windshield, the roof and the rear glass.

Across the width each profile is flat in the middle and rounds off near the sides: a
point at the distance e from the side moves inwards, along the profile's normal, by
r(1 - cos t) where sin t = 1 - e/r, so the body's edges are quarter circles of radius r
seen from the front, and its ends are pulled back a little more (round corners seen from
above). The cabin rounds only where its profile faces up (the roof's edges), leans in
towards the roof (tumblehome) and sits on the beltline.

The glass, the lamps, the grille and the plates are thin shells that follow these
surfaces (`Loft.patch`) or prisms on the flat sides (`side_prism`); the wheels are lathed
meshes; the interior is a few boxes and the steering wheel.

Frame (CONTRIBUTING.md): meters, the wheels on the ground (z = 0), the front towards -Y,
the origin in the middle of the wheelbase; +X is the driver's side (the left of a car
facing -Y: Brazilian cars are left-hand drive).
"""

from __future__ import annotations

import math

from kit import ALL, COARSE, FINE, FULL, Component
from _moto import base as mb
from _moto.base import Mesh, v_add, v_cross, v_dot, v_mul, v_norm, v_sub

# --- materials -----------------------------------------------------------------------------

GLASS = "Vidro automotivo"
TYRE = "Borracha"
RIM = "Alumínio polido"
DISC = "Disco de freio"
BLACK = "Plástico preto"
CHROME = "Cromado"
LENS_CLEAR = "Lente cristal"
LENS_RED = "Lente vermelha"
LENS_AMBER = "Lente âmbar"
TRIM = "Revestimento interno automotivo"
PLATE = "Placa refletiva branca"
STEEL_BLACK = "Aço pintado preto"

# The same definitions as the motorcycle's (tools/appliances/_moto/base.py): one name, one material.
SHARED = {
    RIM: ((214, 217, 221), "Metal", "Polished", 0),
    DISC: ((150, 152, 156), "Metal", "Satin", 0),
    LENS_CLEAR: ((238, 244, 248), "Glass", "Polished", 0.92),
    LENS_RED: ((196, 24, 28), "Glass", "Glossy", 0.25),
    LENS_AMBER: ((236, 138, 32), "Glass", "Glossy", 0.25),
    "Pintura preta automotiva": ((14, 14, 16), "Metal", "Glossy", 0),
}
NEW = {
    GLASS: ((22, 28, 34), "Glass", "Polished", 0.15),
    TRIM: ((44, 44, 48), "Plastic", "Matte", 0),
    PLATE: ((240, 242, 244), "Plastic", "Satin", 0),
    "Pintura prata metálica": ((178, 182, 188), "Metal", "Glossy", 0),
    "Pintura branca automotiva": ((236, 237, 236), "Metal", "Glossy", 0),
    "Pintura azul metálica": ((28, 62, 112), "Metal", "Glossy", 0),
    "Pintura vermelha automotiva": ((168, 18, 24), "Metal", "Glossy", 0),
    "Pintura grafite metálica": ((72, 76, 82), "Metal", "Glossy", 0),
}


def declare_materials(c: Component, paint: str):
    for name, (color, cls, finish, tr) in {**SHARED, **NEW}.items():
        if name == paint or not name.startswith("Pintura"):
            c.material(name, color, cls, finish, tr)


# --- 2D helpers ------------------------------------------------------------------------------

def smooth(points, per=5):
    """A dense polyline (y, z) through the points, rounded (Catmull-Rom), ends kept."""
    return [(q[0], q[1]) for q in mb.catmull([(y, z, 0.0) for y, z in points], per)]


def area2(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))) / 2


def normals2(poly):
    """Outward unit normals of a closed polygon (any orientation)."""
    s = 1.0 if area2(poly) > 0 else -1.0
    n = len(poly)
    out = []
    for i in range(n):
        a, b = poly[i - 1], poly[(i + 1) % n]
        tu, tv = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tu, tv) or 1.0
        out.append((s * tv / ln, -s * tu / ln))
    return out


def offset2(poly, d):
    """The polygon moved inwards by d along its normals (good for small d)."""
    return [(p[0] - d * nn[0], p[1] - d * nn[1]) for p, nn in zip(poly, normals2(poly))]


def clip2(poly, a, b, c):
    """The part of the polygon where a*u + b*v <= c (Sutherland-Hodgman)."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= 0:
            out.append(p)
        if (fp <= 0) != (fq <= 0):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def span_at(poly, u):
    """The lowest and highest v where the vertical line at u crosses the polygon."""
    vs = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        if (p[0] - u) * (q[0] - u) <= 0 and p[0] != q[0]:
            t = (u - p[0]) / (q[0] - p[0])
            vs.append(p[1] + (q[1] - p[1]) * t)
    return (min(vs), max(vs)) if vs else (0.0, 0.0)


def triangulate(poly):
    """Ear clipping: triangles (index triples) of a simple polygon."""
    n = len(poly)
    idx = list(range(n))
    if area2(poly) < 0:
        idx.reverse()

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def inside(p, a, b, c):
        return cross(a, b, p) > 1e-12 and cross(b, c, p) > 1e-12 and cross(c, a, p) > 1e-12

    tris = []
    guard = 0
    while len(idx) > 3 and guard < 10 * n:
        guard += 1
        m = len(idx)
        for k in range(m):
            a, b, c = idx[k - 1], idx[k], idx[(k + 1) % m]
            cr = cross(poly[a], poly[b], poly[c])
            if abs(cr) <= 1e-12:  # collinear or repeated: drop the point
                idx.pop(k)
                break
            if cr < 0:
                continue
            if any(inside(poly[j], poly[a], poly[b], poly[c]) for j in idx if j not in (a, b, c)):
                continue
            tris.append((a, b, c))
            idx.pop(k)
            break
        else:  # degenerate leftovers: a fan
            for k in range(1, len(idx) - 1):
                tris.append((idx[0], idx[k], idx[k + 1]))
            return tris
    if len(idx) == 3:
        tris.append(tuple(idx))
    return tris


def curvature_limits(poly, k=0.6, window=4):
    """How far each point of a closed polygon may move inwards before the sides fold: k times the
    radius of its convex corner (the circle through it and its neighbours); no limit elsewhere."""
    n = len(poly)
    ccw = area2(poly) > 0
    out = []
    for i in range(n):
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % n]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        convex = (cr > 0) == ccw and abs(cr) > 1e-12
        if not convex:
            out.append(1e9)
            continue
        la, lb, lc = math.dist(a, b), math.dist(b, c), math.dist(a, c)
        out.append(k * la * lb * lc / (2 * abs(cr)))
    # a corner's neighbours share its limit, so the points around it stay in order
    return [min(out[(i + j) % n] for j in range(-window, window + 1)) for i in range(n)]


def smoothstep(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


# --- lofts and shells ------------------------------------------------------------------------------

class Loft:
    """A side profile carried across the width, its edges rounded (see the module's doc)."""

    def __init__(self, prof, half, r, weight=None, retract=None, tumble=None, rounds=8):
        self.P = prof
        self.N = normals2(prof)
        self.half, self.r = half, r
        self.w = [weight(nn) if weight else 1.0 for nn in self.N]
        self.lim = curvature_limits(prof)
        self.retract, self.tumble = retract, tumble
        self.rounds = rounds
        cy = sum(p[0] for p in prof) / len(prof)
        cz = sum(p[1] for p in prof) / len(prof)
        self.center = (0.0, cy, cz)

    def _sin(self, x):
        e = abs(x) - (self.half - self.r)
        return 0.0 if e <= 0 else min(1.0, e / self.r)

    def point(self, x, i):
        i %= len(self.P)
        s = self._sin(x)
        d = min(self.r * (1 - math.sqrt(max(0.0, 1 - s * s))) * self.w[i], self.lim[i])
        y, z = self.P[i][0] - d * self.N[i][0], self.P[i][1] - d * self.N[i][1]
        if self.retract:
            y += self.retract(y, s)
        if self.tumble:
            x = self.tumble(x, z)
        return (x, y, z)

    def stations(self):
        xi = self.half - self.r
        ring = [xi + self.r * math.sin(math.pi / 2 * k / self.rounds) for k in range(self.rounds + 1)]
        return [-q for q in reversed(ring)] + [0.0] + ring

    def cap(self, x):
        return [(self.point(x, i)[1], self.point(x, i)[2]) for i in range(len(self.P))]

    def mesh(self) -> Mesh:
        m = Mesh()
        n = len(self.P)
        rows = [[m.vtx(self.point(x, i)) for i in range(n)] for x in self.stations()]
        mb._rows_faces(m, rows, False, True)
        for row, x in ((rows[0], -self.half), (rows[-1], self.half)):
            for a, b, c in triangulate(self.cap(x)):
                m.poly([row[a], row[b], row[c]] if x > 0 else [row[a], row[c], row[b]])
        m.orient(0)
        return m

    def normal(self, x, i):
        h = 1e-3
        du = v_sub(self.point(x + h, i), self.point(x - h, i))
        dv = v_sub(self.point(x, i + 1), self.point(x, i - 1))
        nn = v_norm(v_cross(du, dv))
        p = self.point(x, i)
        if v_dot(nn, v_sub(p, self.center)) < 0:
            nn = v_mul(nn, -1)
        return nn

    def patch(self, x0, x1, i0, i1, off=0.0008, th=0.003, nx=12) -> Mesh:
        """A shell over the surface between x0..x1 and the profile points i0..i1."""
        xs = [x0 + (x1 - x0) * k / (nx - 1) for k in range(nx)]
        top, bot = [], []
        for x in xs:
            rt, rb = [], []
            for i in range(i0, i1 + 1):
                p, nn = self.point(x, i), self.normal(x, i)
                rt.append(v_add(p, v_mul(nn, off + th)))
                rb.append(v_add(p, v_mul(nn, off)))
            top.append(rt)
            bot.append(rb)
        return slab(top, bot)

    def indices(self, cond, start=0, end=None):
        """The first and last profile point (from start to end) for which cond(point, normal) holds."""
        end = len(self.P) if end is None else end
        hits = [i for i in range(start, end) if cond(self.P[i], self.N[i])]
        return (min(hits), max(hits)) if hits else None


def slab(top, bot) -> Mesh:
    """A closed shell between two grids of the same shape (rows x cols)."""
    m = Mesh()
    T = [[m.vtx(p) for p in row] for row in top]
    B = [[m.vtx(p) for p in row] for row in bot]
    nr, nc = len(T), len(T[0])
    for a in range(nr - 1):
        for b in range(nc - 1):
            m.poly([T[a][b], T[a + 1][b], T[a + 1][b + 1], T[a][b + 1]])
            m.poly([B[a][b], B[a][b + 1], B[a + 1][b + 1], B[a + 1][b]])
    edge = [(a, 0) for a in range(nr)] + [(nr - 1, b) for b in range(1, nc)] + \
           [(a, nc - 1) for a in range(nr - 2, -1, -1)] + [(0, b) for b in range(nc - 2, 0, -1)]
    for k in range(len(edge)):
        (a1, b1), (a2, b2) = edge[k], edge[(k + 1) % len(edge)]
        m.poly([T[a1][b1], T[a2][b2], B[a2][b2], B[a1][b1]])
    m.orient(0)
    return m


def side_prism(poly, x0, x1, tumble=None) -> Mesh:
    """A polygon (y, z) on a side plane, extruded across from x0 to x1 (tumble(x, z) leans it)."""
    m = Mesh()
    f = tumble or (lambda x, z: x)
    A = [m.vtx((f(x0, z), y, z)) for y, z in poly]
    B = [m.vtx((f(x1, z), y, z)) for y, z in poly]
    for a, b, c in triangulate(poly):
        m.poly([A[a], A[c], A[b]])
        m.poly([B[a], B[b], B[c]])
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        m.poly([A[i], A[j], B[j], B[i]])
    m.orient(0)
    return m


def shapes_mesh(*shapes) -> Mesh:
    m = Mesh()
    for s in shapes:
        s.mesh_into(m)
    return m


def mirrored(m: Mesh) -> Mesh:
    out = Mesh()
    out.v = [(-x, y, z) for x, y, z in m.v]
    out.f = [list(reversed(fc)) for fc in m.f]
    return out


# --- the car -----------------------------------------------------------------------------------

class Car:
    """The numbers of one car (meters). See carro_hatch.py for an annotated example."""

    def __init__(self, **k):
        self.__dict__.update(k)
        self.yF = -self.WB / 2 - self.OF
        self.yR = self.WB / 2 + self.OR
        self.ra = self.RT + 0.045


def lower_profile(s: Car):
    """The lower body's side profile, counter-clockwise: the bottom from the front, then the top from the back."""
    gc, ra, RT = s.gc, s.ra, s.RT
    yAf, yAr = -s.WB / 2, s.WB / 2

    def arch(yc, zj1, zj2, n=26):
        a0 = math.pi + math.asin((RT - zj1) / ra)
        a1 = -math.asin((RT - zj2) / ra)
        return [(yc + ra * math.cos(a0 + (a1 - a0) * k / n), RT + ra * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]

    fa = arch(yAf, s.gc_front, gc)
    rr = arch(yAr, gc, s.gc_rear)
    sf = fa[0][0] - s.yF  # the front overhang ahead of the arch
    front = smooth([(s.yF + 0.02, s.z_front_bottom + 0.14), (s.yF + 0.1 * sf, s.z_front_bottom + 0.02),
                    (s.yF + 0.45 * sf, s.z_front_bottom - 0.02), (s.yF + 0.8 * sf, s.gc_front + 0.01), fa[0]], 4)[:-1]
    sill = [(fa[-1][0] + (rr[0][0] - fa[-1][0]) * k / 8, gc) for k in range(1, 8)]
    sr = s.yR - rr[-1][0]  # behind the rear arch
    rear = smooth([rr[-1], (rr[-1][0] + 0.25 * sr, s.gc_rear + 0.02), (rr[-1][0] + 0.6 * sr, s.z_rear_bottom - 0.01),
                   (s.yR - 0.12 * sr, s.z_rear_bottom + 0.03), (s.yR - 0.01, s.z_rear_bottom + 0.16)], 4)[1:]
    bottom = front + fa + sill + rr + rear
    top = smooth(s.top, 6)
    # the arches and the sill keep sharp edges: rounding them would fold the sides
    sharp = [False] * len(front) + [True] * (len(fa) + len(sill) + len(rr)) + [False] * (len(rear) + len(top))
    return bottom + top, len(bottom), sharp


def cabin_profile(s: Car):
    """The cabin's side profile: the belt (below the beltline, hidden in the body) and the glass line over it."""
    z0 = s.z_belt - 0.04
    upper = smooth(s.glass, 6)  # from the rear glass' foot over the roof to the windshield's foot
    y_r, y_f = upper[0][0], upper[-1][0]
    belt = [(y_f + (y_r - y_f) * k / 10, z0) for k in range(11)]
    return belt + upper[1:-1], len(belt)


def build_car(c: Component, s: Car):
    paint = s.paint
    declare_materials(c, paint)
    W, half = s.W, s.W / 2
    yAf, yAr = -s.WB / 2, s.WB / 2

    # --- lower body ---------------------------------------------------------------------------------
    prof, top0, sharp = lower_profile(s)

    def retract(y, sn):
        wf = smoothstep((yAf - s.ra - y) / (0.9 * (s.OF - s.ra)))
        wr = smoothstep((y - yAr - s.ra) / (0.9 * (s.OR - s.ra)))
        return (s.round_front * wf - s.round_rear * wr) * sn * sn

    # The bottom and the wheel arches keep sharp edges (rounding them would fold the sides).
    body = Loft(prof, half, 0.11, weight=lambda nn: smoothstep((nn[1] + 0.45) / 0.55), retract=retract)
    body.w = [0.0 if sh else w for sh, w in zip(sharp, body.w)]
    c._add("Carroceria", body.mesh().shape(), paint, ALL, True, False)

    # --- cabin ---------------------------------------------------------------------------------------
    cprof, belt_n = cabin_profile(s)
    zb, zr = s.z_belt, max(p[1] for p in cprof)
    hg = half - s.cabin_inset
    tk = s.tumble

    def tumble(x, z):
        return x * (1 - tk * min(1.0, max(0.0, (z - zb) / (zr - zb))))

    cab = Loft(cprof, hg, 0.16, weight=lambda nn: max(0.0, nn[1]) ** 0.8, tumble=tumble)
    cab.w = [w * smoothstep((p[1] - zb + 0.04) / 0.2) for w, p in zip(cab.w, cprof)]  # not down into the belt
    c._add("Cabine", cab.mesh().shape(), paint, ALL, True, False)

    # Windshield and rear glass: shells over the cabin's front and rear faces.
    ws = cab.indices(lambda p, nn: nn[0] < -0.35 and p[1] > zb + 0.03, belt_n)
    if ws:
        i0, i1 = ws
        c._add("Para-brisa", cab.patch(-(hg - 0.075), hg - 0.075, i0 + 1, i1 - 1, nx=16).shape(), GLASS, FULL, False, False)
    rg = cab.indices(lambda p, nn: nn[0] > 0.35 and p[1] > zb + 0.05 and p[1] < zr - 0.04, belt_n)
    if rg:
        i0, i1 = rg
        c._add("Vidro traseiro", cab.patch(-(hg - 0.1), hg - 0.1, i0 + 1, i1, nx=12).shape(), GLASS, FULL, False, False)

    # Side windows: the cabin's flat side, less the pillars, split at the B pillar.
    capg = cab.cap(hg)
    glass = offset2(capg, 0.045)
    glass = clip2(glass, 0, -1, -(zb + 0.025))  # z >= zb + 0.025
    if s.y_glass_rear is not None:
        glass = clip2(glass, 1, 0, s.y_glass_rear)
    if getattr(s, "y_glass_front", None) is not None:
        glass = clip2(glass, -1, 0, -s.y_glass_front)
    parts = []
    for name, (a, cc) in (("dianteira", (1, s.yB - 0.04)), ("traseira", (-1, -(s.yB + 0.04)))):
        g = clip2(glass, a, 0, cc)
        if len(g) >= 3 and abs(area2(g)) > 0.01:
            parts.append((name, g))
    for side, sg in (("esquerda", 1), ("direita", -1)):
        for name, g in parts:
            m = side_prism(g, hg + 0.0004, hg + 0.0034, tumble)
            c._add(f"Janela {name} {side}", (m if sg > 0 else mirrored(m)).shape(), GLASS, FULL, False, False)
        lo, hi = span_at(glass, s.yB)
        if hi > lo:
            pillar = [(s.yB - 0.04, lo), (s.yB + 0.04, lo), (s.yB + 0.04, hi), (s.yB - 0.04, hi)]
            m = side_prism(pillar, hg + 0.0002, hg + 0.0032, tumble)
            c._add(f"Coluna B {side}", (m if sg > 0 else mirrored(m)).shape(), BLACK, FULL, False, False)

    # --- lamps, grille, plates: shells on the lower body's ends ----------------------------------------
    def face(front, z0, z1):
        sgn = -1 if front else 1
        return body.indices(lambda p, nn: sgn * nn[0] > 0.45 and z0 <= p[1] <= z1, top0)

    def shell(name, rng, x0, x1, mat, detail=FULL, both=True, th=0.004):
        if not rng:
            return
        i0, i1 = rng
        if i1 - i0 < 1:
            i0, i1 = i0 - 1, i1 + 1
        if both:
            c._add(f"{name} esquerda", body.patch(x0, x1, i0, i1, th=th).shape(), mat, detail, False, False)
            c._add(f"{name} direita", body.patch(-x1, -x0, i0, i1, th=th).shape(), mat, detail, False, False)
        else:
            c._add(name, body.patch(x0, x1, i0, i1, th=th).shape(), mat, detail, False, False)

    hz = s.head_z
    shell("Farol", face(True, *hz), half - s.head_w, half - 0.04, LENS_CLEAR, th=0.006)
    shell("Refletor do farol", face(True, *hz), half - s.head_w + 0.02, half - 0.06, CHROME, th=0.002)
    shell("Pisca dianteiro", face(True, hz[0] - 0.05, hz[0] - 0.02), half - 0.2, half - 0.06, LENS_AMBER)
    gz = s.grille_z
    shell("Grade", face(True, *gz), -s.grille_w, s.grille_w, BLACK, both=False, th=0.006)
    shell("Entrada de ar inferior", face(True, s.z_front_bottom + 0.04, s.z_front_bottom + 0.11), -(half - 0.25), half - 0.25, BLACK, both=False)
    shell("Placa dianteira", face(True, *s.plate_front_z), -0.2, 0.2, PLATE, FINE, both=False, th=0.008)
    tz = s.tail_z
    shell("Lanterna", face(False, *tz), half - s.tail_w, half - 0.03, LENS_RED, th=0.006)
    shell("Placa traseira", face(False, *s.plate_rear_z), -0.2, 0.2, PLATE, FINE, both=False, th=0.008)
    shell("Para-choque traseiro - friso", face(False, s.z_rear_bottom + 0.06, s.z_rear_bottom + 0.1), -(half - 0.15), half - 0.15, BLACK, FINE, both=False)

    # --- the body's sides: door gaps, handles, mirrors -------------------------------------------------
    capb = body.cap(half)
    for side, sg in (("esquerdo", 1), ("direito", -1)):
        for k, y in enumerate(s.door_gaps):
            lo, hi = span_at(capb, y)
            if hi > lo:
                gap = [(y - 0.0025, lo + 0.05), (y + 0.0025, lo + 0.05), (y + 0.0025, min(hi, zb) - 0.01), (y - 0.0025, min(hi, zb) - 0.01)]
                m = side_prism(gap, half - 0.001, half + 0.0008)
                c._add(f"Junta da porta {k + 1} {side}", (m if sg > 0 else mirrored(m)).shape(), BLACK, FINE, False, False)
        for k, y in enumerate(s.handles):
            h = [(y - 0.075, zb - 0.135), (y + 0.075, zb - 0.135), (y + 0.075, zb - 0.105), (y - 0.075, zb - 0.105)]
            m = side_prism(h, half - 0.002, half + 0.012)
            c._add(f"Maçaneta {k + 1} {side}", (m if sg > 0 else mirrored(m)).shape(), BLACK, FINE, False, False)
        ym, zm = s.y_mirror, zb + 0.04
        xo = half + 0.1  # the housing's outer end (the width over the mirrors: W + 0.2)
        mirror = shapes_mesh(
            mb.box((xo - 0.085, ym + 0.05, zm + 0.065), (0.17, 0.1, 0.12)),
            mb.box(((hg + xo - 0.17) / 2, ym + 0.06, zm + 0.02), (xo - 0.17 - hg + 0.02, 0.05, 0.04)),
        )
        glass_m = shapes_mesh(mb.box((xo - 0.085, ym + 0.1015, zm + 0.065), (0.15, 0.003, 0.1)))
        c._add(f"Retrovisor {side}", (mirror if sg > 0 else mirrored(mirror)).shape(), paint, FULL, True, False)
        c._add(f"Espelho do retrovisor {side}", (glass_m if sg > 0 else mirrored(glass_m)).shape(), CHROME, FINE, False, False)

    # --- wheels ------------------------------------------------------------------------------------------
    xw = half - 0.035 - s.TW / 2
    for yname, y in (("dianteira", yAf), ("traseira", yAr)):
        # the arch's lining: the part of the arch's circle above the sill
        rl, zc = s.ra - 0.004, s.gc + 0.01
        a0 = math.asin((s.RT - zc) / rl)
        arc = [(y + rl * math.cos(math.pi + a0 - (math.pi + 2 * a0) * k / 24), s.RT + rl * math.sin(math.pi + a0 - (math.pi + 2 * a0) * k / 24))
               for k in range(25)]
        c.profile(f"Caixa de roda {yname}", "Side", arc, -(half - 0.26), W - 0.52, BLACK)
        for side, sg in (("esquerda", 1), ("direita", -1)):
            add_wheel(c, f"{yname} {side}", sg * xw, y, s, sg)

    # --- interior ---------------------------------------------------------------------------------------
    add_interior(c, s, hg)

    if getattr(s, "extras", None):
        s.extras(c, s, body, cab)


def add_wheel(c: Component, name: str, xc: float, y: float, s: Car, sg: int):
    RT, TW, rim = s.RT, s.TW, s.rim
    ax = (float(sg), 0.0, 0.0)
    o = (xc, y, RT)
    tyre = mb.lathe([(rim + 0.004, -TW / 2 + 0.012), (RT - 0.035, -TW / 2), (RT - 0.01, -TW / 2 + 0.014), (RT, -TW / 2 + 0.04),
                     (RT, TW / 2 - 0.04), (RT - 0.01, TW / 2 - 0.014), (RT - 0.035, TW / 2), (rim + 0.004, TW / 2 - 0.012)],
                    o, ax, n=48, closed=True)
    c._add(f"Pneu {name}", shapes_mesh(tyre).shape(), TYRE, FULL, True, False)
    hf = TW / 2 - 0.035  # the face of the spokes
    barrel = mb.lathe([(rim - 0.012, -TW / 2 + 0.01), (rim + 0.012, -TW / 2 + 0.01), (rim + 0.012, -TW / 2 + 0.02), (rim, -TW / 2 + 0.026),
                       (rim, TW / 2 - 0.026), (rim + 0.014, TW / 2 - 0.018), (rim + 0.014, TW / 2 - 0.006), (rim - 0.012, TW / 2 - 0.006)],
                      o, ax, n=48, closed=True)
    hub = mb.lathe([(0, hf - 0.012), (0.075, hf - 0.012), (0.075, hf + 0.01), (0.045, hf + 0.016), (0, hf + 0.016)], o, ax, n=32)
    parts = [barrel, hub]
    for k in range(5):
        a = 2 * math.pi * k / 5 + math.pi / 10
        e = (0.0, math.cos(a), math.sin(a))
        t = (0.0, -math.sin(a), math.cos(a))
        rm = (0.07 + rim - 0.006) / 2
        ctr = v_add(o, v_add(v_mul(ax, hf), v_mul(e, rm)))
        parts.append(mb.box(ctr, (rim - 0.076, 0.042, 0.022), (e, t, ax)))
    c._add(f"Roda {name}", shapes_mesh(*parts).shape(), RIM, FULL, False, False)
    nuts = [mb.lathe([(0, hf + 0.016), (0.009, hf + 0.016), (0.009, hf + 0.026), (0, hf + 0.026)],
                     v_add(o, (0.0, 0.045 * math.cos(2 * math.pi * k / 5), 0.045 * math.sin(2 * math.pi * k / 5))), ax, n=6)
            for k in range(5)]
    c._add(f"Parafusos {name}", shapes_mesh(*nuts).shape(), CHROME, FINE, False, False)
    disc = mb.lathe([(0.06, -0.035), (rim - 0.045, -0.035), (rim - 0.045, -0.013), (0.06, -0.013)], o, ax, n=40, closed=True)
    c._add(f"Disco de freio {name}", shapes_mesh(disc).shape(), DISC, FINE, False, False)
    cal = mb.box(v_add(o, (sg * -0.03, 0.06, rim - 0.06)), (0.05, 0.09, 0.05))
    c._add(f"Pinça de freio {name}", shapes_mesh(cal).shape(), STEEL_BLACK, FINE, False, False)
    c.cyl_x(f"Roda simplificada {name}", y, RT, xc - TW / 2, RT, TW, TYRE, detail=COARSE, in_plan=False)


def add_interior(c: Component, s: Car, hg: float):
    zf = s.z_floor
    m = Mesh()
    for k, x in enumerate((0.36, -0.36)):
        y0 = s.y_seat_front
        mb.box((x, y0, zf + 0.2), (0.5, 0.52, 0.12)).mesh_into(m)
        back = (0.0, math.sin(math.radians(14)), math.cos(math.radians(14)))
        mb.box(v_add((x, y0 + 0.27, zf + 0.26), v_mul(back, 0.32)), (0.5, 0.1, 0.62), ((1, 0, 0), v_cross(back, (1, 0, 0)), back)).mesh_into(m)
        mb.box(v_add((x, y0 + 0.27, zf + 0.26), v_mul(back, 0.7)), (0.26, 0.08, 0.16), ((1, 0, 0), v_cross(back, (1, 0, 0)), back)).mesh_into(m)
    if s.y_seat_rear is not None:
        y1 = s.y_seat_rear
        wr = 2 * hg - 0.2
        mb.box((0, y1, zf + 0.2), (wr, 0.5, 0.12)).mesh_into(m)
        back = (0.0, math.sin(math.radians(20)), math.cos(math.radians(20)))
        mb.box(v_add((0, y1 + 0.26, zf + 0.26), v_mul(back, 0.3)), (wr, 0.1, 0.58), ((1, 0, 0), v_cross(back, (1, 0, 0)), back)).mesh_into(m)
    yd = s.y_dash
    mb.box((0, yd, s.z_belt - 0.07), (2 * hg - 0.1, 0.36, 0.18)).mesh_into(m)
    c._add("Bancos e painel", m.shape(), TRIM, FINE, False, False)
    # The steering wheel, before the driver (+X), leaning back 25 degrees.
    ctr = (0.36, yd + 0.3, s.z_belt + 0.0)
    nrm = (0.0, math.cos(math.radians(25)), math.sin(math.radians(25)))
    e1 = (1.0, 0.0, 0.0)
    e2 = v_cross(nrm, e1)
    ringp = [v_add(ctr, v_add(v_mul(e1, 0.185 * math.cos(2 * math.pi * k / 32)), v_mul(e2, 0.185 * math.sin(2 * math.pi * k / 32)))) for k in range(32)]
    wheel = shapes_mesh(mb.tube(ringp, 0.016, n=10, closed=True), mb.cyl(v_sub(ctr, v_mul(nrm, 0.25)), ctr, 0.03),
                        mb.cyl(v_sub(ctr, v_mul(nrm, 0.02)), v_add(ctr, v_mul(nrm, 0.03)), 0.06))
    c._add("Volante", wheel.shape(), BLACK, FINE, False, False)
