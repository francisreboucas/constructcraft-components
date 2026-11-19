// The ConstructCraft geometry engine (WebAssembly) and the component loader.
//
// `loadComponent(file)` fetches `library/<file>` relative to the page, parses
// and tessellates it in the engine with the values of one of its types, adds
// the pieces of its Lua scripts when ConstructCraft baked them (scripted.ts),
// and caches the result. The cache is bounded
// both by entry count and by total triangle count, because planting meshes are
// much heavier than the parametric components.

import initWasm, { load_component } from '../wasm-pkg/ccomp_viewer.js';
import type { Component } from '../wasm-pkg/ccomp_viewer.js';
import { withScripted } from './scripted';

export type {
  Component,
  ComponentBounds,
  ComponentConnector,
  ComponentError,
  ComponentParam,
  ComponentType,
  Part,
} from '../wasm-pkg/ccomp_viewer.js';

/** Why a component could not be loaded. */
export type LoadErrorKind = 'network' | 'parse' | 'engine';

/** Base class of every loader error; `file` is the catalog path that failed. */
export class ComponentLoadError extends Error {
  readonly kind: LoadErrorKind;
  readonly file: string;

  constructor(kind: LoadErrorKind, file: string, message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = 'ComponentLoadError';
    this.kind = kind;
    this.file = file;
  }
}

/** The file could not be fetched (offline, 404...). `status` is 0 when no response arrived. */
export class ComponentNetworkError extends ComponentLoadError {
  readonly status: number;

  constructor(file: string, status: number, message: string, options?: { cause?: unknown }) {
    super('network', file, message, options);
    this.name = 'ComponentNetworkError';
    this.status = status;
  }
}

/** The engine rejected the file's text. */
export class ComponentParseError extends ComponentLoadError {
  constructor(file: string, message: string, options?: { cause?: unknown }) {
    super('parse', file, message, options);
    this.name = 'ComponentParseError';
  }
}

/** The WebAssembly engine itself failed to start. */
export class EngineInitError extends ComponentLoadError {
  constructor(file: string, message: string, options?: { cause?: unknown }) {
    super('engine', file, message, options);
    this.name = 'EngineInitError';
  }
}

const WASM_URL = new URL('../wasm-pkg/ccomp_viewer_bg.wasm', import.meta.url);

let initPromise: Promise<void> | null = null;

/** Start the engine once; later calls return the same promise. Retried after a failure. */
export function initEngine(): Promise<void> {
  if (!initPromise) {
    initPromise = initWasm({ module_or_path: WASM_URL }).then(
      () => undefined,
      (error: unknown) => {
        initPromise = null;
        throw error;
      },
    );
  }
  return initPromise;
}

/** Absolute URL of a library file (`catalog.json`, `components/<folder>/<name>.ccomp`). */
export function libraryUrl(path: string): string {
  return new URL(`library/${path}`, document.baseURI).href;
}

/** Number of triangles across all parts. */
export function triangleCount(component: Component): number {
  let floats = 0;
  for (const part of component.parts) floats += part.positions.length;
  return floats / 9;
}

// ---------------------------------------------------------------------------
// Cache

/** Cache bounds; whichever is hit first evicts the least recently used entries. */
export const CACHE_LIMITS = { maxEntries: 40, maxTriangles: 250_000 } as const;

interface CacheEntry {
  promise: Promise<Component>;
  /** Known once the promise resolves. */
  triangles: number;
}

const cache = new Map<string, CacheEntry>();
let cachedTriangles = 0;

function touch(file: string, entry: CacheEntry): void {
  cache.delete(file);
  cache.set(file, entry);
}

function evict(keep: string): void {
  for (const [file, entry] of cache) {
    if (cache.size <= CACHE_LIMITS.maxEntries && cachedTriangles <= CACHE_LIMITS.maxTriangles) break;
    if (file === keep) continue;
    cache.delete(file);
    cachedTriangles -= entry.triangles;
  }
}

/** Forget every cached component. */
export function clearComponentCache(): void {
  lastText = null;
  cache.clear();
  cachedTriangles = 0;
}

/** The text of the file loaded last, so showing another of its types does not fetch it again. */
let lastText: { file: string; text: string } | null = null;

async function fetchText(file: string, signal?: AbortSignal): Promise<string> {
  if (lastText?.file === file) return lastText.text;
  try {
    const response = await fetch(libraryUrl(file), signal ? { signal } : undefined);
    if (!response.ok) {
      throw new ComponentNetworkError(file, response.status, `HTTP ${response.status} fetching ${file}`);
    }
    const text = await response.text();
    lastText = { file, text };
    return text;
  } catch (error) {
    if (error instanceof ComponentLoadError) throw error;
    if (signal?.aborted) throw error;
    throw new ComponentNetworkError(file, 0, `Could not fetch ${file}: ${String(error)}`, { cause: error });
  }
}

async function fetchAndParse(file: string, type: number, signal?: AbortSignal): Promise<Component> {
  const text = await fetchText(file, signal);

  try {
    await initEngine();
  } catch (error) {
    throw new EngineInitError(file, `The geometry engine failed to start: ${String(error)}`, { cause: error });
  }

  let component: Component;
  try {
    component = load_component(text, type);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new ComponentParseError(file, `Could not read ${file}: ${message}`, { cause: error });
  }
  return withScripted(file, component, libraryUrl);
}

/**
 * Load a component by its catalog path (`components/<folder>/<name>.ccomp`),
 * resolved with the values of its type at index `type` (default 0, the first).
 * Results are cached; concurrent calls for the same file and type share one request.
 * Rejects with `ComponentNetworkError`, `ComponentParseError` or `EngineInitError`.
 * Aborting `signal` rejects this call only if it started the request.
 *
 * Treat the returned object as read-only: it is shared with other callers.
 */
export function loadComponent(file: string, options?: { signal?: AbortSignal; type?: number }): Promise<Component> {
  const type = options?.type ?? 0;
  // The first type keeps the plain path as its key.
  const key = type === 0 ? file : `${file}#${type}`;
  const hit = cache.get(key);
  if (hit) {
    touch(key, hit);
    return hit.promise;
  }

  const entry: CacheEntry = { promise: fetchAndParse(file, type, options?.signal), triangles: 0 };
  cache.set(key, entry);
  entry.promise.then(
    (component) => {
      if (cache.get(key) !== entry) return;
      entry.triangles = triangleCount(component);
      cachedTriangles += entry.triangles;
      evict(key);
    },
    () => {
      // Failed loads are not cached, so a later call retries.
      if (cache.get(key) === entry) cache.delete(key);
    },
  );
  return entry.promise;
}
