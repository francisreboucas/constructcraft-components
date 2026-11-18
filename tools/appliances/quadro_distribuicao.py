"""Quadro de distribuição de embutir (QDC): caixa de aço galvanizado dentro da parede, moldura, porta com visor fumê
(abre com AnguloPorta), espelho interno com as janelas das fileiras de disjuntores DIN, trilhos TS35, disjuntor geral
bipolar, interruptor DR, disjuntores dos circuitos, barramentos de neutro e de terra e etiquetas.

Dispositivo de parede: a face da parede em y = 0, a frente em -y, a base em z = 0 (o ConstructCraft aplica a
altura de montagem, 1,30 m nos quadros), centrado em x = 0. A caixa vai de y = 0 a y = Profundidade, dentro da parede.

Tamanhos: `Fileiras` (1 a 3) trilhos de 12 módulos de 18 mm; na primeira ficam o geral (2 módulos) e o DR (2 módulos).
`Circuitos` disjuntores unipolares ocupam as posições seguintes; as que sobram ficam fechadas por tampas cegas.
Os disjuntores e as fileiras que um tipo não tem encolhem (escala 0.005) para dentro do espelho.
"""

from kit import *
import _eletrica as el

EPS = 0.005
MOD = 0.018  # passo de um módulo DIN
NMOD = 12  # módulos por fileira
XW = NMOD * MOD / 2  # meia largura da janela de uma fileira
PASSO = 0.125  # entre fileiras
YE = 0.012  # face da frente do espelho interno
TE = 0.0015  # espessura do espelho
YF = 0.006  # frente dos disjuntores (passam 6 mm à frente do espelho)
YS = 0.026  # degrau dos disjuntores
YR = 0.074  # costas dos disjuntores = frente do trilho
FUME = "Acrílico fumê"  # visor da porta: escuro, mas deixa ver os disjuntores


class G:
    """Peças escaladas por `k` em torno do ponto `h` (k = EPS: recolhidas dentro do espelho)."""

    def __init__(self, c, k=None, h=(0, 0, 0)):
        self.c, self.k, self.h = c, k, h

    def _at(self, i, v):
        return e(v) if self.k is None else f"{p(self.h[i])} + {p(self.k)}*({e(v)} - {p(self.h[i])})"

    def l(self, v):
        return e(v) if self.k is None else f"{p(self.k)}*{p(v)}"

    def box(self, name, x0, x1, y0, y1, z0, z1, mat, **kw):
        self.c.box(name, self._at(0, x0), self._at(1, y0), self._at(2, z0),
                   self.l(f"{p(x1)} - {p(x0)}"), self.l(f"{p(y1)} - {p(y0)}"), self.l(f"{p(z1)} - {p(z0)}"), mat, **kw)

    def side(self, name, pts, x0, width, mat, **kw):
        """Contorno (y, z) de lado, de x0 a x0 + width."""
        self.c.profile(name, "Side", [(self._at(1, a), self._at(2, b)) for a, b in pts], self._at(0, x0), self.l(width), mat, **kw)


def disjuntor(g, name, x0, n, zc, alavanca="Plástico preto", dr=False):
    """Disjuntor DIN de n módulos com o lado esquerdo em x0, centrado na altura zc."""
    zc = p(zc)
    w = n * MOD

    def z(d):
        return f"{zc} + {d}" if d >= 0 else f"{zc} - {-d}"

    corpo = [(YF, z(-0.0225)), (YF, z(0.0225)), (YS, z(0.0225)), (YS + 0.006, z(0.045)), (YR, z(0.045)), (YR, z(-0.045)),
             (YS + 0.006, z(-0.045)), (YS, z(-0.0225))]
    g.side(name, corpo, f"{x0} + 0.0002", w - 0.0004, "Branco")
    if n == 1:
        g.box(f"{name} - alavanca", f"{x0} + 0.005", f"{x0} + 0.013", YF - 0.009, YF, z(-0.002), z(0.012), alavanca)
    else:
        g.box(f"{name} - alavanca", f"{x0} + 0.004", f"{x0} + {w / 2 - 0.002:.4f}" if dr else f"{x0} + {w - 0.004:.4f}",
              YF - 0.009, YF, z(-0.002), z(0.012), alavanca)
    g.box(f"{name} - etiqueta", f"{x0} + 0.002", f"{x0} + {w - 0.002:.4f}", YF - 0.0003, YF, z(-0.019), z(-0.007), "Plástico cinza claro", detail=FINE)
    if n > 1:
        g.box(f"{name} - indicador", f"{x0} + 0.004", f"{x0} + 0.012", YF - 0.0004, YF, z(0.015), z(0.019), "Plástico verde", detail=FINE)
    if dr:
        g.box(f"{name} - botão de teste", f"{x0} + {w / 2 + 0.004:.4f}", f"{x0} + {w - 0.005:.4f}", YF - 0.003, YF, z(0.002), z(0.01),
              "Plástico cinza", detail=FINE)


