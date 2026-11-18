"""Shared parts of the surface-mounted sliding doors (porta_correr, porta_correr_dupla): not a component.

Door frame (doorkit): x along the wall from the opening's center, y across it, z up from
the floor; the wall spans y = -WallThickness/2 .. WallThickness/2. The leaves run on the
+y face: each hangs from two carriages rolling in an aluminium top track, screwed to a
wooden header above the casing and hidden behind a wooden pelmet (bandô); a U guide on
the floor keeps the leaf's bottom on line. The opening is lined with plain jambs (no
stop) and mitred casings on both faces; the leaves lap the casings.

A leaf is drawn on a doorkit `Fr` with its origin at the leaf's outer edge (a along the
leaf, n = y absolute); `mx=True` mirrors it (the right leaf of a double door).
"""

from __future__ import annotations

from doorkit import *  # noqa: F401,F403
from doorkit import Fr, s, WT
from kit import e, p, FULL, FINE, COARSE, rrect

WOOD = "Madeira"
ALU = "Alumínio anodizado"
STEEL = "Aço galvanizado"
INOX = "Inox escovado"

# Across the wall, from its +y face (m).
LB, LF = 0.022, 0.057  # the leaf's back and front faces (it clears the casing's back band, 17 mm)
LC = (LB + LF) / 2
TB, TF = 0.0215, 0.0575  # the track
PB, PF = 0.062, 0.08  # the pelmet's front board
OV = 0.06  # the leaf laps the opening (and its 55 mm casings) on each side


def y(d) -> str:
    """y at the distance d (number or expression) from the wall's +y face."""
    return f"({WT}/2 + {e(d)})" if not isinstance(d, str) else f"({WT}/2 + {p(d)})"


def xspan(fr: Fr, a0, a1) -> tuple[str, str]:
    """(lowest x, width) of the leaf-local span a0..a1 (a0 < a1)."""
    xa, xb = fr.pt(a0, 0)[0], fr.pt(a1, 0)[0]
    return (xb if fr.mx else xa), s(a1, f"-{p(a0)}") if isinstance(a0, str) else s(a1, -a0)


def xof(fr: Fr, a) -> str:
    return fr.pt(a, 0)[0]


def frame(c, L, H):
    """Jamb linings without a stop and casings on both faces."""
    wood_frame(c, L, H, WOOD, stop=False, in_plan=True)


def leaf(c, fr: Fr, pre, Lf, H, names=("montante esquerdo", "montante direito")):
    """A stile-and-rail leaf with three raised panels, from a = 0 to Lf."""
    z0, z1 = 0.01, f"({H} + 0.06)"
    fr.box(f"{pre} simplificada", 0, Lf, y(LB), y(LF), z0, f"{H} + 0.05", WOOD, detail=COARSE)
    panel_leaf(fr, pre, 0, Lf, y(LB), y(LF), z0, z1, [(0.88, 0.14), (1.5, 0.09)], WOOD, sw=0.11, top=0.12, bottom=0.2)
    for item in c.items:
        if item["name"].startswith(pre + " - montante"):
            item["name"] = (item["name"].replace("montante da dobradiça", names[0])
                            .replace("montante da fechadura", names[1]))


def carriage(c, fr: Fr, pre, a, H):
    """A hanger: a plate on the leaf's top, the adjusting bolt and the 4-wheel carriage in the track."""
    zl = f"({H} + 0.06)"  # the leaf's top
    fr.box(f"{pre} - chapa", s(a, -0.035), s(a, 0.035), y(LB + 0.003), y(LF - 0.003), zl, 0.004, STEEL)
    for k, da in enumerate((-0.026, 0.026)):
        fr.cyl(f"{pre} - parafuso da chapa {k + 1}", s(a, da), y(LC), f"{zl} + 0.004", 0.0035, 0.0015, "Cromado", detail=FINE)
    fr.cyl(f"{pre} - porca de regulagem", a, y(LC), f"{zl} + 0.004", 0.0075, 0.007, "Cromado", detail=FINE)
    fr.cyl(f"{pre} - parafuso de suspensão", a, y(LC), f"{zl} + 0.011", 0.004, 0.019, "Cromado")
    fr.box(f"{pre} - corpo", s(a, -0.028), s(a, 0.028), y(0.031), y(0.048), f"{H} + 0.086", 0.013, STEEL)
    zw = f"({H} + 0.0925)"  # the wheels ride on the track's lips
    for i, da in enumerate((-0.018, 0.018)):
        x = xof(fr, s(a, da))
        c.cyl_y(f"{pre} - eixo {i + 1}", x, zw, y(0.024), 0.0025, 0.031, "Cromado", detail=FINE)
        for j, yw in enumerate((0.024, 0.0495)):
            c.cyl_y(f"{pre} - roda {2 * i + j + 1}", x, zw, y(yw), 0.0095, 0.0055, "Plástico cinza claro", detail=FINE)


