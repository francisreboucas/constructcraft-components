"""Portão basculante de garagem com contrapesos: colunas em U, folha de metalon com lambril, braços, trilhos e roldanas.

Mecanismo: as roldanas do topo da folha correm em trilhos horizontais que
entram na garagem (+y), e um braço de cada lado liga o batente (eixo F, no
ponto onde fica a roldana com o portão fechado) à lateral da folha a um terço
da altura. Com o braço do mesmo comprimento que a distância da roldana ao
ponto do braço, a roldana anda 2*sP*sin(ângulo) no trilho, e a folha fica
deitada sob a travessa com um terço para fora (-y) quando AnguloAbertura = 90.
Os contrapesos correm dentro das colunas, presos por cabo de aço que passa
por uma polia no alto da coluna e desce até a base da folha.
"""

from doorkit import *

CW = 0.10  # largura das colunas (x)
CD = 0.05  # meia profundidade das colunas (y)
HB = 0.08  # altura da travessa superior
TK = 0.003  # chapa das colunas


def build() -> Component:
    c = Component("Portão basculante", "doors", "portao-basculante", "Door")
    L = c.param("Largura", 2.5)
    H = c.param("Altura", 2.2)
    g = opening_param(c, "AnguloAbertura", 80)
    c.opening = {"width": "Largura", "height": "Altura", "own_symbol": True}
    c.preview_size = (3.0, 2.0, 2.4)
    frame, leaf_mat, dark = "Aço pintado cinza", "Aço pintado branco", "Aço pintado preto"

    xc = f"(-{L}/2 + {CW})"  # face interna da coluna esquerda
    ztop = f"({H} - {HB} - 0.012)"  # topo da folha
    zbot = 0.02
    Hl = f"({ztop} - {zbot})"
    zT = f"({ztop} - 0.03)"  # eixo das roldanas
    sP = f"({Hl}/3)"  # da roldana ao pino do braço
    yT = f"(2*{sP}*sin({g}))"
    sin, cos = f"sin({g})", f"cos({g})"
    xl_leaf = f"({xc} + 0.054)"  # lateral esquerda da folha
    Wl = f"({L} - {2 * CW + 0.108})"

    def lp(s_, t_):
        """(y, z) of the leaf point s down from the roller axis and t out of the leaf (towards -y when closed)."""
        return (f"{yT} - {p(s_)}*{sin} - {p(t_)}*{cos}", f"{zT} - {p(s_)}*{cos} + {p(t_)}*{sin}")

    def leaf_prof(name, pts, x, w, mat, detail=FULL, in_plan=False):
        c.profile(name, "Side", [lp(q[0], q[1]) + tuple(q[2:]) for q in pts], x, w, mat, detail=detail, in_plan=in_plan)

    def leaf_box(name, x, w, s0, s1, t0, t1, mat, detail=FULL, in_plan=False):
        leaf_prof(name, [(s0, t0), (s1, t0), (s1, t1), (s0, t1)], x, w, mat, detail, in_plan)

    def leaf_rod(name, x, w, s_, t_, r, mat, detail=FULL):
        cy, cz = lp(s_, t_)
        c.profile(name, "Side", disc(cy, cz, r), x, w, mat, detail=detail)

    def arm_pt(u, v):
        """(y, z) of a point of the arm turning about F = (0, zT): u along the arm, v across it."""
        return (f"{p(u)}*{sin} + {p(v)}*{cos}", f"{zT} - {p(u)}*{cos} + {p(v)}*{sin}")

    def mx(x, w):
        """The x of the mirrored copy of a piece spanning x..x + w."""
        return f"(-{p(x)} - {p(w)})"

    # --- marco: colunas em U abertas para dentro e travessa superior --------------------
    c.box("Coluna esquerda simplificada", f"-{L}/2", -CD, 0, CW, 2 * CD, H, frame, detail=COARSE, in_plan=True)
    c.box("Coluna direita simplificada", f"{L}/2 - {CW}", -CD, 0, CW, 2 * CD, H, frame, detail=COARSE, in_plan=True)
    c.box("Travessa superior simplificada", xc, -CD, f"{H} - {HB}", f"{L} - {2 * CW}", 2 * CD, HB, frame, detail=COARSE)
    for side, x0 in (("esquerda", f"(-{L}/2)"), ("direita", f"({L}/2 - {CW})")):
        c.box(f"Coluna {side} - alma", x0, -CD, 0, CW, TK, H, frame, in_plan=True)
        c.box(f"Coluna {side} - aba externa", x0 if side == "esquerda" else f"{x0} + {CW - TK}", -CD + TK, 0, TK, 2 * CD - TK, H, frame, in_plan=True)
        c.box(f"Coluna {side} - aba interna", f"{x0} + {CW - TK}" if side == "esquerda" else x0, -CD + TK, 0, TK, 2 * CD - TK, H, frame, in_plan=True)
        c.box(f"Coluna {side} - tampa", x0, -CD, f"{H} - 0.003", CW, 2 * CD, 0.003, frame, detail=FINE)
    c.box("Travessa superior", xc, -CD, f"{H} - {HB}", f"{L} - {2 * CW}", 2 * CD, HB, frame)
    # Batedor de piso do lado de dentro, com borracha.
    c.box("Batedor de piso", xl_leaf, 0.017, 0, Wl, 0.025, 0.004, frame)
    c.box("Batedor de piso - aba", xl_leaf, 0.017, 0.004, Wl, 0.003, 0.03, frame)
    c.box("Batedor de piso - borracha", xl_leaf, 0.0155, 0.004, Wl, 0.0015, 0.025, "Borracha", detail=FINE)

    # --- folha (gira com o ângulo) --------------------------------------------
    s_top, s_bot = -0.03, f"({Hl} - 0.03)"
    leaf_box("Folha simplificada", xl_leaf, Wl, s_top, s_bot, -0.015, 0.028, leaf_mat, detail=COARSE, in_plan=True)
    tw = 0.05  # metalon 50 x 30
    leaf_box("Quadro - montante esquerdo", xl_leaf, tw, s_top, s_bot, -0.015, 0.015, leaf_mat, in_plan=True)
    leaf_box("Quadro - montante direito", f"{xl_leaf} + {Wl} - {tw}", tw, s_top, s_bot, -0.015, 0.015, leaf_mat, in_plan=True)
    xi, wi = f"({xl_leaf} + {tw})", f"({Wl} - {2 * tw})"
    leaf_box("Quadro - travessa superior", xi, wi, s_top, s_top + tw, -0.015, 0.015, leaf_mat)
    leaf_box("Quadro - travessa inferior", xi, wi, s(s_bot, -tw), s_bot, -0.015, 0.015, leaf_mat, in_plan=True)
    for k in (1, 2):
        sk = s(f"{k}*{Hl}/3", -0.055)
        leaf_box(f"Quadro - travessa intermediária {k}", xi, wi, sk, s(sk, tw), -0.015, 0.015, leaf_mat)
    leaf_box("Quadro - montante central", -0.02, 0.04, s_top + tw, s(s_bot, -tw), -0.015, 0.015, leaf_mat)
    # Lambril: chapa e réguas com chanfro (frisos em V entre elas).
    leaf_box("Lambril - chapa", xl_leaf, Wl, s_top, s_bot, 0.015, 0.0165, leaf_mat)
    n_rib = 20
    pitch = f"(({Hl} - 0.01)/{n_rib})"
    for k in range(n_rib):
        sa = s(s_top, 0.005, f"{k}*{pitch}")
        sb = s(sa, pitch)
        leaf_prof(f"Lambril - régua {k + 1}", [(s(sa, 0.002), 0.0165), (s(sb, -0.002), 0.0165), (s(sb, -0.012), 0.026), (s(sa, 0.012), 0.026)],
                  xl_leaf, Wl, leaf_mat)
    leaf_box("Vedação inferior", xl_leaf, Wl, s_bot, s(s_bot, 0.014), -0.008, 0.02, "Borracha", detail=FINE)

    # Fechadura central com trancas laterais; puxadores por fora e alça por dentro.
    s_l = f"({zT} - 1.0)"
    leaf_box("Fechadura - caixa", -0.06, 0.12, s(s_l, -0.07), s(s_l, 0.07), -0.045, -0.015, dark)
    leaf_box("Fechadura - espelho", -0.035, 0.07, s(s_l, -0.05), s(s_l, 0.05), -0.047, -0.045, "Cromado", detail=FINE)
    leaf_box("Fechadura - maçaneta", -0.01, 0.02, s(s_l, -0.012), s(s_l, 0.012), -0.075, -0.047, "Cromado")
    leaf_box("Fechadura - alavanca", -0.01, 0.02, s(s_l, -0.012), s(s_l, 0.09), -0.085, -0.075, "Cromado")
    leaf_box("Fechadura - cilindro (fora)", -0.009, 0.018, s(s_l, -0.016), s(s_l, 0.016), 0.026, 0.032, "Latão", detail=FINE)
    leaf_box("Fechadura - fenda (fora)", -0.001, 0.002, s(s_l, -0.008), s(s_l, 0.008), 0.032, 0.0325, "Plástico preto", detail=FINE)
    rod_l = f"({xl_leaf} - 0.046)"  # ponta da tranca, dentro do batedor da coluna
    rod_w = f"(-{rod_l} - 0.06)"
    leaf_rod("Tranca esquerda", rod_l, rod_w, s_l, -0.03, 0.008, "Aço galvanizado")
    leaf_rod("Tranca direita", 0.06, rod_w, s_l, -0.03, 0.008, "Aço galvanizado")
    for k, xg in enumerate((f"({xl_leaf} + 0.07)", f"({xl_leaf} + {Wl}/4)", f"(-{xl_leaf} - 0.1)", f"(-{xl_leaf} - {Wl}/4 - 0.03)")):
        leaf_box(f"Tranca - guia {k + 1}", xg, 0.03, s(s_l, -0.014), s(s_l, 0.014), -0.042, -0.015, dark, detail=FINE)
    so = f"({s_l} + 0.13)"
    leaf_rod("Puxador externo - barra", -0.15, 0.3, so, 0.065, 0.011, "Cromado")
    for k, xs_ in enumerate((-0.13, 0.11)):
        leaf_box(f"Puxador externo - haste {k + 1}", xs_, 0.02, s(so, -0.008), s(so, 0.008), 0.026, 0.065, "Cromado")
    sa_ = s(s_bot, -0.25)
    leaf_rod("Alça interna - barra", -0.12, 0.24, sa_, -0.06, 0.01, "Cromado")
    for k, xs_ in enumerate((-0.11, 0.09)):
        leaf_box(f"Alça interna - haste {k + 1}", xs_, 0.02, s(sa_, -0.008), s(sa_, 0.008), -0.06, -0.015, "Cromado")

    # --- mecanismo de cada lado ---------------------------------------------------
    zQ = zT  # eixo das polias
    sB = f"({Hl} - 0.08)"  # ponto do cabo na folha
    yB, zB = lp(sB, 0)
    dy, dz = f"({yB} + 0.025)", f"({zB} - {zQ})"
    ln = f"sqrt({dy}*{dy} + {dz}*{dz})"
    l0 = f"sqrt(0.000625 + {sB}*{sB})"
    zcw = f"({zQ} - 0.2 - ({l0} - {ln}))"  # topo do contrapeso
    hw = 0.0025  # meia espessura do cabo
    ox, oz = f"(-{dz}/{ln}*{hw})", f"({dy}/{ln}*{hw})"
    trk_end = f"(2*{sP} + 0.08)"
    for side in ("esquerdo", "direito"):
        left = side == "esquerdo"

        def X(x, w):
            return x if left else mx(x, w)

        # Trilho horizontal em U (alma junto à coluna, abas em cima e embaixo) e suspensão.
        tx = s(xc, 0.012)
        c.box(f"Trilho {side} - alma", X(tx, 0.003), -0.04, s(zT, -0.033), 0.003, f"{trk_end} + 0.04", 0.066, frame)
        c.box(f"Trilho {side} - aba superior", X(tx, 0.03), -0.04, s(zT, 0.03), 0.03, f"{trk_end} + 0.04", 0.003, frame)
        c.box(f"Trilho {side} - aba inferior", X(tx, 0.03), -0.04, s(zT, -0.033), 0.03, f"{trk_end} + 0.04", 0.003, frame)
        c.box(f"Trilho {side} simplificado", X(tx, 0.03), -0.04, s(zT, -0.033), 0.03, f"{trk_end} + 0.04", 0.066, frame, detail=COARSE)
        c.box(f"Trilho {side} - fim de curso", X(s(tx, 0.003), 0.027), s(trk_end, -0.02), s(zT, -0.03), 0.027, 0.02, 0.06, "Borracha", detail=FINE)
        c.box(f"Trilho {side} - suspensão", X(tx, 0.03), s(trk_end, -0.06), s(zT, 0.033), 0.03, 0.004, 0.35, frame)
        c.box(f"Trilho {side} - chapa de fixação", X(s(tx, -0.02), 0.07), s(trk_end, -0.09), s(zT, 0.383), 0.07, 0.06, 0.005, frame, detail=FINE)
        c.box(f"Trilho {side} - suporte na coluna", X(xc, 0.042), -0.04, s(zT, 0.033), 0.042, 0.09, f"{H} - {HB} - {zT} - 0.033", frame)
        # Braço: chapa chata girando em F, pinos em F e na folha.
        bx = s(xc, 0.044)
        c.profile(f"Braço {side}", "Side", [arm_pt(-0.02, -0.018), arm_pt(s(sP, 0.02), -0.018), arm_pt(s(sP, 0.02), 0.018), arm_pt(-0.02, 0.018)],
                  X(bx, 0.006), 0.006, dark)
        c.profile(f"Braço {side} - pino fixo", "Side", disc(0, zT, 0.008), X(s(xc, 0.042), 0.012), 0.012, "Cromado", detail=FINE)
        py, pz = arm_pt(sP, 0)
        c.profile(f"Braço {side} - pino da folha", "Side", disc(py, pz, 0.008), X(bx, 0.012), 0.012, "Cromado", detail=FINE)
        leaf_box(f"Braço {side} - suporte na folha", X(s(bx, 0.006), 0.004), 0.004, s(sP, -0.03), s(sP, 0.03), -0.015, 0.015, dark, detail=FINE)
        # Roldana no topo da folha: roda no trilho, eixo e suporte.
        leaf_rod(f"Roldana {side} - roda", X(s(xc, 0.017), 0.018), 0.018, 0, 0, 0.024, "Plástico preto")
        leaf_rod(f"Roldana {side} - cubo", X(s(xc, 0.015), 0.022), 0.022, 0, 0, 0.009, "Cromado", detail=FINE)
        leaf_rod(f"Roldana {side} - eixo", X(s(xc, 0.035), 0.019), 0.019, 0, 0, 0.007, "Cromado")
        leaf_box(f"Roldana {side} - suporte", X(s(xc, 0.05), 0.004), 0.004, -0.03, 0.06, -0.015, 0.015, dark, detail=FINE)
        # Polia no alto da coluna, contrapeso de concreto e cabos.
        c.profile(f"Polia {side}", "Side", disc(0, zQ, 0.025), X(s(xc, -0.07), 0.078), 0.078, "Aço galvanizado")
        c.profile(f"Polia {side} - eixo", "Side", disc(0, zQ, 0.008), X(s(xc, -0.097), 0.11), 0.11, "Cromado", detail=FINE)
        cwx = f"(-{L}/2 + 0.012)"
        c.box(f"Contrapeso {side}", X(cwx, CW - 0.024), -0.035, f"{zcw} - 0.35", CW - 0.024, 0.075, 0.35, "Concreto")
        c.box(f"Contrapeso {side} - olhal", X(s(cwx, 0.036), 0.004), 0.021, zcw, 0.004, 0.008, 0.012, "Aço galvanizado", detail=FINE)
        c.box(f"Cabo do contrapeso {side}", X(s(cwx, 0.036), 0.004), 0.023, zcw, 0.004, 0.004, f"{zQ} - {zcw}", "Aço galvanizado")
        c.profile(f"Cabo da folha {side}", "Side",
                  [(f"-0.025 + {ox}", f"{zQ} + {oz}"), (f"{yB} + {ox}", f"{zB} + {oz}"), (f"{yB} - {ox}", f"{zB} - {oz}"), (f"-0.025 - {ox}", f"{zQ} - {oz}")],
                  X(s(xc, 0.002), 0.004), 0.004, "Aço galvanizado")
        leaf_box(f"Cabo da folha {side} - suporte", X(xc, 0.054), 0.054, s(sB, -0.02), s(sB, 0.02), -0.01, 0.01, dark, detail=FINE)
        # Batedor na coluna (lado de dentro, abaixo do braço), com borracha e receptor da tranca.
        zs = f"({zT} - {sP} - 0.06)"
        c.box(f"Batedor {side}", X(xc, 0.064), 0.017, 0, 0.064, 0.015, zs, frame)
        c.box(f"Batedor {side} - borracha", X(s(xc, 0.054), 0.01), 0.0155, 0.03, 0.01, 0.0015, f"{zs} - 0.06", "Borracha", detail=FINE)
        c.box(f"Receptor da tranca {side}", X(s(xc, 0.004), 0.03), 0.032, s(zT, -1.03), 0.03, 0.006, 0.06, dark, detail=FINE)

    # --- símbolo em planta: a folha deitada sob a travessa, um terço para fora -------------
    y0, y1 = f"(2*{sP} - {Hl} + 0.03)", f"(2*{sP} + 0.03)"
    c.profile("Abertura", "Plan", [(xl_leaf, y0), (f"-{xl_leaf}", y0), (f"-{xl_leaf}", y1), (xl_leaf, y1)], 0, 0.001, leaf_mat)
    c.plan_only("Abertura")

    for width in (2.5, 3.0):
        c.type(f"Portão basculante {round(width * 100)} x 220", "Portão basculante de garagem com contrapesos: colunas em U, folha de metalon com lambril, braços, trilhos e roldanas",
               Largura=width, Altura=2.2)
    return c
