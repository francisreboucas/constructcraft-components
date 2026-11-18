import type { Route } from '../catalog';
import type { Shell } from '../shell';

export interface PageContext {
  /** The route shown before this one, or null on first load. */
  previous: Route | null;
}

/** Mounts a page into `shell.main`; returns a cleanup function run before the next page mounts. */
export type Page = (shell: Shell, route: Route, context: PageContext) => () => void;

/** Page load state, exposed as `<html data-state>` for tests: loading, ready or error. */
export function setPageState(state: 'loading' | 'ready' | 'error'): void {
  document.documentElement.dataset.state = state;
}

export const SITE_TITLE = 'Componentes ConstructCraft';

/** Sets `document.title` to "<prefix> · Componentes ConstructCraft", or the site title alone. */
export function setTitle(prefix?: string): void {
  document.title = prefix ? `${prefix} · ${SITE_TITLE}` : SITE_TITLE;
}

export function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

/** Whether a key event comes from a text field (where single-key shortcuts must not fire). */
export function isTyping(event: KeyboardEvent): boolean {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return false;
  if (target.isContentEditable) return true;
  if (target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement) return true;
  if (target instanceof HTMLInputElement) {
    return !['checkbox', 'radio', 'button', 'submit', 'reset', 'range', 'color'].includes(target.type);
  }
  return false;
}

/** Whether a key event carries a modifier that should leave it to the browser. */
export function hasModifier(event: KeyboardEvent): boolean {
  return event.ctrlKey || event.metaKey || event.altKey;
}
