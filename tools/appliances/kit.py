"""Helpers to write detailed appliance components as JSON sources.

A module of this package describes one component: it has a `build()` function
returning a `Component`. `python tools/appliances/make.py <module>` writes its
source to sources/, builds the .ccomp with ccad and renders previews.

Frame (CONTRIBUTING.md): meters; origin at the insertion point, X to the
right, Y to the back (the wall), Z up. The front of an appliance faces -Y.
Every coordinate is an expression over the parameters (a string); numbers are
accepted and written as they are. Angles are in degrees.
"""

from __future__ import annotations

# Materials shared by the appliance components: name -> (color, class, finish, transparency).
# The same name must mean the same material in every component, since they load into one project.
PALETTE = {
    "Inox escovado": ((198, 200, 203), "Metal", "Satin", 0),
    "Cromado": ((226, 229, 233), "Metal", "Polished", 0),
    "Alumínio fundido": ((172, 174, 177), "Metal", "Satin", 0),
    "Alumínio anodizado": ((206, 208, 210), "Metal", "Satin", 0),
    "Aço galvanizado": ((160, 165, 170), "Metal", "Matte", 0),
    "Aço pintado cinza": ((128, 130, 134), "Metal", "Satin", 0),
    "Aço pintado branco": ((240, 240, 236), "Metal", "Satin", 0),
    "Aço pintado preto": ((30, 30, 32), "Metal", "Satin", 0),
    "Ferro fundido": ((44, 44, 47), "Metal", "Matte", 0),
    "Cobre": ((184, 115, 72), "Metal", "Satin", 0),
    "Latão": ((192, 160, 84), "Metal", "Satin", 0),
    "Esmalte preto": ((26, 26, 28), "Ceramic", "Glossy", 0),
    "Esmalte do forno": ((52, 56, 66), "Ceramic", "Glossy", 0),
    "Esmalte cinza claro": ((214, 215, 212), "Ceramic", "Glossy", 0),
    "Vitrocerâmica": ((16, 16, 18), "Glass", "Polished", 0),
    "Vidro temperado": ((205, 228, 232), "Glass", "Polished", 0.7),
    "Vidro fumê": ((38, 42, 48), "Glass", "Polished", 0.45),
    "Tela de TV": ((12, 13, 16), "Glass", "Glossy", 0),
    "Visor LCD": ((70, 112, 92), "Glass", "Glossy", 0),
    "Visor LED": ((24, 60, 96), "Glass", "Glossy", 0),
    "Plástico preto": ((34, 34, 37), "Plastic", "Satin", 0),
    "Plástico preto brilhante": ((18, 18, 20), "Plastic", "Glossy", 0),
    "Plástico cinza": ((120, 122, 126), "Plastic", "Satin", 0),
    "Plástico cinza claro": ((196, 198, 200), "Plastic", "Satin", 0),
    "Plástico translúcido": ((222, 236, 240), "Plastic", "Glossy", 0.6),
    "Plástico fumê": ((60, 62, 66), "Plastic", "Glossy", 0.5),
    "Plástico azul": ((126, 176, 222), "Plastic", "Satin", 0),
    "Plástico verde": ((60, 160, 90), "Plastic", "Satin", 0),
    "Plástico vermelho": ((196, 56, 48), "Plastic", "Satin", 0),
    "Branco": ((244, 244, 240), "Plastic", "Satin", 0),
    "Teclado": ((74, 76, 80), "Plastic", "Satin", 0),
    "Borracha": ((30, 30, 30), "Plastic", "Matte", 0),
    "Borracha cinza": ((150, 152, 154), "Plastic", "Matte", 0),
    "Tela perfurada": ((24, 24, 26), "Metal", "Matte", 0.4),
    "Mica": ((202, 182, 140), "Generic", "Matte", 0),
    "Madeira clara": ((196, 160, 112), "Wood", "Satin", 0),
    "Madeira escura": ((92, 62, 40), "Wood", "Satin", 0),
    "Laminado branco": ((238, 238, 234), "Wood", "Satin", 0),
}

# Materials every ConstructCraft project already has.
TEMPLATE_MATERIALS = {
    "Alvenaria", "Reboco", "Concreto", "Madeira", "Vidro", "Gesso", "Telha cerâmica",
    "Contrapiso", "Tecido", "Louça", "Aço", "PVC", "Terra",
}

