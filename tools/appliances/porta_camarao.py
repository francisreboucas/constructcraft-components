"""Porta camarão (bi-fold): batente de madeira, duas folhas articuladas que se dobram para a esquerda.

A folha 1 gira num pivô junto ao batente esquerdo (pivô de piso e pivô
superior no trilho); a folha 2 se articula na folha 1 por três dobradiças e
corre com um rolete-guia no trilho de alumínio sob a travessa. Cada folha tem a
parte de baixo almofadada e a de cima venezianada.

AnguloAbertura dobra as folhas: a folha 1 gira de AnguloAbertura em torno do
pivô (abrindo para +y), a folha 2 fica a -AnguloAbertura e seu rolete segue
no eixo do trilho.
"""

from doorkit import *

JT = 0.035  # batente (wood_frame)
T = 0.03  # espessura das folhas
PIV = 0.03  # do batente ao eixo do pivô
LEAD = 0.024  # da borda da folha ao pivô / ao rolete


def folha(fr, pre, a0, a1, nlo, nhi, z0, z1, wood):
    """Montantes, travessas, almofada inferior e venezianas superiores, entre a0..a1, nlo..nhi, z0..z1."""
    nc = (nlo + nhi) / 2
    sw, top, bot, mid = 0.05, 0.07, 0.16, 0.1
    hg = s(z1, f"-{p(z0)}")
    fr.box(f"{pre} simplificada", a0, a1, nlo, nhi, z0, hg, wood, detail=COARSE)
    fr.box(f"{pre} - montante esquerdo", a0, s(a0, sw), nlo, nhi, z0, hg, wood, in_plan=True)
    fr.box(f"{pre} - montante direito", s(a1, -sw), a1, nlo, nhi, z0, hg, wood, in_plan=True)
    ra0, ra1 = s(a0, sw), s(a1, -sw)
    zm = s(z0, f"0.4*{hg}")
    fr.box(f"{pre} - travessa inferior", ra0, ra1, nlo, nhi, z0, bot, wood)
    fr.box(f"{pre} - travessa intermediária", ra0, ra1, nlo, nhi, zm, mid, wood, in_plan=True)
    fr.box(f"{pre} - travessa superior", ra0, ra1, nlo, nhi, s(z1, -top), top, wood)
    # Almofada inferior: tábua no meio da espessura, relevo nas duas faces e baguetes.
    pz0 = s(z0, bot)
    ph = s(zm, f"-{pz0}")
    fr.box(f"{pre} - almofada", s(ra0, -0.008), s(ra1, 0.008), nc - 0.006, nc + 0.006, s(pz0, -0.008), s(ph, 0.016), wood)
    for face, sg in (("frente", 1), ("fundo", -1)):
        lo, hi = sorted((nc + sg * 0.006, nc + sg * 0.0105))
        fr.box(f"{pre} - relevo da almofada ({face})", s(ra0, 0.03), s(ra1, -0.03), lo, hi, s(pz0, 0.03), s(ph, -0.06), wood)
        lo, hi = sorted((nc + sg * 0.006, nc + sg * 0.0125))
        fr.box(f"{pre} - baguete esquerdo ({face})", ra0, s(ra0, 0.01), lo, hi, pz0, ph, wood, detail=FINE)
        fr.box(f"{pre} - baguete direito ({face})", s(ra1, -0.01), ra1, lo, hi, pz0, ph, wood, detail=FINE)
        fr.box(f"{pre} - baguete inferior ({face})", s(ra0, 0.01), s(ra1, -0.01), lo, hi, pz0, 0.01, wood, detail=FINE)
        fr.box(f"{pre} - baguete superior ({face})", s(ra0, 0.01), s(ra1, -0.01), lo, hi, s(zm, -0.01), 0.01, wood, detail=FINE)
    # Venezianas: cada palheta em dois degraus (frente embaixo, fundo em cima), inclinada como a real.
    n_slats = 20
    vz0 = s(zm, mid)
    pitch = f"(({p(z1)} - {top} - {vz0})/{n_slats})"
    for k in range(n_slats):
        zk = s(vz0, f"{k}*{pitch}", 0.004)
        fr.box(f"{pre} - palheta {k + 1} (frente)", s(ra0, -0.006), s(ra1, 0.006), nc, nhi - 0.004, zk, f"0.55*{pitch}", wood)
        fr.box(f"{pre} - palheta {k + 1} (fundo)", s(ra0, -0.006), s(ra1, 0.006), nlo + 0.004, nc, s(zk, f"0.4*{pitch}"), f"0.55*{pitch}", wood)


