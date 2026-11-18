"""Janela de correr com veneziana, alumínio branco: marco de quatro canais, duas folhas de
venezianas de palhetas fixas nos canais externos e duas folhas de vidro nos internos."""

from kit import *
from janela_comum import *
from _janela_correr_kit import *

WHITE = "Alumínio pintado branco"
D = 0.126  # frame depth across the wall
T = 0.024  # leaf depth
YS = (-0.045, -0.015, 0.015, 0.045)  # tracks: veneziana ext., veneziana int., glass ext., glass int.
EDGE = 0.006
OVER = 0.035  # overlap of the meeting stiles
N_SLATS = 36  # slats per louvered leaf


def slat(y, z):
    """Outline (y, z) of a Z-shaped louver slat centered at (y, z): it falls towards the exterior."""
    return [(plus(y, dy), plus(z, dz)) for dy, dz in (
        (-0.0105, -0.0145), (-0.0093, -0.0145), (-0.0093, -0.0118), (0.0105, 0.0105),
        (0.0105, 0.0145), (0.0093, 0.0145), (0.0093, 0.0118), (-0.0105, -0.0105))]


def louver_section(w, T):
    """Outline (a, t) of a louvered leaf's member: a tube with a shallow channel holding the slats' ends."""
    h = T / 2
    return [(0, -h), (w, -h), (w, -h + 0.0015), (w - 0.003, -h + 0.0015), (w - 0.003, h - 0.0015), (w, h - 0.0015), (w, h), (0, h)]


