// Turns an engine `Component` into three.js meshes.
//
// Parts are merged by (colour, transparency) so a component becomes a handful
// of draw calls. Geometry stays in the engine's frame: metres, Z up, X right,
// +Y towards the wall. Cameras looking at it must set `up = (0, 0, 1)`.

import {
  BufferAttribute,
  BufferGeometry,
  Color,
  DoubleSide,
  FrontSide,
  Group,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshStandardMaterial,
  SRGBColorSpace,
} from 'three';
import type { Component, Part } from '../engine';
import { EDGE_OPACITY, scenePalette } from './palette';

export interface BuildOptions {
  /**
   * Draw the engine's outline edges (`Part.edges`) in the ink colour.
   * Contract: pass `edgesForFolder(entry.folder)` from catalog.ts, which is
   * false for `planting` (foliage meshes turn into noise). Default true.
   */
  edges?: boolean;
}

/** Render order of transparent parts: after the opaque ones and the edges. */
const TRANSPARENT_ORDER = 2;

/** The meshes of one component. Call `dispose()` when it leaves the scene. */
export class ComponentObject extends Group {
  readonly triangles: number;
  private disposed = false;

  constructor(triangles: number) {
    super();
    this.triangles = triangles;
    this.name = 'component';
  }

  /** Free every geometry and material this object created. Safe to call twice. */
  override dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    const materials = new Set<{ dispose(): void }>();
    this.traverse((child) => {
      if (child instanceof Mesh || child instanceof LineSegments) {
        (child.geometry as BufferGeometry).dispose();
        const material = child.material as { dispose(): void } | { dispose(): void }[];
        for (const m of Array.isArray(material) ? material : [material]) materials.add(m);
      }
    });
    for (const m of materials) m.dispose();
    this.removeFromParent();
    this.clear();
  }
}

interface PartGroup {
  color: [number, number, number];
  transparency: number;
  parts: Part[];
}

function groupParts(parts: readonly Part[]): PartGroup[] {
  const groups = new Map<string, PartGroup>();
  for (const part of parts) {
    if (part.positions.length === 0 || part.transparency >= 1) continue;
    const transparency = Math.round(part.transparency * 100) / 100;
    const key = `${part.color.join(',')}|${transparency}`;
    let group = groups.get(key);
    if (!group) {
      group = { color: part.color, transparency, parts: [] };
      groups.set(key, group);
    }
    group.parts.push(part);
  }
  return [...groups.values()];
}

function mergeGeometry(parts: readonly Part[]): BufferGeometry {
  let length = 0;
  for (const p of parts) length += p.positions.length;
  const positions = new Float32Array(length);
  const normals = new Float32Array(length);
  let offset = 0;
  for (const p of parts) {
    positions.set(p.positions, offset);
    // The engine gives one normal per vertex; guard against a short array anyway.
    if (p.normals.length === p.positions.length) normals.set(p.normals, offset);
    offset += p.positions.length;
  }
  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new BufferAttribute(positions, 3));
  geometry.setAttribute('normal', new BufferAttribute(normals, 3));
  if (parts.some((p) => p.normals.length !== p.positions.length)) geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  return geometry;
}

/** The outline edges of the parts as one line-segment geometry, or null when they have none. */
function mergeEdges(parts: readonly Part[]): BufferGeometry | null {
  let length = 0;
  for (const p of parts) length += p.edges.length;
  if (length === 0) return null;
  const positions = new Float32Array(length);
  let offset = 0;
  for (const p of parts) {
    positions.set(p.edges, offset);
    offset += p.edges.length;
  }
  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new BufferAttribute(positions, 3));
  return geometry;
}

/**
 * Build the meshes for a component: one `MeshStandardMaterial` mesh per
 * (colour, transparency) group, plus optional feature edges.
 */
export function buildComponentObject(component: Component, options: BuildOptions = {}): ComponentObject {
  const edges = options.edges ?? true;
  const palette = scenePalette();
  let triangles = 0;
  for (const p of component.parts) triangles += p.positions.length / 9;
  const root = new ComponentObject(triangles);

  const edgeMaterial = edges
    ? new LineBasicMaterial({
        color: palette.ink,
        transparent: true,
        opacity: EDGE_OPACITY,
        depthWrite: false,
      })
    : null;

  for (const group of groupParts(component.parts)) {
    const geometry = mergeGeometry(group.parts);
    const transparent = group.transparency > 0;
    const material = new MeshStandardMaterial({
      color: new Color().setRGB(group.color[0] / 255, group.color[1] / 255, group.color[2] / 255, SRGBColorSpace),
      roughness: 0.85,
      metalness: 0,
      transparent,
      opacity: transparent ? 1 - group.transparency : 1,
      depthWrite: !transparent,
      side: transparent ? DoubleSide : FrontSide,
      // Push faces back a little so coplanar edges are never hidden by them.
      polygonOffset: true,
      polygonOffsetFactor: 1,
      polygonOffsetUnits: 1,
    });
    const mesh = new Mesh(geometry, material);
    mesh.name = group.parts.map((p) => p.name).join(', ');
    if (transparent) mesh.renderOrder = TRANSPARENT_ORDER;
    root.add(mesh);

    const edgeGeometry = edgeMaterial ? mergeEdges(group.parts) : null;
    if (edgeMaterial && edgeGeometry) {
      const lines = new LineSegments(edgeGeometry, edgeMaterial);
      lines.renderOrder = 1;
      root.add(lines);
    }
  }
  return root;
}
