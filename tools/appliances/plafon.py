"""Plafon de sobrepor redondo: base de aço presa no teto, aro, difusor de acrílico leitoso e a placa de LED que aparece através dele.

Luminária de teto: o forro em z = 0 e o plafon abaixo, centrado na origem.
"""

import math

from kit import *
import _luminarias as lu


def build():
    c = Component("Plafon de teto", "lighting", "plafon", "Lighting")
    D = c.param("Diametro", 0.3)
    A = c.param("Altura", 0.06)
    c.mep = {"Device": {"device": "CeilingLight", "power": 100}}
    lu.materiais(c)
    c.type("Plafon Ø30 100 VA", "Ponto de luz no teto")
    c.type("Plafon Ø40 100 VA", "Ponto de luz no teto", Diametro=0.4)
    lu.teto(c, 0.55, -0.03)

    R = f"({D}/2)"
    Rb = f"({R} - 0.004)"  # base de aço
    hb = f"(0.35*{A})"  # altura da base
    z1 = f"(-{hb} - 0.002)"  # borda do difusor, dentro do aro
    Rd = f"({R} - 0.003)"
    ed = f"(0.65*{A} - 0.002)"  # raio da curva da borda do difusor
    t = 0.0025

    # --- simplificado ------------------------------------------------------------
    c.cyl("Volume simplificado", 0, 0, f"-{A}", R, A, "Branco", detail=COARSE, in_plan=True)

    # --- base de aço, presa no teto -------------------------------------------------
    c.rev("Base", "Front", [(0, 0), (Rb, 0), (Rb, f"-{hb} + 0.004", -0.004), (f"{Rb} - 0.004", f"-{hb}"), (0, f"-{hb}")], 0, 0,
          "Aço pintado branco", in_plan=True)
    lu.anel(c, "Base - nervura de reforço", f"0.55*{R}", f"0.55*{R} + 0.004", -0.0011, 0.0004, "Aço pintado branco", detail=FINE)
    lu.anel(c, "Passa-fios", 0.007, 0.011, -0.001, 0.0005, "Borracha", detail=FINE)
    for i, sx in enumerate((-1, 1), 1):
        c.box(f"Furo oblongo de fixação {i}", f"{sx}*0.38*{R} - 0.009", -0.0025, -0.0004, 0.018, 0.005, 0.0008, "Aço pintado preto", detail=FINE)

    # --- aro decorativo na junção da base com o difusor ---------------------------------
    c.rev("Aro", "Front", [(f"{Rd} - 0.002", f"-{hb} + 0.001"), (f"{R} - 0.001", f"-{hb} + 0.001"), (R, f"-{hb} - 0.0015", -0.003),
                           (f"{R} - 0.001", f"-{hb} - 0.005"), (f"{Rd} - 0.002", f"-{hb} - 0.005")], 0, 0, "Cromado", in_plan=True)

    # --- difusor: casca de acrílico leitoso, borda arredondada e fundo plano --------------
    c.rev("Difusor", "Front", [
        (Rd, z1, f"-{ed}"), (f"{Rd} - {ed}", f"-{A}"), (0, f"-{A}"), (0, f"-{A} + {t}"),
        (f"{Rd} - {ed}", f"-{A} + {t}", f"({ed} - {t})"), (f"{Rd} - {t}", z1),
    ], 0, 0, lu.DIFUSOR, in_plan=True)
    lu.anel(c, "Difusor - friso central", f"0.30*{R}", f"0.30*{R} + 0.0015", f"-{A} - 0.0004", f"-{A}", lu.DIFUSOR, detail=FINE)
    for i in range(3):
        a = math.radians(90 + 120 * i)
        c.box(f"Trava do difusor {i + 1}", f"{math.cos(a):.4f}*({Rd} - 0.002) - 0.004", f"{math.sin(a):.4f}*({Rd} - 0.002) - 0.004",
              f"{z1} - 0.004", 0.008, 0.008, 0.004, "Plástico cinza claro", detail=FINE)

    # --- placa de LED e driver, vistos através do difusor -----------------------------------
    zp = f"(-{hb} - 0.0016)"  # face de baixo da placa
    c.cyl("Placa de LED", 0, 0, zp, f"0.86*{R}", 0.0016, "Branco")
    for ring, (n, f) in enumerate(((24, 0.76), (16, 0.56), (8, 0.36)), 1):
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * (ring % 2)) / n
            c.box(f"LED {ring}.{i + 1}", f"{math.cos(a) * f:.4f}*{R} - 0.0028", f"{math.sin(a) * f:.4f}*{R} - 0.0028", f"{zp} - 0.0012",
                  0.0056, 0.0056, 0.0012, lu.LED, detail=FINE)
    c.box("Driver", -0.032, -0.019, f"{zp} - 0.019", 0.064, 0.038, 0.019, "Plástico cinza claro")
    c.box("Driver - etiqueta", -0.026, -0.0195, f"{zp} - 0.016", 0.03, 0.0005, 0.012, "Branco", detail=FINE)
    c.box("Conector de ligação", 0.036, -0.008, f"{zp} - 0.011", 0.014, 0.016, 0.011, "Plástico cinza", detail=FINE)
    for i in range(3):
        c.cyl(f"Conector de ligação - parafuso {i + 1}", f"0.043", f"-0.0055 + {i}*0.0055", f"{zp} - 0.0115", 0.0018, 0.0005, "Aço galvanizado", detail=FINE)
    return c
