#!/usr/bin/env python3
"""Generate the sources of the PVC-U solvent-weld fittings (EN ISO 1452-3).

    python tools/conexoes_pvc.py     writes sources/fittings/*.json

Sizes d16 to d160 with generic, public dimensions:

- socket inside diameter = pipe outside diameter `de`;
- solvent-weld socket depth L = 0.5 de + 6 mm (minimum of EN ISO 1452-3 / ISO 727-1);
- laying length z (fitting centre to socket bottom) = (de / 2) tan(a / 2) + 1 mm,
  the geometric minimum for an `a` degree turn, rounded up to 0.5 mm;
- modelling wall e = de / 13.6 (series S 6.3), at least 1.5 mm, rounded up to 0.1 mm.
- reducer transition = d1 - d2 + 4 mm, at least 12 mm: ConstructCraft joins pipe ends closer
  than 1 cm, so shorter reducers would also count as a derived reducer.

No manufacturer: the fittings are generic. Edit this script, not the JSON.

Frame: metres, the pipe axes lie in the plane z = 0 (place the fitting with
`base_offset` equal to the pipes' height). Each connector sits at a socket
bottom, where the pipe end stops, so a pipe drawn to the connector point
meets it.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sources" / "fittings"

SIZES = [16, 20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160]
REDUCERS = [
    (20, 16), (25, 20), (32, 25), (40, 32), (50, 40), (63, 50), (75, 63), (90, 75),
    (110, 90), (125, 110), (140, 125), (160, 140),
    (32, 20), (40, 25), (50, 32), (63, 40), (75, 50), (90, 63), (110, 75), (125, 90), (160, 110),
]
NORM = "EN ISO 1452-3 / NF EN 1452-3"
EPS = "0.001"


def up(x: float, step: float) -> float:
    return round(math.ceil(round(x / step, 6)) * step, 4)


def socket(de: int) -> float:
    return (0.5 * de + 6) / 1000


def wall(de: int) -> float:
    return max(1.5, up(de / 13.6, 0.1)) / 1000


def laying(de: int, angle: float) -> float:
    return up(de / 2 * math.tan(math.radians(angle / 2)) + 1, 0.5) / 1000


def mm(x: float) -> str:
    return f"{x * 1000:g}"


# ---- pieces ---------------------------------------------------------------

def circle(cu: str, cv: str, r: str) -> list[dict]:
    """A circle of radius `r` centred at (cu, cv), as two half circles."""
    return [
        {"u": f"{cu} - {r}", "v": cv, "radius": r},
        {"u": f"{cu} + {r}", "v": cv, "radius": r},
    ]


def tube_x(name: str, start: str, length: str, r: str, void: bool = False) -> dict:
    """Cylinder of radius `r` along X, from x = start, on the axis y = z = 0."""
    return piece(name, {"Profile": {"plane": "Side", "points": circle("0", "0", r), "offset": start, "depth": length}}, void)


def tube_y(name: str, start: str, length: str, r: str, void: bool = False) -> dict:
    """Cylinder of radius `r` along Y, from y = start, on the axis x = z = 0."""
    return piece(name, {"Profile": {"plane": "Front", "points": circle("0", "0", r), "offset": start, "depth": length}}, void)


def sphere(name: str, r: str, void: bool = False) -> dict:
    """Ball of radius `r` at the origin: a half disc turned about the vertical axis."""
    # A half disc in the front plane (u >= 0), the arc bulging towards +u.
    points = [{"u": "0", "v": r}, {"u": "0", "v": f"-({r})", "radius": r}]
    return piece(name, {"Revolution": {"plane": "Front", "points": points, "offset": "0", "axis": "0", "angle": "360"}}, void)


def cone_y(name: str, y0: str, r0: str, y1: str, r1: str, void: bool = False) -> dict:
    """Frustum along Y from radius r0 at y0 to r1 at y1: a plan outline turned about x = 0."""
    points = [{"u": "0", "v": y0}, {"u": r0, "v": y0}, {"u": r1, "v": y1}, {"u": "0", "v": y1}]
    return piece(name, {"Revolution": {"plane": "Plan", "points": points, "offset": "0", "axis": "0", "angle": "360"}}, void)


def piece(name: str, shape: dict, void: bool) -> dict:
    p = {"name": name, "material": "PVC", "in_plan": not void, "shape": shape}
    if void:
        p["void"] = True
    return p


def connector(name: str, x: str, y: str, direction: str, diameter: str) -> dict:
    return {"name": name, "system": "ColdWater", "x": x, "y": y, "z": "0", "direction": direction, "diameter": diameter}


def length(name: str, value: float) -> dict:
    return {"name": name, "value": value, "kind": "Length", "instance": False}


def params(de: int, angle: float) -> list[dict]:
    return [
        length("Diametro", de / 1000),
        length("Encaixe", socket(de)),
        length("Espessura", wall(de)),
        length("Afastamento", laying(de, angle)),
    ]


def values(de: int, angle: float) -> dict:
    return {p["name"]: p["value"] for p in params(de, angle)}


RO = "(Diametro / 2 + Espessura)"
RS = "(Diametro / 2)"
RI = "(Diametro / 2 - Espessura)"


def info(text: str, de: int, angle: float) -> dict:
    return {
        "description": (
            f"{text} PVC-U para colar, d{de}: encaixe {mm(socket(de))} mm, z {mm(laying(de, angle))} mm "
            f"({NORM}; cotas genéricas, sem fabricante)"
        )
    }


# ---- fittings -------------------------------------------------------------

def elbow90() -> dict:
    a = 90
    items = [
        tube_x("Braço A", "-(Afastamento + Encaixe)", "Afastamento + Encaixe", RO),
        tube_y("Braço B", "0", "Afastamento + Encaixe", RO),
        sphere("Canto", RO),
        tube_x("Encaixe A vazio", f"-(Afastamento + Encaixe) - {EPS}", f"Encaixe + {EPS}", RS, True),
        tube_y("Encaixe B vazio", "Afastamento", f"Encaixe + {EPS}", RS, True),
        tube_x("Passagem A vazio", f"-Afastamento - {EPS}", f"Afastamento + {EPS}", RI, True),
        tube_y("Passagem B vazio", "0", f"Afastamento + {EPS}", RI, True),
        sphere("Canto vazio", RI, True),
    ]
    return {
        "component": "Joelho 90° PVC soldável",
        "def": {
            "kind": "Generic",
            "params": params(SIZES[0], a),
            "items": items,
            "connectors": [
                connector("A", "-Afastamento", "0", "Left", "Diametro"),
                connector("B", "0", "Afastamento", "Back", "Diametro"),
            ],
        },
        "types": [
            {"name": f"Joelho 90° PVC d{de}", "values": values(de, a), "info": info("Joelho 90°", de, a)}
            for de in SIZES
        ],
    }


def tee() -> dict:
    a = 90
    items = [
        tube_x("Corpo", "-(Afastamento + Encaixe)", "2 * (Afastamento + Encaixe)", RO),
        tube_y("Derivação", "0", "Afastamento + Encaixe", RO),
        tube_x("Encaixe A vazio", f"-(Afastamento + Encaixe) - {EPS}", f"Encaixe + {EPS}", RS, True),
        tube_x("Encaixe B vazio", "Afastamento", f"Encaixe + {EPS}", RS, True),
        tube_y("Encaixe C vazio", "Afastamento", f"Encaixe + {EPS}", RS, True),
        tube_x("Passagem vazio", f"-Afastamento - {EPS}", f"2 * Afastamento + 2 * {EPS}", RI, True),
        tube_y("Passagem derivação vazio", "0", f"Afastamento + {EPS}", RI, True),
    ]
    return {
        "component": "Tê 90° PVC soldável",
        "def": {
            "kind": "Generic",
            "params": params(SIZES[0], a),
            "items": items,
            "connectors": [
                connector("A", "-Afastamento", "0", "Left", "Diametro"),
                connector("B", "Afastamento", "0", "Right", "Diametro"),
                connector("C", "0", "Afastamento", "Back", "Diametro"),
            ],
        },
        "types": [
            {"name": f"Tê PVC d{de}", "values": values(de, a), "info": info("Tê 90° igual", de, a)}
            for de in SIZES
        ],
    }


def cap() -> dict:
    def vals(de: int) -> dict:
        return {"Diametro": de / 1000, "Encaixe": socket(de), "Espessura": wall(de), "Fundo": up(max(2.0, 1.5 * wall(de) * 1000), 0.5) / 1000}

    first = vals(SIZES[0])
    items = [
        tube_y("Corpo", "-Encaixe", "Encaixe + Fundo", RO),
        tube_y("Encaixe vazio", f"-Encaixe - {EPS}", f"Encaixe + {EPS}", RS, True),
    ]
    return {
        "component": "Tampão PVC soldável",
        "def": {
            "kind": "Generic",
            "params": [length(k, v) for k, v in first.items()],
            "items": items,
            "connectors": [connector("A", "0", "0", "Front", "Diametro")],
        },
        "types": [
            {
                "name": f"Tampão PVC d{de}",
                "values": vals(de),
                "info": {
                    "description": (
                        f"Tampão PVC-U para colar, d{de}: encaixe {mm(socket(de))} mm, fundo {mm(vals(de)['Fundo'])} mm "
                        f"({NORM}; cotas genéricas, sem fabricante). Origem no fundo do encaixe, onde o tubo termina."
                    )
                },
            }
            for de in SIZES
        ],
    }


def reducer() -> dict:
    def vals(d1: int, d2: int) -> dict:
        return {
            "Diametro": d1 / 1000,
            "Encaixe": socket(d1),
            "Espessura": wall(d1),
            "Diametro2": d2 / 1000,
            "Encaixe2": socket(d2),
            "Espessura2": wall(d2),
            "Transicao": max(12.0, up(d1 - d2 + 4, 0.5)) / 1000,
        }

    ro2 = "(Diametro2 / 2 + Espessura2)"
    rs2 = "(Diametro2 / 2)"
    ri2 = "(Diametro2 / 2 - Espessura2)"
    h = "(Transicao / 2)"
    items = [
        tube_y("Encaixe maior", f"-{h} - Encaixe", "Encaixe", RO),
        cone_y("Transição", f"-{h}", RO, h, ro2),
        tube_y("Encaixe menor", h, "Encaixe2", ro2),
        tube_y("Encaixe maior vazio", f"-{h} - Encaixe - {EPS}", f"Encaixe + {EPS}", RS, True),
        cone_y("Transição vazio", f"-{h} - {EPS}", RI, f"{h} + {EPS}", ri2, True),
        tube_y("Encaixe menor vazio", h, f"Encaixe2 + {EPS}", rs2, True),
    ]
    first = vals(*REDUCERS[0])
    return {
        "component": "Redução concêntrica PVC soldável",
        "def": {
            "kind": "Generic",
            "params": [length(k, v) for k, v in first.items()],
            "items": items,
            "connectors": [
                connector("Maior", "0", f"-{h}", "Front", "Diametro"),
                connector("Menor", "0", h, "Back", "Diametro2"),
            ],
        },
        "types": [
            {
                "name": f"Redução PVC d{d1} x d{d2}",
                "values": vals(d1, d2),
                "info": {
                    "description": (
                        f"Redução concêntrica PVC-U para colar (luva de redução), d{d1} x d{d2}: encaixes "
                        f"{mm(socket(d1))} e {mm(socket(d2))} mm ({NORM}; cotas genéricas, sem fabricante)"
                    )
                },
            }
            for d1, d2 in REDUCERS
        ],
    }


FITTINGS = {
    "joelho-90-pvc-soldavel": elbow90,
    "te-90-pvc-soldavel": tee,
    "reducao-concentrica-pvc-soldavel": reducer,
    "tampao-pvc-soldavel": cap,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, make in FITTINGS.items():
        text = json.dumps(make(), ensure_ascii=False, indent=2) + "\n"
        (OUT / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
        print(f"sources/fittings/{name}.json")


if __name__ == "__main__":
    main()
