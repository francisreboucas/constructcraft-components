"""Guarda-roupa: wardrobe of two to six hinged doors with a maleiro on top, hanging rails, shelves and an internal drawer bank.

Bays behind the doors, from the left: A (hanging, one door in the 2-door type,
two doors otherwise), B (one door: drawer bank and shelves), C (one door,
shelves; 4 doors and up) and D (the rest: double hanging; 5 doors and up).
The doors pivot on their front face (cup hinges): two doors hinged on the
same division clear each other.
"""

from kit import *

EPS = 0.002  # scale of a collapsed group: its pieces shrink into a point hidden inside the right side panel


class Grp:
    """Pieces scaled by `k` about the point `h`.

    k = 1 leaves the pieces as they are; k = EPS shrinks them into `h`, which
    lies inside a solid panel: that is how the doors and bays that a narrower
    type does not have disappear (a piece cannot have zero size).
    Without `k` the pieces are written as they are.
    """

    def __init__(self, c, k=None, h=(0, 0, 0)):
        self.c, self.k, self.h = c, k, h

    def _at(self, i, v):
        return e(v) if self.k is None else f"{p(self.h[i])} + {p(self.k)}*({e(v)} - {p(self.h[i])})"

    def x(self, v):
        return self._at(0, v)

    def y(self, v):
        return self._at(1, v)

    def z(self, v):
        return self._at(2, v)

    def l(self, v):
        return e(v) if self.k is None else f"{p(self.k)}*{p(v)}"

    def box(self, name, x, y, z, w, d, h, mat, **kw):
        self.c.box(name, self.x(x), self.y(y), self.z(z), self.l(w), self.l(d), self.l(h), mat, **kw)

    def cyl(self, name, x, y, z, r, h, mat, **kw):
        self.c.cyl(name, self.x(x), self.y(y), self.z(z), self.l(r), self.l(h), mat, **kw)

    def cyl_x(self, name, y, z, x, r, length, mat, **kw):
        self.c.cyl_x(name, self.y(y), self.z(z), self.x(x), self.l(r), self.l(length), mat, **kw)

    def cyl_y(self, name, x, z, y, r, length, mat, **kw):
        self.c.cyl_y(name, self.x(x), self.z(z), self.y(y), self.l(r), self.l(length), mat, **kw)

    def door_box(self, name, hinge, angle, a0, a1, b0, b1, z, height, mat, side="left", **kw):
        hg = (self.x(hinge[0]), self.y(hinge[1]))
        self.c.door_box(name, hg, angle, self.l(a0), self.l(a1), self.l(b0), self.l(b1), self.z(z), self.l(height), mat, side=side, **kw)

    def door_cyl(self, name, hinge, angle, a, b, z, r, height, mat, side="left", **kw):
        """A vertical cylinder that swings with a door: axis at (a, b) of the door."""
        cx, cy = swing((self.x(hinge[0]), self.y(hinge[1])), angle, self.l(a), self.l(b), side)
        self.c.cyl(name, cx, cy, self.z(z), self.l(r), self.l(height), mat, **kw)

    def profile(self, name, plane, pts, offset, depth, mat, **kw):
        fu, fv, fo = {"Plan": (self.x, self.y, self.z), "Front": (self.x, self.z, self.y), "Side": (self.y, self.z, self.x)}[plane]
        out = [(fu(q[0]), fv(q[1])) + ((self.l(q[2]),) if len(q) > 2 and q[2] not in (None, "", 0) else ()) for q in pts]
        self.c.profile(name, plane, out, fo(offset), self.l(depth), mat, **kw)


def clamp(v):
    """0 below 0, 1 above 1."""
    return f"min(1, max(0, {v}))"


def keep(v):
    """Scale of a group present when v >= 1 (collapsed when v <= 0)."""
    return f"min(1, max({EPS}, {v}))"


def at(base, d):
    """`base` moved by the number `d`."""
    return f"{p(base)} + {e(d)}" if d >= 0 else f"{p(base)} - {e(-d)}"


# --- doors -----------------------------------------------------------------------

TD = 0.018  # door thickness


