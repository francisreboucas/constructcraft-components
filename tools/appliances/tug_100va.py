"""Tomada de uso geral 100 VA: 2P+T 10 A (NBR 14136) em placa 4x2 ou dupla em 4x4."""

from _tomadas import tomadas


def build():
    return tomadas("Tomada de uso geral 100 VA", "tug-100va", "Outlet", 100, 10, [
        ("TUG 100 VA 4x2", "Tomada 2P+T 10 A em caixa 4x2 (NBR 14136)", 0.06, 1),
        ("TUG 100 VA 4x4 dupla", "Duas tomadas 2P+T 10 A em caixa 4x4", 0.1, 2),
    ])
