"""Lava-louças de piso (60 cm e 45 cm) com porta basculante e cestos deslizantes."""

from kit import *


def build() -> Component:
    c = Component("Lava-louças", "furniture", "lava-loucas")

    W = c.param("Largura", 0.6)
    D = c.param("Profundidade", 0.6)
    H = c.param("Altura", 0.85)
    AR = c.param("AlturaRodape", 0.12)
    AP = c.param("AlturaPainel", 0.1)
    EP = c.param("EspessuraPorta", 0.05)
    ET = c.param("EspessuraTampo", 0.03)
    A = c.angle("AnguloPorta", 0, open_at=90)
    XI = c.param("ExtensaoCestoInferior", 0.0, "Length", True)
    XS = c.param("ExtensaoCestoSuperior", 0.0, "Length", True)
    c.open_pose[XI] = 0.36
    c.open_pose[XS] = 0.2

    xl, xr = f"(-{W}/2)", f"({W}/2)"
    yf, yb = f"(-{D}/2)", f"({D}/2)"
    hy = f"({yf} + {EP})"  # the door's back face = the hinge plane
    hinge = (hy, AR)
    Hd = f"({H} - {AR} - {ET} - 0.004)"  # height of the door
    ybp = f"({yb} - 0.03)"  # back panel (recessed: the hoses run behind it)

    # The tub (inside faces).
    txl, txr = f"({xl} + 0.03)", f"({xr} - 0.03)"
    tyf, tyb = f"({hy} + 0.014)", f"({yb} - 0.075)"
    tz0, tz1 = f"({AR} - 0.045)", f"({H} - {ET} - 0.03)"
    tw = f"({W} - 0.06)"
    td = f"({tyb} - {tyf})"
    th = f"({tz1} - {tz0})"
    yc = f"(({tyf} + {tyb})/2)"

    body, inox, dark = "Aço pintado cinza", "Inox escovado", "Plástico preto brilhante"

    # --- coarse ---------------------------------------------------------------
    c.box("Corpo simplificado", xl, hy, 0, W, f"{D} - {EP}", H, body, detail=COARSE, in_plan=True)
    c.flap_box("Porta simplificada", hinge, A, xl, W, 0, Hd, 0, EP, inox, detail=COARSE, in_plan=True)

    # --- cabinet --------------------------------------------------------------
    c.box("Lateral esquerda", xl, f"{hy} + 0.002", 0.015, 0.012, f"{D} - {EP} - 0.002", f"{H} - {ET} - 0.015", body)
    c.box("Lateral direita", f"{xr} - 0.012", f"{hy} + 0.002", 0.015, 0.012, f"{D} - {EP} - 0.002", f"{H} - {ET} - 0.015", body)
    c.box("Tampo", xl, yf, f"{H} - {ET}", W, D, ET, body, in_plan=True)
    c.box("Tampo - friso frontal", f"{xl} + 0.001", f"{yf} - 0.001", f"{H} - {ET} + 0.004", f"{W} - 0.002", 0.001, f"{ET} - 0.008", "Alumínio anodizado", detail=FINE)
    c.box("Painel traseiro", f"{xl} + 0.012", ybp, 0.03, f"{W} - 0.024", 0.002, f"{H} - {ET} - 0.03", "Aço galvanizado")
    c.box("Base do gabinete", f"{xl} + 0.012", f"{hy} + 0.02", 0.015, f"{W} - 0.024", f"{D} - {EP} - 0.05", 0.015, "Aço galvanizado")
    c.box("Rodapé", f"{xl} + 0.012", f"{hy} + 0.02", 0.03, f"{W} - 0.024", 0.012, f"{AR} - 0.036", "Plástico cinza")
    for i in range(6):
        c.box(f"Rodapé - fresta {i + 1}", f"{xl} + {W}*0.3 + {i}*{W}*0.07", f"{hy} + 0.0195", 0.045, f"{W}*0.045", 0.001, f"{AR} - 0.07", "Plástico preto", detail=FINE)
    for sx, nx in ((f"{xl} + 0.045", "esquerdo"), (f"{xr} - 0.045", "direito")):
        for sy, ny in ((f"{hy} + 0.06", "frontal"), (f"{yb} - 0.07", "traseiro")):
            c.cyl(f"Pé {ny} {nx}", sx, sy, 0.006, 0.012, 0.009, "Aço galvanizado", detail=FINE)
            c.cyl(f"Sapata {ny} {nx}", sx, sy, 0, 0.022, 0.006, "Plástico preto")

    # Front frame closing the gap between the casing and the tub.
    my, md = f"{hy} + 0.002", 0.012
    c.box("Moldura esquerda", f"{xl} + 0.012", my, AR, 0.018, md, f"{H} - {ET} - {AR}", inox)
    c.box("Moldura direita", f"{xr} - 0.03", my, AR, 0.018, md, f"{H} - {ET} - {AR}", inox)
    c.box("Moldura superior", txl, my, tz1, tw, md, 0.03, inox)
    c.box("Soleira", f"{xl} + 0.012", my, f"{AR} - 0.05", f"{W} - 0.024", md, 0.054, inox)
    # Seal around the opening.
    c.box("Vedação esquerda", f"{txl} - 0.006", f"{hy} + 0.0005", f"{AR} + 0.004", 0.006, 0.0015, f"{tz1} - {AR}", "Borracha cinza", detail=FINE)
    c.box("Vedação direita", txr, f"{hy} + 0.0005", f"{AR} + 0.004", 0.006, 0.0015, f"{tz1} - {AR}", "Borracha cinza", detail=FINE)
    c.box("Vedação superior", txl, f"{hy} + 0.0005", tz1, tw, 0.0015, 0.006, "Borracha cinza", detail=FINE)
    c.box("Batente do trinco", "-0.02", f"{hy} + 0.0005", f"{tz1} + 0.01", 0.04, 0.0015, 0.014, "Plástico preto", detail=FINE)

    # --- tub ------------------------------------------------------------------
    c.box("Cuba - parede esquerda", f"{txl} - 0.002", tyf, tz0, 0.002, td, th, inox)
    c.box("Cuba - parede direita", txr, tyf, tz0, 0.002, td, th, inox)
    c.box("Cuba - fundo", f"{txl} - 0.002", tyb, tz0, f"{tw} + 0.004", 0.002, th, inox)
    c.box("Cuba - piso", f"{txl} - 0.002", tyf, f"{tz0} - 0.002", f"{tw} + 0.004", f"{td} + 0.002", 0.002, inox)
    c.box("Cuba - teto", f"{txl} - 0.002", tyf, tz1, f"{tw} + 0.004", f"{td} + 0.002", 0.002, inox)
    # Tracks of the lower basket (level with the open door).
    for x, n in ((txl, "esquerdo"), (f"{txr} - 0.024", "direito")):
        c.box(f"Trilho inferior {n}", x, tyf, f"{AR} - 0.004", 0.024, td, 0.008, inox)
    # Sump, filter, salt and arms.
    fx, fy = f"({W}*0.14)", f"({yc} - {td}*0.26)"
    c.cyl("Filtro - aro", fx, fy, tz0, 0.06, 0.003, "Aço galvanizado")
    c.cyl("Filtro - tela", fx, fy, f"{tz0} + 0.003", 0.052, 0.002, "Tela perfurada", detail=FINE)
    c.cyl("Filtro cilíndrico", fx, fy, f"{tz0} + 0.003", 0.028, 0.02, "Plástico cinza")
    c.box("Filtro - pega", f"{fx} - 0.02", f"{fy} - 0.004", f"{tz0} + 0.023", 0.04, 0.008, 0.006, "Plástico cinza claro", detail=FINE)
    sx_, sy_ = f"(-{W}*0.27)", f"({yc} - {td}*0.3)"
    c.cyl("Reservatório de sal - tampa", sx_, sy_, tz0, 0.032, 0.012, "Plástico cinza claro")
    c.box("Reservatório de sal - pega", f"{sx_} - 0.022", f"{sy_} - 0.004", f"{tz0} + 0.012", 0.044, 0.008, 0.005, "Plástico cinza claro", detail=FINE)
    c.rev("Resistência", "Front", disc(f"{W}*0.3", f"{tz0} + 0.012", 0.004), f"{yc} + {td}*0.1", 0, "Aço pintado preto", angle=300, detail=FINE)

    def arm(name, z, half, ang, n_jets):
        """A spray arm: hub at the tub's center, a bar turned by `ang`, jets on top."""
        import math
        cs, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        w = 0.017

        def pt(a, b):  # a along the arm (fraction of half), b across (meters)
            return (f"{a}*{half}*{cs:.4f} - {b * sn:.5f}", f"{yc} + {a}*{half}*{sn:.4f} + {b * cs:.5f}")

        pts = [pt(-1, -w * 0.6), pt(0, -w), pt(1, -w * 0.6), pt(1, w * 0.6), pt(0, w), pt(-1, w * 0.6)]
        c.profile(name, "Plan", pts, z, 0.012, "Plástico cinza")
        for i in range(n_jets):
            f = -0.9 + 1.8 * i / (n_jets - 1)
            if abs(f) < 0.15:
                continue
            ux, uy = pt(round(f, 3), 0)
            c.cyl(f"{name} - bico {i + 1}", ux, uy, f"{z} + 0.012", 0.004, 0.002, "Plástico azul", detail=FINE)

    arm_half = f"({W}/2 - 0.07)"
    c.cyl("Braço aspersor inferior - cubo", 0, yc, tz0, 0.022, 0.034, "Plástico cinza")
    arm("Braço aspersor inferior", f"({tz0} + 0.034)", arm_half, 24, 8)
    c.cyl("Braço aspersor inferior - tampa", 0, yc, f"{tz0} + 0.046", 0.014, 0.005, "Plástico azul", detail=FINE)

    # Upper basket level.
    ub = f"({AR} + ({H} - {AR} - {ET})*0.53)"
    c.box("Duto de alimentação - vertical", "-0.022", f"{tyb} - 0.016", tz0, 0.044, 0.016, f"{ub} - {tz0} - 0.02", "Plástico cinza")
    c.box("Duto de alimentação - horizontal", "-0.016", yc, f"{ub} - 0.05", 0.032, f"{tyb} - {yc} - 0.016", 0.016, "Plástico cinza")
    c.cyl("Braço aspersor superior - cubo", 0, yc, f"{ub} - 0.05", 0.02, 0.022, "Plástico cinza")
    arm("Braço aspersor superior", f"({ub} - 0.04)", arm_half, -32, 8)
    c.box("Duto de alimentação - ramal do teto", "-0.012", f"{tyb} - 0.012", f"{ub} - 0.02", 0.024, 0.012, f"{tz1} - {ub} + 0.02", "Plástico cinza", detail=FINE)
    c.box("Duto do teto", "-0.012", yc, f"{tz1} - 0.012", 0.024, f"{tyb} - {yc}", 0.012, "Plástico cinza", detail=FINE)
    c.cyl("Aspersor do teto", 0, yc, f"{tz1} - 0.022", 0.03, 0.01, "Plástico cinza")
    c.box("Lâmpada interna", f"{txr} - 0.004", f"{tyf} + 0.05", f"{tz1} - 0.06", 0.004, 0.05, 0.02, "Plástico translúcido", detail=FINE)
    for x, n in ((txl, "esquerdo"), (f"{txr} - 0.014", "direito")):
        c.box(f"Trilho superior {n}", x, tyf, f"{ub} + 0.05", 0.014, td, 0.014, inox)
        for j, fy_ in enumerate((0.25, 0.75)):
            c.cyl_x(f"Trilho superior {n} - rolete {j + 1}", f"{tyf} + {td}*{fy_}", f"{ub} + 0.076", f"{x} + 0.002", 0.011, 0.01, "Plástico cinza claro", detail=FINE)

    # --- baskets --------------------------------------------------------------
    rxl, rxr = f"({txl} + 0.028)", f"({txr} - 0.028)"
    rw = f"({tw} - 0.056)"
    rl = f"({td} - 0.06)"  # length of both baskets
    wire = "Aço pintado cinza"
    c.material("Arame revestido", (150, 156, 164), "Metal", "Satin")
    wire = "Arame revestido"
    t = 0.004

    def basket(name, ext, zb, hb, y_front, tines_rows, tine_h, x_tines_end, wheels):
        y0 = f"({tyf} + {y_front} - {ext})"
        y1 = f"({y0} + {rl})"
        # base and rim frames
        for lvl, z, d in (("base", zb, FULL), ("borda", f"{zb} + {hb}", FULL)):
            c.box(f"{name} - {lvl} frontal", rxl, y0, z, rw, t + 0.001, t + 0.001, wire, detail=d)
            c.box(f"{name} - {lvl} traseira", rxl, f"{y1} - 0.005", z, rw, t + 0.001, t + 0.001, wire, detail=d)
            c.box(f"{name} - {lvl} esquerda", rxl, y0, z, t + 0.001, rl, t + 0.001, wire, detail=d)
            c.box(f"{name} - {lvl} direita", f"{rxr} - 0.005", y0, z, t + 0.001, rl, t + 0.001, wire, detail=d)
        c.box(f"{name} - meia altura frontal", rxl, y0, f"{zb} + {hb}/2", rw, t, t, wire, detail=FINE)
        c.box(f"{name} - meia altura traseira", rxl, f"{y1} - {t}", f"{zb} + {hb}/2", rw, t, t, wire, detail=FINE)
        c.box(f"{name} - meia altura esquerda", rxl, y0, f"{zb} + {hb}/2", t, rl, t, wire, detail=FINE)
        c.box(f"{name} - meia altura direita", f"{rxr} - {t}", y0, f"{zb} + {hb}/2", t, rl, t, wire, detail=FINE)
        # posts
        k = 0
        for fx_ in (0, 0.5, 1):
            for fy_ in (0, 0.5, 1):
                if fx_ == 0.5 and fy_ == 0.5:
                    continue
                k += 1
                c.box(f"{name} - montante {k}", f"{rxl} + {fx_}*({rw} - {t})", f"{y0} + {fy_}*({rl} - {t})", zb, t, t, hb, wire,
                      detail=FULL if fx_ != 0.5 and fy_ != 0.5 else FINE)
        # bottom wires
        for i in range(9):
            c.box(f"{name} - arame {i + 1}", f"{rxl} + {(i + 1) / 10}*({rw} - {t})", y0, zb, t, rl, t, wire, detail=FINE)
        for i in range(4):
            c.box(f"{name} - travessa {i + 1}", rxl, f"{y0} + {(i + 1) / 5}*({rl} - {t})", f"{zb} - {t}", rw, t, t, wire, detail=FINE)
        # tines
        k = 0
        for fy_ in tines_rows:
            for i in range(7):
                k += 1
                c.box(f"{name} - pino {k}", f"{rxl} + 0.02 + {i / 6}*({x_tines_end})", f"{y0} + {fy_}*{rl}", f"{zb} + {t}", 0.003, 0.003, tine_h, wire, detail=FINE)
        c.box(f"{name} - puxador", f"-{W}*0.12", f"{y0} - 0.012", f"{zb} + {hb} - 0.012", f"{W}*0.24", 0.012, 0.022, "Plástico cinza claro")
        if wheels:
            for x, n in ((f"{rxl} - 0.02", "esquerda"), (f"{rxr} + 0.008", "direita")):
                for j, fy_ in enumerate((0.1, 0.5, 0.9)):
                    c.cyl_x(f"{name} - roda {n} {j + 1}", f"{y0} + {fy_}*{rl}", f"{AR} + 0.022", x, 0.018, 0.012, "Plástico cinza claro")
                    c.cyl_x(f"{name} - eixo da roda {n} {j + 1}", f"{y0} + {fy_}*{rl}", f"{AR} + 0.022", f"{x} - 0.002" if n == "direita" else f"{x} + 0.01", 0.004, 0.012, wire, detail=FINE)
        return y0

    zb_i = f"({AR} + 0.02)"
    y0i = basket("Cesto inferior", XI, zb_i, 0.14, 0.022, (0.3, 0.52, 0.74), 0.075, f"{rw} - 0.2", True)
    # Cutlery basket inside the lower one, on the right.
    cw, cl, ch = 0.115, f"({rl}*0.55)", 0.12
    cx0, cy0, cz0 = f"({rxr} - 0.012 - {cw})", f"({y0i} + {rl}*0.22)", f"({zb_i} + {t})"
    pc = "Plástico cinza"
    c.box("Cesto de talheres - fundo", cx0, cy0, cz0, cw, cl, 0.004, pc)
    c.box("Cesto de talheres - parede esquerda", cx0, cy0, cz0, 0.003, cl, ch, pc)
    c.box("Cesto de talheres - parede direita", f"{cx0} + {cw} - 0.003", cy0, cz0, 0.003, cl, ch, pc)
    c.box("Cesto de talheres - parede frontal", cx0, cy0, cz0, cw, 0.003, ch, pc)
    c.box("Cesto de talheres - parede traseira", cx0, f"{cy0} + {cl} - 0.003", cz0, cw, 0.003, ch, pc)
    for i in range(3):
        c.box(f"Cesto de talheres - divisória {i + 1}", cx0, f"{cy0} + {(i + 1) / 4}*{cl}", cz0, cw, 0.003, f"{ch} - 0.01", pc, detail=FINE)
    c.box("Cesto de talheres - haste da alça frontal", f"{cx0} + {cw}/2 - 0.004", f"{cy0} + {cl}*0.25", cz0, 0.008, 0.004, ch + 0.07, pc, detail=FINE)
    c.box("Cesto de talheres - haste da alça traseira", f"{cx0} + {cw}/2 - 0.004", f"{cy0} + {cl}*0.75", cz0, 0.008, 0.004, ch + 0.07, pc, detail=FINE)
    c.box("Cesto de talheres - alça", f"{cx0} + {cw}/2 - 0.008", f"{cy0} + {cl}*0.25", f"{cz0} + {ch + 0.07}", 0.016, f"{cl}*0.5 + 0.004", 0.01, pc)

    y0s = basket("Cesto superior", XS, ub, 0.11, 0.022, (0.5,), 0.05, f"{rw} - 0.04", False)
    # Runners that carry the upper basket on the rails.
    for x, n in ((f"{rxl} - 0.014", "esquerda"), (f"{rxr}", "direita")):
        c.box(f"Cesto superior - corrediça {n}", x, y0s, f"{ub} + 0.064", 0.014, rl, 0.01, inox)
    # Folding cup shelf on the left.
    c.box("Cesto superior - prateleira de xícaras", f"{rxl} + 0.006", f"{y0s} + {rl}*0.12", f"{ub} + 0.075", f"{rw}*0.24", f"{rl}*0.76", 0.004, "Plástico cinza claro")
    for i in range(5):
        c.box(f"Cesto superior - prateleira de xícaras - fresta {i + 1}", f"{rxl} + 0.012", f"{y0s} + {rl}*{0.2 + 0.14 * i}", f"{ub} + 0.0792", f"{rw}*0.24 - 0.012", f"{rl}*0.05", 0.0005, "Plástico cinza", detail=FINE)

    # --- door -----------------------------------------------------------------
    def door(name, x, width, s0, s1, t0, t1, material, detail=FULL, in_plan=False):
        c.flap_box(name, hinge, A, x, width, s0, s1, t0, t1, material, detail=detail, in_plan=in_plan)

    sp = f"({Hd} - {AP})"  # bottom of the control panel
    door("Porta - corpo", f"{xl} + 0.002", f"{W} - 0.004", 0, Hd, 0, f"{EP} - 0.004", "Aço pintado cinza", in_plan=True)
    door("Porta - painel frontal", f"{xl} + 0.002", f"{W} - 0.004", 0, f"{sp} - 0.003", f"{EP} - 0.004", EP, inox)
    door("Porta - friso inferior", f"{xl} + 0.002", f"{W} - 0.004", 0.03, 0.033, EP, f"{EP} + 0.0008", "Alumínio anodizado", detail=FINE)
    door("Porta - contraporta", f"{txl} + 0.006", f"{tw} - 0.012", 0.006, f"{tz1} - {AR} - 0.006", -0.004, 0, inox)
    door("Porta - guia do cesto esquerda", f"{txl} + 0.006", 0.022, 0.02, f"{tz1} - {AR} - 0.2", -0.0045, -0.004, "Aço galvanizado", detail=FINE)
    door("Porta - guia do cesto direita", f"{txr} - 0.028", 0.022, 0.02, f"{tz1} - {AR} - 0.2", -0.0045, -0.004, "Aço galvanizado", detail=FINE)
    # Detergent dispenser and rinse aid on the inner face.
    ds = f"({Hd}*0.42)"
    door("Dispenser - corpo", "-0.095", 0.19, ds, f"{ds} + 0.11", -0.008, -0.004, "Plástico cinza claro")
    door("Dispenser - tampa do detergente", "-0.088", 0.085, f"{ds} + 0.012", f"{ds} + 0.098", -0.012, -0.008, "Plástico cinza")
    door("Dispenser - trava", "-0.002", 0.014, f"{ds} + 0.04", f"{ds} + 0.07", -0.013, -0.008, "Plástico azul", detail=FINE)
    door("Dispenser - tampa do abrilhantador", "0.03", 0.05, f"{ds} + 0.03", f"{ds} + 0.08", -0.011, -0.008, "Plástico azul", detail=FINE)
    door("Dispenser - visor do abrilhantador", "0.04", 0.03, f"{ds} + 0.09", f"{ds} + 0.1", -0.009, -0.008, "Plástico translúcido", detail=FINE)
    door("Porta - respiro", f"{W}*0.25", 0.05, f"{Hd}*0.72", f"{Hd}*0.72 + 0.03", -0.007, -0.004, "Plástico cinza", detail=FINE)
    door("Porta - etiqueta de dados", f"-{W}*0.4", 0.07, f"{Hd}*0.8", f"{Hd}*0.8 + 0.035", -0.0045, -0.004, "Alumínio anodizado", detail=FINE)
    door("Porta - trinco", "-0.012", 0.024, f"{tz1} - {AR} + 0.008", f"{tz1} - {AR} + 0.02", -0.014, 0, "Plástico preto", detail=FINE)
    # Control panel on the door.
    te = f"({EP} - 0.004)"
    door("Painel de comando", f"{xl} + 0.002", f"{W} - 0.004", sp, Hd, te, f"{EP} + 0.002", dark)
    door("Painel de comando - friso", f"{xl} + 0.002", f"{W} - 0.004", f"{sp} - 0.003", sp, te, f"{EP} + 0.001", "Cromado", detail=FINE)
    sm = f"({sp} + {AP}/2)"
    door("Visor", "-0.045", 0.09, f"{sm} - 0.016", f"{sm} + 0.016", f"{EP} + 0.002", f"{EP} + 0.003", "Visor LED")
    door("Tecla liga/desliga", f"{xl} + {W}*0.07", 0.026, f"{sm} - 0.013", f"{sm} + 0.013", f"{EP} + 0.002", f"{EP} + 0.005", "Cromado", detail=FINE)
    for i in range(4):
        door(f"Tecla de programa {i + 1}", f"{xl} + {W}*{0.15 + 0.065 * i}", f"{W}*0.045", f"{sm} - 0.008", f"{sm} + 0.008", f"{EP} + 0.002", f"{EP} + 0.004", "Teclado", detail=FINE)
        door(f"Luz de programa {i + 1}", f"{xl} + {W}*{0.15 + 0.065 * i} + {W}*0.0175", f"{W}*0.01", f"{sm} + 0.014", f"{sm} + 0.018", f"{EP} + 0.002", f"{EP} + 0.003", "Plástico verde", detail=FINE)
    for i, n in enumerate(("meia carga", "secagem extra", "início adiado")):
        door(f"Tecla {n}", f"{W}*{0.13 + 0.075 * i}", f"{W}*0.05", f"{sm} - 0.008", f"{sm} + 0.008", f"{EP} + 0.002", f"{EP} + 0.004", "Teclado", detail=FINE)
    door("Tecla iniciar", f"{xr} - {W}*0.07 - 0.03", 0.03, f"{sm} - 0.012", f"{sm} + 0.012", f"{EP} + 0.002", f"{EP} + 0.005", "Plástico verde", detail=FINE)
    # Handle.
    hs = f"({sp} - 0.05)"
    door("Puxador - barra", f"-{W}*0.36", f"{W}*0.72", f"{hs} - 0.009", f"{hs} + 0.009", f"{EP} + 0.028", f"{EP} + 0.042", "Alumínio anodizado")
    door("Puxador - suporte esquerdo", f"-{W}*0.31", 0.014, f"{hs} - 0.007", f"{hs} + 0.007", EP, f"{EP} + 0.028", "Alumínio anodizado")
    door("Puxador - suporte direito", f"{W}*0.31 - 0.014", 0.014, f"{hs} - 0.007", f"{hs} + 0.007", EP, f"{EP} + 0.028", "Alumínio anodizado")
    # Hinge arms (fixed).
    c.box("Dobradiça esquerda", f"{xl} + 0.012", f"{hy} + 0.002", f"{AR} - 0.03", 0.006, 0.05, 0.03, "Aço galvanizado", detail=FINE)
    c.box("Dobradiça direita", f"{xr} - 0.018", f"{hy} + 0.002", f"{AR} - 0.03", 0.006, 0.05, 0.03, "Aço galvanizado", detail=FINE)

    # --- back -----------------------------------------------------------------
    yh = f"({ybp} + 0.002)"
    ix, dx = f"({xl} + {W}*0.18)", f"({xr} - {W}*0.2)"
    c.box("Válvula de entrada de água", f"{ix} - 0.025", yh, 0.07, 0.05, 0.012, 0.045, "Plástico cinza claro")
    c.cyl("Entrada de água - rosca", ix, f"{yh} + 0.013", 0.115, 0.012, 0.014, "Latão")
    c.cyl("Mangueira de entrada - porca", ix, f"{yh} + 0.013", 0.129, 0.015, 0.016, "Plástico cinza")
    c.cyl("Mangueira de entrada", ix, f"{yh} + 0.013", 0.145, 0.007, f"{H}*0.5", "Borracha cinza")
    c.box("Mangueira de entrada - presilha", f"{ix} - 0.014", yh, f"{H}*0.45", 0.028, 0.022, 0.012, "Plástico preto", detail=FINE)
    c.cyl_y("Saída de esgoto - bocal", dx, 0.08, yh, 0.013, 0.012, "Plástico preto")
    c.cyl("Mangueira de esgoto", dx, f"{yh} + 0.013", 0.07, 0.0105, f"{H}*0.68", "Plástico cinza")
    for i in range(8):
        c.cyl(f"Mangueira de esgoto - anel {i + 1}", dx, f"{yh} + 0.013", f"0.1 + {i}*{H}*0.08", 0.0125, 0.012, "Plástico cinza", detail=FINE)
    c.box("Mangueira de esgoto - presilha", f"{dx} - 0.018", yh, f"{H}*0.7", 0.036, 0.026, 0.012, "Plástico preto", detail=FINE)
    c.cyl_y("Passa-cabo", 0, f"{H}*0.2", yh, 0.011, 0.008, "Borracha")
    c.cyl("Cabo de alimentação", 0, f"{yh} + 0.012", 0.03, 0.004, f"{H}*0.2 - 0.03", "Borracha")
    c.box("Cabo de alimentação - plugue", "-0.018", f"{yh} + 0.002", 0.012, 0.036, 0.022, 0.03, "Plástico preto", detail=FINE)
    c.box("Tampa de acesso traseira", f"-{W}*0.3", yh, f"{H}*0.3", f"{W}*0.6", 0.0015, f"{H}*0.3", "Aço galvanizado", detail=FINE)
    for i, (fx_, fz_) in enumerate(((-0.28, 0.31), (0.28, 0.31), (-0.28, 0.59), (0.28, 0.59))):
        c.cyl_y(f"Parafuso da tampa traseira {i + 1}", f"{W}*{fx_}", f"{H}*{fz_}", f"{yh} + 0.0015", 0.004, 0.002, "Cromado", detail=FINE)
    for i in range(7):
        c.box(f"Ventilação traseira {i + 1}", f"-{W}*0.2", f"{yh} - 0.0005", f"{H}*0.72 + {i}*0.012", f"{W}*0.4", 0.001, 0.005, "Aço pintado preto", detail=FINE)
    c.box("Etiqueta de identificação", f"{W}*0.18", yh, f"{H}*0.62", f"{W}*0.22", 0.0008, 0.05, "Alumínio anodizado", detail=FINE)
    c.box("Travessa traseira superior", f"{xl} + 0.012", f"{ybp} + 0.002", f"{H} - {ET} - 0.03", f"{W} - 0.024", 0.028, 0.03, "Aço galvanizado")

    c.type("Lava-louças 60 cm 14 serviços", "Lava-louças de piso ou de embutir sob bancada, 60 x 60 x 85 cm, 14 serviços, porta basculante em inox")
    c.type("Lava-louças 45 cm 10 serviços", "Lava-louças compacta de piso ou de embutir sob bancada, 45 x 60 x 85 cm, 10 serviços, porta basculante em inox", Largura=0.45)
    return c
