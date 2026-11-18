"""Porta-janela de correr de alumínio e vidro, duas folhas móveis: marco com trilho inferior de dois
trilhos e trilho superior de dois canais, folhas com montantes de encontro intertravados, vidro
temperado com baguetes e gaxetas, roldanas, guias superiores, escovas de vedação, fecho com
alavanca, fechadura, trava de piso, puxadores e soleira de granito.

Frame (doorkit): x along the wall from the opening's center, y across it (-y the exterior,
+y the room), z up from the floor. The exterior leaf runs in the -y track and closes on the
left; the interior leaf runs in the +y track, closes on the right and slides left over it.
"""

from doorkit import *
from doorkit import Fr, s
from janela_comum import box_ring, stone, STONE, ALU, RUBBER
from _porta_correr_aparente import xspan, xof

GLASS = "Vidro temperado"
Z0 = 0.005  # top of the granite threshold = bottom of the frame
SW, MW, TR, BR = 0.045, 0.045, 0.045, 0.085  # widths of the outer stile, meeting stile, top and bottom rails
RAIL = {"externa": 0.018, "interna": 0.022}  # heights of the sill's rails above Z0
YC = {"externa": -0.023, "interna": 0.023}  # the leaves' planes
LD = 0.022  # leaf depth


def sash(c, fr: Fr, side, Lw, H):
    """One leaf: stiles, rails, glass, glazing beads and gaskets, rollers, top guides and brush seals.

    Leaf-local a runs from the outer stile (a = 0) to the meeting stile (a = Lw)."""
    yc = YC[side]
    y0, y1 = yc - LD / 2, yc + LD / 2
    rt = Z0 + RAIL[side]  # top of its rail
    zb, zt = rt - 0.008, f"({H} - 0.012)"  # the bottom skirts straddle the rail
    hgt = f"({zt} - {e(zb)})"
    pre = f"Folha {side}"
    fr.box(f"{pre} simplificada", 0, Lw, y0, y1, zb, hgt, GLASS, detail=COARSE)
    fr.box(f"{pre} - montante lateral", 0, SW, y0, y1, zb, hgt, ALU)
    fr.box(f"{pre} - montante de encontro", s(Lw, -MW), Lw, y0, y1, zb, hgt, ALU)
    fr.box(f"{pre} - travessa superior", SW, s(Lw, -MW), y0, y1, f"{zt} - {e(TR)}", TR, ALU)
    # Bottom rail: an inverted U whose skirts hide the rollers and the sill's rail.
    xr, wr = xspan(fr, SW, s(Lw, -MW))
    zc = zb + 0.034  # top of the rollers' cavity
    c.profile(f"{pre} - travessa inferior", "Side", [
        (y0, zb), (y0 + 0.002, zb), (y0 + 0.002, zc), (y1 - 0.002, zc), (y1 - 0.002, zb), (y1, zb), (y1, zb + BR), (y0, zb + BR),
    ], xr, wr, ALU)
    # Glass in the frame's groove, held by a fixed lip outside and a snap-in bead inside, EPDM gaskets both sides.
    g0, g1 = zb + BR, f"({zt} - {e(TR)})"
    fr.box(f"{pre} - vidro", s(SW, -0.008), s(Lw, -MW + 0.008), yc - 0.003, yc + 0.003, g0 - 0.008, f"{g1} - {e(g0 - 0.016)}", GLASS)
    x1 = f"({xr} + {wr})"
    box_ring(c, f"{pre} - baguete", xr, x1, g0, g1, 0, 0.01, yc + 0.0045, y1 - 0.0015, ALU)
    box_ring(c, f"{pre} - aba de encosto", xr, x1, g0, g1, 0, 0.01, y0 + 0.0015, yc - 0.0045, ALU)
    box_ring(c, f"{pre} - gaxeta interna", xr, x1, g0, g1, 0, 0.007, yc + 0.003, yc + 0.0045, RUBBER, FINE)
    box_ring(c, f"{pre} - gaxeta externa", xr, x1, g0, g1, 0, 0.007, yc - 0.0045, yc - 0.003, RUBBER, FINE)
    # Two rollers in the bottom rail, riding on the rail.
    zw = rt + 0.012
    for k, a in enumerate((0.08, s(Lw, -0.08))):
        nm = f"{pre} - roldana {k + 1}"
        x = xof(fr, a)
        fr.box(f"{nm} - caixa traseira", s(a, -0.03), s(a, 0.03), yc - 0.0095, yc - 0.0055, rt + 0.004, zc - rt - 0.004, "Plástico preto", detail=FINE)
        fr.box(f"{nm} - caixa frontal", s(a, -0.03), s(a, 0.03), yc + 0.0055, yc + 0.0095, rt + 0.004, zc - rt - 0.004, "Plástico preto", detail=FINE)
        c.cyl_y(f"{nm} - roda", x, zw, yc - 0.004, 0.012, 0.008, "Plástico cinza claro", detail=FINE)
        c.cyl_y(f"{nm} - eixo", x, zw, yc - 0.0055, 0.004, 0.011, "Cromado", detail=FINE)
        # Top guides in the head's channel.
        fr.box(f"{pre} - guia superior {k + 1}", s(a, -0.03), s(a, 0.03), yc - 0.008, yc + 0.008, zt, 0.008, "Plástico preto", detail=FINE)
    # Brush (pile) seals: on the outer stile's edge, into the jamb, and along both sides of the top rail.
    fr.box(f"{pre} - escova do montante", -0.003, 0, yc - 0.004, yc + 0.004, zb + 0.01, f"{hgt} - 0.02", "Borracha cinza", detail=FINE)
    for nm, ya in (("externa", y0 + 0.0005), ("interna", y1 - 0.0025)):
        fr.box(f"{pre} - escova superior {nm}", 0.01, s(Lw, -0.01), ya, ya + 0.002, zt, 0.006, "Borracha cinza", detail=FINE)
    return zb, zt


