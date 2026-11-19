"""Bodywork and controls of the Moto custom: teardrop tank, solo seat, fenders, lights, plate, forward
controls, handlebar with its controls and mirrors, headlight, speedometer, cables.

How it is built (see base.py): the tank and the seat are lean numeric meshes made here from their
sections (a tank section is a closed loop with a tunnel over the backbone; the ends close by
zipping the outer skin to the tunnel); planar static parts (rear fender, side covers, struts, pedals,
lights at the rear, plate) are engine shapes; everything on the steering head (bar, levers,
switches, mirrors, headlight, signals, speedometer, front fender) is in the moving-parts script
(group STEER), and cables from the bar to the frame are gtubes whose points follow their own group.
Small many-vertex fine details (ribbed pegs, pinstripes, piping, stitches) go to the script too
(lua=True) to keep the .ccomp small. Plan: tank, seat and rear fender draw; the steered bar,
mirrors, headlight and front fender draw through plan-only stand-ins turned by steer_expr.
"""

from __future__ import annotations

import math
from collections import defaultdict, deque

from _moto.base import (
    ACCENT, ALL, BLACK_PLASTIC, CHROME, COARSE, DARK_METAL, FINE, FRAME_BLACK, FULL, LEATHER, LENS_AMBER, LENS_CLEAR,
    LENS_RED, MEDIUM, POLISHED_AL, RUBBER, STAINLESS, STEER, TANK_PAINT, ENGINE_BLACK, Hardpoints, Mesh, box, catmull, circle2,
    circles_hull, cyl, gtube, hexagon, hull2, lathe, ncyl_side, ndisc_x, nhex_x, nprofile, nsweep, put, ring, rrect2, sphere, steer_expr,
    sweep, v_add, v_cross, v_dot, v_len, v_lerp, v_mul, v_norm, v_sub,
)
from _moto.motor import ccw, fillet, inset, nblend  # outline helpers and engine Blends

X = (1.0, 0.0, 0.0)
Y = (0.0, 1.0, 0.0)
Z = (0.0, 0.0, 1.0)

PLATE_WHITE = "Aço pintado branco"
MERCOSUL_BLUE = "Azul Mercosul"
DIAL = "Plástico preto brilhante"
TICKS = "Branco"
NEEDLE = "Plástico vermelho"
IND_GREEN = "Plástico verde"
IND_BLUE = "Plástico azul"
STITCH = ACCENT
SWITCH_BUTTON = "Plástico cinza"
MIRROR_GLASS = "Espelho do retrovisor"
AMBER_PLASTIC = "Plástico âmbar"


def add(c, hp: Hardpoints):
    if MERCOSUL_BLUE not in c.extra_materials:
        c.material(MERCOSUL_BLUE, (18, 54, 140), "Plastic", "Satin", 0)
    if AMBER_PLASTIC not in c.extra_materials:
        c.material(AMBER_PLASTIC, (232, 128, 24), "Plastic", "Glossy", 0)
    if MIRROR_GLASS not in c.extra_materials:  # silvered glass with a cool tint, darker than the chrome round it
        c.material(MIRROR_GLASS, (150, 166, 182), "Metal", "Polished", 0)
    bb = backbone_curve(hp)
    tk = TankShape(hp, bb)
    tank(c, hp, tk)
    st = SeatShape(hp, bb)
    seat(c, hp, st)
    underseat(c, hp)
    rear_fender(c, hp)
    tail(c, hp)
    forward_controls(c, hp)
    dense = bar_curve(hp)
    handlebar(c, hp, dense)
    headlight(c, hp)
    speedometer(c, hp)
    front_fender(c, hp)
    cables(c, hp, dense)
    plan_symbols(c, hp, dense)


# --- small helpers ---------------------------------------------------------------------------------------


def pw(v, e):
    return abs(v) ** e


def curve(ctrl, per=8):
    """z(y) through the control points [(y, z), ...] (Catmull-Rom, then linear)."""
    pts = catmull([(y, z, 0.0) for y, z in ctrl], per)
    ys = [p[0] for p in pts]
    zs = [p[1] for p in pts]

    def f(y):
        if y <= ys[0]:
            return zs[0]
        if y >= ys[-1]:
            return zs[-1]
        lo, hi = 0, len(ys) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if ys[mid] <= y:
                lo = mid
            else:
                hi = mid
        t = (y - ys[lo]) / (ys[hi] - ys[lo]) if ys[hi] > ys[lo] else 0.0
        return zs[lo] + (zs[hi] - zs[lo]) * t
    return f


def backbone_curve(hp):
    return curve([(p[1], p[2]) for p in hp.BACKBONE], 8)


def end_round(u, uf, ur, floor=0.025):
    """1 in the middle, falling to `floor` at u = 0 and u = 1 along quarter ellipses (rounded ends)."""
    ef = 1.0 if u >= uf else math.sqrt(max(0.0, 1 - (1 - u / uf) ** 2))
    er = 1.0 if 1 - u >= ur else math.sqrt(max(0.0, 1 - (1 - (1 - u) / ur) ** 2))
    return max(floor, ef * er)


def cos_spacing(n):
    return [0.5 - 0.5 * math.cos(math.pi * i / (n - 1)) for i in range(n)]


def make_consistent(m: Mesh):
    """Flip faces so that neighbours agree (shared edges run opposite ways), then turn the whole outwards."""
    edge_faces = defaultdict(list)
    for fi, f in enumerate(m.f):
        for k in range(len(f)):
            a, b = f[k], f[(k + 1) % len(f)]
            edge_faces[(min(a, b), max(a, b))].append(fi)
    seen = [False] * len(m.f)
    for start in range(len(m.f)):
        if seen[start]:
            continue
        seen[start] = True
        dq = deque([start])
        while dq:
            fi = dq.popleft()
            f = m.f[fi]
            for k in range(len(f)):
                a, b = f[k], f[(k + 1) % len(f)]
                for fj in edge_faces[(min(a, b), max(a, b))]:
                    if fj == fi or seen[fj]:
                        continue
                    g = m.f[fj]
                    if any(g[t] == a and g[(t + 1) % len(g)] == b for t in range(len(g))):
                        m.f[fj] = list(reversed(g))
                    seen[fj] = True
                    dq.append(fj)
    m.orient(0)


def zipper(A, fa, B, fb):
    """Triangles filling the band between two chains of vertex ids (same start rung, same end rung)."""
    i = j = 0
    tris = []
    while i < len(A) - 1 or j < len(B) - 1:
        if j == len(B) - 1 or (i < len(A) - 1 and fa[i + 1] <= fb[j + 1]):
            tris.append([A[i], A[i + 1], B[j]])
            i += 1
        else:
            tris.append([A[i], B[j + 1], B[j]])
            j += 1
    return tris


def fractions(points):
    d = [0.0]
    for p, q in zip(points, points[1:]):
        d.append(d[-1] + v_len(v_sub(q, p)))
    return [x / d[-1] if d[-1] > 0 else 0.0 for x in d]


def mesh_piece(c, name, m: Mesh, material, detail=FULL, in_plan=False):
    c.mesh_vertices += len(m.v)
    c._add(name, m.shape(4), material, detail, in_plan, False)


def loft(sections, caps="fan"):
    """A closed mesh through closed sections (same point count): quads between them, end caps."""
    m = Mesh()
    rows = [[m.vtx(p) for p in sec] for sec in sections]
    for r1, r2 in zip(rows, rows[1:]):
        n = len(r1)
        for i in range(n):
            m.poly([r1[i], r1[(i + 1) % n], r2[(i + 1) % n], r2[i]])
    if caps == "fan":
        for row in (rows[0], rows[-1]):
            cx = [sum(m.v[i][k] for i in row) / len(row) for k in range(3)]
            cc = m.vtx(cx)
            for i in range(len(row)):
                m.poly([cc, row[i], row[(i + 1) % len(row)]])
    make_consistent(m)
    return m, rows


def frame_at(t):
    """(t, forward, up) frame for a part along the direction t: forward is horizontal-ish towards -Y."""
    t = v_norm(t)
    f0 = (0.0, -1.0, 0.0)
    f = v_norm(v_sub(f0, v_mul(t, v_dot(f0, t))))
    up = v_norm(v_cross(f, t))
    if up[2] < 0:
        up = v_mul(up, -1.0)
    return t, f, up


def lp(o, frame, a, b, cc):
    t, f, up = frame
    return v_add(o, v_add(v_mul(t, a), v_add(v_mul(f, b), v_mul(up, cc))))


def stadium(cu, cv, w, h):
    """A rounded slot (u across w, v across h) as an engine outline with arcs."""
    r = h / 2
    a = w / 2 - r
    return [(cu - a, cv - r), (cu + a, cv - r, r), (cu + a, cv + r), (cu - a, cv + r, r)]


def rev_plan(c, name, axis_x, z, profile, material, detail=FULL, in_plan=False):
    """A round part whose axis runs along Y (lights facing back): profile [(r, y), ...] turned about the line x = axis_x, z."""
    c.rev(name, "Plan", [(axis_x + r, y) for r, y in profile], z, axis_x, material, detail=detail, in_plan=in_plan)


def rev_up(c, name, x0, y0, profile, material, detail=FULL, in_plan=False):
    """A round part with a vertical axis through (x0, y0): profile [(r, z), ...]."""
    c.rev(name, "Front", [(x0 + r, z) for r, z in profile], y0, x0, material, detail=detail, in_plan=in_plan)


# --- fuel tank --------------------------------------------------------------------------------------------

