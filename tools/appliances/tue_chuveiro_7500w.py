"""Ponto de chuveiro elétrico 7500 W: saída de cabo com condutores de 6 mm² e conector cerâmico maior."""

from _eletrica import ponto_chuveiro


def build():
    return ponto_chuveiro("Ponto de chuveiro elétrico 7500 W", "tue-chuveiro-7500w", 7500,
                          "Ponto para chuveiro elétrico 220 V; circuito exclusivo", 0.0026, 0.028)
