"""Rolling chassis of the Moto custom: double-cradle frame, front end, swingarm and twin shocks,
wire-spoke wheels, brakes, final belt and side stand.

How it is built (see base.py): static parts that lie in a principal plane are engine shapes
(sweeps with arcs, profiles: exact and small in the file); static parts curved in 3D are lean
numeric meshes; everything on the steering head (fork, front wheel, front brake, hose) is in the
moving-parts script (group=STEER) and so is the side stand (group=STAND). Small many-vertex fine
details (tread blocks, nipples, coil springs, drilled holes) also go to the script (lua=True) to
keep the .ccomp small.
"""

from __future__ import annotations

import math

from _moto.base import (
    BLACK_PLASTIC, BRASS, CHROME, COARSE, DARK_METAL, DISC_STEEL, FINE, FRAME_BLACK, FULL, MEDIUM, POLISHED_AL,
    RUBBER, STAINLESS, STAND, STEER, Hardpoints, steer_expr, box, catmull, circle2, circles_hull, cyl, disc_x, hexagon, lathe, mx,
    ncyl_side, ndisc_x, nhex_x, nannulus_sector, nprofile, nring_x, nsweep, ntube, prism, put, ring, rrect2, spring, sweep,
    v_add, v_cross, v_dot, v_len, v_lerp, v_mul, v_norm, v_sub,
)

X = (1.0, 0.0, 0.0)
Y = (0.0, 1.0, 0.0)
Z = (0.0, 0.0, 1.0)
UP = Z  # angle 0 of the wheels' lathes points up


def add(c, hp: Hardpoints):
    frame(c, hp)
    rear_suspension(c, hp)
    rear_wheel(c, hp)
    belt(c, hp)
    front_end(c, hp)
    front_wheel(c, hp)
    stand(c, hp)
    plan_symbol(c, hp)


def plan_symbol(c, hp: Hardpoints):
    """Plan outlines of the steered front tyre and clamps: the script's pieces do not draw in plans, so these
    plan-only pieces stand in for them, their corners turned with the steering by expressions (steer_expr)."""
    fa = hp.FRONT_AXLE
    w, r = hp.W_F / 2, hp.R_F
    # seen from above the front fender (carroceria's plan symbol) covers the tyre but for its rear end
    y0 = fa[1] + hp.FENDER_F_INNER * math.cos(math.radians(38.0))
    tyre = [(w, y0), (w * 0.8, fa[1] + r - 0.022), (w * 0.45, fa[1] + r), (-w * 0.45, fa[1] + r), (-w * 0.8, fa[1] + r - 0.022), (-w, y0)]
    pts = [steer_expr((x, y, fa[2]), hp=hp)[:2] for x, y in tyre]
    c.extrusion("Planta do pneu dianteiro", pts, 0, 0.01, RUBBER, detail="cmf", in_plan=True)
    c.plan_only("Planta do pneu dianteiro")
    clamp = clamp_outline(hp.FORK_X, hp.OFFSET, 0.039, 0.033, 0.016)[::3]
    pts = [steer_expr(hp.fork(u, v, hp.W_UPPER_CLAMP[1]), hp=hp)[:2] for u, v in clamp]
    c.extrusion("Planta das mesas do garfo", pts, 0, 0.01, POLISHED_AL, detail=FULL, in_plan=True)
    c.plan_only("Planta das mesas do garfo")


# --- wheel geometry ------------------------------------------------------------------------------------


def wheel_point(axle, x, r, phi):
    """A point of a wheel: x across (absolute offset from the axle), radius r, angle phi (degrees, 0 up, 90 to the front)."""
    t = math.radians(phi)
    return (axle[0] + x, axle[1] - r * math.sin(t), axle[2] + r * math.cos(t))


def tyre_profile(rb, rt, width, rim_w, crown_power=2.0, grooves=(), groove_d=0.0025, groove_w=0.005, n=72):
    """Closed (r, x) section of a tyre: beads inside the rim flanges, round sidewalls, crown at rt, square grooves."""
    hgt = rt - rb
    rc = rb + 0.40 * hgt  # radius of the widest point
    a = width / 2
    b_up = rt - rc
    bead_x = rim_w / 2 - 0.002
    p = crown_power
    pts = []
    for k in range(6):  # lower right side: from the bead up to the widest point
        s = math.radians(90 * (1 - k / 5))
        pts.append((rc - (rc - rb - 0.010) * math.sin(s), bead_x + 0.004 + (a - bead_x - 0.004) * math.cos(s)))

    def crown_at(t):
        co, si = math.cos(t), math.sin(t)
        return a * math.copysign(abs(co) ** (2 / p), co), rc + b_up * abs(si) ** (2 / p)

    def t_of(x):
        t = math.acos(min(abs(x) / a, 1.0) ** (p / 2))
        return t if x >= 0 else math.pi - t

    marks = [(math.pi * k / n, 0) for k in range(1, n)]
    for g in grooves:
        marks += [(t_of(g + groove_w / 2), 1), (t_of(g - groove_w / 2), 2)]
    marks.sort()
    for t, kind in marks:
        x, r = crown_at(t)
        if kind == 1:  # right edge of a groove: surface, then the bottom
            pts += [(r, x), (r - groove_d, x)]
        elif kind == 2:  # left edge: bottom, then the surface
            pts += [(r - groove_d, x), (r, x)]
        else:
            pts.append((r - groove_d if any(abs(x - g) < groove_w / 2 - 1e-7 for g in grooves) else r, x))
    for k in range(6):
        s = math.radians(90 * k / 5)
        pts.append((rc - (rc - rb - 0.010) * math.sin(s), -(bead_x + 0.004 + (a - bead_x - 0.004) * math.cos(s))))
    pts += [(rb, -bead_x), (rb - 0.004, -bead_x + 0.004), (rb - 0.004, bead_x - 0.004), (rb, bead_x)]
    return pts


def rim_profile(rb, w, flange_h=0.0125, t=0.0035, well=0.013, seat=0.016):
    """Closed (r, x) section of a drop-centre spoked rim (rb: bead seat radius, w: width between flanges)."""
    h = w / 2
    ws = h - seat - 0.6 * well  # half width of the well's bottom
    outer = [(rb + flange_h - 0.002, -h - t), (rb + flange_h, -h - t * 0.4), (rb + flange_h - 0.001, -h + 0.0005),
             (rb + 0.003, -h), (rb, -h + 0.003), (rb, -h + seat), (rb - well, -ws), (rb - well, ws), (rb, h - seat),
             (rb, h - 0.003), (rb + 0.003, h), (rb + flange_h - 0.001, h - 0.0005), (rb + flange_h, h + t * 0.4),
             (rb + flange_h - 0.002, h + t)]
    inner = [(rb - 0.007, h + t), (rb - well - t, ws + 0.006), (rb - well - t, -ws - 0.006), (rb - 0.007, -h - t)]
    return outer + inner


