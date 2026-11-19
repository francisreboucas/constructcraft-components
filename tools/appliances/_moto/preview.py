#!/usr/bin/env python3
"""Preview the custom motorcycle from any side, without touching sources/ or components/.

    python tools/appliances/_moto/preview.py --ccad <exe> --out previews/moto_<who>
        [--parts chassi,motor,carroceria] [--steer 25] [--stand 1] [--detail fine|medium|coarse]
        [--views left,right,front34,rear34,top,front,rear] [--lines side,plan] [--close front_wheel,engine,...]
        [--samples 32] [--width 1280] [--height 800]

Builds the component from the selected part builders (moto_custom.build(parts)) into a .ccomp
in a temporary folder, places it once with the given steering and stand, and writes:
renders `moto-<view>.png` (left = rider's left, +X), line drawings `moto-lines-<name>.png`
(side elevations from both sides, the plan) and close-ups `moto-close-<region>.png`.
Close-up regions: front_wheel, rear_wheel, fork, cockpit, engine, tail, stand, pivot,
front_brake, rear_brake, belt, pulley, headlight, speedo, mirror, underseat, lpeg, rpeg, rear_hose. `--views none`, `--lines none` skip a group. It prints the piece
counts, the .ccomp size and the times taken.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent  # tools/appliances/_moto
APPLIANCES = HERE.parent
sys.path[:0] = [str(APPLIANCES), str(APPLIANCES.parent)]

import build as library  # noqa: E402  (tools/build.py)
import make  # noqa: E402  (tools/appliances/make.py: stats())
import moto_custom  # noqa: E402
from _moto.base import HP, v_add  # noqa: E402

# Camera yaw: 0 looks at the front (camera at -Y), 90 from the rider's right (-X), -90 from the left (+X).
VIEWS = {
    "left": (-90, 3, (0, 0.02, 0.56), 3.15),
    "right": (90, 3, (0, 0.02, 0.56), 3.15),
    "front34": (-38, 16, (0, -0.05, 0.52), 3.3),
    "rear34": (142, 16, (0, 0.05, 0.52), 3.3),
    "top": (-90, 89, (0, 0.02, 0.4), 3.6),
    "front": (0, 5, (0, 0, 0.6), 2.6),
    "rear": (180, 5, (0, 0, 0.6), 2.6),
}


def close_ups():
    fa, ra = HP.FRONT_AXLE, HP.REAR_AXLE
    return {
        "front_wheel": (-62, 8, fa, 1.45),
        "rear_wheel": (-118, 8, ra, 1.45),
        "fork": (-55, 12, HP.fork(0, HP.OFFSET, 0.45), 1.5),
        "cockpit": (-150, 38, v_add(HP.BAR_CLAMP, (0, 0.05, -0.05)), 1.25),
        "engine": (-90, 6, (0, -0.05, 0.42), 1.5),
        "tail": (-130, 18, (0, 0.85, 0.5), 1.4),
        "stand": (-50, 12, (0.25, -0.12, 0.12), 0.9),
        "pivot": (-110, 10, (0.15, 0.32, 0.33), 0.8),
        "front_brake": (-80, 4, v_add(fa, (0.05, 0.08, 0.0)), 0.7),
        "rear_brake": (80, 4, v_add(ra, (-0.08, -0.02, 0.0)), 0.8),
        "belt": (-90, 4, (0.12, 0.33, 0.32), 0.95),
        "pulley": (-128, 24, (0.13, 0.24, 0.31), 0.6),
        "headlight": (-22, 4, HP.HEADLIGHT, 0.6),
        "speedo": (180, 42, HP.fork(0, 0.085, 0.885), 0.42),
        "mirror": (160, 12, v_add(HP.GRIP_L[0], (0.06, 0.03, 0.17)), 0.55),
        "underseat": (-90, 4, (0.16, 0.36, 0.50), 0.8),
        "lpeg": (-60, 15, (0.25, -0.40, 0.32), 0.7),
        "rpeg": (60, 15, (-0.25, -0.40, 0.32), 0.7),
        "rear_hose": (90, 6, (-0.15, 0.25, 0.25), 1.2),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ccad", required=True, help="path of the ccad executable")
    ap.add_argument("--out", required=True, help="folder of the images")
    ap.add_argument("--parts", default="chassi,motor,carroceria", help="part builders to include (missing ones are skipped)")
    ap.add_argument("--steer", type=float, default=0.0, help="AnguloGuidao, degrees")
    ap.add_argument("--stand", type=float, default=0.0, help="Descanso, 0 (up) to 1 (down)")
    ap.add_argument("--detail", default="fine", choices=("fine", "medium", "coarse"))
    ap.add_argument("--views", default=",".join(VIEWS), help="renders, or none")
    ap.add_argument("--lines", default="side,plan", help="line drawings: side (both sides), plan; or none")
    ap.add_argument("--close", default="", help="close-up regions (see the docstring), or all")
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=800)
    ap.add_argument("--fov", type=float, default=32.0)
    ap.add_argument("--keep", help="also copy the built .ccomp here")
    opts = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    exe = library.find_ccad(opts.ccad)
    out = Path(opts.out)
    out.mkdir(parents=True, exist_ok=True)
    parts = [p for p in opts.parts.split(",") if p]

    t0 = time.time()
    comp = moto_custom.build(parts)
    src = comp.source()
    t_py = time.time() - t0
    lua = next((i["shape"]["Script"]["source"] for i in src["def"]["items"] if "Script" in i["shape"]), "")
    print(f"parts {parts}: {make.stats(src)}")
    ls = comp.lua_stats
    print(f"  script pieces {ls['pieces']} (coarse {ls['coarse']}, medium {ls['medium']}, fine {ls['fine']}), "
          f"{ls['vertices']} vertices, Lua source {len(lua.encode('utf-8')) / 1024:.1f} KiB; "
          f"static mesh vertices {comp.mesh_vertices}; python {t_py:.1f}s")

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        ccomp = tmp / "moto-custom.ccomp"
        template_materials = {m["name"] for m in library.ccad(exe, "run", "materials_list")}
        script = library.build_script(src, ccomp.resolve(), template_materials)
        t1 = time.time()
        library.ccad(exe, "script", "-", stdin="\n".join(json.dumps(s, ensure_ascii=False) for s in script))
        t_build = time.time() - t1
        size = ccomp.stat().st_size
        print(f"  .ccomp {size / 1024:.0f} KiB, built in {t_build:.1f}s")
        if opts.keep:
            Path(opts.keep).write_bytes(ccomp.read_bytes())
        project = tmp / "moto.ccad"
        t2 = time.time()
        library.ccad(exe, "--save-as", str(project), "run", "component_load", f"path={ccomp.resolve()}")
        t_load = time.time() - t2
        steps = [{"command": "component_place", "args": {"type": src["types"][0]["name"], "position": [0, 0]}}]
        for name, value in (("AnguloGuidao", opts.steer), ("Descanso", opts.stand)):
            if value:
                steps.append({"command": "component_params_set", "args": {"elements": [{"$step": 1}], "name": name, "value": value}})
        steps.append({"command": "element_get", "args": {"id": {"$step": 1}}})
        get_step = len(steps)
        files = []
        suffix = "" if opts.detail == "fine" else f"-{opts.detail}"
        render = {"samples": opts.samples, "width": opts.width, "height": opts.height, "fov_deg": opts.fov}

        def shot(label, yaw, pitch, target, dist, size=None):
            view = f"moto-{label}"
            camera = {"target": list(target), "distance": dist, "yaw_deg": yaw, "pitch_deg": pitch}
            steps.append({"command": "view_create", "args": {"kind": "three_d", "name": view}})
            steps.append({"command": "view_set", "args": {"view": view, "detail": opts.detail, "params": {"camera": camera}}})
            path = out / f"{view}{suffix}.png"
            settings = dict(render)
            if size:
                settings["width"], settings["height"] = size
            steps.append({"command": "view_render", "args": {"view": view, "path": str(path.resolve()), "settings": settings}})
            files.append(path)

        names = [] if opts.views == "none" else [v for v in opts.views.split(",") if v]
        for v in names:
            yaw, pitch, target, dist = VIEWS[v]
            shot(v, yaw, pitch, target, dist * 32.0 / opts.fov)
        regions = close_ups()
        wanted = list(regions) if opts.close == "all" else [r for r in opts.close.split(",") if r]
        for r in wanted:
            yaw, pitch, target, dist = regions[r]
            shot(f"close-{r}", yaw, pitch, target, dist * 32.0 / opts.fov, (1024, 800))
        lines = [] if opts.lines == "none" else [x for x in opts.lines.split(",") if x]
        drawings = []
        if "side" in lines:
            drawings += [("lines-left", "elevation", {"direction": "east"}), ("lines-right", "elevation", {"direction": "west"})]
        if "plan" in lines:
            drawings.append(("lines-plan", "floor_plan", {}))
        if "front" in lines:
            drawings.append(("lines-front", "elevation", {"direction": "south"}))
        for label, kind, extra in drawings:
            view = f"moto-{label}"
            steps.append({"command": "view_create", "args": {"kind": kind, "name": view, "scale": 15, **extra}})
            crop = {"floor_plan": [[-0.75, -1.45], [0.75, 1.45]]}.get(kind, [[-1.45, -0.08], [1.45, 1.45]])
            steps.append({"command": "view_set", "args": {"view": view, "detail": opts.detail, "crop": crop}})
            path = out / f"{view}{suffix}.png"
            steps.append({"command": "view_export", "args": {"view": view, "path": str(path.resolve()), "dpi": 200}})
            files.append(path)
        t3 = time.time()
        res = library.ccad(exe, "-p", str(project), "script", "-", stdin="\n".join(json.dumps(s, ensure_ascii=False) for s in steps))
        t_views = time.time() - t3
        got = res[get_step - 1]["result"]
        errors = got.get("derived", {}).get("script_errors")
        if errors:
            print(f"  SCRIPT ERRORS: {errors}")
        renders = [s["result"] for s in res if isinstance(s.get("result"), dict) and "triangles" in s["result"]]
        if renders:
            tri = renders[0]["triangles"]
            secs = sum(r["seconds"] for r in renders)
            print(f"  load {t_load:.1f}s; {len(renders)} renders, {tri} triangles, {secs:.0f}s rendering; all views {t_views:.0f}s")
        for f in files:
            print(f"  {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
