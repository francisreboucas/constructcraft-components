"""Construção compartilhada pelos dispositivos elétricos de embutir (caixas 4x2 e 4x4).

Dispositivo de parede: face da parede em y = 0, frente em -y, base em z = 0.
A placa ocupa y de -0.008 a 0; atrás da parede (y > 0) ficam a caixa de embutir
e o corpo dos módulos. Um `Mod` é um módulo (tomada, tecla, conector) com centro
(cx, cz) e uma escala `s`: com s perto de zero o módulo some dentro da placa
(a engine recusa tamanho zero, por isso o mínimo é 0.01).
"""

from kit import *

Y0 = -0.004  # miolo da placa: para onde os módulos não usados encolhem
PASSO_COLUNA = 0.0225  # meio passo entre as duas colunas de uma placa 4x4
PASSO_LINHA = 0.0235  # passo vertical entre módulos empilhados
CAIXA = "PVC amarelo"
SUPORTE = "Plástico cinza claro"


def materiais(c):
    c.material(CAIXA, (226, 186, 52), "Plastic", "Matte", 0)


def presente(expr) -> str:
    """Escala 1 quando `expr` >= 1 e 0.01 quando <= 0 (módulo recolhido)."""
    return f"min(1, max(0.01, {expr}))"


class Mod:
    def __init__(self, cx, cz, s=None):
        self.cx, self.cz, self.s = p(cx), p(cz), (None if s is None else f"({s})")

    def k(self, v):
        """Um comprimento do módulo, na sua escala."""
        return e(v) if self.s is None else f"({e(v)})*{self.s}"

    def x(self, d):
        return f"{self.cx} + {self.k(d)}"

    def z(self, d):
        return f"{self.cz} + {self.k(d)}"

    def y(self, ya):
        """y absoluto `ya` do módulo em tamanho real."""
        return e(ya) if self.s is None else f"{e(Y0)} + ({e(ya - Y0)})*{self.s}"

    # peças no referencial do módulo -------------------------------------
    def rrect(self, c, nome, hw, hh, r, y0, y1, mat, dx=0, dz=0, **kw):
        """Retângulo arredondado de frente, centrado em (dx, dz), de y0 a y1."""
        pts = rrect(self.x(dx - hw), self.z(dz - hh), self.x(dx + hw), self.z(dz + hh), self.k(r))
        c.profile(nome, "Front", pts, self.y(y0), self.k(y1 - y0), mat, **kw)

    def box(self, c, nome, x0, x1, y0, y1, z0, z1, mat, **kw):
        c.box(nome, self.x(x0), self.y(y0), self.z(z0), self.k(x1 - x0), self.k(y1 - y0), self.k(z1 - z0), mat, **kw)

    def cyl_y(self, c, nome, dx, dz, y0, y1, r, mat, **kw):
        c.cyl_y(nome, self.x(dx), self.z(dz), self.y(y0), self.k(r), self.k(y1 - y0), mat, **kw)

    def front(self, c, nome, pts, y0, y1, mat, **kw):
        """Contorno (dx, dz) de frente, de y0 a y1."""
        c.profile(nome, "Front", [(self.x(a), self.z(b)) for a, b in pts], self.y(y0), self.k(y1 - y0), mat, **kw)

    def plan(self, c, nome, pts, z0, z1, mat, **kw):
        """Contorno (dx, y absoluto) em planta, de z0 a z1."""
        c.profile(nome, "Plan", [(self.x(a), self.y(b)) for a, b in pts], self.z(z0), self.k(z1 - z0), mat, **kw)

    def side(self, c, nome, pts, x0, x1, mat, **kw):
        """Contorno (y absoluto, dz) de lado, de x0 a x1."""
        c.profile(nome, "Side", [(self.y(a), self.z(b)) for a, b in pts], self.x(x0), self.k(x1 - x0), mat, **kw)


