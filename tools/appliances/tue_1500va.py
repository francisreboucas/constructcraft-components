"""Tomada de uso específico 1500 VA: 2P+T 20 A com filete vermelho de circuito exclusivo."""

from _tomadas import tomadas


def build():
    return tomadas("Tomada de uso específico 1500 VA", "tue-1500va", "DedicatedOutlet", 1500, 20, [
        ("TUE 1500 VA", "Micro-ondas, ar-condicionado até 12000 BTU/h, máquina de lavar", 0.06, 1),
    ], marca="Plástico vermelho")
