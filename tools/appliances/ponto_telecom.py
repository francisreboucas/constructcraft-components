"""Ponto de telecomunicações: conector RJ45 e/ou tomada coaxial F em placa 4x2 ou 4x4."""

from kit import *
import _eletrica as el


def build():
    c = Component("Ponto de telecomunicações", "electrical", "ponto-telecom", "Electrical")
    L = c.param("Largura", 0.06)
    A = c.param("Altura", 0.1)
    RJ = c.param("RJ45", 1, "Number")
    TV = c.param("TV", 0, "Number")
    el.materiais(c)
    el.placa(c, L, A)
    tem_rj, tem_tv = f"min(1, max(0, {RJ}))", f"min(1, max(0, {TV}))"
    # sozinho, o módulo fica no centro; com os dois, RJ45 à esquerda e TV à direita.
    # O módulo ausente encolhe para dentro da placa na sua coluna, fora da cavidade do outro.
    el.rj45(c, "RJ45", el.Mod(f"-{el.PASSO_COLUNA}*(1 - {tem_rj}*(1 - {tem_tv}))", f"{A}/2", el.presente(RJ)))
    el.coaxial(c, "TV", el.Mod(f"{el.PASSO_COLUNA}*(1 - {tem_tv}*(1 - {tem_rj}))", f"{A}/2", el.presente(TV)))
    c.type("Ponto de dados RJ45", "Tomada de rede Cat6 em caixa 4x2")
    c.type("Ponto de TV", "Tomada coaxial para antena/TV a cabo", RJ45=0, TV=1)
    c.type("Ponto dados + TV 4x4", "Tomada RJ45 e coaxial em caixa 4x4", Largura=0.1, TV=1)
    el.enquadrar(c, 0.30)
    return c
