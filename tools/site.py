#!/usr/bin/env python3
"""Generate the outdoor sources: sources/site/ (floor markings, site furniture, tactile
paving), sources/signage/ (signs) and the grab bars of sources/furniture/.

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
import math
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

# --- signs (sources/signage/) ------------------------------------------------------------
#
# Signs face -y. The plate (galvanized sheet, y 0 to 2 mm) and its retroreflective films
# (0.5 mm layers in front of it, towards -y) are plain pieces; the script draws the symbols
# and text over the films. The post stands behind the plate, from the floor.

FILM_W, FILM_R, FILM_Y, FILM_K = "Película refletiva branca", "Película refletiva vermelha", "Película refletiva amarela", "Película preta"
FILM_G, FILM_B = "Película refletiva verde", "Película refletiva azul"
SHEET, STEEL = "Chapa galvanizada", "Aço galvanizado"
PVC_G, PVC_R = "PVC fotoluminescente verde", "PVC vermelho"
ACR_W, ACR_K = "Acrílico branco", "Acrílico preto"
MATERIALS.update({
    FILM_W: {"color": [244, 244, 240], "class": "Plastic", "finish": "Glossy"},
    FILM_R: {"color": [196, 30, 38], "class": "Plastic", "finish": "Glossy"},
    FILM_Y: {"color": [250, 196, 0], "class": "Plastic", "finish": "Glossy"},
    FILM_K: {"color": [24, 24, 26], "class": "Plastic", "finish": "Matte"},
    FILM_G: {"color": [0, 112, 70], "class": "Plastic", "finish": "Glossy"},
    FILM_B: {"color": [0, 72, 150], "class": "Plastic", "finish": "Glossy"},
    SHEET: {"color": [150, 154, 158], "class": "Metal", "finish": "Satin"},
    STEEL: {"color": [176, 180, 184], "class": "Metal", "finish": "Satin"},
    PVC_G: {"color": [0, 136, 76], "class": "Plastic", "finish": "Satin"},
    PVC_R: {"color": [200, 28, 36], "class": "Plastic", "finish": "Satin"},
    ACR_W: {"color": [246, 246, 244], "class": "Plastic", "finish": "Glossy"},
    ACR_K: {"color": [28, 28, 30], "class": "Plastic", "finish": "Glossy"},
})

# The materials the scripts name (MAT.<key> in Lua); each is on a plain piece of the
# components that use it.
MAT_KEYS = {"branca": FILM_W, "vermelha": FILM_R, "amarela": FILM_Y, "preta": FILM_K, "aco": STEEL}


def front(name, points, y0, depth, material, in_plan=False):
    """A plain piece drawn on the front plane (u = x, v = z), from y = y0 to y0 + depth."""
    pts = []
    for p in points:
        q = {"u": p[0], "v": p[1]}
        if len(p) > 2:
            q["radius"] = p[2]
        pts.append(q)
    return {"name": name, "material": material, "in_plan": in_plan,
            "shape": {"Profile": {"plane": "Front", "points": pts, "offset": str(y0), "depth": str(depth)}}}


def circle(cz, r):
    return [[f"-({r})", cz, r], [f"{r}", cz, r]]


def ngon(cz, radius, n, start_deg):
    out = []
    for i in range(n):
        a = math.radians(start_deg + 360 * i / n)
        out.append([f"({radius})*{math.cos(a):.6f}", f"{cz} + ({radius})*{math.sin(a):.6f}"])
    return out


def rounded_rect(x0, z0, x1, z1, r):
    """A rectangle with round corners of radius r (counter-clockwise, arcs bulging out)."""
    return [
        [f"{x0} + {r}", z0], [f"{x1} - {r}", z0, r], [x1, f"{z0} + {r}"], [x1, f"{z1} - {r}", r],
        [f"{x1} - {r}", z1], [f"{x0} + {r}", z1, r], [x0, f"{z1} - {r}"], [x0, f"{z0} + {r}", r],
    ]


def post_and_clamps(top: str, zs: list[str], r="0.0302"):
    y = f"0.014 + {r}"
    items = [{"name": "Poste", "material": STEEL, "in_plan": True,
              "shape": {"Cylinder": {"x": "0", "y": y, "z": "0", "radius": r, "height": top}}}]
    for i, z in enumerate(zs):
        items.append(box(f"Abraçadeira {i + 1}", "-0.035", "0.002", f"{z} - 0.02", "0.07", f"0.012 + {r}", "0.04", STEEL))
    return items


def layered(shapes: list, names: list[str], materials: list[str]):
    """The plate (sheet) and its films, one per shape from the back: each 0.5 mm further out."""
    items = [front("Chapa", shapes[0], 0, 0.002, SHEET, in_plan=True)]
    for i, (pts, name, mat) in enumerate(zip(shapes, names, materials)):
        items.append(front(name, pts, f"{-0.0005 * (i + 1):.4f}", 0.0005, mat))
    return items


def sign_regulation() -> dict:
    cz, r = "AlturaLivre + Diametro/2", "Diametro/2"
    items = layered([circle(cz, r), circle(cz, f"{r} - Diametro*0.1")], ["Orla vermelha", "Fundo branco"], [FILM_R, FILM_W])
    items += post_and_clamps("AlturaLivre + Diametro - 0.03", [f"{cz} - Diametro*0.28", f"{cz} + Diametro*0.28"])
    return {
        "folder": "signage", "file": "placa-regulamentacao", "component": "Placa de regulamentação",
        "material": FILM_K, "font": True, "in_plan": False,
        "figures": ["seta_frente", "seta_direita", "seta_esquerda", "seta_retorno"],
        "params": [
            plain("Diametro", 0.5), Param("length", "AlturaLivre", 2.1, "AlturaLivre", instance=True, script=False),
            Param("choice", "Sinal", "texto", "Sinal", instance=True, choices=[
                ("texto", "Valor e unidade (velocidade, peso, altura...)"), ("proibido_estacionar", "Proibido estacionar (R-6a)"),
                ("proibido_parar", "Proibido parar e estacionar (R-6c)"), ("estacionamento", "Estacionamento regulamentado (R-6b)"),
                ("proibido_esquerda", "Proibido virar à esquerda (R-4a)"), ("proibido_direita", "Proibido virar à direita (R-4b)"),
                ("proibido_retorno", "Proibido retornar (R-5a)"), ("sentido_proibido", "Sentido proibido (R-3)"),
                ("sentido_frente", "Siga em frente"), ("sentido_direita", "Vire à direita"), ("sentido_esquerda", "Vire à esquerda"),
            ]),
            text("Valor", "40", "Valor"),
            text("Unidade", "km/h", "Unidade"),
        ],
        "items": items,
        "types": [
            t("Placa circular 50 cm", "Placa de regulamentação circular de 50 cm em chapa galvanizada com película refletiva, orla vermelha e fundo branco, em poste de aço galvanizado com altura livre de 2,10 m; o sinal (velocidade máxima, proibido estacionar, proibido parar, proibido virar, sentido proibido...) e o valor e a unidade (40 km/h, 10 t, 3,5 m...) são editáveis em cada placa"),
            t("Placa circular 60 cm", "Placa de regulamentação circular de 60 cm, altura livre de 2,10 m", Diametro=0.6),
            t("Placa circular 75 cm", "Placa de regulamentação circular de 75 cm, para vias arteriais e rodovias", Diametro=0.75),
            t("Placa circular 1,00 m", "Placa de regulamentação circular de 1,00 m, para vias de trânsito rápido", Diametro=1.0, AlturaLivre=2.3),
        ],
    }


def sign_stop() -> dict:
    cz, rr = "AlturaLivre + Largura/2", "Largura*0.541196"
    items = layered([ngon(cz, rr, 8, 22.5), ngon(cz, f"{rr} - Largura*0.037", 8, 22.5)], ["Orla branca", "Fundo vermelho"], [FILM_W, FILM_R])
    items += post_and_clamps("AlturaLivre + Largura - 0.03", [f"{cz} - Largura*0.28", f"{cz} + Largura*0.28"])
    return {
        "folder": "signage", "file": "placa-pare", "component": "Placa PARE",
        "material": FILM_W, "font": True, "in_plan": False,
        "params": [plain("Largura", 0.6), Param("length", "AlturaLivre", 2.1, "AlturaLivre", instance=True, script=False),
                   text("Texto", "PARE", "Texto")],
        "items": items,
        "types": [
            t("Placa PARE 60 cm", "Placa R-1 Parada obrigatória: octógono vermelho de 60 cm entre lados, orla e legenda brancas em película refletiva, em poste de aço galvanizado com altura livre de 2,10 m; a legenda é editável (PARE, STOP...)"),
            t("Placa PARE 80 cm", "Placa R-1 octogonal de 80 cm entre lados", Largura=0.8),
            t("Placa PARE 1,00 m", "Placa R-1 octogonal de 1,00 m entre lados, para rodovias", Largura=1.0, AlturaLivre=2.3),
        ],
    }


def sign_give_way() -> dict:
    h = "Lado*0.866025"
    top, bot = f"AlturaLivre + {h}", "AlturaLivre"
    gz = f"AlturaLivre + {h}*0.666667"  # the centroid's height
    outer = [["0", bot], ["Lado/2", top], ["-Lado/2", top]]
    k = 0.62
    inner = [["0", f"{gz} + ({bot} - ({gz}))*{k}"], [f"Lado/2*{k}", f"{gz} + ({top} - ({gz}))*{k}"], [f"-Lado/2*{k}", f"{gz} + ({top} - ({gz}))*{k}"]]
    items = layered([outer, inner], ["Orla vermelha", "Fundo branco"], [FILM_R, FILM_W])
    items += post_and_clamps(f"AlturaLivre + {h} - 0.03", [f"AlturaLivre + {h}*0.35", f"AlturaLivre + {h}*0.85"])
    return {
        "folder": "signage", "file": "placa-de-a-preferencia", "component": "Placa Dê a preferência",
        "params": [plain("Lado", 0.75), Param("length", "AlturaLivre", 2.1, "AlturaLivre", instance=True, script=False)],
        "items": items,
        "types": [
            t("Placa Dê a preferência 75 cm", "Placa R-2 Dê a preferência: triângulo com o vértice para baixo, 75 cm de lado, orla vermelha e fundo branco em película refletiva, em poste de aço galvanizado com altura livre de 2,10 m"),
            t("Placa Dê a preferência 90 cm", "Placa R-2 triangular de 90 cm de lado", Lado=0.9),
            t("Placa Dê a preferência 1,00 m", "Placa R-2 triangular de 1,00 m de lado, para rodovias", Lado=1.0, AlturaLivre=2.3),
        ],
    }


def sign_warning() -> dict:
    a = "Lado*0.707107"  # half the diagonal
    cz = f"AlturaLivre + {a}"
    shapes = [ngon(cz, a, 4, 90), ngon(cz, f"{a} - Lado*0.03", 4, 90), ngon(cz, f"{a} - Lado*0.065", 4, 90)]
    items = layered(shapes, ["Orla externa amarela", "Orla interna preta", "Fundo amarelo"], [FILM_Y, FILM_K, FILM_Y])
    items += post_and_clamps(f"AlturaLivre + 2*{a} - 0.03", [f"{cz} - {a}*0.5", f"{cz} + {a}*0.5"])
    return {
        "folder": "signage", "file": "placa-advertencia", "component": "Placa de advertência",
        "material": FILM_K, "font": True, "in_plan": False,
        "figures": ["seta_frente", "seta_direita", "seta_esquerda"],
        "params": [
            plain("Lado", 0.6), Param("length", "AlturaLivre", 2.1, "AlturaLivre", instance=True, script=False),
            Param("choice", "Sinal", "texto", "Sinal", instance=True, choices=[
                ("texto", "Texto (até duas linhas)"), ("lombada", "Saliência ou lombada (A-18)"), ("curva_direita", "Curva à direita"),
                ("curva_esquerda", "Curva à esquerda"), ("cruzamento", "Cruzamento de vias (A-7a)"), ("duplo_sentido", "Sentido duplo de circulação"),
            ]),
            text("Linha1", "ESCOLA", "Linha 1"),
            text("Linha2", "", "Linha 2"),
        ],
        "items": items,
        "types": [
            t("Placa de advertência 60 cm", "Placa de advertência quadrada de 60 cm de lado, com uma diagonal na vertical, fundo amarelo e orla preta em película refletiva, em poste de aço galvanizado com altura livre de 2,10 m; o sinal (texto, lombada, curva, cruzamento, sentido duplo) e as duas linhas de texto são editáveis em cada placa"),
            t("Placa de advertência 45 cm", "Placa de advertência de 45 cm de lado, para vias locais e condomínios", Lado=0.45),
            t("Placa de advertência 75 cm", "Placa de advertência de 75 cm de lado, para vias arteriais", Lado=0.75),
            t("Placa de advertência 90 cm", "Placa de advertência de 90 cm de lado, para rodovias", Lado=0.9, AlturaLivre=2.3),
        ],
    }


def sign_parking() -> dict:
    cz = "AlturaLivre + AlturaInfo + 0.05 + Diametro/2"
    rect = rounded_rect("-LarguraInfo/2", "AlturaLivre", "LarguraInfo/2", "AlturaLivre + AlturaInfo", "0.02")
    inner = rounded_rect("-LarguraInfo/2 + 0.012", "AlturaLivre + 0.012", "LarguraInfo/2 - 0.012", "AlturaLivre + AlturaInfo - 0.012", "0.012")
    items = layered([circle(cz, "Diametro/2"), circle(cz, "Diametro/2 - Diametro*0.1")], ["Orla vermelha", "Fundo branco"], [FILM_R, FILM_W])
    items += [front("Chapa da informação", rect, 0, 0.002, SHEET, in_plan=True),
              front("Orla da informação", rect, -0.0005, 0.0005, FILM_K),
              front("Fundo da informação", inner, -0.001, 0.0005, FILM_W)]
    items += post_and_clamps("AlturaLivre + AlturaInfo + 0.05 + Diametro - 0.03",
                             ["AlturaLivre + AlturaInfo/2", f"{cz}"])
    return {
        "folder": "signage", "file": "placa-estacionamento", "component": "Placa de estacionamento regulamentado",
        "material": FILM_K, "font": True, "in_plan": False, "figures": ["cadeirante"],
        "params": [
            plain("Diametro", 0.5), plain("LarguraInfo", 0.5), plain("AlturaInfo", 0.4),
            Param("length", "AlturaLivre", 2.1, "AlturaLivre", instance=True, script=False),
            Param("choice", "Simbolo", "nenhum", "Símbolo na informação", instance=True,
                  choices=[("nenhum", "Nenhum"), ("cadeirante", "Símbolo internacional de acesso")]),
            text("Linha1", "VAGA EXCLUSIVA", "Linha 1"),
            text("Linha2", "IDOSO", "Linha 2"),
            text("Linha3", "CREDENCIAL OBRIGATÓRIA", "Linha 3"),
        ],
        "items": items,
        "types": [
            t("Placa estacionamento 50 cm com informação", "Placa R-6b Estacionamento regulamentado de 50 cm com informação complementar de 50 x 40 cm abaixo (Resolução CONTRAN 965/2022), em poste de aço galvanizado; as três linhas da informação (VAGA EXCLUSIVA, IDOSO, PcD, CARGA E DESCARGA, horários...) e o símbolo de acesso são editáveis em cada placa"),
            t("Placa estacionamento 60 cm com informação", "Placa R-6b de 60 cm com informação complementar de 60 x 45 cm", Diametro=0.6, LarguraInfo=0.6, AlturaInfo=0.45),
        ],
    }


def sign_guide(file, component, color, default_lines, arrow, what) -> dict:
    W, Hp = "Largura", "Altura"
    r = "min(Largura, Altura)*0.05"
    outer = rounded_rect(f"-{W}/2", "AlturaLivre", f"{W}/2", f"AlturaLivre + {Hp}", "0.03")
    e = "0.012"
    inner = rounded_rect(f"-{W}/2 + {e}", f"AlturaLivre + {e}", f"{W}/2 - {e}", f"AlturaLivre + {Hp} - {e}", "0.02")
    items = layered([outer, inner], ["Orla branca", "Fundo"], [FILM_W, color])
    for i, z in enumerate((f"AlturaLivre + {Hp}*0.25", f"AlturaLivre + {Hp}*0.75")):
        items.append(box(f"Trilho de fixação {i + 1}", f"-{W}/2 + 0.04", "0.002", f"{z} - 0.02", f"{W} - 0.08", "0.022", "0.04", STEEL))
    del r
    return {
        "folder": "signage", "file": file, "component": component,
        "material": FILM_W, "font": True, "figures": ["seta_frente"],
        "params": [
            plain("Largura", 1.0), plain("Altura", 0.5), Param("length", "AlturaLivre", 2.1, "AlturaLivre", instance=True, script=False),
            text("Linha1", default_lines[0], "Linha 1"),
            text("Linha2", default_lines[1], "Linha 2"),
            text("Linha3", default_lines[2], "Linha 3"),
            Param("choice", "Seta", arrow, "Seta", instance=True, choices=[
                ("nenhuma", "Nenhuma"), ("esquerda", "Para a esquerda"), ("direita", "Para a direita"), ("frente", "Em frente"),
                ("frente_esquerda", "Em frente, à esquerda"), ("frente_direita", "Em frente, à direita"),
            ]),
        ],
        "items": items,
        "script_body": "placa-orientacao",
        "types": [
            t(f"{component} 1,00 x 0,50", f"{what} de 1,00 x 0,50 m com orla branca e cantos arredondados, em película refletiva sobre chapa galvanizada com trilhos de fixação, num poste (dois a partir de 1,30 m de largura) com altura livre de 2,10 m; até três linhas de texto e a seta são editáveis em cada placa"),
            t(f"{component} 0,60 x 0,30", f"{what} de 0,60 x 0,30 m, para condomínios, estacionamentos e vias internas", Largura=0.6, Altura=0.3),
            t(f"{component} 2,00 x 1,00", f"{what} de 2,00 x 1,00 m em dois postes", Largura=2.0, Altura=1.0, AlturaLivre=2.3),
            t(f"{component} 3,00 x 1,50", f"{what} de 3,00 x 1,50 m em dois postes, para vias arteriais", Largura=3.0, Altura=1.5, AlturaLivre=2.5),
        ],
    }


def sign_wall(file, component, plate_mat, defaults, arrow, choices_down, what, sizes) -> dict:
    pts = rounded_rect("-Largura/2", "Elevacao", "Largura/2", "Elevacao + Altura", "Altura*0.04")
    return {
        "folder": "signage", "file": file, "component": component,
        "material": FILM_W, "font": True, "figures": ["seta_frente"],
        "params": [
            plain("Largura", sizes[0][0]), plain("Altura", sizes[0][1]),
            Param("length", "Elevacao", 2.1, "Elevacao", instance=True, script=False),
            text("Linha1", defaults[0], "Linha 1"),
            text("Linha2", defaults[1], "Linha 2"),
            Param("choice", "Seta", arrow, "Seta", instance=True, choices=[
                ("nenhuma", "Nenhuma"), ("esquerda", "Para a esquerda"), ("direita", "Para a direita"), ("frente", "Para cima (em frente)"),
                ("baixo", "Para baixo"), ("frente_esquerda", "Diagonal à esquerda"), ("frente_direita", "Diagonal à direita"),
            ]),
        ],
        "items": [front("Placa", pts, -0.002, 0.002, plate_mat, in_plan=True)],
        "script_body": "placa-emergencia",
        "types": [
            t(f"{component} {w * 100:.0f} x {h * 100:.0f} cm".replace(".", ","),
              (what if i == 0 else f"{component} de {w * 100:.0f} x {h * 100:.0f} cm") , **({} if i == 0 else {"Largura": w, "Altura": h}))
            for i, (w, h) in enumerate(sizes)
        ],
    }


def sign_room() -> dict:
    pts = rounded_rect("-Largura/2", "Elevacao", "Largura/2", "Elevacao + Altura", "0.008")
    return {
        "folder": "signage", "file": "placa-identificacao", "component": "Placa de identificação tátil",
        "material": ACR_K, "font": True,
        "params": [
            plain("Largura", 0.3), plain("Altura", 0.15), Param("length", "Elevacao", 1.3, "Elevacao", instance=True, script=False),
            text("Linha1", "SALA 101", "Linha 1"),
            text("Linha2", "REUNIÕES", "Linha 2"),
            length("AlturaTexto", 0.025, "Altura das letras"),
            Param("boolean", "Braille", True, "Braille", instance=True),
        ],
        "items": [front("Placa", pts, -0.003, 0.003, ACR_W, in_plan=True)],
        "script_body": "placa-identificacao",
        "types": [
            t("Placa de identificação 30 x 15 cm", "Placa de identificação de ambiente em acrílico branco de 3 mm, 30 x 15 cm, com texto em relevo de 1 mm e a transcrição em braille (ABNT NBR 9050), fixada na parede a 1,30 m do piso; as duas linhas de texto são editáveis em cada placa e o braille acompanha o texto"),
            t("Placa de identificação 20 x 10 cm", "Placa de identificação tátil de 20 x 10 cm, letras de 2 cm, para portas", Largura=0.2, Altura=0.1, AlturaTexto=0.02),
            t("Placa de identificação 40 x 20 cm", "Placa de identificação tátil de 40 x 20 cm, letras de 3,5 cm", Largura=0.4, Altura=0.2, AlturaTexto=0.035),
        ],
    }


def house_number() -> dict:
    pts = rounded_rect("-Largura/2", "Elevacao", "Largura/2", "Elevacao + Altura", "0.012")
    return {
        "folder": "signage", "file": "numero-predial", "component": "Número predial",
        "material": ACR_W, "font": True,
        "params": [
            plain("Largura", 0.25), plain("Altura", 0.15), Param("length", "Elevacao", 1.8, "Elevacao", instance=True, script=False),
            text("Numero", "123", "Número"),
            text("Logradouro", "RUA DAS FLORES", "Logradouro"),
        ],
        "items": [front("Placa", pts, -0.004, 0.004, ACR_K, in_plan=True)],
        "script_body": "numero-predial",
        "types": [
            t("Número predial 25 x 15 cm", "Placa de numeração predial em acrílico preto de 4 mm, 25 x 15 cm, com o número e o logradouro em relevo branco de 2 mm, fixada na fachada a 1,80 m; número e logradouro editáveis em cada placa"),
            t("Número predial 40 x 25 cm", "Placa de numeração predial de 40 x 25 cm, para fachadas recuadas", Largura=0.4, Altura=0.25),
        ],
    }


COMPONENTS += [
    sign_regulation(), sign_stop(), sign_give_way(), sign_warning(), sign_parking(),
    sign_guide("placa-orientacao", "Placa de orientação", FILM_G, ("CENTRO", "AEROPORTO", ""), "direita",
               "Placa de orientação de destino (verde)"),
    sign_guide("placa-servicos", "Placa de serviços", FILM_B, ("ESTACIONAMENTO", "", ""), "frente",
               "Placa indicativa de serviços auxiliares e atrativos (azul)"),
    sign_wall("placa-saida-emergencia", "Placa de saída de emergência", PVC_G, ("SAÍDA", ""), "direita", True,
              "Placa de saída de emergência (ABNT NBR 13434) em PVC fotoluminescente verde, 32 x 16 cm, com texto e seta brancos, fixada na parede a 2,10 m; o texto (SAÍDA, SAÍDA DE EMERGÊNCIA, ROTA DE FUGA...) e a seta são editáveis em cada placa",
              [(0.32, 0.16), (0.24, 0.12), (0.48, 0.24)]),
    sign_wall("placa-equipamento-incendio", "Placa de equipamento de incêndio", PVC_R, ("EXTINTOR", "PÓ ABC"), "nenhuma", True,
              "Placa de equipamento de combate a incêndio (ABNT NBR 13434) em PVC vermelho, 32 x 16 cm, com texto branco, fixada na parede acima do equipamento; as duas linhas (EXTINTOR, HIDRANTE, ALARME, PÓ ABC, CO2...) e a seta são editáveis em cada placa",
              [(0.32, 0.16), (0.24, 0.12), (0.48, 0.24)]),
    sign_room(), house_number(),
]

# --- site furniture and accessibility ------------------------------------------------------

WOOD, CONCRETE, PAINTED = "Madeira tratada", "Concreto", "Aço pintado verde"
INOX, RUBBER_SEAT = "Aço inox escovado", "Borracha preta"
PE = {"azul": "Polietileno azul", "vermelho": "Polietileno vermelho", "verde": "Polietileno verde", "amarelo": "Polietileno amarelo"}
TACTILE = "Concreto amarelo (piso tátil)"
LUMINAIRE, LENS = "Alumínio pintado cinza", "Policarbonato leitoso"
MATERIALS.update({
    WOOD: {"color": [150, 104, 62], "class": "Wood", "finish": "Satin"},
    PAINTED: {"color": [38, 78, 58], "class": "Metal", "finish": "Satin"},
    INOX: {"color": [196, 198, 200], "class": "Metal", "finish": "Satin"},
    PE["azul"]: {"color": [0, 92, 178], "class": "Plastic", "finish": "Satin"},
    PE["vermelho"]: {"color": [206, 32, 40], "class": "Plastic", "finish": "Satin"},
    PE["verde"]: {"color": [0, 138, 72], "class": "Plastic", "finish": "Satin"},
    PE["amarelo"]: {"color": [250, 200, 0], "class": "Plastic", "finish": "Satin"},
    TACTILE: {"color": [236, 188, 32], "class": "Concrete", "finish": "Matte"},
    LUMINAIRE: {"color": [92, 96, 100], "class": "Metal", "finish": "Satin"},
    LENS: {"color": [238, 240, 236], "class": "Plastic", "finish": "Satin", "transparency": 0.2},
})
MAT_KEYS.update({"concreto": CONCRETE, "madeira": WOOD})


def number(name, default):
    return Param("number", name, default, name, script=False)


def side(name, points, x0, depth, material, in_plan=True):
    """A plain piece drawn on the side plane (u = y, v = z), from x = x0 to x0 + depth."""
    return profile_side(name, points, x0, depth, material, in_plan=in_plan)


def revolution_front(name, points, material, in_plan=True):
    """A plain body of revolution about the vertical line x = 0, y = 0 (profile on the front plane, u >= 0)."""
    pts = []
    for p in points:
        q = {"u": p[0], "v": p[1]}
        if len(p) > 2:
            q["radius"] = p[2]
        pts.append(q)
    return {"name": name, "material": material, "in_plan": in_plan,
            "shape": {"Revolution": {"plane": "Front", "points": pts, "offset": "0", "axis": "0", "angle": "360"}}}


def sweep_item(name, plane, path, radius, offset, material, in_plan=True):
    pts = []
    for p in path:
        q = {"u": p[0], "v": p[1]}
        if len(p) > 2:
            q["radius"] = p[2]
        pts.append(q)
    return {"name": name, "material": material, "in_plan": in_plan,
            "shape": {"Sweep": {"plane": plane, "path": pts, "offset": offset,
                                "profile": [{"u": f"-{radius}", "v": "0", "radius": radius}, {"u": radius, "v": "0", "radius": radius}]}}}


def bench() -> dict:
    sec = [["-0.24", "0"], ["0.24", "0"], ["0.2", "0.42"], ["-0.2", "0.42"]]
    items = [side(f"Apoio de concreto {i + 1}", sec, f"{s}(Comprimento/2 - 0.25) - 0.06", "0.12", CONCRETE) for i, s in enumerate(("-", ""))]
    for k in range(5):
        y = -0.224 + k * 0.092
        items.append(box(f"Ripa do assento {k + 1}", "-Comprimento/2", f"{y:.3f}", "0.42", "Comprimento", "0.08", "0.035", WOOD))
    return {
        "file": "banco-praca", "component": "Banco de praça", "material": WOOD,
        "params": [plain("Comprimento", 1.8), Param("boolean", "Encosto", True, "Encosto", instance=True)],
        "items": items, "script_body": "banco-praca",
        "types": [
            t("Banco de praça 1,80 m", "Banco de praça com apoios de concreto e assento de cinco ripas de madeira tratada a 45 cm do piso, 1,80 m; o encosto inclinado (três ripas em montantes de concreto) pode ser tirado em cada banco"),
            t("Banco de praça 2,40 m", "Banco de praça de 2,40 m, com um apoio intermediário", Comprimento=2.4),
            t("Banco de praça 1,20 m", "Banco de praça curto, de 1,20 m", Comprimento=1.2),
        ],
    }


def litter_bin() -> dict:
    r, h, z0 = "Raio", "AlturaCesto", "0.85 - AlturaCesto"
    cup = [["0", z0], [r, z0], [r, f"{z0} + {h}"], [f"{r} - 0.003", f"{z0} + {h}"], [f"{r} - 0.003", f"{z0} + 0.003"], ["0", f"{z0} + 0.003"]]
    rim = [[f"{r} - 0.004", f"{z0} + {h} - 0.012"], [f"{r} + 0.008", f"{z0} + {h} - 0.012"], [f"{r} + 0.008", f"{z0} + {h}"], [f"{r} - 0.004", f"{z0} + {h}"]]
    post_y = f"{r} + 0.05"
    return {
        "file": "lixeira", "component": "Lixeira de praça",
        "params": [plain("Raio", 0.2), plain("AlturaCesto", 0.5)],
        "items": [
            revolution_front("Cesto", cup, PAINTED), revolution_front("Aro", rim, PAINTED),
            {"name": "Poste", "material": STEEL, "in_plan": True, "shape": {"Cylinder": {"x": "0", "y": post_y, "z": "0", "radius": "0.03", "height": "1.0"}}},
            box("Braçadeira superior", "-0.03", "Raio - 0.01", "0.85 - 0.05", "0.06", "0.06", "0.03", STEEL),
            box("Braçadeira inferior", "-0.03", "Raio - 0.01", f"{z0} + 0.06", "0.06", "0.06", "0.03", STEEL),
        ],
        "types": [
            t("Lixeira de praça 60 L", "Lixeira de praça em aço pintado, cesto cilíndrico de 40 cm de diâmetro (60 L) com a boca a 85 cm do piso, presa a um poste de aço galvanizado"),
            t("Lixeira de praça 100 L", "Lixeira de praça de 100 L, cesto de 46 cm de diâmetro", Raio=0.23, AlturaCesto=0.6),
            t("Lixeira de praça 40 L", "Lixeira de praça de 40 L, cesto de 34 cm, para calçadas estreitas", Raio=0.17, AlturaCesto=0.45),
        ],
    }


def recycling() -> dict:
    items = []
    w, gap, d = 0.4, 0.03, 0.3
    colors = ["azul", "vermelho", "verde", "amarelo"]
    for i, c in enumerate(colors):
        x = -1.5 * (w + gap) + i * (w + gap)
        items.append(box(f"Coletor {c}", f"{x - w / 2 + 0.01:.3f}", "-0.15", "0.35", f"{w - 0.02:.3f}", f"{d:.3f}", "0.52", PE[c]))
        items.append(box(f"Tampa {c}", f"{x - w / 2:.3f}", "-0.16", "0.87", f"{w:.3f}", f"{d + 0.02:.3f}", "0.04", PE[c]))
        items.append({"name": f"Boca {c}", "material": RUBBER_SEAT, "in_plan": False,
                      "shape": {"Box": {"x": f"{x - 0.12:.3f}", "y": "-0.1615", "z": "0.88", "width": "0.24", "depth": "0.002", "height": "0.022"}}})
    span = 4 * w + 3 * gap
    for i, s in enumerate((-1, 1)):
        items.append({"name": f"Poste {i + 1}", "material": STEEL, "in_plan": True,
                      "shape": {"Cylinder": {"x": f"{s * (span / 2 + 0.04):.3f}", "y": "0.02", "z": "0", "radius": "0.03", "height": "1.0"}}})
    items.append(box("Travessa", f"{-span / 2 - 0.04:.3f}", "0.15", "0.55", f"{span + 0.08:.3f}", "0.03", "0.05", STEEL))
    return {
        "file": "coletores-reciclaveis", "component": "Coletores de recicláveis", "material": ACR_W, "font": True,
        "params": [text("Rotulo1", "PAPEL", "Rótulo do coletor azul"), text("Rotulo2", "PLÁSTICO", "Rótulo do coletor vermelho"),
                   text("Rotulo3", "VIDRO", "Rótulo do coletor verde"), text("Rotulo4", "METAL", "Rótulo do coletor amarelo")],
        "items": items, "script_body": "coletores-reciclaveis",
        "types": [t("Coletores de recicláveis 4 x 50 L", "Conjunto de quatro coletores de 50 L em polietileno nas cores da Resolução CONAMA 275/2001 (azul papel, vermelho plástico, verde vidro, amarelo metal) numa estrutura de aço galvanizado; os rótulos são editáveis em cada conjunto")],
    }


def bike_rack() -> dict:
    x = "-(Suportes - 1)*Espacamento/2"
    items = [{"name": f"Flange {i + 1}", "material": STEEL, "in_plan": True,
              "shape": {"Cylinder": {"x": x, "y": y, "z": "0", "radius": "0.06", "height": "0.006"}}}
             for i, y in enumerate(("-Largura/2", "Largura/2"))]
    return {
        "file": "bicicletario", "component": "Bicicletário", "material": STEEL,
        "params": [number("Suportes", 3), plain("Espacamento", 0.8), plain("Largura", 0.7), plain("Altura", 0.75)],
        "items": items, "script_body": "bicicletario",
        "types": [
            t("Bicicletário 3 suportes", "Bicicletário de suportes em U invertido de tubo de aço galvanizado de 50 mm, 75 cm de altura e 70 cm de largura, chumbados no piso a cada 80 cm; cada suporte prende duas bicicletas (6 vagas)"),
            t("Bicicletário 5 suportes", "Bicicletário de cinco suportes em U invertido (10 vagas)", Suportes=5),
            t("Bicicletário 1 suporte", "Um suporte em U invertido (2 vagas)", Suportes=1),
        ],
    }


def bollard_concrete() -> dict:
    prof = [["0", "0"], ["Raio", "0"], ["Raio", "Altura - Raio*0.5"], ["Raio*0.5", "Altura", "Raio*0.6"], ["0", "Altura"]]
    band = [["Raio - 0.001", "Altura*0.6"], ["Raio + 0.002", "Altura*0.6"], ["Raio + 0.002", "Altura*0.6 + 0.08"], ["Raio - 0.001", "Altura*0.6 + 0.08"]]
    return {
        "file": "frade-concreto", "component": "Frade de concreto",
        "params": [plain("Raio", 0.13), plain("Altura", 0.6)],
        "items": [revolution_front("Corpo", prof, CONCRETE), revolution_front("Faixa amarela", band, YELLOW)],
        "types": [
            t("Frade de concreto 60 cm", "Frade (balizador) cilíndrico de concreto de 26 cm de diâmetro e 60 cm de altura, topo abaulado e faixa amarela, para proteger calçadas e áreas de pedestres"),
            t("Frade de concreto 80 cm", "Frade de concreto de 30 cm de diâmetro e 80 cm de altura", Raio=0.15, Altura=0.8),
            t("Frade de concreto 45 cm", "Frade baixo de concreto, 24 cm de diâmetro e 45 cm de altura", Raio=0.12, Altura=0.45),
        ],
    }


def bollard_steel() -> dict:
    r, h = "Raio", "Altura"
    body = [["0", "0.01"], [r, "0.01"], [r, f"{h} - {r}*0.6"], [f"{r}*0.4", h, f"{r}*0.8"], ["0", h]]
    flange = [["0", "0"], [f"{r} + 0.05", "0"], [f"{r} + 0.05", "0.01"], ["0", "0.01"]]
    items = [revolution_front("Tubo", body, STEEL), revolution_front("Flange", flange, STEEL)]
    for i, z in enumerate((f"{h} - 0.22", f"{h} - 0.12")):
        items.append(revolution_front(f"Faixa refletiva {i + 1}", [[f"{r} - 0.001", z], [f"{r} + 0.001", z], [f"{r} + 0.001", f"{z} + 0.05"], [f"{r} - 0.001", f"{z} + 0.05"]], FILM_Y))
    return {
        "file": "balizador-aco", "component": "Balizador de aço",
        "params": [plain("Raio", 0.057), plain("Altura", 0.9)],
        "items": items,
        "types": [
            t("Balizador de aço 90 cm", "Balizador (frade) de tubo de aço galvanizado de 114 mm, 90 cm de altura, topo abaulado, flange de fixação e duas faixas refletivas amarelas"),
            t("Balizador de aço 1,10 m", "Balizador de aço de 1,10 m, para áreas de manobra", Altura=1.1),
            t("Balizador de aço 75 cm", "Balizador de aço de 76 mm e 75 cm, para calçadas", Raio=0.038, Altura=0.75),
        ],
    }


def picnic_table() -> dict:
    items = []
    for k in range(5):
        y = -0.35 + k * 0.142
        items.append(box(f"Ripa do tampo {k + 1}", "-Comprimento/2", f"{y:.3f}", "0.72", "Comprimento", "0.13", "0.035", WOOD))
    for n, ys in (("frente", (-0.87, -0.735)), ("trás", (0.605, 0.74))):
        for k, y in enumerate(ys):
            items.append(box(f"Ripa do banco da {n} {k + 1}", "-Comprimento/2 + 0.05", f"{y:.3f}", "0.42", "Comprimento - 0.1", "0.13", "0.035", WOOD))
    for i, sx in enumerate(("-", "")):
        x0 = f"{sx}(Comprimento/2 - 0.3) - 0.025"
        items.append(side(f"Perna do tampo {i + 1}a", [["-0.62", "0"], ["-0.52", "0"], ["-0.05", "0.72"], ["-0.15", "0.72"]], x0, "0.05", WOOD))
        items.append(side(f"Perna do tampo {i + 1}b", [["0.52", "0"], ["0.62", "0"], ["0.15", "0.72"], ["0.05", "0.72"]], x0, "0.05", WOOD))
        items.append(box(f"Travessa do banco {i + 1}", x0, "-0.9", "0.33", "0.05", "1.8", "0.09", WOOD))
        items.append(box(f"Travessa do tampo {i + 1}", x0, "-0.33", "0.63", "0.05", "0.66", "0.09", WOOD))
    return {
        "file": "mesa-piquenique", "component": "Mesa de piquenique",
        "params": [plain("Comprimento", 1.8)],
        "items": items,
        "types": [
            t("Mesa de piquenique 1,80 m", "Mesa de piquenique de madeira tratada com bancos fixos dos dois lados: tampo de 1,80 x 0,70 m a 75 cm e bancos a 45 cm, pernas em A; para 6 pessoas"),
            t("Mesa de piquenique 2,40 m", "Mesa de piquenique de 2,40 m, para 8 pessoas", Comprimento=2.4),
        ],
    }


def street_light() -> dict:
    pole = [["0", "0.02"], ["RaioBase", "0.02"], ["RaioTopo", "Altura"], ["0", "Altura"]]
    base = [["0", "0"], ["RaioBase + 0.08", "0"], ["RaioBase + 0.08", "0.02"], ["0", "0.02"]]
    tip = "-Braco"
    return {
        "file": "poste-iluminacao", "component": "Poste de iluminação",
        "params": [plain("Altura", 6.0), plain("Braco", 1.5), plain("RaioBase", 0.075), plain("RaioTopo", 0.035)],
        "items": [
            revolution_front("Poste cônico", pole, STEEL), revolution_front("Placa de base", base, STEEL),
            sweep_item("Braço", "Side", [["0", "Altura - 0.6"], ["0", "Altura - 0.1", "0.5"], ["-0.5", "Altura + 0.4"], [tip, "Altura + 0.45"]], "0.03", "0", STEEL),
            box("Luminária LED", "-0.16", f"{tip} - 0.62", "Altura + 0.36", "0.32", "0.65", "0.09", LUMINAIRE),
            box("Difusor", "-0.13", f"{tip} - 0.58", "Altura + 0.35", "0.26", "0.5", "0.012", LENS),
        ],
        "types": [
            t("Poste de iluminação 6 m", "Poste de iluminação pública cônico de aço galvanizado de 6 m, braço curvo de 1,50 m e luminária LED, sobre placa de base; a luminária avança para -Y (sobre a via)"),
            t("Poste de iluminação 9 m", "Poste cônico de 9 m com braço de 2,00 m, para vias coletoras", Altura=9.0, Braco=2.0, RaioBase=0.09, RaioTopo=0.04),
            t("Poste de iluminação 4 m", "Poste de 4 m com braço de 0,80 m, para praças, condomínios e estacionamentos", Altura=4.0, Braco=0.8, RaioBase=0.06, RaioTopo=0.03),
        ],
    }


def swing() -> dict:
    W, Hh = "Largura", "Altura"
    items = []
    for i, sx in enumerate(("-", "")):
        x = f"{sx}{W}/2"
        for j, sy in enumerate(("-", "")):
            items.append(sweep_item(f"Perna {i + 1}{'ab'[j]}", "Side", [[f"{sy}{Hh}*0.32", "0"], ["0", Hh]], "0.03", x, PAINTED))
    items.append(sweep_item("Travessa superior", "Front", [[f"-{W}/2 - 0.05", f"{Hh} - 0.03"], [f"{W}/2 + 0.05", f"{Hh} - 0.03"]], "0.04", "0", PAINTED))
    for k, cx in enumerate((f"-{W}/4", f"{W}/4")):
        for j, dx in enumerate(("-0.2", "0.2")):
            items.append(sweep_item(f"Corrente {k + 1}{'ab'[j]}", "Front", [[f"{cx} + ({dx})", "0.45"], [f"{cx} + ({dx})", f"{Hh} - 0.07"]], "0.005", "0", STEEL, in_plan=False))
        items.append(box(f"Assento {k + 1}", f"{cx} - 0.23", "-0.08", "0.42", "0.46", "0.16", "0.03", RUBBER_SEAT))
    return {
        "file": "balanco", "component": "Balanço",
        "params": [plain("Largura", 2.4), plain("Altura", 2.2)],
        "items": items,
        "types": [
            t("Balanço 2 lugares", "Balanço de dois lugares em tubo de aço pintado com pernas em A, travessa a 2,20 m, correntes de aço e assentos de borracha a 45 cm do piso"),
            t("Balanço 2 lugares infantil", "Balanço infantil de dois lugares com travessa a 1,90 m", Largura=2.0, Altura=1.9),
        ],
    }


def pergola() -> dict:
    W, D, Hh = "Largura", "Profundidade", "Altura"
    items = []
    for i, (sx, sy) in enumerate((("-", "-"), ("", "-"), ("-", ""), ("", ""))):
        x = f"{sx}({W}/2 - 0.075) - 0.075"
        y = f"{sy}({D}/2 - 0.075) - 0.075"
        items.append(box(f"Pilar {i + 1}", x, y, "0", "0.15", "0.15", f"{Hh} - 0.2", WOOD))
    for i, sy in enumerate(("-", "")):
        items.append(box(f"Viga {i + 1}", f"-{W}/2 - 0.3", f"{sy}({D}/2 - 0.075) - 0.03", f"{Hh} - 0.2", f"{W} + 0.6", "0.06", "0.2", WOOD))
    return {
        "file": "pergolado", "component": "Pergolado", "material": WOOD,
        "params": [plain("Largura", 3.0), plain("Profundidade", 3.0), plain("Altura", 2.6),
                   length("Espacamento", 0.4, "Espaçamento dos caibros"), length("LarguraCaibro", 0.05, "Largura dos caibros"),
                   length("AlturaCaibro", 0.15, "Altura dos caibros")],
        "items": items, "script_body": "pergolado",
        "types": [
            t("Pergolado 3,00 x 3,00", "Pergolado de madeira tratada de 3,00 x 3,00 m: pilares de 15 x 15 cm, vigas duplas de 6 x 20 cm em balanço e caibros de 5 x 15 cm a cada 40 cm, com 2,60 m de altura livre até as vigas"),
            t("Pergolado 4,00 x 3,00", "Pergolado de 4,00 x 3,00 m", Largura=4.0),
            t("Pergolado 6,00 x 3,50", "Pergolado de 6,00 x 3,50 m com pilares intermediários", Largura=6.0, Profundidade=3.5),
        ],
    }


def tactile(file, component, default) -> dict:
    return {
        "file": file, "component": component, "material": TACTILE,
        "params": [plain("Largura", 1.0), plain("Comprimento", 0.25),
                   Param("choice", "Tipo", default, "Relevo", instance=True, choices=[("alerta", "Alerta"), ("direcional", "Direcional")])],
        "items": [box("Placas", "-Largura/2", "-Comprimento/2", "-0.025", "Largura", "Comprimento", "0.025", TACTILE)],
        "script_body": "piso-tatil",
        "types": [
            t(f"{component} 1,00 x 0,25", f"{component} (ABNT NBR 16537) em placas de concreto amarelo de 25 x 25 cm assentadas rente ao piso, com o relevo de 4 mm acima dele; faixa de 1,00 x 0,25 m (o comprimento corre ao longo de Y, o sentido da caminhada); o relevo pode ser trocado em cada faixa"),
            t(f"{component} 1,00 x 1,00", f"{component} em área de 1,00 x 1,00 m", Comprimento=1.0),
            t(f"{component} 0,25 x 1,00", f"{component} em faixa de 0,25 x 1,00 m ao longo de Y", Largura=0.25, Comprimento=1.0),
        ],
    }


def grab_bar(file, component, l_shape) -> dict:
    r = "0.0175"
    yb = f"-(0.04 + {r})"  # the bar's axis: 4 cm clear of the wall
    items = []

    def flange_post(name, x, z):
        disc = [[x, "-0.008"], [f"{x} + 0.035", "-0.008"], [f"{x} + 0.035", "0"], [x, "0"]]
        items.append({"name": f"Canopla {name}", "material": INOX, "in_plan": True,
                      "shape": {"Revolution": {"plane": "Plan", "points": [{"u": u, "v": v} for u, v in disc], "offset": z, "axis": x, "angle": "360"}}})
        items.append(sweep_item(f"Haste {name}", "Side", [["-0.008", z], [yb, z]], "0.011", x, INOX, in_plan=False))

    if not l_shape:
        items.append(sweep_item("Barra", "Front", [["-Comprimento/2", "Elevacao"], ["Comprimento/2", "Elevacao"]], r, yb, INOX))
        flange_post("esquerda", "-Comprimento/2 + 0.0175", "Elevacao")
        flange_post("direita", "Comprimento/2 - 0.0175", "Elevacao")
        params = [plain("Comprimento", 0.8), Param("length", "Elevacao", 0.75, "Elevacao", instance=True, script=False)]
        types = [
            t("Barra de apoio reta 80 cm", "Barra de apoio reta de aço inox de 35 mm, 80 cm, a 4 cm da parede, fixada por canoplas nas pontas (ABNT NBR 9050), com o eixo a 75 cm do piso"),
            t("Barra de apoio reta 40 cm", "Barra de apoio reta de 40 cm, para lavatórios e portas", Comprimento=0.4),
            t("Barra de apoio reta 60 cm", "Barra de apoio reta de 60 cm", Comprimento=0.6),
            t("Barra de apoio reta 90 cm", "Barra de apoio reta de 90 cm, para a parede lateral da bacia", Comprimento=0.9),
        ]
    else:
        path = [["-Comprimento/2", "Elevacao"], ["Comprimento/2 - 0.05", "Elevacao", "0.05"], ["Comprimento/2", "Elevacao + 0.05"], ["Comprimento/2", "Elevacao + AlturaVertical"]]
        items.append(sweep_item("Barra", "Front", path, r, yb, INOX))
        flange_post("horizontal", "-Comprimento/2 + 0.0175", "Elevacao")
        flange_post("do canto", "Comprimento/2 - 0.04", "Elevacao + 0.04")
        flange_post("vertical", "Comprimento/2 - 0.0175", "Elevacao + AlturaVertical - 0.0175")
        params = [plain("Comprimento", 0.7), plain("AlturaVertical", 0.7), Param("length", "Elevacao", 0.75, "Elevacao", instance=True, script=False)]
        types = [
            t("Barra de apoio em L 70 x 70 cm", "Barra de apoio em L de aço inox de 35 mm, 70 cm na horizontal e 70 cm na vertical, a 4 cm da parede (ABNT NBR 9050), para boxes de chuveiro; a parte horizontal a 75 cm do piso"),
            t("Barra de apoio em L 60 x 60 cm", "Barra de apoio em L de 60 x 60 cm", Comprimento=0.6, AlturaVertical=0.6),
        ]
    return {"folder": "furniture", "file": file, "component": component, "params": params, "items": items, "types": types}


COMPONENTS += [
    bench(), litter_bin(), recycling(), bike_rack(), bollard_concrete(), bollard_steel(), picnic_table(),
    street_light(), swing(), pergola(),
    tactile("piso-tatil-alerta", "Piso tátil de alerta", "alerta"),
    tactile("piso-tatil-direcional", "Piso tátil direcional", "direcional"),
    grab_bar("barra-apoio-reta", "Barra de apoio reta", False),
    grab_bar("barra-apoio-l", "Barra de apoio em L", True),
]


# --- scripts ---------------------------------------------------------------------------

def sections() -> dict[str, str]:
    out = {}
    for name in ("componentes.lua", "sinalizacao.lua", "mobiliario.lua"):
        text_ = (HERE / name).read_text(encoding="utf-8")
        parts = re.split(r"^--- ([a-z0-9-]+)\n", text_, flags=re.M)
        out.update({parts[i]: parts[i + 1].strip() + "\n" for i in range(1, len(parts), 2)})
    return out


def script_source(c: dict, body: str, figures: dict) -> str:
    out = [
        f"-- {c['component']}: scripted by tools/site.py from tools/site/lib.lua, componentes.lua",
        "-- and sinalizacao.lua; edit those, not this text.",
    ]
    if c.get("font"):
        out.append((HERE / "fonte.lua").read_text(encoding="utf-8").rstrip())
    if c.get("figures"):
        out.append("local FIGURAS = {")
        out += [f"  {name} = {lua_str(figures[name])}," for name in c["figures"]]
        out.append("}")
    out.append("local MAT = { " + ", ".join(f"{k} = {lua_str(v)}" for k, v in MAT_KEYS.items()) + " }")
    out.append((HERE / "lib.lua").read_text(encoding="utf-8").rstrip())
    out.append("")
    out += [p.lua() for p in c["params"] if p.script]
    out.append("")
    out.append(body.rstrip())
    return "\n".join(out) + "\n"


def source(c: dict, bodies: dict, figures: dict) -> dict:
    items = list(c.get("items", []))
    body = c.get("script_body", c["file"])
    if body in bodies:
        items.append({
            "name": "Script" if c.get("folder") == "signage" else "Pintura (script)",
            "material": c["material"],
            "in_plan": c.get("in_plan", True),
            "shape": {"Script": {"source": script_source(c, bodies[body], figures)}},
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
    for c in COMPONENTS:
        out = ROOT / "sources" / c.get("folder", "site")
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{c['file']}.json"
        path.write_text(json.dumps(source(c, bodies, figures), ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"{path.relative_to(ROOT).as_posix()}: {path.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