def build():
    c = Component("Quadro de distribuição (QDC)", "electrical", "quadro-distribuicao", "Electrical")
    L = c.param("Largura", 0.3)
    A = c.param("Altura", 0.35)
    P = c.param("Profundidade", 0.1)
    NF = c.param("Fileiras", 1, "Number")
    NC = c.param("Circuitos", 6, "Number")
    ang = c.angle("AnguloPorta", 0, open_at=100)
    c.mep = {"Device": {"device": "Panel", "power": 0}}
    c.connector("Eletrodutos", "Power", 0, f"{P} / 2", f"{A} - 0.015", "Up")
    el.materiais(c)
    c.material(FUME, (120, 124, 130), "Plastic", "Glossy", 0.7)
    c.type("QD 12 disjuntores", "Quadro de distribuição de embutir, 12 módulos DIN", Largura=0.3, Altura=0.35)
    c.type("QD 24 disjuntores", "Quadro de distribuição de embutir, 24 módulos DIN", Largura=0.4, Altura=0.5, Fileiras=2, Circuitos=14)
    c.type("QD 36 disjuntores", "Quadro de distribuição de embutir, 36 módulos DIN", Largura=0.45, Altura=0.65, Fileiras=3, Circuitos=24)
    c.preview_base = 1.30  # make.py coloca o quadro à altura de montagem

    hl = f"({L}/2)"
    f = 0.025  # largura da moldura
    yfm = -0.02  # frente da moldura
    bx = 0.015  # recuo da caixa em relação à moldura
    t = 0.0012  # chapa da caixa
    BRANCO, GALV = "Aço pintado branco", "Aço galvanizado"
    zt = f"({A} - {bx + 0.0015})"  # topo do espelho
    zb = f"({zt} - {PASSO}*{NF})"  # base do espelho: abaixo dele, os barramentos

    def zr(r):  # centro da fileira r
        return f"({zt} - {0.0625 + PASSO * (r - 1):.4f})"

    hide = (-(XW + 0.012), YE + TE / 2, zr(1))  # ponto dentro da lateral esquerda do espelho

    def row_k(r):
        return None if r == 1 else f"min(1, max({EPS}, {NF} - {r - 1}))"

    # --- simplificado ---------------------------------------------------------------------------
    c.box("Volume simplificado", f"-{hl}", yfm, 0, L, -yfm, A, BRANCO, detail=COARSE, in_plan=True)
    c.box("Caixa simplificada", f"-{hl} + {bx}", 0, bx, f"{L} - {2 * bx}", P, f"{A} - {2 * bx}", GALV, detail=COARSE, in_plan=True)

    # --- caixa de embutir, dentro da parede ---------------------------------------------------------
    xi, zi0, zi1 = f"({hl} - {bx})", bx, f"({A} - {bx})"
    c.box("Caixa - fundo", f"-{xi}", f"{P} - {t}", zi0, f"2*{xi}", t, f"{zi1} - {zi0}", GALV)
    c.box("Caixa - lateral esquerda", f"-{xi}", 0, zi0, t, f"{P} - {t}", f"{zi1} - {zi0}", GALV, in_plan=True)
    c.box("Caixa - lateral direita", f"{xi} - {t}", 0, zi0, t, f"{P} - {t}", f"{zi1} - {zi0}", GALV, in_plan=True)
    c.box("Caixa - base", f"-{xi} + {t}", 0, zi0, f"2*{xi} - {2 * t}", f"{P} - {t}", t, GALV)
    c.box("Caixa - topo", f"-{xi} + {t}", 0, f"{zi1} - {t}", f"2*{xi} - {2 * t}", f"{P} - {t}", t, GALV)
    for i, x in enumerate((-0.06, 0, 0.06), 1):
        c.cyl(f"Caixa - pré-furo superior {i}", f"{x}*{L}/0.3", f"{P}/2", zi1, 0.0125, 0.0006, GALV, detail=FINE)
        c.cyl(f"Caixa - pré-furo inferior {i}", f"{x}*{L}/0.3", f"{P}/2", f"{zi0} - 0.0006", 0.0125, 0.0006, GALV, detail=FINE)

    # --- moldura, saliente na parede ------------------------------------------------------------------
    c.box("Moldura superior", f"-{hl}", yfm, f"{A} - {f}", L, -yfm, f, BRANCO, in_plan=True)
    c.box("Moldura inferior", f"-{hl}", yfm, 0, L, -yfm, f, BRANCO, in_plan=True)
    c.box("Moldura esquerda", f"-{hl}", yfm, f, f, -yfm, f"{A} - {2 * f}", BRANCO, in_plan=True)
    c.box("Moldura direita", f"{hl} - {f}", yfm, f, f, -yfm, f"{A} - {2 * f}", BRANCO, in_plan=True)

    # --- espelho interno: laterais e faixas acima e abaixo da janela de cada fileira ----------------------------
    xe = f"({hl} - {bx + t + 0.0003})"
    G(c).box("Espelho - lateral esquerda", f"-{xe}", f"-{XW}", YE, YE + TE, zb, zt, BRANCO)
    G(c).box("Espelho - lateral direita", XW, xe, YE, YE + TE, zb, zt, BRANCO)
    for r in (1, 2, 3):
        g = G(c, row_k(r), hide)
        z = zr(r)
        g.box(f"Espelho - faixa acima da fileira {r}", -XW, XW, YE, YE + TE, f"{z} + 0.0235", f"{z} + 0.0625", BRANCO)
        g.box(f"Espelho - faixa abaixo da fileira {r}", -XW, XW, YE, YE + TE, f"{z} - 0.0625", f"{z} - 0.0235", BRANCO)
        g.box(f"Etiqueta da fileira {r}", -XW + 0.004, XW - 0.004, YE - 0.0003, YE, f"{z} + 0.029", f"{z} + 0.041", "Plástico cinza claro", detail=FINE)
        # trilho DIN TS35 x 7,5
        y0, y1, s = YR, YR + 0.0075, 0.001
        hat = [(y0, -0.0175), (y0 + s, -0.0175), (y0 + s, -0.0135), (y1, -0.0135), (y1, 0.0135), (y0 + s, 0.0135), (y0 + s, 0.0175),
               (y0, 0.0175), (y0, 0.0125), (y1 - s, 0.0125), (y1 - s, -0.0125), (y0, -0.0125)]
        g.side(f"Trilho DIN {r}", [(a, f"{z} + {b}") for a, b in hat], -XW - 0.008, 2 * XW + 0.016, GALV)
        g.box(f"Trilho DIN {r} - suporte esquerdo", -XW - 0.008, -XW, y1, f"{P} - {t}", f"{z} - 0.01", f"{z} + 0.01", GALV)
        g.box(f"Trilho DIN {r} - suporte direito", XW, XW + 0.008, y1, f"{P} - {t}", f"{z} - 0.01", f"{z} + 0.01", GALV)
        # tampa cega nas posições livres, à direita
        n = f"min({NMOD}, max(0, {NC} + 4 - {NMOD * (r - 1)}))"
        w = f"max(0.001, ({NMOD} - {n})*{MOD})"
        g.box(f"Tampa cega da fileira {r}", f"{XW} - {w}", XW, YE - 0.0005, YE + TE, f"{z} - 0.0235", f"{z} + 0.0235", BRANCO)

    # --- disjuntores ---------------------------------------------------------------------------------------
    x0 = -XW
    disjuntor(G(c), "Disjuntor geral bipolar", f"{x0}", 2, zr(1))
    disjuntor(G(c), "Interruptor DR", f"{x0 + 2 * MOD:.4f}", 2, zr(1), alavanca="Plástico azul", dr=True)
    j = 0
    for r in (1, 2, 3):
        for m in range(5 if r == 1 else 1, NMOD + 1):
            j += 1
            k = f"min(1, max({EPS}, min({NC} - {j - 1}, {NF} - {r - 1})))"
            disjuntor(G(c, k, hide), f"Disjuntor {j}", f"{x0 + (m - 1) * MOD:.4f}", 1, zr(r))

    # --- barramentos de neutro e de terra, abaixo do espelho ---------------------------------------------------
    zbar = f"({zb} - 0.035)"
    for nome, xa, isol, fio in (("neutro", -0.105, "Plástico azul", "Plástico azul"), ("terra", 0.015, "Plástico verde", "Plástico verde")):
        xb = xa + 0.09
        c.box(f"Barramento de {nome}", xa, f"0.04", f"{zbar} - 0.004", 0.09, 0.008, 0.008, "Latão")
        for i, xs in enumerate((xa - 0.004, xb - 0.008), 1):
            c.box(f"Barramento de {nome} - isolador {i}", xs, 0.048, f"{zbar} - 0.009", 0.012, f"{P} - {t} - 0.048", 0.018, isol)
        for i in range(7):
            xc = xa + 0.009 + i * 0.012
            c.cyl_y(f"Barramento de {nome} - parafuso {i + 1}", xc, zbar, 0.0385, 0.0022, 0.0015, GALV, detail=FINE)
        for i in range(3):
            xc = xa + 0.015 + i * 0.024
            c.cyl(f"Condutor de {nome} {i + 1}", xc, 0.044, f"{zbar} + 0.004", 0.0018, f"{zb} - {zbar} + 0.008", fio, detail=FINE)

    # --- porta com visor fumê, dobradiças à esquerda -------------------------------------------------------------
    gap = 0.0015
    hinge = (f"-{hl} + {f} + {gap}", yfm + 0.0005)
    Wd = f"({L} - {2 * f + 2 * gap})"
    z0, z1 = f + gap, f"({A} - {f + gap})"
    mw = 0.03
    zw1 = f"({z1} - {mw})"
    zw0 = f"max({z0} + 0.06, {zb})"
    bd = (-0.012, 0)

    def porta(name, a0, a1, b, za, zb_, mat, **kw):
        c.door_box(name, hinge, ang, a0, a1, b[0], b[1], za, f"{p(zb_)} - {p(za)}", mat, **kw)

    porta("Porta - montante esquerdo", 0, mw, bd, z0, z1, BRANCO, in_plan=True)
    porta("Porta - montante direito", f"{Wd} - {mw}", Wd, bd, z0, z1, BRANCO, in_plan=True)
    porta("Porta - travessa superior", mw, f"{Wd} - {mw}", bd, zw1, z1, BRANCO, in_plan=True)
    porta("Porta - travessa inferior", mw, f"{Wd} - {mw}", bd, z0, zw0, BRANCO, in_plan=True)
    porta("Porta - visor", mw, f"{Wd} - {mw}", (-0.008, -0.005), zw0, zw1, FUME)
    porta("Porta - vedação do visor", f"{mw} - 0.002", f"{Wd} - {mw} + 0.002", (-0.0085, -0.008), f"{zw0} - 0.002", f"{zw1} + 0.002", "Borracha",
          detail=FINE)
    zm = f"(({zw0} + {zw1})/2)"
    porta("Fecho", f"{Wd} - 0.02", f"{Wd} - 0.008", (0, 0.004), f"{zm} - 0.022", f"{zm} + 0.022", "Plástico cinza")
    porta("Fecho - lingueta", f"{Wd} - 0.017", f"{Wd} - 0.011", (0.004, 0.0065), f"{zm} - 0.008", f"{zm} + 0.008", "Plástico preto", detail=FINE)
    porta("Etiqueta de advertência", f"{Wd}/2 - 0.035", f"{Wd}/2 + 0.035", (0, 0.0004), f"{zw0} - 0.055", f"{zw0} - 0.015", "PVC amarelo", detail=FINE)
    porta("Etiqueta de advertência - símbolo", f"{Wd}/2 - 0.005", f"{Wd}/2 + 0.005", (0.0004, 0.0006), f"{zw0} - 0.047", f"{zw0} - 0.023",
          "Plástico preto", detail=FINE)
    porta("Etiqueta de identificação", f"{Wd}/2 - 0.03", f"{Wd}/2 + 0.03", (0, 0.0004), f"{zw1} + 0.008", f"{zw1} + 0.02", "Alumínio anodizado",
          detail=FINE)
    for i, zh in enumerate((f"{z0} + 0.03", f"{z1} - 0.06"), 1):
        c.cyl(f"Dobradiça {i}", hinge[0], hinge[1], zh, 0.003, 0.03, "Cromado", detail=FINE)
    return c
