"""Shared pieces of the aluminium sliding windows (janela de correr, janela veneziana).

Not a component (make.py skips modules starting with "_"). Frame of a
wall-hosted window as in `janela_comum`: x along the wall from the opening's
center, y across it (-y exterior, +y the room), z up from the sill.

The frame is an extruded aluminium section with one channel per track: the
jambs and the head hold the leaves' edges, the sill is a track with a rounded
rail under each leaf, a low lip outside and a higher one on the room side.
Sections are numbers (meters); positions are expressions over the parameters.
"""

from kit import *
from janela_comum import *

WEB = 0.0015  # wall thickness of the frame's extrusions
LIPW = 0.0015  # thickness of the frame's outer lips


def frame_section(D, ys, web, lip_e, lip_i, div, rail=0.0, divw=0.002, railw=0.003):
    """Outline (y, a[, r]) of a frame member: `a` from the member's outer edge (the wall) inwards.

    `ys` are the tracks' centers; `div` the height of the dividers between
    tracks, `rail` (sill only) the height of a rounded rail under each track.
    """
    h = D / 2
    pts = [(-h, 0), (-h, lip_e), (-h + LIPW, lip_e), (-h + LIPW, web)]
    for k, yc in enumerate(ys):
        if rail:
            pts += [(yc - railw / 2, web), (yc - railw / 2, rail, railw / 2), (yc + railw / 2, rail), (yc + railw / 2, web)]
        if k < len(ys) - 1:
            ym = (yc + ys[k + 1]) / 2
            pts += [(ym - divw / 2, web), (ym - divw / 2, div), (ym + divw / 2, div), (ym + divw / 2, web)]
    pts += [(h - LIPW, web), (h - LIPW, lip_i), (h, lip_i), (h, 0)]
    return pts


def _r(q):
    return tuple(q[2:3])


def frame(c, L, H, D, ys, lip=0.02, sill_lips=(0.018, 0.03), div=0.016, sill_div=0.014, rail=0.010, mat=ALU, in_plan=True):
    """The frame: two jambs and the head of one section, the sill track of another."""
    x0, x1 = f"(-{L}/2)", f"({L}/2)"
    jamb = frame_section(D, ys, WEB, lip, lip, div)
    c.profile("Marco montante esquerdo", "Plan", [(plus(x0, q[1]), q[0]) + _r(q) for q in jamb], 0, H, mat, in_plan=in_plan)
    c.profile("Marco montante direito", "Plan", [(minus(x1, q[1]), q[0]) + _r(q) for q in jamb], 0, H, mat, in_plan=in_plan)
    c.profile("Marco travessa superior", "Side", [(q[0], minus(H, q[1])) + _r(q) for q in jamb], x0, L, mat)
    sill = frame_section(D, ys, 0.0025, sill_lips[0], sill_lips[1], sill_div, rail)
    c.profile("Marco trilho inferior", "Side", [(q[0], q[1]) + _r(q) for q in sill], x0, L, mat)


def coarse_frame(c, L, H, D, mat=ALU, w=0.03):
    """The coarse stand-in of the frame: four bars of the frame's depth, the jambs drawn in plan."""
    y0 = -D / 2
    c.box("Marco simplificado esquerdo", f"(-{L}/2)", y0, 0, w, D, H, mat, COARSE, in_plan=True)
    c.box("Marco simplificado direito", f"({L}/2 - {w})", y0, 0, w, D, H, mat, COARSE, in_plan=True)
    c.box("Marco simplificado inferior", f"(-{L}/2 + {w})", y0, 0, f"({L} - {2 * w})", D, w, mat, COARSE)
    c.box("Marco simplificado superior", f"(-{L}/2 + {w})", y0, f"({H} - {w})", f"({L} - {2 * w})", D, w, mat, COARSE)


def leaf_section(w, T, lip=0.004, g=0.0075, ch=0.010, groove=0.0):
    """Outline (a, t) of a glazed sash member: a body of face width `w` and depth T,
    a glazing channel (half-width g, depth ch) whose lips stand `lip` proud of
    the body; `groove` cuts the roller channel under a bottom rail."""
    h = T / 2
    pts = [(0, -h), (w + lip, -h), (w + lip, -g), (w - ch, -g), (w - ch, g), (w + lip, g), (w + lip, h), (0, h)]
    if groove:
        pts += [(0, 0.0055), (groove, 0.0055), (groove, -0.0055), (0, -0.0055)]
    return pts


def leaf_frame(c, pre, xa, xb, yc, zb, zt, secs, mat=ALU, in_plan=True, detail=FULL):
    """The four members of a sash x xa..xb, z zb..zt centered on y = yc.

    `secs` = outlines (a, t) of the left stile, right stile, bottom rail and top rail.
    """
    sl, sr, sb, st = secs
    c.profile(f"{pre} montante esquerdo", "Plan", [(plus(xa, a), plus(yc, t)) for a, t in sl], zb, minus(zt, zb), mat, detail, in_plan)
    c.profile(f"{pre} montante direito", "Plan", [(minus(xb, a), plus(yc, t)) for a, t in reversed(sr)], zb, minus(zt, zb), mat, detail, in_plan)
    c.profile(f"{pre} travessa inferior", "Side", [(plus(yc, t), plus(zb, a)) for a, t in reversed(sb)], xa, minus(xb, xa), mat, detail)
    c.profile(f"{pre} travessa superior", "Side", [(plus(yc, t), minus(zt, a)) for a, t in st], xa, minus(xb, xa), mat, detail)