def track(c, H, x0, x1, stops=()):
    """The top track from x0 to x1 (x0 < x1) on its wooden header, the pelmet around it, end stops at `stops` (x of their lower end)."""
    zb, zl = f"({H} + 0.08)", f"({H} + 0.083)"
    zi, zt = f"({H} + 0.118)", f"({H} + 0.12)"
    ln = f"({x1} - {x0})"
    c.profile("Trilho superior", "Side", [
        (y(TB), zb), (y(TB + 0.0095), zb), (y(TB + 0.0095), zl), (y(TB + 0.002), zl), (y(TB + 0.002), zi),
        (y(TF - 0.002), zi), (y(TF - 0.002), zl), (y(TF - 0.0095), zl), (y(TF - 0.0095), zb), (y(TF), zb), (y(TF), zt), (y(TB), zt),
    ], x0, ln, ALU)
    c.box("Testeira", x0, y(0), f"{H} + 0.07", ln, TB, 0.075, WOOD)
    for side, x in (("esquerda", f"{x0} - 0.003"), ("direita", x1)):
        c.box(f"Tampa do trilho {side}", x, y(TB), zb, 0.003, TF - TB, 0.04, "Plástico preto", detail=FINE)
    for k, x in enumerate(stops):
        c.box(f"Batente de fim de curso {k + 1}", x, y(TB + 0.0025), zl, 0.025, TF - TB - 0.005, 0.03, "Borracha", detail=FINE)
    # The pelmet: a front board with a rounded bottom edge, a top board and two end boards.
    px0, px1 = f"({x0} - 0.018)", f"({x1} + 0.018)"
    pl = f"({px1} - {px0})"
    c.box("Bandô simplificado", px0, y(0), f"{H} + 0.045", pl, PF, 0.118, WOOD, detail=COARSE)
    c.profile("Bandô - frente", "Side", [
        (y(PB), f"{H} + 0.045"), (y(PF - 0.005), f"{H} + 0.045", 0.005), (y(PF), f"{H} + 0.05"), (y(PF), f"{H} + 0.145"), (y(PB), f"{H} + 0.145"),
    ], px0, pl, WOOD)
    c.profile("Bandô - tampa", "Side", [
        (y(0), f"{H} + 0.145"), (y(PF), f"{H} + 0.145"), (y(PF), f"{H} + 0.158", 0.005), (y(PF - 0.005), f"{H} + 0.163"), (y(0), f"{H} + 0.163"),
    ], px0, pl, WOOD)
    for side, x in (("esquerda", px0), ("direita", x1)):
        c.box(f"Bandô - cabeceira {side}", x, y(0), f"{H} + 0.045", 0.018, PB, 0.1, WOOD)


def floor_guide(c, pre, gx):
    """A U guide screwed to the floor, its cheeks either side of the leaf's bottom."""
    c.box(f"{pre} - base", f"{gx} - 0.025", y(LB - 0.0035), 0, 0.05, LF - LB + 0.016, 0.003, "Plástico preto")
    c.box(f"{pre} - aba traseira", f"{gx} - 0.025", y(LB - 0.0035), 0.003, 0.05, 0.002, 0.03, "Plástico preto")
    c.box(f"{pre} - aba frontal", f"{gx} - 0.025", y(LF + 0.0015), 0.003, 0.05, 0.002, 0.03, "Plástico preto")
    for k, dx in enumerate((-0.016, 0.016)):
        c.cyl(f"{pre} - parafuso {k + 1}", f"{gx} + {e(dx)}", y(LF + 0.0075), 0.003, 0.0035, 0.0012, "Cromado", detail=FINE)


def bar_pull(c, fr: Fr, pre, a, zc, length=0.45):
    """A round bar pull on two standoffs, on the leaf's front (+y) face."""
    x = xof(fr, a)
    c.cyl(f"{pre} - barra", x, y(LF + 0.05), f"{zc} - {e(length / 2)}", 0.0125, length, INOX)
    for k, dz in enumerate((-length / 2 + 0.06, length / 2 - 0.06)):
        c.cyl_y(f"{pre} - haste {k + 1}", x, f"{zc} + {e(dz)}", y(LF), 0.008, 0.045, INOX)
        c.cyl_y(f"{pre} - bucha {k + 1}", x, f"{zc} + {e(dz)}", y(LF), 0.013, 0.003, INOX, detail=FINE)


