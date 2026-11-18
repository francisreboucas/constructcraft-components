import type { Route } from '../catalog';

/** Mounts a page into `root`; returns a cleanup function run before the next page mounts. */
export type Page = (root: HTMLElement, route: Route) => () => void;

/** Page load state, exposed as `<html data-state>` for tests: loading, ready or error. */
export function setPageState(state: 'loading' | 'ready' | 'error'): void {
  document.documentElement.dataset.state = state;
}