def cup(c, fr: Fr, name, a, face_y, sg, zc, w=0.02, h=0.14, depth=0.002):
    """A cup pull (concha) on a stile face at y = face_y, standing out towards sg (+1 = +y)."""
    x0, _ = xspan(fr, s(a, -w / 2), s(a, w / 2))
    y_ = face_y if sg > 0 else face_y - depth
    yi = face_y + depth if sg > 0 else face_y - depth - 0.0003
    c.profile(f"{name} - aro", "Front", rrect(x0, zc - h / 2, f"{x0} + {e(w)}", zc + h / 2, w / 2 - 0.0005), y_, depth, "Alumínio fundido")
    c.profile(f"{name} - concha", "Front", rrect(f"{x0} + 0.004", zc - h / 2 + 0.006, f"{x0} + {e(w - 0.004)}", zc + h / 2 - 0.006, w / 2 - 0.0045),
              yi, 0.0003, "Aço pintado preto", detail=FINE)


def build() -> Component:
    c = Component("Porta-janela de correr", "doors", "porta-janela-correr", "Door")
    L = c.param("Largura", 1.5)
    H = c.param("Altura", 2.1)
    ti = opening_param(c, "Abertura", 0.8, kind="Number")  # the interior leaf, sliding left (0..1)
    te = opening_param(c, "AberturaExterna", 0.25, kind="Number")  # the exterior leaf, sliding right (0..1)
    c.opening = {"width": "Largura", "height": "Altura", "own_symbol": True}
    c.preview_size = (1.6, 0.3, 2.1)
    stone(c)
    x0, x1 = f"(-{L}/2)", f"({L}/2)"

    # --- coarse stand-ins of the frame (the old component's 4 cm bars) ----------------------
    c.box("Marco simplificado esquerdo", x0, -0.04, Z0, 0.04, 0.08, f"{H} - {e(Z0)}", ALU, COARSE, in_plan=True)
    c.box("Marco simplificado direito", f"{x1} - 0.04", -0.04, Z0, 0.04, 0.08, f"{H} - {e(Z0)}", ALU, COARSE, in_plan=True)
    c.box("Marco simplificado inferior", f"{x0} + 0.04", -0.04, Z0, f"{L} - 0.08", 0.08, 0.03, ALU, COARSE)
    c.box("Marco simplificado superior", f"{x0} + 0.04", -0.04, f"{H} - 0.035", f"{L} - 0.08", 0.08, 0.035, ALU, COARSE)

    # --- granite threshold across the wall, nosing out on the exterior ----------------------
    c.profile("Soleira", "Side", [
        ("(-WallThickness/2 - 0.025)", -0.015), ("(WallThickness/2)", -0.015), ("(WallThickness/2)", Z0),
        ("(-WallThickness/2 - 0.02)", Z0, 0.005), ("(-WallThickness/2 - 0.025)", Z0 - 0.005),
    ], x0, L, STONE, detail=ALL)

    # --- frame: jambs with a channel for each leaf, head with two channels, sill with two rails
    jamb = [(0, -0.04), (0.03, -0.04), (0.03, -0.038), (0.003, -0.038), (0.003, -0.0095), (0.022, -0.0095), (0.022, -0.0075),
            (0.003, -0.0075), (0.003, 0.0075), (0.022, 0.0075), (0.022, 0.0095), (0.003, 0.0095), (0.003, 0.038), (0.03, 0.038),
            (0.03, 0.04), (0, 0.04)]
    hz = f"({H} - {e(Z0)})"
    c.profile("Marco montante esquerdo", "Plan", [(f"{x0} + {e(a)}", yy) for a, yy in jamb], Z0, hz, ALU, in_plan=True)
    c.profile("Marco montante direito", "Plan", [(f"{x1} - {e(a)}", yy) for a, yy in reversed(jamb)], Z0, hz, ALU, in_plan=True)
    xi, li = f"({x0} + 0.003)", f"({L} - 0.006)"
    h_ = lambda d: f"({H} - {e(d)})"  # noqa: E731
    c.profile("Trilho superior", "Side", [
        (-0.04, h_(0.035)), (-0.038, h_(0.035)), (-0.038, h_(0.004)), (-0.0095, h_(0.004)), (-0.0095, h_(0.025)), (-0.0075, h_(0.025)),
        (-0.0075, h_(0.004)), (0.0075, h_(0.004)), (0.0075, h_(0.025)), (0.0095, h_(0.025)), (0.0095, h_(0.004)), (0.038, h_(0.004)),
        (0.038, h_(0.035)), (0.04, h_(0.035)), (0.04, H), (-0.04, H),
    ], xi, li, ALU)
    re, ri = Z0 + RAIL["externa"], Z0 + RAIL["interna"]
    c.profile("Trilho inferior", "Side", [
        (-0.045, Z0), (0.04, Z0), (0.04, Z0 + 0.03), (0.0375, Z0 + 0.03), (0.0375, Z0 + 0.008),
        (0.0245, Z0 + 0.008), (0.0245, ri - 0.0007, 0.002), (0.0215, ri - 0.0007), (0.0215, Z0 + 0.008),
        (0.0015, Z0 + 0.008), (0.0015, Z0 + 0.014), (-0.0015, Z0 + 0.014), (-0.0015, Z0 + 0.004),
        (-0.0215, Z0 + 0.004), (-0.0215, re - 0.0007, 0.002), (-0.0245, re - 0.0007), (-0.0245, Z0 + 0.004),
        (-0.038, Z0 + 0.004), (-0.038, Z0 + 0.012), (-0.04, Z0 + 0.012), (-0.04, Z0 + 0.006), (-0.045, Z0 + 0.002),
    ], xi, li, ALU)
    for k, x in enumerate((f"(-{L}/4)", f"({L}/4)")):
        c.box(f"Tampa de dreno {k + 1}", f"{x} - 0.015", -0.0415, Z0 + 0.0065, 0.03, 0.0015, 0.005, "Plástico preto", detail=FINE)
    # Sealant beads where the frame meets the wall's reveal, and screw caps in the jambs' channels.
    box_ring(c, "Cordão de silicone externo", x0, x1, Z0, H, 0, 0.004, -0.0415, -0.04, "Borracha cinza", FINE, "lrt")
    box_ring(c, "Cordão de silicone interno", x0, x1, Z0, H, 0, 0.004, 0.04, 0.0415, "Borracha cinza", FINE, "lrt")
    n = 0
    for x in (f"{x0} + 0.003", f"{x1} - 0.0042"):
        for z in (0.3, f"{H} - 0.3"):
            n += 1
            c.profile(f"Tampa de parafuso {n}", "Side", disc(0, z, 0.005), x, 0.0012, "Plástico cinza claro", detail=FINE)

    # --- the leaves ---------------------------------------------------------------------------
    Lw = f"({L}/2 + 0.019)"  # each leaf, from 6 mm inside the jamb to 25 mm past the middle
    T = f"({L}/2 - 0.071)"  # travel: the moving leaf stacks over the other, its handle 4 cm clear of the jamb
    xc = f"(-{L}/2 + 0.006)"
    fe = Fr(c, f"({xc} + min(max({te}, 0), 1)*{T})", 0, 0)
    fi = Fr(c, f"({xc} + min(max({ti}, 0), 1)*{T})", 0, 0, mx=True)
    zbe, zt = sash(c, fe, "externa", Lw, H)
    zbi, _ = sash(c, fi, "interna", Lw, H)

    # Interlock: a fin on each meeting stile reaching into the other leaf's plane, a brush between them.
    ze0, zi0, z1 = zbe + BR, zbi + BR, f"({zt} - {e(TR)})"
    fe.box("Encontro - aba da folha externa", s(Lw, -0.005), Lw, -0.012, 0.006, ze0, f"{z1} - {e(ze0)}", ALU)
    fi.box("Encontro - aba da folha interna", s(Lw, -0.043), s(Lw, -0.038), -0.006, 0.012, zi0, f"{z1} - {e(zi0)}", ALU)
    fe.box("Encontro - escova", s(Lw, -0.0065), s(Lw, -0.005), -0.006, 0.006, ze0, f"{z1} - {e(ze0)}", "Borracha cinza", detail=FINE)
    for nm, f, a0, a1, n0, n1, zz in (("externa", fe, s(Lw, -0.005), Lw, -0.012, 0.006, ze0), ("interna", fi, s(Lw, -0.043), s(Lw, -0.038), -0.006, 0.012, zi0)):
        f.box(f"Encontro - terminal inferior da folha {nm}", a0, a1, n0, n1, zz - 0.004, 0.004, "Plástico preto", detail=FINE)
        f.box(f"Encontro - terminal superior da folha {nm}", a0, a1, n0, n1, z1, 0.004, "Plástico preto", detail=FINE)

    # --- hardware ----------------------------------------------------------------------------
    am = s(Lw, -MW / 2)  # middle of a meeting stile
    yi1 = YC["interna"] + LD / 2  # the interior leaf's room face
    ye0 = YC["externa"] - LD / 2  # the exterior leaf's outside face
    # Latch (fecho concha com alavanca) on the interior leaf's meeting stile, a bar pull above it.
    xm0, _ = xspan(fi, s(am, -0.013), s(am, 0.013))
    c.profile("Fecho - espelho", "Front", rrect(xm0, 0.94, f"{xm0} + 0.026", 1.06, 0.012), yi1, 0.005, "Alumínio fundido")
    fi.box("Fecho - eixo", s(am, -0.005), s(am, 0.005), yi1 + 0.005, yi1 + 0.012, 0.99, 0.02, "Alumínio fundido", detail=FINE)
    fi.box("Fecho - alavanca", s(am, -0.004), s(am, 0.004), yi1 + 0.009, yi1 + 0.016, 0.995, 0.06, "Alumínio fundido")
    c.cyl_y("Fecho - pega", xof(fi, am), 1.05, yi1 + 0.012, 0.007, 0.008, "Alumínio fundido", detail=FINE)
    xm = xof(fi, am)
    c.cyl("Puxador", xm, yi1 + 0.035, 1.1, 0.01, 0.3, "Alumínio anodizado")
    for k, z in enumerate((1.13, 1.37)):
        c.cyl_y(f"Puxador - haste {k + 1}", xm, z, yi1, 0.006, 0.03, "Alumínio anodizado")
        c.cyl_y(f"Puxador - base {k + 1}", xm, z, yi1, 0.011, 0.003, "Alumínio anodizado", detail=FINE)
    # Security bolt at the foot of the interior leaf's meeting stile, dropping into the sill.
    fi.box("Trava de piso - corpo", s(am, -0.011), s(am, 0.011), yi1, yi1 + 0.008, zbi + 0.1, 0.07, "Alumínio fundido", detail=FINE)
    fi.box("Trava de piso - botão", s(am, -0.005), s(am, 0.005), yi1 + 0.008, yi1 + 0.016, zbi + 0.14, 0.012, "Plástico preto", detail=FINE)
    # Exterior leaf: key lock and a cup pull on its meeting stile, outside.
    xk = xof(fe, am)
    c.cyl_y("Fechadura - espelho (externo)", xk, 0.95, ye0 - 0.004, 0.014, 0.004, "Alumínio fundido")
    c.cyl_y("Fechadura - cilindro (externo)", xk, 0.95, ye0 - 0.006, 0.008, 0.002, "Latão", detail=FINE)
    c.box("Fechadura - fenda da chave (externo)", f"{xk} - 0.001", ye0 - 0.0064, 0.944, 0.002, 0.0004, 0.012, "Plástico preto", detail=FINE)
    cup(c, fe, "Puxador concha externo", am, ye0, -1, 1.08)
    # Cup pulls on the outer stiles, on the faces left in view: inside for the exterior leaf, outside for the interior one.
    cup(c, fe, "Puxador concha da folha externa", 0.032, YC["externa"] + LD / 2, 1, 1.0)
    cup(c, fi, "Puxador concha da folha interna", 0.032, YC["interna"] - LD / 2, -1, 1.0)

    # --- plan symbol: both leaves where they stand and the way each slides --------------------
    for nm, f, yc, d in (("externa", fe, YC["externa"], 1), ("interna", fi, YC["interna"], 1)):
        f.poly(f"Símbolo da folha {nm}", [(0, yc - 0.004), (Lw, yc - 0.004), (Lw, yc + 0.004), (0, yc + 0.004)], 0, 0.001, ALU)
        c.plan_only(f"Símbolo da folha {nm}")
    for nm, xa, yy, d in (("externa", f"(-{L}/4)", -0.1, 1), ("interna", f"({L}/4)", 0.1, -1)):
        a0, a1, ah = f"{xa} - {e(0.12 * d)}", f"{xa} + {e(0.12 * d)}", f"{xa} + {e(0.06 * d)}"
        pts = [(a0, yy - 0.004), (ah, yy - 0.004), (ah, yy - 0.018), (a1, yy), (ah, yy + 0.018), (ah, yy + 0.004), (a0, yy + 0.004)]
        if d < 0:
            pts.reverse()
        c.profile(f"Sentido de abertura da folha {nm}", "Plan", pts, 0, 0.001, ALU)
        c.plan_only(f"Sentido de abertura da folha {nm}")

    d_ = "Porta de correr em alumínio e vidro, duas folhas, para varanda ou jardim"
    c.type("Porta-janela de correr 150 x 210", d_, Largura=1.5, Altura=2.1)
    c.type("Porta-janela de correr 200 x 210", d_, Largura=2.0, Altura=2.1)
    c.type("Porta-janela de correr 250 x 210", d_, Largura=2.5, Altura=2.1)
    return c
