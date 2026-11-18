"""Chuveiro elétrico: braço na parede, corpo com espalhador, seletor, ducha manual e ligação elétrica."""

from kit import *
from kit import _points


def sweep(c, name, plane, path, offset, section, material, detail=FULL, in_plan=False, void=False):
    """A closed `section` (u to the left of the path, v along the plane's normal) carried along `path`."""
    shape = {"Sweep": {"plane": plane, "path": _points(path), "offset": e(offset), "profile": _points(section)}}
    c._add(name, shape, material, detail, in_plan, void)


def tube(c, name, plane, path, offset, radius, material, detail=FULL, in_plan=False, void=False):
    sweep(c, name, plane, path, offset, disc(0, 0, radius), material, detail, in_plan, void)


def build():
    c = Component("Chuveiro elétrico", "plumbing", "chuveiro-eletrico", "Plumbing")
    A = c.param("Altura", 2.1)
    B = c.param("Braco", 0.3)
    c.type("Chuveiro elétrico", "Aquecimento no ponto: ligar também um ponto de TUE de 5500 W ou 7500 W")
    c.mep = {"Fixture": {"drain_units": 2, "supply_weight": 0.1, "hot_water": False}}
    c.connector("Água fria", "ColdWater", 0, 0, f"{A} + 0.065", "Back", 0.02)
    c.connector("Alimentação", "Power", 0, 0, f"{A} + 0.2", "Back")
    c.preview_base = 0.95
    c.preview_size = (0.45, 0.45, 1.4)

    yb = f"-{B}"  # y of the body's axis
    zc = f"{A} + 0.065"  # arm centerline

    def z(dz):
        return f"{A} + {dz}" if dz >= 0 else f"{A} - {-dz}"

    def y(dy):  # from the body's axis
        return f"{dy} - {B}"

    # --- coarse stand-ins (the old pieces) ---
    c.box("Braço simplificado", -0.015, yb, z(0.05), 0.03, B, 0.03, "Cromado", COARSE, in_plan=True)
    c.cyl("Corpo simplificado", 0, yb, A, 0.09, 0.12, "Branco", COARSE, in_plan=True)

    # --- wall arm ---
    c.rev("Canopla", "Plan", [(0, -0.014), (0.017, -0.014), (0.021, -0.01, 0.03), (0.034, -0.002), (0.034, 0), (0, 0)], zc, 0, "Cromado")
    c.cyl_y("Braço", 0, zc, y(0.112), 0.0115, f"{B} - 0.112", "Cromado", in_plan=True)
    c.cyl_y("Porca do braço", 0, zc, y(0.094), 0.017, 0.02, "Cromado", FINE)
    c.cyl_y("Rosca do braço", 0, zc, y(0.114), 0.0135, 0.008, "Latão", FINE)
    c.rev("Entrada de água", "Plan", [(0, y(0.03)), (0.024, y(0.03)), (0.024, y(0.078), 0.01), (0.019, y(0.094)), (0, y(0.094))], zc, 0, "Branco")

    # --- body ---
    c.rev("Corpo", "Front", [
        (0, z(0.009)), (0.0785, z(0.009)), (0.0785, z(0.0)), (0.0895, z(0.0)), (0.0925, z(0.034), 0.11),
        (0.064, z(0.097), 0.06), (0.03, z(0.116)), (0, z(0.119)),
    ], yb, 0, "Branco", in_plan=True)
    c.rev("Friso cromado", "Front", rect(0.088, z(0.034), 0.0937, z(0.040)), yb, 0, "Cromado", detail=FINE)
    c.rev("Aro do espalhador", "Front", rect(0.074, z(-0.0015), 0.0785, z(0.004)), yb, 0, "Cromado", detail=FINE)
    c.rev("Espalhador", "Front", [(0, z(0.0045)), (0.074, z(0.0045)), (0.074, z(0.0095)), (0, z(0.0095))], yb, 0, "Plástico cinza claro")
    for i, r in enumerate((0.017, 0.031, 0.045, 0.059), 1):
        c.rev(f"Anel de jatos {i}", "Front", rect(r - 0.0035, z(0.002), r + 0.0035, z(0.005)), yb, 0, "Borracha cinza", detail=FINE)
        c.rev(f"Furos do anel {i}", "Front", rect(r - 0.001, z(0.0012), r + 0.001, z(0.003)), yb, 0, "Borracha", detail=FINE)
    c.cyl("Jato central", 0, yb, z(0.0015), 0.005, 0.004, "Borracha cinza", FINE)

    # --- temperature selector on the top ---
    c.rev("Seletor de temperatura", "Front", [(0, z(0.116)), (0.027, z(0.114)), (0.027, z(0.126), 0.004), (0.023, z(0.130)), (0, z(0.130))], yb, 0, "Plástico cinza claro")
    c.box("Ponteiro do seletor", -0.004, y(-0.027), z(0.1295), 0.008, 0.03, 0.005, "Plástico cinza", FINE)
    for i, (dx, dy) in enumerate(((-0.026, -0.026), (0, -0.037), (0.026, -0.026)), 1):
        c.cyl(f"Marca de posição {i}", dx, y(dy), z(0.107), 0.0032, 0.0075, ("Plástico azul", "Plástico cinza", "Plástico vermelho")[i - 1], FINE)
    c.box("Etiqueta frontal", -0.022, y(-0.0935), z(0.011), 0.044, 0.004, 0.014, "Plástico cinza claro", FINE)

    # --- hand shower: outlet, hose, holder on the wall ---
    xh = 0.058
    c.cyl("Saída da ducha", xh, y(0.055), z(-0.022), 0.0085, 0.035, "Branco")
    c.cyl("Porca da mangueira", xh, y(0.055), z(-0.034), 0.0105, 0.014, "Cromado", FINE)
    rh = f"({B} - 0.085) / 2"
    tube(c, "Mangueira da ducha", "Side", [
        (y(0.055), z(-0.03)), (y(0.055), z(-1.0), rh), (-0.03, z(-1.0)), (-0.03, z(-0.815)),
    ], xh, 0.0065, "Branco")
    c.cyl("Porca da ducha", xh, -0.03, z(-0.822), 0.0105, 0.014, "Cromado", FINE)
    c.rev("Cabo da ducha", "Front", [(xh, z(-0.81)), (xh + 0.0095, z(-0.81)), (xh + 0.0125, z(-0.70)), (xh + 0.0125, z(-0.652), 0.0125), (xh, z(-0.6395))], -0.03, xh, "Branco")
    c.rev("Cabeça da ducha", "Plan", [(xh, -0.062), (xh + 0.027, -0.062), (xh + 0.027, -0.054, 0.03), (xh + 0.012, -0.03), (xh, -0.03)], z(-0.665), xh, "Branco")
    c.cyl_y("Espalhador da ducha", xh, z(-0.665), -0.0635, 0.022, 0.002, "Plástico cinza claro", FINE)
    c.rev("Suporte da ducha", "Front", rect(xh + 0.012, z(-0.775), xh + 0.018, z(-0.745)), -0.03, xh, "Branco")
    c.box("Braço do suporte", xh - 0.012, -0.016, z(-0.775), 0.024, 0.016, 0.03, "Branco")
    c.box("Base do suporte", xh - 0.02, -0.004, z(-0.79), 0.04, 0.004, 0.06, "Branco")
    c.cyl_y("Parafuso do suporte 1", xh, z(-0.737), -0.0055, 0.003, 0.002, "Inox escovado", FINE)
    c.cyl_y("Parafuso do suporte 2", xh, z(-0.783), -0.0055, 0.003, 0.002, "Inox escovado", FINE)

    # --- wiring: three wires to a connector and the wall plate ---
    c.box("Espelho da caixa elétrica", -0.036, -0.005, z(0.143), 0.072, 0.005, 0.114, "Branco")
    c.cyl_y("Saída dos fios", 0, z(0.2), -0.0075, 0.011, 0.003, "Plástico cinza", FINE)
    c.cyl_y("Parafuso do espelho 1", 0, z(0.243), -0.0062, 0.003, 0.0015, "Inox escovado", FINE)
    c.cyl_y("Parafuso do espelho 2", 0, z(0.157), -0.0062, 0.003, 0.0015, "Inox escovado", FINE)
    c.cyl("Passa-fios", 0, y(0.045), z(0.098), 0.012, 0.012, "Borracha", FINE)
    for name, dx, mat in (("fase", -0.0065, "Plástico preto"), ("neutro", 0, "Plástico azul"), ("terra", 0.0065, "Plástico verde")):
        tube(c, f"Fio {name}", "Side", [
            (y(0.045), z(0.105)), (y(0.045), z(0.16), -0.04), (y(0.085), z(0.2)), (-0.005, z(0.2)),
        ], dx, 0.0026, mat, FINE)
    c.box("Conector de porcelana", -0.014, -0.075, z(0.193), 0.028, 0.03, 0.014, "Louça", FINE)
    for i, dx in enumerate((-0.0065, 0, 0.0065), 1):
        c.cyl(f"Parafuso do conector {i}", dx, -0.06, z(0.2065), 0.0022, 0.0015, "Latão", FINE)
    return c
