"""Janela fixa de alumínio: marco com rebaixo, vidro encaixilhado com baguetes e gaxetas."""

from kit import *
from janela_comum import *


def build() -> Component:
    c = Component("Janela fixa", "windows", "janela-fixa", "Window")
    L = c.param("Largura", 0.6)
    H = c.param("Altura", 0.6)
    c.param("Peitoril", 1.5)
    c.opening = {"width": "Largura", "height": "Altura", "sill": "Peitoril"}
    stone(c)
    x0, x1 = f"(-{L}/2)", f"({L}/2)"

    # --- coarse: the frame as four bars -----------------------------------------
    old_frame(c, L, H, 0.08, ALU)

    peitoril(c, L, -0.04, 0.04)

    # --- frame: a tube with the fixed glazing stop outside ----------------------
    section = [
        (0, -0.04), (0.04, -0.04), (0.04, -0.034), (0.037, -0.034), (0.037, -0.03), (0.04, -0.03),
        (0.04, -0.007), (0.022, -0.007), (0.022, 0.034), (0.019, 0.034), (0.019, 0.04), (0, 0.04),
    ]
    ring(c, "Marco", x0, x1, 0, H, section, ALU)
    box_ring(c, "Baguete", x0, x1, 0, H, 0.022, 0.039, 0.007, 0.022, ALU)
    box_ring(c, "Gaxeta externa", x0, x1, 0, H, 0.034, 0.0405, -0.007, -0.003, RUBBER, FINE)
    box_ring(c, "Gaxeta interna", x0, x1, 0, H, 0.034, 0.0395, 0.003, 0.007, RUBBER, FINE)
    c.box("Vidro", f"{x0} + 0.026", -0.003, 0.026, f"{L} - 0.052", 0.006, f"{H} - 0.052", GLASS, ALL)
    for i, x in enumerate((f"{x0} + 0.1", f"{x1} - 0.15"), 1):
        c.box(f"Calço do vidro {i}", x, -0.004, 0.0221, 0.05, 0.008, 0.0039, "Plástico preto", FINE)

    # --- sealing and fixing -------------------------------------------------------
    box_ring(c, "Cordão de silicone externo", x0, x1, 0.012, H, 0, 0.004, -0.0415, -0.04, "Borracha cinza", FINE, "lrt")
    box_ring(c, "Cordão de silicone interno", x0, x1, 0.005, H, 0, 0.004, 0.04, 0.0415, "Borracha cinza", FINE, "lrt")
    for i, x in enumerate((f"{x0} + 0.12", f"{x1} - 0.145"), 1):
        c.box(f"Dreno {i}", x, -0.045, 0.016, 0.025, 0.012, 0.005, ALU, FINE, void=True)
    n = 0
    for side, x in (("esquerdo", f"{x0} + 0.011"), ("direito", f"{x1} - 0.011")):
        for z in (0.12, f"{H}/2", f"{H} - 0.12"):
            n += 1
            c.cyl_y(f"Tampa de parafuso {n}", x, z, 0.04, 0.005, 0.0012, "Plástico cinza claro", FINE)

    c.type("Janela fixa 60 x 60", "Janela fixa de alumínio e vidro, sem abertura", Largura=0.6, Altura=0.6, Peitoril=1.5)
    c.type("Janela fixa 100 x 100", "Janela fixa de alumínio e vidro, sem abertura", Largura=1.0, Altura=1.0, Peitoril=1.1)
    c.type("Janela fixa 150 x 100", "Janela fixa de alumínio e vidro, sem abertura", Largura=1.5, Altura=1.0, Peitoril=1.1)
    c.preview_size = (0.6, 0.3, 0.6)
    c.preview_base = 1.5
    return c
