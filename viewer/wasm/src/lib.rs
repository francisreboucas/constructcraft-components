//! The geometry core of the web viewer of `.ccomp` component files: the
//! ConstructCraft engine (`cc_core` and `cc_geom`, without Lua) built to
//! WebAssembly. [`load_component`] parses a file, resolves its pieces with the
//! first type's values and tessellates the 3D ones into triangles.
//!
//! Coordinates are the component's frame, as in the engine: meters, origin at
//! the insertion point, X to the right, Y to the back, Z up. Doors and windows
//! are centered on their opening in X, with the wall's axis at Y = 0 and the
//! sill at Z = 0.

use cc_core::component::{ComponentPart, WALL_THICKNESS};
use cc_core::component_file::ComponentFile;
use cc_core::{Category, ElementId, Material, MepData, SystemKind};
use cc_geom::{DVec3, Solid};
use serde::Serialize;
use std::collections::BTreeMap;
use wasm_bindgen::prelude::*;

/// The wall doors and windows are resolved in (`WallThickness`), as the
/// engine's component library and component environment show them.
const PREVIEW_WALL: f64 = 0.15;

/// The color of pieces whose material is missing or empty (the engine's
/// `Project::material_color` fallback).
const NO_MATERIAL: [u8; 3] = [200, 200, 200];

#[wasm_bindgen(typescript_custom_section)]
const TS_TYPES: &str = r#"
/** A parameter of the component with the value it has in the first type. */
export interface ComponentParam {
  name: string;
  /** "Length" (meters), "Angle" (degrees), "Number", "Boolean", "Text", "Choice" or "Material". */
  kind: string;
  /** A number for numeric kinds (booleans are 1 or 0); a string for text, choice (its key) and material kinds. */
  value: number | string;
  /** Elements may override the value. */
  instance: boolean;
}

/** A type of the component: its name, description and parameter values. */
export interface ComponentType {
  name: string;
  description: string;
  values: Record<string, number>;
}

/** Where a pipe or conduit connects, in the component's frame (first type's values). */
export interface ComponentConnector {
  name: string;
  /** The system kind, e.g. "ColdWater", "Sanitary", "Power". */
  system: string;
  /** Meters. */
  position: [number, number, number];
  /** Unit vector of the way runs leave. */
  direction: [number, number, number];
  /** Outside diameter in meters, or null when unset. */
  diameter: number | null;
}

/** An axis-aligned box, meters. */
export interface ComponentBounds {
  min: [number, number, number];
  max: [number, number, number];
}

/** A piece that failed to resolve. */
export interface ComponentError {
  /** Index of the piece in the definition. */
  item: number;
  name: string;
  message: string;
}

/** One solid piece, tessellated. */
export interface Part {
  name: string;
  /** The material's name ("" for none). */
  material: string;
  /** sRGB 0-255: the material's shading color, grey when the material is missing or empty. */
  color: [number, number, number];
  /** 0 (opaque) to 1 (invisible), from the material. */
  transparency: number;
  /** Non-indexed triangles, x, y, z per vertex, counter-clockwise seen from outside. */
  positions: Float32Array;
  /** One unit normal per vertex: smooth across the facets of curved surfaces, flat elsewhere. */
  normals: Float32Array;
}

/** A component file, resolved with its first type's values. */
export interface Component {
  /** The component's name. */
  name: string;
  /** Its kind: "Furniture", "Casework", "Plumbing", "Lighting", "Electrical", "Generic", "Door", "Window", "Niche", "TitleBlock" or "Detail". */
  kind: string;
  /** What wrote the file, e.g. "ConstructCraft 0.12.0". */
  generator: string;
  params: ComponentParam[];
  types: ComponentType[];
  /** Plumbing fixture or electrical device data as the file holds it, e.g. { Fixture: { drain_units, supply_weight, hot_water } }. */
  mep: Record<string, any> | null;
  connectors: ComponentConnector[];
  /** The box of all parts, or null when there are none. */
  bounds: ComponentBounds | null;
  /** The 3D pieces shown at the fine detail level, voids cut out. 2D components (title blocks, detail components) have none. */
  parts: Part[];
  errors: ComponentError[];
}
"#;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(typescript_type = "Component")]
    pub type ComponentJs;
}

