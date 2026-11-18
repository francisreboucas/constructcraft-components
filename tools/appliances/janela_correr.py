"""Janela de correr de alumínio, duas folhas: marco com trilho de dois canais, folhas com
montantes de encontro interligados, roldanas, gaxetas, fecho e drenos."""

from kit import *
from janela_comum import *
from _janela_correr_kit import *

D = 0.07  # frame depth across the wall
T = 0.026  # leaf depth
YS = (-0.016, 0.016)  # track centers: exterior leaf, interior leaf
EDGE = 0.006  # leaf edge from the frame's outer edge (web + brush gap)
OVER = 0.03  # overlap of the meeting stiles


def build() -> Component:
    # "Janela de correr" is a component of the app template: the library's needs another name.
    c = Component("Janela de correr de alumínio", "windows", "janela-correr", "Window")
    L = c.param("Largura", 1.2)
    H = c.param("Altura", 1.2)
    c.param("Peitoril", 1.0)
    Ab = opening_param(c, "Abertura", "Number", 0.8)  # 0 closed, 1 the interior leaf over the exterior one
    c.opening = {"width": "Largura", "height": "Altura", "sill": "Peitoril", "own_symbol": True}
    stone(c)
    x0, x1 = f"(-{L}/2)", f"({L}/2)"
    ye, yi = YS
    wf = f"(({L} + {2 * OVER - 2 * EDGE:g})/2)"  # leaf width
    d = f"({Ab}*({L} - {2 * EDGE + 0.012:g} - {wf}))"  # travel of the interior leaf, up to the track's stop
    zb, zt = 0.004, f"({H} - 0.006)"

    # --- coarse ----------------------------------------------------------------------
    coarse_frame(c, L, H, D)
    c.box("Folha externa simplificada", f"{x0} + 0.03", ye - T / 2, 0.03, f"{wf} - 0.024", T, f"{H} - 0.06", GLASS, COARSE, in_plan=True)
    c.box("Folha interna simplificada", f"{x1} - 0.006 - {wf} - {d}", yi - T / 2, 0.03, f"{wf} - 0.024", T, f"{H} - 0.06", GLASS, COARSE, in_plan=True)
    peitoril(c, L, -D / 2, D / 2)

    # --- frame -----------------------------------------------------------------------
    frame(c, L, H, D, YS)

    # --- exterior leaf: closed on the left, meeting stile on the right ----------------
    xa_e = f"({x0} + {EDGE})"
    xb_e = f"({xa_e} + {wf})"
    glazed_leaf(c, "Folha externa", xa_e, xb_e, ye, zb, zt, T, (0.022, 0.03, 0.04, 0.024), "right")
    interlock(c, "Folha externa", xb_e, "right", ye + T / 2, +1, zb, zt)
    # pull: a small shell on the room face of the outer stile
    c.profile("Folha externa puxador concha", "Front", rrect(f"{xa_e} + 0.006", f"{H}/2 - 0.05", f"{xa_e} + 0.02", f"{H}/2 + 0.05", 0.006),
              ye + T / 2, 0.0016, "Alumínio fundido", FINE)

    # --- interior leaf: closed on the right, meeting stile on the left, slides left ---
    xb_i = f"({x1} - {EDGE} - {d})"
    xa_i = f"({xb_i} - {wf})"
    glazed_leaf(c, "Folha interna", xa_i, xb_i, yi, zb, zt, T, (0.03, 0.022, 0.04, 0.024), "left")
    interlock(c, "Folha interna", xa_i, "left", yi - T / 2, -1, zb, zt)

    # latch on the room face of the interior leaf's meeting stile, with its keeper on the other leaf
    xm, zc, yf = f"({xa_i} + 0.015)", f"({H}/2)", yi + T / 2
    c.profile("Fecho base", "Front", rrect(f"{xm} - 0.0095", f"{zc} - 0.04", f"{xm} + 0.0095", f"{zc} + 0.04", 0.008), yf, 0.006, "Alumínio fundido")
    c.cyl_y("Fecho eixo", xm, f"{zc} + 0.022", yf + 0.006, 0.0035, 0.0065, "Alumínio fundido", FINE)
    c.profile("Fecho alavanca", "Front", [
        (f"{xm} - 0.0055", f"{zc} + 0.022"), (f"{xm} - 0.0035", f"{zc} - 0.03", 0.0035), (f"{xm} + 0.0035", f"{zc} - 0.03"),
        (f"{xm} + 0.0055", f"{zc} + 0.022", 0.0055),
    ], yf + 0.006, 0.005, "Alumínio fundido")
    for k, z in enumerate((f"{zc} - 0.0365", f"{zc} + 0.0345"), 1):
        c.cyl_y(f"Fecho parafuso {k}", xm, z, yf + 0.006, 0.0018, 0.0008, "Inox escovado", FINE)

    # --- sealing, drainage and fixing -------------------------------------------------
    frame_finish(c, L, H, D, drains=(0.08,), screws_at=[
        (f"{x0} + {WEB}", +1, yi), (f"{x1} - {WEB}", -1, ye),
    ])
    # stops at the track's ends keep the interior leaf from hitting the jamb
    c.box("Batente do trilho", f"{x0} + {EDGE}", yi - 0.006, 0.0025, 0.012, 0.012, 0.012, "Plástico preto", FINE)

    d_ = "Janela de correr de duas folhas, alumínio"
    c.type("Janela de correr 100 x 100", d_, Largura=1.0, Altura=1.0, Peitoril=1.1)
    c.type("Janela de correr 120 x 120", d_, Largura=1.2, Altura=1.2, Peitoril=1.0)
    c.type("Janela de correr 150 x 120", d_, Largura=1.5, Altura=1.2, Peitoril=1.0)
    c.type("Janela de correr 200 x 120", d_, Largura=2.0, Altura=1.2, Peitoril=1.0)
    c.preview_size = (1.0, 0.3, 1.0)
    c.preview_base = 1.1
    return c
