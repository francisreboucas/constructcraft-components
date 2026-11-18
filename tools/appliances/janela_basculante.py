"""Janela basculante de alumínio: três básculas pivotadas no eixo horizontal central, ligadas
por uma haste de comando com alavanca; vidro mini boreal, baguetes, gaxetas e peitoril."""

from kit import *
from janela_comum import *

N = 3  # panes
FA = 0.03  # face width of the frame
GLASS_MB = "Vidro mini boreal"


def plan(c, *names):
    """Draw these pieces in plan."""
    for i in c.items:
        if i["name"] in names:
            i["in_plan"] = True


def build() -> Component:
    c = Component("Janela basculante", "windows", "janela-basculante", "Window")
    L = c.param("Largura", 0.6)
    H = c.param("Altura", 0.4)
    c.param("Peitoril", 1.7)
    A = opening_param(c, "AnguloAbertura", "Angle", 50)  # the panes' bottoms swing out, their tops in (up to about 60°)
    c.opening = {"width": "Largura", "height": "Altura", "sill": "Peitoril", "own_symbol": True}
    stone(c)
    c.material(GLASS_MB, (214, 226, 230), "Glass", "Matte", 0.45)
    x0, x1 = f"(-{L}/2)", f"({L}/2)"

    # --- coarse ----------------------------------------------------------------------
    c.box("Marco simplificado esquerdo", x0, -0.03, 0, FA, 0.06, H, ALU, COARSE, in_plan=True)
    c.box("Marco simplificado direito", f"{x1} - {FA}", -0.03, 0, FA, 0.06, H, ALU, COARSE, in_plan=True)
    c.box("Marco simplificado inferior", f"{x0} + {FA}", -0.03, 0, f"{L} - {2 * FA}", 0.06, FA, ALU, COARSE)
    c.box("Marco simplificado superior", f"{x0} + {FA}", -0.03, f"{H} - {FA}", f"{L} - {2 * FA}", 0.06, FA, ALU, COARSE)
    peitoril(c, L, -0.03, 0.03)

    # --- frame: plain jambs with a channel for the pivots; the head stops the panes' tops
    # outside, the sill their bottoms inside, as the panes turn bottom-out ------------
    jamb = [(0, -0.03), (FA, -0.03), (FA, -0.012), (0.026, -0.012), (0.026, 0.012), (FA, 0.012), (FA, 0.03), (0, 0.03)]
    head = [(0, -0.03), (FA, -0.03), (FA, -0.0145), (0.042, -0.0145), (0.042, -0.0125), (FA, -0.0125), (FA, 0.03), (0, 0.03)]
    sill = [(0, -0.03), (0.024, -0.03), (FA, -0.024), (FA, 0.0125), (0.042, 0.0125), (0.042, 0.0145), (FA, 0.0145), (FA, 0.03), (0, 0.03)]
    ring(c, "Marco", x0, x1, 0, H, jamb, ALU, sides="lr")
    ring(c, "Marco", x0, x1, 0, H, head, ALU, sides="t")
    ring(c, "Marco", x0, x1, 0, H, list(reversed(sill)), ALU, sides="b")
    plan(c, "Marco montante esquerdo", "Marco montante direito")

    # --- panes -------------------------------------------------------------------------
    hp = f"(({H} - {0.064 + (N - 1) * 0.002:g})/{N})"
    xp0, xp1 = f"({x0} + 0.033)", f"({x1} - 0.044)"  # the gap on the right holds the linkage
    s0, s1 = f"(-{hp}/2)", f"({hp}/2)"
    pins = []
    for k in range(N):
        n = f"Báscula {k + 1}"
        hz = f"(0.032 + {k}*({hp} + 0.002) + {hp}/2)"
        hinge = (0, hz)
        tilt_box(c, f"{n} simplificada", hinge, A, xp0, minus(xp1, xp0), s0, s1, -0.012, 0.012, GLASS_MB, COARSE)
        plan(c, f"{n} simplificada")
        tilt_ring(c, f"{n} perfil", hinge, A, xp0, xp1, s0, s1, 0, 0.018, -0.012, 0.012, ALU)
        tilt_ring(c, f"{n} aba do vidro", hinge, A, xp0, xp1, s0, s1, 0.018, 0.025, 0.008, 0.012, ALU)
        tilt_ring(c, f"{n} baguete", hinge, A, xp0, xp1, s0, s1, 0.018, 0.0245, -0.012, -0.008, ALU)
        tilt_ring(c, f"{n} gaxeta externa", hinge, A, xp0, xp1, s0, s1, 0.0205, 0.0255, 0.002, 0.008, RUBBER, FINE)
        tilt_ring(c, f"{n} gaxeta interna", hinge, A, xp0, xp1, s0, s1, 0.0205, 0.025, -0.008, -0.002, RUBBER, FINE)
        tilt_box(c, f"{n} vidro", hinge, A, f"{xp0} + 0.019", f"{minus(xp1, xp0)} - 0.038", f"{s0} + 0.019", f"{s1} - 0.019", -0.002, 0.002, GLASS_MB)
        plan(c, f"{n} vidro")
        if k:  # a flap outside the bottom rail laps over the pane below
            tilt_box(c, f"{n} aba de sobreposição", hinge, A, xp0, minus(xp1, xp0), f"{s0} - 0.012", f"{s0} + 0.016", 0.012, 0.0135, ALU)
        # pivots: pins from brackets in the jambs' channels into the pane's stiles
        for side, xa, xb, xs in (("esquerdo", f"{x0} + 0.026", f"{xp0} + 0.006", f"{x0} + 0.0262"),
                                 ("direito", f"{xp1} - 0.006", f"{x1} - 0.026", f"{x1} - 0.0302")):
            c.cyl_x(f"{n} pivô {side}", 0, hz, xa, 0.003, minus(xb, xa), "Inox escovado", FINE)
            c.box(f"{n} suporte do pivô {side}", xs, -0.009, f"{hz} - 0.014", 0.004, 0.018, 0.028, "Plástico preto", FINE)
        # lug on the right stile, pinned to the linkage bar
        tilt_box(c, f"{n} orelha da haste", hinge, A, xp1, 0.004, -0.011, 0.011, -0.022, 0.004, ALU, FINE)
        py, pz = tilt_pt(hinge, A, 0, -0.018)
        c.cyl_x(f"{n} rebite da haste", py, pz, f"{xp1} - 0.0005", 0.0028, 0.0105, "Inox escovado", FINE)
        pins.append((hinge, pz))

    # --- linkage: a flat bar pinned to every lug moves down as the panes open --------------
    py = f"(0.018*cos({A}))"
    pz0, pz1 = pins[0][1], pins[-1][1]
    c.box("Haste de comando", f"{xp1} + 0.0042", f"{py} - 0.005", f"({pz0}) - 0.016", 0.0048, 0.01, f"({pz1}) - ({pz0}) + 0.032", ALU)
    # lever on the bottom pane, rising into the room, with a grip
    hinge0 = pins[0][0]
    tilt_prof(c, "Alavanca de comando", hinge0, A, xp1, 0.004, [(-0.006, -0.012), (0.008, -0.012), (0.048, -0.042), (0.036, -0.046)], "Alumínio fundido")
    gy, gz = tilt_pt(hinge0, A, 0.043, -0.046)
    c.cyl_x("Manopla da alavanca", gy, gz, f"{xp1} - 0.014", 0.0065, 0.018, "Plástico preto")
    c.cyl_x("Ponteira da manopla", gy, gz, f"{xp1} - 0.0155", 0.005, 0.0015, "Plástico preto", FINE)

    # --- sealing, drainage and fixing ---------------------------------------------------
    box_ring(c, "Cordão de silicone externo", x0, x1, 0.012, H, 0, 0.004, -0.0315, -0.03, "Borracha cinza", FINE, "lrt")
    box_ring(c, "Cordão de silicone interno", x0, x1, 0.005, H, 0, 0.004, 0.03, 0.0315, "Borracha cinza", FINE, "lrt")
    for i, x in enumerate((f"{x0} + 0.07", f"{x1} - 0.095"), 1):
        c.box(f"Dreno {i}", x, -0.0302, 0.014, 0.025, 0.004, 0.005, ALU, FINE, void=True)
    n = 0
    for x in (f"{x0} + 0.011", f"{x1} - 0.011"):
        for z in (0.08, f"{H} - 0.08"):
            n += 1
            c.cyl_y(f"Tampa de parafuso {n}", x, z, 0.03, 0.005, 0.0012, "Plástico cinza claro", FINE)

    d_ = "Janela basculante de alumínio e vidro, três básculas, para banheiro ou área de serviço"
    c.type("Janela basculante 60 x 40", d_, Largura=0.6, Altura=0.4, Peitoril=1.7)
    c.type("Janela basculante 60 x 60", d_, Largura=0.6, Altura=0.6, Peitoril=1.5)
    c.type("Janela basculante 100 x 40", d_, Largura=1.0, Altura=0.4, Peitoril=1.7)
    c.preview_size = (0.6, 0.3, 0.6)
    c.preview_base = 1.6
    return c