/// Parse the text of a `.ccomp` file and tessellate its 3D pieces. Throws an
/// `Error` with the engine's message when the file does not parse.
#[wasm_bindgen]
pub fn load_component(text: &str) -> Result<ComponentJs, JsError> {
    let text = text.strip_prefix('\u{feff}').unwrap_or(text);
    let file = cc_core::component_file::from_ron(text).map_err(|e| JsError::new(&e.to_string()))?;
    let (info, parts) = component(&file);
    let serializer = serde_wasm_bindgen::Serializer::json_compatible();
    let out = info
        .serialize(&serializer)
        .map_err(|e| JsError::new(&e.to_string()))?;
    let list = js_sys::Array::new();
    for part in &parts {
        let item = PartInfo {
            name: &part.name,
            material: &part.material,
            color: part.color,
            transparency: part.transparency,
        }
        .serialize(&serializer)
        .map_err(|e| JsError::new(&e.to_string()))?;
        set(
            &item,
            "positions",
            &js_sys::Float32Array::from(&part.positions[..]),
        )?;
        set(
            &item,
            "normals",
            &js_sys::Float32Array::from(&part.normals[..]),
        )?;
        list.push(&item);
    }
    set(&out, "parts", &list)?;
    Ok(out.unchecked_into())
}

fn set(target: &JsValue, key: &str, value: &JsValue) -> Result<(), JsError> {
    js_sys::Reflect::set(target, &JsValue::from_str(key), value)
        .map(|_| ())
        .map_err(|_| JsError::new("could not build the result"))
}

/// Everything of a [`Component`] but its parts.
#[derive(Serialize)]
struct Info<'a> {
    name: &'a str,
    kind: String,
    generator: &'a str,
    params: Vec<Param<'a>>,
    types: Vec<TypeOut<'a>>,
    mep: Option<MepData>,
    connectors: Vec<Connector>,
    bounds: Option<Bounds>,
    errors: Vec<PieceError>,
}

#[derive(Serialize)]
struct Param<'a> {
    name: &'a str,
    kind: String,
    value: Value<'a>,
    instance: bool,
}

#[derive(Serialize)]
#[serde(untagged)]
enum Value<'a> {
    Number(f64),
    Text(&'a str),
}

#[derive(Serialize)]
struct TypeOut<'a> {
    name: &'a str,
    description: &'a str,
    values: &'a BTreeMap<String, f64>,
}

#[derive(Serialize)]
struct Connector {
    name: String,
    system: SystemKind,
    position: [f64; 3],
    direction: [f64; 3],
    diameter: Option<f64>,
}

#[derive(Serialize)]
struct Bounds {
    min: [f64; 3],
    max: [f64; 3],
}

#[derive(Serialize)]
struct PieceError {
    item: usize,
    name: String,
    message: String,
}

/// The scalar fields of a part (its arrays are added as typed arrays).
#[derive(Serialize)]
struct PartInfo<'a> {
    name: &'a str,
    material: &'a str,
    color: [u8; 3],
    transparency: f64,
}

/// A tessellated piece.
struct Mesh {
    name: String,
    material: String,
    color: [u8; 3],
    transparency: f64,
    positions: Vec<f32>,
    normals: Vec<f32>,
}

