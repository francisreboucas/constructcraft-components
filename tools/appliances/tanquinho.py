"""Tanquinho: lavadora semiautomática de cesto único, com batedor central.

Frame of the floor appliances: centered at the origin, the wall at
y = Profundidade/2 (the cabinet's back stands 3 cm off it, where the hoses run).
The cabinet is a ring around the round tub; the lid is hinged at the front of
the back console and lifts with `AnguloTampa`.
"""

import math

from kit import *
from _aparelhos import num, ring_rrect_hole, sphere
from lavadora_frontal import foot


def build() -> Component:
    c = Component("Tanquinho", "plumbing", "tanquinho", "Plumbing")
    W = c.param("Largura", 0.52)
    D = c.param("Profundidade", 0.55)
    H = c.param("Altura", 0.90)
    AP = c.param("AlturaPainel", 0.10)
    DC = c.param("DiametroCesto", 0.40)
    AC = c.param("AlturaCesto", 0.46)
    ang = c.angle("AnguloTampa", 0, open_at=80)

    white, grey = "Branco", "Plástico cinza claro"
    xl, xr = f"(-{W}/2)", f"({W}/2)"
    YF, YB, YW = f"(-{D}/2)", f"({D}/2 - 0.03)", f"({D}/2)"
    CP = 0.10  # depth of the console
    YP = f"({YB} - {CP})"  # front of the console
    ZP = 0.025  # bottom of the cabinet, on the feet
    ZD = f"({H} - {AP})"  # top of the deck
    ED = 0.025  # thickness of the deck
    YC = f"(({YF} + {YB})/2 - 0.02)"  # axis of the tub
    RT = f"({DC}/2 + 0.005)"  # outer radius of the tub = hole of the cabinet
    RH = f"({RT} - 0.035)"  # opening in the deck
    RC = 0.07  # corner radius of the cabinet
    ZT0 = f"({ZD} - {ED} - {AC})"  # bottom of the tub

    # --- coarse ---------------------------------------------------------------
    c.profile("Gabinete simplificado", "Plan", rrect(xl, YF, xr, YB, RC), 0, ZD, white, detail=COARSE, in_plan=True)
    c.box("Painel simplificado", f"{xl} + 0.02", YP, ZD, f"{W} - 0.04", CP, AP, white, detail=COARSE, in_plan=True)
    hinge = (f"{YP} - 0.002", f"{ZD} + 0.004")
    LT = f"({YP} - 0.002 - {YF} - 0.012)"  # length of the lid
    c.lid_box("Tampa simplificada", hinge, ang, f"{xl} + 0.025", f"{W} - 0.05", 0, LT, 0, 0.02, "Plástico fumê", detail=COARSE)

    # --- cabinet: a ring around the tub, the deck, the base ---------------------------
    c.profile("Gabinete", "Plan", ring_rrect_hole(xl, YF, xr, YB, RC, 0, YC, RT), ZP, f"{ZD} - {ED} - {ZP}", white)
    c.profile("Tampo do gabinete", "Plan", ring_rrect_hole(xl, YF, xr, YB, RC, 0, YC, RH), f"{ZD} - {ED}", ED, white)
    c.rev("Borda da abertura", "Front", rect(RH, ZD, f"{RH} + 0.014", f"{ZD} + 0.004"), YC, 0, grey, in_plan=True)
    c.profile("Base", "Plan", rrect(f"{xl} + 0.01", f"{YF} + 0.01", f"{xr} - 0.01", f"{YB} - 0.01", RC - 0.01), f"{ZP} - 0.004", 0.004, "Plástico cinza")
    # The plan outline (the cabinet's ring would draw the slit that reaches its hole).
    c.profile("Contorno em planta", "Plan", rrect(xl, YF, xr, YB, RC), f"{ZP}", 0.002, white, in_plan=True)
    c.box("Rodapé - friso", f"{xl} + {RC}", f"{YF} - 0.0008", f"{ZP} + 0.03", f"{W} - 2*{RC}", 0.0008, 0.006, "Plástico azul", detail=FINE)
    c.box("Friso superior", f"{xl} + {RC}", f"{YF} - 0.0008", f"{ZD} - 0.05", f"{W} - 2*{RC}", 0.0008, 0.006, "Plástico azul", detail=FINE)
    c.profile("Etiqueta de capacidade", "Front", rrect(f"-{W}*0.16", f"{ZD} - 0.15", f"{W}*0.16", f"{ZD} - 0.09", 0.008), f"{YF} - 0.0008", 0.0008, "Plástico azul")
    c.box("Etiqueta de capacidade - texto", f"-{W}*0.11", f"{YF} - 0.0011", f"{ZD} - 0.124", f"{W}*0.22", 0.0003, 0.008, white, detail=FINE)
    # Grips moulded into the sides.
    for name, x, sgn in (("esquerda", xl, -1), ("direita", xr, 1)):
        x0 = f"{x} - 0.002" if sgn < 0 else x
        c.box(f"Pega lateral {name}", x0, f"{YC} - 0.08", f"{ZD} - 0.11", 0.002, 0.16, 0.035, "Plástico cinza")
        c.box(f"Pega lateral {name} - sombra", f"{x} - 0.0025" if sgn < 0 else f"{x} + 0.002", f"{YC} - 0.07", f"{ZD} - 0.1", 0.0005, 0.14, 0.012, "Plástico preto", detail=FINE)
    # Feet.
    for name, x, y in (("dianteiro esquerdo", f"{xl} + 0.06", f"{YF} + 0.06"), ("dianteiro direito", f"{xr} - 0.06", f"{YF} + 0.06"),
                       ("traseiro esquerdo", f"{xl} + 0.06", f"{YB} - 0.06"), ("traseiro direito", f"{xr} - 0.06", f"{YB} - 0.06")):
        foot(c, f"Pé {name}", x, y, f"{ZP} - 0.004")

    # --- tub, agitator, lint filter ------------------------------------------------------
    w = 0.005
    top = f"({ZD} - {ED})"
    c.rev("Cesto", "Front", [(0, ZT0), (f"{RT} - 0.03", ZT0), (f"{RT} - 0.001", f"{ZT0} + 0.03"), (f"{RT} - 0.001", top), (f"{RT} - 0.001 - {w}", top),
                             (f"{RT} - 0.001 - {w}", f"{ZT0} + 0.03 + {w}"), (f"{RT} - 0.03", f"{ZT0} + {w}"), (0, f"{ZT0} + {w}")], YC, 0, grey)
    for i in range(6):
        c.rev(f"Cesto - nervura {i + 1}", "Front", rect(f"{RT} - 0.001 - {w} - 0.003", f"{ZT0} + 0.08 + {i}*{AC}*0.13", f"{RT} - {w}", f"{ZT0} + 0.084 + {i}*{AC}*0.13"),
              YC, 0, grey, detail=FINE)
    zb = f"({ZT0} + {w})"
    hb = f"({AC}*0.62)"  # height of the agitator
    c.rev("Batedor - disco", "Front", [(0, zb), (f"{DC}*0.3", zb), (f"{DC}*0.3", f"{zb} + 0.008"), (f"{DC}*0.12", f"{zb} + 0.03", 0.06), (0, f"{zb} + 0.032")], YC, 0, "Plástico azul")
    c.rev("Batedor - coluna", "Front", [(0, f"{zb} + 0.03"), (0.032, f"{zb} + 0.03"), (0.024, f"{zb} + {hb}"), (0, f"{zb} + {hb}")], YC, 0, "Plástico azul")
    c.rev("Batedor - tampa", "Front", [(0, f"{zb} + {hb}"), (0.03, f"{zb} + {hb}"), (0.03, f"{zb} + {hb} + 0.012", 0.012), (0.018, f"{zb} + {hb} + 0.022"), (0, f"{zb} + {hb} + 0.024")],
          YC, 0, grey)
    # Four fins up the column and six ribs on the disc.
    for i, (name, axis) in enumerate((("esquerda", "x-"), ("direita", "x+"), ("frontal", "y-"), ("traseira", "y+"))):
        sgn = -1 if axis.endswith("-") else 1
        a, b = sgn * 0.02, sgn * 0.075
        a2 = sgn * 0.016
        if axis[0] == "x":
            pts = [(num(a), f"{zb} + 0.03"), (num(b), f"{zb} + 0.05"), (num(sgn * 0.045), f"{zb} + {hb}*0.8"), (num(a2), f"{zb} + {hb}*0.95")]
            c.profile(f"Batedor - aleta {name}", "Front", pts if sgn > 0 else pts[::-1], f"{YC} - 0.004", 0.008, "Plástico azul")
        else:
            pts = [(f"{YC} + {num(a)}", f"{zb} + 0.03"), (f"{YC} + {num(b)}", f"{zb} + 0.05"), (f"{YC} + {num(sgn * 0.045)}", f"{zb} + {hb}*0.8"), (f"{YC} + {num(a2)}", f"{zb} + {hb}*0.95")]
            c.profile(f"Batedor - aleta {name}", "Side", pts if sgn > 0 else pts[::-1], -0.004, 0.008, "Plástico azul")
    for i in range(6):
        g = math.radians(30 + 60 * i)
        cs, sn = math.cos(g), math.sin(g)
        pts = []
        for r_, s_ in ((0.045, -0.004), (0.11, -0.003), (0.11, 0.003), (0.045, 0.004)):
            pts.append((f"{num(r_ * cs - s_ * sn)}*{DC}/0.4", f"{YC} + {num(r_ * sn + s_ * cs)}*{DC}/0.4"))
        c.profile(f"Batedor - nervura {i + 1}", "Plan", pts, f"{zb} + 0.006", 0.012, "Plástico azul", detail=FINE)
    # Lint filter hanging inside the front wall.
    fy = f"({YC} - {RT} + 0.006 + {w})"
    c.box("Filtro de fiapos - moldura", -0.045, fy, f"{top} - 0.2", 0.09, 0.022, 0.16, "Plástico cinza")
    c.box("Filtro de fiapos - tela", -0.038, f"{fy} + 0.022", f"{top} - 0.19", 0.076, 0.001, 0.14, "Tela perfurada", detail=FINE)
    c.box("Filtro de fiapos - gancho", -0.015, f"{fy} - 0.004", f"{top} - 0.045", 0.03, 0.01, 0.045, "Plástico cinza", detail=FINE)
    # Soap cup on the deck, front left.
    sx, sy = f"({xl} + 0.06)", f"({YF} + 0.06)"
    c.rev("Porta-sabão", "Front", [(sx, ZD), (f"{sx} + 0.032", ZD), (f"{sx} + 0.032", f"{ZD} + 0.012"), (f"{sx} + 0.028", f"{ZD} + 0.012"), (f"{sx} + 0.026", f"{ZD} + 0.004"),
                                    (sx, f"{ZD} + 0.004")], sy, sx, grey)

    # --- console with the timer and the selector ----------------------------------------
    side = [(YP, ZD), (YB, ZD), (YB, H), (f"{YP} + 0.035", H, 0.035), (YP, f"{H} - 0.035")]
    c.profile("Painel", "Side", side, f"{xl} + 0.02", f"{W} - 0.04", white, in_plan=True)
    zk = f"({ZD} + {AP}*0.48)"
    c.profile("Painel - faixa", "Front", rrect(f"{xl} + 0.04", f"{zk} - 0.03", f"{xr} - 0.04", f"{zk} + 0.03", 0.01), f"{YP} - 0.001", 0.001, "Plástico azul")

    def knob(name, kx, r):
        c.rev(f"{name} - base", "Plan", [(kx, f"{YP} - 0.003"), (f"{kx} + {r} + 0.006", f"{YP} - 0.003"), (f"{kx} + {r} + 0.006", f"{YP} - 0.001"), (kx, f"{YP} - 0.001")],
              zk, kx, "Cromado")
        c.rev(name, "Plan", [(kx, f"{YP} - 0.026"), (f"{kx} + {r} - 0.003", f"{YP} - 0.026"), (f"{kx} + {r}", f"{YP} - 0.022"), (f"{kx} + {r}", f"{YP} - 0.003"), (kx, f"{YP} - 0.003")],
              zk, kx, grey)
        c.box(f"{name} - pega", f"{kx} - 0.005", f"{YP} - 0.04", f"{zk} - {r} + 0.004", 0.01, 0.016, f"2*{r} - 0.008", grey)
        c.box(f"{name} - marca", f"{kx} - 0.0012", f"{YP} - 0.0405", f"{zk} + {r} - 0.016", 0.0024, 0.0005, 0.01, "Plástico azul", detail=FINE)
        for i in range(10):
            g = math.radians(90 - 30 * i)
            c.box(f"{name} - escala {i + 1}", f"{kx} + {num((0.006 + 0.0) * math.cos(g))} + ({r} + 0.009)*{num(math.cos(g))} - 0.001", f"{YP} - 0.0013",
                  f"{zk} + ({r} + 0.009)*{num(math.sin(g))} - 0.001", 0.002, 0.0003, 0.002, white, detail=FINE)

    knob("Timer", f"{W}*0.24", "0.026")
    knob("Seletor de função", f"-{W}*0.24", "0.02")
    c.cyl_y("Luz piloto", 0, f"{zk} + 0.012", f"{YP} - 0.003", 0.004, 0.002, "Plástico vermelho", detail=FINE)
    c.box("Painel - etiqueta", "-0.04", f"{YP} - 0.0013", f"{zk} - 0.018", 0.08, 0.0003, 0.012, white, detail=FINE)

    # --- lid ---------------------------------------------------------------------------
    lx, lw = f"({xl} + 0.025)", f"({W} - 0.05)"
    fr = 0.03  # width of the frame
    c.lid_box("Tampa - aro traseiro", hinge, ang, lx, lw, 0, fr, 0, 0.018, grey)
    c.lid_box("Tampa - aro frontal", hinge, ang, lx, lw, f"{LT} - {fr}", LT, 0, 0.018, grey)
    c.lid_box("Tampa - aro esquerdo", hinge, ang, lx, fr, fr, f"{LT} - {fr}", 0, 0.018, grey)
    c.lid_box("Tampa - aro direito", hinge, ang, f"{lx} + {lw} - {fr}", fr, fr, f"{LT} - {fr}", 0, 0.018, grey)
    c.lid_box("Tampa - visor", hinge, ang, f"{lx} + {fr}", f"{lw} - 2*{fr}", fr, f"{LT} - {fr}", 0.008, 0.014, "Plástico fumê")
    c.lid_box("Tampa - puxador", hinge, ang, f"-{W}*0.15", f"{W}*0.3", f"{LT} - 0.006", f"{LT} + 0.012", -0.006, 0.02, grey)
    c.lid_box("Tampa - puxador - friso", hinge, ang, f"-{W}*0.13", f"{W}*0.26", f"{LT} + 0.012", f"{LT} + 0.013", 0.0, 0.014, "Plástico azul", detail=FINE)
    for i, sx_ in enumerate((-1, 1), 1):
        c.lid_box(f"Tampa - batente {i}", hinge, ang, f"{sx_}*{W}*0.3 - 0.01", 0.02, f"{LT} - 0.025", f"{LT} - 0.01", -0.004, 0, "Borracha cinza", detail=FINE)
        hx = f"{sx_}*{W}*0.3 - 0.02"
        c.cyl_x(f"Dobradiça {i}", hinge[0], hinge[1], hx, 0.006, 0.04, grey)
        c.box(f"Dobradiça {i} - base", hx, hinge[0], ZD, 0.04, 0.012, 0.004, grey, detail=FINE)

    # --- back: drain hose on its hook, inlet hose, power cable ---------------------------
    HY = f"({YB} + 0.015)"
    OX, OZ, UZ = f"({xr} - 0.12)", f"({ZP} + 0.05)", f"({ZD} - 0.06)"
    c.cyl_y("Saída de esgoto - bocal", OX, OZ, f"{YB} - 0.001", 0.016, 0.008, "Plástico cinza")
    sphere(c, "Mangueira de esgoto - curva 1", OX, HY, OZ, 0.012, "Plástico cinza", detail=FULL)
    c.cyl("Mangueira de esgoto", OX, HY, OZ, 0.012, f"{UZ} - {OZ}", "Plástico cinza")
    sphere(c, "Mangueira de esgoto - curva 2", OX, HY, UZ, 0.012, "Plástico cinza", detail=FULL)
    c.cyl_y("Mangueira de esgoto - ponta", OX, UZ, HY, 0.012, f"{YW} - {HY}", "Plástico cinza")
    c.box("Gancho da mangueira", f"{OX} - 0.02", YB, f"{UZ} - 0.03", 0.04, 0.03, 0.012, grey)
    for i in range(10):
        c.cyl(f"Mangueira de esgoto - anel {i + 1}", OX, HY, f"{OZ} + 0.03 + {i}*({UZ} - {OZ} - 0.06)/9", 0.0135, 0.005, "Plástico cinza", detail=FINE)
    VX, VZ = f"({xl} + 0.09)", f"({H} - 0.04)"
    WX = f"({VX} + 0.1)"
    c.cyl_y("Entrada de água - bocal", VX, VZ, f"{YB} - 0.001", 0.012, 0.01, "Plástico azul")
    sphere(c, "Mangueira de entrada - curva 1", VX, HY, VZ, 0.009, "Plástico translúcido", detail=FULL)
    c.cyl_x("Mangueira de entrada", HY, VZ, VX, 0.009, 0.1, "Plástico translúcido")
    sphere(c, "Mangueira de entrada - curva 2", WX, HY, VZ, 0.009, "Plástico translúcido", detail=FULL)
    c.cyl_y("Mangueira de entrada - ponta", WX, VZ, HY, 0.009, f"{YW} - {HY} - 0.008", "Plástico translúcido")
    c.cyl_y("Mangueira de entrada - porca da torneira", WX, VZ, f"{YW} - 0.01", 0.015, 0.01, "Plástico azul")
    CX, CZ = f"({xr} - 0.06)", f"({H} - 0.05)"
    c.cyl_y("Cabo de força - passa-fio", CX, CZ, f"{YB} - 0.001", 0.008, 0.01, "Plástico preto")
    sphere(c, "Cabo de força - curva", CX, f"{YB} + 0.009", CZ, 0.0045, "Borracha", detail=FINE)
    c.cyl("Cabo de força", CX, f"{YB} + 0.009", f"{CZ} - 0.4", 0.0045, 0.4, "Borracha", detail=FINE)
    c.box("Cabo de força - plugue", f"{CX} - 0.018", f"{YB} + 0.001", f"{CZ} - 0.445", 0.036, 0.018, 0.045, "Plástico preto", detail=FINE)
    for i, dx in enumerate((-0.0095, 0, 0.0095), 1):
        c.cyl(f"Cabo de força - pino {i}", f"{CX} + {dx}", f"{YB} + 0.01", f"{CZ} - 0.463", 0.002, 0.018, "Latão", detail=FINE)
    c.box("Etiqueta de identificação", f"-{W}*0.12", YB, f"{ZD} - 0.25", f"{W}*0.24", 0.0006, 0.06, "Plástico cinza claro", detail=FINE)

    c.mep = {"Fixture": {"drain_units": 3, "supply_weight": 1.0, "hot_water": False}}
    c.connector("Esgoto", "Sanitary", OX, YW, UZ, "Back", 0.04)
    c.connector("Água fria", "ColdWater", WX, YW, VZ, "Back", 0.02)

    c.type("Tanquinho 10 kg", "Lavadora semiautomática (tanquinho) de 10 kg, 52 x 55 x 90 cm, batedor central e timer; ponto de água fria e esgoto; TUG")
    c.type("Tanquinho 15 kg", "Lavadora semiautomática (tanquinho) de 15 kg, 56 x 60 x 97 cm, batedor central e timer; ponto de água fria e esgoto; TUG",
           Largura=0.56, Profundidade=0.60, Altura=0.97, DiametroCesto=0.46, AlturaCesto=0.52)
    return c
