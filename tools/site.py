#!/usr/bin/env python3
"""Generate the outdoor floor sources (sources/site/*.json).

    python tools/site.py      then  python tools/build.py

Floor markings (parking spaces, legends, speed limits, arrows, crossings,
symbols, hatched areas) and the small things fixed to a pavement (speed
humps, wheel stops, road studs), after the Brazilian rules: the Manual
Brasileiro de Sinalização de Trânsito, Volume IV (sinalização horizontal), Resolução CONTRAN 965/2022 (reserved parking),
Resolução CONTRAN 600/2016 (speed humps) and ABNT NBR 9050 (the symbol of
access). They lie on the floor: x to the right, y away from the driver (the
direction of travel), z up from the floor, the paint 3 mm thick.

Markings are scripted pieces (tools/site/componentes.lua), so their text is a
parameter: every word painted on the floor (a spot's number, PARE, ESCOLA,
40 km/h...) is a text parameter that each placed element may change, drawn in
IBM Plex Sans Condensed Bold from the glyph table tools/site/fonte.lua
(written by tools/site/fonte.py). Arrows and pictograms come from
tools/site/figuras.py. A script's materials only travel with the component
when a plain piece uses them, so every material a marking paints with is
either the script piece's own material or that of a plain piece.

Edit this file, lib.lua, componentes.lua or figuras.py, not the JSON.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent / "site"
ROOT = HERE.parent.parent
OUT = ROOT / "sources" / "site"
sys.path.insert(0, str(HERE))

from figuras import all_figures  # noqa: E402

WHITE, YELLOW, BLUE = "Tinta viária branca", "Tinta viária amarela", "Tinta viária azul"
MATERIALS = {
    WHITE: {"color": [244, 244, 238], "class": "Paint", "finish": "Matte"},
    YELLOW: {"color": [246, 186, 18], "class": "Paint", "finish": "Matte"},
    BLUE: {"color": [18, 82, 168], "class": "Paint", "finish": "Matte"},
    "Concreto asfáltico": {"color": [64, 64, 66], "class": "Concrete", "finish": "Matte"},
    "Borracha preta": {"color": [34, 34, 36], "class": "Plastic", "finish": "Matte"},
    "Resina amarela": {"color": [240, 184, 24], "class": "Plastic", "finish": "Satin"},
    "Refletivo": {"color": [236, 236, 228], "class": "Glass", "finish": "Glossy"},
}


# --- parameters ----------------------------------------------------------------------

class Param:
    """A parameter: declared by the script (`script=True`) or a plain one the pieces' expressions read."""

    def __init__(self, kind, name, default, label, instance=False, choices=None, script=True):
        self.kind, self.name, self.default, self.label = kind, name, default, label
        self.instance, self.choices, self.script = instance, choices or [], script

    def lua(self) -> str:
        fields = [lua_str(self.name)]
        if self.kind == "choice":
            fields.append("{ " + ", ".join(f"{{ {lua_str(k)}, {lua_str(v)} }}" for k, v in self.choices) + " }")
        fields.append(f"label = {lua_str(self.label)}")
        if self.kind in ("text", "choice"):
            fields.append(f"default = {lua_str(self.default)}")
        elif self.kind == "boolean":
            fields.append(f"default = {'true' if self.default else 'false'}")
        elif self.kind != "material":
            fields.append(f"default = {self.default:g}")
        if self.instance:
            fields.append("instance = true")
        return f"param.{self.kind} {{ " + ", ".join(fields) + " }"

    def definition(self) -> dict:
        kind = {"length": "Length", "angle": "Angle", "number": "Number", "text": "Text", "boolean": "Boolean",
                "choice": "Choice", "material": "Material"}[self.kind]
        d = {"name": self.name, "value": 0.0, "kind": kind, "instance": self.instance}
        if not self.script:
            d["value"] = float(self.default)
            return d
        d["label"] = self.label
        d["from_script"] = True
        if self.kind in ("text", "choice"):
            d["text"] = self.default
        elif self.kind == "boolean":
            d["value"] = 1.0 if self.default else 0.0
        elif self.kind != "material":
            d["value"] = float(self.default)
        if self.choices:
            d["choices"] = [{"key": k, "label": v} for k, v in self.choices]
        return d


