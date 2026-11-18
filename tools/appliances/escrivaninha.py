"""Escrivaninha: top on a side panel and a three-drawer unit, with a cable grommet."""

from kit import *


def turned(c, name, cx, cy, profile, material, detail=FULL):
    """A turned piece about the vertical axis at (cx, cy): profile = [(radius, z), …] from bottom to top."""
    pts = [(cx, profile[0][1])] + [(f"{p(cx)} + {p(r)}", z) for r, z in profile] + [(cx, profile[-1][1])]
    c.rev(name, "Front", pts, cy, cx, material, detail=detail)


def drawer(c, n, x0, x1, z0, z1, yf, depth, opening, front_mat, handle_mat, bar):
    """Drawer `n` in the opening x0..x1, z0..z1 whose front plane is yf; slides out by `opening`."""
    y = f"{p(yf)} - {opening}"
    yh = f"{p(yf)} - {opening}/2"
    tag = f"Gaveta {n}"
    rv = 0.0025  # reveal around the front
    c.box(f"{tag} - frente", f"{p(x0)} + {rv}", y, f"{p(z0)} + {rv}", f"{p(x1)} - {p(x0)} - {2 * rv}", 0.018,
          f"{p(z1)} - {p(z0)} - {2 * rv}", front_mat)
    g = 0.0125  # slide gap on each side
    bx0, bx1 = f"{p(x0)} + {g}", f"{p(x1)} - {g}"
    bz0, bz1 = f"{p(z0)} + 0.018", f"{p(z1)} - 0.03"
    yb = f"{y} + 0.018"
    bd = f"{p(depth)} - 0.018"
    c.box(f"{tag} - lateral esquerda", bx0, yb, bz0, 0.012, bd, f"{bz1} - {p(bz0)}", "Madeira clara")
    c.box(f"{tag} - lateral direita", f"{bx1} - 0.012", yb, bz0, 0.012, bd, f"{bz1} - {p(bz0)}", "Madeira clara")
    c.box(f"{tag} - fundo traseiro", f"{bx0} + 0.012", f"{y} + {p(depth)} - 0.012", bz0, f"{bx1} - {p(bx0)} - 0.024", 0.012,
          f"{bz1} - {p(bz0)} - 0.01", "Madeira clara")
    c.box(f"{tag} - base", f"{bx0} + 0.012", yb, f"{bz0} + 0.008", f"{bx1} - {p(bx0)} - 0.024", f"{bd} - 0.012", 0.005,
          "Laminado branco", detail=FINE)
    # Telescopic slides: fixed member on the carcass, middle member at half travel, inner member on the drawer.
    zs = f"({p(z0)} + {p(z1)})/2 - 0.022"
    for side, xa in (("esquerda", x0), ("direita", f"{p(x1)} - {g}")):
        c.box(f"{tag} - corrediça fixa {side}", f"{p(xa)} + {0.0 if side == 'esquerda' else 0.008}", f"{p(yf)} + 0.03", zs, 0.0045,
              f"{p(depth)} - 0.05", 0.044, "Aço galvanizado", detail=FINE)
        c.box(f"{tag} - corrediça intermediária {side}", f"{p(xa)} + 0.0042", f"{yh} + 0.03", f"{zs} + 0.004", 0.004,
              f"{p(depth)} - 0.05", 0.036, "Aço galvanizado", detail=FINE)
        c.box(f"{tag} - corrediça móvel {side}", f"{p(xa)} + {0.008 if side == 'esquerda' else 0.0}", f"{y} + 0.03", f"{zs} + 0.008", 0.0045,
              f"{p(depth)} - 0.05", 0.028, "Aço galvanizado", detail=FINE)
    # Bar handle on two posts.
    xm = f"({p(x0)} + {p(x1)})/2"
    zm = f"({p(z0)} + {p(z1)})/2"
    c.cyl_x(f"{tag} - puxador", f"{y} - 0.026", zm, f"{xm} - {p(bar)}/2", 0.005, bar, handle_mat, detail=FINE)
    for k, sx in (("esquerdo", "-"), ("direito", "+")):
        c.cyl_y(f"{tag} - pino do puxador {k}", f"{xm} {sx} ({p(bar)}/2 - 0.015)", zm, f"{y} - 0.026", 0.0035, 0.026, handle_mat,
                detail=FINE)
        turned_y = f"{xm} {sx} ({p(bar)}/2 - 0.015)"
        c.cyl_y(f"{tag} - roseta do puxador {k}", turned_y, zm, f"{y} - 0.003", 0.008, 0.003, handle_mat, detail=FINE)


