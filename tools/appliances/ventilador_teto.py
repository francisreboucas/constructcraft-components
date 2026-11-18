"""Ventilador de teto com luminária: canopy, downrod, motor housing, three or four blades on irons, light kit and pull chains."""

from kit import *
from _mobilia import EPS, Grp, polar, turned, at


def build():
    c = Component("Ventilador de teto com luminária", "lighting", "ventilador-teto", "Lighting")
    D = c.param("Diametro", 1.3)
    NP = c.param("Pas", 4, "Number")
    HS = c.param("Haste", 0.1, "Length", True)
    A = c.angle("AnguloPas", 0, open_at=30)
    c.type("Ventilador de teto 4 pás 130 cm", "Ventilador de teto com 4 pás e luminária de vidro jateado; motor e lâmpadas, 150 VA")
    c.type("Ventilador de teto 3 pás 105 cm", "Ventilador de teto com 3 pás e luminária de vidro jateado; motor e lâmpadas, 150 VA",
           Diametro=1.05, Pas=3)
    c.mep = {"Device": {"device": "CeilingLight", "power": 150}}
    c.preview_base = 3.0 - 0.63  # component_place hangs ceiling lights at the level's height (3 m in a new project)
    c.preview_size = (1.3, 1.3, 0.63)
    c.material("Vidro jateado", (236, 238, 236), "Glass", "Satin", 0.25)

    body, chrome, blade_mat = "Aço pintado branco", "Cromado", "Madeira escura"
    R = f"({D}/2)"
    zr = f"(-0.075 - {HS})"  # bottom of the downrod
    zm = f"({zr} - 0.01)"  # top of the motor housing
    zb = f"({zm} - 0.095)"  # underside of the rotor, where the blade irons are screwed
    zs = f"({zb} - 0.07)"  # bottom of the switch housing
    ze = f"({zs} - 0.24)"  # ends of the pull chains

    def z(base, d):
        return at(base, d)

    # Coarse stand-ins: the hanging body and the disc the blades sweep.
    c.cyl("Corpo simplificado", 0, 0, z(zs, -0.11), 0.105, f"-({z(zs, -0.11)})", body, detail=COARSE)
    c.cyl("Varredura das pás", 0, 0, z(zb, -0.014), R, 0.014, blade_mat, detail=COARSE, in_plan=True)

    # Canopy on the ceiling, with its ball joint, and the downrod.
    turned(c, "Canopla", 0, 0, [(0.028, -0.075), (0.036, -0.068), (0.05, -0.058), (0.06, -0.045), (0.065, -0.025), (0.066, -0.008), (0.066, 0)],
           body)
    turned(c, "Anel da canopla", 0, 0, [(0.0675, -0.012), (0.0675, -0.006)], chrome, detail=FINE)
    for name, x0 in (("esquerdo", -0.0685), ("direito", 0.066)):
        c.cyl_x(f"Parafuso da canopla {name}", 0, -0.02, x0, 0.004, 0.0025, chrome, detail=FINE)
    turned(c, "Rótula da haste", 0, 0, [(0.012, -0.096), (0.02, -0.088), (0.022, -0.08), (0.02, -0.072)], body, detail=FINE)
    c.cyl("Haste", 0, 0, zr, 0.011, f"-0.07 - {zr}", body)
    turned(c, "Acoplamento da haste", 0, 0, [(0.022, z(zr, -0.01)), (0.026, z(zr, 0.0)), (0.026, z(zr, 0.03)), (0.016, z(zr, 0.045))], body)
    c.cyl_x("Pino do acoplamento", 0, z(zr, 0.018), -0.03, 0.0035, 0.06, chrome, detail=FINE)

    # Motor housing, rotor and switch housing.
    turned(c, "Carcaça do motor", 0, 0, [(0.105, z(zm, -0.07)), (0.105, z(zm, -0.045)), (0.1, z(zm, -0.035)), (0.088, z(zm, -0.025)),
                                         (0.068, z(zm, -0.015)), (0.045, z(zm, -0.006)), (0.03, zm)], body, in_plan=True)
    for name, d in (("superior", -0.045), ("inferior", -0.068)):
        turned(c, f"Friso {name} do motor", 0, 0, [(0.1062, z(zm, d - 0.003)), (0.1062, z(zm, d))], chrome, detail=FINE)
    for i in range(12):  # cooling slots around the housing
        a = f"{i * 30 + 15}"
        pts = [polar(a, 0.1045, -0.006), polar(a, 0.1058, -0.006), polar(a, 0.1058, 0.006), polar(a, 0.1045, 0.006)]
        c.extrusion(f"Respiro do motor {i + 1}", pts, z(zm, -0.062), 0.012, "Plástico preto", detail=FINE)
    turned(c, "Rotor", 0, 0, [(0.104, zb), (0.106, z(zb, 0.004)), (0.106, z(zb, 0.025))], body)
    turned(c, "Caixa de comando", 0, 0, [(0.06, zs), (0.085, z(zs, 0.005)), (0.1, z(zs, 0.02)), (0.098, z(zs, 0.04)), (0.08, z(zs, 0.07))], body)
    turned(c, "Friso da caixa de comando", 0, 0, [(0.1005, z(zs, 0.019)), (0.1005, z(zs, 0.023))], chrome, detail=FINE)

    # Light kit: fitter with thumbscrews, frosted glass bowl, finial.
    turned(c, "Suporte da luminária", 0, 0, [(0.05, z(zs, -0.018)), (0.055, z(zs, -0.004)), (0.058, zs)], body)
    c.cyl_x("Parafuso do suporte esquerdo", 0, z(zs, -0.01), -0.062, 0.003, 0.006, chrome, detail=FINE)
    c.cyl_x("Parafuso do suporte direito", 0, z(zs, -0.01), 0.056, 0.003, 0.006, chrome, detail=FINE)
    c.cyl_y("Parafuso do suporte frontal", 0, z(zs, -0.01), -0.062, 0.003, 0.006, chrome, detail=FINE)
    turned(c, "Difusor de vidro", 0, 0, [(0.012, z(zs, -0.112)), (0.035, z(zs, -0.108)), (0.06, z(zs, -0.098)), (0.08, z(zs, -0.082)),
                                         (0.088, z(zs, -0.064)), (0.085, z(zs, -0.048)), (0.068, z(zs, -0.03)), (0.05, z(zs, -0.017))],
           "Vidro jateado")
    turned(c, "Arremate do difusor", 0, 0, [(0.004, z(zs, -0.128)), (0.008, z(zs, -0.124)), (0.012, z(zs, -0.116)), (0.012, z(zs, -0.112))],
           chrome, detail=FINE)

    # Pull chains, fan and light, hanging beside the bowl.
    for name, sx in (("da luz", -1), ("do ventilador", 1)):
        cx, cy = sx * 0.0725, -0.0725
        c.cyl(f"Saída da corrente {name}", cx, cy, z(zs, 0.012), 0.004, 0.01, chrome, detail=FINE)
        c.cyl(f"Corrente {name}", cx, cy, ze, 0.0012, f"{z(zs, 0.012)} - {ze}", chrome)
        turned(c, f"Puxador da corrente {name}", cx, cy, [(0.002, z(ze, -0.036)), (0.006, z(ze, -0.03)), (0.0075, z(ze, -0.016)), (0.0035, z(ze, -0.004)),
                                                           (0.002, ze)], "Latão", detail=FINE)

    # Blades on their irons; the fourth one folds into the motor when the type has three.
    for i in range(4):
        g = Grp(c) if i < 3 else Grp(c, f"min(1, max({EPS}, {NP} - 3))", (0, 0, z(zm, -0.04)))
        a = f"({A} + {i}*360/{NP})"
        n = i + 1
        iron = [(0.088, -0.016), (0.16, -0.02), (0.27, -0.03), (0.28, 0), (0.27, 0.03), (0.16, 0.02), (0.088, 0.016)]
        g.profile(f"Suporte da pá {n}", "Plan", [polar(a, r, s) for r, s in iron], z(zb, -0.006), 0.006, chrome)
        blade = [(0.17, -0.055), (f"{R} - 0.07", -0.07, 0.07), (f"{R} - 0.07", 0.07), (0.17, 0.055)]
        pts = []
        for q in blade:
            x, y = polar(a, q[0], q[1])
            pts.append((x, y, q[2]) if len(q) > 2 else (x, y))
        g.profile(f"Pá {n}", "Plan", pts, z(zb, -0.014), 0.008, blade_mat, in_plan=True)
        for k, (r, s) in enumerate(((0.19, 0), (0.235, -0.016), (0.235, 0.016)), 1):
            x, y = polar(a, r, s)
            g.cyl(f"Parafuso da pá {n}.{k}", x, y, zb, 0.0045, 0.003, chrome, detail=FINE)
        for k, s in enumerate((-0.009, 0.009), 1):
            x, y = polar(a, 0.097, s)
            g.cyl(f"Parafuso do suporte da pá {n}.{k}", x, y, z(zb, -0.009), 0.004, 0.003, chrome, detail=FINE)
    return c
