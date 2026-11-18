"""Banheira de embutir em acrílico: cuba lisa e oca com encosto inclinado, borda, saia frontal,
válvula de escoamento com ladrão, misturador de parede com bica e ducha manual, estrutura com pés reguláveis."""

from louca import *
from _casco import shell, annulus, mid

ACR = "Acrílico branco"
CHROME = "Cromado"


def build():
    c = Component("Banheira", "plumbing", "banheira", "Plumbing")
    L = c.param("Largura", 1.7)
    P = c.param("Profundidade", 0.75)
    A = c.param("Altura", 0.55)
    c.material(ACR, (248, 248, 245), "Plastic", "Glossy")

    desc = "Banheira de embutir em acrílico, com saia frontal, válvula com ladrão e misturador de parede"
    c.type("Banheira 150x70", desc, Largura=1.5, Profundidade=0.7)
    c.type("Banheira 170x75", desc)
    c.type("Banheira 160x70", desc, Largura=1.6, Profundidade=0.7)
    c.type("Banheira 180x80", desc, Largura=1.8, Profundidade=0.8)

    c.mep = {"Fixture": {"drain_units": 2, "supply_weight": 1.0, "hot_water": True}}

    # Frame: the wall at +y (back); the drain and the mixer at the left end (-x), the backrest at the right.
    x0, x1, y0, y1 = f"-{L} / 2", f"{L} / 2", f"-{P} / 2", f"{P} / 2"
    RE, RF, RB = 0.07, 0.075, 0.075  # deck width at the ends, the front and the back
    RC = 0.2  # corner radius of the basin's opening
    ZF = f"(0.24 * {A})"  # top of the basin's floor
    T = f"({A} - {ZF})"  # depth of the basin
    ox0, ox1, oy0, oy1 = add(x0, RE), add(x1, -RE), add(y0, RF), add(y1, -RB)  # the opening

    def z(dz):  # from the floor of the basin
        return add(ZF, dz)

    def za(dz):  # from the rim
        return add(A, dz)

    def opening(side, left, right):
        """The basin's outline inset by `side` on the long sides, `left` and `right` at the ends."""
        return (add(ox0, left), add(oy0, side), add(ox1, -right), add(oy1, -side), e(RC - side))

    # --- coarse stand-in: a block with the basin's walls ---
    c.box("Base simplificada", x0, y0, 0, L, P, ZF, ACR, COARSE, in_plan=True)
    c.box("Parede frontal simplificada", x0, y0, ZF, L, RF + 0.04, T, ACR, COARSE, in_plan=True)
    c.box("Parede traseira simplificada", x0, add(y1, -RB - 0.04), ZF, L, RB + 0.04, T, ACR, COARSE, in_plan=True)
    c.box("Parede esquerda simplificada", x0, add(y0, RF + 0.04), ZF, RE + 0.05, f"{P} - {RF + RB + 0.08}", T, ACR, COARSE, in_plan=True)
    c.box("Encosto simplificado", add(x1, -RE - 0.3), add(y0, RF + 0.04), ZF, RE + 0.3, f"{P} - {RF + RB + 0.08}", T, ACR, COARSE, in_plan=True)

    # --- the basin: a smooth acrylic shell, steep at the drain end, reclined at the backrest ---
    # (height above the floor, inset of the long sides, of the left end, of the right end)
    prof = [
        (-0.012, 0.088, 0.088, 0.43),
        (0.0, 0.085, 0.085, 0.42),
        (0.008, 0.071, 0.071, 0.40),
        (0.025, 0.058, 0.058, 0.375),
        (0.055, 0.048, 0.048, 0.34),
        (0.10, 0.040, 0.040, 0.29),
        (0.20, 0.027, 0.027, 0.185),
        (0.30, 0.014, 0.014, 0.085),
    ]
    levels = [(z(h), opening(s, l, r)) for h, s, l, r in prof]
    levels.append((za(-0.006), opening(0, 0, 0)))
    levels.append((A, opening(-0.006, -0.006, -0.006)))
    shell(c, "Cuba", levels, 0.012, ACR, xs=add(ox0, 0.35))
    floor = opening(0.087, 0.087, 0.425)
    c.profile("Fundo da cuba", "Plan", rrect(*floor[:4], floor[4]), z(-0.012), 0.012, ACR)

    # --- deck: a flat rim around the opening, and the front apron ---
    c.profile("Borda", "Plan", annulus(opening(-0.006, -0.006, -0.006), (x0, y0, x1, y1, 0.015)), za(-0.012), 0.012, ACR)
    # Plan symbol: the outline and the basin's opening (the deck's slit would draw a line).
    c.profile("Símbolo - contorno", "Plan", rrect(x0, y0, x1, y1, 0.015), A, 0.001, ACR)
    c.plan_only("Símbolo - contorno")
    top = opening(-0.006, -0.006, -0.006)
    c.profile("Símbolo - cuba", "Plan", rrect(*top[:4], top[4]), A, 0.001, ACR)
    c.plan_only("Símbolo - cuba")
    c.profile("Saia frontal", "Side", [
        (y0, 0.006), (add(y0, 0.006), 0.006), (add(y0, 0.006), za(-0.012)), (add(y0, RF), za(-0.012)), (add(y0, RF), A),
        (add(y0, 0.012), A, 0.012), (y0, za(-0.012)),
    ], x0, L, ACR)
    c.box("Vedação da saia", add(x0, 0.002), add(y0, 0.001), 0, f"{L} - 0.004", 0.004, 0.006, "Borracha cinza", FINE)
    for side, xs in (("esquerda", x0), ("direita", add(x1, -0.006))):
        c.box(f"Testeira {side} da saia", xs, add(y0, 0.006), 0.006, 0.006, 0.05, za(-0.018), ACR, FINE)

    # --- floor: anti-slip strips and the drain ---
    xd = add(ox0, 0.085 + 0.065)  # the drain, on the floor near the left end
    for i in range(6):
        c.profile(f"Faixa antiderrapante {i + 1}", "Plan", rrect(add(xd, 0.17 + 0.075 * i), -0.11, add(xd, 0.19 + 0.075 * i), 0.11, 0.01),
                  ZF, 0.0015, "Plástico cinza claro", FINE)
    popup_drain(c, "de escoamento", xd, 0, ZF, radius=0.034)
    # Overflow on the left end wall, below the rim.
    zo = za(-0.085)
    c.cyl_x("Ladrão", 0, zo, add(ox0, -0.004), 0.034, 0.013, CHROME)
    for i, dz in enumerate((-0.014, -0.005, 0.004, 0.013), 1):
        c.box(f"Fenda do ladrão {i}", add(ox0, 0.0085), -0.018, add(zo, dz - 0.0015), 0.0006, 0.036, 0.003, "Plástico preto", FINE)

    # --- under the shell: reinforcement board, galvanized frame and adjustable feet ---
    zb = z(-0.012)
    fl = opening(0.1, 0.1, 0.44)
    c.profile("Placa de reforço", "Plan", rrect(*fl[:4], fl[4]), add(zb, -0.015), 0.015, "Madeira", FINE)
    zt = add(zb, -0.055)  # bottom of the frame's tubes
    ys = (add(fl[1], 0.03), add(fl[3], -0.07))
    for name, y in zip(("frontal", "traseira"), ys):
        c.box(f"Longarina {name}", add(fl[0], 0.04), y, zt, f"{p(fl[2])} - {p(fl[0])} - 0.08", 0.04, 0.04, "Aço galvanizado", FINE)
    xs_cross = (add(fl[0], 0.04), mid(fl[0], fl[2]), add(fl[2], -0.08))
    for i, x in enumerate(xs_cross, 1):
        c.box(f"Travessa {i}", x, ys[0], zt, 0.04, f"{p(ys[1])} - {p(ys[0])} + 0.04", 0.04, "Aço galvanizado", FINE)
        for j, y in enumerate(ys, 1):
            xf, yf = add(x, 0.02), add(y, 0.02)
            c.cyl(f"Pé regulável {i}.{j} - haste", xf, yf, 0.01, 0.006, f"{p(zt)} - 0.01", "Aço galvanizado", FINE)
            c.cyl(f"Pé regulável {i}.{j} - porca", xf, yf, add(zt, -0.012), 0.012, 0.008, "Aço galvanizado", FINE)
            c.rev(f"Pé regulável {i}.{j} - sapata", "Front", [(xf, 0), (add(xf, 0.025), 0), (add(xf, 0.025), 0.004), (add(xf, 0.012), 0.012), (xf, 0.012)],
                  yf, xf, "Borracha", detail=FINE)

    # --- waste: valve body under the floor, overflow pipe, trap to the floor drain ---
    c.cyl("Corpo da válvula", xd, 0, add(zb, -0.045), 0.03, 0.045, "Branco")
    c.cyl("Porca da válvula", xd, 0, add(zb, -0.012), 0.04, 0.01, "Branco", FINE)
    c.cyl_x("Tê do ladrão", 0, add(zb, -0.03), add(xd, -0.06), 0.016, 0.034, "Branco")
    xo = add(ox0, -0.035)  # the overflow pipe, outside the end wall
    tube(c, "Tubo do ladrão", "Front", [
        (add(ox0, -0.003), zo), (add(xo, 0.02), zo, 0.02), (xo, add(zo, -0.02)), (xo, add(zb, -0.05), 0.02),
        (add(xo, 0.02), add(zb, -0.03)), (add(xd, -0.028), add(zb, -0.03)),
    ], 0, 0.016, "Branco", n=12)
    c.cyl_x("Flange do ladrão", 0, zo, add(ox0, -0.018), 0.03, 0.006, "Branco", FINE)
    c.cyl("Tubo de descida", xd, 0, 0.05, 0.02, f"{p(zb)} - 0.095", "Branco")
    c.rev("Sifão", "Front", [(xd, 0.004), (add(xd, 0.04), 0.004, 0.012), (add(xd, 0.046), 0.02), (add(xd, 0.046), 0.05), (add(xd, 0.03), 0.062), (xd, 0.062)],
          0, xd, "Branco")
    c.rev("Tampa de limpeza do sifão", "Front", [(xd, 0.0), (add(xd, 0.03), 0.0), (add(xd, 0.03), 0.006), (xd, 0.006)], 0, xd, "Plástico cinza claro", detail=FINE)
    c.connector("Esgoto", "Sanitary", xd, 0, 0, "Down", 0.04)

    # --- wall mixer: two valves, the spout between them and a hand shower ---
    zr = za(0.2)
    for name, x, color in (("fria", add(x0, 0.1), "Plástico azul"), ("quente", add(x0, 0.25), "Plástico vermelho")):
        c.cyl_y(f"Canopla do registro {name}", x, zr, add(y1, -0.006), 0.032, 0.006, CHROME)
        c.rev(f"Castelo do registro {name}", "Plan", [(x, add(y1, -0.05)), (add(x, 0.014), add(y1, -0.05)), (add(x, 0.018), add(y1, -0.04)),
                                                     (add(x, 0.02), add(y1, -0.006)), (x, add(y1, -0.006))], zr, x, CHROME)
        c.rev(f"Volante do registro {name}", "Plan", [(x, add(y1, -0.072)), (add(x, 0.018), add(y1, -0.072), 0.008), (add(x, 0.024), add(y1, -0.062)),
                                                     (add(x, 0.022), add(y1, -0.05)), (x, add(y1, -0.05))], zr, x, CHROME)
        for i, (dx, dz, w, h) in enumerate(((-0.004, -0.03, 0.008, 0.06), (-0.03, -0.004, 0.06, 0.008)), 1):
            c.box(f"Manopla do registro {name} {i}", add(x, dx), add(y1, -0.066), add(zr, dz), w, 0.012, h, CHROME, FINE)
        c.cyl_y(f"Indicador do registro {name}", x, zr, add(y1, -0.0735), 0.007, 0.0015, color, FINE)
        c.connector(f"Água {name}", "ColdWater" if name == "fria" else "HotWater", x, y1, zr, "Back", 0.02)
    xs_ = add(x0, 0.175)
    zs = za(0.12)
    c.cyl_y("Canopla da bica", xs_, zs, add(y1, -0.008), 0.03, 0.008, CHROME)
    sweep(c, "Bica", "Side", [(add(y1, -0.006), zs), (add(y1, -0.13), zs, 0.04), (add(y1, -0.17), add(zs, -0.04))], xs_,
          [(-0.02, -0.011), (0.02, -0.011), (0.024, 0), (0.02, 0.011), (-0.02, 0.011), (-0.024, 0)], CHROME, in_plan=True)
    c.box("Saída da bica", add(xs_, -0.018), add(y1, -0.185), add(zs, -0.052), 0.036, 0.03, 0.012, CHROME, FINE)
    c.box("Arejador da bica", add(xs_, -0.014), add(y1, -0.181), add(zs, -0.0535), 0.028, 0.022, 0.002, "Plástico cinza", FINE)
    c.cyl("Desviador", xs_, add(y1, -0.03), add(zs, 0.01), 0.008, 0.03, CHROME, FINE)
    c.cyl("Botão do desviador", xs_, add(y1, -0.03), add(zs, 0.04), 0.012, 0.008, CHROME, FINE)
    # Hand shower in its wall bracket, with the hose looping above the rim.
    xh = add(x0, 0.4)
    zh = za(0.2)
    c.cyl_y("Suporte da ducha - canopla", xh, add(zh, 0.08), add(y1, -0.006), 0.022, 0.006, CHROME, FINE)
    c.box("Suporte da ducha", add(xh, -0.016), add(y1, -0.05), add(zh, 0.07), 0.032, 0.044, 0.02, CHROME, FINE)
    c.cyl("Ducha manual - cabo", xh, add(y1, -0.04), zh, 0.013, 0.16, CHROME)
    c.cyl("Ducha manual - porca", xh, add(y1, -0.04), add(zh, -0.012), 0.011, 0.014, CHROME, FINE)
    c.cyl_y("Ducha manual - cabeça", xh, add(zh, 0.19), add(y1, -0.06), 0.045, 0.03, CHROME)
    c.cyl_y("Ducha manual - crivo", xh, add(zh, 0.19), add(y1, -0.062), 0.038, 0.002, "Borracha cinza", FINE)
    c.cyl("Conexão da ducha", xs_, add(y1, -0.03), add(zs, -0.05), 0.009, 0.04, CHROME, FINE)
    hose = smooth([(0.175, 0.07), (0.175, 0.03), (0.2, 0.012), (0.3, 0.012), (0.37, 0.02), (0.4, 0.06), (0.4, 0.188)], 4)
    tube(c, "Flexível da ducha", "Front", [(add(x0, u), za(v)) for u, v in hose], add(y1, -0.034), 0.007, "Inox escovado", FINE, n=10)
    # Headrest clipped on the rim at the backrest's end.
    c.profile("Apoio de cabeça", "Front", rrect(add(ox1, -0.07), za(-0.11), add(ox1, 0.035), za(0.022), 0.03), -0.15, 0.3, "Borracha cinza", FINE)
    return c