T_Y0, T_Y1 = -0.333, 0.088
T_TW = 0.034  # half width of the tunnel over the backbone (r 0.0254)
T_SPLIT, T_P = 0.72, 2.6
T_TOP = [(-0.333, 0.962), (-0.27, 1.000), (-0.19, 1.026), (-0.10, 1.027), (-0.02, 1.002), (0.04, 0.958), (0.088, 0.905)]
T_HALF = [(-0.333, 0.080), (-0.27, 0.118), (-0.19, 0.145), (-0.11, 0.148), (-0.03, 0.136), (0.03, 0.112), (0.088, 0.086)]
T_LIP = [(-0.333, 0.875), (-0.26, 0.842), (-0.17, 0.815), (-0.08, 0.800), (0.0, 0.791), (0.088, 0.783)]
S_OUT = [0.0, 0.07, 0.14, 0.22, 0.30, 0.38, 0.46, 0.54, 0.62, 0.72, 0.82, 0.92, 1.0]
F_IN = [0.0, 0.3, 0.55, 0.75, 0.9, 1.0]


class TankShape:
    """The teardrop tank as a function of y (front to back) and s (round the right half: 0 top centre .. 1 the lip)."""

    def __init__(self, hp, bb):
        self.bb = bb
        self.top, self.half, self.lip = curve(T_TOP), curve(T_HALF), curve(T_LIP)

    def u(self, y):
        return (y - T_Y0) / (T_Y1 - T_Y0)

    def params(self, y):
        e = end_round(self.u(y), 0.17, 0.15)
        slope = (self.bb(y + 0.004) - self.bb(y - 0.004)) / 0.008
        roof = self.bb(y) + 0.0254 * math.sqrt(1 + slope * slope) + 0.004
        top = roof + (self.top(y) - roof) * e ** 0.65
        xl = T_TW + 0.013
        a = xl + (self.half(y) - xl) * e ** 0.85
        lip = roof - (roof - self.lip(y)) * e ** 0.5
        zm = lip + 0.42 * (top - lip)
        return roof, top, a, xl, lip, zm

    def outer(self, y, s):
        roof, top, a, xl, lip, zm = self.params(y)
        if s <= T_SPLIT:
            th = math.radians(90.0 * s / T_SPLIT)
            return (a * pw(math.sin(th), 2 / T_P), y, zm + (top - zm) * pw(math.cos(th), 2 / T_P))
        be = math.radians(90.0 * (s - T_SPLIT) / (1 - T_SPLIT))
        return (xl + (a - xl) * math.cos(be), y, zm - (zm - lip) * math.sin(be))

    def inner(self, y, f):
        roof, top, a, xl, lip, zm = self.params(y)
        ps = math.radians(90.0 * f)
        return (T_TW * pw(math.sin(ps), 0.5), y, lip + (roof - lip) * pw(math.cos(ps), 0.5))

    def normal(self, y, s):
        """Outward normal of the right half's outer skin at (y, s)."""
        p0 = self.outer(y, s)
        ds = 0.004 if s < 0.996 else -0.004
        dy = 0.002
        ps = self.outer(y, s + ds)
        py = self.outer(y + dy, s)
        n = v_norm(v_cross(v_sub(py, p0), v_sub(ps, p0)))
        if ds < 0:
            n = v_mul(n, -1.0)
        if n[0] < 0 and s > 0.05:
            n = v_mul(n, -1.0)
        if s <= 0.05 and n[2] < 0:
            n = v_mul(n, -1.0)
        return n

    def section(self, y):
        mxp = lambda p: (-p[0], p[1], p[2])  # noqa: E731
        right_o = [self.outer(y, s) for s in S_OUT]
        right_i = [self.inner(y, f) for f in F_IN]
        return right_o + right_i[::-1] + [mxp(p) for p in right_i[1:]] + [mxp(p) for p in right_o[:0:-1]]


def tank_mesh(tk: TankShape, n_sec=18):
    ys = [T_Y0 + (T_Y1 - T_Y0) * u for u in cos_spacing(n_sec)]
    m = Mesh()
    rows = [[m.vtx(p) for p in tk.section(y)] for y in ys]
    for r1, r2 in zip(rows, rows[1:]):
        n = len(r1)
        for i in range(n):
            m.poly([r1[i], r1[(i + 1) % n], r2[(i + 1) % n], r2[i]])
    no, ni = len(S_OUT), len(F_IN)
    for row, y in ((rows[0], ys[0]), (rows[-1], ys[-1])):
        sec = tk.section(y)
        A = [row[k] for k in range(no)]  # right outer, top centre -> lip
        B = [row[no + ni - 1 - j] for j in range(ni)]  # right inner, roof centre -> lip
        fa = fractions([sec[k] for k in range(no)])
        fb = fractions([sec[no + ni - 1 - j] for j in range(ni)])
        for t in zipper(A, fa, B, fb):
            m.poly(t)
        total = len(row)
        A2 = [row[0]] + [row[total - k] for k in range(1, no)]  # left outer
        B2 = [row[no + ni - 1]] + [row[no + ni - 1 + j] for j in range(1, ni)]  # left inner
        for t in zipper(A2, fa, B2, fb):
            m.poly(t)
    make_consistent(m)
    return m


def scallop(t, hw):
    """Half width (in s) of the side panel at t in 0..1: round front, pointed rear."""
    if t <= 0.0 or t >= 1.0:
        return 0.0
    k = 0.2
    f = math.sqrt(max(0.0, 1 - (1 - t / k) ** 2)) if t < k else 1.0
    g = ((1 - t) / (1 - k)) ** 0.85 if t > k else 1.0
    return hw * f * g


def panel_mesh(tk: TankShape, u0, u1, sm, hw, lift_out=0.0009, lift_in=0.0001, nu=16, nj=5, side=1):
    rows = []
    for i in range(nu):
        t = i / (nu - 1)
        y = T_Y0 + (T_Y1 - T_Y0) * (u0 + (u1 - u0) * t)
        h = scallop(t, hw)
        s_mid = sm + 0.05 * t
        top, bot = [], []
        for j in range(nj):
            s = s_mid - h + 2 * h * j / (nj - 1)
            p = tk.outer(y, s)
            n = tk.normal(y, s)
            top.append(v_add(p, v_mul(n, lift_out)))
            bot.append(v_add(p, v_mul(n, lift_in)))
        sec = top + bot[::-1]
        if side < 0:
            sec = [(-p[0], p[1], p[2]) for p in sec]
        rows.append(sec)
    m = Mesh()
    ids = [[m.vtx(p) for p in sec] for sec in rows]
    for r1, r2 in zip(ids, ids[1:]):
        n = len(r1)
        for i in range(n):
            m.poly([r1[i], r1[(i + 1) % n], r2[(i + 1) % n], r2[i]])
    m.poly(ids[0])
    m.poly(ids[-1])
    make_consistent(m)
    return m


def stripe_path(tk: TankShape, u0, u1, sm, hw, lift=0.0006, n=26, side=1):
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        y = T_Y0 + (T_Y1 - T_Y0) * (u0 + (u1 - u0) * t)
        h = scallop(t, hw)
        s_mid = sm + 0.05 * t
        for s, out in ((s_mid - h, top), (s_mid + h, bot)):
            p = v_add(tk.outer(y, s), v_mul(tk.normal(y, s), lift))
            out.append(p if side > 0 else (-p[0], p[1], p[2]))
    return top + bot[-2:0:-1]


