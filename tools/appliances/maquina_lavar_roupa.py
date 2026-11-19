"""Máquina de lavar roupa de abertura superior: gabinete de aço pintado, tampo com bocal redondo,
tampa de vidro que abre para trás, cesto inox com agitador, painel de comando com seletores e teclas,
pés, mangueiras de entrada e de esgoto e cabo de força atrás."""

from __future__ import annotations

import math

from louca import *
from _casco import shell, corners
from lavadora_frontal import foot, sphere, num


def build():
    c = Component("Máquina de lavar roupa", "plumbing", "maquina-lavar-roupa", "Plumbing")
    W = c.param("Largura", 0.6)
    P = c.param("Profundidade", 0.65)
    A = c.param("Altura", 0.95)
    ang = c.angle("AnguloTampa", 0, open_at=78)
    c.type("Máquina de lavar 12 kg", "Ponto de água fria e esgoto; prever TUE de 1000 VA")
    c.type("Máquina de lavar 17 kg", "Ponto de água fria e esgoto; prever TUE de 1500 VA", Largura=0.68, Profundidade=0.72, Altura=1.05)
    c.mep = {"Fixture": {"drain_units": 3, "supply_weight": 1.0, "hot_water": False}}

    WHITE, TOP = "Aço pintado branco", "Branco"
    x0, x1 = f"-{W} / 2", f"{W} / 2"
    YF = f"(-{P} / 2)"  # front of the cabinet
    YB = f"({P} / 2 - 0.04)"  # back of the cabinet: hoses run behind it
    YW = f"{P} / 2"  # the wall
    ZP = 0.012  # top of the feet
    ZD = f"({A} - 0.14)"  # top of the deck
    YC = add(YB, -0.12)  # front face of the control console
    CY = -0.08  # center of the opening and of the basket
    RO = f"(0.36 * {W})"  # radius of the opening in the deck
    RB = f"({RO} - 0.012)"  # radius of the basket
    ZT = add(ZD, -0.055)  # top of the basket
    ZB = 0.2  # bottom of the basket
    YH, ZH = add(YC, -0.03), add(ZD, 0.006)  # the lid's hinge
    LL = f"({p(YH)} - {YF} - 0.012)"  # length of the lid
    WL = f"({W} - 0.03)"  # width of the lid

    # --- coarse stand-ins ---
    c.box("Gabinete simplificado", x0, YF, 0, W, f"{p(YB)} - {YF}", ZD, WHITE, COARSE, in_plan=True)
    c.box("Painel simplificado", x0, YC, ZD, W, f"{p(YB)} - {p(YC)}", f"{A} - {p(ZD)}", TOP, COARSE, in_plan=True)
    c.lid_box("Tampa simplificada", (YH, ZH), ang, f"-{WL} / 2", WL, 0, LL, 0, 0.022, "Vidro fumê", COARSE)

    # --- plan symbol ---
    c.profile("Símbolo - contorno", "Plan", rrect(x0, YF, x1, YB, 0.02), A, 0.001, WHITE)
    c.plan_only("Símbolo - contorno")
    c.profile("Símbolo - painel", "Plan", rect(x0, YC, x1, YB), A, 0.001, WHITE)
    c.plan_only("Símbolo - painel")
    c.profile("Símbolo - bocal", "Plan", disc(0, CY, RO), A, 0.001, WHITE)
    c.plan_only("Símbolo - bocal")

    # --- feet and cabinet ---
    for name, x, y in (("dianteiro esquerdo", add(x0, 0.05), add(YF, 0.05)), ("dianteiro direito", add(x1, -0.05), add(YF, 0.05)),
                       ("traseiro esquerdo", add(x0, 0.05), add(YB, -0.05)), ("traseiro direito", add(x1, -0.05), add(YB, -0.05))):
        foot(c, f"Pé {name}", x, y, 0.02)
    inner = (add(x0, 0.008), add(YF, 0.008), add(x1, -0.008), add(YB, -0.008), 0.012)
    shell(c, "Gabinete", [(ZP, inner), (add(ZD, -0.028), inner)], 0.008, WHITE)
    c.box("Base", add(x0, 0.008), add(YF, 0.008), ZP, f"{W} - 0.016", f"{p(YB)} - {YF} - 0.016", 0.008, "Aço galvanizado")
    c.box("Rodapé", add(x0, 0.03), add(YF, -0.002), add(ZP, 0.004), f"{W} - 0.06", 0.004, 0.07, "Plástico cinza")
    c.box("Rodapé - frisos", add(x0, 0.06), add(YF, -0.003), add(ZP, 0.03), f"{W} - 0.12", 0.001, 0.004, "Plástico preto", FINE)
    c.box("Etiqueta frontal", -0.05, add(YF, -0.001), add(ZD, -0.11), 0.1, 0.001, 0.022, "Plástico cinza claro", FINE)
    for side, x in (("esquerda", add(x0, -0.001)), ("direita", add(x1, -0.001))):
        c.box(f"Pega lateral {side}", x, add(YB, -0.2), add(ZD, -0.1), 0.002, 0.12, 0.03, "Plástico cinza", FINE)

    # --- deck: plastic top with the round opening, its lip and the dispensers ---
    outer = (add(x0, -0.003), add(YF, -0.004), add(x1, 0.003), add(YB, 0.0), 0.022)
    hole = oval(0, CY, RO, RO, n=48, start=90.0)
    deck = [(0, outer[3]), hole[0]] + hole[1:][::-1] + [hole[0], (0, outer[3])] + corners(outer)
    c.profile("Tampo", "Plan", deck, add(ZD, -0.03), 0.03, TOP)
    c.rev("Borda do bocal", "Front", [(RO, add(ZD, -0.03)), (add(RO, 0.004), add(ZD, -0.03)), (add(RO, 0.004), ZD), (add(RO, 0.02), ZD),
                                      (add(RO, 0.016), add(ZD, 0.006)), (add(RO, 0.004), add(ZD, 0.007)), (RO, add(ZD, 0.003))], CY, 0, TOP)
    for side, sx in (("esquerdo", -1), ("direito", 1)):
        xa = add(x0, 0.035) if sx < 0 else add(x1, -0.115)
        name = "sabão" if sx < 0 else "amaciante"
        c.box(f"Dispenser de {name}", xa, add(YH, -0.1), add(ZD, -0.002), 0.08, 0.07, 0.006, "Plástico cinza claro")
        c.box(f"Tampa do dispenser de {name}", add(xa, 0.008), add(YH, -0.092), add(ZD, 0.004), 0.064, 0.054, 0.002,
              "Plástico translúcido" if sx < 0 else "Plástico azul", FINE)
    c.box("Trava da tampa", -0.02, add(YF, 0.015), add(ZD, -0.002), 0.04, 0.02, 0.006, "Plástico cinza", FINE)
    for i, (x, r) in enumerate(((f"-{WL} / 2 + 0.02", 0.05), (f"{WL} / 2 - 0.04", 0.05), (f"-{WL} / 2 + 0.02", f"{LL} - 0.04"), (f"{WL} / 2 - 0.04", f"{LL} - 0.04")), 1):
        c.lid_box(f"Batente da tampa {i}", (YH, ZH), ang, x, 0.02, r, f"{p(r)} + 0.02", -0.006, 0, "Borracha cinza", FINE)

    # --- tub and basket ---
    c.rev("Tanque", "Front", [(add(RB, 0.012), 0.12), (add(RB, 0.018), 0.12), (add(RB, 0.018), add(ZD, -0.04)), (add(RB, 0.012), add(ZD, -0.04))],
          CY, 0, "Plástico cinza")
    c.rev("Tampa do tanque", "Front", [(add(RB, 0.002), add(ZD, -0.045)), (add(RO, 0.03), add(ZD, -0.045)), (add(RO, 0.03), add(ZD, -0.035)),
                                       (add(RB, 0.006), add(ZD, -0.035)), (add(RB, 0.002), add(ZD, -0.04))], CY, 0, "Plástico cinza claro")
    c.rev("Cesto", "Front", [(0, ZB), (RB, ZB), (RB, ZT), (add(RB, -0.004), ZT), (add(RB, -0.004), ZB + 0.004), (0, ZB + 0.004)], CY, 0, "Inox escovado")
    c.rev("Anel de balanceamento", "Front", [(add(RB, -0.028), add(ZT, -0.03)), (add(RB, 0.001), add(ZT, -0.03)), (add(RB, 0.001), ZT),
                                              (add(RB, -0.012), add(ZT, 0.008)), (add(RB, -0.028), add(ZT, -0.006))], CY, 0, "Plástico cinza claro")
    # Perforation of the basket's wall.
    k = 0
    for row, dz in enumerate((0.1, 0.2, 0.3)):
        for j in range(10):
            a = math.radians(36 * j + 18 * row)
            k += 1
            sphere(c, f"Furo do cesto {k}", mul(RB, math.cos(a) * 0.985), add(CY, mul(RB, math.sin(a) * 0.985)), ZB + dz, 0.004, "Aço pintado preto")
    # Agitator: impeller with blades, ribbed column and the softener cup on top.
    c.rev("Agitador - base", "Front", [(0, ZB + 0.004), (0.15, ZB + 0.004), (0.145, ZB + 0.016), (0.07, ZB + 0.04), (0, ZB + 0.045)], CY, 0, "Plástico cinza claro")
    c.rev("Agitador - coluna", "Front", [(0, ZB + 0.04), (0.06, ZB + 0.04), (0.042, ZB + 0.33), (0.036, ZB + 0.345), (0, ZB + 0.345)], CY, 0, "Plástico cinza claro")
    c.rev("Agitador - copo do amaciante", "Front", [(0, ZB + 0.34), (0.045, ZB + 0.34), (0.048, ZB + 0.365, 0.02), (0.03, ZB + 0.38), (0, ZB + 0.38)],
          CY, 0, "Plástico azul")
    for i in range(6):
        a = math.radians(60 * i + 15)
        ca, sa = math.cos(a), math.sin(a)
        blade = [(r * ca - t * sa, CY + r * sa + t * ca) for r, t in ((0.05, -0.006), (0.14, -0.004), (0.14, 0.004), (0.05, 0.006))]
        c.profile(f"Agitador - pá {i + 1}", "Plan", [(e(u), e(v)) for u, v in blade], ZB + 0.004, 0.032, "Plástico cinza claro")
    for i in range(4):
        a = math.radians(90 * i + 45)
        ca, sa = math.cos(a), math.sin(a)
        fin = [(r * ca - t * sa, CY + r * sa + t * ca) for r, t in ((0.03, -0.004), (0.068, -0.003), (0.068, 0.003), (0.03, 0.004))]
        c.profile(f"Agitador - aleta {i + 1}", "Plan", [(e(u), e(v)) for u, v in fin], ZB + 0.045, 0.24, "Plástico cinza claro", FINE)

    # --- lid: smoked glass in a plastic frame, hinged at the back ---
    hinge = (YH, ZH)
    WL2 = f"{WL} / 2"
    c.lid_box("Tampa - travessa traseira", hinge, ang, f"-{WL2}", WL, 0, 0.05, 0, 0.022, TOP)
    c.lid_box("Tampa - travessa frontal", hinge, ang, f"-{WL2}", WL, f"{LL} - 0.06", LL, 0, 0.022, TOP)
    c.lid_box("Tampa - lateral esquerda", hinge, ang, f"-{WL2}", 0.05, 0.05, f"{LL} - 0.06", 0, 0.022, TOP)
    c.lid_box("Tampa - lateral direita", hinge, ang, f"{WL2} - 0.05", 0.05, 0.05, f"{LL} - 0.06", 0, 0.022, TOP)
    c.lid_box("Tampa - vidro", hinge, ang, f"-{WL2} + 0.045", f"{WL} - 0.09", 0.045, f"{LL} - 0.055", 0.008, 0.016, "Vidro fumê")
    c.lid_box("Tampa - puxador", hinge, ang, -0.08, 0.16, f"{LL} - 0.03", f"{LL} + 0.006", -0.004, 0.018, "Plástico cinza")
    c.lid_box("Tampa - rebaixo do puxador", hinge, ang, -0.06, 0.12, f"{LL} - 0.025", f"{LL} - 0.012", 0.018, 0.0225, "Plástico preto", FINE)
    for side, x in (("esquerda", f"-{WL2} + 0.05"), ("direita", f"{WL2} - 0.09")):
        c.cyl_x(f"Dobradiça {side}", YH, ZH, x, 0.008, 0.04, "Plástico cinza")
        c.box(f"Base da dobradiça {side}", x, add(YH, -0.01), add(ZD, -0.002), 0.04, 0.03, 0.006, "Plástico cinza", FINE)

    # --- control console ---
    zc = add(ZD, 0.055)  # height of the knobs' axes
    top_round = [(add(YC, 0.0), add(A, -0.03)), (add(YC, 0.006), add(A, -0.012)), (add(YC, 0.02), add(A, -0.003)), (add(YC, 0.035), A)]
    c.profile("Painel de comando", "Side", [(add(YC, 0.008), ZD), (YC, add(ZD, 0.01))] + top_round + [(YB, A), (YB, ZD)], x0, W, TOP, in_plan=False)
    c.box("Painel - faixa decorativa", add(x0, 0.02), add(YC, -0.0015), add(ZD, 0.018), f"{W} - 0.04", 0.0015, f"{A} - {p(ZD)} - 0.055", "Plástico preto brilhante")
    for name, x in (("Seletor de nível de água", f"-0.3 * {W}"), ("Seletor de programas", f"0.3 * {W}")):
        c.rev(f"{name} - base", "Plan", [(x, add(YC, -0.003)), (add(x, 0.036), add(YC, -0.003)), (add(x, 0.036), YC), (x, YC)], zc, x, "Cromado")
        c.rev(name, "Plan", [(x, add(YC, -0.03)), (add(x, 0.024), add(YC, -0.03)), (add(x, 0.027), add(YC, -0.026)), (add(x, 0.029), add(YC, -0.003)), (x, add(YC, -0.003))],
              zc, x, "Plástico cinza claro")
        c.box(f"{name} - marca", add(x, -0.0015), add(YC, -0.0305), add(zc, 0.008), 0.003, 0.0006, 0.014, "Plástico preto", FINE)
        for i in range(8):
            a = math.radians(-60 + 120 * i / 7 + 90)
            c.cyl_y(f"{name} - indicador {i + 1}", add(x, 0.042 * math.cos(a)), add(zc, 0.042 * math.sin(a)), add(YC, -0.0021), 0.002, 0.0006, "Plástico cinza claro", FINE)
    c.box("Visor", -0.05, add(YC, -0.0022), add(zc, 0.0), 0.1, 0.0007, 0.03, "Visor LED", FINE)
    for i in range(2):
        c.box(f"Visor - dígito {i + 1}", -0.02 + 0.022 * i, add(YC, -0.0026), add(zc, 0.006), 0.016, 0.0004, 0.018, "Plástico azul", FINE)
    for i in range(4):
        x = -0.06 + 0.04 * i
        c.cyl_y(f"Tecla {i + 1}", x, add(zc, -0.022), add(YC, -0.0045), 0.008, 0.003, "Teclado", FINE)
        c.cyl_y(f"Luz da tecla {i + 1}", x, add(zc, -0.009), add(YC, -0.0022), 0.0016, 0.0007, "Plástico verde", FINE)
    c.cyl_y("Tecla iniciar - aro", 0.085, add(zc, 0.015), add(YC, -0.003), 0.013, 0.0015, "Cromado", FINE)
    c.cyl_y("Tecla iniciar", 0.085, add(zc, 0.015), add(YC, -0.0055), 0.0105, 0.004, "Teclado", FINE)
    c.cyl_y("Tecla liga-desliga", -0.085, add(zc, 0.015), add(YC, -0.0045), 0.008, 0.003, "Plástico vermelho", FINE)

    # --- back: inlet hose, drain hose and power cord ---
    HY = add(YB, 0.015)  # the hoses run in the gap behind the cabinet
    zw = add(A, -0.05)  # tap and standpipe on the wall
    VX, VZ = -0.15, add(ZD, -0.07)
    c.cyl_y("Entrada de água - válvula", VX, VZ, add(YB, -0.001), 0.013, 0.008, "Plástico azul")
    c.cyl_y("Entrada de água - porca", VX, VZ, add(YB, 0.005), 0.016, 0.012, "Plástico cinza claro")
    tube(c, "Mangueira de entrada", "Side", [bez(add(YB, 0.006), VZ, HY, VZ, HY, add(VZ, 0.01)), (HY, add(VZ, 0.04)), (HY, add(zw, -0.03)),
                                               bez(HY, add(zw, -0.03), HY, add(zw, -0.01), add(HY, 0.01), zw), (add(YW, -0.008), zw)],
         VX, 0.0095, "Borracha cinza", n=10)
    c.cyl_y("Mangueira de entrada - porca da torneira", VX, zw, add(YW, -0.012), 0.016, 0.012, "Latão")
    c.connector("Água fria", "ColdWater", VX, YW, zw, "Back", 0.02)
    OX, OZ = 0.15, 0.1
    c.cyl_y("Saída de esgoto - bocal", OX, OZ, add(YB, -0.001), 0.015, 0.008, "Plástico cinza")
    tube(c, "Mangueira de esgoto", "Side", [bez(add(YB, 0.006), OZ, HY, OZ, HY, add(OZ, 0.01)), (HY, add(OZ, 0.04)), (HY, add(zw, -0.04)),
                                               bez(HY, add(zw, -0.04), HY, add(zw, -0.01), add(HY, 0.01), zw), (add(YW, 0.03), zw)],
         OX, 0.012, "Plástico cinza", n=10)
    for i in range(12):
        c.cyl(f"Mangueira de esgoto - anel {i + 1}", OX, HY, add(OZ, 0.06 + 0.04 * i), 0.0135, 0.006, "Plástico cinza", FINE)
    c.box("Curva guia da mangueira", add(OX, -0.016), add(HY, -0.012), add(zw, -0.07), 0.032, 0.03, 0.05, "Plástico cinza claro", FINE)
    for i, z in enumerate((0.3, add(ZD, -0.18)), 1):
        c.box(f"Presilha da mangueira {i}", add(OX, -0.018), YB, z, 0.036, 0.03, 0.014, "Plástico cinza claro", FINE)
    c.connector("Esgoto", "Sanitary", OX, YW, zw, "Back", 0.04)
    CX, CZ = add(x1, -0.06), add(ZD, -0.05)
    c.cyl_y("Cabo de força - passa-fio", CX, CZ, add(YB, -0.001), 0.009, 0.01, "Plástico preto")
    tube(c, "Cabo de força", "Side", [(add(YB, 0.005), CZ), (add(YB, 0.010), CZ, -0.008), (add(YB, 0.018), add(CZ, -0.008)), (add(YB, 0.018), add(CZ, -0.4))], CX, 0.0045, "Borracha", FINE)
    c.box("Cabo de força - plugue", add(CX, -0.018), add(YB, 0.009), add(CZ, -0.445), 0.036, 0.018, 0.045, "Plástico preto", FINE)
    for i, dx in enumerate((-0.0095, 0, 0.0095), 1):
        c.cyl(f"Cabo de força - pino {i}", add(CX, dx), add(YB, 0.018), add(CZ, -0.463), 0.002, 0.018, "Latão", FINE)
    c.box("Etiqueta de identificação", add(x1, -0.2), add(YB, -0.0005), add(ZD, -0.25), 0.1, 0.001, 0.06, "Plástico cinza claro", FINE)
    for i in range(6):
        c.box(f"Ventilação do motor {i + 1}", -0.1, add(YB, -0.0005), 0.06 + 0.012 * i, 0.2, 0.001, 0.005, "Aço pintado preto", FINE)
    return c
