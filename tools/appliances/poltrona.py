"""Poltrona de madeira: mid-century armchair, an exposed wooden frame with paddle arms, loose seat and back cushions."""

from kit import *
from _mobilia import tilted, turned  # noqa: F401

K = 0.15  # rake of the back: y per meter of height
GA = 8.5308  # the same rake as an angle, atan(K) in degrees


def build():
    c = Component("Poltrona de madeira", "furniture", "poltrona")
    W = c.param("Largura", 0.72)
    P = c.param("Profundidade", 0.78)
    H = c.param("Altura", 0.8)
    AS = c.param("AlturaAssento", 0.42)
    c.type("Poltrona de madeira 72 cm", "Poltrona com estrutura de madeira aparente e almofadas soltas")
    c.type("Poltrona de madeira 82 cm", "Poltrona larga com estrutura de madeira aparente", Largura=0.82, Profundidade=0.84,
           Altura=0.84)
    c.material("Tecido mostarda", (201, 152, 58), "Generic", "Matte")
    c.material("Tecido cinza escuro", (92, 95, 100), "Generic", "Matte")
    c.material("Tecido azul petróleo", (48, 92, 110), "Generic", "Matte")
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")

    wood, dark, fabric, welt = "Madeira", "Madeira escura", "Tecido mostarda", "Tecido cinza escuro"
    g = 0.004  # glides
    tw = 0.04  # side frames
    xl, xr = f"(-{W}/2)", f"({W}/2)"
    yf, yb = f"(-{P}/2)", f"({P}/2)"
    zr0, zr1 = f"({AS} - 0.17)", f"({AS} - 0.11)"  # seat rails
    za = f"({AS} + 0.19)"  # top of the arms
    yk = f"({yb} - 0.13)"  # front of the back posts at the seat rails

    def yfr(z):  # front face of the back posts (and of the back frame) above the seat rails
        return f"({yk} + {K}*(({e(z)}) - {zr1}))"

    def yleg(z):  # front face of the back legs below the seat rails
        return f"({yb} - 0.05 - 0.08*(({e(z)}) - {g})/({zr1} - {g}))"

    # Coarse stand-ins.
    c.box("Assento simplificado", f"{xl} + {tw}", f"{yf} + 0.035", zr0, f"{W} - {2 * tw}", f"{yk} + 0.02 - ({yf} + 0.035)",
          f"{AS} - {zr0}", fabric, detail=COARSE, in_plan=True)
    c.profile("Encosto simplificado", "Side", [(f"{yfr(AS)} - 0.1", AS), (f"{yfr(AS)} + 0.03", AS), (f"{yfr(H)} + 0.03", H),
                                               (f"{yfr(H)} - 0.1", H)], xl, W, fabric, detail=COARSE, in_plan=True)
    for name, x0 in (("esquerda", xl), ("direita", f"{xr} - {tw}")):
        c.box(f"Lateral {name} simplificada", x0, f"{yf} + 0.03", 0, tw, f"{yb} - 0.01 - ({yf} + 0.03)", za, wood, detail=COARSE,
              in_plan=True)

    # Side frames: raked front leg, back leg and post in one piece, paddle arm, seat rail and a round stretcher.
    for name, x0, sx in (("esquerdo", xl, -1), ("direito", f"{xr} - {tw}", 1)):
        xm = f"{x0} + {tw / 2}"
        c.profile(f"Perna dianteira - lado {name}", "Side", [(f"{yf} + 0.075", g), (f"{yf} + 0.105", g), (f"{yf} + 0.095", f"{za} - 0.024"),
                                                            (f"{yf} + 0.05", f"{za} - 0.024")], x0, tw, wood)
        top = yfr(H)
        c.profile(f"Montante traseiro - lado {name}", "Side", [
            (f"{yb} - 0.05", g), (f"{yb} - 0.012", g), (f"{yk} + 0.034", zr1), (f"{top} + 0.034", f"{H} - 0.016", 0.02),
            (f"{top} + 0.016", H), (top, H), (yk, zr1)], x0, tw, wood, in_plan=True)
        # The arm overhangs the frame, a little more inwards.
        ax0, ax1 = (f"{x0} - 0.006", f"{x0} + {tw} + 0.024") if sx < 0 else (f"{x0} - 0.024", f"{x0} + {tw} + 0.006")
        c.profile(f"Braço {name}", "Plan", rrect(ax0, f"{yf} + 0.03", ax1, f"{yfr(za)} + 0.022", 0.03), f"{za} - 0.024", 0.024, wood,
                  in_plan=True)
        c.box(f"Travessa do assento - lado {name}", f"{x0} + 0.007", f"{yf} + 0.09", zr0, 0.026, f"{yk} + 0.005 - ({yf} + 0.09)",
              f"{zr1} - {zr0}", wood)
        c.cyl_y(f"Travessa inferior - lado {name}", xm, 0.13, f"{yf} + 0.09", 0.011, f"{yleg(0.13)} + 0.015 - ({yf} + 0.09)", wood)
        # Brass ferrules and felt glides.
        c.profile(f"Ponteira da perna dianteira - lado {name}", "Side", [(f"{yf} + 0.0738", g), (f"{yf} + 0.1062", g),
                                                                        (f"{yf} + 0.1057", f"{g} + 0.03"), (f"{yf} + 0.0725", f"{g} + 0.03")],
                  f"{x0} - 0.001", tw + 0.002, "Latão", detail=FINE)
        c.profile(f"Ponteira da perna traseira - lado {name}", "Side", [(f"{yb} - 0.051", g), (f"{yb} - 0.011", g),
                                                                       (f"{yb} - 0.0193", f"{g} + 0.03"), (f"{yb} - 0.0589", f"{g} + 0.03")],
                  f"{x0} - 0.001", tw + 0.002, "Latão", detail=FINE)
        c.cyl(f"Feltro da perna dianteira - lado {name}", xm, f"{yf} + 0.09", 0, 0.012, g, "Feltro", detail=FINE)
        c.cyl(f"Feltro da perna traseira - lado {name}", xm, f"{yb} - 0.031", 0, 0.012, g, "Feltro", detail=FINE)
        # Wooden plugs over the screws: on the arm, and on the outer face where the rails meet the legs.
        c.cyl(f"Cavilha do braço dianteira - lado {name}", xm, f"{yf} + 0.075", za, 0.007, 0.0008, dark, detail=FINE)
        c.cyl(f"Cavilha do braço traseira - lado {name}", xm, f"{yfr(za)} + 0.017", za, 0.007, 0.0008, dark, detail=FINE)
        xo = f"{x0} - 0.0008" if sx < 0 else f"{x0} + {tw}"
        zm = f"({zr0} + {zr1})/2"
        for where, yc in (("dianteira", f"{yf} + 0.08"), ("traseira", f"{yk} + 0.017")):
            c.cyl_x(f"Cavilha da travessa {where} - lado {name}", yc, zm, xo, 0.007, 0.0008, dark, detail=FINE)
        c.cyl_x(f"Cavilha do encosto - lado {name}", f"{yfr(f'{H} - 0.0475')} + 0.015", f"{H} - 0.0475", xo, 0.007, 0.0008, dark,
                detail=FINE)

    # Seat frame between the side frames, with elastic webbing.
    xa, wi = f"({xl} + {tw})", f"({W} - {2 * tw})"
    c.box("Travessa dianteira do assento", xa, f"{yf} + 0.062", zr0, wi, 0.024, f"{zr1} - {zr0}", wood)
    c.box("Travessa traseira do assento", xa, f"{yk} + 0.004", zr0, wi, 0.024, f"{zr1} - {zr0}", wood)
    for i in range(5):
        c.box(f"Percinta do assento {i + 1}", f"{xa} + {wi}*{(i + 0.5) / 5:.3f} - 0.025", f"{yf} + 0.062", zr1, 0.05,
              f"{yk} + 0.028 - ({yf} + 0.062)", 0.003, "Borracha cinza", detail=FINE)
    for i, yc in enumerate((f"{yf} + 0.2", f"{yk} - 0.1"), 1):
        c.box(f"Percinta transversal do assento {i}", xa, f"{yc} - 0.025", f"{zr1} + 0.003", wi, 0.05, 0.003, "Borracha cinza",
              detail=FINE)

    # Back frame: two raked rails between the posts and three straps.
    for name, z0, z1 in (("inferior", f"{AS} + 0.04", f"{AS} + 0.09"), ("superior", f"{H} - 0.075", f"{H} - 0.02")):
        c.profile(f"Travessa {name} do encosto", "Side", [(f"{yfr(z0)} + 0.004", z0), (f"{yfr(z0)} + 0.026", z0),
                                                          (f"{yfr(z1)} + 0.026", z1), (f"{yfr(z1)} + 0.004", z1)], xa, wi, wood)
    z0, z1 = f"{AS} + 0.04", f"{H} - 0.02"
    for i, f in enumerate((-0.3, 0, 0.3), 1):
        c.profile(f"Percinta do encosto {i}", "Side", [(f"{yfr(z0)} + 0.0005", z0), (f"{yfr(z0)} + 0.004", z0),
                                                       (f"{yfr(z1)} + 0.004", z1), (f"{yfr(z1)} + 0.0005", z1)],
                  f"{f}*{wi} - 0.025", 0.05, "Borracha cinza", detail=FINE)

    # Seat cushion: a crowned box with piping at both ends.
    def seat(m):
        y0, y1, z0, z1, r = f"{yf} + 0.035", f"{yk} + 0.02", f"{zr1} + 0.006", f"{AS} - 0.012", 0.04
        half = f"(({y1}) - ({y0}) - {2 * r})/2"
        crown = f"({half}*{half} + 0.000144)/0.024"
        rr = f"{r} + {m}"
        return [(f"{y0} + {r}", f"{z0} - ({m})"), (f"{y1} - {r}", f"{z0} - ({m})", rr), (f"{y1} + {m}", f"{z0} + {r}"),
                (f"{y1} + {m}", f"{z1} - {r}", rr), (f"{y1} - {r}", f"{z1} + {m}", f"{crown} + {m}"), (f"{y0} + {r}", f"{z1} + {m}", rr),
                (f"{y0} - ({m})", f"{z1} - {r}"), (f"{y0} - ({m})", f"{z0} + {r}", rr)]

    x0, w = f"{xa} + 0.003", f"{wi} - 0.006"
    c.profile("Almofada do assento", "Side", seat(0), x0, w, fabric, in_plan=True)
    for side, xs in (("esquerdo", f"{x0} + 0.012"), ("direito", f"{x0} + {w} - 0.017")):
        c.profile(f"Almofada do assento - vivo {side}", "Side", seat(0.004), xs, 0.005, welt, detail=FINE)

    # Back cushion: a rounded slab leaning on the back frame, tufted with six buttons.
    zb = f"{AS} - 0.01"
    hinge = (yfr(zb), zb)
    tb, lb = 0.1, f"({H} - 0.02 - ({zb}))/cos({GA})"

    def back(m):
        return tilted(hinge, GA, rrect(-m, -m, tb + m, f"{lb} + {m}", 0.035 + m))

    c.profile("Almofada do encosto", "Side", back(0), x0, w, fabric, in_plan=True)
    for side, xs in (("esquerdo", f"{x0} + 0.012"), ("direito", f"{x0} + {w} - 0.017")):
        c.profile(f"Almofada do encosto - vivo {side}", "Side", back(0.004), xs, 0.005, welt, detail=FINE)
    n = 0
    for ft in (0.36, 0.7):
        for fx in (-0.28, 0, 0.28):
            n += 1
            y, z = lift(hinge, GA, tb + 0.003, f"{ft}*{lb}")
            c.cyl_y(f"Botão do capitonê {n}", f"{fx}*{wi}", z, y, 0.011, 0.012, welt, detail=FINE)

    # A throw pillow leaning on the back cushion.
    lo = (f"{yfr(AS)} - {tb} - 0.13", f"{AS} - 0.006")
    hi = (f"{yfr(f'{AS} + 0.34')} - {tb} - 0.03", f"{AS} + 0.34")

    def lens(m):
        return [(lo[0], f"{lo[1]} - {m}", 0.36 - m / 2), (hi[0], f"{hi[1]} + {m}", 0.36 - m / 2)]

    pw = 0.4
    c.profile("Almofada decorativa", "Side", lens(0), -pw / 2, pw, "Tecido azul petróleo", in_plan=True)
    c.profile("Almofada decorativa - vivo esquerdo", "Side", lens(0.004), -pw / 2 + 0.004, 0.004, welt, detail=FINE)
    c.profile("Almofada decorativa - vivo direito", "Side", lens(0.004), pw / 2 - 0.008, 0.004, welt, detail=FINE)
    return c
