"""Lava e seca frontal: a front-loading washer-dryer with a round porthole door.

The porthole door is the difficult part: a ring and a bulged glass are solids
of revolution about a Y axis, and such a piece cannot follow a vertical hinge.
`porthole_door` therefore writes the door twice (see its docstring).
"""

from __future__ import annotations

import math

from kit import *
from _aparelhos import tube


def num(v: float) -> str:
    """A number safe to paste inside an expression."""
    text = f"{v:.5f}".rstrip("0").rstrip(".")
    if text in ("", "-0"):
        text = "0"
    return f"({text})" if text.startswith("-") else text


def sphere(c, name, x, y, z, r, material, detail=FINE):
    """A ball centered at (x, y, z)."""
    c.rev(name, "Front", [(x, f"{p(z)} - {p(r)}", r), (x, f"{p(z)} + {p(r)}")], y, x, material, detail=detail)


def foot(c, name, x, y, height, material="Aço galvanizado", pad="Borracha"):
    """An adjustable foot: a rubber pad, a lock nut and a threaded rod up to `height`."""
    c.rev(f"{name} - sapata", "Front", [(x, 0), (f"{p(x)} + 0.021", 0), (f"{p(x)} + 0.021", 0.005), (f"{p(x)} + 0.016", 0.008), (x, 0.008)], y, x, pad)
    c.rev(f"{name} - haste", "Front", [(x, 0.008), (f"{p(x)} + 0.011", 0.008), (f"{p(x)} + 0.011", 0.012), (f"{p(x)} + 0.005", 0.012), (f"{p(x)} + 0.005", height), (x, height)], y, x, material, detail=FINE)


# --- the porthole door -------------------------------------------------------

def _clip(poly, t):
    """The part of the (rho, b) polygon with rho >= t."""
    out = []
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        ia, ib = a[0] >= t, b[0] >= t
        if ia:
            out.append(a)
        if ia != ib:
            k = (t - a[0]) / (b[0] - a[0])
            out.append((t, a[1] + k * (b[1] - a[1])))
    return out


def _section(poly, t, steps=4):
    """Outlines, in (a, b), of the cut at the height t of the solid that `poly` (rho, b) makes turning about rho = 0.

    A point at the distance rho of the axis is cut at a = +-sqrt(rho^2 - t^2).
    """
    t = abs(t)
    clipped = _clip(poly, t)
    if len(clipped) < 3:
        return []
    pts = []
    for i, a in enumerate(clipped):
        b = clipped[(i + 1) % len(clipped)]
        n = steps if abs(a[0] - b[0]) > 1e-9 else 1
        for k in range(n):
            rho = a[0] + (b[0] - a[0]) * k / n
            pts.append((math.sqrt(max(rho * rho - t * t, 0.0)), a[1] + (b[1] - a[1]) * k / n))
    clean = []
    for q in pts:
        if not clean or abs(q[0] - clean[-1][0]) > 1e-7 or abs(q[1] - clean[-1][1]) > 1e-7:
            clean.append(q)
    if len(clean) > 1 and abs(clean[0][0] - clean[-1][0]) < 1e-7 and abs(clean[0][1] - clean[-1][1]) < 1e-7:
        clean.pop()
    pts = clean
    if len(pts) < 3:
        return []
    zero = [q[0] < 1e-7 for q in pts]
    if not any(zero):  # the cut misses the axis plane: one outline on each side
        return [pts, [(-a, b) for a, b in reversed(pts)]]
    n = len(pts)
    start = next(i for i in range(n) if zero[i] and not zero[(i + 1) % n])
    pts = pts[start:] + pts[:start]
    zero = zero[start:] + zero[:start]
    end = next(i for i in range(1, n) if zero[i])
    if not all(zero[end:]):
        raise ValueError("the section touches the axis plane twice: split the profile")
    path = pts[: end + 1]
    return [path + [(-a, b) for a, b in reversed(path[1:-1])]]


