"""Bacia sanitária para válvula de descarga: bacia oval com assento e tampa que abrem, tubo de ligação e bolsa de borracha
na entrada traseira, acabamento da válvula na parede e parafusos de fixação no piso."""

from _sanitarios import *
from louca.bacia import bacia


def build():
    c = Component("Bacia sanitária com válvula de descarga", "plumbing", "bacia-valvula", "Plumbing")
    L = c.param("Largura", 0.38)
    D = c.param("Profundidade", 0.55)
    H = c.param("AlturaBacia", 0.39)
    Hv = c.param("AlturaValvula", 1.1, instance=True)  # the flush valve's push plate, on the wall
    lid = c.angle("AnguloTampa", 0, open_at=100)
    seat = c.angle("AnguloAssento", 0)
    c.type("Bacia c/ válvula de descarga", "Bacia convencional com válvula de descarga")
    c.type("Bacia c/ válvula de descarga PNE", "Bacia para pessoa com deficiência (assento a 0,46 m), com válvula de descarga",
           Largura=0.4, Profundidade=0.6, AlturaBacia=0.44)
    c.mep = {"Fixture": {"drain_units": 6, "supply_weight": 32, "hot_water": False}}
    c.connector("Esgoto", "Sanitary", 0, V(D) / 2 - 0.3, 0, "Down", 0.1)
    c.connector("Válvula de descarga", "ColdWater", 0, V(D) / 2, Hv, "Back", 0.04)
    c.material("Água", (150, 196, 214), "Glass", "Polished", 0.35)
    c.preview_size = (0.45, 0.6, 1.15)

    yw = V(D) / 2  # the wall
    yf, yb = -V(D) / 2, V(D) / 2 - 0.11  # front and back tips of the bowl
    deck_back = yw - 0.045  # the back face of the ceramic, where the inlet is

    # --- coarse stand-ins ---
    c.box("Pé simplificado", -0.11, -V(D) / 2 + 0.15, 0, 0.22, V(D) - 0.25, 0.25, "Louça", COARSE)
    c.cyl("Bacia simplificada", 0, -V(D) / 2 + V(L) / 2, 0.2, V(L) / 2, V(H) - 0.2, "Louça", COARSE, in_plan=True)
    c.box("Corpo simplificado", -V(L) / 2, -V(D) / 2 + V(L) / 2, 0.2, L, deck_back + V(D) / 2 - V(L) / 2, V(H) - 0.2, "Louça", COARSE, in_plan=True)
    c.box("Válvula simplificada", -0.05, yw - 0.025, V(Hv) - 0.05, 0.1, 0.025, 0.1, "Cromado", COARSE)

    hinge = bacia(c, L, H, yf, yb, deck_back, seat, lid, V(D) / 2 - 0.3)
    # Without a cistern the deck behind the seat shows: round its top edge (it replaces the shared bowl's flat deck).
    deck = next(i for i in c.items if i["name"] == "Mesa da bacia")
    c.items.remove(deck)

    def top(inset):
        return rrect(-0.118 + inset, yb - 0.032 + inset, 0.118 - inset, deck_back - inset, 0.028 - inset)

    loft_x(c, "Mesa da bacia", [(V(H) - 0.07, top(0)), (V(H) - 0.007, top(0))], "Louça", in_plan=True)
    loft_x(c, "Borda da mesa", [(V(H) - 0.007, top(0)), (V(H) - 0.002, top(0.003)), (H, top(0.008))], "Louça")
    # The shared bowl's trapway bulges are drawn for a cistern's deep back; this short back gets its own:
    # the trapway rising from the sump behind the bowl and falling into the pedestal, on both sides of the column.
    for item in [i for i in c.items if i["name"].startswith("Bojo do sifão")]:
        c.items.remove(item)
    hz = V(H)
    path = catmull([(yb - 0.09, hz - 0.255), (yb - 0.05, hz - 0.205), (yb - 0.015, hz - 0.178), (yb + 0.008, hz - 0.2),
                    (yb + 0.006, hz - 0.26), (yb - 0.01, 0.07)], 4)
    for side, x in (("esquerdo", -0.046), ("direito", 0.046)):
        tube(c, f"Bojo do sifão {side}", "Side", path, x, 0.044, "Louça", n=16)

    # --- water inlet at the back: ceramic spigot, rubber spud, chrome connecting pipe and its escutcheon ---
    zi = V(H) - 0.036
    c.cyl_y("Bocal de entrada", 0, zi, deck_back - 0.01, 0.03, 0.022, "Louça")
    c.cyl_y("Bolsa de ligação", 0, zi, deck_back + 0.008, 0.026, 0.016, "Borracha")
    c.cyl_y("Abraçadeira da bolsa", 0, zi, deck_back + 0.016, 0.0268, 0.005, "Inox escovado", FINE)
    c.cyl_y("Tubo de ligação", 0, zi, deck_back + 0.02, 0.019, yw - deck_back - 0.026, "Cromado")
    c.cyl_y("Canopla do tubo de ligação", 0, zi, yw - 0.007, 0.042, 0.007, "Cromado")

    # --- flush valve's push plate on the wall (the valve itself is built into the wall) ---
    plate = [(0, yw), (0.052, yw), (0.052, yw - 0.004), (0.047, yw - 0.010), (0.03, yw - 0.012), (0, yw - 0.012)]
    c.rev("Acabamento da válvula", "Plan", plate, Hv, 0, "Cromado", in_plan=False)
    c.rev("Botão da válvula", "Plan", [(0, yw - 0.011), (0.023, yw - 0.011), (0.023, yw - 0.019), (0.019, yw - 0.023), (0, yw - 0.0245)],
          Hv, 0, "Cromado")
    c.rev("Anel do botão", "Plan", [(0.0235, yw - 0.0105), (0.0275, yw - 0.0105), (0.0275, yw - 0.0135), (0.0235, yw - 0.0135)],
          Hv, 0, "Plástico cinza", detail=FINE)
    c.cyl_y("Tampa do registro integrado", 0, V(Hv) - 0.038, yw - 0.0135, 0.006, 0.003, "Cromado", FINE)
    for side, x in (("esquerdo", -0.04), ("direito", 0.04)):
        c.cyl_y(f"Parafuso do acabamento {side}", x, Hv, yw - 0.0125, 0.0035, 0.002, "Inox escovado", FINE)
    flatten_beziers(c)  # the trapway bulges' curves, which ccad 0.12 would draw straight
    return c
