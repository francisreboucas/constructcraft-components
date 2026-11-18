"""Cama com cabeceira: slatted wooden frame, mattress, bedding, pillows and a channel-tufted headboard."""

from kit import *


def turned(c, name, cx, cy, profile, material, detail=FULL):
    """A turned piece about the vertical axis at (cx, cy): profile = [(radius, z), …] from bottom to top."""
    pts = [(cx, profile[0][1])] + [(f"{p(cx)} + {p(r)}", z) for r, z in profile] + [(cx, profile[-1][1])]
    c.rev(name, "Front", pts, cy, cx, material, detail=detail)


def cover(xo, xi, zb, zi, zo, r):
    """Front outline of a bed cover: over the top (zi..zo) and down both sides to zb, between xi and xo."""
    return [(f"-({xo})", zb), (f"-({xi})", zb), (f"-({xi})", zi), (xi, zi), (xi, zb), (xo, zb), (xo, f"{zo} - {r}", r),
            (f"{xo} - {r}", zo), (f"-({xo}) + {r}", zo, r), (f"-({xo})", f"{zo} - {r}")]


def build():
    c = Component("Cama com cabeceira", "furniture", "cama")
    L = c.param("Largura", 1.38)
    C = c.param("Comprimento", 1.88)
    AC = c.param("AlturaColchao", 0.25)
    c.type("Cama solteiro 88x188", "Colchão de solteiro", Largura=0.88, Comprimento=1.88)
    c.type("Cama viúvo 128x188", "Colchão de viúvo", Largura=1.28, Comprimento=1.88)
    c.type("Cama casal 138x188", "Colchão de casal padrão", Largura=1.38, Comprimento=1.88)
    c.type("Cama queen 158x198", "Colchão queen size", Largura=1.58, Comprimento=1.98)
    c.type("Cama king 193x203", "Colchão king size", Largura=1.93, Comprimento=2.03)
    c.preview_size = (1.44, 1.93, 1.1)
    c.material("Colchão", (232, 228, 218), "Generic", "Matte")
    c.material("Roupa de cama branca", (243, 241, 235), "Generic", "Matte")
    c.material("Tecido cinza", (150, 152, 156), "Generic", "Matte")
    c.material("Tecido cinza escuro", (92, 95, 100), "Generic", "Matte")
    c.material("Tecido mostarda", (201, 152, 58), "Generic", "Matte")
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")

    wood, dark = "Madeira", "Madeira escura"
    xl, xr = f"-{L}/2", f"{L}/2"
    yf, yb = f"-{C}/2", f"{C}/2"
    zm = 0.3  # underside of the mattress
    zs = f"{zm} + {AC} + 0.003"  # top of the made bed's sheet

    # Coarse stand-ins: the old boxes.
    c.box("Estrado simplificado", xl, yf, 0, L, C, 0.3, wood, detail=COARSE, in_plan=True)
    c.box("Colchão simplificado", f"{xl} + 0.01", f"{yf} + 0.01", 0.3, f"{L} - 0.02", f"{C} - 0.02", AC, "Colchão", detail=COARSE)
    c.box("Cabeceira simplificada", f"{xl} - 0.03", yb, 0, f"{L} + 0.06", 0.05, 1.1, "Tecido", detail=COARSE, in_plan=True)

    # Frame: rails, ledgers, a center beam and slats.
    rt, rz, rh = 0.03, 0.12, 0.18
    c.box("Longarina esquerda", xl, yf, rz, rt, C, rh, wood)
    c.box("Longarina direita", f"{xr} - {rt}", yf, rz, rt, C, rh, wood)
    c.box("Travessa dos pés", f"{xl} + {rt}", yf, rz, f"{L} - {2 * rt}", rt, rh, wood)
    c.box("Travessa da cabeceira", f"{xl} + {rt}", f"{yb} - {rt}", rz, f"{L} - {2 * rt}", rt, rh, wood)
    c.box("Sarrafo de apoio esquerdo", f"{xl} + {rt}", f"{yf} + {rt}", 0.25, 0.025, f"{C} - {2 * rt}", 0.03, wood, detail=FINE)
    c.box("Sarrafo de apoio direito", f"{xr} - {rt} - 0.025", f"{yf} + {rt}", 0.25, 0.025, f"{C} - {2 * rt}", 0.03, wood, detail=FINE)
    c.box("Viga central", -0.03, f"{yf} + {rt}", 0.2, 0.06, f"{C} - {2 * rt}", 0.08, wood)
    slats = 14
    for n in range(slats):
        c.box(f"Ripa do estrado {n + 1}", f"{xl} + {rt} + 0.002", f"{yf} + {rt} + {(n + 0.5) / slats:.5f}*({C} - {2 * rt}) - 0.035", 0.28,
              f"{L} - {2 * rt} - 0.004", 0.07, 0.02, "Madeira clara", detail=FINE)
    for n, fy in enumerate((-0.25, 0.25), 1):
        c.cyl(f"Pé central {n}", 0, f"{fy}*{C}", 0.004, 0.022, 0.196, dark)
        c.cyl(f"Sapata do pé central {n}", 0, f"{fy}*{C}", 0, 0.018, 0.004, "Feltro", detail=FINE)
    for where, sx, sy in (("frontal esquerdo", -1, -1), ("frontal direito", 1, -1), ("traseiro esquerdo", -1, 1), ("traseiro direito", 1, 1)):
        cx, cy = f"{sx}*({L}/2 - 0.06)", f"{sy}*({C}/2 - 0.06)"
        c.box(f"Bloco do pé {where}", f"{cx} - 0.03", f"{cy} - 0.03", rz, 0.06, 0.06, 0.1, wood, detail=FINE)
        turned(c, f"Pé {where}", cx, cy, [(0.017, 0.026), (0.03, rz - 0.012), (0.03, rz)], dark)
        turned(c, f"Ponteira do pé {where}", cx, cy, [(0.0145, 0.003), (0.017, 0.026)], "Latão", detail=FINE)
        c.cyl(f"Feltro do pé {where}", cx, cy, 0, 0.013, 0.003, "Feltro", detail=FINE)

    # Mattress with piping, handles and a label; the fitted sheet covers its upper part.
    mx, my = f"{L}/2 - 0.01", f"{C}/2 - 0.01"
    c.profile("Colchão", "Plan", rrect(f"-({mx})", f"-({my})", mx, my, 0.07), zm, AC, "Colchão")
    for name, z in (("inferior", f"{zm} + 0.012"), ("intermediário", f"{zm} + 0.28*{AC}")):
        c.profile(f"Vivo do colchão {name}", "Plan", rrect(f"-({mx}) - 0.003", f"-({my}) - 0.003", f"{mx} + 0.003", f"{my} + 0.003", 0.073), z,
                  0.007, "Tecido cinza", detail=FINE)
    c.profile("Lençol de elástico", "Plan", rrect(f"-({mx}) - 0.002", f"-({my}) - 0.002", f"{mx} + 0.002", f"{my} + 0.002", 0.072),
              f"{zm} + 0.42*{AC}", f"0.58*{AC} + 0.003", "Roupa de cama branca", in_plan=True)
    n = 0
    for sx in (-1, 1):
        for fy in (-0.22, 0.22):
            n += 1
            c.box(f"Alça do colchão {n}", f"{sx}*({mx} + 0.002) - 0.002", f"{fy}*{C} - 0.07", f"{zm} + 0.14*{AC}", 0.004, 0.14, 0.022,
                  "Tecido cinza escuro", detail=FINE)
    c.box("Etiqueta do colchão", f"{mx} - 0.25", f"-({my}) - 0.001", f"{zm} + 0.12*{AC}", 0.09, 0.002, 0.035, "Roupa de cama branca",
          detail=FINE)

    # Duvet over the foot two thirds, its sheet fold, and a throw across the foot.
    xo, xi = f"{L}/2 + 0.014", f"{L}/2 - 0.0075"
    yd = f"{yb} - 0.66"  # where the duvet ends, towards the pillows
    c.profile("Edredom", "Front", cover(xo, xi, 0.2, zs, f"{zs} + 0.04", 0.035), yf, f"{C} - 0.66", "Tecido cinza", in_plan=True)
    c.box("Edredom - queda dos pés", f"-({xi})", yf, 0.2, f"2*({xi})", 0.0075, f"{zs} - 0.2", "Tecido cinza")
    c.profile("Dobra do lençol", "Front", cover(f"{xo} + 0.003", xi, f"{zm} + 0.3*{AC}", zs, f"{zs} + 0.046", 0.035), f"{yd} - 0.2", 0.22,
              "Roupa de cama branca", in_plan=True)
    c.profile("Manta dos pés", "Front", cover(f"{xo} + 0.005", xi, 0.26, zs, f"{zs} + 0.05", 0.035), f"{yf} + 0.14", 0.42,
              "Tecido mostarda", in_plan=True)

    # Pillows: one for a single bed, two from 1.20 m on (the second one folds into the first).
    k = f"min(1, floor({L}/1.2))"
    pw = f"min(0.7, ({L} - 0.1)/(1 + {k}))"
    pd = 0.46
    yc = f"{yb} - 0.07 - {pd / 2}"
    for n, sign in ((1, "-"), (2, "")):
        sh = "0" if n == 1 else f"0.0015*(1 - {k})"  # the folded pillow is a little smaller, inside the other
        cx = f"{sign}{k}*{L}/4"
        w = f"({pw} - 2*{sh})"
        d = f"({pd} - 2*{sh})"
        z0 = f"{zs} + {sh}"
        c.profile(f"Travesseiro {n}", "Plan", rrect(f"{cx} - {w}/2", f"{yc} - {d}/2", f"{cx} + {w}/2", f"{yc} + {d}/2", 0.07), z0, 0.055,
                  "Roupa de cama branca", in_plan=True)
        c.profile(f"Travesseiro {n} - vivo", "Plan", rrect(f"{cx} - {w}/2 - 0.004", f"{yc} - {d}/2 - 0.004", f"{cx} + {w}/2 + 0.004",
                                                            f"{yc} + {d}/2 + 0.004", 0.074), f"{z0} + 0.026", 0.005, "Roupa de cama branca",
                  detail=FINE)
        # Two crossed crowns make the pillow's belly.
        sag = f"(0.085 - {sh})"
        for plane, half, across, mid in (("Side", f"({d}/2 - 0.012)", f"{w} - 0.1", yc), ("Front", f"({w}/2 - 0.012)", f"{d} - 0.1", cx)):
            radius = f"({half}*{half} + {sag}*{sag})/(2*{sag})"
            start = f"{cx} - ({across})/2" if plane == "Side" else f"{yc} - ({across})/2"
            c.profile(f"Travesseiro {n} - volume {'longitudinal' if plane == 'Side' else 'transversal'}", plane,
                      [(f"{mid} - {half}", f"{z0} + 0.05"), (f"{mid} + {half}", f"{z0} + 0.05", radius)], start, across,
                      "Roupa de cama branca")

    # Headboard: a wooden frame on two legs with six upholstered channels.
    hx = f"{L}/2 + 0.03"
    c.box("Cabeceira - painel de fundo", f"-({hx}) + 0.02", f"{yb} + 0.03", 0.1, f"2*({hx}) - 0.04", 0.02, 0.98, dark)
    c.box("Cabeceira - montante esquerdo", f"-({hx})", yb, 0, 0.03, 0.05, 1.1, wood, in_plan=True)
    c.box("Cabeceira - montante direito", f"{hx} - 0.03", yb, 0, 0.03, 0.05, 1.1, wood, in_plan=True)
    c.box("Cabeceira - travessa superior", f"-({hx}) + 0.03", yb, 1.07, f"2*({hx}) - 0.06", 0.05, 0.03, wood, in_plan=True)
    c.box("Cabeceira - travessa inferior", f"-({hx}) + 0.03", f"{yb} + 0.004", 0.2, f"2*({hx}) - 0.06", 0.046, 0.06, wood)
    channels = 6
    cw = f"(2*({hx}) - 0.06)/{channels}"
    for n in range(channels):
        x0 = f"-({hx}) + 0.03 + {n}*{cw} + 0.001"
        x1 = f"-({hx}) + 0.03 + {n + 1}*{cw} - 0.001"
        c.profile(f"Cabeceira - gomo {n + 1}", "Plan", [(f"{x0} + 0.014", f"{yb} + 0.002"), (f"{x1} - 0.014", f"{yb} + 0.002", 0.014),
                                                       (x1, f"{yb} + 0.016"), (x1, f"{yb} + 0.031"), (x0, f"{yb} + 0.031"),
                                                       (x0, f"{yb} + 0.016", 0.014)], 0.26, 0.81, "Tecido")
    return c
