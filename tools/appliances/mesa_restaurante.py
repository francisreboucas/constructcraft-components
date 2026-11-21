"""Mesa de restaurante: a bistro table on a cast iron pedestal with two or four steel and wood chairs.

Centred on the origin; the chairs face the table from ±Y (and ±X when there are four).
"""

from kit import *
from _mobilia import EPS, Grp


def chair(g, tag, cx, cy, facing):
    """A bistro chair centred at (cx, cy) whose front faces `facing` ('+y', '-y', '+x', '-x')."""
    w, d, zs = 0.42, 0.42, 0.45
    hx, hy = w / 2, d / 2
    # Back side offset from the centre, along the facing axis.
    if facing in ("+y", "-y"):
        s = 1 if facing == "-y" else -1  # the back is on the side opposite the facing
        g.box(f"{tag} - assento", f"{cx} - {hx}", f"{cy} - {hy}", zs - 0.03, w, d, 0.03, "Madeira")
        g.box(f"{tag} - encosto", f"{cx} - {hx} + 0.02", f"{cy} + {s * (hy - 0.02)} - 0.01", zs + 0.18, w - 0.04, 0.02, 0.2, "Madeira")
        for k, (px, py) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            back = (py == s)
            g.box(f"{tag} - pé {k + 1}", f"{cx} + {px * (hx - 0.02)} - 0.0125", f"{cy} + {py * (hy - 0.02)} - 0.0125", 0, 0.025, 0.025,
                  zs + (0.4 if back else -0.03), "Aço pintado preto")
    else:
        s = 1 if facing == "-x" else -1
        g.box(f"{tag} - assento", f"{cx} - {hy}", f"{cy} - {hx}", zs - 0.03, d, w, 0.03, "Madeira")
        g.box(f"{tag} - encosto", f"{cx} + {s * (hy - 0.02)} - 0.01", f"{cy} - {hx} + 0.02", zs + 0.18, 0.02, w - 0.04, 0.2, "Madeira")
        for k, (px, py) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            back = (px == s)
            g.box(f"{tag} - pé {k + 1}", f"{cx} + {px * (hy - 0.02)} - 0.0125", f"{cy} + {py * (hx - 0.02)} - 0.0125", 0, 0.025, 0.025,
                  zs + (0.4 if back else -0.03), "Aço pintado preto")


def build():
    c = Component("Mesa de restaurante", "furniture", "mesa-restaurante")
    W = c.param("Largura", 0.7)
    N = c.param("Lugares", 4, "Number")
    desc = "Mesa de restaurante com tampo de madeira sobre pé central de ferro fundido e cadeiras de aço com assento e encosto de madeira"
    c.type("Mesa de restaurante 4 lugares", desc)
    c.type("Mesa de restaurante 2 lugares", desc, Largura=0.6, Lugares=2)
    c.preview_size = (1.6, 1.6, 0.9)

    c.box("Conjunto simplificado", f"-{W}/2", f"-{W}/2", 0, W, W, 0.75, "Madeira", detail=COARSE, in_plan=True)
    c.box("Tampo", f"-{W}/2", f"-{W}/2", 0.72, W, W, 0.03, "Madeira", in_plan=True)
    c.box("Borda do tampo", f"-{W}/2 + 0.005", f"-{W}/2 + 0.005", 0.715, f"{W} - 0.01", f"{W} - 0.01", 0.005, "Madeira escura", detail=FINE)
    c.rev("Pé central", "Front", [(0, 0), (0.25, 0), (0.25, 0.015), (0.06, 0.04), (0.035, 0.08), (0.035, 0.7), (0.1, 0.705), (0.1, 0.72), (0, 0.72)],
          0, 0, "Ferro fundido")
    gap = 0.12  # chairs tucked a little under the table
    for name, cx, cy, f, k in (("Cadeira 1", 0, f"-{W}/2 - 0.21 + {gap}", "+y", None), ("Cadeira 2", 0, f"{W}/2 + 0.21 - {gap}", "-y", None),
                               ("Cadeira 3", f"-{W}/2 - 0.21 + {gap}", 0, "+x", f"min(1, max({EPS}, {N} - 2))"),
                               ("Cadeira 4", f"{W}/2 + 0.21 - {gap}", 0, "-x", f"min(1, max({EPS}, {N} - 2))")):
        g = Grp(c, k, (0, 0, 0.73)) if k else Grp(c)
        chair(g, name, cx, cy, f)
    return c
