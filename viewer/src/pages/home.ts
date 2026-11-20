// The home page, `#/`: the hero with a live component drawn by the engine,
// the categories, what makes a component fit for the library, how to use one
// and the site footer.

import {
  ALL_ROUTE,
  FOLDERS,
  edgesForFolder,
  entryRoute,
  folderRoute,
  loadCatalog,
  type Catalog,
  type CatalogEntry,
  type FolderId,
} from '../catalog';
import { loadComponent } from '../engine';
import { formatDecimal } from '../format';
import { LOCALE, t } from '../i18n';
import { Viewport } from '../scene';
import { prefersReducedMotion } from '../scene/views';
import {
  CATALOG_URL,
  CONSTRUCTCRAFT_URL,
  CONTRIBUTING_URL,
  DOWNLOAD_URL,
  LICENSE_URL,
  REPO_URL,
  VIEWER_LICENSE_URL,
} from '../shell';
import { ThumbnailLoader } from '../thumbnails';
import { describeError, errorElement } from './errors';
import { el, setPageState, setTitle, type Page } from './page';

/** The component drawn in the hero: the first of these in the catalog, else the first with several types. */
const HERO_IDS = ['furniture/sofa', 'casework/guarda-roupa', 'furniture/cama'];
/** Time each type stays on screen while the hero cycles on its own, ms. */
const CYCLE_MS = 3600;

/** The component that stands for each category on its tile. */
const COVERS: Record<FolderId, string> = {
  furniture: 'cama',
  casework: 'guarda-roupa',
  plumbing: 'lavatorio-bancada',
  electrical: 'quadro-distribuicao',
  lighting: 'pendente',
  planting: 'ipe-amarelo',
  doors: 'porta-abrir',
  windows: 'janela-veneziana',
  vehicles: 'moto-custom',
  site: 'vaga-pcd',
  signage: 'placa-pare',
  fire: 'abrigo-hidrante',
};

function link(className: string, text: string, href: string): HTMLAnchorElement {
  const a = el('a', className, text);
  a.href = href;
  return a;
}

function sectionHead(id: string, title: string, note?: string): HTMLElement {
  const head = el('div', 'home-head');
  const h2 = el('h2', 'home-title display', title);
  h2.id = id;
  head.append(h2);
  if (note) head.append(el('p', 'home-note', note));
  return head;
}

function heroEntry(catalog: Catalog): CatalogEntry | null {
  for (const id of HERO_IDS) {
    const entry = catalog.byId.get(id);
    if (entry) return entry;
  }
  return catalog.entries.find((e) => e.types.length > 1) ?? catalog.entries[0] ?? null;
}

/** "2,10 × 0,90 × 0,85 m" from the bounding box of what is drawn. */
function sizeText(bounds: { min: [number, number, number]; max: [number, number, number] }): string {
  const size = [0, 1, 2].map((i) => formatDecimal((bounds.max[i] ?? 0) - (bounds.min[i] ?? 0), 2, 2));
  return `${size.join(' × ')} m`;
}

interface Hero {
  element: HTMLElement;
  /** Draw the entry; resolves once the first type is on screen (or could not be drawn). */
  show(entry: CatalogEntry): Promise<void>;
  setCounts(catalog: Catalog): void;
  dispose(): void;
}

