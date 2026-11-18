"""Helpers shared by the door modules (porta_*, portao_*): not a component.

A door's frame (component_create): x along the wall from the opening's center,
y across the wall towards the side the door opens to (+y), z up from the floor;
the wall spans y = -WallThickness/2 .. WallThickness/2.

The kit's `door_box` opens towards -y (an appliance's front), a door opens
towards +y, so the moving parts here are written on a `Fr`: a plan frame with
an origin, the angle of its `a` axis (counter-clockwise from +x, degrees) and
`n` to the left of `a`. `Fr(c, ox, oy, A)` is a leaf hinged at (ox, oy) on the
-x jamb that opens to +y by A: `a` runs along the leaf from the hinge, `n`
out of the opening side (the leaf's body has n < 0). `mx=True` mirrors the
whole frame about x = 0 (the other leaf of a double door).
"""

from __future__ import annotations

from kit import *  # noqa: F401,F403
from kit import e, p, FULL, FINE, COARSE

WT = "WallThickness"


def _zero(v) -> bool:
    return not isinstance(v, str) and float(v) == 0.0


def _sum(terms: list[str]) -> str:
    out = ""
    for t in terms:
        if not out:
            out = t
        elif t.startswith("-"):
            out += " - " + t[1:]
        else:
            out += " + " + t
    return out or "0"


def _mul(v, f: str, neg: bool = False) -> str:
    """v * f as a term (a leading '-' marks a negative term)."""
    if not isinstance(v, str):
        v = float(v)
        if neg:
            v = -v
        return f"-{e(-v)}*{f}" if v < 0 else f"{e(v)}*{f}"
    return f"{'-' if neg else ''}{p(v)}*{f}"


class Fr:
    def __init__(self, c, ox, oy, ang, mx: bool = False):
        self.c, self.ox, self.oy, self.ang, self.mx = c, e(ox), e(oy), e(ang), mx
        self.fixed = not isinstance(ang, str) and float(ang) == 0.0

    def raw(self, a, n) -> tuple[str, str]:
        """(x, y) of the point (a, n) before the mirror."""
        if self.fixed:
            xs = [p(self.ox)] + ([] if _zero(a) else [_mul(a, "1")[:-2]])
            ys = [p(self.oy)] + ([] if _zero(n) else [_mul(n, "1")[:-2]])
            return _sum(xs), _sum(ys)
        g = p(self.ang)
        xs, ys = [p(self.ox)], [p(self.oy)]
        if not _zero(a):
            xs.append(_mul(a, f"cos({g})"))
            ys.append(_mul(a, f"sin({g})"))
        if not _zero(n):
            xs.append(_mul(n, f"sin({g})", neg=True))
            ys.append(_mul(n, f"cos({g})"))
        return _sum(xs), _sum(ys)

    def pt(self, a, n) -> tuple[str, str]:
        x, y = self.raw(a, n)
        return (f"-({x})" if self.mx else x), y

    def sub(self, a, n, ang) -> "Fr":
        """A frame whose origin is this frame's point (a, n), at the absolute angle `ang`."""
        x, y = self.raw(a, n)
        return Fr(self.c, x, y, ang, self.mx)

    def still(self) -> "Fr":
        """The same frame with the leaf closed (parts fixed to the jamb)."""
        return Fr(self.c, self.ox, self.oy, 0, self.mx)

    # --- pieces -----------------------------------------------------------

    def poly(self, name, pts, z, h, mat, detail=FULL, in_plan=False, void=False):
        """A plan outline [(a, n) or (a, n, radius), …] extruded up from z."""
        pts = [tuple(q) + (None,) * (3 - len(q)) for q in pts]
        if self.mx:  # keep the winding: reverse, moving each arc to its segment's new start
            m = len(pts)
            rev = []
            for i in range(m):
                k = m - 1 - i
                rev.append((pts[k][0], pts[k][1], pts[(k - 1) % m][2]))
            pts = rev
        out = [self.pt(a, n) + ((r,) if r else ()) for a, n, r in pts]
        self.c.profile(name, "Plan", out, z, h, mat, detail=detail, in_plan=in_plan, void=void)

    def box(self, name, a0, a1, n0, n1, z, h, mat, detail=FULL, in_plan=False, void=False):
        self.poly(name, [(a0, n0), (a1, n0), (a1, n1), (a0, n1)], z, h, mat, detail, in_plan, void)

    def cyl(self, name, a, n, z, r, h, mat, detail=FULL, in_plan=False):
        x, y = self.pt(a, n)
        self.c.cyl(name, x, y, z, r, h, mat, detail=detail, in_plan=in_plan)


