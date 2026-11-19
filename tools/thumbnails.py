#!/usr/bin/env python3
"""Render a thumbnail of every component.

    python tools/thumbnails.py                 render the missing and stale thumbnails
    python tools/thumbnails.py --all           render every thumbnail again
    python tools/thumbnails.py --check         render nothing; fail if a thumbnail is missing or stale
    python tools/thumbnails.py plumbing/pia-cozinha ...   only these components

Each components/<folder>/<name>.ccomp gets thumbnails/<folder>/<name>.png: a
360x240 PNG of its first type on a white background, seen from above and in
front (the web viewer's iso view) and drawn by ConstructCraft itself: its 3D
view exported as an axonometric in consistent colors (`ccad view_export`).
Doors and windows are placed in a wall that the view hides, so they show alone.

thumbnails/manifest.json keeps the hash of each .ccomp a thumbnail was
rendered from (without its `generator:` line); a thumbnail is up to date when
its PNG exists and the hash matches. Thumbnails of removed components are
deleted. The `thumbnail` fields of catalog.json are then set as tools/build.py
writes them. `ccad` is found through `--ccad`, the CCAD environment variable
or the PATH.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import sys
import tempfile
import time
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build  # noqa: E402  (tools/build.py)

ROOT = build.ROOT
COMPONENTS = build.COMPONENTS
THUMBNAILS = build.THUMBNAILS
MANIFEST = THUMBNAILS / "manifest.json"

WIDTH, HEIGHT = 360, 240
MAX_BYTES = 1_000_000  # the library's consumers refuse images over 1 MB

# The view: the web viewer's iso angle (camera front-right and above: azimuth -50,
# polar 62), as a ConstructCraft 3D view (yaw 0 looks at the front from -Y, a
# negative yaw moves the camera to +X), drawn as an axonometric in consistent
# colors (material colors with dark edges) without shadows.
YAW, PITCH = -40.0, 28.0
FILL = 0.88  # the component fills this much of the width or the height
DPI = 96  # about: the scale is rounded to a whole 1:N, then the dpi fits exactly
SUPERSAMPLE = 2  # drawn this many times larger, then shrunk: smooth edges
PAGE_MARGIN_MM = 5  # view_export's margin around the drawing, on paper

# Loads the component, places its first type (doors and windows in a wall the view
# hides), draws it in a 3D view at 1:10 to measure it, then exports it at the scale
# and dpi that make it `cfg.width` x `cfg.height` pixels at most.
LUA = r"""
local cfg = ccad.args.cfg
local loaded = ccad.run("component_load", {path = cfg.path})
local t = loaded.types[1]
local kind = ccad.run("type_get", {type = t}).params.def.kind or "Generic"
local hidden = {}
if kind == "Door" or kind == "Window" then
  local wall = ccad.run("wall_create", {start = {-8, 0}, ["end"] = {8, 0}, height = 6})
  ccad.run(kind == "Door" and "door_create" or "window_create", {wall = wall.id, type = t})
  hidden = {wall.id}
else
  ccad.run("component_place", {type = t, position = {0, 0}})
end
ccad.run("view_create", {kind = "three_d", name = "thumbnail"})
if #hidden > 0 then
  ccad.run("element_hide_in_view", {view = "thumbnail", ids = hidden})
end
ccad.run("view_set", {
  view = "thumbnail", visual_style = "consistent_colors", shading = {shadow = 0}, detail = "fine", scale = 10,
  params = {camera = {target = {0, 0, 0}, distance = 10, yaw_deg = cfg.yaw, pitch_deg = cfg.pitch}},
})
local probe = ccad.run("view_export", {view = "thumbnail", path = cfg.svg})
local w = (probe.paper_mm[1] - 2 * cfg.margin_mm) * 10 / 1000
local h = (probe.paper_mm[2] - 2 * cfg.margin_mm) * 10 / 1000
if w <= 0 or h <= 0 then
  error("the component draws nothing in a 3D view")
