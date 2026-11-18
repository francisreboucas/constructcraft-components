"""Luminária linear LED de sobrepor: perfil de alumínio extrudado, difusor leitoso em arco encaixado nos frisos,
tampas de ponta, placa de LED e driver dentro do perfil, presilhas de fixação no teto.

Luminária de teto: o forro em z = 0, o corpo abaixo, comprido ao longo de X e centrado na origem.
"""

from kit import *
import _luminarias as lu


def build():
    c = Component("Luminária linear LED", "lighting", "luminaria-linear", "Lighting")
    C = c.param("Comprimento", 1.2)
    W = c.param("Largura", 0.08)
    H = c.param("Altura", 0.05)
    c.mep = {"Device": {"device": "CeilingLight", "power": 40}}
    lu.materiais(c)
    c.type("Linear LED 60 cm", "Luminária de sobrepor, carga prevista 40 VA", Comprimento=0.6)
    c.type("Linear LED 120 cm", "Luminária de sobrepor, carga prevista 40 VA")
    lu.teto(c, 1.8, -0.025)  # a mesma distância serve aos dois tipos (o de 120 cm é a segunda prévia)

    t = 0.0015  # parede do perfil
    g = 0.0015  # folga das presilhas entre o perfil e o teto
    ec = 0.004  # espessura das tampas de ponta
    hw = f"({W}/2)"
    s = f"(0.4*{H})"  # flecha do difusor
    zb = f"(-{H} + {s})"  # base do perfil: daí para baixo, o difusor
    a = f"({hw} - {t})"
    Rd = f"(({a}*{a} + {s}*{s})/(2*{s}))"
    Rt = f"(({hw}*{hw} + {s}*{s})/(2*{s}))"
    x0, L = f"(-{C}/2 + {ec})", f"({C} - {2 * ec})"  # entre as tampas
    AL, W_ = "Alumínio anodizado", "Branco"

    # --- simplificado ---------------------------------------------------------------------
    c.box("Volume simplificado", f"-{C}/2", f"-{hw}", f"-{H}", C, W, H, AL, detail=COARSE, in_plan=True)

    # --- perfil de alumínio: U invertido com frisos de encaixe do difusor -------------------------
    lip = 0.0025
    perfil = [
        (f"-{hw}", zb), (f"-{hw}", f"-{g}"), (hw, f"-{g}"), (hw, zb), (f"{hw} - 0.001", f"{zb} - 0.001"),
        (f"{hw} - {t} - {lip}", f"{zb} - 0.001"), (f"{hw} - {t} - {lip}", f"{zb} + {t}"), (f"{hw} - {t}", f"{zb} + {t}"),
        (f"{hw} - {t}", f"-{g} - {t}"), (f"-{hw} + {t}", f"-{g} - {t}"), (f"-{hw} + {t}", f"{zb} + {t}"),
        (f"-{hw} + {t} + {lip}", f"{zb} + {t}"), (f"-{hw} + {t} + {lip}", f"{zb} - 0.001"), (f"-{hw} + 0.001", f"{zb} - 0.001"),
    ]
    c.profile("Perfil", "Side", perfil, x0, L, AL, in_plan=True)
    # canaletas laterais (frisos decorativos do perfil)
    for i, sy in enumerate((-1, 1), 1):
        c.box(f"Perfil - friso lateral {i}", x0, f"{sy}*{hw} - 0.0004", f"{zb} + 0.4*({H} - {s})", L, 0.0008, 0.0012, "Alumínio fundido", detail=FINE)

    # --- difusor em arco, entre as tampas ---------------------------------------------------------
    c.profile("Difusor", "Side", [(f"-{a}", f"{zb} + 0.0015"), (a, f"{zb} + 0.0015"), (a, zb, f"-{Rd}"), (f"-{a}", zb)], x0, L, lu.DIFUSOR, in_plan=True)

    # --- tampas de ponta ------------------------------------------------------------------------------
    tampa = [(f"-{hw}", f"-{g}"), (hw, f"-{g}"), (hw, zb, f"-{Rt}"), (f"-{hw}", zb)]
    for i, (x, sx) in enumerate(((f"-{C}/2", -1), (f"{C}/2 - {ec}", 1)), 1):
        c.profile(f"Tampa de ponta {i}", "Side", tampa, x, ec, W_, in_plan=True)
        xo = f"-{C}/2 - 0.0004" if sx < 0 else f"{C}/2"
        c.cyl_x(f"Tampa de ponta {i} - parafuso", 0, f"{zb} + 0.45*({H} - {s})", xo, 0.0022, 0.0004, "Inox escovado", detail=FINE)
        c.cyl_x(f"Tampa de ponta {i} - furo de passagem", 0, f"-{g} - 0.009", xo, 0.0045, 0.0004, "Plástico cinza claro", detail=FINE)

    # --- dentro do perfil: chapa, placa de LED com chips, driver --------------------------------------------
    zc = f"({zb} + 0.004)"  # face de baixo da chapa dissipadora
    c.box("Chapa dissipadora", x0, f"-{a}", zc, L, f"2*{a}", 0.0012, AL)
    c.box("Placa de LED", f"{x0} + 0.01", -0.012, f"{zc} - 0.0012", f"{L} - 0.02", 0.024, 0.0012, W_)
    n = 24
    for i in range(n):
        f = (i + 0.5) / n
        c.box(f"LED {i + 1}", f"{x0} + 0.01 + {f:.5f}*({L} - 0.02) - 0.0025", -0.0025, f"{zc} - 0.0024", 0.005, 0.005, 0.0012, lu.LED, detail=FINE)
    c.box("Driver", f"{C}/2 - {ec} - 0.2", -0.015, f"{zc} + 0.0012", 0.18, 0.03, f"-{g} - {t} - {zc} - 0.0012", "Plástico cinza claro")

    # --- presilhas de fixação no teto (o perfil se encaixa nelas) ----------------------------------------------
    for i, f in enumerate((-0.36, 0, 0.36), 1):
        x = f"{f}*{C} - 0.012"
        c.box(f"Presilha {i}", x, f"-{hw} - 0.0008", f"-{g}", 0.024, f"{W} + 0.0016", g, "Aço galvanizado")
        for j, sy in enumerate((-1, 1), 1):
            c.box(f"Presilha {i} - aba {j}", x, f"{sy}*({hw} + 0.0004) - 0.0004", f"-{g} - 0.014", 0.024, 0.0008, 0.014, "Aço galvanizado")

    # --- topo: passa-fios e etiqueta ------------------------------------------------------------------------------
    lu.anel(c, "Passa-fios", 0.005, 0.0085, f"-{g} - 0.0004", f"-{g} + 0.0006", "Borracha", cx=f"0.18*{C}", detail=FINE)
    c.box("Etiqueta de dados", f"-0.18*{C} - 0.03", -0.014, f"-{g}", 0.06, 0.028, 0.0004, W_, detail=FINE)
    return c
