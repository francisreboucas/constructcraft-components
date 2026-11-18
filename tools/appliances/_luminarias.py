"""Construção compartilhada pelas luminárias (pasta lighting).

Luminária de teto: a face do forro em z = 0, o corpo abaixo (z < 0); o que
fica acima do forro (caixa de um spot de embutir) sobe em z > 0. O make.py
coloca as luminárias de teto à altura do nível (3.0 m no projeto novo), por
isso `teto` desloca a base das câmeras de prévia para lá.
"""

from kit import *

DIFUSOR = "Difusor opalino"  # acrílico leitoso que deixa passar a luz
LED = "Fita de LED"  # chips e módulos de LED (o mesmo material do armário aéreo)
TETO = 3.0  # altura em que o make.py coloca uma luminária de teto
PAREDE = 2.10  # altura em que o make.py coloca uma arandela


def materiais(c):
    c.material(DIFUSOR, (250, 250, 245), "Plastic", "Glossy", 0.3)
    c.material(LED, (255, 244, 214), "Plastic", "Glossy", 0.3)


def teto(c, distancia, centro):
    """Câmeras de prévia numa luminária de teto, apontadas para z = `centro` (do forro, negativo abaixo dele).

    make.py põe a câmera a 1.9*tamanho + 0.35 m do alvo, em z = base + altura/2:
    um tamanho único acerta a `distancia` e a base compensa o alvo.
    """
    s = (distancia - 0.35) / 1.9
    c.preview_size = (s, s, s)
    c.preview_base = TETO + centro - s / 2


def anel(c, nome, r0, r1, z0, z1, mat, cx=0, cy=0, **kw):
    """Anel de revolução (eixo vertical em (cx, cy)) de raio r0 a r1 e altura z0 a z1."""
    c.rev(nome, "Front", rect(f"{p(cx)} + {p(r0)}", z0, f"{p(cx)} + {p(r1)}", z1), cy, cx, mat, **kw)