end
local ppm = math.min(cfg.width / w, cfg.height / h) -- pixels per meter
local scale = math.max(1, math.floor(cfg.dpi * 1000 / (25.4 * ppm) + 0.5))
local dpi = ppm * 25.4 * scale / 1000
ccad.run("view_set", {view = "thumbnail", scale = scale})
local png = ccad.run("view_export", {view = "thumbnail", path = cfg.png, dpi = dpi})
return {kind = kind, scale = scale, dpi = dpi, pixels = png.pixels}
"""

# --- PNG ------------------------------------------------------------------------


def png_size(path: Path) -> tuple[int, int]:
    """Width and height from the IHDR chunk."""
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise build.BuildError(f"{path.name} is not a PNG")
    return struct.unpack(">II", head[16:24])


def png_rows(path: Path) -> tuple[int, int, int, list[bytes]]:
    """Decode an 8-bit grey, RGB or RGBA PNG: width, height, bytes per pixel and the rows."""
    data = path.read_bytes()
    pos, idat, ihdr = 8, [], None
    while pos < len(data):
        (n,) = struct.unpack(">I", data[pos : pos + 4])
        kind, body = data[pos + 4 : pos + 8], data[pos + 8 : pos + 8 + n]
        pos += 12 + n
        if kind == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat.append(body)
    if not ihdr or ihdr[2] != 8 or ihdr[3] not in (0, 2, 4, 6) or ihdr[6]:
        raise build.BuildError(f"{path.name}: unsupported PNG")
    w, h, ctype = ihdr[0], ihdr[1], ihdr[3]
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f, line = raw[i], bytearray(raw[i + 1 : i + 1 + stride])
        i += 1 + stride
        if f == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                line[x] = (line[x] + ((line[x - bpp] if x >= bpp else 0) + prev[x]) // 2) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b, c = prev[x], prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line))
        prev = line
    return w, h, bpp, rows


def png_write(path: Path, rows: list[bytes], width: int, height: int) -> None:
    """Write 8-bit RGB rows as a PNG."""
    chunk = lambda kind, body: struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))  # noqa: E731
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def rgb_rows(path: Path) -> tuple[int, int, list[bytes]]:
    """A PNG's pixels as RGB rows, transparency composited over white."""
    w, h, bpp, rows = png_rows(path)
    if bpp == 3:
        return w, h, rows
    out = []
    for row in rows:
        px = bytearray(w * 3)
        for x in range(w):
            p = row[x * bpp : (x + 1) * bpp]
            rgb, a = (p[:3], p[3]) if bpp == 4 else ((p[0],) * 3, p[1] if bpp == 2 else 255)
            px[x * 3 : x * 3 + 3] = bytes((c * a + 255 * (255 - a)) // 255 for c in rgb)
        out.append(bytes(px))
    return w, h, out


def center_on_canvas(src: Path, out: Path) -> None:
    """Shrink the drawing of `src` (what is not white) by SUPERSAMPLE and center it on a white WIDTH x HEIGHT PNG."""
    _, _, rows = rgb_rows(src)
    inked = [(y, len(r) - len(r.lstrip(b"\xff")), len(r.rstrip(b"\xff"))) for y, r in enumerate(rows) if r.strip(b"\xff")]
    if not inked:
        raise build.BuildError("the drawing is empty")
    n = SUPERSAMPLE
    y0, y1 = inked[0][0], inked[-1][0]
    x0, x1 = min(i[1] for i in inked) // 3, (max(i[2] for i in inked) - 1) // 3
    bw, bh = -(-(x1 - x0 + 1) // n), -(-(y1 - y0 + 1) // n)  # the inked box in thumbnail pixels
    if bw > WIDTH or bh > HEIGHT:
        raise build.BuildError(f"the drawing is {bw}x{bh} pixels, larger than {WIDTH}x{HEIGHT}")
    block = [(rows[y][x0 * 3 : x0 * 3 + bw * n * 3] if y <= y1 else b"").ljust(bw * n * 3, b"\xff") for y in range(y0, y0 + bh * n)]
    left, top = (WIDTH - bw) // 2, (HEIGHT - bh) // 2
    canvas = [bytearray(b"\xff" * WIDTH * 3) for _ in range(HEIGHT)]
    for j in range(bh):
        sums = [sum(v) for v in zip(*block[j * n : (j + 1) * n])]  # the n rows added up
        line = bytearray(bw * 3)
        for c in range(3):
            cols = [sums[c + 3 * k :: 3 * n] for k in range(n)]
            line[c::3] = bytes((sum(v) + n * n // 2) // (n * n) for v in zip(*cols))
        canvas[top + j][left * 3 : (left + bw) * 3] = line
    png_write(out, canvas, WIDTH, HEIGHT)


def render(exe: str, ccomp: Path, out: Path, tmp: Path) -> dict:
    """Draw the thumbnail of `ccomp` to `out`; returns what ccad reports."""
    drawing, image = tmp / "drawing.png", tmp / "thumbnail.png"
    cfg = {
        "path": ccomp.resolve().as_posix(),
        "svg": (tmp / "probe.svg").resolve().as_posix(),
        "png": drawing.resolve().as_posix(),
        "yaw": YAW,
        "pitch": PITCH,
        "width": WIDTH * FILL * SUPERSAMPLE,
        "height": HEIGHT * FILL * SUPERSAMPLE,
        "dpi": DPI * SUPERSAMPLE,
        "margin_mm": PAGE_MARGIN_MM,
    }
    got = build.ccad(exe, "lua", "-", "cfg=" + json.dumps(cfg, ensure_ascii=False), stdin=LUA)
    center_on_canvas(drawing, image)
    check_png(image)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(image), str(out))
    return got


def check_png(path: Path) -> None:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise build.BuildError(f"{path.name} is {size} bytes, over the {MAX_BYTES} allowed")
    if png_size(path) != (WIDTH, HEIGHT):
        raise build.BuildError(f"{path.name} is {'x'.join(map(str, png_size(path)))}, not {WIDTH}x{HEIGHT}")

# --- Bookkeeping ------------------------------------------------------------------


def source_hash(ccomp: Path) -> str:
    """sha256 of the .ccomp without its generator line, with \\n newlines on every system."""
    return hashlib.sha256(build.without_generator(ccomp.read_text(encoding="utf-8")).encode("utf-8")).hexdigest()


def load_manifest() -> dict[str, str]:
    if not MANIFEST.exists():
        return {}
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise build.BuildError(f"{MANIFEST.relative_to(ROOT).as_posix()}: {e}") from None
    return {k: v for k, v in data.items() if isinstance(v, str)}


def write_manifest(manifest: dict[str, str]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != text:
        MANIFEST.write_text(text, encoding="utf-8", newline="\n")


def update_catalog() -> bool:
    """Set the `thumbnail` fields of catalog.json from the PNGs on disk; True if it changed."""
    if not build.CATALOG_JSON.exists():
        return False
    old = build.CATALOG_JSON.read_text(encoding="utf-8")
    data = json.loads(old)
    data["components"] = [build.with_thumbnail(e) for e in data["components"]]
    new = build.catalog_json_text(data["components"])
    if new == old:
        return False
    build.CATALOG_JSON.write_text(new, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="components to consider, as <folder>/<name> (default: all)")
    ap.add_argument("--all", action="store_true", help="render again even the thumbnails that are up to date")
    ap.add_argument("--check", action="store_true", help="render nothing; fail if a thumbnail is missing or stale")
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
        selected = opts.ids or list(ccomps)
        manifest = load_manifest()
        pngs = {p.relative_to(THUMBNAILS).with_suffix("").as_posix(): p for p in sorted(THUMBNAILS.rglob("*.png"))}
        orphans = sorted((set(pngs) | set(manifest)) - set(ccomps))

        def thumb(key: str) -> Path:
            return THUMBNAILS / f"{key}.png"

        def state(key: str) -> str | None:
            if not thumb(key).exists():
                return "missing"
            if manifest.get(key) != source_hash(ccomps[key]):
                return "stale"
            return None

        if opts.check:
            problems = [f"{thumb(k).relative_to(ROOT).as_posix()} is {s}" for k in selected if (s := state(k))]
            for k in selected:
                if thumb(k).exists():
                    try:
                        check_png(thumb(k))
                    except build.BuildError as e:
                        problems.append(f"{thumb(k).relative_to(ROOT).as_posix()}: {e}")
            problems += [f"{thumb(k).relative_to(ROOT).as_posix()} has no component" for k in orphans]
            for p in problems:
                print(f"error: {p}: run tools/thumbnails.py", file=sys.stderr)
            if problems:
                return 1
            print(f"{len(selected)} thumbnails up to date")
            return 0

        exe = build.find_ccad(opts.ccad)
        for key in orphans:
            if key in pngs:
                pngs[key].unlink()
            manifest.pop(key, None)
            print(f"removed {thumb(key).relative_to(ROOT).as_posix()}")
        for folder in sorted(THUMBNAILS.glob("*/"), reverse=True):
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()

        todo = [k for k in selected if opts.all or state(k)]
        rendered, started = 0, time.time()
        with tempfile.TemporaryDirectory() as tmp_name:
            for key in todo:
                t0 = time.time()
                try:
                    got = render(exe, ccomps[key], thumb(key), Path(tmp_name))
                except (build.BuildError, OSError) as e:
                    errors.append(f"{key}: {e}")
                    continue
                manifest[key] = source_hash(ccomps[key])
                rendered += 1
                size = thumb(key).stat().st_size
                print(
                    f"{thumb(key).relative_to(ROOT).as_posix()}  1:{got['scale']}  {size / 1024:.0f} KiB  {time.time() - t0:.1f}s",
                    flush=True,
                )
        total = time.time() - started
        write_manifest(manifest)
        catalog = update_catalog()
        print(
            f"{rendered} rendered in {total:.0f}s, {len(selected) - len(todo)} up to date, {len(orphans)} removed"
            + ("; catalog.json updated" if catalog else "")
        )
    except build.BuildError as e:
        errors.append(str(e))
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
