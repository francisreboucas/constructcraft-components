"""Estante: open bookshelf with five shelves, books of several sizes and a few objects."""

import math
import random

from kit import *

EPS = 0.005  # scale of a collapsed group: its pieces shrink into a point hidden inside a panel


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


COVERS = {
    "Capa de livro vermelha": (152, 44, 40),
    "Capa de livro azul": (44, 72, 128),
    "Capa de livro verde": (52, 100, 72),
    "Capa de livro mostarda": (200, 158, 62),
    "Capa de livro preta": (38, 38, 42),
    "Capa de livro creme": (224, 214, 190),
    "Capa de livro laranja": (204, 106, 52),
    "Capa de livro vinho": (104, 34, 52),
    "Capa de livro turquesa": (62, 140, 148),
    "Capa de livro cinza": (122, 126, 132),
}


def off(base, d):
    """`base` moved by the number `d`."""
    return f"{base} + {e(d)}" if d >= 0 else f"{base} - {e(-d)}"


def book(g, name, x, y, z, t, d, h, mat, lying=False):
    """A book: the cover (two boards and the spine, towards the front) and the block of pages.

    Standing: thickness `t` along x, height `h`. Lying: `h` along x, thickness up.
    """
    c = 0.002 if t < 0.02 else 0.003
    if lying:
        pts = [(y, z), (off(y, d), z), (off(y, d), off(z, c)), (off(y, c), off(z, c)), (off(y, c), off(z, t - c)), (off(y, d), off(z, t - c)), (off(y, d), off(z, t)), (y, off(z, t))]
        g.profile(name, "Side", pts, x, h, mat)
        g.box(f"{name} - miolo", off(x, 0.003), off(y, c), off(z, c), h - 0.006, d - c - 0.004, t - 2 * c, "Papel", detail=FINE)
    else:
        x1 = off(x, t)
        pts = [(x, y), (x1, y), (x1, off(y, d)), (off(x, t - c), off(y, d)), (off(x, t - c), off(y, c)), (off(x, c), off(y, c)), (off(x, c), off(y, d)), (x, off(y, d))]
        g.profile(name, "Plan", pts, z, h, mat)
        g.box(f"{name} - miolo", off(x, c), off(y, c), off(z, 0.003), t - 2 * c, d - c - 0.004, h - 0.006, "Papel", detail=FINE)


def leaning(g, name, x, y, z, t, d, h, mat, sign, a=14):
    """A book leaning on its neighbour: `x` is the neighbour's face, `sign` +1 leans to the left."""
    s, co = math.sin(math.radians(a)), math.cos(math.radians(a))
    xb = h * s + 0.001
    pts = [(xb, 0), (xb + t * co, t * s), (xb + t * co - h * s, t * s + h * co), (xb - h * s, h * co)]
    if sign < 0:
        pts = [(-u, v) for u, v in reversed(pts)]
    g.profile(name, "Front", [(off(x, u), off(z, v)) for u, v in pts], y, d, mat)
    return xb + t * co


def row(g, rng, prefix, x, y, z, n, sign, hmax=0.3, lean=False, number=1):
    """`n` standing books from `x` towards +x (sign 1) or -x (sign -1); returns the width they take."""
    used = 0.0
    names = list(COVERS)
    last = None
    for i in range(n):
        t = rng.choice((0.016, 0.02, 0.024, 0.028, 0.032, 0.038, 0.045))
        h = round(rng.uniform(0.19, hmax), 3)
        d = round(min(0.23, h * rng.uniform(0.66, 0.78)), 3)
        mat = rng.choice([m for m in names if m != last])
        last = mat
        x0 = off(x, used) if sign > 0 else off(x, -used - t)
        book(g, f"{prefix} {number + i}", x0, y, z, t, d, h, mat)
        if t >= 0.028 and rng.random() < 0.6:  # a title band on the spine
            g.box(f"{prefix} {number + i} - etiqueta", off(x0, 0.004), off(y, -0.0006), off(z, round(h * 0.62, 3)), t - 0.008, 0.0006, 0.035, rng.choice(("Papel", "Latão")), detail=FINE)
        used += t + 0.0005
    if lean:
        mat = rng.choice([m for m in names if m != last])
        used += leaning(g, f"{prefix} {number + n} inclinado", off(x, sign * used), y, z, 0.024, 0.15, 0.21, mat, sign)
    import os
    if os.environ.get("ROWS"):
        print(prefix, round(used, 3))
    return used


