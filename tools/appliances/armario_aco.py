"""Armário de aço: a two-door steel office cabinet with adjustable shelves, louvred doors and a handle with a lock.

The number of shelves follows the height: one compartment per ~40 cm (the shelves a type does not have shrink away).
"""

from kit import *
from _escritorio import declare
from _mobilia import EPS, Grp


def build():
    c = Component("Armário de aço", "furniture", "armario-aco")
    W = c.param("Largura", 0.9)
    D = c.param("Profundidade", 0.4)
    H = c.param("Altura", 1.98)
    A = c.angle("AnguloPorta", 0, open_at=100)
    desc = "Armário de aço de duas portas com prateleiras reguláveis, venezianas de ventilação nas portas e puxador com fechadura"
    c.type("Armário de aço alto 90x40x198", desc)
    c.type("Armário de aço baixo 90x40x105", desc, Altura=1.05)
    c.type("Armário de aço alto 120x45x198", desc, Largura=1.2, Profundidade=0.45)
    declare(c, "Aço pintado cinza claro")

    steel = "Aço pintado cinza claro"
    t = 0.008
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{D}/2", f"{D}/2"
    zp = 0.07

    c.box("Armário simplificado", xl, yf, 0, W, D, H, steel, detail=COARSE, in_plan=True)

    # Carcass.
    c.box("Rodapé", f"{xl} + 0.015", f"{yf} + 0.03", 0, f"{W} - 0.03", f"{D} - 0.04", zp, "Aço pintado cinza")
    c.box("Lateral esquerda", xl, yf, 0.004, t, D, f"{H} - 0.004", steel)
    c.box("Lateral direita", f"{xr} - {t}", yf, 0.004, t, D, f"{H} - 0.004", steel)
    c.box("Tampo", xl, yf, f"{H} - {t}", W, D, t, steel, in_plan=True)
    c.box("Base", f"{xl} + {t}", yf, zp, f"{W} - {2 * t}", D, t, steel)
    c.box("Fundo", f"{xl} + {t}", f"{yb} - {t}", f"{zp} + {t}", f"{W} - {2 * t}", t, f"{H} - {zp} - {2 * t}", steel)
    c.box("Batente central", "-0.015", yf, f"{zp} + {t}", 0.03, 0.012, f"{H} - {zp} - {2 * t}", steel, detail=FINE)

    # Shelves: n compartments of equal height; shelf k exists when k < n.
    zi0, zi1 = f"{zp} + {t}", f"{H} - {t}"
    n = f"max(1, round(({zi1} - {zi0})/0.4))"
    for k in range(1, 6):
        z = f"{zi0} + {k}*({zi1} - ({zi0}))/{n}"
        g = Grp(c, f"min(1, max({EPS}, {n} - {k}))", (0, f"{yb} - {t / 2}", f"{H}/2"))
        g.box(f"Prateleira {k}", f"{xl} + {t} + 0.002", f"{yf} + 0.02", f"{z} - 0.025", f"{W} - {2 * t} - 0.004", f"{D} - 0.03", 0.025,
              steel)
        g.box(f"Prateleira {k} - dobra frontal", f"{xl} + {t} + 0.002", f"{yf} + 0.02", f"{z} - 0.035", f"{W} - {2 * t} - 0.004", 0.012,
              0.01, steel, detail=FINE)

    # Doors: each swings about a vertical hinge at the carcass side, on the front face.
    dt = 0.02
    dz, dh = f"{zp} + 0.004", f"{H} - {zp} - 0.008"
    dw = f"{W}/2 - 0.003"
    for side, hx in (("left", xl), ("right", xr)):
        name = "esquerda" if side == "left" else "direita"
        hinge = (hx, yf)
        c.door_box(f"Porta {name}", hinge, A, 0.002, dw, 0, dt, dz, dh, steel, side=side)
        # Ventilation louvres at the top and bottom of each door.
        for where, z0 in (("superior", f"{H} - 0.2"), ("inferior", f"{zp} + 0.08")):
            for m in range(5):
                c.door_box(f"Porta {name} - veneziana {where} {m + 1}", hinge, A, f"0.25*{W}/2 - 0.06", f"0.25*{W}/2 + 0.06", dt,
                           dt + 0.003, f"{z0} + {m * 0.018}", 0.006, "Aço pintado cinza", side=side, detail=FINE)
        for m, z in enumerate((f"{zp} + 0.12", f"{H}/2", f"{H} - 0.12"), 1):
            c.door_box(f"Porta {name} - dobradiça {m}", hinge, A, -0.006, 0.004, -0.004, 0.012, f"{z} - 0.04", 0.08, "Aço galvanizado",
                       side=side, detail=FINE)

    # Handle with a lock on the right door, near the meeting edge.
    hz = f"{zp} + 0.52*({H} - {zp})"
    hinge = (xr, yf)
    c.door_box("Puxador - espelho", hinge, A, f"{dw} - 0.06", f"{dw} - 0.03", dt, dt + 0.004, f"{hz} - 0.09", 0.18, "Cromado", side="right")
    c.door_box("Puxador - alavanca", hinge, A, f"{dw} - 0.055", f"{dw} - 0.035", dt + 0.004, dt + 0.03, f"{hz} - 0.06", 0.1, "Cromado",
               side="right")
    c.door_box("Fechadura", hinge, A, f"{dw} - 0.052", f"{dw} - 0.038", dt + 0.004, dt + 0.008, f"{hz} + 0.05", 0.014, "Plástico preto",
               side="right", detail=FINE)
    return c