def wheel_specs(hp: Hardpoints):
    front = {
        "rb": hp.RIM_F, "rt": hp.R_F, "width": hp.W_F, "rim_w": hp.RIM_W_F, "crown": 2.0,
        "grooves": (0.0, 0.0165, -0.0165, 0.031, -0.031), "groove_d": 0.003,
        "flange_h": 0.0115, "well": 0.012, "seat": 0.013,
        "flange_x": 0.042, "flange_hole_r": 0.041, "rim_hole_x": 0.004, "spoke_r": 0.0019,
        "hub": [(0, -0.074), (0.021, -0.074), (0.022, -0.067), (0.030, -0.065), (0.030, -0.048), (0.047, -0.046),
                (0.048, -0.043), (0.048, -0.039), (0.035, -0.037), (0.031, -0.031), (0.0295, 0.0), (0.031, 0.031),
                (0.035, 0.037), (0.048, 0.039), (0.048, 0.043), (0.047, 0.046), (0.030, 0.048), (0.030, 0.052),
                (0.056, 0.0535), (0.056, 0.0595), (0.024, 0.0605), (0.022, 0.067), (0.021, 0.074), (0, 0.074)],
    }
    rear = {
        "rb": hp.RIM_R, "rt": hp.R_R, "width": hp.W_R, "rim_w": hp.RIM_W_R, "crown": 2.6,
        "grooves": (0.0, 0.038, -0.038), "groove_d": 0.003,
        "flange_h": 0.013, "well": 0.014, "seat": 0.020,
        "flange_x": 0.072, "flange_hole_r": 0.058, "rim_hole_x": 0.012, "spoke_r": 0.0021,
        # hub as discs along X: (x0, x1, r)
        "hub": [(-0.110, -0.103, 0.024), (-0.103, -0.0975, 0.060), (-0.0975, -0.078, 0.042), (-0.078, -0.067, 0.066),
                (-0.067, 0.067, 0.040), (0.067, 0.078, 0.066), (0.078, 0.101, 0.042), (0.101, 0.107, 0.078), (0.107, 0.114, 0.026)],
        "blocks": [(0.019, 0.026, 0.25), (-0.019, 0.026, -0.25), (0.058, 0.030, 0.45), (-0.058, 0.030, -0.45)],
        "block_count": 56, "block_len": 0.022,
    }
    return front, rear


def crown_radius(spec, x):
    """The crown of tyre_profile at x (no grooves)."""
    rb, rt, a, p = spec["rb"], spec["rt"], spec["width"] / 2, spec["crown"]
    rc = rb + 0.40 * (rt - rb)
    u = min(abs(x) / a, 0.999) ** (p / 2)
    return rc + (rt - rc) * math.sqrt(max(0.0, 1 - u * u)) ** (2 / p)


def spokes_shapes(axle, spec, n_sides=5):
    """The 40 spokes (cross-3) as four rings of ten: (left flange shapes, right flange shapes)."""
    fx, fr = spec["flange_x"], spec["flange_hole_r"]
    rr, rx = spec["rb"] - spec["well"] + 0.0015, spec["rim_hole_x"]
    out = {1: [], -1: []}
    for side in (1, -1):
        for lead in (0, 1):
            ph = 18.0 * lead + (0.0 if side > 0 else 9.0)
            pr = ph + side * (54.0 if lead == 0 else -54.0)
            hub = wheel_point(axle, side * fx, fr, ph)
            rim = wheel_point(axle, side * rx, rr, pr)
            d = v_norm(v_sub(rim, hub))
            spoke = sweep([v_add(hub, v_mul(d, -0.003)), rim], circle2(spec["spoke_r"], n_sides), caps=False, up=X)
            out[side].append(ring(spoke, axle, X, 10, 36.0))
    return out[1], out[-1]


def nipples_shapes(axle, spec):
    fx, fr = spec["flange_x"], spec["flange_hole_r"]
    rr, rx = spec["rb"] - spec["well"] + 0.0015, spec["rim_hole_x"]
    out = []
    for side in (1, -1):
        for lead in (0, 1):
            ph = 18.0 * lead + (0.0 if side > 0 else 9.0)
            pr = ph + side * (54.0 if lead == 0 else -54.0)
            hub = wheel_point(axle, side * fx, fr, ph)
            rim = wheel_point(axle, side * rx, rr, pr)
            d = v_norm(v_sub(rim, hub))
            nip = cyl(v_add(rim, v_mul(d, -0.014)), v_add(rim, v_mul(d, 0.004)), spec["spoke_r"] * 1.7, n=6)
            out.append(ring(nip, axle, X, 10, 36.0))
    return out


def tread_shapes(axle, spec):
    """Raised tread blocks (rear tyre): staggered rows, each a ring of small oriented boxes."""
    shapes = []
    count = spec["block_count"]
    for row, (bx, bw, tilt) in enumerate(spec["blocks"]):
        r = crown_radius(spec, bx)
        slope = -(crown_radius(spec, bx + 0.002) - crown_radius(spec, bx - 0.002)) / 0.004
        center = wheel_point(axle, bx, r - 0.0005, 0.0)
        radial = Z
        normal = v_norm(v_add(radial, v_mul(X, slope)))
        along = v_norm(v_add((0.0, -1.0, 0.0), v_mul(X, tilt)))
        across = v_norm(v_cross(normal, along))
        blk = box(center, (spec["block_len"], bw, 0.005), (along, across, normal))
        shapes.append(ring(blk, axle, X, count, 360.0 / count, phase=(180.0 / count if row % 2 else 0.0)))
    return shapes


# --- rear wheel (static, engine shapes) -------------------------------------------------------------------------


