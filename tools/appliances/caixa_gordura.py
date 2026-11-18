"""Caixa de gordura de PVC enterrada: corpo cilíndrico oco com nervuras, porta-tampa, cesto de limpeza
removível com alça, entrada sobre o cesto, saída por tê sifonado (septo) e tampa com alças."""

from __future__ import annotations

import math

from louca import *

GRAY = "Plástico cinza"


def build():
    c = Component("Caixa de gordura", "plumbing", "caixa-gordura", "Plumbing")
    D = c.param("Diametro", 0.4)
    F = c.param("Fundo", 0.5, instance=True)
    lift = c.param("AberturaTampa", 0.0, instance=True)
    c.open_pose["AberturaTampa"] = 0.3
    c.type("Caixa de gordura simples Ø40", "Caixa de gordura simples (CGS), 1 cozinha")
    c.type("Caixa de gordura dupla Ø60", "Caixa de gordura dupla (CGD), até 12 cozinhas", Diametro=0.6, Fundo=0.6)
    c.preview_size = (0.8, 0.8, 0.75)
    c.preview_base = -0.62

    R = f"({D} / 2)"  # inner radius
    t = 0.008  # wall
    RO = add(R, t)
    RC = add(R, 0.05)  # the collar and the lid
    zb = f"(-{F})"  # inner floor

    # --- coarse stand-ins ---
    c.cyl("Caixa simplificada", 0, 0, f"-{F} - 0.06", add(R, 0.03), f"{F} + 0.06", "PVC", COARSE, in_plan=True)
    c.cyl("Tampa simplificada", 0, 0, lift, RC, 0.03, GRAY, COARSE, in_plan=True)

    # --- body: a hollow PVC cylinder with a thick base and the lid's collar ---
    c.rev("Corpo", "Front", [
        (0, add(zb, -0.014)), (add(RO, -0.012), add(zb, -0.014)), (RO, add(zb, -0.002)), (RO, -0.07), (RC, -0.07), (RC, -0.008),
        (add(RC, -0.012), 0), (R, 0), (R, zb), (0, zb),
    ], 0, 0, "PVC")
    c.rev("Base de apoio", "Front", [(0, add(zb, -0.06)), (add(RO, 0.02), add(zb, -0.06)), (add(RO, 0.02), add(zb, -0.014)), (0, add(zb, -0.014))],
          0, 0, "Concreto")
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        ca, sa = math.cos(a), math.sin(a)

        def pt(r, s):
            return (add(mul(r, ca), -s * sa), add(mul(r, sa), s * ca))
        c.profile(f"Nervura {i + 1}", "Plan", [pt(add(RO, -0.002), -0.006), pt(add(RO, 0.014), -0.005), pt(add(RO, 0.014), 0.005), pt(add(RO, -0.002), 0.006)],
                  add(zb, 0.02), f"{F} - 0.11", "PVC", FINE)
    for i, z in enumerate((add(zb, 0.12), f"{p(zb)} / 2", -0.12), 1):
        c.rev(f"Anel de reforço {i}", "Front", [(add(RO, -0.002), add(z, -0.008)), (add(RO, 0.01), add(z, -0.008)), (add(RO, 0.01), add(z, 0.008)),
                                                (add(RO, -0.002), add(z, 0.008))], 0, 0, "PVC", detail=FINE)

    # --- inlet: DN 75 through the wall, pouring over the basket ---
    zi = -0.15
    c.cyl_x("Entrada - tubo", 0, zi, f"-{RO} - 0.12", 0.0375, f"0.12 + {t} + 0.03", "PVC", in_plan=True)
    c.cyl_x("Entrada - bolsa", 0, zi, f"-{RO} - 0.12", 0.044, 0.06, "PVC", FINE)
    c.cyl_x("Entrada - anel de vedação", 0, zi, f"-{RO} - 0.002", 0.045, 0.006, "Borracha", FINE)
    c.connector("Entrada", "Sanitary", f"-{RO} - 0.12", 0, zi, "Left", 0.075)

    # --- removable basket: perforated wall, rims and a bail handle ---
    bx = mul(R, -0.3)
    br = mul(R, 0.55)
    z0, z1 = -0.42, -0.2
    c.rev("Cesto - fundo", "Front", [(bx, z0), (add(br, f"{p(bx)}"), z0), (add(br, f"{p(bx)}"), z0 + 0.006), (bx, z0 + 0.006)], 0, bx, GRAY)
    c.rev("Cesto - tela", "Front", [(add(bx, f"{p(br)} - 0.003"), z0 + 0.006), (add(bx, br), z0 + 0.006), (add(bx, br), z1 - 0.012), (add(bx, f"{p(br)} - 0.003"), z1 - 0.012)],
          0, bx, "Tela perfurada")
    for name, z in (("aro superior", z1 - 0.012), ("aro intermediário", (z0 + z1) / 2 - 0.006)):
        c.rev(f"Cesto - {name}", "Front", [(add(bx, f"{p(br)} - 0.004"), z), (add(bx, f"{p(br)} + 0.004"), z), (add(bx, f"{p(br)} + 0.004"), z + 0.012),
                                          (add(bx, f"{p(br)} - 0.004"), z + 0.012)], 0, bx, GRAY)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        ca, sa = math.cos(a), math.sin(a)
        x = add(bx, mul(br, ca))
        y = mul(br, sa)
        c.cyl(f"Cesto - montante {i + 1}", x, y, z0, 0.005, z1 - z0, GRAY, FINE)
    # The bail: an arch over the basket, pivoting on two lugs.
    zh = -0.08
    xa, xb = add(bx, f"-{p(br)} + 0.004"), add(bx, f"{p(br)} - 0.004")
    tube(c, "Cesto - alça", "Front", [(xa, z1 - 0.006), bez(xa, add(zh, -0.04), xa, zh, xa, zh), (add(xa, 0.04), zh),
                                      bez(add(xb, -0.04), zh, xb, zh, xb, zh), (xb, add(zh, -0.04)), (xb, z1 - 0.006)],
         0, 0.004, "Aço galvanizado", n=8)
    c.cyl("Cesto - pega", bx, 0, add(zh, -0.012), 0.012, 0.022, GRAY, FINE)

    # --- outlet: DN 100 through a siphon tee (the baffle) ---
    zo = -0.2
    xs = add(R, -0.065)  # the siphon's axis
    c.cyl("Tê sifonado - tubo", xs, 0, add(zb, 0.12), 0.0525, f"{F} - 0.2", "PVC")
    c.cyl("Tê sifonado - bolsa", xs, 0, add(zo, -0.07), 0.06, 0.14, "PVC")
    c.cyl_x("Tê sifonado - ramal", 0, zo, xs, 0.05, f"0.065 + {t}", "PVC")
    c.cyl_x("Saída - tubo", 0, zo, R, 0.05, f"{t} + 0.13", "PVC", in_plan=True)
    c.cyl_x("Saída - bolsa", 0, zo, f"{RO} + 0.07", 0.058, 0.06, "PVC", FINE)
    c.cyl_x("Saída - anel de vedação", 0, zo, RO, 0.06, 0.006, "Borracha", FINE)
    c.connector("Saída", "Sanitary", f"{RO} + 0.13", 0, zo, "Right", 0.1)

    # --- lid: a ribbed disc with two handles, lifting off ---
    def zl(d):
        return add(lift, d)

    c.rev("Tampa", "Front", [(0, zl(0.0)), (RC, zl(0.0)), (RC, zl(0.022)), (add(RC, -0.01), zl(0.03)), (0, zl(0.03))], 0, 0, GRAY, in_plan=True)
    c.rev("Tampa - encaixe", "Front", [(add(R, -0.004), zl(-0.025)), (R, zl(-0.025)), (R, zl(0.0)), (add(R, -0.004), zl(0.0))], 0, 0, GRAY)
    c.rev("Tampa - vedação", "Front", [(add(R, 0.004), zl(-0.003)), (add(RC, -0.012), zl(-0.003)), (add(RC, -0.012), zl(0.0)), (add(R, 0.004), zl(0.0))],
          0, 0, "Borracha", detail=FINE)
    for i, r in enumerate((mul(R, 0.35), mul(R, 0.7)), 1):
        c.rev(f"Tampa - friso {i}", "Front", [(r, zl(0.03)), (add(r, 0.008), zl(0.03)), (add(r, 0.008), zl(0.034)), (r, zl(0.034))], 0, 0, GRAY, detail=FINE)
    for i in range(8):
        a = math.radians(22.5 * (2 * i + 1))
        ca, sa = math.cos(a), math.sin(a)

        def pt(r, s):
            return (add(mul(r, ca), -s * sa), add(mul(r, sa), s * ca))
        c.profile(f"Tampa - nervura {i + 1}", "Plan", [pt(mul(R, 0.36), -0.003), pt(mul(R, 0.7), -0.003), pt(mul(R, 0.7), 0.003), pt(mul(R, 0.36), 0.003)],
                  zl(0.03), 0.004, GRAY, FINE)
    for side, sy in (("frontal", -1), ("traseira", 1)):
        y = mul(R, 0.82 * sy)
        tube(c, f"Tampa - alça {side}", "Front", [bez(-0.04, zl(0.028), -0.04, zl(0.05), -0.04, zl(0.05)), (-0.02, zl(0.05)),
                                                  bez(0.02, zl(0.05), 0.04, zl(0.05), 0.04, zl(0.05)), (0.04, zl(0.028))], y, 0.005, GRAY, n=8)
    c.cyl("Tampa - etiqueta", 0, 0, zl(0.03), mul(R, 0.3), 0.001, "Plástico cinza claro", FINE)
    return c
