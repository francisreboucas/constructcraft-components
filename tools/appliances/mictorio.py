"""Mictório sifonado de louça, suspenso na parede: concha com a boca aberta à frente, cuba com grelha do ralo e sifão
integrado, espalhador de água sob a cobertura, registro de pressão com tubo de ligação e spud, parafusos de fixação."""

from _sanitarios import *

POWER = 2.4  # how square the plan of the shell is (2 = ellipse)

# Levels of the shell, as fractions of the height from its bottom, with the outer half width
# (fraction of Largura / 2) and the outer depth from the wall (fraction of Profundidade).
BASE = [(0.0, 0.5, 0.46), (0.03, 0.72, 0.66), (0.08, 0.88, 0.82), (0.14, 0.95, 0.92)]
# The bowl, to its lip: (level, half width, depth, thickness of its wall at that level).
BOWL = [(0.14, 0.95, 0.92, 0.05), (0.2, 0.98, 0.97, 0.032), (0.26, 1.0, 1.0, 0.022), (0.3, 1.0, 1.0, 0.017)]
# The sides of the mouth: (level, half width, depth, how far the mouth opens: fraction of the half width).
MOUTH = [(0.3, 1.0, 1.0, 0.04), (0.315, 1.0, 0.99, 0.4), (0.35, 1.0, 0.96, 0.6), (0.41, 1.0, 0.9, 0.7), (0.5, 1.0, 0.82, 0.76),
         (0.62, 1.0, 0.74, 0.78), (0.72, 1.0, 0.68, 0.76), (0.79, 1.0, 0.63, 0.7), (0.835, 1.0, 0.6, 0.56), (0.86, 1.0, 0.585, 0.25)]
HOOD = [(0.86, 1.0, 0.585), (0.9, 0.99, 0.565), (0.95, 0.955, 0.52), (0.98, 0.9, 0.47), (1.0, 0.8, 0.4)]
WALL = 0.016  # thickness of the sides
BACK = 0.03  # thickness of the back against the wall


