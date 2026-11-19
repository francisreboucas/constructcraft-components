"""Engine and drivetrain of the Moto custom: air-cooled 1600 cm3 48-degree V-twin, primary case,
five-speed gearbox with the belt's front pulley, carburettor and round air cleaner, dual exhaust.

Generic design (no brand or real model). Frame of reference and hardpoints: base.py. The crank
axis runs along X at CRANK; each cylinder's axis lies in the plane x = 0 along CYL_FRONT /
CYL_REAR, so everything round about a cylinder axis is an engine Sweep of the Side plane (a short
straight path along the axis with a round or rounded-rectangle section): barrels, every fin, the
heads and the rocker boxes are exact and cost nothing in the file. Cases and covers are Side-plane
Profiles with Blend edges; the mufflers lie along Y (Plan-plane Revolutions). Only the parts
curved in 3D are numeric meshes (headers, heat shields, intake runners, oil lines, plug leads),
and the bolts, pulley teeth, clamps and plugs go to the moving-parts script (lua=True).

Layout (x: + rider's left): primary case and belt pulley on the left, cam cover, carburettor, air
cleaner and the two exhausts on the right; plugs, coil and horn on the left; oil filter at the
front under the front engine mount; oil lines run under the gearbox to the under-seat tank.
"""

from __future__ import annotations

import math

import kit
from _moto.base import (
    ALL, BLACK_PLASTIC, CAST_AL, CHROME, COARSE, DARK_METAL, ENGINE_BLACK, FINE, FULL, MEDIUM, POLISHED_AL, RUBBER,
    STAINLESS, STEEL_BLACK, Hardpoints, Mesh, _np, box, catmull, circle2, circles_hull, cyl, hexagon, lathe, ncircle,
    ncyl_side, ndisc_x, nhex_x, nprofile, nsweep, put, ring, rmf, sweep, v_add, v_cross, v_mul, v_norm, v_sub,
)

X = (1.0, 0.0, 0.0)
Y = (0.0, 1.0, 0.0)
Z = (0.0, 0.0, 1.0)
CERAMIC = "Louça"  # template material: spark plug insulators

FRONT, REAR = -1, 1


def add(c, hp: Hardpoints):
    eng = Engine(hp)
    crankcase(c, eng)
    cylinders(c, eng)
    valvetrain(c, eng)
    intake(c, eng)
    ignition(c, eng)
    primary(c, eng)
    gearbox(c, eng)
    oil(c, eng)
    exhaust(c, eng)
    coarse(c, eng)


# --- geometry helpers ---------------------------------------------------------------------------------------


class Engine:
    """The engine's own numbers (all from the hardpoints)."""

    def __init__(self, hp: Hardpoints):
        self.hp = hp
        self.cy, self.cz = hp.CRANK[1], hp.CRANK[2]
        a = math.radians(hp.V_ANGLE / 2)
        self.sa, self.ca = math.sin(a), math.cos(a)
        # along a cylinder axis (h from the crank): barrel, head, rocker box
        self.H_BASE, self.H_HEAD, self.H_ROCKER, self.H_TOP = 0.135, 0.265, 0.355, hp.CYL_LEN
        self.R_CORE = 0.056  # barrel wall (95.25 mm bore)
        self.R_FIN = 0.086  # barrel fins
        self.HEAD_A, self.HEAD_B, self.HEAD_D = 0.068, 0.092, -0.012  # head fins: half in-plane, half across, shift
        self.ROCK_A, self.ROCK_B, self.ROCK_D = 0.0875, 0.080, 0.0175  # rocker boxes cover the pushrods (V side)
        self.PUSH_X, self.PUSH_S, self.PUSH_R = -0.066, (0.068, 0.089), 0.0095
        self.H_PORT_EX, self.H_PORT_IN = 0.31, 0.33
        # intake / air cleaner centre (rider's right)
        self.AC = (-0.12, 0.61)
        self.CLUTCH = (0.075, 0.30)
        self.PULLEY = hp.FRONT_PULLEY

    def ax(self, cyl, h, s=0.0):
        """(y, z) of the point h along the cylinder axis, s across it towards the V (cyl FRONT or REAR)."""
        fy, fz = cyl * self.sa, self.ca
        py, pz = -cyl * self.ca, self.sa
        return (self.cy + fy * h + py * s, self.cz + fz * h + pz * s)

    def p3(self, cyl, h, s=0.0, x=0.0):
        y, z = self.ax(cyl, h, s)
        return (x, y, z)

    def dir(self, cyl):
        return (0.0, cyl * self.sa, self.ca)

    def vdir(self, cyl):
        """Unit vector across the axis towards the V."""
        return (0.0, -cyl * self.ca, self.sa)

    def fin_r(self, h):
        """Barrel fin radius: full above, trimmed at the base where the two cylinders close in."""
        return min(self.R_FIN, 0.445 * h - 0.006)


