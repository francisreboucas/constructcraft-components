"""Porta de abrir de duas folhas: batente de madeira com rebaixo, guarnições, folhas almofadadas,
dobradiças, fechadura na folha ativa, mata-junta e fechos de embutir na folha secundária."""

from doorkit import *

STRIKE = ("Fechadura - contratesta", "Fechadura - furo da lingueta", "Fechadura - furo do trinco")


def build() -> Component:
    c = Component("Porta de abrir dupla", "doors", "porta-abrir-dupla", "Door")
    L = c.param("Largura", 1.4)
    H = c.param("Altura", 2.1)
    A = opening_param(c, "AnguloAbertura", 80)  # the active (right) leaf
    B = opening_param(c, "AnguloAberturaSecundaria", 65)  # the passive (left) leaf
    c.opening = {"width": "Largura", "height": "Altura", "own_symbol": True}
    c.preview_size = (1.3, 0.3, 2.1)
    wood = "Madeira"

    wood_frame(c, L, H, wood, in_plan=True)

    # Two leaves hinged on the jambs, flush with the +y face, meeting at x = 0 with a 3 mm gap.
    hx, hy = f"-{L}/2 + 0.037", f"{WT}/2 + 0.006"
    fl = Fr(c, hx, hy, B)  # passive leaf, on the left
    fr = Fr(c, hx, hy, A, mx=True)  # active leaf, on the right (mirrored)
    w = f"({L}/2 - 0.0385)"  # the meeting edge, from the hinge axis
    nf, nb = -0.006, -0.041
    nc = (nf + nb) / 2
    z1 = f"({H} - 0.038)"
    rails = [(0.88, 0.14), (1.5, 0.09)]
    hinges = [0.22, f"({H}/2 - 0.045)", f"({H} - 0.34)"]
    for f, side in ((fl, "esquerda"), (fr, "direita")):
        f.box(f"Folha {side} simplificada", 0.002, w, nb, nf, 0, f"{H} - 0.055", wood, detail=COARSE)
        panel_leaf(f, f"Folha {side}", 0.002, w, nb, nf, 0.008, z1, rails, wood)
        butt_hinges(f, f"Dobradiça {side}", hinges)
    for item in c.items:  # the passive leaf has no lock: its free stile meets the other leaf
        item["name"] = item["name"].replace("Folha esquerda - montante da fechadura", "Folha esquerda - montante de encontro")

    # --- active leaf: lever handles, mortise lock and the astragal over the joint -------------
    lever_set(fr, "Maçaneta", s(w, -0.055), nf, nb, 1.0)
    mortise_lock(fr, "Fechadura", w, nc, 1.0, s(w, 0.003), lip=0.0)
    # The lock's strike sits on the passive leaf's edge (it opens with that leaf), not on a jamb.
    c.items = [i for i in c.items if i["name"] not in STRIKE]
    fl.box("Fechadura - contratesta", w, s(w, 0.0014), nc - 0.011, nc + 0.011, 0.885, 0.17, "Inox escovado", detail=FINE)
    fl.box("Fechadura - furo da lingueta", s(w, 0.0014), s(w, 0.0017), nc - 0.007, nc + 0.007, 0.984, 0.032, "Plástico preto", detail=FINE)
    fl.box("Fechadura - furo do trinco", s(w, 0.0014), s(w, 0.0017), nc - 0.006, nc + 0.006, 0.902, 0.046, "Plástico preto", detail=FINE)
    # Astragal (mata-junta): a moulded strip on the active leaf's opening face, lapping the passive leaf.
    fr.poly("Mata-junta", [(s(w, -0.022), nf), (s(w, 0.025), nf), (s(w, 0.025), nf + 0.006, 0.006), (s(w, 0.019), nf + 0.012),
                           (s(w, -0.016), nf + 0.012, 0.006), (s(w, -0.022), nf + 0.006)], 0.012, f"{z1} - 0.016", wood)

    # --- passive leaf: flush bolts on its meeting edge, top and bottom, with their keepers ---------
    still = fl.still()
    for z0, name in ((0.12, "inferior"), (f"({z1} - 0.29)", "superior")):
        pre = f"Fecho de embutir {name}"
        fl.box(f"{pre} - testa", s(w, -0.0004), s(w, 0.0008), nc - 0.0095, nc + 0.0095, z0, 0.17, "Latão", detail=FINE)
        fl.box(f"{pre} - alavanca", s(w, 0.0008), s(w, 0.0022), nc - 0.004, nc + 0.004, s(z0, 0.055), 0.06, "Latão", detail=FINE)
        for j, dz in enumerate((0.007, 0.155)):
            fl.box(f"{pre} - parafuso {j + 1}", s(w, 0.0008), s(w, 0.0012), nc - 0.003, nc + 0.003, s(z0, dz), 0.006, "Cromado", detail=FINE)
    # The bolts drop into a socket in the floor and rise into a plate under the head jamb.
    still.cyl("Fecho de embutir inferior - bucha do piso", s(w, -0.012), nc, 0, 0.011, 0.0015, "Latão", detail=FINE)
    still.cyl("Fecho de embutir inferior - furo da bucha", s(w, -0.012), nc, 0.0015, 0.0055, 0.0004, "Plástico preto", detail=FINE)
    still.box("Fecho de embutir superior - contrachapa", s(w, -0.03), s(w, 0.006), nc - 0.0095, nc + 0.0095, f"{H} - 0.0365", 0.0015, "Latão", detail=FINE)

    # --- plan symbol: both leaves drawn open at 90 degrees with their swings ------------------------
    Y = f"{WT}/2"
    R = f"({L}/2 - 0.037)"
    xl, xr = f"(-{L}/2 + 0.037)", f"({L}/2 - 0.037)"
    c.profile("Giro esquerdo", "Plan", [(xl, Y), (f"{xl} + {R}", Y, R), (xl, f"{Y} + {R}")], 0, 0.001, wood)
    c.plan_only("Giro esquerdo")
    c.profile("Giro direito", "Plan", [(xr, Y), (xr, f"{Y} + {R}", R), (f"{xr} - {R}", Y)], 0, 0.001, wood)
    c.plan_only("Giro direito")

    d = "Porta de giro de duas folhas, batente de madeira"
    c.type("Porta de abrir dupla 120 x 210", d, Largura=1.2, Altura=2.1)
    c.type("Porta de abrir dupla 140 x 210", d, Largura=1.4, Altura=2.1)
    c.type("Porta de abrir dupla 160 x 210", d, Largura=1.6, Altura=2.1)
    return c
