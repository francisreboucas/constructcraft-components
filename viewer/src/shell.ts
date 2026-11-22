// The page frame shared by every route: the rail (brand, folder nav, footer
// links) and the <main> element pages mount into. On narrow screens the rail
// becomes a sticky top bar and the footer links move to the page bottom.

import { ALL_ROUTE, FOLDERS, folderRoute, loadCatalog, type FolderId } from './catalog';
import { LANGS, lang, setLang, t } from './i18n';
import logoUrl from './logo.png';

export const REPO_URL = 'https://github.com/francisreboucas/constructcraft-components';
export const LICENSE_URL = `${REPO_URL}/blob/main/LICENSE`;
export const VIEWER_LICENSE_URL = `${REPO_URL}/blob/main/viewer/LICENSE`;
export const CATALOG_URL = `${REPO_URL}/blob/main/CATALOG.md`;
export const CONTRIBUTING_URL = `${REPO_URL}/blob/main/CONTRIBUTING.md`;
export const DOWNLOAD_URL = `${REPO_URL}/releases/latest`;
export const CONSTRUCTCRAFT_URL = 'https://github.com/francisreboucas/constructcraft';

/** Which rail item is current: all components, one folder, or none (the home page). */
export type ActiveNav = 'all' | FolderId | null;

/** Page layout, exposed as `data-layout` on the app root. */
export type Layout = 'home' | 'gallery' | 'detail' | 'plain';

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

/** Sites of the ConstructCraft network, in the order of the bar every one of them shows. */
const NETWORK = [
  { label: 'ConstructCraft', href: 'https://constructcraft.net/', current: false },
  { label: '3D CraftHouse', href: '#/', current: true },
  { label: 'Marketplace', href: 'https://marketplace.constructcraft.net/', current: false },
  { label: 'Docs', href: 'https://constructcraft.net/#docs', current: false },
] as const;

/**
 * The network bar: a thin dark strip above the frame, identical on
 * constructcraft.net, 3D CraftHouse and the marketplace, with this site marked.
 * Its few words live here rather than in the string tables.
 */
function networkBar(): HTMLElement {
  const pt = lang === 'pt';
  const bar = el('div', 'netbar');
  const nav = el('nav', 'netbar-nav');
  nav.setAttribute('aria-label', pt ? 'Rede ConstructCraft' : 'ConstructCraft network');
  nav.append(el('span', 'netbar-label', pt ? 'Rede' : 'Network'));
  for (const site of NETWORK) {
    const link = el('a', undefined, site.label);
    link.href = site.href;
    if (site.current) link.setAttribute('aria-current', 'page');
    nav.append(link);
  }
  const community = el('a', undefined, pt ? 'Comunidade' : 'Community');
  community.href = 'https://constructcraft.net/#community';
  nav.append(community);
  const download = el('a', 'netbar-cta', pt ? 'Baixar o ConstructCraft' : 'Get ConstructCraft');
  download.href = 'https://constructcraft.net/#download';
  bar.append(nav, download);
  return bar;
}

function footerLinks(className: string): HTMLElement {
  const box = el('div', className);
  const license = el('a', undefined, t.shell.license);
  license.href = LICENSE_URL;
  const repo = el('a', undefined, 'GitHub');
  repo.href = REPO_URL;
  box.append(license, repo);
  return box;
}

export function createShell(root: HTMLElement): Shell {
  const app = el('div', 'app');

  const skip = el('a', 'skip-link', t.shell.skip);
  skip.href = '#main';
  skip.addEventListener('click', (event) => {
    // The hash is the router's; move focus without changing it.
    event.preventDefault();
    main.focus();
  });

  const rail = el('header', 'rail');
  const brand = el('a', 'brand');
  brand.href = '#/';
  const logo = el('img', 'brand-logo');
  logo.src = logoUrl;
  logo.alt = '';
  logo.width = 40;
  logo.height = 40;
  const brandText = el('span', 'brand-text');
  brandText.append(el('span', 'brand-name display', '3D CraftHouse'), el('span', 'brand-sub', t.shell.brandSub));
  brand.append(logo, brandText);

  const langs = el('div', 'lang-switch');
  langs.setAttribute('role', 'group');
  langs.setAttribute('aria-label', t.shell.language);
  for (const option of LANGS) {
    const button = el('button', 'lang-option', option.short);
    button.type = 'button';
    button.lang = option.id;
    button.title = option.name;
    button.setAttribute('aria-label', option.name);
    button.setAttribute('aria-pressed', String(option.id === lang));
    button.addEventListener('click', () => setLang(option.id));
    langs.append(button);
  }

  const nav = el('nav', 'rail-nav');
  nav.setAttribute('aria-label', t.shell.navLabel);
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
  addItem('all', t.shell.all, ALL_ROUTE);
  for (const folder of FOLDERS) addItem(folder.id, folder.label, folderRoute(folder.id));
  nav.append(list);

  rail.append(brand, langs, nav, footerLinks('rail-foot'));

  const main = el('main', 'main');
  main.id = 'main';
  main.tabIndex = -1;

  const pageFoot = el('footer', 'page-foot');
  pageFoot.append(footerLinks('page-foot-links'));

  app.append(skip, rail, main, pageFoot);
  root.append(networkBar(), app);

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
