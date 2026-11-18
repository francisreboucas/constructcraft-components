// Test hooks for `npm run smoke`, loaded only when the page URL has `?smoke`.
// Not part of the app; kept in its own chunk.

import { edgesForFolder, loadCatalog } from './catalog';
import { loadComponent } from './engine';
import { renderThumbnail, thumbnailRendererInfo } from './scene';

export interface ThumbnailStressResult {
  rendered: number;
  failures: string[];
  /** GPU geometries held by the shared renderer after each render. */
  geometries: number[];
  textures: number[];
}

/** Render a thumbnail of every catalog entry and report renderer memory after each. */
async function thumbnailStress(sizePx = 128): Promise<ThumbnailStressResult> {
  const catalog = await loadCatalog();
  const result: ThumbnailStressResult = { rendered: 0, failures: [], geometries: [], textures: [] };
  for (const entry of catalog.entries) {
    try {
      const component = await loadComponent(entry.file);
      const blob = await renderThumbnail(component, sizePx, { edges: edgesForFolder(entry.folder) });
      if (blob.size === 0) throw new Error('empty image');
      result.rendered++;
    } catch (error) {
      result.failures.push(`${entry.file}: ${String(error)}`);
    }
    const info = thumbnailRendererInfo();
    result.geometries.push(info?.geometries ?? -1);
    result.textures.push(info?.textures ?? -1);
  }
  return result;
}

declare global {
  interface Window {
    __smoke?: { thumbnailStress: typeof thumbnailStress };
  }
}

window.__smoke = { thumbnailStress };