def rear_wheel(c, hp: Hardpoints):
    _, sp = wheel_specs(hp)
    ax = hp.REAR_AXLE
    rb = sp["rb"]
    smooth = tyre_profile(rb, sp["rt"], sp["width"], sp["rim_w"], sp["crown"], n=20)
    grooved = tyre_profile(rb, sp["rt"], sp["width"], sp["rim_w"], sp["crown"], sp["grooves"], sp["groove_d"], n=56)
    nring_x(c, "Pneu traseiro", ax, rb, [(r - rb, x) for r, x in smooth], RUBBER, MEDIUM, in_plan=True)
    nring_x(c, "Pneu traseiro com sulcos", ax, rb, [(r - rb, x) for r, x in grooved], RUBBER, FINE, in_plan=True)
    put(c, "Blocos da banda traseira", tread_shapes(ax, sp), RUBBER, FINE, lua=True)
    nring_x(c, "Aro traseiro", ax, rb, [(r - rb, x) for r, x in rim_profile(rb, sp["rim_w"], sp["flange_h"], 0.0035, sp["well"], sp["seat"])],
            CHROME, FULL)
    # coarse: tyre ring and a web
    nring_x(c, "Roda traseira (simplificada)", ax, rb, [(r - rb, x) for r, x in tyre_profile(rb, sp["rt"], sp["width"], sp["rim_w"], sp["crown"], n=8)],
            RUBBER, COARSE, in_plan=True)
    ndisc_x(c, "Raios traseiros (simplificados)", -0.012, 0.012, ax[1], ax[2], rb - 0.01, STAINLESS, COARSE)
    for i, (x0, x1, r) in enumerate(sp["hub"]):
        ndisc_x(c, f"Cubo traseiro {i + 1}", x0, x1, ax[1], ax[2], r, POLISHED_AL, FULL)
    left, right = spokes_shapes(ax, sp)
    put(c, "Raios esquerdos traseiros", left, STAINLESS, FULL)
    put(c, "Raios direitos traseiros", right, STAINLESS, FULL)
    put(c, "Niples traseiros", nipples_shapes(ax, sp), CHROME, FINE, lua=True)
    v0 = wheel_point(ax, 0.0, rb - sp["well"] - 0.003, 4.5)
    v1 = wheel_point(ax, 0.0, rb - sp["well"] - 0.030, 4.5)
    v2 = wheel_point(ax, 0.0, rb - sp["well"] - 0.044, 4.5)
    ncyl_side(c, "Válvula traseira", v0, v1, 0.0042, RUBBER, FINE)
    ncyl_side(c, "Tampa da válvula traseira", v1, v2, 0.0040, BRASS, FINE)
    # Brake disc (rider's right, -X): one piece, drilled band and five windows, bolted to the hub.
    x0, x1 = -0.1075, -0.1025
    ndisc_x(c, "Disco de freio traseiro", x0, x1, ax[1], ax[2], 0.146, DISC_STEEL, FULL)
    holes = [ring(disc_x(x0 - 0.0004, x1 + 0.0004, ax[1], ax[2] + 0.128, 0.0032, n=8), ax, X, 20, 18.0),
             ring(disc_x(x0 - 0.0004, x1 + 0.0004, ax[1], ax[2] + 0.088, 0.016, n=16), ax, X, 5, 72.0, phase=36.0)]
    put(c, "Furação do disco traseiro", holes, DARK_METAL, FINE, lua=True)
    put(c, "Parafusos do disco traseiro", ring(hexagon((x0 + 0.001, ax[1], ax[2] + 0.068), (x0 - 0.005, ax[1], ax[2] + 0.068), 0.0055),
                                               ax, X, 5, 72.0), CHROME, FINE, lua=True)
    # Belt pulley on the left (+X): web, toothed rim and flange; six windows.
    bx, bw = hp.BELT_X, hp.BELT_W
    pr = hp.REAR_PULLEY_R
    ndisc_x(c, "Polia traseira", 0.106, 0.112, ax[1], ax[2], 0.130, POLISHED_AL, FULL)
    nring_x(c, "Coroa da polia", (0.0, ax[1], ax[2]), 0.126,
            [(0.0, bx - bw / 2 - 0.009), (pr - 0.0015 - 0.126, bx - bw / 2 - 0.009), (pr - 0.0015 - 0.126, bx + bw / 2 + 0.001),
             (0.004, bx + bw / 2 + 0.001)], POLISHED_AL, FULL)
    nring_x(c, "Flange da polia", (0.0, ax[1], ax[2]), pr - 0.012,
            [(0.0, bx + bw / 2 + 0.001), (0.018, bx + bw / 2 + 0.001), (0.018, bx + bw / 2 + 0.004), (0.0, bx + bw / 2 + 0.004)],
            POLISHED_AL, FULL)
    put(c, "Janelas da polia", ring(disc_x(0.1055, 0.1125, ax[1], ax[2] + 0.094, 0.017, n=16), ax, X, 6, 60.0, phase=30.0),
        DARK_METAL, FINE, lua=True)
    tooth = box((bx, ax[1], ax[2] + pr - 0.0005), (bw + 0.002, 0.0045, 0.003))
    put(c, "Dentes da polia", ring(tooth, ax, X, 70), POLISHED_AL, FINE, lua=True)


def belt(c, hp: Hardpoints):
    """The final belt round the gearbox pulley (FRONT_PULLEY, the engine's) and the rear one, in the plane x = BELT_X."""
    c1 = (hp.FRONT_PULLEY[1], hp.FRONT_PULLEY[2])
    c2 = (hp.REAR_AXLE[1], hp.REAR_AXLE[2])
    r1, r2 = hp.FRONT_PULLEY_R + 0.003, hp.REAR_PULLEY_R + 0.003
    dy, dz = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dy, dz)
    u = (dy / d, dz / d)
    n = (-u[1], u[0])
    sb = (r2 - r1) / d
    cb = math.sqrt(1 - sb * sb)
    a_up = math.atan2(n[1] * cb - u[1] * sb, n[0] * cb - u[0] * sb)
    a_dn = math.atan2(-n[1] * cb - u[1] * sb, -n[0] * cb - u[0] * sb)

    def at(cc, r, a):
        return (cc[0] + r * math.cos(a), cc[1] + r * math.sin(a))

    # counter-clockwise: round the front pulley (through its front), along the bottom, round the rear one, back on top
    f_end = a_dn if a_dn > a_up else a_dn + 2 * math.pi
    r_end = a_up if a_up > a_dn else a_up + 2 * math.pi
    pts = []
    for k in range(2):
        pts.append(at(c1, r1, a_up + (f_end - a_up) * k / 2) + (r1,))
    pts.append(at(c1, r1, f_end))
    for k in range(3):
        pts.append(at(c2, r2, a_dn + (r_end - a_dn) * k / 3) + (r2,))
    pts.append(at(c2, r2, r_end))
    pts.append(at(c1, r1, a_up))
    sec = [(-0.003, -hp.BELT_W / 2), (0.003, -hp.BELT_W / 2), (0.003, hp.BELT_W / 2), (-0.003, hp.BELT_W / 2)]
    nsweep(c, "Correia de transmissão", "Side", pts, hp.BELT_X, sec, RUBBER, FULL)


# --- front wheel (steered, script) --------------------------------------------------------------------------------


