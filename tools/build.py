#!/usr/bin/env python3
"""Build, validate and index the component library.

    python tools/build.py            build sources/ into components/, validate, write the catalog
    python tools/build.py --check    fail if anything is invalid or out of date (CI)

Every .ccomp is produced and checked by ConstructCraft itself (`ccad`), so the
files always match the format the app reads. `ccad` is found through
`--ccad`, the CCAD environment variable or the PATH.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
COMPONENTS = ROOT / "components"
CATALOG_JSON = ROOT / "catalog.json"
CATALOG_MD = ROOT / "CATALOG.md"
AUTHORS_JSON = ROOT / "authors.json"
THUMBNAILS = ROOT / "thumbnails"  # rendered by tools/thumbnails.py

# Folder → heading in CATALOG.md, in display order.
SECTIONS = {
    "furniture": "Mobiliário · Furniture",
    "casework": "Marcenaria · Casework",
    "plumbing": "Hidrossanitário · Plumbing",
    "electrical": "Elétrico · Electrical",
    "lighting": "Iluminação · Lighting",
    "planting": "Paisagismo · Planting",
    "doors": "Portas · Doors",
    "windows": "Janelas · Windows",
    "vehicles": "Veículos · Vehicles",
    "site": "Área externa · Site",
    "signage": "Sinalização · Signage",
}


# Parameter kinds whose value is the `text` of the parameter, not its number.
TEXT_KINDS = {"Text", "Choice", "Material"}


def param_value(p: dict):
    """A parameter's value as the catalog lists it: its text for texts, choices and materials."""
    if p.get("kind") in TEXT_KINDS:
        return p.get("text", "")
    if p.get("kind") == "Boolean":
        return bool(p["value"])
    return p["value"]


class BuildError(Exception):
    pass


def find_ccad(arg: str | None) -> str:
    exe = arg or os.environ.get("CCAD") or shutil.which("ccad")
    if not exe or not Path(exe).exists() and not shutil.which(exe):
        raise BuildError("ccad not found: pass --ccad, set CCAD or put ccad on the PATH")
    return exe