def length(name, default, label, **kw):
    return Param("length", name, default, label, **kw)


def plain(name, default):
    return Param("length", name, default, name, script=False)


def text(name, default, label):
    return Param("text", name, default, label, instance=True)


def paint():
    return Param("material", "Pintura", "", "Pintura (vazio: a da peça)")


def lua_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# --- plain pieces --------------------------------------------------------------------

def box(name, x, y, z, w, d, h, material):
    return {"name": name, "material": material, "in_plan": True,
            "shape": {"Box": {"x": x, "y": y, "z": z, "width": w, "depth": d, "height": h}}}


def profile_side(name, points, offset, depth, material, void=False, in_plan=True):
    pts = []
    for p in points:
        q = {"u": p[0], "v": p[1]}
        if len(p) > 2:
            q["radius"] = p[2]
        pts.append(q)
    item = {"name": name, "material": material, "in_plan": in_plan,
            "shape": {"Profile": {"plane": "Side", "points": pts, "offset": offset, "depth": depth}}}
    if void:
        item["void"] = True
    return item


def cylinder(name, x, y, z, r, h, material="", void=False):
    item = {"name": name, "material": material, "in_plan": True,
            "shape": {"Cylinder": {"x": x, "y": y, "z": z, "radius": r, "height": h}}}
    if void:
        item["void"] = True
    return item


# --- the components --------------------------------------------------------------------

def t(name, description, **values):
    return {"name": name, "values": values, "info": {"description": description}}


