"""Reservatório térmico (boiler): a horizontal insulated hot-water tank for solar heating, on two saddles.

The tank lies along X centred on the origin, on the floor or slab; the pipe stubs are at the ends.
"""

from kit import *


def build():
    c = Component("Reservatório térmico", "plumbing", "reservatorio-termico", "Plumbing")
    L = c.param("Comprimento", 1.25)
    D = c.param("Diametro", 0.6)
    desc = ("Reservatório térmico horizontal de aço inox isolado com poliuretano, revestimento de alumínio, resistência elétrica "
            "de apoio com termostato, para aquecimento solar de baixa pressão (NBR 15569)")
    c.type("Reservatório térmico 300 L", desc)
    c.type("Reservatório térmico 200 L", desc, Comprimento=0.95)
    c.type("Reservatório térmico 500 L", desc, Comprimento=1.6, Diametro=0.72)
    c.mep = {"Fixture": {"drain_units": 0, "supply_weight": 0, "hot_water": True}}
    c.material("Alumínio corrugado", (196, 198, 200), "Metal", "Satin")
    c.preview_size = (1.4, 0.8, 0.85)

    zc = f"{D}/2 + 0.12"  # the axis, above the saddles
    xl = f"-{L}/2"
    c.box("Reservatório simplificado", xl, f"-{D}/2", 0, L, D, f"{D} + 0.12", "Alumínio corrugado", detail=COARSE, in_plan=True)
    c.cyl_x("Corpo", 0, zc, f"{xl} + 0.04", f"{D}/2", f"{L} - 0.08", "Alumínio corrugado", in_plan=True)
    for side, x in (("esquerda", xl), ("direita", f"{L}/2 - 0.04")):
        c.cyl_x(f"Tampa {side}", 0, zc, x, f"{D}/2 - 0.01", 0.04, "Plástico cinza")
    for k in range(1, 6):  # the corrugation rings
        c.cyl_x(f"Anel {k}", 0, zc, f"{xl} + {k}*{L}/6 - 0.005", f"{D}/2 + 0.003", 0.01, "Alumínio anodizado", detail=FINE)
    # Saddles.
    for side, s in (("esquerdo", -1), ("direito", 1)):
        x = f"{s}*{L}*0.3 - 0.04"
        c.profile(f"Berço {side}", "Front", [(x, 0), (f"{x} + 0.08", 0), (f"{x} + 0.08", f"{zc} - {D}*0.42"), (x, f"{zc} - {D}*0.42")],
                  f"-{D}*0.42", f"{D}*0.84", "Aço pintado preto")
    # Pipe stubs: cold in low at the left end, hot out high at the right, solar loop, drain; the heater box.
    stubs = (("Entrada de água fria", xl, f"{zc} - {D}*0.3", "ColdWater", "Left"),
             ("Saída de água quente", f"{L}/2", f"{zc} + {D}*0.3", "HotWater", "Right"),
             ("Retorno dos coletores", f"{L}/2", f"{zc} - {D}*0.1", "HotWater", "Right"),
             ("Ida aos coletores", xl, f"{zc} - {D}*0.38", "ColdWater", "Left"))
    for name, x, z, system, direction in stubs:
        x0 = f"{x} - 0.06" if direction == "Left" else x
        c.cyl_x(name, 0, z, x0, 0.012, 0.06, "Cobre")
        c.connector(name, system, f"{x} - 0.06" if direction == "Left" else f"{x} + 0.06", 0, z, direction, 0.022)
    c.box("Caixa da resistência", f"{L}/2", f"-{D}*0.2", f"{zc} + {D}*0.02", 0.05, f"{D}*0.25", 0.1, "Plástico cinza")
    c.cyl_x("Respiro", f"{D}*0.25", f"{zc} + {D}*0.42", f"{L}/2 - 0.04", 0.008, 0.05, "Cobre", detail=FINE)
    return c
