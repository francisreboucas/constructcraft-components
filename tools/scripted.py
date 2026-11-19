#!/usr/bin/env python3
"""Bake the pieces that Lua scripts make, for the web viewer.

    python tools/scripted.py                    bake every component with a script piece
    python tools/scripted.py vehicles/moto-custom ...   only these components

The web viewer's geometry engine runs without Lua, so it cannot draw the pieces
that a component's script pieces return. ConstructCraft can: for each
components/<folder>/<name>.ccomp with a script piece, ccad loads it, removes
the pieces that are not scripts (the viewer draws those itself; voids stay, as
they may cut the scripts' pieces), places each of its types and exports them
to IFC. The meshes of each type are written, one part per material, to
scripted/<folder>/<name>.bin, which the viewer adds to what its engine draws.

scripted/ is not kept in git: the Viewer workflow bakes it before each build,
and so can anyone running the viewer locally. Files of components that no
longer have a script piece are deleted. `ccad` (0.13 or later) is found
through `--ccad`, the CCAD environment variable or the PATH.

The file: b"CCSM", then little-endian u32 format version (1) and u32 length of
a UTF-8 JSON header padded with spaces to a multiple of 4 bytes, the header,
then for each part of each type, in the order the header lists them: its
vertices (f32 x, y, z, meters, in the component's frame), the vertex count of
each face (u32) and the faces' vertex indices (u32, counter-clockwise seen
from outside). The header:

    {"types": [{"index": 0, "name": "...", "parts": [{"name": "...",
      "material": "...", "color": [r, g, b], "transparency": 0.0,
      "vertices": 120, "faces": 64, "indices": 256}]}]}
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build  # noqa: E402  (tools/build.py)

ROOT = build.ROOT
COMPONENTS = build.COMPONENTS
SCRIPTED = ROOT / "scripted"

MAGIC = b"CCSM"
VERSION = 1

# Keeps only the script pieces (and voids), places every type at the origin and
# exports the model to IFC. Doors and windows would need a wall: not supported yet.
LUA = r"""
local cfg = ccad.args.cfg
local loaded = ccad.run("component_load", {path = cfg.path})
local first = loaded.types[1]
local c = ccad.run("component_get", {type = first})
local kind = c.def.kind or "Generic"
if kind == "Door" or kind == "Window" then
  error("scripted " .. kind:lower() .. "s are not supported yet")