def placa(c, L, A, cor="Branco", tampas=True, volume=True):
    """Caixa de embutir atrás da parede, suporte, placa com cantos arredondados e ressalto, tampas dos parafusos."""
    hl = f"({L}/2)"
    if volume:
        c.box("Volume simplificado", f"-{hl}", -0.03, 0, L, 0.03, A, cor, detail=COARSE, in_plan=True)
    # caixa de embutir (dentro da parede)
    bx, bz, t, pr = 0.005, 0.005, 0.002, 0.046
    c.box("Caixa de embutir - fundo", f"-{hl} + {bx}", pr - t, bz, f"{L} - {2 * bx}", t, f"{A} - {2 * bz}", CAIXA)
    c.box("Caixa de embutir - lateral esquerda", f"-{hl} + {bx}", 0, bz, t, pr - t, f"{A} - {2 * bz}", CAIXA)
    c.box("Caixa de embutir - lateral direita", f"{hl} - {bx + t}", 0, bz, t, pr - t, f"{A} - {2 * bz}", CAIXA)
    c.box("Caixa de embutir - base", f"-{hl} + {bx + t}", 0, bz, f"{L} - {2 * (bx + t)}", pr - t, t, CAIXA)
    c.box("Caixa de embutir - topo", f"-{hl} + {bx + t}", 0, f"{A} - {bz + t}", f"{L} - {2 * (bx + t)}", pr - t, t, CAIXA)
    c.cyl("Caixa de embutir - entrada de eletroduto superior", 0, 0.028, f"{A} - {bz}", 0.0105, 0.0006, CAIXA, detail=FINE)
    c.cyl("Caixa de embutir - entrada de eletroduto inferior", 0, 0.028, f"{bz} - 0.0006", 0.0105, 0.0006, CAIXA, detail=FINE)
    c.cyl_y("Caixa de embutir - entrada de eletroduto do fundo", 0, f"{A}/2", pr, 0.0105, 0.0006, CAIXA, detail=FINE)
    # suporte
    c.profile("Suporte", "Front", rrect(f"-{hl} + 0.003", 0.003, f"{hl} - 0.003", f"{A} - 0.003", 0.004), -0.0015, 0.0015, SUPORTE)
    # placa
    c.profile("Placa", "Front", rrect(f"-{hl}", 0, hl, A, 0.006), -0.0065, 0.005, cor, in_plan=True)
    c.profile("Placa - ressalto frontal", "Front", rrect(f"-{hl} + 0.0012", 0.0012, f"{hl} - 0.0012", f"{A} - 0.0012", 0.005), -0.008, 0.0015, cor)
    if tampas:
        for nome, z in (("inferior", "0.0075"), ("superior", f"{A} - 0.0075")):
            c.profile(f"Tampa do parafuso {nome}", "Front", rrect(-0.005, f"{z} - 0.0022", 0.005, f"{z} + 0.0022", 0.0015),
                      -0.0084, 0.0004, cor, detail=FINE)


def modulo(c, nome, m, cor="Branco", corpo=True):
    """Miolo de um módulo: moldura saliente na placa e corpo atrás da parede."""
    m.rrect(c, nome, 0.0215, 0.0113, 0.002, -0.0095, -0.008, cor)
    if corpo:
        m.box(c, f"{nome} - corpo", -0.0195, 0.0195, 0, 0.026, -0.0105, 0.0105, SUPORTE)


def tomada(c, nome, m, amperes=10, cor="Branco", marca=None):
    """Tomada 2P+T NBR 14136: poço hexagonal rebaixado e três furos (4 mm em 10 A, 4,8 mm em 20 A)."""
    modulo(c, nome, m, cor)
    poco = [(-0.0186, -0.0022), (-0.0118, -0.0088), (0.0118, -0.0088), (0.0186, -0.0022),
            (0.0186, 0.0022), (0.0118, 0.0088), (-0.0118, 0.0088), (-0.0186, 0.0022)]
    m.front(c, f"{nome} - poço", poco, -0.0096, -0.0025, cor, void=True)
    r = 0.00225 if amperes == 10 else 0.00268
    for rot, dx, dz in (("fase", -0.0095, 0), ("neutro", 0.0095, 0), ("terra", 0, -0.003)):
        m.cyl_y(c, f"{nome} - furo {rot}", dx, dz, -0.0026, 0.005, r, cor, detail=FINE, void=True)
        m.cyl_y(c, f"{nome} - contato {rot}", dx, dz, 0.005, 0.014, r + 0.0008, "Latão", detail=FINE)
    if marca:
        # filete de identificação do circuito, acima do poço
        m.rrect(c, f"{nome} - identificação", 0.006, 0.0006, 0.0005, -0.0097, -0.0095, marca, dz=0.0101, detail=FINE)


