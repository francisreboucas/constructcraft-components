"""Criado-mudo: carcass on tapered legs with two drawers that slide open."""

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
    c = Component("Criado-mudo", "furniture", "criado-mudo")
    W = c.param("Largura", 0.45)
    D = c.param("Profundidade", 0.4)
    H = c.param("Altura", 0.55)
    LH = c.param("AlturaPes", 0.1)
    a1 = c.param("AberturaGaveta1", 0, "Length", True)
    a2 = c.param("AberturaGaveta2", 0, "Length", True)
    c.open_pose[a1] = 0.24
    c.open_pose[a2] = 0.1
    c.type("Criado-mudo 45 cm", "Mesa de cabeceira com gaveta")
    c.type("Criado-mudo 60 cm", "Mesa de cabeceira com gaveta", Largura=0.6)
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")

    wood, dark = "Madeira", "Madeira escura"
    t = 0.018
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{D}/2", f"{D}/2"

    # Coarse stand-ins: the old boxes.
    c.box("Corpo simplificado", xl, yf, LH, W, D, f"{H} - {LH}", wood, detail=COARSE, in_plan=True)
    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        c.box(f"Perna simplificada {n}", f"{sx}*({W}/2 - 0.045) - 0.015", f"{sy}*({D}/2 - 0.045) - 0.015", 0, 0.03, 0.03, LH, dark,
              detail=COARSE)

    # Top with a rounded front edge.
    r = 0.008
    zt0, zt1 = f"{H} - 0.022", H
    c.profile("Tampo", "Side", [(f"{yf} + {r}", zt0), (yb, zt0), (yb, zt1), (f"{yf} + {r}", zt1, r), (yf, f"{H} - {r}"),
                                 (yf, f"{zt0} + {r}", r)], xl, W, wood, in_plan=True)
    # Carcass.
    ys = f"{yf} + 0.006"  # the carcass front edge, behind the top's nose
    sd = f"{D} - 0.006"
    zc0 = LH
    hc = f"{H} - 0.022 - {LH}"
    c.box("Lateral esquerda", f"{xl} + 0.002", ys, zc0, t, sd, hc, wood)
    c.box("Lateral direita", f"{xr} - 0.002 - {t}", ys, zc0, t, sd, hc, wood)
    xi0, xi1 = f"{xl} + 0.002 + {t}", f"{xr} - 0.002 - {t}"
    wi = f"{W} - 0.004 - {2 * t}"
    c.box("Base da caixa", xi0, ys, zc0, wi, sd, t, wood)
    c.box("Travessa superior frontal", xi0, f"{ys} + 0.02", f"{H} - 0.022 - 0.02", wi, 0.06, 0.02, wood)
    c.box("Travessa superior traseira", xi0, f"{yb} - 0.08", f"{H} - 0.022 - 0.02", wi, 0.06, 0.02, wood)
    c.box("Fundo", xi0, f"{yb} - 0.012", f"{zc0} + {t}", wi, 0.006, f"{hc} - {t}", "Laminado branco")
    zo0, zo1 = f"{LH} + {t}", f"{H} - 0.022"
    zmid = f"({zo0} + {zo1})/2"
    c.box("Travessa entre gavetas", xi0, ys, f"{zmid} - {t / 2}", wi, 0.05, t, wood)
    # Edge shadow gap under the top.
    c.box("Rebaixo sob o tampo", f"{xl} + 0.006", f"{ys} + 0.004", f"{H} - 0.0225", f"{W} - 0.012", f"{sd} - 0.008", 0.001, dark,
          detail=FINE)

    # Drawers.
    bar = f"0.28*{W}"
    dd = f"{D} - 0.05"
    drawer(c, 1, xi0, xi1, f"{zmid} + {t / 2}", zo1, f"{ys} + 0.002", dd, a1, wood, "Latão", bar)
    drawer(c, 2, xi0, xi1, zo0, f"{zmid} - {t / 2}", f"{ys} + 0.002", dd, a2, wood, "Latão", bar)

    # Tapered legs with brass ferrules, on steel mounting plates.
    for n, (sx, sy, where) in enumerate(((-1, -1, "frontal esquerda"), (1, -1, "frontal direita"), (-1, 1, "traseira esquerda"),
                                         (1, 1, "traseira direita")), 1):
        cx, cy = f"{sx}*({W}/2 - 0.05)", f"{sy}*({D}/2 - 0.05)"
        c.cyl(f"Chapa da perna {where}", cx, cy, f"{LH} - 0.004", 0.03, 0.004, "Aço pintado preto", detail=FINE)
        turned(c, f"Perna {where}", cx, cy, [(0.0125, 0.028), (0.021, f"{LH} - 0.012"), (0.021, f"{LH} - 0.004")], dark)
        turned(c, f"Ponteira da perna {where}", cx, cy, [(0.0105, 0.003), (0.013, 0.028)], "Latão", detail=FINE)
        c.cyl(f"Feltro da perna {where}", cx, cy, 0, 0.0095, 0.003, "Feltro", detail=FINE)
    return c