def front_wheel(c, hp: Hardpoints):
    sp, _ = wheel_specs(hp)
    ax = hp.FRONT_AXLE
    rb = sp["rb"]
    smooth = tyre_profile(rb, sp["rt"], sp["width"], sp["rim_w"], sp["crown"], n=16)
    grooved = tyre_profile(rb, sp["rt"], sp["width"], sp["rim_w"], sp["crown"], sp["grooves"], sp["groove_d"], n=28)
    put(c, "Pneu dianteiro", lathe(smooth, ax, X, n=56, ref=UP, closed=True), RUBBER, MEDIUM, group=STEER, in_plan=True)
    put(c, "Pneu dianteiro com sulcos", lathe(grooved, ax, X, n=64, ref=UP, closed=True), RUBBER, FINE, group=STEER, in_plan=True)
    put(c, "Aro dianteiro", lathe(rim_profile(rb, sp["rim_w"], sp["flange_h"], 0.0035, sp["well"], sp["seat"]), ax, X, n=72, ref=UP,
                                  closed=True), CHROME, FULL, group=STEER)
    coarse = [(0.0, -0.05), (0.032, -0.05), (0.032, -0.012), (rb - 0.02, -0.006), (rb - 0.02, -sp["rim_w"] / 2),
              (rb + 0.02, -sp["width"] / 2), (sp["rt"] - 0.02, -sp["width"] / 2 * 0.8), (sp["rt"], 0.0),
              (sp["rt"] - 0.02, sp["width"] / 2 * 0.8), (rb + 0.02, sp["width"] / 2), (rb - 0.02, sp["rim_w"] / 2),
              (rb - 0.02, 0.006), (0.032, 0.012), (0.032, 0.05), (0.0, 0.05)]
    put(c, "Roda dianteira (simplificada)", lathe(coarse, ax, X, n=32, ref=UP), RUBBER, COARSE, group=STEER, in_plan=True)
    put(c, "Cubo dianteiro", lathe(sp["hub"], ax, X, n=36, ref=UP), POLISHED_AL, FULL, group=STEER)
    left, right = spokes_shapes(ax, sp)
    put(c, "Raios esquerdos dianteiros", left, STAINLESS, FULL, group=STEER)
    put(c, "Raios direitos dianteiros", right, STAINLESS, FULL, group=STEER)
    put(c, "Niples dianteiros", nipples_shapes(ax, sp), CHROME, FINE, group=STEER)
    v0 = wheel_point(ax, 0.0, rb - sp["well"] - 0.003, 4.5)
    v1 = wheel_point(ax, 0.0, rb - sp["well"] - 0.030, 4.5)
    v2 = wheel_point(ax, 0.0, rb - sp["well"] - 0.044, 4.5)
    put(c, "Válvula dianteira", [cyl(v0, v1, 0.0042, n=8)], RUBBER, FINE, group=STEER)
    put(c, "Tampa da válvula dianteira", [cyl(v1, v2, 0.0040, n=8)], BRASS, FINE, group=STEER)
    # Disc (rider's left, +X): floating friction ring on a five-arm carrier with ten buttons.
    x0, x1 = 0.0595, 0.0645
    put(c, "Disco de freio dianteiro", lathe([(0.112, x0), (0.150, x0), (0.150, x1), (0.112, x1)], ax, X, n=72, ref=UP, closed=True),
        DISC_STEEL, FULL, group=STEER)
    holes = [ring(disc_x(x0 - 0.0004, x1 + 0.0004, ax[1], ax[2] + 0.124, 0.0033, n=6), ax, X, 24, 15.0),
             ring(disc_x(x0 - 0.0004, x1 + 0.0004, ax[1], ax[2] + 0.139, 0.0033, n=6), ax, X, 24, 15.0, phase=7.5)]
    put(c, "Furação do disco dianteiro", holes, DARK_METAL, FINE, group=STEER)
    carrier = []
    for k in range(90):
        th = 4.0 * k
        dmin = min(abs(((th - 72 * j + 180) % 360) - 180) for j in range(5))
        bump = 1.0 if dmin < 10 else (0.0 if dmin > 22 else 0.5 * (1 + math.cos(math.pi * (dmin - 10) / 12)))
        r = 0.050 + (0.119 - 0.050) * bump
        t = math.radians(th)
        carrier.append((r * math.cos(t), r * math.sin(t)))
    put(c, "Suporte do disco dianteiro", prism(carrier, (x0, ax[1], ax[2]), Z, (0, -1, 0), X, -0.0005, 0.0055), POLISHED_AL,
        FULL, group=STEER)
    buttons = [ring(disc_x(x0 - 0.0018, x1 + 0.0018, *wheel_point(ax, 0, 0.1145, d)[1:], 0.0058, n=10), ax, X, 5, 72.0)
               for d in (-8.5, 8.5)]
    put(c, "Botões do disco dianteiro", buttons, STAINLESS, FINE, group=STEER)
    bolt = hexagon((x1 - 0.001, ax[1], ax[2] + 0.045), (x1 + 0.005, ax[1], ax[2] + 0.045), 0.0055)
    put(c, "Parafusos do disco dianteiro", ring(bolt, ax, X, 5, 72.0, phase=36.0), CHROME, FINE, group=STEER)


# --- frame (static) ---------------------------------------------------------------------------------------------


def split_planar(points, x, per):
    """A smooth (Catmull-Rom) curve through `points`, split where it runs in a plane x = const (`x`: one value or
    several): returns [(plane x or None, [points...]), ...] with shared ends."""
    dense = catmull(points, per)
    planes = x if isinstance(x, (list, tuple)) else (x,)
    groups = []
    for q in dense:
        flat = next((px for px in planes if abs(q[0] - px) < 1e-6), None)
        if groups and groups[-1][0] == flat:
            groups[-1][1].append(q)
        else:
            if groups:
                groups[-1][1].append(q)  # overlap the joint
                groups.append((flat, [groups[-1][1][-2], q]))
            else:
                groups.append((flat, [q]))
    return [(f, pts) for f, pts in groups if len(pts) >= 2]


def frame_tube(c, name, points, x, r, per, n_mesh=12, material=FRAME_BLACK, detail=FULL, in_plan=False, mirror=True):
    """A frame tube through `points`: the stretch in the plane x is an engine sweep, the rest lean meshes."""
    sides = [(1, "esquerdo"), (-1, "direito")] if mirror else [(1, "")]
    for s, label in sides:
        pts = points if s > 0 else [mx(q) for q in points]
        meshes = []
        k = 0
        planes = [s * q for q in (x if isinstance(x, (list, tuple)) else (x,))]
        for flat, run in split_planar(pts, planes, per):
            if flat is not None and len(run) >= 2:
                k += 1
                ntube(c, f"{name} {label} {k}".replace("  ", " ").strip(), "Side", [(q[1], q[2]) for q in run], flat, r, material,
                      detail, in_plan)
            else:
                # the polygon's corners stand out and its flats sink in by the same amount: no step at the joints
                # with the exact (engine) circles of the planar runs
                meshes.append(sweep(run, circle2(r / math.sqrt(math.cos(math.pi / n_mesh)), n_mesh), caps=True))
        if meshes:
            put(c, f"{name} {label} curvas".replace("  ", " "), meshes, material, detail, in_plan)