def tank(c, hp, tk: TankShape):
    m = tank_mesh(tk)
    mesh_piece(c, "Tanque de combustível", m, TANK_PAINT, ALL, in_plan=True)
    # Two-tone: a black scallop on each flank, outlined by a gold pinstripe.
    u0, u1, sm, hw = 0.12, 0.86, 0.40, 0.12
    for side, label in ((1, "esquerdo"), (-1, "direito")):
        mesh_piece(c, f"Painel lateral do tanque {label}", panel_mesh(tk, u0, u1, sm, hw, side=side), FRAME_BLACK, FULL)
        path = stripe_path(tk, u0 - 0.035, u1 + 0.07, sm, hw + 0.045, side=side)
        put(c, f"Filete do tanque {label}", sweep(path, circle2(0.0017, 6), closed=True), ACCENT, FINE, lua=True)
    # Centre stripe along the top.
    ys = [T_Y0 + (T_Y1 - T_Y0) * u for u in [0.10 + 0.78 * k / 20 for k in range(21)]]
    for dx, label in ((0.012, "esquerdo"), (-0.012, "direito")):
        pts = []
        for y in ys:
            p = tk.outer(y, 0.0)
            roof, top, a, xl, lip, zm = tk.params(y)
            s = (abs(dx) / a) ** (T_P / 2)
            s = math.degrees(math.asin(min(1.0, s))) / 90.0 * T_SPLIT
            q = tk.outer(y, s)
            pts.append((dx, y, q[2] + 0.0006))
        put(c, f"Filete superior do tanque {label}", sweep(pts, circle2(0.0015, 6)), ACCENT, FINE, lua=True)
    # Filler cap at the crown.
    yc = -0.165
    z0 = tk.outer(yc, 0.0)[2]
    rev_up(c, "Base do bocal do tanque", 0.0, yc, [(0, z0 - 0.006), (0.044, z0 - 0.006), (0.044, z0 - 0.001), (0.040, z0 + 0.003),
                                                   (0, z0 + 0.003)], CHROME, FULL)
    rev_up(c, "Tampa do tanque", 0.0, yc, [(0, z0), (0.036, z0), (0.037, z0 + 0.006), (0.034, z0 + 0.013), (0.024, z0 + 0.018),
                                           (0, z0 + 0.019)], CHROME, ALL)
    rev_up(c, "Botão da tampa do tanque", 0.0, yc, [(0, z0 + 0.017), (0.010, z0 + 0.017), (0.009, z0 + 0.022), (0, z0 + 0.023)],
           ACCENT, FINE)
    # Indicator lights in a chrome strip on the crown, ahead of the cap (neutral, high beam, turn, oil).
    yi = -0.236
    zi = tk.outer(yi, 0.0)[2]
    c.profile("Painel de luzes indicadoras", "Plan", stadium(0.0, yi, 0.092, 0.020), zi - 0.006, 0.0085, CHROME, FULL)
    for k, (mat, nm) in enumerate(((IND_GREEN, "neutro"), (IND_BLUE, "farol alto"), (LENS_AMBER, "pisca"), (NEEDLE, "óleo"))):
        x = -0.0285 + 0.019 * k
        rev_up(c, f"Luz indicadora ({nm})", x, yi, [(0, zi + 0.0015), (0.0058, zi + 0.0015), (0.0052, zi + 0.0048), (0.0030, zi + 0.0062),
                                                     (0, zi + 0.0066)], mat, FINE)
    # Petcock under the left flank, with its fuel line towards the carburettor (between the cylinders).
    yp = -0.045
    pc = tk.outer(yp, 0.93)
    xp, zp = pc[0] - 0.004, pc[2]
    rev_up(c, "Torneira de combustível", xp, yp, [(0, zp - 0.034), (0.010, zp - 0.034), (0.012, zp - 0.028), (0.012, zp - 0.008),
                                                  (0.016, zp - 0.006), (0.016, zp + 0.004), (0, zp + 0.004)], CHROME, FULL)
    nhex_x(c, "Porca da torneira", xp - 0.013, xp + 0.013, yp, zp - 0.003, 0.0095, CHROME, FINE)
    c.box("Alavanca da torneira", xp - 0.004, yp - 0.040, zp - 0.022, 0.008, 0.032, 0.007, BLACK_PLASTIC, detail=FINE)
    # (behind the head-steady link and above the coil, then down behind the intake to the float bowl)
    fuel = [(xp, yp, zp - 0.034), (xp - 0.004, yp - 0.008, zp - 0.056), (0.035, -0.070, 0.735), (0.0, -0.075, 0.738),
            (-0.060, -0.076, 0.728), (-0.090, -0.079, 0.690), (-0.091, -0.081, 0.625), (-0.094, -0.086, 0.585), (-0.104, -0.096, 0.570)]
    put(c, "Mangueira de combustível", sweep(catmull(fuel, 4), circle2(0.0045, 8)), RUBBER, FINE, lua=True)
    # Mounts: rubber-cushioned tabs either side of the backbone at the front, a bolted tab at the back.
    for s, label in ((1, "esquerda"), (-1, "direita")):
        y = -0.285
        zb = tk.bb(y)
        c.box(f"Orelha dianteira do tanque {label}", s * 0.0254 - (0.009 if s < 0 else 0), y - 0.015, zb - 0.012, 0.009, 0.030, 0.030,
              FRAME_BLACK, detail=FINE)
        ndisc_x(c, f"Coxim dianteiro do tanque {label}", s * 0.0254, s * 0.034, y, zb + 0.012, 0.009, RUBBER, FINE)
    yb = 0.082
    zb = tk.bb(yb) + 0.0254
    c.box("Orelha traseira do tanque", -0.018, yb - 0.004, zb - 0.002, 0.036, 0.026, 0.004, FRAME_BLACK, detail=FINE)
    rev_up(c, "Parafuso traseiro do tanque", 0.0, yb + 0.012, [(0, zb), (0.008, zb), (0.008, zb + 0.006), (0.005, zb + 0.008),
                                                                (0, zb + 0.008)], CHROME, FINE)


# --- seat ---------------------------------------------------------------------------------------------------

S_Y0, S_Y1 = 0.072, 0.478
S_TOP = [(0.072, 0.806), (0.10, 0.803), (0.13, 0.785), (0.17, 0.742), (0.21, 0.703), (0.25, 0.685), (0.30, 0.680), (0.35, 0.690),
         (0.40, 0.713), (0.44, 0.742), (0.465, 0.758), (0.478, 0.762)]
S_BOT = [(0.072, 0.792), (0.10, 0.787), (0.13, 0.760), (0.16, 0.715), (0.19, 0.674), (0.22, 0.653), (0.26, 0.637), (0.32, 0.629),
         (0.40, 0.627), (0.478, 0.629)]
S_HALF = [(0.072, 0.034), (0.10, 0.050), (0.14, 0.078), (0.19, 0.115), (0.24, 0.148), (0.30, 0.166), (0.36, 0.168), (0.41, 0.162),
          (0.45, 0.150), (0.478, 0.135)]
S_TH = [0, 12, 24, 36, 48, 60, 72, 84, 96, 110, 125, 140, 160, 180]


class SeatShape:
    def __init__(self, hp, bb):
        self.bb = bb
        self.top, self.bot, self.half = curve(S_TOP), curve(S_BOT), curve(S_HALF)
        self.j = hp.J

    def params(self, y):
        u = (y - S_Y0) / (S_Y1 - S_Y0)
        e = end_round(u, 0.10, 0.13, 0.03)
        zb = self.bot(y)
        if y < self.j[1]:
            slope = (self.bb(y + 0.004) - self.bb(y - 0.004)) / 0.008
            zb = max(zb, self.bb(y) + 0.0254 * math.sqrt(1 + slope * slope) + 0.003)
        if abs(y - self.j[1]) < 0.021:
            zb = max(zb, self.j[2] + math.sqrt(0.021 ** 2 - (y - self.j[1]) ** 2) + 0.003)
        zt = zb + (self.top(y) - zb) * e ** 0.6
        w = 0.010 + (self.half(y) - 0.010) * e ** 0.7
        zc = zb + 0.35 * (zt - zb)
        return zb, zt, w, zc

    def point(self, y, th):
        zb, zt, w, zc = self.params(y)
        t = math.radians(th)
        if th <= 90:
            return (w * pw(math.sin(t), 2 / 3.0), y, zc + (zt - zc) * pw(math.cos(t), 2 / 3.0))
        return (w * pw(math.sin(t), 0.25), y, zc - (zc - zb) * pw(math.cos(t), 0.25))

    def section(self, y):
        right = [self.point(y, th) for th in S_TH]
        return right + [(-p[0], p[1], p[2]) for p in right[-2:0:-1]]


def seat(c, hp, st: SeatShape):
    ys = [S_Y0 + (S_Y1 - S_Y0) * u for u in cos_spacing(18)]
    m, _ = loft([st.section(y) for y in ys])
    mesh_piece(c, "Banco", m, LEATHER, ALL, in_plan=True)
    # Pan under the cushion.
    secs = []
    for y in ys[1:-1]:
        zb, zt, w, zc = st.params(y)
        wp = w * 0.93
        secs.append([(wp, y, zb - 0.006), (wp, y, zb + 0.001), (-wp, y, zb + 0.001), (-wp, y, zb - 0.006)])
    m, _ = loft(secs)
    mesh_piece(c, "Base do banco", m, BLACK_PLASTIC, FULL)
    # Piping round the top panel and a stitch line inside it.

    def loop(th, lift):
        right, left = [], []
        for y in ys[1:-1]:
            zb, zt, w, zc = st.params(y)
            p = st.point(y, th)
            d = v_norm((p[0], 0.0, (p[2] - zc) * 3.0))
            q = v_add(p, v_mul(d, lift))
            right.append(q)
            left.append((-q[0], q[1], q[2]))
        return right + left[::-1]
    put(c, "Debrum do banco", sweep(loop(64, 0.0012), circle2(0.0035, 6), closed=True), LEATHER, FINE, lua=True)
    path = loop(50, 0.0004)
    dashes = []
    acc = 0.0
    for p, q in zip(path, path[1:] + path[:1]):
        seg = v_sub(q, p)
        length = v_len(seg)
        d = v_norm(seg)
        s = (0.006 - acc) if acc > 0 else 0.0
        while s + 0.007 <= length:
            ctr = v_add(p, v_mul(d, s + 0.0035))
            nrm = v_norm((ctr[0], 0.0, 1.0))
            side = v_norm(v_cross(nrm, d))
            dashes.append(box(ctr, (0.007, 0.0016, 0.0016), (d, side, v_norm(v_cross(d, side)))))
            s += 0.0115
        acc = s - length if s > length else 0.0
    put(c, "Costura do banco", dashes, STITCH, FINE, lua=True)
    # Rear mount: a bent tab to the seat rails' cross tube and a chrome knob.
    zb_r = st.params(0.455)[0]
    nprofile(c, "Orelha traseira do banco", "Side", [(0.440, zb_r - 0.006), (0.452, zb_r - 0.006), (0.500, 0.6125), (0.506, 0.6125),
                                                     (0.506, 0.6175), (0.497, 0.6175), (0.450, zb_r - 0.001), (0.440, zb_r - 0.001)],
             -0.018, 0.036, FRAME_BLACK, FULL)
    rev_up(c, "Botão de fixação do banco", 0.0, 0.497, [(0, 0.6175), (0.013, 0.6175), (0.014, 0.625), (0.011, 0.632), (0, 0.633)],
           CHROME, FINE)
    # Front tongue under the tank.
    c.box("Lingueta do banco", -0.012, 0.055, st.params(0.08)[0] - 0.004, 0.024, 0.035, 0.003, FRAME_BLACK, detail=FINE)


# --- under the seat: oil tank, battery, side covers -------------------------------------------------------------


def rrect_pts(u0, v0, u1, v1, r):
    return [(u0 + r, v0), (u1 - r, v0, r), (u1, v0 + r), (u1, v1 - r, r), (u1 - r, v1), (u0 + r, v1, r), (u0, v1 - r), (u0, v0 + r, r)]


