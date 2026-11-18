"""Luminária pendente de cúpula: canopla no teto, cabo com prensa-cabos na altura da queda,
soquete E27, cúpula de alumínio repuxado (preta por fora, branca por dentro) e lâmpada LED A60.

Luminária de teto: o forro em z = 0 e o pendente abaixo, no eixo z. `Queda` é a distância
do forro à borda de baixo da cúpula (parâmetro de instância: cada pendente na sua altura).
"""

from kit import *
import _luminarias as lu


def build():
    c = Component("Luminária pendente", "lighting", "pendente", "Lighting")
    D = c.param("Diametro", 0.35)
    Q = c.param("Queda", 0.8, instance=True)
    c.mep = {"Device": {"device": "CeilingLight", "power": 60}}
    lu.materiais(c)
    c.type("Pendente Ø35 60 VA", "Luminária pendente sobre mesa ou bancada")
    c.type("Pendente Ø50 60 VA", "Luminária pendente sobre mesa ou bancada", Diametro=0.5)
    lu.teto(c, 1.55, -0.45)
    c.open_pose["Queda"] = 0.55  # a prévia "open" mostra o pendente mais alto

    R = f"({D}/2)"
    Hc = f"(0.55*{D})"  # altura da cúpula
    zr = f"(-{Q})"  # borda da cúpula
    zt = f"(-{Q} + {Hc})"  # topo da cúpula
    rn = 0.03  # raio do pescoço da cúpula
    Ra = f"(0.5*{D})"  # raio da curva da cúpula
    zs = f"({zt} - 0.045)"  # boca do soquete
    PRETO, BRANCO = "Aço pintado preto", "Aço pintado branco"

    def casca(name, o1, o2, mat, **kw):
        """Casca da cúpula entre os afastamentos o1 e o2 da face de fora."""
        c.rev(name, "Front", [
            (rn - o1, zt), (rn - o1, f"{zt} - 0.03", f"-({Ra} - {o1})"), (f"{R} - {o1}", zr),
            (f"{R} - {o2}", zr, f"{Ra} - {o2}"), (rn - o2, f"{zt} - 0.03"), (rn - o2, zt),
        ], 0, 0, mat, **kw)

    # --- canopla no teto ---------------------------------------------------------------------
    c.rev("Canopla", "Front", [(0, 0), (0.06, 0), (0.06, -0.022, -0.008), (0.052, -0.03), (0, -0.03)], 0, 0, PRETO, detail=ALL)
    for i, sx in enumerate((-1, 1), 1):
        c.cyl_x(f"Canopla - parafuso lateral {i}", 0, -0.012, 0.0598 if sx > 0 else -0.0618, 0.0022, 0.002, "Latão", detail=FINE)
    c.cyl("Prensa-cabo da canopla", 0, 0, -0.042, 0.007, 0.012, PRETO)
    lu.anel(c, "Prensa-cabo da canopla - porca", 0.007, 0.0085, -0.034, -0.03, PRETO, detail=FINE)

    # --- cabo ----------------------------------------------------------------------------------
    c.cyl("Cabo", 0, 0, f"{zt} + 0.032", 0.0032, f"-0.042 - {zt} - 0.032", "Plástico preto", detail=ALL)

    # --- simplificado ------------------------------------------------------------------------------
    c.rev("Cúpula simplificada", "Front", [(0, f"{zt} + 0.03"), (rn, f"{zt} + 0.03"), (rn, f"{zt} - 0.03", f"-{Ra}"), (R, zr), (0, zr)], 0, 0, PRETO,
          detail=COARSE, in_plan=True)

    # --- soquete E27 e prensa-cabo da cúpula -------------------------------------------------------------
    c.rev("Soquete - tampa", "Front", [(0, f"{zt} + 0.032"), (0.006, f"{zt} + 0.032"), (0.016, f"{zt} + 0.022"), (0.017, zt), (0, zt)], 0, 0, PRETO)
    lu.anel(c, "Soquete - prensa-cabo", 0.0032, 0.0055, f"{zt} + 0.032", f"{zt} + 0.038", PRETO, detail=FINE)
    c.cyl("Soquete", 0, 0, zs, 0.0205, f"{zt} - {zs}", "Plástico preto")
    lu.anel(c, "Soquete - anel de fixação", 0.0205, 0.026, f"{zt} - 0.008", f"{zt} - 0.003", "Plástico preto", detail=FINE)
    for k in range(3):
        lu.anel(c, f"Soquete - nervura {k + 1}", 0.0205, 0.0215, f"{zs} + {0.006 + 0.008 * k}", f"{zs} + {0.0075 + 0.008 * k}", "Plástico preto", detail=FINE)

    # --- cúpula: casca preta por fora, branca por dentro ------------------------------------------------------
    casca("Cúpula", 0, 0.0012, PRETO, in_plan=True)
    casca("Cúpula - pintura interna", 0.0012, 0.002, BRANCO)
    lu.anel(c, "Cúpula - tampo", 0.0215, rn, f"{zt} - 0.002", zt, PRETO)
    lu.anel(c, "Cúpula - friso da borda", f"{R} - 0.003", f"{R} + 0.0008", zr, f"{zr} + 0.0035", PRETO, detail=FINE)

    # --- lâmpada LED A60 -------------------------------------------------------------------------------------
    c.cyl("Lâmpada - rosca E27", 0, 0, f"{zs} - 0.004", 0.0132, 0.006, "Alumínio anodizado")
    c.rev("Lâmpada - corpo", "Front", [(0, f"{zs} - 0.004"), (0.016, f"{zs} - 0.004"), (0.0235, f"{zs} - 0.03"), (0, f"{zs} - 0.03")], 0, 0, "Branco")
    c.rev("Lâmpada - bulbo", "Front", [(0, f"{zs} - 0.03"), (0.0235, f"{zs} - 0.03", -0.045), (0.03, f"{zs} - 0.058", -0.03), (0, f"{zs} - 0.088")],
          0, 0, lu.DIFUSOR)
    lu.anel(c, "Lâmpada - anel do bulbo", 0.0225, 0.0238, f"{zs} - 0.031", f"{zs} - 0.028", "Plástico cinza claro", detail=FINE)
    return c
