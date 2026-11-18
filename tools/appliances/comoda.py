"""Cômoda: chest of three to five drawers on telescopic slides, a solid wood top and a recessed plinth."""

from kit import *
from _mobilia import EPS, Grp

CLOTHES = ("Tecido azul petróleo", "Roupa de cama branca", "Tecido mostarda")


def drawer(g, n, x0, x1, z0, z1, yf, depth, opening, bar):
    """Drawer `n` in the opening x0..x1, z0..z1 whose front plane is yf; slides out by `opening`."""
    y = f"({yf} - {opening})"
    yh = f"({yf} - {opening}/2)"
    tag = f"Gaveta {n}"
    rv = 0.0025  # reveal around the front
    g.box(f"{tag} - frente", f"{x0} + {rv}", y, f"{z0} + {rv}", f"{x1} - {x0} - {2 * rv}", 0.018, f"{z1} - {z0} - {2 * rv}", "MDF branco")
    gap = 0.0125  # room for the slides on each side
    bx0, bx1 = f"({x0} + {gap})", f"({x1} - {gap})"
    bz0, bh = f"({z0} + 0.018)", f"({z1} - {z0} - 0.05)"
    yb = f"{y} + 0.018"
    bd = f"{depth} - 0.018"
    g.box(f"{tag} - lateral esquerda", bx0, yb, bz0, 0.012, bd, bh, "Madeira clara")
    g.box(f"{tag} - lateral direita", f"{bx1} - 0.012", yb, bz0, 0.012, bd, bh, "Madeira clara")
    g.box(f"{tag} - traseira", f"{bx0} + 0.012", f"{y} + {depth} - 0.012", bz0, f"{bx1} - {bx0} - 0.024", 0.012, f"{bh} - 0.01",
          "Madeira clara")
    g.box(f"{tag} - fundo", f"{bx0} + 0.012", yb, f"{bz0} + 0.008", f"{bx1} - {bx0} - 0.024", f"{bd} - 0.012", 0.005, "Laminado branco")
    g.box(f"{tag} - contrafrente", f"{bx0} + 0.012", yb, bz0, f"{bx1} - {bx0} - 0.024", 0.012, f"{bh} - 0.01", "Madeira clara",
          detail=FINE)
    # Telescopic slides: the fixed member on the side panel, the middle one at half travel, the inner one on the drawer.
    zs = f"(({z0} + {z1})/2 - 0.018)"
    for side, xa, s in (("esquerda", x0, 0), ("direita", f"{x1} - {gap}", 1)):
        g.box(f"{tag} - corrediça fixa {side}", f"{xa} + {0.008 * s}", f"{yf} + 0.03", zs, 0.0045, f"{depth} - 0.05", 0.036, "Aço galvanizado",
              detail=FINE)
        g.box(f"{tag} - corrediça intermediária {side}", f"{xa} + 0.0042", f"{yh} + 0.03", f"{zs} + 0.004", 0.004, f"{depth} - 0.05", 0.028,
              "Aço galvanizado", detail=FINE)
        g.box(f"{tag} - corrediça móvel {side}", f"{xa} + {0.008 * (1 - s)}", f"{y} + 0.03", f"{zs} + 0.008", 0.0045, f"{depth} - 0.05", 0.02,
              "Cromado", detail=FINE)
    # Bar pull on two posts with roses.
    xm, zm = f"(({x0} + {x1})/2)", f"(({z0} + {z1})/2)"
    g.cyl_x(f"{tag} - puxador", f"{y} - 0.028", zm, f"{xm} - {bar}/2", 0.0055, bar, "Latão")
    for k, sx in (("esquerdo", "-"), ("direito", "+")):
        xp = f"{xm} {sx} ({bar}/2 - 0.016)"
        g.cyl_y(f"{tag} - pino do puxador {k}", xp, zm, f"{y} - 0.026", 0.0035, 0.026, "Latão", detail=FINE)
        g.cyl_y(f"{tag} - roseta do puxador {k}", xp, zm, f"{y} - 0.003", 0.008, 0.003, "Latão", detail=FINE)
    return bx0, bx1, f"{bz0} + 0.013", yb