def build():
    c = Component("Mictório", "plumbing", "mictorio", "Plumbing")
    L = c.param("Largura", 0.35)
    D = c.param("Profundidade", 0.3)
    A = c.param("Altura", 0.6)
    E = c.param("Elevacao", 0.6, instance=True)
    c.type("Mictório sifonado", "Mictório de louça com registro de pressão")
    c.type("Mictório sifonado compacto", "Mictório de louça sifonado de dimensões reduzidas", Largura=0.3, Profundidade=0.27, Altura=0.5)
    c.mep = {"Fixture": {"drain_units": 2, "supply_weight": 0.3, "hot_water": False}}
    zv = V(E) + V(A) + 0.2  # the pressure valve, on the wall above the urinal
    c.connector("Esgoto", "Sanitary", 0, V(D) / 2, V(E) + 0.05, "Back", 0.04)
    c.connector("Água fria", "ColdWater", 0, V(D) / 2, zv, "Back", 0.02)
    c.preview_base = 0.55
    c.preview_size = (0.4, 0.35, 0.9)

    yw = V(D) / 2  # the wall

    def z(h):
        return V(E) + V(A) * h

    def radii(wf, df, inset=0.0):
        return V(L) / 2 * wf - inset, V(D) * df - inset

    def angles(a0, a1, n):
        return [a0 + (a1 - a0) * i / n for i in range(n + 1)]

    def closed(wf, df, n=32):
        rx, ry = radii(wf, df)
        return soval(0, yw, rx, ry, angles(0, -180, n), POWER)

    def horseshoe(wf, df, t, n=32):
        rx, ry = radii(wf, df)
        return soval(0, yw, rx, ry, angles(0, -180, n), POWER) + soval(0, yw, rx - t, ry - t, angles(-180, 0, n), POWER)

    def arm(wf, df, frac, side, k=12):
        rx, ry = radii(wf, df)
        tip = -angle_for_x(frac, POWER)
        pts = soval(0, yw, rx, ry, angles(0, tip, k), POWER) + soval(0, yw, rx - WALL, ry - WALL, angles(tip, 0, k), POWER)
        return pts if side > 0 else [(-x, y) for x, y in reversed(pts)]

    # --- coarse stand-in: the shell's volume, closed ---
    loft_x(c, "Corpo simplificado", [(z(h), closed(w, d, 12)) for h, w, d in ((0, 0.5, 0.46), (0.3, 1, 1), (0.86, 1, 0.585), (1, 0.8, 0.4))],
           "Louça", COARSE, in_plan=True)
    c.box("Registro simplificado", -0.03, yw - 0.05, zv - 0.03, 0.06, 0.05, 0.06, "Cromado", COARSE)
    c.cyl("Tubo simplificado", 0, yw - 0.045, z(1), 0.01, 0.06, "Cromado", COARSE)

    # --- the shell: back against the wall, base with the siphon, bowl, the two sides of the mouth, hood ---
    levels = [lv for lv in BASE] + [lv[:3] for lv in BOWL[1:]] + [lv[:3] for lv in MOUTH[1:]] + [lv for lv in HOOD[1:]]
    right = [(V(L) / 2 * w, z(h)) for h, w, d in levels]
    left = [(-V(L) / 2 * w, z(h)) for h, w, d in reversed(levels)]
    c.profile("Costas", "Front", right + left, yw - BACK, BACK, "Louça")
    loft_x(c, "Base", [(z(h), closed(w, d)) for h, w, d in BASE], "Louça")
    loft_x(c, "Cuba", [(z(h), horseshoe(w, d, t)) for h, w, d, t in BOWL], "Louça")
    for name, side in (("Lateral direita", 1), ("Lateral esquerda", -1)):
        loft_x(c, name, [(z(h), arm(w, d, f, side)) for h, w, d, f in MOUTH], "Louça")
    loft_x(c, "Cobertura", [(z(h), closed(w, d)) for h, w, d in HOOD], "Louça")

    # --- plan symbol: the outline at the lip, the mouth, the top ---
    rx, ry = radii(1.0, 1.0)
    c.profile("Planta – contorno", "Plan", closed(1.0, 1.0), z(0.3), 0.002, "Louça")
    c.profile("Planta – boca", "Plan", soval(0, yw - BACK, rx - 0.03, ry - BACK - 0.03, angles(0, -180, 32), POWER), z(0.3), 0.002, "Louça")
    c.profile("Planta – topo", "Plan", closed(0.8, 0.4), z(1), 0.002, "Louça")
    for name in ("Planta – contorno", "Planta – boca", "Planta – topo"):
        c.plan_only(name)

    # --- inside: drain grate on the bowl's floor, water spreader under the hood, fixing screws ---
    zf = z(0.14)
    yd = yw - BACK - 0.075
    c.rev("Grelha do ralo", "Front", [(0, zf), (0.034, zf), (0.034, zf + 0.0025), (0.026, zf + 0.004), (0, zf + 0.0045)], yd, 0, "Cromado",
          in_plan=True)
    for i, r in enumerate((0.009, 0.016, 0.023), 1):
        c.rev(f"Furos da grelha {i}", "Front", [(r - 0.0018, zf + 0.004), (r + 0.0018, zf + 0.004), (r + 0.0018, zf + 0.0048), (r - 0.0018, zf + 0.0048)],
              yd, 0, "Plástico preto", detail=FINE)
    c.cyl_x("Espalhador de água", yw - BACK - 0.012, z(0.86) - 0.011, -0.05, 0.012, 0.1, "Branco", FINE)
    for side, x in (("esquerdo", -0.065), ("direito", 0.065)):
        c.cyl_y(f"Arruela do parafuso {side}", x, z(0.74), yw - BACK - 0.002, 0.011, 0.002, "Plástico cinza claro", FINE)
        c.rev(f"Capa do parafuso {side}", "Plan", [(x, yw - BACK - 0.002), (V(x) + 0.008, yw - BACK - 0.002), (V(x) + 0.008, yw - BACK - 0.006, 0.006),
                                                    (x, yw - BACK - 0.009)], z(0.74), x, "Cromado", detail=FINE)

    # --- pressure valve (registro de pressão) on the wall; below it the outlet and the bent tube down to the spud ---
    c.rev("Canopla do registro", "Plan", [(0, yw), (0.036, yw), (0.036, yw - 0.003), (0.03, yw - 0.008), (0, yw - 0.009)], zv, 0, "Cromado")
    c.rev("Acabamento do registro", "Plan", [(0, yw - 0.008), (0.017, yw - 0.008), (0.017, yw - 0.032), (0.014, yw - 0.036), (0, yw - 0.036)],
          zv, 0, "Cromado")
    c.cyl_y("Cubo da alavanca", 0, zv, yw - 0.05, 0.012, 0.015, "Cromado", FINE)
    c.box("Alavanca do registro", -0.004, yw - 0.049, zv - 0.065, 0.008, 0.012, 0.065, "Cromado")
    c.cyl_y("Indicador do registro", 0, zv, yw - 0.052, 0.006, 0.0025, "Plástico azul", FINE)
    yt = yw - 0.045  # the tube's axis, down to the spud
    zo = z(1) + 0.075  # the wall outlet, below the valve
    c.cyl_y("Canopla da saída", 0, zo, yw - 0.006, 0.022, 0.006, "Cromado")
    c.cyl_y("Porca da saída", 0, zo, yw - 0.018, 0.0115, 0.012, "Cromado", FINE)
    path = [(yw - 0.012, zo)] + arc(yw - 0.025, zo - 0.02, 0.02, 90, 180, n=6) + [(yt, z(1) + 0.012)]
    tube(c, "Tubo de ligação", "Side", path, 0, 0.0075, "Cromado", n=12)
    c.cyl("Anel de vedação do spud", 0, yt, z(1), 0.021, 0.003, "Borracha", FINE)
    c.rev("Porca do spud", "Front", [(0, z(1) + 0.003), (0.019, z(1) + 0.003), (0.019, z(1) + 0.011), (0.014, z(1) + 0.015), (0, z(1) + 0.015)],
          yt, 0, "Cromado")
    return c
