// Scene lights: a hemisphere fill plus one directional key from the upper
// front-left. No shadows. Tuned so white ceramic keeps its shape on the light
// paper background and dark materials do not read as black blobs.

import { Color, DirectionalLight, Group, HemisphereLight, Vector3 } from 'three';

/** Direction the key light comes from (front = -Y, left = -X, up = +Z). */
const KEY_DIRECTION = new Vector3(-0.55, -0.75, 1.0).normalize();

/** A group of lights. Lights follow `target`, so call `aim(center)` when the component changes. */
export class SceneLights extends Group {
  private readonly key: DirectionalLight;

  constructor() {
    super();
    this.name = 'lights';
    const hemi = new HemisphereLight(new Color(0xffffff), new Color(0x8a96a6), 2.0);
    hemi.up.set(0, 0, 1);
    hemi.position.set(0, 0, 1);
    this.add(hemi);

    this.key = new DirectionalLight(0xffffff, 1.7);
    this.key.position.copy(KEY_DIRECTION);
    this.add(this.key);
    this.add(this.key.target);
  }

  /** Point the key light at `center`. */
  aim(center: Vector3): void {
    this.key.target.position.copy(center);
    this.key.position.copy(center).add(KEY_DIRECTION);
    this.key.target.updateMatrixWorld();
  }
}