def tecla_horizontal(c, nome, m, cor="Branco", indicador="Plástico cinza", s_ind=None):
    """Tecla larga que bascula para os lados (módulo deitado): leve inclinação com o lado direito pressionado."""
    m.rrect(c, f"{nome} - moldura", 0.0215, 0.0113, 0.002, -0.0088, -0.008, SUPORTE)
    m.plan(c, nome, [(-0.0205, -0.008), (0.0205, -0.008), (0.0205, -0.0096), (-0.0205, -0.0126)], -0.0103, 0.0103, cor)
    # o indicador encolhe para dentro da tecla quando não existe (interruptor paralelo)
    k = f"max(0.01, ({m.s or 1})*({s_ind or 1}))"
    c.box(f"{nome} - indicador", f"{m.x(0.016)} - 0.0015*{k}", f"{m.y(-0.0092)} - 0.0011*{k}", f"{m.z(0)} - 0.003*{k}",
          f"0.003*{k}", f"0.0011*{k}", f"0.006*{k}", indicador, detail=FINE)


def tecla_vertical(c, nome, m, cor="Branco", indicador="Plástico cinza", s_ind=None):
    """Tecla alta que bascula para cima e para baixo (módulo em pé): parte de baixo pressionada."""
    m.rrect(c, f"{nome} - moldura", 0.0113, 0.0215, 0.002, -0.0088, -0.008, SUPORTE)
    m.side(c, nome, [(-0.008, -0.0205), (-0.008, 0.0205), (-0.0126, 0.0205), (-0.0096, -0.0205)], -0.0103, 0.0103, cor)
    k = f"max(0.01, ({m.s or 1})*({s_ind or 1}))"
    c.box(f"{nome} - indicador", f"{m.x(0)} - 0.003*{k}", f"{m.y(-0.0092)} - 0.0011*{k}", f"{m.z(-0.016)} - 0.0015*{k}",
          f"0.006*{k}", f"0.0011*{k}", f"0.003*{k}", indicador, detail=FINE)


def rj45(c, nome, m):
    """Conector RJ45 fêmea (keystone): cavidade com entalhe da trava, oito contatos ao fundo, tampa deslizante e etiqueta."""
    modulo(c, nome, m, corpo=False)
    z0 = -0.0015  # a cavidade fica um pouco abaixo do centro, com a tampa recolhida acima
    m.box(c, f"{nome} - conector", -0.0085, 0.0085, 0, 0.006, -0.0095, 0.0065, "Plástico preto")
    m.box(c, f"{nome} - corpo", -0.0195, 0.0195, 0.0075, 0.03, -0.0105, 0.0105, "Plástico preto")
    boca = [(-0.006, -0.0035), (-0.003, -0.0035), (-0.003, -0.0055), (0.003, -0.0055), (0.003, -0.0035),
            (0.006, -0.0035), (0.006, 0.0045), (-0.006, 0.0045)]
    m.front(c, f"{nome} - cavidade", [(a, b + z0) for a, b in boca], -0.0096, 0.006, "Plástico preto", void=True)
    m.box(c, f"{nome} - fundo da cavidade", -0.0065, 0.0065, 0.006, 0.0075, -0.006 + z0, 0.0028 + z0, "Plástico preto")
    for i in range(8):
        x = -0.00445 + i * 0.00127
        m.box(c, f"{nome} - contato {i + 1}", x - 0.00028, x + 0.00028, 0.006, 0.0075, 0.0028 + z0, 0.0045 + z0, "Latão", detail=FINE)
    m.rrect(c, f"{nome} - tampa deslizante", 0.0068, 0.0029, 0.0008, -0.0102, -0.0095, SUPORTE, dz=0.0068)
    m.box(c, f"{nome} - pega da tampa", -0.004, 0.004, -0.0107, -0.0102, 0.0074, 0.0082, SUPORTE, detail=FINE)
    m.rrect(c, f"{nome} - etiqueta", 0.0028, 0.002, 0.0005, -0.0097, -0.0095, "Plástico azul", dx=-0.0145, detail=FINE)


