"""Coletor solar: a flat-plate solar water-heating collector on a tilted support (thermosiphon or pumped systems).

The collector runs along Y (its length, down the slope towards -Y) and X (its width); `Inclinacao` tilts it about its
lower edge, which stands `AlturaFrente` above the base. Cold water enters at the lower left, hot water leaves at the
upper right. Place several side by side.
"""

from kit import *


def build():
    c = Component("Coletor solar", "plumbing", "coletor-solar", "Plumbing")
    W = c.param("Largura", 1.0)
    L = c.param("Comprimento", 2.0)
    A = c.param("Inclinacao", 25, "Angle")
    Z = c.param("AlturaFrente", 0.25)
    desc = ("Coletor solar plano para aquecimento de água, caixa de alumínio com vidro e placa absorvedora de aletas de cobre, "
            "em suporte inclinado; inclinação ≈ latitude + 10° (NBR 15569)")
    c.type("Coletor solar 1,0 x 2,0 m", desc)
    c.type("Coletor solar 1,0 x 1,5 m", desc, Comprimento=1.5)
    c.mep = {"Fixture": {"drain_units": 0, "supply_weight": 0, "hot_water": True}}
    c.material("Placa absorvedora", (24, 26, 32), "Metal", "Satin")
    c.preview_size = (1.1, 1.9, 1.2)

    t = 0.08
    ca, sa = f"cos({A})", f"sin({A})"
    y0 = f"-{L}/2*{ca}"

    def pt(s, n):
        return (f"{y0} + ({s})*{ca} - ({n})*{sa}", f"{Z} + ({s})*{sa} + ({n})*{ca}")

    def slab(name, s0, s1, n0, n1, x, w, mat, **kw):
        c.profile(name, "Side", [pt(s0, n0), pt(s1, n0), pt(s1, n1), pt(s0, n1)], x, w, mat, **kw)

    xl = f"-{W}/2"
    c.box("Coletor simplificado", xl, y0, Z, W, f"{L}*{ca}", f"{L}*{sa} + {t}", "Alumínio anodizado", detail=COARSE, in_plan=True)
    slab("Caixa", 0, L, 0, f"{t} - 0.01", xl, W, "Alumínio anodizado", in_plan=True)
    slab("Placa absorvedora", 0.03, f"{L} - 0.03", f"{t} - 0.012", f"{t} - 0.006", f"{xl} + 0.03", f"{W} - 0.06", "Placa absorvedora")
    slab("Vidro", 0.02, f"{L} - 0.02", f"{t} - 0.006", t, f"{xl} + 0.02", f"{W} - 0.04", "Vidro temperado")
    for k in range(1, 10):  # the risers seen through the glass
        x = f"{xl} + {k}*{W}/10"
        slab(f"Tubo da placa {k}", 0.05, f"{L} - 0.05", f"{t} - 0.006", f"{t} - 0.004", f"{x} - 0.004", 0.008, "Cobre", detail=FINE)
    # Header pipes out of the sides.
    yi, zi = pt(0.06, t / 2)
    yo, zo = pt(f"{L} - 0.06", t / 2)
    c.cyl_x("Entrada de água fria", yi, zi, f"{xl} - 0.06", 0.011, 0.06, "Cobre")
    c.cyl_x("Saída de água quente", yo, zo, f"{W}/2", 0.011, 0.06, "Cobre")
    c.connector("Água fria", "ColdWater", f"{xl} - 0.06", yi, zi, "Left", 0.022)
    c.connector("Água quente", "HotWater", f"{W}/2 + 0.06", yo, zo, "Right", 0.022)
    # Support: two angle frames under the sides.
    for side, x in (("esquerdo", f"{xl} + 0.05"), ("direito", f"{W}/2 - 0.08")):
        slab(f"Trilho {side}", 0.05, f"{L} - 0.05", -0.03, 0, x, 0.03, "Aço galvanizado")
        for leg, s in (("frontal", 0.12), ("traseiro", f"{L} - 0.12")):
            y, zt = pt(s, -0.03)
            c.box(f"Pé {leg} {side}", x, f"{y} - 0.015", 0, 0.03, 0.03, zt, "Aço galvanizado")
    return c