function buildHero(): Hero {
  let alive = true;
  let viewport: Viewport | null = null;
  let timer = 0;
  let request = 0;

  const hero = el('section', 'hero');
  hero.setAttribute('aria-labelledby', 'hero-title');

  const copy = el('div', 'hero-copy');
  const h1 = el('h1', 'hero-title display', t.home.title);
  h1.id = 'hero-title';
  const lead = el('p', 'hero-lead');
  const counts = el('span', 'hero-counts', t.home.kinds);
  lead.append(counts, t.home.lead);
  const actions = el('div', 'hero-actions');
  actions.append(
    link('button-primary', t.home.browse, ALL_ROUTE),
    link('button', t.home.downloadZip, DOWNLOAD_URL),
  );
  copy.append(el('p', 'eyebrow', t.home.eyebrow), h1, lead, actions);

  // The sheet: the live drawing and, below it, its title block.
  const sheet = el('div', 'sheet');
  const view = el('div', 'hero-view');
  view.setAttribute('role', 'img');
  const status = el('p', 'sheet-status', t.common.loadingGeometry);
  view.append(status);

  const block = el('dl', 'sheet-block');
  const cell = (term: string, className: string): HTMLElement => {
    const box = el('div', `sheet-cell ${className}`);
    const dd = el('dd');
    box.append(el('dt', undefined, term), dd);
    block.append(box);
    return dd;
  };
  const nameCell = cell(t.home.sheet.component, 'sheet-name');
  const sizeCell = cell(t.home.sheet.size, 'sheet-size');
  const authorCell = cell(t.common.author, 'sheet-author');
  const typesCell = cell(t.home.sheet.type, 'sheet-types');
  sheet.append(view, block);
  hero.append(copy, sheet);

  let buttons: HTMLButtonElement[] = [];
  let shown = 0;

  const stop = () => {
    clearInterval(timer);
    timer = 0;
  };

  async function showType(entry: CatalogEntry, index: number): Promise<void> {
    const mine = ++request;
    const component = await loadComponent(entry.file, { type: index });
    if (!alive || mine !== request) return;
    if (!component.bounds) throw new Error('no geometry');
    viewport ??= new Viewport(view);
    viewport.setComponent(component, { edges: edgesForFolder(entry.folder), view: 'iso', dimensions: true });
    shown = component.type_index;
    buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === shown)));
    sizeCell.textContent = sizeText(component.bounds);
    view.setAttribute('aria-label', t.home.modelLabel(entry.types[shown]?.name ?? entry.title));
  }

  return {
    element: hero,
    setCounts(catalog) {
      const types = catalog.entries.reduce((n, e) => n + e.types.length, 0);
      counts.textContent = t.home.counts(catalog.entries.length, types);
    },
    async show(entry) {
      const open = link('sheet-link', entry.title, entryRoute(entry));
      nameCell.replaceChildren(open);
      authorCell.textContent = entry.author || '—';
      const group = el('div', 'chips');
      group.setAttribute('role', 'group');
      group.setAttribute('aria-label', t.home.typeGroup);
      buttons = entry.types.map((type, index) => {
        const button = el('button', 'chip', type.name);
        button.type = 'button';
        button.setAttribute('aria-pressed', String(index === 0));
        button.addEventListener('click', () => {
          // A pick by hand ends the automatic cycle.
          stop();
          void showType(entry, index).catch(() => undefined);
        });
        group.append(button);
        return button;
      });
      typesCell.replaceChildren(group);
      try {
        await showType(entry, 0);
        if (!alive) return;
        status.hidden = true;
        if (entry.types.length > 1 && !prefersReducedMotion()) {
          timer = window.setInterval(() => {
            // Not while the tab is hidden or the drawing is scrolled away.
            const rect = view.getBoundingClientRect();
            if (document.hidden || rect.bottom < 0 || rect.top > window.innerHeight) return;
            void showType(entry, (shown + 1) % entry.types.length).catch(stop);
          }, CYCLE_MS);
        }
      } catch (error) {
        if (!alive) return;
        status.textContent = describeError(error, entry.file);
        sizeCell.textContent = '—';
      }
    },
    dispose() {
      alive = false;
      stop();
      viewport?.dispose();
      viewport = null;
    },
  };
}

function categoriesSection(catalog: Catalog, loader: ThumbnailLoader): HTMLElement {
  const section = el('section', 'home-section');
  section.setAttribute('aria-labelledby', 'home-categories');
  section.append(sectionHead('home-categories', t.home.categories));
  const grid = el('div', 'category-grid');
  for (const folder of FOLDERS) {
    const entries = catalog.entries.filter((e) => e.folder === folder.id);
    const first = entries[0];
    if (!first) continue;
    const cover = catalog.byId.get(`${folder.id}/${COVERS[folder.id]}`) ?? first;
    // `.card` so the thumbnail loader and its states apply.
    const tile = link('card category', '', folderRoute(folder.id));
    const text = el('span', 'category-text');
    const name = el('span', 'category-name display', folder.label);
    const count = el('span', 'category-count', t.common.componentCount(entries.length));
    text.append(name, count, el('span', 'category-desc', t.home.categoryText[folder.id]));
    tile.append(el('span', 'card-thumb'), text);
    loader.observe(tile, cover);
    grid.append(tile);
  }
  section.append(grid);
  return section;
}