def coaxial(c, nome, m):
    """Tomada coaxial tipo F: porca sextavada, corpo roscado, dielétrico e furo do condutor central."""
    modulo(c, nome, m)
    r = 0.0068
    hexa = [(r, 0), (r / 2, r * 0.866), (-r / 2, r * 0.866), (-r, 0), (-r / 2, -r * 0.866), (r / 2, -r * 0.866)]
    m.cyl_y(c, f"{nome} - arruela", 0, 0, -0.0101, -0.0095, 0.0078, "Cromado", detail=FINE)
    m.front(c, f"{nome} - porca sextavada", hexa, -0.0122, -0.0101, "Cromado")
    m.cyl_y(c, f"{nome} - conector F", 0, 0, -0.0195, -0.0122, 0.0045, "Cromado")
    for i in range(4):
        y = -0.0188 + i * 0.0016
        m.cyl_y(c, f"{nome} - filete da rosca {i + 1}", 0, 0, y, y + 0.0008, 0.0049, "Cromado", detail=FINE)
    m.cyl_y(c, f"{nome} - dielétrico", 0, 0, -0.0197, -0.0195, 0.0034, "Branco", detail=FINE)
    m.cyl_y(c, f"{nome} - furo do condutor central", 0, 0, -0.0199, -0.0197, 0.0009, "Plástico preto", detail=FINE)
    m.rrect(c, f"{nome} - etiqueta", 0.0028, 0.002, 0.0005, -0.0097, -0.0095, "Plástico cinza", dx=-0.0145, detail=FINE)


def ponto_chuveiro(nome, arquivo, potencia, descricao, r_fio, h_bloco):
    """Ponto de chuveiro: placa com saída de cabo, três condutores (fase, fase, terra) e conector cerâmico de três polos."""
    c = Component(nome, "electrical", arquivo, "Electrical")
    L = c.param("Largura", 0.06)
    A = c.param("Altura", 0.1)
    c.mep = {"Device": {"device": "DedicatedOutlet", "power": potencia}}
    c.connector("Eletroduto", "Power", 0, 0, f"{A} / 2", "Back")
    materiais(c)
    placa(c, L, A)
    zc = f"({A}/2 + 0.012)"
    # saída de cabo: bucha em anel e interior escuro
    c.rev("Saída de cabo - bucha", "Plan", [(0.0108, -0.0108), (0.0138, -0.0108), (0.0138, -0.008), (0.0108, -0.008)], zc, 0, SUPORTE)
    c.cyl_y("Saída de cabo - interior", 0, zc, -0.0083, 0.0108, 0.0003, "Plástico preto")
    passo, yv = 0.0075, -0.0205
    zb = f"({zc} - 0.022)"  # topo do conector cerâmico
    for rot, dx, mat in (("fase 1", -passo, "Plástico preto"), ("fase 2", 0, "Plástico vermelho"), ("terra", passo, "Plástico verde")):
        c.cyl_y(f"Condutor {rot} - saída", dx, zc, yv - r_fio, r_fio, 0.0125 + r_fio, mat)
        c.cyl(f"Condutor {rot} - descida", dx, yv, f"{zb} - 0.004", r_fio, f"0.026 + {r_fio}", mat)
        c.cyl(f"Conector cerâmico - entrada {rot}", dx, yv, f"{zb} - {h_bloco} - 0.0004", r_fio + 0.0005, 0.0004, "Plástico preto", detail=FINE)
        for j, dz in enumerate((0.006, h_bloco - 0.006), 1):
            c.cyl_y(f"Conector cerâmico - parafuso {rot} {j}", dx, f"{zb} - {dz}", -0.0282, 0.0021, 0.0008, "Latão", detail=FINE)
    c.profile("Conector cerâmico", "Front", rrect(-0.0125, f"{zb} - {h_bloco}", 0.0125, zb, 0.002), -0.0276, 0.0142, "Louça")
    for i, dx in enumerate((-passo / 2, passo / 2), 1):
        c.box(f"Conector cerâmico - sulco {i}", dx - 0.0004, -0.0278, f"{zb} - {h_bloco} + 0.001", 0.0008, 0.0002, f"{h_bloco} - 0.002", "Plástico cinza", detail=FINE)
    c.type(f"TUE chuveiro {potencia} W", descricao)
    enquadrar(c, 0.30)  # make.py coloca o ponto à altura padrão de tomada; no projeto ele sobe para a altura do chuveiro
    return c


def enquadrar(c, altura_montagem, L=0.1, A=0.1, aproximar=0.055):
    """Aponta as câmeras do make.py para o dispositivo, de perto.

    make.py põe a câmera a 1.9*max(tamanho) + 0.35 m do alvo, longe demais para
    uma placa de 10 cm: um tamanho negativo encurta a distância, e a base
    compensa o deslocamento do alvo (alvo em z = base + altura/2).
    """
    c.preview_size = (-aproximar, -aproximar, -aproximar)
    c.preview_base = altura_montagem + A / 2 + aproximar / 2
