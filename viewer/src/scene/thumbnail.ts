// Thumbnails of components, rendered by ONE shared offscreen WebGL renderer
// (never one context per card). Requests are queued and rendered one at a
// time; every scene resource is freed after each render.

import { Box3, PerspectiveCamera, Scene, Vector3, WebGLRenderer } from 'three';
import type { Component } from '../engine';
import { buildComponentObject } from './component-object';
import { SceneLights } from './lighting';
import { CAMERA_FOV, VIEW_ANGLES, boundsToBox, fitDistance, viewDirection } from './views';

export interface ThumbnailOptions {
  /** Feature edges. Contract: pass `edgesForFolder(folder)` (false for planting). Default true. */
  edges?: boolean;
  /** Free margin around the component (fraction of the half-extent). Default 0.06. */
  margin?: number;
}

export class ThumbnailError extends Error {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = 'ThumbnailError';
  }
}

interface Shared {
  renderer: WebGLRenderer;
  scene: Scene;
  camera: PerspectiveCamera;
  lights: SceneLights;
}

let shared: Shared | null = null;
let queue: Promise<unknown> = Promise.resolve();

function getShared(): Shared {
  if (shared) return shared;
  const canvas = document.createElement('canvas');
  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setClearColor(0x000000, 0);
  const camera = new PerspectiveCamera(CAMERA_FOV, 1, 0.01, 100);
  camera.up.set(0, 0, 1);
  const scene = new Scene();
  const lights = new SceneLights();
  scene.add(lights);
  canvas.addEventListener('webglcontextlost', () => disposeThumbnailRenderer());
  shared = { renderer, scene, camera, lights };
  return shared;
}

function toBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new ThumbnailError('Canvas produced no image'))), 'image/png');
  });
}

async function render(component: Component, sizePx: number, options: ThumbnailOptions): Promise<Blob> {
  if (!component.bounds) throw new ThumbnailError(`${component.name} has no 3D geometry`);
  const { renderer, scene, camera, lights } = getShared();
  const size = Math.max(16, Math.min(2048, Math.round(sizePx)));
  renderer.setSize(size, size, false);

  const box: Box3 = boundsToBox(component.bounds);
  const center = box.getCenter(new Vector3());
  const direction = viewDirection(VIEW_ANGLES.iso);
  const distance = fitDistance(box, direction, CAMERA_FOV, 1, options.margin ?? 0.06);
  const radius = box.getSize(new Vector3()).length() / 2;
  camera.aspect = 1;
  camera.near = Math.max(0.005, distance - radius * 1.5);
  camera.far = distance + radius * 1.5;
  camera.position.copy(center).addScaledVector(direction, distance);
  camera.lookAt(center);
  camera.updateProjectionMatrix();
  lights.aim(center);

  const object = buildComponentObject(component, { edges: options.edges ?? true });
  scene.add(object);
  try {
    renderer.render(scene, camera);
    // toBlob snapshots the canvas synchronously, so the scene can be freed right after.
    const blob = toBlob(renderer.domElement);
    return await blob;
  } finally {
    object.dispose();
    renderer.renderLists.dispose();
  }
}

/**
 * Render a component in the iso view, fitted to its bounds with a small
 * margin, on a transparent background, without grid or dimensions, as a
 * `sizePx` x `sizePx` PNG. Calls are queued and rendered one after another on
 * one shared renderer. Use `URL.createObjectURL(blob)` to show it (and revoke
 * the URL when the image goes away).
 */
export function renderThumbnail(component: Component, sizePx: number, options: ThumbnailOptions = {}): Promise<Blob> {
  const result = queue.then(() => render(component, sizePx, options));
  queue = result.catch(() => undefined);
  return result;
}

/** Free the shared thumbnail renderer and its WebGL context (it is recreated on the next call). */
export function disposeThumbnailRenderer(): void {
  if (!shared) return;
  const { renderer } = shared;
  shared = null;
  renderer.dispose();
  renderer.forceContextLoss();
}

/** GPU resources currently held by the shared renderer (for leak checks). */
export function thumbnailRendererInfo(): { geometries: number; textures: number; programs: number } | null {
  if (!shared) return null;
  const info = shared.renderer.info;
  return { geometries: info.memory.geometries, textures: info.memory.textures, programs: info.programs?.length ?? 0 };
}
