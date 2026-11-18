"""Porta pivotante: marco de madeira com batedores, folha maciça frisada, pivôs de piso e de topo, puxador tubular.

O eixo do pivô fica a 17% do vão livre a partir do batente esquerdo, no meio
da espessura da parede; a parte larga da folha abre para +y e a estreita para
-y. Os batedores trocam de lado no pivô: no batente esquerdo e na travessa até
o pivô ficam do lado +y, depois dele e no batente direito do lado -y.
"""

from doorkit import *

JT = 0.04  # espessura do marco
T = 0.045  # espessura da folha
GAP = 0.004  # folga da folha ao marco
N_BANDS = 9  # réguas entre os frisos horizontais


def build() -> Component:
    c = Component("Porta pivotante", "doors", "porta-pivotante", "Door")
    L = c.param("Largura", 1.0)
    H = c.param("Altura", 2.4)
    A = opening_param(c, "AnguloAbertura", 75)
    c.opening = {"width": "Largura", "height": "Altura", "own_symbol": True}
    c.preview_size = (1.2, 1.0, 2.4)
    wood, core, steel = "Madeira escura", "Madeira", "Inox escovado"

    xl, xr = f"(-{L}/2)", f"({L}/2)"
    yb, yf = f"(-{WT}/2)", f"({WT}/2)"
    zh = f"({H} - {JT})"  # face de baixo da travessa
    wc = f"({L} - {2 * JT})"  # vão livre
    d = f"(0.17*{wc})"  # do batente esquerdo ao eixo
    xp = f"({xl} + {JT} + {d})"

    # --- marco ---------------------------------------------------------------
    c.box("Batente esquerdo simplificado", xl, yb, 0, 0.05, WT, H, wood, detail=COARSE, in_plan=True)
    c.box("Batente direito simplificado", f"{xr} - 0.05", yb, 0, 0.05, WT, H, wood, detail=COARSE, in_plan=True)
    c.box("Batente superior simplificado", f"{xl} + 0.05", yb, f"{H} - 0.05", f"{L} - 0.1", WT, 0.05, wood, detail=COARSE)
    c.box("Batente esquerdo", xl, yb, 0, JT, WT, H, wood, in_plan=True)
    c.box("Batente direito", f"{xr} - {JT}", yb, 0, JT, WT, H, wood, in_plan=True)
    c.box("Batente superior", f"{xl} + {JT}", yb, zh, wc, WT, JT, wood)
    st = 0.015  # batedores
    sd_f = f"({WT}/2 - {T / 2 + 0.002})"  # da face da parede à face da folha
    c.box("Batedor esquerdo", f"{xl} + {JT}", f"{T / 2 + 0.002}", 0, st, sd_f, zh, wood, in_plan=True)
    c.box("Batedor direito", f"{xr} - {JT + st}", yb, 0, st, sd_f, zh, wood, in_plan=True)
    c.box("Batedor superior até o pivô", f"{xl} + {JT + st}", f"{T / 2 + 0.002}", s(zh, -st), f"{d} - {st}", sd_f, st, wood)
    c.box("Batedor superior após o pivô", xp, yb, s(zh, -st), f"{wc} - {d} - {st}", sd_f, st, wood)
    # Vedação de borracha nas faces dos batedores.
    sl = 0.0015
    c.box("Vedação do batedor esquerdo", f"{xl} + {JT + 0.003}", f"{T / 2 + 0.002 - sl}", 0.02, 0.008, sl, s(zh, -0.03), "Borracha", detail=FINE)
    c.box("Vedação do batedor direito", f"{xr} - {JT + 0.011}", f"{-T / 2 - 0.002}", 0.02, 0.008, sl, s(zh, -0.03), "Borracha", detail=FINE)
    c.box("Vedação superior até o pivô", f"{xl} + {JT + 0.011}", f"{T / 2 + 0.002 - sl}", s(zh, -0.011), f"{d} - 0.05", sl, 0.008, "Borracha", detail=FINE)
    c.box("Vedação superior após o pivô", f"{xp} + 0.04", f"{-T / 2 - 0.002}", s(zh, -0.011), f"{wc} - {d} - 0.051", sl, 0.008, "Borracha", detail=FINE)
    casing(c, L, H, wood, yf, "frente", cw=0.08, ct=0.015)
    casing(c, L, H, wood, f"({yb} - 0.015)", "fundo", cw=0.08, ct=0.015)

    # --- folha ---------------------------------------------------------------
    fr = Fr(c, xp, 0, A)
    a0 = f"({GAP} - {d})"
    a1 = f"({wc} - {d} - {GAP})"
    zb, zt = 0.012, s(zh, -0.006)
    hl = s(zt, -zb)
    fr.box("Folha simplificada", a0, a1, -T / 2, T / 2, zb, hl, wood, detail=COARSE)
    fr.box("Folha - miolo", s(a0, 0.003), s(a1, -0.003), -T / 2 + 0.004, T / 2 - 0.004, zb, hl, core, in_plan=True)
    fr.box("Folha - fita de borda (pivô)", a0, s(a0, 0.003), -T / 2, T / 2, zb, hl, wood)
    fr.box("Folha - fita de borda (fechadura)", s(a1, -0.003), a1, -T / 2, T / 2, zb, hl, wood)
    g = 0.008  # largura dos frisos
    band = f"(({hl} - {(N_BANDS - 1) * g})/{N_BANDS})"
    for k in range(N_BANDS):
        zk = s(zb, f"{k}*({band} + {g})")
        for face, n0, n1 in (("frente", T / 2 - 0.004, T / 2), ("fundo", -T / 2, -T / 2 + 0.004)):
            fr.box(f"Folha - régua {k + 1} ({face})", s(a0, 0.003), s(a1, -0.003), n0, n1, zk, band, wood)
    # Veda-porta automático embutido na base da folha.
    fr.box("Veda-porta - perfil", s(a0, 0.05), s(a1, -0.05), -0.009, 0.009, 0.006, zb - 0.006, "Alumínio anodizado", detail=FINE)
    fr.box("Veda-porta - borracha", s(a0, 0.05), s(a1, -0.05), -0.005, 0.005, 0.0015, 0.0045, "Borracha", detail=FINE)

    # --- pivôs ---------------------------------------------------------------
    still = fr.still()
    still.box("Pivô de piso - base", -0.045, 0.045, -0.022, 0.022, 0, 0.003, steel)
    for k, a in enumerate((-0.033, 0.033)):
        still.cyl(f"Pivô de piso - parafuso {k + 1}", a, 0, 0.003, 0.0035, 0.001, "Cromado", detail=FINE)
    still.cyl("Pivô de piso - mancal", 0, 0, 0.003, 0.012, 0.004, "Cromado", detail=FINE)
    fr.cyl("Pivô de piso - eixo", 0, 0, 0.007, 0.008, zb - 0.002 + 0.02, "Cromado", detail=FINE)
    fr.box("Pivô de piso - sapata da folha", -0.04, 0.06, -0.012, 0.012, zb, 0.004, steel, detail=FINE)
    still.box("Pivô de topo - chapa", -0.035, 0.035, -0.02, 0.02, s(zh, -0.003), 0.003, steel)
    for k, a in enumerate((-0.025, 0.025)):
        still.cyl(f"Pivô de topo - parafuso {k + 1}", a, 0, s(zh, -0.004), 0.003, 0.001, "Cromado", detail=FINE)
    fr.cyl("Pivô de topo - eixo", 0, 0, s(zt, -0.01), 0.008, s(zh, f"-{zt}", 0.007), "Cromado", detail=FINE)
    fr.box("Pivô de topo - sapata da folha", -0.03, 0.05, -0.012, 0.012, s(zt, -0.003), 0.003, steel, detail=FINE)

    # --- puxador tubular nas duas faces ----------------------------------------
    ah = s(a1, -0.13)
    z0, z1 = 0.45, s(H, -0.75)
    hb = s(z1, -z0)
    so = 0.065  # afastamento do tubo à face
    for face, sg in (("frente", 1), ("fundo", -1)):
        nf = sg * T / 2
        nb = sg * (T / 2 + so)
        fr.cyl(f"Puxador ({face}) - tubo", ah, nb, z0, 0.016, hb, steel)
        fr.cyl(f"Puxador ({face}) - ponteira inferior", ah, nb, z0 - 0.006, 0.0165, 0.006, steel, detail=FINE)
        fr.cyl(f"Puxador ({face}) - ponteira superior", ah, nb, z1, 0.0165, 0.006, steel, detail=FINE)
        for k, zc in enumerate((s(z0, 0.15), s(z1, -0.15))):
            lo, hi = sorted((nf, nb))
            fr.box(f"Puxador ({face}) - haste {k + 1}", s(ah, -0.0095), s(ah, 0.0095), lo, hi, s(zc, -0.0095), 0.019, steel)
            lo, hi = sorted((nf, nf + sg * 0.004))
            fr.box(f"Puxador ({face}) - canopla {k + 1}", s(ah, -0.016), s(ah, 0.016), lo, hi, s(zc, -0.016), 0.032, steel, detail=FINE)
        # Cilindro da fechadura com espelho.
        zk = 1.05
        lo, hi = sorted((nf, nf + sg * 0.004))
        fr.box(f"Fechadura ({face}) - espelho", s(a1, -0.06), s(a1, -0.03), lo, hi, zk - 0.035, 0.07, steel, detail=FINE)
        lo, hi = sorted((nf + sg * 0.004, nf + sg * 0.008))
        fr.box(f"Fechadura ({face}) - cilindro", s(a1, -0.0535), s(a1, -0.0365), lo, hi, zk - 0.016, 0.032, "Latão", detail=FINE)
        lo, hi = sorted((nf + sg * 0.008, nf + sg * 0.0085))
        fr.box(f"Fechadura ({face}) - fenda", s(a1, -0.046), s(a1, -0.044), lo, hi, zk - 0.008, 0.012, "Plástico preto", detail=FINE)
    mortise_lock(fr, "Fechadura", a1, 0, 1.05 + 0.08, s(wc, f"-{d}"))

    # --- símbolo em planta: giro da parte larga para +y e da estreita para -y ----
    R, r = f"({wc} - {d})", d
    c.profile("Giro", "Plan", [(xp, 0), (f"{xp} + {R}", 0, R), (xp, R)], 0, 0.001, wood)
    c.plan_only("Giro")
    c.profile("Giro da parte estreita", "Plan", [(xp, 0), (f"{xp} - {r}", 0, r), (xp, f"-{r}")], 0, 0.001, wood)
    c.plan_only("Giro da parte estreita")

    for width in (1.0, 1.2, 1.5):
        c.type(f"Porta pivotante {round(width * 100)} x 240", "Porta de entrada pivotante, folha maciça frisada, pivôs de piso e de topo, puxador tubular de inox",
               Largura=width, Altura=2.4)
    return c
