"""Armário aéreo: wall cabinet with two or three doors, shelves, hanging rail and light strip."""

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


def plate_stack(g, name, x, y, z, r, n, mat="Louça", step=0.011):
    """A stack of `n` plates of radius `r` standing at z."""
    pts = [(x, z)]
    for i in range(n):
        z0 = f"{z} + {e(i * step)}"
        pts += [(f"{x} + {e(r * 0.55)}", z0), (f"{x} + {e(r)}", f"{z0} + {e(step * 0.75)}"), (f"{x} + {e(r * 0.62)}", f"{z0} + {e(step * 0.95)}")]
    pts.append((x, f"{z} + {e(n * step)}"))
    g.rev(name, "Front", pts, y, x, mat, detail=FINE)


def bowl_stack(g, name, x, y, z, r, n, mat="Louça", step=0.018, h=0.06):
    """A stack of `n` nested bowls of rim radius `r`."""
    pts = [(x, z), (f"{x} + {e(r * 0.45)}", z)]
    for i in range(n):
        z1 = f"{z} + {e(h + i * step)}"
        pts += [(f"{x} + {e(r)}", z1), (f"{x} + {e(r * 0.93)}", z1)]
    pts.append((x, f"{z} + {e(h * 0.5 + (n - 1) * step)}"))
    g.rev(name, "Front", pts, y, x, mat, detail=FINE)