def ccad(exe: str, *args: str, stdin: str | None = None) -> object:
    """Run ccad and return its JSON output."""
    proc = subprocess.run(
        [exe, "--lang", "pt-BR", *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise BuildError((proc.stderr or proc.stdout).strip())
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def type_get_all(exe: str, ids: list[int], *opts: str) -> list[dict]:
    """`type_get` of several types in one ccad run."""
    script = "\n".join(json.dumps({"command": "type_get", "args": {"type": i}}) for i in ids)
    return [step["result"] for step in ccad(exe, *opts, "script", "-", stdin=script)]


def build_script(src: dict, out: Path, existing_materials: set[str]) -> list[dict]:
    """Engine commands that create the component of `src` and save it to `out`."""
    types = src["types"]
    params = src["def"].get("params", [])

    def def_with(values: dict) -> dict:
        unknown = set(values) - {p["name"] for p in params}
        if unknown:
            raise BuildError(f"type values for unknown parameters: {', '.join(sorted(unknown))}")
        d = json.loads(json.dumps(src["def"]))
        for p in d.get("params", []):
            if p["name"] not in values:
                continue
            v = values[p["name"]]
            if p.get("kind") in TEXT_KINDS:
                p["text"] = v  # a text, a choice's key or a material's name
            elif p.get("kind") == "Boolean":
                p["value"] = 1.0 if v else 0.0
            else:
                p["value"] = v
        return d

    # A .ccomp keeps one number per parameter for each type; texts, choices and materials
    # are the definition's, shared by every type (each placed element may still change them).
    kinds = {p["name"]: p.get("kind") for p in params}
    for t in types:
        shared = sorted(n for n in t.get("values", {}) if kinds.get(n) in TEXT_KINDS)
        if shared:
            raise BuildError(f"type {t['name']!r}: {', '.join(shared)} cannot change by type "
                             "(texts, choices and materials are shared by every type); set them in the definition")

    steps = []
    for m in src.get("materials", []):
        if m["name"] in existing_materials:
            continue
        steps.append({"command": "material_create", "args": {"name": m["name"], "color": m["color"]}})
        # Optional fields beyond the color: what kind of material it is and how it looks.
        values: dict = {}
        if "class" in m:
            values["identity"] = {"class": m["class"]}
        if "finish" in m:
            values["appearance"] = {"finish": m["finish"]}
        if m.get("transparency"):
            values["graphics"] = {"transparency": m["transparency"]}
        if values:
            steps.append({"command": "material_set", "args": {"material": m["name"], "values": values}})
    first = types[0]
    steps.append({"command": "component_create", "args": {"name": src["component"], "def": def_with(first.get("values", {}))}})
    steps.append({"command": "type_set", "args": {"type": src["component"], "name": first["name"], "info": first.get("info", {})}})
    for t in types[1:]:
        steps.append({"command": "type_duplicate", "args": {"type": first["name"], "name": t["name"]}})
        steps.append({
            "command": "type_set",
            "args": {"type": t["name"], "params": {"def": def_with(t.get("values", {}))}, "info": t.get("info", {})},
        })
    steps.append({"command": "component_save", "args": {"component": src["component"], "path": str(out)}})
    return steps


def build(exe: str, out_root: Path) -> list[Path]:
    template_materials = {m["name"] for m in ccad(exe, "run", "materials_list")}
    # Names are resolved by name in the script, so they must not repeat the template's.
    ids = [t["id"] for c in ("component", "door", "window") for t in ccad(exe, "run", "types_list", f"category={c}")]
    got = type_get_all(exe, ids)
    template_types = {t["name"] for t in got} | {t["params"]["component"] for t in got if "component" in t["params"]}
    built = []
    for path in sorted(SOURCES.rglob("*.json")):
        rel = path.relative_to(SOURCES).with_suffix(".ccomp")
        out = out_root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            src = json.loads(path.read_text(encoding="utf-8"))
            taken = template_types & ({src["component"]} | {t["name"] for t in src["types"]})
            if taken:
                raise BuildError(f"names already used by the ConstructCraft template: {', '.join(sorted(taken))}")
            script = build_script(src, out.resolve(), template_materials)
            ccad(exe, "script", "-", stdin="\n".join(json.dumps(s, ensure_ascii=False) for s in script))
        except (BuildError, KeyError, json.JSONDecodeError) as e:
            raise BuildError(f"{path.relative_to(ROOT)}: {e}") from None
        built.append(rel)
    return built


def load_authors() -> dict:
    """authors.json: the default author and the components credited to someone else."""
    try:
        data = json.loads(AUTHORS_JSON.read_text(encoding="utf-8"))
        default, by_component = data["default"], data.get("components", {})
    except (OSError, KeyError, json.JSONDecodeError) as e:
        raise BuildError(f"authors.json: {e}") from None
    names = [default, *by_component.values()]
    if not isinstance(by_component, dict) or not all(isinstance(n, str) and n.strip() for n in names):
        raise BuildError("authors.json: \"default\" and every entry of \"components\" must be a name")
    return {"default": default, "components": by_component}


def author_of(authors: dict, path: Path) -> str:
    """The author of components/<folder>/<name>.ccomp, keyed as "<folder>/<name>"."""
    key = path.relative_to(COMPONENTS).with_suffix("").as_posix()
    return authors["components"].get(key, authors["default"])


def describe(exe: str, path: Path, tmp: Path, authors: dict) -> dict:
    """Load a .ccomp into a new project (validating it) and describe its types."""
    project = tmp / "check.ccad"
    loaded = ccad(exe, "--save-as", str(project), "run", "component_load", f"path={path.resolve()}")
    got = ccad(exe, "-p", str(project), "script", "-",
               stdin="\n".join(json.dumps({"command": "type_get", "args": {"type": i}}) for i in loaded["types"]))
    types = [step["result"] for step in got]
    d = types[0]["params"]["def"]
    return with_thumbnail({
        "file": path.relative_to(ROOT).as_posix(),
        "component": loaded["component"],
        "author": author_of(authors, path),
        "kind": d.get("kind", "Generic"),
        "mep": d.get("mep"),
        "parameters": [p["name"] for p in d.get("params", [])],
        "types": [
            {
                "name": t["name"],
                "values": {p["name"]: param_value(p) for p in t["params"]["def"].get("params", [])},
                "description": t["info"].get("description", ""),
            }
            for t in types
        ],
    })


def with_thumbnail(entry: dict) -> dict:
    """The catalog entry with `thumbnail` right after `file` when its PNG exists, without it otherwise."""
    rel = Path(entry["file"]).relative_to("components").with_suffix(".png")
    out = {}
    for key, value in entry.items():
        if key == "thumbnail":
            continue
        out[key] = value
        if key == "file" and (THUMBNAILS / rel).is_file():
            out["thumbnail"] = (THUMBNAILS / rel).relative_to(ROOT).as_posix()
    return out


def catalog_json_text(entries: list[dict]) -> str:
    return json.dumps({"format_version": 1, "components": entries}, ensure_ascii=False, indent=2) + "\n"


def mep_summary(mep: dict | None) -> str:
    if not mep:
        return ""
    if "Fixture" in mep:
        f = mep["Fixture"]
        hot = ", água quente" if f["hot_water"] else ""
        return f"UHC {f['drain_units']:g}, peso {f['supply_weight']:g}{hot}"
    dev = mep["Device"]
    return f"{dev['device']}, {dev['power']:g} VA"


def catalog_md(entries: list[dict]) -> str:
    lines = [
        "# Catálogo · Catalog",
        "",
        "<!-- Gerado por tools/build.py; não edite à mão. Generated by tools/build.py; do not edit. -->",
        "",
        f"{len(entries)} componentes, {sum(len(e['types']) for e in entries)} tipos.",
        "",
    ]
    by_section: dict[str, list[dict]] = {}
    for e in entries:
        by_section.setdefault(e["file"].split("/")[1], []).append(e)
    order = list(SECTIONS) + sorted(set(by_section) - set(SECTIONS))
    for key in order:
        if key not in by_section:
            continue
        lines += [f"## {SECTIONS.get(key, key)}", "", "| Componente | Tipos | MEP | Autor | Arquivo |", "|---|---|---|---|---|"]
        for e in by_section[key]:
            names = "<br>".join(t["name"] for t in e["types"])
            lines.append(f"| **{e['component']}** | {names} | {mep_summary(e['mep'])} | {e['author']} | [`{Path(e['file']).name}`]({e['file']}) |")
        lines.append("")
    return "\n".join(lines)


def without_generator(text: str) -> str:
    return "\n".join(l for l in text.splitlines() if not l.strip().startswith("generator:"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only verify; change nothing")
    ap.add_argument("--ccad", help="path of the ccad executable")
    opts = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    try:
        exe = find_ccad(opts.ccad)
        authors = load_authors()
        problems = []
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            if opts.check:
                for rel in build(exe, tmp / "built"):
                    target = COMPONENTS / rel
                    if not target.exists():
                        problems.append(f"{target.relative_to(ROOT)} is missing: run tools/build.py")
                    elif without_generator(target.read_text(encoding="utf-8")) != without_generator(
                        (tmp / "built" / rel).read_text(encoding="utf-8")
                    ):
                        problems.append(f"{target.relative_to(ROOT)} is out of date with its source: run tools/build.py")
            else:
                build(exe, COMPONENTS)

            entries = []
            paths = sorted(COMPONENTS.rglob("*.ccomp"))
            for path in paths:
                try:
                    entries.append(describe(exe, path, tmp, authors))
                except BuildError as e:
                    problems.append(f"{path.relative_to(ROOT)}: {e}")
            known = {p.relative_to(COMPONENTS).with_suffix("").as_posix() for p in paths}
            for key in sorted(set(authors["components"]) - known):
                problems.append(f"authors.json: no component named {key}")

        catalog = catalog_json_text(entries)
        md = catalog_md(entries) + "\n"
        for target, text in ((CATALOG_JSON, catalog), (CATALOG_MD, md)):
            if opts.check:
                if not target.exists() or target.read_text(encoding="utf-8") != text:
                    problems.append(f"{target.name} is out of date: run tools/build.py")
            else:
                target.write_text(text, encoding="utf-8", newline="\n")

        for p in problems:
            print(f"error: {p}", file=sys.stderr)
        if problems:
            return 1
        print(f"{len(entries)} components OK")
        return 0
    except BuildError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
