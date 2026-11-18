"""Caixa d'água de polietileno: corpo cônico oco com frisos, aba superior, tampa com travas e respiro,
entrada com torneira de boia, saída com registro, extravasor e limpeza com adaptadores de flange."""

from __future__ import annotations

import math

from louca import *
from lavadora_frontal import sphere

PE = "Polietileno"
RIBS = (0.28, 0.52, 0.74)  # height fractions of the body's horizontal ribs


def build():
    c = Component("Caixa d'água de polietileno", "plumbing", "caixa-dagua", "Plumbing")
    RB = c.param("RaioBase", 0.48)
    RT = c.param("RaioTopo", 0.61)
    A = c.param("Altura", 0.73)
    lift = c.param("AberturaTampa", 0.0, instance=True)
    c.open_pose["AberturaTampa"] = 0.35
    c.material(PE, (40, 90, 160), "Plastic", "Satin")
    desc = "Reservatório de polietileno com tampa, torneira de boia e adaptadores de flange"
    c.type("Caixa d'água 310 L", desc, RaioBase=0.42, RaioTopo=0.52, Altura=0.62)
    c.type("Caixa d'água 500 L", desc, RaioBase=0.48, RaioTopo=0.61, Altura=0.73)
    c.type("Caixa d'água 1000 L", desc, RaioBase=0.6, RaioTopo=0.76, Altura=0.86)
    c.type("Caixa d'água 2000 L", desc, RaioBase=0.78, RaioTopo=0.96, Altura=1.12)
    c.preview_size = (1.4, 1.4, 0.8)

    HB = f"({A} - 0.08)"  # top of the body's rim

    def rf(f):  # outer radius of the body at the height fraction f
        return f"({RB} + ({RT} - {RB}) * {e(f)})"

    def rz(z):  # outer radius of the body at the height z
        return f"({RB} + ({RT} - {RB}) * {p(z)} / {HB})"

    def zf(f):
        return f"{HB} * {e(f)}"

    # --- coarse stand-ins (the old pieces) ---
    c.rev("Reservatório simplificado", "Front", [(0, 0), (RB, 0), (RT, HB), (0, HB)], 0, 0, PE, detail=COARSE, in_plan=True)
    c.cyl("Tampa simplificada", 0, 0, add(HB, lift), add(RT, 0.03), 0.08, PE, COARSE, in_plan=True)

    # --- body: a hollow cone with a rounded foot, horizontal ribs and the top flange ---
    t = 0.006
    outer = [(add(RB, -0.03), 0), (add(RB, -0.009), 0.006), (RB, 0.03)]
    inner_up = [(add(RB, -0.03 - t), t), (add(RB, -t - 0.006), 0.012), (add(RB, -t), 0.032)]
    for f in RIBS:
        for df, dr in ((-0.03, 0), (-0.015, 0.012), (0.015, 0.012), (0.03, 0)):
            outer.append((add(rf(f + df), dr), zf(f + df)))
    outer += [(add(RT, 0.0), add(HB, -0.03)), (add(RT, 0.045), add(HB, -0.022)), (add(RT, 0.045), HB)]
    inner = inner_up + [(add(rf(f), -t), zf(f)) for f in RIBS] + [(add(RT, -t), HB)]
    section = [(0, 0)] + outer + list(reversed(inner)) + [(0, t)]
    c.rev("Reservatório", "Front", section, 0, 0, PE)
    c.rev("Aba - reforço", "Front", [(add(RT, -0.002), add(HB, -0.03)), (add(RT, 0.045), add(HB, -0.03)), (add(RT, 0.045), add(HB, -0.022)), (add(RT, -0.002), add(HB, -0.01))],
          0, 0, PE, detail=FINE)
    # The base's reinforcement ring.
    c.rev("Base - anel de apoio", "Front", [(add(RB, -0.09), 0), (add(RB, -0.06), 0), (add(RB, -0.06), 0.004), (add(RB, -0.09), 0.004)], 0, 0, PE, detail=FINE)
    # Label on the body.
    zl = zf(0.4)
    c.rev("Etiqueta", "Front", [(add(rf(0.4), 0.0005), add(zl, -0.04)), (add(rf(0.4), 0.0015), add(zl, -0.04)), (add(rf(0.48), 0.0015), add(zf(0.48), 0.0)),
                                (add(rf(0.48), 0.0005), zf(0.48))], 0, 0, "Plástico cinza claro", angle=24, detail=FINE)

    # --- lid: a low dome with a skirt over the flange, latches and a vent ---
    def zl_(dz):
        return add(add(A, dz), lift)

    def zh(dz):
        return add(add(HB, dz), lift)

    R2 = f"({RT} * 0.5)"
    R8 = f"({RT} * 0.85)"
    c.rev("Tampa", "Front", [
        (0, zl_(0)), (R2, zl_(-0.012)), (R8, zl_(-0.034)), (add(RT, 0.012), zh(0.026)), (add(RT, 0.052), zh(0.014)),
        (add(RT, 0.052), zh(-0.026)), (add(RT, 0.046), zh(-0.026)), (add(RT, 0.046), zh(0.006)), (add(RT, 0.006), zh(0.018)),
        (R8, zl_(-0.042)), (R2, zl_(-0.02)), (0, zl_(-0.008)),
    ], 0, 0, PE, in_plan=True)
    c.rev("Tampa - anel de vedação", "Front", [(add(RT, -0.004), zh(0.0005)), (add(RT, 0.046), zh(0.0005)), (add(RT, 0.046), zh(0.006)), (add(RT, -0.004), zh(0.012))],
          0, 0, "Borracha", detail=FINE)
    c.rev("Tampa - frisos", "Front", [(R2, zl_(-0.012)), (add(R2, 0.02), zl_(-0.0135)), (add(R2, 0.02), zl_(-0.008)), (R2, zl_(-0.006))], 0, 0, PE, detail=FINE)
    c.rev("Respiro", "Front", [(0, zl_(-0.002)), (0.05, zl_(-0.002)), (0.05, zl_(0.012)), (0.035, zl_(0.03)), (0, zl_(0.034))], 0, 0, PE)
    for i in range(6):
        a = math.radians(30 + 60 * i)
        c.profile(f"Respiro - fenda {i + 1}", "Plan", [(e(r * math.cos(a) - s * math.sin(a)), e(r * math.sin(a) + s * math.cos(a)))
                                                       for r, s in ((0.03, -0.004), (0.049, -0.004), (0.049, 0.004), (0.03, 0.004))],
                  zl_(0.004), 0.006, "Plástico preto", FINE)
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        ca, sa = math.cos(a), math.sin(a)

        def pt(r, s):
            return (add(mul(r, ca), -s * sa), add(mul(r, sa), s * ca))
        r0, r1 = add(RT, 0.05), add(RT, 0.066)
        c.profile(f"Trava da tampa {i + 1}", "Plan", [pt(r0, -0.03), pt(r1, -0.026), pt(r1, 0.026), pt(r0, 0.03)], zh(-0.032), 0.04, PE)
        c.profile(f"Trava da tampa {i + 1} - pega", "Plan", [pt(r1, -0.018), pt(add(r1, 0.006), -0.016), pt(add(r1, 0.006), 0.016), pt(r1, 0.018)],
                  zh(-0.012), 0.016, PE, FINE)

    # --- fittings: flange adapters through the wall ---
    def flange_x(name, z, sign, reach, r_pipe=0.016):
        """A flange adapter through the wall on the +x (sign 1) or -x side at the height z; returns the stub's outer end (x)."""
        rw = rz(z)
        if sign > 0:
            c.cyl_x(f"{name} - flange externa", 0, z, add(rw, -0.002), 0.036, 0.008, "PVC")
            c.cyl_x(f"{name} - flange interna", 0, z, add(rw, -0.018), 0.036, 0.008, "PVC", FINE)
            c.cyl_x(f"{name} - corpo", 0, z, add(rw, -0.03), add(r_pipe, 0.006), 0.05, "PVC")
            c.cyl_x(f"{name} - tubo", 0, z, add(rw, 0.006), r_pipe, reach, "PVC", in_plan=True)
            return add(add(rw, 0.006), reach)
        c.cyl_x(f"{name} - flange externa", 0, z, f"-{rw} - 0.006", 0.036, 0.008, "PVC")
        c.cyl_x(f"{name} - flange interna", 0, z, f"-{rw} + 0.01", 0.036, 0.008, "PVC", FINE)
        c.cyl_x(f"{name} - corpo", 0, z, f"-{rw} - 0.02", add(r_pipe, 0.006), 0.05, "PVC")
        c.cyl_x(f"{name} - tubo", 0, z, f"-{rw} - 0.006 - {reach}", r_pipe, reach, "PVC", in_plan=True)
        return f"-{rw} - 0.006 - {reach}"

    # Inlet near the top, with the float valve inside.
    zi = add(A, -0.15)
    xi = flange_x("Entrada", zi, 1, 0.07, 0.0125)
    c.connector("Entrada", "ColdWater", xi, 0, zi, "Right", 0.025)
    rwi = rz(zi)
    c.cyl_x("Torneira de boia - corpo", 0, zi, add(rwi, -0.09), 0.018, 0.065, "Branco")
    c.cyl("Torneira de boia - bico", add(rwi, -0.07), 0, add(zi, -0.05), 0.008, 0.035, "Branco", FINE)
    c.cyl_x("Torneira de boia - haste", 0, zi, add(rwi, -0.33), 0.004, 0.245, "Latão")
    sphere(c, "Torneira de boia - boia", add(rwi, -0.39), 0, zi, 0.065, "Plástico cinza claro", detail=FULL)
    c.cyl("Torneira de boia - pino", add(rwi, -0.085), 0, add(zi, 0.012), 0.004, 0.012, "Latão", FINE)
    # Outlet at the bottom with a gate valve.
    zo = 0.07
    xo = flange_x("Saída", zo, 1, 0.16, 0.016)
    c.cyl_x("Registro da saída", 0, zo, add(xo, -0.12), 0.026, 0.06, "Latão")
    c.cyl("Registro da saída - castelo", add(xo, -0.09), 0, zo, 0.012, 0.055, "Latão")
    c.cyl("Registro da saída - volante", add(xo, -0.09), 0, add(zo, 0.055), 0.03, 0.01, "Plástico vermelho")
    c.connector("Saída", "ColdWater", xo, 0, zo, "Right", 0.032)
    # Cleaning outlet at the bottom on the other side, capped.
    zc = 0.07
    xc = flange_x("Limpeza", zc, -1, 0.1, 0.016)
    c.cyl_x("Limpeza - registro", 0, zc, add(xc, 0.03), 0.026, 0.05, "Latão", FINE)
    c.cyl("Limpeza - volante", add(xc, 0.055), 0, add(zc, 0.026), 0.028, 0.01, "Plástico vermelho", FINE)
    c.cyl_x("Limpeza - tampão", 0, zc, add(xc, -0.012), 0.02, 0.014, "PVC", FINE)
    # Overflow near the top on the -x side, turning down.
    zx = add(A, -0.17)
    xx = flange_x("Extravasor", zx, -1, 0.05, 0.016)
    tube(c, "Extravasor - curva e descida", "Front", [(add(xx, 0.004), zx), (add(xx, -0.02), zx, 0.0), bez(add(xx, -0.04), zx, add(xx, -0.06), zx, add(xx, -0.06), add(zx, -0.02)),
                                                    (add(xx, -0.06), add(zx, -0.04)), (add(xx, -0.06), 0.05)], 0, 0.016, "PVC", n=12)
    c.rev("Extravasor - tela", "Front", [(add(xx, -0.06), 0.04), (add(xx, -0.04), 0.04), (add(xx, -0.04), 0.055), (add(xx, -0.06), 0.055)], 0, add(xx, -0.06),
          "Tela perfurada", detail=FINE)
    return c
