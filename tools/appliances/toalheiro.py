"""Toalheiro: barra de parede em latão cromado sobre duas canoplas, ou argola, com a toalha pendurada."""

from _banheiro import *

CHROME, STEEL = "Cromado", "Inox escovado"
TOWEL, STRIPE = "Toalha de algodão", "Tecido cinza"
HIDE = 0.01  # scale of the variant a type does not have (EPS makes the blends too thin for the engine)


def flange(g, name, x, z, in_plan=True):
    """A round wall rose (y = 0 is the wall) with a rounded front edge, about the axis along Y at (x, z)."""
    g.rev(name, "Plan", [(x, -0.011), (add(x, 0.019), -0.011, 0.008), (add(x, 0.026), -0.004), (add(x, 0.026), 0), (x, 0)],
          z, x, CHROME, in_plan=in_plan)


def build():
    c = Component("Toalheiro", "furniture", "toalheiro", "Furniture")
    W = c.param("Largura", 0.6)
    D = c.param("Profundidade", 0.075)
    K = c.param("Argola", 0, "Number")
    E = c.param("Elevacao", 1.1, "Length", True)
    c.material(TOWEL, (236, 232, 222), "Generic", "Matte")
    c.material(STRIPE, (150, 152, 156), "Generic", "Matte")
    desc = "Toalheiro de barra de parede, latão cromado, fixação oculta"
    c.type("Toalheiro barra 60 cm", desc, Largura=0.6)
    c.type("Toalheiro argola", "Toalheiro de argola de parede para toalha de rosto, latão cromado", Largura=0.2, Argola=1)
    c.type("Toalheiro barra 40 cm", desc, Largura=0.4)

    yb = f"(0.0135 - {D})"  # axis of the bar (or of the ring's head), 13.5 mm behind the front
    xp = f"({W}/2 - 0.026)"  # axis of the posts
    kb = f"min(1, max({HIDE}, 1 - {K}))"
    kr = f"min(1, max({HIDE}, {K}))"
    gb = Grp(c, kb, (0, -0.006, E))  # the bar: hides in the ring's rose
    gr = Grp(c, kr, (0, yb, E))  # the ring: hides in the bar

    # --- bar: coarse stand-ins ---
    gb.box("Barra simplificada", f"-{xp} - 0.022", f"{yb} - 0.0135", f"{E} - 0.0135", f"2*{xp} + 0.044", 0.027, 0.027, CHROME, detail=COARSE, in_plan=True)
    for nm, s in (("esquerdo", "-"), ("direito", "")):
        gb.box(f"Suporte {nm} simplificado", f"{s}{xp} - 0.026", yb, f"{E} - 0.026", 0.052, f"-{yb}", 0.052, CHROME, detail=COARSE, in_plan=True)

    # --- bar: two posts on roses and the tube ---
    for nm, s in (("esquerdo", -1), ("direito", 1)):
        x = f"-{xp}" if s < 0 else xp
        flange(gb, f"Canopla {nm}", x, E)
        gb.cyl_y(f"Haste {nm}", x, E, yb, 0.0085, f"-0.011 - {yb}", CHROME, in_plan=True)
        gb.cyl_y(f"Anel da haste {nm}", x, E, f"{yb} + 0.012", 0.0105, 0.005, CHROME, detail=FINE)
        gb.cyl_x(f"Cabeça {nm}", yb, E, f"{x} - 0.016", 0.0135, 0.032, CHROME, in_plan=True)
        big, small = circ(yb, E, 0.0135), circ(yb, E, 0.0075)
        if s < 0:
            gb.blend(f"Tampa da cabeça {nm}", "Side", small, big, f"{x} - 0.022", 0.006, CHROME)
        else:
            gb.blend(f"Tampa da cabeça {nm}", "Side", big, small, f"{x} + 0.016", 0.006, CHROME)
        gb.cyl(f"Parafuso de fixação {nm}", x, yb, f"{E} - 0.0148", 0.0025, 0.0016, STEEL, detail=FINE)
        gb.cyl(f"Sextavado do parafuso {nm}", x, yb, f"{E} - 0.0152", 0.0011, 0.0005, "Aço pintado preto", detail=FINE)
    gb.cyl_x("Barra", yb, E, f"-{xp}", 0.0095, f"2*{xp}", CHROME, in_plan=True)

    # --- bar: a bath towel folded in three, hanging over the tube ---
    tw = f"(0.55*{W})"
    rr = 0.0155  # the towel's mid-surface round the tube
    sec = [(-0.005, f"-{tw}/2"), (0.005, f"-{tw}/2"), (0.005, f"{tw}/2"), (-0.005, f"{tw}/2")]
    gb.sweep("Toalha", "Side", [
        (f"{yb} - {rr + 0.007}", f"{E} - 0.46"), (f"{yb} - {rr}", f"{E} - 0.36"), (f"{yb} - {rr}", E, -rr),
        (f"{yb} + {rr}", E), (f"{yb} + {rr}", f"{E} - 0.3"), (f"{yb} + {rr + 0.004}", f"{E} - 0.41"),
    ], 0, sec, TOWEL, detail=FINE)
    yt = f"{yb} - {rr + 0.0062}"
    gb.box("Barrado da toalha", f"-{tw}/2", yt, f"{E} - 0.33", tw, 0.0013, 0.035, STRIPE, detail=FINE)
    gb.box("Friso do barrado da toalha", f"-{tw}/2", yt, f"{E} - 0.286", tw, 0.0013, 0.006, STRIPE, detail=FINE)

    # --- ring: rose, arm, head with a pivot and the ring hanging from it ---
    R = f"({W}/2 - 0.006)"  # radius of the ring's axis
    zc = f"({E} - 0.036 - {R})"  # center of the ring
    gr.box("Suporte da argola simplificado", -0.026, yb, f"{E} - 0.036", 0.052, f"-{yb}", 0.062, CHROME, detail=COARSE, in_plan=True)
    flange(gr, "Canopla da argola", 0, E)
    gr.cyl_y("Haste da argola", 0, E, yb, 0.0085, f"-0.011 - {yb}", CHROME, in_plan=True)
    gr.cyl_y("Anel da haste da argola", 0, E, f"{yb} + 0.012", 0.0105, 0.005, CHROME, detail=FINE)
    gr.cyl("Cabeça da argola", 0, yb, f"{E} - 0.03", 0.0125, 0.042, CHROME, in_plan=True)
    zt = f"{E} + 0.012"
    gr.rev("Topo da cabeça da argola", "Front", [(0, zt), (0.0125, zt, 0.01), (0.007, f"{zt} + 0.006"), (0, f"{zt} + 0.007")], yb, 0, CHROME)
    gr.cyl_y("Pino da argola", 0, f"{E} - 0.036", f"{yb} - 0.0085", 0.0028, 0.017, STEEL, detail=FINE)
    gr.cyl_y("Cabeça do pino da argola", 0, f"{E} - 0.036", f"{yb} - 0.0095", 0.0042, 0.0012, CHROME, detail=FINE)
    gr.cyl("Parafuso de fixação da argola", 0, f"{yb} + 0.004", f"{E} + 0.0068", 0.0022, 0.012, STEEL, detail=FINE)
    gr.tube("Argola", "Front", loop_path(0, zc, R, R, n=48), yb, 0.006, CHROME, n=12, in_plan=True)

    # --- ring: a hand towel through it ---
    tr = f"(1.3*{R})"
    zr = f"({zc} - {R})"
    r2 = 0.0115
    sec2 = [(-0.004, f"-{tr}/2"), (0.004, f"-{tr}/2"), (0.004, f"{tr}/2"), (-0.004, f"{tr}/2")]
    gr.sweep("Toalha de rosto", "Side", [
        (f"{yb} - {r2 + 0.005}", f"{zr} - 0.3"), (f"{yb} - {r2}", f"{zr} - 0.2"), (f"{yb} - {r2}", zr, -r2),
        (f"{yb} + {r2}", zr), (f"{yb} + {r2}", f"{zr} - 0.2"), (f"{yb} + {r2 + 0.003}", f"{zr} - 0.28"),
    ], 0, sec2, TOWEL, detail=FINE)
    gr.box("Barrado da toalha de rosto", f"-{tr}/2", f"{yb} - {r2 + 0.0051}", f"{zr} - 0.175", tr, 0.0012, 0.025, STRIPE, detail=FINE)

    c.preview_base = 0.6
    c.preview_size = (0.6, 0.3, 0.55)
    return c
