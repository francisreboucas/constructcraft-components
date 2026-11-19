"""TV com rack: a flat-screen TV standing on a media console.

Frame: rack centered on the origin, wall side at +Y, floor at z = 0. The rack
has a hinged door on the left (shelves inside), an open niche in the middle
(soundbar above, set-top box below) and two drawers on the right.
"""

from kit import *
from _aparelhos import tube


def build() -> Component:
    c = Component("TV com rack", "furniture", "tv-rack", "Furniture")
    L = c.param("Largura", 1.80)
    P = c.param("Profundidade", 0.40)
    H = c.param("Altura", 0.55)
    HP = c.param("AlturaPes", 0.12)
    TW = c.param("LarguraTV", 1.232)
    TH = c.param("AlturaTV", 0.712)
    A = c.angle("AnguloPorta", 0, open_at=80)
    c.preview_size = (1.80, 0.40, 1.33)

    c.type('TV 55" com rack 180 cm', 'Rack de 180 cm com porta, nicho e gavetas, e TV de tela plana de 55"')
    c.type('TV 43" com rack 136 cm', 'Rack de 136 cm com porta, nicho e gavetas, e TV de tela plana de 43"',
           Largura=1.36, LarguraTV=0.966, AlturaTV=0.562)

    WOOD, FRONT, DARK = "Madeira clara", "Laminado branco", "Madeira escura"
    BLK, GLOSS, STEEL = "Plástico preto", "Plástico preto brilhante", "Aço pintado preto"
    t = 0.018  # panel thickness
    tt = 0.025  # top thickness
    xl, xr = f"(-{L}/2)", f"({L}/2)"
    yf = f"(-{P}/2 + 0.02)"  # carcass front (the door and drawer fronts overlay it)
    yb = f"({P}/2)"
    zb = HP  # carcass bottom
    zt = f"({H} - {tt})"  # underside of the top
    S = f"(0.3*{L})"  # width of each side section
    xd1 = f"(-0.2*{L})"  # axis of the left divider
    xd2 = f"(0.2*{L})"
    hi = f"({H} - {tt} - {HP} - {t})"  # inner height
    zi = f"({HP} + {t})"  # inner floor
    zs = f"({zi} + {hi}/2 - {t}/2)"  # mid shelf bottom
    cd = f"({P} - 0.02)"  # carcass depth

    # --- coarse stand-ins -------------------------------------------------
    c.box("Rack simplificado", xl, f"-{P}/2", HP, L, P, f"{H} - {HP}", WOOD, detail=COARSE, in_plan=True)
    c.box("TV simplificada", f"-{TW}/2", -0.02, f"{H} + 0.055", TW, 0.05, TH, BLK, detail=COARSE, in_plan=True)
    for i, sx in enumerate((-1, 1), 1):
        c.box(f"Pés simplificados {i}", f"{sx}*({L}/2 - 0.08) - 0.02", f"-{P}/2 + 0.04", 0, 0.04, f"{P} - 0.08", HP, DARK, detail=COARSE)

    # --- carcass ----------------------------------------------------------
    c.box("Tampo", xl, f"-{P}/2", zt, L, P, tt, WOOD, in_plan=True)
    c.box("Base", xl, yf, zb, L, cd, t, WOOD)
    c.box("Lateral esquerda", xl, yf, zi, t, cd, hi, WOOD)
    c.box("Lateral direita", f"{xr} - {t}", yf, zi, t, cd, hi, WOOD)
    c.box("Divisória esquerda", f"{xd1} - {t}/2", yf, zi, t, f"{cd} - 0.012", hi, WOOD)
    c.box("Divisória direita", f"{xd2} - {t}/2", yf, zi, t, f"{cd} - 0.012", hi, WOOD)
    c.box("Fundo", f"{xl} + {t}", f"{yb} - 0.012", zi, f"{L} - 2*{t}", 0.006, hi, FRONT)
    c.box("Prateleira do nicho", f"{xd1} + {t}/2", f"{yf} + 0.01", zs, f"0.4*{L} - {t}", f"{cd} - 0.022", t, WOOD)
    c.box("Prateleira do armário", f"{xl} + {t}", f"{yf} + 0.03", zs, f"{S} - 1.5*{t}", f"{cd} - 0.042", t, WOOD)
    c.box("Fita de borda do tampo", xl, f"-{P}/2 - 0.0008", zt, L, 0.0008, tt, WOOD, detail=FINE)
    c.box("Travessa traseira", f"{xl} + {t}", f"{yb} - 0.03", f"{zt} - 0.06", f"{L} - 2*{t}", 0.018, 0.06, WOOD)
    for k in range(4):
        c.cyl(f"Suporte da prateleira {k + 1}", f"{xl} + {t} + 0.004", f"{yf} + 0.06 + {k % 2}*({cd} - 0.14)",
              f"{zs} - 0.006", 0.004, 0.006, "Cromado", detail=FINE) if k < 2 else \
            c.cyl(f"Suporte da prateleira {k + 1}", f"{xd1} - {t}/2 - 0.004", f"{yf} + 0.06 + {k % 2}*({cd} - 0.14)",
                  f"{zs} - 0.006", 0.004, 0.006, "Cromado", detail=FINE)

    # --- feet: tapered wooden legs with brass ferrules ----------------------
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        fx = f"({sx}*({L}/2 - 0.09))"
        fy = f"({sy}*({P}/2 - 0.07))"
        c.box(f"Pé {i} - chapa de fixação", f"{fx} - 0.04", f"{fy} - 0.04", f"{HP} - 0.004", 0.08, 0.08, 0.004, STEEL, detail=FINE)
        c.rev(f"Pé {i}", "Front", [(fx, 0.022), (f"{fx} + 0.013", 0.022), (f"{fx} + 0.021", f"{HP} - 0.004"), (fx, f"{HP} - 0.004")],
              fy, fx, DARK)
        c.rev(f"Pé {i} - ponteira", "Front", [(fx, 0.002), (f"{fx} + 0.012", 0.002), (f"{fx} + 0.0135", 0.022), (fx, 0.022)],
              fy, fx, "Latão")
        c.cyl(f"Pé {i} - sapata", fx, fy, 0, 0.010, 0.002, "Borracha", detail=FINE)

    # --- left door (hinged on the left, swings with AnguloPorta) -------------
    hinge = (f"{xl} + 0.002", yf)
    dw = f"({S} - 0.004)"
    dz0, dh = f"({HP} + 0.002)", f"({H} - {tt} - {HP} - 0.004)"
    c.door_box("Porta", hinge, A, 0, dw, 0, 0.018, dz0, dh, FRONT, in_plan=True)
    c.door_box("Porta - puxador", hinge, A, f"{dw} - 0.045", f"{dw} - 0.033", 0.018, 0.043, f"{dz0} + {dh}/2 - 0.08", 0.16, STEEL)
    c.door_box("Porta - base do puxador superior", hinge, A, f"{dw} - 0.047", f"{dw} - 0.031", 0.018, 0.021, f"{dz0} + {dh}/2 + 0.06", 0.022, STEEL, detail=FINE)
    c.door_box("Porta - base do puxador inferior", hinge, A, f"{dw} - 0.047", f"{dw} - 0.031", 0.018, 0.021, f"{dz0} + {dh}/2 - 0.082", 0.022, STEEL, detail=FINE)
    for k, zz in enumerate((f"{dz0} + 0.06", f"{dz0} + {dh} - 0.10"), 1):
        c.door_box(f"Dobradiça {k} - caneco", hinge, A, 0.012, 0.050, -0.012, 0, zz, 0.04, "Cromado", detail=FINE)
        c.door_box(f"Dobradiça {k} - braço", hinge, A, 0.016, 0.040, -0.030, -0.012, f"{zz} + 0.008", 0.024, "Cromado", detail=FINE)
        c.box(f"Dobradiça {k} - calço", f"{xl} + {t}", f"{yf} + 0.025", f"{zz} + 0.004", 0.006, 0.05, 0.032, "Cromado", detail=FINE)
    c.door_box("Porta - batente de silicone", hinge, A, f"{dw} - 0.02", f"{dw} - 0.012", -0.002, 0, f"{dz0} + 0.02", 0.008, "Plástico translúcido", detail=FINE)

    # inside the cupboard: a game console, a media player and boxes
    ax0 = f"({xl} + {t})"  # inner left
    aw = f"({S} - 1.5*{t})"  # inner width
    zu = f"({zs} + {t})"  # top of the mid shelf
    c.box("Reprodutor de mídia", f"{ax0} + 0.04", f"{yf} + 0.07", f"{zi} + 0.006", f"{aw} - 0.08", 0.24, 0.045, BLK)
    c.box("Reprodutor de mídia - frente", f"{ax0} + 0.04", f"{yf} + 0.068", f"{zi} + 0.006", f"{aw} - 0.08", 0.002, 0.045, GLOSS)
    c.box("Reprodutor de mídia - gaveta de disco", f"{ax0} + 0.06", f"{yf} + 0.067", f"{zi} + 0.03", 0.14, 0.001, 0.012, "Plástico cinza", detail=FINE)
    c.box("Reprodutor de mídia - visor", f"{ax0} + {aw} - 0.14", f"{yf} + 0.067", f"{zi} + 0.02", 0.07, 0.001, 0.014, "Visor LED", detail=FINE)
    for k in range(4):
        c.cyl(f"Reprodutor de mídia - pé {k + 1}", f"{ax0} + 0.06 + {k % 2}*({aw} - 0.12)", f"{yf} + 0.09 + {k // 2}*0.20", zi, 0.008, 0.006, "Borracha", detail=FINE)
    c.box("Console de jogos", f"{ax0} + 0.05", f"{yf} + 0.08", zu, 0.07, 0.22, f"{hi}/2 - {t}/2 - 0.03", "Branco")
    c.box("Console de jogos - faixa", f"{ax0} + 0.083", f"{yf} + 0.078", zu, 0.006, 0.224, f"{hi}/2 - {t}/2 - 0.028", GLOSS, detail=FINE)
    c.box("Console de jogos - base", f"{ax0} + 0.035", f"{yf} + 0.12", zu, 0.10, 0.14, 0.006, GLOSS, detail=FINE)
    for k in range(5):
        c.box(f"Caixa de jogo {k + 1}", f"{ax0} + 0.16 + {k}*0.016", f"{yf} + 0.09", zu, 0.014, 0.135, f"0.17 - {k % 2}*0.004",
              ("Plástico azul", "Plástico verde", "Plástico azul", "Plástico vermelho", "Plástico azul")[k], detail=FINE)
    c.box("Controle de jogos", f"{ax0} + {aw} - 0.19", f"{yf} + 0.10", zu, 0.15, 0.09, 0.03, "Branco", detail=FINE)

    # --- right drawers ------------------------------------------------------
    gx = f"({xd2} - {t}/2 + 0.002)"  # left edge of the fronts
    gw = f"({S} + {t}/2 - 0.004)"
    gh = f"(({H} - {tt} - {HP})/2 - 0.003)"
    for k in (1, 2):
        gz = f"({HP} + 0.002 + {k - 1}*({gh} + 0.002))"
        n = "inferior" if k == 1 else "superior"
        c.box(f"Gaveta {n} - frente", gx, f"-{P}/2", gz, gw, 0.018, gh, FRONT, in_plan=(k == 1))
        c.box(f"Gaveta {n} - puxador", f"{gx} + {gw}/2 - 0.08", f"-{P}/2 - 0.025", f"{gz} + {gh} - 0.045", 0.16, 0.025, 0.012, STEEL)
        c.box(f"Gaveta {n} - base do puxador esquerda", f"{gx} + {gw}/2 - 0.082", f"-{P}/2 - 0.003", f"{gz} + {gh} - 0.047", 0.022, 0.003, 0.016, STEEL, detail=FINE)
        c.box(f"Gaveta {n} - base do puxador direita", f"{gx} + {gw}/2 + 0.06", f"-{P}/2 - 0.003", f"{gz} + {gh} - 0.047", 0.022, 0.003, 0.016, STEEL, detail=FINE)
        bx0 = f"({xd2} + {t}/2 + 0.013)"
        bw = f"({S} - 1.5*{t} - 0.026)"
        bz = f"({gz} + 0.02)"
        bh = f"({gh} - 0.05)"
        bd = f"({cd} - 0.05)"
        c.box(f"Gaveta {n} - lateral esquerda", bx0, yf, bz, 0.012, bd, bh, WOOD)
        c.box(f"Gaveta {n} - lateral direita", f"{bx0} + {bw} - 0.012", yf, bz, 0.012, bd, bh, WOOD)
        c.box(f"Gaveta {n} - traseira", bx0, f"{yf} + {bd} - 0.012", bz, bw, 0.012, bh, WOOD)
        c.box(f"Gaveta {n} - fundo", bx0, yf, f"{bz} + 0.008", bw, bd, 0.004, FRONT)
        c.box(f"Gaveta {n} - corrediça esquerda", f"{bx0} - 0.013", f"{yf} + 0.01", f"{bz} + {bh}/2 - 0.02", 0.013, f"{bd} - 0.02", 0.04, "Aço galvanizado", detail=FINE)
        c.box(f"Gaveta {n} - corrediça direita", f"{bx0} + {bw}", f"{yf} + 0.01", f"{bz} + {bh}/2 - 0.02", 0.013, f"{bd} - 0.02", 0.04, "Aço galvanizado", detail=FINE)

    # --- open niche: soundbar above, set-top box and power strip below -------
    nw = f"(0.4*{L} - {t})"  # niche width (centered on x = 0)
    sbw = f"({nw} - 0.10)"
    sy0 = f"({yf} + 0.035)"
    c.profile("Soundbar", "Side", rrect(sy0, zu, f"{sy0} + 0.085", f"{zu} + 0.058", 0.014), f"-{sbw}/2", sbw, BLK)
    c.box("Soundbar - tela frontal", f"-{sbw}/2 + 0.03", f"{sy0} - 0.0008", f"{zu} + 0.008", f"{sbw} - 0.06", 0.001, 0.042, "Tela perfurada")
    c.profile("Soundbar - tampa esquerda", "Side", rrect(f"{sy0} - 0.001", f"{zu} - 0.0005", f"{sy0} + 0.086", f"{zu} + 0.059", 0.014), f"-{sbw}/2 - 0.004", 0.012, "Plástico cinza")
    c.profile("Soundbar - tampa direita", "Side", rrect(f"{sy0} - 0.001", f"{zu} - 0.0005", f"{sy0} + 0.086", f"{zu} + 0.059", 0.014), f"{sbw}/2 - 0.008", 0.012, "Plástico cinza")
    c.box("Soundbar - visor", -0.03, f"{sy0} - 0.0014", f"{zu} + 0.022", 0.06, 0.001, 0.012, "Visor LED", detail=FINE)
    for k in range(4):
        c.cyl(f"Soundbar - botão {k + 1}", f"{-0.045 + k * 0.03}", f"{sy0} + 0.045", f"{zu} + 0.058", 0.006, 0.0012, "Plástico cinza", detail=FINE)
    for k, sx in enumerate((-1, 1), 1):
        c.cyl_y(f"Soundbar - alto-falante {k}", f"{sx}*({sbw}/2 - 0.09)", f"{zu} + 0.029", f"{sy0} - 0.0003", 0.02, 0.001, "Plástico cinza", detail=FINE)
    c.cyl_y("Soundbar - cabo", f"{sbw}/2 - 0.06", f"{zu} + 0.02", f"{sy0} + 0.085", 0.003, f"{yb} - 0.012 - ({sy0} + 0.085)", "Borracha", detail=FINE)

    stw, std = 0.26, 0.19
    stx = f"(-{nw}/2 + 0.05)"
    sty = f"({yf} + 0.05)"
    stz = f"({zi} + 0.006)"
    c.box("Receptor de TV", stx, sty, stz, stw, std, 0.038, BLK)
    c.box("Receptor de TV - frente", stx, f"{sty} - 0.002", stz, stw, 0.002, 0.038, GLOSS)
    c.box("Receptor de TV - visor", f"{stx} + 0.15", f"{sty} - 0.003", f"{stz} + 0.012", 0.07, 0.001, 0.016, "Visor LED", detail=FINE)
    c.cyl_y("Receptor de TV - botão liga", f"{stx} + 0.03", f"{stz} + 0.019", f"{sty} - 0.004", 0.007, 0.002, "Plástico cinza", detail=FINE)
    c.cyl_y("Receptor de TV - LED", f"{stx} + 0.055", f"{stz} + 0.019", f"{sty} - 0.003", 0.0025, 0.001, "Plástico verde", detail=FINE)
    for k in range(6):
        c.box(f"Receptor de TV - ventilação {k + 1}", f"{stx} + 0.04 + {k}*0.032", f"{sty} + 0.05", f"{stz} + 0.038", 0.02, 0.10, 0.0006, "Plástico preto brilhante", detail=FINE)
    for k in range(4):
        c.cyl(f"Receptor de TV - pé {k + 1}", f"{stx} + 0.02 + {k % 2}*{stw - 0.04}", f"{sty} + 0.02 + {k // 2}*{std - 0.04}", zi, 0.008, 0.006, "Borracha", detail=FINE)
    c.cyl_y("Receptor de TV - conector de antena", f"{stx} + 0.04", f"{stz} + 0.02", f"{sty} + {std}", 0.005, 0.012, "Cromado", detail=FINE)
    c.cyl_y("Receptor de TV - cabo", f"{stx} + 0.10", f"{stz} + 0.018", f"{sty} + {std}", 0.003, f"{yb} - 0.012 - ({sty} + {std})", "Borracha", detail=FINE)

    # power strip lying at the back of the lower niche
    rx = f"({nw}/2 - 0.31)"
    ry = f"({yb} - 0.012 - 0.075)"
    c.box("Régua de tomadas", rx, ry, zi, 0.26, 0.05, 0.035, "Branco")
    for k in range(4):
        c.cyl(f"Régua de tomadas - tomada {k + 1}", f"{rx} + 0.075 + {k}*0.05", f"{ry} + 0.025", f"{zi} + 0.035", 0.017, 0.001, "Plástico cinza claro", detail=FINE)
    c.box("Régua de tomadas - interruptor", f"{rx} + 0.015", f"{ry} + 0.015", f"{zi} + 0.035", 0.025, 0.02, 0.004, "Plástico vermelho", detail=FINE)
    c.box("Régua de tomadas - plugue", f"{rx} + 0.058", f"{ry} + 0.008", f"{zi} + 0.036", 0.034, 0.034, 0.03, BLK, detail=FINE)
    c.cyl("Régua de tomadas - cabo do plugue", f"{rx} + 0.075", f"{ry} + 0.025", f"{zi} + 0.066", 0.003, f"{zs} - {zi} - 0.066", "Borracha", detail=FINE)

    # cable grommets: one through the top, one through the back panel
    gxp = f"(0.12*{L})"
    gyp = f"({yb} - 0.075)"
    c.cyl("Passa-fios do tampo - furo", gxp, gyp, f"{zt} - 0.001", 0.026, f"{tt} + 0.002", WOOD, void=True)
    c.rev("Passa-fios do tampo - anel", "Front", [(f"{gxp} + 0.025", zt), (f"{gxp} + 0.033", f"{H} + 0.002"), (f"{gxp} + 0.025", f"{H} + 0.002")], gyp, gxp, BLK)
    c.rev("Passa-fios do tampo - luva", "Front", rect(f"{gxp} + 0.0245", f"{zt} - 0.004", f"{gxp} + 0.0262", H), gyp, gxp, BLK, detail=FINE)
    c.cyl_y("Passa-fios do fundo - furo", 0, f"{zi} + 0.06", f"{yb} - 0.013", 0.03, 0.008, FRONT, void=True)
    c.cyl_y("Passa-fios do fundo - anel", 0, f"{zi} + 0.06", f"{yb} - 0.0135", 0.036, 0.001, BLK, detail=FINE)

    # --- TV -------------------------------------------------------------------
    z0 = f"({H} + 0.055)"  # underside of the TV
    yt = -0.022  # front of the frame
    c.box("TV - moldura", f"-{TW}/2", yt, z0, TW, 0.012, TH, BLK, in_plan=True)
    c.box("TV - tela", f"-{TW}/2 + 0.007", yt - 0.001, f"{z0} + 0.018", f"{TW} - 0.014", 0.001, f"{TH} - 0.025", "Tela de TV")
    c.box("TV - filete inferior", f"-{TW}/2", yt - 0.002, z0, TW, 0.002, 0.016, "Alumínio anodizado")
    c.box("TV - sensor infravermelho", -0.02, yt - 0.003, f"{z0} - 0.008", 0.04, 0.012, 0.008, "Plástico fumê", detail=FINE)
    c.cyl_y("TV - LED de espera", 0, f"{z0} - 0.004", yt - 0.0035, 0.0015, 0.001, "Plástico vermelho", detail=FINE)
    c.box("TV - tampa traseira", f"-{TW}/2 + 0.004", yt + 0.012, f"{z0} + 0.004", f"{TW} - 0.008", 0.003, f"{TH} - 0.008", "Aço pintado preto")
    # back bulge with the electronics: a sloped housing on the lower part
    yb0 = yt + 0.015
    bw_ = f"(0.8*{TW})"
    bt = f"({z0} + 0.62*{TH})"
    c.profile("TV - caixa traseira", "Side",
              [(yb0, f"{z0} + 0.02"), (yb0 + 0.036, f"{z0} + 0.035"), (yb0 + 0.036, f"{bt} - 0.05"), (yb0, bt)],
              f"-{bw_}/2", bw_, BLK)
    ybk = yb0 + 0.036  # back face of the bulge
    for g, sx in enumerate((-1, 1), 1):
        for k in range(9):
            c.box(f"TV - ventilação {g}.{k + 1}", f"{sx}*0.22*{TW} - 0.11*{TW}", ybk, f"{bt} - 0.07 - {k}*0.011", f"0.22*{TW}", 0.0008, 0.005,
                  GLOSS, detail=FINE)
    for k, (sx, sz) in enumerate(((-1, 0), (1, 0), (-1, 1), (1, 1)), 1):
        c.cyl_y(f"TV - fixação VESA {k}", f"{sx}*0.1", f"{z0} + 0.2*{TH} + {sz}*0.2", ybk, 0.006, 0.0015, "Aço galvanizado", detail=FINE)
    c.box("TV - etiqueta", -0.05, ybk, f"{z0} + 0.2*{TH} + 0.07", 0.10, 0.0005, 0.06, "Plástico cinza claro", detail=FINE)
    # connections panel on the back, on the right seen from the front
    px = f"(0.26*{TW})"
    pz = f"({z0} + 0.10)"
    c.box("TV - painel de conexões", px, ybk, pz, 0.09, 0.001, 0.17, "Plástico cinza")
    for k in range(3):
        c.box(f"TV - entrada HDMI {k + 1}", f"{px} + 0.012", ybk + 0.001, f"{pz} + 0.125 - {k}*0.024", 0.016, 0.001, 0.007, GLOSS, detail=FINE)
    for k in range(2):
        c.box(f"TV - entrada USB {k + 1}", f"{px} + 0.05", ybk + 0.001, f"{pz} + 0.125 - {k}*0.024", 0.014, 0.001, 0.007, "Plástico azul", detail=FINE)
    c.cyl_y("TV - entrada de antena", f"{px} + 0.022", f"{pz} + 0.045", ybk + 0.001, 0.005, 0.011, "Cromado", detail=FINE)
    c.box("TV - entrada de rede", f"{px} + 0.05", ybk + 0.001, f"{pz} + 0.05", 0.016, 0.001, 0.014, GLOSS, detail=FINE)
    c.cyl_y("TV - saída de áudio óptica", f"{px} + 0.058", f"{pz} + 0.028", ybk + 0.001, 0.004, 0.003, BLK, detail=FINE)
    c.cyl_y("TV - saída de fone", f"{px} + 0.022", f"{pz} + 0.02", ybk + 0.001, 0.003, 0.002, "Latão", detail=FINE)
    for g, sx in enumerate((-1, 1), 1):
        c.box(f"TV - grade do alto-falante {g}", f"{sx}*0.3*{TW} - 0.07", yt + 0.002, f"{z0} - 0.0008", 0.14, 0.03, 0.001, "Tela perfurada", detail=FINE)
    # power cord and HDMI cable: down the back, along the top, into the grommet
    cy = ybk + 0.012
    cx = f"({gxp} - 0.008)"
    c.cyl_y("TV - prensa-cabo", cx, f"{z0} + 0.07", ybk, 0.007, 0.012, BLK, detail=FINE)
    rc = 0.012  # bend radius of the cables
    zc = f"({H} + 0.004)"  # the cables lie on the top

    def cable(name, x, z, radius, material):
        path = [(cy, z), (cy, f"{zc} + {rc}", rc), (cy + rc, zc), (f"{gyp} - {rc}", zc, -rc), (gyp, f"{zc} - {rc}"), (gyp, f"{zt} - 0.05")]
        tube(c, name, "Side", path, x, radius, material, FINE)

    cable("TV - cabo de força", cx, f"{z0} + 0.07", 0.0035, "Borracha")
    hx = f"({gxp} + 0.01)"
    c.box("TV - plugue HDMI", f"{hx} - 0.009", cy - 0.006, f"{z0} + 0.045", 0.018, 0.012, 0.03, BLK, detail=FINE)
    cable("TV - cabo HDMI", hx, f"{z0} + 0.045", 0.003, BLK)
    # two V-shaped feet
    for g, sx in enumerate((-1, 1), 1):
        fx = f"({sx}*0.36*{TW} - 0.011)"
        c.profile(f"TV - pé {g}", "Side",
                  [(-0.125, H), (-0.105, H), (-0.006, f"{z0} + 0.004"), (0.012, f"{z0} + 0.004"), (0.105, H), (0.125, H),
                   (0.024, f"{z0} + 0.03"), (-0.016, f"{z0} + 0.03")],
                  fx, 0.022, GLOSS)
        c.box(f"TV - pé {g} - sapata dianteira", f"{fx} + 0.003", -0.122, f"{H} - 0.0", 0.016, 0.014, 0.0015, "Borracha", detail=FINE)
        c.box(f"TV - pé {g} - sapata traseira", f"{fx} + 0.003", 0.108, f"{H} - 0.0", 0.016, 0.014, 0.0015, "Borracha", detail=FINE)
        c.cyl_y(f"TV - pé {g} - parafuso", f"{fx} + 0.011", f"{z0} + 0.018", yb0, 0.004, 0.012, "Aço galvanizado", detail=FINE)
    return c
