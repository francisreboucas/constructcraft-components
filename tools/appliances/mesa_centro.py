"""Mesa de centro: mitered wooden frame with a glass (or wooden) inset top, tapered legs with through tenons, slatted lower shelf."""

from kit import *
from _mobilia import EPS, Grp, blend, at


def blob(c, name, x, y, z, r, mat, n=8, detail=FINE):
    """A sphere of radius r standing on z."""
    import math
    pts = [(x, z)]
    for i in range(1, n):
        a = math.pi * i / n
        pts.append((at(x, r * math.sin(a)), at(z, r - r * math.cos(a))))
    pts.append((x, at(z, 2 * r)))
    c.rev(name, "Front", pts, y, x, mat, detail=detail)


def lying_book(c, name, x, y, z, w, d, t, mat):
    """A book lying flat: x, y its lowest corner, w along x, d along y (the spine at -y), t thick."""
    b = 0.0025  # cover boards
    c.box(f"{name} - capa inferior", x, y, z, w, d, b, mat, detail=FINE)
    c.box(f"{name} - capa superior", x, y, at(z, t - b), w, d, b, mat, detail=FINE)
    c.box(f"{name} - lombada", x, y, at(z, b), w, 0.003, t - 2 * b, mat, detail=FINE)
    c.box(f"{name} - miolo", at(x, 0.003), at(y, 0.003), at(z, b), w - 0.006, d - 0.006, t - 2 * b, "Papel", detail=FINE)


