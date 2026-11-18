"""Pia de cozinha: bancada de granito com cuba inox de embutir, torneira de bica alta, sifão, registros e gabinete."""

from kit import *
from kit import _points


def sweep(c, name, plane, path, offset, section, material, detail=FULL, in_plan=False, void=False):
    """A closed `section` (u to the left of the path, v along the plane's normal) carried along `path`."""
    shape = {"Sweep": {"plane": plane, "path": _points(path), "offset": e(offset), "profile": _points(section)}}
    c._add(name, shape, material, detail, in_plan, void)


def tube(c, name, plane, path, offset, radius, material, detail=FULL, in_plan=False, void=False):
    sweep(c, name, plane, path, offset, disc(0, 0, radius), material, detail, in_plan, void)


def build():
    c = Component("Pia de cozinha com bancada", "plumbing", "pia-cozinha", "Plumbing")
    L = c.param("Largura", 1.2)
    P = c.param("Profundidade", 0.55)
    A = c.param("Altura", 0.9)
    ang = c.angle("AberturaPortas", 0, open_at=100)
    desc = "Bancada de granito com cuba inox e gabinete"
    c.type("Pia cozinha 120 cm", desc, Largura=1.2)
    c.type("Pia cozinha 150 cm", desc, Largura=1.5)
    c.type("Pia cozinha 200 cm", desc, Largura=2.0)
    c.mep = {"Fixture": {"drain_units": 3, "supply_weight": 0.7, "hot_water": True}}
    c.connector("Esgoto", "Sanitary", 0, f"{P} / 2", 0.5, "Back", 0.05)
    c.connector("Água fria", "ColdWater", -0.1, f"{P} / 2", 0.6, "Back", 0.02)
    c.connector("Água quente", "HotWater", 0.1, f"{P} / 2", 0.6, "Back", 0.02)
    c.material("Granito cinza", (88, 88, 92), "Generic", "Polished")

    INOX, CHROME, LAM = "Inox escovado", "Cromado", "Laminado branco"
    x0, y0, y1 = f"-{L} / 2", f"-{P} / 2", f"{P} / 2"

    def z(dz):  # from the top of the countertop
        return f"{A} + {dz}" if dz >= 0 else f"{A} - {-dz}"

    def yb(dy):  # from the back (the wall)
        return f"{P} / 2 - {dy}"

    def yf(dy):  # from the front edge of the countertop
        return f"{dy} - {P} / 2"

    # --- coarse stand-ins (the old pieces) ---
    c.box("Gabinete simplificado", x0, yf(0.03), 0.1, L, f"{P} - 0.03", f"{A} - 0.13", LAM, COARSE)
    c.box("Cuba simplificada", -0.25, yf(0.075), z(-0.2), 0.5, f"{P} - 0.15", 0.17, INOX, COARSE, in_plan=True)

    # --- countertop ---
    c.box("Bancada", x0, y0, z(-0.03), L, P, 0.03, "Granito cinza", ALL, in_plan=True)
    c.box("Saia frontal", x0, y0, z(-0.06), L, 0.02, 0.03, "Granito cinza")
    c.box("Rodabanca", x0, yb(0.02), A, L, 0.02, 0.07, "Granito cinza", in_plan=True)
    # The bowl: inner outline 48 cm wide, 8.5 cm from the front and the back.
    bx, by0, by1, br = 0.24, yf(0.085), yb(0.085), 0.06
    c.profile("Recorte da cuba", "Plan", rrect(-bx, by0, bx, by1, br), z(-0.031), 0.032, "Granito cinza", void=True)
    # Drainer grooves cut in the stone, to the right of the bowl.
    for i in range(7):
        yg = f"{(i - 3) * 0.045 / 0.55:.5f} * {P} - 0.004"
        c.box(f"Sulco do escorredor {i + 1}", bx + 0.055, yg, z(-0.004), f"min({L} / 2 - 0.355, 0.45)", 0.008, 0.005, "Granito cinza", FINE, void=True)

    # --- bowl: walls swept around the outline (no void, so the strainer stays whole) ---
    wall = [(-0.004, -0.004), (0.022, -0.004), (0.022, 0, -0.022), (0, 0.022), (0, 0.16), (-0.016, 0.16), (-0.016, 0.157), (-0.004, 0.157)]
    path = [
        (0, by1), (-bx + br, by1, br), (-bx, f"{by1} - {br}"), (-bx, f"{by0} + {br}", br), (-bx + br, by0),
        (bx - br, by0, br), (bx, f"{by0} + {br}"), (bx, f"{by1} - {br}", br), (bx - br, by1), (0, by1),
    ]
    sweep(c, "Cuba", "Plan", path, z(-0.19), wall, INOX)
    c.profile("Fundo da cuba", "Plan", rrect(-bx, by0, bx, by1, br), z(-0.1935), 0.0035, INOX, in_plan=True)
    zf = -0.19  # the bowl's floor
    c.rev("Válvula da cuba", "Front", [(0.031, z(zf)), (0.046, z(zf)), (0.044, z(zf + 0.0022)), (0.031, z(zf + 0.0022))], 0, 0, CHROME, in_plan=True)
    c.cyl("Cesto da válvula", 0, 0, z(zf), 0.031, 0.0012, INOX, FINE)
    for i, r in enumerate((0.012, 0.019, 0.026), 1):
        c.rev(f"Furos do cesto {i}", "Front", rect(r - 0.0015, z(zf + 0.001), r + 0.0015, z(zf + 0.0016)), 0, 0, "Borracha", detail=FINE)
    c.rev("Pino do cesto", "Front", [(0, z(zf + 0.001)), (0.004, z(zf + 0.001)), (0.004, z(zf + 0.007)), (0.007, z(zf + 0.009), 0.0045), (0, z(zf + 0.013))], 0, 0, CHROME, detail=FINE)

    # --- drain: strainer body, tailpiece, bottle trap, arm to the wall ---
    c.cyl("Corpo da válvula", 0, 0, z(-0.225), 0.04, 0.0315, INOX)
    c.cyl("Porca da válvula", 0, 0, z(-0.213), 0.05, 0.014, "Branco", FINE)
    c.cyl("Tubo de descida", 0, 0, 0.55, 0.019, f"{A} - 0.775", "Branco")
    c.cyl("Porca de descida", 0, 0, z(-0.245), 0.027, 0.02, "Branco", FINE)
    c.rev("Copo do sifão", "Front", [(0, 0.43), (0.03, 0.43, 0.02), (0.045, 0.447), (0.045, 0.535), (0.03, 0.552), (0, 0.552)], 0, 0, "Branco")
    c.cyl("Porca do sifão", 0, 0, 0.548, 0.03, 0.018, "Branco", FINE)
    c.rev("Tampa de limpeza do sifão", "Front", [(0, 0.418), (0.022, 0.418), (0.022, 0.432), (0, 0.432)], 0, 0, "Branco", detail=FINE)
    c.cyl_y("Braço do sifão", 0, 0.5, 0.04, 0.02, f"{P} / 2 - 0.04", "Branco")
    c.cyl_y("Porca do braço do sifão", 0, 0.5, 0.042, 0.028, 0.02, "Branco", FINE)
    c.cyl_y("Luva de esgoto", 0, 0.5, yb(0.045), 0.025, 0.045, "PVC")
    c.cyl_y("Canopla do esgoto", 0, 0.5, yb(0.006), 0.04, 0.006, "Branco", FINE)

    # --- angle valves on the wall and hoses to the faucet ---
    yv = yb(0.045)
    for name, s in (("fria", -1), ("quente", 1)):
        xv = 0.1 * s
        c.cyl_y(f"Canopla do registro {name}", xv, 0.6, yb(0.005), 0.026, 0.005, CHROME, FINE)
        c.cyl_y(f"Niple do registro {name}", xv, 0.6, yb(0.04), 0.009, 0.04, CHROME)
        c.rev(f"Registro {name}", "Plan", [(xv, yb(0.07)), (xv + 0.011, yb(0.07)), (xv + 0.014, yb(0.062)), (xv + 0.014, yb(0.036)), (xv, yb(0.036))], 0.6, xv, CHROME)
        c.rev(f"Volante do registro {name}", "Plan", [(xv, yb(0.088)), (xv + 0.014, yb(0.088), 0.004), (xv + 0.017, yb(0.084)), (xv + 0.017, yb(0.076)), (xv + 0.006, yb(0.07)), (xv, yb(0.07))], 0.6, xv, "Branco", detail=FINE)
        c.cyl(f"Saída do registro {name}", xv, yv, 0.6, 0.007, 0.03, CHROME, FINE)
        c.cyl(f"Porca inferior do flexível {name}", xv, yv, 0.626, 0.0095, 0.016, CHROME, FINE)
        xt, r = 0.012 * s, 0.044
        tube(c, f"Flexível {name}", "Front", [
            (xv, 0.64), (xv, 0.69, r * s), (xv - r * s, 0.69 + r, -r * s), (xt, 0.69 + 2 * r), (xt, z(-0.085)),
        ], yv, 0.006, INOX)
        c.cyl(f"Porca superior do flexível {name}", xt, yv, z(-0.098), 0.0085, 0.016, CHROME, FINE)

    # --- faucet: single-lever mixer with a high spout ---
    yq = yb(0.047)
    c.cyl("Haste roscada da torneira", 0, yq, z(-0.085), 0.017, 0.056, "Latão", FINE)
    c.cyl("Porca de fixação da torneira", 0, yq, z(-0.048), 0.026, 0.012, "Latão", FINE)
    c.cyl("Arruela da torneira", 0, yq, z(-0.035), 0.03, 0.005, "Borracha", FINE)
    c.rev("Base da torneira", "Front", [(0, A), (0.027, A), (0.027, z(0.004), 0.012), (0.021, z(0.012)), (0.021, z(0.085), 0.014), (0.0125, z(0.1)), (0, z(0.1))], yq, 0, CHROME, in_plan=True)
    rn = 0.075
    tube(c, "Bica", "Side", [
        (yq, z(0.095)), (yq, z(0.285), rn), (f"{yq} - {2 * rn}", z(0.285)), (f"{yq} - {2 * rn}", z(0.24)),
    ], 0, 0.011, CHROME, in_plan=True)
    c.cyl("Arejador", 0, f"{yq} - {2 * rn}", z(0.222), 0.0128, 0.022, CHROME, FINE)
    c.cyl("Tela do arejador", 0, f"{yq} - {2 * rn}", z(0.2205), 0.0095, 0.003, "Plástico cinza", FINE)
    c.cyl_x("Cartucho do misturador", yq, z(0.05), 0.016, 0.0155, 0.018, CHROME)
    c.profile("Alavanca do misturador", "Front", [(0.03, z(0.043)), (0.04, z(0.04)), (0.092, z(0.085), 0.0045), (0.088, z(0.092)), (0.036, z(0.058)), (0.03, z(0.058))], f"{yq} - 0.007", 0.014, CHROME)
    c.cyl_x("Tampa do cartucho", yq, z(0.05), 0.034, 0.011, 0.003, CHROME, FINE)
    c.box("Indicador frio", 0.0355, f"{yq} - 0.0078", z(0.046), 0.004, 0.001, 0.004, "Plástico azul", FINE)
    c.box("Indicador quente", 0.0355, f"{yq} - 0.0078", z(0.052), 0.004, 0.001, 0.004, "Plástico vermelho", FINE)

    # --- cabinet: carcass 1 cm inside the countertop's ends, four doors ---
    H = f"({L} / 2 - 0.01)"  # half width of the carcass
    yc = yf(0.05)  # front of the carcass (behind the doors)
    dc = f"{P} - 0.05"
    zt = f"{A} - 0.03"
    c.box("Lateral esquerda", f"-{H}", yc, 0.1, 0.018, dc, f"{A} - 0.13", LAM)
    c.box("Lateral direita", f"{H} - 0.018", yc, 0.1, 0.018, dc, f"{A} - 0.13", LAM)
    c.box("Fundo do gabinete", f"0.018 - {H}", yc, 0.1, f"2 * {H} - 0.036", dc, 0.018, LAM)
    c.box("Divisória esquerda", f"-{H} / 2 - 0.009", f"{yc} + 0.002", 0.118, 0.018, f"{dc} - 0.002", f"{A} - 0.148", LAM)
    c.box("Divisória direita", f"{H} / 2 - 0.009", f"{yc} + 0.002", 0.118, 0.018, f"{dc} - 0.002", f"{A} - 0.148", LAM)
    c.box("Travessa frontal", f"0.018 - {H}", yc, z(-0.11), f"2 * {H} - 0.036", 0.018, 0.08, LAM)
    c.box("Travessa traseira", f"0.018 - {H}", yb(0.018), z(-0.13), f"2 * {H} - 0.036", 0.018, 0.1, LAM)
    c.box("Rodapé frontal", f"-{H}", yf(0.09), 0, f"2 * {H}", 0.018, 0.1, LAM)
    c.box("Rodapé esquerdo", f"-{H}", yf(0.108), 0, 0.018, f"{P} - 0.108", 0.1, LAM)
    c.box("Rodapé direito", f"{H} - 0.018", yf(0.108), 0, 0.018, f"{P} - 0.108", 0.1, LAM)
    c.box("Prateleira esquerda", f"0.018 - {H}", f"{yc} + 0.03", 0.45, f"{H} / 2 - 0.027", f"{dc} - 0.03", 0.018, LAM)
    c.box("Prateleira direita", f"{H} / 2 + 0.009", f"{yc} + 0.03", 0.45, f"{H} / 2 - 0.027", f"{dc} - 0.03", 0.018, LAM)

    yd = yf(0.048)  # back face of the doors
    w = f"({H} / 2 - 0.003)"  # door width
    zd, hd = 0.102, f"{A} - 0.14"
    doors = (
        (1, (f"0.0015 - {H}", yd), "left"),
        (2, (f"0.0015 - {H} / 2", yd), "left"),
        (3, (f"{H} / 2 - 0.0015", yd), "right"),
        (4, (f"{H} - 0.0015", yd), "right"),
    )
    for i, hinge, side in doors:
        c.door_box(f"Porta {i}", hinge, ang, 0, w, 0, 0.018, zd, hd, LAM, side)
        c.door_box(f"Puxador {i}", hinge, ang, f"{w} - 0.046", f"{w} - 0.034", 0.04, 0.05, z(-0.23), 0.16, INOX, side)
        c.door_box(f"Pé superior do puxador {i}", hinge, ang, f"{w} - 0.044", f"{w} - 0.036", 0.018, 0.041, z(-0.095), 0.008, INOX, side, FINE)
        c.door_box(f"Pé inferior do puxador {i}", hinge, ang, f"{w} - 0.044", f"{w} - 0.036", 0.018, 0.041, z(-0.213), 0.008, INOX, side, FINE)
        c.door_box(f"Dobradiça superior {i}", hinge, ang, 0.004, 0.05, -0.012, 0, z(-0.16), 0.045, "Aço galvanizado", side, FINE)
        c.door_box(f"Dobradiça inferior {i}", hinge, ang, 0.004, 0.05, -0.012, 0, 0.16, 0.045, "Aço galvanizado", side, FINE)
    return c
