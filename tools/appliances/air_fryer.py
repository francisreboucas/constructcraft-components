"""Air fryer: corpo arredondado, painel digital no topo, gaveta deslizante com cesto e grelha, resistência e ventilador na cavidade."""

import math

from kit import *


def cabo(c, x, y, z, comprimento=0.14):
    """Passa-cabo na traseira (y), cabo que desce até a bancada e corre ao longo dela, com plugue."""
    r = 0.003
    c.cyl_y("Passa-cabo", x, z, y, 0.006, 0.014, "Borracha", detail=FINE)
    c.cyl_y("Cabo elétrico - saída", x, z, f"{p(y)} + 0.014", r, 0.014, "Borracha", detail=FINE)
    c.cyl("Cabo elétrico - descida", x, f"{p(y)} + 0.026", r, r, f"{p(z)} - {r}", "Borracha", detail=FINE)
    c.cyl_x("Cabo elétrico - trecho na bancada", f"{p(y)} + 0.026", r, f"{p(x)} - {comprimento}", r, comprimento, "Borracha", detail=FINE)
    c.box("Plugue - corpo", f"{p(x)} - {comprimento} - 0.034", f"{p(y)} + 0.026 - 0.017", 0, 0.034, 0.034, 0.016, "Plástico preto", detail=FINE)
    for i, dy in enumerate((-0.0095, 0.0095), 1):
        c.cyl_x(f"Plugue - pino {i}", f"{p(y)} + 0.026 + {dy}", 0.008, f"{p(x)} - {comprimento} - 0.052", 0.002, 0.018, "Latão", detail=FINE)


def polar(radius, deg, dy="0"):
    """Ponto (x, y) no raio `radius` (expressão) e ângulo `deg` (0 = +X, 90 = fundo)."""
    cs, sn = round(math.cos(math.radians(deg)), 5), round(math.sin(math.radians(deg)), 5)
    y = f"{p(radius)}*{sn}" if dy == "0" else f"{p(radius)}*{sn} + {p(dy)}"
    return (f"{p(radius)}*{cs}", y)


def setor(r_out, r_in, a0, a1, dy="0", n=12):
    """Contorno em planta de um setor de anel de a0 a a1 graus (anti-horário): arcos por fora, poligonal por dentro."""
    passos = max(1, math.ceil((a1 - a0) / 65))
    pts = []
    for i in range(passos + 1):
        ang = a0 + (a1 - a0) * i / passos
        x, y = polar(r_out, ang, dy)
        pts.append((x, y, r_out) if i < passos else (x, y))
    for i in range(n + 1):
        pts.append(polar(r_in, a1 + (a0 - a1) * i / n, dy))
    return pts