def hinge(g, name, side, hinge_pt, xi, zc, A):
    """A cup hinge: the cup in the back of the door (swings), the arm on its plate on the panel.

    `hinge_pt` is the door's pivot, on its front face; `xi` the inner face of
    the panel that carries the hinge; `zc` the height of its center.
    """
    hx, hy = hinge_pt
    g.door_box(f"{name} - caneca", hinge_pt, A, 0.005, 0.04, -TD - 0.003, -TD, at(zc, -0.025), 0.05, "Aço galvanizado", side=side, detail=FINE)
    x0 = xi if side == "left" else at(xi, -0.012)
    g.box(f"{name} - braço", x0, at(hy, TD + 0.003), at(zc, -0.01), 0.012, 0.069, 0.02, "Aço galvanizado", detail=FINE)


def pull(g, name, side, hinge_pt, a, zc, length, A):
    """A vertical bar pull on the front of a door, centered at the height `zc`."""
    g.door_cyl(f"{name} - barra", hinge_pt, A, a, 0.026, f"{p(zc)} - {e(length / 2)}", 0.006, length, "Inox escovado", side=side)
    for k, dz in enumerate((-length / 2 + 0.02, length / 2 - 0.028), 1):
        g.door_box(f"{name} - pino {k}", hinge_pt, A, at(a, -0.004), at(a, 0.004), 0, 0.026, at(zc, dz), 0.008, "Inox escovado", side=side, detail=FINE)


# --- contents --------------------------------------------------------------------

HOOK_RO, HOOK_RI, STEM = 0.0165, 0.0135, 0.0015
RAIL_R = 0.0125

# outlines of garments on a hanger, (y, z) about the top of the hanger
SHIRT = [(-0.06, -0.012), (-0.2, -0.058), (-0.225, -0.14), (-0.215, -0.74), (0.215, -0.74), (0.225, -0.14), (0.2, -0.058), (0.06, -0.012)]
SHORT_SHIRT = [(-0.06, -0.012), (-0.2, -0.058), (-0.225, -0.14), (-0.215, -0.66), (0.215, -0.66), (0.225, -0.14), (0.2, -0.058), (0.06, -0.012)]
DRESS = [(-0.05, -0.012), (-0.17, -0.05), (-0.165, -0.32), (-0.245, -1.1), (0.245, -1.1), (0.165, -0.32), (0.17, -0.05), (0.05, -0.012)]
COAT = [(-0.07, -0.01), (-0.215, -0.055), (-0.24, -0.16), (-0.235, -1.0), (0.235, -1.0), (0.24, -0.16), (0.215, -0.055), (0.07, -0.01)]
HANGER = [(-0.205, -0.066), (0, -0.016), (0.205, -0.066), (0.2, -0.052), (0, 0), (-0.2, -0.052)]


def rail(g, name, x0, x1, y, z):
    """A round chrome hanging tube between two panel faces, on two flanged supports."""
    g.cyl_x(name, y, z, at(x0, 0.002), RAIL_R, f"{p(x1)} - {p(x0)} - 0.004", "Cromado")
    g.cyl_x(f"{name} - suporte esquerdo", y, z, x0, 0.019, 0.01, "Cromado")
    g.cyl_x(f"{name} - suporte direito", y, z, at(x1, -0.01), 0.019, 0.01, "Cromado")


def hanger(g, name, x, y, zr, mat="Madeira escura"):
    """A hanger on the rail at height zr: the hook (a wire bent over the tube) and the body. Returns its top."""
    zh = at(zr, -0.045)
    hook = [(-STEM, -0.05), (STEM, -0.05), (STEM, -0.035), (HOOK_RO, -0.018), (HOOK_RO, 0, HOOK_RO), (-HOOK_RO, 0), (-HOOK_RI, 0, -HOOK_RI),
            (HOOK_RI, 0), (HOOK_RI, -0.017), (-STEM, -0.0345)]
    g.profile(f"{name} - gancho", "Side", [(at(y, u), at(zr, v)) + tuple(q) for u, v, *q in hook], at(x, -0.0015), 0.003, "Cromado", detail=FINE)
    g.profile(f"{name} - cabide", "Side", [(at(y, u), at(zh, v)) for u, v in HANGER], at(x, -0.006), 0.012, mat, detail=FINE)
    return zh


def garment(g, name, x, y, zr, t, outline, mat, hmat="Madeira escura"):
    """A garment of thickness t on a hanger; x is its left face."""
    xc = at(x, t / 2)
    zh = hanger(g, name, xc, y, zr, hmat)
    g.profile(name, "Side", [(at(y, u), at(zh, v)) for u, v in outline], x, t, mat, detail=FINE)


