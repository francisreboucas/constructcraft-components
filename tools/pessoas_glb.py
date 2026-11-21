#!/usr/bin/env python3
"""Generate the people of the Citizen NPC pack (sources/people/cidadao-*.json) from its .glb file.

    python tools/pessoas_glb.py path/to/citizen_npc_pack_1_character_lowpoly_mobile.glb   then  python tools/build.py

"Citizen NPC Pack 1 Character Lowpoly Mobile" by 00amza (https://sketchfab.com/00amza), licensed under CC BY 4.0
(https://sketchfab.com/3d-models/citizen-npc-pack-1-character-lowpoly-mobile-711ee48bcf80426bbf98ad01e1b9da1c).
Changes made here: each character is turned to ConstructCraft's frame (Z up, facing -Y, feet on z = 0, centred on its
footprint); its arms are lowered from the A pose to hang by the body; and its photo textures, which a .ccomp cannot
map, are reduced to flat colours, one mesh piece per colour, from a palette shared by all the characters.

The .glb is read as data only (glTF 2.0: JSON chunk, binary chunk, PNG/JPEG textures). Needs numpy and Pillow.
"""

from __future__ import annotations

import io
import json
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sources" / "people"
CREDIT = ("Modelo \"Citizen NPC Pack 1 Character Lowpoly Mobile\" de 00amza (sketchfab.com/00amza), CC BY 4.0; "
          "alterado: braços abaixados e texturas convertidas em cores sólidas")
AUTHOR = "00amza (Sketchfab), CC BY 4.0"
PER_CHARACTER = 12  # flat colours per character
MERGE = 0.035  # colours of two characters closer than this (each channel, 0 to 1) share a material

# Each character of the pack (in its order): file name, display name and a short description.
CHARACTERS = [
    ("cidadao-terno-cinza", "Homem de terno cinza", "homem de terno cinza e gravata"),
    ("cidadao-blusa-branca-saia", "Mulher de blusa branca e saia", "mulher de blusa branca, saia escura e salto"),
    ("cidadao-blazer-camiseta", "Homem de blazer e camiseta", "homem de blazer escuro sobre camiseta e calça"),
    ("cidadao-terno-preto", "Homem de terno preto", "homem de terno preto e camisa branca"),
    ("cidadao-tailleur", "Mulher de tailleur", "mulher de tailleur cinza com saia"),
    ("cidadao-sueter-vermelho", "Homem de suéter vermelho", "homem de suéter vermelho e calça cinza"),
    ("cidadao-saia-clara", "Mulher de saia clara", "mulher de blusa branca e saia clara"),
    ("cidadao-blazer-gravata", "Homem de blazer e gravata", "homem de blazer escuro, gravata e calça cinza"),
    ("cidadao-saia-laranja", "Mulher de saia laranja", "mulher de blusa rosada e saia laranja"),
    ("cidadao-camisa-verde", "Homem de camisa verde", "homem de camisa verde aberta sobre camiseta"),
    ("cidadao-camisa-azul", "Homem de camisa azul", "homem de camisa azul e calça preta"),
    ("cidadao-camisa-aberta", "Homem de camisa aberta", "homem de camisa azul-marinho aberta sobre camiseta e calça clara"),
    ("cidadao-saia-vinho", "Mulher de saia vinho", "mulher de blusa clara e saia vinho"),
    ("cidadao-calca-clara", "Mulher de calça clara", "mulher de blusa clara, cinto vermelho e calça clara"),
]

_CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


# --- reading the .glb ----------------------------------------------------------------------------