def build():
    c = Component("Air fryer", "furniture", "air-fryer")
    D = c.param("Diametro", 0.27)
    H = c.param("Altura", 0.32)
    AG = c.param("AberturaGaveta", 0, "Length", True)
    c.open_pose["AberturaGaveta"] = 0.16

    corpo, brilho = "Plástico preto", "Plástico preto brilhante"
    R = f"({D}/2)"
    zA = "0.050"  # piso da cavidade
    zB = f"({H}*0.62)"  # teto da cavidade
    zC = f"({H}*0.74)"
    dy = f"(-{AG})"

    # --- volumes simplificados ---------------------------------------------
    c.rev("Corpo simplificado", "Front", [(0, 0), (f"{R}*0.82", 0), (R, zA), (R, zC), (f"{R}*0.62", H), (0, H)], 0, 0, corpo, detail=COARSE, in_plan=True)
    zh = f"({zA} + ({zB} - {zA})*0.56)"
    c.box("Puxador simplificado", -0.018, f"-{R} - 0.085 - {AG}", f"{zh} - 0.018", 0.036, 0.087, 0.038, corpo, detail=COARSE, in_plan=True)

    # --- corpo ----------------------------------------------------------------
    c.rev("Base", "Front", [(0, 0.008), (f"{R}*0.82", 0.008, f"{zA}*1.3"), (R, zA), (0, zA)], 0, 0, corpo)
    c.rev("Base - fundo", "Front", rect(0, 0.005, f"{R}*0.80", 0.008), 0, 0, "Plástico cinza")
    c.profile("Corpo - parede da cavidade", "Plan", setor(R, f"({R} - 0.012)", -35, 215, n=30), zA, f"{zB} - {zA}", corpo)
    c.rev("Corpo superior", "Front", [(0, zB), (R, zB), (R, zC, f"{H}*0.36"), (f"{R}*0.62", H), (0, H)], 0, 0, corpo, in_plan=True)
    c.rev("Friso do corpo", "Front", rect(f"{R} - 0.002", f"{zB} + 0.001", f"{R} + 0.0012", f"{zB} + 0.005"), 0, 0, "Inox escovado")
    for i in range(4):
        ang = 45 + 90 * i
        x, y = polar(f"({R}*0.62)", ang)
        c.cyl(f"Pé antiderrapante {i + 1}", x, y, 0, 0.011, 0.006, "Borracha")
    for i in range(5):
        c.box(f"Ventilação inferior {i + 1}", f"-{R}*0.3", f"{-0.024 + 0.012 * i}", 0.0043, f"{R}*0.6", 0.005, 0.001, "Tela perfurada", detail=FINE)
    c.box("Etiqueta de identificação", f"-{R}*0.25", f"{R}*0.42", 0.0044, f"{R}*0.5", f"{R}*0.2", 0.0008, "Alumínio anodizado", detail=FINE)

    # --- cavidade: teto refletor, ventilador, resistência -------------------
    c.cyl("Cavidade - teto refletor", 0, 0, f"{zB} - 0.002", f"{R} - 0.013", 0.0015, "Inox escovado")
    c.box("Cavidade - piso", f"-{R}*0.6", f"-{R}*0.6", zA, f"{R}*1.2", f"{R}*1.2", 0.001, "Aço galvanizado", detail=FINE)
    c.cyl("Ventilador - cubo", 0, 0, f"{zB} - 0.020", 0.014, 0.018, "Alumínio fundido")
    for i in range(6):
        a0 = 60 * i
        pts = [polar("0.012", a0 - 20), polar(f"({R}*0.40)", a0 - 8), polar(f"({R}*0.40)", a0 + 14), polar("0.012", a0 + 20)]
        c.profile(f"Ventilador - pá {i + 1}", "Plan", pts, f"{zB} - 0.018", 0.010, "Alumínio anodizado")
    zr = f"({zB} - 0.034)"
    for i, k in enumerate((0.30, 0.48, 0.66), 1):
        c.rev(f"Resistência - espira {i}", "Front", disc(f"{R}*{k}", zr, 0.004), 0, 0, "Aço pintado preto")
    c.box("Resistência - ligação entre espiras", f"{R}*0.30", -0.004, f"{zr} - 0.004", f"{R}*0.36", 0.008, 0.008, "Aço pintado preto", detail=FINE)
    for i, sx in enumerate((-1, 1), 1):
        c.cyl(f"Resistência - terminal {i}", f"{sx}*0.012", f"{R}*0.66", zr, 0.004, f"{zB} - {zr}", "Aço pintado preto", detail=FINE)
        c.cyl(f"Resistência - suporte {i}", f"{sx}*{R}*0.48", 0, zr, 0.0025, f"{zB} - {zr}", "Inox escovado", detail=FINE)
    c.cyl_y("Sensor de temperatura", f"{R}*0.3", f"{zB} - 0.05", f"{R} - 0.030", 0.003, 0.018, "Inox escovado", detail=FINE)
    c.box("Interruptor de segurança da gaveta", -0.010, f"{R} - 0.020", f"{zA} + 0.030", 0.020, 0.008, 0.012, "Branco", detail=FINE)
    for i, sx in enumerate((-1, 1), 1):
        c.box(f"Guia da gaveta {i}", f"{sx}*{R}*0.5 - 0.004", f"-{R}*0.6", f"{zA} + 0.001", 0.008, f"{R}*1.2", 0.003, "Plástico cinza", detail=FINE)

    # --- painel superior --------------------------------------------------------
    rp = f"({R}*0.54)"
    c.cyl("Painel superior", 0, 0, H, rp, 0.0015, brilho, in_plan=True)
    c.rev("Painel superior - aro", "Front", rect(rp, f"{H} - 0.001", f"{rp} + 0.003", f"{H} + 0.0022"), 0, 0, "Cromado")
    zp = f"({H} + 0.0015)"
    c.box("Visor", f"-{R}*0.21", f"{R}*0.09", zp, f"{R}*0.42", f"{R}*0.17", 0.0005, "Visor LED")
    for i, kx in enumerate((-0.14, -0.06, 0.04, 0.12), 1):
        c.box(f"Visor - dígito {i}", f"{R}*{kx}", f"{R}*0.12", f"{zp} + 0.0005", f"{R}*0.05", f"{R}*0.11", 0.0003, "Plástico azul", detail=FINE)
    nomes = ["Batata frita", "Frango", "Carne", "Peixe", "Legumes", "Bolo", "Pizza", "Reaquecer"]
    for i, nome in enumerate(nomes):
        kx, ky = (-0.27, -0.09, 0.09, 0.27)[i % 4], (-0.07, -0.24)[i // 4]
        c.cyl(f"Tecla {nome}", f"{R}*{kx}", f"{R}*{ky}", zp, 0.0065, 0.0005, "Teclado", detail=FINE)
        c.cyl(f"Tecla {nome} - ícone", f"{R}*{kx}", f"{R}*{ky}", f"{zp} + 0.0005", 0.003, 0.0003, "Branco", detail=FINE)
    for nome, kx, ky in (("Temperatura +", 0.36, 0.25), ("Temperatura -", 0.36, 0.11), ("Tempo +", -0.36, 0.25), ("Tempo -", -0.36, 0.11)):
        c.cyl(f"Tecla {nome}", f"{R}*{kx}", f"{R}*{ky}", zp, 0.006, 0.0005, "Teclado", detail=FINE)
    c.cyl("Tecla Liga/Desliga - aro", 0, f"-{R}*0.41", zp, 0.009, 0.0005, "Plástico vermelho", detail=FINE)
    c.cyl("Tecla Liga/Desliga", 0, f"-{R}*0.41", zp, 0.007, 0.0008, "Teclado", detail=FINE)

    # --- traseira: saída de ar e cabo -----------------------------------------
    z0, z1 = f"({zB} + 0.010)", f"({zC} - 0.002)"
    c.profile("Saída de ar - moldura", "Plan", setor(f"({R} + 0.010)", f"({R} - 0.004)", 58, 122, n=8), z0, f"{z1} - {z0}", corpo, in_plan=True)
    for i in range(9):
        ang = 62 + 7 * i
        x, y = polar(f"({R} + 0.0095)", ang)
        c.box(f"Saída de ar - fenda {i + 1}", f"{x} - 0.003", f"{y} - 0.001", f"{z0} + 0.004", 0.006, 0.0025, f"{z1} - {z0} - 0.008", "Tela perfurada", detail=FINE)
    cabo(c, f"{R}*0.3", f"{R}*0.93", 0.030)

    # --- gaveta (desliza para a frente com AberturaGaveta) -------------------
    zg0, zg1 = f"({zA} + 0.003)", f"({zB} - 0.003)"
    c.profile("Gaveta - frente", "Plan", setor(f"({R} + 0.0015)", f"({R} - 0.010)", -144, -36, dy=dy, n=10), zg0, f"{zg1} - {zg0}", brilho)
    Rg = f"({R} - 0.016)"
    zp0, zp1 = f"({zA} + 0.005)", f"({zB} - 0.046)"
    c.rev("Gaveta - cuba", "Front", [(0, zp0), (f"{Rg} - 0.010", zp0), (Rg, f"{zp0} + 0.010"), (Rg, zp1), (f"{Rg} - 0.003", zp1),
                                     (f"{Rg} - 0.003", f"{zp0} + 0.011"), (f"{Rg} - 0.011", f"{zp0} + 0.003"), (0, f"{zp0} + 0.003")], dy, 0, "Aço pintado preto")
    Rb = f"({Rg} - 0.007)"
    zb0 = f"({zp0} + 0.012)"
    c.rev("Cesto", "Front", [(0, zb0), (f"{Rb} - 0.008", zb0), (Rb, f"{zb0} + 0.008"), (Rb, f"{zp1} + 0.002"), (f"{Rb} + 0.006", f"{zp1} + 0.002"),
                             (f"{Rb} + 0.006", f"{zp1} + 0.005"), (f"{Rb} - 0.002", f"{zp1} + 0.005"), (f"{Rb} - 0.002", f"{zb0} + 0.009"),
                             (f"{Rb} - 0.009", f"{zb0} + 0.002"), (0, f"{zb0} + 0.002")], dy, 0, "Aço pintado cinza")
    zgr = f"({zb0} + 0.022)"
    c.rev("Grelha perfurada", "Front", rect(0, zgr, f"{Rb} - 0.004", f"{zgr} + 0.003"), dy, 0, "Alumínio fundido")
    n = 0
    for iy in range(-3, 4):
        half = 3 - abs(iy) // 2 if abs(iy) < 3 else 1
        for ix in range(-half, half + 1):
            n += 1
            c.box(f"Grelha perfurada - fenda {n}", f"{Rb}*{round(0.24 * ix, 3)} - {Rb}*0.09", f"{Rb}*{round(0.24 * iy, 3)} - 0.003 - {AG}", f"{zgr} + 0.003",
                  f"{Rb}*0.18", 0.006, 0.0004, "Borracha", detail=FINE)
    for i in range(3):
        x, y = polar(f"({Rb} - 0.006)", 90 + 120 * i, dy)
        c.cyl(f"Grelha perfurada - batente de silicone {i + 1}", x, y, f"{zgr} - 0.002", 0.005, 0.007, "Borracha cinza", detail=FINE)
    c.cyl("Grelha perfurada - pega", 0, dy, f"{zgr} + 0.003", 0.008, 0.012, "Alumínio fundido", detail=FINE)
    c.box("Cesto - marca de nível máximo", -0.012, f"{Rb} - 0.003 - {AG}", f"{zp1} - 0.020", 0.024, 0.0015, 0.002, "Branco", detail=FINE)
    # puxador
    yF = f"(-{R} - {AG})"
    c.profile("Puxador", "Side", [(f"{yF} + 0.006", f"{zh} - 0.020"), (f"{yF} + 0.006", f"{zh} + 0.020"), (f"{yF} - 0.073", f"{zh} + 0.020", 0.012),
                                  (f"{yF} - 0.085", f"{zh} + 0.008"), (f"{yF} - 0.085", f"{zh} - 0.002"), (f"{yF} - 0.030", f"{zh} - 0.020")],
              -0.018, 0.036, corpo, in_plan=True)
    c.profile("Puxador - base de fixação", "Side", rect(f"{yF} - 0.004", f"{zh} - 0.032", f"{yF} + 0.006", f"{zh} + 0.030"), -0.026, 0.052, corpo)
    c.box("Puxador - friso", -0.012, f"{yF} - 0.070", f"{zh} + 0.020", 0.024, 0.030, 0.0008, "Inox escovado", detail=FINE)
    c.box("Botão de liberação do cesto", -0.008, f"{yF} - 0.034", f"{zh} + 0.020", 0.016, 0.022, 0.004, "Plástico vermelho", detail=FINE)
    c.box("Proteção do botão de liberação", -0.011, f"{yF} - 0.037", f"{zh} + 0.020", 0.022, 0.028, 0.007, "Plástico translúcido", detail=FINE)
    for i, sx in enumerate((-1, 1), 1):
        c.cyl_y(f"Parafuso do puxador {i}", f"{sx}*0.010", f"{zh} - 0.006", f"{yF} + 0.009 + 0.0005", 0.003, 0.002, "Aço", detail=FINE)

    c.preview_size = (0.27, 0.36, 0.32)
    c.type("Air fryer 4 L", "Fritadeira elétrica sem óleo de 4 litros, com painel digital e gaveta com cesto antiaderente")
    c.type("Air fryer 7 L", "Fritadeira elétrica sem óleo de 7 litros, com painel digital e gaveta com cesto antiaderente", Diametro=0.33, Altura=0.37)
    return c
