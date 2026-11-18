"""Porta de correr aparente de duas folhas (bipartida): folhas almofadadas penduradas em carrinhos
num trilho superior de alumínio, com testeira e bandô de madeira, guias de piso, fechadura bico de
papagaio entre as folhas, puxadores de barra e conchas embutidas."""

from _porta_correr_aparente import *
from _porta_correr_aparente import LC, OV, y


def build() -> Component:
    c = Component("Porta de correr dupla", "doors", "porta-correr-dupla", "Door")
    L = c.param("Largura", 1.4)
    H = c.param("Altura", 2.1)
    t = opening(c)  # each leaf slides outwards, over the wall, by t * Largura/2
    c.opening = {"width": "Largura", "height": "Altura", "own_symbol": True}
    c.preview_size = (2.4, 0.3, 2.2)

    frame(c, L, H)

    # Each leaf laps the opening by 6 cm at its side; they meet at x = 0 with a 3 mm gap.
    # Leaf-local a runs from the outer edge (a = 0) to the meeting edge (a = Lf); the right leaf is mirrored.
    Lf = f"({L}/2 + {e(OV - 0.0015)})"
    x_closed = f"(-{L}/2 - {e(OV)})"
    leaves = {}
    for side, mx in (("esquerda", False), ("direita", True)):
        fr0 = Fr(c, x_closed, 0, 0, mx)
        fr = Fr(c, f"({x_closed} - {t}*{L}/2)", 0, 0, mx)
        leaves[side] = fr
        names = ("montante externo", "montante de encontro")
        leaf(c, fr, f"Folha {side}", Lf, H, names=names)
        carriage(c, fr, f"Carrinho {side} 1", 0.12, H)
        carriage(c, fr, f"Carrinho {side} 2", f"{Lf} - 0.12", H)
        bar_pull(c, fr, f"Puxador {side} (frente)", f"{Lf} - 0.1", 1.05)
        cup_pull(c, fr, f"Puxador concha {side} (fundo)", f"{Lf} - 0.1", 1.05)
        symbols(c, fr, fr0, f"da folha {side}", Lf, -1)
        sg = -1 if mx else 1
        floor_guide(c, f"Guia de piso {side}", f"({sg}*({L}/2 + 0.02))")

    # The track spans both parked leaves; rubber stops at the ends of the travel.
    track(c, H, f"(-{L} - 0.1)", f"({L} + 0.1)", stops=(f"(-{L} + 0.007)", f"({L} - 0.032)"))

    # The hook lock in the right leaf's meeting edge; its strike on the left leaf's.
    fd, fe = leaves["direita"], leaves["esquerda"]
    hook_lock(c, fd, "Fechadura", Lf, -1, 1.0)
    fe.box("Contratesta", Lf, f"{Lf} + 0.0006", y(LC - 0.009), y(LC + 0.009), 0.9, 0.2, "Inox escovado", detail=FINE)
    fe.box("Furo do bico", f"{Lf} + 0.0006", f"{Lf} + 0.0008", y(LC - 0.005), y(LC + 0.005), 0.975, 0.05, "Plástico preto", detail=FINE)

    d = "Porta de correr aparente de duas folhas, trilho superior"
    c.type("Porta de correr dupla 140 x 210", d, Largura=1.4, Altura=2.1)
    c.type("Porta de correr dupla 160 x 210", d, Largura=1.6, Altura=2.1)
    c.type("Porta de correr dupla 200 x 210", d, Largura=2.0, Altura=2.1)
    return c
