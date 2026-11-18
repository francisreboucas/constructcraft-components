"""Spot LED de embutir em forro: aro de acabamento sob o forro, refletor, módulo LED com lente,
corpo dissipador aletado acima do forro, molas de fixação apoiadas sobre a placa e o driver remoto.

Luminária de teto: a face de baixo do forro em z = 0. O aro fica abaixo (z < 0);
o corpo atravessa a placa de gesso (12,5 mm) e sobe acima dela, onde as molas se apoiam.
"""

import math

from kit import *
import _luminarias as lu

FORRO = 0.0125  # espessura da placa de gesso: as molas se apoiam em cima dela


def build():
    c = Component("Spot LED de embutir", "lighting", "spot-embutido", "Lighting")
    D = c.param("Diametro", 0.1)
    c.mep = {"Device": {"device": "CeilingLight", "power": 18}}
    lu.materiais(c)
    c.type("Spot LED Ø10", "Spot de embutir em forro de gesso, até 18 VA")
    c.type("Downlight LED Ø17", "Downlight de embutir em forro de gesso, até 18 VA", Diametro=0.17)
    lu.teto(c, 0.5, 0.02)

    R = f"({D}/2)"
    Rc = f"(0.38*{D})"  # corpo: o furo no forro tem 2*Rc (76 mm no Ø10, 129 mm no Ø17)
    Ri = f"(0.33*{D})"  # boca do refletor
    zl = f"(0.3*{D})"  # módulo LED, no fundo do refletor
    rl = f"(0.12*{D})"
    Hh = f"(0.5*{D} + 0.005)"  # topo do dissipador
    W, AL = "Aço pintado branco", "Alumínio fundido"

    # --- simplificado ------------------------------------------------------------------
    c.cyl("Aro simplificado", 0, 0, -0.004, R, 0.004, W, detail=COARSE, in_plan=True)
    c.cyl("Corpo simplificado", 0, 0, 0, Rc, Hh, AL, detail=COARSE)

    # --- aro de acabamento, abaixo do forro -----------------------------------------------
    c.rev("Aro", "Front", [(Ri, 0), (R, 0), (R, -0.0015, -0.003), (f"{R} - 0.004", -0.004), (Ri, -0.004)], 0, 0, W, in_plan=True)
    lu.anel(c, "Aro - borda interna", f"{Ri} - 0.0012", Ri, -0.0042, 0, W, detail=FINE)

    # --- colar que atravessa o forro e refletor ---------------------------------------------
    lu.anel(c, "Colar", f"{Rc} - 0.002", Rc, 0, zl, AL)
    c.rev("Refletor", "Front", [(f"{Ri} - 0.0012", -0.003), (Ri, -0.003), (f"{rl} + 0.0012", zl), (rl, zl)], 0, 0, "Cromado")
    lu.anel(c, "Refletor - anel de fixação", f"{Ri}", f"{Rc} - 0.002", -0.001, 0.004, "Alumínio anodizado", detail=FINE)

    # --- módulo LED e lente ----------------------------------------------------------------
    c.cyl("Módulo LED (COB)", 0, 0, f"{zl} - 0.0015", rl, 0.0015, lu.LED)
    c.cyl("Lente", 0, 0, f"{zl} - 0.0045", f"0.8*{rl}", 0.003, lu.DIFUSOR)
    lu.anel(c, "Lente - anel", f"0.8*{rl}", rl, f"{zl} - 0.0045", f"{zl} - 0.0015", "Plástico preto", detail=FINE)

    # --- corpo dissipador acima do módulo -------------------------------------------------------
    c.cyl("Base do dissipador", 0, 0, zl, Rc, 0.004, AL)
    c.cyl("Núcleo do dissipador", 0, 0, f"{zl} + 0.004", f"0.2*{D}", f"{Hh} - {zl} - 0.004", AL)
    nf = 12
    for i in range(nf):
        a = 2 * math.pi * (i + 0.5) / nf
        cs, sn, h = math.cos(a), math.sin(a), 0.0012
        pts = []
        for r, s in ((f"0.19*{D}", 1), (f"{Rc} - 0.0005", 1), (f"{Rc} - 0.0005", -1), (f"0.19*{D}", -1)):
            pts.append((f"{cs:.4f}*{p(r)} - {s * h * sn:.5f}", f"{sn:.4f}*{p(r)} + {s * h * cs:.5f}"))
        c.extrusion(f"Aleta do dissipador {i + 1}", pts, f"{zl} + 0.004", f"{Hh} - {zl} - 0.006", AL, detail=FINE)
    c.cyl("Tampa do dissipador", 0, 0, f"{Hh} - 0.002", f"0.2*{D} + 0.002", 0.002, AL, detail=FINE)
    c.cyl("Prensa-cabo do corpo", 0, f"0.2*{D}", f"{Hh} - 0.012", 0.004, 0.008, "Borracha", detail=FINE)

    # --- molas de fixação, abertas sobre a placa de gesso ------------------------------------------
    for i, sx in enumerate((-1, 1), 1):
        def x(d):
            return f"{sx}*({Rc} + {d})"
        name = f"Mola {i}"
        c.box(f"{name} - suporte", x(0) if sx > 0 else x(0.004), -0.007, FORRO + 0.004, 0.004, 0.014, 0.02, "Aço galvanizado")
        c.cyl_y(f"{name} - espiral", x(0.008), FORRO + 0.012, -0.006, 0.0045, 0.012, "Aço galvanizado")
        F = FORRO
        arm = [(0.007, F + 0.0085), (0.04, F + 0.001), (0.05, F + 0.001), (0.0535, F + 0.0045), (0.0547, F + 0.0037),
               (0.0505, F), (0.04, F), (0.007, F + 0.0075)]
        if sx < 0:
            arm = arm[::-1]
        c.profile(f"{name} - braço", "Front", [(x(u), v) for u, v in arm], -0.004, 0.008, "Aço galvanizado")
        c.cyl_y(f"{name} - pino", x(0.008), FORRO + 0.012, -0.008, 0.0012, 0.016, "Aço galvanizado", detail=FINE)

    # --- driver remoto, apoiado sobre o forro, e cabos ----------------------------------------------
    yd = f"({Rc} + 0.06)"
    c.box("Driver", -0.0175, yd, FORRO, 0.035, 0.075, 0.022, "Branco")
    for j, y in enumerate((f"{yd} - 0.006", f"{yd} + 0.075"), 1):
        c.box(f"Driver - tampa do borne {j}", -0.016, y, FORRO + 0.001, 0.032, 0.006, 0.02, "Plástico cinza claro", detail=FINE)
    c.box("Driver - etiqueta", -0.012, f"{yd} + 0.012", FORRO + 0.022, 0.024, 0.05, 0.0004, "Plástico cinza claro", detail=FINE)
    c.cyl_y("Cabo do LED", 0, FORRO + 0.011, f"{Rc} - 0.001", 0.0025, f"{yd} - {Rc} - 0.005", "Borracha")
    c.cyl_y("Cabo de alimentação", 0, FORRO + 0.011, f"{yd} + 0.081", 0.003, 0.04, "Borracha")
    c.box("Conector de engate rápido", -0.008, f"{yd} + 0.121", FORRO + 0.004, 0.016, 0.02, 0.014, "Plástico cinza claro", detail=FINE)
    return c
