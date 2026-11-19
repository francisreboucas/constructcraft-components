"""Cafeteira elétrica: base com placa aquecedora, jarra de vidro, reservatório com visor, porta-filtro sob tampa basculante."""

from kit import *
from _aparelhos import tube


def cabo(c, x, y, z, comprimento=0.14):
    """Passa-cabo na traseira (y), cabo que desce até a bancada e corre ao longo dela, com plugue."""
    r = 0.003
    c.cyl_y("Passa-cabo", x, z, y, 0.006, 0.014, "Borracha", detail=FINE)
    yc, rc = f"{p(y)} + 0.026", 0.008  # where the cable comes down, and its bend radius
    tube(c, "Cabo elétrico - descida", "Side", [(f"{p(y)} + 0.014", z), (f"{p(y)} + 0.018", z, -rc), (yc, f"{p(z)} - {rc}"), (yc, r + rc)], x, r, "Borracha", FINE)
    tube(c, "Cabo elétrico - trecho na bancada", "Front", [(x, r + rc, -rc), (f"{p(x)} - {rc}", r), (f"{p(x)} - {comprimento}", r)], yc, r, "Borracha", FINE)
    c.box("Plugue - corpo", f"{p(x)} - {comprimento} - 0.034", f"{p(y)} + 0.026 - 0.017", 0, 0.034, 0.034, 0.016, "Plástico preto", detail=FINE)
    for i, dy in enumerate((-0.0095, 0.0095), 1):
        c.cyl_x(f"Plugue - pino {i}", f"{p(y)} + 0.026 + {dy}", 0.008, f"{p(x)} - {comprimento} - 0.052", 0.002, 0.018, "Latão", detail=FINE)


