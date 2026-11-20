#!/usr/bin/env python3
"""Turn a TrueType font into the glyph table the floor markings' scripts draw text with.

    python tools/site/fonte.py --ttf path/to/IBMPlexSans_Condensed-Bold.ttf

Writes tools/site/fonte.lua, which tools/site.py puts into every component of
sources/site/ that has editable text. Each glyph is flattened to polygons
(outer outlines counter-clockwise, holes clockwise, in font units with y up)
and triangulated here, so the Lua script only has to lay the triangles out
and extrude them: no triangulation runs in ConstructCraft.

The glyphs come from IBM Plex Sans Condensed Bold (SIL Open Font License 1.1,
copyright IBM Corp.), a condensed bold sans that stays legible when the
markings stretch it along the direction of travel. Only the outlines are kept,
as geometry; no font file goes into the library.

Encoding (one Lua string per glyph, read by `glifo()` in lib.lua): every
number is two characters of the alphabet ALPHABET (base 64, most significant
first), offset by OFFSET so it is never negative:

    advance, contour count, then per contour its point count,
    then every point (x, y), then the triangle count and its vertex indices
    (from 0, over the points in the order written, counter-clockwise).
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import shapely
import shapely.affinity
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.polygon import orient

HERE = Path(__file__).resolve().parent
OUT = HERE / "fonte.lua"

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
OFFSET = 1024  # numbers from -1024 to 3071
TOLERANCE = 1.2  # largest gap between a curve and its chords, font units (1/1000 em)

CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ"
    "áàâãäéèêëíìîïóòôõöúùûüçñ"
    ".,:;-–/\\!?¡¿%()[]+&°ºª'\"=*#@$<>_|"
)


class FlatPen(BasePen):
    """Records the contours of a glyph as point lists, curves flattened to TOLERANCE."""

    def __init__(self, glyphset):
        super().__init__(glyphset)
        self.contours: list[list[tuple[float, float]]] = []
        self.cur: list[tuple[float, float]] = []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        n = segments(p0, p3, max(dist_line(p1, p0, p3), dist_line(p2, p0, p3)) * 0.75)
        for i in range(1, n + 1):
            t = i / n
            u = 1 - t
            self.cur.append((
                u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
            ))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        n = segments(p0, p2, dist_line(p1, p0, p2) * 0.5)
        for i in range(1, n + 1):
            t = i / n
            u = 1 - t
            self.cur.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))

    def _closePath(self):
        if len(self.cur) >= 3:
            self.contours.append(self.cur)
        self.cur = []

    _endPath = _closePath


def dist_line(p, a, b) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    return abs((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / length


def segments(a, b, bulge: float) -> int:
    """Chords for a curve whose control points stand `bulge` off its chord."""
    if bulge <= TOLERANCE:
        return 1
    return max(1, min(24, math.ceil(math.sqrt(bulge / TOLERANCE))))


def glyph_shape(font: TTFont, ch: str):
    """The glyph of `ch` as polygons (even-odd fill) in integer font units, and its advance."""
    cmap = font.getBestCmap()
    name = cmap.get(ord(ch))
    if name is None:
        raise SystemExit(f"the font has no glyph for {ch!r}")
    glyphset = font.getGlyphSet()
    pen = FlatPen(glyphset)
    glyphset[name].draw(pen)
    advance = font["hmtx"][name][0]
    shape = None
    for contour in pen.contours:
        ring = [(round(x), round(y)) for x, y in contour]
        poly = shapely.make_valid(Polygon(ring))
        shape = poly if shape is None else shape.symmetric_difference(poly)
    polys = []
    if shape is not None and not shape.is_empty:
        shape = shape.simplify(0.45, preserve_topology=True)
        for g in getattr(shape, "geoms", [shape]):
            if isinstance(g, Polygon) and g.area > 1:
                polys.append(orient(g, 1.0))
            elif isinstance(g, MultiPolygon):
                polys += [orient(p, 1.0) for p in g.geoms if p.area > 1]
    return polys, advance


def rings_of(poly: Polygon) -> list[list[tuple[int, int]]]:
    out = []
    for ring in [poly.exterior, *poly.interiors]:
        pts = [(round(x), round(y)) for x, y in ring.coords[:-1]]
        clean = []
        for p in pts:
            if not clean or clean[-1] != p:
                clean.append(p)
        if len(clean) > 1 and clean[0] == clean[-1]:
            clean.pop()
        if len(clean) >= 3:
            out.append(clean)
    return out


def triangles_of(poly: Polygon, index: dict) -> list[tuple[int, int, int]]:
    tris = []
    for tri in shapely.constrained_delaunay_triangles(poly).geoms:
        pts = [(round(x), round(y)) for x, y in tri.exterior.coords[:3]]
        try:
            ids = [index[p] for p in pts]
        except KeyError as e:
            raise SystemExit(f"a triangle vertex {e} is not a contour point") from None
        (ax, ay), (bx, by), (cx, cy) = pts
        cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        if cross == 0:
            continue
        if cross < 0:
            ids = [ids[0], ids[2], ids[1]]
        tris.append(tuple(ids))
    return tris


def encode_shape(polys: list[Polygon], advance: int = 0) -> str:
    """Polygons (integer coordinates, oriented) as a figure string: see the module's docstring."""
    rings, tris = [], []
    for poly in polys:
        base = sum(len(r) for r in rings)
        prs = rings_of(poly)
        if not prs:
            continue
        local = {}
        n = base
        for r in prs:
            for p in r:
                local.setdefault(p, n)
                n += 1
        rings += prs
        tris += triangles_of(Polygon(prs[0], prs[1:]), local)
    values = [advance, len(rings), *[len(r) for r in rings]]
    for r in rings:
        for x, y in r:
            values += [x, y]
    values.append(len(tris))
    for t in tris:
        values += list(t)
    return encode(values)


