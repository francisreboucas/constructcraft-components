"""Box de vidro frontal de correr: um vidro fixo e um de correr em vidro temperado 8 mm, roldanas aparentes sobre trilho tubular, perfis de alumínio."""

from _banheiro import *

GLASS, ALU, INOX, CHROME = "Vidro temperado", "Alumínio anodizado", "Inox escovado", "Cromado"
SEAL, NYLON = "Plástico translúcido", "Plástico cinza claro"


def build():
    c = Component("Box de vidro", "furniture", "box-vidro", "Furniture")
    W = c.param("Largura", 1.0)
    H = c.param("Altura", 1.9)
    A = c.param("Abertura", 0, "Length", True)
    c.open_pose["Abertura"] = 0.42
    desc = "Box frontal de correr, vidro temperado incolor 8 mm, roldanas aparentes e perfis de alumínio, entre paredes"
    c.type("Box frontal 100 cm", desc, Largura=1.0)
    c.type("Box frontal 120 cm", desc, Largura=1.2)
    c.type("Box frontal 150 cm", desc, Largura=1.5)

    TG = 0.008  # glass
    ys, yf, yr = 0, 0.045, 0.024  # planes of the sliding glass (bathroom side), the fixed glass (shower side) and the rail
    xL, xR = f"(-{W}/2)", f"({W}/2)"
    Wp = f"(({W} + 0.05)/2 - 0.01)"  # each glass: they overlap 4 cm
    zr = f"({H} - 0.0485)"  # the rail's axis
    zw = f"({zr} + 0.029)"  # the wheels' axis: the groove sits on the rail
    zs0, zs1 = 0.01, f"({zr} + 0.01)"  # sliding glass
    zf0, zf1 = 0.004, f"({zr} - 0.02)"  # fixed glass
    xf0, xf1 = f"({xL} + 0.006)", f"({xL} + 0.006 + {Wp})"
    xs0, xs1 = f"({xR} - 0.006 - {Wp} - {A})", f"({xR} - 0.006 - {A})"

    # --- coarse stand-ins ---
    c.box("Vidro fixo simplificado", xf0, yf - TG / 2, 0, Wp, TG, zf1, GLASS, COARSE, in_plan=True)
    c.box("Vidro de correr simplificado", xs0, ys - TG / 2, 0, Wp, TG, zs1, GLASS, COARSE, in_plan=True)
    c.box("Trilho simplificado", xL, yr - 0.0125, f"{zr} - 0.0125", W, 0.025, f"{H} - {zr} + 0.0125", INOX, COARSE)
    c.box("Perfil de piso simplificado", xL, -0.015, 0, W, yf + 0.03, 0.018, ALU, COARSE, in_plan=True)

    # --- floor channel: base and four lips guiding the glasses ---
    c.box("Perfil de piso - base", xL, -0.015, 0, W, yf + 0.03, 0.003, ALU, in_plan=True)
    for nm, y0 in (("aba externa", -0.012), ("guia do vidro de correr", 0.0095), ("aba do vidro fixo externa", yf - 0.0095), ("aba do vidro fixo interna", yf + 0.0065)):
        c.box(f"Perfil de piso - {nm}", xL, y0, 0.003, W, 0.003, 0.015, ALU)
    for i, x in enumerate((f"{xf0} + 0.08", f"{xf1} - 0.08"), 1):
        c.box(f"Calço de apoio do vidro fixo {i}", f"{x} - 0.02", yf - 0.0045, 0.003, 0.04, 0.009, 0.001, "Borracha", FINE)

    # --- wall channels: a U holding the fixed glass, a U stop with a seal for the sliding glass ---
    zu = f"({zf1} + 0.005)"
    c.box("Perfil U de parede - fundo", xL, yf - 0.015, 0, 0.003, 0.03, zu, ALU, in_plan=True)
    c.box("Perfil U de parede - aba externa", f"{xL} + 0.003", yf - 0.015, 0, 0.017, 0.003, zu, ALU, in_plan=True)
    c.box("Perfil U de parede - aba interna", f"{xL} + 0.003", yf + 0.012, 0, 0.017, 0.003, zu, ALU, in_plan=True)
    c.box("Perfil batente - fundo", f"{xR} - 0.003", ys - 0.015, 0, 0.003, 0.03, zs1, ALU, in_plan=True)
    c.box("Perfil batente - aba externa", f"{xR} - 0.02", ys - 0.015, 0, 0.017, 0.003, zs1, ALU, in_plan=True)
    c.box("Perfil batente - aba interna", f"{xR} - 0.02", ys + 0.012, 0, 0.017, 0.003, zs1, ALU, in_plan=True)
    c.box("Vedação do perfil batente", f"{xR} - 0.006", ys - 0.006, 0.02, 0.003, 0.012, f"{zs1} - 0.04", "Borracha", FINE)
    for i, k in enumerate((0.15, 0.5, 0.85), 1):
        c.cyl_x(f"Parafuso do perfil U {i}", yf, f"{zu}*{k}", f"{xL} + 0.003", 0.004, 0.002, INOX, FINE)
        c.cyl_x(f"Parafuso do perfil batente {i}", ys, f"{zs1}*{k}", f"{xR} - 0.0045", 0.004, 0.0015, INOX, FINE)

    # --- rail: a 25 mm tube between two wall roses, stops for the rollers ---
    c.cyl_x("Trilho", yr, zr, f"{xL} + 0.006", 0.0125, f"{W} - 0.012", INOX, in_plan=True)
    for nm, x0, x1 in (("esquerdo", xL, f"{xL} + 0.006"), ("direito", f"{xR} - 0.006", xR)):
        c.profile(f"Suporte de parede do trilho {nm}", "Side", disc(yr, zr, 0.022), x0, 0.006, INOX)
        xc = f"{xL} + 0.006" if nm == "esquerdo" else f"{xR} - 0.026"
        c.cyl_x(f"Luva do suporte do trilho {nm}", yr, zr, xc, 0.016, 0.02, INOX)
        c.cyl_x(f"Parafuso da luva {nm}", yr, f"{zr} + 0.0155", f"{xc} + 0.008", 0.0025, 0.004, INOX, FINE)
    wheel = 0.02
    stops = (("esquerdo", f"{xL} + 0.108"), ("direito", f"{xR} - 0.006 - 0.12 + {wheel} + 0.002"))
    for nm, x in stops:
        c.cyl_x(f"Batente do trilho {nm}", yr, zr, x, 0.0155, 0.02, CHROME)
        c.cyl_x(f"Amortecedor do batente {nm}", yr, zr, f"{x} + 0.02" if nm == "esquerdo" else f"{x} - 0.004", 0.012, 0.004, "Borracha", FINE)

    # --- fixed glass: brackets under the rail, seals at its free edge ---
    c.box("Vidro fixo", xf0, yf - TG / 2, zf0, Wp, TG, f"{zf1} - {zf0}", GLASS, in_plan=True)
    c.box("Vedação do vidro fixo", f"{xf1} - 0.004", yf - 0.0065, zf0, 0.007, 0.013, f"{zf1} - {zf0}", SEAL)
    c.box("Aba de vedação do vidro fixo", f"{xf1} - 0.002", 0.0135, f"{zf0} + 0.02", 0.0015, yf - 0.0065 - 0.0135, f"{zf1} - {zf0} - 0.1", SEAL, FINE)
    for i, x in enumerate((f"{xf0} + 0.14", f"{xf1} - 0.12"), 1):
        c.box(f"Suporte do vidro fixo {i}", f"{x} - 0.02", 0.031, f"{zr} - 0.06", 0.04, 0.021, 0.054, CHROME)
        c.box(f"Suporte do vidro fixo {i} - garra", f"{x} - 0.012", 0.026, f"{zr} - 0.0175", 0.024, 0.007, 0.006, CHROME, FINE)
        for j, dx in enumerate((-0.01, 0.01), 1):
            c.cyl_y(f"Parafuso do suporte do vidro fixo {i}.{j}", f"{x} + {dx}", f"{zr} - 0.04", 0.052, 0.0035, 0.0015, INOX, FINE)

    # --- sliding glass: hangs from two rollers, seals, handle ---
    c.box("Vidro de correr", xs0, ys - TG / 2, zs0, Wp, TG, f"{zs1} - {zs0}", GLASS, in_plan=True)
    c.box("Vedação vertical do vidro de correr", f"{xs1} - 0.004", ys - 0.0065, zs0, 0.007, 0.013, f"{zs1} - {zs0}", SEAL)
    c.box("Vedação inferior do vidro de correr", xs0, ys - 0.0055, 0.004, Wp, 0.011, 0.016, SEAL)
    for i, xw in enumerate((f"{xs0} + 0.12", f"{xs1} - 0.12"), 1):
        top = [(f"{xw} - 0.03", f"{zs1} - 0.07"), (f"{xw} + 0.03", f"{zs1} - 0.07"), (f"{xw} + 0.03", zw, 0.03), (f"{xw} - 0.03", zw)]
        c.profile(f"Placa da roldana {i}", "Front", top, TG / 2, 0.004, CHROME)
        c.profile(f"Contraplaca da roldana {i}", "Front", rrect(f"{xw} - 0.03", f"{zs1} - 0.07", f"{xw} + 0.03", f"{zs1} - 0.005", 0.008), -TG / 2 - 0.004, 0.004, CHROME)
        c.cyl_y(f"Eixo da roldana {i}", xw, zw, TG / 2 + 0.004, 0.0045, yr + 0.011 - TG / 2 - 0.004, INOX)
        c.rev(f"Roda da roldana {i}", "Plan", [(xw, yr - 0.006), (add(xw, wheel), yr - 0.006), (add(xw, wheel), yr - 0.0035), (add(xw, 0.0165), yr),
                                               (add(xw, wheel), yr + 0.0035), (add(xw, wheel), yr + 0.006), (xw, yr + 0.006)], zw, xw, NYLON)
        c.cyl_y(f"Rolamento da roldana {i}", xw, zw, yr - 0.0065, 0.008, 0.013, INOX, FINE)
        c.cyl_y(f"Porca do eixo da roldana {i}", xw, zw, yr + 0.006, 0.0065, 0.004, INOX, FINE)
        c.box(f"Trava antidescarrilamento {i}", f"{xw} - 0.008", TG / 2 + 0.004, f"{zr} - 0.0195", 0.016, 0.019, 0.005, CHROME, FINE)
        for j, dx in enumerate((-0.016, 0.016), 1):
            c.cyl_y(f"Parafuso da roldana {i}.{j}", f"{xw} + {dx}", f"{zs1} - 0.035", -TG / 2 - 0.0055, 0.004, 0.0015, CHROME, FINE)
    # handle: a tube on two posts outside, a flush knob inside (it passes the fixed glass)
    xh, zh = f"({xs0} + 0.06)", 1.0
    c.cyl("Puxador tubular", xh, -0.036, zh - 0.15, 0.0095, 0.3, CHROME, in_plan=True)
    for j, dz in enumerate((-0.12, 0.12), 1):
        c.cyl_y(f"Haste do puxador {j}", xh, zh + dz, -0.03, 0.0065, 0.026, CHROME)
        c.cyl_y(f"Bucha do puxador {j}", xh, zh + dz, -TG / 2 - 0.002, 0.009, 0.002, "Plástico preto", FINE)
    c.cyl_y("Puxador interno", xh, zh, TG / 2, 0.022, 0.007, CHROME)
    c.cyl_y("Bucha do puxador interno", xh, zh, TG / 2 - 0.0005, 0.024, 0.0015, "Plástico preto", FINE)
    c.cyl("Tampa dos puxadores", xh, -0.036, zh + 0.15, 0.0095, 0.004, CHROME, FINE)
    c.cyl("Tampa inferior dos puxadores", xh, -0.036, zh - 0.154, 0.0095, 0.004, CHROME, FINE)

    # plan symbol: the sliding direction
    c.extrusion("Seta de correr", [(-0.15, -0.06), (-0.1, -0.075), (-0.1, -0.0635), (0.1, -0.0635), (0.1, -0.0565), (-0.1, -0.0565), (-0.1, -0.045)], 0, 0.001, ALU)
    c.plan_only("Seta de correr")
    c.preview_size = (1.0, 0.6, 1.9)
    return c