COMPONENTS = [
    {
        "file": "vaga-estacionamento",
        "component": "Vaga de estacionamento",
        "material": WHITE,
        "font": True,
        "params": [
            length("Largura", 2.5, "Largura (entre os eixos das linhas)"),
            length("Comprimento", 5.0, "Comprimento"),
            Param("angle", "Angulo", 90, "Ângulo com o corredor"),
            length("LarguraLinha", 0.10, "Largura da linha"),
            Param("choice", "Demarcacao", "laterais", "Demarcação",
                  choices=[("laterais", "Linhas laterais"), ("u", "Laterais e fundo (U)"), ("retangulo", "Retângulo fechado")], instance=True),
            text("Numero", "01", "Número"),
            length("AlturaNumero", 0.5, "Altura do número"),
            text("Legenda", "", "Legenda"),
            length("AlturaLegenda", 0.6, "Altura da legenda"),
            paint(),
        ],
        "types": [
            t("Vaga 2,50 x 5,00", "Vaga de estacionamento perpendicular de 2,50 x 5,00 m, demarcada por linhas brancas de 10 cm; em cada vaga o número, a legenda (IDOSO, MOTO, VISITANTE...) e a demarcação (laterais, U ou retângulo) são editáveis"),
            t("Vaga 2,30 x 4,50", "Vaga perpendicular compacta de 2,30 x 4,50 m; número, legenda e demarcação editáveis em cada vaga", Largura=2.3, Comprimento=4.5),
            t("Vaga 45° 2,50 x 5,00", "Vaga oblíqua a 45° do corredor, 2,50 m entre linhas e 5,00 m de comprimento; número, legenda e demarcação editáveis", Angulo=45),
            t("Vaga 60° 2,50 x 5,00", "Vaga oblíqua a 60° do corredor, 2,50 m entre linhas e 5,00 m de comprimento; número, legenda e demarcação editáveis", Angulo=60),
            t("Vaga paralela 5,50 x 2,20", "Vaga paralela ao meio-fio, 5,50 m ao longo da via e 2,20 m de largura; a entrada (-Y) é o lado da via", Largura=5.5, Comprimento=2.2, AlturaNumero=0.4),
            t("Vaga moto 1,00 x 2,00", "Vaga para motocicleta de 1,00 x 2,00 m (escreva MOTO na legenda)", Largura=1.0, Comprimento=2.0, AlturaLegenda=0.4, AlturaNumero=0.3),
        ],
    },
    {
        "file": "vaga-pcd",
        "component": "Vaga PcD",
        "material": WHITE,
        "font": True,
        "figures": ["cadeirante"],
        "params": [
            plain("Largura", 2.5),
            plain("Comprimento", 5.0),
            plain("LarguraCirculacao", 1.2),
            plain("LarguraLinha", 0.10),
            plain("LadoSimbolo", 1.2),
            Param("choice", "Lado", "direita", "Faixa de circulação",
                  choices=[("direita", "À direita"), ("esquerda", "À esquerda"), ("ambos", "Dos dois lados"), ("nenhum", "Sem faixa (compartilhada)")], instance=True),
            length("LarguraZebrado", 0.10, "Largura das faixas do zebrado"),
            length("EspacamentoZebrado", 0.40, "Espaço entre as faixas do zebrado"),
            text("Numero", "", "Número"),
            length("AlturaNumero", 0.4, "Altura do número"),
            text("Legenda", "", "Legenda"),
            length("AlturaLegenda", 0.4, "Altura da legenda"),
        ],
        "items": [
            box("Fundo azul do símbolo", "-LadoSimbolo/2", "Comprimento/2 - LadoSimbolo/2", "0", "LadoSimbolo", "LadoSimbolo", "0.002", BLUE),
        ],
        "types": [
            t("Vaga PcD 2,50 x 5,00", "Vaga reservada a pessoa com deficiência (Resolução CONTRAN 965/2022, ABNT NBR 9050): 2,50 x 5,00 m com faixa adicional de circulação de 1,20 m zebrada e o símbolo internacional de acesso em branco sobre quadrado azul de 1,20 m; a faixa pode ficar à direita, à esquerda ou dos dois lados; número e legenda editáveis"),
            t("Vaga PcD 3,70 x 5,00 sem faixa", "Vaga PcD de 3,70 x 5,00 m com a área de circulação incluída na própria vaga (sem faixa zebrada)", Largura=3.7, LarguraCirculacao=0.0),
        ],
    },
    {
        "file": "legenda-pare",
        "component": "Legenda PARE com linha de retenção",
        "material": WHITE,
        "font": True,
        "params": [
            text("Texto", "PARE", "Texto"),
            length("AlturaLetra", 1.6, "Altura das letras"),
            length("LarguraLetra", 0.5, "Largura das letras"),
            length("Espacamento", 0.12, "Espaço entre as letras"),
            length("Distancia", 1.0, "Distância da legenda à linha"),
            Param("boolean", "LinhaRetencao", True, "Linha de retenção", instance=True),
            length("LarguraVia", 3.5, "Largura da faixa de trânsito"),
            length("LarguraLinha", 0.4, "Largura da linha de retenção"),
            paint(),
        ],
        "types": [
            t("PARE 1,60 m faixa 3,50 m", "Legenda PARE em letras de 1,60 m antes da linha de retenção (LRE) de 0,40 m numa faixa de 3,50 m (vias até 80 km/h); a origem é o meio da linha, o condutor chega por -Y; o texto é editável"),
            t("PARE 2,40 m faixa 3,60 m", "Legenda PARE em letras de 2,40 m (vias acima de 80 km/h) antes da linha de retenção de 0,50 m numa faixa de 3,60 m", AlturaLetra=2.4, LarguraLetra=0.75, Espacamento=0.18, Distancia=1.6, LarguraVia=3.6, LarguraLinha=0.5),
            t("PARE 0,80 m estacionamento", "Legenda PARE de 0,80 m para estacionamentos e vias internas, com linha de retenção de 0,30 m em faixa de 3,00 m", AlturaLetra=0.8, LarguraLetra=0.35, Espacamento=0.08, Distancia=0.6, LarguraVia=3.0, LarguraLinha=0.3),
        ],
    },
    {
        "file": "legenda-piso",
        "component": "Legenda no piso",
        "material": WHITE,
        "font": True,
        "params": [
            text("Linha1", "ESCOLA", "Linha 1 (a mais próxima do condutor)"),
            text("Linha2", "", "Linha 2"),
            text("Linha3", "", "Linha 3"),
            length("AlturaLetra", 1.6, "Altura das letras"),
            length("LarguraLetra", 0.5, "Largura das letras"),
            length("Espacamento", 0.12, "Espaço entre as letras"),
            length("EntreLinhas", 1.0, "Espaço entre as linhas"),
            length("LarguraMaxima", 3.2, "Largura máxima (as letras estreitam para caber; 0: sem limite)"),
            paint(),
        ],
        "types": [
            t("Legenda 1,60 m", "Inscrição no pavimento em letras alongadas de 1,60 m (vias até 80 km/h): ESCOLA, DEVAGAR, ÔNIBUS, TÁXI, CARGA E DESCARGA...; até três linhas de texto editáveis em cada elemento, a primeira a mais próxima do condutor"),
            t("Legenda 2,40 m", "Inscrição no pavimento em letras de 2,40 m (vias acima de 80 km/h); texto editável", AlturaLetra=2.4, LarguraLetra=0.75, Espacamento=0.18, EntreLinhas=1.5, LarguraMaxima=3.4),
            t("Legenda 0,60 m estacionamento", "Inscrição pequena para estacionamentos e áreas internas, letras de 0,60 m (SAÍDA, ENTRADA, VISITANTE...); texto editável", AlturaLetra=0.6, LarguraLetra=0.3, Espacamento=0.06, EntreLinhas=0.4, LarguraMaxima=2.2),
        ],
    },
    {
        "file": "velocidade-piso",
        "component": "Velocidade máxima no piso",
        "material": WHITE,
        "font": True,
        "params": [
            text("Velocidade", "40", "Velocidade"),
            text("Unidade", "km/h", "Unidade"),
            length("AlturaNumero", 1.6, "Altura dos algarismos"),
            length("LarguraNumero", 0.6, "Largura dos algarismos"),
            length("AlturaUnidade", 0.8, "Altura da unidade"),
            length("LarguraUnidade", 0.4, "Largura das letras da unidade"),
            length("Afastamento", 0.4, "Espaço entre o número e a unidade"),
            length("LarguraMaxima", 3.2, "Largura máxima (0: sem limite)"),
            paint(),
        ],
        "types": [
            t("Velocidade 1,60 m", "Inscrição da velocidade máxima permitida no pavimento: algarismos de 1,60 m e km/h logo depois, no sentido do trânsito; velocidade (30, 40, 50, 60...) e unidade editáveis em cada elemento"),
            t("Velocidade 2,40 m", "Velocidade máxima no pavimento com algarismos de 2,40 m, para vias acima de 80 km/h", AlturaNumero=2.4, LarguraNumero=0.9, AlturaUnidade=1.2, LarguraUnidade=0.6, Afastamento=0.6, LarguraMaxima=3.4),
            t("Velocidade 0,80 m estacionamento", "Velocidade para estacionamentos e condomínios (10, 20 km/h), algarismos de 0,80 m", AlturaNumero=0.8, LarguraNumero=0.4, AlturaUnidade=0.4, LarguraUnidade=0.24, Afastamento=0.25, LarguraMaxima=2.4),
        ],
    },
    {
        "file": "seta-direcional",
        "component": "Seta direcional no piso",
        "material": WHITE,
        "figures": ["seta_frente", "seta_direita", "seta_esquerda", "seta_frente_direita", "seta_frente_esquerda", "seta_direita_esquerda", "seta_retorno"],
        "params": [
            Param("choice", "Tipo", "frente", "Movimento", instance=True, choices=[
                ("frente", "Siga em frente"), ("direita", "Vire à direita"), ("esquerda", "Vire à esquerda"),
                ("frente_direita", "Siga em frente ou vire à direita"), ("frente_esquerda", "Siga em frente ou vire à esquerda"),
                ("direita_esquerda", "Vire à direita ou à esquerda"), ("retorno", "Retorno"),
            ]),
            length("Comprimento", 5.0, "Comprimento"),
            Param("number", "Alongamento", 3.0, "Alongamento no sentido do trânsito"),
            paint(),
        ],
        "types": [
            t("Seta 5,00 m", "Seta indicativa de posicionamento na pista de 5,00 m, alongada para a leitura do condutor; o movimento (siga em frente, vire à direita ou à esquerda, frente ou direita, frente ou esquerda, direita ou esquerda, retorno) é escolhido em cada seta"),
            t("Seta 7,50 m", "Seta indicativa de 7,50 m, para vias de velocidade mais alta; movimento escolhido em cada seta", Comprimento=7.5),
            t("Seta estacionamento 2,50 m", "Seta de 2,50 m pouco alongada, para o sentido de circulação em estacionamentos; movimento escolhido em cada seta", Comprimento=2.5, Alongamento=1.6),
        ],
    },
    {
        "file": "faixa-pedestres",
        "component": "Faixa de pedestres",
        "material": WHITE,
        "params": [
            Param("choice", "Tipo", "zebrada", "Tipo", choices=[("zebrada", "Zebrada (FTP-1)"), ("paralela", "Paralela (FTP-2)")], instance=True),
            length("LarguraVia", 7.0, "Largura da via"),
            length("LarguraFaixa", 4.0, "Largura da faixa (no sentido da travessia)"),
            length("LarguraBarra", 0.4, "Largura das barras"),
            length("Espacamento", 0.6, "Espaço entre as barras"),
            Param("boolean", "LinhasRetencao", False, "Linha de retenção", instance=True),
            Param("boolean", "RetencaoDosDoisLados", True, "Retenção dos dois lados (mão dupla)", instance=True),
            length("DistanciaRetencao", 1.6, "Distância da linha de retenção à faixa"),
            length("LarguraRetencao", 0.4, "Largura da linha de retenção"),
            paint(),
        ],
        "types": [
            t("Faixa de pedestres 4,00 m via 7,00 m", "Faixa de travessia de pedestres zebrada (FTP-1): barras brancas de 0,40 m a cada 1,00 m paralelas ao trânsito, faixa de 4,00 m numa via de 7,00 m; o trânsito corre ao longo de Y; cada faixa pode ser trocada para paralela (FTP-2)"),
            t("Faixa de pedestres 3,00 m via 7,00 m", "Faixa zebrada de 3,00 m (largura mínima) numa via de 7,00 m", LarguraFaixa=3.0),
            t("Faixa de pedestres 4,00 m com retenção", "Faixa zebrada de 4,00 m com linhas de retenção de 0,40 m a 1,60 m dos dois lados, via de 7,00 m", LinhasRetencao=True),
            t("Faixa de pedestres 3,00 m via 3,50 m", "Faixa zebrada de 3,00 m sobre uma única faixa de 3,50 m (estacionamentos e vias locais)", LarguraVia=3.5, LarguraFaixa=3.0),
        ],
    },
    {
        "file": "simbolo-piso",
        "component": "Símbolo no piso",
        "material": WHITE,
        "figures": ["cadeirante", "bicicleta"],
        "params": [
            Param("choice", "Simbolo", "bicicleta", "Símbolo", instance=True, choices=[("bicicleta", "Bicicleta"), ("cadeirante", "Símbolo internacional de acesso")]),
            length("Largura", 1.2, "Largura"),
            Param("number", "Alongamento", 1.0, "Alongamento no sentido do trânsito"),
            paint(),
        ],
        "types": [
            t("Símbolo bicicleta 1,20 m", "Pictograma de bicicleta para ciclofaixas e ciclovias, 1,20 m de largura, a bicicleta de lado e o alto voltado para +Y; cada símbolo pode ser trocado pelo símbolo internacional de acesso (ABNT NBR 9050)"),
            t("Símbolo bicicleta alongado 1,00 m", "Pictograma de bicicleta de 1,00 m alongado 2 vezes no sentido do trânsito, para a leitura do ciclista em movimento", Largura=1.0, Alongamento=2.0),
        ],
    },
    {
        "file": "de-a-preferencia",
        "component": "Dê a preferência no piso",
        "material": WHITE,
        "params": [
            length("Base", 1.5, "Base do triângulo"),
            length("Comprimento", 3.6, "Comprimento do triângulo"),
            length("LarguraTraco", 0.2, "Largura do contorno"),
            Param("boolean", "Vazado", True, "Triângulo vazado", instance=True),
            length("Distancia", 1.0, "Distância do triângulo à linha"),
            Param("boolean", "Linha", True, "Linha de dê a preferência", instance=True),
            length("LarguraVia", 3.5, "Largura da faixa de trânsito"),
            length("LarguraLinha", 0.3, "Largura da linha"),
            length("Traco", 0.5, "Comprimento dos traços"),
            length("Intervalo", 0.5, "Intervalo entre os traços"),
            paint(),
        ],
        "types": [
            t("Dê a preferência 1,50 x 3,60", "Símbolo triangular Dê a preferência (inscrição no pavimento) de 1,50 x 3,60 m com contorno de 0,20 m, apontando para o condutor, e a linha tracejada de dê a preferência à frente; a origem é o meio da linha"),
            t("Dê a preferência 1,00 x 2,40 cheio", "Triângulo Dê a preferência cheio de 1,00 x 2,40 m, sem a linha, para vias locais e estacionamentos", Base=1.0, Comprimento=2.4, Vazado=False, Linha=False, Distancia=0.0),
        ],
    },
    {
        "file": "area-zebrada",
        "component": "Área zebrada",
        "material": YELLOW,
        "params": [
            plain("Largura", 5.0),
            plain("Comprimento", 2.5),
            plain("LarguraLinha", 0.1),
            length("LarguraFaixa", 0.3, "Largura das faixas"),
            length("Espacamento", 0.9, "Espaço entre as faixas"),
            Param("angle", "AnguloFaixas", 45, "Ângulo das faixas"),
        ],
        "items": [
            box("Contorno esquerdo", "-Largura/2", "-Comprimento/2", "0", "LarguraLinha", "Comprimento", "0.003", YELLOW),
            box("Contorno direito", "Largura/2 - LarguraLinha", "-Comprimento/2", "0", "LarguraLinha", "Comprimento", "0.003", YELLOW),
            box("Contorno da frente", "-Largura/2 + LarguraLinha", "-Comprimento/2", "0", "Largura - 2*LarguraLinha", "LarguraLinha", "0.003", YELLOW),
            box("Contorno do fundo", "-Largura/2 + LarguraLinha", "Comprimento/2 - LarguraLinha", "0", "Largura - 2*LarguraLinha", "LarguraLinha", "0.003", YELLOW),
        ],
        "types": [
            t("Área zebrada 5,00 x 2,50", "Marcação de área de proibição de estacionamento e parada (zebrado amarelo): contorno de 0,10 m e faixas de 0,30 m a 45°, 5,00 x 2,50 m; faixas, espaço e ângulo ajustáveis"),
            t("Área zebrada 10,00 x 3,00", "Zebrado amarelo de 10,00 x 3,00 m, faixas de 0,40 m a 45°", Largura=10.0, Comprimento=3.0, LarguraFaixa=0.4, Espacamento=1.1),
            t("Área zebrada 2,50 x 2,50", "Zebrado amarelo quadrado de 2,50 m, para frente de portões e hidrantes", Largura=2.5),
        ],
    },
    {
        "file": "lombada",
        "component": "Lombada",
        "material": YELLOW,
        "params": [
            plain("LarguraVia", 7.0),
            plain("Comprimento", 3.7),
            plain("Altura", 0.08),
            length("LarguraFaixa", 0.25, "Largura das faixas pintadas"),
            length("Espacamento", 0.5, "Espaço entre as faixas"),
            Param("angle", "AnguloFaixas", 45, "Ângulo das faixas"),
        ],
        "items": [
            profile_side("Lombada", [["-Comprimento/2", "0"], ["Comprimento/2", "0", "(Comprimento*Comprimento/4 + Altura*Altura)/(2*Altura)"]],
                         "-LarguraVia/2", "LarguraVia", "Concreto asfáltico"),
        ],
        "types": [
            t("Lombada tipo A 3,70 m", "Ondulação transversal tipo A (Resolução CONTRAN 600/2016): 3,70 m no sentido do trânsito e 8 cm de altura, em arco, numa via de 7,00 m, com faixas amarelas a 45° pintadas sobre ela; o trânsito corre ao longo de Y"),
            t("Lombada tipo B 1,50 m", "Ondulação transversal tipo B (Resolução CONTRAN 600/2016): 1,50 m e 6 cm de altura, para vias locais, numa via de 7,00 m", Comprimento=1.5, Altura=0.06, LarguraFaixa=0.2, Espacamento=0.4),
            t("Lombada estacionamento 0,90 m", "Redutor de velocidade de 0,90 m e 5 cm para estacionamentos e condomínios, faixa de 3,00 m", LarguraVia=3.0, Comprimento=0.9, Altura=0.05, LarguraFaixa=0.15, Espacamento=0.3),
        ],
    },
]