def polygons(shape, scale: float = 1.0) -> list[Polygon]:
    """A shapely shape as oriented polygons with coordinates rounded to integers after `scale`."""
    shape = shapely.affinity.scale(shape, scale, scale, origin=(0, 0))
    shape = shapely.set_precision(shape, 1.0)
    shape = shape.simplify(0.45, preserve_topology=True)
    out = []
    for g in getattr(shape, "geoms", [shape]):
        if isinstance(g, Polygon) and g.area > 1:
            out.append(orient(g, 1.0))
    return out


def encode(values: list[int]) -> str:
    out = []
    for v in values:
        n = v + OFFSET
        if not 0 <= n < 64 * 64:
            raise SystemExit(f"value {v} out of the encodable range")
        out.append(ALPHABET[n // 64] + ALPHABET[n % 64])
    return "".join(out)


def lua_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ttf", required=True, help="IBMPlexSans_Condensed-Bold.ttf")
    opts = ap.parse_args()
    font = TTFont(opts.ttf)
    upm = font["head"].unitsPerEm
    cap = font["OS/2"].sCapHeight
    hpolys, _ = glyph_shape(font, "H")
    hx0, _, hx1, _ = MultiPolygon(hpolys).bounds
    space = font["hmtx"][font.getBestCmap()[32]][0]

    lines = [
        "-- Glyphs of IBM Plex Sans Condensed Bold (SIL Open Font License 1.1, copyright IBM Corp.),",
        "-- as triangulated outlines. Generated by tools/site/fonte.py; do not edit.",
        f"local FONTE = {{ em = {upm}, cap = {cap}, h_width = {round(hx1 - hx0)}, space = {space}, glyphs = {{",
    ]
    total = 0
    for ch in CHARS:
        polys, advance = glyph_shape(font, ch)
        data = encode_shape(polys, advance)
        total += len(data)
        lines.append(f"  [{ord(ch)}] = {lua_string(data)},")
    lines.append("} }")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(HERE.parent.parent)}: {len(CHARS)} glyphs, {total / 1024:.0f} KiB of data")


if __name__ == "__main__":
    main()
