// The pieces that Lua scripts make, baked by ConstructCraft.
//
// The geometry engine in wasm-pkg/ runs without Lua, so it reports each script
// piece of a component as an error ("script: …"). tools/scripted.py has ccad
// run those scripts for every type and writes their meshes to
// `scripted/<folder>/<name>.bin` (the format is described there); `withScripted`
// turns the meshes of the type shown into parts like the engine's — triangles
// with normals smooth across the facets of curved surfaces, and the outline
// edges — and adds them in place of those errors. Without a baked file the
// component is returned as the engine made it.

import { BufferAttribute, BufferGeometry, EdgesGeometry, ShapeUtils, Vector2, Vector3 } from 'three';
import { toCreasedNormals } from 'three/addons/utils/BufferGeometryUtils.js';
import type { Component, Part } from '../wasm-pkg/ccomp_viewer.js';

/** Faces meeting at less than this read as one curved surface: smooth normals and no line between them. */
const SMOOTH_ANGLE_DEG = 20;

const MAGIC = 'CCSM';
const VERSION = 1;

interface BakedPart {
  name: string;
  material: string;
  color: [number, number, number];
  transparency: number;
  vertices: Float32Array;
  sizes: Uint32Array;
  indices: Uint32Array;
}

interface BakedType {
  index: number;
  name: string;
  parts: BakedPart[];
}

interface HeaderPart {
  name: string;
  material: string;
  color: [number, number, number];
  transparency: number;
  vertices: number;
  faces: number;
  indices: number;
}

interface Header {
  types: { index: number; name: string; parts: HeaderPart[] }[];
}

/** Whether a piece error is a script that the engine could not run. */
export function isScriptError(error: { message: string }): boolean {
  return error.message.startsWith('script:');
}

/** `components/<folder>/<name>.ccomp` → `scripted/<folder>/<name>.bin`. */
export function scriptedPath(file: string): string | null {
  const m = /^components\/([a-z0-9-]+)\/([a-z0-9-]+)\.ccomp$/.exec(file);
  return m ? `scripted/${m[1]}/${m[2]}.bin` : null;
}

/** Read a baked file; throws on a malformed one. */
export function decodeScripted(buffer: ArrayBuffer): BakedType[] {
  const view = new DataView(buffer);
  const magic = new TextDecoder().decode(new Uint8Array(buffer, 0, 4));
  if (magic !== MAGIC) throw new Error('not a baked script file');
  const version = view.getUint32(4, true);
  if (version !== VERSION) throw new Error(`baked script file version ${version}, expected ${VERSION}`);
  const headerLength = view.getUint32(8, true);
  const header = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 12, headerLength))) as Header;
  let offset = 12 + headerLength;
  const take = <T>(make: (b: ArrayBuffer, o: number, n: number) => T, count: number): T => {
    if (offset + count * 4 > buffer.byteLength) throw new Error('baked script file is cut short');
    const out = make(buffer, offset, count);
    offset += count * 4;
    return out;
  };
  return header.types.map((t) => ({
    index: t.index,
    name: t.name,
    parts: t.parts.map((p) => ({
      name: p.name,
      material: p.material,
      color: p.color,
      transparency: p.transparency,
      vertices: take((b, o, n) => new Float32Array(b, o, n), p.vertices * 3),
      sizes: take((b, o, n) => new Uint32Array(b, o, n), p.faces),
      indices: take((b, o, n) => new Uint32Array(b, o, n), p.indices),
    })),
  }));
}

