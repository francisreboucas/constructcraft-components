"""Cooktop a gás de vidro temperado: 4 bocas (60 cm) e 5 bocas com tripla chama (75 cm).

The origin is on the countertop's top face, at the middle of the cooktop:
the glass and what stands on it are above z = 0, the body that goes through
the countertop's cut-out is below it (place it with the countertop's height
as base offset). `Bocas5` (0 or 1) shows the central triple-crown burner,
its trivet and its knob; with 0 they shrink into the glass.
"""

from kit import *
from _aparelhos import num, ring_points, sphere


def build() -> Component:
    c = Component("Cooktop a gás", "furniture", "cooktop-4-bocas")
    W = c.param("Largura", 0.60)
    D = c.param("Profundidade", 0.51)
    EV = c.param("EspessuraVidro", 0.008)
    AC = c.param("AlturaCorpo", 0.05)
    B5 = c.param("Bocas5", 0, "Number")

    c.material("Vidro temperado preto", (20, 20, 23), "Glass", "Glossy", 0)
    glass, iron, alu = "Vidro temperado preto", "Ferro fundido", "Alumínio fundido"
    cap, silk = "Esmalte preto", "Branco"

    ZG0 = 0.003  # bottom of the glass, on the gasket
    ZG = f"({ZG0} + {EV})"  # top of the glass
    BW, BD = f"({W} - 0.05)", f"({D} - 0.05)"  # body under the glass (fits a cut-out of about W - 4 cm x D - 3 cm)
    K5 = f"max(0.005, {B5})"  # size of the central burner (tiny when hidden)
    Z5 = f"({ZG} - (1 - {B5})*{EV}/2)"  # its base: on the glass, or inside it when hidden
    # Hidden, the central burner and its knob shrink onto the glass's front edge (inside the glass),
    # where their plan symbols vanish into the glass outline.
    Y_EDGE = f"(-{D}/2 + 0.00015)"

    XB = f"({W}/2 - 0.15)"  # x of the side burners
    YF, YB = f"(-{D}/2 + 0.17)", f"({D}/2 - 0.13)"  # rows of burners
    YC = f"(({YF} + {YB})/2)"
    Y5 = f"({B5}*{YC} + (1 - {B5})*{Y_EDGE})"
    # name, x, y, cap radius, scale, base z, knob x
    burners = [
        ("traseira esquerda", f"-{XB}", YB, 0.035, "1", ZG, f"-0.36*{W}"),
        ("dianteira esquerda", f"-{XB}", YF, 0.045, "1", ZG, f"-0.22*{W}"),
        ("central", "0", Y5, 0.052, K5, Z5, "0"),
        ("dianteira direita", XB, YF, 0.035, "1", ZG, f"0.22*{W}"),
        ("traseira direita", XB, YB, 0.026, "1", ZG, f"0.36*{W}"),
    ]

    # --- coarse ---------------------------------------------------------------
    c.box("Vidro simplificado", f"-{W}/2", f"-{D}/2", ZG0, W, D, EV, glass, detail=COARSE, in_plan=True)
    c.box("Corpo simplificado", f"-{BW}/2", f"-{BD}/2", f"-{AC}", BW, BD, f"{AC} + {ZG0}", "Aço galvanizado", detail=COARSE)
    for name, x, y, r, k, zb, _ in burners:
        c.cyl(f"Queimador simplificado {name}", x, y, zb, f"{r + 0.014}*{k}", f"0.03*{k}", cap, detail=COARSE, in_plan=True)
        c.box(f"Trempe simplificada {name}", f"{x} - 0.095*{k}", f"{y} - 0.095*{k}", zb, f"0.19*{k}", f"0.19*{k}", f"0.004*{k}", iron, detail=COARSE)

    # --- glass top --------------------------------------------------------------
    c.profile("Mesa de vidro", "Plan", rrect(f"-{W}/2", f"-{D}/2", f"{W}/2", f"{D}/2", 0.008), ZG0, EV, glass, in_plan=True)
    for side, x in (("esquerdo", f"-{W}/2 - 0.0015"), ("direito", f"{W}/2")):
        c.box(f"Perfil lateral {side}", x, f"-{D}/2 + 0.004", f"{ZG0} - 0.001", 0.0015, f"{D} - 0.008", f"{EV} + 0.0018", "Inox escovado")
        lip = f"-{W}/2 - 0.0015" if side == "esquerdo" else f"{W}/2 - 0.0025"
        c.box(f"Perfil lateral {side} - aba superior", lip, f"-{D}/2 + 0.004", f"{ZG} + 0.0008", 0.004, f"{D} - 0.008", 0.0005, "Inox escovado", detail=FINE)
    # Gasket between the glass and the countertop.
    for name, x, y, w, d in (
        ("frontal", f"-{W}/2 + 0.012", f"-{D}/2 + 0.012", f"{W} - 0.024", 0.008),
        ("traseira", f"-{W}/2 + 0.012", f"{D}/2 - 0.02", f"{W} - 0.024", 0.008),
        ("esquerda", f"-{W}/2 + 0.012", f"-{D}/2 + 0.02", 0.008, f"{D} - 0.04"),
        ("direita", f"{W}/2 - 0.02", f"-{D}/2 + 0.02", 0.008, f"{D} - 0.04"),
    ):
        c.box(f"Vedação {name}", x, y, 0, w, d, ZG0, "Borracha")

    # --- burners ----------------------------------------------------------------
    for name, x, y, r, k, zb, _ in burners:
        def z(dz, zb=zb, k=k):
            return f"{zb} + {num(dz)}*{k}"

        def u(du, x=x, k=k):
            return f"{x} + {num(du)}*{k}"

        q = f"Queimador {name}"
        c.rev(f"{q} - base", "Front", [(x, zb), (u(r + 0.016), zb), (u(r + 0.012), z(0.008)), (u(r + 0.002), z(0.011)), (x, z(0.011))], y, x, alu)
        c.rev(f"{q} - anel de acabamento", "Front", rect(u(r + 0.016), zb, u(r + 0.021), z(0.0015)), y, x, "Inox escovado", detail=FINE)
        if name == "central":
            # Triple crown: an outer ring crown and an inner crown, each with its cap.
            ri = 0.024
            c.rev(f"{q} - difusor externo", "Front", rect(u(ri + 0.008), z(0.011), u(r - 0.002), z(0.025)), y, x, alu)
            c.rev(f"{q} - tampa externa", "Front", [(u(ri + 0.006), z(0.025)), (u(r + 0.001), z(0.025)), (u(r + 0.001), z(0.029), 0.012), (u(r - 0.008), z(0.032)),
                                                    (u(ri + 0.014), z(0.032), 0.012), (u(ri + 0.006), z(0.029))], y, x, cap, in_plan=True)
            c.rev(f"{q} - difusor interno", "Front", rect(x, z(0.011), u(ri - 0.004), z(0.027)), y, x, alu)
            c.rev(f"{q} - tampa interna", "Front", [(x, z(0.027)), (u(ri - 0.002), z(0.027)), (u(ri - 0.002), z(0.031), 0.05), (x, z(0.034))], y, x, cap, in_plan=True)
            c.rev(f"{q} - canal entre coroas", "Front", rect(u(ri - 0.004), z(0.011), u(ri + 0.008), z(0.0115)), y, x, "Aço pintado preto", detail=FINE)
            ports = [(ri - 0.004, 8, 0), (r - 0.002, 16, 11.25)]
        else:
            c.rev(f"{q} - difusor", "Front", rect(x, z(0.011), u(r - 0.002), z(0.025)), y, x, alu)
            c.rev(f"{q} - tampa", "Front", [(x, z(0.025)), (u(r + 0.001), z(0.025)), (u(r + 0.001), z(0.029), 2 * r), (x, z(0.033))], y, x, cap, in_plan=True)
            ports = [(r - 0.002, 12, 0)]
        n = 0
        for rr, count, phase in ports:
            for dx, dy in ring_points(count, rr, phase):
                n += 1
                c.box(f"{q} - saída de chama {n}", f"{x} + {num(dx)}*{k} - 0.0015*{k}", f"{y} + {num(dy)}*{k} - 0.0015*{k}", z(0.016), f"0.003*{k}", f"0.003*{k}", f"0.004*{k}",
                      "Aço pintado preto", detail=FINE)
        # Spark plug and flame-failure thermocouple beside the crown.
        c.cyl(f"{q} - vela de ignição", u(r + 0.007), f"{y} - 0.004*{k}", z(0.008), f"0.0032*{k}", f"0.014*{k}", "Louça", detail=FINE)
        c.cyl(f"{q} - eletrodo", u(r + 0.007), f"{y} - 0.004*{k}", z(0.022), f"0.0008*{k}", f"0.007*{k}", "Cromado", detail=FINE)
        c.cyl(f"{q} - termopar", f"{x} - {r + 0.007}*{k}", f"{y} + 0.004*{k}", z(0.008), f"0.0022*{k}", f"0.02*{k}", "Cromado", detail=FINE)

        # --- cast-iron trivet: a square frame on rubber feet, four fingers carry the pan
        t = f"Trempe {name}"
        hs = 0.095  # half side
        bw = 0.009  # bar width
        for i, (fx, fy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1)), 1):
            c.cyl(f"{t} - pé {i}", f"{x} + {num(fx * (hs - bw / 2))}*{k}", f"{y} + {num(fy * (hs - bw / 2))}*{k}", zb, f"0.0055*{k}", f"0.004*{k}", "Borracha", detail=FINE)
        for side, bx, by, bwid, bdep in (
            ("frontal", -hs, -hs, 2 * hs, bw), ("traseira", -hs, hs - bw, 2 * hs, bw),
            ("esquerda", -hs, -hs + bw, bw, 2 * hs - 2 * bw), ("direita", hs - bw, -hs + bw, bw, 2 * hs - 2 * bw),
        ):
            c.box(f"{t} - barra {side}", f"{x} + {num(bx)}*{k}", f"{y} + {num(by)}*{k}", z(0.004), f"{num(bwid)}*{k}", f"{num(bdep)}*{k}", f"0.011*{k}", iron)
        tip = r + 0.012  # the fingers stop short of the cap
        out = hs - bw / 2
        for side, sgn in (("esquerda", -1), ("direita", 1)):
            a, b = sgn * out, sgn * tip
            c.profile(f"{t} - garra {side}", "Front", [(u(a), z(0.004)), (u(b), z(0.026)), (u(b), z(0.042)), (u(a), z(0.042))] if sgn < 0 else
                      [(u(b), z(0.026)), (u(a), z(0.004)), (u(a), z(0.042)), (u(b), z(0.042))],
                      f"{y} - 0.004*{k}", f"0.008*{k}", iron)
        for side, sgn in (("frontal", -1), ("traseira", 1)):
            a, b = sgn * out, sgn * tip
            pts = [(f"{y} + {num(a)}*{k}", z(0.004)), (f"{y} + {num(b)}*{k}", z(0.026)), (f"{y} + {num(b)}*{k}", z(0.042)), (f"{y} + {num(a)}*{k}", z(0.042))]
            c.profile(f"{t} - garra {side}", "Side", pts if sgn < 0 else pts[::-1], f"{x} - 0.004*{k}", f"0.008*{k}", iron)

    # --- knobs along the front edge, with their silk-screen marks ---------------
    YK0 = f"(-{D}/2 + 0.042)"
    # where each knob's burner sits on the little layout icon
    icon = {"traseira esquerda": (-1, 1), "dianteira esquerda": (-1, -1), "central": (0, 0), "dianteira direita": (1, -1), "traseira direita": (1, 1)}
    for name, _, _, _, k, zb, kx in burners:
        YK = f"({B5}*{YK0} + (1 - {B5})*{Y_EDGE})" if name == "central" else YK0

        def z(dz, zb=zb, k=k):
            return f"{zb} + {num(dz)}*{k}"

        def u(du, kx=kx, k=k):
            return f"{kx} + {num(du)}*{k}"

        b = f"Botão {name}"
        c.rev(f"{b} - canopla", "Front", [(kx, zb), (u(0.025), zb), (u(0.024), z(0.002)), (kx, z(0.002))], YK, kx, "Inox escovado", in_plan=True)
        c.rev(b, "Front", [(kx, z(0.002)), (u(0.020), z(0.002)), (u(0.0195), z(0.015)), (u(0.017), z(0.019), 0.004), (u(0.012), z(0.020)), (kx, z(0.020))],
              YK, kx, "Plástico preto")
        c.rev(f"{b} - aro cromado", "Front", rect(u(0.0195), z(0.004), u(0.0205), z(0.009)), YK, kx, "Cromado", detail=FINE)
        c.profile(f"{b} - pega", "Side", [(f"{YK} - 0.017*{k}", z(0.019)), (f"{YK} + 0.017*{k}", z(0.019)), (f"{YK} + 0.015*{k}", z(0.031), 0.03), (f"{YK} - 0.015*{k}", z(0.031))],
                  u(-0.004), f"0.008*{k}", "Plástico preto")
        c.box(f"{b} - indicador", u(-0.001), f"{YK} - 0.013*{k}", z(0.031), f"0.002*{k}", f"0.009*{k}", f"0.0004*{k}", silk, detail=FINE)
        # Silk-screen: the burner layout with this knob's burner filled, and min / max flame marks.
        ix, iy = icon[name]
        cy = f"{YK} + 0.034*{k}"
        dots = [(-1, -1), (1, -1), (1, 1), (-1, 1)] + ([(0, 0)] if name == "central" else [])
        for jx, jy in dots:
            s = 0.003 if (jx, jy) == (ix, iy) else 0.0018  # the knob's own burner is the bigger dot
            c.box(f"{b} - serigrafia {jx + 2}{jy + 2}", u(jx * 0.0045 - s / 2), f"{cy} + {num(jy * 0.0045 - s / 2)}*{k}", zb,
                  f"{s}*{k}", f"{s}*{k}", f"0.0003*{k}", silk, detail=FINE)
        for j, (dx, dy) in enumerate(((-0.026, 0.008), (0.026, 0.008)), 1):
            c.box(f"{b} - marca de chama {j}", u(dx - 0.001), f"{YK} + {dy}*{k}", zb, f"0.002*{k}", f"0.005*{k}", f"0.0003*{k}", silk, detail=FINE)

    # --- body under the countertop ----------------------------------------------
    zb0 = f"(-{AC})"
    galv = "Aço galvanizado"
    c.box("Corpo - bandeja", f"-{BW}/2", f"-{BD}/2", zb0, BW, BD, f"{AC} + {ZG0}", galv)
    c.box("Corpo - friso de reforço", f"-{BW}/2 + 0.03", f"-{BD}/2 + 0.03", f"{zb0} - 0.003", f"{BW} - 0.06", f"{BD} - 0.06", 0.003, galv, detail=FINE)
    for i, (fx, fy) in enumerate(((-0.4, -0.4), (0, -0.4), (0.4, -0.4), (-0.4, 0.4), (0, 0.4), (0.4, 0.4)), 1):
        c.cyl(f"Corpo - parafuso {i}", f"{fx}*{BW}", f"{fy}*{BD}", f"{zb0} - 0.0045", 0.004, 0.0015, "Cromado", detail=FINE)
    c.box("Etiqueta de identificação", f"-0.3*{BW}", f"-0.05", f"{zb0} - 0.0035", f"0.2*{BW}", 0.06, 0.0005, "Alumínio anodizado", detail=FINE)
    # Fixing clamps on the sides (they grip the countertop from below).
    for side, x, sgn in (("esquerdo", f"-{BW}/2", -1), ("direito", f"{BW}/2", 1)):
        for j, fy in enumerate((-0.3, 0.3), 1):
            x0 = f"{x} - 0.002" if sgn < 0 else x
            c.box(f"Grampo de fixação {side} {j}", x0, f"{fy}*{BD} - 0.015", f"-0.035", 0.002, 0.03, 0.03, galv)
            xl = f"{x} - 0.018" if sgn < 0 else x
            c.box(f"Grampo de fixação {side} {j} - garra", xl, f"{fy}*{BD} - 0.015", -0.008, 0.018, 0.03, 0.002, galv, detail=FINE)
            c.cyl_x(f"Grampo de fixação {side} {j} - parafuso", f"{fy}*{BD}", -0.022, f"{x} - 0.006" if sgn < 0 else f"{x} + 0.002", 0.0035, 0.004, "Cromado", detail=FINE)
    # Gas inlet: a ½" brass elbow out of the right side, at the back.
    GX, GY, GZ = f"({BW}/2)", f"({BD}/2 - 0.05)", f"(-{AC}/2)"
    c.cyl_x("Entrada de gás - tubo", GY, GZ, GX, 0.0085, 0.03, "Latão")
    sphere(c, "Entrada de gás - cotovelo", f"{GX} + 0.03", GY, GZ, 0.0085, "Latão", detail=FULL)
    c.cyl("Entrada de gás - descida", f"{GX} + 0.03", GY, f"{GZ} - 0.03", 0.0085, 0.03, "Latão")
    c.cyl("Entrada de gás - sextavado", f"{GX} + 0.03", GY, f"{GZ} - 0.042", 0.012, 0.012, "Latão", detail=FINE)
    c.cyl("Entrada de gás - rosca", f"{GX} + 0.03", GY, f"{GZ} - 0.054", 0.0095, 0.012, "Latão", detail=FINE)
    c.cyl_x("Entrada de gás - flange", GY, GZ, f"{GX}", 0.014, 0.003, "Latão", detail=FINE)
    # Ignition module and its cable.
    MX, MY = f"(-{BW}/2 + 0.07)", f"({BD}/2 - 0.09)"
    c.box("Módulo de ignição", f"{MX} - 0.035", f"{MY} - 0.025", f"{zb0} - 0.022", 0.07, 0.05, 0.022, "Plástico preto")
    c.box("Módulo de ignição - etiqueta", f"{MX} - 0.02", f"{MY} - 0.0255", f"{zb0} - 0.016", 0.04, 0.0005, 0.01, "Branco", detail=FINE)
    c.cyl_y("Cabo de alimentação", MX, f"{zb0} - 0.011", f"{MY} + 0.025", 0.003, 0.08, "Borracha", detail=FINE)
    c.box("Cabo de alimentação - plugue", f"{MX} - 0.017", f"{MY} + 0.105", f"{zb0} - 0.029", 0.034, 0.022, 0.034, "Plástico preto", detail=FINE)
    for i, dx in enumerate((-0.0095, 0, 0.0095), 1):
        c.cyl_y(f"Cabo de alimentação - pino {i}", f"{MX} + {dx}", f"{zb0} - 0.012", f"{MY} + 0.127", 0.002, 0.016, "Latão", detail=FINE)

    c.preview_size = (0.6, 0.51, 0.12)
    c.preview_base = -0.07
    c.type("Cooktop 4 bocas 60 cm", "Cooktop a gás de vidro temperado preto, 4 bocas (1 rápida, 2 semirrápidas, 1 auxiliar), 60 x 51 cm, recorte de 56 x 48 cm; trempes de ferro fundido, acendimento automático")
    c.type("Cooktop 5 bocas 75 cm", "Cooktop a gás de vidro temperado preto, 5 bocas com tripla chama central, 75 x 51 cm, recorte de 71 x 48 cm; trempes de ferro fundido, acendimento automático",
           Largura=0.75, Bocas5=1)
    return c