def trousers(g, name, x, y, zr, mat, t=0.03):
    """Trousers folded over the bar of a hanger; x is their left face."""
    xc = at(x, t / 2)
    zh = hanger(g, name, xc, y, zr, "Plástico preto")
    g.cyl_y(f"{name} - barra do cabide", xc, at(zh, -0.07), at(y, -0.2), 0.004, 0.4, "Plástico preto", detail=FINE)
    g.profile(name, "Side", rrect(at(y, -0.16), at(zh, -0.66), at(y, 0.16), at(zh, -0.064), 0.012), x, t, mat, detail=FINE)


def stack(g, name, xc, y, z, w, d, items):
    """Folded clothes piled from z, centered on xc: items = [(height, material, inset)]."""
    zz = e(z)
    for k, (h, mat, dw) in enumerate(items, 1):
        pts = rrect(at(xc, -w / 2 + dw), zz, at(xc, w / 2 - dw), at(zz, h), round(h * 0.45, 4))
        g.profile(f"{name} - peça {k}", "Front", pts, at(y, dw / 2), d - dw, mat, detail=FINE)
        zz = at(zz, h)


def storage_box(g, name, x, y, z, w, d, h, mat):
    """A fabric box with its lid; (x, y, z) is its lowest corner."""
    g.box(name, x, y, z, w, d, h - 0.03, mat, detail=FINE)
    g.box(f"{name} - tampa", at(x, -0.003), at(y, -0.003), at(z, h - 0.03), w + 0.006, d + 0.006, 0.03, mat, detail=FINE)


