"""The floor-standing toilet bowl shared by the two bacia components."""

from __future__ import annotations

from louca import *  # noqa: F401,F403


def bowl_section():
    """(distance outwards from the sump's outline, height below the rim) around the bowl's wall."""
    funnel = smooth([(0, -0.195), (0.012, -0.178), (0.04, -0.135), (0.072, -0.085), (0.092, -0.045), (0.100, -0.030)], 4)
    lip = [(0.093, -0.030), (0.093, -0.006), (0.095, -0.002), (0.099, 0)]
    top = [(0.130, 0), (0.134, -0.002)]
    outer = smooth([(0.135, -0.006), (0.135, -0.045), (0.131, -0.085), (0.118, -0.13), (0.095, -0.175), (0.07, -0.215),
                    (0.055, -0.245), (0.05, -0.26)], 4)
    return [(0, -0.26)] + funnel + lip + top + outer


RIM = 0.135  # the rim's outer edge, out of the sump's outline


def bacia(c, L, H, yf, yb, deck_back, seat_angle, lid_angle, y_bolts):
    """Bowl, pedestal, rear column, deck, water, seat and lid, hinges and floor bolts.

    L: width; H: height of the rim; yf, yb: front and back tips of the bowl;
    deck_back: y where the deck ends; y_bolts: y of the floor bolts.
    Returns the names worth knowing: the hinge (y, z).
    """
    cy = f"({p(yf)} + {p(yb)}) / 2"
    b = f"({p(yb)} - {p(yf)}) / 2"
    a0 = f"{p(L)} / 2 - {RIM}"
    b0 = f"{b} - {RIM}"

    def z(d):
        return add(H, d)

    # --- the bowl: its wall carried around the sump, hollow by construction ---
    ring(c, "Bacia", 0, cy, a0, b0, H, bowl_section(), "Louça", in_plan=True)
    c.profile("Água", "Plan", oval(0, cy, add(a0, 0.004), add(b0, 0.004), n=32), z(-0.24), 0.041, "Água")

    # --- pedestal and rear column (trapway) ---
    def ped(rx, front, back, power=2.6):
        y0, y1 = add(yf, front), add(deck_back, back)
        return oval(0, f"({y0} + {y1}) / 2", rx, f"({p(y1)} - {p(y0)}) / 2", power=power)

    loft(c, "Pedestal", [
        (0, ped(0.118, 0.15, -0.03)),
        (0.012, ped(0.118, 0.15, -0.03)),
        (0.04, ped(0.104, 0.165, -0.037)),
        (0.11, ped(0.098, 0.16, -0.04)),
        (z(-0.235), ped(0.116, 0.11, -0.035)),
    ], "Louça")

    def col(rx, front, back):
        y0, y1 = add(yb, front), add(deck_back, back)
        return oval(0, f"({y0} + {y1}) / 2", rx, f"({p(y1)} - {p(y0)}) / 2", power=3.2)

    loft(c, "Coluna do sifão", [(z(-0.236), col(0.1, -0.045, -0.04)), (z(-0.07), col(0.112, -0.034, -0.008))], "Louça")
    c.profile("Mesa da bacia", "Plan", rrect(-0.118, add(yb, -0.032), 0.118, deck_back, 0.028), z(-0.07), 0.07, "Louça", in_plan=True)
    # The trapway shows as a bulge on both sides of the column.
    ya, yc_, yd = add(yb, -0.012), f"({p(yb)} + {p(deck_back)}) / 2 - 0.02", add(deck_back, -0.07)
    zt = z(-0.2)
    for side, x in (("esquerdo", -0.06), ("direito", 0.06)):
        tube(c, f"Bojo do sifão {side}", "Side", [
            bez(ya, 0.045, ya, f"{zt} * 0.7", add(yc_, -0.06), zt),
            bez(yc_, zt, add(yc_, 0.05), zt, yd, f"{zt} * 0.7"),
            (yd, 0.045),
        ], x, 0.046, "Louça", n=16)

    # --- floor bolts ---
    for side, x in (("esquerdo", -0.128), ("direito", 0.128)):
        c.cyl(f"Orelha de fixação {side}", x, y_bolts, 0, 0.024, 0.012, "Louça")
        c.rev(f"Capa do parafuso {side}", "Front", [(x, 0.012), (add(x, 0.013), 0.012), (add(x, 0.012), 0.02, 0.012), (x, 0.026)],
              y_bolts, x, "Branco", detail=FINE)

    # --- seat and lid ---
    hinge = (add(yb, 0.008), z(0.014))
    a_s, b_s = f"{p(L)} / 2 - 0.004", f"{b} - 0.004"
    seat_and_lid(c, hinge, seat_angle, lid_angle, cy, a_s, b_s, 0.66, f"{b} - 0.07", seat_t=(-0.010, 0.010), lid_t=(0.0115, 0.022))
    c.lid_box("Barra do assento", hinge, seat_angle, -0.062, 0.124, -0.011, 0.05, -0.010, 0.010, "Branco")
    c.lid_box("Barra da tampa", hinge, lid_angle, -0.09, 0.18, -0.011, 0.05, 0.0115, 0.022, "Branco")
    for i, (side, x) in enumerate((("esquerda", -0.09), ("direita", 0.062)), 1):
        c.cyl_x(f"Dobradiça {side}", hinge[0], hinge[1], x, 0.0095, 0.028, "Cromado")
        c.cyl(f"Pino da dobradiça {side}", add(x, 0.014), hinge[0], H, 0.0075, 0.014, "Cromado", FINE)
        c.cyl(f"Base da dobradiça {side}", add(x, 0.014), hinge[0], H, 0.014, 0.003, "Cromado", FINE)
    # Bumpers under the seat, turning with it.
    for i, (x, r) in enumerate(((-0.13, 0.2), (0.105, 0.2), (-0.11, 0.36), (0.085, 0.36)), 1):
        c.lid_box(f"Batente do assento {i}", hinge, seat_angle, x, 0.025, r, r + 0.012, -0.0135, -0.010, "Borracha cinza", FINE)
    return hinge
