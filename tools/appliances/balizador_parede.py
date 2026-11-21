"""Balizador de parede: a recessed step and path light with a louvred face that throws the light down onto the floor.

Recessed wall device: the wall face is y = 0, the box inside the wall (y > 0), the face plate in front; the instance
parameter Elevacao is the height of its centre (0,30 m along stairs and paths). No device data (a wall light would be
lifted to 2,10 m); the power is in the description.
"""

from kit import *
import _luminarias as lu


def build():
    c = Component("Balizador de parede", "lighting", "balizador-parede", "Lighting")
    W = c.param("Largura", 0.12)
    H = c.param("Altura", 0.08)
    E = c.param("Elevacao", 0.3, "Length", True)
    lu.materiais(c)
    desc = "Balizador LED de embutir na parede com aletas que direcionam a luz para o chão, alumínio pintado, 3 W, IP65; para escadas e caminhos"
    c.type("Balizador de parede retangular", desc)
    c.type("Balizador de parede quadrado", desc, Largura=0.1, Altura=0.1)
    c.preview_size = (0.2, 0.15, 0.15)
    c.preview_base = 0.22

    zb = f"{E} - {H}/2"
    c.box("Balizador simplificado", f"-{W}/2", -0.006, zb, W, 0.066, H, "Aço pintado preto", detail=COARSE, in_plan=True)
    c.box("Caixa de embutir", f"-{W}/2 + 0.005", 0, f"{zb} + 0.005", f"{W} - 0.01", 0.06, f"{H} - 0.01", "Plástico preto")
    c.box("Espelho", f"-{W}/2", -0.006, zb, W, 0.006, H, "Aço pintado preto", in_plan=True)
    c.box("Difusor", f"-{W}/2 + 0.012", -0.0065, f"{zb} + 0.01", f"{W} - 0.024", 0.002, f"{H}*0.45", lu.DIFUSOR)
    for k in range(3):
        z = f"{zb} + 0.012 + {k}*{H}*0.15"
        c.profile(f"Aleta {k + 1}", "Side", [(-0.006, f"{z} + 0.012"), (-0.006, f"{z} + 0.016"), (-0.02, f"{z} + 0.008"), (-0.02, f"{z} + 0.004")],
                  f"-{W}/2 + 0.012", f"{W} - 0.024", "Aço pintado preto")
    return c