def underseat(c, hp):
    z0, z1 = 0.452, 0.566
    c.profile("Tanque de óleo", "Plan", rrect_pts(-0.092, 0.292, 0.092, 0.402, 0.028), z0, z1 - z0, FRAME_BLACK, ALL)
    c.profile("Cinta do tanque de óleo", "Plan", rrect_pts(-0.094, 0.335, 0.094, 0.360, 0.008), z0 + 0.03, 0.018, CHROME, FINE)
    rev_up(c, "Gargalo do tanque de óleo", -0.060, 0.318, [(0, z1 - 0.002), (0.011, z1 - 0.002), (0.011, 0.588), (0, 0.588)], CHROME, FULL)
    rev_up(c, "Tampa do tanque de óleo", -0.060, 0.318, [(0, 0.586), (0.017, 0.586), (0.017, 0.594), (0.012, 0.600), (0, 0.601)],
           CHROME, FULL)
    c.box("Bateria", -0.070, 0.408, 0.462, 0.140, 0.050, 0.092, ENGINE_BLACK, detail=FULL)
    for s, label, mat in ((1, "positivo", NEEDLE), (-1, "negativo", BLACK_PLASTIC)):
        rev_up(c, f"Polo {label} da bateria", s * 0.045, 0.433, [(0, 0.553), (0.007, 0.553), (0.006, 0.562), (0, 0.562)], mat, FINE)
    c.box("Cinta da bateria", -0.072, 0.427, 0.460, 0.144, 0.012, 0.095, RUBBER, detail=FINE)
    # Oil lines: the engine's feed and return lines end at (x -0.072 / -0.088, y 0.284, z 0.304); from there up in
    # front of the swingarm pivot tube to two fittings on the tank's front face.
    for k, x in enumerate((-0.072, -0.088)):
        zf = 0.470 + 0.020 * k
        pts = [(x, 0.284, 0.304), (x, 0.2745, 0.345), (x, 0.2745, 0.420), (x, 0.280, zf - 0.008), (x, 0.287, zf)]  # clear of the pivot tube
        put(c, f"Mangueira de óleo {('de alimentação', 'de retorno')[k]}", sweep(catmull(pts, 4), circle2(0.0055, 8)), RUBBER, FINE,
            lua=True)
        c.cyl_y(f"Conexão do tanque de óleo {k + 1}", x, zf, 0.282, 0.0075, 0.010, CHROME, detail=FINE)
    # Side covers (painted like the tank): a pressed panel with a rolled edge rising to a low dome, a chrome bolt in
    # its middle. Layers of engine Blends from the outline inwards (each a ring of the cover's section).
    corners = [(0.286, 0.452, 0.030), (0.410, 0.440, 0.040), (0.466, 0.590, 0.016), (0.268, 0.597, 0.022)]
    outline = ccw(fillet(corners, 6))
    x_in = 0.158
    #           (inset from, inset to, rise): the rolled edge, then the dome's flanks and crown
    layers = [(0.0, 0.0015, 0.0030), (0.0015, 0.0055, 0.0030), (0.0055, 0.016, 0.0040), (0.016, 0.034, 0.0030)]
    for s, label in ((1, "esquerda"), (-1, "direita")):
        nprofile(c, f"Tampa lateral {label}", "Side", outline, x_in if s > 0 else -x_in - 0.003, 0.003, TANK_PAINT, ALL)
        x = x_in + 0.003
        for k, (a, b, rise) in enumerate(layers):
            lo, hi = (inset(outline, a) if a else outline), inset(outline, b)
            if s > 0:
                nblend(c, f"Tampa lateral {label} {k + 1}", "Side", lo, hi, x, rise, TANK_PAINT, FULL)
            else:
                nblend(c, f"Tampa lateral {label} {k + 1}", "Side", hi, lo, -x - rise, rise, TANK_PAINT, FULL)
            x += rise
        top = inset(outline, layers[-1][1])
        nprofile(c, f"Topo da tampa lateral {label}", "Side", top, x - 0.0005 if s > 0 else -x - 0.0005, 0.001, TANK_PAINT, FULL)
        ndisc_x(c, f"Parafuso da tampa lateral {label}", s * (x - 0.001), s * (x + 0.005), 0.365, 0.52, 0.0075, CHROME, FINE)
        nprofile(c, f"Suporte da tampa lateral {label}", "Side", circles_hull([(0.365, 0.52, 0.012), (0.34, 0.585, 0.008)], n=12),
                 0.142 if s > 0 else -0.160, 0.018, FRAME_BLACK, FINE)


# --- rear fender, lights and plate --------------------------------------------------------------------------------


def arc_path(cy, cz, R, psi0, psi1, nseg):
    """A path of arcs round (cy, cz) from psi0 to psi1 (degrees from +y towards +z; counter-clockwise if psi1 > psi0)."""
    out = []
    for k in range(nseg + 1):
        t = math.radians(psi0 + (psi1 - psi0) * k / nseg)
        p = (cy + R * math.cos(t), cz + R * math.sin(t))
        out.append(p + ((R,) if k < nseg else ()))
    return out


def fender_section(W, C, t, bead=0.0022, n=9, power=3.0):
    """Closed (d, x) section of a fender: d outwards from the inner radius at the centre; edges curl in by C."""
    xs = [-W + 2 * W * k / (n - 1) for k in range(n)]

    def din(x):
        return -C * (abs(x) / W) ** power
    outer = [(din(x) + t, x) for x in xs]
    inner = [(din(x), x) for x in reversed(xs)]
    e = din(W)
    return (outer + [(e + t * 0.5 - 0.0005, W + bead)] + inner + [(e + t * 0.5 - 0.0005, -W - bead)])


def rear_fender(c, hp):
    ra = hp.REAR_AXLE
    R = hp.FENDER_R_INNER
    W = hp.FENDER_R_HALF_W
    sec = fender_section(W, 0.032, 0.003, n=11)
    path = arc_path(ra[1], ra[2], R, -2.0, 145.0, 3)
    nsweep(c, "Para-lama traseiro", "Side", path, 0.0, [(-d, x) for d, x in sec], TANK_PAINT, ALL, in_plan=True)
    # Struts on the fender's sides up to the seat rails.
    rs = R - 0.022
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        xs = s * (W + 0.0065)
        strut = arc_path(ra[1], ra[2], rs, 14.0, 100.0, 2)
        nsweep(c, f"Suporte do para-lama {label}", "Side", strut, xs, [(-0.010, -0.003), (0.010, -0.003), (0.010, 0.003), (-0.010, 0.003)],
               CHROME, FULL)
        for psi in (80.0,):
            t = math.radians(psi)
            p0 = (ra[1] + rs * math.cos(t), ra[2] + rs * math.sin(t))
            rail = (0.90, 0.708)
            nprofile(c, f"Orelha do suporte do para-lama {label}", "Side",
                     circles_hull([(p0[0], p0[1], 0.010), (rail[0], rail[1] - 0.004, 0.012)], n=12), xs - 0.003, 0.006, CHROME, FULL)
        for k, psi in enumerate((22.0, 52.0, 90.0)):
            t = math.radians(psi)
            y, z = ra[1] + rs * math.cos(t), ra[2] + rs * math.sin(t)
            ndisc_x(c, f"Parafuso do suporte do para-lama {label} {k + 1}", s * (W - 0.002), s * (W + 0.0125), y, z, 0.0055, CHROME, FINE)


def tail(c, hp):
    ra = hp.REAR_AXLE
    Ro = hp.FENDER_R_INNER + 0.003
    ty, tz = hp.TAIL_LIGHT[1], hp.TAIL_LIGHT[2]

    def on_fender(y):
        return ra[2] + math.sqrt(Ro ** 2 - (y - ra[1]) ** 2)
    # Tail light: chrome housing (an oval facing back), bezel and red lens; pedestal to the fender.
    y0, y1 = ty - 0.024, ty + 0.016
    c.profile("Corpo da lanterna traseira", "Front", stadium(0.0, tz, 0.124, 0.046), y0, y1 - y0, CHROME, ALL)
    c.profile("Aro da lanterna traseira", "Front", stadium(0.0, tz, 0.118, 0.040), y1, 0.004, CHROME, FULL)
    c.profile("Lente da lanterna traseira", "Front", stadium(0.0, tz, 0.108, 0.031), y1, 0.011, LENS_RED, ALL)
    c.profile("Refletor da lanterna traseira", "Front", stadium(0.0, tz, 0.100, 0.025), y1 - 0.001, 0.008, NEEDLE, FULL)
    fz0, fz1 = on_fender(y0 + 0.004), on_fender(y1 - 0.006)
    nprofile(c, "Pé da lanterna traseira", "Side", [(y0 + 0.004, fz0 - 0.004), (y1 - 0.006, fz1 - 0.004), (y1 - 0.010, tz - 0.012),
                                                     (y0 + 0.010, tz - 0.012)], -0.016, 0.032, CHROME, FULL)
    # Plate holder, Mercosul plate (blank, 200 x 170 mm), plate light, reflectors.
    py = hp.PLATE[1]
    pz0, pz1 = hp.PLATE[2] - 0.085, hp.PLATE[2] + 0.085
    c.box("Suporte da placa", -0.106, py - 0.005, pz0 - 0.006, 0.212, 0.005, pz1 - pz0 + 0.050, FRAME_BLACK, detail=ALL)
    c.box("Placa", -0.100, py, pz0, 0.200, 0.0012, pz1 - pz0, PLATE_WHITE, detail=ALL)
    c.box("Faixa azul da placa", -0.100, py + 0.0012, pz1 - 0.030, 0.200, 0.0004, 0.030, MERCOSUL_BLUE, detail=FULL)
    for i, (x, z) in enumerate(((-0.08, pz0 + 0.012), (0.08, pz0 + 0.012), (-0.08, pz1 - 0.044), (0.08, pz1 - 0.044))):
        rev_plan(c, f"Parafuso da placa {i + 1}", x, z, [(0, py + 0.0012), (0.0055, py + 0.0012), (0.0045, py + 0.0042), (0, py + 0.005)],
                 CHROME, FINE)
    # bracket from the fender's back to the holder
    pts = []
    for psi in (40.0, 52.0):
        t = math.radians(psi)
        pts.append((ra[1] + (Ro - 0.004) * math.cos(t), ra[2] + (Ro - 0.004) * math.sin(t)))
    nprofile(c, "Braço do suporte da placa", "Side", [pts[0], (py - 0.004, 0.596), (py - 0.004, 0.640), pts[1]], -0.028, 0.056,
             FRAME_BLACK, FULL)
    hood = [(py - 0.004, pz1 + 0.006), (py + 0.022, pz1 + 0.006), (py + 0.022, pz1 + 0.012, 0.018), (py + 0.004, pz1 + 0.030),
            (py - 0.004, pz1 + 0.030)]
    nprofile(c, "Luz da placa", "Side", hood, -0.034, 0.068, CHROME, FULL)
    c.box("Lente da luz da placa", -0.028, py + 0.002, pz1 + 0.002, 0.056, 0.018, 0.004, LENS_CLEAR, detail=FINE)
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        rev_plan(c, f"Refletor traseiro {label}", s * 0.072, pz1 + 0.022, [(0, py), (0.019, py), (0.019, py + 0.004), (0.016, py + 0.007),
                                                                            (0, py + 0.007)], NEEDLE, FULL)
    # Rear turn signals on stalks from the frame's rear loop.
    sy, sz = 0.935, 0.714
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        ax = s * 0.224
        ndisc_x(c, f"Haste do pisca traseiro {label}", s * 0.136, s * 0.208, sy + 0.010, sz, 0.0055, CHROME, FULL)
        rev_plan(c, f"Corpo do pisca traseiro {label}", ax, sz, [(0, sy - 0.022), (0.010, sy - 0.021), (0.018, sy - 0.012), (0.021, sy + 0.004),
                                                                 (0.021, sy + 0.028), (0, sy + 0.028)], CHROME, FULL)
        rev_plan(c, f"Fundo do pisca traseiro {label}", ax, sz, [(0, sy + 0.027), (0.0195, sy + 0.027), (0.0195, sy + 0.0305), (0, sy + 0.0305)],
                 AMBER_PLASTIC, FINE)
        rev_plan(c, f"Lente do pisca traseiro {label}", ax, sz, [(0, sy + 0.029), (0.0195, sy + 0.029), (0.018, sy + 0.038), (0.012, sy + 0.044),
                                                                 (0, sy + 0.046)], LENS_AMBER, FULL)


