"""Liquidificador: base com seletor e botões, copo translúcido removível, lâminas, tampa com sobretampa."""

import math

from kit import *
from _aparelhos import tube


def cabo(c, x, y, z, comprimento=0.14, sentido=-1):
    """Passa-cabo na traseira (y), cabo que desce até a bancada e corre ao longo dela, com plugue."""
    r = 0.003
    c.cyl_y("Passa-cabo", x, z, y, 0.006, 0.014, "Borracha", detail=FINE)
    yc, rc = f"{p(y)} + 0.026", 0.008  # where the cable comes down, and its bend radius
    tube(c, "Cabo elétrico - descida", "Side", [(f"{p(y)} + 0.014", z), (f"{p(y)} + 0.018", z, -rc), (yc, f"{p(z)} - {rc}"), (yc, r + rc)], x, r, "Borracha", FINE)
    s = "-" if sentido < 0 else "+"
    tube(c, "Cabo elétrico - trecho na bancada", "Front", [(x, r + rc, rc * sentido), (f"{p(x)} {s} {rc}", r), (f"{p(x)} {s} {comprimento}", r)], yc, r, "Borracha", FINE)
    px = f"{p(x)} - {comprimento} - 0.034" if sentido < 0 else f"{p(x)} + {comprimento}"
    c.box("Plugue - corpo", px, f"{p(y)} + 0.026 - 0.017", 0, 0.034, 0.034, 0.016, "Plástico preto", detail=FINE)
    pin = f"{p(x)} - {comprimento} - 0.034 - 0.018" if sentido < 0 else f"{p(x)} + {comprimento} + 0.034"
    for i, dy in enumerate((-0.0095, 0.0095), 1):
        c.cyl_x(f"Plugue - pino {i}", f"{p(y)} + 0.026 + {dy}", 0.008, pin, 0.002, 0.018, "Latão", detail=FINE)


