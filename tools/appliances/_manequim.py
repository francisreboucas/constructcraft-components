"""Smooth mannequin bodies: a signed distance field of body parts blended into one surface, meshed by surface nets.

Not a component module. The parts (round cones for the limbs and the neck, ellipsoids for the head, the torso, the
hands and the feet) join with a smooth union, so shoulders, elbows, hips and knees flow into each other like a shop
mannequin's. Each garment (skin, hair, top, bottom, shoes) is meshed as its own closed solid: the body clipped to where
that garment's parts are the nearest, so the colours meet along clean seams.
"""

from __future__ import annotations

import numpy as np

from _moto.base import Mesh


# --- distance functions (p: N x 3 array) ---------------------------------------------------------

def sd_round_cone(p, a, b, r1, r2):
    """A cone from the sphere (a, r1) to the sphere (b, r2), rounded at both ends (Inigo Quilez's formula)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ba = b - a
    l2 = float(ba @ ba)
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pa = p - a
    y = pa @ ba
    z = y - l2
    q = pa * l2 - np.outer(y, ba)
    x2 = np.einsum("ij,ij->i", q, q)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d3 = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    d1 = np.sqrt(x2 + z2) * il2 - r2
    d2 = np.sqrt(x2 + y2) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d1, np.where(np.sign(y) * a2 * y2 < k, d2, d3))


def sd_ellipsoid(p, c, r, basis=None, floor=None):
    """An ellipsoid of semi-axes r about c (axes along `basis`' rows when given); `floor` flattens it below that z."""
    q = p - np.asarray(c, float)
    if basis is not None:
        q = q @ np.asarray(basis, float).T
    r = np.asarray(r, float)
    k0 = np.linalg.norm(q / r, axis=1)
    k1 = np.linalg.norm(q / (r * r), axis=1)
    d = k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)
    if floor is not None:
        d = np.maximum(d, floor - p[:, 2])
    return d