# --- forward controls ------------------------------------------------------------------------------------------------


def ribbed_x(x0, x1, r_core, r_rib, pitch, y, z, end_r=None):
    """A ribbed rubber cylinder along X from x0 to x1 (|x1| > |x0|) at (y, z), as a lathe profile."""
    s = 1.0 if x1 > x0 else -1.0
    length = abs(x1 - x0)
    prof = [(0.0, 0.0), (r_core, 0.0)]
    h = 0.003
    while h + pitch <= length - 0.003:
        prof += [(r_rib, h + 0.15 * pitch), (r_rib, h + 0.5 * pitch), (r_core, h + 0.65 * pitch), (r_core, h + pitch)]
        h += pitch
    er = end_r if end_r is not None else r_core
    prof += [(er, length - 0.002), (er * 0.8, length), (0.0, length)]
    return lathe(prof, (x0, y, z), (s, 0.0, 0.0), n=14)


def forward_controls(c, hp):
    py, pz = hp.PEG_L[1], hp.PEG_L[2]
    my, mz = hp.PEG_MOUNT_L[1], hp.PEG_MOUNT_L[2]
    pad = {1: (-0.475, 0.385), -1: (-0.485, 0.372)}
    low = {1: (-0.372, 0.272), -1: (-0.410, 0.275)}
    for s, label in ((1, "esquerda"), (-1, "direita")):
        def xo(a, b):  # an x span on this side: (offset, depth) for a Side-plane profile
            lo, hi = sorted((s * a, s * b))
            return lo, hi - lo
        plate = circles_hull([(my, mz, 0.021), (py, pz, 0.019)], n=16)
        o, d = xo(0.168, 0.177)
        nprofile(c, f"Suporte do comando avançado {label}", "Side", plate, o, d, POLISHED_AL, FULL)
        for k, z in enumerate((mz - 0.011, mz + 0.011)):
            nhex_x(c, f"Parafuso do suporte do comando {label} {k + 1}", s * 0.177, s * 0.183, my, z, 0.0068, CHROME, FINE)
        ndisc_x(c, f"Eixo do comando avançado {label}", s * 0.177, s * 0.250, py, pz, 0.0095, CHROME, ALL)
        # Peg: chrome core and end cap, ribbed rubber (plain at medium).
        # (the core at every level, so the peg draws in the plan; the fine ribbed rubber in the script wraps it)
        ndisc_x(c, f"Pedaleira {label}", s * 0.246, s * 0.364, py, pz, 0.0148, RUBBER, ALL, in_plan=True)
        put(c, f"Borracha da pedaleira {label}", ribbed_x(s * 0.246, s * 0.364, 0.0150, 0.0168, 0.0075, py, pz), RUBBER, FINE, lua=True)
        ndisc_x(c, f"Ponteira da pedaleira {label}", s * 0.364, s * 0.371, py, pz, 0.0125, CHROME, FULL)
        ndisc_x(c, f"Garfo da pedaleira {label}", s * 0.238, s * 0.250, py, pz, 0.017, CHROME, FULL)
        # Lever (brake pedal on the right, shifter on the left): hub, arm to the pad, lower arm to the linkage.
        ndisc_x(c, f"Cubo do {'câmbio' if s > 0 else 'pedal de freio'}", s * 0.206, s * 0.236, py, pz, 0.0175, POLISHED_AL, FULL)
        o, d = xo(0.214, 0.228)
        pyy, pzz = pad[s]
        nprofile(c, f"Braço do {'câmbio' if s > 0 else 'pedal de freio'}", "Side",
                 circles_hull([(py, pz, 0.0145), (pyy, pzz, 0.0105)], n=16), o, d, POLISHED_AL, FULL)
        ly, lz = low[s]
        nprofile(c, f"Braço inferior do {'câmbio' if s > 0 else 'pedal de freio'}", "Side",
                 circles_hull([(py, pz, 0.012), (ly, lz, 0.0085)], n=14), o, d, POLISHED_AL, FULL)
        if s > 0:
            ndisc_x(c, "Pino do câmbio", 0.214, 0.232, pyy, pzz, 0.0065, CHROME, FULL)
            ndisc_x(c, "Pedaleira do câmbio", 0.232, 0.300, pyy, pzz, 0.0118, RUBBER, "cm")
            put(c, "Borracha da pedaleira do câmbio", ribbed_x(0.232, 0.300, 0.0112, 0.0128, 0.0070, pyy, pzz), RUBBER, FINE, lua=True)
        else:
            ndisc_x(c, "Pino do pedal de freio", -0.232, -0.214, pyy, pzz, 0.0075, CHROME, FULL)
            ndisc_x(c, "Sapata do pedal de freio", -0.330, -0.232, pyy, pzz, 0.0170, RUBBER, "cm")
            put(c, "Borracha do pedal de freio", ribbed_x(-0.232, -0.330, 0.0162, 0.0180, 0.0075, pyy, pzz), RUBBER, FINE, lua=True)
            ndisc_x(c, "Ponteira do pedal de freio", -0.337, -0.330, pyy, pzz, 0.0140, CHROME, FULL)
    # Left: shift rod back to the gearbox's shift lever (on its shaft at the primary's front).
    ly, lz = low[1]
    rx = 0.238
    ndisc_x(c, "Olhal dianteiro da vareta do câmbio", 0.228, 0.246, ly, lz, 0.0085, CHROME, FULL)
    shaft = (-0.195, 0.228)
    lever_top = (-0.208, lz)
    ncyl_side(c, "Vareta do câmbio", (rx, ly, lz), (rx, lever_top[0], lz), 0.0045, CHROME, FULL)
    ndisc_x(c, "Olhal traseiro da vareta do câmbio", 0.228, 0.246, lever_top[0], lz, 0.0085, CHROME, FULL)
    ndisc_x(c, "Eixo seletor do câmbio", 0.098, 0.230, shaft[0], shaft[1], 0.0085, CHROME, FULL)  # out of the crankcase
    nprofile(c, "Alavanca seletora do câmbio", "Side", circles_hull([(shaft[0], shaft[1], 0.012), (lever_top[0], lz, 0.0085)], n=14),
             0.214, 0.014, POLISHED_AL, FULL)
    for k, (yy, zz) in enumerate(((ly, lz), lever_top)):
        nhex_x(c, f"Parafuso da vareta do câmbio {k + 1}", 0.246, 0.253, yy, zz, 0.0065, CHROME, FINE)
    nhex_x(c, "Parafuso do eixo seletor", 0.230, 0.236, shaft[0], shaft[1], 0.0075, CHROME, FINE)
    # Right: rear brake master cylinder behind the lower arm, pushrod, reservoir, banjo to the chassis hose.
    ly, lz = low[-1]
    mx_, mz_ = -0.205, 0.275
    ncyl_side(c, "Cilindro mestre traseiro", (mx_, -0.398, mz_), (mx_, -0.338, mz_), 0.012, POLISHED_AL, FULL)
    ncyl_side(c, "Haste do cilindro mestre traseiro", (mx_, ly, mz_), (mx_, -0.398, mz_), 0.0042, CHROME, FULL)
    ndisc_x(c, "Garfo da haste do freio", -0.232, -0.200, ly, lz, 0.0068, CHROME, FULL)
    c.box("Suporte do cilindro mestre traseiro", -0.196, -0.375, mz_ - 0.010, 0.020, 0.024, 0.020, POLISHED_AL, detail=FULL)
    rev_up(c, "Reservatório do freio traseiro", mx_, -0.352, [(0, mz_ + 0.006), (0.0105, mz_ + 0.006), (0.0105, mz_ + 0.028),
                                                             (0, mz_ + 0.028)], LENS_CLEAR, FULL)
    rev_up(c, "Tampa do reservatório traseiro", mx_, -0.352, [(0, mz_ + 0.027), (0.012, mz_ + 0.027), (0.012, mz_ + 0.034),
                                                             (0, mz_ + 0.035)], CHROME, FINE)
    hose_end = (-0.17, -0.33, 0.30)
    put(c, "Conexão do freio traseiro", sweep([(mx_ + 0.004, -0.336, mz_ + 0.004), (-0.188, -0.333, mz_ + 0.014), hose_end],
                                               circle2(0.0060, 8)), CHROME, FINE, lua=True)


