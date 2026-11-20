"""Lavatório com cuba de apoio: a floating quartz countertop with a round vessel basin, a tall single-lever mixer, a click
waste and a chrome bottle trap into the wall."""

from _sanitarios import *

T = 0.03  # countertop
R_OUT, H_BOWL, WALL = 0.19, 0.14, 0.008  # the basin: outer radius at the rim, height, wall


def tall_mixer(c, x, y, z, height=0.3, reach=0.17):
    """A tall single-lever mixer (bica alta) on (x, y, z): a slender column, a spout at the top, a side joystick lever."""
    def zs(d):
        return add(z, d)

    c.rev("Base do misturador", "Front", [(x, z), (add(x, 0.03), z), (add(x, 0.03), zs(0.004)), (add(x, 0.025), zs(0.01)), (x, zs(0.01))], y, x,
          "Cromado")
    c.rev("Coluna do misturador", "Front", [(x, zs(0.01)), (add(x, 0.021), zs(0.01)), (add(x, 0.019), zs(height - 0.004)),
                                            (add(x, 0.015), zs(height)), (x, zs(height))], y, x, "Cromado")
    # Spout: a round tube from the top of the column forward, slightly falling.
    path = [(add(y, 0.0), zs(height - 0.025)), (add(y, -0.06), zs(height - 0.022)), (add(y, -reach + 0.01), zs(height - 0.03))]
    tube(c, "Bica do misturador", "Side", path, x, 0.011, "Cromado", n=16)
    ya = add(y, -reach)
    c.cyl("Ponteira da bica", x, ya, zs(height - 0.06), 0.012, 0.035, "Cromado")
    c.cyl("Arejador", x, ya, zs(height - 0.062), 0.009, 0.002, "Plástico cinza", FINE)
    # Lever on the right side of the column.
    c.cyl_x("Alavanca - eixo", y, zs(height - 0.1), add(x, 0.018), 0.009, 0.02, "Cromado")
    c.cyl_x("Alavanca - haste", y, zs(height - 0.1), add(x, 0.036), 0.0045, 0.06, "Cromado", FINE)
    return ya


def build():
    c = Component("Lavatório com cuba de apoio", "plumbing", "lavatorio-cuba-apoio", "Plumbing")
    L = c.param("Largura", 0.8)
    D = c.param("Profundidade", 0.55)
    A = c.param("Altura", 0.78)
    desc = ("Bancada suspensa de quartzo branco com cuba de apoio redonda de louça (Ø 38 cm), misturador monocomando de bica "
            "alta, válvula click e sifão de copo cromado; a borda da cuba fica a 92 cm do piso")
    c.type("Lavatório cuba de apoio 80x55", desc)
    c.type("Lavatório cuba de apoio 100x55", desc, Largura=1.0)
    c.type("Lavatório cuba de apoio 120x55", desc, Largura=1.2)
    c.mep = {"Fixture": {"drain_units": 1, "supply_weight": 0.3, "hot_water": True}}
    c.connector("Esgoto", "Sanitary", 0, V(D) / 2, 0.5, "Back", 0.04)
    c.connector("Água fria", "ColdWater", -0.1, V(D) / 2, 0.6, "Back", 0.02)
    c.connector("Água quente", "HotWater", 0.1, V(D) / 2, 0.6, "Back", 0.02)
    c.material("Quartzo branco", (238, 237, 232), "Generic", "Polished")
    c.preview_base = 0.3
    c.preview_size = (0.9, 0.6, 0.95)

    yw = V(D) / 2
    yc = yw - 0.27  # the basin's centre
    ym = yw - 0.045  # the mixer
    za = V(A)  # top of the countertop
    stone = "Quartzo branco"

    # --- countertop ---
    c.box("Bancada simplificada", -V(L) / 2, -V(D) / 2, za - T, L, D, T, stone, COARSE, in_plan=True)
    c.rev("Cuba simplificada", "Front", [(0, za), (R_OUT, za), (R_OUT, za + H_BOWL), (0, za + H_BOWL)], yc, 0, "Louça", detail=COARSE)
    c.profile("Bancada", "Side", [(-V(D) / 2 + 0.004, za - T), (yw, za - T), (yw, za), (-V(D) / 2 + 0.004, za, 0.004), (-V(D) / 2, za - 0.004),
                                  (-V(D) / 2, za - T + 0.004, 0.004)], -V(L) / 2, L, stone, in_plan=True)
    for side, sx in (("esquerda", -1), ("direita", 1)):
        x0 = (V(L) / 2 - 0.15) * sx - 0.02
        c.box(f"Suporte oculto {side}", x0, yw - 0.4, za - T - 0.006, 0.04, 0.4, 0.006, "Aço galvanizado", FINE)

    # --- the vessel basin: a turned bowl, outer and inner walls ---
    outer, inner = [], []
    n = 10
    for i in range(n + 1):
        t = i / n
        a = math.radians(90 * t)
        # Outer wall: a foot of r 0.08 widening to the rim, like a quarter of an ellipse.
        outer.append((0.08 + (R_OUT - 0.08) * math.sin(a), 0.006 + (H_BOWL - 0.006) * (1 - math.cos(a)) ** 0.8))
    for i in range(n, -1, -1):
        t = i / n
        a = math.radians(90 * t)
        inner.append((0.035 + (R_OUT - WALL - 0.035) * math.sin(a), 0.016 + (H_BOWL - 0.016) * (1 - math.cos(a)) ** 0.75))
    pts = [(0, za + 0.016), (0, za), (0.075, za), (0.08, za + 0.006)]
    pts += [(r, za + h) for r, h in outer[1:]]
    pts += [(R_OUT - WALL / 2, za + H_BOWL + 0.003)]
    pts += [(r, za + h) for r, h in inner]
    c.rev("Cuba de apoio", "Front", pts, yc, 0, "Louça", in_plan=True)

    # --- waste, mixer ---
    zf = za + 0.016  # the bowl's floor
    popup_drain(c, "click", 0, yc, zf, radius=0.032)
    tall_mixer(c, 0, ym, za)
    c.cyl("Haste roscada do misturador", 0, ym, za - T - 0.05, 0.016, 0.05, "Latão", FINE)
    c.cyl("Porca do misturador", 0, ym, za - T - 0.014, 0.026, 0.012, "Latão", FINE)

    # --- drain under the countertop and the bottle trap into the wall ---
    zt = za - T - 0.05
    c.cyl("Corpo da válvula", 0, yc, zt, 0.017, za + 0.016 - zt, "Cromado")
    c.cyl("Porca da válvula", 0, yc, za - T - 0.016, 0.03, 0.013, "Cromado", FINE)
    bottle_trap(c, 0, yc, zt, za - T - 0.2, yw)

    # --- supply: angle valves and hoses to the mixer ---
    for name, x in (("fria", -0.1), ("quente", 0.1)):
        yo, zo = angle_valve_ext(c, "registro", x, yw, 0.6, reach=yw - ym, suffix=name)
        hose(c, f"Flexível {name}", x, zo, 0.007 if x > 0 else -0.007, za - T - 0.05, ym, radius=0.005)

    # --- plan symbol of the basin ---
    c.profile("Planta – cuba", "Plan", oval(0, yc, R_OUT, R_OUT, n=48), za + H_BOWL, 0.002, "Louça")
    c.profile("Planta – bancada", "Plan", rect(-V(L) / 2, -V(D) / 2, V(L) / 2, yw), za, 0.002, stone)
    for name in ("Planta – cuba", "Planta – bancada"):
        c.plan_only(name)
    return c
