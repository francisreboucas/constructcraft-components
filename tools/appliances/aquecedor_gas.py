"""Aquecedor de água a gás de passagem (exaustão forçada), de parede.

Wall-mounted frame: the back on the wall at y = 0, the front at
y = -Profundidade. The cold-water, gas and hot-water stubs hang under the
cabinet and end at z = 0 (the app applies the mounting height); the cabinet
starts `AlturaConexoes` above them and the flue collar stands on its top.
"""

import math

from kit import *
from _aparelhos import num, sphere


def build() -> Component:
    c = Component("Aquecedor a gás de passagem", "plumbing", "aquecedor-gas", "Plumbing")
    W = c.param("Largura", 0.35)
    D = c.param("Profundidade", 0.16)
    H = c.param("Altura", 0.55)
    AL = c.param("AlturaConexoes", 0.08)
    DCh = c.param("DiametroChamine", 0.06)
    ACo = c.param("AlturaColar", 0.05)

    c.material("Aço pintado amarelo", (226, 184, 44), "Metal", "Satin")
    white, dark, galv = "Aço pintado branco", "Plástico preto brilhante", "Aço galvanizado"
    xl, xr = f"(-{W}/2)", f"({W}/2)"
    yf = f"(-{D})"
    Z0, Z1 = AL, f"({AL} + {H})"  # bottom and top of the cabinet
    yb = -0.01  # back of the front cover (the back plate fills the rest)
    YS = f"(-{D}*0.45)"  # plane of the stubs
    RCh = f"({DCh}/2)"
    stubs = [("Saída de água quente", f"(-{W}*0.3)", "Plástico vermelho"), ("Entrada de gás", "0", "Aço pintado amarelo"), ("Entrada de água fria", f"({W}*0.3)", "Plástico azul")]

    # --- coarse ---------------------------------------------------------------
    c.box("Gabinete simplificado", xl, yf, Z0, W, D, H, white, detail=COARSE, in_plan=True)
    c.cyl("Colar simplificado", 0, f"-{D}/2", Z1, RCh, ACo, "Aço galvanizado", detail=COARSE)
    for name, x, _ in stubs:
        c.cyl(f"{name} simplificada", x, YS, 0, 0.012, Z0, "Latão", detail=COARSE)

    # --- cabinet ------------------------------------------------------------------
    c.box("Chapa traseira", f"{xl} + 0.005", yb, Z0, f"{W} - 0.01", -yb, H, galv)
    for name, z in (("superior", f"{Z1} - 0.005"), ("inferior", f"{Z0} - 0.025")):
        c.box(f"Aba de fixação {name}", -0.04, -0.0015, z, 0.08, 0.0015, 0.03, galv)
        c.cyl_y(f"Aba de fixação {name} - parafuso", 0, f"{z} + 0.015", -0.004, 0.005, 0.0025, "Cromado", detail=FINE)
    c.profile("Tampa frontal", "Front", rrect(xl, Z0, xr, Z1, 0.025), yf, f"{D} + {yb}", white, in_plan=True)
    c.box("Tampa frontal - friso de vedação", f"{xl} + 0.004", f"{yb} - 0.002", f"{Z0} + 0.004", f"{W} - 0.008", 0.002, f"{H} - 0.008", "Borracha cinza", detail=FINE)
    # Sides: louvres at the top.
    for name, x in (("esquerda", f"{xl} - 0.0006"), ("direita", xr)):
        for i in range(6):
            c.box(f"Ventilação lateral {name} {i + 1}", x, f"{yf} + 0.025", f"{Z1} - 0.05 - {i}*0.014", 0.0006, f"{D} - 0.05", 0.006, "Aço pintado preto", detail=FINE)
    # Front face: brand plate, flame sight glass, control panel.
    c.profile("Placa frontal", "Front", rrect(f"-{W}*0.42", f"{Z1} - 0.075", f"{W}*0.42", f"{Z1} - 0.03", 0.01), f"{yf} - 0.0012", 0.0012, "Inox escovado")
    c.box("Placa frontal - inscrição", f"-{W}*0.18", f"{yf} - 0.0015", f"{Z1} - 0.057", f"{W}*0.36", 0.0003, 0.01, "Aço pintado preto", detail=FINE)
    zv = f"({Z0} + {H}*0.55)"
    c.cyl_y("Visor da chama - aro", 0, zv, f"{yf} - 0.003", 0.018, 0.003, "Cromado")
    c.cyl_y("Visor da chama - vidro", 0, zv, f"{yf} - 0.0035", 0.012, 0.001, "Vidro fumê")
    c.cyl_y("Visor da chama - chama", 0, f"{zv} - 0.004", f"{yf} - 0.0005", 0.004, 0.0005, "Plástico azul", detail=FINE)
    zp0, zp1 = f"({Z0} + 0.06)", f"({Z0} + 0.06 + {H}*0.3)"
    zpm = f"(({zp0} + {zp1})/2)"
    c.profile("Painel de comando", "Front", rrect(f"-{W}*0.38", zp0, f"{W}*0.38", zp1, 0.015), f"{yf} - 0.003", 0.003, dark)
    c.box("Visor", f"-{W}*0.16", f"{yf} - 0.0035", f"{zp1} - 0.065", f"{W}*0.32", 0.0005, 0.045, "Visor LCD")
    for i in range(2):
        c.box(f"Visor - dígito {i + 1}", f"-{W}*0.1 + {i}*{W}*0.1", f"{yf} - 0.0038", f"{zp1} - 0.058", f"{W}*0.08", 0.0003, 0.03, "Aço pintado preto", detail=FINE)
    c.box("Visor - unidade", f"{W}*0.11", f"{yf} - 0.0038", f"{zp1} - 0.035", 0.008, 0.0003, 0.008, "Aço pintado preto", detail=FINE)
    c.box("Visor - indicador de chama", f"{W}*0.11", f"{yf} - 0.0038", f"{zp1} - 0.056", 0.008, 0.0003, 0.012, "Aço pintado preto", detail=FINE)
    # Knobs: water temperature (left) and winter / summer power (right).
    zk = f"({zp0} + 0.035)"
    for name, kx in (("temperatura", f"-{W}*0.22"), ("potência", f"{W}*0.22")):
        c.rev(f"Botão de {name} - base", "Plan", [(kx, f"{yf} - 0.006"), (f"{kx} + 0.026", f"{yf} - 0.006"), (f"{kx} + 0.026", f"{yf} - 0.003"), (kx, f"{yf} - 0.003")],
              zk, kx, "Cromado")
        c.rev(f"Botão de {name}", "Plan", [(kx, f"{yf} - 0.026"), (f"{kx} + 0.018", f"{yf} - 0.026"), (f"{kx} + 0.021", f"{yf} - 0.022"), (f"{kx} + 0.022", f"{yf} - 0.006"),
                                          (kx, f"{yf} - 0.006")], zk, kx, "Plástico cinza claro")
        c.box(f"Botão de {name} - pega", f"{kx} - 0.004", f"{yf} - 0.034", f"{zk} - 0.017", 0.008, 0.01, 0.034, "Plástico cinza claro")
        c.box(f"Botão de {name} - marca", f"{kx} - 0.001", f"{yf} - 0.0345", f"{zk} + 0.008", 0.002, 0.0005, 0.008, "Plástico vermelho", detail=FINE)
        for i in range(7):
            g = math.radians(210 - 40 * i)
            c.box(f"Botão de {name} - escala {i + 1}", f"{kx} + {num(0.03 * math.cos(g))} - 0.001", f"{yf} - 0.0034", f"{zk} + {num(0.03 * math.sin(g))} - 0.001",
                  0.002, 0.0003, 0.002, "Branco", detail=FINE)
    c.cyl_y("Tecla liga-desliga - aro", 0, zk, f"{yf} - 0.0045", 0.013, 0.0015, "Cromado", detail=FINE)
    c.cyl_y("Tecla liga-desliga", 0, zk, f"{yf} - 0.0075", 0.01, 0.003, "Teclado")
    c.cyl_y("Tecla liga-desliga - símbolo", 0, zk, f"{yf} - 0.0078", 0.004, 0.0003, "Branco", detail=FINE)
    c.cyl_y("Luz de funcionamento", 0, f"{zk} + 0.022", f"{yf} - 0.0038", 0.0025, 0.0008, "Plástico verde", detail=FINE)
    for i, x in enumerate((f"{xl} + 0.03", f"{xr} - 0.03"), 1):
        c.cyl("Tampa frontal - parafuso {}".format(i), x, f"{yf} + 0.02", f"{Z0} - 0.0015", 0.004, 0.0015, "Cromado", detail=FINE)

    # --- top: flue collar --------------------------------------------------------
    yc = f"(-{D}/2)"
    c.profile("Colar - flange", "Plan", rrect(f"-{RCh} - 0.02", f"{yc} - {RCh} - 0.02", f"{RCh} + 0.02", f"{yc} + {RCh} + 0.02", 0.01), Z1, 0.003, galv)
    c.rev("Colar da chaminé", "Front", rect(f"{RCh} - 0.0015", f"{Z1} + 0.003", RCh, f"{Z1} + {ACo}"), yc, 0, galv, in_plan=True)
    c.rev("Colar da chaminé - vedação", "Front", rect(RCh, f"{Z1} + {ACo} - 0.02", f"{RCh} + 0.002", f"{Z1} + {ACo} - 0.012"), yc, 0, "Borracha", detail=FINE)
    c.cyl("Colar da chaminé - boca do exaustor", 0, yc, f"{Z1} + 0.003", f"{RCh} - 0.0015", 0.002, "Aço pintado preto")
    for i in range(4):
        g = math.radians(45 + 90 * i)
        c.cyl(f"Colar - parafuso {i + 1}", f"({RCh} + 0.012)*{num(math.cos(g))}", f"{yc} + ({RCh} + 0.012)*{num(math.sin(g))}", f"{Z1} + 0.003", 0.003, 0.0015, "Cromado", detail=FINE)
    c.box("Etiqueta de advertência", f"-{W}*0.3", f"{yf} + 0.01", Z1, f"{W}*0.15", f"{D}*0.4", 0.0004, "Plástico cinza claro", detail=FINE)

    # --- bottom: air intake, stubs, drain, power cable -----------------------------
    for i in range(8):
        c.box(f"Entrada de ar {i + 1}", f"-{W}*0.42 + {i}*0.012", f"{yf} + 0.02", f"{Z0} - 0.0005", 0.006, f"{D}*0.25", 0.0005, "Aço pintado preto", detail=FINE)
    for name, x, color in stubs:
        c.cyl(f"{name} - sextavado", x, YS, f"{Z0} - 0.018", 0.0125, 0.018, "Latão")
        c.cyl(f"{name} - tubo", x, YS, 0.016, 0.0095, f"{Z0} - 0.034", "Cobre" if name != "Entrada de gás" else "Latão")
        c.cyl(f"{name} - porca", x, YS, 0, 0.0125, 0.016, "Latão")
        c.cyl(f"{name} - anel de identificação", x, YS, f"{Z0} - 0.026", 0.0105, 0.006, color, detail=FINE)
    c.cyl("Registro de água fria - corpo", f"{W}*0.3", f"{YS} - 0.014", f"{Z0}*0.45", 0.006, 0.012, "Latão", detail=FINE)
    c.box("Registro de água fria - alavanca", f"{W}*0.3 - 0.004", f"{YS} - 0.05", f"{Z0}*0.45 + 0.004", 0.008, 0.038, 0.004, "Plástico azul", detail=FINE)
    c.cyl("Dreno", f"{W}*0.17", YS, f"{Z0} - 0.012", 0.006, 0.012, "Plástico cinza", detail=FINE)
    c.box("Dreno - pega", f"{W}*0.17 - 0.006", f"{YS} - 0.0015", f"{Z0} - 0.018", 0.012, 0.003, 0.006, "Plástico cinza", detail=FINE)
    CX = f"({xr} - 0.03)"
    c.cyl("Cabo de alimentação - passa-fio", CX, -0.03, f"{Z0} - 0.008", 0.007, 0.008, "Borracha", detail=FINE)
    c.cyl("Cabo de alimentação", CX, -0.03, 0.036, 0.0035, f"{Z0} - 0.044", "Borracha", detail=FINE)
    c.box("Cabo de alimentação - plugue", f"{CX} - 0.017", -0.041, 0.002, 0.034, 0.022, 0.034, "Plástico preto", detail=FINE)
    for i, dx in enumerate((-0.0095, 0, 0.0095), 1):
        c.cyl_y(f"Cabo de alimentação - pino {i}", f"{CX} + {dx}", 0.016, -0.057, 0.002, 0.016, "Latão", detail=FINE)
    c.box("Etiqueta de identificação", f"{xl} - 0.0006", f"{yf} + 0.03", f"{Z0} + 0.08", 0.0006, f"{D} - 0.06", 0.06, "Alumínio anodizado", detail=FINE)

    hot, cold = stubs[0][1], stubs[2][1]
    c.connector("Água quente", "HotWater", hot, YS, 0, "Down", 0.02)
    c.connector("Água fria", "ColdWater", cold, YS, 0, "Down", 0.02)

    c.preview_size = (0.35, 0.3, 0.7)
    c.type("Aquecedor a gás 15 L/min", "Aquecedor de passagem a gás (GN ou GLP) com exaustão forçada, 15 L/min, 35 x 16 x 55 cm, chaminé Ø 60 mm; água fria, gás e água quente de 1/2\" por baixo; TUG 127 V")
    c.type("Aquecedor a gás 27 L/min", "Aquecedor de passagem a gás (GN ou GLP) com exaustão forçada, 27 L/min, 37 x 21 x 60 cm, chaminé Ø 80 mm; água fria, gás e água quente de 3/4\" por baixo; TUG 127 V",
           Largura=0.37, Profundidade=0.21, Altura=0.60, DiametroChamine=0.08)
    return c