# --- handlebar and its controls (steered) -----------------------------------------------------------------------------


def bar_curve(hp):
    """The bar's centre line: Catmull-Rom through HANDLEBAR, straight along both grip spans."""
    H = hp.HANDLEBAR
    per = 6
    dense = catmull(H, per)
    for k in range(1, per):
        dense[k] = v_lerp(H[0], H[1], k / per)
        dense[-1 - k] = v_lerp(H[-1], H[-2], k / per)
    return dense


def bar_at(dense, s, xa):
    """(point, unit tangent towards the bar end) of the bar's centre line at |x| = xa on side s (+1 left)."""
    pts = [p for p in dense if s * p[0] >= -1e-9]
    pts.sort(key=lambda p: s * p[0])
    for p, q in zip(pts, pts[1:]):
        if s * p[0] <= xa <= s * q[0]:
            t = (xa - s * p[0]) / (s * q[0] - s * p[0])
            return v_lerp(p, q, t), v_norm(v_sub(q, p))
    return pts[-1], v_norm(v_sub(pts[-1], pts[-2]))


def grip_profile(a0, a1, r_core=0.0163, r_rib=0.0176, pitch=0.007):
    prof = [(0.0, a0), (0.0215, a0), (0.0215, a0 + 0.004), (0.0180, a0 + 0.007)]
    h = a0 + 0.009
    while h + pitch <= a1 - 0.004:
        prof += [(r_rib, h + 0.15 * pitch), (r_rib, h + 0.5 * pitch), (r_core, h + 0.65 * pitch), (r_core, h + pitch)]
        h += pitch
    prof += [(0.0178, a1 - 0.002), (0.0178, a1), (0.0, a1)]
    return prof


def controls_geometry(hp, dense, s):
    G0, G1 = (hp.GRIP_L if s > 0 else hp.GRIP_R)
    fr = frame_at(v_sub(G1, G0))
    Pp, Tp = bar_at(dense, s, 0.262)
    fp = frame_at(Tp)
    pivot = lp(G0, fr, -0.006, 0.047, -0.006)
    return G0, fr, Pp, fp, pivot


def handlebar(c, hp, dense):
    put(c, "Guidão", sweep(dense, circle2(hp.BAR_R, 14)), CHROME, ALL, group=STEER)
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        G0, fr, Pp, fp, pivot = controls_geometry(hp, dense, s)
        g, f, up = fr
        Tp = fp[0]
        put(c, f"Manopla {label}", lathe(grip_profile(0.016, 0.128), G0, g, n=14), RUBBER, FULL, group=STEER)
        put(c, f"Manopla {label} (simplificada)", lathe([(0, 0.0), (0.019, 0.0), (0.019, 0.128), (0, 0.128)], G0, g, n=10), RUBBER, COARSE,
            group=STEER)
        put(c, f"Peso da ponta do guidão {label}", lathe([(0, 0.128), (0.0185, 0.128), (0.0190, 0.132), (0.0172, 0.139), (0.0105, 0.1425),
                                                           (0, 0.143)], G0, g, n=18), CHROME, FULL, group=STEER)
        # Switch housing (left) / throttle housing (right).
        hb = sweep([lp(G0, fr, -0.012, 0.004, -0.002), lp(G0, fr, 0.016, 0.004, -0.002)], rrect2(0.052, 0.046, 0.014, 3), up=f)
        put(c, f"{'Punho de interruptores' if s > 0 else 'Punho do acelerador'} {label}", hb, BLACK_PLASTIC, FULL, group=STEER)
        buttons = [cyl(lp(G0, fr, 0.002, -0.019, cc), lp(G0, fr, 0.002, -0.027, cc), 0.0042, n=10) for cc in (0.011, -0.001, -0.013)]
        buttons.append(box(lp(G0, fr, 0.002, 0.004, 0.022), (0.010, 0.016, 0.004), fr))
        put(c, f"Botões do punho {label}", buttons, SWITCH_BUTTON, FINE, group=STEER)
        put(c, f"Parafusos do punho {label}", [cyl(lp(G0, fr, 0.002, 0.016, -0.024), lp(G0, fr, 0.002, 0.016, -0.028), 0.0032, n=6),
                                                cyl(lp(G0, fr, 0.002, -0.010, -0.024), lp(G0, fr, 0.002, -0.010, -0.028), 0.0032, n=6)],
            CHROME, FINE, group=STEER)
        # Perch clamp on the bend, perch arm to the lever pivot.
        clamp = lathe([(0, -0.009), (0.0195, -0.009), (0.0195, 0.009), (0, 0.009)], Pp, Tp, n=16)
        arm = sweep([Pp, v_lerp(Pp, pivot, 0.6), pivot], rrect2(0.016, 0.017, 0.005, 2), up=up)
        boss = cyl(v_add(pivot, v_mul(up, -0.011)), v_add(pivot, v_mul(up, 0.011)), 0.0095, n=14)
        put(c, f"Manete base {label}", [clamp, arm, boss], POLISHED_AL, FULL, group=STEER)
        put(c, f"Parafusos da base do manete {label}", [hexagon(v_add(pivot, v_mul(up, 0.011)), v_add(pivot, v_mul(up, 0.016)), 0.0062, ref=g),
                                                         cyl(v_add(Pp, v_mul(fp[1], -0.02)), v_add(Pp, v_mul(fp[1], -0.026)), 0.0048, n=8)],
            CHROME, FINE, group=STEER)
        blade_pts = [v_add(pivot, v_mul(g, -0.004)), lp(G0, fr, 0.030, 0.046, -0.009), lp(G0, fr, 0.070, 0.042, -0.012),
                     lp(G0, fr, 0.102, 0.037, -0.013), lp(G0, fr, 0.120, 0.035, -0.011)]
        blade = sweep(catmull(blade_pts, 3), rrect2(0.016, 0.0075, 0.003, 2), up=up)
        tip = sphere(blade_pts[-1], 0.0058, n=6, axis=g)
        put(c, f"{'Manete da embreagem' if s > 0 else 'Manete do freio dianteiro'}", [blade, tip], POLISHED_AL, FULL, group=STEER)
        if s > 0:
            adj = [cyl(v_add(pivot, v_mul(g, -0.008)), v_add(pivot, v_mul(g, -0.030)), 0.0055, n=10),
                   hexagon(v_add(pivot, v_mul(g, -0.016)), v_add(pivot, v_mul(g, -0.020)), 0.0085, ref=up)]
            put(c, "Regulador do cabo da embreagem", adj, CHROME, FINE, group=STEER)
        else:
            # master cylinder, reservoir, banjo
            Cm = v_add(Pp, v_add(v_mul(fp[1], 0.030), v_mul(fp[2], 0.004)))
            body = cyl(v_add(Cm, v_mul(Tp, -0.030)), v_add(Cm, v_mul(Tp, 0.012)), 0.0125, n=16)
            res = box(v_add(Cm, v_add(v_mul(fp[2], 0.026), v_mul(Tp, -0.008))), (0.046, 0.034, 0.024), fp)
            put(c, "Cilindro mestre dianteiro", [body, res], POLISHED_AL, FULL, group=STEER)
            lid = box(v_add(Cm, v_add(v_mul(fp[2], 0.0395), v_mul(Tp, -0.008))), (0.049, 0.037, 0.003), fp)
            put(c, "Tampa do reservatório dianteiro", lid, CHROME, FULL, group=STEER)
            screws = [cyl(v_add(Cm, v_add(v_mul(fp[2], 0.041), v_add(v_mul(Tp, -0.008 + a), v_mul(fp[1], b)))),
                          v_add(Cm, v_add(v_mul(fp[2], 0.0435), v_add(v_mul(Tp, -0.008 + a), v_mul(fp[1], b)))), 0.0028, n=6)
                      for a in (-0.019, 0.019) for b in (-0.013, 0.013)]
            put(c, "Parafusos da tampa do reservatório", screws, CHROME, FINE, group=STEER)
            put(c, "Visor do reservatório", cyl(v_add(Cm, v_add(v_mul(fp[2], 0.026), v_mul(fp[1], -0.0168))),
                                                v_add(Cm, v_add(v_mul(fp[2], 0.026), v_mul(fp[1], -0.0185))), 0.0055, n=12),
                LENS_CLEAR, FINE, group=STEER)
            Pb = v_add(Cm, v_mul(Tp, -0.036))
            banjo = [cyl(v_add(Pb, v_mul(fp[2], -0.012)), v_add(Pb, v_mul(fp[2], 0.008)), 0.0075, n=12),
                     hexagon(v_add(Pb, v_mul(fp[2], 0.008)), v_add(Pb, v_mul(fp[2], 0.014)), 0.0085, ref=Tp)]
            put(c, "Banjo do freio dianteiro", banjo, CHROME, FINE, group=STEER)
            Ph = v_add(hp.BAR_CLAMP, (-0.20, 0.01, -0.025))
            link = [v_add(Pb, v_mul(fp[2], -0.010)), v_add(Pb, v_add(v_mul(fp[2], -0.040), v_mul(fp[1], 0.004))),
                    v_lerp(Pb, Ph, 0.75), Ph]
            put(c, "Mangueira do cilindro mestre dianteiro", sweep(catmull(link, 4), circle2(0.0045, 8)), RUBBER, FULL, group=STEER)
            # throttle cable outlets under the housing
            outs = [cyl(lp(G0, fr, a, 0.016, -0.020), lp(G0, fr, a - 0.004, 0.026, -0.036), 0.0045, n=8) for a in (-0.006, 0.006)]
            put(c, "Saídas dos cabos do acelerador", outs, BLACK_PLASTIC, FINE, group=STEER)
        # Mirror on the perch: stem, round head, glass.
        m0 = v_add(Pp, v_add(v_mul(fp[2], 0.017), v_mul(fp[1], 0.010)))
        stem = [m0, v_add(m0, (s * 0.012, 0.004, 0.050)), v_add(m0, (s * 0.050, 0.016, 0.125)), v_add(m0, (s * 0.068, 0.022, 0.160))]
        n = v_norm((-s * 0.33, 0.93, 0.12))
        hc = v_add(stem[-1], v_mul(n, 0.016))
        put(c, f"Haste do retrovisor {label}", [sweep(catmull(stem, 4), circle2(0.0055, 8)),
                                                 hexagon(v_add(m0, (0, 0, -0.002)), v_add(m0, (0, 0, 0.008)), 0.0085, ref=X)],
            CHROME, FULL, group=STEER)
        shell = lathe([(0, -0.024), (0.022, -0.022), (0.039, -0.015), (0.049, -0.006), (0.053, 0.002), (0.053, 0.007), (0, 0.007)],
                      hc, n, n=26)
        put(c, f"Retrovisor {label}", shell, CHROME, FULL, group=STEER)
        # convex glass: it shows the sky above and the ground below, as a mirror does
        put(c, f"Espelho do retrovisor {label}", lathe([(0, 0.006), (0.049, 0.006), (0.049, 0.0078), (0.044, 0.0090), (0.033, 0.0102),
                                                        (0.018, 0.0110), (0, 0.0113)], hc, n, n=26),
            MIRROR_GLASS, FULL, group=STEER)


