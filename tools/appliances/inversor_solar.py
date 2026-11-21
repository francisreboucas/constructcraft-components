"""Inversor solar: a wall string inverter for a grid-tied PV system, with its DC string box.

Wall device: the wall is y = 0, the front -Y; the instance parameter Elevacao is the height of its base.
"""

from kit import *


def build():
    c = Component("Inversor solar", "electrical", "inversor-solar", "Electrical")
    E = c.param("Elevacao", 1.2, "Length", True)
    c.type("Inversor solar 5 kW", "Inversor fotovoltaico monofásico de 5 kW conectado à rede, com dissipador de aletas, visor e "
           "chave seccionadora CC, e string box com DPS e fusíveis ao lado; instalar à sombra, com 30 cm livres em volta")
    c.material("Plástico vermelho segurança", (196, 40, 36), "Plastic", "Satin")
    c.preview_size = (0.8, 0.25, 0.7)
    c.preview_base = 1.0

    def z(d):
        return f"{E} + {d}"

    w, d, h = 0.42, 0.17, 0.5
    c.box("Inversor simplificado", -w / 2, -d, E, w, d, h, "Aço pintado branco", detail=COARSE, in_plan=True)
    c.box("Suporte de parede", -w / 2 + 0.04, -0.015, z(0.06), w - 0.08, 0.015, h - 0.12, "Aço galvanizado", detail=FINE)
    c.profile("Corpo", "Front", rrect(-w / 2, E, w / 2, z(h), 0.02), -d, d - 0.03, "Aço pintado branco", in_plan=True)
    for k in range(9):  # heat-sink fins on the back half of each side
        y = -0.03 - 0.012 * k
        for s in (-1, 1):
            c.box(f"Aleta {'esquerda' if s < 0 else 'direita'} {k + 1}", (w / 2 if s > 0 else -w / 2 - 0.012), y, z(0.04), 0.012, 0.003,
                  h - 0.08, "Alumínio anodizado", detail=FINE)
    c.profile("Painel frontal", "Front", rrect(-w / 2 + 0.03, z(0.12), w / 2 - 0.03, z(h - 0.04), 0.015), f"-{d} - 0.003", 0.003,
              "Plástico cinza claro")
    c.box("Visor", -0.06, f"-{d} - 0.0045", z(h - 0.14), 0.12, 0.002, 0.06, "Visor LCD")
    for k, x in enumerate((-0.03, 0.0, 0.03)):
        c.cyl_y(f"LED {k + 1}", x, z(h - 0.18), f"-{d} - 0.005", 0.004, 0.002, ("Plástico verde", "Plástico vermelho", "Visor LED")[k],
                detail=FINE)
    # Bottom: DC switch, cable glands, conduits down.
    c.box("Base de conexões", -w / 2 + 0.02, f"-{d} + 0.02", z(-0.035), w - 0.04, d - 0.05, 0.035, "Plástico cinza")
    c.cyl("Chave CC - base", 0.12, f"-{d}/2", z(-0.06), 0.03, 0.025, "Plástico preto")
    c.box("Chave CC - manopla", 0.1, f"-{d}/2 - 0.007", z(-0.085), 0.04, 0.014, 0.03, "Plástico vermelho segurança")
    for k, x in enumerate((-0.12, -0.06, 0.0, 0.05)):
        c.cyl(f"Prensa-cabo {k + 1}", x, f"-{d}/2", z(-0.055), 0.009, 0.02, "Plástico preto", detail=FINE)
    c.cyl("Eletroduto CA", -0.12, -0.04, f"{E} - 0.6", 0.0125, 0.565, "Plástico cinza claro")
    c.cyl("Eletroduto CC", -0.06, -0.04, f"{E} - 0.6", 0.0125, 0.565, "Plástico cinza claro")
    # String box at the right: a grey enclosure with a transparent cover.
    xs = w / 2 + 0.08
    c.box("String box", xs, -0.12, z(0.1), 0.22, 0.12, 0.3, "Plástico cinza claro")
    c.box("String box - tampa", xs + 0.015, -0.125, z(0.115), 0.19, 0.005, 0.27, "Plástico translúcido", detail=FINE)
    for k in range(4):
        c.box(f"String box - dispositivo {k + 1}", xs + 0.03 + 0.04 * k, -0.115, z(0.22), 0.032, 0.03, 0.08, "Branco", detail=FINE)
    c.cyl("Eletroduto da string box", xs + 0.11, -0.06, f"{E} + 0.4", 0.0125, 0.9, "Plástico cinza claro")
    return c