def build():
    c = Component("Guarda-roupa", "casework", "guarda-roupa", "Casework")
    W = c.param("Largura", 1.5)
    D = c.param("Profundidade", 0.6)
    H = c.param("Altura", 2.3)
    N = c.param("Portas", 3, "Number")
    A = c.angle("AnguloPortas", 0, open_at=80)
    AM = c.angle("AnguloMaleiro", 0, open_at=80)
    G = c.param("AberturaGavetas", 0, "Length", True)
    c.open_pose["AberturaGavetas"] = 0.3
    c.material("MDF branco", (240, 240, 235), "Wood", "Satin")
    c.material("Espelho", (222, 228, 232), "Metal", "Polished")  # a silvered glass: a reflecting face
    c.material("Roupa de cama branca", (243, 241, 235), "Generic", "Matte")
    c.material("Tecido cinza", (150, 152, 156), "Generic", "Matte")
    c.material("Tecido cinza escuro", (92, 95, 100), "Generic", "Matte")
    c.material("Tecido mostarda", (201, 152, 58), "Generic", "Matte")
    c.material("Tecido azul petróleo", (48, 92, 110), "Generic", "Matte")
    WOOD, MDF, STEEL = "Madeira clara", "MDF branco", "Aço galvanizado"
    WHITE, GREY, DARK, MUST, BLUE = "Roupa de cama branca", "Tecido cinza", "Tecido cinza escuro", "Tecido mostarda", "Tecido azul petróleo"

    T = 0.018
    xL, xR = f"(-{W}/2)", f"({W}/2)"
    yF, yB = f"(-{D}/2)", f"({D}/2)"
    yC = f"({yF} + 0.02)"  # front edge of the carcass, behind the doors
    yK = f"({yB} - 0.006)"  # front face of the back panel
    dK = f"({D} - 0.026)"  # depth of the panels inside
    yr = f"(({yC} + {yK})/2)"  # the hanging rails
    zg, zP = 0.008, 0.08  # glides, top of the plinth
    zM = f"({H} - 0.42)"  # middle of the maleiro floor
    zT = f"({H} - {T})"  # underside of the top
    Wd = f"({W}/{N})"
    nA = f"min(2, {N} - 1)"  # doors over bay A
    xd1 = f"({xL} + {nA}*{Wd})"  # divisions
    xd2 = f"({xd1} + {Wd})"
    xd3 = f"({xd1} + 2*{Wd})"
    lastB = f"(1 - {clamp(f'{N} - 3')})"  # 1 when bay B ends at the right side
    lastC = f"(1 - {clamp(f'{N} - 4')})"
    xa0, xa1 = f"({xL} + {T})", f"({xd1} - {T}/2)"
    xb0, xb1 = f"({xd1} + {T}/2)", f"({xd1} + {Wd} - {T}/2 - {T}/2*{lastB})"
    xc0, xc1 = f"({xd2} + {T}/2)", f"({xd2} + {Wd} - {T}/2 - {T}/2*{lastC})"
    xe0, xe1 = f"({xd3} + {T}/2)", f"({xR} - {T})"
    wa, wb, wc = f"({xa1} - {xa0})", f"({xb1} - {xb0})", f"({xc1} - {xc0})"
    we = f"max(0.3, {xe1} - {xe0})"
    xbc, xcc, xec = f"(({xb0} + {xb1})/2)", f"(({xc0} + {xc1})/2)", f"({xe0} + {we}/2)"

    hide = (f"{xR} - {T}/2", f"({yC} + {yB})/2", f"{H}/2")  # inside the right side
    gA = gB = Grp(c)
    gC = Grp(c, keep(f"{N} - 3"), hide)
    gD = Grp(c, keep(f"{N} - 4"), hide)
    gd = {i: Grp(c) if i <= 2 else Grp(c, keep(f"{N} - {i - 1}"), hide) for i in range(1, 7)}

    # coarse stand-ins: the plinth and the body
    c.box("Rodapé", xL, f"{yF} + 0.05", 0, W, f"{D} - 0.05", zP, WOOD, detail=COARSE)
    c.box("Corpo", xL, yF, zP, W, D, f"{H} - {zP}", WOOD, detail=COARSE, in_plan=True)

    # carcass
    c.box("Lateral esquerda", xL, yC, zg, T, f"{D} - 0.02", f"{zT} - {zg}", WOOD)
    c.box("Lateral direita", f"{xR} - {T}", yC, zg, T, f"{D} - 0.02", f"{zT} - {zg}", WOOD)
    c.box("Tampo", xL, yC, zT, W, f"{D} - 0.02", T, WOOD, in_plan=True)
    c.box("Base", xa0, yC, zP, f"{W} - 2*{T}", dK, T, MDF)
    c.box("Fundo", xa0, yK, zP, f"{W} - 2*{T}", 0.006, f"{zT} - {zP}", "Laminado branco")
    c.box("Rodapé frontal", xa0, f"{yC} + 0.03", zg, f"{W} - 2*{T}", T, zP - zg, WOOD)
    c.box("Rodapé traseiro", xa0, f"{yK} - {T}", zg, f"{W} - 2*{T}", T, zP - zg, MDF, detail=FINE)
    for nm, x in (("esquerda", f"{xL} + {T}/2"), ("direita", f"{xR} - {T}/2")):
        for pos, y in (("frontal", f"{yC} + 0.04"), ("traseira", f"{yB} - 0.04")):
            c.cyl(f"Sapata {pos} {nm}", x, y, 0, 0.0085, zg, "Plástico preto", detail=FINE)
        x0 = f"{xL} + 0.06" if nm == "esquerda" else f"{xR} - 0.09"
        c.box(f"Cantoneira antitombamento {nm}", x0, f"{yB} - 0.045", H, 0.03, 0.045, 0.002, STEEL, detail=FINE)
        c.box(f"Cantoneira antitombamento {nm} - aba", x0, f"{yB} - 0.002", f"{H} + 0.002", 0.03, 0.002, 0.04, STEEL, detail=FINE)
    hd = f"{zT} - {zP} - {T}"
    gA.box("Divisória 1", f"{xd1} - {T}/2", yC, f"{zP} + {T}", T, dK, hd, MDF)
    gC.box("Divisória 2", f"{xd2} - {T}/2", yC, f"{zP} + {T}", T, dK, hd, MDF)
    gD.box("Divisória 3", f"{xd3} - {T}/2", yC, f"{zP} + {T}", T, dK, hd, MDF)
    zmf = f"({zM} - {T}/2)"
    for nm, q, x0, w in (("A", gA, xa0, wa), ("B", gB, xb0, wb), ("C", gC, xc0, wc), ("D", gD, xe0, we)):
        q.box(f"Piso do maleiro - vão {nm}", x0, yC, zmf, w, dK, T, MDF)

    # doors: tall ones below the maleiro, short ones in front of it; pairs open from the middle
    z0, z1 = f"({zP} + 0.003)", f"({zM} - 0.0015)"
    m0, m1 = f"({zM} + 0.0015)", f"({H} - 0.002)"
    wd = f"({Wd} - 0.003)"
    for i in range(1, 7):
        g = gd[i]
        side = "left" if i % 2 else "right"
        if side == "left":
            hx = f"({xL} + {i - 1}*{Wd} + 0.0015)"
            xi = xa0 if i == 1 else f"({xL} + {i - 1}*{Wd} + {T}/2)"
        else:
            hx = f"({xL} + {i}*{Wd} - 0.0015)"
            xi = f"({xL} + {i}*{Wd} - {T}/2 - {T}/2*(1 - {clamp(f'{N} - {i}')}))"
        hp = (hx, yF)
        g.door_box(f"Porta {i}", hp, A, 0, wd, -TD, 0, z0, f"{z1} - {z0}", WOOD, side=side, in_plan=True)
        for k, zc in enumerate((at(z0, 0.11), f"({z0} + {z1})/2", at(z1, -0.11)), 1):
            hinge(g, f"Dobradiça {k} da porta {i}", side, hp, xi, zc, A)
        pull(g, f"Puxador da porta {i}", side, hp, f"{wd} - 0.035", f"({z0} + {z1})/2", 0.32, A)
        if i == 2:
            g.door_box("Espelho da porta 2", hp, A, 0.06, f"{wd} - 0.075", 0, 0.004, at(z0, 0.3), f"{z1} - {z0} - 0.45", "Espelho", side=side)
        g.door_box(f"Porta do maleiro {i}", hp, AM, 0, wd, -TD, 0, m0, f"{m1} - {m0}", WOOD, side=side)
        for k, zc in enumerate((at(m0, 0.07), at(m1, -0.07)), 1):
            hinge(g, f"Dobradiça {k} da porta do maleiro {i}", side, hp, xi, zc, AM)
        pull(g, f"Puxador da porta do maleiro {i}", side, hp, f"{wd} - 0.035", at(m0, 0.1), 0.128, AM)
        # swing in plan
        if side == "left":
            pts = [(hx, yF), (hx, f"{yF} - {wd}", wd), (f"{hx} + {wd}", yF)]
        else:
            pts = [(hx, yF), (f"{hx} - {wd}", yF, wd), (hx, f"{yF} - {wd}")]
        g.profile(f"Abertura da porta {i}", "Plan", pts, 0, 0.001, WOOD, detail=ALL)
        c.plan_only(f"Abertura da porta {i}")

    # bay A: long hanging and shoe boxes
    zr = f"({zmf} - 0.065)"
    rail(gA, "Cabideiro do vão A", xa0, xa1, yr, zr)
    sp = f"min(0.085, ({wa} - 0.2)/5)"
    clothes = ((SHIRT, 0.03, BLUE, "Madeira escura"), (DRESS, 0.03, MUST, "Madeira escura"), (SHIRT, 0.03, WHITE, "Plástico preto"),
               (SHIRT, 0.03, GREY, "Madeira escura"), (DRESS, 0.035, DARK, "Plástico preto"))
    for k, (outline, t, mat, hm) in enumerate(clothes):
        garment(gA, f"Roupa {k + 1} no cabideiro A", f"{xa0} + 0.06 + {k}*{sp}", yr, zr, t, outline, mat, hm)
    garment(gA, "Casaco no cabideiro A", f"{xa1} - 0.12", yr, zr, 0.06, COAT, GREY)
    zi = f"({zP} + {T})"
    for k, dx in enumerate((0.02, 0.245), 1):
        gA.box(f"Caixa de sapatos {k}", f"{xa0} + {dx}", f"{yC} + 0.1", zi, 0.2, 0.33, 0.115, "Plástico translúcido", detail=FINE)
        gA.box(f"Caixa de sapatos {k} - tampa", f"{xa0} + {dx - 0.003}", f"{yC} + 0.097", f"{zi} + 0.115", 0.206, 0.336, 0.012, "Plástico translúcido", detail=FINE)

    # bay B: internal drawer bank, then shelves
    zk = f"({zi} + 0.332)"  # underside of the top of the drawer bank
    gB.box("Tampo do gaveteiro", xb0, yC, zk, wb, dK, T, MDF)
    yo0 = f"({yF} + 0.11)"  # front of the drawer boxes, closed
    L = f"({D} - 0.14)"
    for nm, x0 in (("esquerda", f"{xb0} + 0.024"), ("direita", f"{xb1} - 0.042")):
        gB.box(f"Lateral do gaveteiro {nm}", x0, f"{yF} + 0.1", zi, T, f"{yK} - {yF} - 0.1", 0.332, MDF)
    s = 0.055  # the drawers clear the open doors: runners on the drawer bank's own sides
    for j in (1, 2):
        zf = f"({zi} + {0.004 + (j - 1) * 0.164})"
        yo = f"({yo0} - {G})"
        x0, w = f"({xb0} + {s})", f"({wb} - {2 * s})"
        gB.box(f"Frente da gaveta {j}", x0, f"{yo} - 0.015", zf, w, 0.015, 0.156, WOOD)
        gB.box(f"Gaveta {j} - lateral esquerda", x0, yo, f"{zf} + 0.02", 0.012, L, 0.1, MDF)
        gB.box(f"Gaveta {j} - lateral direita", f"{x0} + {w} - 0.012", yo, f"{zf} + 0.02", 0.012, L, 0.1, MDF)
        gB.box(f"Gaveta {j} - traseira", f"{x0} + 0.012", f"{yo} + {L} - 0.012", f"{zf} + 0.03", f"{w} - 0.024", 0.012, 0.09, MDF)
        gB.box(f"Gaveta {j} - fundo", f"{x0} + 0.012", yo, f"{zf} + 0.024", f"{w} - 0.024", f"{L} - 0.012", 0.006, "Laminado branco")
        for nm, xf, xm in (("esquerda", f"{xb0} + 0.042", f"{xb0} + 0.0485"), ("direita", f"{xb1} - 0.0485", f"{xb1} - 0.055")):
            gB.box(f"Corrediça {nm} da gaveta {j} - trilho fixo", xf, yo0, f"{zf} + 0.05", 0.0065, L, 0.04, STEEL, detail=FINE)
            gB.box(f"Corrediça {nm} da gaveta {j} - trilho móvel", xm, f"{yo} + 0.003", f"{zf} + 0.056", 0.0065, f"{L} - 0.006", 0.028, "Cromado", detail=FINE)
        yp = f"{yo} - 0.015"
        gB.cyl_x(f"Puxador da gaveta {j} - barra", f"{yp} - 0.026", f"{zf} + 0.11", f"{xbc} - 0.075", 0.005, 0.15, "Inox escovado")
        for k, dx in enumerate((-0.048, 0.048), 1):
            gB.cyl_y(f"Puxador da gaveta {j} - pino {k}", f"{xbc} + {dx}", f"{zf} + 0.11", f"{yp} - 0.026", 0.004, 0.026, "Inox escovado", detail=FINE)
    zb1 = f"({zk} + {T})"
    hb = f"({zmf} - {zb1})"
    zsB = [f"({zb1} + {hb}*{k}/4 - {T}/2)" for k in (1, 2, 3)]
    for k, z in enumerate(zsB, 1):
        gB.box(f"Prateleira {k} do vão B", xb0, yC, z, wb, dK, T, MDF)
    levels = [zb1] + [f"({z} + {T})" for z in zsB]
    folded = (
        [(0.05, WHITE, 0.0), (0.05, BLUE, 0.01), (0.05, WHITE, 0.005)],  # towels
        [(0.035, GREY, 0.0), (0.035, DARK, 0.01), (0.035, MUST, 0.005)],  # T-shirts
        [(0.045, BLUE, 0.0), (0.045, BLUE, 0.008), (0.045, DARK, 0.004)],  # jeans
        [(0.06, MUST, 0.0), (0.06, GREY, 0.012)],  # sweaters
    )
    for k, (z, items) in enumerate(zip(levels, folded), 1):
        stack(gB, f"Pilha de roupas {k} do vão B", xbc, f"{yC} + 0.07", z, 0.3, 0.32, items)

    # bay C: shelves
    hc = f"({zmf} - {zi})"
    zsC = [f"({zi} + {hc}*{k}/5 - {T}/2)" for k in (1, 2, 3, 4)]
    for k, z in enumerate(zsC, 1):
        gC.box(f"Prateleira {k} do vão C", xc0, yC, z, wc, dK, T, MDF)
    lv = [zi] + [f"({z} + {T})" for z in zsC]
    storage_box(gC, "Caixa organizadora do vão C", f"{xcc} - 0.17", f"{yC} + 0.08", lv[0], 0.34, 0.4, 0.22, DARK)
    stack(gC, "Pilha de toalhas do vão C", xcc, f"{yC} + 0.07", lv[1], 0.32, 0.34, [(0.055, WHITE, 0.0), (0.055, MUST, 0.01), (0.055, WHITE, 0.004)])
    stack(gC, "Pilha de suéteres do vão C", xcc, f"{yC} + 0.07", lv[2], 0.3, 0.32, [(0.06, DARK, 0.0), (0.06, BLUE, 0.01), (0.06, GREY, 0.005)])
    stack(gC, "Pilha de calças do vão C", xcc, f"{yC} + 0.07", lv[3], 0.3, 0.34, [(0.045, DARK, 0.0), (0.045, GREY, 0.008)])
    gC.cyl("Chapeleira do vão C", xcc, f"{yC} + 0.25", lv[4], 0.15, 0.17, MUST, detail=FINE)
    gC.cyl("Chapeleira do vão C - tampa", xcc, f"{yC} + 0.25", f"{lv[4]} + 0.17", 0.153, 0.03, MUST, detail=FINE)

    # bay D: double hanging, shirts above and trousers below
    rail(gD, "Cabideiro superior do vão D", xe0, f"({xe0} + {we})", yr, zr)
    spD = f"min(0.11, ({we} - 0.2)/3)"
    for k, (t, mat, hm) in enumerate(((0.03, WHITE, "Madeira escura"), (0.03, BLUE, "Madeira escura"), (0.03, GREY, "Plástico preto"), (0.035, MUST, "Madeira escura"))):
        garment(gD, f"Camisa {k + 1} no cabideiro D", f"{xe0} + 0.07 + {k}*{spD}", yr, zr, t, SHORT_SHIRT, mat, hm)
    zr2 = f"({zi} + 0.8)"
    rail(gD, "Cabideiro inferior do vão D", xe0, f"({xe0} + {we})", yr, zr2)
    spT = f"min(0.13, ({we} - 0.2)/2)"
    for k, mat in enumerate((DARK, BLUE, GREY)):
        trousers(gD, f"Calça {k + 1} no cabideiro D", f"{xe0} + 0.08 + {k}*{spT}", yr, zr2, mat)

    # maleiro: a suitcase, bedding, pillows and a box
    zm = f"({zmf} + {T})"
    ys0 = f"({yC} + 0.04)"
    sx0, sx1 = f"({xa0} + 0.04)", f"({xa0} + 0.4)"
    gA.profile("Mala", "Plan", rrect(sx0, ys0, sx1, f"{ys0} + 0.48", 0.045), zm, 0.24, "Plástico azul", detail=FINE)
    gA.profile("Mala - zíper", "Plan", rrect(f"{sx0} - 0.002", f"{ys0} - 0.002", f"{sx1} + 0.002", f"{ys0} + 0.482", 0.047), f"{zm} + 0.115", 0.01, "Plástico preto", detail=FINE)
    gA.box("Mala - alça", f"({sx0} + {sx1})/2 - 0.06", f"{ys0} - 0.022", f"{zm} + 0.09", 0.12, 0.022, 0.06, "Plástico preto", detail=FINE)
    stack(gB, "Edredons no maleiro", xbc, f"{yC} + 0.05", zm, 0.38, 0.42, [(0.13, WHITE, 0.0), (0.11, GREY, 0.015)])
    stack(gC, "Travesseiros no maleiro", xcc, f"{yC} + 0.05", zm, 0.38, 0.5, [(0.12, WHITE, 0.0), (0.11, WHITE, 0.01)])
    storage_box(gD, "Caixa organizadora do maleiro", f"{xec} - 0.25", f"{yC} + 0.06", zm, 0.5, 0.42, 0.28, GREY)

    desc = "Guarda-roupa de portas de abrir com maleiro, cabideiros, prateleiras e gaveteiro interno"
    c.type("Guarda-roupa 2 portas 100 cm", desc, Largura=1.0, Portas=2)
    c.type("Guarda-roupa 3 portas 150 cm", desc, Largura=1.5, Portas=3)
    c.type("Guarda-roupa 4 portas 200 cm", desc, Largura=2.0, Portas=4)
    c.type("Guarda-roupa 6 portas 270 cm", desc, Largura=2.7, Portas=6)
    return c
