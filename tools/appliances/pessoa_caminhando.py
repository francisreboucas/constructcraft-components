"""Pessoa caminhando: a generic human figure for scale."""

from kit import Component
from _pessoa import add_figure, declare

MATERIALS = {'skin': 'Pele clara', 'hair': 'Cabelo castanho', 'top': 'Tecido vermelho', 'bottom': 'Tecido azul-marinho', 'shoes': 'Couro preto'}


def build():
    c = Component("Pessoa caminhando", "people", "pessoa-caminhando", "Generic")
    declare(c, MATERIALS)
    c.type("Pessoa caminhando 1,72 m", "Figura humana genérica caminhando, para escala e circulação, 1,72 m: camisa de manga longa e calça (a frente para -Y)")
    c.preview_size = (0.5, 0.7, 1.72)
    add_figure(c, MATERIALS, **{'H': 1.72, 'pose': 'walk', 'female': True, 'sleeves': 'long', 'hair': 'bun'})
    return c