def area2(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def ccw(poly):
    return poly if area2(poly) > 0 else list(reversed(poly))


def fillet(pts, n=5):
    """A closed polygon [(u, v, r), ...] with each corner rounded by its radius r (arcs as n segments)."""
    out = []
    m = len(pts)
    for i in range(m):
        p = pts[i]
        r = p[2] if len(p) > 2 else 0.0
        if r <= 0:
            out.append((p[0], p[1]))
            continue
        a, b = pts[i - 1], pts[(i + 1) % m]
        d1 = (a[0] - p[0], a[1] - p[1])
        d2 = (b[0] - p[0], b[1] - p[1])
        l1, l2 = math.hypot(*d1), math.hypot(*d2)
        d1, d2 = (d1[0] / l1, d1[1] / l1), (d2[0] / l2, d2[1] / l2)
        cosang = max(-0.9999, min(0.9999, d1[0] * d2[0] + d1[1] * d2[1]))
        ang = math.acos(cosang)
        t = min(r / math.tan(ang / 2), 0.45 * l1, 0.45 * l2)
        r = t * math.tan(ang / 2)
        bis = (d1[0] + d2[0], d1[1] + d2[1])
        lb = math.hypot(*bis)
        bis = (bis[0] / lb, bis[1] / lb)
        dc = r / math.sin(ang / 2)
        cen = (p[0] + bis[0] * dc, p[1] + bis[1] * dc)
        pa = (p[0] + d1[0] * t, p[1] + d1[1] * t)
        pb = (p[0] + d2[0] * t, p[1] + d2[1] * t)
        a0 = math.atan2(pa[1] - cen[1], pa[0] - cen[0])
        a1 = math.atan2(pb[1] - cen[1], pb[0] - cen[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            t_ = a0 + da * k / n
            out.append((cen[0] + r * math.cos(t_), cen[1] + r * math.sin(t_)))
    return out


def inset(poly, d):
    """A counter-clockwise polygon moved inwards by d (outwards for d < 0), mitred corners."""
    m = len(poly)
    out = []
    for i in range(m):
        p, a, b = poly[i], poly[i - 1], poly[(i + 1) % m]
        e1 = (p[0] - a[0], p[1] - a[1])
        e2 = (b[0] - p[0], b[1] - p[1])
        l1, l2 = math.hypot(*e1) or 1e-9, math.hypot(*e2) or 1e-9
        n1 = (-e1[1] / l1, e1[0] / l1)
        n2 = (-e2[1] / l2, e2[0] / l2)
        nb = (n1[0] + n2[0], n1[1] + n2[1])
        lb = math.hypot(*nb)
        if lb < 1e-9:
            nb, k = n1, d
        else:
            nb = (nb[0] / lb, nb[1] / lb)
            k = d / max(0.35, nb[0] * n1[0] + nb[1] * n1[1])
        out.append((p[0] + nb[0] * k, p[1] + nb[1] * k))
    return out


def circ(cu, cv, r, n=48, phase=0.0):
    return [(cu + r * math.cos(2 * math.pi * i / n + phase), cv + r * math.sin(2 * math.pi * i / n + phase)) for i in range(n)]


def rrect_sec(a, b, r):
    """A rounded rectangle section (u half a, v half b) with exact corner arcs (engine points)."""
    r = min(r, a - 1e-4, b - 1e-4)
    return [(-a + r, -b), (a - r, -b, r), (a, -b + r), (a, b - r, r), (a - r, b), (-a + r, b, r), (-a, b - r), (-a, -b + r, r)]


def rrect_poly(u0, v0, u1, v1, r, n=4):
    return fillet([(u0, v0, r), (u1, v0, r), (u1, v1, r), (u0, v1, r)], n)


def nblend(c, name, plane, bottom, top, offset, depth, material, detail=FULL, in_plan=False):
    """An engine Blend: the `bottom` outline at `offset` lofted to the `top` outline `depth` farther along the normal."""
    assert len(bottom) == len(top), name
    shape = {"Blend": {"plane": plane, "bottom": _np(bottom), "top": _np(top), "offset": kit.e(offset), "depth": kit.e(depth)}}
    c._add(name, shape, material, detail, in_plan, False)


def nrev_y(c, name, prof, xc, z, material, detail=FULL, in_plan=False):
    """A solid of revolution about the line (x = xc, z) along Y: `prof` [(r, y), ...] from the axis back to it."""
    pts = [(xc + r, y) for r, y in prof]
    shape = {"Revolution": {"plane": "Plan", "points": _np(pts), "offset": kit.e(z), "axis": kit.e(xc), "angle": "360"}}
    c._add(name, shape, material, detail, in_plan, False)


def axis_sweep(c, name, eng, cyl, h0, h1, a, b, r, s, material, detail=FULL, x=0.0):
    """A straight sweep along a cylinder axis from h0 to h1: rounded-rectangle section (a in the side plane, b across),
    its centre shifted s towards the V."""
    nsweep(c, name, "Side", [eng.ax(cyl, h0, s), eng.ax(cyl, h1, s)], x, rrect_sec(a, b, r), material, detail)


def axis_disc(c, name, eng, cyl, h0, h1, rad, material, detail=FULL, s=0.0, x=0.0):
    ncyl_side(c, name, eng.p3(cyl, h0, s, x), eng.p3(cyl, h1, s, x), rad, material, detail)


def mesh_piece(c, name, rows_list, material, detail=FULL, in_plan=False, caps=True):
    """A static numeric mesh from rows of points (each row a closed ring, consecutive rows joined)."""
    m = Mesh()
    for rows in rows_list:
        f0 = len(m.f)
        ids = [[m.vtx(p) for p in row] for row in rows]
        for j in range(len(ids) - 1):
            r1, r2 = ids[j], ids[j + 1]
            k = len(r1)
            for i in range(k):
                m.poly([r1[i], r1[(i + 1) % k], r2[(i + 1) % k], r2[i]])
        if caps:
            m.poly(list(reversed(ids[0])))
            m.poly(list(ids[-1]))
        m.orient(f0)
    c.mesh_vertices += len(m.v)
    c._add(name, m.shape(4), material, detail, in_plan, False)


def oriented_rows(path, section, side_of):
    """Rows of a sweep whose section (u, v) is laid with u towards side_of(i, tangent) at each point (no twist)."""
    n = len(path)
    rows = []
    for i in range(n):
        if i == 0:
            t = v_norm(v_sub(path[1], path[0]))
        elif i == n - 1:
            t = v_norm(v_sub(path[-1], path[-2]))
        else:
            t = v_norm(v_add(v_norm(v_sub(path[i], path[i - 1])), v_norm(v_sub(path[i + 1], path[i]))))
        o = side_of(i, t)
        u = v_norm(v_sub(o, v_mul(t, sum(o[k] * t[k] for k in range(3)))))
        w = v_cross(t, u)
        rows.append([v_add(path[i], v_add(v_mul(u, a), v_mul(w, b))) for a, b in section])
    return rows


def hexes_on(points_yz, x0, x1, r):
    """Hex bolt heads along X (from x0 to x1) at (y, z) points."""
    return [hexagon((x0, y, z), (x1, y, z), r) for y, z in points_yz]


def along(poly, k, d=0.0):
    """k points spread evenly along a closed polygon (by length), moved d inwards."""
    pts = inset(poly, d) if d else poly
    seg = [math.hypot(pts[(i + 1) % len(pts)][0] - pts[i][0], pts[(i + 1) % len(pts)][1] - pts[i][1]) for i in range(len(pts))]
    total = sum(seg)
    out = []
    for j in range(k):
        s = total * (j + 0.5) / k
        i = 0
        while s > seg[i]:
            s -= seg[i]
            i += 1
        p, q = pts[i], pts[(i + 1) % len(pts)]
        t = s / seg[i] if seg[i] else 0
        out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


# --- crankcase -------------------------------------------------------------------------------------------------


def case_outline(eng: Engine):
    """Side outline (y, z) of the crankcase: rounded bottom round the flywheels, the two cylinder decks on top."""
    hb = eng.H_BASE
    dfo = eng.ax(FRONT, hb, -0.070)  # front deck, outer end
    dro = eng.ax(REAR, hb, -0.070)
    # the two decks meet over the crank on the V's bisector
    t = (eng.cy - dro[0]) / (-eng.ca)
    ridge = (eng.cy, dro[1] + eng.sa * t)
    pts = [(-0.255, 0.152, 0.075), (0.020, 0.152, 0.030), (0.046, 0.190, 0.012), (0.046, 0.345, 0.025), (dro[0], dro[1], 0.0),
           (ridge[0], ridge[1], 0.0), (dfo[0], dfo[1], 0.0), (-0.288, 0.352, 0.030), (-0.300, 0.272, 0.050)]
    return ccw(fillet(pts, 5))


def crankcase(c, eng: Engine):
    out = case_outline(eng)
    ins = inset(out, 0.011)
    # left and right halves with rounded (blended) outer edges, a recessed split line between them
    nprofile(c, "Carcaça do motor esquerda", "Side", out, 0.0015, 0.0865, CAST_AL, FULL, in_plan=True)
    nblend(c, "Borda da carcaça esquerda", "Side", out, ins, 0.088, 0.012, CAST_AL, FULL, in_plan=True)
    nprofile(c, "Carcaça do motor direita", "Side", out, -0.088, 0.0865, CAST_AL, FULL, in_plan=True)
    nblend(c, "Borda da carcaça direita", "Side", ins, out, -0.100, 0.012, CAST_AL, FULL, in_plan=True)
    nprofile(c, "Junta da carcaça", "Side", inset(out, 0.003), -0.0015, 0.003, DARK_METAL, FULL)
    # sump pan and drain plug
    pan = rrect_poly(-0.070, -0.195, 0.070, 0.005, 0.03)
    nblend(c, "Cárter de óleo", "Plan", inset(ccw(pan), 0.008), ccw(pan), 0.1455, 0.0075, CAST_AL, FULL)
    c.cyl("Bujão do cárter", 0.0, -0.06, 0.1385, 0.008, 0.0075, CHROME, FINE)
    put(c, "Sextavado do bujão", hexagon((0.0, -0.06, 0.1385), (0.0, -0.06, 0.1415), 0.0105, ref=X), CHROME, FINE, lua=True)
    # lower mount bosses against the frame's lugs
    hp = eng.hp
    for i, (x, y, z) in enumerate(hp.ENGINE_MOUNTS["lower"]):
        s = 1 if x > 0 else -1
        x0 = s * 0.072 if s > 0 else -0.0995
        c.box(f"Pé de fixação do motor {i + 1}", x0, y - 0.018, 0.150, 0.0275, 0.036, 0.034, CAST_AL)
    # front engine mount: a cast bracket from the case to the downtube lugs (bolt at y -0.40, z 0.40)
    fm = hp.ENGINE_MOUNTS["front"][0]
    bracket = ccw(circles_hull([(fm[1], fm[2], 0.017), (-0.285, 0.352, 0.032)], n=20))
    nprofile(c, "Suporte dianteiro do motor", "Side", bracket, -0.0845, 0.169, ENGINE_BLACK, FULL)
    ndisc_x(c, "Bucha do suporte dianteiro", -0.086, 0.086, fm[1], fm[2], 0.0115, DARK_METAL, FINE)
    # cam chest and timing (cam) cover on the right
    cam = ccw(circles_hull([(-0.120, 0.300, 0.045), (-0.062, 0.365, 0.050)], n=24))
    nprofile(c, "Caixa de comando", "Side", inset(cam, -0.006), -0.112, 0.0125, CAST_AL, FULL)
    nprofile(c, "Tampa de comando", "Side", cam, -0.1325, 0.0205, CHROME, FULL)
    nblend(c, "Borda da tampa de comando", "Side", inset(cam, 0.010), cam, -0.1415, 0.009, CHROME, FULL)
    nblend(c, "Tampa do ponto", "Side", circ(-0.120, 0.300, 0.022, 32), circ(-0.120, 0.300, 0.029, 32), -0.1485, 0.007, CHROME, FULL)
    screws = hexes_on(along(cam, 9, 0.006), -0.1415, -0.1465, 0.0045)
    screws += hexes_on([(-0.120 + 0.020 * math.cos(math.radians(a)), 0.300 + 0.020 * math.sin(math.radians(a))) for a in (40, 220)],
                       -0.1485, -0.1515, 0.0032)
    put(c, "Parafusos da tampa de comando", screws, CHROME, FINE, lua=True)


# --- cylinders and heads ----------------------------------------------------------------------------------------


def cylinders(c, eng: Engine):
    for cyl, label in ((FRONT, "dianteiro"), (REAR, "traseiro")):
        # FINE: barrel wall + individual fins (exact circles), head block + rounded-rectangle fins
        axis_disc(c, f"Cilindro {label}", eng, cyl, eng.H_BASE - 0.003, eng.H_HEAD + 0.004, eng.R_CORE, ENGINE_BLACK, FINE)
        axis_disc(c, f"Base do cilindro {label}", eng, cyl, eng.H_BASE - 0.003, eng.H_BASE + 0.006, eng.R_CORE + 0.005, ENGINE_BLACK, FINE)
        pitch, t = 0.0105, 0.0036
        h = 0.150
        k = 0
        while h <= eng.H_HEAD - 0.006:
            k += 1
            axis_disc(c, f"Aleta do cilindro {label} {k}", eng, cyl, h - t / 2, h + t / 2, eng.fin_r(h), ENGINE_BLACK, FINE)
            h += pitch
        a, b, d = eng.HEAD_A, eng.HEAD_B, eng.HEAD_D
        axis_sweep(c, f"Cabeçote {label}", eng, cyl, eng.H_HEAD - 0.002, eng.H_ROCKER + 0.002, a - 0.016, b - 0.022, 0.016, d,
                   ENGINE_BLACK, FINE)
        h = eng.H_HEAD + 0.0045
        k = 0
        while h <= eng.H_ROCKER - 0.004:
            k += 1
            grow = 1.0 if k > 1 else 0.93
            axis_sweep(c, f"Aleta do cabeçote {label} {k}", eng, cyl, h - 0.002, h + 0.002, a * grow, b * grow, 0.022, d,
                       ENGINE_BLACK, FINE)
            h += pitch
        # MEDIUM: stepped stand-in of the finned barrel and head
        for i, (h0, h1, r) in enumerate(((eng.H_BASE - 0.003, 0.168, 0.060), (0.168, 0.200, 0.074), (0.200, eng.H_HEAD, eng.R_FIN - 0.002))):
            axis_disc(c, f"Cilindro {label} (médio) {i + 1}", eng, cyl, h0, h1, r, ENGINE_BLACK, MEDIUM)
        axis_sweep(c, f"Cabeçote {label} (médio)", eng, cyl, eng.H_HEAD, eng.H_ROCKER + 0.002, a - 0.002, b - 0.002, 0.022, d,
                   ENGINE_BLACK, MEDIUM)
        # exhaust port (outer face, right of centre) and intake port (V face)
        axis_disc_across(c, f"Saída de escape {label}", eng, cyl, eng.H_PORT_EX, -0.050, -0.090, 0.025, -0.032, ENGINE_BLACK, FULL)
        axis_disc_across(c, f"Entrada de admissão {label}", eng, cyl, eng.H_PORT_IN, 0.035, 0.062, 0.019, -0.025, ENGINE_BLACK, FULL)
        # spark plug boss on the left face
        y, z = eng.ax(cyl, eng.H_PORT_EX, -0.010)
        ndisc_x(c, f"Ressalto da vela {label}", 0.070, 0.094, y, z, 0.014, ENGINE_BLACK, FULL)


def axis_disc_across(c, name, eng, cyl, h, s0, s1, r, x, material, detail):
    """A round boss across a cylinder axis (along the in-plane normal) at height h, from s0 to s1, at x."""
    ncyl_side(c, name, eng.p3(cyl, h, s0, x), eng.p3(cyl, h, s1, x), r, material, detail)


def valvetrain(c, eng: Engine):
    a, b, d = eng.ROCK_A, eng.ROCK_B, eng.ROCK_D
    bolts, collars = [], []
    for cyl, label in ((FRONT, "dianteira"), (REAR, "traseira")):
        hr, ht = eng.H_ROCKER, eng.H_TOP
        axis_sweep(c, f"Base da caixa de balancins {label}", eng, cyl, hr, hr + 0.018, a, b, 0.020, d, POLISHED_AL, FULL)
        axis_sweep(c, f"Espaçador da caixa de balancins {label}", eng, cyl, hr + 0.018, hr + 0.025, a - 0.003, b - 0.003, 0.020, d,
                   CHROME, FULL)
        axis_sweep(c, f"Tampa de balancins {label}", eng, cyl, hr + 0.025, ht - 0.006, a - 0.001, b - 0.001, 0.026, d, CHROME, FULL)
        axis_sweep(c, f"Topo da tampa de balancins {label}", eng, cyl, ht - 0.006, ht, a - 0.010, b - 0.010, 0.022, d, CHROME, FULL)
        dv, du = eng.dir(cyl), eng.vdir(cyl)
        for su in (-0.050, 0.050):
            for sx in (-0.050, 0.050):
                p0 = v_add(eng.p3(cyl, ht - 0.001, d + su), (sx, 0, 0))
                bolts.append(hexagon(p0, v_add(p0, v_mul(dv, 0.006)), 0.0055, ref=X))
        for sx in (-1, 1):
            for su in (-0.045, 0.045):
                p0 = v_add(eng.p3(cyl, hr + 0.009, d + su), (sx * b, 0, 0))
                bolts.append(hexagon(p0, v_add(p0, (sx * 0.005, 0, 0)), 0.0048, ref=du))
        # pushrod tubes: from the lifter block on the V's bisector up to the rocker box (right side, one plane)
        for k, s in enumerate(eng.PUSH_S):
            h0 = s / math.tan(math.radians(eng.hp.V_ANGLE / 2))
            axis_disc(c, f"Tubo de vareta {label} {k + 1}", eng, cyl, h0, hr + 0.004, eng.PUSH_R, CHROME, FULL, s=s, x=eng.PUSH_X)
            for hh in (hr - 0.020, h0 + 0.070):
                collars.append(cyl_ax(eng.p3(cyl, hh, s, eng.PUSH_X), dv, 0.010, eng.PUSH_R + 0.002, 14))
    put(c, "Parafusos das caixas de balancins", bolts, CHROME, FINE, lua=True)
    put(c, "Anéis dos tubos de vareta", collars, CHROME, FINE, lua=True)
    blk = ccw([(-0.163, 0.528), (-0.077, 0.528), (-0.093, 0.442), (-0.147, 0.442)])
    nprofile(c, "Bloco dos tuchos", "Side", blk, eng.PUSH_X - 0.015, 0.030, CAST_AL, FULL)
    # head steady: twin plates from both rocker boxes up to the frame tab under the backbone
    top = eng.hp.ENGINE_MOUNTS["top"][0]
    fa = eng.ax(FRONT, eng.H_ROCKER + 0.016, d + a - 0.012)
    ra = eng.ax(REAR, eng.H_ROCKER + 0.016, d + a - 0.012)
    bar = ccw(circles_hull([(fa[0], fa[1], 0.011), (ra[0], ra[1], 0.011)], n=16))
    link = ccw(circles_hull([(top[1], fa[1] + 0.004, 0.012), (top[1], top[2] - 0.012, 0.0105)], n=16))
    for s, label in ((1, "esquerda"), (-1, "direita")):
        nprofile(c, f"Ponte do suporte superior {label}", "Side", bar, 0.0045 if s > 0 else -0.0085, 0.004, STEEL_BLACK, FULL)
        nprofile(c, f"Tirante do suporte superior {label}", "Side", link, 0.0045 if s > 0 else -0.0085, 0.004, STEEL_BLACK, FULL)
    ndisc_x(c, "Parafuso do suporte superior", -0.012, 0.012, top[1], top[2] - 0.012, 0.0045, CHROME, FINE)


def cyl_ax(center, axis, length, r, n=16):
    return cyl(v_add(center, v_mul(axis, -length / 2)), v_add(center, v_mul(axis, length / 2)), r, n)


# --- intake: manifold, carburettor, air cleaner (rider's right) ------------------------------------------------------


def intake(c, eng: Engine):
    acy, acz = eng.AC
    runners = []
    for cyl in (FRONT, REAR):
        y0, z0 = eng.ax(cyl, eng.H_PORT_IN, 0.045)
        sgn = -cyl  # front runner comes from -y towards the centre
        path = [(-0.025, y0, z0), (-0.026, acy - sgn * 0.050, acz + 0.004), (-0.031, acy - sgn * 0.022, acz + 0.001), (-0.044, acy - sgn * 0.004, acz)]
        path = catmull(path, 3)
        runners.append(sweep(path, circle2(0.0165, 12)))
    put(c, "Coletor de admissão", runners, CAST_AL, FULL)
    ndisc_x(c, "Bocal de admissão", -0.096, -0.036, acy, acz, 0.0215, CAST_AL, FULL)
    ndisc_x(c, "Flange do coletor", -0.100, -0.094, acy, acz, 0.027, CAST_AL, FINE)
    ndisc_x(c, "Corpo do carburador", -0.1395, -0.098, acy, acz, 0.030, CAST_AL, FULL)
    c.cyl("Câmara de vácuo do carburador", -0.118, acy, acz + 0.020, 0.0215, 0.032, CAST_AL)
    c.cyl("Tampa da câmara de vácuo", -0.118, acy, acz + 0.052, 0.0185, 0.005, POLISHED_AL, FINE)
    c.box("Cuba do carburador", -0.136, acy - 0.026, acz - 0.058, 0.034, 0.052, 0.034, CAST_AL)
    ndisc_x(c, "Tambor do acelerador", -0.142, -0.098, acy + 0.034, acz + 0.006, 0.011, POLISHED_AL, FINE)
    # round air cleaner: backing plate, drum, domed cover, cap
    ndisc_x(c, "Base do filtro de ar", -0.1475, -0.1395, acy, acz, 0.098, ENGINE_BLACK, FULL, in_plan=True)
    nblend(c, "Tampa do filtro de ar", "Side", circ(acy, acz, 0.108), circ(acy, acz, 0.112), -0.186, 0.0385, CHROME, FULL, in_plan=True)
    nblend(c, "Cúpula do filtro de ar", "Side", circ(acy, acz, 0.086), circ(acy, acz, 0.108), -0.2005, 0.0145, CHROME, FULL)
    nblend(c, "Centro do filtro de ar", "Side", circ(acy, acz, 0.050), circ(acy, acz, 0.086), -0.2065, 0.006, CHROME, FULL)
    ndisc_x(c, "Friso do filtro de ar", -0.1900, -0.1840, acy, acz, 0.1115, POLISHED_AL, FINE)
    screws = [hexagon((-0.2065, acy, acz), (-0.2125, acy, acz), 0.008)]
    screws += hexes_on([(acy + 0.068 * math.cos(math.radians(a)), acz + 0.068 * math.sin(math.radians(a))) for a in (90, 210, 330)],
                       -0.2035, -0.2075, 0.0045)
    put(c, "Parafusos do filtro de ar", screws, CHROME, FINE, lua=True)


# --- ignition: plugs, leads, coil, horn (left) ---------------------------------------------------------------------


def ignition(c, eng: Engine):
    plugs, boots = [], []
    leads = []
    coil_y = (-0.137, -0.103)
    for side, cy_ in zip((FRONT, REAR), coil_y):
        y, z = eng.ax(side, eng.H_PORT_EX, -0.010)
        plugs.append(hexagon((0.094, y, z), (0.104, y, z), 0.0095))
        plugs.append(cyl((0.104, y, z), (0.124, y, z), 0.0055, 12))
        boots.append(lathe([(0, 0.112), (0.0085, 0.112), (0.0095, 0.118), (0.0095, 0.134), (0.0065, 0.142), (0, 0.142)], (0, y, z), X, 14))
        path = [(0.140, y, z), (0.154, y, z + 0.004), (0.158, y + side * 0.012, z + 0.030), (0.140, cy_ + side * 0.050, 0.645),
                (0.110, cy_ + side * 0.012, 0.664), (0.086, cy_, 0.664)]
        leads.append(sweep(catmull(path, 3), circle2(0.0042, 8)))
    put(c, "Velas de ignição", plugs, CERAMIC, FINE, lua=True)
    put(c, "Cachimbos das velas", boots, RUBBER, FINE, lua=True)
    put(c, "Cabos de vela", leads, BLACK_PLASTIC, FINE)
    c.box("Bobina de ignição", 0.024, -0.152, 0.640, 0.056, 0.064, 0.048, BLACK_PLASTIC)
    c.box("Suporte da bobina", 0.0085, -0.128, 0.652, 0.0160, 0.016, 0.026, STEEL_BLACK, FINE)
    put(c, "Terminais da bobina", [cyl((0.080, y_, 0.664), (0.090, y_, 0.664), 0.0068, 12) for y_ in coil_y], BLACK_PLASTIC, FINE, lua=True)
    # horn on the left of the front engine mount
    hy, hz = -0.325, 0.372
    ndisc_x(c, "Corpo da buzina", 0.0845, 0.102, hy, hz, 0.040, ENGINE_BLACK, FULL)
    nblend(c, "Tampa da buzina", "Side", circ(hy, hz, 0.042, 40), circ(hy, hz, 0.030, 40), 0.102, 0.012, CHROME, FULL)
    ndisc_x(c, "Centro da buzina", 0.1135, 0.117, hy, hz, 0.012, CHROME, FINE)


# --- primary case (left) -------------------------------------------------------------------------------------------


def primary(c, eng: Engine):
    cy, cz = eng.cy, eng.cz
    ky, kz = eng.CLUTCH
    outer = ccw(circles_hull([(cy, cz, 0.088), (ky, kz, 0.100), (-0.025, 0.205, 0.050)], n=40))
    inner = ccw(circles_hull([(cy, cz, 0.082), (0.040, 0.300, 0.074), (-0.025, 0.210, 0.048)], n=32))
    nprofile(c, "Carcaça interna da primária", "Side", inner, 0.0995, 0.0390, CAST_AL, FULL, in_plan=True)
    nprofile(c, "Tampa da primária", "Side", outer, 0.1380, 0.0420, CHROME, FULL, in_plan=True)
    nblend(c, "Borda da tampa da primária", "Side", outer, inset(outer, 0.012), 0.1800, 0.0120, CHROME, FULL, in_plan=True)
    # derby (clutch) cover and inspection cover
    nprofile(c, "Aro da tampa da embreagem", "Side", circ(ky, kz, 0.075, 48), 0.1915, 0.0055, POLISHED_AL, FULL)
    nblend(c, "Tampa da embreagem", "Side", circ(ky, kz, 0.059, 48), circ(ky, kz, 0.043, 48), 0.1965, 0.0085, CHROME, FULL)
    insp_c = (-0.040, 0.348)
    oval = [(insp_c[0] + 0.052 * math.cos(2 * math.pi * i / 40) * math.cos(0.12) - 0.024 * math.sin(2 * math.pi * i / 40) * math.sin(0.12),
             insp_c[1] + 0.052 * math.cos(2 * math.pi * i / 40) * math.sin(0.12) + 0.024 * math.sin(2 * math.pi * i / 40) * math.cos(0.12))
            for i in range(40)]
    small = [(insp_c[0] + (u - insp_c[0]) * 0.80, insp_c[1] + (v - insp_c[1]) * 0.70) for u, v in oval]
    nblend(c, "Tampa de inspeção da primária", "Side", oval, small, 0.1915, 0.0065, CHROME, FULL)
    bolts = hexes_on(along(outer, 14, 0.019), 0.1915, 0.1965, 0.0045)
    bolts += hexes_on([(ky + 0.067 * math.cos(math.radians(90 + 72 * i)), kz + 0.067 * math.sin(math.radians(90 + 72 * i))) for i in range(5)],
                      0.1970, 0.2015, 0.0042)
    bolts += hexes_on([(insp_c[0] + 0.041 * s * math.cos(0.12) - 0.012 * t * math.sin(0.12), insp_c[1] + 0.041 * s * math.sin(0.12)
                        + 0.012 * t * math.cos(0.12)) for s in (-1, 1) for t in (-1, 1)], 0.1980, 0.2015, 0.0035)
    put(c, "Parafusos da primária", bolts, CHROME, FINE, lua=True)


# --- gearbox, starter, front pulley ---------------------------------------------------------------------------------


def gearbox_outline():
    # stays out of UNDERSEAT_ENV (y > 0.20 above z 0.30): the rear block under the output shaft, the main block ahead of it
    pts = [(0.040, 0.166, 0.012), (0.238, 0.160, 0.030), (0.266, 0.200, 0.015), (0.266, 0.288, 0.010), (0.244, 0.299, 0.006),
           (0.198, 0.299, 0.006), (0.198, 0.418, 0.014), (0.184, 0.434, 0.010), (0.121, 0.434, 0.006), (0.118, 0.356, 0.006),
           (0.040, 0.352, 0.006)]
    return ccw(fillet(pts, 4))


def gearbox(c, eng: Engine):
    out = gearbox_outline()
    ins = inset(out, 0.009)
    nprofile(c, "Caixa de câmbio", "Side", out, -0.090, 0.180, CAST_AL, FULL)
    nblend(c, "Borda esquerda do câmbio", "Side", out, ins, 0.090, 0.010, CAST_AL, FULL)
    nblend(c, "Borda direita do câmbio", "Side", ins, out, -0.100, 0.010, CAST_AL, FULL)
    # top cover
    tc = ccw(rrect_poly(-0.066, 0.126, 0.066, 0.192, 0.014))
    nblend(c, "Tampa superior do câmbio", "Plan", tc, inset(tc, 0.007), 0.433, 0.014, CHROME, FULL)
    # right-hand end cover with the clutch release cover on the output shaft line
    py, pz = eng.PULLEY[1], eng.PULLEY[2]
    ec = ccw(rrect_poly(0.120, 0.196, 0.196, 0.408, 0.020))
    nprofile(c, "Tampa lateral do câmbio", "Side", ec, -0.1100, 0.0105, CHROME, FULL)
    nblend(c, "Borda da tampa lateral do câmbio", "Side", inset(ec, 0.006), ec, -0.1150, 0.005, CHROME, FULL)
    rc = (0.160, pz + 0.010)
    nblend(c, "Tampa do acionamento da embreagem", "Side", circ(*rc, 0.016, 36), circ(*rc, 0.0235, 36), -0.1240, 0.009, CHROME, FULL)
    bolts = hexes_on(along(ec, 8, 0.008), -0.1150, -0.1195, 0.0042)
    bolts += hexes_on([(rc[0] + 0.019 * math.cos(math.radians(30 + 120 * i)), rc[1] + 0.019 * math.sin(math.radians(30 + 120 * i)))
                       for i in range(3)], -0.1215, -0.1255, 0.0030)
    bolts += [hexagon((x, y, 0.447), (x, y, 0.4525), 0.0045, ref=X) for x in (-0.052, 0.052) for y in (0.140, 0.159, 0.178)]
    put(c, "Parafusos do câmbio", bolts, CHROME, FINE, lua=True)
    # rear mount bosses against the frame's lugs
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        x, y, z = eng.hp.ENGINE_MOUNTS["rear"][0 if s > 0 else 1]
        ndisc_x(c, f"Ressalto de fixação traseiro {label}", s * 0.088, s * 0.1035, y, z, 0.017, CAST_AL, FULL)
    # starter motor in the pocket at the gearbox's front top, solenoid on it
    sy, sz = 0.079, 0.392
    ndisc_x(c, "Motor de partida", -0.100, 0.085, sy, sz, 0.034, ENGINE_BLACK, FULL)
    nblend(c, "Tampa do motor de partida", "Side", circ(sy, sz, 0.026, 32), circ(sy, sz, 0.035, 32), -0.1160, 0.016, CHROME, FULL)
    ndisc_x(c, "Solenoide de partida", -0.108, -0.020, sy + 0.006, sz + 0.050, 0.0185, CHROME, FULL)
    nblend(c, "Tampa do solenoide", "Side", circ(sy + 0.006, sz + 0.050, 0.013, 24), circ(sy + 0.006, sz + 0.050, 0.0185, 24),
           -0.1160, 0.008, CHROME, FINE)
    put(c, "Terminais do motor de partida", [hexagon((-0.116, sy + 0.006, sz + 0.050 + dz), (-0.122, sy + 0.006, sz + 0.050 + dz), 0.0042)
                                             for dz in (-0.008, 0.008)] + [hexagon((-0.116, sy + dy, sz), (-0.121, sy + dy, sz), 0.0042)
                                                                           for dy in (-0.024, 0.024)], CHROME, FINE, lua=True)
    # front pulley (gearbox output): flanges, toothed rim, hub and nut, in the belt's plane
    bx, bw = eng.hp.BELT_X, eng.hp.BELT_W
    pr = eng.hp.FRONT_PULLEY_R
    ndisc_x(c, "Ressalto do eixo de saída", 0.0995, 0.1040, py, pz, 0.036, CAST_AL, FULL)
    ndisc_x(c, "Polia dianteira", bx - bw / 2 - 0.0005, bx + bw / 2 + 0.0005, py, pz, pr - 0.0045, POLISHED_AL, FULL)
    ndisc_x(c, "Flange interna da polia dianteira", 0.1035, bx - bw / 2 - 0.0005, py, pz, pr + 0.0045, POLISHED_AL, FULL)
    ndisc_x(c, "Flange externa da polia dianteira", bx + bw / 2 + 0.0005, 0.1365, py, pz, pr + 0.0045, POLISHED_AL, FULL)
    nhex_x(c, "Porca da polia dianteira", 0.1365, 0.1455, py, pz, 0.021, CHROME, FINE)
    tooth = box((bx, py, pz + pr - 0.0032), (bw, 0.0060, 0.0034))
    put(c, "Dentes da polia dianteira", ring(tooth, (bx, py, pz), X, 30), POLISHED_AL, FINE, lua=True)
    put(c, "Trava da porca da polia", [hexagon((0.1365, py + 0.032 * math.cos(math.radians(a)), pz + 0.032 * math.sin(math.radians(a))),
                                                (0.1395, py + 0.032 * math.cos(math.radians(a)), pz + 0.032 * math.sin(math.radians(a))), 0.004)
                                        for a in (45, 225)], CHROME, FINE, lua=True)


# --- oil filter and lines -------------------------------------------------------------------------------------------------


def oil(c, eng: Engine):
    a0, a1 = (0.0, -0.278, 0.262), (0.0, -0.296, 0.256)
    f0, f1 = (0.0, -0.296, 0.256), (0.0, -0.374, 0.228)
    ncyl_side(c, "Suporte do filtro de óleo", a0, a1, 0.031, CAST_AL, FULL)
    ncyl_side(c, "Filtro de óleo", f0, (0.0, -0.366, 0.231), 0.038, CHROME, FULL)
    ncyl_side(c, "Fundo do filtro de óleo", (0.0, -0.366, 0.231), f1, 0.034, CHROME, FULL)
    put(c, "Sextavado do filtro de óleo", hexagon((0.0, -0.373, 0.2283), (0.0, -0.381, 0.2255), 0.014), CHROME, FINE, lua=True)
    lines = []
    for dx in (0.0, -0.016):
        path = [(-0.097 + dx * 0.4, -0.040, 0.238), (-0.104 + dx * 0.4, -0.006, 0.212), (-0.088 + dx, 0.040, 0.170),
                (-0.072 + dx, 0.100, 0.1515), (-0.072 + dx, 0.215, 0.1515), (-0.072 + dx, 0.262, 0.167), (-0.072 + dx, 0.281, 0.215),
                (-0.072 + dx, 0.284, 0.304)]
        lines.append(sweep(catmull(path, 3), circle2(0.0055, 8)))
    put(c, "Mangueiras de óleo", lines, STAINLESS, FINE)
    put(c, "Conexões das mangueiras de óleo", [cyl((-0.091 + dx * 0.4, -0.048, 0.246), (-0.101 + dx * 0.4, -0.034, 0.232), 0.0075, 6)
                                               for dx in (0.0, -0.016)], CHROME, FINE, lua=True)


# --- exhaust (rider's right) ------------------------------------------------------------------------------------------------


MUF_X = -0.265
MUF = {FRONT: (0.250, 0.362, 1.060), REAR: (0.345, 0.402, 1.100)}  # z of the axis, inlet y, end y
R_PIPE, R_MUF = 0.0222, 0.040


def header_paths(eng: Engine):
    fy, fz = eng.ax(FRONT, eng.H_PORT_EX, -0.084)
    ry, rz = eng.ax(REAR, eng.H_PORT_EX, -0.084)
    zf, yf = MUF[FRONT][0], MUF[FRONT][1]
    zr, yr = MUF[REAR][0], MUF[REAR][1]
    front = [(-0.032, fy, fz), (-0.040, fy - 0.026, fz - 0.010), (-0.080, -0.374, 0.512), (-0.145, -0.392, 0.482), (-0.190, -0.384, 0.445),
             (-0.205, -0.352, 0.408), (-0.208, -0.290, 0.372), (-0.210, -0.215, 0.310), (-0.212, -0.130, 0.258), (-0.218, -0.030, 0.238),
             (-0.230, 0.090, 0.238), (-0.248, 0.215, 0.245), (-0.262, 0.320, zf), (MUF_X, yf + 0.030, zf)]
    rear = [(-0.032, ry, rz), (-0.040, ry + 0.026, rz - 0.010), (-0.090, 0.132, 0.505), (-0.160, 0.152, 0.470), (-0.214, 0.182, 0.420),
            (-0.241, 0.232, 0.375), (-0.256, 0.300, 0.350), (-0.263, 0.360, zr), (MUF_X, yr + 0.030, zr)]
    return front, rear


def exhaust(c, eng: Engine):
    paths = header_paths(eng)
    pipes, shields, clamps, flanges = [], [], [], []
    shield_spans = {FRONT: (3, 8), REAR: (2, 6)}
    for (cyl, label), pts in zip(((FRONT, "dianteiro"), (REAR, "traseiro")), paths):
        dense = catmull(pts, 3)
        pipes.append(sweep(dense, circle2(R_PIPE, 12)))
        # port flange and its two nuts
        d0 = v_norm(v_sub(pts[1], pts[0]))
        flanges.append(cyl_ax(v_add(pts[0], v_mul(d0, 0.010)), d0, 0.008, R_PIPE + 0.008, 16))
        e1 = v_norm(v_cross(d0, X))
        for s in (-1, 1):
            q = v_add(v_add(pts[0], v_mul(d0, 0.016)), v_mul(e1, s * 0.024))
            flanges.append(hexagon(q, v_add(q, v_mul(d0, 0.007)), 0.0055))
        # heat shield over the visible run (outer side), clamps at its ends
        i0, i1 = shield_spans[cyl]
        run = catmull(pts[i0:i1 + 1], 3)
        sec = [(0.0300 * math.cos(math.radians(a)), 0.0300 * math.sin(math.radians(a))) for a in range(-85, 86, 17)]
        sec += [(0.0284 * math.cos(math.radians(a)), 0.0284 * math.sin(math.radians(a))) for a in range(85, -86, -17)]
        out_dir = (-1.0, -0.35, 0.25) if cyl == FRONT else (-1.0, 0.25, 0.35)
        rows = oriented_rows(run, sec, lambda i, t, o=out_dir: o)
        shields.append(rows)
        for q, t in ((run[1], v_norm(v_sub(run[2], run[0]))), (run[-2], v_norm(v_sub(run[-1], run[-3])))):
            clamps.append(cyl_ax(q, t, 0.012, 0.0318, 20))
        # slip joint clamp at the muffler inlet
        zm, ym, _ = MUF[cyl]
        clamps.append(lathe([(0.0245, 0.0), (0.0275, 0.0), (0.0275, 0.016), (0.0245, 0.016)], (MUF_X, ym + 0.004, zm), Y, 24, closed=True))
        clamps.append(hexagon((MUF_X - 0.020, ym + 0.012, zm + 0.020), (MUF_X - 0.026, ym + 0.012, zm + 0.026), 0.0045))
    put(c, "Coletores de escape", pipes, CHROME, FULL, in_plan=True)
    mesh_piece(c, "Protetores de calor", shields, CHROME, FULL)
    put(c, "Flanges do escapamento", flanges, CHROME, FINE, lua=True)
    put(c, "Abraçadeiras do escapamento", clamps, STAINLESS, FINE, lua=True)
    # staggered mufflers: inlet sleeve, cone, body, end cap with the outlet recessed in it
    for cyl, label in ((FRONT, "inferior"), (REAR, "superior")):
        zm, y0, y1 = MUF[cyl]
        body = [(0.0, y0), (0.0245, y0), (0.0245, y0 + 0.030), (0.034, y0 + 0.060), (R_MUF - 0.001, y0 + 0.095), (R_MUF, y0 + 0.110),
                (R_MUF, y1 - 0.040), (0.0, y1 - 0.040)]
        nrev_y(c, f"Silencioso {label}", body, MUF_X, zm, CHROME, FULL, in_plan=True)
        cap = [(0.0, y1 - 0.034), (0.0170, y1 - 0.034), (0.0170, y1), (0.0345, y1), (0.0408, y1 - 0.007), (0.0410, y1 - 0.044),
               (R_MUF - 0.004, y1 - 0.046), (0.0, y1 - 0.046)]
        nrev_y(c, f"Ponteira do silencioso {label}", cap, MUF_X, zm, CHROME, FULL)
        nrev_y(c, f"Saída do silencioso {label}", [(0.0, y1 - 0.0335), (0.0166, y1 - 0.0335), (0.0166, y1 - 0.030), (0.0, y1 - 0.030)],
               MUF_X, zm, DARK_METAL, FINE)
    # brackets: header straps to the case and gearbox cover, muffler hanger to the right seat stay, bridge between mufflers
    zf, zr = MUF[FRONT][0], MUF[REAR][0]
    nprofile(c, "Suporte do coletor dianteiro", "Front", [(-0.0995, 0.296), (-0.0995, 0.316), (-0.200, 0.318), (-0.200, 0.298)],
             -0.209, 0.006, STEEL_BLACK, FULL)
    nprofile(c, "Suporte do coletor traseiro", "Front", [(-0.1145, 0.392), (-0.1145, 0.410), (-0.200, 0.436), (-0.200, 0.414)],
             0.176, 0.006, STEEL_BLACK, FULL)
    hang = [(-0.140, 0.522), (-0.130, 0.545), (-0.146, 0.551), (-0.257, 0.393), (-0.272, 0.381), (-0.262, 0.374)]
    nprofile(c, "Suporte dos silenciosos", "Front", hang, 0.452, 0.007, STEEL_BLACK, FULL)
    nprofile(c, "Ponte dos silenciosos", "Front", rrect_poly(MUF_X - 0.012, zf + 0.030, MUF_X + 0.012, zr - 0.030, 0.004, 2),
             0.800, 0.008, STEEL_BLACK, FULL)
    nprofile(c, "Ponte dianteira dos silenciosos", "Front", rrect_poly(MUF_X - 0.012, zf + 0.030, MUF_X + 0.012, zr - 0.030, 0.004, 2),
             0.452, 0.007, STEEL_BLACK, FULL)
    put(c, "Parafusos dos suportes do escapamento",
        [hexagon((-0.138, 0.452, 0.536), (-0.138, 0.444, 0.536), 0.0055, ref=X), hexagon((MUF_X, 0.799, (zf + zr) / 2), (MUF_X, 0.793, (zf + zr) / 2), 0.005, ref=X),
         hexagon((MUF_X, 0.451, (zf + zr) / 2), (MUF_X, 0.445, (zf + zr) / 2), 0.005, ref=X)], CHROME, FINE, lua=True)


# --- coarse stand-ins ------------------------------------------------------------------------------------------------------


def coarse(c, eng: Engine):
    nprofile(c, "Motor (simplificado)", "Side", case_outline(eng), -0.100, 0.200, CAST_AL, COARSE, in_plan=True)
    nprofile(c, "Câmbio (simplificado)", "Side", gearbox_outline(), -0.100, 0.200, CAST_AL, COARSE)
    cam = ccw(circles_hull([(-0.120, 0.300, 0.045), (-0.062, 0.365, 0.050)], n=12))
    nprofile(c, "Tampa de comando (simplificada)", "Side", cam, -0.1415, 0.0415, CHROME, COARSE)
    outer = ccw(circles_hull([(eng.cy, eng.cz, 0.088), (eng.CLUTCH[0], eng.CLUTCH[1], 0.100), (-0.025, 0.205, 0.050)], n=20))
    nprofile(c, "Primária (simplificada)", "Side", outer, 0.0995, 0.0975, CHROME, COARSE, in_plan=True)
    for cyl, label in ((FRONT, "dianteiro"), (REAR, "traseiro")):
        axis_disc(c, f"Cilindro {label} (simplificado)", eng, cyl, eng.H_BASE - 0.003, eng.H_ROCKER, eng.R_FIN - 0.002, ENGINE_BLACK, COARSE)
        axis_sweep(c, f"Caixa de balancins {label} (simplificada)", eng, cyl, eng.H_ROCKER, eng.H_TOP, eng.ROCK_A, eng.ROCK_B, 0.022,
                   eng.ROCK_D, CHROME, COARSE)
    acy, acz = eng.AC
    ndisc_x(c, "Filtro de ar (simplificado)", -0.2065, -0.1395, acy, acz, 0.111, CHROME, COARSE, in_plan=True)
    paths = header_paths(eng)
    put(c, "Coletores (simplificados)", [sweep(p, circle2(R_PIPE, 8)) for p in paths], CHROME, COARSE, in_plan=True)
    for cyl, label in ((FRONT, "inferior"), (REAR, "superior")):
        zm, y0, y1 = MUF[cyl]
        nrev_y(c, f"Silencioso {label} (simplificado)", [(0.0, y0), (0.0245, y0), (0.034, y0 + 0.060), (R_MUF, y0 + 0.110), (R_MUF, y1),
                                                          (0.0, y1)], MUF_X, zm, CHROME, COARSE, in_plan=True)
