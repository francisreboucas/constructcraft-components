"""Cadeira com encosto: raked back posts, curved rails with slats, upholstered seat."""

from kit import *


def build():
    c = Component("Cadeira com encosto", "furniture", "cadeira")
    W = c.param("Largura", 0.45)
    P = c.param("Profundidade", 0.5)
    AS = c.param("AlturaAssento", 0.45)
    H = c.param("Altura", 0.9)
    c.type("Cadeira de jantar", "Cadeira com assento estofado")
    c.type("Cadeira de escritório", "Cadeira de trabalho", Largura=0.6, Profundidade=0.6, AlturaAssento=0.48, Altura=1.0)
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")
    c.material("Tecido cinza escuro", (92, 95, 100), "Generic", "Matte")

    wood, dark, fabric = "Madeira", "Madeira escura", "Tecido"
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{P}/2", f"{P}/2"
    zt = f"{AS} - 0.05"  # top of the seat frame
    g = 0.003  # glides

    # Coarse stand-ins: the old boxes.
    c.box("Assento simplificado", xl, yf, f"{AS} - 0.05", W, P, 0.05, fabric, detail=COARSE, in_plan=True)
    c.box("Encosto simplificado", xl, f"{yb} - 0.03", AS, W, 0.03, f"{H} - {AS}", wood, detail=COARSE, in_plan=True)
    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        c.box(f"Perna simplificada {n}", f"{sx}*({W}/2 - 0.04) - 0.02", f"{sy}*({P}/2 - 0.04) - 0.02", 0, 0.04, 0.04, f"{AS} - 0.05", wood,
              detail=COARSE)

    # Back posts: one piece from the floor to the top, kicked back at the foot and raked above the seat.
    pw = 0.034
    post = [(f"{yb} - 0.034", g), (f"{yb} - 0.002", g), (f"{yb} - 0.05", AS), (f"{yb} - 0.002", f"{H} - 0.012", 0.014),
            (f"{yb} - 0.016", H), (f"{yb} - 0.028", H), (f"{yb} - 0.092", AS)]
    c.profile("Montante traseiro esquerdo", "Side", post, xl, pw, wood)
    c.profile("Montante traseiro direito", "Side", post, f"{xr} - {pw}", pw, wood)
    k = f"0.064/({H} - {AS})"  # how much the back's front face leans per meter of height

    def face(z):  # y of the posts' front face at the height z above the seat
        return f"{yb} - 0.092 + {k}*({z})"

    # Front legs, tapered on the inside.
    fw = 0.036
    zr = f"{zt} - 0.065"
    for name, pts in (("esquerda", [(xl, g), (f"{xl} + 0.024", g), (f"{xl} + {fw}", zr), (f"{xl} + {fw}", zt), (xl, zt)]),
                      ("direita", [(f"{xr} - 0.024", g), (xr, g), (xr, zt), (f"{xr} - {fw}", zt), (f"{xr} - {fw}", zr)])):
        c.profile(f"Perna frontal {name}", "Front", pts, f"{yf} + 0.008", fw, wood)

    # Seat frame.
    c.box("Travessa do assento frontal", f"{xl} + {fw}", f"{yf} + 0.014", zr, f"{W} - {2 * fw}", 0.022, 0.065, wood)
    c.box("Travessa do assento traseira", f"{xl} + {pw}", f"{yb} - 0.082", zr, f"{W} - {2 * pw}", 0.022, 0.065, wood)
    c.box("Travessa do assento esquerda", f"{xl} + 0.006", f"{yf} + 0.044", zr, 0.022, f"{P} - 0.13", 0.065, wood)
    c.box("Travessa do assento direita", f"{xr} - 0.028", f"{yf} + 0.044", zr, 0.022, f"{P} - 0.13", 0.065, wood)
    for where, sx, sy, ya in (("frontal esquerda", -1, -1, f"{yf} + 0.036"), ("frontal direita", 1, -1, f"{yf} + 0.036"),
                              ("traseira esquerda", -1, 1, f"{yb} - 0.082"), ("traseira direita", 1, 1, f"{yb} - 0.082")):
        xa = f"{sx}*({W}/2 - 0.028)"
        pts = [(xa, f"{ya} + {-sy}*0.075"), (f"{sx}*({W}/2 - 0.105)", ya), (f"{sx}*({W}/2 - 0.125)", ya), (xa, f"{ya} + {-sy}*0.095")]
        if sx * sy < 0:
            pts.reverse()
        c.profile(f"Cantoneira {where}", "Plan", pts, f"{zt} - 0.045", 0.04, wood, detail=FINE)

    # Stretchers: one on each side, a cross one between them, one at the back.
    c.box("Travessa lateral esquerda", f"{xl} + 0.007", f"{yf} + 0.04", 0.17, 0.018, f"{P} - 0.085", 0.026, wood)
    c.box("Travessa lateral direita", f"{xr} - 0.025", f"{yf} + 0.04", 0.17, 0.018, f"{P} - 0.085", 0.026, wood)
    c.box("Travessa central", f"{xl} + 0.025", f"-0.05*{P} - 0.009", 0.173, f"{W} - 0.05", 0.018, 0.02, wood)
    c.box("Travessa traseira inferior", f"{xl} + {pw}", f"{yb} - 0.062", 0.26, f"{W} - {2 * pw}", 0.018, 0.026, wood)

    # Seat: a board with rounded corners and a crowned cushion with piping.
    ys1 = f"{yb} - 0.093"  # the seat stops at the back posts
    c.profile("Base do assento", "Plan", rrect(xl, yf, xr, ys1, 0.022), zt, 0.012, wood, in_plan=True)
    c.profile("Vivo do assento", "Plan", rrect(f"{xl} + 0.002", f"{yf} + 0.002", f"{xr} - 0.002", f"{ys1} - 0.002", 0.022),
              f"{zt} + 0.012", 0.005, "Tecido cinza escuro", detail=FINE)
    for n, (inset, z0, h, r) in enumerate(((0.005, 0.012, 0.022, 0.024), (0.012, 0.034, 0.009, 0.03), (0.028, 0.043, 0.007, 0.04)), 1):
        c.profile(f"Almofada do assento - camada {n}", "Plan",
                  rrect(f"{xl} + {inset}", f"{yf} + {inset}", f"{xr} - {inset}", f"{ys1} - {inset}", r), f"{zt} + {z0}", h, fabric,
                  in_plan=(n == 1))

    # Backrest: two rails curved in plan between the posts and five slats that follow the curve and the rake.
    span = f"({W} - {2 * pw})"
    sag = 0.012
    radius = f"({span}*{span}/4 + {sag * sag})/{2 * sag}"
    xa, xb = f"{xl} + {pw}", f"{xr} - {pw}"

    def rail(name, z0, h, thick, plan=False):
        zm = f"{z0} + {h / 2} - {AS}"
        y0 = f"{face(zm)} + 0.004"
        c.profile(name, "Plan", [(xa, y0, f"-({radius})"), (xb, y0), (xb, f"{y0} + {thick}", radius), (xa, f"{y0} + {thick}")], z0, h, wood,
                  in_plan=plan)

    rail("Travessa superior do encosto", f"{H} - 0.085", 0.075, 0.018, plan=True)
    rail("Travessa inferior do encosto", f"{AS} + 0.11", 0.04, 0.018)
    zs0, zs1 = f"{AS} + 0.145", f"{H} - 0.08"
    for n, f in enumerate((-0.68, -0.34, 0, 0.34, 0.68), 1):
        s = sag * (1 - f * f) + 0.007
        y0, y1 = f"{face('0.145')} + {s:.5f}", f"{face(f'{H} - 0.08 - {AS}')} + {s:.5f}"
        c.profile(f"Ripa do encosto {n}", "Side", [(y0, zs0), (f"{y0} + 0.012", zs0), (f"{y1} + 0.012", zs1), (y1, zs1)],
                  f"{f / 2}*{span} - 0.016", 0.032, wood, detail=FINE)

    # Glides.
    for where, x, y in (("frontal esquerda", f"{xl} + 0.012", f"{yf} + 0.026"), ("frontal direita", f"{xr} - 0.012", f"{yf} + 0.026"),
                        ("traseira esquerda", f"{xl} + 0.017", f"{yb} - 0.018"), ("traseira direita", f"{xr} - 0.017", f"{yb} - 0.018")):
        c.cyl(f"Deslizador {where}", x, y, 0, 0.01, g, "Feltro", detail=FINE)
    return c