def cup_pull(c, fr: Fr, pre, a, zc, w=0.045, h=0.16):
    """A flush cup pull (concha) set in the leaf's back (-y) face: it passes the casing as the leaf slides."""
    x0, _ = xspan(fr, s(a, -w / 2), s(a, w / 2))
    z0, z1 = f"{zc} - {e(h / 2)}", f"{zc} + {e(h / 2)}"
    c.profile(f"{pre} - aro", "Front", rrect(x0, z0, f"{x0} + {e(w)}", z1, 0.02), y(LB - 0.0015), 0.0015, INOX)
    c.profile(f"{pre} - concha", "Front", rrect(f"{x0} + 0.006", f"{z0} + 0.006", f"{x0} + {e(w - 0.006)}", f"{z1} - 0.006", 0.015),
              y(LB - 0.0018), 0.0003, "Aço pintado preto", detail=FINE)


def hook_lock(c, fr: Fr, pre, a_edge, sg, zc):
    """A hook lock (bico de papagaio) mortised in the leaf's edge `a_edge` (the leaf's body on the side sg of it):
    face plate, hook slot and screws; a key cylinder on the front face, a flush turn on the back face."""
    def edge(d0, d1):  # a span measured outwards from the edge
        lo, hi = s(a_edge, -sg * d1), s(a_edge, -sg * d0)
        return (lo, hi) if sg > 0 else (hi, lo)
    a0, a1 = edge(0, 0.0006)
    fr.box(f"{pre} - testa", a0, a1, y(LC - 0.009), y(LC + 0.009), f"{zc} - 0.1", 0.2, INOX, detail=FINE)
    a0, a1 = edge(0.0006, 0.0008)
    fr.box(f"{pre} - bico", a0, a1, y(LC - 0.004), y(LC + 0.004), f"{zc} - 0.02", 0.04, "Plástico preto", detail=FINE)
    for k, dz in enumerate((-0.09, 0.082)):
        fr.box(f"{pre} - parafuso da testa {k + 1}", a0, a1, y(LC - 0.003), y(LC + 0.003), f"{zc} + {e(dz)}", 0.008, "Cromado", detail=FINE)
    x = xof(fr, s(a_edge, sg * 0.04))
    c.cyl_y(f"{pre} - espelho (frente)", x, zc, y(LF), 0.02, 0.004, INOX)
    c.cyl_y(f"{pre} - cilindro (frente)", x, zc, y(LF + 0.004), 0.0085, 0.002, "Latão", detail=FINE)
    c.box(f"{pre} - fenda da chave (frente)", f"{x} - 0.001", y(LF + 0.006), f"{zc} - 0.006", 0.002, 0.0004, 0.011, "Plástico preto", detail=FINE)
    c.cyl_y(f"{pre} - espelho (fundo)", x, zc, y(LB - 0.0015), 0.02, 0.0015, INOX)
    c.box(f"{pre} - tranqueta embutida (fundo)", f"{x} - 0.003", y(LB - 0.0019), f"{zc} - 0.012", 0.006, 0.0004, 0.024, "Aço pintado preto", detail=FINE)


def symbols(c, fr: Fr, fr0: Fr, pre, Lf, d):
    """Plan symbol: the leaf where it stands, and an arrow along the wall (d = +1 or -1 along a) where it slides."""
    fr.poly(f"Símbolo {pre}", [(0, y(LB)), (Lf, y(LB)), (Lf, y(LF)), (0, y(LF))], 0, 0.001, WOOD)
    c.plan_only(f"Símbolo {pre}")
    ac = f"({Lf})/2"
    a0, a1, ah = s(ac, -0.15 * d), s(ac, 0.15 * d), s(ac, 0.09 * d)
    n = LF + 0.06
    pts = [(a0, y(n - 0.004)), (ah, y(n - 0.004)), (ah, y(n - 0.02)), (a1, y(n)), (ah, y(n + 0.02)), (ah, y(n + 0.004)), (a0, y(n + 0.004))]
    if d < 0:
        pts.reverse()
    fr0.poly(f"Sentido de abertura {pre}", pts, 0, 0.001, WOOD)
    c.plan_only(f"Sentido de abertura {pre}")


def opening(c, open_value=0.75):
    """The instance parameter that slides the leaves: 0 closed, 1 fully open; returned clamped."""
    A = opening_param(c, "Abertura", open_value, kind="Number")
    return f"min(max({A}, 0), 1)"
