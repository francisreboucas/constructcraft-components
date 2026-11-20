// The library catalog (`library/catalog.json`), its folders and the routes
// that address its entries.
//
// An entry's id is `<folder>/<name>`, taken from its file path
// `components/<folder>/<name>.ccomp`; its route is `#/<folder>/<name>`.
// `#/` is the home page and `#/componentes` the gallery of every folder.

import { libraryUrl } from './engine';
import { lang, t } from './i18n';
import { COMPONENT_NAMES_EN } from './i18n/components-en';

export type FolderId =
  | 'furniture'
  | 'casework'
  | 'plumbing'
  | 'electrical'
  | 'lighting'
  | 'planting'
  | 'doors'
  | 'windows'
  | 'vehicles'
  | 'site'
  | 'signage';

export interface FolderInfo {
  id: FolderId;
  /** Display label in the page's language. */
  label: string;
}

/** Folders in display order. */
const FOLDER_ORDER: readonly FolderId[] = [
  'furniture',
  'casework',
  'plumbing',
  'electrical',
  'lighting',
  'planting',
  'doors',
  'windows',
  'vehicles',
  'site',
  'signage',
];

export const FOLDERS: readonly FolderInfo[] = FOLDER_ORDER.map((id) => ({ id, label: t.folders[id] }));

const FOLDER_IDS = new Set<string>(FOLDERS.map((f) => f.id));

export function isFolderId(value: string): value is FolderId {
  return FOLDER_IDS.has(value);
}

export function folderLabel(id: FolderId): string {
  return FOLDERS.find((f) => f.id === id)?.label ?? id;
}

/**
 * Whether the scene should draw feature edges for components of this folder.
 * Off for `planting`: foliage meshes turn into noise. This is the contract
 * callers of `buildComponentObject`, `Viewport.setComponent` and
 * `renderThumbnail` follow when passing `edges`.
 */
export function edgesForFolder(id: FolderId): boolean {
  return id !== 'planting';
}

export interface CatalogType {
  name: string;
  /** Numbers for lengths, angles and numbers; texts for texts, choices and materials; booleans for yes/no. */
  values: Record<string, number | string | boolean>;
  description: string;
}

/** One catalog entry as in catalog.json, plus its derived id. */
export interface CatalogEntry {
  /** `<folder>/<name>`, e.g. `plumbing/pia-cozinha`. */
  id: string;
  folder: FolderId;
  /** The file name without extension, e.g. `pia-cozinha`. */
  slug: string;
  /** Path relative to the library root, e.g. `components/plumbing/pia-cozinha.ccomp`. */
  file: string;
  /** Name of the component as written in its file (pt-BR). */
  component: string;
  /** Display name in the page's language: `component`, or its English name. */
  title: string;
  /** Who made the component; empty when the catalog does not say. */
  author: string;
  /** Engine kind: "Furniture", "Plumbing", "Door"... */
  kind: string;
  mep: Record<string, unknown> | null;
  parameters: string[];
  types: CatalogType[];
}

export interface Catalog {
  formatVersion: number;
  /** In catalog.json order. */
  entries: readonly CatalogEntry[];
  byId: ReadonlyMap<string, CatalogEntry>;
}

export class CatalogError extends Error {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = 'CatalogError';
  }
}

const FILE_PATTERN = /^components\/([a-z0-9-]+)\/([a-z0-9-]+)\.ccomp$/;

interface RawEntry {
  file: string;
  component: string;
  author?: string;
  kind: string;
  mep: Record<string, unknown> | null;
  parameters?: string[];
  types?: CatalogType[];
}

