"""Caixa de inspeção de esgoto enterrada: laje de fundo, paredes de alvenaria rebocadas por dentro, cinta de
concreto, fundo com canaleta em meia-cana e bermas inclinadas, tubos de entrada e saída, espera lateral com
tampão, tampa de concreto com alças que se levanta."""

from __future__ import annotations

import math

from louca import *


def build():
    c = Component("Caixa de inspeção", "plumbing", "caixa-inspecao", "Plumbing")
    L = c.param("Largura", 0.6)
    P = c.param("Profundidade", 0.6)
    F = c.param("Fundo", 0.6, instance=True)
    lift = c.param("AberturaTampa", 0.0, instance=True)
    c.open_pose["AberturaTampa"] = 0.35
    desc = "Caixa de inspeção de esgoto em alvenaria/concreto"
    c.type("Caixa de inspeção 60x60", desc)
    c.type("Caixa de inspeção 80x80", desc, Largura=0.8, Profundidade=0.8)
    c.preview_size = (1.2, 1.2, 0.85)
    c.preview_base = -0.75

    x0, x1, y0, y1 = f"-{L} / 2", f"{L} / 2", f"-{P} / 2", f"{P} / 2"
    W = 0.1  # wall, plaster included
    PL = 0.015  # plaster
    zf = f"(-{F})"  # the floor inside

    # --- coarse stand-ins ---
    c.box("Caixa simplificada", add(x0, -W), add(y0, -W), add(zf, -0.1), f"{L} + {2 * W}", f"{P} + {2 * W}", f"{F} + 0.1", "Concreto", COARSE, in_plan=True)
    c.box("Tampa simplificada", add(x0, -W), add(y0, -W), lift, f"{L} + {2 * W}", f"{P} + {2 * W}", 0.05, "Concreto", COARSE, in_plan=True)

    c.profile("Símbolo - abertura", "Plan", rect(x0, y0, x1, y1), 0.05, 0.001, "Concreto")
    c.plan_only("Símbolo - abertura")

    # --- base slab, brick walls plastered inside, concrete collar ---
    c.box("Laje de fundo", add(x0, -W - 0.03), add(y0, -W - 0.03), add(zf, -0.1), f"{L} + {2 * W + 0.06}", f"{P} + {2 * W + 0.06}", 0.1, "Concreto")
    zc = -0.06  # bottom of the collar
    hw = f"{F} - 0.06"
    LW = f"{L} + {2 * PL}"
    for name, x, y, w, d in (("esquerda", add(x0, -W), add(y0, -W), W - PL, f"{P} + {2 * W}"), ("direita", add(x1, PL), add(y0, -W), W - PL, f"{P} + {2 * W}"),
                             ("frontal", add(x0, -PL), add(y0, -W), LW, W - PL), ("traseira", add(x0, -PL), add(y1, PL), LW, W - PL)):
        c.box(f"Parede {name}", x, y, zf, w, d, hw, "Alvenaria")
    for name, x, y, w, d in (("esquerda", add(x0, -PL), add(y0, -PL), PL, f"{P} + {2 * PL}"), ("direita", x1, add(y0, -PL), PL, f"{P} + {2 * PL}"),
                             ("frontal", x0, add(y0, -PL), L, PL), ("traseira", x0, y1, L, PL)):
        c.box(f"Reboco {name}", x, y, zf, w, d, f"{F} - 0.002", "Reboco")
    for name, x, y, w, d in (("esquerda", add(x0, -W), add(y0, -W), W, f"{P} + {2 * W}"), ("direita", x1, add(y0, -W), W, f"{P} + {2 * W}"),
                             ("frontal", x0, add(y0, -W), L, W), ("traseira", x0, y1, L, W)):
        c.box(f"Cinta {name}", x, y, zc, w, d, 0.06, "Concreto")
    # Mortar joints on the outer faces of the brick walls.
    n = 8
    for k in range(1, n + 1):
        z = f"{p(zf)} + {p(hw)} * {e(k / (n + 1))}"
        c.box(f"Junta frontal {k}", add(x0, -W), add(y0, -W - 0.002), z, f"{L} + {2 * W}", 0.003, 0.01, "Reboco", FINE)
        c.box(f"Junta traseira {k}", add(x0, -W), add(y1, W - 0.001), z, f"{L} + {2 * W}", 0.003, 0.01, "Reboco", FINE)
        c.box(f"Junta esquerda {k}", add(x0, -W - 0.002), add(y0, -W), z, 0.003, f"{P} + {2 * W}", 0.01, "Reboco", FINE)
        c.box(f"Junta direita {k}", add(x1, W - 0.001), add(y0, -W), z, 0.003, f"{P} + {2 * W}", 0.01, "Reboco", FINE)

    # --- benching: a half-round channel from the inlet to the outlet, sloped berms to the walls ---
    rc = 0.055
    zo = add(zf, 0.1)  # axis of the outlet and of the channel
    zb = add(zf, 0.17)  # top of the berms at the walls
    channel = [(e(rc * math.cos(math.pi * k / 10)), add(zo, -rc * math.sin(math.pi * k / 10))) for k in range(11)]
    section = [(y0, zf), (y1, zf), (y1, zb), (e(rc + 0.01), add(zo, 0.012)), (e(rc), zo)] + channel[1:-1] + [(e(-rc), zo), (e(-rc - 0.01), add(zo, 0.012)), (y0, zb)]
    c.profile("Fundo com canaleta", "Side", section, x0, L, "Concreto")

    # --- pipes: inlet and outlet DN 100, a capped branch on the back wall ---
    zi = add(zf, 0.15)
    reach = 0.15
    c.cyl_x("Entrada - tubo", 0, zi, f"{x0} - {W} - {reach}", 0.05, f"{W} + {reach}", "PVC", in_plan=True)
    c.cyl_x("Entrada - luva", 0, zi, f"{x0} - {W} - {reach}", 0.058, 0.07, "PVC", FINE)
    c.cyl_x("Entrada - argamassa", 0, zi, f"{x0} - {W} - 0.012", 0.07, 0.012, "Reboco", FINE)
    c.connector("Entrada", "Sanitary", f"{x0} - {W} - {reach}", 0, zi, "Left", 0.1)
    c.cyl_x("Saída - tubo", 0, zo, x1, 0.05, f"{W} + {reach}", "PVC", in_plan=True)
    c.cyl_x("Saída - luva", 0, zo, f"{x1} + {W} + {reach} - 0.07", 0.058, 0.07, "PVC", FINE)
    c.cyl_x("Saída - argamassa", 0, zo, add(x1, W), 0.07, 0.012, "Reboco", FINE)
    c.connector("Saída", "Sanitary", f"{x1} + {W} + {reach}", 0, zo, "Right", 0.1)
    ze = add(zf, 0.25)
    c.cyl_y("Espera lateral - tubo", 0, ze, add(y1, -PL), 0.05, f"{W} + 0.12", "PVC", in_plan=True)
    c.cyl_y("Espera lateral - tampão", 0, ze, f"{y1} + {W} + 0.1", 0.058, 0.035, "PVC", FINE)
    c.cyl_y("Espera lateral - argamassa", 0, ze, add(y1, W), 0.07, 0.012, "Reboco", FINE)

    # The pipes' bores, seen from inside the chamber.
    c.cyl_x("Entrada - boca", 0, zi, add(x0, -0.001), 0.045, 0.002, "Plástico preto", FINE)
    c.cyl_x("Saída - boca", 0, zo, add(x1, -0.001), 0.045, 0.002, "Plástico preto", FINE)
    c.cyl_y("Espera lateral - boca", 0, ze, add(y1, -PL - 0.001), 0.045, 0.002, "Plástico preto", FINE)

    # --- lid: a precast concrete slab with two recessed lifting handles, lifting off ---
    def zl(d):
        return add(lift, d)

    LX, LY = f"{L} + {2 * W}", f"{P} + {2 * W}"
    c.box("Tampa", add(x0, -W), add(y0, -W), zl(0.004), LX, LY, 0.046, "Concreto", in_plan=True)
    c.box("Tampa - assentamento", add(x0, -W + 0.01), add(y0, -W + 0.01), zl(0), f"{LX} - 0.02", f"{LY} - 0.02", 0.004, "Reboco", FINE)
    for name, x, y, w, d in (("frontal", add(x0, -W), add(y0, -W), LX, 0.008), ("traseira", add(x0, -W), add(y1, W - 0.008), LX, 0.008),
                             ("esquerda", add(x0, -W), add(y0, -W), 0.008, LY), ("direita", add(x1, W - 0.008), add(y0, -W), 0.008, LY)):
        c.box(f"Tampa - cantoneira {name}", x, y, zl(0.004), w, d, 0.046, "Aço galvanizado", FINE)
    for side, sx in (("esquerda", -1), ("direita", 1)):
        xh = mul(L, 0.3 * sx)
        c.box(f"Tampa - rebaixo da alça {side}", add(xh, -0.06), -0.035, zl(0.0495), 0.12, 0.07, 0.001, "Aço pintado preto", FINE)
        tube(c, f"Tampa - alça {side}", "Plan", [(add(xh, -0.05), 0.03), (add(xh, -0.05), -0.02), (add(xh, 0.05), -0.02), (add(xh, 0.05), 0.03)],
             zl(0.054), 0.005, "Aço", n=8)
    return c