/** The faces of a baked part as non-indexed triangles, each wound like its face. */
function triangles(part: BakedPart): Float32Array {
  const { vertices: v, sizes, indices } = part;
  let count = 0;
  for (const n of sizes) count += n - 2;
  const out = new Float32Array(count * 9);
  let w = 0;
  const push = (i: number) => {
    out[w++] = v[3 * i]!;
    out[w++] = v[3 * i + 1]!;
    out[w++] = v[3 * i + 2]!;
  };
  const normal = new Vector3();
  const p = new Vector3();
  const q = new Vector3();
  const u = new Vector3();
  const t = new Vector3();
  let start = 0;
  for (const n of sizes) {
    const face = indices.subarray(start, start + n);
    start += n;
    if (n === 3) {
      push(face[0]!);
      push(face[1]!);
      push(face[2]!);
      continue;
    }
    // Newell's normal, then the face drawn on its plane and cut into triangles.
    normal.set(0, 0, 0);
    for (let k = 0; k < n; k++) {
      const a = face[k]!;
      const b = face[(k + 1) % n]!;
      p.set(v[3 * a]!, v[3 * a + 1]!, v[3 * a + 2]!);
      q.set(v[3 * b]!, v[3 * b + 1]!, v[3 * b + 2]!);
      normal.x += (p.y - q.y) * (p.z + q.z);
      normal.y += (p.z - q.z) * (p.x + q.x);
      normal.z += (p.x - q.x) * (p.y + q.y);
    }
    if (normal.lengthSq() === 0) continue;
    normal.normalize();
    u.set(Math.abs(normal.x) < 0.9 ? 1 : 0, Math.abs(normal.x) < 0.9 ? 0 : 1, 0).cross(normal).normalize();
    t.crossVectors(normal, u);
    const contour: Vector2[] = [];
    for (const i of face) {
      p.set(v[3 * i]!, v[3 * i + 1]!, v[3 * i + 2]!);
      contour.push(new Vector2(p.dot(u), p.dot(t)));
    }
    // (u, t, normal) is right-handed, so a face counter-clockwise about its normal is counter-clockwise here.
    for (const [a, b, c] of ShapeUtils.triangulateShape(contour, [])) {
      const ccw = ShapeUtils.area([contour[a]!, contour[b]!, contour[c]!]) >= 0;
      push(face[a]!);
      push(face[ccw ? b : c]!);
      push(face[ccw ? c : b]!);
    }
  }
  return w === out.length ? out : out.slice(0, w);
}

/** A baked part as a part of the engine's kind. */
function toPart(baked: BakedPart): Part | null {
  const positions = triangles(baked);
  if (positions.length === 0) return null;
  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new BufferAttribute(positions, 3));
  const smooth = toCreasedNormals(geometry, (SMOOTH_ANGLE_DEG * Math.PI) / 180);
  const edges = new EdgesGeometry(geometry, SMOOTH_ANGLE_DEG);
  const part = {
    name: baked.name,
    material: baked.material,
    color: baked.color,
    transparency: baked.transparency,
    positions: smooth.getAttribute('position').array as Float32Array,
    normals: smooth.getAttribute('normal').array as Float32Array,
    edges: edges.getAttribute('position').array as Float32Array,
  };
  geometry.dispose();
  smooth.dispose();
  edges.dispose();
  return part as Part;
}

const files = new Map<string, Promise<BakedType[] | null>>();

/** The baked file of a component, or null when there is none; cached, and retried after a network failure. */
function fetchScripted(url: string): Promise<BakedType[] | null> {
  let promise = files.get(url);
  if (!promise) {
    promise = (async () => {
      const response = await fetch(url);
      if (response.status === 404) return null;
      if (!response.ok) throw new Error(`HTTP ${response.status} fetching ${url}`);
      return decodeScripted(await response.arrayBuffer());
    })();
    promise.catch(() => files.delete(url));
    files.set(url, promise);
  }
  return promise;
}

/**
 * `component` with the baked pieces of its scripts added in place of their
 * errors, when it has script errors and a baked file covers the type shown.
 * Otherwise (or when the file cannot be read) `component` unchanged.
 */
export async function withScripted(file: string, component: Component, url: (path: string) => string): Promise<Component> {
  if (!component.errors.some(isScriptError)) return component;
  const path = scriptedPath(file);
  if (!path) return component;
  let baked: BakedType[] | null;
  try {
    baked = await fetchScripted(url(path));
  } catch (error) {
    console.warn(`Could not read the baked script pieces of ${file}:`, error);
    return component;
  }
  const shown = component.types[component.type_index]?.name;
  const type = baked?.find((t) => t.index === component.type_index && t.name === shown);
  if (!type) return component;
  const parts = type.parts.map(toPart).filter((p): p is Part => p !== null);
  const lo = component.bounds ? [...component.bounds.min] : [Infinity, Infinity, Infinity];
  const hi = component.bounds ? [...component.bounds.max] : [-Infinity, -Infinity, -Infinity];
  for (const part of parts) {
    const a = part.positions;
    for (let i = 0; i < a.length; i += 3) {
      for (let k = 0; k < 3; k++) {
        const x = a[i + k]!;
        if (x < lo[k]!) lo[k] = x;
        if (x > hi[k]!) hi[k] = x;
      }
    }
  }
  const all = [...component.parts, ...parts];
  return {
    ...component,
    parts: all,
    errors: component.errors.filter((e) => !isScriptError(e)),
    bounds:
      all.length > 0
        ? { min: lo as [number, number, number], max: hi as [number, number, number] }
        : component.bounds,
  };
}
