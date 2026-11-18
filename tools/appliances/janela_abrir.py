"""Janela de abrir de madeira, duas folhas abrindo para dentro: marco com batedor do tamanho da
parede, folhas envidraçadas com travessa intermediária, baguetes, pingadeira, mata-junta,
cremona, tarjetas, dobradiças, guarnição interna e peitoril de granito."""

from kit import *
from janela_comum import *

WOOD = "Madeira"
I = "(WallThickness/2)"  # the wall's room face
YE = "(-WallThickness/2 + 0.02)"  # the frame's exterior face (the plaster returns 2 cm onto it)
YL1 = f"({I} - 0.008)"  # the leaves' room face, closed
YL0 = f"({I} - 0.043)"  # their exterior face (35 mm leaves)
YB0 = f"({I} - 0.063)"  # the stop's exterior face
FA = 0.035  # face width of the frame boards
STOP = 0.05  # the stop's edge from the frame's outer edge
SW, TR, BR, MU = 0.05, 0.05, 0.08, 0.035  # leaf stiles, top rail, bottom rail, glazing bar
LIP = 0.012  # glazing rebate lip and bead width


def build() -> Component:
    # "Janela de abrir" is a component of the app template: the library's needs another name.
    c = Component("Janela de abrir de madeira", "windows", "janela-abrir", "Window")
    L = c.param("Largura", 1.0)
    H = c.param("Altura", 1.0)
    c.param("Peitoril", 1.1)
    AE = opening_param(c, "AnguloFolhaEsquerda", "Angle", 75)
    AD = opening_param(c, "AnguloFolhaDireita", "Angle", 95)
    c.opening = {"width": "Largura", "height": "Altura", "sill": "Peitoril", "own_symbol": True, "operation": "DoubleSideHung"}
    stone(c)
    x0, x1 = f"(-{L}/2)", f"({L}/2)"

    # --- coarse ----------------------------------------------------------------------
    dep = f"({I} - {YE})"
    c.box("Marco simplificado esquerdo", x0, YE, 0, 0.05, dep, H, WOOD, COARSE, in_plan=True)
    c.box("Marco simplificado direito", f"{x1} - 0.05", YE, 0, 0.05, dep, H, WOOD, COARSE, in_plan=True)
    c.box("Marco simplificado inferior", f"{x0} + 0.05", YE, 0, f"{L} - 0.1", dep, 0.045, WOOD, COARSE)
    c.box("Marco simplificado superior", f"{x0} + 0.05", YE, f"{H} - 0.05", f"{L} - 0.1", dep, 0.05, WOOD, COARSE)
    peitoril(c, L, YE, I)

    # --- frame: boards across the wall with a stop on the exterior side of the leaves ----
    jamb = [(0, YE), (FA, YE), (FA, YB0), (STOP, YB0), (STOP, YL0), (FA, YL0), (FA, I), (0, I)]
    ring(c, "Marco", x0, x1, 0, H, jamb, WOOD, sides="lrt")
    for i in c.items:
        if i["name"].startswith("Marco montante"):
            i["in_plan"] = True
    # the sill board: a raised stop under the leaves, sloping out to the exterior
    c.profile("Marco travessa inferior", "Side", [(YE, 0), (I, 0), (I, 0.03), (YL0, 0.03), (YL0, 0.045), (YB0, 0.045), (YB0, 0.035), (YE, 0.022)],
              x0, L, WOOD)

    # --- interior casing (guarnição) on the room face of the wall -----------------------
    def casing(x, sgn):  # outline of a jamb casing, its inner edge 1 cm over the frame
        q = lambda d: plus(x, d) if sgn > 0 else minus(x, d)
        return [(q(-0.04), I), (q(0.01), I), (q(0.01), f"{I} + 0.008"), (q(0.006), f"{I} + 0.012"), (q(-0.04), f"{I} + 0.012")]
    c.profile("Guarnição esquerda", "Plan", casing(x0, +1), 0.005, f"{H} + 0.035", WOOD, in_plan=True)
    c.profile("Guarnição direita", "Plan", list(reversed(casing(x1, -1))), 0.005, f"{H} + 0.035", WOOD, in_plan=True)
    c.profile("Guarnição superior", "Side", [(I, f"{H} + 0.04"), (I, f"{H} - 0.01"), (f"{I} + 0.008", f"{H} - 0.01"),
                                             (f"{I} + 0.012", f"{H} - 0.006"), (f"{I} + 0.012", f"{H} + 0.04")], f"{x0} - 0.04", f"{L} + 0.08", WOOD)

    # --- the leaves ------------------------------------------------------------------------
    wl = f"(({L} - {2 * 0.037 + 0.003:g})/2)"
    ea = 0.001  # leaf edge from the hinge axis, along the leaf
    a1 = f"({ea} + {wl})"
    zl0, zl1 = 0.033, f"({H} - 0.037)"
    zm = f"(({zl0 + BR:g} + {zl1} - {TR})/2)"  # glazing bar's center
    zc = f"({H}/2)"
    panes = [(zl0 + BR, f"({zm} - {MU / 2})"), (f"({zm} + {MU / 2})", f"({zl1} - {TR})")]  # z ranges of the lights inside the leaf members
    bf, bi = -0.039, -0.004  # the leaf's exterior and room faces, from the hinge axis (b to the room)
    bg0, bg1 = bf + 0.015, bf + 0.019  # the glass, against the exterior lip
    leaves = []
    for side, name, A, hx in (("left", "Folha esquerda", AE, f"({x0} + 0.036)"), ("right", "Folha direita", AD, f"({x1} - 0.036)")):
        hinge = (hx, f"({I} - 0.004)")
        leaves.append((side, name, A, hinge))

        def sbox(n, a0, a1_, b0, b1, z, h, mat=WOOD, detail=FULL):
            swing_box(c, f"{name} {n}", hinge, A, a0, a1_, b0, b1, z, h, mat, side, detail)

        def sprof(n, pts, z, h, mat=WOOD, detail=FULL):
            swing_prof(c, f"{name} {n}", hinge, A, pts, z, h, mat, side, detail)

        hl = minus(zl1, zl0)
        sbox("simplificada", ea, a1, bf, bi, zl0, hl, GLASS, COARSE)
        for i in c.items:
            if i["name"] == f"{name} simplificada":
                i["in_plan"] = True
        # stiles with the exterior glazing lip
        sprof("montante da dobradiça", [(ea, bf), (ea + SW + LIP, bf), (ea + SW + LIP, bg0), (ea + SW, bg0), (ea + SW, bi), (ea, bi)], zl0, hl)
        sprof("montante de encontro", [(a1, bf), (a1, bi), (f"{a1} - {SW}", bi), (f"{a1} - {SW}", bg0), (f"{a1} - {SW + LIP}", bg0),
                                       (f"{a1} - {SW + LIP}", bf)], zl0, hl)
        for i in c.items:
            if i["name"] in (f"{name} montante da dobradiça", f"{name} montante de encontro"):
                i["in_plan"] = True
        ra0, ra1 = ea + SW, f"({a1} - {SW})"
        sbox("travessa inferior", ra0, ra1, bf, bi, zl0, BR)
        sbox("travessa superior", ra0, ra1, bf, bi, f"{zl1} - {TR}", TR)
        sbox("travessa intermediária", ra0, ra1, bf, bi, f"{zm} - {MU / 2}", MU)
        # exterior lips along the rails, glass, and the beads holding it from the room side
        la0, la1 = ea + SW + LIP, f"({a1} - {SW + LIP})"
        for k, (z0, z1) in enumerate(panes, 1):
            sbox(f"aba inferior do vidro {k}", ra0, ra1, bf, bg0, z0, LIP)
            sbox(f"aba superior do vidro {k}", ra0, ra1, bf, bg0, f"{z1} - {LIP}", LIP)
            sbox(f"vidro {k}", ea + SW - 0.003, f"{a1} - {SW - 0.003}", bg0, bg1, f"{z0} - 0.003", f"{minus(z1, z0)} + 0.006", GLASS)
            if k == 1:
                for i in c.items:
                    if i["name"] == f"{name} vidro 1":
                        i["in_plan"] = True
            sprof(f"baguete esquerdo {k}", [(ea + SW, bg1), (la0, bg1), (la0, bg1 + 0.004), (ea + SW + 0.004, bi), (ea + SW, bi)],
                  plus(z0, LIP), minus(minus(z1, z0), 2 * LIP), WOOD, FINE)
            sprof(f"baguete direito {k}", [(f"{a1} - {SW}", bg1), (f"{a1} - {SW}", bi), (f"{a1} - {SW + 0.004}", bi), (la1, bg1 + 0.004), (la1, bg1)],
                  plus(z0, LIP), minus(minus(z1, z0), 2 * LIP), WOOD, FINE)
            sbox(f"baguete inferior {k}", ra0, ra1, bg1, bi, z0, LIP, WOOD, FINE)
            sbox(f"baguete superior {k}", ra0, ra1, bg1, bi, f"{z1} - {LIP}", LIP, WOOD, FINE)
        # weather drip on the bottom rail, over the sill's stop
        sbox("pingadeira", ea + 0.017, a1, bf - 0.018, bf, 0.047, 0.026)
        sbox("pingadeira friso", ea + 0.017, a1, bf - 0.018, bf - 0.012, 0.043, 0.004)
        # butt hinges: the knuckle on the axis, its finials, the leaves in the gap
        for k, z in enumerate((f"{zl0} + 0.13", f"{zl1} - 0.2"), 1):
            c.cyl(f"{name} dobradiça {k}", hinge[0], hinge[1], z, 0.0048, 0.07, "Latão")
            c.cyl(f"{name} dobradiça {k} ponteira inferior", hinge[0], hinge[1], f"{z} - 0.006", 0.0032, 0.006, "Latão", FINE)
            c.cyl(f"{name} dobradiça {k} ponteira superior", hinge[0], hinge[1], f"{z} + 0.07", 0.0032, 0.006, "Latão", FINE)
            sbox(f"dobradiça {k} aba", -0.0005, 0.0015, -0.03, -0.0025, z, 0.07, "Latão", FINE)

    # --- meeting joint and locking -------------------------------------------------------------
    side, name, A, hinge = leaves[1]  # the right leaf carries the cover strip and the espagnolette

    def rbox(n, a0, a1_, b0, b1, z, h, mat, detail=FULL):
        swing_box(c, n, hinge, A, a0, a1_, b0, b1, z, h, mat, side, detail)

    rbox("Mata-junta", f"{a1} - 0.02", f"{a1} + 0.015", bi, 0.008, zl0, minus(zl1, zl0), WOOD)
    am = f"({a1} - 0.0025)"
    swing_prof(c, "Cremona caixa", hinge, A, [(f"{am} - 0.011", 0.008), (f"{am} + 0.011", 0.008), (f"{am} + 0.011", 0.0105),
                                              (f"{am} + 0.008", 0.0125), (f"{am} - 0.008", 0.0125), (f"{am} - 0.011", 0.0105)],
               f"{zc} - 0.055", 0.11, "Latão", side)
    swing_prof(c, "Cremona manopla", hinge, A, [(f"{am} - 0.0065", 0.0125), (f"{am} + 0.0065", 0.0125), (f"{am} + 0.0045", 0.026, 0.006),
                                                (f"{am} - 0.0045", 0.026)], f"{zc} - 0.115", 0.13, "Latão", side)
    gx, gy = swing_pt(hinge, A, am, 0.0115, side)
    c.cyl("Cremona haste superior", gx, gy, f"{zc} + 0.055", 0.0035, f"{zl1} - 0.012 - ({zc} + 0.055)", "Latão", FINE)
    c.cyl("Cremona haste inferior", gx, gy, f"{zl0} + 0.012", 0.0035, f"{zc} - 0.055 - {zl0} - 0.012", "Latão", FINE)
    for k, z in enumerate((f"{zl1} - 0.16", f"{zl0} + 0.16"), 1):
        rbox(f"Cremona guia {k}", f"{am} - 0.01", f"{am} + 0.01", 0.008, 0.0165, z, 0.012, "Latão", FINE)
    # keepers on the frame where the rods' ends engage (closed position)
    kx = f"({x1} - 0.036 - {am})"
    c.box("Cremona receptor superior", f"{kx} - 0.01", f"{I} - 0.012", f"{H} - 0.038", 0.02, 0.026, 0.003, "Latão", FINE)
    c.box("Cremona receptor inferior", f"{kx} - 0.01", f"{I} - 0.012", 0.03, 0.02, 0.026, 0.003, "Latão", FINE)

    # barrel bolts on the left leaf's room face, at the top and the bottom
    side, name, A, hinge = leaves[0]
    for k, (zb, zt, zk) in enumerate(((f"{zl1} - 0.13", f"{zl1} - 0.004", f"{zl1} - 0.09"), (f"{zl0} + 0.004", f"{zl0} + 0.13", f"{zl0} + 0.082")), 1):
        n = "superior" if k == 1 else "inferior"
        swing_box(c, f"Tarjeta {n} chapa", hinge, A, f"{a1} - 0.04", f"{a1} - 0.014", bi, -0.0015, zb, minus(zt, zb), "Latão", side)
        tx, ty = swing_pt(hinge, A, f"{a1} - 0.027", 0.0025, side)
        c.cyl(f"Tarjeta {n} ferrolho", tx, ty, f"{zb} + 0.006", 0.004, f"{minus(zt, zb)} - 0.008", "Latão", FINE)
        swing_box(c, f"Tarjeta {n} pino", hinge, A, f"{a1} - 0.0305", f"{a1} - 0.0235", 0.0, 0.016, zk, 0.008, "Latão", side, FINE)

    # --- plan symbol: the swings of the leaves (into the room) ---------------------------------
    R = f"({wl} + {ea})"
    for side, name, A, (hx, hy) in leaves:
        if side == "left":
            pts = [(hx, hy), (plus(hx, R), hy, R), (hx, plus(hy, R))]
        else:
            pts = [(hx, hy), (hx, plus(hy, R), R), (minus(hx, R), hy)]
        c.profile(f"{name} giro", "Plan", pts, 0, 0.001, WOOD, ALL)
        c.plan_only(f"{name} giro")

    # --- fixing -------------------------------------------------------------------------------
    n = 0
    for x in (f"{x0} + 0.0175", f"{x1} - 0.0175"):
        for z in (0.15, f"{H} - 0.15"):
            n += 1
            c.cyl_y(f"Cavilha do marco {n}", x, z, f"{YE} - 0.0004", 0.005, 0.0006, "Madeira escura", FINE)

    d_ = "Janela de abrir de duas folhas, madeira e vidro"
    c.type("Janela de abrir 100 x 100", d_, Largura=1.0, Altura=1.0, Peitoril=1.1)
    c.type("Janela de abrir 120 x 120", d_, Largura=1.2, Altura=1.2, Peitoril=1.0)
    c.type("Janela de abrir 150 x 120", d_, Largura=1.5, Altura=1.2, Peitoril=1.0)
    c.preview_size = (1.0, 0.3, 1.0)
    c.preview_base = 1.1
    return c