def build():
    c = Component("Mesa de centro", "furniture", "mesa-centro")
    W = c.param("Largura", 1.0)
    D = c.param("Profundidade", 0.6)
    H = c.param("Altura", 0.4)
    V = c.param("TampoVidro", 1, "Number")
    c.type("Mesa de centro 100x60 vidro", "Mesa de centro com tampo de vidro temperado e prateleira de ripas")
    c.type("Mesa de centro 80x80 madeira", "Mesa de centro quadrada com tampo de madeira", Largura=0.8, Profundidade=0.8, TampoVidro=0)
    c.type("Mesa de centro 120x70 vidro", "Mesa de centro com tampo de vidro temperado e prateleira de ripas", Largura=1.2,
           Profundidade=0.7)
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")
    c.material("Papel", (238, 232, 214), "Generic", "Matte")
    c.material("Capa de livro azul", (44, 72, 128), "Generic", "Matte")
    c.material("Capa de livro vinho", (104, 34, 52), "Generic", "Matte")

    wood, dark, steel = "Madeira", "Madeira escura", "Aço galvanizado"
    g = 0.004  # glides
    bw = 0.07  # frame band
    xh, yh = f"({W}/2)", f"({D}/2)"
    zu = f"({H} - 0.032)"  # underside of the top frame
    za = f"({zu} - 0.07)"  # bottom of the apron
    lx, ly = f"({xh} - 0.05)", f"({yh} - 0.05)"  # leg centers
    lb, lt = 0.016, 0.025  # half sizes of the legs at the floor and under the top

    def half(z):  # half size of a leg at the height z
        return f"({lb} + {lt - lb}*(({e(z)}) - {g})/({zu} - {g}))"

    # Coarse stand-ins.
    c.box("Tampo simplificado", f"-{xh}", f"-{yh}", zu, W, D, 0.032, wood, detail=COARSE, in_plan=True)
    c.box("Prateleira simplificada", f"-({lx})", f"-({ly})", 0.09, f"2*{lx}", f"2*{ly}", 0.048, wood, detail=COARSE)
    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        c.box(f"Perna simplificada {n}", f"{sx}*{lx} - {lt}", f"{sy}*{ly} - {lt}", 0, 2 * lt, 2 * lt, zu, wood, detail=COARSE)

    # Top frame: four mitered rails in two layers; the lower one makes the ledge the inset rests on.
    def rails(name, z, h, b, plan):
        a, bx, by = f"{xh} - {b}", f"{xh} - {b}", f"{yh} - {b}"
        outlines = {
            "frontal": [(f"-{xh}", f"-{yh}"), (xh, f"-{yh}"), (a, f"-({by})"), (f"-({bx})", f"-({by})")],
            "traseira": [(xh, yh), (f"-{xh}", yh), (f"-({bx})", by), (bx, by)],
            "esquerda": [(f"-{xh}", yh), (f"-{xh}", f"-{yh}"), (f"-({bx})", f"-({by})"), (f"-({bx})", by)],
            "direita": [(xh, f"-{yh}"), (xh, yh), (bx, by), (bx, f"-({by})")],
        }
        for side, pts in outlines.items():
            c.extrusion(f"{name} {side}", pts, z, h, wood, in_plan=plan)

    rails("Moldura do tampo", f"{H} - 0.012", 0.012, bw, True)
    rails("Rebaixo da moldura", zu, 0.02, bw + 0.012, False)
    # Miter joints: a thin dark line on top at each corner.
    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        pts = [(f"{sx}*{xh}", f"{sy}*{yh} - 0.0006"), (f"{sx}*{xh}", f"{sy}*{yh} + 0.0006"),
               (f"{sx}*({xh} - {bw})", f"{sy}*({yh} - {bw}) + 0.0006"), (f"{sx}*({xh} - {bw})", f"{sy}*({yh} - {bw}) - 0.0006")]
        if sx * sy < 0:
            pts.reverse()
        c.extrusion(f"Junta de meia-esquadria {n}", pts, H, 0.0003, dark, detail=FINE)

    # The inset: tempered glass on rubber bumpers, or a wooden panel (TampoVidro = 0); the other one folds into the frame.
    hide = (0, f"-{yh} + 0.03", f"{H} - 0.02")
    glass = Grp(c, f"max({EPS}, {V})", hide)
    panel = Grp(c, f"max({EPS}, 1 - {V})", hide)
    gx, gy = f"({xh} - {bw} - 0.001)", f"({yh} - {bw} - 0.001)"
    glass.box("Vidro do tampo", f"-{gx}", f"-{gy}", f"{H} - 0.011", f"2*{gx}", f"2*{gy}", 0.008, "Vidro temperado")
    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        glass.cyl(f"Batente de borracha {n}", f"{sx}*({xh} - {bw} - 0.006)", f"{sy}*({yh} - {bw} - 0.006)", f"{H} - 0.012", 0.004, 0.001,
                  "Plástico translúcido", detail=FINE)
    panel.box("Painel de madeira do tampo", f"-{gx}", f"-{gy}", f"{H} - 0.012", f"2*{gx}", f"2*{gy}", 0.0115, wood)
    for i in range(1, 4):  # the panel is glued up from boards
        panel.box(f"Junta das tábuas do painel {i}", f"-{gx}", f"-{gy} + 2*{gy}*{i / 4}", f"{H} - 0.0005", f"2*{gx}", 0.0008, 0.0002, dark,
                  detail=FINE)

    # Legs: square, tapered towards the floor, on felt glides.
    names = {(-1, -1): "frontal esquerda", (1, -1): "frontal direita", (-1, 1): "traseira esquerda", (1, 1): "traseira direita"}
    for (sx, sy), where in names.items():
        cx, cy = f"{sx}*{lx}", f"{sy}*{ly}"
        bottom = rect(f"{cx} - {lb}", f"{cy} - {lb}", f"{cx} + {lb}", f"{cy} + {lb}")
        top = rect(f"{cx} - {lt}", f"{cy} - {lt}", f"{cx} + {lt}", f"{cy} + {lt}")
        blend(c, f"Perna {where}", "Plan", bottom, top, g, f"{zu} - {g}", wood)
        c.cyl(f"Feltro da perna {where}", cx, cy, 0, 0.012, g, "Feltro", detail=FINE)
        # Through tenons of the apron and the shelf stretcher, and the pegs that lock them (a little proud of the faces).
        zt = f"{za} + 0.015"
        hz = half(f"{za} + 0.035")

        def face(s, center, h, t=0.002):
            return f"{s}*({center} + {h}) - {t / 2 if s > 0 else t / 2}"

        c.box(f"Espiga da saia longitudinal - perna {where}", face(sx, lx, hz), f"{sy}*({ly} + {lt} - 0.02) - 0.005", zt, 0.002, 0.01, 0.04,
              dark, detail=FINE)
        c.box(f"Espiga da saia transversal - perna {where}", f"{sx}*({lx} + {lt} - 0.02) - 0.005", face(sy, ly, hz), zt, 0.01, 0.002, 0.04,
              dark, detail=FINE)
        c.box(f"Espiga da travessa da prateleira - perna {where}", f"{cx} - 0.005", face(sy, ly, half(0.105)), 0.095, 0.01, 0.002, 0.02,
              dark, detail=FINE)
        for k, dz in enumerate((0.02, 0.05), 1):
            c.cyl_y(f"Cavilha {k} da perna {where}", f"{sx}*({lx} - 0.008)", f"{za} + {dz}", face(sy, ly, half(f"{za} + {dz}"), 0.0016),
                    0.004, 0.0016, dark, detail=FINE)

    # Apron, set back 1 cm from the legs' faces.
    ax, ay = f"({lx} - {lt})", f"({ly} - {lt})"  # where the legs' inner faces are
    t = 0.02
    for name, x0, y0, w, d in (("frontal", f"-{ax}", f"-({ly} + {lt} - 0.01)", f"2*{ax}", t),
                               ("traseira", f"-{ax}", f"{ly} + {lt} - 0.01 - {t}", f"2*{ax}", t),
                               ("esquerda", f"-({lx} + {lt} - 0.01)", f"-{ay}", t, f"2*{ay}"),
                               ("direita", f"{lx} + {lt} - 0.01 - {t}", f"-{ay}", t, f"2*{ay}")):
        c.box(f"Saia {name}", x0, y0, za, w, d, f"{zu} - {za}", wood)
    # Corner blocks screwed to the apron and up into the top frame.
    for (sx, sy), where in names.items():
        xi, yi = f"{sx}*({lx} + {lt} - 0.03)", f"{sy}*({ly} + {lt} - 0.03)"
        pts = [(xi, f"{sy}*({ly} - {lt} - 0.07)"), (xi, f"{sy}*({ly} - {lt} - 0.04)"), (f"{sx}*({lx} - {lt} - 0.04)", yi),
               (f"{sx}*({lx} - {lt} - 0.07)", yi)]
        if sx * sy < 0:
            pts.reverse()
        c.extrusion(f"Taco de canto {where}", pts, f"{zu} - 0.05", 0.05, wood, detail=FINE)
        c.cyl(f"Parafuso do taco de canto {where}", f"{sx}*({lx} - {lt} - 0.045)", f"{sy}*({ly} - {lt} - 0.045)", f"{zu} - 0.052", 0.005, 0.003,
              steel, detail=FINE)

    # Lower shelf: two stretchers across and slats along the table.
    for name, sx in (("esquerda", -1), ("direita", 1)):
        c.box(f"Travessa da prateleira {name}", f"{sx}*{lx} - 0.011", f"-{ly}", 0.09, 0.022, f"2*{ly}", 0.03, wood)
    ns = 7
    ys = f"({yh} - 0.08)"
    for i in range(ns):
        c.box(f"Ripa da prateleira {i + 1}", f"-({lx} + 0.011)", f"-{ys} + 2*{ys}*{i / ns:.5f} + 0.006", 0.12, f"2*({lx} + 0.011)",
              f"2*{ys}/{ns} - 0.012", 0.018, wood, in_plan=False)
        for name, sx in (("esquerdo", -1), ("direito", 1)):
            c.cyl(f"Prego da ripa {i + 1} - {name}", f"{sx}*{lx}", f"-{ys} + 2*{ys}*{(i + 0.5) / ns:.5f}", 0.1385, 0.0025, 0.0004,
                  steel, detail=FINE)

    # On the top: two books and a bowl with wooden balls. On the shelf: magazines.
    zs = f"({H} - 0.001 - 0.003*{V})"  # surface of the inset
    xb = f"{xh} - 0.36"
    lying_book(c, "Livro 1", xb, -0.12, zs, 0.28, 0.21, 0.032, "Capa de livro azul")
    lying_book(c, "Livro 2", f"{xb} + 0.025", -0.1, f"{zs} + 0.032", 0.235, 0.17, 0.024, "Capa de livro vinho")
    xc = f"(-{xh} + 0.25)"
    bowl = [(xc, zs), (f"{xc} + 0.05", zs), (f"{xc} + 0.06", f"{zs} + 0.008"), (f"{xc} + 0.115", f"{zs} + 0.07"),
            (f"{xc} + 0.11", f"{zs} + 0.07"), (f"{xc} + 0.058", f"{zs} + 0.013"), (xc, f"{zs} + 0.013")]
    c.rev("Fruteira", "Front", bowl, 0.04, xc, "Louça", detail=FINE)
    for i, (dx, dy, r) in enumerate(((-0.035, 0.0, 0.032), (0.03, -0.02, 0.03), (0.01, 0.04, 0.03)), 1):
        blob(c, f"Bola decorativa {i}", f"{xc} + {dx}", 0.04 + dy, f"{zs} + 0.013", r, dark)
    for i, (dx, dy, mat) in enumerate(((0, 0, "Capa de livro azul"), (0.015, 0.02, "Papel")), 1):
        c.box(f"Revista {i}", f"-0.15 + {dx}", f"-0.12 + {dy}", 0.138 + 0.006 * (i - 1), 0.21, 0.275, 0.006, mat, detail=FINE)
    return c