end
local scripts, kept = {}, {}
for _, item in ipairs(c.def.items) do
  local script = item.shape and item.shape.Script ~= nil
  if script then
    scripts[#scripts + 1] = {name = item.name, material = item.material or ""}
  end
  if script or item.void then
    kept[#kept + 1] = item
  end
end
-- One change of the definition: removing the pieces one by one resolves the
-- component again each time.
local def = ccad.run("type_get", {type = first}).params.def
def.items = kept
ccad.run("type_set", {type = first, params = {def = def}})
local types = {}
for i, t in ipairs(c.types) do
  ccad.run("component_place", {type = t.name, position = {0, 0}})
  types[i] = t.name
end
local problems = ccad.run("component_get", {type = first}).problems
ccad.run("ifc_export", {path = cfg.ifc})
return {kind = kind, scripts = scripts, types = types, problems = problems}
"""

# --- IFC (STEP) ---------------------------------------------------------------

ENTITY = re.compile(r"#(\d+)\s*=\s*([A-Z0-9_]+)\s*\((.*)\)\s*;\s*$", re.S)


def ifc_string(raw: str) -> str:
    """Decode a STEP string literal (without its quotes)."""
    raw = raw.replace("''", "'")

    def x2(m: re.Match) -> str:
        hexes = m.group(1)
        return "".join(chr(int(hexes[i : i + 4], 16)) for i in range(0, len(hexes), 4))

    raw = re.sub(r"\\X2\\([0-9A-Fa-f]*)\\X0\\", x2, raw)
    raw = re.sub(r"\\X\\([0-9A-Fa-f]{2})", lambda m: bytes([int(m.group(1), 16)]).decode("latin-1"), raw)
    return raw.replace("\\\\", "\\")


def parse_args(text: str) -> list:
    """The arguments of an entity: lists, '#n' references (ints in a tuple), strings, numbers, None ($ and *)."""
    pos = 0

    def value():
        nonlocal pos
        while text[pos] in " \t\r\n":
            pos += 1
        ch = text[pos]
        if ch == "(":
            pos += 1
            out = []
            while True:
                while text[pos] in " \t\r\n":
                    pos += 1
                if text[pos] == ")":
                    pos += 1
                    return out
                out.append(value())
                while text[pos] in " \t\r\n":
                    pos += 1
                if text[pos] == ",":
                    pos += 1
        if ch == "'":
            end = pos + 1
            while True:
                end = text.index("'", end)
                if end + 1 < len(text) and text[end + 1] == "'":
                    end += 2
                    continue
                break
            s = ifc_string(text[pos + 1 : end])
            pos = end + 1
            return s
        if ch == "#":
            m = re.compile(r"#(\d+)").match(text, pos)
            pos = m.end()
            return ("ref", int(m.group(1)))
        if ch in "$*":
            pos += 1
            return None
        if ch == ".":
            end = text.index(".", pos + 1)
            s = text[pos : end + 1]
            pos = end + 1
            return s
        m = re.compile(r"([A-Z0-9_]+)\s*\(").match(text, pos)
        if m:  # a typed value such as IFCLABEL('x'): keep the inner value
            pos = m.end() - 1
            inner = value()
            return inner[0] if len(inner) == 1 else inner
        m = re.compile(r"[-+0-9.Ee]+").match(text, pos)
        if not m:
            raise build.BuildError(f"IFC: cannot read {text[pos:pos + 30]!r}")
        pos = m.end()
        num = m.group(0)
        return float(num) if any(c in num for c in ".Ee") else int(num)

    out = []
    while pos < len(text):
        out.append(value())
        while pos < len(text) and text[pos] in " \t\r\n,":
            pos += 1
    return out


def read_ifc(path: Path) -> dict[int, tuple[str, str]]:
    """Every entity of the DATA section: id -> (type, raw arguments)."""
    text = path.read_text(encoding="latin-1")
    data = text[text.index("DATA;") + 5 : text.rindex("ENDSEC;")]
    entities = {}
    for stmt in re.split(r";\s*\n", data):
        stmt = stmt.strip()
        if not stmt:
            continue
        m = ENTITY.match(stmt + ";")
        if m:
            entities[int(m.group(1))] = (m.group(2), m.group(3))
    return entities


class Ifc:
    def __init__(self, path: Path) -> None:
        self.raw = read_ifc(path)
        self.cache: dict[int, tuple[str, list]] = {}

    def get(self, ref) -> tuple[str, list]:
        n = ref[1] if isinstance(ref, tuple) else ref
        if n not in self.cache:
            kind, args = self.raw[n]
            self.cache[n] = (kind, parse_args(args))
        return self.cache[n]

    def of_kind(self, kind: str) -> list[int]:
        return [n for n, (k, _) in self.raw.items() if k == kind]

    # Placements: a 4x3 matrix as (x axis, y axis, z axis, origin).

    def axis2(self, ref) -> tuple:
        kind, a = self.get(ref)
        if kind != "IFCAXIS2PLACEMENT3D":
            raise build.BuildError(f"IFC: unexpected placement {kind}")
        origin = self.get(a[0])[1][0]
        z = norm(self.get(a[1])[1][0]) if a[1] else (0.0, 0.0, 1.0)
        xr = norm(self.get(a[2])[1][0]) if a[2] else (1.0, 0.0, 0.0)
        x = norm(sub(xr, scale(z, dot(xr, z))))
        y = cross(z, x)
        return (x, y, z, tuple(float(v) for v in origin))

    def placement(self, ref) -> tuple:
        if ref is None:
            return IDENTITY
        kind, a = self.get(ref)
        if kind != "IFCLOCALPLACEMENT":
            raise build.BuildError(f"IFC: unexpected placement {kind}")
        return compose(self.placement(a[0]), self.axis2(a[1]))

    def style_of(self) -> dict[int, tuple[str, list[int], float]]:
        """Styled representation item -> (material name, sRGB 0-255, transparency)."""
        out = {}
        for n in self.of_kind("IFCSTYLEDITEM"):
            item, styles, _ = self.get(n)[1]
            for s in styles or []:
                kind, sa = self.get(s)
                if kind == "IFCPRESENTATIONSTYLEASSIGNMENT":
                    s = sa[0][0]
                    kind, sa = self.get(s)
                if kind != "IFCSURFACESTYLE":
                    continue
                name = sa[0] or ""
                color, transparency = [200, 200, 200], 0.0
                for el in sa[2] or []:
                    ek, ea = self.get(el)
                    if ek in ("IFCSURFACESTYLESHADING", "IFCSURFACESTYLERENDERING"):
                        _, rgb = self.get(ea[0])
                        color = [round(max(0.0, min(1.0, float(v))) * 255) for v in rgb[1:4]]
                        if len(ea) > 1 and isinstance(ea[1], (int, float)):
                            transparency = float(ea[1])
                out[item[1]] = (name, color, transparency)
        return out


IDENTITY = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0))


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def scale(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    a = tuple(float(v) for v in a)
    length = dot(a, a) ** 0.5
    return scale(a, 1 / length) if length > 1e-12 else (0.0, 0.0, 1.0)


def apply(m, p):
    x, y, z, o = m
    return (
        o[0] + x[0] * p[0] + y[0] * p[1] + z[0] * p[2],
        o[1] + x[1] * p[0] + y[1] * p[1] + z[1] * p[2],
        o[2] + x[2] * p[0] + y[2] * p[1] + z[2] * p[2],
    )


def compose(parent, child):
    """parent ∘ child."""
    px, py, pz, po = parent
    rot = lambda v: (  # noqa: E731
        px[0] * v[0] + py[0] * v[1] + pz[0] * v[2],
        px[1] * v[0] + py[1] * v[1] + pz[1] * v[2],
        px[2] * v[0] + py[2] * v[1] + pz[2] * v[2],
    )
    return (rot(child[0]), rot(child[1]), rot(child[2]), apply(parent, child[3]))


# --- Baking -----------------------------------------------------------------------


class Part:
    def __init__(self, name: str, material: str, color: list[int], transparency: float) -> None:
        self.name, self.material, self.color, self.transparency = name, material, color, transparency
        self.vertices: list[tuple[float, float, float]] = []
        self.sizes: list[int] = []
        self.indices: list[int] = []

    def add(self, points: list, faces: list[list[int]]) -> None:
        base = len(self.vertices)
        self.vertices.extend(points)
        for face in faces:
            if len(face) >= 3:
                self.sizes.append(len(face))
                self.indices.extend(base + i for i in face)


def type_parts(ifc: Ifc, product: int, names: dict[str, str], styles: dict) -> list[Part]:
    """The meshes of a placed product, one part per material, in the component's frame."""
    _, args = ifc.get(product)
    frame = ifc.placement(args[5])
    parts: dict[str, Part] = {}
    shape = ifc.get(args[6])[1]
    for rep in shape[2] or []:
        for item in ifc.get(rep)[1][3] or []:
            kind, a = ifc.get(item)
            if kind == "IFCPOLYGONALFACESET":
                coords, faces = a[0], a[2]
                index_map = a[3]
                face_lists = []
                for f in faces:
                    fk, fa = ifc.get(f)
                    if fk != "IFCINDEXEDPOLYGONALFACE":
                        raise build.BuildError(f"IFC: {fk} is not supported")
                    face_lists.append(fa[0])
            elif kind == "IFCTRIANGULATEDFACESET":
                coords, face_lists, index_map = a[0], a[3], a[4] if len(a) > 4 else None
            else:
                raise build.BuildError(f"IFC: {kind} is not supported")
            points = [apply(frame, p) for p in ifc.get(coords)[1][0]]
            if index_map:
                face_lists = [[index_map[i - 1] for i in f] for f in face_lists]
            material, color, transparency = styles.get(item[1], ("", [200, 200, 200], 0.0))
            part = parts.get(material)
            if part is None:
                part = parts[material] = Part(names.get(material, names[""]), material, color, transparency)
            part.add(points, [[i - 1 for i in f] for f in face_lists])
    return list(parts.values())


def write_bin(out: Path, types: list[dict]) -> int:
    header = {"types": []}
    blobs = []
    for t in types:
        entry = {"index": t["index"], "name": t["name"], "parts": []}
        for p in t["parts"]:
            entry["parts"].append(
                {
                    "name": p.name,
                    "material": p.material,
                    "color": p.color,
                    "transparency": p.transparency,
                    "vertices": len(p.vertices),
                    "faces": len(p.sizes),
                    "indices": len(p.indices),
                }
            )
            blobs.append(struct.pack(f"<{3 * len(p.vertices)}f", *(c for v in p.vertices for c in v)))
            blobs.append(struct.pack(f"<{len(p.sizes)}I", *p.sizes))
            blobs.append(struct.pack(f"<{len(p.indices)}I", *p.indices))
        header["types"].append(entry)
    text = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    text += b" " * (-len(text) % 4)
    data = MAGIC + struct.pack("<II", VERSION, len(text)) + text + b"".join(blobs)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".bin.tmp")
    tmp.write_bytes(data)
    tmp.replace(out)
    return len(data)


def bake(exe: str, ccomp: Path, out: Path, tmp: Path) -> tuple[int, int]:
    """Write the baked file of `ccomp`; returns its size and the number of triangles."""
    ifc_path = tmp / "scripted.ifc"
    cfg = {"path": ccomp.resolve().as_posix(), "ifc": ifc_path.resolve().as_posix()}
    got = build.ccad(exe, "lua", "-", "cfg=" + json.dumps(cfg, ensure_ascii=False), stdin=LUA)
    failed = [p for p in got.get("problems") or [] if "script" in json.dumps(p, ensure_ascii=False).lower()]
    if failed:
        raise build.BuildError(f"the script fails: {json.dumps(failed, ensure_ascii=False)}")
    scripts = got["scripts"]
    names = {s["material"]: s["name"] for s in scripts}
    names[""] = scripts[0]["name"] if len(scripts) == 1 else "Script"
    ifc = Ifc(ifc_path)
    styles = ifc.style_of()
    # The placed elements: what has a product shape as its representation.
    shapes = set(ifc.of_kind("IFCPRODUCTDEFINITIONSHAPE"))
    by_name: dict[str, int] = {}
    for n, (kind, raw) in ifc.raw.items():
        refs = {int(r) for r in re.findall(r"#(\d+)", raw)}
        if kind == "IFCPRODUCTDEFINITIONSHAPE" or not refs & shapes:
            continue
        _, args = ifc.get(n)
        if len(args) > 6 and isinstance(args[6], tuple) and args[6][1] in shapes:
            by_name.setdefault(args[2], n)
    types, triangles = [], 0
    for index, name in enumerate(got["types"]):
        if name not in by_name:
            raise build.BuildError(f"the IFC export has no element of type {name!r}")
        parts = type_parts(ifc, by_name[name], names, styles)
        triangles += sum(s - 2 for p in parts for s in p.sizes)
        types.append({"index": index, "name": name, "parts": parts})
    if not triangles:
        raise build.BuildError("the scripts make no 3D pieces")
    return write_bin(out, types), triangles


def has_script(ccomp: Path) -> bool:
    return re.search(r"\bshape:\s*Script\s*\(", ccomp.read_text(encoding="utf-8")) is not None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="components to bake, as <folder>/<name> (default: all with a script piece)")
    ap.add_argument("--ccad", help="path of the ccad executable")
    opts = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    errors: list[str] = []
    try:
        ccomps = {p.relative_to(COMPONENTS).with_suffix("").as_posix(): p for p in sorted(COMPONENTS.rglob("*.ccomp"))}
        unknown = [i for i in opts.ids if i not in ccomps]
        if unknown:
            raise build.BuildError(f"no component named {', '.join(unknown)} (ids are <folder>/<name>)")
        scripted = {k for k, p in ccomps.items() if has_script(p)}
        selected = [k for k in (opts.ids or sorted(scripted)) if k in scripted]
        exe = build.find_ccad(opts.ccad)
        if SCRIPTED.exists():
            for old in sorted(SCRIPTED.rglob("*.bin")):
                key = old.relative_to(SCRIPTED).with_suffix("").as_posix()
                if key not in scripted:
                    old.unlink()
                    print(f"removed {old.relative_to(ROOT).as_posix()}")
        baked, started = 0, time.time()
        with tempfile.TemporaryDirectory() as tmp_name:
            for key in selected:
                t0 = time.time()
                out = SCRIPTED / f"{key}.bin"
                try:
                    size, triangles = bake(exe, ccomps[key], out, Path(tmp_name))
                except (build.BuildError, OSError, KeyError, ValueError) as e:
                    errors.append(f"{key}: {e}")
                    continue
                baked += 1
                print(
                    f"{out.relative_to(ROOT).as_posix()}  {triangles} triangles  {size / 1024:.0f} KiB  {time.time() - t0:.1f}s",
                    flush=True,
                )
        print(f"{baked} baked in {time.time() - started:.0f}s")
    except build.BuildError as e:
        errors.append(str(e))
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
