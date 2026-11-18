"""Ducha higiênica: registro de parede com canopla e alavanca de 1/4 de volta, flexível pendente, gatilho e suporte."""

import math

from _banheiro import *
from louca import bez, tube

CHROME, STEEL = "Cromado", "Inox escovado"

# The hose hangs between the valve's outlet (A) and the gun's tail (G) in two Bézier spans
# meeting at its lowest point B; its sideways spread `w` grows with the hose's length.
XG = 0.095  # the holder and the gun, to the right of the valve
ZA, ZG, ZB, HANDLE = -0.087, -0.224, -0.567, 0.2  # heights below the valve's axis


def _bez_len(p0, p1, p2, p3, n=400):
    out, prev = 0.0, p0
    for i in range(1, n + 1):
        t = i / n
        k = ((1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3)
        pt = (sum(c * q[0] for c, q in zip(k, (p0, p1, p2, p3))), sum(c * q[1] for c, q in zip(k, (p0, p1, p2, p3))))
        out += math.hypot(pt[0] - prev[0], pt[1] - prev[1])
        prev = pt
    return out


def _spread(length):
    """The spread w that gives the swept part of a hose of nominal `length` (its two 25 mm ends excluded)."""
    xm = XG / 2

    def total(w):
        return (_bez_len((0, ZA), (0, ZA - HANDLE), (xm - w, ZB), (xm, ZB))
                + _bez_len((xm, ZB), (xm + w, ZB), (XG, ZG - HANDLE), (XG, ZG)))

    lo, hi = 0.0, 3.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if total(mid) < length - 0.05 else (lo, mid)
    return lo


def hexagon(x, y, r):
    return [(add(x, r * math.cos(math.radians(30 + 60 * i))), add(y, r * math.sin(math.radians(30 + 60 * i)))) for i in range(6)]


def build():
    c = Component("Ducha higiênica", "plumbing", "ducha-higienica", "Plumbing")
    M = c.param("Mangueira", 1.2)
    E = c.param("Elevacao", 0.6, "Length", True)
    G = c.angle("AnguloRegistro", 0, open_at=90)
    T = c.angle("AnguloGatilho", 0, open_at=11)
    desc = "Ducha higiênica cromada com registro de 1/4 de volta, flexível de aço inox e suporte de parede"
    c.type("Ducha higiênica 1,2 m", desc + " (flexível de 1,20 m)", Mangueira=1.2)
    c.type("Ducha higiênica 1,5 m", desc + " (flexível de 1,50 m)", Mangueira=1.5)
    c.mep = {"Fixture": {"drain_units": 0, "supply_weight": 0.4, "hot_water": False}}
    c.connector("Água fria", "ColdWater", 0, 0, E, "Back", 0.02)
    c.preview_base = 0.0
    c.preview_size = (0.55, 0.3, 0.68)

    yh = -0.04  # the plane of the outlet, the hose and the gun's axis

    def z(dz):
        return add(E, dz)

    # --- coarse stand-ins ---
    c.box("Registro simplificado", -0.032, -0.066, z(-0.087), 0.064, 0.066, 0.119, CHROME, COARSE, in_plan=True)
    c.box("Suporte simplificado", XG - 0.022, yh - 0.018, z(-0.028), 0.044, -yh + 0.018, 0.04, CHROME, COARSE, in_plan=True)
    c.cyl("Ducha simplificada", XG, yh, z(-0.224), 0.02, 0.266, CHROME, COARSE, in_plan=True)

    # --- valve: rose, bonnet, lever on a hub ---
    c.rev("Canopla do registro", "Plan", [(0, -0.011), (0.024, -0.011, 0.009), (0.032, -0.004), (0.032, 0), (0, 0)], E, 0, CHROME, in_plan=True)
    c.cyl_y("Castelo do registro", 0, E, -0.045, 0.0165, 0.035, CHROME, in_plan=True)
    c.cyl_y("Anel do castelo", 0, E, -0.017, 0.019, 0.006, CHROME, FINE)
    c.cyl_y("Cubo da alavanca", 0, E, -0.066, 0.012, 0.021, CHROME, in_plan=True)
    th = f"(180 - {G})"  # the lever points left when closed, up when open

    def lever(r, t):
        return (f"{e(r)}*cos({th}) - {p(e(t))}*sin({th})", f"{E} + {e(r)}*sin({th}) + {p(e(t))}*cos({th})")

    c.profile("Alavanca do registro", "Front", [lever(r, t) for r, t in (
        (0, -0.009), (0.058, -0.0062), (0.064, -0.0045), (0.067, 0), (0.064, 0.0045), (0.058, 0.0062), (0, 0.009))],
        -0.064, 0.008, CHROME, in_plan=True)
    c.cyl_y("Indicador de água fria", 0, E, -0.0672, 0.0075, 0.0012, "Plástico azul", FINE)
    c.cyl_y("Parafuso de fixação da canopla", 0, z(-0.022), -0.0115, 0.0022, 0.0006, STEEL, FINE)

    # --- outlet under the bonnet and the hose's end on it ---
    c.cyl("Bico de saída", 0, yh, z(-0.05), 0.0075, 0.04, CHROME)
    c.extrusion("Porca do flexível no registro", hexagon(0, yh, 0.0115), z(-0.062), 0.014, CHROME, FINE)
    c.cyl("Terminal do flexível no registro", 0, yh, z(ZA), 0.0085, -0.062 - ZA, CHROME)
    c.cyl("Anel de crimpagem no registro", 0, yh, z(ZA + 0.004), 0.0092, 0.004, STEEL, FINE)

    # --- the hose, hanging in a loop ---
    w1, w2 = _spread(1.2), _spread(1.5)
    w = f"({w1:.5f} + {(w2 - w1) / 0.3:.5f}*({M} - 1.2))"
    xm = XG / 2
    path = []
    n = 14
    for seg in (0, 1):  # the two Bézier spans, sampled (x is linear in w, so every point is an expression)
        for i in range(n + (seg == 1)):
            t = i / n
            b = ((1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3)
            if seg == 0:
                cx, kw = (b[2] + b[3]) * xm, -b[2]
                cz = b[0] * ZA + b[1] * (ZA - HANDLE) + (b[2] + b[3]) * ZB
            else:
                cx, kw = (b[0] + b[1]) * xm + (b[2] + b[3]) * XG, b[1]
                cz = (b[0] + b[1]) * ZB + b[2] * (ZG - HANDLE) + b[3] * ZG
            x = e(cx) if abs(kw) < 1e-9 else f"{cx:.5f} {'+' if kw > 0 else '-'} {abs(kw):.5f}*{w}"
            path.append((x, z(round(cz, 5))))
    tube(c, "Flexível", "Front", path, yh, 0.0065, STEEL, ALL, n=12)

    # --- holder on the wall: rose, arm and a C clip round the gun's neck ---
    c.rev("Canopla do suporte", "Plan", [(XG, -0.009), (XG + 0.016, -0.009, 0.007), (XG + 0.022, -0.003), (XG + 0.022, 0), (XG, 0)], z(-0.006), XG, CHROME, in_plan=True)
    c.box("Braço do suporte", XG - 0.006, yh + 0.016, z(-0.011), 0.012, -0.008 - yh - 0.016, 0.01, CHROME)
    clip = [(add(XG, r * math.cos(math.radians(a))), add(yh, r * math.sin(math.radians(a))))
            for r, angles in ((0.018, range(-60, 241, 20)), (0.0115, range(240, -61, -20))) for a in angles]
    c.extrusion("Garfo do suporte", clip, z(-0.012), 0.012, CHROME, in_plan=True)
    c.cyl_y("Tampa do parafuso do suporte", XG, z(0.008), -0.0095, 0.003, 0.0006, CHROME, FINE)

    # --- the gun: handle, head resting on the clip, spray face, trigger ---
    c.extrusion("Porca do flexível na ducha", hexagon(XG, yh, 0.0115), z(-0.199), 0.014, CHROME, FINE)
    c.cyl("Terminal do flexível na ducha", XG, yh, z(ZG), 0.0085, -0.199 - ZG, CHROME)
    c.cyl("Anel de crimpagem na ducha", XG, yh, z(ZG + 0.019), 0.0092, 0.004, STEEL, FINE)
    c.rev("Cabo da ducha", "Front", [
        (XG, z(-0.185)), (XG + 0.011, z(-0.185)), (XG + 0.0128, z(-0.17), 0.4), (XG + 0.0138, z(-0.07)),
        (XG + 0.0118, z(-0.03), 0.06), (XG + 0.0105, z(-0.012)), (XG + 0.0105, z(0.001)), (XG, z(0.001)),
    ], yh, XG, CHROME)
    c.rev("Cabeça da ducha", "Front", [
        (XG, z(0)), (XG + 0.0125, z(0)), (XG + 0.0205, z(0.008), 0.012), (XG + 0.0215, z(0.03)),
        (XG + 0.019, z(0.04), 0.012), (XG + 0.0155, z(0.042)), (XG, z(0.042)),
    ], yh, XG, CHROME, in_plan=True)
    c.rev("Anel decorativo do cabo", "Front", rect(XG + 0.0105, z(-0.012), XG + 0.0122, z(-0.004)), yh, XG, CHROME, detail=FINE)
    c.cyl("Espalhador da ducha", XG, yh, z(0.0405), 0.0152, 0.0025, "Borracha cinza", FINE)
    for i, r in enumerate((0.0045, 0.0095), 1):
        c.rev(f"Anel de jatos {i}", "Front", rect(XG + r - 0.0012, z(0.042), XG + r + 0.0012, z(0.0432)), yh, XG, "Borracha", detail=FINE)
    c.cyl("Jato central", XG, yh, z(0.042), 0.0015, 0.0012, "Borracha", FINE)
    yp, zp = yh - 0.012, z(-0.025)  # the trigger's pivot

    def trig(dy, dz):
        return (f"{e(yp)} + {e(dy)}*cos({T}) - {p(e(dz))}*sin({T})", f"{zp} + {e(dy)}*sin({T}) + {p(e(dz))}*cos({T})")

    c.profile("Gatilho", "Side", [trig(dy, dz) for dy, dz in (
        (0.0, 0.006), (-0.008, -0.004), (-0.016, -0.04), (-0.019, -0.082), (-0.016, -0.09), (-0.011, -0.088),
        (-0.009, -0.05), (-0.002, -0.012))], XG - 0.0055, 0.011, CHROME, in_plan=True)
    c.cyl_x("Pino do gatilho", yp, zp, XG - 0.0075, 0.002, 0.015, STEEL, FINE)
    return c