def louver_leaf(c, pre, xa, xb, yc, zb, zt, w, mat):
    wl, wr, wb, wt = w
    secs = (louver_section(wl, T), louver_section(wr, T), leaf_section(wb, T, lip=0.0, g=T / 2 - 0.0015, ch=0.003, groove=0.013),
            louver_section(wt, T))
    leaf_frame(c, pre, xa, xb, yc, zb, zt, secs, mat)
    sx0, sx1 = plus(xa, wl - 0.0025), minus(xb, wr - 0.0025)
    z0, z1 = plus(zb, wb), minus(zt, wt)
    pitch = f"({minus(z1, z0)}/{N_SLATS})"
    for k in range(N_SLATS):
        zk = f"({z0} + {k + 0.5:g}*{pitch})"
        # the middle slat draws the leaf in plan
        c.profile(f"{pre} palheta {k + 1}", "Side", slat(yc, zk), sx0, minus(sx1, sx0), mat, in_plan=k == N_SLATS // 2)
    for k, x in enumerate((plus(xa, 0.07), minus(xb, 0.07)), 1):
        c.cyl_y(f"{pre} roldana {k}", x, plus(zb, 0.0135), plus(yc, -0.0025), 0.0058, 0.005, "Plástico preto", FINE)
        c.cyl_y(f"{pre} eixo da roldana {k}", x, plus(zb, 0.0135), plus(yc, -T / 2 - 0.0004), 0.0018, T + 0.0008, "Inox escovado", FINE)
    for k, x in enumerate((plus(xa, 0.03), minus(xb, 0.06)), 1):
        c.box(f"{pre} calço anti-levantamento {k}", x, plus(yc, -0.004), zt, 0.03, 0.008, 0.0035, "Plástico preto", FINE)


def build() -> Component:
    c = Component("Janela de correr com veneziana", "windows", "janela-veneziana", "Window")
    L = c.param("Largura", 1.2)
    H = c.param("Altura", 1.2)
    c.param("Peitoril", 1.0)
    Av = opening_param(c, "AberturaVeneziana", "Number", 1.0)  # 0 closed, 1 the inner veneziana over the outer one
    Ag = opening_param(c, "AberturaVidro", "Number", 1.0)  # 0 closed, 1 the inner glass leaf over the outer one
    c.opening = {"width": "Largura", "height": "Altura", "sill": "Peitoril", "own_symbol": True}
    stone(c)
    c.material(WHITE, (240, 240, 236), "Metal", "Satin")
    x0, x1 = f"(-{L}/2)", f"({L}/2)"
    wf = f"(({L} + {2 * OVER - 2 * EDGE:g})/2)"
    travel = f"({L} - {2 * EDGE + 0.012:g} - {wf})"
    dv, dg = f"({Av}*{travel})", f"({Ag}*{travel})"
    zb, zt = 0.004, f"({H} - 0.006)"
    yv0, yv1, yg0, yg1 = YS

    # --- coarse ----------------------------------------------------------------------
    coarse_frame(c, L, H, D, WHITE)
    for name, xa, y, mat in (
        ("Veneziana externa simplificada", f"{x0} + 0.03", yv0, WHITE),
        ("Veneziana interna simplificada", f"{x1} - 0.006 - {wf} - {dv}", yv1, WHITE),
        ("Folha de vidro externa simplificada", f"{x0} + 0.03", yg0, GLASS),
        ("Folha de vidro interna simplificada", f"{x1} - 0.006 - {wf} - {dg}", yg1, GLASS),
    ):
        c.box(name, xa, y - T / 2, 0.03, f"{wf} - 0.024", T, f"{H} - 0.06", mat, COARSE, in_plan=True)
    peitoril(c, L, -D / 2, D / 2)

    # --- frame -----------------------------------------------------------------------
    frame(c, L, H, D, YS, mat=WHITE)

    # --- venezianas: louvered leaves in the two outer tracks ----------------------------
    wv = (0.035, 0.045, 0.07, 0.045)
    xa, xb = f"({x0} + {EDGE})", f"({x0} + {EDGE} + {wf})"
    louver_leaf(c, "Veneziana externa", xa, xb, yv0, zb, zt, wv, WHITE)
    interlock(c, "Veneziana externa", xb, "right", yv0 + T / 2, +1, zb, zt, w=0.03, mat=WHITE)
    c.profile("Veneziana externa puxador concha", "Front", rrect(f"{xa} + 0.008", f"{H}/2 - 0.05", f"{xa} + 0.026", f"{H}/2 + 0.05", 0.007),
              yv0 + T / 2, 0.0015, "Branco", FINE)
    xb = f"({x1} - {EDGE} - {dv})"
    xa = f"({xb} - {wf})"
    louver_leaf(c, "Veneziana interna", xa, xb, yv1, zb, zt, tuple(wv[i] for i in (1, 0, 2, 3)), WHITE)
    interlock(c, "Veneziana interna", xa, "left", yv1 - T / 2, -1, zb, zt, w=0.03, mat=WHITE)
    # latch of the venezianas: a slim lever on the room face of the inner one's meeting stile
    xm, zc, yf = f"({xa} + 0.022)", f"({H}/2)", yv1 + T / 2
    c.profile("Trinco da veneziana base", "Front", rrect(f"{xm} - 0.008", f"{zc} - 0.03", f"{xm} + 0.008", f"{zc} + 0.03", 0.006), yf, 0.0012, "Branco", FINE)
    c.profile("Trinco da veneziana alavanca", "Front", [
        (f"{xm} - 0.004", f"{zc} + 0.012"), (f"{xm} - 0.003", f"{zc} - 0.026", 0.003), (f"{xm} + 0.003", f"{zc} - 0.026"),
        (f"{xm} + 0.004", f"{zc} + 0.012", 0.004)], yf + 0.0012, 0.0012, "Branco", FINE)

    # --- glass leaves in the two inner tracks -------------------------------------------
    xa, xb = f"({x0} + {EDGE})", f"({x0} + {EDGE} + {wf})"
    glazed_leaf(c, "Folha de vidro externa", xa, xb, yg0, zb, zt, T, (0.022, 0.03, 0.04, 0.024), "right", mat=WHITE)
    interlock(c, "Folha de vidro externa", xb, "right", yg0 + T / 2, +1, zb, zt, mat=WHITE)
    xb = f"({x1} - {EDGE} - {dg})"
    xa = f"({xb} - {wf})"
    glazed_leaf(c, "Folha de vidro interna", xa, xb, yg1, zb, zt, T, (0.03, 0.022, 0.04, 0.024), "left", mat=WHITE)
    interlock(c, "Folha de vidro interna", xa, "left", yg1 - T / 2, -1, zb, zt, mat=WHITE)
    xm, yf = f"({xa} + 0.015)", yg1 + T / 2
    c.profile("Fecho base", "Front", rrect(f"{xm} - 0.0095", f"{zc} - 0.04", f"{xm} + 0.0095", f"{zc} + 0.04", 0.008), yf, 0.006, "Branco")
    c.cyl_y("Fecho eixo", xm, f"{zc} + 0.022", yf + 0.006, 0.0035, 0.0065, "Branco", FINE)
    c.profile("Fecho alavanca", "Front", [
        (f"{xm} - 0.0055", f"{zc} + 0.022"), (f"{xm} - 0.0035", f"{zc} - 0.03", 0.0035), (f"{xm} + 0.0035", f"{zc} - 0.03"),
        (f"{xm} + 0.0055", f"{zc} + 0.022", 0.0055)], yf + 0.006, 0.005, "Branco")
    for k, z in enumerate((f"{zc} - 0.0365", f"{zc} + 0.0345"), 1):
        c.cyl_y(f"Fecho parafuso {k}", xm, z, yf + 0.006, 0.0018, 0.0008, "Inox escovado", FINE)

    # --- sealing, drainage and fixing -------------------------------------------------
    frame_finish(c, L, H, D, drains=(0.08,), screws_at=[(f"{x0} + {WEB}", +1, yg1), (f"{x1} - {WEB}", -1, yg0)])
    for name, y in (("Batente do trilho da veneziana", yv1), ("Batente do trilho do vidro", yg1)):
        c.box(name, f"{x0} + {EDGE}", y - 0.006, 0.0025, 0.012, 0.012, 0.012, "Plástico preto", FINE)

    d_ = "Janela de correr de quatro folhas, duas venezianas e duas de vidro, para dormitório"
    c.type("Janela de correr com veneziana 120 x 120", d_, Largura=1.2, Altura=1.2, Peitoril=1.0)
    c.type("Janela de correr com veneziana 150 x 120", d_, Largura=1.5, Altura=1.2, Peitoril=1.0)
    c.type("Janela de correr com veneziana 200 x 120", d_, Largura=2.0, Altura=1.2, Peitoril=1.0)
    c.preview_size = (1.2, 0.3, 1.2)
    c.preview_base = 1.0
    return c
