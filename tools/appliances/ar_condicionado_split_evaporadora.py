"""Ar-condicionado split - evaporadora: the hi-wall indoor unit.

Frame: wall device. The back is on the wall at y = 0, the body goes from
y = -Profundidade to 0, the bottom is at z = 0 (the mounting height is set by
the user) and the unit is centered on x = 0. The outlet is a channel cut at
45 degrees in the lower front edge; the louver that closes it is hinged at its
lower rear edge and drops with AnguloAleta.
"""

from kit import *

K = 0.70710678  # cos 45 = sin 45


def build() -> Component:
    c = Component("Ar-condicionado split - evaporadora", "furniture", "ar-condicionado-split-evaporadora", "Furniture")
    L = c.param("Largura", 0.80)
    P = c.param("Profundidade", 0.20)
    H = c.param("Altura", 0.29)
    A = c.angle("AnguloAleta", 0, open_at=50)

    c.type("Evaporadora split 9.000 a 12.000 BTU", "Unidade interna hi-wall de 9.000 a 12.000 BTU/h, 80 x 20 x 29 cm")
    c.type("Evaporadora split 18.000 a 24.000 BTU", "Unidade interna hi-wall de 18.000 a 24.000 BTU/h, 105 x 23 x 33 cm",
           Largura=1.05, Profundidade=0.23, Altura=0.33)

    W, GREY, DARK = "Branco", "Plástico cinza claro", "Plástico cinza"
    yb = -0.004  # back of the body: the mounting plate fills the rest up to the wall
    d = f"(0.42*{P})"  # the outlet face runs at 45 degrees from (-P + d, 0) to (-P, d)
    chord = f"(0.594*{P})"
    dn = f"(0.2*{P})"  # depth of the outlet channel, square to its face
    capw = 0.022
    R = f"(0.8*sqrt(0.2025*{P}*{P} + 0.1444*{H}*{H}))"  # radius of the front curve
    hinge = (f"(-{P} + {d})", 0)

    def q(s, t):
        """Side (y, z) of a point of the outlet: s up along its face from the hinge, t out of it."""
        return (f"-{P} + {d} - ({p(s)} + {p(t)})*{K}", f"({p(s)} - {p(t)})*{K}")

    def outline(g=0.0, grooves=False, notch=False):
        """The body's side outline, grown outwards by g."""
        pts = [(yb, -g), (yb, f"{H} + {g}")]
        if grooves:
            for k in range(7):
                ys = f"(-{0.10 + 0.06 * k:.2f}*{P})"
                pts += [(ys, f"{H} + {g}"), (ys, f"{H} - 0.008"), (f"{ys} - 0.03*{P}", f"{H} - 0.008"), (f"{ys} - 0.03*{P}", f"{H} + {g}")]
        pts += [(f"-0.55*{P}", f"{H} + {g}", f"{R} + {g}"), (f"-{P} - {g}", f"0.62*{H}"), (f"-{P} - {g}", f"{d} - {0.4 * g}")]
        if notch:
            pts += [q(chord, f"-{dn}"), q(0, f"-{dn}")]
        pts += [(f"-{P} + {d} - {0.4 * g}", -g)]
        return pts

    xin = f"(-{L}/2 + {capw})"  # inner body, between the caps
    win = f"({L} - {2 * capw})"

    # --- coarse stand-in ----------------------------------------------------
    c.profile("Corpo simplificado", "Side", outline(), f"-{L}/2", L, W, detail=COARSE, in_plan=True)

    # --- body -----------------------------------------------------------------
    c.profile("Corpo", "Side", outline(grooves=True, notch=True), xin, win, W)
    # the chassis inside the body draws the clean plan outline (the body's own would show every groove)
    c.box("Chassi", xin, f"-{P} + 0.0005", f"0.5*{H}", win, f"{P} - 0.0005 + {yb}", f"0.1*{H}", GREY, in_plan=True)
    c.profile("Tampa lateral esquerda", "Side", outline(0.0015), f"-{L}/2", capw, W, in_plan=True)
    c.profile("Tampa lateral direita", "Side", outline(0.0015), f"{L}/2 - {capw}", capw, W, in_plan=True)
    g = 0.0025
    c.profile("Painel frontal", "Side",
              [(f"-0.5*{P}", f"{H} + {g}", f"{R} + {g}"), (f"-{P} - {g}", f"0.62*{H}"), (f"-{P} - {g}", f"{d} + 0.006"),
               (f"-{P} + 0.01", f"{d} + 0.006"), (f"-{P} + 0.01", f"0.62*{H}"), (f"-0.5*{P}", f"{H} - 0.01")],
              f"{xin} + 0.004", f"{win} - 0.008", W)
    c.box("Friso do painel", f"{xin} + 0.004", f"-{P} - 0.0032", f"{d} + 0.006", f"{win} - 0.008", 0.004, 0.004, "Alumínio anodizado")

    # top intake: the grooves of the body are the slats; filter underneath, ribs across
    c.box("Filtro de ar", f"{xin} + 0.002", f"-0.5*{P}", f"{H} - 0.0085", f"{win} - 0.004", f"0.41*{P}", 0.001, DARK)
    nr = 11
    for k in range(nr):
        c.box(f"Grade superior - nervura {k + 1}", f"{xin} + {(k + 0.5) / nr:.4f}*{win} - 0.0015", f"-0.49*{P}", f"{H} - 0.008", 0.003, f"0.39*{P}", 0.0075,
              W, detail=FINE)
    for k in range(2):
        c.box(f"Filtro de ar - puxador {k + 1}", f"{'-' if k == 0 else ''}0.22*{L} - 0.02", f"-0.52*{P}", f"{H} - 0.004", 0.04, 0.012, 0.0048, GREY, detail=FINE)

    # --- outlet channel ---------------------------------------------------------
    def chan(name, s0, s1, t0, t1, x, width, material, detail=FULL):
        c.profile(name, "Side", [q(s0, t0), q(s0, t1), q(s1, t1), q(s1, t0)], x, width, material, detail=detail)

    chan("Saída de ar - fundo", 0, chord, f"-{dn}", f"-{dn} + 0.002", xin, win, DARK)
    chan("Saída de ar - parede superior", f"{chord} - 0.002", chord, f"-{dn}", -0.001, xin, win, DARK)
    chan("Saída de ar - parede inferior", 0, 0.002, f"-{dn}", -0.001, xin, win, DARK)
    chan("Saída de ar - parede esquerda", 0, chord, f"-{dn}", -0.001, xin, 0.002, DARK)
    chan("Saída de ar - parede direita", 0, chord, f"-{dn}", -0.001, f"{xin} + {win} - 0.002", 0.002, DARK)
    ty, tz = q(f"0.5*{chord}", f"-{dn} - 0.022")
    c.cyl_x("Turbina tangencial", ty, tz, f"{xin} + 0.03", 0.036, f"{win} - 0.09", "Plástico preto")
    c.cyl_x("Motor da turbina", ty, tz, f"{xin} + {win} - 0.06", 0.03, 0.05, "Aço galvanizado", detail=FINE)
    c.cyl_x("Mancal da turbina", ty, tz, f"{xin} + 0.012", 0.012, 0.018, "Borracha", detail=FINE)
    chan("Aleta interna", f"0.5*{chord} - 0.001", f"0.5*{chord} + 0.001", f"-{dn} + 0.004", -0.012, f"{xin} + 0.004", f"{win} - 0.008", GREY)
    nf = 16
    for k in range(nf):
        chan(f"Defletor vertical {k + 1}", f"0.12*{chord}", f"0.88*{chord}", f"-{dn} + 0.002", f"-0.4*{dn}",
             f"{xin} + {(k + 0.5) / nf:.4f}*{win} - 0.001", 0.002, GREY, detail=FINE)
    chan("Haste dos defletores", f"0.3*{chord}", f"0.3*{chord} + 0.004", f"-0.4*{dn} - 0.006", f"-0.4*{dn} - 0.002", f"{xin} + 0.02", f"{win} - 0.04", DARK, detail=FINE)

    # --- louver: drops about its lower rear edge ----------------------------------
    ang = f"(45 + {A})"
    lx, lw = f"({xin} + 0.004)", f"({win} - 0.008)"
    c.flap_box("Aleta horizontal", hinge, ang, lx, lw, 0.003, f"{chord} - 0.003", -0.001, 0.004, W)
    c.flap_box("Aleta horizontal - borda", hinge, ang, lx, lw, f"{chord} - 0.008", f"{chord} - 0.003", 0.004, 0.0055, W, detail=FINE)
    for k in range(5):
        c.flap_box(f"Aleta horizontal - nervura {k + 1}", hinge, ang, f"{lx} + {(k + 0.5) / 5:.2f}*{lw} - 0.002", 0.004,
                   0.006, f"0.8*{chord}", -0.004, -0.001, W, detail=FINE)
    for k, x in enumerate((f"{lx} - 0.003", f"{lx} + {lw}/2 - 0.004", f"{lx} + {lw} - 0.005"), 1):
        c.cyl_x(f"Aleta horizontal - pino {k}", f"-{P} + {d} - 0.004", 0.004, x, 0.004, 0.008, GREY, detail=FINE)
    c.box("Motor de passo da aleta", f"{xin} + {win} - 0.036", f"-{P} + {d} + 0.004", 0.006, 0.03, 0.03, 0.03, "Aço galvanizado", detail=FINE)

    # --- display on the right of the front panel ----------------------------------
    yp = f"(-{P} - {g})"
    dx = f"({L}/2 - 0.17)"
    dz = f"(0.62*{H} - 0.04)"
    c.box("Visor - janela", dx, f"{yp} - 0.0008", dz, 0.075, 0.001, 0.026, "Plástico fumê")
    c.box("Visor de temperatura", f"{dx} + 0.008", f"{yp} - 0.0012", f"{dz} + 0.006", 0.03, 0.001, 0.014, "Visor LED", detail=FINE)
    for k, m in enumerate(("Plástico verde", "Plástico vermelho", "Plástico azul")):
        c.cyl_y(f"Visor - LED {k + 1}", f"{dx} + 0.048 + {k}*0.009", f"{dz} + 0.008", f"{yp} - 0.0014", 0.002, 0.001, m, detail=FINE)
    c.cyl_y("Receptor infravermelho", f"{dx} + 0.057", f"{dz} + 0.018", f"{yp} - 0.0014", 0.004, 0.001, "Plástico preto brilhante", detail=FINE)
    c.box("Botão de emergência", f"{L}/2 - {capw} - 0.035", f"-{P} + {d} + 0.02", -0.0015, 0.016, 0.01, 0.002, GREY, detail=FINE)

    # --- sides and underside ---------------------------------------------------------
    c.box("Etiqueta de eficiência energética", f"{L}/2 + 0.0015", f"-0.75*{P}", f"0.3*{H}", 0.0005, f"0.4*{P}", f"0.45*{H}", "Plástico cinza claro", detail=FINE)
    c.box("Etiqueta de dados", f"-{L}/2 + 0.08", f"-0.45*{P}", -0.0004, 0.12, f"0.3*{P}", 0.0005, "Alumínio anodizado", detail=FINE)
    for k, f in enumerate((-0.3, 0.0, 0.3), 1):
        c.box(f"Tampa de parafuso {k}", f"{f}*{L} - 0.01", f"-{P} + {d} + 0.012", -0.001, 0.02, 0.012, 0.0015, GREY, detail=FINE)
    for k, sx in enumerate((-1, 1), 1):
        c.box(f"Trava do painel {k}", f"{sx}*({L}/2 - 0.0005) - 0.001", f"-0.8*{P}", f"0.55*{H}", 0.002, 0.03, 0.008, GREY, detail=FINE)
    c.box("Tampa da passagem de tubos", f"{L}/2 - 0.0005", f"-0.3*{P}", 0.012, 0.002, f"0.22*{P}", 0.06, GREY, detail=FINE)

    # --- hidden internals ---------------------------------------------------------------
    c.box("Serpentina evaporadora", f"{xin} + 0.02", f"-0.85*{P}", f"0.55*{H}", f"{win} - 0.08", f"0.6*{P}", f"0.3*{H}", "Alumínio anodizado")
    c.box("Bandeja de dreno", f"{xin} + 0.02", f"-0.4*{P}", 0.012, f"{win} - 0.04", f"0.3*{P}", 0.02, DARK, detail=FINE)
    c.box("Placa eletrônica", f"{xin} + {win} - 0.055", f"-0.7*{P}", f"0.45*{H}", 0.04, f"0.5*{P}", f"0.4*{H}", "Plástico verde", detail=FINE)

    # --- wall mounting plate --------------------------------------------------------------
    c.box("Suporte de parede", f"-{L}/2 + 0.07", yb, 0.035, f"{L} - 0.14", 0.004, f"{H} - 0.06", "Aço galvanizado")
    for k, sx in enumerate((-1, 1), 1):
        c.box(f"Suporte de parede - gancho {k}", f"{sx}*0.3*{L} - 0.03", yb - 0.006, f"{H} - 0.04", 0.06, 0.006, 0.012, "Aço galvanizado", detail=FINE)
        c.box(f"Suporte de parede - trava inferior {k}", f"{sx}*0.3*{L} - 0.02", yb - 0.006, 0.04, 0.04, 0.006, 0.01, "Aço galvanizado", detail=FINE)
    for k, (fx, fz) in enumerate(((-0.36, 0.78), (0, 0.78), (0.36, 0.78), (-0.36, 0.3), (0, 0.3), (0.36, 0.3)), 1):
        c.cyl_y(f"Suporte de parede - parafuso {k}", f"{fx}*{L}", f"{fz}*{H}", yb + 0.0035, 0.005, 0.001, "Aço pintado preto", detail=FINE)

    # --- refrigerant lines, drain and cable leaving through the wall at the back right ------
    px = f"({L}/2 - 0.085)"
    c.cyl_y("Tubo de gás - isolamento", px, 0.07, yb, 0.012, 0.074, "Borracha cinza")
    c.cyl_y("Tubo de gás", px, 0.07, yb, 0.0065, 0.10, "Cobre", detail=FINE)
    c.cyl_y("Tubo de líquido - isolamento", f"{px} + 0.027", 0.07, yb, 0.009, 0.074, "Borracha cinza")
    c.cyl_y("Tubo de líquido", f"{px} + 0.027", 0.07, yb, 0.0035, 0.10, "Cobre", detail=FINE)
    c.cyl_y("Mangueira de dreno", f"{px} + 0.012", 0.047, yb, 0.008, 0.11, "Plástico cinza claro")
    c.cyl_y("Cabo de interligação", f"{px} - 0.012", 0.047, yb, 0.0045, 0.10, "Borracha", detail=FINE)
    c.cyl_y("Fita de acabamento dos tubos", f"{px} + 0.01", 0.06, 0.03, 0.028, 0.012, "Branco", detail=FINE)
    return c
