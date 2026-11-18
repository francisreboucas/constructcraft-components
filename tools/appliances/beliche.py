"""Beliche: bunk bed for two single mattresses, posts and rails, slatted decks, guard rails, a ladder and made-up bedding."""

from kit import *
from _mobilia import blend


def cover(xo, xi, zb, zi, zo, r):
    """Side outline of a bed cover: over the top (zi..zo) and down both sides to zb, between xi and xo (about y = 0)."""
    return [(f"-({xo})", zb), (f"-({xi})", zb), (f"-({xi})", zi), (xi, zi), (xi, zb), (xo, zb), (xo, f"{zo} - {r}", r),
            (f"{xo} - {r}", zo), (f"-({xo}) + {r}", zo, r), (f"-({xo})", f"{zo} - {r}")]


def build():
    c = Component("Beliche", "furniture", "beliche")
    L = c.param("Largura", 0.88)  # mattress, across the bed (y)
    C = c.param("Comprimento", 1.88)  # mattress, along the bed (x)
    H = c.param("Altura", 1.65)
    AC = c.param("AlturaColchao", 0.14)
    c.type("Beliche solteiro 88x188", "Beliche para dois colchões de solteiro 88 x 188 cm")
    c.type("Beliche solteiro 78x188", "Beliche estreito para dois colchões de solteiro 78 x 188 cm", Largura=0.78)
    c.preview_size = (2.03, 1.08, 1.65)
    c.material("Colchão", (232, 228, 218), "Generic", "Matte")
    c.material("Roupa de cama branca", (243, 241, 235), "Generic", "Matte")
    c.material("Tecido cinza", (150, 152, 156), "Generic", "Matte")
    c.material("Tecido mostarda", (201, 152, 58), "Generic", "Matte")
    c.material("Tecido azul petróleo", (48, 92, 110), "Generic", "Matte")
    c.material("Feltro", (70, 66, 60), "Generic", "Matte")

    wood, slat, bolt = "Madeira", "Madeira clara", "Aço pintado preto"
    ps = 0.065  # posts
    rt = 0.025  # rails
    xi, yi = f"({C}/2 + 0.005)", f"({L}/2 + 0.005)"  # inner faces of the frame
    decks = (("inferior", "0.28", "Tecido azul petróleo"), ("superior", f"({H} - 0.45)", "Tecido mostarda"))
    zg0, zg1 = f"({H} - 0.09)", f"({H} - 0.035)"  # guard rails
    xc = f"({xi} - 0.33)"  # ladder's center
    ls0, ls1 = f"({xc} - 0.195)", f"({xc} + 0.165)"  # left ends of the two stiles
    ya0, ya1 = f"(-({yi} + {rt}) - 0.045)", f"(-({yi} + {rt}))"  # ladder's depth, in front of the front rails

    # Coarse stand-ins.
    for n, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        c.box(f"Coluna simplificada {n}", f"{sx}*({xi} + {ps / 2}) - {ps / 2}", f"{sy}*({yi} + {ps / 2}) - {ps / 2}", 0, ps, ps, H, wood,
              detail=COARSE, in_plan=True)
    for name, zm, _ in decks:
        c.box(f"Leito {name} simplificado", f"-{xi}", f"-({yi} + {rt})", f"{zm} - 0.08", f"2*{xi}", f"2*({yi} + {rt})", f"0.08 + {AC}",
              "Colchão", detail=COARSE, in_plan=(name == "superior"))
    c.box("Grade superior simplificada", f"-{xi}", f"{yi}", f"{decks[1][1]} + {AC}", f"2*{xi}", rt, f"{zg1} - {decks[1][1]} - {AC}", wood,
          detail=COARSE)
    c.box("Escada simplificada", ls0, ya0, 0, f"{ls1} + 0.03 - {ls0}", 0.045, zg1, wood, detail=COARSE, in_plan=True)

    # Posts with chamfered caps and felt glides.
    for (sx, sy), where in {(-1, -1): "frontal da cabeceira", (1, -1): "frontal dos pés", (-1, 1): "traseira da cabeceira",
                            (1, 1): "traseira dos pés"}.items():
        x0 = f"{xi}" if sx > 0 else f"-({xi} + {ps})"
        y0 = f"{yi}" if sy > 0 else f"-({yi} + {ps})"
        c.box(f"Coluna {where}", x0, y0, 0.004, ps, ps, f"{H} - 0.024", wood, in_plan=True)
        blend(c, f"Capitel da coluna {where}", "Plan", rect(x0, y0, f"{x0} + {ps}", f"{y0} + {ps}"),
              rect(f"{x0} + 0.016", f"{y0} + 0.016", f"{x0} + {ps - 0.016}", f"{y0} + {ps - 0.016}"), f"{H} - 0.02", 0.02, wood)
        c.box(f"Feltro da coluna {where}", f"{x0} + 0.008", f"{y0} + 0.008", 0, ps - 0.016, ps - 0.016, 0.004, "Feltro", detail=FINE)

    def bolts(tag, z):
        """Bolt heads where the rails at the height z meet the posts: on the posts' end faces and side faces."""
        for sx, ex in ((-1, "cabeceira"), (1, "pés")):
            for sy, ey in ((-1, "frontal"), (1, "traseira")):
                c.cyl_x(f"Parafuso {tag} - longarina {ey} - lado dos {ex}", f"{sy}*({yi} + {rt / 2})", z,
                        f"{sx}*({xi} + {ps})" if sx > 0 else f"-({xi} + {ps}) - 0.003", 0.009, 0.003, bolt, detail=FINE)
                c.cyl_y(f"Parafuso {tag} - travessa dos {ex} - lado {ey}", f"{sx}*({xi} + {rt / 2})", z,
                        f"{sy}*({yi} + {ps})" if sy > 0 else f"-({yi} + {ps}) - 0.003", 0.009, 0.003, bolt, detail=FINE)

    for name, zm, duvet in decks:
        top = name == "superior"
        zr = f"({zm} - 0.08)"
        # Rails, ledgers and slats.
        c.box(f"Longarina frontal {name}", f"-{xi}", f"-({yi} + {rt})", zr, f"2*{xi}", rt, 0.14, wood, in_plan=top)
        c.box(f"Longarina traseira {name}", f"-{xi}", yi, zr, f"2*{xi}", rt, 0.14, wood, in_plan=top)
        c.box(f"Travessa da cabeceira {name}", f"-({xi} + {rt})", f"-{yi}", zr, rt, f"2*{yi}", 0.14, wood, in_plan=top)
        c.box(f"Travessa dos pés {name}", xi, f"-{yi}", zr, rt, f"2*{yi}", 0.14, wood, in_plan=top)
        c.box(f"Sarrafo de apoio frontal {name}", f"-{xi}", f"-{yi}", f"{zm} - 0.043", f"2*{xi}", 0.022, 0.025, wood, detail=FINE)
        c.box(f"Sarrafo de apoio traseiro {name}", f"-{xi}", f"{yi} - 0.022", f"{zm} - 0.043", f"2*{xi}", 0.022, 0.025, wood, detail=FINE)
        ns = 13
        for i in range(ns):
            c.box(f"Ripa do estrado {name} {i + 1}", f"-{xi} + 2*{xi}*{(i + 0.5) / ns:.5f} - 0.035", f"-{yi} + 0.002", f"{zm} - 0.018", 0.07,
                  f"2*{yi} - 0.004", 0.018, slat, detail=FINE)
        bolts(name, f"{zm} - 0.02")

        # Mattress with piping, fitted sheet.
        mx, my = f"({C}/2)", f"({L}/2)"
        c.profile(f"Colchão {name}", "Plan", rrect(f"-{mx}", f"-{my}", mx, my, 0.06), zm, AC, "Colchão", in_plan=top)
        for k, z in (("inferior", f"{zm} + 0.01"), ("superior", f"{zm} + {AC} - 0.017")):
            c.profile(f"Vivo {k} do colchão {name}", "Plan", rrect(f"-{mx} - 0.003", f"-{my} - 0.003", f"{mx} + 0.003", f"{my} + 0.003", 0.063),
                      z, 0.007, "Tecido cinza", detail=FINE)
        zs = f"({zm} + {AC} + 0.003)"  # top of the sheet
        c.profile(f"Lençol de elástico {name}", "Plan", rrect(f"-{mx} - 0.002", f"-{my} - 0.002", f"{mx} + 0.002", f"{my} + 0.002", 0.062),
                  f"{zm} + 0.45*{AC}", f"0.55*{AC} + 0.003", "Roupa de cama branca")

        # Duvet over the foot, the sheet folded over it, a throw across the foot.
        xo, xin = f"{L}/2 + 0.014", f"{L}/2 - 0.0075"
        xd = f"(-{mx} + 0.62)"  # where the duvet ends, towards the pillow
        zb = f"{zm} + 0.065"
        c.profile(f"Edredom {name}", "Side", cover(xo, xin, zb, zs, f"{zs} + 0.035", 0.03), xd, f"{mx} - {xd} + 0.0075", duvet, in_plan=top)
        c.box(f"Edredom {name} - queda dos pés", mx, f"-({xin})", zb, 0.0075, f"2*({xin})", f"{zs} - ({zb})", duvet)
        c.profile(f"Dobra do lençol {name}", "Side", cover(f"{xo} + 0.003", xin, f"{zm} + 0.3*{AC}", zs, f"{zs} + 0.041", 0.03), f"{xd} - 0.02",
                  0.2, "Roupa de cama branca")
        c.profile(f"Manta dos pés {name}", "Side", cover(f"{xo} + 0.005", xin, f"{zm} + 0.5*{AC}", zs, f"{zs} + 0.045", 0.03), f"{mx} - 0.5",
                  0.36, "Tecido cinza")

        # Pillow at the head (-x), with two crossed crowns.
        pw, pd = f"min(0.6, {L} - 0.16)", 0.4
        cx = f"(-{mx} + 0.06 + {pd / 2})"
        z0 = zs
        c.profile(f"Travesseiro {name}", "Plan", rrect(f"{cx} - {pd / 2}", f"-{pw}/2", f"{cx} + {pd / 2}", f"{pw}/2", 0.07), z0, 0.05,
                  "Roupa de cama branca", in_plan=top)
        c.profile(f"Travesseiro {name} - vivo", "Plan", rrect(f"{cx} - {pd / 2 + 0.004}", f"-{pw}/2 - 0.004", f"{cx} + {pd / 2 + 0.004}",
                                                              f"{pw}/2 + 0.004", 0.074), f"{z0} + 0.023", 0.005, "Roupa de cama branca",
                  detail=FINE)
        sag = 0.075
        for plane, half, across, mid, start in (("Side", f"({pw}/2 - 0.012)", pd - 0.1, 0, f"{cx} - {(pd - 0.1) / 2}"),
                                                ("Front", f"({pd / 2 - 0.012})", f"{pw} - 0.1", cx, f"-({pw} - 0.1)/2")):
            radius = f"({half}*{half} + {sag * sag})/{2 * sag}"
            c.profile(f"Travesseiro {name} - volume {'transversal' if plane == 'Side' else 'longitudinal'}", plane,
                      [(f"{mid} - {half}", f"{z0} + 0.045"), (f"{mid} + {half}", f"{z0} + 0.045", radius)], start, across,
                      "Roupa de cama branca")

    zu = decks[1][1]
    # Lower bunk's head and foot boards.
    for name, x0 in (("cabeceira", f"-({xi} + 0.022)"), ("pés", f"{xi} + 0.004")):
        c.box(f"Painel da {name} inferior", x0, f"-{yi}", "0.34", 0.018, f"2*{yi}", 0.3, wood)
    # Upper guard rails: full length at the back, up to the ladder at the front, and at both ends; round spindles.
    c.box("Grade traseira - corrimão", f"-{xi}", yi, zg0, f"2*{xi}", rt, f"{zg1} - {zg0}", wood, in_plan=True)
    c.box("Grade frontal - corrimão", f"-{xi}", f"-({yi} + {rt})", zg0, f"{ls0} + {xi}", rt, f"{zg1} - {zg0}", wood, in_plan=True)
    c.box("Grade da cabeceira - corrimão", f"-({xi} + {rt})", f"-{yi}", zg0, rt, f"2*{yi}", f"{zg1} - {zg0}", wood)
    c.box("Grade dos pés - corrimão", xi, f"-{yi}", zg0, rt, f"2*{yi}", f"{zg1} - {zg0}", wood)
    zs0 = f"{zu} + 0.06"
    hs = f"{zg0} - ({zs0})"
    for j in range(5):
        c.cyl(f"Grade traseira - balaústre {j + 1}", f"-{xi} + 2*{xi}*{(j + 1) / 6:.5f}", f"{yi} + {rt / 2}", zs0, 0.011, hs, wood)
    for j in range(3):
        c.cyl(f"Grade frontal - balaústre {j + 1}", f"-{xi} + ({ls0} + {xi})*{(j + 1) / 4:.5f}", f"-({yi} + {rt / 2})", zs0, 0.011, hs, wood)
    for name, sx in (("cabeceira", -1), ("pés", 1)):
        for j in range(3):
            c.cyl(f"Grade da {name} - balaústre {j + 1}", f"{sx}*({xi} + {rt / 2})", f"-{yi} + 2*{yi}*{(j + 1) / 4:.5f}", zs0, 0.011, hs, wood)
    bolts("da grade", f"({zg0} + {zg1})/2")

    # Ladder: two stiles hooked on the upper rail, four rungs.
    for name, x0 in (("esquerdo", ls0), ("direito", ls1)):
        c.box(f"Escada - banzo {name}", x0, ya0, 0.004, 0.03, 0.045, f"{zg1} - 0.004", wood, in_plan=True)
        c.box(f"Escada - feltro do banzo {name}", f"{x0} + 0.004", f"{ya0} + 0.004", 0, 0.022, 0.037, 0.004, "Feltro", detail=FINE)
        c.box(f"Escada - gancho {name}", f"{x0} - 0.005", f"{ya1} - 0.002", f"{zu} + 0.06", 0.04, f"{rt} + 0.004", 0.004, bolt, detail=FINE)
        c.box(f"Escada - aba do gancho {name}", f"{x0} - 0.005", f"-{yi} - 0.001", f"{zu} + 0.02", 0.04, 0.003, 0.044, bolt, detail=FINE)
        c.cyl_y(f"Escada - parafuso inferior {name}", f"{x0} + 0.015", "0.25", f"{ya0} - 0.003", 0.008, 0.003, bolt, detail=FINE)
    for j in range(1, 5):
        c.cyl_x(f"Escada - degrau {j}", f"({ya0} + {ya1})/2", f"({zu} + 0.06)*{j / 5}", ls0, 0.016, f"{ls1} + 0.03 - {ls0}", wood)
    return c
