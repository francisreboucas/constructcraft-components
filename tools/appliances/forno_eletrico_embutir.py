"""Forno elétrico de embutir (60 cm e 90 cm) com porta basculante de vidro."""

import math

from kit import *


def build() -> Component:
    c = Component("Forno elétrico de embutir", "furniture", "forno-eletrico-embutir")

    W = c.param("Largura", 0.595)
    D = c.param("Profundidade", 0.57)
    H = c.param("Altura", 0.595)
    AP = c.param("AlturaPainel", 0.11)
    EP = c.param("EspessuraPorta", 0.04)
    FL = c.param("FolgaLateralGabinete", 0.0175)
    A = c.angle("AnguloPorta", 0, open_at=90)
    XG = c.param("ExtensaoGrade", 0.0, "Length", True)
    c.open_pose[XG] = 0.22

    xl, xr = f"(-{W}/2)", f"({W}/2)"
    yf, yb = f"(-{D}/2)", f"({D}/2)"
    hy = f"({yf} + {EP})"  # back face of the door and of the control panel
    z0 = 0.012  # bottom of the door
    hz = f"({z0} + {EP})"  # the hinge: the door's foot turns into the recess under the cavity
    hinge = (hy, hz)
    Hd = f"({H} - {AP} - {z0} - 0.004)"
    sb, st = f"(-{EP})", f"({Hd} - {EP})"  # the door along s
    zp = f"({H} - {AP})"  # bottom of the control panel

    # casing (narrower than the front) and cavity (inside faces)
    kxl, kxr = f"({xl} + {FL})", f"({xr} - {FL})"
    kw = f"({W} - 2*{FL})"
    ky0 = f"({hy} + 0.02)"
    kyr = f"({hy} + {EP} + 0.005)"  # behind the door's recess
    kyb = f"({yb} - 0.025)"
    kz1 = f"({H} - 0.012)"
    cxl, cxr = f"({xl} + 0.06)", f"({xr} - 0.06)"
    cw = f"({W} - 0.12)"
    cyf, cyb = ky0, f"({yb} - 0.09)"
    cd = f"({cyb} - {cyf})"
    cz0, cz1 = f"({hz} + 0.022)", f"({zp} - 0.03)"
    ch = f"({cz1} - {cz0})"
    zcm = f"(({cz0} + {cz1})/2)"

    inox, galv, enamel, black = "Inox escovado", "Aço galvanizado", "Esmalte do forno", "Aço pintado preto"

    # --- coarse ---------------------------------------------------------------
    c.box("Corpo simplificado", kxl, ky0, z0, kw, f"{yb} - {ky0}", f"{kz1} - {z0}", galv, detail=COARSE, in_plan=True)
    c.box("Painel simplificado", xl, yf, zp, W, f"{EP} + 0.02", AP, "Esmalte preto", detail=COARSE, in_plan=True)
    c.flap_box("Porta simplificada", hinge, A, xl, W, sb, st, 0, EP, "Esmalte preto", detail=COARSE, in_plan=True)

    # --- casing ---------------------------------------------------------------
    side = [(kyr, z0), (kyb, z0), (kyb, kz1), (ky0, kz1), (ky0, f"{hz} + 0.003"), (kyr, f"{hz} + 0.003")]
    c.profile("Gabinete - lateral esquerda", "Side", side, kxl, 0.002, galv)
    c.profile("Gabinete - lateral direita", "Side", side, f"{kxr} - 0.002", 0.002, galv)
    c.box("Gabinete - teto", kxl, ky0, f"{kz1} - 0.002", kw, f"{kyb} - {ky0}", 0.002, galv, in_plan=True)
    c.box("Gabinete - base", kxl, kyr, z0, kw, f"{kyb} - {kyr}", 0.002, galv)
    c.box("Gabinete - fundo", kxl, f"{kyb} - 0.002", z0, kw, 0.002, f"{kz1} - {z0}", galv)
    c.box("Travessa inferior", kxl, kyr, z0, kw, 0.004, f"{hz} + 0.003 - {z0}", black)
    for sx, nx in ((f"{kxl} + 0.04", "esquerdo"), (f"{kxr} - 0.04", "direito")):
        for sy, ny in ((f"{kyr} + 0.04", "frontal"), (f"{kyb} - 0.05", "traseiro")):
            c.cyl(f"Apoio {ny} {nx}", sx, sy, 0, 0.012, z0, "Plástico preto", detail=FINE)

    # Front flange around the cavity (as wide as the door).
    fz0 = f"({hz} + 0.003)"
    c.box("Moldura frontal esquerda", xl, hy, fz0, f"{cxl} - {xl}", 0.02, f"{zp} - {fz0}", enamel)
    c.box("Moldura frontal direita", cxr, hy, fz0, f"{xr} - {cxr}", 0.02, f"{zp} - {fz0}", enamel)
    c.box("Moldura frontal inferior", cxl, hy, fz0, cw, 0.02, f"{cz0} - {fz0}", enamel)
    c.box("Moldura frontal superior", cxl, hy, cz1, cw, 0.02, f"{zp} - {cz1}", enamel)
    g = 0.008
    c.box("Vedação da porta esquerda", f"{cxl} - 0.014", f"{hy} - 0.003", f"{cz0} - 0.006", g, 0.003, f"{ch} + 0.02", "Borracha cinza", detail=FINE)
    c.box("Vedação da porta direita", f"{cxr} + 0.006", f"{hy} - 0.003", f"{cz0} - 0.006", g, 0.003, f"{ch} + 0.02", "Borracha cinza", detail=FINE)
    c.box("Vedação da porta superior", f"{cxl} - 0.014", f"{hy} - 0.003", f"{cz1} + 0.006", f"{cw} + 0.028", 0.003, g, "Borracha cinza", detail=FINE)
    for i, (sx, fz) in enumerate(((f"{xl} + 0.025", 0.25), (f"{xl} + 0.025", 0.8), (f"{xr} - 0.025", 0.25), (f"{xr} - 0.025", 0.8))):
        c.cyl_y(f"Parafuso de fixação ao nicho {i + 1}", sx, f"{cz0} + {fz}*{ch}", f"{hy} - 0.0015", 0.005, 0.0015, "Cromado", detail=FINE)
    for sx, n in ((f"{xl} + 0.012", "esquerda"), (f"{xr} - 0.034", "direita")):
        c.box(f"Dobradiça {n} - caixa", sx, kyr, f"{z0} + 0.004", 0.022, 0.06, f"{EP} - 0.004", galv, detail=FINE)
        c.flap_box(f"Dobradiça {n} - braço", hinge, A, f"{sx} + 0.004", 0.014, f"-{EP}*0.5", 0.1, -0.012, 0.002, galv, detail=FINE)

    # --- cavity ---------------------------------------------------------------
    c.box("Cavidade - parede esquerda", f"{cxl} - 0.003", cyf, cz0, 0.003, cd, ch, enamel)
    c.box("Cavidade - parede direita", cxr, cyf, cz0, 0.003, cd, ch, enamel)
    c.box("Cavidade - fundo", f"{cxl} - 0.003", cyb, f"{cz0} - 0.003", f"{cw} + 0.006", 0.003, f"{ch} + 0.006", enamel)
    c.box("Cavidade - piso", f"{cxl} - 0.003", cyf, f"{cz0} - 0.003", f"{cw} + 0.006", cd, 0.003, enamel)
    c.box("Cavidade - teto", f"{cxl} - 0.003", cyf, cz1, f"{cw} + 0.006", cd, 0.003, enamel)

    # Convection fan cover on the back wall.
    rf = 0.105
    c.cyl_y("Tampa do ventilador", 0, zcm, f"{cyb} - 0.01", rf, 0.01, enamel)
    c.cyl_y("Tampa do ventilador - aro", 0, zcm, f"{cyb} - 0.012", rf * 0.42, 0.002, black, detail=FINE)
    c.cyl_y("Tampa do ventilador - parafuso central", 0, zcm, f"{cyb} - 0.014", 0.007, 0.002, "Cromado", detail=FINE)
    k = 0
    for dz in (-0.078, -0.06, 0.06, 0.078):
        k += 1
        half = math.sqrt(rf * rf - dz * dz) * 0.8
        c.box(f"Tampa do ventilador - fresta {k}", -half, f"{cyb} - 0.011", f"{zcm} + {dz} - 0.004", 2 * half, 0.001, 0.008, black, detail=FINE)
    for i, sx in enumerate((-0.08, -0.064, 0.064, 0.08)):
        k += 1
        half = math.sqrt(rf * rf - sx * sx) * 0.55
        c.box(f"Tampa do ventilador - fresta {k}", sx - 0.004, f"{cyb} - 0.011", f"{zcm} - {half}", 0.008, 0.001, 2 * half, black, detail=FINE)

    # Grill element under the ceiling.
    ze = f"({cz1} - 0.022)"
    ey0, ey1 = f"({cyf} + 0.07)", cyb
    bars = (-0.36, -0.14, 0.14, 0.36)
    for i, fx in enumerate(bars):
        c.box(f"Resistência superior - barra {i + 1}", f"{cw}*{fx} - 0.0035", ey0, ze, 0.007, f"{ey1} - {ey0}" if abs(fx) > 0.2 else f"{ey1} - {ey0} - 0.05", 0.007, black)
    c.box("Resistência superior - curva frontal esquerda", f"{cw}*-0.36 - 0.0035", f"{ey0} - 0.007", ze, f"{cw}*0.22 + 0.007", 0.007, 0.007, black)
    c.box("Resistência superior - curva frontal direita", f"{cw}*0.14 - 0.0035", f"{ey0} - 0.007", ze, f"{cw}*0.22 + 0.007", 0.007, 0.007, black)
    c.box("Resistência superior - curva traseira", f"{cw}*-0.14 - 0.0035", f"{ey1} - 0.05", ze, f"{cw}*0.28 + 0.007", 0.007, 0.007, black)
    for i, fx in enumerate((-0.25, 0.25)):
        c.box(f"Resistência superior - suporte {i + 1}", f"{cw}*{fx} - 0.003", f"{ey0} + 0.03", f"{ze} + 0.007", 0.006, 0.012, 0.015, galv, detail=FINE)
    # Lamp and temperature probe.
    c.cyl_y("Lâmpada - soquete", f"{cxl} + 0.06", f"{cz1} - 0.045", f"{cyb} - 0.006", 0.024, 0.006, galv)
    c.cyl_y("Lâmpada - lente", f"{cxl} + 0.06", f"{cz1} - 0.045", f"{cyb} - 0.022", 0.019, 0.016, "Vidro temperado")
    c.cyl_y("Sensor de temperatura", f"{cxr} - 0.05", f"{cz1} - 0.04", f"{cyb} - 0.05", 0.003, 0.05, "Cromado", detail=FINE)

    # Side rack guides: wire ladders with 4 levels.
    levels = [f"({cz0} + {ch}*{f})" for f in (0.14, 0.34, 0.54, 0.74)]
    for sx, n in ((f"{cxl} + 0.003", "esquerda"), (f"{cxr} - 0.008", "direita")):
        for j, y in enumerate((f"{cyf} + {cd}*0.15", f"{cyf} + {cd}*0.85")):
            c.box(f"Guia {n} - montante {j + 1}", sx, y, f"{levels[0]} - 0.03", 0.005, 0.005, f"{levels[3]} - {levels[0]} + 0.06", "Cromado")
        for j, z in enumerate(levels):
            c.box(f"Guia {n} - trilho {j + 1}", f"{sx} - 0.002" if n == "direita" else f"{sx} + 0.002", f"{cyf} + 0.02", z, 0.005, f"{cd} - 0.04", 0.005, "Cromado")

    # Wire racks on levels 2 and 4 (the upper one slides with ExtensaoGrade).
    rxl, rw = f"({cxl} + 0.006)", f"({cw} - 0.012)"
    rl = f"({cd} - 0.03)"
    n_w = 15
    for name, lvl, ext in (("Grade inferior", 1, "0"), ("Grade superior", 2, XG)):
        z = f"({levels[lvl]} + 0.005)"
        y0 = f"({cyf} + 0.012 - {ext})"
        c.box(f"{name} - travessa frontal", rxl, y0, z, rw, 0.006, 0.006, "Cromado")
        c.box(f"{name} - travessa traseira", rxl, f"{y0} + {rl} - 0.006", z, rw, 0.006, 0.006, "Cromado")
        c.box(f"{name} - lateral esquerda", rxl, y0, z, 0.006, rl, 0.006, "Cromado")
        c.box(f"{name} - lateral direita", f"{rxl} + {rw} - 0.006", y0, z, 0.006, rl, 0.006, "Cromado")
        c.box(f"{name} - batente traseiro", f"{rxl} + 0.02", f"{y0} + {rl} - 0.004", f"{z} + 0.006", f"{rw} - 0.04", 0.004, 0.018, "Cromado", detail=FINE)
        for i in range(2):
            c.box(f"{name} - reforço {i + 1}", rxl, f"{y0} + {(i + 1) / 3}*{rl}", f"{z} - 0.004", rw, 0.004, 0.004, "Cromado", detail=FINE)
        for i in range(n_w):
            c.box(f"{name} - arame {i + 1}", f"{rxl} + {(i + 1) / (n_w + 1)}*({rw} - 0.003)", y0, f"{z} + 0.002", 0.003, rl, 0.003, "Cromado", detail=FINE)

    # Enamel tray on level 1.
    zt = f"({levels[0]} + 0.005)"
    ty0 = f"({cyf} + 0.012)"
    c.box("Assadeira - fundo", rxl, ty0, zt, rw, rl, 0.002, "Esmalte preto")
    c.box("Assadeira - borda frontal", rxl, ty0, f"{zt} + 0.002", rw, 0.003, 0.028, "Esmalte preto")
    c.box("Assadeira - borda traseira", rxl, f"{ty0} + {rl} - 0.003", f"{zt} + 0.002", rw, 0.003, 0.028, "Esmalte preto")
    c.box("Assadeira - borda esquerda", rxl, f"{ty0} + 0.003", f"{zt} + 0.002", 0.003, f"{rl} - 0.006", 0.028, "Esmalte preto")
    c.box("Assadeira - borda direita", f"{rxl} + {rw} - 0.003", f"{ty0} + 0.003", f"{zt} + 0.002", 0.003, f"{rl} - 0.006", 0.028, "Esmalte preto")

    # --- door -----------------------------------------------------------------
    def door(name, x, width, s0, s1, t0, t1, material, detail=FULL, in_plan=False):
        c.flap_box(name, hinge, A, x, width, s0, s1, t0, t1, material, detail=detail, in_plan=in_plan)

    fr = 0.065  # width of the door's frame around the window
    dx0, dw = f"({xl} + 0.001)", f"({W} - 0.002)"
    tg = f"({EP} - 0.005)"
    door("Porta - vidro externo", dx0, dw, sb, st, tg, EP, "Vidro fumê", in_plan=True)
    door("Porta - travessa inferior", dx0, dw, sb, f"{sb} + {fr}", 0.001, tg, black)
    door("Porta - travessa superior", dx0, dw, f"{st} - {fr}", st, 0.001, tg, black)
    door("Porta - montante esquerdo", dx0, fr, f"{sb} + {fr}", f"{st} - {fr}", 0.001, tg, black)
    door("Porta - montante direito", f"{xr} - 0.001 - {fr}", fr, f"{sb} + {fr}", f"{st} - {fr}", 0.001, tg, black)
    wx0, ww = f"({dx0} + {fr})", f"({dw} - {2 * fr})"
    door("Porta - vidro interno", f"{wx0} - 0.012", f"{ww} + 0.024", f"{sb} + {fr} - 0.012", f"{st} - {fr} + 0.012", -0.003, 0.001, "Vidro temperado")
    door("Porta - vidro intermediário", wx0, ww, f"{sb} + {fr}", f"{st} - {fr}", f"{EP}*0.45", f"{EP}*0.45 + 0.004", "Vidro temperado", detail=FINE)
    for i in range(7):
        door(f"Porta - respiro superior {i + 1}", f"{xl} + {W}*{0.15 + 0.105 * i}", f"{W}*0.07", f"{st} - 0.001", f"{st} + 0.0006", f"{EP}*0.25", f"{EP}*0.7", "Plástico preto", detail=FINE)
    door("Porta - friso inferior", dx0, dw, f"{sb} + 0.012", f"{sb} + 0.016", EP, f"{EP} + 0.0008", inox, detail=FINE)
    hs = f"({st} - 0.04)"
    door("Puxador - barra", f"-{W}*0.42", f"{W}*0.84", f"{hs} - 0.009", f"{hs} + 0.009", f"{EP} + 0.032", f"{EP} + 0.048", inox)
    door("Puxador - suporte esquerdo", f"-{W}*0.36", 0.016, f"{hs} - 0.007", f"{hs} + 0.007", EP, f"{EP} + 0.032", inox)
    door("Puxador - suporte direito", f"{W}*0.36 - 0.016", 0.016, f"{hs} - 0.007", f"{hs} + 0.007", EP, f"{EP} + 0.032", inox)

    # --- control panel --------------------------------------------------------
    c.box("Painel de comando - corpo", xl, f"{yf} + 0.005", zp, W, f"{EP} + 0.015", AP, black, in_plan=True)
    c.box("Painel de comando - vidro", xl, yf, f"{zp} + 0.008", W, 0.005, f"{AP} - 0.008", "Esmalte preto")
    c.box("Painel de comando - friso", xl, f"{yf} - 0.001", zp, W, 0.006, 0.008, inox)
    for i in range(9):
        c.box(f"Painel de comando - saída de ar {i + 1}", f"{xl} + {W}*{0.07 + 0.097 * i}", f"{yf} + 0.01", f"{zp} - 0.0006", f"{W}*0.08", f"{EP} - 0.012", 0.001, "Plástico preto", detail=FINE)
    zk = f"({zp} + 0.004 + {AP}/2)"
    c.box("Visor", -0.055, f"{yf} - 0.001", f"{zk} - 0.017", 0.11, 0.001, 0.034, "Visor LED")
    for i, (sx, n) in enumerate(((-0.105, "menos"), (-0.08, "mais"), (0.064, "relógio"), (0.089, "timer"))):
        c.box(f"Tecla {n}", sx, f"{yf} - 0.0012", f"{zk} - 0.008", 0.016, 0.0012, 0.016, "Teclado", detail=FINE)
    for sx, n in ((f"(-{W}/2 + 0.085)", "de funções"), (f"({W}/2 - 0.085)", "de temperatura")):
        c.rev(f"Botão {n} - aro", "Plan", [(sx, yf), (f"{sx} + 0.026", yf), (f"{sx} + 0.026", f"{yf} - 0.003"), (sx, f"{yf} - 0.003")], zk, sx, "Cromado")
        c.rev(f"Botão {n}", "Plan", [(sx, f"{yf} - 0.003"), (f"{sx} + 0.02", f"{yf} - 0.003"), (f"{sx} + 0.017", f"{yf} - 0.022", 0.004), (f"{sx} + 0.013", f"{yf} - 0.026"), (sx, f"{yf} - 0.026")],
              zk, sx, inox)
        c.box(f"Botão {n} - indicador", f"{sx} - 0.0015", f"{yf} - 0.0268", f"{zk} + 0.003", 0.003, 0.001, 0.011, "Plástico preto", detail=FINE)
        for j, ang in enumerate((-120, -60, 0, 60, 120)):
            ux, uz = 0.034 * math.sin(math.radians(ang)), 0.034 * math.cos(math.radians(ang))
            c.cyl_y(f"Botão {n} - marca {j + 1}", f"{sx} + {ux:.5f}", f"{zk} + {uz:.5f}", f"{yf} - 0.0006", 0.002, 0.0006, "Branco", detail=FINE)
    c.cyl_y("Luz piloto do aquecimento", f"{W}/2 - 0.15", zk, f"{yf} - 0.0008", 0.003, 0.0008, "Plástico vermelho", detail=FINE)
    c.cyl_y("Luz piloto de energia", f"-{W}/2 + 0.15", zk, f"{yf} - 0.0008", 0.003, 0.0008, "Plástico verde", detail=FINE)

    # --- top, back and sides ----------------------------------------------------
    c.box("Canal de ar de resfriamento", f"-{kw}*0.3", f"{ky0} + 0.03", kz1, f"{kw}*0.6", f"{D}*0.45", 0.01, galv)
    c.box("Ventilador de resfriamento - carcaça", f"-{kw}*0.2", f"{ky0} + 0.03 + {D}*0.45", kz1, f"{kw}*0.4", f"{D}*0.2", 0.012, "Plástico preto")
    for i in range(8):
        c.box(f"Gabinete - ventilação do teto {i + 1}", f"{kxl} + 0.03", f"{kyb} - 0.04 - {i}*0.014", f"{kz1} - 0.0005", f"{kw}*0.16", 0.006, 0.001, black, detail=FINE)
    for sx, n in ((f"{kxl} - 0.0006", "esquerda"), (f"{kxr} - 0.0004", "direita")):
        for i in range(6):
            c.box(f"Gabinete - ventilação lateral {n} {i + 1}", sx, f"{kyb} - 0.18", f"{H}*0.2 + {i}*0.016", 0.001, 0.12, 0.007, black, detail=FINE)
    yk = kyb  # outer face of the back
    c.cyl_y("Motor do ventilador - tampa", 0, zcm, yk, 0.08, 0.02, galv)
    c.cyl_y("Motor do ventilador - mancal", 0, zcm, f"{yk} + 0.02", 0.018, 0.004, black, detail=FINE)
    for i in range(3):
        ang = math.radians(90 + 120 * i)
        c.cyl_y(f"Motor do ventilador - parafuso {i + 1}", f"{0.068 * math.cos(ang):.5f}", f"{zcm} + {0.068 * math.sin(ang):.5f}", f"{yk} + 0.02", 0.004, 0.002, "Cromado", detail=FINE)
    for sx, n in ((f"-{kw}*0.36", "esquerda"), (f"{kw}*0.36 - {kw}*0.18", "direita")):
        for i in range(6):
            c.box(f"Fundo - ventilação {n} {i + 1}", sx, f"{yk} - 0.0005", f"{H}*0.62 + {i}*0.014", f"{kw}*0.18", 0.001, 0.006, black, detail=FINE)
    for i, fx in enumerate((-0.25, 0.25)):
        c.box(f"Fundo - nervura {i + 1}", f"{kw}*{fx} - 0.01", yk, f"{z0} + 0.03", 0.02, 0.003, f"{H}*0.35", galv, detail=FINE)
    tx = f"({kxr} - 0.14)"
    c.box("Caixa de ligação", tx, yk, f"{z0} + 0.04", 0.1, 0.022, 0.07, "Plástico preto")
    c.cyl_y("Caixa de ligação - parafuso", f"{tx} + 0.05", f"{z0} + 0.075", f"{yk} + 0.022", 0.004, 0.0015, "Cromado", detail=FINE)
    c.cyl("Caixa de ligação - prensa-cabo", f"{tx} + 0.02", f"{yk} + 0.011", f"{z0} + 0.03", 0.008, 0.01, "Plástico cinza", detail=FINE)
    c.cyl("Cabo de alimentação", f"{tx} + 0.02", f"{yk} + 0.011", 0.004, 0.0045, f"{z0} + 0.026", "Borracha")
    c.box("Etiqueta de identificação", f"-{kw}*0.42", yk, f"{z0} + 0.05", f"{kw}*0.25", 0.0008, 0.05, "Alumínio anodizado", detail=FINE)
    k = 0
    for fx in (-0.47, 0, 0.47):
        for z in (f"{z0} + 0.015", f"{kz1} - 0.015"):
            k += 1
            c.cyl_y(f"Fundo - parafuso {k}", f"{kw}*{fx}", z, yk, 0.004, 0.0015, "Cromado", detail=FINE)

    c.type("Forno elétrico de embutir 60 cm 70 L", "Forno elétrico de embutir multifunção, frente 59,5 x 59,5 cm, 57 cm de profundidade, 70 L, para nicho de 56 cm")
    c.type("Forno elétrico de embutir 90 cm 115 L", "Forno elétrico de embutir multifunção, frente 89,5 x 59,5 cm, 57 cm de profundidade, 115 L, para nicho de 86 cm", Largura=0.895)
    return c