def read_glb(path):
    """The characters of the scene: [[{pos (world, glTF frame), uv, tri, tex}, ...] per root child node]."""
    data = Path(path).read_bytes()
    magic, _, _ = struct.unpack("<4sII", data[:12])
    if magic != b"glTF":
        raise SystemExit(f"{path}: not a .glb file")
    jl, _ = struct.unpack("<II", data[12:20])
    js = json.loads(data[20:20 + jl])
    o = 20 + jl
    bl, _ = struct.unpack("<II", data[o:o + 8])
    blob = data[o + 8:o + 8 + bl]

    def accessor(i):
        a = js["accessors"][i]
        bv = js["bufferViews"][a["bufferView"]]
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        n, dt = _NC[a["type"]], _CT[a["componentType"]]
        size = n * np.dtype(dt).itemsize
        stride = bv.get("byteStride") or size
        raw = np.frombuffer(blob, np.uint8, count=stride * (a["count"] - 1) + size, offset=off)
        rows = np.lib.stride_tricks.as_strided(raw, (a["count"], size), (stride, 1))
        return rows.copy().view(dt).reshape(a["count"], n)

    def image(i):
        bv = js["bufferViews"][js["images"][i]["bufferView"]]
        start = bv.get("byteOffset", 0)
        return np.asarray(Image.open(io.BytesIO(blob[start:start + bv["byteLength"]])).convert("RGB"), float) / 255

    def local(node):
        if "matrix" in node:
            return np.asarray(node["matrix"], float).reshape(4, 4).T
        M = np.eye(4)
        if "scale" in node:
            M = np.diag(list(node["scale"]) + [1.0]) @ M
        if "rotation" in node:
            x, y, z, w = node["rotation"]
            R = np.eye(4)
            R[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
            M = R @ M
        if "translation" in node:
            T = np.eye(4)
            T[:3, 3] = node["translation"]
            M = T @ M
        return M

    def collect(i, parent, out):
        node = js["nodes"][i]
        W = parent @ local(node)
        if "mesh" in node:
            for prim in js["meshes"][node["mesh"]]["primitives"]:
                pos = accessor(prim["attributes"]["POSITION"]).astype(float)
                pbr = js["materials"][prim.get("material", 0)].get("pbrMetallicRoughness", {})
                out.append({
                    "pos": (np.c_[pos, np.ones(len(pos))] @ W.T)[:, :3],
                    "uv": accessor(prim["attributes"]["TEXCOORD_0"]).astype(float),
                    "tri": accessor(prim["indices"]).ravel().astype(np.int64).reshape(-1, 3),
                    "tex": image(js["textures"][pbr["baseColorTexture"]["index"]]["source"]),
                })
        for c in node.get("children", []):
            collect(c, W, out)

    # The characters are the nodes that hold meshes below them, one level above the mesh nodes.
    chars = []

    def find(i, parent):
        node = js["nodes"][i]
        W = parent @ local(node)
        kids = node.get("children", [])
        if kids and all("mesh" in js["nodes"][c] and not js["nodes"][c].get("children") for c in kids):
            parts = []
            for c in kids:
                collect(c, W, parts)
            chars.append(parts)
            return
        for c in kids:
            find(c, W)

    for r in js["scenes"][js.get("scene", 0)]["nodes"]:
        find(r, np.eye(4))
    return chars


# --- colours -----------------------------------------------------------------------------------------

def face_colors(part):
    """Each face's colour: its texture averaged over seven points inside it."""
    tex = part["tex"]
    H, W, _ = tex.shape
    uv = part["uv"][part["tri"]]
    ws = np.array([[1, 1, 1], [4, 1, 1], [1, 4, 1], [1, 1, 4], [2, 2, 1], [1, 2, 2], [2, 1, 2]], float)
    ws /= ws.sum(1, keepdims=True)
    acc = np.zeros((len(uv), 3))
    for w in ws:
        p = (uv * w[None, :, None]).sum(1)
        u = np.clip((p[:, 0] % 1) * (W - 1), 0, W - 1).astype(int)
        v = np.clip((p[:, 1] % 1) * (H - 1), 0, H - 1).astype(int)
        acc += tex[v, u]
    return acc / len(ws)


def kmeans(X, k, weights=None, rounds=40):
    """Colour clusters (farthest-point start, so a small but distinct colour keeps its own cluster)."""
    w = np.ones(len(X)) if weights is None else weights
    C = [X[np.argmax(w)]]
    for _ in range(k - 1):
        d = np.min([((X - c) ** 2).sum(1) for c in C], axis=0)
        C.append(X[np.argmax(d * np.sqrt(w))])
    C = np.array(C)
    for _ in range(rounds):
        lab = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(2), axis=1)
        for i in range(k):
            m = lab == i
            if m.any():
                C[i] = (X[m] * w[m, None]).sum(0) / w[m].sum()
    return C, lab


