// Dimension lines (cotas) for a component's bounds: width (X) and depth (Y)
// on the ground plane just outside the footprint, height (Z) on a vertical at
// a front corner. Thin accent lines with slash ticks and extension lines; the
// labels are HTML (CSS2DRenderer) so text stays crisp.
//
// `update(camera)` re-places them for the current view so labels stay legible:
// - width/depth go on the side of the footprint that faces the camera; when
//   the camera is near the ground plane (front and side views) they drop
//   below the base instead, since the ground plane is then seen edge-on;
// - the height goes on the vertical edge at the left of the silhouette (the
//   front-left corner in the iso view), pushed further left;
// - a dimension whose axis points at the camera is hidden (e.g. the height
//   seen from above).

import { BufferAttribute, BufferGeometry, Group, LineBasicMaterial, LineSegments, Vector2, Vector3 } from 'three';
import type { Box3, Camera } from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { groundZ } from './grid';
import { scenePalette } from './palette';

/** Dimensions smaller than this (metres) are not drawn. */
const MIN_DIMENSION = 0.01;
/** Hide a dimension when its axis is this close to the view direction (|cos|). */
const DEGENERATE_COS = 0.94;
/** Below this |view direction . Z| the ground plane is too oblique for width/depth to sit on it. */
const LOW_VIEW = 0.3;
/** Above this |view direction . Z| the view counts as a plan (top) view. */
const PLAN_VIEW = 0.9;

/** `1,50`: metres with a decimal comma and two decimals. */
export function formatMetres(value: number): string {
  return value.toFixed(2).replace('.', ',');
}

/** Distance from the box to the dimension lines, metres. */
export function dimensionOffset(box: Box3): number {
  const size = Math.max(box.max.x - box.min.x, box.max.y - box.min.y, box.max.z - box.min.z);
  return Math.min(0.45, Math.max(0.03, size * 0.09));
}

type Axis = 'x' | 'y' | 'z';
type Vec3 = [number, number, number];

interface Dimension {
  axis: Axis;
  value: number;
  lines: LineSegments<BufferGeometry, LineBasicMaterial>;
  label: CSS2DObject;
}

interface Placement {
  /** +1 / -1: side of the footprint facing the camera. */
  sideX: number;
  sideY: number;
  /** Camera near the ground plane: width/depth go below (or above, for ceiling fixtures) the base. */
  low: boolean;
  /**
   * Level of width/depth when they lie flat: the ground, or, when looking
   * (nearly) straight down or up, the face of the box towards the camera, so
   * perspective does not tuck them under the object.
   */
  planZ: number;
  /** Vertical edge (x, y) that carries the height, and the outward unit direction on the XY plane. */
  cornerX: number;
  cornerY: number;
  outX: number;
  outY: number;
}

const _dir = new Vector3();
const _right = new Vector3();
const _rightXY = new Vector2();
const _center = new Vector3();

export class DimensionSet extends Group {
  private readonly box: Box3;
  private readonly offset: number;
  private readonly z: number;
  /** -1 when the base is the bottom (floor items), +1 when it is the top (ceiling fixtures). */
  private readonly away: number;
  private readonly material: LineBasicMaterial;
  private readonly dimensions: Dimension[] = [];
  private placementKey = '';

  constructor(box: Box3) {
    super();
    this.name = 'dimensions';
    this.box = box.clone();
    this.offset = dimensionOffset(box);
    this.z = groundZ(box);
    this.away = this.z > box.min.z ? 1 : -1;
    const palette = scenePalette();
    this.material = new LineBasicMaterial({ color: palette.accent, depthWrite: false, transparent: true });

    const size = box.getSize(new Vector3());
    for (const axis of ['x', 'y', 'z'] as const) {
      const value = size[axis];
      if (value < MIN_DIMENSION) continue;
      const lines = new LineSegments(new BufferGeometry(), this.material);
      lines.renderOrder = 3;
      const element = document.createElement('div');
      element.className = 'cota-label';
      element.dataset.axis = axis;
      element.textContent = formatMetres(value);
      const label = new CSS2DObject(element);
      label.center.set(0.5, 0.5);
      this.add(lines, label);
      this.dimensions.push({ axis, value, lines, label });
    }
  }

  /** Re-place the dimensions for the camera. Cheap when the placement does not change. */
  update(camera: Camera): void {
    camera.updateMatrixWorld();
    camera.getWorldDirection(_dir);
    this.box.getCenter(_center);
    const placement = this.placementFor(camera);
    const key = JSON.stringify(placement);
    if (key !== this.placementKey) {
      this.placementKey = key;
      this.rebuild(placement);
    }
    for (const d of this.dimensions) {
      const visible = Math.abs(_dir[d.axis]) < DEGENERATE_COS;
      d.lines.visible = visible;
      d.label.visible = visible;
      // Belt and braces: CSS2DRenderer only hides labels it visits.
      d.label.element.style.visibility = visible && this.visible ? '' : 'hidden';
    }
  }