def glazed_leaf(c, pre, xa, xb, yc, zb, zt, T, w, meet, glass=GLASS, mat=ALU, gasket=RUBBER, rollers=True):
    """A glazed sliding sash with its glass, gaskets, rollers and anti-lift blocks.

    `w` = face widths (left stile, right stile, bottom rail, top rail) of the
    body; the glazing lips add 4 mm. `meet` is the side of its meeting stile
    ("left"/"right"), which gets the interlock fin towards the other track.
    Returns the light (x0, x1, z0, z1) inside the lips.
    """
    wl, wr, wb, wt = w
    lip, g = 0.004, 0.0075
    secs = (leaf_section(wl, T), leaf_section(wr, T), leaf_section(wb, T, groove=0.013 if rollers else 0.0), leaf_section(wt, T))
    leaf_frame(c, pre, xa, xb, yc, zb, zt, secs, mat)
    lx0, lx1 = plus(xa, wl + lip), minus(xb, wr + lip)
    lz0, lz1 = plus(zb, wb + lip), minus(zt, wt + lip)
    c.box(f"{pre} vidro", minus(lx0, 0.008), plus(yc, -0.002), minus(lz0, 0.008), f"{minus(lx1, lx0)} + 0.016", 0.004,
          f"{minus(lz1, lz0)} + 0.016", glass, in_plan=True)
    box_ring(c, f"{pre} gaxeta externa", minus(lx0, 0.0035), plus(lx1, 0.0035), minus(lz0, 0.0035), plus(lz1, 0.0035),
             0, 0.004, plus(yc, -g), plus(yc, -0.002), gasket, FINE)
    box_ring(c, f"{pre} gaxeta interna", minus(lx0, 0.0035), plus(lx1, 0.0035), minus(lz0, 0.0035), plus(lz1, 0.0035),
             0, 0.004, plus(yc, 0.002), plus(yc, g), gasket, FINE)
    if rollers:
        for k, x in enumerate((plus(xa, 0.07), minus(xb, 0.07)), 1):
            c.cyl_y(f"{pre} roldana {k}", x, plus(zb, 0.0135), plus(yc, -0.0025), 0.0058, 0.005, "Plástico preto", FINE)
            c.cyl_y(f"{pre} eixo da roldana {k}", x, plus(zb, 0.0135), plus(yc, -T / 2 - 0.0004), 0.0018, T + 0.0008, "Inox escovado", FINE)
    for k, x in enumerate((plus(xa, 0.03), minus(xb, 0.06)), 1):
        c.box(f"{pre} calço anti-levantamento {k}", x, plus(yc, -0.004), zt, 0.03, 0.008, 0.0035, "Plástico preto", FINE)
    return lx0, lx1, lz0, lz1


def interlock(c, pre, xedge, side, yface, toward, zb, zt, w=0.026, fin=0.0018, mat=ALU, detail=FULL):
    """The interlock fin of a meeting stile: a plate on the stile's face towards the other track.

    `xedge` = the leaf's edge on its meeting side ("left"/"right" = `side`),
    `yface` = the face it stands on, `toward` = +1 (to the room) or -1.
    """
    xa = xedge if side == "left" else minus(xedge, w)
    y0 = yface if toward > 0 else minus(yface, fin)
    c.box(f"{pre} aleta de encontro", xa, y0, plus(zb, 0.045), w, fin, f"{minus(zt, zb)} - 0.075", mat, detail)
    xb = plus(xedge, 0.0015) if side == "left" else minus(xedge, 0.0035)
    c.box(f"{pre} escova do encontro", xb, plus(y0, -0.0002) if toward > 0 else y0, plus(zb, 0.045), 0.002, fin + 0.0002,
          f"{minus(zt, zb)} - 0.075", "Borracha", FINE)


def frame_finish(c, L, H, D, drains=(0.08,), screw_y=0.0, screws_at=None):
    """Silicone cords around the frame, the drain slots of the sill's outer lip with their flaps,
    and the caps of the frame's fixing screws."""
    x0, x1 = f"(-{L}/2)", f"({L}/2)"
    h = D / 2
    box_ring(c, "Cordão de silicone externo", x0, x1, 0.012, H, 0, 0.004, -h - 0.0015, -h, "Borracha cinza", FINE, "lrt")
    box_ring(c, "Cordão de silicone interno", x0, x1, 0.005, H, 0, 0.004, h, h + 0.0015, "Borracha cinza", FINE, "lrt")
    n = 0
    for d in drains:
        for x in (plus(x0, d), minus(x1, d + 0.028)):
            n += 1
            c.box(f"Dreno {n}", x, -h - 0.0002, 0.0045, 0.028, 0.0022, 0.005, ALU, FINE, void=True)
            c.box(f"Aba do dreno {n}", minus(x, 0.002), -h - 0.0022, 0.0095, 0.032, 0.0022, 0.004, "Plástico preto", FINE)
    n = 0
    for x, sgn, yy in screws_at or ():
        for z in (0.15, f"{H}/2", f"{H} - 0.15"):
            n += 1
            c.cyl_x(f"Tampa de parafuso {n}", yy, z, x if sgn > 0 else minus(x, 0.001), 0.0045, 0.001, "Plástico cinza claro", FINE)
