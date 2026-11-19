r"""Skeleton of the custom motorcycle (`moto_custom`): hardpoints, materials and the 3D geometry helpers.

Every part module (`chassi`, `motor`, `carroceria`) has `add(c, hp)`: `c` is the
`MotoComponent` (a kit.Component) and `hp` the `Hardpoints` below. They build on
the numbers published here and need not read each other's code.

FRAME OF REFERENCE (meters): front of the bike towards -Y (front wheel at
negative y), X across (centre plane x = 0; +X is the RIDER'S LEFT, the side of
the side stand and of the final belt; -X the rider's right, the exhaust side),
Z up, tyres on z = 0, origin on the ground under the middle of the wheelbase.
The bike stands upright.

SIDE VIEW from the left (+X), front to the left (z up, y to the right):

  z
 1.16 |                 grips .-~~-.  (bar pulled back, grips at y -0.15..-0.11)
 1.00 |       head top o====' TANK  `-._                  SEAT
 0.90 |     headlight (O)\ \___________  `-.___      __.--~~-.
 0.80 |      fork tubes  \ \  backbone ~~~~~~~~~--. /   0.68  \__ rear loop
 0.70 |                   \ \  /\ /\  (V-twin)    J\__seat rails___===-- tail light
 0.60 |                    \ \/ fr \/ re\          |\     /shock     \ fender
 0.50 |   downtubes ------->\|  cyl   cyl |  gear  | \   / (twin)     \
 0.40 |       .--.           |\ crank  ___|  box   |  \ /  .--.        \
 0.30 |     /  .  \ axle F   | \(C)___/   |_______(P)==swingarm=( . )  axle R
 0.20 |    |  ( )  |         |  sump   stand        |         |     |
 0.13 |     \  '  /          '-- lower cradle rails -'          \   /
 0.00 +------'--'---------------------------------------------'-'------------ y
     -0.83  (front axle)       -0.12 (crank)      0.31 (pivot)  0.83 (rear axle)

  Steering: axis through STEER_G on the ground, tilted back by RAKE; the front
  axle is OFFSET ahead of it and the tyre's contact patch TRAIL behind G.

HARDPOINTS (attributes of `Hardpoints`, numbers in m; points are (x, y, z) in
the neutral pose: AnguloGuidao = 0, Descanso = 0):

  name                value                               what
  WHEELBASE           1.665                               axle to axle
  FRONT_AXLE          (0, -0.8325, 0.3477)                90/90-21 tyre, R_F 0.3477
  REAR_AXLE           (0,  0.8325, 0.3292)                180/70B16 tyre, R_R 0.3292
  R_F, W_F / R_R, W_R tyre outer radius / section width   0.3477, 0.090 / 0.3292, 0.180
  RIM_F, RIM_R        bead-seat radius                    0.2667 (21") / 0.2032 (16")
  RAKE, TRAIL, OFFSET 32 deg, 0.150, 0.0570               steering geometry (OFFSET: axle ahead of the axis)
  STEER_G, STEER_D    (0, -0.9825, 0), (0, 0.5299, 0.8480) steering axis: point on the ground, unit dir (up, back)
  FORK_O, FORK_V      (0, -0.7841, 0.3175), (0, -0.8480, 0.5299)  axis point nearest the axle; forward-up normal
  fork(u, v, w)       FORK_O + u*X + v*FORK_V + w*STEER_D (fork coordinates; front axle = fork(0, OFFSET, 0))
  FORK_X              0.115                               half spacing of the fork tube centres (v = OFFSET)
  R_STANCHION/SLIDER  0.0245 / 0.031                      W_SLIDER (-0.045, 0.37), W_STANCHION (0.30, 0.858)
  W_HEAD              (0.582, 0.792)                      head tube ends along the axis (w)
  HEAD_BOTTOM/TOP     (0, -0.4757, 0.8110) / (0, -0.3644, 0.9891)
  W_LOWER_CLAMP       (0.535, 0.575)                      lower triple clamp (w); bottom centre (0, -0.5006, 0.7712)
  W_UPPER_CLAMP       (0.800, 0.832)                      upper triple clamp (w); top centre (0, -0.3432, 1.0230)
  RISER_U, RISER_V    +-0.045, -0.005                     risers on the upper clamp up to w 0.925 (drawn by chassi)
  BAR_CLAMP           (0, -0.3003, 1.0823) = fork(0, -0.005, 0.905)  handlebar clamp centre (bar along X)
  HANDLEBAR, BAR_R    polyline left end -> right end, r 0.0127  1" pulled-back bar (to be drawn by the bodywork)
  GRIP_L / GRIP_R     (+-0.285, -0.1503, 1.1603) -> (+-0.41, -0.1103, 1.1543)  grip spans (inboard, outboard end)
  HEADLIGHT, _DIR     (0, -0.6305, 0.9408) = fork(0, 0.20, 0.61), facing -Y  lamp body centre; mount on the lower clamp
  FENDER_F_MOUNTS     (+-0.080, -0.7848, 0.4240), (+-0.080, -0.7212, 0.5258)  bosses on the sliders' inner faces
  FENDER_F_INNER      R_F + 0.025 about FRONT_AXLE; fender half width <= 0.075 (between the sliders)
  CRANK               (0, -0.12, 0.29)                    crank axis (along X)
  V_ANGLE             48 deg, symmetric about vertical    CYL_FRONT / CYL_REAR = (CRANK, (0, -+0.4067, 0.9135))
  CYL_LEN             0.40                                crank axis to the top of a rocker box
  ENGINE_BOX          x -0.14..0.14, y -0.37..0.06, z 0.12..0.70   crankcase + cylinders (between the cradles)
  GEARBOX_BOX         x -0.11..0.12, y 0.04..0.27, z 0.16..0.45   in fact two blocks: the main one y 0.04..0.20 up to
                      z 0.434, the rear one (output shaft) y 0.04..0.266 below z 0.30 only, so the box's corner
                      y 0.20..0.27 above z 0.30 is free: it belongs to UNDERSEAT_ENV (the oil lines rise there)
  PRIMARY_BOX         x 0.10..0.20, y -0.22..0.18, z 0.15..0.42   (left side; stay above z 0.15: retracted stand)
  BELT_X, BELT_W      0.120, 0.028                        final belt plane (drawn by chassi round both pulleys)
  FRONT_PULLEY        (0.120, 0.20, 0.30), pitch r 0.0668 gearbox output pulley: the ENGINE part draws it
                      (flanges x 0.1035..0.1365, r 0.0713; nut to x 0.1455). The belt runs between the gearbox and
                      the left upright (UPRIGHT_X), and inboard of the left swingarm leg (inner face x 0.146)
  REAR_PULLEY_R       0.156                               on the rear hub (chassi), x 0.106..0.137
  ENGINE_MOUNTS       front (+-0.098, -0.40, 0.40) x2, top (0, -0.12, 0.838), lower (+-0.105, -0.22|0.02, 0.15) x4,
                      rear (+-0.110, 0.225, 0.180) x2     frame lugs/plates the engine bolts to (the rear lugs run out
                      to the flaring lower rails under the belt's bottom run)
  EXHAUST_ENV         x -0.32..-0.12, y -0.45..1.12, z 0.16..0.62  right side; ports from the CYL_* heads
  PIVOT               (0, 0.31, 0.33)                     swingarm pivot axis (along X); pivot tube x +-0.170 between
                      the frame's pivot plates at x +-0.170..0.178 (on the uprights' outer faces)
  SWINGARM_X          0.165                               leg centre lines (r 0.019, horizontal at z 0.33)
  SHOCK_UPPER/LOWER   (+-0.195, 0.58, 0.635) / (+-0.195, 0.74, 0.35)  eye centres
  BACKBONE            polyline head -> J, tube r 0.0254   (0, -0.25, 0.90), (0, -0.02, 0.828), (0, 0.10, 0.76) ...
  J                   (0, 0.20, 0.625)                    seat-post junction (cross tube x -0.105..0.105, r 0.021)
  CRADLE_L, CRADLE_X  left cradle polyline (mirror for the right); planar at x +-0.125 from z 0.42 down the
                      downtube and along the lower rail (z 0.13) to y 0.10; tube r 0.019
  UPRIGHT_X           0.165: behind the gearbox the rails flare out and the uprights stand at x +-0.165 (y ~0.27,
                      z 0.19..0.39), outboard of the belt and front pulley, then turn back in to J above z 0.45
  SEAT_RAIL_L, RAIL_X left seat rail J -> (0.142, 0.90, 0.708), r 0.016, planar at x +-0.142 from y 0.45;
  SEAT_STAY_L         stay from the rail (y 0.585) down to the upright (y 0.284, z 0.398), planar at x +-0.142;
  SEAT_LOOP           the rear loop joining the rails, up to y 1.026 at z 0.729
  TANK_ENV            x -0.16..0.16, y -0.40..0.09, z 0.775..1.04 (tunnel over the backbone)
  SEAT_H, SEAT_LOW    0.68 at (0, 0.25, 0.68)             solo seat; SEAT_ENV x +-0.17, y 0.07..0.47, z 0.60..0.76
  UNDERSEAT_ENV       x -0.11..0.11, y 0.20..0.47, z 0.30..0.57  (oil tank y 0.29..0.40 and battery y 0.41..0.46 at
                      z 0.45..0.57; below them only the oil lines, up the front at y ~0.28, ahead of the pivot tube)
  FENDER_R_INNER      R_R + 0.030 about REAR_AXLE; FENDER_R_HALF_W 0.12 (rails at +-0.142)
  TAIL_LIGHT, PLATE   (0, 1.07, 0.70), (0, 1.176, 0.561)     plate 200 x 170 mm facing back, its face at y 1.176
  PEG_L / PEG_R       (+-0.30, -0.37, 0.33)               forward-control pegs; brackets (frame) end at x +-0.168
  PEG_MOUNT_L/R       (+-0.118, -0.40, 0.25)              bracket roots on the downtubes
  BRAKE_PEDAL, SHIFTER  (-0.24, -0.37, 0.33) / (0.24, -0.37, 0.33)  forward-control pivots (right / left)
  STAND_PIVOT, _FOOT  (0.160, -0.10, 0.115), (0.40, -0.22, 0.012)  side stand (rider's left); STAND_AXIS,
                      STAND_SWING 112.5 deg: modelled down, turned up by (Descanso - 1) * SWING

INSTANCE PARAMETERS: AnguloGuidao (deg, + turns the front wheel to the rider's
left, +X; the script clamps it to +-45, real lock about +-35; open pose 25) and
Descanso (0 retracted .. 1 down). Turning the bars lifts the front tyre 5 mm at
25 deg (the frame stays put).

GEOMETRY. The engine draws Box, Cylinder, Extrusion, Profile, Revolution, Sweep
and Blend only in its three principal planes (a Sweep's path is planar, a
Revolution has no axis along X, nothing can be tilted out of its plane), a
`Mesh` takes numeric vertices only, and a Lua `Script` piece builds any piece
(meshes included) from the parameter values. So:

  * static parts lying in a principal plane -> engine shapes (`nsweep`, `ntube`,
    `nring_x`, `nprofile`, `ndisc_x`...): exact arcs, small in the file;
  * static parts curved in 3D -> numeric `Mesh` pieces from the Python kernel
    below (`put` with group None). They cost ~140 bytes per vertex in the
    pretty-printed .ccomp: keep them lean;
  * parts that move with an instance parameter (everything on the steering
    head, the side stand, cables/springs between moving and fixed parts) and
    small many-vertex fine details (`put(..., lua=True)`) -> the one Lua
    `Script` piece, whose kernel (LUA_KERNEL, a port of the Python one) builds
    the same shapes and turns them about the steering axis by AnguloGuidao or
    about the stand pivot by Descanso. Shapes are sent as their parameters,
    not as vertices.

LIMITS measured on this engine build (budget against them):
  * script source <= 256 KiB (262144 bytes; refused above);
  * script run: 20 M Lua instructions. The kernel passes ~66 k vertices and fails
    by ~85 k (all detail levels count: the script returns every level at once).
    A failed script shows NOTHING of the script's pieces. Keep the whole bike's
    script <= 60 k vertices; the chassis uses ~20 k (see preview.py's stats);
  * script pieces do not draw in plans even with in_plan (hence `plan_only`
    stand-ins whose corners follow the steering through `steer_expr`), and the
    web viewer does not render them;
  * one script piece per component;
  * the .ccomp keeps only the materials its pieces name, and a script piece's own pieces are not
    seen: MotoComponent.source() adds, for each material only script pieces use, a holder piece
    shown at no detail level (it never draws), so any material can be used in the script.

API: build shapes with `lathe`, `sweep`, `tube`, `cyl`, `disc_x`, `hexagon`, `box`,
`prism`, `sphere`, `ring`, `spring`, `gtube` (each returns a `Shape`; `.mx()`
mirrors it about x = 0, `.moved()`, `.turned()`), then write a piece with
`put(c, name, shapes, material, detail, in_plan, group, lua=False)`: group None
= static, STEER = steered, STAND = side stand. Native shapes: `nsweep`, `ntube`,
`ncyl_side`, `nring_x`, `nprofile`, `ndisc_x`, `nhex_x`, `nannulus_sector`.
Steering of points: `hp.steer(p, deg)` (numbers), `steer_expr(p)` (expressions).
"""