ALL = "cmf"  # every detail level
FULL = "mf"  # medium and fine: the default of a detailed piece
FINE = "f"  # small details
COARSE = "c"  # the simplified stand-in drawn in coarse views


def e(value) -> str:
    """A number or an expression as an expression string."""
    if isinstance(value, str):
        return value
    text = f"{float(value):.6f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def p(value) -> str:
    """An expression in parentheses, safe inside a larger expression."""
    text = e(value)
    return text if text.replace(".", "").isalnum() else f"({text})"


class Component:
    def __init__(self, name: str, folder: str, file: str, kind: str = "Furniture"):
        self.name, self.folder, self.file, self.kind = name, folder, file, kind
        self.params: list[dict] = []
        self.items: list[dict] = []
        self.types: list[dict] = []
        self.extra_materials: dict[str, tuple] = {}
        self.mep: dict | None = None
        self.connectors: list[dict] = []
        # Doors and windows: the opening cut in the wall, e.g. {"width": "Largura", "height": "Altura"}
        # plus a window's "sill", "own_symbol", "operation" or a door's "door_operation" (see component_create).
        self.opening: dict | None = None
        # Instance parameter values of the "open" preview render, e.g. {"AnguloPorta": 100}.
        self.open_pose: dict[str, float] = {}

    # --- definition -------------------------------------------------------

    def param(self, name: str, value: float, kind: str = "Length", instance: bool = False) -> str:
        """Declare a parameter and return its name, to use in expressions."""
        self.params.append({"name": name, "value": value, "kind": kind, "instance": instance})
        return name

    def angle(self, name: str, value: float = 0.0, open_at: float | None = None) -> str:
        """An instance angle (a door's opening); `open_at` is its value in the open preview."""
        if open_at is not None:
            self.open_pose[name] = open_at
        return self.param(name, value, "Angle", True)

    def material(self, name: str, color: tuple, cls: str = "Generic", finish: str = "Satin", transparency: float = 0):
        """A material only this component uses (prefer the PALETTE)."""
        if name in PALETTE or name in TEMPLATE_MATERIALS:
            raise ValueError(f"material {name!r} already exists: use it as it is")
        self.extra_materials[name] = (tuple(color), cls, finish, transparency)

    def type(self, name: str, description: str, **values: float):
        """A type: the first takes the parameters' own values, the others override some."""
        self.types.append({"name": name, "values": values, "info": {"description": description}})

    def connector(self, name: str, system: str, x, y, z, direction: str, diameter=None):
        c = {"name": name, "system": system, "x": e(x), "y": e(y), "z": e(z), "direction": direction}
        if diameter is not None:
            c["diameter"] = e(diameter)
        self.connectors.append(c)

    # --- pieces -----------------------------------------------------------

    def _add(self, name: str, shape: dict, material: str, detail: str, in_plan: bool, void: bool):
        if any(i["name"] == name for i in self.items):
            raise ValueError(f"piece name used twice: {name}")
        if set(detail) - set(ALL) or not detail:
            raise ValueError(f"{name}: detail is a combination of c, m and f")
        item = {"name": name, "shape": shape, "material": material, "in_plan": in_plan}
        if set(detail) != set(ALL):
            item["detail"] = {"coarse": "c" in detail, "medium": "m" in detail, "fine": "f" in detail}
        if void:
            item["void"] = True
        self.items.append(item)

    def box(self, name, x, y, z, width, depth, height, material, detail=FULL, in_plan=False, void=False):
        """A box from its lowest corner (x, y, z)."""
        shape = {"Box": {"x": e(x), "y": e(y), "z": e(z), "width": e(width), "depth": e(depth), "height": e(height)}}
        self._add(name, shape, material, detail, in_plan, void)

    def extrusion(self, name, points, z, height, material, detail=FULL, in_plan=False, void=False):
        """A plan outline [(x, y), …] of straight sides, extruded up from z."""
        shape = {"Extrusion": {"points": [[e(x), e(y)] for x, y in points], "z": e(z), "height": e(height)}}
        self._add(name, shape, material, detail, in_plan, void)

    def plan_only(self, name: str):
        """Make the piece `name` a plan symbol (a door's swing): drawn in plans, not a solid."""
        item = next(i for i in self.items if i["name"] == name)
        item["plan_only"] = True
        item["in_plan"] = True

    def cyl(self, name, x, y, z, radius, height, material, detail=FULL, in_plan=False, void=False):
        """A vertical cylinder: center (x, y), base at z."""
        shape = {"Cylinder": {"x": e(x), "y": e(y), "z": e(z), "radius": e(radius), "height": e(height)}}
        self._add(name, shape, material, detail, in_plan, void)

    def profile(self, name, plane, points, offset, depth, material, detail=FULL, in_plan=False, void=False):
        """A closed outline extruded along its plane's normal.

        plane "Plan": u = x, v = y, stands at z = offset, extrudes up.
        plane "Front": u = x, v = z, stands at y = offset, extrudes towards +y.
        plane "Side": u = y, v = z, stands at x = offset, extrudes towards +x.
        `points` are (u, v) or (u, v, radius): a radius turns the segment to the
        next point into an arc (positive bulges outwards).
        """
        shape = {"Profile": {"plane": plane, "points": _points(points), "offset": e(offset), "depth": e(depth)}}
        self._add(name, shape, material, detail, in_plan, void)

    def rev(self, name, plane, points, offset, axis, material, angle=360, detail=FULL, in_plan=False, void=False):
        """A half-profile turned about the line u = axis of its plane.

        Front or Side plane: a vertical axis (knobs on a top, feet, jars, bowls).
        Plan plane: an axis along Y at height `offset` (knobs on a front panel, a
        washer's porthole). There is no axis along X.
        """
        shape = {"Revolution": {"plane": plane, "points": _points(points), "offset": e(offset), "axis": e(axis), "angle": e(angle)}}
        self._add(name, shape, material, detail, in_plan, void)

    # --- compound pieces --------------------------------------------------

    def cyl_y(self, name, x, z, y, radius, length, material, detail=FULL, in_plan=False, void=False):
        """A cylinder lying along Y: axis at (x, z), from y to y + length."""
        pts = [(x, y), (f"{p(x)} + {p(radius)}", y), (f"{p(x)} + {p(radius)}", f"{p(y)} + {p(length)}"), (x, f"{p(y)} + {p(length)}")]
        self.rev(name, "Plan", pts, z, x, material, detail=detail, in_plan=in_plan, void=void)

    def cyl_x(self, name, y, z, x, radius, length, material, detail=FULL, in_plan=False, void=False):
        """A cylinder lying along X: axis at (y, z), from x to x + length."""
        self.profile(name, "Side", disc(y, z, radius), x, length, material, detail=detail, in_plan=in_plan, void=void)

    def door_box(self, name, hinge, angle, a0, a1, b0, b1, z, height, material, side="left", detail=FULL, in_plan=False, void=False):
        """A box that swings with a side-hinged door (vertical hinge).

        `hinge` = (x, y) of the hinge axis, on the door's back face. In the
        closed door, `a` runs from the hinge along the door (to +x for a hinge
        on the `left`, to -x on the `right`) and `b` runs out of the back face
        towards the front (-y). The box spans a0..a1, b0..b1 and z..z + height;
        `angle` (degrees) opens it towards the front.
        """
        pts = [swing(hinge, angle, a, b, side) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
        self.profile(name, "Plan", pts, z, height, material, detail=detail, in_plan=in_plan, void=void)

    def flap_box(self, name, hinge, angle, x, width, s0, s1, t0, t1, material, detail=FULL, in_plan=False, void=False):
        """A box that tilts with a drop-down door (oven, dishwasher): a horizontal hinge along X at the bottom.

        `hinge` = (y, z) of the hinge axis, on the door's back face. In the
        closed door `s` runs up from the hinge and `t` out towards the front
        (-y). The box spans x..x + width, s0..s1 and t0..t1; `angle` lowers
        the door's top towards the front (90 = lying flat).
        """
        pts = [drop(hinge, angle, s, t) for s, t in ((s0, t0), (s0, t1), (s1, t1), (s1, t0))]
        self.profile(name, "Side", pts, x, width, material, detail=detail, in_plan=in_plan, void=void)

    def lid_box(self, name, hinge, angle, x, width, r0, r1, t0, t1, material, detail=FULL, in_plan=False, void=False):
        """A box that lifts with a top lid hinged at the back (horizontal hinge along X).

        `hinge` = (y, z) of the hinge axis. In the closed lid `r` runs from the
        hinge towards the front (-y) and `t` up. The box spans x..x + width,
        r0..r1 and t0..t1; `angle` lifts the lid's front (90 = standing up).
        """
        pts = [lift(hinge, angle, r, t) for r, t in ((r0, t0), (r0, t1), (r1, t1), (r1, t0))]
        self.profile(name, "Side", pts, x, width, material, detail=detail, in_plan=in_plan, void=void)

    # --- output -----------------------------------------------------------

    def source(self) -> dict:
        if not self.types:
            raise ValueError("a component needs at least one type")
        names = {q["name"] for q in self.params}
        for t in self.types:
            if set(t["values"]) - names:
                raise ValueError(f"type {t['name']}: unknown parameters {sorted(set(t['values']) - names)}")
        materials = []
        for name in dict.fromkeys(i["material"] for i in self.items):
            if name in TEMPLATE_MATERIALS:
                continue
            if name not in PALETTE and name not in self.extra_materials:
                raise ValueError(f"unknown material {name!r}: use the PALETTE or Component.material()")
            color, cls, finish, transparency = PALETTE.get(name) or self.extra_materials[name]
            materials.append({"name": name, "color": list(color), "class": cls, "finish": finish, "transparency": transparency})
        d: dict = {"kind": self.kind, "params": self.params, "items": self.items}
        if self.mep:
            d["mep"] = self.mep
        if self.connectors:
            d["connectors"] = self.connectors
        if self.opening:
            d["opening"] = self.opening
        return {"component": self.name, "def": d, "types": self.types, "materials": materials}


def _points(points) -> list[dict]:
    out = []
    for pt in points:
        d = {"u": e(pt[0]), "v": e(pt[1])}
        if len(pt) > 2 and pt[2] not in (None, "", 0):
            d["radius"] = e(pt[2])
        out.append(d)
    return out


# --- outlines --------------------------------------------------------------

def rect(u0, v0, u1, v1) -> list[tuple]:
    """A rectangle from (u0, v0) to (u1, v1), counter-clockwise."""
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def rrect(u0, v0, u1, v1, r) -> list[tuple]:
    """A rectangle with corners rounded by the radius r (u0 < u1, v0 < v1)."""
    r_ = p(r)
    return [
        (f"{p(u0)} + {r_}", v0),
        (f"{p(u1)} - {r_}", v0, r),
        (u1, f"{p(v0)} + {r_}"),
        (u1, f"{p(v1)} - {r_}", r),
        (f"{p(u1)} - {r_}", v1),
        (f"{p(u0)} + {r_}", v1, r),
        (u0, f"{p(v1)} - {r_}"),
        (u0, f"{p(v0)} + {r_}", r),
    ]


def disc(cu, cv, r) -> list[tuple]:
    """A circle of radius r centered at (cu, cv), as two arcs."""
    return [(f"{p(cu)} - {p(r)}", cv, r), (f"{p(cu)} + {p(r)}", cv, r)]


# --- moving parts ------------------------------------------------------------

def swing(hinge, angle, a, b, side="left") -> tuple[str, str]:
    """Plan (x, y) of the point (a, b) of a side-hinged door opened by `angle` (see `door_box`)."""
    hx, hy = p(hinge[0]), p(hinge[1])
    a, b, g = p(a), p(b), p(angle)
    sign_a, sign_b = ("+", "-") if side == "left" else ("-", "+")
    return (
        f"{hx} {sign_a} {a}*cos({g}) {sign_b} {b}*sin({g})",
        f"{hy} - {a}*sin({g}) - {b}*cos({g})",
    )


def drop(hinge, angle, s, t) -> tuple[str, str]:
    """Side (y, z) of the point (s up, t out) of a drop-down door lowered by `angle` (see `flap_box`)."""
    hy, hz = p(hinge[0]), p(hinge[1])
    s, t, g = p(s), p(t), p(angle)
    return (f"{hy} - {t}*cos({g}) - {s}*sin({g})", f"{hz} + {s}*cos({g}) - {t}*sin({g})")


def lift(hinge, angle, r, t) -> tuple[str, str]:
    """Side (y, z) of the point (r forward, t up) of a back-hinged lid lifted by `angle` (see `lid_box`)."""
    hy, hz = p(hinge[0]), p(hinge[1])
    r, t, g = p(r), p(t), p(angle)
    return (f"{hy} - {r}*cos({g}) + {t}*sin({g})", f"{hz} + {r}*sin({g}) + {t}*cos({g})")
