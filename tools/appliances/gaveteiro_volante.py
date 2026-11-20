"""Gaveteiro volante: a mobile pedestal with two drawers and a file drawer for hanging folders, on four casters, with a lock."""

from kit import *
from _escritorio import declare
from escrivaninha import drawer


def caster(c, n, x, y):
    """A twin-wheel caster under the base: plate, swivel stem, hood and two wheels along X."""
    c.box(f"Rodízio {n} - placa", f"{p(x)} - 0.025", f"{p(y)} - 0.025", 0.052, 0.05, 0.05, 0.003, "Aço galvanizado", detail=FINE)
    c.cyl(f"Rodízio {n} - pino", x, y, 0.044, 0.008, 0.009, "Aço galvanizado", detail=FINE)
    c.profile(f"Rodízio {n} - carenagem", "Side", [(f"{p(y)} - 0.012", 0.044), (f"{p(y)} + 0.012", 0.044), (f"{p(y)} + 0.03", 0.03, 0.02),
                                                    (f"{p(y)} + 0.006", 0.006), (f"{p(y)} - 0.012", 0.03)], f"{p(x)} - 0.012", 0.024,
              "Plástico preto")
    for side, x0 in (("esquerda", f"{p(x)} - 0.032"), ("direita", f"{p(x)} + 0.012")):
        c.cyl_x(f"Rodízio {n} - roda {side}", f"{p(y)} + 0.012", 0.024, x0, 0.024, 0.02, "Borracha")


def build():
    c = Component("Gaveteiro volante", "furniture", "gaveteiro-volante")
    W = c.param("Largura", 0.4)
    D = c.param("Profundidade", 0.5)
    H = c.param("Altura", 0.6)
    a1 = c.param("AberturaGaveta1", 0, "Length", True)
    a2 = c.param("AberturaGaveta2", 0, "Length", True)
    a3 = c.param("AberturaGaveta3", 0, "Length", True)
    c.open_pose.update({a1: 0.3, a2: 0.2, a3: 0.36})
    desc = ("Gaveteiro volante de escritório: duas gavetas e um gavetão para pastas suspensas, fechadura com trava das três gavetas, "
            "puxadores de alumínio e quatro rodízios duplos; cabe sob a estação de trabalho")
    c.type("Gaveteiro volante 40x50", desc)
    c.type("Gaveteiro volante 45x55", desc, Largura=0.45, Profundidade=0.55, Altura=0.62)
    declare(c, "Melamina carvalho", "Melamina grafite", "Papel kraft")

    body, front = "Melamina grafite", "Melamina carvalho"
    t = 0.018
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{D}/2", f"{D}/2"
    zb = 0.055  # underside of the carcass, above the casters

    c.box("Gaveteiro simplificado", xl, yf, zb, W, D, f"{H} - {zb}", front, detail=COARSE, in_plan=True)
    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        c.cyl(f"Rodízio simplificado {n}", f"{sx}*({W}/2 - 0.05)", f"{sy}*({D}/2 - 0.05)", 0, 0.025, zb, "Plástico preto", detail=COARSE)

    # Carcass: top, base, sides and back.
    c.box("Tampo", xl, yf, f"{H} - 0.025", W, D, 0.025, body, in_plan=True)
    c.box("Base", xl, f"{yf} + 0.02", zb, W, f"{D} - 0.02", t, body)
    c.box("Lateral esquerda", xl, f"{yf} + 0.02", f"{zb} + {t}", t, f"{D} - 0.02", f"{H} - 0.025 - {zb} - {t}", body)
    c.box("Lateral direita", f"{xr} - {t}", f"{yf} + 0.02", f"{zb} + {t}", t, f"{D} - 0.02", f"{H} - 0.025 - {zb} - {t}", body)
    c.box("Fundo", f"{xl} + {t}", f"{yb} - 0.015", f"{zb} + {t}", f"{W} - {2 * t}", 0.006, f"{H} - 0.025 - {zb} - {t}", body)

    # Drawers: two small ones over the file drawer.
    x0, x1 = f"{xl} + {t}", f"{xr} - {t}"
    z0, z3 = f"{zb} + {t}", f"{H} - 0.025"
    hh = f"({z3} - {z0})"
    za, zc = f"{z0} + 0.52*{hh}", f"{z0} + 0.76*{hh}"
    fy = f"{yf} + 0.02"
    dd = f"{D} - 0.06"
    bar = f"0.5*{W}"
    drawer(c, 1, x0, x1, zc, z3, fy, dd, a1, front, "Alumínio anodizado", bar)
    drawer(c, 2, x0, x1, za, zc, fy, dd, a2, front, "Alumínio anodizado", bar)
    drawer(c, 3, x0, x1, z0, za, fy, dd, a3, front, "Alumínio anodizado", bar)

    # Hanging folders in the file drawer: rails on its sides and a few folders.
    yd = f"{fy} - {a3} + 0.03"
    zr = f"{za} - 0.04"
    for side, x in (("esquerdo", f"{x0} + 0.026"), ("direito", f"{x1} - 0.036")):
        c.box(f"Gaveta 3 - trilho de pastas {side}", x, yd, zr, 0.01, f"{dd} - 0.06", 0.012, "Aço galvanizado", detail=FINE)
    for k in range(5):
        y = f"{yd} + 0.04 + {k}*({dd} - 0.14)/4"
        c.box(f"Pasta suspensa {k + 1}", f"{x0} + 0.04", y, f"{z0} + 0.03", f"{W} - {2 * t} - 0.08", 0.004, f"{za} - {p(z0)} - 0.08",
              "Papel kraft", detail=FINE)
        c.box(f"Pasta suspensa {k + 1} - haste", f"{x0} + 0.03", y, f"{zr} + 0.006", f"{W} - {2 * t} - 0.06", 0.006, 0.006,
              "Plástico preto", detail=FINE)

    # Lock at the top right of the first drawer.
    c.cyl_y("Fechadura - cilindro", f"{xr} - 0.04", f"{z3} - 0.03", f"{fy} - {a1} - 0.004", 0.01, 0.004, "Cromado", detail=FINE)
    c.box("Fechadura - fenda", f"{xr} - 0.041", f"{fy} - {a1} - 0.0045", f"{z3} - 0.036", 0.002, 0.001, 0.012, "Plástico preto",
          detail=FINE)

    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        caster(c, n, f"{sx}*({W}/2 - 0.05)", f"{sy}*({D}/2 - 0.05)")
    return c