from __future__ import annotations

import math
import kit
from kit import ALL, FULL, FINE, COARSE  # noqa: F401  (re-exported for the part modules)

MEDIUM = "m"
MF = FULL  # medium and fine
STEER = "steer"
STAND = "stand"

# --- vectors ---------------------------------------------------------------------


def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def v_len(a):
    return math.sqrt(v_dot(a, a))


def v_norm(a):
    n = v_len(a)
    return (0.0, 0.0, 1.0) if n < 1e-12 else (a[0] / n, a[1] / n, a[2] / n)


def v_lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def mx(p):
    """The point (or vector) mirrored about x = 0."""
    return (-p[0], p[1], p[2])


def perp(a):
    """A unit vector normal to `a`."""
    t = (1.0, 0.0, 0.0) if abs(a[0]) < 0.9 else (0.0, 1.0, 0.0)
    return v_norm(v_cross(v_cross(a, t), a))


def rotate(p, o, axis, deg):
    """The point p turned by `deg` about the axis through o with direction `axis` (right hand)."""
    k = v_norm(axis)
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    v = v_sub(p, o)
    kv = v_cross(k, v)
    kd = v_dot(k, v)
    return tuple(o[i] + v[i] * c + kv[i] * s + k[i] * kd * (1 - c) for i in range(3))


def rotate_vec(v, axis, deg):
    return rotate(v, (0.0, 0.0, 0.0), axis, deg)


# --- curves ----------------------------------------------------------------------


def catmull(points, per=6, closed=False):
    """A dense polyline through `points` (3D tuples), rounded by Catmull-Rom; ends kept."""
    pts = [tuple(map(float, q)) for q in points]
    n = len(pts)
    if n < 3:
        return pts
    out = []
    segs = n if closed else n - 1
    for i in range(segs):
        if closed:
            p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        else:
            p1, p2 = pts[i], pts[i + 1]
            p0 = pts[i - 1] if i > 0 else v_sub(v_mul(p1, 2), p2)
            p3 = pts[i + 2] if i + 2 < n else v_sub(v_mul(p2, 2), p1)
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            w0 = 0.5 * (-t + 2 * t2 - t3)
            w1 = 0.5 * (2 - 5 * t2 + 3 * t3)
            w2 = 0.5 * (t + 4 * t2 - 3 * t3)
            w3 = 0.5 * (-t2 + t3)
            out.append(tuple(p0[j] * w0 + p1[j] * w1 + p2[j] * w2 + p3[j] * w3 for j in range(3)))
    if not closed:
        out.append(pts[-1])
    return out


def bezier3(p0, p1, p2, p3, n=12, first=True):
    """Points of the cubic Bézier p0 -> p3 with handles p1, p2."""
    out = []
    for i in range(0 if first else 1, n + 1):
        t = i / n
        w = ((1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3)
        out.append(tuple(p0[j] * w[0] + p1[j] * w[1] + p2[j] * w[2] + p3[j] * w[3] for j in range(3)))
    return out


def arc3(center, e1, e2, r, a0, a1, n=12):
    """Points of a circular arc of radius r about `center` in the plane of the unit vectors e1, e2 (degrees)."""
    out = []
    for i in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * i / n)
        out.append(v_add(center, v_add(v_mul(e1, r * math.cos(t)), v_mul(e2, r * math.sin(t)))))
    return out


def circle2(r, n=12, phase=0.0):
    """A circular section (u, v) of radius r."""
    return [(r * math.cos(2 * math.pi * i / n + phase), r * math.sin(2 * math.pi * i / n + phase)) for i in range(n)]


def rrect2(w, h, r, n=4):
    """A rounded rectangle section w x h (centred), corner radius r, n points per corner."""
    r = min(r, w / 2 - 1e-5, h / 2 - 1e-5)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def ellipse2(a, b, n=16):
    return [(a * math.cos(2 * math.pi * i / n), b * math.sin(2 * math.pi * i / n)) for i in range(n)]


