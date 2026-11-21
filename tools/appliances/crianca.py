"""Criança: a generic human figure for scale."""

from kit import Component
from _pessoa import add_figure, declare

MATERIALS = {'skin': 'Pele negra', 'hair': 'Cabelo preto', 'top': 'Tecido mostarda', 'bottom': 'Tecido azul-marinho', 'shoes': 'Couro preto'}


def build():
    c = Component("Criança", "people", "crianca", "Generic")
    declare(c, MATERIALS)
    c.type("Criança 1,15 m", "Figura genérica de criança de cerca de 6 anos em pé, 1,15 m, para escala de playgrounds, escolas e áreas infantis")
    c.preview_size = (0.35, 0.25, 1.15)
    add_figure(c, MATERIALS, **{'H': 1.15, 'pose': 'stand', 'child': True, 'sleeves': 'short', 'hair': 'short'})
    return c