def blob(g, name, x, y, z, r, h, mat, n=7, **kw):
    """An ellipsoid of radius `r` and height `h` standing at z (a sphere when h = 2 r)."""
    pts = [(x, z)]
    for i in range(1, n):
        a = math.pi * i / n
        pts.append((off(x, r * math.sin(a)), off(z, h / 2 - h / 2 * math.cos(a))))
    pts.append((x, off(z, h)))
    g.rev(name, "Front", pts, y, x, mat, **kw)


def storage_box(g, name, x, y, z, w, d, h, mat="Tecido"):
    g.box(name, x, y, z, w, d, h - 0.03, mat)
    g.box(f"{name} - tampa", off(x, -0.003), off(y, -0.003), off(z, h - 0.03), w + 0.006, d + 0.006, 0.03, mat)
    g.box(f"{name} - porta-etiqueta", off(x, w / 2 - 0.035), off(y, -0.002), off(z, h * 0.38), 0.07, 0.002, 0.03, "Latão", detail=FINE)
    g.box(f"{name} - etiqueta", off(x, w / 2 - 0.03), off(y, -0.0025), off(z, h * 0.38 + 0.005), 0.06, 0.0005, 0.02, "Papel", detail=FINE)


def build():
    c = Component("Estante", "casework", "estante", "Casework")
    W = c.param("Largura", 0.8)
    D = c.param("Profundidade", 0.3)
    H = c.param("Altura", 1.8)
    c.material("Papel", (238, 232, 214), "Generic", "Matte")
    c.material("Folhagem", (78, 122, 58), "Generic", "Matte")
    for name, color in COVERS.items():
        c.material(name, color, "Generic", "Matte")
    WOOD, STEEL = "Madeira", "Aço galvanizado"
    rng = random.Random(7)

    T = 0.02
    xL, xR = f"(-{W}/2)", f"({W}/2)"
    yF, yB = f"(-{D}/2)", f"({D}/2)"
    xi0, xi1 = f"({xL} + {T})", f"({xR} - {T})"
    wi = f"({W} - 2*{T})"
    ds = f"({D} - 0.006)"
    zsh = ["0.05"] + [f"({i}*({H} - 0.07)/4 + 0.05)" for i in (1, 2, 3)] + [f"({H} - 0.02)"]  # bottom of the shelves
    S = [f"({z} + {T})" for z in zsh]  # their tops

    # carcass: the same at every detail level
    c.box("Lateral esquerda", xL, yF, 0, T, D, H, WOOD, detail=ALL, in_plan=True)
    c.box("Lateral direita", xi1, yF, 0, T, D, H, WOOD, detail=ALL, in_plan=True)
    c.box("Fundo", xi0, f"{yB} - 0.006", 0, wi, 0.006, H, WOOD, detail=ALL)
    for i, z in enumerate(zsh):
        c.box(f"Prateleira {i}", xi0, yF, z, wi, ds, T, WOOD, detail=ALL, in_plan=(i == 4))
    c.box("Rodapé", xi0, f"{yF} + 0.02", 0, wi, 0.018, 0.05, WOOD)
    c.box("Travessa traseira do rodapé", xi0, f"{yB} - 0.024", 0, wi, 0.018, 0.05, WOOD, detail=FINE)

    # shelf pins of the three loose shelves, cam fittings of the two fixed ones, wall brackets
    for i in (1, 2, 3):
        for j, yp in enumerate((f"{yF} + 0.05", f"{yB} - 0.06"), 1):
            c.cyl_x(f"Pino da prateleira {i} - esquerdo {j}", yp, f"{zsh[i]} - 0.0025", xi0, 0.0025, 0.009, STEEL, detail=FINE)
            c.cyl_x(f"Pino da prateleira {i} - direito {j}", yp, f"{zsh[i]} - 0.0025", f"{xi1} - 0.009", 0.0025, 0.009, STEEL, detail=FINE)
    for i, zc in ((0, f"{zsh[0]} - 0.0005"), (4, f"{zsh[4]} - 0.0005")):
        for j, yp in enumerate((f"{yF} + 0.06", f"{yB} - 0.07"), 1):
            c.cyl(f"Tambor de fixação da prateleira {i} - esquerdo {j}", f"{xi0} + 0.03", yp, zc, 0.0075, 0.0005, STEEL, detail=FINE)
            c.cyl(f"Tambor de fixação da prateleira {i} - direito {j}", f"{xi1} - 0.03", yp, zc, 0.0075, 0.0005, STEEL, detail=FINE)
    for nm, x0 in (("esquerda", f"{xi0} + 0.06"), ("direita", f"{xi1} - 0.09")):
        c.box(f"Cantoneira de parede {nm}", x0, f"{yB} - 0.008", f"{zsh[4]} - 0.04", 0.03, 0.002, 0.04, STEEL, detail=FINE)
        c.box(f"Cantoneira de parede {nm} - aba", x0, f"{yB} - 0.04", f"{zsh[4]} - 0.002", 0.03, 0.034, 0.002, STEEL, detail=FINE)

    g = Grp(c)
    # the wider type has room for two more groups on each shelf
    x = Grp(c, f"min(1, max({EPS}, round({W}/0.4) - 2))", (f"{xL} + {T}/2", 0, f"{H}/2"))
    yb = f"({yF} + 0.025)"  # the spines stand a little behind the shelf's edge
    L, R = f"({xi0} + 0.004)", f"({xi1} - 0.004)"
    XA, XB = "(-0.26)", "0.1"  # left ends of the extra groups

    # shelf 0: boxes, tall books
    z = S[0]
    storage_box(g, "Caixa organizadora 1", L, f"{yF} + 0.03", z, 0.27, 0.22, 0.22)
    row(g, rng, "Livro de arte", R, yb, z, 5, -1, hmax=0.33, lean=True)
    storage_box(x, "Caixa organizadora 2", "(-0.08)", f"{yF} + 0.03", z, 0.16, 0.2, 0.16, mat="Capa de livro cinza")
    for i in (1, 2):
        x0 = off(XA, (i - 1) * 0.082)
        x.box(f"Porta-revistas {i}", x0, f"{yF} + 0.02", z, 0.078, 0.24, 0.25, "Plástico cinza claro")
        x.box(f"Porta-revistas {i} - revistas", off(x0, 0.006), f"{yF} + 0.03", off(z, 0.003), 0.066, 0.22, 0.29, "Papel")
        x.box(f"Porta-revistas {i} - etiqueta", off(x0, 0.02), f"{yF} + 0.0195", off(z, 0.05), 0.04, 0.0005, 0.06, "Papel", detail=FINE)
    row(x, rng, "Enciclopédia", XB, yb, z, 4, 1, hmax=0.3)

    # shelf 1: books, a globe, a lying stack
    z = S[1]
    row(g, rng, "Romance", L, yb, z, 7, 1, hmax=0.25, lean=True)
    g.cyl("Globo - base", 0, 0.01, z, 0.05, 0.012, "Madeira escura")
    g.cyl("Globo - haste", 0, 0.01, off(z, 0.012), 0.005, 0.045, "Latão", detail=FINE)
    blob(g, "Globo", 0, 0.01, off(z, 0.05), 0.075, 0.15, "Plástico azul", n=10)
    g.cyl("Globo - eixo", 0, 0.01, off(z, 0.2), 0.004, 0.012, "Latão", detail=FINE)
    zz, dims = z, ((0.04, 0.2, 0.27, "Capa de livro vinho"), (0.032, 0.19, 0.25, "Capa de livro creme"), (0.028, 0.17, 0.24, "Capa de livro azul"), (0.022, 0.15, 0.21, "Capa de livro mostarda"))
    for i, (t, d, h, mat) in enumerate(dims, 1):
        book(g, f"Livro deitado {i}", f"{R} - 0.275 + {e((0.27 - h) / 2)}", yb, zz, t, d, h, mat, lying=True)
        zz = off(zz, t + 0.0003)
    blob(g, "Esfera decorativa", f"{R} - 0.14", f"{yb} + 0.075", zz, 0.035, 0.07, "Latão", n=8, detail=FINE)
    row(x, rng, "Livro de bolso", XA, yb, z, 5, 1, hmax=0.22)
    row(x, rng, "Manual", XB, yb, z, 4, 1, hmax=0.28)

    # shelf 2: books and a bookend, a clock, books
    z = S[2]
    w = row(g, rng, "Biografia", L, yb, z, 5, 1, hmax=0.27)
    g.box("Aparador de livros - encosto", off(L, w + 0.0005), f"{yb} + 0.01", z, 0.002, 0.12, 0.16, "Aço pintado preto")
    g.box("Aparador de livros - base", off(L, w + 0.0005), f"{yb} + 0.01", z, 0.09, 0.12, 0.002, "Aço pintado preto", detail=FINE)
    g.box("Relógio - pé", -0.04, -0.03, z, 0.08, 0.05, 0.012, "Aço pintado preto", detail=FINE)
    g.cyl_y("Relógio - caixa", 0, off(z, 0.085), -0.025, 0.075, 0.04, "Aço pintado preto")
    g.cyl_y("Relógio - mostrador", 0, off(z, 0.085), -0.026, 0.068, 0.002, "Branco", detail=FINE)
    g.box("Relógio - ponteiro das horas", -0.003, -0.0268, off(z, 0.085), 0.006, 0.0008, 0.035, "Plástico preto", detail=FINE)
    g.box("Relógio - ponteiro dos minutos", 0, -0.0268, off(z, 0.083), 0.052, 0.0008, 0.004, "Plástico preto", detail=FINE)
    row(g, rng, "Livro técnico", R, yb, z, 6, -1, hmax=0.29, lean=True)
    vase = [(0, 0), (0.035, 0), (0.06, 0.05), (0.065, 0.1), (0.045, 0.17), (0.028, 0.21), (0.036, 0.24), (0.03, 0.24), (0.022, 0.21), (0, 0.2)]
    x.rev("Vaso", "Front", [(off("(-0.18)", u), off(z, v)) for u, v in vase], 0.01, "(-0.18)", "Louça")
    row(x, rng, "Livro de receitas", XB, yb, z, 4, 1, hmax=0.27)

    # shelf 3: a plant, a picture frame, books
    z = S[3]
    xp = f"({L} + 0.11)"
    pot = [(0, 0), (0.05, 0), (0.07, 0.11), (0.075, 0.11), (0.075, 0.125), (0.062, 0.125), (0.062, 0.115), (0, 0.115)]
    g.rev("Vaso da planta", "Front", [(off(xp, u), off(z, v)) for u, v in pot], 0.01, xp, "Telha cerâmica")
    g.cyl("Terra do vaso", xp, 0.01, off(z, 0.115), 0.06, 0.004, "Terra", detail=FINE)
    for i, (dx, dy, dz, r, h) in enumerate(((0, 0, 0.12, 0.055, 0.16), (-0.05, 0.02, 0.13, 0.04, 0.1), (0.05, -0.02, 0.14, 0.042, 0.11), (0.01, 0.05, 0.17, 0.04, 0.1), (-0.02, -0.05, 0.16, 0.038, 0.09), (0.03, 0.01, 0.22, 0.035, 0.08)), 1):
        blob(g, f"Folhagem {i}", off(xp, dx), 0.01 + dy, off(z, dz), r, h, "Folhagem", n=6)
    g.box("Porta-retrato - moldura", -0.075, 0, z, 0.15, 0.014, 0.2, "Madeira escura")
    g.box("Porta-retrato - passe-partout", -0.063, -0.0008, off(z, 0.012), 0.126, 0.0008, 0.176, "Papel", detail=FINE)
    g.box("Porta-retrato - fotografia", -0.043, -0.0014, off(z, 0.035), 0.086, 0.0006, 0.13, "Capa de livro turquesa", detail=FINE)
    g.box("Porta-retrato - apoio", -0.01, 0.014, z, 0.02, 0.05, 0.004, "Madeira escura", detail=FINE)
    w = row(g, rng, "Livro de poesia", R, yb, z, 6, -1, hmax=0.24)
    g.box("Aparador de livros 2 - encosto", off(R, -w - 0.0025), f"{yb} + 0.01", z, 0.002, 0.12, 0.16, "Aço pintado preto")
    g.box("Aparador de livros 2 - base", off(R, -w - 0.0905), f"{yb} + 0.01", z, 0.09, 0.12, 0.002, "Aço pintado preto", detail=FINE)
    row(x, rng, "Atlas", XA, yb, z, 4, 1, hmax=0.3)
    zz = z
    for i, (t, d, h, mat) in enumerate(((0.035, 0.19, 0.15, "Capa de livro verde"), (0.03, 0.17, 0.15, "Capa de livro laranja"), (0.02, 0.15, 0.14, "Capa de livro preta")), 1):
        book(x, f"Livro empilhado {i}", off(XB, (0.15 - h) / 2), yb, zz, t, d, h, mat, lying=True)
        zz = off(zz, t + 0.0003)

    c.type("Estante 80 cm", "Estante aberta com 5 prateleiras")
    c.type("Estante 120 cm", "Estante aberta com 5 prateleiras", Largura=1.2)
    return c