/// The component of `file` with its first type's values (the definition
/// carries them), no instance values, and its tessellated 3D pieces.
fn component(file: &ComponentFile) -> (Info<'_>, Vec<Mesh>) {
    let def = &file.def;
    let none = BTreeMap::new();
    // As the engine's component library resolves a file (`cc_app::library`):
    // doors and windows read the wall's thickness; others may ignore it.
    let extra = [(WALL_THICKNESS, PREVIEW_WALL)];
    let (parts, errors) = if def.kind.is_2d() {
        (Vec::new(), Vec::new())
    } else {
        (
            cc_geom::resolve_component_in(def, &none, &extra),
            cc_geom::resolve_pieces(def, &none, &extra).1,
        )
    };
    let name_of = |item: usize| def.items.get(item).map_or("", |i| i.name.as_str());
    let mut lo = DVec3::splat(f64::INFINITY);
    let mut hi = DVec3::splat(f64::NEG_INFINITY);
    let mut meshes = Vec::new();
    // Plan symbols are no solids, voids are cut out already, and the viewer
    // shows the fine detail level.
    for part in parts
        .iter()
        .filter(|p| !p.plan_only && !p.void && p.detail.fine)
    {
        let Some((positions, normals, (a, b))) = tessellate(part) else {
            continue;
        };
        lo = lo.min(a);
        hi = hi.max(b);
        let material = file.materials.iter().find(|m| m.name == part.material);
        meshes.push(Mesh {
            name: name_of(part.item).to_string(),
            material: part.material.clone(),
            color: material.map_or(NO_MATERIAL, Material::shading_color),
            transparency: material
                .map(|m| m.graphics.transparency)
                .filter(|t| t.is_finite())
                .map_or(0.0, |t| t.clamp(0.0, 1.0)),
            positions,
            normals,
        });
    }
    let info = Info {
        name: &file.component,
        kind: format!("{:?}", def.kind),
        generator: &file.generator,
        params: def
            .params
            .iter()
            .map(|p| Param {
                name: &p.name,
                kind: format!("{:?}", p.kind),
                value: if p.kind.is_text() {
                    Value::Text(&p.text)
                } else {
                    Value::Number(p.value)
                },
                instance: p.instance,
            })
            .collect(),
        types: file
            .types
            .iter()
            .map(|t| TypeOut {
                name: &t.name,
                description: &t.info.description,
                values: &t.values,
            })
            .collect(),
        mep: def.mep,
        connectors: def
            .resolve_connectors(&none)
            .into_iter()
            .map(|c| Connector {
                name: c.name,
                system: c.system,
                position: c.point.to_array(),
                direction: c.direction.vector().to_array(),
                diameter: c.diameter,
            })
            .collect(),
        bounds: (!meshes.is_empty()).then(|| Bounds {
            min: lo.to_array(),
            max: hi.to_array(),
        }),
        errors: errors
            .into_iter()
            .map(|(item, e)| PieceError {
                item,
                name: name_of(item).to_string(),
                message: e.to_string(),
            })
            .collect(),
    };
    (info, meshes)
}

type Tessellated = (Vec<f32>, Vec<f32>, (DVec3, DVec3));

/// The triangles of a piece as the engine's 3D view draws them (its faces
/// triangulated, smooth normals on the facets of curved surfaces), each wound
/// counter-clockwise about its face's outward normal, with their box; `None`
/// when no triangle is left.
fn tessellate(part: &ComponentPart) -> Option<Tessellated> {
    let mut solid = Solid::new(ElementId(0), Category::Component, NO_MATERIAL);
    solid.add_part(part);
    let mut positions = Vec::new();
    let mut normals = Vec::new();
    let mut lo = DVec3::splat(f64::INFINITY);
    let mut hi = DVec3::splat(f64::NEG_INFINITY);
    for (face, shading) in solid.faces.iter().zip(solid.vertex_normals()) {
        for [a, b, c] in face.triangulate() {
            let corner = |i: usize| Some((*face.verts.get(i)?, *shading.get(i)?));
            let (Some(pa), Some(pb), Some(pc)) = (corner(a), corner(b), corner(c)) else {
                continue;
            };
            if ![pa, pb, pc]
                .iter()
                .all(|(p, n)| p.is_finite() && n.is_finite())
            {
                continue;
            }
            let reversed = (pb.0 - pa.0).cross(pc.0 - pa.0).dot(face.normal) < 0.0;
            let tri = if reversed { [pa, pc, pb] } else { [pa, pb, pc] };
            for (p, n) in tri {
                lo = lo.min(p);
                hi = hi.max(p);
                positions.extend(p.as_vec3().to_array());
                normals.extend(n.as_vec3().to_array());
            }
        }
    }
    (!positions.is_empty()).then_some((positions, normals, (lo, hi)))
}