def build():
    c = Component("Cômoda", "casework", "comoda", "Casework")
    W = c.param("Largura", 0.8)
    D = c.param("Profundidade", 0.45)
    H = c.param("Altura", 0.85)
    N = c.param("Gavetas", 4, "Number")
    A = [c.param(f"AberturaGaveta{i}", 0, "Length", True) for i in range(1, 6)]
    c.open_pose[A[0]] = 0.3
    c.open_pose[A[2]] = 0.15
    c.type("Cômoda 4 gavetas 80 cm", "Cômoda com 4 gavetas e tampo de madeira")
    c.type("Cômoda 5 gavetas 90 cm", "Cômoda alta com 5 gavetas e tampo de madeira", Largura=0.9, Altura=1.05, Gavetas=5)
    c.type("Cômoda 3 gavetas 120 cm", "Cômoda baixa e larga com 3 gavetas e tampo de madeira", Largura=1.2, Profundidade=0.5, Altura=0.75,
           Gavetas=3)
    c.material("MDF branco", (240, 240, 235), "Wood", "Satin")
    c.material("Tecido azul petróleo", (48, 92, 110), "Generic", "Matte")
    c.material("Tecido mostarda", (201, 152, 58), "Generic", "Matte")
    c.material("Roupa de cama branca", (243, 241, 235), "Generic", "Matte")
    MDF, TOP, HDF, STEEL = "MDF branco", "Madeira clara", "Laminado branco", "Aço galvanizado"

    T = 0.018
    g0 = 0.004  # glides
    xl, xr = f"(-{W}/2)", f"({W}/2)"
    yf, yb = f"(-{D}/2)", f"({D}/2)"
    zp = 0.08  # top of the plinth
    zb0 = f"({zp} + {T})"  # bottom of the drawer openings
    zt = f"({H} - 0.025)"  # under the wooden top
    zb1 = f"({zt} - {T})"  # top of the drawer openings
    xi0, xi1 = f"({xl} + {T})", f"({xr} - {T})"
    wi = f"({W} - {2 * T})"
    hr = f"(({zb1} - {zb0} - ({N} - 1)*{T})/{N})"  # height of a drawer opening
    hide = (f"{xl} + {T}/2", 0, f"{H}/2")  # inside the left side

    # Coarse stand-ins.
    c.box("Rodapé simplificado", xl, f"{yf} + 0.03", 0, W, f"{D} - 0.03", zp, MDF, detail=COARSE)
    c.box("Corpo simplificado", xl, yf, zp, W, D, f"{zt} - {zp}", MDF, detail=COARSE)
    c.box("Tampo simplificado", f"{xl} - 0.01", f"{yf} - 0.012", zt, f"{W} + 0.02", f"{D} + 0.012", 0.025, TOP, detail=COARSE, in_plan=True)

    # Carcass.
    for name, x0 in (("esquerda", xl), ("direita", xi1)):
        c.box(f"Lateral {name}", x0, yf, g0, T, D, f"{zt} - {g0}", MDF)
    c.box("Base", xi0, yf, zp, wi, f"{D} - 0.009", T, MDF)
    c.box("Painel superior", xi0, yf, zb1, wi, f"{D} - 0.009", T, MDF)
    c.box("Fundo", xi0, f"{yb} - 0.009", zb0, wi, 0.006, f"{zb1} - {zb0}", HDF)
    c.box("Rodapé frontal", xi0, f"{yf} + 0.03", g0, wi, T, f"{zp} - {g0}", MDF)
    c.box("Rodapé traseiro", xi0, f"{yb} - 0.06", g0, wi, T, f"{zp} - {g0}", MDF, detail=FINE)
    for name, x0, y0 in (("frontal esquerda", xl, yf), ("frontal direita", xi1, yf), ("traseira esquerda", xl, f"{yb} - 0.04"),
                         ("traseira direita", xi1, f"{yb} - 0.04")):
        c.box(f"Sapata {name}", f"{x0} + 0.001", f"{y0} + 0.002", 0, T - 0.002, 0.038, g0, "Plástico preto", detail=FINE)
    # Solid wood top with a rounded front edge, and the shadow gap under it.
    r = 0.008
    c.profile("Tampo", "Side", [(f"{yf} - 0.012 + {r}", zt), (yb, zt), (yb, H), (f"{yf} - 0.012 + {r}", H, r), (f"{yf} - 0.012", f"{H} - {r}"),
                                (f"{yf} - 0.012", f"{zt} + {r}", r)], f"{xl} - 0.01", f"{W} + 0.02", TOP, in_plan=True)
    c.box("Rebaixo sob o tampo", f"{xl} + 0.004", f"{yf} + 0.004", f"{zt} - 0.0005", f"{W} - 0.008", f"{D} - 0.008", 0.0005, "Madeira escura",
          detail=FINE)
    # Anti-tip bracket to the wall.
    c.box("Cantoneira antitombamento", -0.025, f"{yb} - 0.003", f"{zb1} - 0.04", 0.05, 0.003, 0.04, STEEL, detail=FINE)
    c.box("Cantoneira antitombamento - aba", -0.025, f"{yb} - 0.035", f"{zb1} - 0.003", 0.05, 0.032, 0.003, STEEL, detail=FINE)

    # Drawers, top down; the rows a type does not have fold into the left side.
    bar = f"min(0.32, 0.3*{W})"
    for i in range(1, 6):
        g = Grp(c) if i <= 3 else Grp(c, f"min(1, max({EPS}, {N} - {i - 1}))", hide)
        z1 = f"({zb1} - {i - 1}*({hr} + {T}))"
        z0 = f"({z1} - {hr})"
        if i > 1:  # the rail above this row
            g.box(f"Travessa entre gavetas {i - 1}", xi0, yf, z1, wi, 0.06, T, MDF)
            g.box(f"Travessa traseira entre gavetas {i - 1}", xi0, f"{yb} - 0.069", z1, wi, 0.06, T, MDF, detail=FINE)
        bx0, bx1, bz, ybox = drawer(g, i, xi0, xi1, z0, z1, yf, f"{D} - 0.04", A[i - 1], bar)
        if i == 1:  # folded clothes in the top drawer
            inner = f"({bx1} - {bx0} - 0.024)"
            sw = f"(({inner} - 0.04)/3)"
            for j, mat in enumerate(CLOTHES):
                for k in range(2):
                    g.box(f"Roupa dobrada {j + 1}.{k + 1}", f"{bx0} + 0.022 + {j}*({sw} + 0.01) + {0.004 * k}", f"{ybox} + 0.025 + {0.006 * k}",
                          f"{bz} + {0.034 * k}", f"{sw} - 0.008", 0.2, 0.033, mat if k == 0 else CLOTHES[(j + 1) % 3], detail=FINE)
    return c
