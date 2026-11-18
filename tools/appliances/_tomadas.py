"""Tomadas de uso geral e específico: a mesma placa com um ou dois módulos NBR 14136."""

from kit import *
import _eletrica as el


def tomadas(nome, arquivo, device, potencia, amperes, tipos, cor_modulo="Branco", marca=None):
    """`tipos`: [(nome, descrição, largura, módulos)]; o primeiro dá os valores padrão."""
    c = Component(nome, "electrical", arquivo, "Electrical")
    L = c.param("Largura", 0.06)
    A = c.param("Altura", 0.1)
    c.mep = {"Device": {"device": device, "power": potencia}}
    c.connector("Eletroduto", "Power", 0, 0, f"{A} / 2", "Back")
    el.materiais(c)
    el.placa(c, L, A)
    cz = f"{A}/2"
    if any(t[3] > 1 for t in tipos):
        N = c.param("Modulos", 1, "Number")
        s2 = el.presente(f"{N} - 1")
        el.tomada(c, "Tomada 1", el.Mod(f"-{el.PASSO_COLUNA}*min(1, max(0, {N} - 1))", cz), amperes, cor_modulo, marca)
        # a segunda tomada encolhe para dentro da placa, ao lado do poço da primeira
        el.tomada(c, "Tomada 2", el.Mod(el.PASSO_COLUNA, cz, s2), amperes, cor_modulo, marca)
    else:
        el.tomada(c, "Tomada", el.Mod(0, cz), amperes, cor_modulo, marca)
    for i, (tn, desc, larg, mods) in enumerate(tipos):
        v = {}
        if i and larg != 0.06:
            v["Largura"] = larg
        if i and mods != 1:
            v["Modulos"] = mods
        c.type(tn, desc, **v)
    el.enquadrar(c, 0.30)
    return c