def wheel_stop() -> dict:
    """A rubber wheel stop: a crowned trapezoid, two yellow bands and two counterbored bolt holes."""
    def section(e: str):
        return [
            [f"-Largura/2 - {e}", "0"],
            [f"Largura/2 + {e}", "0"],
            [f"Largura*0.28 + {e}", f"Altura*0.97 + {e}", "Largura*1.6"],
            [f"-Largura*0.28 - {e}", f"Altura*0.97 + {e}"],
        ]
    items = [profile_side("Corpo", section("0"), "-Comprimento/2", "Comprimento", "Borracha preta")]
    for i, side in enumerate(("-", "")):
        items.append(profile_side(f"Faixa refletiva {i + 1}", section("0.0015"), f"{side}Comprimento/4 - Comprimento*0.09", "Comprimento*0.18", YELLOW))
    for i, side in enumerate(("-", "")):
        x = f"{side}(Comprimento/2 - 0.065)"
        items.append(cylinder(f"Furo do chumbador {i + 1}", x, "0", "-0.01", "0.011", "Altura + 0.05", void=True))
        items.append(cylinder(f"Rebaixo do chumbador {i + 1}", x, "0", "Altura*0.55", "0.021", "Altura", void=True))
    return {
        "file": "batente-estacionamento",
        "component": "Batente de estacionamento",
        "params": [plain("Comprimento", 0.5), plain("Largura", 0.15), plain("Altura", 0.1)],
        "items": items,
        "types": [
            t("Batente borracha 50 cm", "Batente (trava) de roda de borracha para estacionamento, 50 x 15 x 10 cm, com duas faixas refletivas amarelas e dois furos rebaixados para chumbadores; o comprimento corre ao longo de X, o veículo chega por -Y"),
            t("Batente borracha 60 cm", "Batente de roda de borracha de 60 x 15 x 10 cm", Comprimento=0.6),
            t("Batente borracha 1,00 m", "Batente de roda de borracha de 1,00 m x 15 x 10 cm, para as duas rodas de motos ou carrinhos", Comprimento=1.0),
            t("Batente borracha 1,80 m", "Batente contínuo de borracha de 1,80 m x 18 x 12 cm, para as duas rodas do carro", Comprimento=1.8, Largura=0.18, Altura=0.12),
        ],
    }


