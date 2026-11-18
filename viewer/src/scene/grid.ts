// Ground grid: 10 cm cells with a heavier line every metre, thin ink lines at
// low opacity, extending a little past the component's footprint and fading
// out at the rim. Lines sit on absolute multiples of 10 cm.

import { BufferAttribute, BufferGeometry, LineBasicMaterial, LineSegments } from 'three';
import type { Box3 } from 'three';
import { scenePalette } from './palette';

const CELL = 0.1;
const MINOR_ALPHA = 0.14;
const MAJOR_ALPHA = 0.32;
/** Beyond this many cells per side the grid would be too dense to read; lines get coarser. */
const MAX_LINES = 40;
/** Minor line spacings tried in order, metres (all divide 1 m). */
const MINOR_STEPS = [CELL, 0.2, 0.5, 1];

/**
 * The plane the grid (and the dimension lines) sit on: the component's base,
 * or z = 0 above the object for ceiling fixtures (bounds entirely at or below 0).
 */
export function groundZ(box: Box3): number {
  return box.max.z <= 1e-6 && box.min.z < 0 ? 0 : box.min.z;
}

/** Margin around the footprint covered by the grid before it fades out, metres. */
export function gridMargin(box: Box3): number {
  const span = Math.max(box.max.x - box.min.x, box.max.y - box.min.y);
  return Math.max(0.3, Math.min(2, span * 0.35));
}

function smoothstep(edge0: number, edge1: number, x: number): number {
  const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

export class GroundGrid extends LineSegments<BufferGeometry, LineBasicMaterial> {
  constructor(box: Box3) {
    const palette = scenePalette();
    const margin = gridMargin(box);
    const z = groundZ(box);

    // 10 cm cells; for large footprints (trees) the minor step grows so the
    // grid does not turn into a solid tint. Metre lines are always kept.
    const span = Math.max(box.max.x - box.min.x, box.max.y - box.min.y) + 2 * margin;
    const step = MINOR_STEPS.find((s) => span / s <= MAX_LINES) ?? 1;

    // Lines sit on absolute multiples of the step.
    const snapDown = (v: number) => Math.floor(v / step + 1e-6) * step;
    const snapUp = (v: number) => Math.ceil(v / step - 1e-6) * step;
    const x0 = snapDown(box.min.x - margin);
    const x1 = snapUp(box.max.x + margin);
    const y0 = snapDown(box.min.y - margin);
    const y1 = snapUp(box.max.y + margin);
    const isMajor = (v: number) => Math.abs(v - Math.round(v)) < 1e-4;

    // Fade by the distance outside the footprint: full inside a small border, zero at the rim.
    const fadeStart = margin * 0.25;
    const alphaAt = (x: number, y: number) => {
      const dx = Math.max(box.min.x - x, 0, x - box.max.x);
      const dy = Math.max(box.min.y - y, 0, y - box.max.y);
      return 1 - smoothstep(fadeStart, margin, Math.hypot(dx, dy));
    };

    const positions: number[] = [];
    const colors: number[] = [];
    const { r, g, b } = palette.ink;
    const pushSegment = (ax: number, ay: number, bx: number, by: number, weight: number) => {
      const aa = alphaAt(ax, ay) * weight;
      const ba = alphaAt(bx, by) * weight;
      if (aa <= 0.001 && ba <= 0.001) return;
      positions.push(ax, ay, z, bx, by, z);
      colors.push(r, g, b, aa, r, g, b, ba);
    };

    // Each line is split into cell-long segments so the fade can vary along it.
    const lineCount = (a: number, b: number) => Math.round((b - a) / step);
    const nx = lineCount(x0, x1);
    const ny = lineCount(y0, y1);
    for (let i = 0; i <= nx; i++) {
      const x = x0 + i * step;
      const weight = isMajor(x) ? MAJOR_ALPHA : MINOR_ALPHA;
      for (let j = 0; j < ny; j++) pushSegment(x, y0 + j * step, x, y0 + (j + 1) * step, weight);
    }
    for (let j = 0; j <= ny; j++) {
      const y = y0 + j * step;
      const weight = isMajor(y) ? MAJOR_ALPHA : MINOR_ALPHA;
      for (let i = 0; i < nx; i++) pushSegment(x0 + i * step, y, x0 + (i + 1) * step, y, weight);
    }

    const geometry = new BufferGeometry();
    geometry.setAttribute('position', new BufferAttribute(new Float32Array(positions), 3));
    geometry.setAttribute('color', new BufferAttribute(new Float32Array(colors), 4));
    const material = new LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      depthWrite: false,
    });
    super(geometry, material);
    this.name = 'ground-grid';
    // Drawn before the component so its transparent lines never cover opaque parts it is behind.
    this.renderOrder = -1;
  }

  override dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
    this.removeFromParent();
  }
}