def smin(a, b, k):
    """Smooth minimum (polynomial): blends two distances over the width k."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


class Body:
    """Body parts by garment; distances evaluated on point arrays."""

    def __init__(self, blend=0.035):
        self.parts: list[tuple[str, callable, float]] = []  # (garment, distance function, blend)
        self.blend = blend
        self.lo = np.array([np.inf] * 3)
        self.hi = np.array([-np.inf] * 3)
        self.boxes: dict[str, list] = {}

    def _grow(self, c, r, g=None):
        c = np.asarray(c, float)
        self.lo = np.minimum(self.lo, c - r)
        self.hi = np.maximum(self.hi, c + r)
        if g is not None:
            lo, hi = self.boxes.get(g, (np.array([np.inf] * 3), np.array([-np.inf] * 3)))
            self.boxes[g] = (np.minimum(lo, c - r), np.maximum(hi, c + r))

    def box(self, g):
        return self.boxes[g]

    def cone(self, garment, a, b, r1, r2, blend=None, zmin=None):
        if zmin is None:
            f = lambda p, a=a, b=b, r1=r1, r2=r2: sd_round_cone(p, a, b, r1, r2)  # noqa: E731
        else:  # cut flat below zmin (a skirt's hem)
            f = lambda p, a=a, b=b, r1=r1, r2=r2: np.maximum(sd_round_cone(p, a, b, r1, r2), zmin - p[:, 2])  # noqa: E731
        self.parts.append((garment, f, blend or self.blend))
        self._grow(a, r1, garment)
        self._grow(b, r2, garment)

    def ellipsoid(self, garment, c, r, basis=None, floor=None, blend=None):
        self.parts.append((garment, lambda p, c=c, r=r, basis=basis, floor=floor: sd_ellipsoid(p, c, r, basis, floor), blend or self.blend))
        self._grow(c, max(r), garment)

    def fields(self, p):
        """The body's distance (smooth union of every part) and each garment's distance (hard minimum of its parts)."""
        body = None
        by_garment: dict[str, np.ndarray] = {}
        for g, f, k in self.parts:
            d = f(p)
            body = d if body is None else smin(body, d, k)
            by_garment[g] = d if g not in by_garment else np.minimum(by_garment[g], d)
        return body, by_garment

    def garment_fields(self, g):
        """The body's field and the seam field of garment g (negative where g's parts are the nearest)."""
        def both(p):
            body, gd = self.fields(p)
            others = [v for k, v in gd.items() if k != g]
            seam = gd[g] - np.min(np.stack(others), axis=0) if others else np.full(len(p), -1.0)
            return body, seam
        return both

    def garment_field(self, g):
        both = self.garment_fields(g)

        def f(p):
            body, seam = both(p)
            return np.maximum(body, seam)
        return f


# --- surface nets ----------------------------------------------------------------------------------

_CORNERS = np.array([(i, j, k) for k in (0, 1) for j in (0, 1) for i in (0, 1)])
_EDGES = [(a, b) for a in range(8) for b in range(a + 1, 8) if np.abs(_CORNERS[a] - _CORNERS[b]).sum() == 1]


def surface_net(field, lo, hi, h, refine=2):
    """A closed quad mesh of the surface field = 0 over the box lo..hi with the cell size h (surface nets)."""
    lo = np.asarray(lo, float) - 2 * h
    hi = np.asarray(hi, float) + 2 * h
    n = np.ceil((hi - lo) / h).astype(int) + 1
    xs = [lo[i] + h * np.arange(n[i]) for i in range(3)]
    X, Y, Z = np.meshgrid(*xs, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    F = field(pts).reshape(n)
    inside = F < 0
    # Cells crossing the surface, a vertex in each at the mean of its edge crossings.
    cn = n - 1
    acc = np.zeros(tuple(cn) + (3,))
    cnt = np.zeros(tuple(cn))
    for a, b in _EDGES:
        ia, ib = _CORNERS[a], _CORNERS[b]
        fa = F[ia[0]:ia[0] + cn[0], ia[1]:ia[1] + cn[1], ia[2]:ia[2] + cn[2]]
        fb = F[ib[0]:ib[0] + cn[0], ib[1]:ib[1] + cn[1], ib[2]:ib[2] + cn[2]]
        m = (fa < 0) != (fb < 0)
        t = np.where(m, fa / np.where(m, fa - fb, 1.0), 0.0)
        for ax in range(3):
            base = (np.arange(cn[ax]) + ia[ax]) * h + lo[ax]
            shape = [1, 1, 1]
            shape[ax] = cn[ax]
            pos = base.reshape(shape) + t * (ib[ax] - ia[ax]) * h
            acc[..., ax] += np.where(m, pos, 0.0)
        cnt += m
    active = cnt > 0
    idx = -np.ones(tuple(cn), dtype=np.int64)
    idx[active] = np.arange(active.sum())
    verts = acc[active] / cnt[active][:, None]
    # A quad round every grid edge that crosses the surface, from the four cells sharing it.
    quads = []
    for ax in range(3):
        u, v = [(1, 2), (0, 2), (0, 1)][ax]
        s0 = [slice(0, n[0]), slice(0, n[1]), slice(0, n[2])]
        s0[ax] = slice(0, n[ax] - 1)
        s1 = list(s0)
        s1[ax] = slice(1, n[ax])
        cross = inside[tuple(s0)] != inside[tuple(s1)]
        start_in = inside[tuple(s0)]
        e = np.argwhere(cross)
        e = e[(e[:, u] > 0) & (e[:, v] > 0) & (e[:, u] < n[u] - 1) & (e[:, v] < n[v] - 1)]
        flip = start_in[tuple(e.T)]

        def cell(du, dv):
            c = e.copy()
            c[:, u] -= du
            c[:, v] -= dv
            return idx[tuple(c.T)]

        q = np.stack([cell(1, 1), cell(0, 1), cell(0, 0), cell(1, 0)], axis=1)
        if ax == 1:
            flip = ~flip
        q[flip] = q[flip][:, ::-1]
        quads.append(q)
    quads = np.concatenate(quads)
    quads = quads[(quads >= 0).all(axis=1)]
    # Pull the vertices onto the surface (Newton steps along the numerical gradient).
    for _ in range(refine):
        d = field(verts)
        g = np.zeros_like(verts)
        e = h * 0.25
        for ax in range(3):
            off = np.zeros(3)
            off[ax] = e
            g[:, ax] = (field(verts + off) - field(verts - off)) / (2 * e)
        gn = np.maximum((g * g).sum(axis=1), 1e-9)
        step = (d / gn)[:, None] * g
        step = np.clip(step, -h, h)
        verts = verts - step
    return verts, quads


def to_mesh(verts, quads) -> Mesh:
    m = Mesh()
    m.v = [tuple(map(float, v)) for v in verts]
    m.f = [list(map(int, q)) for q in quads]
    m.orient(0)
    return m


def _project(verts, f, h, mask):
    """One Newton step of the vertices in `mask` onto the surface f = 0."""
    if not mask.any():
        return verts
    v = verts[mask]
    d = f(v)
    g = np.zeros_like(v)
    e = h * 0.25
    for ax in range(3):
        off = np.zeros(3)
        off[ax] = e
        g[:, ax] = (f(v + off) - f(v - off)) / (2 * e)
    gn = np.maximum((g * g).sum(axis=1), 1e-9)
    out = verts.copy()
    out[mask] = v - np.clip((d / gn)[:, None] * g, -h, h)
    return out


def garment_meshes(body: Body, h: float, finer: dict | None = None) -> dict[str, Mesh]:
    """One closed mesh per garment; `finer` maps garments to a smaller cell size (the head)."""
    out = {}
    finer = finer or {}
    for g in dict.fromkeys(p[0] for p in body.parts):
        hg = finer.get(g, h)
        lo, hi = body.lo, body.hi
        if g in finer:  # only the box of that garment's parts
            lo, hi = body.box(g)
        v, q = surface_net(body.garment_field(g), lo, hi, hg)
        h_ = hg
        if not len(q):
            continue
        # Seams: the vertices near the crease where the body meets the seam surface go onto both surfaces, so the
        # garment's edge follows the crease instead of the grid's steps.
        both = body.garment_fields(g)
        b, s = both(v)
        near = np.abs(b - s) < 1.2 * h_
        for _ in range(4):
            v = _project(v, lambda p: both(p)[0], h_, near)
            v = _project(v, lambda p: both(p)[1], h_, near)
        v = _relax(v, q, ~near, body.garment_field(g), h_)
        out[g] = to_mesh(v, q)
    return out


def _relax(verts, quads, free, field, h, rounds=3):
    """Even out the vertices (Taubin smoothing of the `free` ones, then back onto the surface)."""
    n = len(verts)
    src = np.concatenate([quads[:, i] for i in range(4)])
    dst = np.concatenate([quads[:, (i + 1) % 4] for i in range(4)])
    deg = np.bincount(src, minlength=n).astype(float) + np.bincount(dst, minlength=n)

    def lap(v):
        acc = np.zeros_like(v)
        np.add.at(acc, src, v[dst])
        np.add.at(acc, dst, v[src])
        return acc / np.maximum(deg, 1)[:, None] - v

    for _ in range(rounds):
        for w in (0.5, -0.53):
            d = lap(verts)
            verts = verts + w * d * free[:, None]
    for _ in range(2):
        verts = _project(verts, field, h, free)
    return verts
