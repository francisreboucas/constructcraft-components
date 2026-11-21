"""Balcão de atendimento: a reception counter with a raised transaction ledge, a work desk behind it and a lowered
accessible section at the right (NBR 9050: top at 0,85 m, free knee space 0,73 m high, 0,90 m wide).

The customer side is -Y, the attendant behind (+Y); centred on the origin.
"""

from kit import *
from _escritorio import declare


def build():
    c = Component("Balcão de atendimento", "furniture", "balcao-atendimento")
    W = c.param("Largura", 2.0)
    D = c.param("Profundidade", 0.7)
    desc = ("Balcão de atendimento de melamina com tampo de transação a 1,10 m, mesa de trabalho a 0,75 m atrás e trecho "
            "rebaixado acessível de 0,90 m com tampo a 0,85 m e vão livre para as pernas (NBR 9050)")
    c.type("Balcão de atendimento 2,0 m", desc)
    c.type("Balcão de atendimento 2,6 m", desc, Largura=2.6)
    c.type("Balcão de atendimento 3,2 m", desc, Largura=3.2)
    declare(c, "Melamina carvalho", "Melamina grafite")
    c.preview_size = (2.2, 0.8, 1.2)

    wood, dark = "Melamina carvalho", "Melamina grafite"
    t = 0.025
    xl, xr = f"-{W}/2", f"{W}/2"
    yf, yb = f"-{D}/2", f"{D}/2"
    xa = f"{xr} - 0.9"  # start of the accessible section
    c.box("Balcão simplificado", xl, yf, 0, W, D, 1.1, wood, detail=COARSE, in_plan=True)
    # The high part: front panel to the transaction ledge, ends, the desk behind.
    c.box("Painel frontal", xl, f"{yf} + 0.1", 0.05, f"{W} - 0.9", t, 1.03, dark)
    c.box("Rodapé", f"{xl} + 0.02", f"{yf} + 0.12", 0, f"{xa} - ({xl}) - 0.04", 0.02, 0.05, "Aço pintado preto")
    c.box("Tampo de transação", xl, yf, 1.08, f"{W} - 0.9", 0.32, 0.03, wood, in_plan=True)
    c.box("Apoio do tampo de transação", xl, f"{yf} + 0.1", 1.04, f"{W} - 0.9", 0.22, 0.04, dark)
    c.box("Lateral esquerda", xl, f"{yf} + 0.1", 0, t, f"{D} - 0.1", 1.08, wood)
    c.box("Mesa de trabalho", xl, f"{yf} + 0.12", 0.73, f"{W} - 0.9", f"{D} - 0.12", t, wood, in_plan=True)
    c.box("Gaveteiro", f"{xl} + {t}", f"{yb} - 0.5", 0, 0.42, 0.48, 0.72, wood)
    for k in range(3):
        c.box(f"Gaveta {k + 1}", f"{xl} + {t} + 0.01", f"{yb} - 0.505", 0.05 + 0.22 * k, 0.4, 0.005, 0.2, dark, detail=FINE)
    # The accessible section: lower top on two side panels, free underneath, an open front.
    c.box("Divisória do trecho acessível", f"{xa} - {t}", f"{yf} + 0.1", 0, t, f"{D} - 0.1", 1.08, wood)
    c.box("Lateral direita", f"{xr} - {t}", yf, 0, t, D, 0.83, wood)
    c.box("Tampo acessível", xa, yf, 0.83, 0.9, D, 0.03, wood, in_plan=True)
    c.box("Saia do tampo acessível", xa, f"{yb} - 0.03", 0.73, 0.9 - t, 0.02, 0.1, dark)
    c.box("Faixa do símbolo de acesso", f"{xa} + 0.35", f"{yf} - 0.001", 0.84, 0.2, 0.001, 0.015, "Plástico azul", detail=FINE)
    return c