def porthole_door(c, prefix, hinge, zc, radius, angle, solids, hybrid=True, arm=1.06, tuck=0.004):
    """A round door hinged on the left that looks round closed and open.

    `solids` = (name, material, polygon, bands, detail, in_plan): each polygon
    is a half-section in (rho, b), in units of the door's `radius`: rho from
    the door's axis and b out of the door's back plane towards the front.
    `hinge` = (x, y) of the vertical hinge, on the back plane; the door's axis
    stands `arm` radii to the right of it at the height `zc`.

    A solid of revolution about Y cannot swing about a vertical hinge, so each
    solid is written as a stack of `bands` horizontal slices (Plan profiles
    whose points go through `swing`): each slice is the true section of the
    solid at its mid height, and the bands are evenly spaced in angle so they
    get thinner where the outline turns faster. `in_plan` marks the middle
    slice (and the closed revolution, unless it is "open") for the plan.

    With `hybrid`, the closed door is an exact revolution instead: while the
    angle is 0 the slices are shrunk (to `tuck` of their size) into the hinge
    pin, where they cannot be seen, and once the door opens the revolutions
    are tucked there and the slices take their place. The closed door draws
    as clean circles in elevations; the open one shows the slice lines.
    """
    hx, hy = hinge
    R = p(radius)
    if hybrid:
        s_open = f"max({tuck}, min(1, {p(angle)}*100))"
        s_closed = f"max({tuck}, 1 - {p(angle)}*100)"
    else:
        s_open, s_closed = "1", None
    for name, material, poly, bands, detail, in_plan in solids:
        top = max(q[0] for q in poly)
        if hybrid:
            axis = f"{p(hx)} + {num(arm)}*{R}*{s_closed}"
            pts = [(f"{axis} + {num(rho)}*{R}*{s_closed}", f"{p(hy)} - {num(b)}*{R}*{s_closed}") for rho, b in reversed(poly)]
            c.rev(f"{prefix} - {name}", "Plan", pts, zc, axis, material, detail=detail, in_plan=in_plan is True)
        edges = [top * math.sin(math.radians(-90 + 180 * i / bands)) for i in range(bands + 1)]
        count = 0
        for i in range(bands):
            t0, t1 = edges[i], edges[i + 1]
            outlines = _section(poly, (t0 + t1) / 2)
            for outline in outlines:
                count += 1
                pts = [swing(hinge, angle, f"{num(arm + a)}*{R}*{s_open}", f"{num(b)}*{R}*{s_open}") for a, b in outline]
                widest = bool(in_plan) and i == bands // 2
                c.profile(
                    f"{prefix} - {name} - fatia {count}", "Plan", pts,
                    f"{p(zc)} + {num(t0)}*{R}*{s_open}", f"{num(t1 - t0)}*{R}*{s_open}",
                    material, detail=detail, in_plan=widest,
                )


def door_part(c, name, hinge, angle, radius, a0, a1, b0, b1, zc, t0, t1, material, detail=FULL, arm=1.06, in_plan=False):
    """A box of the door in the units of `porthole_door`: a from the door's axis, b out of its back plane, t up from the axis."""
    R = p(radius)
    c.door_box(
        name, hinge, angle, f"{num(arm + a0)}*{R}", f"{num(arm + a1)}*{R}", f"{num(b0)}*{R}", f"{num(b1)}*{R}",
        f"{p(zc)} + {num(t0)}*{R}", f"{num(t1 - t0)}*{R}", material, detail=detail, in_plan=in_plan,
    )