def s(*terms) -> str:
    """Sum of expressions and numbers, in parentheses."""
    num = sum(float(t) for t in terms if not isinstance(t, str))
    parts = [p(t) for t in terms if isinstance(t, str)]
    if num or not parts:
        parts.append(e(num))
    return "(" + _sum([q if not q.startswith("-") else q for q in parts]) + ")"


# --- wood frame ------------------------------------------------------------

def wood_frame(c, L, H, mat, jt=0.035, st=0.013, leaf_t=0.035, casing_front=True, casing_back=True,
               stop=True, in_plan=False, cw=0.07, ct=0.012):
    """Jambs and head lining the opening, with a stop (rebate) and mitred casings on both faces.

    Jamb `jt` thick plus a stop `st`; the leaf (leaf_t thick) sits in the rebate
    flush with the +y face. Coarse stand-ins are the 5 cm boxes of the old doors.
    """
    xl, xr = f"(-{L}/2)", f"({L}/2)"
    yb, yf = f"(-{WT}/2)", f"({WT}/2)"
    ys = f"({WT}/2 - {e(leaf_t + 0.002)})"  # face of the stop
    c.box("Batente esquerdo simplificado", xl, yb, 0, 0.05, WT, H, mat, detail=COARSE, in_plan=in_plan)
    c.box("Batente direito simplificado", f"{xr} - 0.05", yb, 0, 0.05, WT, H, mat, detail=COARSE, in_plan=in_plan)
    c.box("Batente superior simplificado", f"{xl} + 0.05", yb, f"{H} - 0.05", f"{L} - 0.1", WT, 0.05, mat, detail=COARSE)
    c.box("Batente esquerdo", xl, yb, 0, jt, WT, H, mat, in_plan=in_plan)
    c.box("Batente direito", f"{xr} - {e(jt)}", yb, 0, jt, WT, H, mat, in_plan=in_plan)
    c.box("Batente superior", f"{xl} + {e(jt)}", yb, f"{H} - {e(jt)}", f"{L} - {e(2 * jt)}", WT, jt, mat)
    if stop:
        sd = f"({WT} - {e(leaf_t + 0.002)})"
        c.box("Batedor esquerdo", f"{xl} + {e(jt)}", yb, 0, st, sd, f"{H} - {e(jt)}", mat, in_plan=in_plan)
        c.box("Batedor direito", f"{xr} - {e(jt + st)}", yb, 0, st, sd, f"{H} - {e(jt)}", mat, in_plan=in_plan)
        c.box("Batedor superior", f"{xl} + {e(jt + st)}", yb, f"{H} - {e(jt + st)}", f"{L} - {e(2 * (jt + st))}", sd, st, mat)
        # Rubber seal on the stop.
        c.box("Amortecedor esquerdo", f"{xl} + {e(jt + 0.003)}", ys, 0.01, 0.006, 0.0015, f"{H} - {e(jt + 0.012)}", "Borracha cinza", detail=FINE)
        c.box("Amortecedor direito", f"{xr} - {e(jt + 0.009)}", ys, 0.01, 0.006, 0.0015, f"{H} - {e(jt + 0.012)}", "Borracha cinza", detail=FINE)
        c.box("Amortecedor superior", f"{xl} + {e(jt + 0.009)}", ys, f"{H} - {e(jt + 0.009)}", f"{L} - {e(2 * (jt + 0.009))}", 0.0015, 0.006, "Borracha cinza", detail=FINE)
    ov = 0.015  # the casing laps the jamb's edge
    for on, y0, face in ((casing_front, yf, "frente"), (casing_back, f"({yb} - {e(ct)})", "fundo")):
        if on:
            casing(c, L, H, mat, y0, face, cw, ct, ov)


