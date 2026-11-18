"""Bacia sanitária com caixa acoplada: bacia oval com assento e tampa que abrem, caixa com botão duplo, engate e registro."""

from louca import *
from louca.bacia import bacia


def build():
    c = Component("Bacia sanitária com caixa acoplada", "plumbing", "bacia-caixa-acoplada", "Plumbing")
    L = c.param("Largura", 0.38)
    D = c.param("Profundidade", 0.65)
    A = c.param("Altura", 0.78)
    H = c.param("AlturaBacia", 0.39)
    lid = c.angle("AnguloTampa", 0, open_at=90)
    seat = c.angle("AnguloAssento", 0)
    c.type("Bacia c/ caixa acoplada", "Bacia convencional com caixa acoplada 6 L")
    c.type("Bacia c/ caixa acoplada PNE", "Bacia para pessoa com deficiência (assento a 0,46 m)",
           Largura=0.4, Profundidade=0.7, Altura=0.82, AlturaBacia=0.44)
    c.mep = {"Fixture": {"drain_units": 6, "supply_weight": 0.3, "hot_water": False}}
    c.connector("Esgoto", "Sanitary", 0, f"{D} / 2 - 0.3", 0, "Down", 0.1)
    c.connector("Água fria", "ColdWater", -0.15, f"{D} / 2", 0.2, "Back", 0.02)
    c.material("Água", (150, 196, 214), "Glass", "Polished", 0.35)

    yw = f"{D} / 2"  # the wall
    yf, yb = f"-{D} / 2", f"{D} / 2 - 0.215"

    # --- coarse stand-ins (the old pieces) ---
    c.box("Pé simplificado", -0.11, f"-{D} / 2 + 0.15", 0, 0.22, f"{D} - 0.33", 0.25, "Louça", COARSE)
    c.cyl("Bacia simplificada", 0, f"-{D} / 2 + {L} / 2", 0.2, f"{L} / 2", f"{H} - 0.2", "Louça", COARSE, in_plan=True)
    c.box("Corpo simplificado", f"-{L} / 2", f"-{D} / 2 + {L} / 2", 0.2, L, f"{D} - {L} / 2 - 0.18", f"{H} - 0.2", "Louça", COARSE, in_plan=True)
    c.box("Caixa simplificada", f"-{L} / 2", f"{D} / 2 - 0.18", H, L, 0.18, f"{A} - {H}", "Louça", COARSE, in_plan=True)

    bacia(c, L, H, yf, yb, f"{D} / 2 - 0.012", seat, lid, f"{D} / 2 - 0.3")

    # --- cistern ---
    def tank(inset_side, front, back, r):
        return rrect(f"-{L} / 2 + {inset_side}", f"{D} / 2 - {front}", f"{L} / 2 - {inset_side}", f"{D} / 2 - {back}", r)

    zt = f"{A} - 0.034"  # under the lid
    blend(c, "Base da caixa", "Plan", tank(0.05, 0.15, 0.022, 0.035), tank(0.016, 0.168, 0.012, 0.035), H, 0.05, "Louça")
    blend(c, "Caixa acoplada", "Plan", tank(0.016, 0.168, 0.012, 0.035), tank(0.006, 0.175, 0.006, 0.035), f"{H} + 0.05", f"{zt} - {H} - 0.05", "Louça")
    c.profile("Tampa da caixa", "Plan", tank(0, 0.18, 0, 0.03), zt, 0.024, "Louça", in_plan=True)
    blend(c, "Chanfro da tampa da caixa", "Plan", tank(0, 0.18, 0, 0.03), tank(0.012, 0.168, 0.012, 0.024), f"{A} - 0.01", 0.01, "Louça")
    yk = f"{D} / 2 - 0.09"  # the button, on the lid's center
    c.cyl("Aro do botão", 0, yk, f"{A} - 0.001", 0.029, 0.004, "Cromado", in_plan=True)
    c.profile("Botão de descarga parcial", "Plan", [(-0.0015, f"{yk} - 0.024"), (-0.0015, f"{yk} + 0.024", 0.024)], f"{A} + 0.001", 0.0045, "Cromado", FINE)
    c.profile("Botão de descarga total", "Plan", [(0.0015, f"{yk} + 0.024"), (0.0015, f"{yk} - 0.024", 0.024)], f"{A} + 0.001", 0.0045, "Cromado", FINE)
    for side, x in (("esquerdo", -0.075), ("direito", 0.075)):
        c.cyl(f"Parafuso da caixa {side}", x, f"{D} / 2 - 0.1", f"{H} - 0.1", 0.004, 0.03, "Latão", FINE)
        c.cyl(f"Porca borboleta {side}", x, f"{D} / 2 - 0.1", f"{H} - 0.088", 0.012, 0.007, "Branco", FINE)

    # --- supply: angle valve on the wall, braided hose and the cistern's inlet ---
    xs = -0.15
    yo, zo = angle_valve(c, "registro", xs, yw, 0.2)
    yi = f"{D} / 2 - 0.085"  # the inlet under the cistern
    c.cyl("Entrada da caixa", xs, yi, f"{H} - 0.03", 0.011, 0.031, "Branco", FINE)
    c.cyl("Porca da entrada", xs, yi, f"{H} - 0.016", 0.017, 0.016, "Branco", FINE)
    c.cyl("Porca do engate", xs, yi, f"{H} - 0.046", 0.0115, 0.016, "Latão", FINE)
    tube(c, "Engate flexível", "Side", [bez(yo, zo, yo, f"{zo} + 0.07", yi, f"{H} - 0.13"), (yi, f"{H} - 0.046")], xs, 0.0065, "Inox escovado", FINE, n=10)
    return c