def drum(c, zc, radius, y0, depth, mouth, lifters=(90, 210, 330)):
    """A stainless drum lying along Y with its lifters and hints of the perforation."""
    Rd, y1 = p(radius), f"({p(y0)} + {p(depth)})"
    w = 0.003
    c.rev("Tambor", "Plan", [
        (mouth, y0), (Rd, y0), (Rd, y1), (0, y1), (0, f"{y1} - {w}"),
        (f"{Rd} - {w}", f"{y1} - {w}"), (f"{Rd} - {w}", f"{p(y0)} + {w}"), (mouth, f"{p(y0)} + {w}"),
    ], zc, 0, "Inox escovado")
    c.rev("Tambor - borda da boca", "Plan", [
        (mouth, f"{p(y0)} - 0.004"), (f"{p(mouth)} + 0.008", f"{p(y0)} - 0.004"), (f"{p(mouth)} + 0.008", f"{p(y0)} + 0.001"), (mouth, f"{p(y0)} + 0.001"),
    ], zc, 0, "Inox escovado")
    c.rev("Tambor - cubo do eixo", "Plan", [
        (0, f"{y1} - 0.012"), (0.03, f"{y1} - 0.012"), (0.05, f"{y1} - {w}"), (0, f"{y1} - {w}"),
    ], zc, 0, "Inox escovado")
    for i, deg in enumerate(lifters, 1):
        rx, rz = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        tx, tz = -rz, rx

        def pt(d, s):
            return (
                f"{num(rx)}*({Rd} - {d}) + {num(s * tx)}",
                f"{p(zc)} + {num(rz)}*({Rd} - {d}) + {num(s * tz)}",
            )

        c.profile(f"Tambor - aleta {i}", "Front", [pt(0.002, 0.032), pt(0.035, 0.016), pt(0.045, 0), pt(0.035, -0.016), pt(0.002, -0.032)],
                  f"{p(y0)} + 0.03", f"{p(depth)} - 0.06", "Plástico cinza claro")
    # Perforation: dark dots on the back wall, on the bottom and on the sides.
    k = 0
    for frac, count, phase in ((0.36, 6, 0), (0.60, 8, 22.5), (0.84, 10, 0)):
        for j in range(count):
            a = math.radians(phase + 360 * j / count)
            k += 1
            c.cyl_y(f"Tambor - furo {k}", f"{num(frac * math.cos(a))}*{Rd}", f"{p(zc)} + {num(frac * math.sin(a))}*{Rd}",
                    f"{y1} - {w} - 0.001", 0.0045, 0.001, "Aço pintado preto", detail=FINE)
    for row in range(4):
        y = f"{p(y0)} + {num(0.14 + 0.24 * row)}*{p(depth)}"
        for x in (-0.05, 0, 0.05):
            k += 1
            c.cyl(f"Tambor - furo {k}", x, y, f"{p(zc)} - sqrt(({Rd} - {w})*({Rd} - {w}) - {num(x * x)}) - 0.0005", 0.0045, 0.0015, "Aço pintado preto", detail=FINE)
    for side, sign in (("esquerdo", -1), ("direito", 1)):
        for row in range(3):
            y = f"{p(y0)} + {num(0.26 + 0.24 * row)}*{p(depth)}"
            for dz in (-0.045, 0.045):
                k += 1
                half = f"sqrt(({Rd} - {w})*({Rd} - {w}) - {num(dz * dz)})"
                x = f"-{half} - 0.0005" if sign < 0 else f"{half} - 0.001"
                c.cyl_x(f"Tambor - furo {k}", y, f"{p(zc)} + {num(dz)}", x, 0.0045, 0.0015, "Aço pintado preto", detail=FINE)


# Half-sections of the door, in units of its radius (rho, b), counter-clockwise.
DOOR_RING = [(0.70, 0), (1.0, 0), (1.0, 0.05), (0.94, 0.125), (0.74, 0.125), (0.70, 0.10)]
DOOR_TRIM = [(0.60, 0), (0.70, 0), (0.70, 0.10), (0.60, 0.07)]
DOOR_DISC = [(0, 0), (1.0, 0), (1.0, 0.12), (0, 0.12)]
DOOR_GLASS = [(0, -0.30), (0.34, -0.30), (0.60, -0.02), (0.60, 0.05), (0.56, 0.05), (0.31, -0.265), (0, -0.265)]


