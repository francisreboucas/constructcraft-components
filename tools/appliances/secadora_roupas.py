"""Secadora de roupas: a floor-standing front-loading condenser tumble dryer.

The porthole door, the drum and the small helpers are the ones of the
front-loading washer (`lavadora_frontal`), so the two read as one family.
"""

from __future__ import annotations

import math

from kit import *
from lavadora_frontal import door_part, drum, foot, num, porthole_door, sphere

# Half-sections of the door, in units of its radius (rho, b), counter-clockwise: a flatter glass than the washer's.
DOOR_RING = [(0.68, 0), (1.0, 0), (1.0, 0.06), (0.95, 0.115), (0.72, 0.115), (0.68, 0.10)]
DOOR_TRIM = [(0.56, 0), (0.68, 0), (0.68, 0.10), (0.56, 0.075)]
DOOR_GLASS = [(0, -0.07), (0.42, -0.07), (0.56, 0.0), (0.56, 0.05), (0.52, 0.05), (0.40, -0.04), (0, -0.04)]
DOOR_DISC = [(0, 0), (1.0, 0), (1.0, 0.11), (0, 0.11)]


def build() -> Component:
    c = Component("Secadora de roupas", "furniture", "secadora-roupas", "Furniture")
    c.param("Largura", 0.60)
    c.param("Profundidade", 0.65)
    c.param("Altura", 0.85)
    c.param("AlturaPainel", 0.11)
    c.param("AlturaRodape", 0.13)
    c.param("AlturaPes", 0.015)
    c.param("DiametroPorta", 0.46)
    c.param("DiametroTambor", 0.54)
    c.param("ProfundidadeTambor", 0.45)
    ang = c.angle("AnguloPorta", 0, open_at=105)

    W2 = "Largura/2"
    YF = "(-Profundidade/2 + 0.032)"  # front face of the cabinet
    YB = "(Profundidade/2 - 0.03)"  # back face of the cabinet: the exhaust collar reaches the wall
    YW = "Profundidade/2"
    DC = f"({YB} - {YF})"
    Z0 = "AlturaPes"
    ZR = "(AlturaPes + AlturaRodape)"  # top of the kick plate
    ZT = "(Altura - 0.03)"  # underside of the top
    ZP = "(Altura - 0.03 - AlturaPainel)"  # bottom of the control panel
    ZPC = "(Altura - 0.03 - AlturaPainel/2)"
    ZC = "(AlturaPes/2 + AlturaRodape/2 + Altura/2 - 0.015 - AlturaPainel/2)"  # axis of the door and of the drum
    RP = "(DiametroPorta/2)"
    RH = f"(0.70*{RP})"  # opening of the front panel
    RM = f"(0.66*{RP})"  # mouth of the drum
    RD = "(DiametroTambor/2)"
    white, dark = "Aço pintado branco", "Plástico preto brilhante"

    # --- coarse stand-ins ---
    c.box("Corpo simplificado", f"-{W2}", YF, 0, "Largura", DC, "Altura", white, detail=COARSE, in_plan=True)
    hinge = (f"(-1.06*{RP})", f"({YF} - 0.002)")
    porthole_door(c, "Porta simplificada", hinge, ZC, RP, ang, [("disco", "Plástico cinza claro", DOOR_DISC, 8, COARSE, True)])

    # --- cabinet ---
    for name, x in (("dianteiro esquerdo", f"-{W2} + 0.05"), ("dianteiro direito", f"{W2} - 0.05")):
        foot(c, f"Pé {name}", x, f"{YF} + 0.05", Z0)
    for name, x in (("traseiro esquerdo", f"-{W2} + 0.05"), ("traseiro direito", f"{W2} - 0.05")):
        foot(c, f"Pé {name}", x, f"{YB} - 0.05", Z0)
    c.box("Lateral esquerda", f"-{W2}", YF, Z0, 0.008, DC, f"{ZT} - {Z0}", white)
    c.box("Lateral direita", f"{W2} - 0.008", YF, Z0, 0.008, DC, f"{ZT} - {Z0}", white)
    c.box("Base", f"-{W2} + 0.008", f"{YF} + 0.012", Z0, "Largura - 0.016", f"{DC} - 0.02", 0.008, "Aço galvanizado")
    c.box("Painel traseiro", f"-{W2} + 0.008", f"{YB} - 0.008", Z0, "Largura - 0.016", 0.008, f"{ZT} - {Z0}", "Aço galvanizado")
    c.box("Tampo", f"-{W2}", f"{YF} - 0.006", ZT, "Largura", f"{DC} + 0.006", 0.03, "Laminado branco", in_plan=True)
    c.box("Tampo - friso frontal", f"-{W2}", f"{YF} - 0.007", f"{ZT} + 0.004", "Largura", 0.001, 0.022, "Plástico cinza claro", detail=FINE)
    c.profile("Painel frontal", "Front", [
        (0, ZR), (0, f"{ZC} - {RH}", f"-{RH}"), (0, f"{ZC} + {RH}", f"-{RH}"), (0, f"{ZC} - {RH}"), (0, ZR),
        (f"{W2} - 0.008", ZR), (f"{W2} - 0.008", ZP), (f"-{W2} + 0.008", ZP), (f"-{W2} + 0.008", ZR),
    ], YF, 0.012, white)
    c.rev("Batente da porta", "Plan", [
        (f"{RH} - 0.002", f"{YF} - 0.0015"), (f"1.02*{RP}", f"{YF} - 0.0015"), (f"1.02*{RP}", f"{YF} + 0.001"), (f"{RH} - 0.002", f"{YF} + 0.001"),
    ], ZC, 0, "Plástico cinza claro")

    # --- kick plate: condenser hatch on the left, air intake grille on the right ---
    c.box("Rodapé", f"-{W2} + 0.008", f"{YF} + 0.004", Z0, "Largura - 0.016", 0.012, "AlturaRodape", white)
    c.box("Rodapé - sombra superior", f"-{W2} + 0.008", f"{YF} + 0.001", f"{ZR} - 0.004", "Largura - 0.016", 0.004, 0.004, "Plástico preto", detail=FINE)
    HX, HW = f"(-{W2} + 0.035)", "(0.40*Largura)"
    c.box("Tampa do condensador", HX, f"{YF} + 0.001", f"{Z0} + 0.014", HW, 0.004, "AlturaRodape - 0.03", "Branco")
    c.box("Tampa do condensador - contorno", f"{HX} - 0.002", f"{YF} + 0.0035", f"{Z0} + 0.012", f"{HW} + 0.004", 0.001, "AlturaRodape - 0.026", "Plástico cinza", detail=FINE)
    c.box("Tampa do condensador - trava", f"{HX} + {HW}/2 - 0.025", f"{YF} + 0.0005", f"{ZR} - 0.034", 0.05, 0.001, 0.01, "Plástico cinza", detail=FINE)
    for i in range(2):
        c.box(f"Tampa do condensador - dobradiça {i + 1}", f"{HX} + {num(0.15 + 0.55 * i)}*{HW}", f"{YF} + 0.0005", f"{Z0} + 0.011", 0.03, 0.004, 0.005, "Plástico cinza claro", detail=FINE)
    GX, GW = "(0.06*Largura)", f"({W2} - 0.035 - 0.06*Largura)"
    c.box("Grade de ar - fundo", GX, f"{YF} + 0.003", f"{Z0} + 0.02", GW, 0.002, "AlturaRodape - 0.042", "Aço pintado preto")
    for i in range(7):
        c.box(f"Grade de ar - aleta {i + 1}", GX, f"{YF} + 0.0005", f"{Z0} + 0.022 + {num(i / 7)}*(AlturaRodape - 0.046)", GW, 0.004, "0.07*(AlturaRodape - 0.046)", "Branco", detail=FINE)
    for i in range(2):
        c.box(f"Grade de ar - montante {i + 1}", f"{GX} + {num(0.33 * (i + 1))}*{GW} - 0.002", f"{YF} + 0.0008", f"{Z0} + 0.02", 0.004, 0.004, "AlturaRodape - 0.042", "Branco", detail=FINE)

    # --- control panel: water tank on the left, display in the middle, dial on the right ---
    YP = f"({YF} - 0.005)"
    c.box("Painel de comando", f"-{W2}", YP, ZP, "Largura", 0.025, "AlturaPainel", "Branco")
    c.box("Painel de comando - friso inferior", f"-{W2}", f"{YP} - 0.001", ZP, "Largura", 0.001, 0.006, "Plástico cinza", detail=FINE)
    DX, DW = f"(-{W2} + 0.018)", "(0.25*Largura)"
    c.box("Reservatório de água - frente", DX, f"{YP} - 0.004", f"{ZP} + 0.016", DW, 0.004, "AlturaPainel - 0.03", "Branco")
    c.box("Reservatório de água - contorno", f"{DX} - 0.002", f"{YP} - 0.0005", f"{ZP} + 0.014", f"{DW} + 0.004", 0.0005, "AlturaPainel - 0.026", "Plástico cinza", detail=FINE)
    c.box("Reservatório de água - puxador", f"{DX} + 0.02", f"{YP} - 0.0045", f"{ZPC} + 0.008", f"{DW} - 0.04", 0.0005, 0.018, "Plástico cinza", detail=FINE)
    c.box("Reservatório de água - visor de nível", f"{DX} + {DW} - 0.022", f"{YP} - 0.0045", f"{ZP} + 0.024", 0.008, 0.0005, 0.03, "Plástico translúcido", detail=FINE)
    c.box("Reservatório de água - tanque", f"{DX} + 0.006", YP, f"{ZP} + 0.02", f"{DW} - 0.012", f"0.7*{DC}", "AlturaPainel - 0.045", "Plástico translúcido", detail=FINE)
    SX, SW = "(-0.17*Largura)", "(0.36*Largura)"
    c.profile("Visor - máscara", "Front", rrect(SX, f"{ZPC} - 0.03", f"{SX} + {SW}", f"{ZPC} + 0.03", 0.03), f"{YP} - 0.0015", 0.0015, dark)
    c.box("Visor", f"{SX} + 0.03", f"{YP} - 0.002", f"{ZPC} - 0.012", f"0.3*{SW}", 0.0005, 0.026, "Visor LED", detail=FINE)
    for i in range(3):
        c.box(f"Visor - dígito {i + 1}", f"{SX} + 0.036 + {num(0.085 * i)}*{SW}", f"{YP} - 0.0024", f"{ZPC} - 0.007", f"0.06*{SW}", 0.0004, 0.016, "Plástico azul", detail=FINE)
    for i in range(4):
        x = f"{SX} + {num(0.50 + 0.105 * i)}*{SW}"
        c.cyl_y(f"Tecla de função {i + 1}", x, f"{ZPC} - 0.006", f"{YP} - 0.0035", 0.0065, 0.002, "Teclado", detail=FINE)
        c.cyl_y(f"Luz de função {i + 1}", x, f"{ZPC} + 0.008", f"{YP} - 0.0022", 0.0015, 0.0007, "Plástico verde", detail=FINE)
    KX = "(0.30*Largura)"
    c.rev("Seletor de programas - base", "Plan", [(KX, f"{YP} - 0.002"), (f"{KX} + 0.04", f"{YP} - 0.002"), (f"{KX} + 0.04", YP), (KX, YP)], ZPC, KX, "Plástico cinza claro")
    c.rev("Seletor de programas", "Plan", [
        (KX, f"{YP} - 0.024"), (f"{KX} + 0.028", f"{YP} - 0.024"), (f"{KX} + 0.031", f"{YP} - 0.02"), (f"{KX} + 0.031", f"{YP} - 0.002"), (KX, f"{YP} - 0.002"),
    ], ZPC, KX, "Branco")
    c.rev("Seletor de programas - aro", "Plan", [
        (f"{KX} + 0.031", f"{YP} - 0.008"), (f"{KX} + 0.033", f"{YP} - 0.008"), (f"{KX} + 0.033", f"{YP} - 0.002"), (f"{KX} + 0.031", f"{YP} - 0.002"),
    ], ZPC, KX, "Cromado", detail=FINE)
    c.box("Seletor de programas - marca", f"{KX} - 0.0015", f"{YP} - 0.0245", f"{ZPC} + 0.01", 0.003, 0.0005, 0.016, "Plástico cinza", detail=FINE)
    for i in range(10):
        a = math.radians(36 * i + 18)
        c.cyl_y(f"Seletor de programas - indicador {i + 1}", f"{KX} + {num(0.047 * math.cos(a))}", f"{ZPC} + {num(0.047 * math.sin(a))}",
                f"{YP} - 0.0006", 0.002, 0.0006, "Plástico cinza", detail=FINE)
    BX = "(0.165*Largura + 0.012)"
    c.cyl_y("Tecla iniciar - aro", BX, f"{ZPC} + 0.014", f"{YP} - 0.003", 0.012, 0.0015, "Cromado", detail=FINE)
    c.cyl_y("Tecla iniciar", BX, f"{ZPC} + 0.014", f"{YP} - 0.0045", 0.0095, 0.003, "Plástico verde", detail=FINE)
    c.cyl_y("Tecla liga-desliga", BX, f"{ZPC} - 0.02", f"{YP} - 0.0035", 0.007, 0.002, "Plástico vermelho", detail=FINE)

    # --- door opening, lint filter and drum ---
    YD = f"({YF} + 0.065)"  # front of the drum
    c.rev("Boca de carga", "Plan", [
        (f"{RH} - 0.006", f"{YF} - 0.001"), (f"{RH} + 0.004", f"{YF} - 0.001"), (f"{RH} + 0.004", f"{YF} + 0.013"), (f"{RM} + 0.012", f"{YD} - 0.004"),
        (f"{RM} + 0.002", f"{YD} - 0.004"),
    ], ZC, 0, "Plástico cinza claro")
    c.rev("Vedação de feltro", "Plan", [
        (f"{RM} - 0.004", f"{YD} - 0.008"), (f"{RM} + 0.012", f"{YD} - 0.008"), (f"{RM} + 0.012", f"{YD} - 0.002"), (f"{RM} - 0.004", f"{YD} - 0.002"),
    ], ZC, 0, "Borracha cinza", detail=FINE)
    # The lint filter sits across the bottom of the opening.
    FW = f"(0.50*{RH})"
    FZ = f"({ZC} - 0.90*{RH})"
    c.box("Filtro de fiapos - alojamento", f"-{FW} - 0.008", f"{YF} + 0.012", f"{ZC} - {RH} - 0.02", f"2*{FW} + 0.016", f"{YD} - {YF} - 0.016", f"0.10*{RH} + 0.02", "Plástico cinza claro")
    c.box("Filtro de fiapos", f"-{FW}", f"{YF} + 0.016", FZ, f"2*{FW}", f"{YD} - {YF} - 0.024", f"0.07*{RH}", "Plástico cinza")
    c.box("Filtro de fiapos - tela", f"-{FW} + 0.012", f"{YF} + 0.02", f"{FZ} + 0.07*{RH}", f"2*{FW} - 0.024", f"{YD} - {YF} - 0.032", 0.001, "Tela perfurada", detail=FINE)
    c.box("Filtro de fiapos - puxador", "-0.03", f"{YF} + 0.014", f"{FZ} + 0.07*{RH}", 0.06, 0.006, 0.012, "Plástico azul", detail=FINE)
    drum(c, ZC, RD, YD, "ProfundidadeTambor", RM, lifters=(30, 150, 270))
    # Hot air inlet on the back wall of the drum and the drum lamp.
    YD1 = f"({YD} + ProfundidadeTambor)"
    c.rev("Tambor - entrada de ar quente", "Plan", [
        (0.055, f"{YD1} - 0.006"), (f"0.52*{RD}", f"{YD1} - 0.006"), (f"0.52*{RD}", f"{YD1} - 0.003"), (0.055, f"{YD1} - 0.003"),
    ], ZC, 0, "Tela perfurada", detail=FINE)
    c.cyl_y("Lâmpada do tambor", f"0.45*{RM}", f"{ZC} + 0.78*{RM}", f"{YD} - 0.012", 0.012, 0.008, "Plástico translúcido", detail=FINE)
    c.cyl_y("Motor - polia tensora", 0, ZC, f"{YD1} + 0.004", 0.05, 0.02, "Alumínio fundido", detail=FINE)

    # --- door ---
    c.cyl("Dobradiça - pino", hinge[0], hinge[1], f"{ZC} - 0.06", 0.009, 0.12, "Cromado")
    c.box("Dobradiça - base", f"{hinge[0]} - 0.022", f"{YF} - 0.003", f"{ZC} - 0.07", 0.03, 0.003, 0.14, "Cromado")
    for i, dz in enumerate((-0.052, 0.052), 1):
        c.cyl_y(f"Dobradiça - parafuso {i}", f"{hinge[0]} - 0.014", f"{ZC} + {num(dz)}", f"{YF} - 0.004", 0.003, 0.001, "Aço galvanizado", detail=FINE)
    porthole_door(c, "Porta", hinge, ZC, RP, ang, [
        ("aro", "Branco", DOOR_RING, 44, FULL, True),
        ("moldura do vidro", dark, DOOR_TRIM, 28, FULL, True),
        ("vidro", "Vidro fumê", DOOR_GLASS, 14, FULL, "open"),
    ])
    door_part(c, "Porta - braço da dobradiça", hinge, ang, RP, -1.045, -0.90, 0.004, 0.06, ZC, -0.19, 0.19, "Cromado")
    door_part(c, "Porta - puxador", hinge, ang, RP, 0.84, 1.03, 0.03, 0.125, ZC, -0.30, 0.30, "Branco")
    door_part(c, "Porta - puxador - pega", hinge, ang, RP, 0.90, 1.032, 0.05, 0.127, ZC, -0.24, 0.24, "Plástico cinza claro", detail=FINE)
    door_part(c, "Porta - trinco", hinge, ang, RP, 0.85, 0.89, -0.07, 0.01, ZC, -0.035, 0.035, "Cromado", detail=FINE)
    c.box("Fecho da porta", f"0.84*{RP}", f"{YF} - 0.0008", f"{ZC} - 0.02", f"0.06*{RP}", 0.0008, 0.04, "Plástico preto", detail=FINE)

    # --- back ---
    c.box("Tampa traseira", "-0.38*Largura", YB, f"{ZC} - 0.30*Largura", "0.76*Largura", 0.002, "0.72*Largura", "Aço galvanizado")
    k = 0
    for sx in (-1, 0, 1):
        for sz in (-0.28, 0.40):
            k += 1
            c.cyl_y(f"Tampa traseira - parafuso {k}", f"{num(0.36 * sx)}*Largura", f"{ZC} + {num(sz)}*Largura", f"{YB} + 0.002", 0.004, 0.0015, "Aço galvanizado", detail=FINE)
    # Round air intake cover of the heater.
    AZ = f"({ZC} + 0.08*Largura)"
    c.rev("Entrada de ar traseira", "Plan", [(0, f"{YB} + 0.002"), ("0.26*Largura", f"{YB} + 0.002"), ("0.24*Largura", f"{YB} + 0.016"), (0, f"{YB} + 0.016")], AZ, 0, "Aço galvanizado")
    for i in range(9):
        z = (i - 4) * 0.045
        half = math.sqrt(0.21 ** 2 - z ** 2)
        c.box(f"Entrada de ar traseira - fresta {i + 1}", f"{num(-half)}*Largura", f"{YB} + 0.016", f"{AZ} + {num(z)}*Largura - 0.004", f"{num(2 * half)}*Largura", 0.0005, 0.008, "Aço pintado preto", detail=FINE)
    # Exhaust outlet: a collar that reaches the wall.
    EX, EZ = f"(-{W2} + 0.13)", f"({Z0} + 0.10)"
    c.rev("Saída de exaustão - colar", "Plan", [
        (f"{EX} + 0.046", f"{YB} - 0.001"), (f"{EX} + 0.058", f"{YB} - 0.001"), (f"{EX} + 0.058", f"{YB} + 0.004"), (f"{EX} + 0.051", f"{YB} + 0.004"),
        (f"{EX} + 0.051", YW), (f"{EX} + 0.048", YW), (f"{EX} + 0.046", f"{YB} + 0.004"),
    ], EZ, EX, "Plástico cinza claro")
    c.cyl_y("Saída de exaustão - fundo", EX, EZ, f"{YB} - 0.001", 0.047, 0.002, "Aço pintado preto", detail=FINE)
    for i in range(3):
        c.rev(f"Saída de exaustão - anel {i + 1}", "Plan", [
            (f"{EX} + 0.051", f"{YB} + {num(0.009 + 0.006 * i)}"), (f"{EX} + 0.053", f"{YB} + {num(0.009 + 0.006 * i)}"),
            (f"{EX} + 0.053", f"{YB} + {num(0.012 + 0.006 * i)}"), (f"{EX} + 0.051", f"{YB} + {num(0.012 + 0.006 * i)}"),
        ], EZ, EX, "Plástico cinza claro", detail=FINE)
    # Condensate drain hose (optional connection), looped and clipped to the back.
    OX, OZ = f"({W2} - 0.12)", f"({Z0} + 0.06)"
    HY = f"({YB} + 0.012)"
    c.cyl_y("Dreno de condensado - bocal", OX, OZ, f"{YB} - 0.001", 0.01, 0.006, "Plástico cinza")
    sphere(c, "Mangueira de condensado - curva 1", OX, HY, OZ, 0.007, "Plástico translúcido")
    c.cyl("Mangueira de condensado", OX, HY, OZ, 0.007, "0.30*Altura", "Plástico translúcido", detail=FINE)
    sphere(c, "Mangueira de condensado - curva 2", OX, HY, f"{OZ} + 0.30*Altura", 0.007, "Plástico translúcido")
    c.cyl_x("Mangueira de condensado - retorno", HY, f"{OZ} + 0.30*Altura", f"{OX} - 0.06", 0.007, 0.06, "Plástico translúcido", detail=FINE)
    c.box("Mangueira de condensado - presilha", f"{OX} - 0.012", YB, f"{OZ} + 0.15*Altura", 0.024, 0.021, 0.01, "Plástico cinza claro", detail=FINE)
    c.cyl_y("Mangueira de condensado - tampão", f"{OX} - 0.06", f"{OZ} + 0.30*Altura", f"{YB} - 0.001", 0.01, 0.022, "Plástico cinza", detail=FINE)
    for i in range(6):
        c.box(f"Ventilação traseira {i + 1}", "0.02*Largura", f"{YB} + 0.0005", f"{Z0} + 0.03 + {num(0.011 * i)}", "0.2*Largura", 0.0005, 0.005, "Aço pintado preto", detail=FINE)
    c.box("Etiqueta de identificação", f"-{W2} + 0.05", f"{YB} + 0.0005", f"{ZT} - 0.065", 0.1, 0.0005, 0.045, "Plástico cinza claro", detail=FINE)
    # Power cable.
    CX, CZ = f"({W2} - 0.05)", "(Altura - 0.07)"
    c.cyl_y("Cabo de força - passa-fio", CX, CZ, f"{YB} - 0.001", 0.009, 0.01, "Plástico preto")
    sphere(c, "Cabo de força - curva", CX, f"{YB} + 0.009", CZ, 0.0045, "Borracha")
    c.cyl("Cabo de força", CX, f"{YB} + 0.009", f"{CZ} - 0.40", 0.0045, 0.40, "Borracha", detail=FINE)
    c.box("Cabo de força - plugue", f"{CX} - 0.018", f"{YB} + 0.001", f"{CZ} - 0.445", 0.036, 0.018, 0.045, "Plástico preto", detail=FINE)
    for i, dx in enumerate((-0.0095, 0, 0.0095), 1):
        c.cyl(f"Cabo de força - pino {i}", f"{CX} + {num(dx)}", f"{YB} + 0.01", f"{CZ} - 0.463", 0.002, 0.018, "Latão", detail=FINE)

    c.type("Secadora 10 kg 60 x 65 x 85 cm", "Secadora de roupas de piso por condensação, 10 kg; prever TUE de 2000 VA e ventilação do ambiente")
    c.type("Secadora 8 kg compacta 60 x 56 x 85 cm", "Secadora de roupas de piso compacta, 8 kg; prever TUE de 1600 VA e ventilação do ambiente",
           Profundidade=0.56, ProfundidadeTambor=0.36, DiametroTambor=0.52)
    return c
