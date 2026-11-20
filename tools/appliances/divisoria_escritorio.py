"""Divisória de escritório: a free-standing panel of an aluminium frame, a fabric lower part and a glass band at the top.

The panel runs along X, centred on the origin, on two steel feet along Y. The glass band appears when the panel is
taller than 1,25 m (lower panels are all fabric).
"""

from kit import *
from _escritorio import declare
from _mobilia import EPS, Grp


def build():
    c = Component("Divisória de escritório", "furniture", "divisoria-escritorio")
    W = c.param("Largura", 1.2)
    H = c.param("Altura", 1.5)
    desc = ("Painel divisório de escritório autoportante: quadro de alumínio, painel acústico revestido de tecido, faixa de vidro "
            "no alto (nos painéis com mais de 1,25 m) e dois pés de aço com sapatas niveladoras")
    c.type("Divisória de escritório 120x150", desc)
    c.type("Divisória de escritório 160x150", desc, Largura=1.6)
    c.type("Divisória de escritório 120x120", desc, Altura=1.2)
    c.type("Divisória de escritório 80x150", desc, Largura=0.8)
    declare(c, "Tecido de divisória")
    c.preview_size = (1.2, 0.5, 1.5)

    al = "Alumínio anodizado"
    T = 0.06  # panel thickness
    f = 0.03  # frame profile width
    xl, xr = f"-{W}/2", f"{W}/2"
    z0 = 0.03  # bottom of the frame (above the feet)

    c.box("Divisória simplificada", xl, -T / 2, z0, W, T, f"{H} - {z0}", "Tecido de divisória", detail=COARSE, in_plan=True)

    # Frame: posts, bottom rail, top rail and the mid rail under the glass.
    c.box("Montante esquerdo", xl, -T / 2, z0, f, T, f"{H} - {z0}", al, in_plan=True)
    c.box("Montante direito", f"{xr} - {f}", -T / 2, z0, f, T, f"{H} - {z0}", al, in_plan=True)
    c.box("Travessa inferior", f"{xl} + {f}", -T / 2 + 0.004, z0, f"{W} - {2 * f}", T - 0.008, 0.07, al)
    c.box("Travessa superior", f"{xl} + {f}", -T / 2, f"{H} - {f}", f"{W} - {2 * f}", T, f, al)
    for side, x in (("esquerdo", xl), ("direito", f"{xr} - {f}")):
        c.box(f"Tampa do montante {side}", x, -T / 2, H, f, T, 0.004, "Plástico cinza", detail=FINE)

    # Glass band: shown on panels taller than 1,25 m.
    zg = 1.08  # top of the fabric part on a tall panel
    k = f"min(1, max({EPS}, ({H} - 1.25)*40))"
    zt = f"{zg} + (1 - {k})*({H} - {f} - {zg})"  # top of the fabric: the top rail when there is no glass
    c.box("Painel de tecido - face frontal", f"{xl} + {f}", -T / 2 + 0.006, f"{z0} + 0.07", f"{W} - {2 * f}", 0.016,
          f"{zt} - {z0} - 0.07", "Tecido de divisória")
    c.box("Painel de tecido - face traseira", f"{xl} + {f}", T / 2 - 0.022, f"{z0} + 0.07", f"{W} - {2 * f}", 0.016,
          f"{zt} - {z0} - 0.07", "Tecido de divisória")
    c.box("Painel de tecido - núcleo", f"{xl} + {f}", -T / 2 + 0.022, f"{z0} + 0.07", f"{W} - {2 * f}", T - 0.044, f"{zt} - {z0} - 0.07",
          "Aço galvanizado", detail=FINE)
    g = Grp(c, k, (0, 0, f"{H} - {f}/2"))
    g.box("Travessa intermediária", f"{xl} + {f}", -T / 2, zg, f"{W} - {2 * f}", T, f, al)
    g.box("Vidro", f"{xl} + {f}", -0.003, f"{zg} + {f}", f"{W} - {2 * f}", 0.006, f"{H} - {zg} - {2 * f}", "Vidro temperado")
    for side, y in (("frontal", -0.009), ("traseiro", 0.003)):
        g.box(f"Baguete do vidro {side} inferior", f"{xl} + {f}", y, f"{zg} + {f}", f"{W} - {2 * f}", 0.006, 0.012, "Borracha")
        g.box(f"Baguete do vidro {side} superior", f"{xl} + {f}", y, f"{H} - {f} - 0.012", f"{W} - {2 * f}", 0.006, 0.012, "Borracha")

    # Feet: steel bars along Y under each post, on two levelers each.
    for side, x in (("esquerdo", f"{xl} + {f}/2"), ("direito", f"{xr} - {f}/2")):
        c.profile(f"Pé {side}", "Side", [(-0.25, 0.008), (0.25, 0.008), (0.25, 0.02), (0.2, z0), (-0.2, z0), (-0.25, 0.02)], f"{x} - 0.025",
                  0.05, "Aço pintado preto", in_plan=True)
        for n, y in enumerate((-0.22, 0.22), 1):
            c.cyl(f"Pé {side} - sapata {n}", x, y, 0, 0.016, 0.008, "Plástico preto", detail=FINE)
    return c
