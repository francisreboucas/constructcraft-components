"""Mesa de reunião: a top with rounded corners on two steel T-legs joined by a beam, with a flip-top power box."""

from kit import *
from _escritorio import declare, t_leg


def build():
    c = Component("Mesa de reunião", "furniture", "mesa-reuniao")
    W = c.param("Largura", 2.4)
    D = c.param("Profundidade", 1.1)
    H = c.param("Altura", 0.74)
    desc = ("Mesa de reunião de escritório: tampo de melamina com cantos arredondados e fita de borda, dois pés de aço em T "
            "ligados por viga, calha para cabos e caixa de tomadas com tampa basculante no centro do tampo")
    c.type("Mesa de reunião 180x90 (6 lugares)", desc, Largura=1.8, Profundidade=0.9)
    c.type("Mesa de reunião 240x110 (8 lugares)", desc)
    c.type("Mesa de reunião 300x120 (10 lugares)", desc, Largura=3.0, Profundidade=1.2)
    declare(c, "Melamina carvalho")

    top, steel = "Melamina carvalho", "Aço pintado preto"
    tt = 0.03
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{D}/2", f"{D}/2"
    zu = f"{H} - {tt}"
    r = 0.12

    c.box("Tampo simplificado", xl, yf, zu, W, D, tt, top, detail=COARSE, in_plan=True)
    lx = f"{W}/2 - 0.32"
    for n, s in enumerate(("-", ""), 1):
        c.box(f"Pé simplificado {n}", f"{s}({lx}) - 0.03", f"{yf} + 0.15", 0, 0.06, f"{D} - 0.3", zu, steel, detail=COARSE)

    # Top: an edge band all round and the board inset by its thickness.
    c.profile("Fita de borda", "Plan", rrect(xl, yf, xr, yb, r), zu, tt, "Melamina grafite", in_plan=True)
    c.profile("Tampo", "Plan", rrect(f"{xl} + 0.002", f"{yf} + 0.002", f"{xr} - 0.002", f"{yb} - 0.002", r - 0.002), f"{zu} + 0.0005",
              f"{tt} - 0.0002", top, detail=FINE)
    declare(c, "Melamina grafite")

    # Two T-legs and a beam between the columns.
    for name, s in (("esquerdo", "-"), ("direito", "")):
        t_leg(c, f"Pé {name}", f"{s}({lx})", f"{yf} + 0.15", f"{yb} - 0.15", zu, steel, foot=0.08, col=(0.05, 0.1))
    c.box("Viga de ligação", f"-({lx}) + 0.025", "-0.02", f"{zu} - 0.11", f"2*({lx}) - 0.05", 0.04, 0.08, steel)

    # Cable tray hanging from the beam, under the power box.
    t = 0.0015
    c.profile("Calha para cabos", "Side", [(-0.12, f"{zu} - 0.16"), (0.12, f"{zu} - 0.16"), (0.12, f"{zu} - 0.11"), (f"0.12 - {t}", f"{zu} - 0.11"),
                                           (f"0.12 - {t}", f"{zu} - 0.16 + {t}"), (f"-0.12 + {t}", f"{zu} - 0.16 + {t}"),
                                           (f"-0.12 + {t}", f"{zu} - 0.11"), (-0.12, f"{zu} - 0.11")], "-0.45", 0.9, steel)

    # Flip-top power box at the centre: an aluminium frame flush with the top, a lid and the sockets below.
    bw, bd = 0.32, 0.13
    c.box("Caixa de tomadas - moldura", -bw / 2, -bd / 2, f"{H} - 0.001", bw, bd, 0.004, "Alumínio anodizado")
    c.box("Caixa de tomadas - tampa", -bw / 2 + 0.008, -bd / 2 + 0.008, f"{H} + 0.003", bw - 0.016, bd - 0.016, 0.002,
          "Alumínio anodizado", detail=FINE)
    c.box("Caixa de tomadas - fenda da tampa", -bw / 2 + 0.03, -bd / 2 + 0.008, f"{H} + 0.0045", bw - 0.06, 0.008, 0.001, "Plástico preto",
          detail=FINE)
    c.box("Caixa de tomadas - corpo", -bw / 2 + 0.01, -bd / 2 + 0.01, f"{zu} - 0.09", bw - 0.02, bd - 0.02, 0.09, "Plástico preto")
    return c
