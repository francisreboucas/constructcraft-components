"""Coifa de parede piramidal (60 cm e 90 cm) com chaminé telescópica."""

import kit
from kit import *


def blend(c, name, bottom, top, z, height, material, detail=FULL, in_plan=False):
    """A solid joining the plan outline `bottom` at z to `top` at z + height (the kit has no helper for it)."""
    shape = {"Blend": {"plane": "Plan", "bottom": kit._points(bottom), "top": kit._points(top), "offset": e(z), "depth": e(height)}}
    c._add(name, shape, material, detail, in_plan, False)


def build() -> Component:
    c = Component("Coifa de parede", "furniture", "coifa-parede")

    W = c.param("Largura", 0.6)
    D = c.param("Profundidade", 0.48)
    H = c.param("Altura", 0.78)
    AA = c.param("AlturaAba", 0.05)
    APi = c.param("AlturaPiramide", 0.12)
    LD = c.param("LarguraChamine", 0.25)
    PD = c.param("ProfundidadeChamine", 0.21)
    AC = c.param("AlturaChamineInferior", 0.34)

    xl, xr = f"(-{W}/2)", f"({W}/2)"
    yf = f"(-{D})"
    zc = f"({AA} + {APi})"  # where the chimney starts
    zm = f"({zc} + {AC})"  # where the upper section shows
    inox, galv = "Inox escovado", "Aço galvanizado"

    # --- coarse ---------------------------------------------------------------
    c.box("Corpo simplificado", xl, yf, 0, W, D, zc, inox, detail=COARSE, in_plan=True)
    c.box("Chaminé simplificada", f"-{LD}/2", f"-{PD}", zc, LD, PD, f"{H} - {zc}", inox, detail=COARSE, in_plan=True)

    # --- canopy ---------------------------------------------------------------
    c.box("Aba frontal", xl, yf, 0, W, 0.02, AA, inox)
    c.box("Aba traseira", xl, -0.02, 0, W, 0.02, AA, inox)
    c.box("Aba esquerda", xl, f"{yf} + 0.02", 0, 0.02, f"{D} - 0.04", AA, inox)
    c.box("Aba direita", f"{xr} - 0.02", f"{yf} + 0.02", 0, 0.02, f"{D} - 0.04", AA, inox)
    c.box("Fundo interno", f"{xl} + 0.02", f"{yf} + 0.02", 0.012, f"{W} - 0.04", f"{D} - 0.04", 0.004, inox)
    blend(c, "Pirâmide", rect(xl, yf, xr, 0), rect(f"-{LD}/2", f"-{PD}", f"{LD}/2", 0), AA, APi, inox, in_plan=True)
    c.box("Aba - friso superior", f"{xl} - 0.0008", f"{yf} - 0.0008", f"{AA} - 0.004", f"{W} + 0.0016", f"{D} + 0.0008", 0.004, "Cromado", detail=FINE)

    # Controls on the front of the rim.
    zb = f"({AA}/2)"
    c.box("Painel de comando", -0.1, f"{yf} - 0.0015", f"{zb} - 0.014", 0.2, 0.0015, 0.028, "Plástico preto brilhante")
    for i, n in enumerate(("liga/desliga", "velocidade 1", "velocidade 2", "velocidade 3", "luz")):
        x = f"{-0.07 + 0.035 * i}"
        c.cyl_y(f"Tecla {n} - aro", x, zb, f"{yf} - 0.0025", 0.0095, 0.001, "Cromado", detail=FINE)
        c.cyl_y(f"Tecla {n}", x, zb, f"{yf} - 0.005", 0.0075, 0.0035, "Alumínio anodizado", detail=FINE)
    c.cyl_y("Luz indicadora", 0.088, zb, f"{yf} - 0.0022", 0.003, 0.0007, "Plástico verde", detail=FINE)

    # --- underside ------------------------------------------------------------
    # Light strip at the front, filters behind it.
    ly0 = f"({yf} + 0.02)"
    c.box("Faixa de iluminação", f"{xl} + 0.02", ly0, 0.006, f"{W} - 0.04", 0.075, 0.006, inox)
    for sx, n in ((f"-{W}*0.3", "esquerda"), (f"{W}*0.3", "direita")):
        c.cyl(f"Lâmpada LED {n} - aro", sx, f"{ly0} + 0.038", 0.004, 0.03, 0.002, "Cromado")
        c.cyl(f"Lâmpada LED {n} - lente", sx, f"{ly0} + 0.038", 0.003, 0.024, 0.002, "Plástico translúcido", detail=FINE)
    fy0 = f"({ly0} + 0.08)"
    fd = f"({D} - 0.13)"
    fw = f"(({W} - 0.056)/2)"
    n_slats = 13
    for k, n in enumerate(("esquerdo", "direito")):
        fx0 = f"({xl} + 0.026 + {k}*({fw} + 0.004))"
        c.box(f"Filtro {n} - moldura frontal", fx0, fy0, 0.004, fw, 0.012, 0.008, "Alumínio anodizado")
        c.box(f"Filtro {n} - moldura traseira", fx0, f"{fy0} + {fd} - 0.012", 0.004, fw, 0.012, 0.008, "Alumínio anodizado")
        c.box(f"Filtro {n} - moldura esquerda", fx0, f"{fy0} + 0.012", 0.004, 0.012, f"{fd} - 0.024", 0.008, "Alumínio anodizado")
        c.box(f"Filtro {n} - moldura direita", f"{fx0} + {fw} - 0.012", f"{fy0} + 0.012", 0.004, 0.012, f"{fd} - 0.024", 0.008, "Alumínio anodizado")
        c.box(f"Filtro {n} - manta", f"{fx0} + 0.012", f"{fy0} + 0.012", 0.009, f"{fw} - 0.024", f"{fd} - 0.024", 0.002, "Tela perfurada")
        for i in range(n_slats):
            c.box(f"Filtro {n} - lâmina {i + 1}", f"{fx0} + 0.012", f"{fy0} + 0.012 + {(i + 0.5) / n_slats}*({fd} - 0.024) - 0.005", 0.0055, f"{fw} - 0.024", 0.01, 0.003,
                  "Alumínio anodizado", detail=FINE)
        c.box(f"Filtro {n} - travessa central", f"{fx0} + {fw}/2 - 0.005", f"{fy0} + 0.012", 0.0045, 0.01, f"{fd} - 0.024", 0.004, "Alumínio anodizado", detail=FINE)
        c.box(f"Filtro {n} - trava", f"{fx0} + {fw}/2 - 0.03", f"{fy0} + 0.02", 0.001, 0.06, 0.016, 0.0035, "Plástico preto")
        c.box(f"Filtro {n} - mola da trava", f"{fx0} + {fw}/2 - 0.012", f"{fy0} + 0.002", 0.002, 0.024, 0.018, 0.002, "Aço galvanizado", detail=FINE)

    # --- chimney --------------------------------------------------------------
    t = 0.002
    for name, w, d, z0, h, plan in (
        ("Chaminé inferior", LD, PD, zc, AC, True),
        ("Chaminé superior", f"({LD} - 0.01)", f"({PD} - 0.005)", zm, f"({H} - {zm})", False),
    ):
        c.box(f"{name} - frente", f"-{w}/2", f"-{d}", z0, w, t, h, inox, in_plan=plan)
        c.box(f"{name} - lateral esquerda", f"-{w}/2", f"-{d} + {t}", z0, t, f"{d} - {t}", h, inox, in_plan=plan)
        c.box(f"{name} - lateral direita", f"{w}/2 - {t}", f"-{d} + {t}", z0, t, f"{d} - {t}", h, inox, in_plan=plan)
    # Air outlet slots at the top of the upper section.
    us = f"({LD} - 0.01)"
    for side, x in (("esquerda", f"-{us}/2 - 0.0006"), ("direita", f"{us}/2 - 0.0004")):
        for i in range(6):
            c.box(f"Chaminé superior - saída de ar {side} {i + 1}", x, f"-{PD}*0.78", f"{H} - 0.045 - {i}*0.016", 0.001, f"{PD}*0.56", 0.007, "Aço pintado preto", detail=FINE)
    for side, x in (("esquerdo", f"-{LD}/2 - 0.0015"), ("direito", f"{LD}/2")):
        for j, (y, z) in enumerate(((f"-{PD} + 0.03", f"{zc} + 0.025"), (-0.03, f"{zc} + 0.025"))):
            c.cyl_x(f"Chaminé inferior - parafuso {side} {j + 1}", y, z, x, 0.004, 0.0015, "Cromado", detail=FINE)

    # Inside the chimney: motor box, duct, wall brackets and cable (seen from above).
    c.box("Caixa do motor", f"-{LD}/2 + 0.02", f"-{PD} + 0.02", zc, f"{LD} - 0.04", f"{PD} - 0.04", f"{AC}*0.5", galv)
    zd = f"({zc} + {AC}*0.5)"
    c.cyl("Bocal de saída do motor", 0, f"-{PD}/2", zd, f"min({LD}, {PD})/2 - 0.03", 0.03, "Plástico preto")
    rd = f"(min({LD}, {PD})/2 - 0.036)"
    c.cyl("Duto de exaustão", 0, f"-{PD}/2", f"{zd} + 0.03", rd, f"{H} - {zd} - 0.03", "Alumínio anodizado")
    for i in range(8):
        c.cyl(f"Duto de exaustão - anel {i + 1}", 0, f"-{PD}/2", f"{zd} + 0.05 + {i / 8}*({H} - {zd} - 0.06)", f"{rd} + 0.003", 0.008, "Alumínio anodizado", detail=FINE)
    c.cyl("Duto de exaustão - abraçadeira", 0, f"-{PD}/2", f"{zd} + 0.03", f"{rd} + 0.004", 0.012, galv, detail=FINE)
    for name, z in (("superior", f"{H} - 0.05"), ("inferior", f"{zm} - 0.06")):
        w = f"({LD} - 0.014)" if name == "superior" else f"({LD} - 0.004)"
        c.box(f"Suporte de parede {name}", f"-{w}/2", -0.0025, z, w, 0.0025, 0.04, galv)
        c.box(f"Suporte de parede {name} - aba esquerda", f"-{w}/2", -0.03, z, 0.002, 0.0275, 0.04, galv, detail=FINE)
        c.box(f"Suporte de parede {name} - aba direita", f"{w}/2 - 0.002", -0.03, z, 0.002, 0.0275, 0.04, galv, detail=FINE)
        for j, fx in enumerate((-0.3, 0.3)):
            c.cyl_y(f"Suporte de parede {name} - parafuso {j + 1}", f"{LD}*{fx}", f"{z} + 0.02", -0.0045, 0.005, 0.002, "Cromado", detail=FINE)
    c.cyl("Cabo de alimentação", f"{LD}/2 - 0.03", -0.012, f"{zd}", 0.004, f"{H} - {zd} - 0.06", "Borracha", detail=FINE)
    c.box("Cabo de alimentação - plugue", f"{LD}/2 - 0.048", -0.026, f"{H} - 0.06", 0.036, 0.024, 0.03, "Plástico preto", detail=FINE)
    # Keyhole plates that hang the canopy on the wall.
    for sx, n in ((f"-{W}*0.35", "esquerda"), (f"{W}*0.35 - 0.05", "direita")):
        c.box(f"Chapa de fixação {n}", sx, -0.0015, f"{AA} + 0.008", 0.05, 0.0015, 0.03, galv, detail=FINE)

    c.preview_size = (0.6, 0.48, 0.78)
    c.type("Coifa de parede 60 cm", "Coifa de parede piramidal em inox, 60 x 48 cm, chaminé telescópica, 3 velocidades, filtros metálicos e LED")
    c.type("Coifa de parede 90 cm", "Coifa de parede piramidal em inox, 90 x 50 cm, chaminé telescópica, 3 velocidades, filtros metálicos e LED", Largura=0.9, Profundidade=0.5)
    return c
