"""Espelheira: armário de banheiro de parede com duas portas de espelho, prateleiras de vidro, iluminação e objetos de higiene."""

from _banheiro import *

MDF, HDF, STEEL = "MDF branco", "Laminado branco", "Aço galvanizado"
MIRROR = "Espelho"


def bottle(c, name, x, y, z, r, h, body, cap, neck=0.4, cap_h=0.025):
    """A bottle turned about a vertical axis, with a shoulder, a neck and a screw cap."""
    rn = r * neck
    c.rev(name, "Front", [(x, z), (add(x, r - 0.003), z), (add(x, r), add(z, 0.004)), (add(x, r), add(z, h * 0.78)),
                          (add(x, rn + 0.002), add(z, h * 0.95)), (add(x, rn), add(z, h)), (x, add(z, h))], y, x, body, detail=FINE)
    c.cyl(f"{name} - tampa", x, y, add(z, h - 0.004), rn + 0.0025, cap_h, cap, FINE)


def build():
    c = Component("Espelheira", "casework", "espelheira", "Casework")
    W = c.param("Largura", 0.6)
    D = c.param("Profundidade", 0.13)
    H = c.param("Altura", 0.6)
    E = c.param("Elevacao", 1.2, "Length", True)
    A = c.angle("AnguloPortas", 0, open_at=100)
    c.material(MDF, (240, 240, 235), "Wood", "Satin")
    c.material(MIRROR, (222, 228, 232), "Metal", "Polished")  # same values as guarda_roupa.py
    c.material("Fita de LED", (255, 244, 214), "Plastic", "Glossy", 0.3)
    c.material("Papel", (238, 232, 214), "Generic", "Matte")
    desc = "Armário de banheiro de sobrepor com duas portas de espelho, prateleiras de vidro e luz de LED"
    c.type("Espelheira 60 cm", desc, Largura=0.6, Altura=0.6)
    c.type("Espelheira 80 cm", desc, Largura=0.8, Altura=0.65)
    c.type("Espelheira 100 cm", desc, Largura=1.0, Altura=0.7)
    c.preview_base = 1.2

    T, TD, TM = 0.015, 0.015, 0.004  # carcass panels, doors' MDF, mirrors
    xL, xR = f"(-{W}/2)", f"({W}/2)"
    yF = f"(-{D})"
    yD = f"({yF} + {TD + TM})"  # back face of the doors
    yC = f"({yD} + 0.001)"  # front edge of the carcass
    dc = f"(-{yC})"  # depth of the carcass
    z0 = f"({E} + 0.02)"  # bottom of the carcass: the doors hang 2 cm lower, a finger pull
    zT = f"({E} + {H})"
    zi = f"({z0} + {T})"  # inside floor
    hi = f"({H} - 0.02 - 2*{T})"  # inside height
    xi0, wi = f"({xL} + {T})", f"({W} - 2*{T})"
    g = Grp(c)

    # --- coarse stand-in ---
    c.box("Espelheira simplificada", xL, yF, E, W, D, H, MIRROR, COARSE, in_plan=True)

    # --- carcass ---
    c.box("Lateral esquerda", xL, yC, z0, T, dc, f"{H} - 0.02", MDF, in_plan=True)
    c.box("Lateral direita", f"{xR} - {T}", yC, z0, T, dc, f"{H} - 0.02", MDF, in_plan=True)
    c.box("Tampo", xi0, yC, f"{zT} - {T}", wi, dc, T, MDF, in_plan=True)
    c.box("Base", xi0, yC, z0, wi, dc, T, MDF)
    c.box("Fundo", xi0, -0.006, zi, wi, 0.003, hi, HDF)
    c.box("Travessa de fixação", xi0, -0.003, f"{zT} - {T} - 0.08", wi, 0.003, 0.08, MDF)
    for nm, x in (("esquerdo", f"{xi0} + 0.05"), ("direito", f"{xR} - {T} - 0.05")):
        c.cyl_y(f"Parafuso de fixação {nm}", x, f"{zT} - {T} - 0.04", -0.0072, 0.0045, 0.0012, STEEL, FINE)
        c.cyl_y(f"Capa do parafuso {nm}", x, f"{zT} - {T} - 0.04", -0.0082, 0.0065, 0.001, "Branco", FINE)
    c.box("Fita de borda da base", xi0, f"{yC} - 0.0005", z0, wi, 0.0005, T, HDF, FINE)
    c.box("Fita de borda do tampo", xi0, f"{yC} - 0.0005", f"{zT} - {T}", wi, 0.0005, T, HDF, FINE)

    # --- LED strip under the bottom panel, hidden by the doors' overhang ---
    c.box("Perfil da luz de LED", f"{xi0} + 0.02", f"{yC} + 0.012", f"{z0} - 0.008", f"{wi} - 0.04", 0.016, 0.008, "Alumínio anodizado")
    c.box("Difusor da luz de LED", f"{xi0} + 0.022", f"{yC} + 0.014", f"{z0} - 0.0095", f"{wi} - 0.044", 0.012, 0.0015, "Fita de LED")
    c.box("Tampa do perfil esquerda", f"{xi0} + 0.018", f"{yC} + 0.012", f"{z0} - 0.0095", 0.002, 0.016, 0.0095, "Plástico cinza claro", FINE)
    c.box("Tampa do perfil direita", f"{xi0} + {wi} - 0.02", f"{yC} + 0.012", f"{z0} - 0.0095", 0.002, 0.016, 0.0095, "Plástico cinza claro", FINE)
    c.box("Cabo da luz de LED", f"{xi0} + {wi} - 0.03", f"{yC} + 0.028", f"{z0} - 0.004", 0.004, f"{dc} - 0.034", 0.004, "Plástico preto", FINE)

    # --- glass shelves on pins ---
    zs = [f"({zi} + {hi}*{k:.4f} - 0.003)" for k in (1 / 3, 2 / 3)]
    ys, ds = f"({yC} + 0.012)", f"({dc} - 0.022)"
    for i, z in enumerate(zs, 1):
        c.box(f"Prateleira de vidro {i}", f"{xi0} + 0.002", ys, z, f"{wi} - 0.004", ds, 0.006, "Vidro temperado")
        for j, yp in enumerate((f"{ys} + 0.02", f"{ys} + {ds} - 0.02"), 1):
            c.cyl_x(f"Suporte da prateleira {i} - esquerdo {j}", yp, f"{z} - 0.003", xi0, 0.003, 0.01, "Plástico translúcido", detail=FINE)
            c.cyl_x(f"Suporte da prateleira {i} - direito {j}", yp, f"{z} - 0.003", f"{xR} - {T} - 0.01", 0.003, 0.01, "Plástico translúcido", detail=FINE)

    # --- two mirror doors, hinged at the sides ---
    wd = f"({W}/2 - 0.0015)"
    for i, side, hx, xi in ((1, "left", f"({xL} + 0.0005)", xi0), (2, "right", f"({xR} - 0.0005)", f"({xR} - {T})")):
        g.door_box(f"Porta {i}", (hx, yD), A, 0, wd, 0, TD, E, H, MDF, side=side, in_plan=True)
        g.door_box(f"Espelho da porta {i}", (hx, yD), A, 0.0015, f"{wd} - 0.0015", TD, TD + TM, f"{E} + 0.0015", f"{H} - 0.003", MIRROR, side=side, in_plan=True)
        g.door_box(f"Fita adesiva do espelho {i}", (hx, yD), A, 0.03, f"{wd} - 0.03", TD - 0.0005, TD, f"{E} + 0.05", f"{H} - 0.1", "Borracha", side=side, detail=FINE)
        hinge(g, f"Dobradiça superior da porta {i}", side, hx, yD, xi, f"{zT} - 0.09", A)
        hinge(g, f"Dobradiça inferior da porta {i}", side, hx, yD, xi, f"{z0} + 0.09", A)
        for nm, z in (("inferior", f"{z0} + 0.004"), ("superior", f"{zT} - 0.012")):
            g.door_box(f"Batente {nm} da porta {i}", (hx, yD), A, f"{wd} - 0.03", f"{wd} - 0.022", -0.0012, 0, z, 0.008, "Plástico translúcido", side=side, detail=FINE)

    # --- what is kept inside ---
    ym = f"({yC}/2 - 0.002)"

    def xf(k):
        return f"({xi0} + {wi}*{k})"

    # bottom: toothbrush cup, liquid soap, cotton jar
    x = xf(0.17)
    c.rev("Copo de escovas", "Front", [(x, zi), (add(x, 0.027), zi), (add(x, 0.031), add(zi, 0.095)), (add(x, 0.028), add(zi, 0.095)),
                                        (add(x, 0.024), add(zi, 0.006)), (x, add(zi, 0.006))], ym, x, "Plástico translúcido", detail=FINE)
    for j, (dx, s, mat) in enumerate(((-0.014, -1, "Plástico azul"), (0.008, 1, "Plástico verde")), 1):
        x0, sh = add(x, dx), 0.014 * s  # foot of the handle, lean of its top
        yj = f"{ym} - {0.004 - 0.006 * (j - 1):.4f}"
        c.profile(f"Escova de dentes {j}", "Front", [(x0, add(zi, 0.008)), (add(x0, 0.006), add(zi, 0.008)), (add(x0, 0.006 + sh), add(zi, 0.17)),
                                                       (add(x0, sh), add(zi, 0.17))], yj, 0.005, mat, FINE)
        c.box(f"Cerdas da escova {j}", add(x0, sh * 0.85 - 0.001), f"{yj} - 0.008", add(zi, 0.135), 0.008, 0.008, 0.028, "Branco", FINE)
    x = xf(0.48)
    bottle(c, "Frasco de sabonete líquido", x, ym, zi, 0.03, 0.11, "Plástico translúcido", "Branco", neck=0.35)
    c.cyl("Válvula pump do sabonete", x, ym, add(zi, 0.13), 0.005, 0.03, "Branco", FINE)
    c.cyl("Cabeça do pump do sabonete", x, ym, add(zi, 0.158), 0.012, 0.014, "Branco", FINE)
    c.box("Bico do pump do sabonete", x, f"{ym} - 0.003", add(zi, 0.162), 0.032, 0.006, 0.006, "Branco", FINE)
    c.box("Sabonete líquido", f"{x} - 0.025", f"{ym} - 0.0302", add(zi, 0.025), 0.05, 0.0005, 0.03, "Plástico verde", FINE)
    x = xf(0.8)
    c.rev("Pote de algodão", "Front", [(x, zi), (add(x, 0.04), zi), (add(x, 0.04), add(zi, 0.1)), (x, add(zi, 0.1))], ym, x, "Vidro", detail=FINE)
    c.cyl("Algodão", x, ym, add(zi, 0.004), 0.036, 0.085, "Branco", FINE)
    c.cyl("Tampa do pote de algodão", x, ym, add(zi, 0.1), 0.042, 0.012, "Inox escovado", FINE)

    # first shelf: perfume, deodorant, cream jar, lotion
    z1 = f"({zs[0]} + 0.006)"
    x = xf(0.16)
    c.box("Frasco de perfume", f"{x} - 0.025", f"{ym} - 0.016", z1, 0.05, 0.032, 0.085, "Vidro fumê", detail=FINE)
    c.cyl("Válvula do perfume", x, ym, add(z1, 0.085), 0.006, 0.012, "Cromado", FINE)
    c.cyl("Tampa do perfume", x, ym, add(z1, 0.097), 0.014, 0.025, "Plástico preto brilhante", FINE)
    x = xf(0.38)
    c.cyl("Desodorante", x, ym, z1, 0.024, 0.115, "Aço pintado branco", FINE)
    c.rev("Tampa do desodorante", "Front", [(x, add(z1, 0.115)), (add(x, 0.0245), add(z1, 0.115)), (add(x, 0.0245), add(z1, 0.13), 0.02), (x, add(z1, 0.14))], ym, x, "Plástico azul", detail=FINE)
    x = xf(0.6)
    c.rev("Pote de creme", "Front", [(x, z1), (add(x, 0.03), z1), (add(x, 0.034), add(z1, 0.04)), (x, add(z1, 0.04))], ym, x, "Branco", detail=FINE)
    c.cyl("Tampa do pote de creme", x, ym, add(z1, 0.04), 0.035, 0.016, "Latão", FINE)
    bottle(c, "Frasco de loção", xf(0.83), ym, z1, 0.026, 0.13, "Plástico azul", "Branco", neck=0.45, cap_h=0.03)

    # second shelf: medicine box and bottle, hairbrush
    z2 = f"({zs[1]} + 0.006)"
    x = xf(0.2)
    c.box("Caixa de remédio", f"{x} - 0.04", f"{ym} - 0.02", z2, 0.08, 0.04, 0.11, "Papel", detail=FINE)
    c.box("Faixa da caixa de remédio", f"{x} - 0.04", f"{ym} - 0.0205", add(z2, 0.07), 0.08, 0.0005, 0.012, "Plástico vermelho", detail=FINE)
    bottle(c, "Frasco de remédio", xf(0.45), ym, z2, 0.02, 0.08, "Vidro fumê", "Branco", neck=0.6, cap_h=0.018)
    x = xf(0.73)
    c.box("Escova de cabelo - cabo", f"{x} - 0.06", f"{ym} - 0.01", z2, 0.13, 0.02, 0.014, "Madeira clara", detail=FINE)
    c.box("Escova de cabelo - almofada", f"{x} + 0.035", f"{ym} - 0.03", z2, 0.07, 0.06, 0.022, "Borracha", detail=FINE)
    c.box("Escova de cabelo - cerdas", f"{x} + 0.04", f"{ym} - 0.025", add(z2, 0.022), 0.06, 0.05, 0.012, "Plástico preto", detail=FINE)
    return c
