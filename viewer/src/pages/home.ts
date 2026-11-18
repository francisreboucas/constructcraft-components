// Placeholder home page: every catalog entry as a plain link, grouped by
// folder, plus a strip of the first 12 thumbnails. Replaced by the gallery.

import { edgesForFolder, entriesInFolder, entryRoute, folderSummaries, loadCatalog } from '../catalog';
import { loadComponent } from '../engine';
import { renderThumbnail } from '../scene';
import { describeError, errorElement } from './errors';
import { setPageState, type Page } from './page';

const THUMB_COUNT = 12;
const THUMB_PX = 256;

export const homePage: Page = (root) => {
  let alive = true;
  const urls: string[] = [];
  const main = document.createElement('main');
  main.className = 'page';
  const title = document.createElement('h1');
  title.className = 'display';
  title.textContent = 'Componentes ConstructCraft';
  main.append(title);
  root.append(main);

  (async () => {
    let catalog;
    try {
      catalog = await loadCatalog();
    } catch (error) {
      main.append(errorElement(describeError(error, 'catalog.json')));
      setPageState('error');
      return;
    }
    if (!alive) return;

    const strip = document.createElement('div');
    strip.className = 'thumb-strip';
    strip.setAttribute('aria-label', 'Miniaturas');
    main.append(strip);

    for (const folder of folderSummaries(catalog)) {
      const h2 = document.createElement('h2');
      h2.className = 'display';
      h2.textContent = `${folder.label} (${folder.count})`;
      const list = document.createElement('ul');
      for (const entry of entriesInFolder(catalog, folder.id)) {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = entryRoute(entry);
        a.textContent = entry.component;
        li.append(a);
        list.append(li);
      }
      main.append(h2, list);
    }

    let failed = false;
    for (const entry of catalog.entries.slice(0, THUMB_COUNT)) {
      const link = document.createElement('a');
      link.href = entryRoute(entry);
      link.title = entry.component;
      strip.append(link);
      try {
        const component = await loadComponent(entry.file);
        const blob = await renderThumbnail(component, THUMB_PX, { edges: edgesForFolder(entry.folder) });
        if (!alive) return;
        const url = URL.createObjectURL(blob);
        urls.push(url);
        const img = document.createElement('img');
        img.alt = entry.component;
        img.src = url;
        await img.decode().catch(() => undefined);
        link.append(img);
      } catch (error) {
        if (!alive) return;
        failed = true;
        link.replaceWith(errorElement(describeError(error, entry.file)));
      }
    }
    if (alive) setPageState(failed ? 'error' : 'ready');
  })();

  return () => {
    alive = false;
    for (const url of urls) URL.revokeObjectURL(url);
  };
};