def build():
    c = Component("Armário aéreo", "casework", "armario-aereo", "Casework")
    W = c.param("Largura", 0.8)
    D = c.param("Profundidade", 0.35)
    H = c.param("Altura", 0.7)
    E = c.param("Elevacao", 1.5, "Length", True)
    A = c.angle("AnguloPortas", 0, open_at=95)
    c.material("MDF branco", (240, 240, 235), "Wood", "Satin")
    c.material("Fita de LED", (255, 244, 214), "Plastic", "Glossy", 0.3)
    MDF, STEEL = "MDF branco", "Aço galvanizado"

    T, TD = 0.018, 0.018
    xL, xR = f"(-{W}/2)", f"({W}/2)"
    yF, yB = f"(-{D}/2)", f"({D}/2)"
    yD = f"({yF} + {TD})"  # back face of the doors
    yC = f"({yF} + 0.02)"  # front edge of the carcass
    zT = f"({E} + {H})"
    zb = f"({E} + 0.02)"  # bottom panel: raised, the doors and sides hide the light strip under it
    zi = f"({zb} + {T})"  # inside floor

    N = f"ceil({W}/0.45 - 0.01)"  # doors: 2 up to 90 cm, 3 above
    K3 = f"min(1, max(0, {N} - 2))"  # 1 with a third door
    k3 = f"min(1, max({EPS}, {N} - 2))"
    Wd = f"({W}/{N})"
    xd = f"({xL} + 2*{Wd})"  # right end of the pair of doors: the partition, or the right side
    xa1 = f"({xd} - {T} + {T}/2*{K3})"  # inner face of the panel right of bay A
    wa = f"({xa1} - {xL} - {T})"

    g = Grp(c)
    b = Grp(c, k3, (f"{xR} - {T}/2", 0, f"{E} + {H}/2"))  # the third door and its bay

    # coarse stand-in
    c.box("Corpo", xL, yF, E, W, D, H, MDF, detail=COARSE, in_plan=True)

    # carcass
    c.box("Lateral esquerda", xL, yC, E, T, f"{D} - 0.02", H, MDF, in_plan=True)
    c.box("Lateral direita", f"{xR} - {T}", yC, E, T, f"{D} - 0.02", H, MDF, in_plan=True)
    c.box("Tampo superior", f"{xL} + {T}", yC, f"{zT} - {T}", f"{W} - 2*{T}", f"{D} - 0.035", T, MDF, in_plan=True)
    c.box("Base", f"{xL} + {T}", yC, zb, f"{W} - 2*{T}", f"{D} - 0.035", T, MDF)
    c.box("Fundo", f"{xL} + {T}", f"{yB} - 0.018", zb, f"{W} - 2*{T}", 0.003, f"{H} - 0.02", "Laminado branco")
    b.box("Divisória", f"{xd} - {T}/2", f"{yC} + 0.002", zi, T, f"{D} - 0.04", f"{H} - 0.02 - 2*{T}", MDF)
    c.box("Fita de borda da base", f"{xL} + {T}", f"{yC} - 0.0005", zb, f"{W} - 2*{T}", 0.0005, T, "Laminado branco", detail=FINE)

    # hanging rail and suspension brackets
    c.box("Trilho de fixação", f"{xL} + 0.03", f"{yB} - 0.006", f"{zT} - 0.075", f"{W} - 0.06", 0.006, 0.035, STEEL)
    c.box("Trilho de fixação - aba", f"{xL} + 0.03", f"{yB} - 0.012", f"{zT} - 0.046", f"{W} - 0.06", 0.006, 0.006, STEEL, detail=FINE)
    for nm, x0 in (("esquerdo", f"{xL} + {T}"), ("direito", f"{xR} - {T} - 0.045")):
        c.box(f"Suporte de suspensão {nm}", x0, f"{yB} - 0.04", f"{zT} - {T} - 0.06", 0.045, 0.022, 0.06, "Plástico cinza claro")
        c.cyl_y(f"Suporte de suspensão {nm} - parafuso de regulagem", f"{x0} + 0.0225", f"{zT} - {T} - 0.02", f"{yB} - 0.042", 0.004, 0.002, STEEL, detail=FINE)
        c.cyl_y(f"Suporte de suspensão {nm} - parafuso de aperto", f"{x0} + 0.0225", f"{zT} - {T} - 0.042", f"{yB} - 0.042", 0.004, 0.002, STEEL, detail=FINE)

    # light strip under the bottom panel
    yl = f"({yC} + 0.03)"
    c.box("Perfil da fita de LED", f"{xL} + {T} + 0.02", yl, f"{zb} - 0.008", f"{W} - 2*{T} - 0.04", 0.018, 0.008, "Alumínio anodizado")
    c.box("Difusor da fita de LED", f"{xL} + {T} + 0.022", f"{yl} + 0.002", f"{zb} - 0.0095", f"{W} - 2*{T} - 0.044", 0.014, 0.0015, "Fita de LED")
    c.box("Fonte da fita de LED", f"{xR} - {T} - 0.14", f"{yB} - 0.075", f"{zb} - 0.018", 0.11, 0.04, 0.018, "Plástico preto", detail=FINE)
    c.box("Cabo da fita de LED", f"{xR} - {T} - 0.09", f"{yl} + 0.018", f"{zb} - 0.005", 0.004, f"{D} - 0.143", 0.004, "Plástico preto", detail=FINE)

    # shelves: two in bay A, two in bay B
    ys, ds = f"({yC} + 0.02)", f"({D} - 0.02 - 0.02 - 0.0185)"
    hi = f"({H} - 0.02 - 2*{T})"  # inside height
    zs = [f"({zi} + {hi}*{f} - {T}/2)" for f in (0.345, 0.68)]
    wb = f"max(0.02, {xR} - {T} - {xd} - {T}/2)"
    xb0 = f"({xd} + {T}/2)"
    for i, z in enumerate(zs, 1):
        c.box(f"Prateleira {i}", f"{xL} + {T} + 0.001", ys, z, f"{wa} - 0.002", ds, T, MDF)
        b.box(f"Prateleira {i + 2}", f"{xb0} + 0.001", ys, z, f"{wb} - 0.002", ds, T, MDF)
        for j, yp in enumerate((f"{ys} + 0.04", f"{ys} + {ds} - 0.04"), 1):
            c.cyl_x(f"Pino da prateleira {i} - esquerdo {j}", yp, f"{z} - 0.0025", f"{xL} + {T}", 0.0025, 0.009, STEEL, detail=FINE)
            c.cyl_x(f"Pino da prateleira {i} - direito {j}", yp, f"{z} - 0.0025", f"{xa1} - 0.009", 0.0025, 0.009, STEEL, detail=FINE)
            b.cyl_x(f"Pino da prateleira {i + 2} - esquerdo {j}", yp, f"{z} - 0.0025", xb0, 0.0025, 0.009, STEEL, detail=FINE)
            b.cyl_x(f"Pino da prateleira {i + 2} - direito {j}", yp, f"{z} - 0.0025", f"{xb0} + {wb} - 0.009", 0.0025, 0.009, STEEL, detail=FINE)

    # doors
    dz, dh = f"({E} + 0.0015)", f"({H} - 0.003)"
    wd = f"({Wd} - 0.003)"
    doors = [
        (1, g, "left", f"({xL} + 0.0015)", f"({xL} + {T})"),
        (2, g, "right", f"({xd} - 0.0015)", xa1),
        (3, b, "right", f"({xR} - 0.0015)", f"({xR} - {T})"),
    ]
    for i, q, side, hx, xi in doors:
        q.door_box(f"Porta {i}", (hx, yD), A, 0, wd, 0, TD, dz, dh, MDF, side=side, in_plan=True)
        hinge(q, f"Dobradiça superior da porta {i}", side, hx, yD, xi, f"{zT} - 0.1", A)
        hinge(q, f"Dobradiça inferior da porta {i}", side, hx, yD, xi, f"{E} + 0.12", A)
        pull(q, f"Puxador da porta {i}", side, hx, yD, f"{wd} - 0.035", f"{E} + 0.13", 0.16, A)
        for nm, z in (("inferior", f"{zb} + 0.005"), ("superior", f"{zT} - 0.013")):
            q.door_box(f"Batente {nm} da porta {i}", (hx, yD), A, f"{wd} - 0.03", f"{wd} - 0.022", -0.0018, 0, z, 0.008, "Plástico translúcido", side=side, detail=FINE)

    # what is kept inside
    x0 = f"({xL} + {T})"
    plate_stack(g, "Pilha de pratos rasos", f"{x0} + 0.14", 0.02, zi, 0.125, 8)
    plate_stack(g, "Pilha de pratos de sobremesa", f"{x0} + 0.39", 0.03, zi, 0.095, 6)
    z1 = f"({zs[0]} + {T})"
    bowl_stack(g, "Pilha de tigelas", f"{x0} + 0.12", 0.03, z1, 0.08, 4)
    for i, (dx, dy) in enumerate(((0.26, 0.06), (0.335, 0.06), (0.41, 0.06), (0.26, -0.015), (0.335, -0.015), (0.41, -0.015)), 1):
        c.rev(f"Copo {i}", "Front", [(f"{x0} + {dx}", z1), (f"{x0} + {dx} + 0.026", z1), (f"{x0} + {dx} + 0.032", f"{z1} + 0.12"), (f"{x0} + {dx}", f"{z1} + 0.12")], dy, f"{x0} + {dx}", "Vidro", detail=FINE)
    z2 = f"({zs[1]} + {T})"
    for i, (dx, r, h, lid) in enumerate(((0.09, 0.05, 0.15, "Inox escovado"), (0.205, 0.05, 0.12, "Inox escovado"), (0.31, 0.042, 0.1, "Inox escovado")), 1):
        c.cyl(f"Pote de mantimentos {i}", f"{x0} + {dx}", 0.04, z2, r, h, "Vidro", detail=FINE)
        c.cyl(f"Pote de mantimentos {i} - conteúdo", f"{x0} + {dx}", 0.04, f"{z2} + 0.004", r - 0.004, h * 0.7, "Mica", detail=FINE)
        c.cyl(f"Pote de mantimentos {i} - tampa", f"{x0} + {dx}", 0.04, f"{z2} + {h}", r + 0.002, 0.014, lid, detail=FINE)
    for i, dx in enumerate((0.42, 0.5), 1):
        c.rev(f"Caneca {i}", "Front", [(f"{x0} + {dx}", z2), (f"{x0} + {dx} + 0.036", z2), (f"{x0} + {dx} + 0.04", f"{z2} + 0.095"), (f"{x0} + {dx} + 0.035", f"{z2} + 0.095"), (f"{x0} + {dx} + 0.033", f"{z2} + 0.008"), (f"{x0} + {dx}", f"{z2} + 0.008")], 0.03, f"{x0} + {dx}", "Louça", detail=FINE)
    # bay B
    bowl_stack(b, "Pilha de saladeiras", f"{xb0} + {wb}/2", 0.03, zi, 0.115, 3, step=0.022, h=0.09)
    plate_stack(b, "Pilha de pratos fundos", f"{xb0} + {wb}/2", 0.03, z1, 0.11, 6, step=0.014)
    for i, dx in enumerate((-0.085, 0.03), 1):
        b.cyl(f"Garrafa {i}", f"{xb0} + {wb}/2 + {dx}", 0.05, z2, 0.036, 0.125, "Vidro fumê", detail=FINE)
        b.cyl(f"Garrafa {i} - gargalo", f"{xb0} + {wb}/2 + {dx}", 0.05, f"{z2} + 0.125", 0.014, 0.045, "Vidro fumê", detail=FINE)

    c.preview_base = 1.5  # make.py aims its cameras at the cabinet, not at the floor
    c.type("Aéreo 60 cm", "Armário suspenso de cozinha", Largura=0.6)
    c.type("Aéreo 80 cm", "Armário suspenso de cozinha", Largura=0.8)
    c.type("Aéreo 120 cm", "Armário suspenso de cozinha", Largura=1.2)
    return c