def build():
    c = Component("Liquidificador", "furniture", "liquidificador")
    S = c.param("Diametro", 0.20)
    H = c.param("Altura", 0.40)
    HB = c.param("AlturaBase", 0.165)
    DC = c.param("DiametroCopo", 0.16)
    EC = c.param("ElevacaoCopo", 0, "Length", True)
    c.open_pose["ElevacaoCopo"] = 0.16
    c.material("Aço das lâminas", (214, 216, 220), "Metal", "Polished", 0)

    corpo, escuro, copo_mat = "Branco", "Plástico preto", "Plástico translúcido"
    h2 = f"({S}/2)"
    zt = f"({HB}*0.55)"  # topo do bloco inferior
    rcol = f"({DC}*0.36)"  # raio do assento do copo
    rb = f"({rcol} - 0.012)"  # raio externo do fundo do copo
    rt = f"({DC}/2)"  # raio externo da boca do copo
    zj0 = f"({HB} + 0.030 + {EC})"  # fundo do copo
    z1 = f"({H} - 0.022 + {EC})"  # boca do copo
    hj = f"({H} - 0.052 - {HB})"  # altura do copo

    def rw(zrel):
        """Raio externo do copo à altura zrel acima do fundo."""
        return f"({rb} + ({rt} - {rb})*({e(zrel)})/{hj})"

    # --- volumes simplificados ---------------------------------------------
    c.profile("Base simplificada", "Plan", rrect(f"-{h2}", f"-{h2}", h2, h2, f"{S}*0.25"), 0, HB, corpo, detail=COARSE, in_plan=True)
    c.rev("Copo simplificado", "Front", [(0, f"{HB} + {EC}"), (rb, f"{HB} + {EC}"), (rt, z1), (rt, f"{H} + {EC} - 0.012"), (0, f"{H} + {EC} - 0.012")],
          0, 0, copo_mat, detail=COARSE, in_plan=True)

    # --- base -----------------------------------------------------------------
    c.profile("Base - fundo", "Plan", rrect(f"-{h2} + 0.005", f"-{h2} + 0.005", f"{h2} - 0.005", f"{h2} - 0.005", f"{S}*0.25 - 0.005"),
              0.006, 0.007, escuro)
    c.profile("Base - corpo", "Plan", rrect(f"-{h2}", f"-{h2}", h2, h2, f"{S}*0.25"), 0.012, f"{zt} - 0.012", corpo, in_plan=True)
    c.profile("Base - friso cromado", "Plan", rrect(f"-{h2} - 0.001", f"-{h2} - 0.001", f"{h2} + 0.001", f"{h2} + 0.001", f"{S}*0.25 + 0.001"),
              f"{zt} - 0.005", 0.005, "Cromado")
    c.rev("Base - ombro", "Front", [
        (0, zt), (f"{S}*0.49", zt), (f"{S}*0.49", f"{zt} + 0.006", f"{HB}*0.62"),
        (f"{rcol} + 0.005", f"{HB} - 0.010"), (rcol, HB), (0, HB)], 0, 0, corpo)
    c.rev("Assento do copo", "Front", [(f"{rcol} - 0.007", HB), (rcol, HB), (rcol, f"{HB} + 0.012"), (f"{rcol} - 0.003", f"{HB} + 0.014"),
                                       (f"{rcol} - 0.007", f"{HB} + 0.014")], 0, 0, escuro)
    c.cyl("Acoplamento do motor", 0, 0, HB, 0.015, 0.008, "Borracha")
    for i in range(6):
        a = math.radians(60 * i)
        c.cyl(f"Acoplamento do motor - dente {i + 1}", round(0.015 * math.cos(a), 5), round(0.015 * math.sin(a), 5), HB, 0.0042, 0.008,
              "Borracha", detail=FINE)
    c.cyl("Eixo do motor", 0, 0, HB, 0.004, 0.010, "Aço", detail=FINE)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        cx, sy = round(math.cos(a), 5), round(math.sin(a), 5)
        c.cyl(f"Guia de encaixe do copo {i + 1}", f"({rcol} - 0.012)*{cx}", f"({rcol} - 0.012)*{sy}", HB, 0.004, 0.006, escuro, detail=FINE)

    # pés com ventosa
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        nome = f"Pé {'frontal' if sy < 0 else 'traseiro'} {'esquerdo' if sx < 0 else 'direito'}"
        cx = f"{sx}*{S}*0.32"
        c.rev(nome, "Front", [(cx, 0.008), (f"{cx} + 0.007", 0.008), (f"{cx} + 0.013", 0), (f"{cx} + 0.0145", 0), (f"{cx} + 0.0145", 0.002),
                               (f"{cx} + 0.009", 0.0085), (cx, 0.0085)][:6] + [(cx, 0.0085)], f"{sy}*{S}*0.32", cx, "Borracha")
    # fundo: ventilação e etiqueta
    for i in range(6):
        c.box(f"Ventilação inferior {i + 1}", f"-{S}*0.2", f"{-0.03 + i * 0.012}", 0.0052, f"{S}*0.4", 0.005, 0.001, "Tela perfurada", detail=FINE)
    c.box("Etiqueta de identificação", f"-{S}*0.15", f"-{S}*0.3", 0.0054, f"{S}*0.3", f"{S}*0.12", 0.0008, "Alumínio anodizado", detail=FINE)

    # traseira: ventilação e cabo
    for i in range(6):
        c.box(f"Ventilação traseira {i + 1}", f"-{S}*0.2", f"{h2} - 0.001", f"0.030 + {i}*({zt} - 0.050)/5", f"{S}*0.4", 0.0016, 0.004,
              "Tela perfurada", detail=FINE)
    cabo(c, f"{S}*0.12", f"{h2} - 0.004", 0.022)

    # painel frontal
    yf = f"(-{h2})"
    zd = f"({zt}*0.50 + 0.004)"  # centro do seletor
    c.box("Painel de comando", f"-{S}*0.24", f"{yf} - 0.0012", 0.022, f"{S}*0.48", 0.002, f"{zt} - 0.036", "Plástico preto brilhante")
    c.cyl_y("Seletor - aro", 0, zd, f"{yf} - 0.004", 0.022, 0.004, "Cromado")
    c.rev("Seletor de velocidade", "Plan", [(0, f"{yf} - 0.004"), (0.019, f"{yf} - 0.004"), (0.017, f"{yf} - 0.020", 0.003),
                                            (0.014, f"{yf} - 0.023"), (0, f"{yf} - 0.023")], zd, 0, corpo)
    c.box("Seletor - pega", -0.004, f"{yf} - 0.030", f"{zd} - 0.016", 0.008, 0.008, 0.032, corpo, detail=FINE)
    c.box("Seletor - indicador", -0.001, f"{yf} - 0.0305", f"{zd} + 0.006", 0.002, 0.001, 0.009, "Plástico vermelho", detail=FINE)
    for i in range(7):
        a = math.radians(210 - i * 40)  # marcas de velocidade em arco sobre o seletor
        mx, mz = round(0.0275 * math.cos(a), 5), round(0.0275 * math.sin(a), 5)
        c.box(f"Marca de velocidade {i + 1}", f"{mx} - 0.0012", f"{yf} - 0.0018", f"{zd} + {mz} - 0.0012", 0.0024 + 0.0003 * i, 0.001,
              0.0024 + 0.0003 * i, "Branco", detail=FINE)
    for nome, sx in (("Pulsar", -1), ("Autolimpeza", 1)):
        bx = f"{sx}*{S}*0.185"
        c.cyl_y(f"Botão {nome} - aro", bx, f"{zd} - 0.012", f"{yf} - 0.003", 0.0085, 0.003, "Cromado", detail=FINE)
        c.cyl_y(f"Botão {nome}", bx, f"{zd} - 0.012", f"{yf} - 0.0055", 0.007, 0.0055, "Teclado", detail=FINE)
    c.cyl_y("Luz indicadora", f"{S}*0.185", f"{zd} + 0.014", f"{yf} - 0.002", 0.0025, 0.002, "Plástico verde", detail=FINE)

    # --- copo (sobe com ElevacaoCopo) ---------------------------------------
    zc0 = f"({HB} + 0.001 + {EC})"
    c.rev("Base do copo", "Front", [(0.020, zc0), (f"{rcol} - 0.008", zc0), (f"{rcol} - 0.008", f"{zc0} + 0.026"), (f"{rb} + 0.004", f"{zc0} + 0.040"),
                                    (f"{rb} - 0.002", f"{zc0} + 0.040"), (f"{rb} - 0.002", f"{zc0} + 0.028"), (0.020, f"{zc0} + 0.028")], 0, 0, escuro)
    for i in range(12):
        a = math.radians(30 * i)
        cx, sy = round(math.cos(a), 5), round(math.sin(a), 5)
        c.cyl(f"Base do copo - estria {i + 1}", f"({rcol} - 0.008)*{cx}", f"({rcol} - 0.008)*{sy}", f"{zc0} + 0.003", 0.0025, 0.020, escuro, detail=FINE)
    c.cyl("Acoplamento do copo", 0, 0, f"{zc0} + 0.008", 0.012, 0.020, "Alumínio fundido")
    c.rev("Anel de vedação", "Front", rect(f"{rb} - 0.010", f"{zj0} - 0.0015", f"{rb} - 0.003", f"{zj0} + 0.0005"), 0, 0, "Borracha cinza", detail=FINE)
    c.rev("Copo", "Front", [(0, zj0), (rb, zj0), (rt, z1), (f"{rt} - 0.003", z1), (f"{rb} - 0.003", f"{zj0} + 0.004"), (0, f"{zj0} + 0.004")],
          0, 0, copo_mat, in_plan=True)
    c.rev("Copo - borda", "Front", [(f"{rt} - 0.003", f"{z1} - 0.004"), (f"{rt} + 0.0015", f"{z1} - 0.004"), (f"{rt} + 0.0015", z1),
                                    (f"{rt} - 0.003", z1)], 0, 0, copo_mat)
    # alça à direita
    zm = f"({zj0} + 0.035)"
    xa = f"({rw(0.035)} - 0.002)"
    c.profile("Alça do copo", "Front", [
        (xa, zm), (f"{rt} + 0.034", zm, 0.014), (f"{rt} + 0.048", f"{zm} + 0.014"), (f"{rt} + 0.048", f"{z1} - 0.026", 0.014),
        (f"{rt} + 0.034", f"{z1} - 0.012"), (f"{rt} - 0.005", f"{z1} - 0.012"), (f"{rt} - 0.005", f"{z1} - 0.030"),
        (f"{rt} + 0.030", f"{z1} - 0.030"), (f"{rt} + 0.030", f"{zm} + 0.017"), (xa, f"{zm} + 0.017")],
        -0.012, 0.024, copo_mat, in_plan=True)
    c.profile("Alça - revestimento", "Front", rect(f"{rt} + 0.030", f"{zm} + 0.030", f"{rt} + 0.0495", f"{z1} - 0.040"), -0.013, 0.026, escuro)
    # bico à esquerda
    c.profile("Bico do copo", "Plan", [(f"-{rt} + 0.005", -0.020), (f"-{rt} + 0.005", 0.020), (f"-{rt} - 0.016", 0.004), (f"-{rt} - 0.016", -0.004)],
              f"{z1} - 0.022", 0.022, copo_mat, in_plan=True)
    # nervuras internas
    for i, (plano, s) in enumerate((("Front", 1), ("Front", -1), ("Side", 1), ("Side", -1)), 1):
        za, zb = f"({zj0} + 0.010)", f"({zj0} + {hj}*0.72)"
        ra, rbb = f"({rw(0.010)} - 0.003)", f"({rw(f'{hj}*0.72')} - 0.003)"
        pts = [(f"{s}*({ra} - 0.006)", za), (f"{s}*({ra} + 0.001)", za), (f"{s}*({rbb} + 0.001)", zb), (f"{s}*({rbb} - 0.003)", zb)]
        c.profile(f"Nervura interna {i}", plano, pts if s > 0 else pts[::-1], -0.002, 0.004, copo_mat, detail=FINE)
    # escala de medidas na frente do copo
    n_marcas = 8
    for i in range(n_marcas):
        zr = f"{hj}*{round(0.14 + 0.09 * i, 3)}"
        longa = i % 2 == 1
        w = 0.022 if longa else 0.012
        c.box(f"Escala do copo - marca {i + 1}", -0.004 if not longa else -0.004, f"-{rw(zr)} - 0.0006", f"{zj0} + {zr}", w, 0.0016, 0.0012,
              "Plástico vermelho", detail=FINE)
    # lâminas
    zl = f"({zj0} + 0.004)"
    c.cyl("Cubo das lâminas", 0, 0, zl, 0.011, 0.010, "Alumínio fundido")
    c.cyl("Porca das lâminas", 0, 0, f"{zl} + 0.010", 0.006, 0.007, "Aço das lâminas", detail=FINE)
    lr = f"({rb}*0.74)"
    for i, s in enumerate((1, -1), 1):
        pts = [(f"{s}*0.006", f"{zl} + 0.010"), (f"{s}*{lr}", f"{zl} + 0.028"), (f"{s}*{lr}", f"{zl} + 0.0295"), (f"{s}*0.006", f"{zl} + 0.0115")]
        c.profile(f"Lâmina superior {i}", "Front", pts if s > 0 else pts[::-1], -0.006, 0.012, "Aço das lâminas")
        pts = [(f"{s}*0.006", f"{zl} + 0.0085"), (f"{s}*{lr}", f"{zl} + 0.003"), (f"{s}*{lr}", f"{zl} + 0.0045"), (f"{s}*0.006", f"{zl} + 0.010")]
        c.profile(f"Lâmina inferior {i}", "Side", pts if s > 0 else pts[::-1], -0.006, 0.012, "Aço das lâminas")

    # tampa e sobretampa
    c.rev("Tampa", "Front", [(0.026, f"{z1} + 0.001"), (f"{rt} + 0.004", f"{z1} + 0.001"), (f"{rt} + 0.004", f"{z1} + 0.006", 0.004),
                             (f"{rt}", f"{z1} + 0.010"), (0.026, f"{z1} + 0.012")], 0, 0, escuro, in_plan=True)
    c.rev("Tampa - encaixe", "Front", rect(f"{rt} - 0.009", f"{z1} - 0.014", f"{rt} - 0.0035", f"{z1} + 0.001"), 0, 0, escuro)
    c.rev("Tampa - vedação", "Front", rect(f"{rt} - 0.0045", f"{z1} - 0.010", f"{rt} - 0.003", f"{z1} - 0.006"), 0, 0, "Borracha cinza", detail=FINE)
    c.box("Tampa - aba de abertura", -0.012, f"-{rt} - 0.012", f"{z1} + 0.003", 0.024, 0.012, 0.004, escuro, detail=FINE)
    c.rev("Sobretampa", "Front", [(0, f"{z1} + 0.012"), (0.031, f"{z1} + 0.012"), (0.031, f"{z1} + 0.015"), (0.024, f"{z1} + 0.016"),
                                  (0.021, f"{z1} + 0.022"), (0, f"{z1} + 0.022")], 0, 0, "Plástico fumê", in_plan=True)
    c.rev("Sobretampa - copo dosador", "Front", [(0.021, f"{z1} - 0.020"), (0.0255, f"{z1} + 0.012"), (0.0235, f"{z1} + 0.012"),
                                                 (0.0195, f"{z1} - 0.018"), (0, f"{z1} - 0.018"), (0, f"{z1} - 0.020")], 0, 0, "Plástico fumê")
    for i, sx in enumerate((-1, 1), 1):
        c.box(f"Sobretampa - trava {i}", f"{sx}*0.029 - 0.003", -0.004, f"{z1} + 0.0125", 0.006, 0.008, 0.003, "Plástico fumê", detail=FINE)

    c.preview_size = (0.26, 0.22, 0.40)
    c.type("Liquidificador 2 L", "Liquidificador de bancada com copo de 2 litros, seletor de velocidades e função pulsar")
    c.type("Liquidificador 3 L", "Liquidificador de bancada com copo de 3 litros, seletor de velocidades e função pulsar",
           Diametro=0.22, Altura=0.43, AlturaBase=0.175, DiametroCopo=0.18)
    return c