def road_stud() -> dict:
    """A bidirectional road stud: a resin body with sloped faces and a reflector on each."""
    a = "Altura*1.4"  # the run of each sloped face
    items = [profile_side("Corpo", [["-Comprimento/2", "0"], ["Comprimento/2", "0"], [f"Comprimento/2 - {a}", "Altura"], [f"-Comprimento/2 + {a}", "Altura"]],
                          "-Largura/2", "Largura", "Resina amarela")]
    # The reflectors stand on the sloped faces, from 22 % to 86 % of the height, 1.2 mm proud.
    nx, nz = 0.581 * 0.0012, 0.814 * 0.0012  # the faces' normal for a run of 1.4 times the height
    for name, s in (("Refletor da frente", -1), ("Refletor de trás", 1)):
        def pt(f: float, out: bool, s=s):
            u = f"{s}*(Comprimento/2 - {a}*{f})" + (f" + {s * nx:.6f}" if out else "")
            v = f"Altura*{f}" + (f" + {nz:.6f}" if out else "")
            return [u, v]
        pts = [pt(0.22, False), pt(0.86, False), pt(0.86, True), pt(0.22, True)]
        items.append(profile_side(name, pts, "-Largura/2 + Largura*0.12", "Largura*0.76", "Refletivo", in_plan=False))
    return {
        "file": "tacha-refletiva",
        "component": "Tacha refletiva",
        "params": [plain("Largura", 0.1), plain("Comprimento", 0.1), plain("Altura", 0.018)],
        "items": items,
        "types": [
            t("Tacha bidirecional 10 x 10 cm", "Tacha refletiva bidirecional de resina amarela, 10 x 10 cm e 1,8 cm de altura, com um refletor em cada face inclinada (para os dois sentidos do trânsito ao longo de Y)"),
            t("Tachão bidirecional 15 x 25 cm", "Tachão refletivo bidirecional de resina amarela, 15 x 25 cm e 4,6 cm de altura, para canalização e divisão de fluxos", Largura=0.15, Comprimento=0.25, Altura=0.046),
        ],
    }


