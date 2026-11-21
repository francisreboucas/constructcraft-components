"""Módulo fotovoltaico: a 550 W monocrystalline module in portrait on a tilted aluminium mounting (ground or flat roof).

The module runs along Y (its length, 2,28 m, down the slope towards -Y) and X (its width, 1,13 m); `Inclinacao`
tilts it about its lower edge, which stands `AlturaFrente` above the base. Place several side by side for an array.
"""

from kit import *


def build():
    c = Component("Módulo fotovoltaico", "electrical", "modulo-fotovoltaico", "Generic")
    W = c.param("Largura", 1.134)
    L = c.param("Comprimento", 2.278)
    A = c.param("Inclinacao", 20, "Angle")
    Z = c.param("AlturaFrente", 0.3)
    desc = ("Módulo fotovoltaico monocristalino de 550 W (2,28 x 1,13 m, 144 meias-células) com moldura de alumínio, em "
            "estrutura de alumínio para solo ou laje inclinada; repita lado a lado para formar o arranjo")
    c.type("Módulo fotovoltaico 550 W - 20°", desc)
    c.type("Módulo fotovoltaico 550 W - 10°", desc, Inclinacao=10)
    c.type("Módulo fotovoltaico 550 W - 30°", desc, Inclinacao=30)
    c.material("Célula fotovoltaica", (22, 32, 62), "Generic", "Glossy")
    c.material("Grade das células", (190, 196, 206), "Metal", "Satin")
    c.preview_size = (1.2, 2.2, 1.2)

    t = 0.035  # module thickness
    y0 = f"-{L}/2*cos({A})"  # the lower edge
    ca, sa = f"cos({A})", f"sin({A})"

    def pt(s, n):  # (y, z) of the point s along the slope from the lower edge and n above the module's underside
        return (f"{y0} + ({s})*{ca} - ({n})*{sa}", f"{Z} + ({s})*{sa} + ({n})*{ca}")

    def slab(name, s0, s1, n0, n1, x, w, mat, **kw):
        c.profile(name, "Side", [pt(s0, n0), pt(s1, n0), pt(s1, n1), pt(s0, n1)], x, w, mat, **kw)

    xl = f"-{W}/2"
    c.box("Módulo simplificado", xl, y0, Z, W, f"{L}*{ca}", f"{L}*{sa} + {t}", "Célula fotovoltaica", detail=COARSE, in_plan=True)
    # Frame: four aluminium sides, the glass with the cells between them.
    f = 0.03
    slab("Moldura inferior", 0, f, 0, t, xl, W, "Alumínio anodizado")
    slab("Moldura superior", f"{L} - {f}", L, 0, t, xl, W, "Alumínio anodizado")
    slab("Moldura esquerda", f, f"{L} - {f}", 0, t, xl, f, "Alumínio anodizado")
    slab("Moldura direita", f, f"{L} - {f}", 0, t, f"{W}/2 - {f}", f, "Alumínio anodizado")
    slab("Vidro e células", f, f"{L} - {f}", 0.012, t - 0.003, f"{xl} + {f}", f"{W} - {2 * f}", "Célula fotovoltaica", in_plan=True)
    # The gaps between the rows of half-cells (24 rows) and the split across the middle.
    for k in range(1, 24):
        s = f"{f} + {k}*({L} - {2 * f})/24"
        slab(f"Linha das células {k}", f"{s} - 0.0015", f"{s} + 0.0015", t - 0.003, t - 0.0025, f"{xl} + {f}", f"{W} - {2 * f}",
             "Grade das células", detail=FINE)
    c.box("Caixa de junção", -0.08, f"{y0} + ({L} - 0.25)*{ca}", f"{Z} + ({L} - 0.25)*{sa} - 0.025", 0.16, 0.1, 0.025, "Plástico preto",
          detail=FINE)
    # Mounting: two rails along the slope, a short front leg and a tall back leg under each, a ground beam.
    for side, x in (("esquerdo", f"-{W}/4"), ("direito", f"{W}/4")):
        slab(f"Trilho {side}", 0.1, f"{L} - 0.1", -0.04, 0, f"{x} - 0.02", 0.04, "Alumínio anodizado")
        for leg, s in (("frontal", 0.25), ("traseiro", f"{L} - 0.25")):
            y, zt = pt(s, -0.04)
            c.box(f"Pé {leg} {side}", f"{x} - 0.02", f"{y} - 0.02", 0, 0.04, 0.04, zt, "Alumínio anodizado")
            c.box(f"Sapata {leg} {side}", f"{x} - 0.06", f"{y} - 0.06", 0, 0.12, 0.12, 0.008, "Aço galvanizado", detail=FINE)
        yb, _ = pt(0.25, 0)
        yt, ztt = pt(f"{L} - 0.25", -0.04)
        c.profile(f"Diagonal {side}", "Side", [(f"{yb}", 0.05), (f"{yb} + 0.04", 0.05), (yt, f"{ztt} - 0.05"), (f"{yt} - 0.04", f"{ztt} - 0.05")],
                  f"{x} - 0.012", 0.024, "Alumínio anodizado", detail=FINE)
    return c