def build():
    c = Component("Escrivaninha", "furniture", "escrivaninha")
    W = c.param("Largura", 1.2)
    D = c.param("Profundidade", 0.6)
    H = c.param("Altura", 0.75)
    G = c.param("Gaveteiro", 0.4)
    a1 = c.param("AberturaGaveta1", 0, "Length", True)
    a2 = c.param("AberturaGaveta2", 0, "Length", True)
    a3 = c.param("AberturaGaveta3", 0, "Length", True)
    c.open_pose.update({a1: 0.3, a2: 0.18, a3: 0.08})
    c.type("Escrivaninha 100x50", "Escrivaninha com gaveteiro", Largura=1.0, Profundidade=0.5)
    c.type("Escrivaninha 120x60", "Escrivaninha com gaveteiro")
    c.type("Escrivaninha 150x70", "Escrivaninha com gaveteiro", Largura=1.5, Profundidade=0.7)

    wood, dark, white = "Madeira", "Madeira escura", "Laminado branco"
    tt = 0.025  # top
    t = 0.018
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{D}/2", f"{D}/2"
    zu = f"{H} - {tt}"

    # Coarse stand-ins: the old boxes.
    c.box("Tampo simplificado", xl, yf, zu, W, D, tt, wood, detail=COARSE, in_plan=True)
    c.box("Lateral simplificada", xl, yf, 0, 0.025, D, zu, wood, detail=COARSE)
    c.box("Gaveteiro simplificado", f"{xr} - {G}", yf, 0, G, D, zu, wood, detail=COARSE)

    # Top with a rounded front edge and a dark edge band at the back.
    r = 0.01
    c.profile("Tampo", "Side", [(f"{yf} + {r}", zu), (yb, zu), (yb, H), (f"{yf} + {r}", H, r), (yf, f"{H} - {r}"), (yf, f"{zu} + {r}", r)],
              xl, W, wood, in_plan=True)
    c.box("Rebaixo sob o tampo", f"{xl} + 0.012", f"{yf} + 0.03", f"{zu} - 0.003", f"{W} - 0.024", f"{D} - 0.04", 0.003, dark, detail=FINE)
    zc = f"{zu} - 0.003"  # top of the carcass and of the side panel

    # Cable grommet at the back, on the left.
    gx, gy = f"{xl} + 0.2*{W}", f"{yb} - 0.075"
    c.rev("Passa-cabos - aro", "Front", [(f"{gx} + 0.024", H), (f"{gx} + 0.034", H), (f"{gx} + 0.034", f"{H} + 0.002"),
                                          (f"{gx} + 0.031", f"{H} + 0.0035"), (f"{gx} + 0.024", f"{H} + 0.0035")], gy, gx, "Plástico preto",
          detail=FINE)
    c.cyl("Passa-cabos - tampa", gx, gy, H, 0.024, 0.002, "Plástico cinza", detail=FINE)
    c.box("Passa-cabos - abertura", f"{gx} - 0.007", f"{gy} + 0.008", H, 0.014, 0.015, 0.0022, "Plástico preto", detail=FINE)

    # Left side panel on levelers, with a stretcher rail under the top.
    lv = 0.012
    c.box("Lateral esquerda", f"{xl} + 0.015", f"{yf} + 0.03", lv, 0.025, f"{D} - 0.04", f"{zc} - {lv}", wood)
    for n, y in enumerate((f"{yf} + 0.07", f"{yb} - 0.05"), 1):
        c.cyl(f"Sapata niveladora da lateral {n}", f"{xl} + 0.0275", y, 0, 0.011, lv, "Plástico preto", detail=FINE)
    ux = f"{xr} - 0.012 - {G}"  # left face of the drawer unit
    kw = f"{W} - 0.052 - {G}"  # knee space between the panel and the unit
    c.box("Painel frontal traseiro", f"{xl} + 0.04", f"{yb} - 0.07", f"{zc} - 0.38", kw, t, 0.38, wood)
    c.box("Travessa sob o tampo", f"{xl} + 0.04", f"{yf} + 0.08", f"{zc} - 0.05", kw, t, 0.05, wood)
    for n, (x, sx) in enumerate(((f"{xl} + 0.04", 1), (ux, -1)), 1):
        for m, y in enumerate((f"{yf} + 0.098", f"{yb} - 0.1"), 1):
            c.box(f"Cantoneira metálica {n}.{m}", x if sx > 0 else f"{x} - 0.03", y, f"{zc} - 0.003", 0.03, 0.03, 0.003, "Aço galvanizado",
                  detail=FINE)
            c.box(f"Cantoneira metálica {n}.{m} - aba", x if sx > 0 else f"{x} - 0.003", y, f"{zc} - 0.033", 0.003, 0.03, 0.03,
                  "Aço galvanizado", detail=FINE)

    # Drawer unit: plinth, carcass, three drawers.
    ph = 0.07
    x0, x1 = ux, f"{xr} - 0.012"
    ys = f"{yf} + 0.03"
    ud = f"{D} - 0.04"
    c.box("Rodapé do gaveteiro", f"{x0} + 0.01", f"{ys} + 0.04", lv, f"{G} - 0.02", f"{ud} - 0.05", ph - lv, dark)
    for n, (x, y) in enumerate(((f"{x0} + 0.04", f"{ys} + 0.07"), (f"{x1} - 0.04", f"{ys} + 0.07"), (f"{x0} + 0.04", f"{yb} - 0.05"),
                                (f"{x1} - 0.04", f"{yb} - 0.05")), 1):
        c.cyl(f"Sapata niveladora do gaveteiro {n}", x, y, 0, 0.011, lv, "Plástico preto", detail=FINE)
    hc = f"{zc} - {ph}"
    c.box("Gaveteiro - lateral esquerda", x0, ys, ph, t, ud, hc, wood)
    c.box("Gaveteiro - lateral direita", f"{x1} - {t}", ys, ph, t, ud, hc, wood)
    xi0, xi1 = f"{x0} + {t}", f"{x1} - {t}"
    wi = f"{G} - {2 * t}"
    c.box("Gaveteiro - base", xi0, ys, ph, wi, ud, t, wood)
    c.box("Gaveteiro - tampo interno", xi0, ys, f"{zc} - {t}", wi, ud, t, wood)
    c.box("Gaveteiro - fundo", xi0, f"{yb} - 0.022", f"{ph} + {t}", wi, 0.006, f"{hc} - {2 * t}", white)
    zo0, zo1 = ph + t, f"{zc} - {t}"
    ho = f"({zo1} - {zo0})"
    za, zb = f"{zo0} + 0.44*{ho}", f"{zo0} + 0.72*{ho}"
    c.box("Gaveteiro - travessa 1", xi0, ys, f"{zb} - {t / 2}", wi, 0.05, t, wood)
    c.box("Gaveteiro - travessa 2", xi0, ys, f"{za} - {t / 2}", wi, 0.05, t, wood)
    bar = f"0.34*{G}"
    dd = f"{D} - 0.09"
    fy = f"{ys} + 0.002"
    drawer(c, 1, xi0, xi1, f"{zb} + {t / 2}", zo1, fy, dd, a1, wood, "Inox escovado", bar)
    drawer(c, 2, xi0, xi1, f"{za} + {t / 2}", f"{zb} - {t / 2}", fy, dd, a2, wood, "Inox escovado", bar)
    drawer(c, 3, xi0, xi1, zo0, f"{za} - {t / 2}", fy, dd, a3, wood, "Inox escovado", bar)
    # Lock on the top drawer.
    c.cyl_y("Fechadura - espelho", f"{xi1} - 0.045", f"{zo1} - 0.03", f"{fy} - {a1} - 0.002", 0.009, 0.002, "Cromado", detail=FINE)
    c.box("Fechadura - fenda", f"{xi1} - 0.046", f"{fy} - {a1} - 0.0025", f"{zo1} - 0.035", 0.002, 0.001, 0.01, "Plástico preto", detail=FINE)
    return c
