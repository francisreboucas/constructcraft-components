// An interactive 3D view of one component, mounted on a container element.
//
// Renders on demand only: a frame is drawn when the controls move, the
// container resizes, the component changes or a view transition runs. The
// requestAnimationFrame loop exists only while something is moving (damping
// or a transition).

import { Box3, PerspectiveCamera, Scene, Vector3, WebGLRenderer } from 'three';
import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import type { Component } from '../engine';
import { buildComponentObject, type ComponentObject } from './component-object';
import { DimensionSet } from './dimensions';
import { GroundGrid } from './grid';
import { SceneLights } from './lighting';
import {
  CAMERA_FOV,
  VIEW_ANGLES,
  anglesOf,
  boundsToBox,
  fitDistance,
  prefersReducedMotion,
  viewDirection,
  type ViewAngles,
  type ViewName,
} from './views';

export interface ComponentDisplayOptions {
  /** Feature edges. Contract: pass `edgesForFolder(folder)` (false for planting). Default true. */
  edges?: boolean;
  /** Ground grid. Default true. */
  grid?: boolean;
  /** Dimension lines (cotas). Default true. */
  dimensions?: boolean;
  /** View to frame the new component in. Default: the current view (`iso` at first). */
  view?: ViewName;
  /**
   * Keep looking from where the camera is when the user has orbited away from
   * the presets (another type of the same component), instead of going back
   * to a preset view. The distance is fitted to the new component.
   */
  keepOrbit?: boolean;
}

export interface SetViewOptions {
  /** Ease the camera to the view. Default true; always off under prefers-reduced-motion. */
  animate?: boolean;
}

/** Duration of the eased transition between preset views, ms. */
const TRANSITION_MS = 450;
/** Free margin around the framed content (fraction of the half-extent). */
const FIT_MARGIN = 0.08;

function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function shortestAngle(from: number, to: number): number {
  let d = (to - from) % (2 * Math.PI);
  if (d > Math.PI) d -= 2 * Math.PI;
  if (d < -Math.PI) d += 2 * Math.PI;
  return d;
}

interface Transition {
  start: number;
  from: { angles: ViewAngles; distance: number };
  to: { angles: ViewAngles; distance: number };
}

/**
 * State exposed on the container for tests and styling:
 * `data-view` (current preset or `free` after the user orbits),
 * `data-rendered` ("true" once a component has been drawn),
 * `data-moving` (present while a transition or damping runs).
 */
export class Viewport {
  readonly container: HTMLElement;
  readonly canvas: HTMLCanvasElement;
  readonly camera: PerspectiveCamera;

  private readonly renderer: WebGLRenderer;
  private readonly labels: CSS2DRenderer;
  private readonly controls: OrbitControls;
  private readonly scene = new Scene();
  private readonly lights = new SceneLights();
  private readonly resizeObserver: ResizeObserver;

  private object: ComponentObject | null = null;
  private grid: GroundGrid | null = null;
  private dimensions: DimensionSet | null = null;
  private box: Box3 | null = null;
  /** The box used for framing: the component plus room for the dimensions. */
  private readonly frameBox = new Box3();

  private currentView: ViewName | 'free' = 'iso';
  private transition: Transition | null = null;
  private frame = 0;
  private disposed = false;
  private interacting = false;

  constructor(container: HTMLElement) {
    this.container = container;
    if (getComputedStyle(container).position === 'static') container.style.position = 'relative';

    this.renderer = new WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.setClearColor(0x000000, 0);
    this.canvas = this.renderer.domElement;
    this.canvas.style.display = 'block';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    container.appendChild(this.canvas);

    this.labels = new CSS2DRenderer();
    const overlay = this.labels.domElement;
    overlay.classList.add('viewport-labels');
    overlay.style.position = 'absolute';
    overlay.style.inset = '0';
    overlay.style.pointerEvents = 'none';
    container.appendChild(overlay);

    this.camera = new PerspectiveCamera(CAMERA_FOV, 1, 0.01, 100);
    this.camera.up.set(0, 0, 1);
    this.scene.add(this.lights);

    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.12;
    this.controls.screenSpacePanning = true;
    this.controls.addEventListener('change', this.onControlsChange);
    this.controls.addEventListener('start', this.onControlsStart);
    this.controls.addEventListener('end', this.onControlsEnd);

    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(container);
    this.resize();
  }

  /** The preset the camera is at, or `free` after the user orbited away from it. */
  get view(): ViewName | 'free' {
    return this.currentView;
  }

  /**
   * Show a component (replacing the previous one, which is disposed), framed
   * in `options.view`. `null` clears the view.
   */
  setComponent(component: Component | null, options: ComponentDisplayOptions = {}): void {
    const orbit = this.object ? anglesOf(this.camera.position.clone().sub(this.controls.target)) : null;
    this.clearComponent();
    if (!component || !component.bounds) {
      this.requestRender();
      return;
    }
    const box = boundsToBox(component.bounds);
    this.box = box;
    this.object = buildComponentObject(component, { edges: options.edges ?? true });
    this.scene.add(this.object);

    this.grid = new GroundGrid(box);
    this.grid.visible = options.grid ?? true;
    this.scene.add(this.grid);

    this.dimensions = new DimensionSet(box);
    this.dimensions.visible = options.dimensions ?? true;
    this.scene.add(this.dimensions);

    this.updateFrameBox();
    const center = box.getCenter(new Vector3());
    this.lights.aim(center);
    this.controls.target.copy(center);

    if (options.keepOrbit && options.view === undefined && this.currentView === 'free' && orbit) {
      this.transition = null;
      this.placeCamera(orbit, this.fitDistanceFor(orbit));
      this.requestRender();
    } else {
      const view = options.view ?? (this.currentView === 'free' ? 'iso' : this.currentView);
      this.setView(view, { animate: false });
    }
    this.container.dataset.rendered = 'false';
  }