# --- posing ---------------------------------------------------------------------------------------------

def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def lower_arms(V, F, H, hang=6.0):
    """Turn the arms of an A-pose figure (Z up, facing -Y) down about the shoulders, the armpits blending.

    The arm is what the mesh's edges reach from the vertices clearly on it (near its axis, past the shoulder) without
    coming back past a cut near the shoulder or far from the axis, so loose sleeves, cuffs and fingers come along and
    the torso stays.
    """
    V = V.copy()
    s = H / 1.75
    n = len(V)
    nbr = [[] for _ in range(n)]
    for a, b, c in F:
        nbr[a] += [b, c]
        nbr[b] += [a, c]
        nbr[c] += [a, b]
    for side in (1, -1):
        sx = V[:, 0] * side
        band = (V[:, 2] > 0.4 * H) & (V[:, 2] < 0.8 * H)
        far = band & (sx > np.percentile(sx[band], 99.0))
        hand = V[far].mean(0)
        pivot = np.array([side * 0.17 * s, V[(V[:, 2] > 0.76 * H) & (V[:, 2] < 0.82 * H)][:, 1].mean(), 0.79 * H])
        axis = hand - pivot
        L = np.linalg.norm(axis)
        axis /= L
        cur = np.degrees(np.arctan2(abs(axis[0]), -axis[2]))
        turn = np.radians(cur - hang) * side
        rel = V - pivot
        t = rel @ axis
        perp = np.linalg.norm(rel - np.outer(t, axis), axis=1)
        limit = 0.14 * s + 0.08 * s * smoothstep((t - 0.7 * L) / (0.15 * L))
        allowed = (t > 0.05 * s) & (perp < limit) & (sx > 0.1 * s)
        arm = np.zeros(n, bool)
        seeds = allowed & (t > 0.15 * s) & (perp < 0.11 * s)  # clearly the arm (the hands are a separate mesh)
        stack = list(np.flatnonzero(seeds))
        arm[stack] = True
        while stack:
            v = stack.pop()
            for u in nbr[v]:
                if not arm[u] and allowed[u]:
                    arm[u] = True
                    stack.append(u)
        # The shoulder ring (between the cut and the arm) turns partly, so the armpit stretches instead of tearing.
        ring = (~arm) & (t > -0.03 * s) & (t <= 0.05 * s) & (perp < 0.14 * s) & (sx > 0.1 * s)
        w = np.where(arm, smoothstep(t / (0.15 * s)), 0.0) + np.where(ring, 0.25 * smoothstep((t + 0.03 * s) / (0.08 * s)), 0.0)
        a = turn * w  # rotation about the y axis through the pivot (x' = x cos a + z sin a)
        ca, sa = np.cos(a), np.sin(a)
        x, z = rel[:, 0], rel[:, 2]
        V[:, 0] = pivot[0] + x * ca + z * sa
        V[:, 2] = pivot[2] - x * sa + z * ca
    return V


# --- sources ----------------------------------------------------------------------------------------------