def frame(c, hp: Hardpoints):
    F, D = hp.fork, hp.STEER_D
    hb, ht = F(0, 0, hp.W_HEAD[0]), F(0, 0, hp.W_HEAD[1])
    ncyl_side(c, "Caixa de direção", F(0, 0, 0.592), F(0, 0, 0.782), 0.029, FRAME_BLACK, FULL)
    ncyl_side(c, "Capa inferior da caixa de direção", hb, F(0, 0, 0.594), 0.033, FRAME_BLACK, FULL)
    ncyl_side(c, "Capa superior da caixa de direção", F(0, 0, 0.780), ht, 0.033, FRAME_BLACK, FULL)
    bb = catmull(hp.BACKBONE, 8)
    ntube(c, "Tubo central", "Side", [(q[1], q[2]) for q in bb], 0.0, hp.R_BACKBONE, FRAME_BLACK, FULL, in_plan=True)
    frame_tube(c, "Berço", hp.CRADLE_L, (hp.CRADLE_X, hp.UPRIGHT_X), hp.R_DOWN, 5, n_mesh=16, in_plan=True)
    frame_tube(c, "Trilho do banco", hp.SEAT_RAIL_L, hp.RAIL_X, hp.R_RAIL, 5, n_mesh=14, in_plan=True)
    put(c, "Alça traseira do quadro", sweep(catmull(hp.SEAT_LOOP, 3), circle2(hp.R_RAIL, 10)), FRAME_BLACK, FULL, in_plan=True)
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        ntube(c, f"Tirante do chassi traseiro {label}", "Side", [(q[1], q[2]) for q in hp.SEAT_STAY_L], s * hp.SEAT_STAY_L[1][0],
              0.0135, FRAME_BLACK, FULL)
    # Cross tubes.
    jy, jz = hp.J[1], hp.J[2]
    for name, x0, y, z, r in (("da junção do banco", 0.105, jy, jz, 0.021), ("dianteira do motor", 0.100, -0.447, 0.425, 0.0135),
                              ("inferior dianteira", 0.125, -0.22, 0.130, 0.0135), ("inferior traseira", 0.125, 0.06, 0.130, 0.0135),
                              ("dos trilhos do banco", 0.142, 0.50, 0.600, 0.0125)):
        ndisc_x(c, f"Travessa {name}", -x0, x0, y, z, r, FRAME_BLACK, FULL)
    # Gussets: head (between backbone and downtubes) and the lower bends.
    head_g = [(-0.400, 0.905), (-0.330, 0.905), (-0.250, 0.888), (-0.300, 0.860), (-0.395, 0.775), (-0.414, 0.758), (-0.434, 0.815)]
    nprofile(c, "Reforço da caixa de direção", "Side", head_g, -0.005, 0.010, FRAME_BLACK, FULL)
    low_g = [(-0.418, 0.275), (-0.396, 0.20), (-0.352, 0.152), (-0.300, 0.142), (-0.300, 0.150), (-0.395, 0.250)]
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        nprofile(c, f"Reforço da curva inferior {label}", "Side", low_g, s * 0.1225 - 0.002, 0.004, FRAME_BLACK, FULL)
    # Swingarm pivot plates round the uprights and the pivot boss.
    py, pz = hp.PIVOT[1], hp.PIVOT[2]
    plate = circles_hull([(0.268, 0.255, 0.028), (0.272, 0.405, 0.024), (py, pz, 0.034)], n=20)
    px0 = hp.UPRIGHT_X + 0.005  # the plates lie on the uprights' outer faces
    for s, label in ((1, "esquerda"), (-1, "direita")):
        nprofile(c, f"Placa do pivô {label}", "Side", plate, px0 if s > 0 else -px0 - 0.008, 0.008, FRAME_BLACK, FULL)
    # Engine mount lugs (front plates, head steady tab, lower and rear tabs).
    fm = hp.ENGINE_MOUNTS["front"][0]
    front_lug = circles_hull([(-0.447, 0.425, 0.020), (fm[1], fm[2], 0.016)], n=16)
    for s, label in ((1, "esquerda"), (-1, "direita")):
        nprofile(c, f"Orelha dianteira do motor {label}", "Side", front_lug, 0.088 if s > 0 else -0.094, 0.006, FRAME_BLACK, FULL)
    nprofile(c, "Orelha superior do motor", "Side", circles_hull([(-0.15, 0.855, 0.020), (-0.12, 0.832, 0.012)], n=16), -0.004, 0.008,
             FRAME_BLACK, FULL)
    for i, (x, y, z) in enumerate(hp.ENGINE_MOUNTS["lower"]):
        c.box(f"Orelha inferior do motor {i + 1}", x - 0.005, y - 0.020, z - 0.017, 0.010, 0.040, 0.034, FRAME_BLACK)
    for i, (x, y, z) in enumerate(hp.ENGINE_MOUNTS["rear"]):  # under the belt's bottom run, out to the flaring rail
        x0 = x - 0.006 if x > 0 else -0.142
        c.box(f"Orelha traseira do motor {i + 1}", x0, y - 0.018, z - 0.017, 0.142 - abs(x) + 0.006, 0.036, 0.034, FRAME_BLACK)
    for s in (1, -1):
        ndisc_x(c, f"Parafuso da orelha dianteira {'esquerdo' if s > 0 else 'direito'}", s * 0.080, s * 0.102, fm[1], fm[2], 0.0065,
                CHROME, FINE)
    # Footpeg mounts (the pegs and forward controls belong to the bodywork).
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        x0 = 0.118 if s > 0 else -0.168
        c.box(f"Suporte da pedaleira {label}", x0, hp.PEG_MOUNT_L[1] - 0.017, hp.PEG_MOUNT_L[2] - 0.020, 0.050, 0.034, 0.040, FRAME_BLACK)
    # Shock upper mounts on the seat rails.
    sy, sz = hp.SHOCK_UPPER[1], hp.SHOCK_UPPER[2]
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        ndisc_x(c, f"Suporte superior do amortecedor {label}", s * 0.140, s * 0.181, sy, sz, 0.015, FRAME_BLACK, FULL)
    # Side stand bracket under the left rail, and the spring's tab.
    sp = hp.STAND_PIVOT
    c.box("Suporte do descanso", 0.123, sp[1] - 0.030, 0.115, 0.034, 0.060, 0.014, FRAME_BLACK)
    put(c, "Bucha do descanso", cyl(v_add(sp, v_mul(hp.STAND_AXIS, -0.022)), v_add(sp, v_mul(hp.STAND_AXIS, -0.012)), 0.015, n=12),
        FRAME_BLACK, FULL)
    c.box("Orelha da mola do descanso", 0.125, 0.024, 0.108, 0.016, 0.012, 0.024, FRAME_BLACK, detail=FINE)
    # Coarse frame: the main members, flattened into their planes.
    bbc = catmull(hp.BACKBONE, 3)
    ntube(c, "Quadro (simplificado) central", "Side", [(q[1], q[2]) for q in bbc], 0.0, 0.025, FRAME_BLACK, COARSE, in_plan=True)
    cr = catmull(hp.CRADLE_L, 2)
    rl = catmull(hp.SEAT_RAIL_L + hp.SEAT_LOOP[1:3], 2)
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        ntube(c, f"Quadro (simplificado) {label}", "Side", [(q[1], q[2]) for q in cr], s * 0.115, 0.02, FRAME_BLACK, COARSE, in_plan=True)
        ntube(c, f"Chassi traseiro (simplificado) {label}", "Side", [(q[1], q[2]) for q in rl], s * 0.14, 0.017, FRAME_BLACK, COARSE)


# --- swingarm and shocks (static) --------------------------------------------------------------------------------------