  /** Show or hide the ground grid. */
  setGridVisible(visible: boolean): void {
    if (this.grid) this.grid.visible = visible;
    this.requestRender();
  }

  /** Show or hide the dimension lines. */
  setDimensionsVisible(visible: boolean): void {
    if (this.dimensions) {
      this.dimensions.visible = visible;
      this.updateFrameBox();
    }
    this.requestRender();
  }

  /** Move the camera to a preset view, with a short eased transition unless reduced motion is preferred. */
  setView(view: ViewName, options: SetViewOptions = {}): void {
    this.currentView = view;
    this.container.dataset.view = view;
    if (!this.box) return;
    const target = { angles: VIEW_ANGLES[view], distance: this.fitDistanceFor(VIEW_ANGLES[view]) };
    const animate = (options.animate ?? true) && !prefersReducedMotion();
    if (!animate) {
      this.transition = null;
      this.placeCamera(target.angles, target.distance);
      this.requestRender();
      return;
    }
    const offset = this.camera.position.clone().sub(this.controls.target);
    this.transition = {
      start: performance.now(),
      from: { angles: anglesOf(offset), distance: offset.length() },
      to: target,
    };
    this.container.dataset.moving = 'true';
    this.requestRender();
  }

  /** Draw a frame soon (coalesced to one per animation frame). */
  requestRender(): void {
    if (this.disposed || this.frame) return;
    this.frame = requestAnimationFrame(this.renderFrame);
  }

  /** Stop rendering and free the WebGL context, DOM nodes and scene resources. */
  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    if (this.frame) cancelAnimationFrame(this.frame);
    this.frame = 0;
    this.resizeObserver.disconnect();
    this.controls.removeEventListener('change', this.onControlsChange);
    this.controls.removeEventListener('start', this.onControlsStart);
    this.controls.removeEventListener('end', this.onControlsEnd);
    this.controls.dispose();
    this.clearComponent();
    this.renderer.dispose();
    this.renderer.forceContextLoss();
    this.canvas.remove();
    this.labels.domElement.remove();
    delete this.container.dataset.view;
    delete this.container.dataset.rendered;
    delete this.container.dataset.moving;
  }

  // -------------------------------------------------------------------------

  private clearComponent(): void {
    this.object?.dispose();
    this.grid?.dispose();
    this.dimensions?.dispose();
    this.object = null;
    this.grid = null;
    this.dimensions = null;
    this.box = null;
  }

  private updateFrameBox(): void {
    if (!this.box) return;
    if (this.dimensions?.visible) DimensionSet.extent(this.box, this.frameBox);
    else this.frameBox.copy(this.box);
    const radius = this.frameBox.getSize(new Vector3()).length() / 2;
    const fit = this.fitDistanceFor(VIEW_ANGLES.iso);
    this.controls.minDistance = Math.max(0.05, radius * 0.6);
    this.controls.maxDistance = fit * 4;
    this.camera.near = Math.max(0.005, radius * 0.02);
    this.camera.far = fit * 4 + radius * 4;
    this.camera.updateProjectionMatrix();
  }

  private fitDistanceFor(angles: ViewAngles): number {
    const direction = viewDirection(angles);
    return fitDistance(this.frameBox, direction, CAMERA_FOV, Math.max(this.camera.aspect, 0.1), FIT_MARGIN);
  }

  private placeCamera(angles: ViewAngles, distance: number): void {
    const direction = viewDirection(angles);
    // Frame on the framing box centre so the dimensions fit too; orbit around the component centre.
    this.camera.position.copy(this.controls.target).addScaledVector(direction, distance);
    this.camera.lookAt(this.controls.target);
    this.controls.update();
  }

  private resize(): void {
    const width = Math.max(1, this.container.clientWidth);
    const height = Math.max(1, this.container.clientHeight);
    this.renderer.setSize(width, height, false);
    this.labels.setSize(width, height);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    if (this.box) this.updateFrameBox();
    this.requestRender();
  }

  private readonly onControlsStart = (): void => {
    this.interacting = true;
    this.transition = null;
  };

  private readonly onControlsEnd = (): void => {
    this.interacting = false;
    this.requestRender();
  };

  private readonly onControlsChange = (): void => {
    if (this.interacting && this.currentView !== 'free') {
      this.currentView = 'free';
      this.container.dataset.view = 'free';
    }
    this.requestRender();
  };

  private readonly renderFrame = (now: number): void => {
    this.frame = 0;
    if (this.disposed) return;

    let moving = false;
    if (this.transition) {
      const { start, from, to } = this.transition;
      const t = Math.min(1, (now - start) / TRANSITION_MS);
      const k = easeInOutCubic(t);
      const angles = {
        azimuth: from.angles.azimuth + shortestAngle(from.angles.azimuth, to.angles.azimuth) * k,
        polar: from.angles.polar + (to.angles.polar - from.angles.polar) * k,
      };
      this.placeCamera(angles, from.distance + (to.distance - from.distance) * k);
      if (t >= 1) this.transition = null;
      else moving = true;
    } else {
      // Advances damping; emits `change` (which requests the next frame) while still moving.
      moving = this.controls.update();
    }

    if (moving) this.container.dataset.moving = 'true';
    else delete this.container.dataset.moving;

    this.dimensions?.update(this.camera);
    this.renderer.render(this.scene, this.camera);
    this.labels.render(this.scene, this.camera);
    if (this.box) this.container.dataset.rendered = 'true';

    if (moving) this.requestRender();
  };
}
