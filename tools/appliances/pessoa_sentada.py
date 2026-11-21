"""Pessoa sentada: a generic human figure for scale."""

from kit import Component
from _pessoa import add_figure, declare

MATERIALS = {'skin': 'Pele clara', 'hair': 'Cabelo grisalho', 'top': 'Tecido verde-oliva', 'bottom': 'Tecido cinza-chumbo', 'shoes': 'Couro preto'}


def build():
    c = Component("Pessoa sentada", "people", "pessoa-sentada", "Generic")
    declare(c, MATERIALS)
    c.type("Pessoa sentada 1,70 m", "Figura humana genérica sentada, para colocar em cadeiras e sofás com assento a 45 cm: a origem fica no chão sob o quadril, que fica 7 cm atrás dela; os pés vão 45 cm à frente (a frente para -Y)")
    c.preview_size = (0.5, 0.7, 1.3)
    add_figure(c, MATERIALS, **{'H': 1.7, 'pose': 'sit', 'sleeves': 'short', 'hair': 'short'})
    return c
