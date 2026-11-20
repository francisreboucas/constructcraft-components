"""Estação de trabalho: an office desk on steel T-legs, with a cable tray, a modesty panel and a fabric privacy screen."""

from kit import *
from _escritorio import declare, grommet, t_leg, top_side


def build():
    c = Component("Estação de trabalho", "furniture", "estacao-trabalho")
    W = c.param("Largura", 1.4)
    D = c.param("Profundidade", 0.7)
    H = c.param("Altura", 0.74)
    S = c.param("AlturaDivisoria", 0.35)
    desc = ("Estação de trabalho de escritório: tampo de melamina com borda frontal arredondada, pés de aço em T com sapatas "
            "niveladoras, calha para cabos, painel frontal de chapa perfurada e divisória de tecido sobre o tampo")
    c.type("Estação de trabalho 120x60", desc, Largura=1.2, Profundidade=0.6)
    c.type("Estação de trabalho 140x70", desc)
    c.type("Estação de trabalho 160x70", desc, Largura=1.6)
    declare(c, "Melamina carvalho", "Tecido de divisória")

    top, steel = "Melamina carvalho", "Aço pintado preto"
    tt = 0.025
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{D}/2", f"{D}/2"
    zu = f"{H} - {tt}"

    c.box("Tampo simplificado", xl, yf, zu, W, D, tt, top, detail=COARSE, in_plan=True)
    for n, x in enumerate((f"{xl} + 0.04", f"{xr} - 0.1"), 1):
        c.box(f"Pé simplificado {n}", x, f"{yf} + 0.05", 0, 0.06, f"{D} - 0.1", zu, steel, detail=COARSE)
    c.box("Divisória simplificada", f"{xl} + 0.03", f"{yb} - 0.035", H, f"{W} - 0.06", 0.025, S, "Tecido de divisória", detail=COARSE)

    top_side(c, "Tampo", xl, W, yf, yb, zu, H, top)
    c.box("Fita de borda traseira", xl, f"{yb} - 0.001", zu, W, 0.0015, tt, "Plástico preto", detail=FINE)
    grommet(c, f"{xl} + 0.18", f"{yb} - 0.09", H)
    grommet_x = f"{xr} - 0.18"
    c.rev("Passa-cabos direito - aro", "Front", [(f"{grommet_x} + 0.024", H), (f"{grommet_x} + 0.034", H),
                                                  (f"{grommet_x} + 0.034", f"{H} + 0.002"), (f"{grommet_x} + 0.031", f"{H} + 0.0035"),
                                                  (f"{grommet_x} + 0.024", f"{H} + 0.0035")], f"{yb} - 0.09", grommet_x, "Plástico preto",
          detail=FINE)
    c.cyl("Passa-cabos direito - tampa", grommet_x, f"{yb} - 0.09", H, 0.024, 0.002, "Plástico cinza", detail=FINE)

    # Legs at both ends, a beam between the columns.
    lx = f"{W}/2 - 0.07"
    t_leg(c, "Pé esquerdo", f"-({lx})", f"{yf} + 0.04", f"{yb} - 0.04", zu, steel)
    t_leg(c, "Pé direito", lx, f"{yf} + 0.04", f"{yb} - 0.04", zu, steel)
    c.box("Viga de ligação", f"-({lx}) + 0.02", "-0.015", f"{zu} - 0.13", f"2*({lx}) - 0.04", 0.03, 0.05, steel)

    # Cable tray under the back of the top: a U-channel of sheet steel across the span.
    t = 0.0015
    ty0, ty1, tz0, tz1 = f"{yb} - 0.2", f"{yb} - 0.06", f"{zu} - 0.11", f"{zu} - 0.02"
    c.profile("Calha para cabos", "Side", [(ty0, tz0), (ty1, tz0), (ty1, tz1), (f"{ty1} - {t}", tz1), (f"{ty1} - {t}", f"{tz0} + {t}"),
                                           (f"{ty0} + {t}", f"{tz0} + {t}"), (f"{ty0} + {t}", f"{tz0} + 0.05"), (ty0, f"{tz0} + 0.05")],
              f"-({lx}) + 0.05", f"2*({lx}) - 0.1", steel)
    for n, x in enumerate((f"-({lx}) + 0.12", f"{lx} - 0.12"), 1):
        c.box(f"Suporte da calha {n}", f"{x} - 0.015", f"{ty1} - 0.002", f"{tz1} - 0.002", 0.03, 0.04, 0.022, steel,
              detail=FINE)

    # Modesty panel: perforated sheet between the legs, set back from the front.
    c.box("Painel frontal", f"-({lx}) + 0.03", f"{yb} - 0.045", f"{zu} - 0.42", f"2*({lx}) - 0.06", 0.002, 0.38, "Tela perfurada")
    c.box("Painel frontal - dobra superior", f"-({lx}) + 0.03", f"{yb} - 0.06", f"{zu} - 0.045", f"2*({lx}) - 0.06", 0.017, 0.002, steel,
          detail=FINE)
    c.box("Painel frontal - dobra inferior", f"-({lx}) + 0.03", f"{yb} - 0.06", f"{zu} - 0.42", f"2*({lx}) - 0.06", 0.017, 0.002, steel,
          detail=FINE)

    # Privacy screen: a fabric panel in an aluminium frame on two clamps at the back edge.
    sx0, sw = f"{xl} + 0.03", f"{W} - 0.06"
    sy = f"{yb} - 0.032"
    zs = f"{H} + 0.012"
    c.box("Divisória - painel de tecido", f"{sx0} + 0.012", sy, f"{zs} + 0.012", f"{sw} - 0.024", 0.022, f"{S} - 0.024",
          "Tecido de divisória", in_plan=True)
    c.box("Divisória - perfil superior", sx0, f"{sy} - 0.002", f"{zs} + {S} - 0.012", sw, 0.026, 0.012, "Alumínio anodizado")
    c.box("Divisória - perfil inferior", sx0, f"{sy} - 0.002", zs, sw, 0.026, 0.012, "Alumínio anodizado")
    c.box("Divisória - perfil esquerdo", sx0, f"{sy} - 0.002", f"{zs} + 0.012", 0.012, 0.026, f"{S} - 0.024", "Alumínio anodizado")
    c.box("Divisória - perfil direito", f"{sx0} + {sw} - 0.012", f"{sy} - 0.002", f"{zs} + 0.012", 0.012, 0.026, f"{S} - 0.024",
          "Alumínio anodizado")
    for n, x in enumerate((f"{xl} + 0.2", f"{xr} - 0.26"), 1):
        c.box(f"Divisória - grampo {n}", x, f"{sy} - 0.006", H, 0.06, 0.006, 0.07, "Alumínio fundido")
        c.box(f"Divisória - grampo {n} traseiro", x, yb, f"{zu} - 0.036", 0.06, 0.006, f"{tt} + 0.106", "Alumínio fundido")
        c.box(f"Divisória - grampo {n} superior", x, f"{sy} - 0.006", f"{H} + 0.064", 0.06, 0.044, 0.006,
              "Alumínio fundido", detail=FINE)
        c.box(f"Divisória - grampo {n} inferior", x, f"{yb} - 0.06", f"{zu} - 0.036", 0.06, 0.066, 0.006, "Alumínio fundido",
              detail=FINE)
        c.cyl(f"Divisória - manípulo {n}", f"{x} + 0.03", f"{yb} - 0.03", f"{zu} - 0.052", 0.012, 0.016, "Plástico preto", detail=FINE)
    return c
