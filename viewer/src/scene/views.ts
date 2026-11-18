// Preset views and camera fitting, in the engine's Z-up frame
// (X right, +Y towards the wall/back, front = the -Y side).

import { Box3, Vector3 } from 'three';
import type { ComponentBounds } from '../engine';

export type ViewName = 'iso' | 'front' | 'top' | 'side';

export const VIEW_NAMES: readonly ViewName[] = ['iso', 'front', 'top', 'side'];

/** Vertical field of view of the perspective camera: narrow, so it reads like an axonometric drawing. */
export const CAMERA_FOV = 30;

/** Spherical angles of a view, Z up: `azimuth` from +X towards +Y, `polar` from +Z. Radians. */
export interface ViewAngles {
  azimuth: number;
  polar: number;
}

const DEG = Math.PI / 180;

export const VIEW_ANGLES: Readonly<Record<ViewName, ViewAngles>> = {
  // Front-right-above.
  iso: { azimuth: -50 * DEG, polar: 62 * DEG },
  // From the -Y side, looking towards +Y.
  front: { azimuth: -90 * DEG, polar: 90 * DEG },
  // From above; the tiny tilt keeps +Y up on screen with camera.up = +Z.
  top: { azimuth: -90 * DEG, polar: 0.001 },
  // From the right (+X), looking towards -X.
  side: { azimuth: 0, polar: 90 * DEG },
};

/** Unit vector from the target towards the camera. */
export function viewDirection(angles: ViewAngles, out = new Vector3()): Vector3 {
  const s = Math.sin(angles.polar);
  return out.set(s * Math.cos(angles.azimuth), s * Math.sin(angles.azimuth), Math.cos(angles.polar));
}

/** Angles of a (not necessarily unit) offset from the target to the camera. */
export function anglesOf(offset: Vector3): ViewAngles {
  const r = offset.length() || 1;
  return {
    azimuth: Math.atan2(offset.y, offset.x),
    polar: Math.acos(Math.min(1, Math.max(-1, offset.z / r))),
  };
}

export function boundsToBox(bounds: ComponentBounds, out = new Box3()): Box3 {
  out.min.fromArray(bounds.min);
  out.max.fromArray(bounds.max);
  return out;
}

const UP = new Vector3(0, 0, 1);
const _right = new Vector3();
const _up = new Vector3();
const _corner = new Vector3();
const _center = new Vector3();

/**
 * Camera distance from the box centre, along `direction` (unit, target to
 * camera), at which every corner of `box` fits the frustum with `margin`
 * (0.1 = 10 % of the half-extent left free on the tighter axis).
 */
export function fitDistance(box: Box3, direction: Vector3, fovDeg: number, aspect: number, margin = 0.1): number {
  const tanV = Math.tan((fovDeg * DEG) / 2) / (1 + margin);
  const tanH = tanV * aspect;
  // Camera basis (same as lookAt with up = +Z; a straight-down view uses +Y as up).
  _right.crossVectors(UP, direction);
  if (_right.lengthSq() < 1e-8) _right.set(1, 0, 0);
  _right.normalize();
  _up.crossVectors(direction, _right).normalize();
  box.getCenter(_center);

  let distance = 0;
  for (let i = 0; i < 8; i++) {
    _corner.set(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z);
    _corner.sub(_center);
    const u = Math.abs(_corner.dot(_right));
    const v = Math.abs(_corner.dot(_up));
    const w = _corner.dot(direction); // towards the camera
    distance = Math.max(distance, u / tanH + w, v / tanV + w);
  }
  // Never closer than the bounding sphere allows (keeps the near plane sane).
  const radius = box.getSize(_corner).length() / 2;
  return Math.max(distance, radius * 1.05, 0.05);
}

export function prefersReducedMotion(): boolean {
  return typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}