def rear_suspension(c, hp: Hardpoints):
    py, pz = hp.PIVOT[1], hp.PIVOT[2]
    ra = hp.REAR_AXLE
    sx = hp.SWINGARM_X
    pw = hp.UPRIGHT_X + 0.005  # between the frame's pivot plates
    ndisc_x(c, "Tubo do pivô da balança", -pw, pw, py, pz, 0.026, FRAME_BLACK, FULL)
    # legs: horizontal, so each is an engine sweep in the plan at the pivot's height
    leg = [{"u": "0.110", "v": f"{py + 0.008:.4f}", "bezier": {"u1": "0.125", "v1": f"{py + 0.10:.4f}", "u2": f"{sx:.4f}",
                                                               "v2": f"{py + 0.14:.4f}"}},
           (sx, py + 0.25), (sx, ra[1] - 0.06)]
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        pts = leg if s > 0 else [{"u": "-0.110", "v": leg[0]["v"], "bezier": {"u1": "-0.125", "v1": leg[0]["bezier"]["v1"],
                                                                                "u2": f"{-sx:.4f}", "v2": leg[0]["bezier"]["v2"]}},
                                 (-sx, py + 0.25), (-sx, ra[1] - 0.06)]
        ntube(c, f"Braço da balança {label}", "Plan", pts, pz, hp.R_SWINGARM, FRAME_BLACK, FULL, in_plan=True)
    ndisc_x(c, "Travessa da balança", -0.150, 0.150, 0.445, pz, 0.016, FRAME_BLACK, FULL)
    # Axle plates with the adjusters.
    drop = [(u + ra[1] - 0.015, v + ra[2]) for u, v in rrect2(0.135, 0.050, 0.018, 3)]
    for s, label in ((1, "esquerda"), (-1, "direita")):
        nprofile(c, f"Ponteira da balança {label}", "Side", drop, s * sx - 0.007, 0.014, FRAME_BLACK, FULL)
        c.box(f"Rasgo do eixo traseiro {label}", s * (sx + 0.0072) - 0.0005, ra[1] - 0.025, ra[2] - 0.007, 0.001, 0.07, 0.014, DARK_METAL,
              detail=FINE)
        y0 = ra[1] + 0.053
        c.box(f"Bloco do esticador {label}", s * sx - 0.008, y0, ra[2] - 0.015, 0.016, 0.012, 0.030, CHROME, detail=FINE)
        c.cyl_y(f"Parafuso do esticador {label}", s * sx, ra[2], ra[1] + 0.012, 0.0045, y0 + 0.040 - ra[1] - 0.012, CHROME, detail=FINE)
        for k, (ya, yb, r) in enumerate(((y0 + 0.012, y0 + 0.020, 0.0075), (y0 + 0.032, y0 + 0.038, 0.0068))):
            nprofile(c, f"Porca do esticador {label} {k + 1}", "Front", [(s * sx + r * math.cos(math.radians(60 * i)), ra[2] + r * math.sin(math.radians(60 * i)))
                                                                        for i in range(6)], ya, yb - ya, CHROME, FINE)
    # Rear axle with nuts and spacers.
    ndisc_x(c, "Eixo traseiro", -0.192, 0.192, ra[1], ra[2], 0.0125, CHROME, FULL)
    ndisc_x(c, "Espaçador esquerdo do eixo traseiro", 0.114, 0.157, ra[1], ra[2], 0.018, CHROME, FULL)
    ndisc_x(c, "Espaçador direito do eixo traseiro", -0.157, -0.110, ra[1], ra[2], 0.018, CHROME, FULL)
    for s, label in ((1, "esquerda"), (-1, "direita")):
        nhex_x(c, f"Porca do eixo traseiro {label}", s * 0.173, s * 0.188, ra[1], ra[2], 0.0195, CHROME, FINE)
    # Pivot bolt.
    ndisc_x(c, "Parafuso do pivô", -(pw + 0.022), pw + 0.022, py, pz, 0.010, CHROME, FINE)
    for s, label in ((1, "esquerda"), (-1, "direita")):
        nhex_x(c, f"Porca do pivô {label}", s * (pw + 0.008), s * (pw + 0.021), py, pz, 0.0175, CHROME, FINE)
    rear_caliper(c, hp)
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        shock(c, hp, s, label)
    # Coarse: swingarm and shocks.
    for s, label in ((1, "esquerdo"), (-1, "direito")):
        ntube(c, f"Balança (simplificada) {label}", "Plan", [(s * 0.12, py), (s * sx, py + 0.2), (s * sx, ra[1])], pz, 0.02, FRAME_BLACK,
              COARSE, in_plan=True)
        lo, up = hp.SHOCK_LOWER, hp.SHOCK_UPPER
        ncyl_side(c, f"Amortecedor (simplificado) {label}", (s * lo[0], lo[1], lo[2]), (s * up[0], up[1], up[2]), 0.034, CHROME, COARSE)


def shock(c, hp, s, label):
    lo = (s * hp.SHOCK_LOWER[0], hp.SHOCK_LOWER[1], hp.SHOCK_LOWER[2])
    up = (s * hp.SHOCK_UPPER[0], hp.SHOCK_UPPER[1], hp.SHOCK_UPPER[2])
    length = v_len(v_sub(up, lo))
    ax = v_norm(v_sub(up, lo))

    def at(h):
        return v_add(lo, v_mul(ax, h))

    # a stack of round parts along the axis (all in the plane x = const: engine sweeps)
    for name, h0, h1, r, mat, det in (
            ("Corpo", 0.016, 0.168, 0.0205, CHROME, FULL), ("Base", 0.010, 0.026, 0.0150, CHROME, FULL),
            ("Haste", 0.160, length - 0.040, 0.0078, CHROME, FULL), ("Prato inferior da mola", 0.046, 0.058, 0.0370, POLISHED_AL, FULL),
            ("Anel de regulagem", 0.040, 0.046, 0.0300, POLISHED_AL, FINE),
            ("Tampa superior", length - 0.062, length - 0.048, 0.0370, CHROME, FULL), ("Cúpula", length - 0.048, length - 0.030, 0.0280, CHROME, FULL),
            ("Pescoço superior", length - 0.032, length - 0.012, 0.0140, CHROME, FULL)):
        ncyl_side(c, f"{name} do amortecedor {label}", at(h0), at(h1), r, mat, det)
    put(c, f"Mola do amortecedor {label}", spring(at(0.058), at(length - 0.062), 0.0305, 0.0058, 7.5, per_turn=12, n=8, ref=X),
        CHROME, FULL, lua=True)
    for end, name in ((lo, "inferior"), (up, "superior")):
        ndisc_x(c, f"Olhal {name} do amortecedor {label}", end[0] - 0.013, end[0] + 0.013, end[1], end[2], 0.0165, CHROME, FULL)
        ndisc_x(c, f"Bucha {name} do amortecedor {label}", end[0] - 0.0135, end[0] + 0.0135, end[1], end[2], 0.0095, RUBBER, FINE)
        nhex_x(c, f"Porca {name} do amortecedor {label}", end[0] + s * 0.0135, end[0] + s * 0.021, end[1], end[2], 0.012, CHROME, FINE)
    # lower mount stub on the swingarm leg
    sx = hp.SWINGARM_X
    ndisc_x(c, f"Pino inferior do amortecedor {label}", s * (sx + 0.010), s * (abs(lo[0]) - 0.012), lo[1], lo[2], 0.0125, FRAME_BLACK, FULL)
    c.box(f"Suporte inferior do amortecedor {label}", s * (sx + 0.010) - 0.005, lo[1] - 0.017, hp.PIVOT[2], 0.010, 0.034, lo[2] - hp.PIVOT[2],
          FRAME_BLACK)


def rear_caliper(c, hp):
    ra = hp.REAR_AXLE
    xd = -0.105
    nprofile(c, "Pinça do freio traseiro", "Side", nannulus_sector(ra[1], ra[2], 0.107, 0.149, 196, 236), xd - 0.023, 0.046, POLISHED_AL, FULL)
    nprofile(c, "Ponte da pinça traseira", "Side", nannulus_sector(ra[1], ra[2], 0.147, 0.153, 198, 234), xd - 0.025, 0.050, POLISHED_AL, FINE)
    b1 = (ra[1] + 0.128 * math.cos(math.radians(192)), ra[2] + 0.128 * math.sin(math.radians(192)))
    b2 = (ra[1] + 0.128 * math.cos(math.radians(240)), ra[2] + 0.128 * math.sin(math.radians(240)))
    outline = circles_hull([(ra[1], ra[2], 0.024), (b1[0], b1[1], 0.014), (b2[0], b2[1], 0.014)], n=16)
    nprofile(c, "Suporte da pinça traseira", "Side", outline, -0.142, 0.008, FRAME_BLACK, FULL)
    ntube(c, "Tirante do freio traseiro", "Side", [(ra[1] - 0.10, ra[2] - 0.040), (ra[1] - 0.20, ra[2] - 0.016), (ra[1] - 0.25, ra[2] - 0.016)],
          -0.150, 0.007, FRAME_BLACK, FULL)
    for i, b in enumerate((b1, b2)):
        nhex_x(c, f"Parafuso da pinça traseira {i + 1}", -0.142, -0.150, b[0], b[1], 0.0075, CHROME, FINE)
    # hose from the caliper towards the rear master cylinder (right forward control, BRAKE_PEDAL)
    # (under the right swingarm leg, down behind the upright, under the rear engine lug, over the flaring rail and
    # forward along the top of the lower rail's outer side, then up to the master cylinder's banjo)
    start = (-0.118, ra[1] + 0.14 * math.cos(math.radians(214)), ra[2] + 0.14 * math.sin(math.radians(214)))
    sx = hp.SWINGARM_X
    hose = [start, (-0.140, ra[1] - 0.045, 0.262), (-sx, ra[1] - 0.14, 0.298), (-sx, 0.55, 0.304), (-sx, 0.43, 0.304),
            (-0.150, 0.35, 0.290), (-0.134, 0.305, 0.250), (-0.120, 0.270, 0.190), (-0.112, 0.235, 0.151), (-0.112, 0.200, 0.153),
            (-0.124, 0.160, 0.166), (-0.142, 0.120, 0.163), (-0.150, 0.06, 0.150), (-0.150, -0.20, 0.149), (-0.152, -0.285, 0.158), (-0.162, -0.315, 0.230),
            (-0.17, -0.33, 0.30)]
    put(c, "Mangueira do freio traseiro", sweep(catmull(hose, 4), circle2(0.0045, 8)), RUBBER, FULL, lua=True)


