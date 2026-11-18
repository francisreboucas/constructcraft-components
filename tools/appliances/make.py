#!/usr/bin/env python3
"""Write an appliance's source, build its .ccomp and render previews.

    python tools/appliances/make.py lava_loucas --ccad path/to/ccad --out previews/
    python tools/appliances/make.py --all --ccad path/to/ccad --no-preview

Each module of this folder (other than kit and make) has a `build()` returning
a `kit.Component`. The source goes to sources/<folder>/<file>.json and the
component to components/<folder>/<file>.ccomp. With --out, the first type is
placed closed and open, and the second type beside them, and the views are
written as PNG files: renders from the front and the back, the front
elevation and the plan at fine detail, and the coarse 3D view.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(HERE), str(HERE.parent)]

import build as library  # noqa: E402  (tools/build.py)


def modules() -> list[str]:
    return sorted(f.stem for f in HERE.glob("*.py") if f.stem not in ("kit", "make") and not f.stem.startswith("_"))


def write_source(comp) -> tuple[dict, Path]:
    src = comp.source()
    if comp.file != comp.file.lower() or "_" in comp.file or " " in comp.file or not comp.file.isascii():
        raise library.BuildError(f"file name {comp.file!r}: lowercase ASCII with hyphens")
    path = ROOT / "sources" / comp.folder / f"{comp.file}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return src, path


def build_component(exe: str, src: dict, out: Path, template_materials: set[str]):
    out.parent.mkdir(parents=True, exist_ok=True)
    script = library.build_script(src, out.resolve(), template_materials)
    library.ccad(exe, "script", "-", stdin="\n".join(json.dumps(s, ensure_ascii=False) for s in script))


def stats(src: dict) -> str:
    items = src["def"]["items"]
    shapes = Counter(next(iter(i["shape"])) for i in items)
    level = Counter()
    for i in items:
        d = i.get("detail", {"coarse": True, "medium": True, "fine": True})
        for k in ("coarse", "medium", "fine"):
            level[k] += d[k]
    return (
        f"{len(items)} pieces ({', '.join(f'{k} {v}' for k, v in sorted(shapes.items()))}); "
        f"coarse {level['coarse']}, medium {level['medium']}, fine {level['fine']}; "
        f"{len(src['materials'])} materials, {len(src['types'])} types"
    )


def size_of(comp, values: dict) -> tuple[float, float, float]:
    """Rough width, depth and height of a type, to aim the preview cameras."""
    if getattr(comp, "preview_size", None):
        return comp.preview_size
    v = {q["name"]: q["value"] for q in comp.params} | values
    w = v.get("Largura") or v.get("Diametro") or 0.6
    d = v.get("Profundidade") or w
    h = v.get("Altura") or w
    return w, d, h


def preview(exe: str, comp, src: dict, ccomp: Path, out: Path, tmp: Path, samples: int):
    out.mkdir(parents=True, exist_ok=True)
    project = tmp / f"{comp.file}.ccad"
    library.ccad(exe, "--save-as", str(project), "run", "component_load", f"path={ccomp.resolve()}")
    types = src["types"]
    w, d, h = size_of(comp, {})
    reach = max(w, d, h)
    gap = max(2.0, 3 * reach)
    # Where each instance stands: the first type closed, open, and the second type.
    spots = {"closed": 0.0}
    steps = []
    hosted = {"Door": "door_create", "Window": "window_create"}.get(comp.kind)
    if hosted:
        gap = w + 1.2
    scale = 25 if hosted else (5 if reach < 1.3 else 10)  # of the line drawings
    if hosted:  # doors and windows stand in a wall along X
        steps.append({"command": "wall_create", "args": {"start": [-gap, 0], "end": [3 * gap, 0], "height": 3}})

    def place(type_name: str, x: float):
        if hosted:
            steps.append({"command": hosted, "args": {"type": type_name, "wall": {"$step": 1}, "offset": x + gap}})
        else:
            steps.append({"command": "component_place", "args": {"type": type_name, "position": [x, 0]}})

    place(types[0]["name"], 0)
    if comp.open_pose:
        spots["open"] = gap
        place(types[0]["name"], gap)
        placed = len(steps)
        for name, value in comp.open_pose.items():
            steps.append({"command": "component_params_set", "args": {"elements": [{"$step": placed}], "name": name, "value": value}})
    if len(types) > 1:
        spots["type2"] = 2 * gap
        place(types[1]["name"], 2 * gap)

    base = getattr(comp, "preview_base", 0.0)  # z of the bottom of what is drawn (ceiling pieces: negative)
    files = []

    def shot(name: str, x: float, yaw: float, pitch: float, size, render: bool = True, detail: str = "fine"):
        sw, sd, sh = size
        view = f"prev-{name}"
        camera = {"target": [x, 0, base + sh / 2], "distance": 1.9 * max(sw, sd, sh) + 0.35, "yaw_deg": yaw, "pitch_deg": pitch}
        steps.append({"command": "view_create", "args": {"kind": "three_d", "name": view}})
        steps.append({"command": "view_set", "args": {"view": view, "detail": detail, "scale": scale, "params": {"camera": camera}}})
        path = out / f"{comp.file}-{name}.png"
        if render:
            settings = {"samples": samples, "width": 960, "height": 760}
            steps.append({"command": "view_render", "args": {"view": view, "path": str(path), "settings": settings}})
        else:
            steps.append({"command": "view_export", "args": {"view": view, "path": str(path), "dpi": 150}})
        files.append(path)

    shot("front", spots["closed"], FRONT_YAW, 22, (w, d, h))
    shot("back", spots["closed"], FRONT_YAW + 180, 22, (w, d, h))
    shot("coarse", spots["closed"], FRONT_YAW, 22, (w, d, h), render=False, detail="coarse")
    shot("medium", spots["closed"], FRONT_YAW, 22, (w, d, h), render=False, detail="medium")
    if "open" in spots:
        shot("open", spots["open"], FRONT_YAW, 30, (w, d + 0.5 * reach, h))
        shot("open-lines", spots["open"], FRONT_YAW - 35, 35, (w, d + 0.5 * reach, h), render=False)
    if "type2" in spots:
        shot("type2", spots["type2"], FRONT_YAW, 22, size_of(comp, types[1]["values"]))
    for name, kind, extra in (("elevation", "elevation", {"direction": "south"}), ("plan", "floor_plan", {})):
        view = f"prev-{name}"
        steps.append({"command": "view_create", "args": {"kind": kind, "name": view, "scale": 2 * scale, **extra}})
        steps.append({"command": "view_set", "args": {"view": view, "detail": "fine"}})
        path = out / f"{comp.file}-{name}.png"
        steps.append({"command": "view_export", "args": {"view": view, "path": str(path), "dpi": 110}})
        files.append(path)

    library.ccad(exe, "-p", str(project), "script", "-", stdin="\n".join(json.dumps(s, ensure_ascii=False) for s in steps))
    return files


# Yaw of the camera that looks at the front (-Y) of a component from its right.
FRONT_YAW = -30.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modules", nargs="*", help="modules to make (see --all)")
    ap.add_argument("--all", action="store_true", help="every module of the folder")
    ap.add_argument("--ccad", help="path of the ccad executable")
    ap.add_argument("--out", help="folder of the preview images (no previews without it)")
    ap.add_argument("--samples", type=int, default=24, help="samples per pixel of the renders")
    opts = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    names = modules() if opts.all else opts.modules
    if not names:
        ap.error("name a module or pass --all")
    try:
        exe = library.find_ccad(opts.ccad)
        template_materials = {m["name"] for m in library.ccad(exe, "run", "materials_list")}
        with tempfile.TemporaryDirectory() as tmp_name:
            for name in names:
                comp = importlib.import_module(name).build()
                src, path = write_source(comp)
                ccomp = ROOT / "components" / comp.folder / f"{comp.file}.ccomp"
                try:
                    build_component(exe, src, ccomp, template_materials)
                except library.BuildError as err:
                    raise library.BuildError(f"{path.relative_to(ROOT)}: {err}") from None
                print(f"{ccomp.relative_to(ROOT).as_posix()}: {stats(src)}")
                if opts.out:
                    for f in preview(exe, comp, src, ccomp, Path(opts.out), Path(tmp_name), opts.samples):
                        print(f"  {f}")
        return 0
    except (library.BuildError, ValueError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