def build() -> Component:
    c = Component("Lava e seca frontal", "plumbing", "lavadora-frontal", "Plumbing")
    c.param("Largura", 0.60)
    c.param("Profundidade", 0.60)
    c.param("Altura", 0.85)
    c.param("AlturaPainel", 0.115)
    c.param("AlturaRodape", 0.10)
    c.param("AlturaPes", 0.015)
    c.param("DiametroPorta", 0.48)
    c.param("DiametroTambor", 0.47)
    c.param("ProfundidadeTambor", 0.33)
    ang = c.angle("AnguloPorta", 0, open_at=105)

    W2 = "Largura/2"
    YF = "(-Profundidade/2 + 0.036)"  # front face of the cabinet
    YB = "(Profundidade/2 - 0.03)"  # back face of the cabinet: the hoses run behind it
    YW = "Profundidade/2"  # the wall
    DC = f"({YB} - {YF})"  # depth of the cabinet
    Z0 = "AlturaPes"
    ZR = "(AlturaPes + AlturaRodape)"  # top of the plinth
    ZT = "(Altura - 0.03)"  # underside of the top
    ZP = "(Altura - 0.03 - AlturaPainel)"  # bottom of the control panel
    ZPC = "(Altura - 0.03 - AlturaPainel/2)"  # middle of the control panel
    ZC = "(AlturaPes/2 + AlturaRodape/2 + Altura/2 - 0.015 - AlturaPainel/2)"  # axis of the door and of the drum
    RP = "(DiametroPorta/2)"
    RH = f"(0.68*{RP})"  # hole of the front panel
    RM = f"(0.60*{RP})"  # mouth of the drum
    RD = "(DiametroTambor/2)"
    white, dark = "Aço pintado branco", "Plástico preto brilhante"

    # --- coarse stand-ins ---
    c.box("Corpo simplificado", f"-{W2}", YF, 0, "Largura", DC, "Altura", white, detail=COARSE, in_plan=True)
    hinge = (f"(-1.06*{RP})", f"({YF} - 0.002)")
    porthole_door(c, "Porta simplificada", hinge, ZC, RP, ang, [("disco", "Plástico cinza", DOOR_DISC, 8, COARSE, True)])

    # --- cabinet ---
    for name, x in (("dianteiro esquerdo", f"-{W2} + 0.05"), ("dianteiro direito", f"{W2} - 0.05")):
        foot(c, f"Pé {name}", x, f"{YF} + 0.05", Z0)
    for name, x in (("traseiro esquerdo", f"-{W2} + 0.05"), ("traseiro direito", f"{W2} - 0.05")):
        foot(c, f"Pé {name}", x, f"{YB} - 0.05", Z0)
    c.box("Lateral esquerda", f"-{W2}", YF, Z0, 0.008, DC, f"{ZT} - {Z0}", white)
    c.box("Lateral direita", f"{W2} - 0.008", YF, Z0, 0.008, DC, f"{ZT} - {Z0}", white)
    c.box("Base", f"-{W2} + 0.008", f"{YF} + 0.012", Z0, "Largura - 0.016", f"{DC} - 0.02", 0.008, "Aço galvanizado")
    c.box("Painel traseiro", f"-{W2} + 0.008", f"{YB} - 0.008", Z0, "Largura - 0.016", 0.008, f"{ZT} - {Z0}", "Aço galvanizado")
    c.box("Tampo", f"-{W2}", f"{YF} - 0.006", ZT, "Largura", f"{DC} + 0.006", 0.03, "Laminado branco", in_plan=True)
    c.box("Tampo - friso frontal", f"-{W2}", f"{YF} - 0.007", f"{ZT} + 0.004", "Largura", 0.001, 0.022, "Plástico cinza claro", detail=FINE)
    # Front panel: two halves around the round opening.
    # Front panel: one sheet with the round opening, reached by a slit under it.
    c.profile("Painel frontal", "Front", [
        (0, ZR), (0, f"{ZC} - {RH}", f"-{RH}"), (0, f"{ZC} + {RH}", f"-{RH}"), (0, f"{ZC} - {RH}"), (0, ZR),
        (f"{W2} - 0.008", ZR), (f"{W2} - 0.008", ZP), (f"-{W2} + 0.008", ZP), (f"-{W2} + 0.008", ZR),
    ], YF, 0.012, white)
    c.rev("Batente da porta", "Plan", [
        (f"{RH} - 0.002", f"{YF} - 0.0015"), (f"1.02*{RP}", f"{YF} - 0.0015"), (f"1.02*{RP}", f"{YF} + 0.001"), (f"{RH} - 0.002", f"{YF} + 0.001"),
    ], ZC, 0, "Plástico cinza claro")
    # Plinth with the filter hatch.
    c.box("Rodapé", f"-{W2} + 0.008", f"{YF} + 0.004", Z0, "Largura - 0.016", 0.012, "AlturaRodape", white)
    c.box("Rodapé - sombra superior", f"-{W2} + 0.008", f"{YF} + 0.001", f"{ZR} - 0.004", "Largura - 0.016", 0.004, 0.004, "Plástico preto", detail=FINE)
    HX = f"({W2} - 0.19)"
    c.box("Tampa do filtro", HX, f"{YF} + 0.002", f"{Z0} + 0.018", 0.14, 0.003, "AlturaRodape - 0.036", "Branco")
    c.box("Tampa do filtro - rebaixo", f"{HX} + 0.05", f"{YF} + 0.0015", f"{ZR} - 0.03", 0.04, 0.001, 0.008, "Plástico cinza", detail=FINE)
    c.box("Tampa do filtro - dobradiça", f"{HX} + 0.01", f"{YF} + 0.0015", f"{Z0} + 0.014", 0.12, 0.003, 0.004, "Plástico cinza claro", detail=FINE)

    # --- control panel ---
    YP = f"({YF} - 0.005)"
    c.box("Painel de comando", f"-{W2}", YP, ZP, "Largura", 0.025, "AlturaPainel", "Branco")
    c.box("Painel de comando - friso inferior", f"-{W2}", f"{YP} - 0.001", ZP, "Largura", 0.001, 0.006, "Alumínio anodizado", detail=FINE)
    # Detergent drawer.
    DX = f"(-{W2} + 0.018)"
    DW = "(0.29*Largura)"
    c.box("Gaveta de sabão", DX, f"{YP} - 0.004", f"{ZP} + 0.016", DW, 0.004, "AlturaPainel - 0.03", "Branco")
    c.box("Gaveta de sabão - contorno", f"{DX} - 0.002", f"{YP} - 0.0005", f"{ZP} + 0.014", f"{DW} + 0.004", 0.0005, "AlturaPainel - 0.026", "Plástico cinza", detail=FINE)
    c.box("Gaveta de sabão - puxador", f"{DX} + 0.02", f"{YP} - 0.0045", f"{ZP} + 0.022", f"{DW} - 0.04", 0.0005, 0.016, "Plástico cinza", detail=FINE)
    c.box("Gaveta de sabão - corpo", f"{DX} + 0.006", YP, f"{ZP} + 0.02", f"{DW} - 0.012", 0.16, "AlturaPainel - 0.045", "Plástico cinza claro", detail=FINE)
    # Program dial.
    KX = "(-0.085*Largura)"
    c.rev("Seletor de programas - base", "Plan", [(KX, f"{YP} - 0.003"), (f"{KX} + 0.038", f"{YP} - 0.003"), (f"{KX} + 0.038", YP), (KX, YP)], ZPC, KX, "Cromado")
    c.rev("Seletor de programas", "Plan", [
        (KX, f"{YP} - 0.026"), (f"{KX} + 0.027", f"{YP} - 0.026"), (f"{KX} + 0.030", f"{YP} - 0.022"), (f"{KX} + 0.032", f"{YP} - 0.003"), (KX, f"{YP} - 0.003"),
    ], ZPC, KX, "Alumínio anodizado")
    c.box("Seletor de programas - marca", f"{KX} - 0.0015", f"{YP} - 0.0265", f"{ZPC} + 0.012", 0.003, 0.0005, 0.016, "Plástico preto", detail=FINE)
    for i in range(12):
        a = math.radians(30 * i)
        c.cyl_y(f"Seletor de programas - indicador {i + 1}", f"{KX} + {num(0.047 * math.cos(a))}", f"{ZPC} + {num(0.047 * math.sin(a))}",
                f"{YP} - 0.0006", 0.0022, 0.0006, "Plástico cinza", detail=FINE)
    # Display and keys on a dark glossy strip.
    SX = "(0.02*Largura + 0.012)"
    SW = f"({W2} - 0.02 - {SX})"
    c.profile("Visor - máscara", "Front", rrect(SX, f"{ZPC} - 0.036", f"{SX} + {SW}", f"{ZPC} + 0.036", 0.008), f"{YP} - 0.0015", 0.0015, dark)
    c.box("Visor", f"{SX} + 0.012", f"{YP} - 0.002", f"{ZPC} - 0.006", f"0.36*{SW}", 0.0005, 0.03, "Visor LED", detail=FINE)
    for i in range(3):
        c.box(f"Visor - dígito {i + 1}", f"{SX} + 0.022 + {num(0.1 * i)}*{SW}", f"{YP} - 0.0024", f"{ZPC}", f"0.07*{SW}", 0.0004, 0.018, "Plástico azul", detail=FINE)
    for i in range(4):
        c.cyl_y(f"Tecla de função {i + 1}", f"{SX} + {num(0.09 + 0.105 * i)}*{SW}", f"{ZPC} - 0.021", f"{YP} - 0.0035", 0.007, 0.002, "Teclado", detail=FINE)
        c.cyl_y(f"Luz de função {i + 1}", f"{SX} + {num(0.09 + 0.105 * i)}*{SW}", f"{ZPC} - 0.0095", f"{YP} - 0.0022", 0.0015, 0.0007, "Plástico verde", detail=FINE)
    for i in range(3):
        c.cyl_y(f"Tecla de ajuste {i + 1}", f"{SX} + {num(0.50 + 0.105 * i)}*{SW}", f"{ZPC} + 0.012", f"{YP} - 0.0035", 0.007, 0.002, "Teclado", detail=FINE)
        c.cyl_y(f"Luz de ajuste {i + 1}", f"{SX} + {num(0.50 + 0.105 * i)}*{SW}", f"{ZPC} - 0.004", f"{YP} - 0.0022", 0.0015, 0.0007, "Plástico verde", detail=FINE)
    BX = f"({SX} + 0.88*{SW})"
    c.cyl_y("Tecla iniciar - aro", BX, ZPC, f"{YP} - 0.003", 0.015, 0.0015, "Cromado", detail=FINE)
    c.cyl_y("Tecla iniciar", BX, ZPC, f"{YP} - 0.0045", 0.012, 0.003, "Teclado", detail=FINE)
    c.cyl_y("Tecla liga-desliga", f"{SX} + 0.50*{SW}", f"{ZPC} - 0.021", f"{YP} - 0.0035", 0.007, 0.002, "Plástico vermelho", detail=FINE)

    # --- tub, gasket and drum ---
    YD = f"({YF} + 0.075)"  # front of the drum
    YT1 = f"({YD} + ProfundidadeTambor + 0.02)"
    RT = f"({RD} + 0.02)"
    c.rev("Cuba externa", "Plan", [
        (f"{RM} + 0.014", f"{YD} - 0.008"), (RT, f"{YD} - 0.008"), (RT, YT1), (0, YT1), (0, f"{YT1} - 0.005"),
        (f"{RT} - 0.005", f"{YT1} - 0.005"), (f"{RT} - 0.005", f"{YD} - 0.003"), (f"{RM} + 0.014", f"{YD} - 0.003"),
    ], ZC, 0, "Plástico cinza")
    c.rev("Guarnição da porta", "Plan", [
        (f"{RH} - 0.014", f"{YF} - 0.001"), (f"{RH} + 0.004", f"{YF} - 0.001"), (f"{RH} + 0.004", f"{YF} + 0.013"), (f"{RM} + 0.016", f"{YD} - 0.006"),
        (f"{RM} + 0.001", f"{YD} - 0.006"), (f"{RH} - 0.014", f"{YF} + 0.012"),
    ], ZC, 0, "Borracha cinza")
    c.rev("Guarnição da porta - lábio", "Plan", [
        (f"{RH} - 0.022", f"{YF} + 0.016"), (f"{RH} - 0.012", f"{YF} + 0.012"), (f"{RH} - 0.012", f"{YF} + 0.022"), (f"{RH} - 0.022", f"{YF} + 0.024"),
    ], ZC, 0, "Borracha cinza", detail=FINE)
    drum(c, ZC, RD, YD, "ProfundidadeTambor", RM)
    c.cyl_y("Motor - polia do tambor", 0, ZC, YT1, f"0.55*{RD}", 0.012, "Alumínio fundido", detail=FINE)

    # --- door ---
    c.cyl("Dobradiça - pino", hinge[0], hinge[1], f"{ZC} - 0.06", 0.009, 0.12, "Cromado")
    c.box("Dobradiça - base", f"{hinge[0]} - 0.022", f"{YF} - 0.003", f"{ZC} - 0.07", 0.03, 0.003, 0.14, "Cromado")
    for i, dz in enumerate((-0.052, 0.052), 1):
        c.cyl_y(f"Dobradiça - parafuso {i}", f"{hinge[0]} - 0.014", f"{ZC} + {num(dz)}", f"{YF} - 0.004", 0.003, 0.001, "Aço galvanizado", detail=FINE)
    porthole_door(c, "Porta", hinge, ZC, RP, ang, [
        ("aro", "Alumínio anodizado", DOOR_RING, 44, FULL, True),
        ("moldura do vidro", dark, DOOR_TRIM, 28, FULL, True),
        ("vidro", "Vidro fumê", DOOR_GLASS, 16, FULL, "open"),
    ])
    door_part(c, "Porta - braço da dobradiça", hinge, ang, RP, -1.045, -0.90, 0.004, 0.06, ZC, -0.19, 0.19, "Cromado")
    door_part(c, "Porta - puxador", hinge, ang, RP, 0.80, 1.035, 0.03, 0.135, ZC, -0.26, 0.26, "Alumínio anodizado")
    door_part(c, "Porta - puxador - pega", hinge, ang, RP, 0.87, 1.037, 0.06, 0.137, ZC, -0.20, 0.20, "Plástico cinza", detail=FINE)
    door_part(c, "Porta - trinco", hinge, ang, RP, 0.83, 0.87, -0.07, 0.01, ZC, -0.035, 0.035, "Cromado", detail=FINE)
    c.box("Fecho da porta", f"0.82*{RP}", f"{YF} - 0.0008", f"{ZC} - 0.02", f"0.06*{RP}", 0.0008, 0.04, "Plástico preto", detail=FINE)

    # --- back ---
    c.box("Tampa traseira", f"-0.36*Largura", YB, f"{ZC} - 0.36*Largura", "0.72*Largura", 0.002, "0.72*Largura", "Aço galvanizado")
    k = 0
    for sx in (-1, 0, 1):
        for sz in (-1, 1):
            k += 1
            c.cyl_y(f"Tampa traseira - parafuso {k}", f"{num(0.34 * sx)}*Largura", f"{ZC} + {num(0.34 * sz)}*Largura", f"{YB} + 0.002", 0.004, 0.0015, "Aço galvanizado", detail=FINE)
    k = 0
    for sx in (-1, 1):
        for sz in (-1, 1):
            k += 1
            x, z = f"{num(0.2 * sx)}*Largura", f"{ZC} + {num(0.2 * sz)}*Largura"
            c.cyl_y(f"Tampa do parafuso de transporte {k}", x, z, f"{YB} + 0.002", 0.017, 0.005, "Plástico cinza claro")
            c.box(f"Tampa do parafuso de transporte {k} - fenda", f"{x} - 0.01", f"{YB} + 0.007", f"{z} - 0.0015", 0.02, 0.0005, 0.003, "Plástico cinza", detail=FINE)
    for i in range(7):
        c.box(f"Ventilação traseira {i + 1}", f"-0.2*Largura", f"{YB} + 0.0005", f"{Z0} + 0.03 + {num(0.011 * i)}", "0.4*Largura", 0.0005, 0.005, "Aço pintado preto", detail=FINE)
    c.box("Etiqueta de identificação", f"{W2} - 0.16", f"{YB} + 0.0005", f"{ZT} - 0.075", 0.1, 0.0005, 0.045, "Plástico cinza claro", detail=FINE)
    # Water inlet: valve, elbow and hose to the tap on the wall.
    VX, VZ = f"(-{W2} + 0.07)", "(Altura - 0.085)"
    HY = f"({YB} + 0.015)"  # the hoses run in the gap behind the cabinet
    WX = f"({VX} + 0.11)"
    c.cyl_y("Entrada de água - válvula", VX, VZ, f"{YB} - 0.001", 0.013, 0.008, "Plástico azul")
    c.cyl_y("Entrada de água - porca", VX, VZ, f"{YB} + 0.005", 0.016, 0.012, "Plástico cinza claro")
    sphere(c, "Mangueira de entrada - curva 1", VX, HY, VZ, 0.0095, "Borracha cinza", detail=FULL)
    c.cyl_x("Mangueira de entrada", HY, VZ, VX, 0.0095, "0.11", "Borracha cinza")
    sphere(c, "Mangueira de entrada - curva 2", WX, HY, VZ, 0.0095, "Borracha cinza", detail=FULL)
    c.cyl_y("Mangueira de entrada - ponta", WX, VZ, HY, 0.0095, f"{YW} - {HY} - 0.008", "Borracha cinza")
    c.cyl_y("Mangueira de entrada - porca da torneira", WX, VZ, f"{YW} - 0.01", 0.016, 0.01, "Latão")
    # Drain: outlet low on the back, hose clipped up the back and hooked to the wall drain.
    OX, OZ, UZ = f"({W2} - 0.15)", f"({Z0} + 0.07)", "(Altura - 0.23)"
    c.cyl_y("Saída de esgoto - bocal", OX, OZ, f"{YB} - 0.001", 0.015, 0.006, "Plástico cinza")
    sphere(c, "Mangueira de esgoto - curva 1", OX, HY, OZ, 0.011, "Plástico cinza", detail=FULL)
    c.cyl("Mangueira de esgoto", OX, HY, OZ, 0.011, f"{UZ} - {OZ}", "Plástico cinza")
    sphere(c, "Mangueira de esgoto - curva 2", OX, HY, UZ, 0.011, "Plástico cinza", detail=FULL)
    c.cyl_y("Mangueira de esgoto - ponta", OX, UZ, HY, 0.011, f"{YW} - {HY}", "Plástico cinza")
    for i, z in enumerate((f"({OZ} + 0.12)", f"({UZ} - 0.10)"), 1):
        c.box(f"Mangueira de esgoto - presilha {i}", f"{OX} - 0.016", YB, z, 0.032, 0.028, 0.012, "Plástico cinza claro", detail=FINE)
    for i in range(6):
        c.cyl(f"Mangueira de esgoto - anel {i + 1}", OX, HY, f"{OZ} + 0.02 + {num(0.012 * i)}", 0.0125, 0.005, "Plástico cinza", detail=FINE)
    # Power cable.
    CX, CZ = f"({W2} - 0.05)", "(Altura - 0.07)"
    c.cyl_y("Cabo de força - passa-fio", CX, CZ, f"{YB} - 0.001", 0.009, 0.01, "Plástico preto")
    tube(c, "Cabo de força", "Side", [(f"{YB} + 0.005", CZ), (f"{YB} + 0.010", CZ, -0.008), (f"{YB} + 0.018", f"{CZ} - 0.008"), (f"{YB} + 0.018", f"{CZ} - 0.40")], CX, 0.0045, "Borracha", FINE)
    c.box("Cabo de força - plugue", f"{CX} - 0.018", f"{YB} + 0.009", f"{CZ} - 0.445", 0.036, 0.018, 0.045, "Plástico preto", detail=FINE)
    for i, dx in enumerate((-0.0095, 0, 0.0095), 1):
        c.cyl(f"Cabo de força - pino {i}", f"{CX} + {num(dx)}", f"{YB} + 0.018", f"{CZ} - 0.463", 0.002, 0.018, "Latão", detail=FINE)

    c.mep = {"Fixture": {"drain_units": 3, "supply_weight": 1.0, "hot_water": False}}
    c.connector("Esgoto", "Sanitary", OX, YW, UZ, "Back", 0.04)
    c.connector("Água fria", "ColdWater", WX, YW, VZ, "Back", 0.02)

    c.type("Lava e seca 11 kg 60 x 60 x 85 cm", "Lava e seca frontal de 11 kg; ponto de água fria e esgoto; prever TUE de 1800 VA")
    c.type("Lava e seca 13 kg 63 x 67 x 89 cm", "Lava e seca frontal de 13 kg; ponto de água fria e esgoto; prever TUE de 2000 VA",
           Largura=0.63, Profundidade=0.67, Altura=0.89, DiametroPorta=0.52, DiametroTambor=0.50, ProfundidadeTambor=0.40)
    return c
