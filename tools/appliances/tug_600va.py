"""Tomada de uso geral 600 VA: 2P+T 20 A (furos de 4,8 mm) em placa 4x2 ou dupla em 4x4."""

from _tomadas import tomadas


def build():
    return tomadas("Tomada de uso geral 600 VA", "tug-600va", "Outlet", 600, 20, [
        ("TUG 600 VA 4x2", "Tomada 2P+T 20 A para cozinha e área de serviço (NBR 5410: 3 primeiras a 600 VA)", 0.06, 1),
        ("TUG 600 VA 4x4 dupla", "Duas tomadas 2P+T 20 A em caixa 4x4", 0.1, 2),
    ])