# --- headlight, front signals, speedometer (steered) ------------------------------------------------------------------


def headlight(c, hp):
    O = hp.HEADLIGHT
    A = hp.HEADLIGHT_DIR
    bucket = [(0, -0.085), (0.034, -0.083), (0.060, -0.074), (0.078, -0.060), (0.089, -0.042), (0.094, -0.020), (0.0945, 0.040),
              (0.091, 0.044), (0.087, 0.041), (0.0, -0.068)]
    put(c, "Farol", lathe(bucket, O, A, n=40, ref=Z), CHROME, ALL, group=STEER)
    put(c, "Aro do farol", lathe([(0.087, 0.040), (0.0965, 0.041), (0.0985, 0.047), (0.096, 0.054), (0.090, 0.056), (0.086, 0.050)],
                                 O, A, n=40, ref=Z, closed=True), CHROME, FULL, group=STEER)
    # a clear glass shell 2 mm thick, the chrome reflector and the bulb behind it
    put(c, "Lente do farol", lathe([(0, 0.062), (0.045, 0.0605), (0.074, 0.056), (0.086, 0.050), (0.086, 0.044), (0.088, 0.044),
                                    (0.087, 0.052), (0.075, 0.058), (0.045, 0.0625), (0, 0.064)], O, A, n=36, ref=Z),
        LENS_CLEAR, ALL, group=STEER)
    put(c, "Refletor do farol", lathe([(0.086, 0.040), (0.070, 0.024), (0.045, 0.010), (0.016, 0.004), (0.016, 0.000), (0.050, 0.005),
                                       (0.075, 0.020), (0.089, 0.040)], O, A, n=32, ref=Z, closed=True), CHROME, FULL, group=STEER)
    put(c, "Lâmpada do farol", [sphere(v_add(O, v_mul(A, 0.022)), 0.012, n=6, axis=A),
                                cyl(v_add(O, v_mul(A, 0.003)), v_add(O, v_mul(A, 0.014)), 0.007, n=10)], LENS_CLEAR, FINE, group=STEER)
    put(c, "Capa da lâmpada do farol", lathe([(0, 0.031), (0.012, 0.031), (0.0135, 0.036), (0, 0.037)], O, A, n=16, ref=Z), CHROME, FINE,
        group=STEER)
    # Bracket: from the lower clamp's front face round under the bucket to the side ears.
    F = hp.fork
    w_c = sum(hp.W_LOWER_CLAMP) / 2
    arms = []
    ears = []
    for s in (1, -1):
        ear = (s * 0.100, O[1], O[2])
        mid = (s * 0.098, O[1] + 0.022, O[2] - 0.060)
        foot = F(s * 0.046, 0.094, w_c)
        arms.append(sweep(catmull([ear, mid, v_add(foot, (s * 0.01, -0.012, 0.006)), foot], 4), rrect2(0.016, 0.006, 0.002, 2), up=X))
        ears.append(hexagon((s * 0.0945, O[1], O[2]), (s * 0.106, O[1], O[2]), 0.0085, ref=Z))
        ears.append(cyl((s * 0.090, O[1], O[2]), (s * 0.103, O[1], O[2]), 0.011, n=12))
        arms.append(box(F(s * 0.046, 0.097, w_c), (0.022, 0.006, 0.032), (X, hp.FORK_V, hp.STEER_D)))
    put(c, "Suporte do farol", arms, CHROME, FULL, group=STEER)
    put(c, "Parafusos do farol", ears, CHROME, FINE, group=STEER)
    # Front turn signals on clamps round the fork tubes, between the triple clamps.
    D = hp.STEER_D
    w = 0.640
    bodies, lenses, stalks, backs = [], [], [], []
    for s in (1, -1):
        tc = F(s * hp.FORK_X, hp.OFFSET, w)
        stalks.append(lathe([(0.0270, -0.009), (0.0305, -0.009), (0.0305, 0.009), (0.0270, 0.009)], tc, D, n=18, closed=True))
        base = v_add(tc, (s * 0.030, 0.0, 0.0))
        end = (s * 0.200, tc[1] - 0.030, tc[2] + 0.004)
        stalks.append(sweep([base, v_add(base, (s * 0.04, -0.008, 0.002)), end], circle2(0.0058, 8)))
        o = v_add(end, (s * 0.018, 0.0, 0.0))
        bodies.append(lathe([(0, -0.030), (0.010, -0.029), (0.018, -0.022), (0.021, -0.008), (0.021, 0.016), (0, 0.016)], o, A, n=20,
                            ref=Z))
        backs.append(lathe([(0, 0.0155), (0.0195, 0.0155), (0.0195, 0.0185), (0, 0.0185)], o, A, n=20, ref=Z))
        lenses.append(lathe([(0, 0.017), (0.0195, 0.017), (0.018, 0.026), (0.012, 0.032), (0, 0.034)], o, A, n=20, ref=Z))
    put(c, "Hastes dos piscas dianteiros", stalks, CHROME, FULL, group=STEER)
    put(c, "Piscas dianteiros", bodies, CHROME, FULL, group=STEER)
    put(c, "Lentes dos piscas dianteiros", lenses, LENS_AMBER, FULL, group=STEER)
    put(c, "Fundos dos piscas dianteiros", backs, AMBER_PLASTIC, FINE, group=STEER)


def speedometer(c, hp):
    F, D, V = hp.fork, hp.STEER_D, hp.FORK_V
    Sc = F(0, 0.085, 0.885)
    cup = [(0, -0.047), (0.028, -0.047), (0.042, -0.040), (0.049, -0.026), (0.050, -0.006), (0.050, 0.000), (0.0455, 0.000),
           (0.0455, -0.0065), (0, -0.0065)]
    put(c, "Velocímetro", lathe(cup, Sc, D, n=32, ref=V), CHROME, ALL, group=STEER)
    put(c, "Aro do velocímetro", lathe([(0.0435, -0.001), (0.0505, -0.001), (0.0515, 0.004), (0.0495, 0.0075), (0.0445, 0.0075),
                                        (0.0435, 0.004)], Sc, D, n=32, ref=V, closed=True), CHROME, FULL, group=STEER)
    put(c, "Mostrador do velocímetro", lathe([(0, -0.006), (0.0445, -0.006), (0.0445, -0.003), (0, -0.003)], Sc, D, n=32, ref=V),
        DIAL, FULL, group=STEER)
    e12 = V
    e3 = v_norm(v_cross(D, V))  # to the rider's right when read from behind
    if e3[0] > 0:
        e3 = v_mul(e3, -1.0)
    # ticks: 0..240 km/h over 270 degrees, from 7:30 to 4:30 clockwise (as read)
    ctr = v_add(Sc, v_mul(D, -0.0028))

    def dial_dir(clock_deg):
        t = math.radians(clock_deg)
        return v_add(v_mul(e12, math.cos(t)), v_mul(e3, math.sin(t)))
    ticks = []
    for k in range(25):
        a = -135 + 270 * k / 24
        d = dial_dir(a)
        big = k % 2 == 0
        L = 0.007 if big else 0.004
        ticks.append(box(v_add(ctr, v_mul(d, 0.0385 - L / 2)), (L, 0.0016 if big else 0.0011, 0.0008), (d, v_cross(D, d), D)))
    put(c, "Marcações do velocímetro", ticks, TICKS, FINE, group=STEER)
    nd = dial_dir(-80)
    put(c, "Ponteiro do velocímetro", [box(v_add(ctr, v_add(v_mul(nd, 0.013), v_mul(D, 0.0008))), (0.034, 0.0016, 0.0009),
                                           (nd, v_cross(D, nd), D)),
                                       cyl(v_add(ctr, v_mul(D, 0.0)), v_add(ctr, v_mul(D, 0.0022)), 0.0035, n=10)], NEEDLE, FINE, group=STEER)
    # stalk to the upper clamp
    base = F(0, 0.085, hp.W_UPPER_CLAMP[1])
    put(c, "Suporte do velocímetro", [cyl(base, v_add(Sc, v_mul(D, -0.046)), 0.0085, n=12),
                                       lathe([(0, 0.0), (0.016, 0.0), (0.016, 0.004), (0, 0.004)], base, D, n=16)], CHROME, FULL,
        group=STEER)


# --- front fender (steered) ---------------------------------------------------------------------------------------------


