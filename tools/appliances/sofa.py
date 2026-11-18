"""Sofá estofado: rolled arms, one seat and one back cushion per seat, throw pillows, tapered legs."""

from kit import *


def turned(c, name, cx, cy, profile, material, detail=FULL):
    """A turned piece about the vertical axis at (cx, cy): profile = [(radius, z), …] from bottom to top."""
    pts = [(cx, profile[0][1])] + [(f"{p(cx)} + {p(r)}", z) for r, z in profile] + [(cx, profile[-1][1])]
    c.rev(name, "Front", pts, cy, cx, material, detail=detail)


def build():
    c = Component("Sofá estofado", "furniture", "sofa")
    W = c.param("Largura", 2.1)
    P = c.param("Profundidade", 0.9)
    H = c.param("Altura", 0.85)
    AS = c.param("AlturaAssento", 0.42)
    B = c.param("Braco", 0.18)
    c.type("Poltrona 85 cm", "Poltrona de 1 lugar", Largura=0.85)
    c.type("Sofá 2 lugares 160 cm", "Sofá de 2 lugares", Largura=1.6)
    c.type("Sofá 3 lugares 210 cm", "Sofá de 3 lugares", Largura=2.1)
    c.type("Sofá 4 lugares 260 cm", "Sofá de 4 lugares", Largura=2.6)
    c.material("Tecido cinza escuro", (92, 95, 100), "Generic", "Matte")
    c.material("Tecido mostarda", (201, 152, 58), "Generic", "Matte")
    c.material("Tecido azul petróleo", (48, 92, 110), "Generic", "Matte")
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")

    fabric, welt, dark = "Tecido", "Tecido cinza escuro", "Madeira escura"
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{P}/2", f"{P}/2"
    zl = 0.12  # legs
    zd = 0.27  # seat deck
    N = f"max(1, min(4, round(({W} - 2*{B})/0.58)))"  # seats
    multi = f"min(1, {N} - 1)"  # 0 for the armchair, 1 for a sofa

    # Coarse stand-ins: the old boxes.
    c.box("Base simplificada", xl, yf, 0, W, P, AS, fabric, detail=COARSE, in_plan=True)
    c.box("Encosto simplificado", xl, f"{yb} - 0.2", AS, W, 0.2, f"{H} - {AS}", fabric, detail=COARSE, in_plan=True)
    c.box("Braço esquerdo simplificado", xl, yf, AS, B, f"{P} - 0.2", 0.22, fabric, detail=COARSE, in_plan=True)
    c.box("Braço direito simplificado", f"{xr} - {B}", yf, AS, B, f"{P} - 0.2", 0.22, fabric, detail=COARSE, in_plan=True)

    # Legs: four at the corners and, on a sofa, two in the middle (on the armchair they fold into the left ones).
    legs = [("frontal esquerda", f"-({W}/2 - 0.075)", f"{yf} + 0.075", "0"), ("frontal direita", f"{W}/2 - 0.075", f"{yf} + 0.075", "0"),
            ("traseira esquerda", f"-({W}/2 - 0.075)", f"{yb} - 0.075", "0"), ("traseira direita", f"{W}/2 - 0.075", f"{yb} - 0.075", "0"),
            ("central frontal", f"-(1 - {multi})*({W}/2 - 0.075)", f"{yf} + 0.075", f"0.001*(1 - {multi})"),
            ("central traseira", f"-(1 - {multi})*({W}/2 - 0.075)", f"{yb} - 0.075", f"0.001*(1 - {multi})")]
    for where, cx, cy, sh in legs:
        turned(c, f"Perna {where}", cx, cy, [(f"0.015 - {sh}", 0.03), (f"0.026 - {sh}", f"{zl - 0.01} - {sh}"), (f"0.026 - {sh}", f"{zl} - {sh}")],
               dark)
        turned(c, f"Ponteira da perna {where}", cx, cy, [(f"0.0125 - {sh}", f"0.003 + {sh}"), (f"0.015 - {sh}", 0.03)], "Latão", detail=FINE)
        c.cyl(f"Feltro da perna {where}", cx, cy, sh, f"0.011 - {sh}", 0.003, "Feltro", detail=FINE)

    # Arms: rolled top, full depth.
    za = f"{AS} + 0.22"

    def arm(x0, x1, m=0.0):
        rb, rt = 0.012, f"0.46*{B}"
        return [(f"{x0} + {rb}", zl - m), (f"{x1} - {rb}", zl - m, rb + m), (f"{x1} + {m}", zl + rb), (f"{x1} + {m}", f"{za} - {rt}", f"{rt} + {m}"),
                (f"{x1} - {rt}", f"{za} + {m}"), (f"{x0} + {rt}", f"{za} + {m}", f"{rt} + {m}"), (f"{x0} - {m}", f"{za} - {rt}"),
                (f"{x0} - {m}", zl + rb, rb + m)]

    for name, x0, x1 in (("esquerdo", xl, f"{xl} + {B}"), ("direito", f"{xr} - {B}", xr)):
        c.profile(f"Braço {name}", "Front", arm(x0, x1), yf, P, fabric, in_plan=True)
        c.profile(f"Braço {name} - vivo frontal", "Front", arm(f"{x0} + 0.003", f"{x1} - 0.003", 0.006), f"{yf} + 0.022", 0.006, welt,
                  detail=FINE)
        c.profile(f"Braço {name} - vivo traseiro", "Front", arm(f"{x0} + 0.003", f"{x1} - 0.003", 0.006), f"{yb} - 0.028", 0.006, welt,
                  detail=FINE)

    # Base rail and back frame between the arms.
    xa, xb = f"{xl} + {B}", f"{xr} - {B}"
    wi = f"({W} - 2*{B})"
    c.box("Base", f"{xa} - 0.01", f"{yf} + 0.035", zl, f"{wi} + 0.02", f"{P} - 0.05", zd - zl, fabric)
    c.box("Vivo da base", f"{xa} - 0.01", f"{yf} + 0.032", zl + 0.012, f"{wi} + 0.02", 0.004, 0.006, welt, detail=FINE)
    yk = f"{yb} - 0.14"  # front of the back frame
    zk = f"{H} - 0.05"
    c.profile("Estrutura do encosto", "Side", [(yk, zd), (f"{yb} - 0.012", zd), (f"{yb} - 0.012", f"{zk} - 0.05", 0.05), (f"{yb} - 0.062", zk),
                                                (f"{yk} + 0.05", zk, 0.05), (yk, f"{zk} - 0.05")], f"{xa} - 0.01", f"{wi} + 0.02", fabric,
              in_plan=True)

    # One seat cushion and one back cushion per seat. Cushions beyond the number of seats fold into the last one,
    # a little smaller. `m` is the margin added around an outline (an expression).
    def seat(m):
        y0, y1, z0, z1, r = f"{yf} + 0.004", yk, zd, f"{AS} - 0.012", 0.04
        half = f"(({y1}) - ({y0}) - {2 * r})/2"
        crown = f"({half}*{half} + 0.000144)/0.024"
        rr = f"{r} + {m}"
        return [(f"{y0} + {r}", f"{z0} - ({m})"), (f"{y1} - {r}", f"{z0} - ({m})", rr), (f"{y1} + {m}", z0 + r), (f"{y1} + {m}", f"{z1} - {r}", rr),
                (f"{y1} - {r}", f"{z1} + {m}", f"{crown} + {m}"), (f"{y0} + {r}", f"{z1} + {m}", rr), (f"{y0} - ({m})", f"{z1} - {r}"),
                (f"{y0} - ({m})", z0 + r, rr)]

    def back(m):
        return [(f"{yb} - 0.315 - ({m})", f"{AS} - 0.012 - ({m})"), (f"{yb} - 0.13", f"{AS} - 0.012 - ({m})"),
                (f"{yb} - 0.05", f"{H} - 0.035", f"0.1 + {m}"), (f"{yb} - 0.2 - ({m})", f"{H} - 0.03 + {m}", 1.1)]

    cw = f"({wi}/{N})"
    for i in range(4):
        j = f"min({i}, {N} - 1)"
        sh = "0" if i == 0 else f"0.0015*(1 - min(1, max(0, {N} - {i})))"
        x0 = f"{xa} + {j}*{cw} + 0.002 + {sh}"
        w = f"{cw} - 0.004 - 2*{sh}"
        tag = f"{i + 1}"
        c.profile(f"Almofada do assento {tag}", "Side", seat(f"-{sh}"), x0, w, fabric, in_plan=True)
        c.profile(f"Almofada do encosto {tag}", "Side", back(f"-{sh}"), x0, w, fabric, in_plan=True)
        for side, xs in (("esquerdo", f"{x0} + 0.012"), ("direito", f"{x0} + {w} - 0.017")):
            c.profile(f"Almofada do assento {tag} - vivo {side}", "Side", seat(f"0.004 - {sh}"), xs, 0.005, welt, detail=FINE)
            c.profile(f"Almofada do encosto {tag} - vivo {side}", "Side", back(f"0.004 - {sh}"), xs, 0.005, welt, detail=FINE)

    # Throw pillows leaning on the back cushions, one at each end (one only on the armchair).
    tw = f"min(0.4, {wi} - 0.1)"
    for n, x0, sh, material in ((1, f"{xa} + 0.035", "0", "Tecido mostarda"),
                                (2, f"{multi}*({xb} - 0.035 - {tw}) + (1 - {multi})*({xa} + 0.0365)", f"0.0015*(1 - {multi})",
                                 "Tecido azul petróleo")):
        lo = (f"{yb} - 0.42", f"{AS} - 0.008 + {sh}")
        hi = (f"{yb} - 0.25", f"{AS} + 0.36 - {sh}")

        def lens(m, lo=lo, hi=hi, sh=sh):
            return [(lo[0], f"{lo[1]} - {m}", f"0.36 - {sh} - {m / 2}"), (hi[0], f"{hi[1]} + {m}", f"0.36 - {sh} - {m / 2}")]

        c.profile(f"Almofada decorativa {n}", "Side", lens(0), x0, f"{tw} - 2*{sh}", material, in_plan=True)
        c.profile(f"Almofada decorativa {n} - vivo esquerdo", "Side", lens(0.004), f"{x0} + 0.004", 0.004, welt, detail=FINE)
        c.profile(f"Almofada decorativa {n} - vivo direito", "Side", lens(0.004), f"{x0} + {tw} - 2*{sh} - 0.008", 0.004, welt, detail=FINE)
    return c

