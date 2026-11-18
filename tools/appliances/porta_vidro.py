"""Porta de vidro temperado 10 mm sem batente: ferragens de canto (dobradiças 1101 e 1103), fechadura 1520 de piso, puxador tubular.

A folha gira num eixo vertical a 5,6 cm do vão esquerdo: pivô de piso sob a
dobradiça inferior e bucha superior fixada na verga. Ao fechar, o vidro
encosta num batente de alumínio com borracha no vão direito, do lado -y; a
fechadura do canto inferior direito trava num contra-fecho no piso.
"""

from doorkit import *

GT = 0.010  # vidro temperado
AX = 0.056  # do vão ao eixo
EDGE = 0.052  # do eixo à borda do vidro
PT = 0.013  # meia espessura das ferragens de canto


def corner(fr, pre, a_lo, a_hi, z0, h, mat="Inox escovado"):
    """A corner fitting clamping the glass: rounded body, cover plates, screws and rubber gaskets."""
    fr.poly(f"{pre} - corpo", rrect(a_lo, -PT, a_hi, PT, 0.006), z0, h, mat)
    for face, sg in (("frente", 1), ("fundo", -1)):
        lo, hi = sorted((sg * PT, sg * (PT + 0.0012)))
        fr.box(f"{pre} - tampa ({face})", s(a_lo, 0.006), s(a_hi, -0.006), lo, hi, s(z0, 0.006), h - 0.012, "Cromado", detail=FINE)
        lo, hi = sorted((sg * (PT + 0.0012), sg * (PT + 0.0018)))
        for k, f in enumerate((0.3, 0.7)):
            fr.box(f"{pre} - parafuso {k + 1} ({face})", s(a_lo, f"{f}*({p(a_hi)} - {p(a_lo)})", -0.004), s(a_lo, f"{f}*({p(a_hi)} - {p(a_lo)})", 0.004),
                   lo, hi, s(z0, h / 2 - 0.004), 0.008, "Inox escovado", detail=FINE)


