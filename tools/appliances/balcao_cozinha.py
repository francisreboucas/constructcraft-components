"""Balcão de cozinha: base cabinet of one to three modules, each a door under a drawer, with a granite top."""

from kit import *

EPS = 0.001  # scale of a collapsed group: its pieces shrink into a point hidden inside a panel


class Grp:
    """Pieces scaled by `k` about the point `h`.

    k = 1 leaves the pieces as they are; k = EPS shrinks them into `h`, which
    lies inside a solid panel: that is how the parts of a door or a module
    that a narrower type does not have disappear (a piece cannot have zero size).
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

    def rev(self, name, plane, pts, offset, axis, mat, **kw):
        fu, fv, fo = {"Plan": (self.x, self.y, self.z), "Front": (self.x, self.z, self.y), "Side": (self.y, self.z, self.x)}[plane]
        out = [(fu(q[0]), fv(q[1])) + ((self.l(q[2]),) if len(q) > 2 and q[2] not in (None, "", 0) else ()) for q in pts]
        self.c.rev(name, plane, out, fo(offset), fu(axis), mat, **kw)


def hinge(g, name, side, hx, hy, xi, zc, A, steel="Aço galvanizado"):
    """A cup hinge: the cup on the door (swings), the arm and its plate on the panel.

    `hx`, `hy`: the door's hinge axis; `xi`: inner face of the panel that carries
    the hinge; `zc`: height of its center.
    """
    s = 1 if side == "left" else -1
    g.door_box(f"{name} - caneca", (hx, hy), A, 0.005, 0.04, -0.003, 0, f"{zc} - 0.025", 0.05, steel, side=side, detail=FINE)
    x0 = xi if s > 0 else f"{xi} - 0.012"
    g.box(f"{name} - braço", x0, f"{hy} + 0.0035", f"{zc} - 0.01", 0.012, 0.055, 0.02, steel, detail=FINE)
    x0 = xi if s > 0 else f"{xi} - 0.004"
    g.box(f"{name} - calço", x0, f"{hy} + 0.022", f"{zc} - 0.0225", 0.004, 0.05, 0.045, steel, detail=FINE)


def pull(g, name, side, hx, hy, a, zc, length, A, td=0.018, mat="Inox escovado"):
    """A vertical bar pull on a door: a round bar on two posts, centered at `zc`."""
    g.door_cyl(f"{name} - barra", (hx, hy), A, a, td + 0.026, f"{zc} - {p(length)}/2", 0.005, length, mat, side=side)
    for i, dz in enumerate((f"- {p(length)}/2 + 0.02", f"+ {p(length)}/2 - 0.028"), 1):
        g.door_box(f"{name} - pino {i}", (hx, hy), A, f"{p(a)} - 0.004", f"{p(a)} + 0.004", td, td + 0.026, f"{zc} {dz}", 0.008, mat, side=side, detail=FINE)


def pot(g, name, x, y, z, r, h, mat="Inox escovado", lid=True):
    """A cooking pot with two side handles and a lid."""
    g.rev(name, "Front", [(x, z), (f"{x} + {e(r)}", z), (f"{x} + {e(r)}", f"{z} + {e(h)}"), (f"{x} + {e(r - 0.003)}", f"{z} + {e(h)}"), (f"{x} + {e(r - 0.003)}", f"{z} + 0.004"), (x, f"{z} + 0.004")], y, x, mat, detail=FINE)
    for nm, x0 in (("esquerda", f"{x} - {e(r + 0.025)}"), ("direita", f"{x} + {e(r)}")):
        g.box(f"{name} - alça {nm}", x0, f"{y} - 0.02", f"{z} + {e(h - 0.025)}", 0.025, 0.04, 0.008, "Plástico preto", detail=FINE)
    if lid:
        zl = f"{z} + {e(h)}"
        g.rev(f"{name} - tampa", "Front", [(x, zl), (f"{x} + {e(r + 0.003)}", zl), (f"{x} + {e(r + 0.003)}", f"{zl} + 0.004"), (f"{x} + {e(r * 0.5)}", f"{zl} + 0.02"), (x, f"{zl} + 0.024")], y, x, "Vidro temperado", detail=FINE)
        g.cyl(f"{name} - pegador da tampa", x, y, f"{zl} + 0.024", 0.015, 0.02, "Plástico preto", detail=FINE)


def build():
    c = Component("Balcão de cozinha", "casework", "balcao-cozinha", "Casework")
    W = c.param("Largura", 0.8)
    D = c.param("Profundidade", 0.6)
    H = c.param("Altura", 0.9)
    A = c.angle("AnguloPortas", 0, open_at=95)
    G = c.param("AberturaGavetas", 0, "Length", True)
    c.open_pose["AberturaGavetas"] = 0.3
    c.material("MDF branco", (240, 240, 235), "Wood", "Satin")
    c.material("Granito", (70, 70, 75), "Generic", "Polished")
    MDF, STEEL, HDF = "MDF branco", "Aço galvanizado", "Laminado branco"

    T, TD = 0.018, 0.018
    xL, xR = f"(-{W}/2)", f"({W}/2)"
    yF, yB = f"(-{D}/2)", f"({D}/2)"
    yD = f"({yF} + {TD})"  # back face of the fronts
    yC = f"({yF} + 0.02)"  # front edge of the carcass
    zP = 0.1  # top of the plinth
    zC = f"({H} - 0.03)"  # top of the carcass, under the stone
    zd1 = f"({H} - 0.053)"  # top of the drawer fronts, under the top's apron
    zd0 = f"({H} - 0.193)"  # bottom of the drawer fronts
    zf0 = f"{zP} + 0.002"  # bottom of the doors
    zf1 = f"({zd0} - 0.003)"  # top of the doors

    N = f"ceil({W}/0.45 - 0.01)"  # modules: 1 up to 45 cm, 2 up to 90 cm, 3 above
    Wd = f"({W}/{N})"
    K = {i: f"min(1, max(0, {N} - {i - 1}))" for i in (1, 2, 3)}
    K[4] = "0"
    hide = (f"{xR} - {T}/2", 0, 0.5)  # inside the right side
    grp = {1: Grp(c)}
    for i in (2, 3):
        grp[i] = Grp(c, f"min(1, max({EPS}, {N} - {i - 1}))", hide)

    # coarse stand-ins: the three volumes
    c.box("Rodapé", xL, f"{yF} + 0.05", 0, W, f"{D} - 0.05", 0.1, "Alumínio anodizado", detail=COARSE)
    c.box("Gabinete", xL, yF, 0.1, W, D, f"{H} - 0.13", MDF, detail=COARSE, in_plan=True)
    c.box("Tampo", xL, f"{yF} - 0.02", f"{H} - 0.03", W, f"{D} + 0.02", 0.03, "Granito", detail=COARSE, in_plan=True)

    # carcass: the sides reach the floor, notched at the toe kick
    side = [(f"{yF} + 0.05", 0), (yB, 0), (yB, zC), (yC, zC), (yC, zP), (f"{yF} + 0.05", zP)]
    c.profile("Lateral esquerda", "Side", side, xL, T, MDF)
    c.profile("Lateral direita", "Side", side, f"{xR} - {T}", T, MDF)
    c.box("Base", f"{xL} + {T}", yC, zP, f"{W} - 2*{T}", f"{D} - 0.02 - 0.015", T, MDF)
    c.box("Fundo", f"{xL} + {T}", f"{yB} - 0.018", zP, f"{W} - 2*{T}", 0.003, f"{zC} - {zP}", HDF)
    c.box("Travessa superior frontal", f"{xL} + {T}", yC, f"{zC} - {T}", f"{W} - 2*{T}", 0.08, T, MDF)
    c.box("Travessa superior traseira", f"{xL} + {T}", f"{yB} - 0.098", f"{zC} - {T}", f"{W} - 2*{T}", 0.08, T, MDF)

    # plinth: toe kick and leveling feet
    c.box("Rodapé frontal", f"{xL} + {T}", f"{yF} + 0.052", 0.003, f"{W} - 2*{T}", 0.012, 0.097, "Alumínio anodizado")
    c.box("Rodapé frontal - vedação", f"{xL} + {T}", f"{yF} + 0.054", 0, f"{W} - 2*{T}", 0.004, 0.003, "Borracha", detail=FINE)
    feet = [("frontal esquerdo", Grp(c), f"{xL} + {T} + 0.05", f"{yF} + 0.12"), ("frontal direito", Grp(c), f"{xR} - {T} - 0.05", f"{yF} + 0.12"),
            ("traseiro esquerdo", Grp(c), f"{xL} + {T} + 0.05", f"{yB} - 0.08"), ("traseiro direito", Grp(c), f"{xR} - {T} - 0.05", f"{yB} - 0.08"),
            ("frontal central", grp[2], 0, f"{yF} + 0.12"), ("traseiro central", grp[2], 0, f"{yB} - 0.08")]
    for nm, q, x, y in feet:
        q.cyl(f"Pé regulável {nm} - sapata", x, y, 0, 0.028, 0.01, "Plástico preto", detail=FINE)
        q.cyl(f"Pé regulável {nm} - haste", x, y, 0.01, 0.012, 0.035, "Plástico preto", detail=FINE)
        q.cyl(f"Pé regulável {nm} - corpo", x, y, 0.045, 0.02, 0.055, "Plástico preto", detail=FINE)

    # stone top with a doubled front edge
    c.box("Tampo de granito", xL, f"{yF} - 0.02", f"{H} - 0.03", W, f"{D} + 0.02", 0.03, "Granito", in_plan=True)
    c.box("Testeira do tampo", xL, f"{yF} - 0.02", f"{H} - 0.05", W, 0.02, 0.0195, "Granito")

    for i in (1, 2, 3):
        g = grp[i]
        m = f"módulo {i}"
        xm = f"({xL} + {i - 1}*{Wd})"  # left end of the module
        last = f"(1 - {K[i + 1]})"  # 1 when the module is the last one
        xi0 = f"({xm} + {T})" if i == 1 else f"({xm} + {T}/2)"
        xi1 = f"({xm} + {Wd} - {T}/2 - {T}/2*{last})"
        wi = f"({xi1} - {xi0})"
        if i > 1:
            g.box(f"Divisória {i - 1}", f"{xm} - {T}/2", f"{yC} + 0.001", f"{zP} + {T}", T, f"{D} - 0.04", f"{zC} - {zP} - 2*{T}", MDF)

        # rail between the drawer and the door, shelf on pins
        g.box(f"Travessa da gaveta - {m}", xi0, yC, f"{zd0} - 0.0015 - {T}/2", wi, 0.06, T, MDF)
        zs = f"({zP} + {T} + ({zf1} - {zP} - {T})*0.5)"
        ys, ds = f"({yC} + 0.05)", f"({D} - 0.02 - 0.05 - 0.0185)"
        g.box(f"Prateleira - {m}", f"{xi0} + 0.001", ys, zs, f"{wi} - 0.002", ds, T, MDF)
        for j, yp in enumerate((f"{ys} + 0.05", f"{ys} + {ds} - 0.05"), 1):
            g.cyl_x(f"Pino da prateleira esquerdo {j} - {m}", yp, f"{zs} - 0.0025", xi0, 0.0025, 0.009, STEEL, detail=FINE)
            g.cyl_x(f"Pino da prateleira direito {j} - {m}", yp, f"{zs} - 0.0025", f"{xi1} - 0.009", 0.0025, 0.009, STEEL, detail=FINE)

        # door
        sd = "left" if i == 1 else "right"
        hx = f"({xm} + 0.0015)" if i == 1 else f"({xm} + {Wd} - 0.0015)"
        xi = xi0 if i == 1 else xi1
        wd = f"({Wd} - 0.003)"
        g.door_box(f"Porta - {m}", (hx, yD), A, 0, wd, 0, TD, zf0, f"{zf1} - {zP} - 0.002", MDF, side=sd, in_plan=True)
        hinge(g, f"Dobradiça superior - {m}", sd, hx, yD, xi, f"{zf1} - 0.09", A)
        hinge(g, f"Dobradiça inferior - {m}", sd, hx, yD, xi, f"{zP} + 0.1", A)
        pull(g, f"Puxador da porta - {m}", sd, hx, yD, f"{wd} - 0.035", f"{zf1} - 0.12", 0.16, A)
        g.door_box(f"Batente da porta - {m}", (hx, yD), A, f"{wd} - 0.03", f"{wd} - 0.022", -0.0018, 0, f"{zP} + 0.005", 0.008, "Plástico translúcido", side=sd, detail=FINE)

        # drawer: front, box and full-extension slides
        yo = f"({yD} - {G})"  # back face of the drawer front, moving
        xb, wb = f"({xi0} + 0.0135)", f"({wi} - 0.027)"
        zb = f"({zd0} + 0.022)"
        L = 0.45
        g.box(f"Frente da gaveta - {m}", f"{xm} + 0.0015", f"{yo} - {TD}", zd0, wd, TD, 0.14, MDF, in_plan=True)
        g.box(f"Gaveta - lateral esquerda - {m}", xb, yo, zb, 0.015, L, 0.095, MDF)
        g.box(f"Gaveta - lateral direita - {m}", f"{xb} + {wb} - 0.015", yo, zb, 0.015, L, 0.095, MDF)
        g.box(f"Gaveta - traseira - {m}", f"{xb} + 0.015", f"{yo} + {L} - 0.015", f"{zb} + 0.012", f"{wb} - 0.03", 0.015, 0.075, MDF)
        g.box(f"Gaveta - fundo - {m}", f"{xb} + 0.015", yo, f"{zb} + 0.008", f"{wb} - 0.03", L - 0.015, 0.004, HDF)
        for nm, x0, x1 in (("esquerda", xi0, f"{xi0} + 0.0065"), ("direita", f"{xi1} - 0.0065", f"{xi1} - 0.013")):
            g.box(f"Corrediça {nm} - trilho fixo - {m}", x0, f"{yC} + 0.003", f"{zb} + 0.025", 0.0065, L, 0.04, STEEL, detail=FINE)
            g.box(f"Corrediça {nm} - trilho móvel - {m}", x1, f"{yo} + 0.003", f"{zb} + 0.031", 0.0065, L - 0.005, 0.028, "Cromado", detail=FINE)
        xh = f"({xm} + {Wd}/2)"
        g.cyl_x(f"Puxador da gaveta - barra - {m}", f"{yo} - {TD} - 0.026", f"{zd0} + 0.07", f"{xh} - 0.08", 0.005, 0.16, "Inox escovado")
        for j, dx in enumerate((-0.06, 0.06), 1):
            g.cyl_y(f"Puxador da gaveta - pino {j} - {m}", f"{xh} + {dx}", f"{zd0} + 0.07", f"{yo} - {TD} - 0.026", 0.004, 0.026, "Inox escovado", detail=FINE)

    # what is kept inside
    g = grp[1]
    xm1 = f"({xL} + {T})"
    wi1 = f"({Wd} - {T} - {T}/2 - {T}/2*(1 - {K[2]}))"
    xc = f"({xm1} + {wi1}/2)"
    zi = f"({zP} + {T})"
    zs1 = f"({zP} + {T} + ({zf1} - {zP} - {T})*0.5 + {T})"
    pot(g, "Panela grande", xc, 0.03, zi, 0.105, 0.14)
    pot(g, "Caçarola", xc, 0.04, zs1, 0.09, 0.085)
    # cutlery tray in the first drawer
    yo = f"({yD} - {G})"
    xt, wt = f"({xm1} + 0.0135 + 0.015 + 0.006)", f"({wi1} - 0.027 - 0.03 - 0.012)"
    zt = f"({zd0} + 0.022 + 0.012)"
    c.box("Porta-talheres - fundo", xt, f"{yo} + 0.03", zt, wt, 0.3, 0.003, "Plástico cinza claro", detail=FINE)
    c.box("Porta-talheres - borda frontal", xt, f"{yo} + 0.03", f"{zt} + 0.003", wt, 0.004, 0.04, "Plástico cinza claro", detail=FINE)
    c.box("Porta-talheres - borda traseira", xt, f"{yo} + 0.326", f"{zt} + 0.003", wt, 0.004, 0.04, "Plástico cinza claro", detail=FINE)
    for j in range(5):
        c.box(f"Porta-talheres - divisória {j + 1}", f"{xt} + ({wt} - 0.004)*{j}/4", f"{yo} + 0.034", f"{zt} + 0.003", 0.004, 0.292, 0.04, "Plástico cinza claro", detail=FINE)
    for j, (nm, ln, wd_) in enumerate((("Garfos", 0.19, 0.022), ("Facas", 0.22, 0.016), ("Colheres", 0.18, 0.03), ("Colheres de chá", 0.13, 0.022))):
        for n in (1, 2):
            c.box(f"{nm} {n}", f"{xt} + ({wt} - 0.004)*{j + 0.5}/4 + 0.002 - {wd_ / 2} + {0.006 * (n - 1.5)}", f"{yo} + 0.05 + {0.012 * n}", f"{zt} + {0.003 + 0.004 * (n - 1)}", wd_, ln, 0.003, "Inox escovado", detail=FINE)
    # module 2: bowls; module 3: cleaning bottles
    g = grp[2]
    x2 = f"({xL} + 1.5*{Wd})"
    g.rev("Escorredor de massa", "Front", [(x2, zi), (f"{x2} + 0.06", zi), (f"{x2} + 0.07", f"{zi} + 0.02"), (f"{x2} + 0.115", f"{zi} + 0.11"), (f"{x2} + 0.11", f"{zi} + 0.11"), (f"{x2} + 0.066", f"{zi} + 0.024"), (x2, f"{zi} + 0.024")], 0.03, x2, "Inox escovado", detail=FINE)
    g.rev("Frigideira", "Front", [(x2, zs1), (f"{x2} + 0.1", zs1), (f"{x2} + 0.115", f"{zs1} + 0.045"), (f"{x2} + 0.111", f"{zs1} + 0.045"), (f"{x2} + 0.097", f"{zs1} + 0.004"), (x2, f"{zs1} + 0.004")], 0.06, x2, "Ferro fundido", detail=FINE)
    g.box("Frigideira - cabo", f"{x2} - 0.012", -0.2, f"{zs1} + 0.03", 0.024, 0.15, 0.012, "Plástico preto", detail=FINE)
    g = grp[3]
    x3 = f"({xL} + 2.5*{Wd})"
    for j, (dx, dy, r, h, mat) in enumerate(((-0.08, 0.05, 0.04, 0.2, "Plástico azul"), (0.02, 0.07, 0.035, 0.24, "Plástico verde"), (0.09, -0.02, 0.045, 0.17, "Branco")), 1):
        g.cyl(f"Frasco de limpeza {j}", f"{x3} + {dx}", dy, zi, r, h, mat, detail=FINE)
        g.cyl(f"Frasco de limpeza {j} - tampa", f"{x3} + {dx}", dy, f"{zi} + {h}", r * 0.45, 0.035, "Plástico vermelho", detail=FINE)
    g.box("Balde", f"{x3} - 0.1", -0.02, zs1, 0.2, 0.2, 0.004, "Plástico cinza", detail=FINE)
    g.rev("Balde - corpo", "Front", [(x3, f"{zs1} + 0.004"), (f"{x3} + 0.085", f"{zs1} + 0.004"), (f"{x3} + 0.105", f"{zs1} + 0.2"), (f"{x3} + 0.1", f"{zs1} + 0.2"), (f"{x3} + 0.082", f"{zs1} + 0.008"), (x3, f"{zs1} + 0.008")], 0.08, x3, "Plástico azul", detail=FINE)

    c.type("Balcão 40 cm", "Balcão inferior com tampo de granito", Largura=0.4)
    c.type("Balcão 60 cm", "Balcão inferior com tampo de granito", Largura=0.6)
    c.type("Balcão 80 cm", "Balcão inferior com tampo de granito", Largura=0.8)
    c.type("Balcão 120 cm", "Balcão inferior com tampo de granito", Largura=1.2)
    return c
