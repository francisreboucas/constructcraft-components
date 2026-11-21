"""Pessoa em pé: a generic human figure for scale."""

from kit import Component
from _pessoa import add_figure, declare

MATERIALS = {'skin': 'Pele morena', 'hair': 'Cabelo preto', 'top': 'Tecido branco', 'bottom': 'Jeans', 'shoes': 'Couro preto'}


def build():
    c = Component("Pessoa em pé", "people", "pessoa-em-pe", "Generic")
    declare(c, MATERIALS)
    c.type("Pessoa em pé 1,75 m", "Figura humana genérica em pé para escala, 1,75 m: camiseta, calça jeans e tênis (a frente para -Y, a origem no chão entre os pés)")
    c.preview_size = (0.5, 0.3, 1.75)
    add_figure(c, MATERIALS, **{'H': 1.75, 'pose': 'stand', 'sleeves': 'short', 'hair': 'short'})
    return c
