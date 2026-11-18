"""Purificador de água refrigerado, de bancada ou de parede.

Wall-mounted frame: the back on the wall at y = 0 (a hanging plate behind the
body), the front at y = -Profundidade, the feet at z = 0. On a countertop it
stands on its feet; on a wall the app applies the mounting height. The filter
cartridge sits in a pocket of the right side, behind a door hinged at its back
edge (`AnguloPortaFiltro`).
"""

from kit import *
from _aparelhos import blend, num, side_door_box


def build() -> Component:
    c = Component("Purificador de água", "plumbing", "purificador-agua", "Plumbing")
    W = c.param("Largura", 0.27)
    D = c.param("Profundidade", 0.31)
    H = c.param("Altura", 0.40)
    LN = c.param("LarguraNicho", 0.15)
    PN = c.param("ProfundidadeNicho", 0.085)
    AN = c.param("AlturaNicho", 0.20)
    ang = c.angle("AnguloPortaFiltro", 0, open_at=100)

    white, dark = "Branco", "Plástico preto brilhante"
    xl, xr = f"(-{W}/2)", f"({W}/2)"
    yf, yk = f"(-{D})", -0.004  # front; back of the body (the hanging plate is behind it)
    RF = 0.05  # radius of the front corners
    ZB, ZN0 = 0.012, 0.045  # bottom of the body; floor of the niche
    ZN1 = f"({ZN0} + {AN})"  # ceiling of the niche
    ZT = f"({H} - 0.025)"  # where the rounded top starts
    PD = 0.055  # depth of the filter pocket
    yp0, yp1 = f"({yf} + {RF} + 0.025)", -0.04  # the pocket along y

    def outline(niche=False, pocket=False, inset=0.0):
        i = num(inset)
        pts = [(f"{xl} + {RF}", f"{yf} + {i}")]
        if niche:
            pts += [(f"-{LN}/2", yf), (f"-{LN}/2", f"{yf} + {PN} - 0.015", -0.015), (f"-{LN}/2 + 0.015", f"{yf} + {PN}"),
                    (f"{LN}/2 - 0.015", f"{yf} + {PN}", -0.015), (f"{LN}/2", f"{yf} + {PN} - 0.015"), (f"{LN}/2", yf)]
        pts += [(f"{xr} - {RF}", f"{yf} + {i}", RF - inset), (f"{xr} - {i}", f"{yf} + {RF}")]
        if pocket:
            pts += [(xr, yp0), (f"{xr} - {PD}", yp0), (f"{xr} - {PD}", yp1), (xr, yp1)]
        pts += [(f"{xr} - {i}", f"{yk} - 0.012", 0.012 - inset), (f"{xr} - 0.012", f"{yk} - {i}"), (f"{xl} + 0.012", f"{yk} - {i}", 0.012 - inset),
                (f"{xl} + {i}", f"{yk} - 0.012"), (f"{xl} + {i}", f"{yf} + {RF}", RF - inset)]
        return pts

    # --- coarse ---------------------------------------------------------------
    c.profile("Corpo simplificado", "Plan", outline(), 0, H, white, detail=COARSE, in_plan=True)
    hinge = (xr, f"{yp1} + 0.012")
    door_len = f"({yp1} + 0.012 - {yp0} + 0.012)"
    side_door_box(c, "Porta do filtro simplificada", hinge, ang, 0, door_len, 0, 0.003, ZN0, f"{ZT} - {ZN0}", white, detail=COARSE)

    # --- body: lower block, the niche block, upper block and the rounded top -----
    c.profile("Corpo - base", "Plan", outline(), ZB, f"{ZN0} - {ZB}", white, in_plan=True)
    c.profile("Corpo - altura do nicho", "Plan", outline(niche=True, pocket=True), ZN0, AN, white)
    c.profile("Corpo - parte superior", "Plan", outline(pocket=True), ZN1, f"{ZT} - {ZN1}", white)
    blend(c, "Corpo - tampo arredondado", outline(), outline(inset=0.012), ZT, f"{H} - {ZT}", white)
    c.box("Rodapé - friso", f"{xl} + {RF}", f"{yf} - 0.0008", ZB, f"{W} - 2*{RF}", 0.0008, 0.006, "Plástico cinza claro", detail=FINE)
    c.profile("Nicho - fundo escuro", "Front", rrect(f"-{LN}/2 + 0.015", f"{ZN0} + 0.01", f"{LN}/2 - 0.015", f"{ZN1} - 0.01", 0.01), f"{yf} + {PN} - 0.001", 0.001,
              "Plástico cinza")
    c.box("Nicho - teto", f"-{LN}/2", f"{yf}", f"{ZN1} - 0.001", LN, PN, 0.001, "Plástico cinza claro", detail=FINE)
    # Feet.
    for i, (fx, fy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        x = f"{xl} + 0.035" if fx < 0 else f"{xr} - 0.035"
        y = f"{yf} + 0.04" if fy < 0 else f"{yk} - 0.035"
        c.rev(f"Pé {i}", "Front", [(x, 0), (f"{x} + 0.012", 0), (f"{x} + 0.012", 0.004, 0.006), (f"{x} + 0.009", ZB), (x, ZB)], y, x, "Borracha")

    # --- front panel with display and keys ------------------------------------------
    zp0, zp1 = f"({ZN1} + 0.018)", f"({ZT} - 0.02)"
    pw = f"({W} - 2*{RF} - 0.01)"
    c.profile("Painel frontal", "Front", rrect(f"-{pw}/2", zp0, f"{pw}/2", zp1, 0.012), f"{yf} - 0.0015", 0.0015, dark)
    zm = f"(({zp0} + {zp1})/2)"
    c.box("Visor", f"-{pw}*0.18", f"{yf} - 0.0019", f"{zm} + 0.006", f"{pw}*0.36", 0.0004, 0.022, "Visor LED")
    for i in range(2):
        c.box(f"Visor - dígito {i + 1}", f"-{pw}*0.08 + {i}*{pw}*0.09", f"{yf} - 0.0022", f"{zm} + 0.009", f"{pw}*0.07", 0.0003, 0.016, "Plástico azul", detail=FINE)
    c.box("Visor - termômetro", f"{pw}*0.13", f"{yf} - 0.0022", f"{zm} + 0.01", 0.003, 0.0003, 0.014, "Plástico azul", detail=FINE)
    for i, (name, mat) in enumerate((("água natural", "Plástico verde"), ("água fria", "Plástico azul"), ("água gelada", "Plástico azul"))):
        bx = f"{pw}*{num(-0.3 + 0.3 * i)}"
        c.cyl_y(f"Tecla {name} - aro", bx, f"{zm} - 0.014", f"{yf} - 0.0022", 0.0105, 0.0007, "Cromado", detail=FINE)
        c.cyl_y(f"Tecla {name}", bx, f"{zm} - 0.014", f"{yf} - 0.0040", 0.0085, 0.0025, "Teclado")
        c.cyl_y(f"Tecla {name} - ícone", bx, f"{zm} - 0.014", f"{yf} - 0.0043", 0.003, 0.0003, mat, detail=FINE)
    c.cyl_y("Luz de troca do filtro", f"{pw}*0.4", f"{zm} + 0.017", f"{yf} - 0.0021", 0.002, 0.0006, "Plástico vermelho", detail=FINE)
    c.cyl_y("Luz de ligado", f"-{pw}*0.4", f"{zm} + 0.017", f"{yf} - 0.0021", 0.002, 0.0006, "Plástico verde", detail=FINE)
    c.box("Etiqueta frontal", f"-{pw}*0.15", f"{yf} - 0.0008", f"{ZN1} + 0.006", f"{pw}*0.3", 0.0008, 0.006, "Plástico cinza claro", detail=FINE)

    # --- spout in the niche ceiling ----------------------------------------------------
    ys = f"({yf} + {PN}*0.45)"
    c.rev("Bica - base", "Front", [(0, f"{ZN1} - 0.001"), (0.016, f"{ZN1} - 0.001"), (0.016, f"{ZN1} - 0.006", 0.006), (0.012, f"{ZN1} - 0.01"), (0, f"{ZN1} - 0.01")],
          ys, 0, "Cromado")
    c.rev("Bica", "Front", [(0, f"{ZN1} - 0.01"), (0.0085, f"{ZN1} - 0.01"), (0.0065, f"{ZN1} - 0.034"), (0, f"{ZN1} - 0.034")], ys, 0, "Cromado")
    c.rev("Bica - bico", "Front", rect(0, f"{ZN1} - 0.038", 0.0045, f"{ZN1} - 0.034"), ys, 0, "Plástico cinza", detail=FINE)
    c.cyl("Bica - saída", 0, ys, f"{ZN1} - 0.0385", 0.0025, 0.0005, "Plástico preto", detail=FINE)
    c.cyl("Luz do nicho", 0, f"{yf} + {PN}*0.8", f"{ZN1} - 0.0015", 0.006, 0.0006, "Plástico translúcido", detail=FINE)

    # --- drip tray with its grille -----------------------------------------------------
    tx = f"({LN}/2 - 0.004)"
    ty0, ty1 = f"({yf} - 0.018)", f"({yf} + {PN} - 0.004)"
    c.profile("Bandeja", "Plan", [(f"-{tx}", ty1), (f"-{tx}", f"{ty0} + 0.012"), (f"-{tx} + 0.012", ty0, 0.3), (f"{tx} - 0.012", ty0), (tx, f"{ty0} + 0.012"), (tx, ty1)],
              ZN0, 0.012, "Plástico cinza", in_plan=True)
    c.profile("Bandeja - frente", "Front", rrect(f"-{tx}", f"{ZN0} - 0.012", tx, f"{ZN0} + 0.012", 0.006), f"{ty0} + 0.003", 0.004, "Plástico cinza")
    n = 7
    for i in range(n):
        c.box(f"Bandeja - grelha {i + 1}", f"-{tx} + 0.008", f"{ty0} + 0.01 + {i}*({ty1} - {ty0} - 0.02)/{n - 1} - 0.002", f"{ZN0} + 0.012", f"2*{tx} - 0.016", 0.004, 0.0015,
              "Inox escovado", detail=FINE)
    c.box("Bandeja - nervura", "-0.002", f"{ty0} + 0.01", f"{ZN0} + 0.011", 0.004, f"{ty1} - {ty0} - 0.02", 0.0012, "Inox escovado", detail=FINE)

    # --- filter pocket: cartridge and its head, behind the side door ----------------
    zf0, zf1 = f"({ZN0} + 0.02)", f"({ZT} - 0.03)"
    fx, fy = f"({xr} - {PD}/2)", f"(({yp0} + {yp1})/2)"
    c.box("Bolsão do filtro - fundo", f"{xr} - {PD}", yp0, ZN0, 0.002, f"{yp1} - {yp0}", f"{ZT} - {ZN0}", "Plástico cinza claro")
    c.cyl("Refil", fx, fy, zf0, 0.024, f"({zf1} - {zf0})*0.78", white)
    c.cyl("Refil - faixa", fx, fy, f"{zf0} + ({zf1} - {zf0})*0.3", 0.0245, 0.03, "Plástico azul", detail=FINE)
    c.cyl("Refil - cabeçote", fx, fy, f"{zf0} + ({zf1} - {zf0})*0.78", 0.02, f"({zf1} - {zf0})*0.22", "Plástico cinza")
    c.box("Refil - trava", f"{fx} - 0.004", f"{fy} - 0.028", f"{zf1} - 0.03", 0.008, 0.056, 0.012, "Plástico azul", detail=FINE)
    c.cyl("Refil - mangueira de entrada", f"{fx} - 0.012", f"{fy} + 0.022", f"{zf1} - 0.01", 0.003, f"{ZT} - {zf1} + 0.005", "Plástico translúcido", detail=FINE)
    c.cyl("Refil - mangueira de saída", f"{fx} + 0.012", f"{fy} + 0.022", f"{zf1} - 0.01", 0.003, f"{ZT} - {zf1} + 0.005", "Plástico translúcido", detail=FINE)
    # The door.
    side_door_box(c, "Porta do filtro", hinge, ang, 0, door_len, 0, 0.003, ZN0, f"{ZT} - {ZN0}", white)
    side_door_box(c, "Porta do filtro - pega", hinge, ang, f"{door_len} - 0.025", f"{door_len} - 0.006", 0.003, 0.0045, f"({ZN0} + {ZT})/2 - 0.03", 0.06, "Plástico cinza claro",
                  detail=FINE)
    side_door_box(c, "Porta do filtro - dobradiça", hinge, ang, 0, 0.006, 0.0005, 0.004, f"{ZN0} + 0.02", f"{ZT} - {ZN0} - 0.04", "Plástico cinza", detail=FINE)
    side_door_box(c, "Porta do filtro - etiqueta", hinge, ang, f"{door_len}*0.3", f"{door_len}*0.7", 0.003, 0.0034, f"{ZT} - 0.07", 0.03, "Plástico cinza claro", detail=FINE)
    side_door_box(c, "Porta do filtro - vedação", hinge, ang, 0.004, f"{door_len} - 0.004", -0.0015, 0, f"{ZN0} + 0.004", f"{ZT} - {ZN0} - 0.008", "Borracha cinza", detail=FINE)

    # --- left side: cooling vents ------------------------------------------------------
    for i in range(8):
        c.box(f"Ventilação lateral {i + 1}", f"{xl} - 0.0006", f"{yf} + {RF} + 0.02 + {i}*0.022", f"{ZN0} + 0.03", 0.0006, 0.009, f"{AN}*0.7", "Plástico cinza", detail=FINE)

    # --- back: hanging plate, water inlet, power cable ------------------------------
    c.box("Placa de fixação", f"-{W}*0.3", yk, f"{H}*0.45", f"{W}*0.6", -yk, f"{H}*0.35", "Aço galvanizado")
    for i, fx_ in enumerate((-0.2, 0.2), 1):
        c.cyl_y(f"Placa de fixação - parafuso {i}", f"{W}*{fx_}", f"{H}*0.73", -0.0005, 0.0045, 0.0005, "Cromado", detail=FINE)
    IX, IZ = f"({xr} - 0.05)", 0.07
    c.cyl_y("Entrada de água - conexão", IX, IZ, f"{yk} - 0.004", 0.009, 0.008, "Plástico azul")
    c.box("Entrada de água - trava", f"{IX} - 0.011", f"{yk} - 0.002", f"{IZ} - 0.011", 0.022, 0.002, 0.022, "Plástico azul", detail=FINE)
    CX = f"({xl} + 0.05)"
    c.cyl_y("Cabo de alimentação - passa-fio", CX, 0.05, f"{yk} - 0.004", 0.007, 0.006, "Borracha", detail=FINE)
    c.cyl_y("Cabo de alimentação", CX, 0.05, f"{yk} + 0.002", 0.0032, f"-{yk} - 0.002", "Borracha", detail=FINE)  # runs down behind, against the wall
    c.box("Etiqueta de identificação", f"-{W}*0.1", f"{yk} - 0.0005", 0.07, f"{W}*0.2", 0.0005, 0.05, "Plástico cinza claro", detail=FINE)

    c.mep = {"Fixture": {"drain_units": 0, "supply_weight": 0.1, "hot_water": False}}
    c.connector("Água fria", "ColdWater", IX, 0, IZ, "Back", 0.02)

    c.preview_size = (0.27, 0.40, 0.40)
    c.type("Purificador refrigerado 27 x 31 x 40 cm", "Purificador de água refrigerado por compressor, de bancada ou de parede, água natural, fria e gelada; refil na lateral; prever ponto de água fria e TUG")
    c.type("Purificador compacto 22 x 27 x 35 cm", "Purificador de água compacto refrigerado por placa eletrônica, de bancada ou de parede, água natural e gelada; refil na lateral",
           Largura=0.22, Profundidade=0.27, Altura=0.35, LarguraNicho=0.13, ProfundidadeNicho=0.075, AlturaNicho=0.17)
    return c
