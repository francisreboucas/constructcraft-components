"""Ar-condicionado split - condensadora: the outdoor unit.

Frame: stands on the floor or on a bracket, bottom at z = 0, centered on the
origin, the fan grille facing -Y. Largura includes the valve cover on the
right side; the sheet-metal cabinet takes the rest. The coil wraps the back
and the left side; the compressor sits in the right bay behind a partition.
"""

from math import cos, sin, radians

from kit import *


def n(v: float) -> str:
    """A number, in parentheses so that a negative one is safe in an expression."""
    return f"({v:.5f})"


def build() -> Component:
    c = Component("Ar-condicionado split - condensadora", "furniture", "ar-condicionado-split-condensadora", "Furniture")
    L = c.param("Largura", 0.70)
    P = c.param("Profundidade", 0.26)
    H = c.param("Altura", 0.50)

    c.type("Condensadora split 9.000 a 12.000 BTU", "Unidade externa de 9.000 a 12.000 BTU/h, 70 x 26 x 50 cm")
    c.type("Condensadora split 18.000 a 24.000 BTU", "Unidade externa de 18.000 a 24.000 BTU/h, 85 x 32 x 60 cm",
           Largura=0.85, Profundidade=0.32, Altura=0.60)

    WHT, GALV, GREY = "Aço pintado branco", "Aço galvanizado", "Plástico cinza claro"
    VC = 0.05  # width of the valve cover, on the right
    zb = 0.03  # underside of the cabinet (on the rails)
    x0 = f"(-{L}/2)"
    x1 = f"({L}/2 - {VC})"
    CW = f"({L} - {VC})"
    xc = -VC / 2  # center of the cabinet
    yf, yk = f"(-{P}/2)", f"({P}/2)"
    Rf = f"(0.38*{H})"  # radius of the fan opening
    xf = f"({x0} + 0.045 + {Rf})"  # fan axis
    zf = f"(({H} + {zb})/2)"
    xp = f"({xf} + {Rf} + 0.03)"  # partition between the fan and the compressor bays
    tp = 0.003
    hz0, hh = zb + 0.02, f"({H} - {zb + 0.04})"  # the walls stand between the base pan and the top cover

    def pol(rf, th, rc=0.0, off=0.0):
        """Front (x, z) of the point at radius rf*Rf + rc and angle th about the fan axis, moved `off` across the radius."""
        ca, sa = cos(radians(th)), sin(radians(th))
        return (f"{xf} + {n(rf * ca)}*{Rf} + {n(rc * ca - off * sa)}", f"{zf} + {n(rf * sa)}*{Rf} + {n(rc * sa + off * ca)}")

    # --- coarse stand-ins -------------------------------------------------
    c.box("Gabinete simplificado", x0, yf, zb, CW, P, f"{H} - {zb}", WHT, detail=COARSE, in_plan=True)
    c.box("Tampa das válvulas simplificada", x1, -0.03, zb + 0.03, VC, f"{P}/2 - 0.04", 0.19, GREY, detail=COARSE, in_plan=True)
    c.cyl_y("Grade simplificada", xf, zf, f"{yf} - 0.012", Rf, 0.012, GREY, detail=COARSE)
    for k, sx in enumerate((-1, 1), 1):
        c.box(f"Trilho simplificado {k}", f"{xc} + {sx}*0.32*{CW} - 0.025", f"{yf} - 0.02", 0, 0.05, f"{P} + 0.04", zb, GALV, detail=COARSE)

    # --- cabinet ------------------------------------------------------------
    c.box("Bandeja da base", x0, yf, zb, CW, P, 0.02, WHT)
    c.box("Tampa superior", f"{x0} - 0.003", f"{yf} - 0.003", f"{H} - 0.02", f"{CW} + 0.006", f"{P} + 0.006", 0.02, WHT, in_plan=True)
    for k, f in enumerate((0.3, 0.7), 1):
        c.box(f"Tampa superior - nervura {k}", f"{x0} + 0.04", f"{yf} + {f}*{P} - 0.015", H, f"{CW} - 0.08", 0.03, 0.002, WHT, detail=FINE)
    c.box("Painel frontal", x0, yf, hz0, CW, tp, hh, WHT)
    c.cyl_y("Painel frontal - abertura do ventilador", xf, zf, f"{yf} - 0.0005", Rf, tp + 0.001, WHT, void=True)
    c.rev("Painel frontal - bocal", "Plan",
          [(f"{xf} + {Rf}", f"{yf} - 0.0007"), (f"{xf} + {Rf} + 0.016", f"{yf} - 0.0007"), (f"{xf} + {Rf} + 0.008", f"{yf} - 0.012"), (f"{xf} + {Rf}", f"{yf} - 0.012")],
          zf, xf, WHT)
    c.rev("Bocal interno do ventilador", "Plan", rect(f"{xf} + {Rf}", f"{yf} + {tp} + 0.0006", f"{xf} + {Rf} + 0.004", f"{yf} + 0.05"), zf, xf, GALV)
    c.box("Painel lateral direito", f"{x1} - {tp}", yf, hz0, tp, P, hh, WHT)
    c.box("Painel traseiro direito", xp, f"{yk} - {tp}", hz0, f"{x1} - {xp}", tp, hh, WHT)
    c.box("Coluna frontal esquerda", x0, yf, hz0, tp, 0.04, hh, WHT)
    c.box("Coluna traseira esquerda", x0, f"{yk} - 0.014", hz0, 0.014, 0.014, hh, WHT)
    c.box("Divisória interna", xp, f"{yf} + {tp}", hz0, tp, f"{P} - {2 * tp}", hh, GALV)
    for k in range(5):
        c.box(f"Painel frontal - friso {k + 1}", f"{xp} + 0.02", f"{yf} - 0.0012", f"{zf} + {0.06 - k * 0.03:.3f}", f"{x1} - {xp} - 0.04", 0.0012, 0.008, WHT, detail=FINE)
    c.box("Selo de eficiência energética", f"{xp} + 0.03", f"{yf} - 0.0006", f"{H} - 0.16", 0.07, 0.0006, 0.10, "Plástico cinza claro", detail=FINE)
    c.box("Plaqueta frontal", f"{xp} + 0.03", f"{yf} - 0.0015", hz0 + 0.03, 0.06, 0.0015, 0.014, "Alumínio anodizado", detail=FINE)
    for k, (bx, bz) in enumerate(((f"{x0} + 0.012", hz0 + 0.012), (f"{x1} - 0.012", hz0 + 0.012), (f"{x0} + 0.012", f"{H} - 0.032"), (f"{x1} - 0.012", f"{H} - 0.032"),
                                  (f"{xp} + 0.0015", hz0 + 0.012), (f"{xp} + 0.0015", f"{H} - 0.032")), 1):
        c.cyl_y(f"Painel frontal - parafuso {k}", bx, bz, f"{yf} - 0.0015", 0.004, 0.0015, GALV, detail=FINE)

    # --- fan guard: concentric rings on radial spokes -----------------------------
    yg = f"({yf} - 0.012)"
    for k in range(2, 10):
        r = f"({xf} + {k / 9:.5f}*{Rf})"
        c.rev(f"Grade frontal - anel {k - 1}", "Plan", rect(f"{r} - 0.003", f"{yg} - 0.003", r, yg), zf, xf, GREY)
    for k in range(12):
        th = 15 + 30 * k
        pts = [pol(0.12, th, 0, -0.002), pol(1, th, 0.012, -0.002), pol(1, th, 0.012, 0.002), pol(0.12, th, 0, 0.002)]
        c.profile(f"Grade frontal - raio {k + 1}", "Front", pts, yg, 0.003, GREY)
    c.cyl_y("Grade frontal - miolo", xf, zf, f"{yg} - 0.005", f"0.15*{Rf}", 0.008, GREY)
    for k in range(4):
        px, pz = pol(1, 45 + 90 * k, 0.008)
        c.cyl_y(f"Grade frontal - parafuso {k + 1}", px, pz, f"{yg} - 0.002", 0.004, 0.002, GALV, detail=FINE)

    # --- fan: hub, three blades (two steps each, as the pitch), motor and bracket ----
    yv = f"({yf} + 0.022)"
    lead = [(0.2, -14), (0.45, -26), (0.75, -34), (0.92, -34), (0.96, -28), (0.96, -12), (0.6, -6), (0.2, 0)]
    trail = [(0.2, 0), (0.6, -6), (0.96, -12), (0.96, 4), (0.9, 10), (0.7, 12), (0.45, 12), (0.2, 14)]
    for k in range(3):
        b = 90 + 120 * k
        c.profile(f"Hélice - pá {k + 1} (bordo de ataque)", "Front", [pol(r, b + a) for r, a in lead], yv, 0.007, "Plástico cinza")
        c.profile(f"Hélice - pá {k + 1} (bordo de fuga)", "Front", [pol(r, b + a) for r, a in trail], f"{yv} + 0.007", 0.007, "Plástico cinza")
    c.cyl_y("Hélice - cubo", xf, zf, f"{yv} - 0.004", f"0.22*{Rf}", 0.03, "Plástico cinza")
    c.cyl_y("Hélice - porca do cubo", xf, zf, f"{yv} - 0.01", 0.012, 0.006, GALV, detail=FINE)
    c.cyl_y("Motor do ventilador - eixo", xf, zf, f"{yv} + 0.026", 0.006, 0.02, GALV, detail=FINE)
    c.cyl_y("Motor do ventilador", xf, zf, f"{yv} + 0.04", 0.05, 0.085, "Aço pintado cinza")
    c.cyl_y("Motor do ventilador - tampa traseira", xf, zf, f"{yv} + 0.125", 0.035, 0.012, "Aço pintado cinza", detail=FINE)
    ym = f"({yv} + 0.07)"
    for k, sx in enumerate((-1, 1), 1):
        c.box(f"Suporte do motor - montante {k}", f"{xf} + {sx}*0.065 - 0.01", ym, hz0, 0.02, 0.022, hh, GALV)
    for k, sz in enumerate((-1, 1), 1):
        c.box(f"Suporte do motor - travessa {k}", f"{xf} - 0.065", ym, f"{zf} + {sz}*0.058 - 0.006", 0.13, 0.022, 0.012, GALV, detail=FINE)

    # --- condenser coil: across the back and around the left side -------------------
    cz0, ch = hz0 + 0.004, f"({H} - {zb + 0.048})"
    bx0 = f"({x0} + 0.016)"
    bw = f"({xp} - {x0} - 0.016)"
    c.box("Serpentina traseira", bx0, f"{yk} - 0.03", cz0, bw, 0.024, ch, "Alumínio anodizado")
    nb = 64
    for k in range(nb):
        c.box(f"Serpentina traseira - aleta {k + 1}", f"{bx0} + {(k + 0.5) / nb:.5f}*{bw} - 0.0006", f"{yk} - 0.006", cz0, 0.0012, 0.005, ch, "Alumínio anodizado", detail=FINE)
    sy0 = f"({yf} + 0.045)"
    sd = f"({P} - 0.075)"
    c.box("Serpentina lateral", f"{x0} + 0.006", sy0, cz0, 0.024, sd, ch, "Alumínio anodizado")
    ns = 24
    for k in range(ns):
        c.box(f"Serpentina lateral - aleta {k + 1}", f"{x0} + 0.001", f"{sy0} + {(k + 0.5) / ns:.5f}*{sd} - 0.0006", cz0, 0.005, 0.0012, ch, "Alumínio anodizado", detail=FINE)
    for k in range(9):
        zz = f"({cz0} + {(k + 0.5) / 9:.5f}*{ch})"
        c.cyl_x(f"Serpentina - curva de cobre {k + 1}", f"{yk} - 0.018", zz, f"{xp} + {tp}", 0.005, 0.012, "Cobre", detail=FINE)
    # wire guard over the coil
    for k in range(8):
        zz = f"({cz0} + {(k + 0.5) / 8:.5f}*{ch} - 0.0015)"
        c.box(f"Grade traseira - arame horizontal {k + 1}", f"{x0} + 0.004", f"{yk} + 0.0005", zz, f"{xp} - {x0} - 0.004", 0.003, 0.003, WHT, detail=FINE)
        c.box(f"Grade lateral - arame horizontal {k + 1}", f"{x0} - 0.0035", f"{yf} + 0.04", zz, 0.003, f"{P} - 0.04 + 0.0035", 0.003, WHT, detail=FINE)
    for k in range(5):
        c.box(f"Grade traseira - arame vertical {k + 1}", f"{x0} + 0.03 + {k / 4:.2f}*({xp} - {x0} - 0.06)", f"{yk} + 0.0035", cz0, 0.003, 0.003, ch, WHT, detail=FINE)
    for k in range(2):
        c.box(f"Grade lateral - arame vertical {k + 1}", f"{x0} - 0.0065", f"{yf} + 0.08 + {k}*({P} - 0.13)", cz0, 0.003, 0.003, ch, WHT, detail=FINE)

    # --- compressor bay (behind the right part of the front panel) --------------------
    kx = f"(({xp} + {x1})/2)"
    c.cyl("Compressor", kx, 0.01, hz0 + 0.012, 0.058, f"0.5*{H}", "Aço pintado preto")
    c.rev("Compressor - calota", "Front", [(kx, f"{hz0 + 0.012} + 0.5*{H}"), (f"{kx} + 0.058", f"{hz0 + 0.012} + 0.5*{H}", 0.07), (kx, f"{hz0 + 0.042} + 0.5*{H}")], 0.01, kx, "Aço pintado preto")
    c.cyl("Compressor - acumulador", f"{kx} + 0.045", f"{yk} - 0.06", hz0 + 0.05, 0.022, f"0.3*{H}", "Aço pintado preto", detail=FINE)
    c.cyl("Compressor - tubo de descarga", kx, 0.01, f"{hz0 + 0.04} + 0.5*{H}", 0.005, 0.05, "Cobre", detail=FINE)
    for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (0, 1)), 1):
        c.cyl(f"Compressor - coxim {k}", f"{kx} + {sx}*0.05", f"0.01 + {sy}*0.05", hz0, 0.012, 0.014, "Borracha", detail=FINE)
    c.box("Caixa elétrica", f"{xp} + 0.01", f"{yf} + 0.02", f"{H} - 0.14", f"{x1} - {xp} - 0.02", f"{P} - 0.06", 0.10, GALV)
    c.cyl("Capacitor", f"{xp} + 0.04", f"{yf} + 0.06", f"{H} - 0.19", 0.02, 0.05, "Alumínio anodizado", detail=FINE)

    # --- right side: electrical cover, handle, valve cover, service valves and lines ----
    c.box("Tampa elétrica", x1, -0.04, f"{H} - 0.19", 0.008, f"{P}/2 + 0.01", 0.13, WHT)
    c.cyl_x("Tampa elétrica - parafuso", -0.01, f"{H} - 0.17", f"{x1} + 0.008", 0.004, 0.0015, GALV, detail=FINE)
    c.box("Alça lateral", x1, f"{yf} + 0.03", f"{H} - 0.10", 0.012, 0.07, 0.03, GREY)
    c.box("Alça lateral - rebaixo", f"{x1} + 0.0005", f"{yf} + 0.035", f"{H} - 0.108", 0.011, 0.06, 0.008, "Plástico preto", detail=FINE)
    c.box("Etiqueta de dados", x1, f"{yf} + 0.03", f"{zf} - 0.02", 0.0005, 0.07, 0.06, "Alumínio anodizado", detail=FINE)
    vz0 = zb + 0.03
    c.profile("Tampa das válvulas", "Front",
              [(x1, vz0), (f"{x1} + {VC}", vz0), (f"{x1} + {VC}", vz0 + 0.15), (f"{x1} + {VC} - 0.02", vz0 + 0.19), (x1, vz0 + 0.19)],
              -0.03, f"{P}/2 - 0.04", GREY, in_plan=True)
    c.cyl_x("Tampa das válvulas - parafuso", f"{P}/4 - 0.035", vz0 + 0.12, f"{x1} + {VC}", 0.004, 0.0015, GALV, detail=FINE)
    for k in range(4):
        c.box(f"Tampa das válvulas - nervura {k + 1}", f"{x1} + {VC}", -0.02, vz0 + 0.02 + k * 0.02, 0.001, f"{P}/2 - 0.06", 0.006, GREY, detail=FINE)
    c.cyl("Prensa-cabo", f"{x1} + 0.02", 0.0, vz0 + 0.19, 0.009, 0.014, "Plástico preto", detail=FINE)
    c.cyl("Cabo de interligação", f"{x1} + 0.02", 0.0, vz0 + 0.19, 0.005, f"{H} - 0.19 - {vz0 + 0.19}", "Borracha", detail=FINE)
    # the valves stand out of the side panel just behind the cover; the lines leave towards the back
    yvlv = f"({yk} - 0.042)"
    for name, vz, r, ri in (("gás", vz0 + 0.105, 0.011, 0.0065), ("líquido", vz0 + 0.045, 0.008, 0.0035)):
        c.cyl_x(f"Válvula de serviço de {name}", yvlv, vz, x1, r, 0.036, "Latão")
        c.cyl_x(f"Válvula de serviço de {name} - tampa", yvlv, vz, f"{x1} + 0.036", r + 0.002, 0.008, "Latão", detail=FINE)
        c.cyl(f"Válvula de serviço de {name} - haste", f"{x1} + 0.024", yvlv, vz, r * 0.7, r + 0.012, "Latão", detail=FINE)
        c.cyl_y(f"Válvula de serviço de {name} - porca", f"{x1} + 0.024", vz, f"{yvlv} + {r}", r + 0.003, 0.014, "Latão", detail=FINE)
        c.cyl_y(f"Tubo de {name}", f"{x1} + 0.024", vz, f"{yvlv} + {r}", ri, 0.115, "Cobre", detail=FINE)
        c.cyl_y(f"Tubo de {name} - isolamento", f"{x1} + 0.024", vz, f"{yvlv} + {r} + 0.024", ri + 0.006, 0.08, "Borracha cinza")

    # --- base rails, rubber pads and anchor bolts ------------------------------------------
    for k, sx in enumerate((-1, 1), 1):
        rx = f"({xc} + {sx}*0.32*{CW})"
        c.box(f"Trilho da base {k}", f"{rx} - 0.025", f"{yf} - 0.02", 0.012, 0.05, f"{P} + 0.04", zb - 0.012, GALV)
        for j, sy in enumerate((-1, 1), 1):
            py = f"({sy}*({P}/2 + 0.005))"
            m = f"{k}.{j}"
            c.box(f"Coxim de borracha {m}", f"{rx} - 0.03", f"{py} - 0.02", 0, 0.06, 0.04, 0.012, "Borracha")
            c.cyl(f"Parafuso de fixação {m}", rx, py, 0.004, 0.004, zb + 0.008, GALV, detail=FINE)
            c.cyl(f"Parafuso de fixação {m} - porca", rx, py, zb, 0.008, 0.006, GALV, detail=FINE)
    c.cyl("Bico de dreno", f"{xf} + 0.05", 0.03, zb - 0.015, 0.008, 0.015, "Plástico preto", detail=FINE)
    return c
