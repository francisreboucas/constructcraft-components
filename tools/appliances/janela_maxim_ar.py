"""Janela maxim-ar de alumínio: folha projetante para fora sobre braços articulados."""

from kit import *
from janela_comum import *


def build() -> Component:
    c = Component("Janela maxim-ar de alumínio", "windows", "janela-maxim-ar", "Window")
    L = c.param("Largura", 0.6)
    H = c.param("Altura", 0.6)
    c.param("Peitoril", 1.5)
    A = opening_param(c, "AnguloAbertura", "Angle", 38)
    c.opening = {"width": "Largura", "height": "Altura", "sill": "Peitoril"}
    stone(c)
    x0, x1 = f"(-{L}/2)", f"({L}/2)"

    old_frame(c, L, H, 0.08, ALU)
    peitoril(c, L, -0.04, 0.04)

    # --- frame: a tube with the stop the sash closes against, on the room side ----
    section = [(0, -0.04), (0.018, -0.04), (0.018, 0.016), (0.04, 0.016), (0.04, 0.034), (0.037, 0.034), (0.037, 0.04), (0, 0.04)]
    ring(c, "Marco", x0, x1, 0, H, section, ALU)
    box_ring(c, "Gaxeta de vedação", x0, x1, 0, H, 0.022, 0.03, 0.0138, 0.016, RUBBER, FINE)
    c.profile("Pingadeira", "Side", [(-0.04, f"{H} - 0.003"), (-0.054, f"{H} - 0.013"), (-0.054, f"{H} - 0.015"), (-0.04, f"{H} - 0.008")],
              f"{x0} + 0.001", f"{L} - 0.002", ALU)

    # --- the sash: it hangs from two friction stays, its top sliding down as it opens
    d = f"(0.4*{H})"  # length of the stay arm = distance of its pivot on the sash from the top
    Hh = f"({H} - 0.02)"  # top of the closed sash
    hinge = (-0.01, f"({Hh} - 2*{d}*(1 - cos({A})))")
    xs0, xs1 = f"({x0} + 0.02)", f"({x1} - 0.02)"
    s0, s1 = f"(-({H} - 0.04))", 0
    # t is measured from the stays' plane (y = -0.01), positive to the exterior.
    tilt_box(c, "Folha simplificada", hinge, A, f"{x0} + 0.04", f"{L} - 0.08", f"{s0} + 0.02", -0.02, -0.016, -0.004, GLASS, COARSE)
    tilt_ring(c, "Folha perfil", hinge, A, xs0, xs1, s0, s1, 0, 0.02, -0.024, 0.02, ALU)
    tilt_ring(c, "Folha encosto do vidro", hinge, A, xs0, xs1, s0, s1, 0.02, 0.036, -0.004, 0.017, ALU)
    tilt_ring(c, "Folha baguete", hinge, A, xs0, xs1, s0, s1, 0.02, 0.035, -0.024, -0.016, ALU)
    tilt_ring(c, "Folha gaxeta externa", hinge, A, xs0, xs1, s0, s1, 0.03, 0.0365, -0.007, -0.004, RUBBER, FINE)
    tilt_ring(c, "Folha gaxeta interna", hinge, A, xs0, xs1, s0, s1, 0.03, 0.0355, -0.016, -0.013, RUBBER, FINE)
    tilt_box(c, "Vidro", hinge, A, f"{xs0} + 0.024", f"{L} - 0.088", f"{s0} + 0.024", -0.024, -0.013, -0.007, GLASS)

    # --- friction stays -----------------------------------------------------------
    py, pz = -0.01, f"({Hh} - 2*{d})"
    qy, qz = tilt_pt(hinge, A, f"(-{d})", 0)
    for side, xa in (("esquerdo", f"{x0} + 0.0183"), ("direito", f"{x1} - 0.0197")):
        c.profile(f"Braço articulado {side}", "Side", [(py - 0.006, pz), (py + 0.006, pz), (f"({qy}) + 0.006", qz), (f"({qy}) - 0.006", qz)],
                  xa, 0.0014, "Inox escovado")
        tilt_box(c, f"Sapata deslizante {side}", hinge, A, xa, 0.0014, -0.03, -0.002, -0.008, 0.008, "Plástico preto", FINE)
        c.cyl_x(f"Rebite do braço no marco {side}", py, pz, f"({xa}) - 0.0002", 0.004, 0.0018, "Inox escovado", FINE)
        c.cyl_x(f"Rebite do braço na folha {side}", qy, qz, f"({xa}) - 0.0002", 0.004, 0.0018, "Inox escovado", FINE)

    # --- handle: a lever on the bottom rail hooking a keeper on the frame ----------
    tilt_box(c, "Fecho base", hinge, A, -0.035, 0.07, f"{s0} + 0.0205", f"{s0} + 0.0345", -0.0275, -0.024, "Alumínio fundido")
    tilt_box(c, "Fecho eixo", hinge, A, -0.009, 0.018, f"{s0} + 0.0215", f"{s0} + 0.0335", -0.046, -0.0275, "Alumínio fundido")
    tilt_prof(c, "Fecho alavanca", hinge, A, -0.012, 0.1, [(f"{s0} + 0.008", -0.046), (f"{s0} + 0.008", -0.04), (f"{s0} + 0.034", -0.04), (f"{s0} + 0.034", -0.05), (f"{s0} + 0.012", -0.05)],
              "Alumínio fundido")
    c.box("Contra-fecho", -0.02, 0.04, 0.012, 0.04, 0.004, 0.022, "Alumínio fundido", FINE)

    # --- sealing and fixing -------------------------------------------------------
    box_ring(c, "Cordão de silicone externo", x0, x1, 0.012, H, 0, 0.004, -0.0415, -0.04, "Borracha cinza", FINE, "lrt")
    box_ring(c, "Cordão de silicone interno", x0, x1, 0.005, H, 0, 0.004, 0.04, 0.0415, "Borracha cinza", FINE, "lrt")
    n = 0
    for x in (f"{x0} + 0.011", f"{x1} - 0.011"):
        for z in (0.1, f"{H} - 0.1"):
            n += 1
            c.cyl_y(f"Tampa de parafuso {n}", x, z, 0.04, 0.005, 0.0012, "Plástico cinza claro", FINE)

    d_ = "Janela maxim-ar de uma folha, alumínio, para banheiros"
    c.type("Janela maxim-ar 60 x 60", d_, Largura=0.6, Altura=0.6)
    c.type("Janela maxim-ar 80 x 60", d_, Largura=0.8, Altura=0.6)
    c.type("Janela maxim-ar 100 x 60", d_, Largura=1.0, Altura=0.6)
    c.preview_size = (0.6, 0.3, 0.6)
    c.preview_base = 1.5
    return c
