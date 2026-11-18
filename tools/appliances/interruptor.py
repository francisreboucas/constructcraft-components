"""Interruptor de embutir: 1 a 3 teclas basculantes; em 4x2 as teclas ficam deitadas e empilhadas, em 4x4 em pé, lado a lado."""

from kit import *
import _eletrica as el


def build():
    c = Component("Interruptor de embutir", "electrical", "interruptor", "Electrical")
    L = c.param("Largura", 0.06)
    A = c.param("Altura", 0.1)
    N = c.param("Teclas", 1, "Number")
    PAR = c.param("Paralelo", 0, "Number")
    c.mep = {"Device": {"device": "Switch", "power": 0}}
    c.connector("Eletroduto", "Lighting", 0, 0, f"{A} / 2", "Back")
    el.materiais(c)
    el.placa(c, L, A)

    h = f"min(1, max(0, ({L} - 0.08)*1000))"  # 1 na placa 4x4 (teclas em pé), 0 na 4x2 (teclas deitadas)
    nh = f"({N}*(1 - {h}))"
    nv = f"({N}*{h})"
    s_ind = el.presente(f"1 - {PAR}")  # o interruptor paralelo não tem posição "ligado" marcada
    for k in (1, 2, 3):
        # deitadas: empilhadas de cima para baixo, centradas na altura
        m = el.Mod(0, f"{A}/2 + (({nh} + 1)/2 - {k})*{el.PASSO_LINHA}", el.presente(f"{nh} - {k - 1}"))
        el.tecla_horizontal(c, f"Tecla {k}", m, s_ind=s_ind)
        # em pé: lado a lado da esquerda para a direita
        m = el.Mod(f"({k} - ({nv} + 1)/2)*{el.PASSO_LINHA}", f"{A}/2", el.presente(f"{nv} - {k - 1}"))
        el.tecla_vertical(c, f"Tecla em pé {k}", m, s_ind=s_ind)
    # mecanismo atrás da parede, do tamanho do conjunto de teclas
    c.box("Corpo do mecanismo", f"-0.0195 - {h}*({N} - 1)*{el.PASSO_LINHA / 2}", 0, f"{A}/2 - 0.0105 - (1 - {h})*({N} - 1)*{el.PASSO_LINHA / 2} - {h}*0.009",
          f"0.039 + {h}*({N} - 1)*{el.PASSO_LINHA}", 0.026, f"0.021 + (1 - {h})*({N} - 1)*{el.PASSO_LINHA} + {h}*0.018", el.SUPORTE)

    c.type("Interruptor simples 1 tecla", "Interruptor simples 10 A")
    c.type("Interruptor simples 2 teclas", "Interruptor simples 10 A, 2 seções", Teclas=2)
    c.type("Interruptor paralelo 1 tecla", "Interruptor paralelo (three-way) 10 A", Paralelo=1)
    c.type("Interruptor 3 teclas 4x4", "Interruptor simples 10 A, 3 seções", Largura=0.1, Teclas=3)
    el.enquadrar(c, 1.10)
    return c