def build() -> Component:
    c = Component("Porta de vidro temperado", "doors", "porta-vidro", "Door")
    L = c.param("Largura", 0.8)
    H = c.param("Altura", 2.1)
    A = opening_param(c, "AnguloAbertura", 75)
    c.opening = {"width": "Largura", "height": "Altura"}
    c.preview_size = (0.9, 0.6, 2.1)
    glass, steel, alu = "Vidro temperado", "Inox escovado", "Alumínio anodizado"

    xl, xr = f"(-{L}/2)", f"({L}/2)"
    yg = f"({WT}/2 - 0.025)"  # plano do vidro
    xp = f"({xl} + {AX})"
    fr = Fr(c, xp, yg, A)
    still = fr.still()
    a0, a1 = -EDGE, f"({L} - {AX + 0.004})"
    z0, z1 = 0.015, s(H, -0.012)
    hg = s(z1, -z0)

    # --- vidro ---------------------------------------------------------------
    fr.box("Folha simplificada", a0, a1, -GT / 2, GT / 2, z0, hg, glass, detail=COARSE, in_plan=True)
    fr.box("Folha", a0, a1, -GT / 2, GT / 2, z0, hg, glass, in_plan=True)
    fr.box("Faixa jateada", s(a0, 0.06), s(a1, -0.06), GT / 2, GT / 2 + 0.0004, 1.0, 0.1, "Plástico translúcido", detail=FINE)

    # --- ferragens de canto (lado do eixo) -------------------------------------
    hb = 0.06
    corner(fr, "Dobradiça inferior", a0 - 0.003, 0.11, z0 - 0.006, hb)
    corner(fr, "Dobradiça superior", a0 - 0.003, 0.11, s(z1, -hb + 0.006), hb)
    fr.box("Ferragens simplificadas inferior", a0 - 0.003, 0.11, -PT, PT, z0 - 0.006, hb, steel, detail=COARSE)
    fr.box("Ferragens simplificadas superior", a0 - 0.003, 0.11, -PT, PT, s(z1, -hb + 0.006), hb, steel, detail=COARSE)
    # Pivô de piso: base embutida rente ao piso, eixo sob a dobradiça inferior.
    still.poly("Pivô de piso - tampa", rrect(-0.03, -0.022, 0.07, 0.022, 0.006), 0, 0.003, steel)
    still.cyl("Pivô de piso - mancal", 0, 0, 0.003, 0.009, 0.003, "Cromado", detail=FINE)
    fr.cyl("Pivô de piso - eixo", 0, 0, 0.004, 0.006, z0 - 0.006 - 0.004 + 0.01, "Cromado")
    for k, a in enumerate((-0.02, 0.06)):
        still.cyl(f"Pivô de piso - parafuso {k + 1}", a, 0, 0.003, 0.003, 0.0008, "Cromado", detail=FINE)
    # Bucha superior na verga, com o pino da dobradiça superior.
    still.poly("Bucha superior - chapa", rrect(-0.03, -0.018, 0.05, 0.018, 0.005), s(H, -0.004), 0.004, steel)
    still.box("Bucha superior - calço", -0.03, 0.05, -0.018, 0.018, s(H, -0.0045), 0.0005, "Borracha", detail=FINE)
    fr.cyl("Bucha superior - pino", 0, 0, s(z1, 0.006 - 0.001), 0.006, s(H, f"-{z1}", -0.0105), "Cromado")
    for k, a in enumerate((-0.02, 0.04)):
        still.cyl(f"Bucha superior - parafuso {k + 1}", a, 0, s(H, -0.0048), 0.003, 0.0008, "Cromado", detail=FINE)

    # --- fechadura 1520 no canto inferior direito, contra-fecho no piso -----------
    corner(fr, "Fechadura", s(a1, -0.16), s(a1, 0.003), z0 - 0.006, hb)
    fr.box("Fechadura simplificada", s(a1, -0.16), s(a1, 0.003), -PT, PT, z0 - 0.006, hb, steel, detail=COARSE)
    ak = s(a1, -0.05)
    for face, sg in (("frente", 1), ("fundo", -1)):
        n0 = sg * (PT + 0.0012)
        fr.box(f"Fechadura - cilindro ({face})", s(ak, -0.009), s(ak, 0.009), *sorted((n0, n0 + sg * 0.004)), z0 + 0.012, 0.03, "Latão", detail=FINE)
        fr.box(f"Fechadura - fenda ({face})", s(ak, -0.001), s(ak, 0.001), *sorted((n0 + sg * 0.004, n0 + sg * 0.0045)), z0 + 0.016, 0.022, "Plástico preto", detail=FINE)
    fr.cyl("Fechadura - lingueta", s(a1, -0.11), 0, 0.006, 0.006, z0 - 0.012, "Cromado", detail=FINE)
    still.poly("Contra-fecho de piso", rrect(s(a1, -0.13), -0.016, s(a1, -0.09), 0.016, 0.006), 0, 0.003, steel, detail=FINE)
    still.cyl("Contra-fecho de piso - furo", s(a1, -0.11), 0, 0.0025, 0.0075, 0.0007, "Plástico preto", detail=FINE)

    # --- batente lateral de alumínio com borracha, no vão direito (lado -y) --------
    bz = s(H, -0.03)
    by0 = f"({yg} - {GT / 2 + 0.002 + 0.015})"
    c.box("Batente lateral - aba", s(xr, -0.022), by0, 0.03, 0.022, 0.003, bz, alu)
    c.box("Batente lateral - base", s(xr, -0.003), by0, 0.03, 0.003, 0.03, bz, alu)
    c.box("Batente lateral - borracha", s(xr, -0.02), s(by0, 0.003), 0.04, 0.012, 0.014, s(bz, -0.02), "Borracha", detail=FINE)

    # --- puxador tubular nas duas faces -------------------------------------------
    ah = s(a1, -0.1)
    pz0, pz1 = 0.75, 1.35
    so = 0.055
    fr.box("Puxador simplificado", s(ah, -0.0125), s(ah, 0.0125), -GT / 2 - so - 0.0125, GT / 2 + so + 0.0125, pz0, pz1 - pz0, steel, detail=COARSE)
    for face, sg in (("frente", 1), ("fundo", -1)):
        nb = sg * (GT / 2 + so)
        fr.cyl(f"Puxador ({face}) - tubo", ah, nb, pz0, 0.0125, pz1 - pz0, steel)
        fr.cyl(f"Puxador ({face}) - ponteira inferior", ah, nb, pz0 - 0.004, 0.013, 0.004, "Cromado", detail=FINE)
        fr.cyl(f"Puxador ({face}) - ponteira superior", ah, nb, pz1, 0.013, 0.004, "Cromado", detail=FINE)
        for k, zc in enumerate((pz0 + 0.06, pz1 - 0.06)):
            lo, hi = sorted((sg * GT / 2, nb))
            fr.box(f"Puxador ({face}) - haste {k + 1}", s(ah, -0.008), s(ah, 0.008), lo, hi, zc - 0.008, 0.016, steel)
            lo, hi = sorted((sg * GT / 2, sg * (GT / 2 + 0.003)))
            fr.box(f"Puxador ({face}) - arruela {k + 1}", s(ah, -0.013), s(ah, 0.013), lo, hi, zc - 0.013, 0.026, "Borracha", detail=FINE)

    for width in (0.8, 0.9, 1.0):
        c.type(f"Porta de vidro temperado {round(width * 100)} x 210", "Porta de giro em vidro temperado 10 mm, sem batente, ferragens de canto 1101/1103, fechadura 1520 e puxador tubular",
               Largura=width, Altura=2.1)
    return c