function parseCatalog(raw: unknown): Catalog {
  if (typeof raw !== 'object' || raw === null || !Array.isArray((raw as { components?: unknown }).components)) {
    throw new CatalogError('catalog.json has no "components" list');
  }
  const data = raw as { format_version?: number; components: RawEntry[] };
  const entries: CatalogEntry[] = [];
  const byId = new Map<string, CatalogEntry>();
  for (const item of data.components) {
    const match = FILE_PATTERN.exec(item.file ?? '');
    if (!match) throw new CatalogError(`catalog.json lists an unexpected file: ${String(item.file)}`);
    const [, folder, slug] = match as unknown as [string, string, string];
    if (!isFolderId(folder)) throw new CatalogError(`catalog.json lists an unknown folder: ${folder}`);
    const entry: CatalogEntry = {
      id: `${folder}/${slug}`,
      folder,
      slug,
      file: item.file,
      component: item.component,
      title: (lang === 'en' && COMPONENT_NAMES_EN[`${folder}/${slug}`]) || item.component,
      author: item.author ?? '',
      kind: item.kind,
      mep: item.mep ?? null,
      parameters: item.parameters ?? [],
      types: item.types ?? [],
    };
    entries.push(entry);
    byId.set(entry.id, entry);
  }
  return { formatVersion: data.format_version ?? 1, entries, byId };
}

let catalogPromise: Promise<Catalog> | null = null;

/** Fetch and parse the catalog once. Rejects with `CatalogError`; a failure is retried on the next call. */
export function loadCatalog(): Promise<Catalog> {
  if (!catalogPromise) {
    catalogPromise = (async () => {
      let response: Response;
      try {
        response = await fetch(libraryUrl('catalog.json'));
      } catch (error) {
        throw new CatalogError(`Could not fetch catalog.json: ${String(error)}`, { cause: error });
      }
      if (!response.ok) throw new CatalogError(`HTTP ${response.status} fetching catalog.json`);
      let raw: unknown;
      try {
        raw = await response.json();
      } catch (error) {
        throw new CatalogError(`catalog.json is not valid JSON: ${String(error)}`, { cause: error });
      }
      return parseCatalog(raw);
    })();
    catalogPromise.catch(() => {
      catalogPromise = null;
    });
  }
  return catalogPromise;
}

export interface FolderSummary extends FolderInfo {
  count: number;
}

/** Folders in display order with their entry counts; empty folders are left out. */
export function folderSummaries(catalog: Catalog): FolderSummary[] {
  const counts = new Map<FolderId, number>();
  for (const entry of catalog.entries) counts.set(entry.folder, (counts.get(entry.folder) ?? 0) + 1);
  return FOLDERS.filter((f) => counts.has(f.id)).map((f) => ({ ...f, count: counts.get(f.id) ?? 0 }));
}

/** The entries of one folder, in catalog order. */
export function entriesInFolder(catalog: Catalog, folder: FolderId): CatalogEntry[] {
  return catalog.entries.filter((e) => e.folder === folder);
}

// ---------------------------------------------------------------------------
// Routes (hash routing only)

export type Route =
  | { name: 'home' }
  | { name: 'all' }
  | { name: 'folder'; folder: FolderId }
  | { name: 'component'; folder: FolderId; slug: string; id: string }
  | { name: 'not-found'; hash: string };

/** `#/plumbing/pia-cozinha` for an entry or an id. */
export function entryRoute(entry: CatalogEntry | string): string {
  return `#/${typeof entry === 'string' ? entry : entry.id}`;
}

/** The gallery of every folder. */
export const ALL_ROUTE = '#/componentes';

/** `#/plumbing` */
export function folderRoute(folder: FolderId): string {
  return `#/${folder}`;
}

/** Parse `location.hash`. Only checks the shape; look ids up with `catalog.byId`. */
export function parseRoute(hash: string): Route {
  const path = hash.replace(/^#\/?/, '').replace(/\/+$/, '');
  if (path === '') return { name: 'home' };
  if (path === 'componentes') return { name: 'all' };
  const segments = path.split('/').map((s) => {
    try {
      return decodeURIComponent(s);
    } catch {
      return s;
    }
  });
  const [folder, slug] = segments;
  if (folder === undefined || !isFolderId(folder) || segments.length > 2) return { name: 'not-found', hash };
  if (slug === undefined) return { name: 'folder', folder };
  if (!/^[a-z0-9-]+$/.test(slug)) return { name: 'not-found', hash };
  return { name: 'component', folder, slug, id: `${folder}/${slug}` };
}