# --- front end (steered, script) ------------------------------------------------------------------------------------


def caliper_arc(axle, x, r, psi0, psi1, width, height, n=8):
    """A caliper body: a rounded section swept along an arc of radius r (psi: degrees from +y towards +z) at x."""
    pts = []
    for i in range(n + 1):
        t = math.radians(psi0 + (psi1 - psi0) * i / n)
        pts.append((x, axle[1] + r * math.cos(t), axle[2] + r * math.sin(t)))
    return sweep(pts, rrect2(width, height, min(width, height) * 0.3, 2), up=X)


def caliper_point(axle, x, r, psi):
    t = math.radians(psi)
    return (x, axle[1] + r * math.cos(t), axle[2] + r * math.sin(t))


def front_end(c, hp: Hardpoints):
    F, D, V = hp.fork, hp.STEER_D, hp.FORK_V
    fx, off = hp.FORK_X, hp.OFFSET
    fa = hp.FRONT_AXLE
    sliders, stanchions, wipers, caps, bosses = [], [], [], [], []
    for s in (1, -1):
        base = F(s * fx, off, 0.0)
        sliders.append(lathe([(0, -0.050), (0.016, -0.050), (0.025, -0.044), (0.030, -0.032), (0.031, -0.010), (0.031, 0.320),
                              (0.0325, 0.326), (0.0325, 0.352), (0.029, 0.362), (0, 0.362)], base, D, n=28))
        sliders.append(disc_x(s * (fx - 0.034), s * (fx + 0.030), fa[1], fa[2], 0.0235, n=20))
        stanchions.append(cyl(F(s * fx, off, 0.300), F(s * fx, off, 0.852), hp.R_STANCHION, n=28))
        wipers.append(lathe([(0.0244, 0.360), (0.0298, 0.360), (0.0298, 0.368), (0.0270, 0.378), (0.0244, 0.381)], base, D, n=28,
                            closed=True))
        caps.append(lathe([(0, 0.850), (0.0235, 0.850), (0.0235, 0.856), (0.0205, 0.866), (0.012, 0.871), (0, 0.872)], base, D, n=24))
        for w in (0.09, 0.21):
            bosses.append(cyl(F(s * (fx - 0.026), off, w), F(s * (fx - hp.R_SLIDER - 0.007), off, w), 0.0085, n=10))
    put(c, "Bainhas do garfo", sliders, POLISHED_AL, FULL, group=STEER)
    put(c, "Tubos do garfo", stanchions, CHROME, FULL, group=STEER, in_plan=True)
    put(c, "Retentores do garfo", wipers, RUBBER, FULL, group=STEER)
    put(c, "Tampas do garfo", caps, CHROME, FULL, group=STEER)
    put(c, "Suportes do para-lama dianteiro", bosses, POLISHED_AL, FULL, group=STEER)
    pinch = []
    for s in (1, -1):
        for dx in (-0.016, 0.016):
            x = s * fx + dx
            pinch.append(hexagon((x, fa[1] - 0.020, fa[2] - 0.018), (x, fa[1] - 0.030, fa[2] - 0.018), 0.0065))
    put(c, "Parafusos das bainhas", pinch, CHROME, FINE, group=STEER)
    # Triple clamps: outlines round the fork tubes and the stem, waisted between them.
    lower = clamp_outline(fx, off, 0.042, 0.036, 0.020)
    upper = clamp_outline(fx, off, 0.039, 0.033, 0.016)
    put(c, "Mesa inferior", prism(lower, hp.FORK_O, X, V, D, *hp.W_LOWER_CLAMP), POLISHED_AL, FULL, group=STEER)
    put(c, "Mesa superior", prism(upper, hp.FORK_O, X, V, D, *hp.W_UPPER_CLAMP), POLISHED_AL, FULL, group=STEER, in_plan=True)
    clamp_bolts = []
    for s in (1, -1):
        for w in (sum(hp.W_LOWER_CLAMP) / 2, sum(hp.W_UPPER_CLAMP) / 2):
            p0, p1 = F(s * (fx + 0.012), off - 0.040, w), F(s * (fx + 0.046), off - 0.040, w)
            clamp_bolts.append(cyl(p0, p1, 0.0045, n=8))
            clamp_bolts.append(hexagon(p1, v_add(p1, (s * 0.007, 0, 0)), 0.0075))
    put(c, "Parafusos das mesas", clamp_bolts, CHROME, FINE, group=STEER)
    put(c, "Coluna de direção", cyl(F(0, 0, 0.520), F(0, 0, 0.800), 0.0185, n=16), CHROME, FULL, group=STEER)
    put(c, "Porca da coluna de direção", [cyl(F(0, 0, 0.832), F(0, 0, 0.836), 0.026, n=20),
                                           hexagon(F(0, 0, 0.836), F(0, 0, 0.852), 0.024, ref=V)], CHROME, FULL, group=STEER)
    risers = []
    for s in (1, -1):
        u = s * hp.RISER_U
        risers.append(lathe([(0, 0.832), (0.019, 0.832), (0.019, 0.838), (0.0155, 0.845), (0.0155, 0.884), (0, 0.884)],
                            F(u, hp.RISER_V, 0), D, n=20))
        risers.append(box(F(u, hp.RISER_V, 0.900), (0.030, 0.040, 0.034), (X, V, D)))
        risers.append(lathe([(0, -0.015), (0.020, -0.015), (0.020, 0.015), (0, 0.015)], F(u, hp.RISER_V, 0.905), X, n=20))
    put(c, "Elevadores do guidão", risers, CHROME, FULL, group=STEER)
    rb = [hexagon(F(s * hp.RISER_U, hp.RISER_V + dv, 0.921), F(s * hp.RISER_U, hp.RISER_V + dv, 0.928), 0.0055, ref=X)
          for s in (1, -1) for dv in (-0.012, 0.012)]
    put(c, "Parafusos das capas do guidão", rb, CHROME, FINE, group=STEER)
    put(c, "Eixo dianteiro", [disc_x(-0.150, 0.150, fa[1], fa[2], 0.0125, n=16), disc_x(0.074, 0.082, fa[1], fa[2], 0.017, n=16),
                              disc_x(-0.082, -0.074, fa[1], fa[2], 0.017, n=16)], CHROME, FULL, group=STEER)
    put(c, "Porcas do eixo dianteiro", [hexagon((0.145, fa[1], fa[2]), (0.160, fa[1], fa[2]), 0.0185),
                                         hexagon((-0.145, fa[1], fa[2]), (-0.158, fa[1], fa[2]), 0.0185)], CHROME, FINE, group=STEER)
    front_caliper(c, hp)
    co = [cyl(F(s * fx, off, -0.04), F(s * fx, off, 0.86), 0.028, n=10) for s in (1, -1)]
    co += [prism(upper[::2], hp.FORK_O, X, V, D, *hp.W_LOWER_CLAMP), prism(upper[::2], hp.FORK_O, X, V, D, *hp.W_UPPER_CLAMP)]
    put(c, "Garfo (simplificado)", co, POLISHED_AL, COARSE, group=STEER, in_plan=True)