COMPONENTS += [wheel_stop(), road_stud()]


# --- scripts ---------------------------------------------------------------------------

def sections() -> dict[str, str]:
    text_ = (HERE / "componentes.lua").read_text(encoding="utf-8")
    parts = re.split(r"^--- ([a-z0-9-]+)\n", text_, flags=re.M)
    return {parts[i]: parts[i + 1].strip() + "\n" for i in range(1, len(parts), 2)}


def script_source(c: dict, body: str, figures: dict) -> str:
    out = [
        f"-- {c['component']}: floor marking scripted by tools/site.py from tools/site/lib.lua and",
        "-- tools/site/componentes.lua; edit those, not this text.",
    ]
    if c.get("font"):
        out.append((HERE / "fonte.lua").read_text(encoding="utf-8").rstrip())
    if c.get("figures"):
        out.append("local FIGURAS = {")
        out += [f"  {name} = {lua_str(figures[name])}," for name in c["figures"]]
        out.append("}")
    out.append((HERE / "lib.lua").read_text(encoding="utf-8").rstrip())
    out.append("")
    out += [p.lua() for p in c["params"] if p.script]
    out.append("")
    out.append(body.rstrip())
    return "\n".join(out) + "\n"


def source(c: dict, bodies: dict, figures: dict) -> dict:
    items = list(c.get("items", []))
    if c["file"] in bodies:
        items.append({
            "name": "Pintura (script)",
            "material": c["material"],
            "in_plan": True,
            "shape": {"Script": {"source": script_source(c, bodies[c["file"]], figures)}},
        })
    used = {i["material"] for i in items if i.get("material")}
    return {
        "component": c["component"],
        "def": {"kind": "Generic", "params": [p.definition() for p in c["params"]], "items": items},
        "types": c["types"],
        "materials": [{"name": n, **m} for n, m in MATERIALS.items() if n in used],
    }


def main() -> None:
    bodies = sections()
    figures = all_figures()
    OUT.mkdir(parents=True, exist_ok=True)
    for c in COMPONENTS:
        path = OUT / f"{c['file']}.json"
        path.write_text(json.dumps(source(c, bodies, figures), ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"{path.relative_to(ROOT).as_posix()}: {path.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