def casing(c, L, H, mat, y0, face, cw=0.07, ct=0.012, ov=0.015, top=None):
    """Mitred casings (guarnições) around the opening, from y0 to y0 + ct, plus a back band."""
    xl, xr = f"(-{L}/2)", f"({L}/2)"
    zi = f"({H} - {e(ov)})"
    zo = f"({H} + {e(cw - ov)})"
    xi_l, xo_l = f"({xl} + {e(ov)})", f"({xl} - {e(cw - ov)})"
    xi_r, xo_r = f"({xr} - {e(ov)})", f"({xr} + {e(cw - ov)})"
    c.profile(f"Guarnição esquerda ({face})", "Front", [(xo_l, 0), (xi_l, 0), (xi_l, zi), (xo_l, zo)], y0, ct, mat)
    c.profile(f"Guarnição direita ({face})", "Front", [(xi_r, 0), (xo_r, 0), (xo_r, zo), (xi_r, zi)], y0, ct, mat)
    c.profile(f"Guarnição superior ({face})", "Front", [(xi_l, zi), (xi_r, zi), (xo_r, zo), (xo_l, zo)], y0, ct, mat)
    # Back band: a thicker moulding along the outer edge.
    bw, bt = 0.018, 0.005
    yb = f"({y0} + {e(ct)})" if face == "frente" else f"({y0} - {e(bt)})"
    zb = f"({zo} - {e(bw)})"
    xb_l, xb_r = f"({xo_l} + {e(bw)})", f"({xo_r} - {e(bw)})"
    c.profile(f"Guarnição esquerda - moldura ({face})", "Front", [(xo_l, 0), (xb_l, 0), (xb_l, zb), (xo_l, zo)], yb, bt, mat, detail=FINE)
    c.profile(f"Guarnição direita - moldura ({face})", "Front", [(xb_r, 0), (xo_r, 0), (xo_r, zo), (xb_r, zb)], yb, bt, mat, detail=FINE)
    c.profile(f"Guarnição superior - moldura ({face})", "Front", [(xb_l, zb), (xb_r, zb), (xo_r, zo), (xo_l, zo)], yb, bt, mat, detail=FINE)


# --- leaves ----------------------------------------------------------------

