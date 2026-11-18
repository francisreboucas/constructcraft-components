"""Tomada de uso específico 3500 VA: 2P+T 20 A com módulo vermelho (circuito exclusivo de 220 V)."""

from _tomadas import tomadas


def build():
    return tomadas("Tomada de uso específico 3500 VA", "tue-3500va", "DedicatedOutlet", 3500, 20, [
        ("TUE 3500 VA", "Forno elétrico, torneira elétrica, ar-condicionado 24000 BTU/h", 0.06, 1),
    ], cor_modulo="Plástico vermelho")
