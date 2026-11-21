"""Pessoa em pé de vestido: a generic human figure for scale."""

from kit import Component
from _pessoa import add_figure, declare

MATERIALS = {'skin': 'Pele negra', 'hair': 'Cabelo preto', 'top': 'Tecido mostarda', 'bottom': 'Tecido mostarda', 'shoes': 'Couro preto'}


def build():
    c = Component("Pessoa em pé de vestido", "people", "pessoa-em-pe-vestido", "Generic")
    declare(c, MATERIALS)
    c.type("Pessoa em pé de vestido 1,65 m", "Figura humana genérica em pé para escala, 1,65 m, de vestido e cabelo longo (a frente para -Y, a origem no chão entre os pés)")
    c.preview_size = (0.5, 0.3, 1.65)
    add_figure(c, MATERIALS, **{'H': 1.65, 'pose': 'stand', 'female': True, 'skirt': True, 'sleeves': 'short', 'hair': 'long'})
    return c