function qualitySection(catalog: Catalog): HTMLElement {
  const types = catalog.entries.reduce((n, e) => n + e.types.length, 0);
  const withMep = catalog.entries.filter((e) => e.mep).length;
  const q = t.home.qualityItems;
  const items: { title: string; text: string; data: string }[] = [
    { ...q.parametric, data: q.parametric.data(types, catalog.entries.length) },
    q.detail,
    { ...q.mep, data: q.mep.data(withMep) },
    q.checked,
  ];
  const section = el('section', 'home-section');
  section.setAttribute('aria-labelledby', 'home-quality');
  section.append(
    sectionHead('home-quality', t.home.quality, t.home.qualityNote),
  );
  const list = el('ul', 'quality');
  for (const item of items) {
    const li = el('li', 'quality-item');
    li.append(el('h3', 'quality-title', item.title), el('p', 'quality-text', item.text), el('p', 'quality-data', item.data));
    list.append(li);
  }
  section.append(list);
  return section;
}

function usageSection(entry: CatalogEntry | null): HTMLElement {
  const section = el('section', 'home-section');
  section.setAttribute('aria-labelledby', 'home-usage');
  section.append(sectionHead('home-usage', t.home.usage));
  const list = el('ol', 'steps');

  const download = el('li', 'step');
  const steps = t.home.steps;
  const downloadText = el('p', 'step-text', steps.download.before);
  downloadText.append(link('text-link', steps.download.link, DOWNLOAD_URL), steps.download.after);
  download.append(el('h3', 'step-title', steps.download.title), downloadText);

  const load = el('li', 'step');
  load.append(
    el('h3', 'step-title', steps.load.title),
    el('p', 'step-text', steps.load.text),
    el('code', 'step-code', `ccad -p casa.ccad --save run component_load path=${entry?.file ?? 'components/furniture/sofa.ccomp'}`),
  );

  const place = el('li', 'step');
  place.append(
    el('h3', 'step-title', steps.place.title),
    el('p', 'step-text', steps.place.text),
  );

  list.append(download, load, place);
  section.append(list);
  return section;
}

function footer(catalog: Catalog | null): HTMLElement {
  const foot = el('footer', 'home-foot');

  const about = el('div', 'foot-about');
  const authors = catalog ? [...new Set(catalog.entries.map((e) => e.author).filter(Boolean))] : [];
  const f = t.home.foot;
  const by = authors.length ? f.by(new Intl.ListFormat(LOCALE).format(authors)) : '';
  about.append(
    el('p', 'foot-brand display', '3D CraftHouse'),
    el('p', 'foot-text', `${f.about} ${by}`.trim()),
  );

  const column = (title: string, links: [string, string][]): HTMLElement => {
    const nav = el('nav', 'foot-col');
    nav.setAttribute('aria-label', title);
    const list = el('ul');
    for (const [text, href] of links) {
      const li = el('li');
      li.append(link('', text, href));
      list.append(li);
    }
    nav.append(el('p', 'foot-head', title), list);
    return nav;
  };

  foot.append(
    about,
    column(f.library, [
      [f.allComponents, ALL_ROUTE],
      [f.catalogTable, CATALOG_URL],
      [f.zip, DOWNLOAD_URL],
    ]),
    column(f.project, [
      ['ConstructCraft', CONSTRUCTCRAFT_URL],
      [f.code, REPO_URL],
      [f.contribute, CONTRIBUTING_URL],
    ]),
    column(f.licenses, [
      [f.componentsLicense, LICENSE_URL],
      [f.viewerLicense, VIEWER_LICENSE_URL],
    ]),
  );
  return foot;
}

export const homePage: Page = (shell) => {
  let alive = true;
  shell.setLayout('home');
  shell.setActive(null);
  setTitle();
  setPageState('loading');

  const page = el('div', 'home');
  const hero = buildHero();
  const body = el('div', 'home-body');
  page.append(hero.element, body);
  shell.main.append(page);

  const loader = new ThumbnailLoader();

  loadCatalog().then(
    (catalog) => {
      if (!alive) return;
      const entry = heroEntry(catalog);
      hero.setCounts(catalog);
      body.append(categoriesSection(catalog, loader), qualitySection(catalog), usageSection(entry));
      page.append(footer(catalog));
      const drawn = entry ? hero.show(entry) : Promise.resolve();
      void drawn.then(() => {
        if (alive) setPageState('ready');
      });
    },
    (error: unknown) => {
      if (!alive) return;
      body.append(errorElement(describeError(error, 'catalog.json')));
      page.append(footer(null));
      setPageState('error');
    },
  );

  return () => {
    alive = false;
    hero.dispose();
    loader.dispose();
  };
};
