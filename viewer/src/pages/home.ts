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

/** What each category holds, and the component that stands for it on its tile. */
const CATEGORIES: Record<FolderId, { text: string; cover: string }> = {
  furniture: { text: 'Camas, sofás, mesas, cadeiras e eletrodomésticos.', cover: 'cama' },
  casework: { text: 'Guarda-roupas, cômodas, balcões, aéreos e estantes.', cover: 'guarda-roupa' },
  plumbing: { text: 'Louças, tanques e caixas, com os pontos de água e esgoto.', cover: 'lavatorio-bancada' },
  electrical: { text: 'Tomadas, interruptores e quadros, com a potência de cada ponto.', cover: 'quadro-distribuicao' },
  lighting: { text: 'Plafons, pendentes, spots, arandelas e ventiladores de teto.', cover: 'pendente' },
  planting: { text: 'Árvores, palmeiras, arbustos e vasos no porte adulto.', cover: 'ipe-amarelo' },
  doors: { text: 'De abrir, de correr, pivotante, camarão e portão basculante.', cover: 'porta-abrir' },
  windows: { text: 'De correr, de abrir, basculante, maxim-ar, veneziana e fixa.', cover: 'janela-veneziana' },
  vehicles: { text: 'Para compor garagens e fachadas.', cover: 'moto-custom' },
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
  const h1 = el('h1', 'hero-title display', 'Componentes 3D de alta qualidade para o ConstructCraft');
  h1.id = 'hero-title';
  const lead = el('p', 'hero-lead');
  const counts = el('span', 'hero-counts', 'Móveis, louças, portas, janelas, pontos elétricos e plantas.');
  lead.append(
    counts,
    ' Cada componente é paramétrico, tem três níveis de detalhe e leva os dados que o ConstructCraft usa para dimensionar as instalações.',
  );
  const actions = el('div', 'hero-actions');
  actions.append(
    link('button-primary', 'Ver os componentes', ALL_ROUTE),
    link('button', 'Baixar a biblioteca (ZIP)', DOWNLOAD_URL),
  );
  copy.append(
    el('p', 'eyebrow', 'Biblioteca aberta · CC BY 4.0'),
    h1,
    lead,
    actions,
  );

  // The sheet: the live drawing and, below it, its title block.
  const sheet = el('div', 'sheet');
  const view = el('div', 'hero-view');
  view.setAttribute('role', 'img');
  const status = el('p', 'sheet-status', 'Carregando geometria…');
  view.append(status);

  const block = el('dl', 'sheet-block');
  const cell = (term: string, className: string): HTMLElement => {
    const box = el('div', `sheet-cell ${className}`);
    const dd = el('dd');
    box.append(el('dt', undefined, term), dd);
    block.append(box);
    return dd;
  };
  const nameCell = cell('Componente', 'sheet-name');
  const sizeCell = cell('Medidas', 'sheet-size');
  const authorCell = cell('Autor', 'sheet-author');
  const typesCell = cell('Tipo', 'sheet-types');
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
    view.setAttribute('aria-label', `Modelo 3D: ${entry.types[shown]?.name ?? entry.component}`);
  }

  return {
    element: hero,
    setCounts(catalog) {
      const types = catalog.entries.reduce((n, e) => n + e.types.length, 0);
      counts.textContent = `${catalog.entries.length} componentes e ${types} tipos: móveis, louças, portas, janelas, pontos elétricos e plantas.`;
    },
    async show(entry) {
      const open = link('sheet-link', entry.component, entryRoute(entry));
      nameCell.replaceChildren(open);
      authorCell.textContent = entry.author || '—';
      const group = el('div', 'chips');
      group.setAttribute('role', 'group');
      group.setAttribute('aria-label', 'Tipo mostrado no modelo 3D');
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
  section.append(sectionHead('home-categories', 'Categorias'));
  const grid = el('div', 'category-grid');
  for (const folder of FOLDERS) {
    const entries = catalog.entries.filter((e) => e.folder === folder.id);
    const first = entries[0];
    if (!first) continue;
    const info = CATEGORIES[folder.id];
    const cover = catalog.byId.get(`${folder.id}/${info.cover}`) ?? first;
    // `.card` so the thumbnail loader and its states apply.
    const tile = link('card category', '', folderRoute(folder.id));
    const text = el('span', 'category-text');
    const name = el('span', 'category-name display', folder.label);
    const count = el('span', 'category-count', entries.length === 1 ? '1 componente' : `${entries.length} componentes`);
    text.append(name, count, el('span', 'category-desc', info.text));
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
  const items: { title: string; text: string; data: string }[] = [
    {
      title: 'Paramétrico',
      text: 'Um arquivo traz o componente e todos os seus tamanhos. Os tipos compartilham a geometria e mudam só os parâmetros, que você ainda ajusta no projeto.',
      data: `${types} tipos em ${catalog.entries.length} componentes`,
    },
    {
      title: 'Três níveis de detalhe',
      text: 'Cada peça diz em que nível aparece, baixo, médio ou alto, e se entra na planta. O modelo fica leve de longe e completo de perto.',
      data: 'baixo · médio · alto',
    },
    {
      title: 'Dados de instalações',
      text: 'As louças trazem as unidades Hunter e os pesos relativos; os pontos elétricos, o tipo e a potência em VA. O ConstructCraft dimensiona tubulações e circuitos com eles.',
      data: `${withMep} componentes · NBR 8160, 5626 e 5410`,
    },
    {
      title: 'Conferido pelo próprio app',
      text: 'A cada alteração, o ConstructCraft abre todos os arquivos num projeto novo. O que ele não carrega não entra na biblioteca.',
      data: 'verificação automática',
    },
  ];
  const section = el('section', 'home-section');
  section.setAttribute('aria-labelledby', 'home-quality');
  section.append(
    sectionHead(
      'home-quality',
      'O que todo componente traz',
      'O que um componente precisa ter para entrar na biblioteca.',
    ),
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
  section.append(sectionHead('home-usage', 'Do arquivo ao projeto'));
  const list = el('ol', 'steps');

  const download = el('li', 'step');
  const downloadText = el('p', 'step-text', 'Abra um componente e baixe o arquivo .ccomp, ou leve a biblioteca inteira no ');
  downloadText.append(link('text-link', 'ZIP da última versão', DOWNLOAD_URL), '.');
  download.append(el('h3', 'step-title', 'Baixe'), downloadText);

  const load = el('li', 'step');
  load.append(
    el('h3', 'step-title', 'Carregue no ConstructCraft'),
    el('p', 'step-text', 'O componente e todos os seus tipos entram no projeto, com os materiais que faltarem. Pela linha de comando:'),
    el('code', 'step-code', `ccad -p casa.ccad --save run component_load path=${entry?.file ?? 'components/furniture/sofa.ccomp'}`),
  );

  const place = el('li', 'step');
  place.append(
    el('h3', 'step-title', 'Insira'),
    el('p', 'step-text', 'Use a ferramenta de componente e escolha o tipo. Os parâmetros continuam editáveis depois de inserir.'),
  );

  list.append(download, load, place);
  section.append(list);
  return section;
}

function footer(catalog: Catalog | null): HTMLElement {
  const foot = el('footer', 'home-foot');

  const about = el('div', 'foot-about');
  const authors = catalog ? [...new Set(catalog.entries.map((e) => e.author).filter(Boolean))] : [];
  const by = authors.length ? `Componentes por ${new Intl.ListFormat('pt-BR').format(authors)}.` : '';
  about.append(
    el('p', 'foot-brand display', '3D CraftHouse'),
    el('p', 'foot-text', `Biblioteca aberta de componentes para o ConstructCraft. ${by}`.trim()),
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
    column('Biblioteca', [
      ['Todos os componentes', ALL_ROUTE],
      ['Catálogo em tabela', CATALOG_URL],
      ['Baixar em ZIP', DOWNLOAD_URL],
    ]),
    column('Projeto', [
      ['ConstructCraft', CONSTRUCTCRAFT_URL],
      ['Código no GitHub', REPO_URL],
      ['Como contribuir', CONTRIBUTING_URL],
    ]),
    column('Licenças', [
      ['Componentes: CC BY 4.0', LICENSE_URL],
      ['Visualizador: GPL-3.0-or-later', VIEWER_LICENSE_URL],
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
