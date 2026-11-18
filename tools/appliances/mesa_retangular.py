"""Mesa retangular: top with rounded corners on an apron frame with turned legs."""

from kit import *


def turned(c, name, cx, cy, profile, material, detail=FULL):
    """A turned piece about the vertical axis at (cx, cy): profile = [(radius, z), …] from bottom to top."""
    pts = [(cx, profile[0][1])] + [(f"{p(cx)} + {p(r)}", z) for r, z in profile] + [(cx, profile[-1][1])]
    c.rev(name, "Front", pts, cy, cx, material, detail=detail)


def build():
    c = Component("Mesa retangular", "furniture", "mesa-retangular")
    W = c.param("Largura", 1.2)
    D = c.param("Profundidade", 0.8)
    H = c.param("Altura", 0.75)
    T = c.param("Tampo", 0.03)
    c.type("Mesa retangular 120x80", "Mesa de jantar, 4 lugares", Largura=1.2, Profundidade=0.8)
    c.type("Mesa retangular 160x90", "Mesa de jantar, 6 lugares", Largura=1.6, Profundidade=0.9)
    c.type("Mesa retangular 200x100", "Mesa de jantar, 8 lugares", Largura=2.0, Profundidade=1.0)
    c.type("Mesa retangular 240x100", "Mesa de jantar, 10 lugares", Largura=2.4, Profundidade=1.0)
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")

    wood, dark = "Madeira", "Madeira escura"
    xl, yf = f"-{W}/2", f"-{D}/2"
    zu = f"{H} - {T}"  # underside of the top

    # Coarse stand-ins: the old boxes.
    c.box("Tampo simplificado", xl, yf, zu, W, D, T, wood, detail=COARSE, in_plan=True)
    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        c.box(f"Perna simplificada {n}", f"{sx}*({W}/2 - 0.07) - 0.025", f"{sy}*({D}/2 - 0.07) - 0.025", 0, 0.05, 0.05, zu, wood,
              detail=COARSE)

    # Top: a slab with rounded corners over a chamfered lower layer.
    c.profile("Tampo", "Plan", rrect(xl, yf, f"{W}/2", f"{D}/2", 0.03), f"{H} - 0.6*{T}", f"0.6*{T}", wood, in_plan=True)
    c.profile("Tampo - bisel inferior", "Plan", rrect(f"{xl} + 0.01", f"{yf} + 0.01", f"{W}/2 - 0.01", f"{D}/2 - 0.01", 0.024), zu,
              f"0.4*{T}", wood)

    # Apron.
    ah = 0.1
    za = f"{zu} - {ah}"
    lx, ly = f"{W}/2 - 0.105", f"{D}/2 - 0.105"  # where the leg blocks start
    c.box("Saia frontal", f"-({lx})", f"{yf} + 0.047", za, f"2*({lx})", 0.022, ah, wood)
    c.box("Saia traseira", f"-({lx})", f"{D}/2 - 0.069", za, f"2*({lx})", 0.022, ah, wood)
    c.box("Saia esquerda", f"{xl} + 0.047", f"-({ly})", za, 0.022, f"2*({ly})", ah, wood)
    c.box("Saia direita", f"{W}/2 - 0.069", f"-({ly})", za, 0.022, f"2*({ly})", ah, wood)
    # A bead along the bottom of the apron.
    c.box("Filete da saia frontal", f"-({lx})", f"{yf} + 0.043", za, f"2*({lx})", 0.004, 0.012, dark, detail=FINE)
    c.box("Filete da saia traseira", f"-({lx})", f"{D}/2 - 0.047", za, f"2*({lx})", 0.004, 0.012, dark, detail=FINE)
    c.box("Filete da saia esquerda", f"{xl} + 0.043", f"-({ly})", za, 0.004, f"2*({ly})", 0.012, dark, detail=FINE)
    c.box("Filete da saia direita", f"{W}/2 - 0.047", f"-({ly})", za, 0.004, f"2*({ly})", 0.012, dark, detail=FINE)
    # Cross rails that keep the long rails straight.
    for n, sx in enumerate((-1, 1), 1):
        c.box(f"Travessa interna {n}", f"{sx}*{W}/6 - 0.011", f"{yf} + 0.069", f"{zu} - 0.07", 0.022, f"{D} - 0.138", 0.07, wood)

    names = {(-1, -1): "frontal esquerda", (1, -1): "frontal direita", (-1, 1): "traseira esquerda", (1, 1): "traseira direita"}
    zb = f"{zu} - 0.115"  # bottom of the square leg block
    for (sx, sy), where in names.items():
        cx, cy = f"{sx}*({W}/2 - 0.07)", f"{sy}*({D}/2 - 0.07)"
        c.box(f"Perna {where} - bloco", f"{cx} - 0.035", f"{cy} - 0.035", zb, 0.07, 0.07, 0.115, wood)
        turned(c, f"Perna {where}", cx, cy, [
            (0.017, 0.014), (0.0185, 0.05), (0.031, f"{zb} - 0.075"), (0.031, f"{zb} - 0.062"), (0.037, f"{zb} - 0.054"),
            (0.037, f"{zb} - 0.04"), (0.027, f"{zb} - 0.032"), (0.027, f"{zb} - 0.016"), (0.034, f"{zb} - 0.008"), (0.034, zb)], wood)
        turned(c, f"Perna {where} - anel", cx, cy, [(0.0195, 0.05), (0.0215, 0.054), (0.0215, 0.06), (0.02, 0.064)], dark, detail=FINE)
        turned(c, f"Perna {where} - sapata", cx, cy, [(0.012, 0.003), (0.019, 0.008), (0.019, 0.014)], "Latão", detail=FINE)
        c.cyl(f"Perna {where} - feltro", cx, cy, 0, 0.011, 0.003, "Feltro", detail=FINE)
        # Corner brace between the two rails.
        pts = [(f"{sx}*({W}/2 - 0.205)", f"{sy}*({D}/2 - 0.069)"), (f"{sx}*({W}/2 - 0.069)", f"{sy}*({D}/2 - 0.205)"),
               (f"{sx}*({W}/2 - 0.069)", f"{sy}*({D}/2 - 0.235)"), (f"{sx}*({W}/2 - 0.235)", f"{sy}*({D}/2 - 0.069)")]
        if sx * sy > 0:
            pts.reverse()
        c.profile(f"Cantoneira {where}", "Plan", pts, f"{zu} - 0.085", 0.07, wood, detail=FINE)
        c.cyl_y(f"Parafuso da cantoneira {where}", f"{sx}*({W}/2 - 0.16)", f"{zu} - 0.05", f"{sy}*({D}/2 - 0.118) - 0.004", 0.005, 0.008,
                "Aço galvanizado", detail=FINE)

    # Clips that hold the top to the apron.
    n = 0
    for sy in (-1, 1):
        for fx in (-0.3, 0, 0.3):
            n += 1
            c.box(f"Presilha do tampo {n}", f"{fx}*{W} - 0.012", f"{sy}*({D}/2 - 0.084) - 0.015", f"{zu} - 0.004", 0.024, 0.03, 0.004,
                  "Aço galvanizado", detail=FINE)
    for sx in (-1, 1):
        n += 1
        c.box(f"Presilha do tampo {n}", f"{sx}*({W}/2 - 0.084) - 0.015", -0.012, f"{zu} - 0.004", 0.03, 0.024, 0.004, "Aço galvanizado",
              detail=FINE)
    return c
