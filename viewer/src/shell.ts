// The page frame shared by every route: the rail (brand, folder nav, footer
// links) and the <main> element pages mount into. On narrow screens the rail
// becomes a sticky top bar and the footer links move to the page bottom.

import { FOLDERS, folderRoute, loadCatalog, type FolderId } from './catalog';

export const REPO_URL = 'https://github.com/francisreboucas/constructcraft-components';
export const LICENSE_URL = `${REPO_URL}/blob/main/LICENSE`;

/** Which rail item is current: all components, one folder, or none. */
export type ActiveNav = 'all' | FolderId | null;

/** Page layout, exposed as `data-layout` on the app root. */
export type Layout = 'gallery' | 'detail' | 'plain';

export interface Shell {
  main: HTMLElement;
  setActive(active: ActiveNav): void;
  setLayout(layout: Layout): void;
}

function el<K extends keyof HTMLElementTagNameMap>(tag: K, className?: string, text?: string): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function footerLinks(className: string): HTMLElement {
  const box = el('div', className);
  const license = el('a', undefined, 'Componentes sob CC BY 4.0');
  license.href = LICENSE_URL;
  const repo = el('a', undefined, 'GitHub');
  repo.href = REPO_URL;
  box.append(license, repo);
  return box;
}

export function createShell(root: HTMLElement): Shell {
  const app = el('div', 'app');

  const skip = el('a', 'skip-link', 'Ir para o conteúdo');
  skip.href = '#main';
  skip.addEventListener('click', (event) => {
    // The hash is the router's; move focus without changing it.
    event.preventDefault();
    main.focus();
  });

  const rail = el('header', 'rail');
  const brand = el('a', 'brand');
  brand.href = '#/';
  brand.append(el('span', 'brand-name display', 'ConstructCraft'), el('span', 'brand-sub', 'Componentes'));

  const nav = el('nav', 'rail-nav');
  nav.setAttribute('aria-label', 'Pastas');
  const list = el('ul');
  const items = new Map<ActiveNav, { link: HTMLAnchorElement; count: HTMLElement }>();
  const addItem = (key: ActiveNav, label: string, href: string) => {
    const li = el('li');
    const link = el('a', 'nav-item');
    link.href = href;
    const count = el('span', 'nav-count');
    link.append(el('span', 'nav-label', label), count);
    li.append(link);
    list.append(li);
    items.set(key, { link, count });
  };
  addItem('all', 'Todos', '#/');
  for (const folder of FOLDERS) addItem(folder.id, folder.label, folderRoute(folder.id));
  nav.append(list);

  rail.append(brand, nav, footerLinks('rail-foot'));

  const main = el('main', 'main');
  main.id = 'main';
  main.tabIndex = -1;

  const pageFoot = el('footer', 'page-foot');
  pageFoot.append(footerLinks('page-foot-links'));

  app.append(skip, rail, main, pageFoot);
  root.append(app);

  // The sticky top bar's height, for elements that stick below it on narrow screens.
  new ResizeObserver(() => {
    app.style.setProperty('--bar-h', `${rail.offsetHeight}px`);
  }).observe(rail);

  loadCatalog().then(
    (catalog) => {
      const counts = new Map<ActiveNav, number>([['all', catalog.entries.length]]);
      for (const entry of catalog.entries) counts.set(entry.folder, (counts.get(entry.folder) ?? 0) + 1);
      for (const [key, item] of items) item.count.textContent = String(counts.get(key) ?? 0);
    },
    () => {
      // The page reports the catalog error; the rail just stays without counts.
    },
  );

  let active: ActiveNav = null;
  return {
    main,
    setActive(next) {
      active = next;
      for (const [key, item] of items) {
        if (key === active) item.link.setAttribute('aria-current', 'page');
        else item.link.removeAttribute('aria-current');
      }
      const current = active ? items.get(active)?.link : undefined;
      if (current && list.scrollWidth > list.clientWidth) {
        // Narrow screens: bring the active tab into the horizontally scrolling row.
        const left = current.offsetLeft - (list.clientWidth - current.offsetWidth) / 2;
        list.scrollLeft = Math.max(0, left);
      }
    },
    setLayout(layout) {
      app.dataset.layout = layout;
    },
  };
}