def hull2(points):
    """Convex hull (counter-clockwise) of 2D points."""
    pts = sorted(set((round(p[0], 7), round(p[1], 7)) for p in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def circles_hull(circles, n=24):
    """Outline (u, v) round several circles [(cu, cv, r), ...]: their convex hull."""
    pts = []
    for cu, cv, r in circles:
        pts += [(cu + r * math.cos(2 * math.pi * i / n), cv + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return hull2(pts)


# --- hardpoints ---------------------------------------------------------------------


class Hardpoints:
    """The bike's skeleton (see the module docstring for the table). All numbers, neutral pose."""

    def __init__(self):
        r = math.radians
        self.WHEELBASE = 1.665
        # Tyres: 90/90-21 front, 180/70B16 rear (outer radius = bead radius + section height).
        self.RIM_F, self.RIM_R = 0.5334 / 2, 0.4064 / 2
        self.W_F, self.W_R = 0.090, 0.180
        self.R_F = self.RIM_F + 0.90 * self.W_F
        self.R_R = self.RIM_R + 0.70 * self.W_R
        self.RIM_W_F, self.RIM_W_R = 0.0546, 0.1143  # 21 x 2.15, 16 x 4.5
        self.FRONT_AXLE = (0.0, -self.WHEELBASE / 2, self.R_F)
        self.REAR_AXLE = (0.0, self.WHEELBASE / 2, self.R_R)
        # Steering geometry.
        self.RAKE = 32.0
        self.TRAIL = 0.150
        rk = r(self.RAKE)
        self.STEER_D = (0.0, math.sin(rk), math.cos(rk))
        self.FORK_V = (0.0, -math.cos(rk), math.sin(rk))
        self.STEER_G = (0.0, self.FRONT_AXLE[1] - self.TRAIL, 0.0)
        s_axle = v_dot(v_sub(self.FRONT_AXLE, self.STEER_G), self.STEER_D)
        self.FORK_O = v_add(self.STEER_G, v_mul(self.STEER_D, s_axle))
        self.OFFSET = v_dot(v_sub(self.FRONT_AXLE, self.FORK_O), self.FORK_V)
        self.STEER_LOCK = 35.0
        # Front end, in fork coordinates (w along the axis from FORK_O).
        self.FORK_X = 0.115
        self.R_STANCHION, self.R_SLIDER = 0.0245, 0.031
        self.W_SLIDER = (-0.045, 0.370)
        self.W_STANCHION = (0.300, 0.858)
        self.W_LOWER_CLAMP = (0.535, 0.575)
        self.W_HEAD = (0.582, 0.792)
        self.W_UPPER_CLAMP = (0.800, 0.832)
        self.HEAD_BOTTOM = self.fork(0, 0, self.W_HEAD[0])
        self.HEAD_TOP = self.fork(0, 0, self.W_HEAD[1])
        self.RISER_U, self.RISER_V = 0.045, -0.005
        self.BAR_CLAMP = self.fork(0, self.RISER_V, 0.905)
        self.HEADLIGHT = self.fork(0, 0.20, 0.61)
        self.HEADLIGHT_DIR = (0.0, -1.0, 0.0)
        self.FENDER_F_MOUNTS = [self.fork(s * (self.FORK_X - self.R_SLIDER - 0.004), self.OFFSET, w) for w in (0.09, 0.21) for s in (1, -1)]
        bc = self.BAR_CLAMP
        # Pulled-back 1" bar: straight centre, rising sweep back, straight grip sections (last span).
        half = [(0.0, 0.0, 0.0), (0.08, 0.0, 0.0), (0.15, 0.015, 0.02), (0.21, 0.06, 0.055), (0.255, 0.12, 0.075),
                (0.285, 0.150, 0.078), (0.41, 0.19, 0.072)]
        right = [v_add(bc, (-x, y, z)) for x, y, z in half]
        left = [v_add(bc, (x, y, z)) for x, y, z in half]
        self.HANDLEBAR = list(reversed(left)) + right[1:]
        self.BAR_R = 0.0127
        # Grips: (inboard start, outboard end) of each end's straight span.
        self.GRIP_L = (left[-2], left[-1])
        self.GRIP_R = (right[-2], right[-1])
        # Engine (air-cooled V-twin, 48 degrees, symmetric about vertical).
        self.CRANK = (0.0, -0.12, 0.29)
        self.V_ANGLE = 48.0
        h = r(self.V_ANGLE / 2)
        self.CYL_FRONT = (self.CRANK, (0.0, -math.sin(h), math.cos(h)))
        self.CYL_REAR = (self.CRANK, (0.0, math.sin(h), math.cos(h)))
        self.CYL_LEN = 0.40
        self.ENGINE_BOX = ((-0.14, -0.37, 0.12), (0.14, 0.06, 0.70))
        self.GEARBOX_BOX = ((-0.11, 0.04, 0.16), (0.12, 0.27, 0.45))
        self.PRIMARY_BOX = ((0.10, -0.22, 0.15), (0.20, 0.18, 0.42))
        self.BELT_X = 0.120
        self.BELT_W = 0.028
        self.FRONT_PULLEY = (self.BELT_X, 0.20, 0.30)
        self.FRONT_PULLEY_R = 0.0668
        self.REAR_PULLEY_R = 0.156
        self.EXHAUST_ENV = ((-0.32, -0.45, 0.16), (-0.12, 1.12, 0.62))
        # Frame.
        self.R_BACKBONE, self.R_DOWN, self.R_RAIL = 0.0254, 0.019, 0.016
        self.J = (0.0, 0.20, 0.625)
        self.BACKBONE = [self.fork(0, -0.018, 0.735), (0.0, -0.25, 0.900), (0.0, -0.02, 0.828), (0.0, 0.10, 0.760), (0.0, 0.165, 0.680), self.J]
        self.CRADLE_X = 0.125  # the cradle runs in the planes x = +-CRADLE_X from z ~0.4 on the downtube along the lower rail
        # The uprights behind the gearbox flare out to x = +-UPRIGHT_X, outboard of the final belt and its front pulley
        # (the belt runs between the gearbox and the left upright), and turn back in above the belt's top run.
        self.UPRIGHT_X = 0.165
        ux = self.UPRIGHT_X
        self.CRADLE_L = [  # one side's downtube -> lower rail -> upright -> J cross tube (left, +x)
            self.fork(0.024, -0.025, 0.645), self.fork(0.050, -0.085, 0.565), (0.110, -0.436, 0.545), (0.125, -0.440, 0.420),
            (0.125, -0.428, 0.300), (0.125, -0.395, 0.190), (0.125, -0.315, 0.135), (0.125, -0.15, 0.130), (0.125, 0.0, 0.130),
            (0.125, 0.10, 0.130), (0.140, 0.208, 0.148), (ux, 0.247, 0.190), (ux, 0.266, 0.240), (ux, 0.274, 0.320),
            (ux, 0.273, 0.390), (0.148, 0.266, 0.450), (0.127, 0.252, 0.510), (0.112, 0.235, 0.568), (0.095, 0.208, 0.612)]
        self.RAIL_X = 0.142  # seat rails run in the planes x = +-RAIL_X from y 0.45 to 0.90
        self.SEAT_RAIL_L = [(0.092, 0.200, 0.622), (0.125, 0.255, 0.600), (0.142, 0.33, 0.594), (0.142, 0.45, 0.598),
                            (0.142, 0.60, 0.638), (0.142, 0.78, 0.682), (0.142, 0.90, 0.708)]
        self.SEAT_LOOP = [(0.142, 0.90, 0.708), (0.135, 0.975, 0.721), (0.10, 1.012, 0.727), (0.0, 1.026, 0.729),
                          (-0.10, 1.012, 0.727), (-0.135, 0.975, 0.721), (-0.142, 0.90, 0.708)]
        self.SEAT_STAY_L = [(0.142, 0.585, 0.632), (0.142, 0.44, 0.52), (0.142, 0.284, 0.398)]  # planar at x +-0.142
        self.PIVOT = (0.0, 0.31, 0.33)
        self.SWINGARM_X = 0.165
        self.R_SWINGARM = 0.019
        self.SHOCK_X = 0.195
        self.SHOCK_UPPER = (self.SHOCK_X, 0.58, 0.635)
        self.SHOCK_LOWER = (self.SHOCK_X, 0.74, 0.35)
        self.ENGINE_MOUNTS = {
            "front": [(s * 0.098, -0.40, 0.40) for s in (1, -1)],
            "top": [(0.0, -0.12, 0.838)],
            "lower": [(s * 0.105, y, 0.15) for y in (-0.22, 0.02) for s in (1, -1)],
            "rear": [(s * 0.110, 0.225, 0.180) for s in (1, -1)],  # below the belt's bottom run
        }
        # Bodywork envelopes.
        self.TANK_ENV = ((-0.16, -0.40, 0.775), (0.16, 0.09, 1.04))
        self.SEAT_H = 0.68
        self.SEAT_LOW = (0.0, 0.25, self.SEAT_H)
        self.SEAT_ENV = ((-0.17, 0.07, 0.60), (0.17, 0.47, 0.76))
        self.UNDERSEAT_ENV = ((-0.11, 0.20, 0.30), (0.11, 0.47, 0.57))
        self.FENDER_R_INNER = self.R_R + 0.030
        self.FENDER_R_HALF_W = 0.12
        self.FENDER_F_INNER = self.R_F + 0.025
        self.TAIL_LIGHT = (0.0, 1.07, 0.70)
        self.PLATE = (0.0, 1.176, 0.561)
        self.PEG_L, self.PEG_R = (0.30, -0.37, 0.33), (-0.30, -0.37, 0.33)
        self.PEG_MOUNT_L, self.PEG_MOUNT_R = (0.118, -0.40, 0.25), (-0.118, -0.40, 0.25)
        self.BRAKE_PEDAL = (-0.24, -0.37, 0.33)
        self.SHIFTER = (0.24, -0.37, 0.33)
        # Side stand (designed down; turned up by Descanso).
        self.STAND_PIVOT = (0.160, -0.10, 0.115)
        self.STAND_FOOT = (0.40, -0.22, 0.012)
        u1 = v_norm(v_sub(self.STAND_FOOT, self.STAND_PIVOT))
        u0 = v_norm((0.10, 1.0, 0.03))  # retracted: back along the lower rail, outboard of its flare
        self.STAND_AXIS = v_norm(v_cross(u0, u1))
        self.STAND_SWING = math.degrees(math.acos(max(-1.0, min(1.0, v_dot(u0, u1)))))
        self.STAND_RETRACTED_DIR = u0

    # --- frames -----------------------------------------------------------------
    def fork(self, u, v, w):
        """World point (neutral pose) of the fork coordinates (u across = x, v forward normal to the axis, w up the axis)."""
        return v_add(v_add(self.FORK_O, (u, 0.0, 0.0)), v_add(v_mul(self.FORK_V, v), v_mul(self.STEER_D, w)))

    def fork_vec(self, u, v, w):
        return v_add((u, 0.0, 0.0), v_add(v_mul(self.FORK_V, v), v_mul(self.STEER_D, w)))

    def steer(self, p, deg):
        """Numeric: the neutral-pose point p turned with the steering by `deg`."""
        return rotate(p, self.STEER_G, self.STEER_D, deg)

    def stand(self, p, descanso):
        """Numeric: the point p of the stand (modelled down) at Descanso = descanso."""
        return rotate(p, self.STAND_PIVOT, self.STAND_AXIS, (descanso - 1.0) * self.STAND_SWING)


HP = Hardpoints()


def steer_expr(p, param="AnguloGuidao", hp: Hardpoints = HP):
    """(x, y, z) expressions of the neutral-pose point p turned with the steering (for native pieces).

    Rodrigues' rotation about STEER_D through STEER_G by the parameter, written out with numbers.
    Native shapes can follow it only by their points (a Profile or Revolution keeps its plane), so
    use it for points of small parts; meshes go through `put(..., group=STEER)`.
    """
    k, o = hp.STEER_D, hp.STEER_G
    v = v_sub(p, o)
    kv = v_cross(k, v)
    kd = v_dot(k, v)
    out = []
    for i in range(3):
        a = v[i] - k[i] * kd  # * cos
        b = kv[i]  # * sin
        c0 = o[i] + k[i] * kd
        out.append(f"{_n(c0)} + {_n(a)}*cos({param}) + {_n(b)}*sin({param})")
    return tuple(out)


def _n(v: float) -> str:
    t = f"{v:.6f}".rstrip("0").rstrip(".")
    t = "0" if t in ("", "-0") else t
    return f"({t})" if t.startswith("-") else t


# --- materials ---------------------------------------------------------------------

# The bike's palette: PALETTE names where one fits, new names (checked unused in the library) otherwise.
CHROME = "Cromado"
CAST_AL = "Alumínio fundido"
POLISHED_AL = "Alumínio polido"
FRAME_BLACK = "Pintura preta automotiva"
ENGINE_BLACK = "Pintura preta texturizada"
TANK_PAINT = "Pintura vinho metálico"
ACCENT = "Filete dourado"
RUBBER = "Borracha"
LEATHER = "Couro preto"
LENS_RED = "Lente vermelha"
LENS_AMBER = "Lente âmbar"
LENS_CLEAR = "Lente cristal"
DISC_STEEL = "Disco de freio"
BRASS = "Latão"
STAINLESS = "Inox escovado"
DARK_METAL = "Ferro fundido"
BLACK_PLASTIC = "Plástico preto"
STEEL_BLACK = "Aço pintado preto"

NEW_MATERIALS = {
    POLISHED_AL: ((214, 217, 221), "Metal", "Polished", 0),
    FRAME_BLACK: ((14, 14, 16), "Metal", "Glossy", 0),
    ENGINE_BLACK: ((30, 30, 32), "Metal", "Matte", 0),
    TANK_PAINT: ((96, 12, 28), "Metal", "Glossy", 0),
    ACCENT: ((206, 166, 82), "Metal", "Glossy", 0),
    LEATHER: ((28, 23, 21), "Generic", "Satin", 0),
    LENS_RED: ((196, 24, 28), "Glass", "Glossy", 0.25),
    LENS_AMBER: ((236, 138, 32), "Glass", "Glossy", 0.25),
    LENS_CLEAR: ((238, 244, 248), "Glass", "Polished", 0.92),
    DISC_STEEL: ((150, 152, 156), "Metal", "Satin", 0),
}


def declare_materials(c):
    for name, (color, cls, finish, tr) in NEW_MATERIALS.items():
        if name not in c.extra_materials:
            c.material(name, color, cls, finish, tr)


# --- the Python mesh kernel ---------------------------------------------------------------


class Mesh:
    """Vertices and polygon faces (0-based, counter-clockwise seen from outside)."""

    def __init__(self):
        self.v: list[tuple] = []
        self.f: list[list[int]] = []

    def vtx(self, p) -> int:
        self.v.append((float(p[0]), float(p[1]), float(p[2])))
        return len(self.v) - 1

    def poly(self, ids):
        out = []
        for i in ids:
            if not out or out[-1] != i:
                out.append(i)
        while len(out) > 1 and out[0] == out[-1]:
            out.pop()
        if len(set(out)) >= 3:
            self.f.append(out)

    def orient(self, f0: int):
        """Turn the faces from f0 on outwards (positive signed volume)."""
        vol = 0.0
        for fc in self.f[f0:]:
            a = self.v[fc[0]]
            for j in range(1, len(fc) - 1):
                vol += v_dot(a, v_cross(self.v[fc[j]], self.v[fc[j + 1]]))
        if vol < 0:
            self.f[f0:] = [list(reversed(fc)) for fc in self.f[f0:]]

    def extend(self, other: "Mesh"):
        base = len(self.v)
        self.v += other.v
        self.f += [[i + base for i in fc] for fc in other.f]

    def shape(self, digits=4) -> dict:
        def r(x):
            y = round(x, digits)
            return 0.0 if y == 0 else y
        return {"Mesh": {"vertices": [[r(a), r(b), r(c)] for a, b, c in self.v], "faces": self.f}}

    def bounds(self):
        xs, ys, zs = zip(*self.v)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def _frame_vectors(a, ref):
    a = v_norm(a)
    if ref is None:
        e1 = perp(a)
    else:
        e1 = v_norm(v_sub(ref, v_mul(a, v_dot(ref, a))))
    return a, e1, v_cross(a, e1)


def _rows_faces(m: Mesh, rows, wrap_rows: bool, wrap_cols: bool):
    nr = len(rows)
    for j in range(nr if wrap_rows else nr - 1):
        r1, r2 = rows[j], rows[(j + 1) % nr]
        cnt = len(r1)
        for i in range(cnt if wrap_cols else cnt - 1):
            i2 = (i + 1) % cnt
            m.poly([r1[i], r1[i2], r2[i2], r2[i]])


def k_lathe(m: Mesh, s: dict):
    f0 = len(m.f)
    a, e1, e2 = _frame_vectors(s["a"], s.get("ref"))
    n, a0, a1 = s["n"], s.get("a0", 0.0), s.get("a1", 360.0)
    full = (a1 - a0) >= 359.999
    cnt = n if full else n + 1
    rows = []
    for rr, hh in s["prof"]:
        c = v_add(s["o"], v_mul(a, hh))
        if rr < 1e-7:
            idx = m.vtx(c)
            rows.append([idx] * cnt)
            continue
        row = []
        for i in range(cnt):
            t = math.radians(a0 + (a1 - a0) * i / n)
            row.append(m.vtx(v_add(c, v_add(v_mul(e1, rr * math.cos(t)), v_mul(e2, rr * math.sin(t))))))
        rows.append(row)
    closed = s.get("closed", False)
    _rows_faces(m, rows, closed, full)
    if not closed and full:  # flat discs closing ends off the axis (start reversed, end in order)
        if s["prof"][0][0] >= 1e-7:
            m.poly(list(reversed(rows[0])))
        if s["prof"][-1][0] >= 1e-7:
            m.poly(list(rows[-1]))
    if not full:  # flat ends: fans from the profile's centroid
        np_ = len(rows)
        cr = sum(q[0] for q in s["prof"]) / np_
        ch = sum(q[1] for q in s["prof"]) / np_
        for i in (0, cnt - 1):
            t = math.radians(a0 + (a1 - a0) * i / n)
            cc = m.vtx(v_add(v_add(s["o"], v_mul(a, ch)), v_add(v_mul(e1, cr * math.cos(t)), v_mul(e2, cr * math.sin(t)))))
            ring = [rows[j][i] for j in range(np_)]
            for j in range(np_ if closed else np_ - 1):
                if i == 0:
                    m.poly([cc, ring[j], ring[(j + 1) % np_]])
                else:
                    m.poly([cc, ring[(j + 1) % np_], ring[j]])
    m.orient(f0)


def _tangents(path, closed):
    n = len(path)
    out = []
    for i in range(n):
        if closed:
            a, b = path[(i - 1) % n], path[(i + 1) % n]
            d1 = v_norm(v_sub(path[i], a))
            d2 = v_norm(v_sub(b, path[i]))
            out.append(v_norm(v_add(d1, d2)))
        elif i == 0:
            out.append(v_norm(v_sub(path[1], path[0])))
        elif i == n - 1:
            out.append(v_norm(v_sub(path[-1], path[-2])))
        else:
            d1 = v_norm(v_sub(path[i], path[i - 1]))
            d2 = v_norm(v_sub(path[i + 1], path[i]))
            out.append(v_norm(v_add(d1, d2)))
    return out


def rmf(path, closed=False, up=None):
    """Rotation-minimising frames (t, r, s) along a polyline (double reflection)."""
    n = len(path)
    ts = _tangents(path, closed)
    t0 = ts[0]
    if up is not None and v_len(v_sub(up, v_mul(t0, v_dot(up, t0)))) > 1e-6:
        r0 = v_norm(v_sub(up, v_mul(t0, v_dot(up, t0))))
    else:
        r0 = perp(t0)
    rs = [r0]
    steps = n if closed else n - 1
    for i in range(steps):
        x0, x1 = path[i], path[(i + 1) % n]
        t_0, t_1 = ts[i], ts[(i + 1) % n]
        v1 = v_sub(x1, x0)
        c1 = v_dot(v1, v1)
        ri = rs[-1]
        if c1 < 1e-16:
            rs.append(ri)
            continue
        rl = v_sub(ri, v_mul(v1, 2 / c1 * v_dot(v1, ri)))
        tl = v_sub(t_0, v_mul(v1, 2 / c1 * v_dot(v1, t_0)))
        v2 = v_sub(t_1, tl)
        c2 = v_dot(v2, v2)
        rn = rl if c2 < 1e-16 else v_sub(rl, v_mul(v2, 2 / c2 * v_dot(v2, rl)))
        rs.append(v_norm(v_sub(rn, v_mul(t_1, v_dot(rn, t_1)))))
    if closed:  # spread the twist left after going round
        end = rs[-1]
        s0 = v_cross(ts[0], rs[0])
        ang = math.atan2(v_dot(end, s0), v_dot(end, rs[0]))
        rs = rs[:-1]
        rs = [rotate_vec(rs[i], ts[i], -ang * i / n * 180 / math.pi) for i in range(n)]
    return [(ts[i], rs[i], v_cross(ts[i], rs[i])) for i in range(n)]


def k_sweep(m: Mesh, s: dict):
    f0 = len(m.f)
    path = [tuple(q) for q in s["path"]]
    closed = s.get("closed", False)
    frames = rmf(path, closed, s.get("up"))
    sec = s["sec"]
    scale = s.get("scale")  # optional per-point section scale
    rows = []
    for i, (x, (t, rr, ss)) in enumerate(zip(path, frames)):
        k = scale[i] if scale else 1.0
        rows.append([m.vtx(v_add(x, v_add(v_mul(rr, u * k), v_mul(ss, v * k)))) for u, v in sec])
    _rows_faces(m, rows, closed, True)
    if not closed and s.get("caps", True):
        m.poly(list(reversed(rows[0])))
        m.poly(list(rows[-1]))
    m.orient(f0)


def k_box(m: Mesh, s: dict):
    f0 = len(m.f)
    c, (U, V, W), (hu, hv, hw) = s["c"], s["ax"], s["h"]
    ids = {}
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                ids[(i, j, k)] = m.vtx(v_add(c, v_add(v_mul(U, i * hu), v_add(v_mul(V, j * hv), v_mul(W, k * hw)))))
    for fc in (((-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1)), ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)),
               ((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)), ((-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)),
               ((-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)), ((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1))):
        m.poly([ids[q] for q in fc])
    m.orient(f0)


def k_prism(m: Mesh, s: dict):
    """A star-shaped outline (u, v) in the plane (o, U, V) extruded along W from w0 to w1."""
    f0 = len(m.f)
    o, U, V, W = s["o"], s["U"], s["V"], s["W"]
    out = s["out"]
    cu = sum(q[0] for q in out) / len(out)
    cv = sum(q[1] for q in out) / len(out)

    def at(u, v, w):
        return v_add(o, v_add(v_mul(U, u), v_add(v_mul(V, v), v_mul(W, w))))

    rows = [[m.vtx(at(u, v, w)) for u, v in out] for w in (s["w0"], s["w1"])]
    _rows_faces(m, rows, False, True)
    for k, (row, w) in enumerate(zip(rows, (s["w0"], s["w1"]))):
        c = m.vtx(at(cu, cv, w))
        for j in range(len(row)):
            if k == 0:
                m.poly([c, row[(j + 1) % len(row)], row[j]])
            else:
                m.poly([c, row[j], row[(j + 1) % len(row)]])
    m.orient(f0)


def helix_path(a, b, r, turns, per_turn=16, ref=None):
    """Points of a helix of radius r round the segment a -> b."""
    ax, e1, e2 = _frame_vectors(v_sub(b, a), ref)
    length = v_len(v_sub(b, a))
    n = max(4, int(turns * per_turn))
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * turns * t
        pts.append(v_add(v_add(a, v_mul(ax, length * t)), v_add(v_mul(e1, r * math.cos(ang)), v_mul(e2, r * math.sin(ang)))))
    return pts


def k_ring(m: Mesh, s: dict):
    """`count` copies of `part` turned by `step` degrees each (from `phase`) about the axis (o, a)."""
    for i in range(s["count"]):
        v0 = len(m.v)
        s["part"].mesh_into(m)
        ang = s.get("phase", 0.0) + s["step"] * i
        for j in range(v0, len(m.v)):
            m.v[j] = rotate(m.v[j], s["o"], s["a"], ang)


KERNELS = {"lathe": k_lathe, "sweep": k_sweep, "box": k_box, "prism": k_prism, "ring": k_ring}


# --- shapes ------------------------------------------------------------------------------


class Shape:
    """A shape to be meshed: `kind` and its arguments (points as 3-tuples, vectors, numbers)."""

    POINTS = {"lathe": ("o",), "sweep": (), "box": ("c",), "prism": ("o",), "spring": (), "gtube": (), "ring": ("o",)}
    VECTORS = {"lathe": ("a", "ref"), "sweep": ("up",), "box": (), "prism": ("U", "V", "W"), "spring": ("ref",), "gtube": ("up",),
               "ring": ("a",)}

    def __init__(self, kind, **args):
        self.kind, self.args = kind, args

    def map(self, fp, fv) -> "Shape":
        a = dict(self.args)
        for k in self.POINTS[self.kind]:
            if a.get(k) is not None:
                a[k] = fp(a[k])
        for k in self.VECTORS[self.kind]:
            if a.get(k) is not None:
                a[k] = fv(a[k])
        if self.kind == "sweep":
            a["path"] = [fp(q) for q in a["path"]]
        if self.kind == "box":
            a["ax"] = [fv(q) for q in a["ax"]]
        if self.kind in ("spring",):
            a["a"], a["b"] = (fp(a["a"][0]), a["a"][1]), (fp(a["b"][0]), a["b"][1])
        if self.kind == "gtube":
            a["pts"] = [(fp(q), g) for q, g in a["pts"]]
        if self.kind == "ring":
            a["part"] = a["part"].map(fp, fv)
            ex, ey, ez = fv((1.0, 0.0, 0.0)), fv((0.0, 1.0, 0.0)), fv((0.0, 0.0, 1.0))
            if v_dot(ex, v_cross(ey, ez)) < 0:  # a mirror turns the other way
                a["step"], a["phase"] = -a["step"], -a.get("phase", 0.0)
        return Shape(self.kind, **a)

    def mx(self) -> "Shape":
        """Mirrored about x = 0."""
        return self.map(mx, mx)

    def moved(self, d) -> "Shape":
        return self.map(lambda q: v_add(q, d), lambda q: q)

    def turned(self, o, axis, deg) -> "Shape":
        """Turned rigidly about the axis through o."""
        return self.map(lambda q: rotate(q, o, axis, deg), lambda q: rotate_vec(q, axis, deg))

    # Python meshing (static: every group is the neutral pose)
    def mesh_into(self, m: Mesh):
        if self.kind in KERNELS:
            KERNELS[self.kind](m, self.args)
        elif self.kind == "spring":
            a, b = self.args["a"][0], self.args["b"][0]
            path = helix_path(a, b, self.args["r"], self.args["turns"], self.args.get("per_turn", 16), self.args.get("ref"))
            k_sweep(m, {"path": path, "sec": circle2(self.args["wire"], self.args.get("n", 8)), "caps": True})
        elif self.kind == "gtube":
            path = catmull([q for q, _ in self.args["pts"]], self.args.get("per", 6))
            k_sweep(m, {"path": path, "sec": circle2(self.args["r"], self.args.get("n", 10)), "caps": True, "up": self.args.get("up")})
        else:
            raise ValueError(self.kind)

    def lua(self) -> str:
        args = {k: v for k, v in self.args.items() if v is not None}
        if self.kind == "ring":
            part = args.pop("part")
            return _lua_value({"k": "ring", **args})[:-1] + f", part = {part.lua()}}}"
        return _lua_value({"k": self.kind, **args})


def lathe(profile, origin, axis, n=48, ref=None, closed=False, a0=0.0, a1=360.0) -> Shape:
    """A profile [(r, h), ...] (r from the axis, h along it from `origin`) turned about the axis.

    `closed` joins the last point to the first (a ring: tyre, rim). Open profiles get flat
    caps at ends off the axis; points on the axis (r = 0) close the solid. a0..a1 turns part of it
    (angles from `ref`, the direction of angle 0, about `axis`).
    """
    return Shape("lathe", prof=[(float(r), float(h)) for r, h in profile], o=tuple(origin), a=tuple(axis), n=n,
                 ref=tuple(ref) if ref is not None else None, closed=closed, a0=a0, a1=a1)


def sweep(path, section, closed=False, caps=True, up=None, scale=None) -> Shape:
    """A closed section [(u, v), ...] carried along a 3D polyline (rotation-minimising frames).

    u lies along the frame's normal (towards `up` at the start when given), v along the binormal.
    """
    return Shape("sweep", path=[tuple(q) for q in path], sec=[(float(u), float(v)) for u, v in section], closed=closed,
                 caps=caps, up=tuple(up) if up is not None else None, scale=scale)


def tube(path, r, n=12, closed=False, caps=True, smooth=0, up=None) -> Shape:
    """A round tube along a 3D polyline; `smooth` > 0 rounds it through the points (Catmull-Rom, that many per span)."""
    pts = catmull(path, smooth, closed) if smooth else list(path)
    if closed and smooth:
        pts = pts[:]
    return sweep(pts, circle2(r, n), closed=closed, caps=caps, up=up)


def cyl(p0, p1, r, n=24) -> Shape:
    """A cylinder from p0 to p1."""
    length = v_len(v_sub(p1, p0))
    return lathe([(0, 0), (r, 0), (r, length), (0, length)], p0, v_sub(p1, p0), n=n)


def disc_x(x0, x1, y, z, r, n=32) -> Shape:
    """A cylinder along X (a disc, a boss, an axle) from x0 to x1 at (y, z)."""
    return cyl((x0, y, z), (x1, y, z), r, n)


def hexagon(p0, p1, r, ref=None) -> Shape:
    """A hex nut/bolt head from p0 to p1, r across corners."""
    length = v_len(v_sub(p1, p0))
    return lathe([(0, 0), (r, 0), (r, length), (0, length)], p0, v_sub(p1, p0), n=6, ref=ref)


def box(center, size, axes=((1, 0, 0), (0, 1, 0), (0, 0, 1))) -> Shape:
    """A box of `size` (along the three unit `axes`) centred on `center`."""
    ax = [v_norm(a) for a in axes]
    return Shape("box", c=tuple(center), ax=ax, h=(size[0] / 2, size[1] / 2, size[2] / 2))


def prism(outline, origin, U, V, W, w0, w1) -> Shape:
    """A star-shaped outline [(u, v), ...] in the plane (origin, U, V) extruded along W from w0 to w1."""
    return Shape("prism", out=[(float(u), float(v)) for u, v in outline], o=tuple(origin), U=tuple(U), V=tuple(V), W=tuple(W),
                 w0=float(w0), w1=float(w1))


def sphere(center, r, n=16, axis=(0, 0, 1)) -> Shape:
    prof = [(r * math.sin(math.pi * i / n), -r * math.cos(math.pi * i / n)) for i in range(n + 1)]
    prof[0], prof[-1] = (0.0, -r), (0.0, r)
    return lathe(prof, center, axis, n=2 * n)


def spring(a, b, r, wire, turns, ga=None, gb=None, per_turn=16, n=8, ref=None) -> Shape:
    """A coil spring round the segment a -> b; `ga`/`gb` are the groups each end moves with (None = fixed)."""
    return Shape("spring", a=(tuple(a), ga), b=(tuple(b), gb), r=r, wire=wire, turns=turns, per_turn=per_turn, n=n,
                 ref=tuple(ref) if ref is not None else None)


def ring(part: Shape, origin, axis, count, step=None, phase=0.0) -> Shape:
    """`count` copies of `part`, each turned `step` degrees (default 360/count) further about the axis (origin, axis)."""
    return Shape("ring", part=part, o=tuple(origin), a=tuple(axis), count=int(count),
                 step=float(step if step is not None else 360.0 / count), phase=float(phase))


def gtube(points, r, n=10, per=6, up=None) -> Shape:
    """A smooth round tube (cable, hose) through [(point, group), ...]: each point moves with its group."""
    return Shape("gtube", pts=[(tuple(q), g) for q, g in points], r=r, n=n, per=per, up=tuple(up) if up is not None else None)


# --- writing pieces ---------------------------------------------------------------------------


class MotoComponent(kit.Component):
    """A kit.Component that also gathers the Lua-built (moving) pieces into one script piece."""

    SCRIPT_PIECE = "Partes móveis (script)"

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.lua_pieces: list[str] = []
        self.lua_names: set[str] = set()
        self.lua_materials: list[str] = []
        self.lua_stats = {"coarse": 0, "medium": 0, "fine": 0, "pieces": 0, "vertices": 0}
        self.mesh_vertices = 0  # of the static numeric meshes

    def lua_source(self, hp: Hardpoints = HP) -> str:
        head = (
            f"local STEER_O = {_lua_value(hp.STEER_G)}\nlocal STEER_D = {_lua_value(hp.STEER_D)}\n"
            f"local STEER_LOCK = {_lua_num(hp.STEER_LOCK + 10)}\n"
            f"local STAND_O = {_lua_value(hp.STAND_PIVOT)}\nlocal STAND_D = {_lua_value(hp.STAND_AXIS)}\n"
            f"local STAND_SWING = {_lua_num(hp.STAND_SWING)}\n"
        )
        body = "local PIECES = {\n" + ",\n".join(self.lua_pieces) + "\n}\n"
        return LUA_HEADER + head + LUA_KERNEL + body + LUA_MAIN

    # Where the material holders sit: a 5 mm cube deep inside the crankcase (never drawn anyway).
    HOLDER_AT = (0.0, -0.12, 0.22)

    def source(self) -> dict:
        src = super().source()
        if self.lua_pieces:
            have = {m["name"] for m in src["materials"]}
            static_users = {i["material"] for i in src["def"]["items"]}
            for name in self.lua_materials:
                if name not in static_users and name not in kit.TEMPLATE_MATERIALS:
                    # The engine saves to the .ccomp only the materials its pieces name; a script piece's
                    # material is invisible to it, so a material that only script pieces use would be
                    # dropped and those pieces would render white. Each such material is declared on the
                    # component by a holder piece shown at no detail level (it never draws).
                    x, y, z = self.HOLDER_AT
                    src["def"]["items"].append({
                        "name": f"Material do script: {name}",
                        "shape": {"Box": {"x": kit.e(x - 0.0025), "y": kit.e(y - 0.0025), "z": kit.e(z - 0.0025),
                                          "width": "0.005", "depth": "0.005", "height": "0.005"}},
                        "material": name, "in_plan": False, "detail": {"coarse": False, "medium": False, "fine": False},
                    })
                    static_users.add(name)
                if name in have or name in kit.TEMPLATE_MATERIALS:
                    continue
                if name not in kit.PALETTE and name not in self.extra_materials:
                    raise ValueError(f"unknown material {name!r}")
                color, cls, finish, tr = kit.PALETTE.get(name) or self.extra_materials[name]
                src["materials"].append({"name": name, "color": list(color), "class": cls, "finish": finish, "transparency": tr})
                have.add(name)
            source = self.lua_source()
            if len(source.encode("utf-8")) > 250_000:
                raise ValueError(f"the moving parts' Lua source is {len(source.encode('utf-8'))} bytes: the engine takes 256 KiB at most")
            src["def"]["items"].append({"name": self.SCRIPT_PIECE, "shape": {"Script": {"source": source}}, "material": CHROME,
                                        "in_plan": False})
        return src


def put(c: MotoComponent, name: str, shapes, material: str, detail: str = FULL, in_plan: bool = False, group: str | None = None,
        digits: int = 4, lua: bool = False):
    """Write the shapes as one piece.

    Static (group None): a numeric Mesh piece, written into the .ccomp (about 140 bytes per vertex
    there: keep these lean). With `lua=True` a static piece goes to the script instead: it costs no
    file size but uses the script's run budget and does not show in the web viewer (good for small
    many-vertex fine details: tread blocks, nipples, springs).
    Moving (group STEER or STAND, or gtube/spring ends in such groups): a piece of the script.
    """
    if isinstance(shapes, Shape):
        shapes = [shapes]
    shapes = list(shapes)
    moving = lua or group is not None or any(_moves(s) for s in shapes)
    if group is not None and any(_moves(s) for s in shapes):
        raise ValueError(f"{name}: a gtube/spring with grouped points takes group=None (its points move by themselves)")
    if not moving:
        if name in c.lua_names:
            raise ValueError(f"piece name used twice: {name}")
        m = Mesh()
        for s in shapes:
            s.mesh_into(m)
        c.mesh_vertices += len(m.v)
        c._add(name, m.shape(digits), material, detail, in_plan, False)
        return
    if name in c.lua_names or any(i["name"] == name for i in c.items):
        raise ValueError(f"piece name used twice: {name}")
    c.lua_names.add(name)
    if material not in c.lua_materials:
        c.lua_materials.append(material)
    levels = [lv for lv, ch in (("coarse", "c"), ("medium", "m"), ("fine", "f")) if ch in detail]
    for lv in levels:
        c.lua_stats[lv] += 1
    c.lua_stats["pieces"] += 1
    c.lua_stats["vertices"] += mesh_size(shapes)[0]
    rec = {"nm": name, "mt": material, "dt": levels, "pl": bool(in_plan), "g": group or "", "parts": None}
    parts = "{" + ", ".join(s.lua() for s in shapes) + "}"
    text = _lua_value({k: v for k, v in rec.items() if k != "parts"})
    c.lua_pieces.append(text[:-1] + f", parts = {parts}}}")


def mesh_size(shapes) -> tuple[int, int]:
    """(vertices, faces) of the shapes meshed in the neutral pose."""
    m = Mesh()
    for s in ([shapes] if isinstance(shapes, Shape) else shapes):
        s.mesh_into(m)
    return len(m.v), len(m.f)


def _moves(s: Shape) -> bool:
    if s.kind == "spring":
        return bool(s.args["a"][1] or s.args["b"][1])
    if s.kind == "gtube":
        return any(g for _, g in s.args["pts"])
    return False


def mirrored(shapes):
    return [s.mx() for s in shapes]


def _lua_num(v) -> str:
    t = f"{float(v):.5f}".rstrip("0").rstrip(".")
    return "0" if t in ("", "-0") else t


def _lua_value(v) -> str:
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return _lua_num(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k} = {_lua_value(x)}" for k, x in v.items() if x is not None) + "}"
    if isinstance(v, (list, tuple)):
        return "{" + ", ".join(_lua_value(x) for x in v) + "}"
    raise TypeError(type(v))


# --- native pieces (engine shapes in the three principal planes) -----------------------------------
#
# Static parts that lie in a principal plane are cheaper and exact as engine shapes: a Sweep's path
# and section take arcs (a point's `radius`) and Bézier handles, and the engine tessellates them.
# Points are (u, v) or (u, v, radius) or ready dicts {"u", "v", "bezier": {...}}. Planes: "Side"
# (u = y, v = z, at x = offset, normal +X), "Front" (u = x, v = z, at y = offset), "Plan" (u = x,
# v = y, at z = offset).


def _np(points) -> list[dict]:
    out = []
    for q in points:
        if isinstance(q, dict):
            out.append(q)
            continue
        d = {"u": kit.e(q[0]), "v": kit.e(q[1])}
        if len(q) > 2 and q[2] not in (None, 0, 0.0):
            d["radius"] = kit.e(q[2])
        out.append(d)
    return out


def ncircle(r, cu=0.0, cv=0.0):
    """A circle as two arcs (a sweep's round section, or a profile's disc)."""
    return [(cu - r, cv, r), (cu + r, cv, r)]


def nsweep(c, name, plane, path, offset, section, material, detail=FULL, in_plan=False):
    """An engine Sweep: the closed `section` (u to the left of the path, v along the plane's normal) along `path`."""
    shape = {"Sweep": {"plane": plane, "path": _np(path), "offset": kit.e(offset), "profile": _np(section)}}
    c._add(name, shape, material, detail, in_plan, False)


def ntube(c, name, plane, path, offset, r, material, detail=FULL, in_plan=False):
    """A round tube (exact circle) along a path of a principal plane."""
    nsweep(c, name, plane, path, offset, ncircle(r), material, detail, in_plan)


def ncyl_side(c, name, p0, p1, r, material, detail=FULL, in_plan=False):
    """A cylinder between two points of the same x (any direction in the Side plane)."""
    assert abs(p0[0] - p1[0]) < 1e-9, "ncyl_side: both ends at the same x"
    nsweep(c, name, "Side", [(p0[1], p0[2]), (p1[1], p1[2])], p0[0], ncircle(r), material, detail, in_plan)


def ncircle_path(cy, cz, R):
    """A closed counter-clockwise circle path of the Side plane (four arcs), starting at the front (-y).

    A closed sweep shows a seam where its path starts; at the front of the rear wheel it lies behind the swingarm
    legs in the side elevations and on the outline in the plan."""
    return [(cy - R, cz, R), (cy, cz - R, R), (cy + R, cz, R), (cy, cz + R, R), (cy - R, cz)]


def nring_x(c, name, axle, R, section, material, detail=FULL, in_plan=False):
    """A ring about the X axis through `axle`: `section` [(d, x), ...] (d outwards from the circle of radius R,
    x across, absolute) carried round the circle. Tyres, rims, bands."""
    sec = [(-q[0], q[1] - axle[0]) + ((q[2],) if len(q) > 2 else ()) for q in section]
    nsweep(c, name, "Side", ncircle_path(axle[1], axle[2], R), axle[0], sec, material, detail, in_plan)


def nprofile(c, name, plane, points, offset, depth, material, detail=FULL, in_plan=False):
    """An engine Profile: a closed outline of a plane extruded `depth` along its normal from `offset`."""
    shape = {"Profile": {"plane": plane, "points": _np(points), "offset": kit.e(offset), "depth": kit.e(depth)}}
    c._add(name, shape, material, detail, in_plan, False)


def ndisc_x(c, name, x0, x1, y, z, r, material, detail=FULL, in_plan=False):
    """A disc/cylinder along X from x0 to x1 (exact circle)."""
    lo, hi = min(x0, x1), max(x0, x1)
    nprofile(c, name, "Side", ncircle(r, y, z), lo, hi - lo, material, detail, in_plan)


def hexagon2(cu, cv, r, phase=0.0):
    return [(cu + r * math.cos(math.radians(phase + 60 * i)), cv + r * math.sin(math.radians(phase + 60 * i))) for i in range(6)]


def nhex_x(c, name, x0, x1, y, z, r, material, detail=FINE, in_plan=False):
    """A hex nut / bolt head along X (r across corners)."""
    lo, hi = min(x0, x1), max(x0, x1)
    nprofile(c, name, "Side", hexagon2(y, z, r, 30), lo, hi - lo, material, detail, in_plan)


def nannulus_sector(cy, cz, r0, r1, psi0, psi1):
    """Outline (y, z) of a ring sector between radii r0 < r1 and angles psi (degrees from +y towards +z), with arcs."""
    def pt(r, a):
        t = math.radians(a)
        return (cy + r * math.cos(t), cz + r * math.sin(t))
    p0, p1, p2, p3 = pt(r0, psi0), pt(r1, psi0), pt(r1, psi1), pt(r0, psi1)
    return [p0, (p1[0], p1[1], r1), p2, (p3[0], p3[1], -r0)]


# --- the Lua kernel (a port of the Python one) ----------------------------------------------------

LUA_HEADER = "-- Moto custom: the parts that move (steering AnguloGuidao, side stand Descanso).\n" \
             "-- Generated by tools/appliances/_moto/base.py; edit the generator, not this text.\n"

LUA_KERNEL = r'''
local sqrt, cos, sin, rad, abs, atan2, floor = math.sqrt, math.cos, math.sin, math.rad, math.abs, math.atan, math.floor
local function sub(a, b) return { a[1] - b[1], a[2] - b[2], a[3] - b[3] } end
local function add(a, b) return { a[1] + b[1], a[2] + b[2], a[3] + b[3] } end
local function mul(a, k) return { a[1] * k, a[2] * k, a[3] * k } end
local function dot(a, b) return a[1] * b[1] + a[2] * b[2] + a[3] * b[3] end
local function cross(a, b) return { a[2] * b[3] - a[3] * b[2], a[3] * b[1] - a[1] * b[3], a[1] * b[2] - a[2] * b[1] } end
local function norm(a) local l = sqrt(a[1] * a[1] + a[2] * a[2] + a[3] * a[3]); if l < 1e-12 then return { 0, 0, 1 } end; return { a[1] / l, a[2] / l, a[3] / l } end
local function perp(a) local t = abs(a[1]) < 0.9 and { 1, 0, 0 } or { 0, 1, 0 }; return norm(cross(cross(a, t), a)) end
-- a rotation about the axis through o (unit-normalised `axis`) by deg, applied in place to a list of points
local function rotation(o, axis, deg)
  local k = norm(axis); local c, s = cos(rad(deg)), sin(rad(deg)); local t = 1 - c
  local kx, ky, kz = k[1], k[2], k[3]
  local r11, r12, r13 = c + kx * kx * t, kx * ky * t - kz * s, kx * kz * t + ky * s
  local r21, r22, r23 = ky * kx * t + kz * s, c + ky * ky * t, ky * kz * t - kx * s
  local r31, r32, r33 = kz * kx * t - ky * s, kz * ky * t + kx * s, c + kz * kz * t
  local ox, oy, oz = o[1], o[2], o[3]
  local R = {}
  function R.point(q)
    local x, y, z = q[1] - ox, q[2] - oy, q[3] - oz
    return { ox + r11 * x + r12 * y + r13 * z, oy + r21 * x + r22 * y + r23 * z, oz + r31 * x + r32 * y + r33 * z }
  end
  function R.all(v, n)
    for i = 1, n do
      local q = v[i]; local x, y, z = q[1] - ox, q[2] - oy, q[3] - oz
      q[1], q[2], q[3] = ox + r11 * x + r12 * y + r13 * z, oy + r21 * x + r22 * y + r23 * z, oz + r31 * x + r32 * y + r33 * z
    end
  end
  return R
end
local function rotvec(v, axis, deg) return rotation({ 0, 0, 0 }, axis, deg).point(v) end

local function vtx(m, x, y, z) local n = m.nv + 1; m.nv = n; m.v[n] = { x, y, z }; return n end
local function face(m, f) local n = m.nf + 1; m.nf = n; m.f[n] = f end
local function quad(m, a, b, c, d)
  if a ~= b and b ~= c and c ~= d and d ~= a and a ~= c and b ~= d then face(m, { a, b, c, d })
  else
    local out = {}
    for _, i in ipairs({ a, b, c, d }) do
      local dup = false
      for _, j in ipairs(out) do if j == i then dup = true end end
      if not dup then out[#out + 1] = i end
    end
    if #out >= 3 then face(m, out) end
  end
end
local function orient(m, f0)
  local vol, V, F = 0, m.v, m.f
  for i = f0, m.nf do
    local fc = F[i]; local a = V[fc[1]]; local ax, ay, az = a[1], a[2], a[3]
    for j = 2, #fc - 1 do
      local b, c = V[fc[j]], V[fc[j + 1]]
      vol = vol + ax * (b[2] * c[3] - b[3] * c[2]) + ay * (b[3] * c[1] - b[1] * c[3]) + az * (b[1] * c[2] - b[2] * c[1])
    end
  end
  if vol < 0 then for i = f0, m.nf do local fc, r = F[i], {}; for j = #fc, 1, -1 do r[#r + 1] = fc[j] end; F[i] = r end end
end
local function frame(a, ref)
  a = norm(a); local e1
  if ref then e1 = norm(sub(ref, mul(a, dot(ref, a)))) else e1 = perp(a) end
  return a, e1, cross(a, e1)
end
local function rows_faces(m, rows, wrap_rows, wrap_cols)
  local nr = #rows
  local last = wrap_rows and nr or nr - 1
  for j = 1, last do
    local r1, r2 = rows[j], rows[(j % nr) + 1]
    local cnt = #r1
    local lc = wrap_cols and cnt or cnt - 1
    for i = 1, lc do local i2 = (i % cnt) + 1; quad(m, r1[i], r1[i2], r2[i2], r2[i]) end
  end
end
local function cap(m, row, flip)
  local f = {}
  if flip then for i = #row, 1, -1 do f[#f + 1] = row[i] end else for i = 1, #row do f[i] = row[i] end end
  face(m, f)
end

local K = {}
function K.lathe(m, s)
  local f0 = m.nf + 1
  local a, e1, e2 = frame(s.a, s.ref)
  local n, a0, a1 = s.n, s.a0 or 0, s.a1 or 360
  local full = (a1 - a0) >= 359.999
  local cnt = full and n or n + 1
  local cs, sn = {}, {}
  for i = 0, cnt - 1 do local t = rad(a0 + (a1 - a0) * i / n); cs[i + 1], sn[i + 1] = cos(t), sin(t) end
  local ox, oy, oz = s.o[1], s.o[2], s.o[3]
  local rows = {}
  for j, q in ipairs(s.prof) do
    local rr, hh = q[1], q[2]
    local cx, cy, cz = ox + a[1] * hh, oy + a[2] * hh, oz + a[3] * hh
    local row = {}
    if rr < 1e-7 then local id = vtx(m, cx, cy, cz); for i = 1, cnt do row[i] = id end
    else
      local ux, uy, uz, wx, wy, wz = e1[1] * rr, e1[2] * rr, e1[3] * rr, e2[1] * rr, e2[2] * rr, e2[3] * rr
      for i = 1, cnt do local c_, s_ = cs[i], sn[i]; row[i] = vtx(m, cx + ux * c_ + wx * s_, cy + uy * c_ + wy * s_, cz + uz * c_ + wz * s_) end
    end
    rows[j] = row
  end
  rows_faces(m, rows, s.closed, full)
  if not s.closed and full then
    if s.prof[1][1] >= 1e-7 then cap(m, rows[1], true) end
    if s.prof[#rows][1] >= 1e-7 then cap(m, rows[#rows], false) end
  end
  if not full then
    local np = #rows; local cr, ch = 0, 0
    for _, q in ipairs(s.prof) do cr = cr + q[1]; ch = ch + q[2] end
    cr, ch = cr / np, ch / np
    for _, i in ipairs({ 1, cnt }) do
      local c_, s_ = cs[i], sn[i]
      local cc = vtx(m, ox + a[1] * ch + (e1[1] * c_ + e2[1] * s_) * cr, oy + a[2] * ch + (e1[2] * c_ + e2[2] * s_) * cr,
                     oz + a[3] * ch + (e1[3] * c_ + e2[3] * s_) * cr)
      local last = s.closed and np or np - 1
      for j = 1, last do
        local p, q = rows[j][i], rows[(j % np) + 1][i]
        if p ~= q then if i == 1 then face(m, { cc, p, q }) else face(m, { cc, q, p }) end end
      end
    end
  end
  orient(m, f0)
end

local function tangents(path, closed)
  local n, out = #path, {}
  for i = 1, n do
    if closed then
      local a, b = path[((i - 2) % n) + 1], path[(i % n) + 1]
      out[i] = norm(add(norm(sub(path[i], a)), norm(sub(b, path[i]))))
    elseif i == 1 then out[i] = norm(sub(path[2], path[1]))
    elseif i == n then out[i] = norm(sub(path[n], path[n - 1]))
    else out[i] = norm(add(norm(sub(path[i], path[i - 1])), norm(sub(path[i + 1], path[i])))) end
  end
  return out
end
local function rmf(path, closed, up)
  local n = #path; local ts = tangents(path, closed); local t0 = ts[1]
  local r0
  if up then local w = sub(up, mul(t0, dot(up, t0))); if dot(w, w) > 1e-12 then r0 = norm(w) end end
  r0 = r0 or perp(t0)
  local rs = { r0 }
  local steps = closed and n or n - 1
  for i = 1, steps do
    local x0, x1 = path[i], path[(i % n) + 1]
    local t_0, t_1 = ts[i], ts[(i % n) + 1]
    local v1 = sub(x1, x0); local c1 = dot(v1, v1); local ri = rs[#rs]
    if c1 < 1e-16 then rs[#rs + 1] = ri else
      local rl = sub(ri, mul(v1, 2 / c1 * dot(v1, ri)))
      local tl = sub(t_0, mul(v1, 2 / c1 * dot(v1, t_0)))
      local v2 = sub(t_1, tl); local c2 = dot(v2, v2)
      local rn = (c2 < 1e-16) and rl or sub(rl, mul(v2, 2 / c2 * dot(v2, rl)))
      rs[#rs + 1] = norm(sub(rn, mul(t_1, dot(rn, t_1))))
    end
  end
  if closed then
    local e = rs[#rs]; local s0 = cross(ts[1], rs[1])
    local ang = atan2(dot(e, s0), dot(e, rs[1]))
    rs[#rs] = nil
    for i = 1, n do rs[i] = rotvec(rs[i], ts[i], -math.deg(ang) * (i - 1) / n) end
  end
  local fr = {}
  for i = 1, n do fr[i] = { rs[i], cross(ts[i], rs[i]) } end
  return fr
end
function K.sweep(m, s)
  local f0 = m.nf + 1
  local fr = rmf(s.path, s.closed, s.up)
  local rows, sec, ns = {}, s.sec, #s.sec
  for i, x in ipairs(s.path) do
    local k = s.scale and s.scale[i] or 1
    local r, b = fr[i][1], fr[i][2]
    local rx, ry, rz, bx, by, bz = r[1] * k, r[2] * k, r[3] * k, b[1] * k, b[2] * k, b[3] * k
    local px, py, pz = x[1], x[2], x[3]
    local row = {}
    for j = 1, ns do local u, v = sec[j][1], sec[j][2]; row[j] = vtx(m, px + rx * u + bx * v, py + ry * u + by * v, pz + rz * u + bz * v) end
    rows[i] = row
  end
  rows_faces(m, rows, s.closed, true)
  if (not s.closed) and s.caps ~= false then cap(m, rows[1], true); cap(m, rows[#rows], false) end
  orient(m, f0)
end
function K.box(m, s)
  local f0 = m.nf + 1
  local c, U, V, W, h = s.c, s.ax[1], s.ax[2], s.ax[3], s.h
  local id = {}
  local k = 0
  for _, i in ipairs({ -1, 1 }) do for _, j in ipairs({ -1, 1 }) do for _, l in ipairs({ -1, 1 }) do
    k = k + 1
    local du, dv, dw = i * h[1], j * h[2], l * h[3]
    id[k] = vtx(m, c[1] + U[1] * du + V[1] * dv + W[1] * dw, c[2] + U[2] * du + V[2] * dv + W[2] * dw, c[3] + U[3] * du + V[3] * dv + W[3] * dw)
  end end end
  -- k index: (i, j, l) -> 1 + 4*(i>0) + 2*(j>0) + (l>0)
  local F = { { 1, 3, 7, 5 }, { 2, 6, 8, 4 }, { 1, 5, 6, 2 }, { 3, 4, 8, 7 }, { 1, 2, 4, 3 }, { 5, 7, 8, 6 } }
  for _, fc in ipairs(F) do face(m, { id[fc[1]], id[fc[2]], id[fc[3]], id[fc[4]] }) end
  orient(m, f0)
end
function K.prism(m, s)
  local f0 = m.nf + 1
  local cu, cv = 0, 0
  for _, q in ipairs(s.out) do cu = cu + q[1]; cv = cv + q[2] end
  cu, cv = cu / #s.out, cv / #s.out
  local o, U, V, W = s.o, s.U, s.V, s.W
  local function at(u, v, w) return o[1] + U[1] * u + V[1] * v + W[1] * w, o[2] + U[2] * u + V[2] * v + W[2] * w, o[3] + U[3] * u + V[3] * v + W[3] * w end
  local rows = {}
  for k, w in ipairs({ s.w0, s.w1 }) do
    local row = {}
    for j, q in ipairs(s.out) do row[j] = vtx(m, at(q[1], q[2], w)) end
    rows[k] = row
  end
  rows_faces(m, rows, false, true)
  for k, w in ipairs({ s.w0, s.w1 }) do
    local c = vtx(m, at(cu, cv, w)); local row = rows[k]
    for j = 1, #row do if k == 1 then face(m, { c, row[(j % #row) + 1], row[j] }) else face(m, { c, row[j], row[(j % #row) + 1] }) end end
  end
  orient(m, f0)
end
local function circle2(r, n) local out = {}; for i = 0, n - 1 do out[i + 1] = { r * cos(2 * math.pi * i / n), r * sin(2 * math.pi * i / n) } end; return out end
local function catmull(pts, per)
  local n = #pts
  if n < 3 then return pts end
  local out = {}
  for i = 1, n - 1 do
    local p1, p2 = pts[i], pts[i + 1]
    local p0 = pts[i - 1] or sub(mul(p1, 2), p2)
    local p3 = pts[i + 2] or sub(mul(p2, 2), p1)
    for k = 0, per - 1 do
      local t = k / per; local t2, t3 = t * t, t * t * t
      local w0, w1 = 0.5 * (-t + 2 * t2 - t3), 0.5 * (2 - 5 * t2 + 3 * t3)
      local w2, w3 = 0.5 * (t + 4 * t2 - 3 * t3), 0.5 * (-t2 + t3)
      out[#out + 1] = { p0[1] * w0 + p1[1] * w1 + p2[1] * w2 + p3[1] * w3, p0[2] * w0 + p1[2] * w1 + p2[2] * w2 + p3[2] * w3,
                        p0[3] * w0 + p1[3] * w1 + p2[3] * w2 + p3[3] * w3 }
    end
  end
  out[#out + 1] = pts[n]
  return out
end
-- a ring of `count` copies of a part turned about an axis (spokes, holes, bolts): s.part, s.o, s.a, s.count, s.step
function K.ring(m, s, G)
  for i = 0, s.count - 1 do
    local f0 = m.nv
    K[s.part.k](m, s.part, G)
    local R = rotation(s.o, s.a, (s.phase or 0) + s.step * i)
    for j = f0 + 1, m.nv do m.v[j] = R.point(m.v[j]) end
  end
end
'''

LUA_MAIN = r'''
local function grouped(G, q, g) if g and g ~= "" then return G[g].point(q) end; return q end
function K.spring(m, s, G)
  local a, b = grouped(G, s.a[1], s.a[2]), grouped(G, s.b[1], s.b[2])
  local ax, e1, e2 = frame(sub(b, a), s.ref)
  local len = sqrt(dot(sub(b, a), sub(b, a)))
  local per = s.per_turn or 16
  local n = math.max(4, floor(s.turns * per))
  local path = {}
  for i = 0, n do
    local t = i / n; local ang = 2 * math.pi * s.turns * t
    path[i + 1] = add(add(a, mul(ax, len * t)), add(mul(e1, s.r * cos(ang)), mul(e2, s.r * sin(ang))))
  end
  K.sweep(m, { path = path, sec = circle2(s.wire, s.n or 8), caps = true })
end
function K.gtube(m, s, G)
  local pts = {}
  for i, q in ipairs(s.pts) do pts[i] = grouped(G, q[1], q[2]) end
  K.sweep(m, { path = catmull(pts, s.per or 6), sec = circle2(s.r, s.n or 10), caps = true, up = s.up })
end

function geometry(p)
  local steer = p.AnguloGuidao or 0
  if steer > STEER_LOCK then steer = STEER_LOCK elseif steer < -STEER_LOCK then steer = -STEER_LOCK end
  local stand = p.Descanso or 0
  if stand < 0 then stand = 0 elseif stand > 1 then stand = 1 end
  local G = { steer = rotation(STEER_O, STEER_D, steer), stand = rotation(STAND_O, STAND_D, (stand - 1) * STAND_SWING) }
  local out = {}
  for _, pc in ipairs(PIECES) do
    local m = { v = {}, f = {}, nv = 0, nf = 0 }
    for _, s in ipairs(pc.parts) do K[s.k](m, s, G) end
    if pc.g ~= "" then G[pc.g].all(m.v, m.nv) end
    out[#out + 1] = mesh { vertices = m.v, faces = m.f, name = pc.nm, material = pc.mt, detail = pc.dt, in_plan = pc.pl }
  end
  return out
end
'''