def clamp_outline(fx, off, r_tube, r_stem, waist):
    """A triple clamp's outline (u across, v forward): the hull of round bosses at the fork tubes and the stem,
    waisted front and back between them."""
    hull = circles_hull([(fx, off, r_tube), (-fx, off, r_tube), (0.0, 0.0, r_stem)], n=24)
    dense = []
    for i, p in enumerate(hull):
        q = hull[(i + 1) % len(hull)]
        k = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) / 0.006))
        dense += [(p[0] + (q[0] - p[0]) * j / k, p[1] + (q[1] - p[1]) * j / k) for j in range(k)]
    vm = off / 2
    out = []
    for u, v in dense:
        t = min(abs(u) / fx, 1.0)
        pull = waist * (1 - t * t) ** 2 * (0.3 if v > vm else 1.0)  # the front edge stays nearly straight
        out.append((u, v - math.copysign(pull, v - vm)))
    return out


def front_caliper(c, hp: Hardpoints):
    fa = hp.FRONT_AXLE
    F, D = hp.fork, hp.STEER_D
    xd = 0.062
    put(c, "Pinça do freio dianteiro", caliper_arc(fa, xd, 0.128, -4, 30, 0.048, 0.042), POLISHED_AL, FULL, group=STEER)
    put(c, "Ponte da pinça dianteira", caliper_arc(fa, xd, 0.150, -2, 28, 0.052, 0.006, n=6), POLISHED_AL, FINE, group=STEER)
    b1, b2 = caliper_point(fa, 0.088, 0.128, -8), caliper_point(fa, 0.088, 0.128, 34)
    lugs = []
    for b in (b1, b2):
        base = F(hp.FORK_X, hp.OFFSET, 0)
        on_axis = v_add(base, v_mul(D, v_dot(v_sub(b, base), D)))
        lugs.append(sweep([v_add(on_axis, (-0.012, 0, 0)), b], rrect2(0.016, 0.022, 0.006, 2), up=X))
        lugs.append(cyl(v_add(b, (-0.010, 0, 0)), v_add(b, (0.012, 0, 0)), 0.0105, n=14))
    put(c, "Orelhas da pinça dianteira", lugs, POLISHED_AL, FULL, group=STEER)
    bolts = [hexagon(v_add(b, (0.012, 0, 0)), v_add(b, (0.020, 0, 0)), 0.0078) for b in (b1, b2)]
    bolts.append(cyl(caliper_point(fa, 0.078, 0.146, 22), caliper_point(fa, 0.090, 0.152, 22), 0.0032, n=6))  # bleed nipple
    bolts.append(cyl(caliper_point(fa, 0.036, 0.142, 10), caliper_point(fa, 0.088, 0.142, 10), 0.0028, n=6))  # pad pin
    put(c, "Parafusos da pinça dianteira", bolts, CHROME, FINE, group=STEER)
    hose = [caliper_point(fa, 0.084, 0.150, 20), F(hp.FORK_X + 0.012, hp.OFFSET - 0.045, 0.16), F(hp.FORK_X + 0.008, hp.OFFSET - 0.050, 0.40),
            F(0.07, -0.040, hp.W_LOWER_CLAMP[0] - 0.01), F(0.07, -0.016, hp.W_LOWER_CLAMP[0] + 0.02), F(0.055, 0.062, 0.645),
            F(-0.060, 0.070, 0.705), F(-0.085, 0.115, 0.790), F(-0.100, 0.100, 0.860),
            v_add(hp.BAR_CLAMP, (-0.13, 0.002, -0.014)), v_add(hp.BAR_CLAMP, (-0.20, 0.01, -0.025))]
    # (behind the lower clamp's waist, across in front of the head tube between the clamps, up in front of the upper
    # clamp and under the bar: ahead of the steering axis, so it swings away from the tank)
    put(c, "Mangueira do freio dianteiro", sweep(catmull(hose, 5), circle2(0.0045, 8)), RUBBER, FULL, group=STEER)
    clips = [cyl(F(hp.FORK_X + 0.003, hp.OFFSET - 0.042, w - 0.007), F(hp.FORK_X + 0.003, hp.OFFSET - 0.042, w + 0.007), 0.0075, n=8)
             for w in (0.16, 0.30)]
    put(c, "Presilhas da mangueira", clips, BLACK_PLASTIC, FINE, group=STEER)


# --- side stand (script) ----------------------------------------------------------------------------------------------


def stand(c, hp: Hardpoints):
    """The side stand, modelled down (Descanso = 1) and turned up about its pivot by the script."""
    P, Fo = hp.STAND_PIVOT, hp.STAND_FOOT
    knee = v_add(v_lerp(P, Fo, 0.55), (0.012, -0.010, 0.0))
    foot_top = v_add(Fo, (0, 0, 0.012))
    leg = sweep(catmull([P, knee, foot_top], 5), circle2(0.0115, 12))
    put(c, "Perna do descanso", [leg, cyl(v_add(P, v_mul(hp.STAND_AXIS, -0.012)), v_add(P, v_mul(hp.STAND_AXIS, 0.016)), 0.0145, n=16)],
        FRAME_BLACK, FULL, group=STAND)
    put(c, "Sapata do descanso", box((Fo[0], Fo[1], 0.006), (0.050, 0.036, 0.012)), FRAME_BLACK, FULL, group=STAND)
    t0 = v_lerp(P, Fo, 0.28)
    put(c, "Pedal do descanso", sweep([t0, v_add(t0, (0.045, -0.020, 0.012)), v_add(t0, (0.065, -0.028, 0.022))], circle2(0.0065, 8)),
        FRAME_BLACK, FINE, group=STAND)
    tab = v_lerp(P, Fo, 0.16)
    put(c, "Orelha da mola na perna", box(v_add(tab, (-0.010, 0.0, 0.006)), (0.012, 0.012, 0.020)), FRAME_BLACK, FINE, group=STAND)
    put(c, "Mola do descanso", spring(v_add(tab, (-0.014, 0.0, 0.010)), (0.133, 0.030, 0.118), 0.0055, 0.0012, 14, ga=STAND, per_turn=8,
                                       n=4), STAINLESS, FINE)
    put(c, "Pino do descanso", hexagon(v_add(P, v_mul(hp.STAND_AXIS, 0.016)), v_add(P, v_mul(hp.STAND_AXIS, 0.024)), 0.009),
        CHROME, FINE, group=STAND)
