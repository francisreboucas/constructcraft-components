"""Porta de abrir de uma folha: batente de madeira com rebaixo, guarnições, folha almofadada, dobradiças e fechadura."""

from doorkit import *


def build() -> Component:
    c = Component("Porta de abrir", "doors", "porta-abrir", "Door")
    L = c.param("Largura", 0.8)
    H = c.param("Altura", 2.1)
    A = opening_param(c, "AnguloAbertura", 75)
    c.opening = {"width": "Largura", "height": "Altura"}
    c.preview_size = (0.9, 0.3, 2.1)
    wood = "Madeira"

    wood_frame(c, L, H, wood)

    # The leaf: hinged on the -x jamb, flush with the +y face, opening to +y.
    fr = Fr(c, f"-{L}/2 + 0.037", f"{WT}/2 + 0.006", A)
    w = f"({L} - 0.075)"
    nf, nb = -0.006, -0.041
    z1 = f"({H} - 0.038)"
    fr.box("Folha simplificada", 0.002, w, nb, nf, 0, f"{H} - 0.055", wood, detail=COARSE)
    panel_leaf(fr, "Folha", 0.002, w, nb, nf, 0.008, z1, [(0.88, 0.14), (1.5, 0.09)], wood)
    butt_hinges(fr, "Dobradiça", [0.22, f"({H}/2 - 0.045)", f"({H} - 0.34)"])
    lever_set(fr, "Maçaneta", s(w, -0.055), nf, nb, 1.0)
    mortise_lock(fr, "Fechadura", w, (nf + nb) / 2, 1.0, s(w, 0.003))

    for name, desc, width in (
        ("Porta de abrir 60 x 210", "Porta de giro de uma folha, batente de madeira", 0.6),
        ("Porta de abrir 70 x 210", "Porta de giro de uma folha, batente de madeira", 0.7),
        ("Porta de abrir 80 x 210", "Porta de giro de uma folha, batente de madeira", 0.8),
        ("Porta de abrir 90 x 210", "Porta de giro de uma folha, batente de madeira", 0.9),
    ):
        c.type(name, desc, Largura=width, Altura=2.1)
    return c