def build():
    c = Component("Cafeteira elétrica", "furniture", "cafeteira")
    L = c.param("Largura", 0.16)
    P = c.param("Profundidade", 0.235)
    H = c.param("Altura", 0.27)
    HB = c.param("AlturaBase", 0.045)
    DT = c.param("ProfundidadeReservatorio", 0.075)
    AT = c.angle("AnguloTampa", 0, open_at=72)
    AJ = c.param("AvancoJarra", 0, "Length", True)
    c.open_pose["AvancoJarra"] = 0.10
    c.material("Café", (58, 34, 20), "Generic", "Glossy", 0)
    c.material("Pó de café", (44, 28, 18), "Generic", "Matte", 0)
    c.material("Filtro de papel", (226, 212, 186), "Generic", "Matte", 0)
    c.material("Água", (150, 200, 235), "Generic", "Glossy", 0.5)

    corpo = "Plástico preto"
    a = f"({L}/2)"
    y0 = f"(-{P}/2)"
    yb = f"({P}/2)"
    ycol = f"({P}/2 - {DT})"  # frente da coluna
    yc = f"(-{DT}/2)"  # centro da placa e do porta-filtro
    yj = f"({yc} - {AJ})"  # centro da jarra
    zl = f"({H} - 0.012)"  # topo do corpo, sob a tampa
    zh0 = f"({H} - 0.090)"  # fundo do cabeçote
    rj = f"({L}*0.36)"
    zb = f"({HB} + 0.004)"  # fundo da jarra
    hc = f"({zh0} - {zb} - 0.024)"  # altura da jarra
    t = 0.004
    r = 0.02

    def frente(x_half, yf, ybk, rad):
        return [(f"-{x_half} + {rad}", yf), (f"{x_half} - {rad}", yf, rad), (x_half, f"{yf} + {rad}"), (x_half, ybk), (f"-{x_half}", ybk),
                (f"-{x_half}", f"{yf} + {rad}", rad)]

    # --- volumes simplificados ---------------------------------------------
    c.profile("Corpo simplificado", "Side", [(y0, 0), (yb, 0), (yb, H), (y0, H), (y0, zh0), (ycol, zh0), (ycol, HB), (y0, HB)],
              f"-{a}", L, corpo, detail=COARSE, in_plan=True)
    c.cyl("Jarra simplificada", 0, yj, HB, rj, f"{hc} + 0.008", "Vidro temperado", detail=COARSE, in_plan=True)

    # --- base -----------------------------------------------------------------
    c.profile("Base - fundo", "Plan", frente(f"({a} - 0.004)", f"({y0} + 0.004)", f"({yb} - 0.004)", r - 0.004), 0.005, 0.005, "Plástico cinza")
    c.profile("Base", "Plan", frente(a, y0, yb, r), 0.009, f"{HB} - 0.009", corpo, in_plan=True)
    c.cyl("Placa aquecedora", 0, yc, HB, f"{rj}*0.92", 0.003, "Aço pintado preto")
    c.rev("Placa aquecedora - aro", "Front", rect(f"{rj}*0.92", HB, f"{rj}*0.92 + 0.005", f"{HB} + 0.0045"), yc, 0, "Inox escovado")
    for i in range(3):
        c.rev(f"Placa aquecedora - friso {i + 1}", "Front", rect(f"{rj}*{0.25 + 0.22 * i}", f"{HB} + 0.003", f"{rj}*{0.25 + 0.22 * i} + 0.002", f"{HB} + 0.0036"),
              yc, 0, "Aço pintado cinza", detail=FINE)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        nome = f"Pé {'frontal' if sy < 0 else 'traseiro'} {'esquerdo' if sx < 0 else 'direito'}"
        c.cyl(nome, f"{sx}*({a} - 0.022)", f"{sy}*({yb} - 0.024)", 0, 0.009, 0.006, "Borracha")
        c.cyl(f"Parafuso da base {i}", f"{sx}*({a} - 0.022)", f"{sy}*({yb} - 0.050)", 0.0042, 0.003, 0.001, "Aço", detail=FINE)
    for i in range(6):
        c.box(f"Ventilação inferior {i + 1}", f"-{L}*0.22", f"{yc} + {-0.030 + 0.012 * i}", 0.0043, f"{L}*0.44", 0.005, 0.001, "Tela perfurada", detail=FINE)
    c.box("Etiqueta de identificação", f"-{L}*0.2", f"{yb} - 0.0008", f"{HB} + 0.02", f"{L}*0.4", 0.0015, 0.03, "Alumínio anodizado", detail=FINE)
    # interruptor na frente da base
    xs = f"({L}*0.2)"
    zs = f"({HB}/2 + 0.004)"
    c.box("Interruptor - moldura", f"{xs} - 0.013", f"{y0} - 0.0015", f"{zs} - 0.010", 0.026, 0.002, 0.020, "Plástico preto brilhante", detail=FINE)
    c.profile("Interruptor - tecla", "Side", [(f"{y0} - 0.0015", f"{zs} - 0.008"), (f"{y0} - 0.0015", f"{zs} + 0.008"), (f"{y0} - 0.0035", f"{zs} + 0.008"),
                                             (f"{y0} - 0.0065", f"{zs} - 0.008")], f"{xs} - 0.011", 0.022, "Plástico vermelho", detail=FINE)
    c.cyl_y("Luz indicadora", f"-{L}*0.2", zs, f"{y0} - 0.002", 0.004, 0.003, "Plástico vermelho", detail=FINE)
    c.cyl_y("Luz indicadora - aro", f"-{L}*0.2", zs, f"{y0} - 0.001", 0.006, 0.002, "Cromado", detail=FINE)
    cabo(c, f"{L}*0.18", f"{yb} - 0.004", 0.022)

    # --- coluna do reservatório ----------------------------------------------
    hcol = f"({zl} - {HB})"
    c.box("Coluna - parede frontal", f"-{a} + {t}", ycol, HB, f"{L} - {2 * t}", t, hcol, corpo)
    c.box("Coluna - parede traseira", f"-{a}", f"{yb} - {t}", HB, L, t, hcol, corpo)
    y_v0, y_v1 = f"({ycol} + {DT}*0.30)", f"({ycol} + {DT}*0.62)"  # visor de nível
    zv0, zv1 = f"({HB} + 0.018)", f"({zl} - 0.022)"
    for lado, sx in (("esquerda", -1), ("direita", 1)):
        x = f"-{a}" if sx < 0 else f"{a} - {t}"
        c.box(f"Coluna - parede {lado}, trecho frontal", x, ycol, HB, t, f"{DT}*0.30", hcol, corpo)
        c.box(f"Coluna - parede {lado}, trecho traseiro", x, y_v1, HB, t, f"{DT}*0.38 - {t}", hcol, corpo)
        c.box(f"Coluna - parede {lado}, sob o visor", x, y_v0, HB, t, f"{DT}*0.32", 0.018, corpo)
        c.box(f"Coluna - parede {lado}, sobre o visor", x, y_v0, zv1, t, f"{DT}*0.32", 0.022, corpo)
        c.box(f"Visor de nível {'esquerdo' if sx < 0 else 'direito'}", f"-{a} + 0.0008" if sx < 0 else f"{a} - {t}", y_v0, zv0, t - 0.0008,
              f"{DT}*0.32", f"{zv1} - {zv0}", "Plástico translúcido")
        for i in range(5):
            longa = i % 2 == 0
            c.box(f"Visor de nível {'esquerdo' if sx < 0 else 'direito'} - marca {i + 1}", f"-{a} + 0.0002" if sx < 0 else f"{a} - 0.0008",
                  y_v0, f"{zv0} + ({zv1} - {zv0})*{0.15 + 0.17 * i}", 0.0006, f"{DT}*{0.2 if longa else 0.12}", 0.0012, "Branco", detail=FINE)
    zw = f"({HB} + {hcol}*0.6)"
    c.box("Reservatório - fundo", f"-{a} + {t}", f"{ycol} + {t}", HB, f"{L} - {2 * t}", f"{DT} - {2 * t}", 0.004, "Plástico cinza claro")
    c.box("Água do reservatório", f"-{a} + {t} + 0.0005", f"{ycol} + {t} + 0.0005", f"{HB} + 0.004", f"{L} - {2 * t} - 0.001", f"{DT} - {2 * t} - 0.001",
          f"{zw} - {HB} - 0.004", "Água")
    c.cyl("Tubo de subida da água", 0, f"{yb} - 0.016", f"{HB} + 0.004", 0.005, f"{zl} - {HB} - 0.012", "Alumínio anodizado")
    c.cyl("Válvula do reservatório", 0, f"{yb} - 0.016", f"{HB} + 0.004", 0.009, 0.006, "Plástico cinza", detail=FINE)

    # --- cabeçote com porta-filtro ---------------------------------------------
    c.profile("Cabeçote - parede", "Plan", [
        (f"-{a}", ycol), (f"-{a}", f"{y0} + {r}", r), (f"-{a} + {r}", y0), (f"{a} - {r}", y0, r), (a, f"{y0} + {r}"), (a, ycol),
        (f"{a} - {t}", ycol), (f"{a} - {t}", f"{y0} + {r}"), (f"{a} - {r}", f"{y0} + {t}"), (f"-{a} + {r}", f"{y0} + {t}"),
        (f"-{a} + {t}", f"{y0} + {r}")] + [(f"-{a} + {t}", ycol)], zh0, f"{zl} - {zh0}", corpo, in_plan=True)
    c.profile("Cabeçote - fundo", "Plan", frente(f"({a} - 0.002)", f"({y0} + 0.002)", ycol, r - 0.002), zh0, 0.004, corpo)
    c.box("Faixa frontal", f"-{a} + {r}", f"{y0} - 0.0008", f"{zh0} + 0.022", f"{L} - {2 * r}", 0.001, 0.030, "Inox escovado")
    rk = f"({a} - 0.012)"  # raio da boca do porta-filtro
    zk0, zk1 = f"({zh0} + 0.004)", f"({zl} - 0.018)"
    c.rev("Porta-filtro", "Front", [(0.007, zk0), (0.024, zk0), (rk, zk1), (f"{rk} + 0.004", zk1), (f"{rk} + 0.004", f"{zk1} + 0.003"),
                                    (f"{rk} - 0.003", f"{zk1} + 0.003"), (0.021, f"{zk0} + 0.003"), (0.007, f"{zk0} + 0.003")], yc, 0, "Plástico cinza")
    c.box("Porta-filtro - alça", -0.012, f"{yc} - {rk} - 0.008", f"{zk1} + 0.001", 0.024, 0.012, 0.003, "Plástico cinza", detail=FINE)
    for i, (dx, dy) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1)), 1):
        if dx:
            pts = [(f"{dx}*0.010", f"{zk0} + 0.003"), (f"{dx}*0.021", f"{zk0} + 0.003"), (f"{dx}*({rk} - 0.004)", f"{zk1} - 0.004"), (f"{dx}*({rk} - 0.008)", f"{zk1} - 0.004")]
            c.profile(f"Porta-filtro - nervura {i}", "Front", pts if dx > 0 else pts[::-1], f"{yc} - 0.001", 0.002, "Plástico cinza", detail=FINE)
        else:
            pts = [(f"{yc} + {dy}*0.010", f"{zk0} + 0.003"), (f"{yc} + {dy}*0.021", f"{zk0} + 0.003"), (f"{yc} + {dy}*({rk} - 0.004)", f"{zk1} - 0.004"),
                   (f"{yc} + {dy}*({rk} - 0.008)", f"{zk1} - 0.004")]
            c.profile(f"Porta-filtro - nervura {i}", "Side", pts if dy > 0 else pts[::-1], -0.001, 0.002, "Plástico cinza", detail=FINE)
    zf0, zf1 = f"({zk0} + 0.007)", f"({zk1} + 0.006)"
    rf = f"({rk} - 0.005)"
    c.rev("Filtro de papel", "Front", [(0, zf0), (0.018, zf0), (rf, zf1), (f"{rf} - 0.001", zf1), (0.0175, f"{zf0} + 0.001"), (0, f"{zf0} + 0.001")],
          yc, 0, "Filtro de papel")
    c.rev("Pó de café", "Front", [(0, f"{zf0} + 0.001"), (0.0172, f"{zf0} + 0.001"), (f"0.0172 + ({rf} - 0.0185)*0.4", f"{zf0} + ({zf1} - {zf0})*0.4"),
                                  (0, f"{zf0} + ({zf1} - {zf0})*0.34")], yc, 0, "Pó de café")
    c.cyl("Válvula corta-pingo", 0, yc, f"{zh0} - 0.009", 0.010, 0.009, "Plástico cinza")
    c.cyl("Válvula corta-pingo - pino", 0, yc, f"{zh0} - 0.013", 0.0035, 0.004, "Branco", detail=FINE)
    # braço do chuveiro, da coluna até o centro do filtro
    c.box("Braço do chuveiro", -0.008, f"{yc} - 0.004", f"{zl} - 0.011", 0.016, f"{yb} - 0.012 - {yc}", 0.007, "Plástico cinza claro")
    c.cyl("Chuveiro", 0, yc, f"{zl} - 0.016", 0.017, 0.012, "Plástico cinza claro")
    for i, (dx, dy) in enumerate(((0, 0), (0.009, 0), (-0.009, 0), (0, 0.009), (0, -0.009)), 1):
        c.cyl(f"Chuveiro - furo {i}", dx, f"{yc} + {dy}", f"{zl} - 0.0165", 0.0015, 0.0006, "Borracha", detail=FINE)

    # --- tampa basculante (dobradiça atrás) ---------------------------------
    hinge = (f"({yb} - 0.004)", f"({zl} + 0.001)")
    RL = f"({P} - 0.004)"
    xl = f"(-{a})"
    c.lid_box("Tampa", hinge, AT, xl, L, 0, f"{RL} - 0.014", 0, 0.011, corpo)
    c.lid_box("Tampa - chanfro frontal 1", hinge, AT, f"{xl} + 0.005", f"{L} - 0.010", f"{RL} - 0.014", f"{RL} - 0.006", 0, 0.011, corpo)
    c.lid_box("Tampa - chanfro frontal 2", hinge, AT, f"{xl} + 0.013", f"{L} - 0.026", f"{RL} - 0.006", RL, 0, 0.011, corpo)
    c.lid_box("Tampa - pega", hinge, AT, -0.022, 0.044, RL, f"{RL} + 0.009", 0.003, 0.008, corpo, detail=FINE)
    c.lid_box("Tampa - forro interno", hinge, AT, f"{xl} + 0.008", f"{L} - 0.016", f"{DT} + 0.004", f"{RL} - 0.022", -0.004, 0, "Plástico cinza")
    c.lid_box("Tampa - friso", hinge, AT, f"{xl} + 0.012", f"{L} - 0.024", f"{DT}", f"{DT} + 0.002", 0.011, 0.0118, "Plástico cinza", detail=FINE)
    for i in range(5):
        c.lid_box(f"Tampa - saída de vapor {i + 1}", hinge, AT, f"{-0.024 + 0.0105 * i}", 0.006, f"{RL}*0.62", f"{RL}*0.62 + 0.022", 0.011, 0.0116,
                  "Borracha", detail=FINE)
    for i, sx in enumerate((-1, 1), 1):
        c.cyl_x(f"Dobradiça da tampa {i}", hinge[0], f"{hinge[1]} + 0.003", f"{sx}*({a} - 0.030) - 0.010", 0.004, 0.020, corpo, detail=FINE)

    # --- jarra (desliza para a frente com AvancoJarra) -----------------------
    zt1 = f"({zb} + {hc})"
    c.rev("Jarra", "Front", [
        (0, zb), (f"{rj}*0.82", zb, f"{hc}*0.45"), (rj, f"{zb} + {hc}*0.38", f"{hc}*0.9"), (f"{rj}*0.74", f"{zb} + {hc}*0.9"), (f"{rj}*0.76", zt1),
        (f"{rj}*0.76 - 0.003", zt1), (f"{rj}*0.74 - 0.003", f"{zb} + {hc}*0.9"), (f"{rj} - 0.003", f"{zb} + {hc}*0.38"),
        (f"{rj}*0.82 - 0.003", f"{zb} + 0.004"), (0, f"{zb} + 0.004")], yj, 0, "Vidro temperado", in_plan=True)
    c.rev("Café na jarra", "Front", [(0, f"{zb} + 0.0045"), (f"{rj}*0.82 - 0.0036", f"{zb} + 0.0045"), (f"{rj} - 0.0036", f"{zb} + {hc}*0.38"),
                                     (f"{rj}*0.94 - 0.0036", f"{zb} + {hc}*0.5"), (0, f"{zb} + {hc}*0.5")], yj, 0, "Café")
    c.rev("Jarra - cinta", "Front", [(f"{rj}*0.74 - 0.0005", f"{zb} + {hc}*0.86"), (f"{rj}*0.76 + 0.004", f"{zb} + {hc}*0.86"), (f"{rj}*0.76 + 0.004", f"{zt1} + 0.002"),
                                     (f"{rj}*0.76 - 0.0005", f"{zt1} + 0.002")], yj, 0, corpo)
    yo = f"({yj} - {rj} - 0.034)"
    ya = f"({yj} - {rj}*0.76 - 0.002)"
    zlow = f"({zb} + {hc}*0.22)"
    c.profile("Jarra - alça", "Side", [
        (ya, f"{zt1} + 0.002"), (f"{yo} + 0.012", f"{zt1} + 0.002", 0.012), (yo, f"{zt1} - 0.010"), (yo, f"{zlow} + 0.010", 0.010), (f"{yo} + 0.010", zlow),
        (f"{yo} + 0.014", zlow), (f"{yo} + 0.014", f"{zt1} - 0.014"), (ya, f"{zt1} - 0.014")], -0.011, 0.022, corpo, in_plan=True)
    c.profile("Jarra - bico", "Plan", [(f"-{rj}*0.76 + 0.004", f"{yj} - 0.014"), (f"-{rj}*0.76 + 0.004", f"{yj} + 0.014"), (f"-{rj}*0.76 - 0.012", f"{yj} + 0.003"),
                                      (f"-{rj}*0.76 - 0.012", f"{yj} - 0.003")], f"{zt1} - 0.008", 0.010, corpo)
    c.rev("Jarra - tampa", "Front", [(0.007, f"{zt1} + 0.002"), (f"{rj}*0.76 + 0.002", f"{zt1} + 0.002"), (f"{rj}*0.76 + 0.002", f"{zt1} + 0.006"),
                                     (0.022, f"{zt1} + 0.008"), (0.007, f"{zt1} + 0.004")], yj, 0, corpo, in_plan=True)
    c.box("Jarra - apoio do polegar", -0.008, f"{ya} - 0.016", f"{zt1} + 0.006", 0.016, 0.022, 0.004, corpo, detail=FINE)
    for i in range(4):
        zr = f"{hc}*{0.2 + 0.14 * i}"
        c.box(f"Jarra - marca de nível {i + 1}", f"{rj}*{[0.93, 0.985, 0.96, 0.89][i]} - 0.0008", f"{yj} - 0.007", f"{zb} + {zr}", 0.0016, 0.014, 0.0012,
              "Branco", detail=FINE)

    c.preview_size = (0.18, 0.26, 0.28)
    c.type("Cafeteira 15 xícaras (0,6 L)", "Cafeteira elétrica de filtro com jarra de vidro para 15 xícaras (0,6 L) e placa aquecedora")
    c.type("Cafeteira 30 xícaras (1,2 L)", "Cafeteira elétrica de filtro com jarra de vidro para 30 xícaras (1,2 L) e placa aquecedora",
           Largura=0.19, Profundidade=0.275, Altura=0.32, ProfundidadeReservatorio=0.085)
    return c