def mesh_piece(name, material, V, F):
    used = np.unique(F)
    remap = -np.ones(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    verts = [[round(float(c), 4) + 0.0 for c in v] for v in V[used]]
    faces = remap[F].tolist()
    return {"name": name, "material": material, "in_plan": True, "shape": {"Mesh": {"vertices": verts, "faces": faces}}}


def dumps(src) -> str:
    import re
    text = json.dumps(src, ensure_ascii=False, indent=2)
    return re.sub(r"\[\s+(-?[\d.e-]+(?:,\s+-?[\d.e-]+)*)\s+\]", lambda m: "[" + re.sub(r",\s+", ", ", m.group(1)) + "]", text) + "\n"


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    chars = read_glb(sys.argv[1])
    if len(chars) != len(CHARACTERS):
        raise SystemExit(f"expected {len(CHARACTERS)} characters, found {len(chars)}")
    # Turn each character to Z up facing -Y (glTF: Y up, the front +Z), centre it, lower its arms.
    figures = []
    for parts in chars:
        V = np.concatenate([p["pos"] for p in parts])
        V = np.c_[V[:, 0], -V[:, 2], V[:, 1]]
        lo, hi = V.min(0), V.max(0)
        V -= [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]]
        H = V[:, 2].max()
        V = lower_arms(V, np.concatenate([p['tri'] + o for p, o in zip(parts, np.cumsum([0] + [len(p['pos']) for p in parts[:-1]]))]), H)
        # Recentre on the footprint now that the arms are in.
        lo, hi = V.min(0), V.max(0)
        V -= [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0]
        F, offset, cols, areas = [], 0, [], []
        for p in parts:
            F.append(p["tri"] + offset)
            offset += len(p["pos"])
            cols.append(face_colors(p))
        F = np.concatenate(F)
        cols = np.concatenate(cols)
        e1, e2 = V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]
        areas = np.linalg.norm(np.cross(e1, e2), axis=1) / 2
        figures.append((V, F, cols, areas, H))
    # Colours: a dozen per character (so a small saturated garment keeps its own), then the colours that two
    # characters share almost exactly merged into one material.
    palette, labels = [], []
    for V, F, cols, areas, H in figures:
        C, lab = kmeans(cols, PER_CHARACTER, areas / areas.mean())
        ids = []
        for c in C:
            d = [np.abs(c - q).max() for q in palette]
            if d and min(d) < MERGE:
                ids.append(int(np.argmin(d)))
            else:
                palette.append(c)
                ids.append(len(palette) - 1)
        labels.append(np.array(ids)[lab])
    C = np.array(palette)
    names = {i: f"Pessoa - tom {i + 1:03d}" for i in range(len(C))}
    OUT.mkdir(parents=True, exist_ok=True)
    authors = json.loads((ROOT / "authors.json").read_text(encoding="utf-8"))
    for (file, title, desc), (V, F, cols, areas, H), L in zip(CHARACTERS, figures, labels):
        items = []
        for i in sorted(set(L.tolist()), key=lambda i: -areas[L == i].sum()):
            items.append(mesh_piece(f"Cor {len(items) + 1}", names[i], V, F[L == i]))
        mats = [{"name": it["material"], "color": [int(round(c * 255)) for c in C[int(it["material"][-3:]) - 1]], "class": "Generic",
                 "finish": "Matte", "transparency": 0} for it in items]
        src = {"component": title, "def": {"kind": "Generic", "params": [], "items": items},
               "types": [{"name": f"{title} {H:.2f} m".replace(".", ","), "values": {},
                          "info": {"description": f"Pessoa em pé para escala, {desc}, {H:.2f} m de altura (a frente para -Y). {CREDIT}".replace(f"{H:.2f}", f"{H:.2f}".replace(".", ","))}}],
               "materials": mats}
        (OUT / f"{file}.json").write_text(dumps(src), encoding="utf-8", newline="\n")
        authors["components"][f"people/{file}"] = AUTHOR
        print(f"sources/people/{file}.json: {len(V)} vertices, {len(items)} colours, {H:.2f} m")
    (ROOT / "authors.json").write_text(json.dumps(authors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
