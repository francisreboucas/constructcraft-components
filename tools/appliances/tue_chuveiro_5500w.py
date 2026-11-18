"""Ponto de chuveiro elétrico 5500 W: saída de cabo com condutores de 4 mm² e conector cerâmico."""

from _eletrica import ponto_chuveiro


def build():
    return ponto_chuveiro("Ponto de chuveiro elétrico 5500 W", "tue-chuveiro-5500w", 5500,
                          "Ponto para chuveiro elétrico 220 V; circuito exclusivo", 0.0021, 0.024)