  private placementFor(camera: Camera): Placement {
    const { box } = this;
    const sideX = camera.position.x >= _center.x ? 1 : -1;
    const sideY = camera.position.y >= _center.y ? 1 : -1;
    const low = Math.abs(_dir.z) < LOW_VIEW;

    // Screen-right on the XY plane, quantised to 15 degrees so orbiting does not rebuild every frame.
    _right.setFromMatrixColumn(camera.matrixWorld, 0);
    _rightXY.set(_right.x, _right.y);
    if (_rightXY.lengthSq() < 1e-8) _rightXY.set(1, 0);
    const step = Math.PI / 12;
    const angle = Math.round(_rightXY.angle() / step) * step;
    const rx = Math.round(Math.cos(angle) * 1e6) / 1e6;
    const ry = Math.round(Math.sin(angle) * 1e6) / 1e6;

    // The vertical edge furthest to the left on screen; ties go to the one nearer the camera.
    let best: [number, number] = [box.min.x, box.min.y];
    let bestScore = Infinity;
    for (const cx of [box.min.x, box.max.x]) {
      for (const cy of [box.min.y, box.max.y]) {
        const screen = cx * rx + cy * ry;
        const towardCamera = -(cx * _dir.x + cy * _dir.y);
        const score = screen * 1000 - towardCamera;
        if (score < bestScore - 1e-9) {
          bestScore = score;
          best = [cx, cy];
        }
      }
    }
    const planZ = Math.abs(_dir.z) > PLAN_VIEW ? (_dir.z < 0 ? box.max.z : box.min.z) : this.z;
    return { sideX, sideY, low, planZ, cornerX: best[0], cornerY: best[1], outX: -rx, outY: -ry };
  }

  private rebuild(pl: Placement): void {
    const { box, offset, away } = this;
    const z = pl.planZ;
    const ext = offset * 0.3; // extension past the dimension line
    const gap = Math.min(0.02, offset * 0.25); // gap between the object and its extension lines
    const tick = offset * 0.16; // half tick, shrunk for tiny dimensions below
    const yEdge = pl.sideY > 0 ? box.max.y : box.min.y;
    const xEdge = pl.sideX > 0 ? box.max.x : box.min.x;
    // Base of the box (bottom for floor items, top for ceiling fixtures) and the level below/above it.
    const base = away < 0 ? box.min.z : box.max.z;
    const zLow = base + away * offset;

    for (const d of this.dimensions) {
      const p: number[] = [];
      const seg = (a: Vec3, b: Vec3) => p.push(...a, ...b);
      let mid: Vec3;
      const t = Math.min(tick, d.value * 0.2);
      if (d.axis === 'x' || d.axis === 'y') {
        const along = d.axis === 'x' ? 0 : 1;
        const a = d.axis === 'x' ? box.min.x : box.min.y;
        const b = d.axis === 'x' ? box.max.x : box.max.y;
        // Build in (u along the axis, v across it, w = z); map back to x, y, z.
        const map = (u: number, v: number, w: number): Vec3 => (along === 0 ? [u, v, w] : [v, u, w]);
        if (!pl.low) {
          const side = along === 0 ? pl.sideY : pl.sideX;
          const edge = along === 0 ? yEdge : xEdge;
          const line = edge + side * offset;
          seg(map(a, line, z), map(b, line, z));
          for (const u of [a, b]) {
            seg(map(u, edge + side * gap, z), map(u, line + side * ext, z));
            seg(map(u - t, line - t, z), map(u + t, line + t, z));
          }
          mid = map((a + b) / 2, line, z);
        } else {
          // Seen from the side: drop below the base, in the plane of the face towards the camera.
          const face = along === 0 ? yEdge : xEdge;
          seg(map(a, face, zLow), map(b, face, zLow));
          for (const u of [a, b]) {
            seg(map(u, face, base + away * gap), map(u, face, zLow + away * ext));
            seg(map(u - t, face, zLow - t), map(u + t, face, zLow + t));
          }
          mid = map((a + b) / 2, face, zLow);
        }
      } else {
        const a = box.min.z;
        const b = box.max.z;
        const x = pl.cornerX + pl.outX * offset;
        const y = pl.cornerY + pl.outY * offset;
        seg([x, y, a], [x, y, b]);
        for (const zz of [a, b]) {
          seg(
            [pl.cornerX + pl.outX * gap, pl.cornerY + pl.outY * gap, zz],
            [x + pl.outX * ext, y + pl.outY * ext, zz],
          );
          seg([x - pl.outX * t, y - pl.outY * t, zz - t], [x + pl.outX * t, y + pl.outY * t, zz + t]);
        }
        mid = [x, y, (a + b) / 2];
      }
      const geometry = d.lines.geometry;
      geometry.setAttribute('position', new BufferAttribute(new Float32Array(p), 3));
      geometry.computeBoundingSphere();
      d.label.position.set(...mid);
    }
  }

  /** The space the dimensions may occupy (the box grown by the dimension offset), for camera fitting. */
  static extent(box: Box3, out: Box3): Box3 {
    return out.copy(box).expandByScalar(dimensionOffset(box) * 1.35);
  }

  override dispose(): void {
    for (const d of this.dimensions) {
      d.lines.geometry.dispose();
      d.label.element.remove();
    }
    this.material.dispose();
    this.removeFromParent();
    this.clear();
  }
}
