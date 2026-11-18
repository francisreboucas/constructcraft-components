"""Porta de correr aparente de uma folha: folha almofadada pendurada em carrinhos num trilho superior
de alumínio, com testeira e bandô de madeira, guia de piso, batedor de encosto, fechadura bico de
papagaio, puxador de barra e concha embutida."""

from _porta_correr_aparente import *
from _porta_correr_aparente import LC, LF, OV, y


def build() -> Component:
    c = Component("Porta de correr", "doors", "porta-correr", "Door")
    L = c.param("Largura", 0.8)
    H = c.param("Altura", 2.1)
    t = opening(c)  # the leaf slides to +x, over the wall, by t * Largura
    c.opening = {"width": "Largura", "height": "Altura", "own_symbol": True}
    c.preview_size = (1.7, 0.3, 2.2)

    frame(c, L, H)

    # The leaf laps the opening by 6 cm on each side; closed, its leading edge (a = 0) meets the batedor.
    Lf = f"({L} + {e(2 * OV)})"
    x_closed = f"(-{L}/2 - {e(OV)})"
    fr0 = Fr(c, x_closed, 0, 0)
    fr = Fr(c, f"({x_closed} + {t}*{L})", 0, 0)
    leaf(c, fr, "Folha", Lf, H, names=("montante da fechadura", "montante traseiro"))
    carriage(c, fr, "Carrinho 1", 0.12, H)
    carriage(c, fr, "Carrinho 2", f"{Lf} - 0.12", H)
    # The track runs from beside the batedor to past the open leaf; rubber stops at both ends of the travel.
    track(c, H, f"(-{L}/2 - 0.1)", f"(1.5*{L} + 0.1)", stops=(f"(-{L}/2 + 0.007)", f"(1.5*{L} - 0.032)"))
    floor_guide(c, "Guia de piso", f"({L}/2 + 0.02)")

    # --- hardware on the leading edge ------------------------------------------------------
    bar_pull(c, fr, "Puxador (frente)", 0.1, 1.05)
    cup_pull(c, fr, "Puxador concha (fundo)", 0.1, 1.05)
    hook_lock(c, fr, "Fechadura", 0, 1, 1.0)

    # --- the batedor the leaf closes against: a wooden post on the wall, bumpers and the lock's strike
    xb = f"(-{L}/2 - 0.062)"  # its face
    c.box("Batedor de encosto", f"{xb} - 0.03", y(0), 0, 0.03, LF, f"{H} + 0.06", "Madeira", in_plan=True)
    for k, z in enumerate((0.3, f"{H} - 0.3")):
        c.box(f"Amortecedor do batedor {k + 1}", xb, y(LC - 0.008), z, 0.0015, 0.016, 0.04, "Borracha", detail=FINE)
    c.box("Contratesta", xb, y(LC - 0.009), 0.9, 0.0006, 0.018, 0.2, "Inox escovado", detail=FINE)
    c.box("Furo do bico", f"{xb} + 0.0006", y(LC - 0.005), 0.975, 0.0002, 0.01, 0.05, "Plástico preto", detail=FINE)

    symbols(c, fr, fr0, "da folha", Lf, 1)

    d = "Porta de correr aparente de uma folha"
    c.type("Porta de correr 70 x 210", d, Largura=0.7, Altura=2.1)
    c.type("Porta de correr 80 x 210", d, Largura=0.8, Altura=2.1)
    c.type("Porta de correr 90 x 210", d, Largura=0.9, Altura=2.1)
    return c