def build() -> Component:
    c = Component("Porta camarão", "doors", "porta-camarao", "Door")
    L = c.param("Largura", 0.7)
    H = c.param("Altura", 2.1)
    A = opening_param(c, "AnguloAbertura", 80)
    c.opening = {"width": "Largura", "height": "Altura", "own_symbol": True}
    c.preview_size = (0.8, 0.5, 2.1)
    wood, alu = "Madeira", "Alumínio anodizado"

    wood_frame(c, L, H, wood, stop=False, in_plan=True)

    # Trilho: perfil U de alumínio sob a travessa do batente, no eixo das folhas.
    y0 = f"({WT}/2 - 0.025)"
    xl, xr = f"(-{L}/2 + {JT})", f"({L}/2 - {JT})"
    zh = f"({H} - {JT})"  # face de baixo da travessa
    tw, th = 0.026, 0.028
    c.box("Trilho - alma", xl, s(y0, -tw / 2), s(zh, -0.003), f"{L} - {2 * JT}", tw, 0.003, alu)
    c.box("Trilho - aba da frente", xl, s(y0, tw / 2 - 0.0022), s(zh, -th), f"{L} - {2 * JT}", 0.0022, th - 0.003, alu)
    c.box("Trilho - aba do fundo", xl, s(y0, -tw / 2), s(zh, -th), f"{L} - {2 * JT}", 0.0022, th - 0.003, alu)
    for i, f in enumerate((0.12, 0.5, 0.88)):
        c.cyl(f"Trilho - parafuso {i + 1}", f"{xl} + {f}*({L} - {2 * JT})", y0, s(zh, -0.0045), 0.0035, 0.0015, "Cromado", detail=FINE)
    c.box("Trilho - batente de fim de curso", s(xr, -0.012), s(y0, -0.009), s(zh, -0.02), 0.012, 0.018, 0.017, "Borracha", detail=FINE)

    # Batedor e amortecedor no batente direito, atrás da folha 2.
    c.box("Batedor direito", s(xr, -0.012), f"(-{WT}/2)", 0, 0.012, f"{WT}/2 + {y0} - {T / 2 + 0.002}", s(zh, -0.03), wood)
    for k, z in enumerate((0.3, 1.0, 1.7)):
        c.box(f"Amortecedor do batedor {k + 1}", s(xr, -0.0115), s(y0, -T / 2 - 0.0035), z, 0.005, 0.0015, 0.025, "Borracha cinza", detail=FINE)

    # Folhas: largura w de pivô a dobradiça e de dobradiça a rolete.
    w = f"(({L} - {2 * JT + 2 * PIV})/2)"
    x0 = f"(-{L}/2 + {JT + PIV})"
    zb = 0.012
    zt = s(zh, -th - 0.008)
    f1 = Fr(c, x0, y0, A)  # folha 1: pivô na origem, corpo n = -T/2..T/2
    f2 = f1.sub(w, -T / 2, f"-{A}")  # folha 2: articulada na face de trás da folha 1, corpo n = 0..T
    folha(f1, "Folha 1", -LEAD, s(w, -0.0015), -T / 2, T / 2, zb, zt, wood)
    folha(f2, "Folha 2", 0.0015, s(w, LEAD), 0, T, zb, zt, wood)

    # Dobradiças entre as folhas, no eixo comum (origem de f2).
    for i, z in enumerate((0.25, f"({zb} + {zt})/2 - 0.04", s(zt, -0.33))):
        nm = f"Dobradiça {i + 1}"
        for k in range(3):
            f2.cyl(f"{nm} - nó {k + 1}", 0, 0, s(z, k * 0.0267 + 0.0003), 0.005, 0.026, "Inox escovado", detail=FINE)
        f2.cyl(f"{nm} - pino", 0, 0, s(z, -0.003), 0.0028, 0.086, "Cromado", detail=FINE)
        f1.box(f"{nm} - aba da folha 1", s(w, -0.0027), s(w, -0.0015), -T / 2, -T / 2 + 0.024, z, 0.08, "Inox escovado", detail=FINE)
        f2.box(f"{nm} - aba da folha 2", 0.0015, 0.0027, 0, 0.024, z, 0.08, "Inox escovado", detail=FINE)

    # Pivô inferior: cantoneira no piso e no batente, pino e bucha sob a folha 1.
    still = f1.still()
    still.box("Pivô inferior - base", -PIV, 0.022, -0.02, 0.02, 0, 0.004, "Aço pintado branco", detail=FINE)
    still.box("Pivô inferior - aba no batente", -PIV, -PIV + 0.003, -0.02, 0.02, 0.004, 0.05, "Aço pintado branco", detail=FINE)
    for k, nn in enumerate((-0.012, 0.012)):
        still.cyl(f"Pivô inferior - parafuso {k + 1}", 0.012, nn, 0.004, 0.003, 0.0015, "Cromado", detail=FINE)
    still.cyl("Pivô inferior - regulagem", 0, 0, 0.004, 0.007, 0.005, "Latão", detail=FINE)
    f1.cyl("Pivô inferior - pino", 0, 0, 0.009, 0.004, 0.025, "Cromado")
    f1.box("Pivô inferior - chapa da folha", -0.02, 0.02, -0.011, 0.011, zb, 0.002, "Aço pintado branco", detail=FINE)
    # Pivô superior: pino com bucha de náilon no trilho, travado por um suporte.
    f1.box("Pivô superior - chapa da folha", -0.02, 0.02, -0.011, 0.011, s(zt, -0.002), 0.002, "Aço pintado branco", detail=FINE)
    f1.cyl("Pivô superior - pino", 0, 0, zt, 0.004, s(zh, f"-{zt}", -0.004), "Cromado")
    f1.cyl("Pivô superior - bucha", 0, 0, s(zh, -0.02), 0.009, 0.014, "Plástico preto", detail=FINE)
    still.box("Pivô superior - trava no trilho", -0.026, -0.012, -tw / 2 + 0.003, tw / 2 - 0.003, s(zh, -0.022), 0.019, "Aço pintado branco", detail=FINE)
    # Rolete-guia na ponta livre da folha 2.
    f2.box("Rolete - chapa da folha", s(w, -0.02), s(w, 0.02), 0.004, T - 0.004, s(zt, -0.002), 0.002, "Aço pintado branco", detail=FINE)
    f2.cyl("Rolete - eixo", w, T / 2, zt, 0.004, s(zh, f"-{zt}", -0.006), "Cromado")
    f2.cyl("Rolete - roda", w, T / 2, s(zh, -0.022), 0.0105, 0.012, "Plástico preto", detail=FINE)
    # Puxador de barra na folha 2, junto à dobradiça, na face que se dobra para fora.
    zp = 1.0
    for k, dz in enumerate((0, 0.128)):
        f2.box(f"Puxador - base {k + 1}", 0.036, 0.048, T, T + 0.03, s(zp, dz - 0.006), 0.012, "Cromado")
    f2.cyl("Puxador - barra", 0.042, T + 0.03, zp - 0.03, 0.0065, 0.188, "Cromado")

    # Símbolo em planta: as folhas a meio caminho (60°), como um V a partir do pivô.
    yf = f"({WT}/2)"
    xs = x0
    c.profile("Dobra", "Plan", [(xs, yf), (f"{xs} + {w}*0.5", f"{yf} + {w}*0.866"), (f"{xs} + {w}", yf)], 0, 0.001, wood)
    c.plan_only("Dobra")

    for width in (0.7, 0.8, 0.6, 0.9):
        cm = round(width * 100)
        c.type(f"Porta camarão {cm} x 210", "Porta camarão de duas folhas articuladas (venezianada em cima, almofadada embaixo), recolhida para a esquerda em trilho superior",
               Largura=width, Altura=2.1)
    return c