def panel_leaf(fr: Fr, pre, a0, a1, n0, n1, z0, z1, rails, mat, sw=0.1, top=0.11, bottom=0.19,
               board=0.014, field=0.006, bead=0.012, inset=0.035, panel_mat=None):
    """A stile-and-rail leaf with raised panels (almofadas) on both faces.

    Spans a0..a1, n0..n1 (n0 < n1) and z0..z1 (expressions or numbers);
    `rails` are the intermediate rails [(z, height), …] from the bottom up.
    """
    c = fr.c
    panel_mat = panel_mat or mat
    w = s(a1, f"-{p(a0)}") if isinstance(a0, str) or isinstance(a1, str) else a1 - a0
    fr.box(f"{pre} - montante da dobradiça", a0, s(a0, sw), n0, n1, z0, s(z1, f"-{p(z0)}"), mat)
    fr.box(f"{pre} - montante da fechadura", s(a1, -sw), a1, n0, n1, z0, s(z1, f"-{p(z0)}"), mat)
    ra0, ra1 = s(a0, sw), s(a1, -sw)
    fr.box(f"{pre} - travessa inferior", ra0, ra1, n0, n1, z0, bottom, mat)
    fr.box(f"{pre} - travessa superior", ra0, ra1, n0, n1, s(z1, -top), top, mat)
    edges = [s(z0, bottom)]
    for i, (rz, rh) in enumerate(rails):
        fr.box(f"{pre} - travessa intermediária {i + 1}", ra0, ra1, n0, n1, rz, rh, mat)
        edges += [rz, s(rz, rh)]
    edges.append(s(z1, -top))
    nc = s(n0, n1)[1:-1]
    nc = f"(({nc})/2)"
    for k in range(len(edges) // 2):
        pz0, pz1 = edges[2 * k], edges[2 * k + 1]
        ph = s(pz1, f"-{p(pz0)}")
        nm = f"{pre} - almofada {k + 1}"
        fr.box(nm, s(ra0, -0.008), s(ra1, 0.008), s(nc, -board / 2), s(nc, board / 2), s(pz0, -0.008), s(ph, 0.016), panel_mat)
        for face, sg in (("frente", 1), ("fundo", -1)):
            nb = s(nc, sg * board / 2)  # the board's face
            nf = s(nc, sg * (board / 2 + field))
            lo, hi = (nb, nf) if sg > 0 else (nf, nb)
            fr.box(f"{nm} - relevo ({face})", s(ra0, inset), s(ra1, -inset), lo, hi, s(pz0, inset), s(ph, -2 * inset), panel_mat)
            nd = s(nc, sg * (board / 2 + 0.0075))
            lo, hi = (nb, nd) if sg > 0 else (nd, nb)
            fr.box(f"{nm} - baguete esquerdo ({face})", ra0, s(ra0, bead), lo, hi, pz0, ph, mat, detail=FINE)
            fr.box(f"{nm} - baguete direito ({face})", s(ra1, -bead), ra1, lo, hi, pz0, ph, mat, detail=FINE)
            fr.box(f"{nm} - baguete inferior ({face})", s(ra0, bead), s(ra1, -bead), lo, hi, pz0, bead, mat, detail=FINE)
            fr.box(f"{nm} - baguete superior ({face})", s(ra0, bead), s(ra1, -bead), lo, hi, s(pz1, -bead), bead, mat, detail=FINE)


def butt_hinges(fr: Fr, pre, zs, mat="Inox escovado", knuckle=0.0065, height=0.09, plate=0.032, gap=0.002, face=0.006):
    """Butt hinges on the frame's axis: 5 knuckles, pin with tips, a leaf on the jamb and one on the door.

    The axis is the frame's origin; the door's edge is at a = gap and its face at n = -face.
    """
    still = fr.still()
    kh = height / 5
    for i, z in enumerate(zs):
        nm = f"{pre} {i + 1}"
        for k in range(5):
            fr.cyl(f"{nm} - nó {k + 1}", 0, 0, s(z, k * kh + 0.0003), knuckle, kh - 0.0006, mat, detail=FINE)
        fr.cyl(f"{nm} - pino", 0, 0, s(z, -0.003), 0.0035, height + 0.006, "Cromado", detail=FINE)
        fr.cyl(f"{nm} - ponteira inferior", 0, 0, s(z, -0.007), 0.005, 0.005, "Cromado", detail=FINE)
        fr.cyl(f"{nm} - ponteira superior", 0, 0, s(z, height + 0.002), 0.005, 0.005, "Cromado", detail=FINE)
        still.box(f"{nm} - aba do batente", -gap, -gap + 0.0012, -face - plate, 0, z, height, mat, detail=FINE)
        fr.box(f"{nm} - aba da folha", gap - 0.0012, gap, -face - plate, 0, z, height, mat, detail=FINE)
        for j in range(3):  # screw heads on both leaves
            zc = s(z, 0.015 + j * 0.03)
            still.box(f"{nm} - parafuso do batente {j + 1}", -gap + 0.0012, -gap + 0.0018, -face - 0.022, -face - 0.014, s(zc, -0.004), 0.008, "Cromado", detail=FINE)
            fr.box(f"{nm} - parafuso da folha {j + 1}", gap - 0.0018, gap - 0.0012, -face - 0.022, -face - 0.014, s(zc, -0.004), 0.008, "Cromado", detail=FINE)


def lever_set(fr: Fr, pre, ax, n_front, n_back, z, mat="Cromado", lever=0.125, key=True, thumb=True):
    """Lever handles on both faces, square roses, keyhole escutcheons.

    `ax` is the spindle's position along the leaf; the levers point back to the hinge (-a).
    """
    for face, nf, sg in (("frente", n_front, 1), ("fundo", n_back, -1)):
        def span(d0, d1):
            lo, hi = s(nf, sg * d0), s(nf, sg * d1)
            return (lo, hi) if sg > 0 else (hi, lo)
        lo, hi = span(0, 0.008)
        fr.box(f"{pre} - roseta ({face})", s(ax, -0.026), s(ax, 0.026), lo, hi, s(z, -0.026), 0.052, mat)
        lo, hi = span(0.008, 0.0095)
        fr.box(f"{pre} - anel da roseta ({face})", s(ax, -0.017), s(ax, 0.017), lo, hi, s(z, -0.017), 0.034, "Inox escovado", detail=FINE)
        lo, hi = span(0.0095, 0.056)
        fr.box(f"{pre} - pescoço ({face})", s(ax, -0.0095), s(ax, 0.0095), lo, hi, s(z, -0.0095), 0.019, mat)
        d0, d1 = 0.04, 0.056
        ni, no = s(nf, sg * d0), s(nf, sg * d1)
        nt = s(nf, sg * (d0 + 0.006))
        pts = [(s(ax, 0.0095), ni), (s(ax, 0.0095), no), (s(ax, -lever + 0.008), no), (s(ax, -lever), s(nf, sg * (d1 - 0.004))),
               (s(ax, -lever), nt), (s(ax, -lever + 0.03), ni)]
        if sg < 0:
            pts.reverse()
        fr.poly(f"{pre} - alavanca ({face})", pts, s(z, -0.009), 0.018, mat)
        if key:
            zk = s(z, -0.075)
            lo, hi = span(0, 0.008)
            fr.box(f"{pre} - entrada de chave ({face})", s(ax, -0.026), s(ax, 0.026), lo, hi, s(zk, -0.026), 0.052, mat)
            if sg < 0 and thumb:
                lo, hi = span(0.008, 0.014)
                fr.cyl(f"{pre} - base da tranqueta ({face})", ax, s(nf, sg * 0.011), s(zk, -0.006), 0.003, 0.012, mat, detail=FINE)
                fr.box(f"{pre} - base do trinco ({face})", s(ax, -0.011), s(ax, 0.011), lo, hi, s(zk, -0.011), 0.022, "Inox escovado", detail=FINE)
                lo, hi = span(0.014, 0.03)
                fr.box(f"{pre} - tranqueta ({face})", s(ax, -0.004), s(ax, 0.004), lo, hi, s(zk, -0.016), 0.032, mat, detail=FINE)
            else:
                lo, hi = span(0.008, 0.012)
                fr.box(f"{pre} - cilindro ({face})", s(ax, -0.0085), s(ax, 0.0085), lo, hi, s(zk, -0.016), 0.032, "Latão", detail=FINE)
                lo, hi = span(0.012, 0.0125)
                fr.box(f"{pre} - fenda da chave ({face})", s(ax, -0.001), s(ax, 0.001), lo, hi, s(zk, -0.007), 0.012, "Plástico preto", detail=FINE)


def mortise_lock(fr: Fr, pre, a_edge, nc, z, jamb_a, mat="Inox escovado", lip=0.02, bolt=True):
    """The lock's face plate on the leaf's edge, latch and dead bolt, and the strike on the jamb.

    `a_edge` is the leaf's lock edge, `nc` the middle of its thickness, `jamb_a`
    the jamb's face (same frame, closed); the strike's lip turns to +n.
    """
    still = fr.still()
    fr.box(f"{pre} - testa", s(a_edge, -0.002), s(a_edge, 0.0006), s(nc, -0.011), s(nc, 0.011), s(z, -0.135), 0.235, mat, detail=FINE)
    fr.poly(f"{pre} - lingueta", [(a_edge, s(nc, -0.006)), (s(a_edge, 0.011), s(nc, -0.006)), (s(a_edge, 0.004), s(nc, 0.006)), (a_edge, s(nc, 0.006))],
            s(z, -0.012), 0.024, "Latão", detail=FINE)
    if bolt:
        fr.box(f"{pre} - trinco", s(a_edge, -0.004), s(a_edge, 0.0012), s(nc, -0.005), s(nc, 0.005), s(z, -0.095), 0.04, "Latão", detail=FINE)
    for k, dz in enumerate((-0.128, 0.088)):
        fr.box(f"{pre} - parafuso da testa {k + 1}", s(a_edge, 0.0006), s(a_edge, 0.001), s(nc, -0.004), s(nc, 0.004), s(z, dz), 0.008, "Cromado", detail=FINE)
    # Strike plate on the jamb, with a lip turned around its edge.
    still.box(f"{pre} - contratesta", s(jamb_a, -0.0014), jamb_a, s(nc, -0.011), s(nc, 0.011 + lip), s(z, -0.115), 0.17, mat, detail=FINE)
    still.box(f"{pre} - furo da lingueta", s(jamb_a, -0.0017), s(jamb_a, -0.0014), s(nc, -0.007), s(nc, 0.007), s(z, -0.016), 0.032, "Plástico preto", detail=FINE)
    if bolt:
        still.box(f"{pre} - furo do trinco", s(jamb_a, -0.0017), s(jamb_a, -0.0014), s(nc, -0.006), s(nc, 0.006), s(z, -0.098), 0.046, "Plástico preto", detail=FINE)


def opening_param(c, name: str, open_value: float, kind: str = "Angle") -> str:
    """An instance parameter that opens the door (0 = closed).

    A door hosted in a wall keeps no instance values (component_params_set
    refuses it), so make.py's open pose cannot be used: with the environment
    variable DOOR_PREVIEW_OPEN set, the parameter's own value is `open_value`,
    to preview the open door. Never commit a source built that way.
    """
    import os
    value = open_value if os.environ.get("DOOR_PREVIEW_OPEN") else 0.0
    return c.param(name, value, kind, True)