def front_fender(c, hp):
    fa = hp.FRONT_AXLE
    R = hp.FENDER_F_INNER
    W = 0.072
    sec = fender_section(W, 0.022, 0.0025, bead=0.0018, n=9, power=3.0)
    path = []
    for k in range(29):
        t = math.radians(38.0 + (162.0 - 38.0) * k / 28)
        path.append((0.0, fa[1] + R * math.cos(t), fa[2] + R * math.sin(t)))
    put(c, "Para-lama dianteiro", sweep(path, [(x, d) for d, x in sec], caps=False, up=X), TANK_PAINT, ALL, group=STEER)
    # stays along the sliders' inner faces, from the lower boss up to the fender
    psi = math.atan2(hp.FENDER_F_MOUNTS[0][2] - fa[2], hp.FENDER_F_MOUNTS[0][1] - fa[1])
    d = (0.0, math.cos(psi), math.sin(psi))
    nrm = v_cross(X, d)
    stays, bolts = [], []
    for s in (1, -1):
        x = s * (W + 0.0042)
        a0, a1 = 0.068, R - 0.008
        stays.append(box(v_add(fa, v_add((x, 0, 0), v_mul(d, (a0 + a1) / 2))), (0.0034, a1 - a0, 0.017), (X, d, nrm)))
        for m in hp.FENDER_F_MOUNTS:
            if m[0] * s > 0:
                bolts.append(hexagon((s * (W + 0.0025), m[1], m[2]), (s * (W - 0.004), m[1], m[2]), 0.0072, ref=Z))
        # a curved brace along the fender's edge, from the stay forward
        br = []
        for k in range(7):
            t = psi + math.radians(4 + 40 * k / 6)
            br.append((x, fa[1] + (R - 0.012) * math.cos(t), fa[2] + (R - 0.012) * math.sin(t)))
        stays.append(sweep(br, rrect2(0.0034, 0.014, 0.0012, 1), up=X))
    put(c, "Suportes do para-lama dianteiro (hastes)", stays, POLISHED_AL, FULL, group=STEER)
    put(c, "Parafusos do para-lama dianteiro", bolts, CHROME, FINE, group=STEER)


# --- cables ---------------------------------------------------------------------------------------------------------------


def cables(c, hp, dense):
    F = hp.fork
    S = STEER
    # Clutch cable: left perch -> in front of the head -> along the left downtube -> top of the primary.
    G0, fr, Pp, fp, pivot = controls_geometry(hp, dense, 1)
    g = fr[0]
    p0 = v_add(pivot, v_mul(g, -0.030))
    # (the clutch release is on the gearbox's right end cover: the cable crosses in front of the crankcase, then runs back
    # inboard of the front header to the release cover at (x -0.124, y 0.16, z 0.31))
    # (in front of the head, under the lower clamp, back to the left downtube and down its outer front face)
    pts = [(p0, S), (v_add(p0, (-0.035, -0.030, -0.050)), S), (F(0.130, 0.140, 0.86), S), (F(0.080, 0.125, 0.72), S),
           (F(0.072, 0.112, 0.62), S), (F(0.060, 0.100, 0.49), S), ((0.094, -0.448, 0.690), None), ((0.112, -0.443, 0.62), None), ((0.139, -0.452, 0.50), None),
           ((0.095, -0.488, 0.418), None),
           ((-0.095, -0.488, 0.418), None), ((-0.160, -0.445, 0.392), None), ((-0.170, -0.33, 0.352), None),
           ((-0.170, -0.20, 0.318), None), ((-0.160, 0.0, 0.302), None), ((-0.146, 0.10, 0.306), None), ((-0.134, 0.136, 0.310), None)]
    put(c, "Cabo da embreagem", gtube(pts, 0.0038, n=8, per=5), BLACK_PLASTIC, FULL)
    # Throttle cables: right housing -> in front of the head -> over the front cylinder -> the throttle body in the V.
    G0, fr, Pp, fp, pivot = controls_geometry(hp, dense, -1)
    for k, a in enumerate((-0.006, 0.006)):
        p0 = lp(G0, fr, a - 0.004, 0.026, -0.036)
        dx = 0.010 * k
        pts = [(p0, S), (v_add(p0, (0.02, -0.03, -0.07)), S), (F(-0.130 - dx, 0.140, 0.86), S), (F(-0.080 - dx, 0.125, 0.72), S),
               (F(-0.072 - dx, 0.112, 0.62), S), (F(-0.060 - dx, 0.100, 0.49), S), ((-0.080 - 0.5 * dx, -0.452, 0.690), None),
               ((-0.086 - dx, -0.40, 0.768), None), ((-0.088 - dx, -0.28, 0.752), None),
               ((-0.097 - 1.4 * dx, -0.160, 0.730), None), ((-0.108 - 1.6 * dx, -0.080, 0.690), None),
               ((-0.108 - 1.6 * dx, -0.079, 0.629), None)]  # onto the throttle drum
        put(c, f"Cabo do acelerador {k + 1}", gtube(pts, 0.0036, n=8, per=5), BLACK_PLASTIC, FULL)
    # Wiring: both switch housings along under the bar, down in front of the upper clamp into the back of the headlight
    # bucket (the connections are in it; its harness goes on to the frame through the lower clamp, below).
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        G0, fr, Pp, fp, pivot = controls_geometry(hp, dense, s)
        p0 = lp(G0, fr, -0.012, -0.004, -0.022)
        q1, _ = bar_at(dense, s, 0.215)
        q2, _ = bar_at(dense, s, 0.13)
        pts = [(p0, S), (v_add(q1, (0, 0.004, -0.019)), S), (v_add(q2, (0, 0.006, -0.019)), S),
               (F(s * 0.052, 0.130, 0.875), S), (F(s * 0.035, 0.160, 0.78), S), ((s * 0.015, -0.553, 0.950), S)]
        put(c, f"Fiação do punho {label}", gtube(pts, 0.0040, n=8, per=5), BLACK_PLASTIC, FINE)
    # Headlight and speedometer wires into the lower / upper clamp (grommets).
    O = hp.HEADLIGHT
    pts = [(v_add(O, (0.0, 0.080, -0.020)), S), (v_add(O, (0.0, 0.095, -0.045)), S), (F(0.0, 0.080, 0.585), S)]
    put(c, "Fiação do farol", gtube(pts, 0.0045, n=8, per=4), BLACK_PLASTIC, FINE)
    Sc = F(0, 0.085, 0.885)
    pts = [(v_add(Sc, v_add(v_mul(hp.STEER_D, -0.040), v_mul(hp.FORK_V, -0.026))), S), (F(0.0, 0.040, 0.855), S),
           (F(0.0, 0.035, hp.W_UPPER_CLAMP[1]), S)]
    put(c, "Fiação do velocímetro", gtube(pts, 0.0035, n=8, per=4), BLACK_PLASTIC, FINE)


# --- plan symbols ------------------------------------------------------------------------------------------------------------


def plan_symbols(c, hp, dense):
    """Plan outlines of the steered bar, mirrors, headlight and front fender (the script does not draw in plans)."""
    H = hp.HANDLEBAR
    r = 0.019
    left, right = [], []
    for k, p in enumerate(H):
        a = H[max(0, k - 1)]
        b = H[min(len(H) - 1, k + 1)]
        t = v_norm((b[0] - a[0], b[1] - a[1], 0.0))
        n = (-t[1], t[0], 0.0)
        left.append(v_add(p, v_mul(n, r)))
        right.append(v_add(p, v_mul(n, -r)))
    outline = left + right[::-1]
    pts = [steer_expr(q, hp=hp)[:2] for q in outline]
    c.extrusion("Planta do guidão", pts, 0, 0.01, CHROME, detail=ALL, in_plan=True)
    c.plan_only("Planta do guidão")
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        G0, fr, Pp, fp, pivot = controls_geometry(hp, dense, s)
        m0 = v_add(Pp, v_add(v_mul(fp[2], 0.017), v_mul(fp[1], 0.010)))
        top = v_add(m0, (s * 0.068, 0.022, 0.160))
        n = v_norm((-s * 0.33, 0.93, 0.12))
        hc = v_add(top, v_mul(n, 0.016))
        e1 = v_norm(v_cross(n, Z))
        e2 = v_cross(e1, n)
        rim = []
        for k in range(12):
            t = 2 * math.pi * k / 12
            for h in (-0.022, 0.008):
                rim.append(v_add(hc, v_add(v_mul(n, h), v_add(v_mul(e1, 0.053 * math.cos(t)), v_mul(e2, 0.053 * math.sin(t))))))
        hull = hull2([(q[0], q[1]) for q in rim])
        zc = hc[2]
        pts = [steer_expr((u, v, zc), hp=hp)[:2] for u, v in hull]
        c.extrusion(f"Planta do retrovisor {label}", pts, 0, 0.01, CHROME, detail=ALL, in_plan=True)
        c.plan_only(f"Planta do retrovisor {label}")
    O = hp.HEADLIGHT
    hull = hull2([(O[0] + 0.0985 * math.cos(2 * math.pi * k / 16), O[1] + h) for k in range(16) for h in (-0.064, 0.0)] +
                 [(O[0] + 0.05 * math.cos(2 * math.pi * k / 16), O[1] + 0.085) for k in range(16)])
    pts = [steer_expr((u, v, O[2]), hp=hp)[:2] for u, v in hull]
    c.extrusion("Planta do farol", pts, 0, 0.01, CHROME, detail=ALL, in_plan=True)
    c.plan_only("Planta do farol")
    fa = hp.FRONT_AXLE
    R = hp.FENDER_F_INNER + 0.003
    ys = [fa[1] + R * math.cos(math.radians(a)) for a in (38.0, 162.0)]
    zs = fa[2] + R * 0.5
    box_pts = [(0.075, min(ys)), (0.075, max(ys)), (-0.075, max(ys)), (-0.075, min(ys))]
    pts = [steer_expr((u, v, zs), hp=hp)[:2] for u, v in box_pts]
    c.extrusion("Planta do para-lama dianteiro", pts, 0, 0.01, TANK_PAINT, detail=ALL, in_plan=True)
    c.plan_only("Planta do para-lama dianteiro")
