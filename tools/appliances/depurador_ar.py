"""Depurador de ar slim (60 cm e 80 cm), fixado sob o armário aéreo.

Wall-mounted frame: the back on the wall at y = 0, the front at y = -Profundidade,
the underside at z = 0 (the app applies the mounting height). The outlet collar
stands on the top and goes up into the cabinet above.
"""

from kit import *
from _aparelhos import num


def build() -> Component:
    c = Component("Depurador de ar", "furniture", "depurador-ar")
    W = c.param("Largura", 0.60)
    D = c.param("Profundidade", 0.475)
    H = c.param("Altura", 0.12)
    DS = c.param("DiametroSaida", 0.12)
    AS = c.param("AlturaColar", 0.035)

    body, front, inox = "Aço pintado preto", "Inox escovado", "Inox escovado"
    xl, xr = f"(-{W}/2)", f"({W}/2)"
    yf = f"(-{D})"
    zn = 0.04  # top of the rounded nose
    YS = f"(-{D}*0.42)"  # axis of the outlet collar
    RS = f"({DS}/2)"

    # --- coarse ---------------------------------------------------------------
    c.box("Corpo simplificado", xl, yf, 0, W, D, H, body, detail=COARSE, in_plan=True)
    c.cyl("Colar simplificado", 0, YS, H, RS, AS, "Plástico preto", detail=COARSE)

    # --- body: a sheet-steel shell with a rounded nose ---------------------------
    side = [(0, 0), (f"{yf} + 0.05", 0, 0.06), (yf, zn), (yf, H), (0, H)]
    c.profile("Corpo", "Side", side, f"{xl} + 0.002", f"{W} - 0.004", body, in_plan=True)
    for name, x in (("esquerda", xl), ("direita", f"{xr} - 0.002")):
        c.profile(f"Tampa lateral {name}", "Side", side, x, 0.002, "Plástico preto")
    # Front visor in brushed stainless steel, wrapped over the nose.
    c.box("Frente em inox", f"{xl} + 0.002", f"{yf} - 0.0012", zn, f"{W} - 0.004", 0.0012, f"{H} - {zn} - 0.004", front)
    c.profile("Frente em inox - curva", "Side", [(f"{yf} + 0.05", -0.0012, 0.0612), (f"{yf} - 0.0012", zn), (yf, zn), (f"{yf} + 0.05", 0, -0.06)],
              f"{xl} + 0.002", f"{W} - 0.004", front)
    c.box("Frente - friso superior", f"{xl} + 0.002", f"{yf} - 0.0014", f"{H} - 0.004", f"{W} - 0.004", 0.0014, 0.004, "Plástico preto brilhante", detail=FINE)
    # Recirculation grille: slots along the top of the front.
    n_slots = 22
    for i in range(n_slots):
        c.box(f"Grade de retorno - fenda {i + 1}", f"{xl} + 0.04 + {i}*({W} - 0.08 - 0.008)/{n_slots - 1}", f"{yf} - 0.0016", f"{H} - 0.034", 0.008, 0.0005, 0.022,
              "Tela perfurada", detail=FINE)

    # --- controls on the right of the front: speed slider and light slider --------
    zc = f"(({zn} + {H} - 0.04)/2)"
    for name, x0, w, pos, marks in (("velocidade", f"{xr} - 0.15", 0.06, 0.5, 4), ("luz", f"{xr} - 0.07", 0.03, 0.25, 2)):
        c.profile(f"Chave de {name} - placa", "Front", rrect(f"{x0} - 0.008", f"{zc} - 0.011", f"{x0} + {w} + 0.008", f"{zc} + 0.011", 0.004), f"{yf} - 0.0025", 0.0013,
                  "Plástico preto brilhante")
        c.box(f"Chave de {name} - rasgo", x0, f"{yf} - 0.0028", f"{zc} - 0.002", w, 0.0004, 0.004, "Plástico preto", detail=FINE)
        c.box(f"Chave de {name} - cursor", f"{x0} + {num(pos * w)} - 0.006", f"{yf} - 0.0085", f"{zc} - 0.006", 0.012, 0.006, 0.012, "Plástico cinza claro")
        c.box(f"Chave de {name} - cursor - estrias", f"{x0} + {num(pos * w)} - 0.0045", f"{yf} - 0.0088", f"{zc} - 0.0045", 0.009, 0.0004, 0.009, "Plástico cinza", detail=FINE)
        for j in range(marks):
            c.box(f"Chave de {name} - marca {j + 1}", f"{x0} + {num(j * w / (marks - 1))} - 0.0006", f"{yf} - 0.0029", f"{zc} + 0.0055", 0.0012, 0.0004, 0.004, "Branco", detail=FINE)
    c.cyl_y("Luz indicadora", f"{xr} - 0.18", zc, f"{yf} - 0.0022", 0.0022, 0.001, "Plástico verde", detail=FINE)

    # --- underside: two metal filters and the lamp between them -------------------
    fy0, fy1 = f"({yf} + 0.07)", -0.045
    fd = f"({fy1} - {fy0})"
    gap = 0.06  # half width of the lamp's strip
    fw = f"(({W} - 0.07)/2 - {gap})"
    c.box("Fundo - moldura", f"{xl} + 0.02", f"{yf} + 0.055", -0.0015, f"{W} - 0.04", f"{D} - 0.085", 0.0015, "Aço pintado preto")
    n_slats = 11
    for k, (n, fx0) in enumerate((("esquerdo", f"({xl} + 0.035)"), ("direito", f"({gap})"))):
        z0 = -0.005
        c.box(f"Filtro {n} - moldura frontal", fx0, fy0, z0, fw, 0.01, 0.0035, "Alumínio anodizado")
        c.box(f"Filtro {n} - moldura traseira", fx0, f"{fy1} - 0.01", z0, fw, 0.01, 0.0035, "Alumínio anodizado")
        c.box(f"Filtro {n} - moldura esquerda", fx0, f"{fy0} + 0.01", z0, 0.01, f"{fd} - 0.02", 0.0035, "Alumínio anodizado")
        c.box(f"Filtro {n} - moldura direita", f"{fx0} + {fw} - 0.01", f"{fy0} + 0.01", z0, 0.01, f"{fd} - 0.02", 0.0035, "Alumínio anodizado")
        c.box(f"Filtro {n} - manta", f"{fx0} + 0.01", f"{fy0} + 0.01", -0.003, f"{fw} - 0.02", f"{fd} - 0.02", 0.0015, "Tela perfurada")
        for i in range(n_slats):
            c.box(f"Filtro {n} - lâmina {i + 1}", f"{fx0} + 0.01", f"{fy0} + 0.01 + {(i + 0.5) / n_slats}*({fd} - 0.02) - 0.004", -0.0042, f"{fw} - 0.02", 0.008, 0.0012,
                  "Alumínio anodizado", detail=FINE)
        c.box(f"Filtro {n} - travessa", f"{fx0} + {fw}/2 - 0.004", f"{fy0} + 0.01", -0.0045, 0.008, f"{fd} - 0.02", 0.0015, "Alumínio anodizado", detail=FINE)
        c.box(f"Filtro {n} - trava", f"{fx0} + {fw}/2 - 0.02", f"{fy0} + 0.012", -0.0075, 0.04, 0.014, 0.003, "Plástico preto")
        c.box(f"Filtro {n} - mola da trava", f"{fx0} + {fw}/2 - 0.009", f"{fy0} + 0.003", -0.0065, 0.018, 0.012, 0.0015, "Aço galvanizado", detail=FINE)
    # Lamp lens with its chrome frame.
    ly0, ly1 = f"({yf} + 0.12)", f"({yf} + 0.22)"
    c.profile("Lâmpada - aro", "Plan", rrect(f"-{gap} + 0.012", ly0, f"{gap} - 0.012", ly1, 0.008), -0.004, 0.004, "Cromado")
    c.profile("Lâmpada - lente", "Plan", rrect(f"-{gap} + 0.017", f"{ly0} + 0.005", f"{gap} - 0.017", f"{ly1} - 0.005", 0.005), -0.0055, 0.0015, "Plástico translúcido")
    for i in range(3):
        c.box(f"Lâmpada - LED {i + 1}", -0.004, f"{ly0} + 0.025 + {i}*0.025 - 0.004", -0.0057, 0.008, 0.008, 0.0004, "Branco", detail=FINE)
    # Screws and the data label on the underside.
    for i, (fx, fy) in enumerate(((-1, 0), (1, 0), (-1, 1), (1, 1)), 1):
        x = f"{xl} + 0.01" if fx < 0 else f"{xr} - 0.01"
        y = f"{yf} + 0.06" if fy == 0 else -0.025
        c.cyl(f"Fundo - parafuso {i}", x, y, -0.0025, 0.0035, 0.001, "Cromado", detail=FINE)
    c.box("Etiqueta de identificação", f"-{gap} + 0.015", f"{fy1} - 0.03", -0.0005, f"2*{gap} - 0.03", 0.025, 0.0005, "Alumínio anodizado", detail=FINE)
    c.box("Fundo - aba frontal", f"{xl} + 0.02", f"{yf} + 0.02", -0.0015, f"{W} - 0.04", 0.035, 0.0015, "Plástico preto", detail=FINE)

    # --- top: outlet collar, mounting screws, cable --------------------------------
    c.profile("Colar - flange", "Plan", rrect(f"-{RS} - 0.02", f"{YS} - {RS} - 0.02", f"{RS} + 0.02", f"{YS} + {RS} + 0.02", 0.015), H, 0.003, "Plástico preto")
    c.rev("Colar de saída", "Front", rect(f"{RS} - 0.003", f"{H} + 0.003", RS, f"{H} + {AS}"), YS, 0, "Plástico preto", in_plan=True)
    c.rev("Colar de saída - frisos", "Front", rect(f"{RS} - 0.003", f"{H} + {AS} - 0.012", f"{RS} + 0.0015", f"{H} + {AS} - 0.008"), YS, 0, "Plástico preto", detail=FINE)
    c.cyl("Colar - boca do ventilador", 0, YS, f"{H} + 0.0005", f"{RS} - 0.003", 0.0025, "Plástico cinza")
    for side, sgn in (("esquerda", -1), ("direita", 1)):
        x0 = f"-{RS} + 0.005" if sgn < 0 else "0.0015"
        c.box(f"Válvula anti-retorno {side}", x0, f"{YS} - {RS}*0.85", f"{H} + {AS}*0.55", f"{RS} - 0.0065", f"{RS}*1.7", 0.0015, "Plástico cinza claro")
    c.box("Válvula anti-retorno - eixo", -0.0015, f"{YS} - {RS} + 0.003", f"{H} + {AS}*0.55", 0.003, f"{DS} - 0.006", 0.003, "Aço galvanizado", detail=FINE)
    for i, (fx, fy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        x = f"{xl} + 0.04" if fx < 0 else f"{xr} - 0.04"
        y = f"{yf} + 0.06" if fy < 0 else -0.04
        c.cyl(f"Parafuso de fixação {i} - arruela", x, y, H, 0.008, 0.0012, "Aço galvanizado", detail=FINE)
        c.cyl(f"Parafuso de fixação {i}", x, y, f"{H} + 0.0012", 0.0045, 0.003, "Cromado", detail=FINE)
    CX, CY = f"({xr} - 0.07)", -0.03
    # The cord leaves through a rubber strain relief on the top and lies on it back to the wall,
    # where it goes up into the cabinet to its socket.
    zc_ = f"({H} + 0.0035)"
    c.rev("Cabo de alimentação - passa-fio", "Plan", [(CX, f"{CY} - 0.014"), (f"{CX} + 0.0065", f"{CY} - 0.014"), (f"{CX} + 0.0065", f"{CY} - 0.004"),
                                                      (f"{CX} + 0.0045", f"{CY} + 0.008"), (CX, f"{CY} + 0.008")], zc_, CX, "Borracha", detail=FINE)
    c.box("Cabo de alimentação - placa do passa-fio", f"{CX} - 0.011", f"{CY} - 0.018", H, 0.022, 0.016, 0.0015, "Plástico preto", detail=FINE)
    c.cyl_y("Cabo de alimentação", CX, zc_, f"{CY} + 0.008", 0.0035, -CY - 0.008, "Borracha", detail=FINE)
    # Ventilation louvres on the side caps.
    for name, x in (("esquerda", f"{xl} - 0.0005"), ("direita", f"{xr}")):
        for i in range(5):
            c.box(f"Tampa lateral {name} - respiro {i + 1}", x, f"-{D}*0.6 + {i}*0.03", f"{H}*0.35", 0.0005, 0.018, f"{H}*0.4", "Plástico cinza", detail=FINE)

    c.preview_size = (0.6, 0.475, 0.2)
    c.type("Depurador de ar 60 cm", "Depurador de ar slim sob armário, 60 x 47,5 x 12 cm, 3 velocidades, filtros metálicos laváveis, iluminação LED, saída Ø 12 cm (exaustão ou recirculação)")
    c.type("Depurador de ar 80 cm", "Depurador de ar slim sob armário, 80 x 47,5 x 12 cm, 3 velocidades, filtros metálicos laváveis, iluminação LED, saída Ø 12 cm (exaustão ou recirculação)",
           Largura=0.8)
    return c
