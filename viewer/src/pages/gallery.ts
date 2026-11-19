// The gallery: `#/componentes` (every folder, grouped) and `#/<folder>` (one folder),
// with the search box at the top of the main column.

import {
  FOLDERS,
  entryRoute,
  folderLabel,
  loadCatalog,
  type Catalog,
  type CatalogEntry,
  type Route,
} from '../catalog';
import { normalizeText, typeCount } from '../format';
import { t } from '../i18n';
import { ThumbnailLoader } from '../thumbnails';
import { describeError, errorElement } from './errors';
import { el, hasModifier, isTyping, setPageState, setTitle, type Page } from './page';

/** The search query; survives navigating to a component and back. */
let query = '';
/** Gallery scroll positions by route hash, restored when coming back from a component. */
const scrollMemory = new Map<string, number>();
/** Search text of each entry, normalised once. */
const haystacks = new Map<string, string>();

function haystack(entry: CatalogEntry): string {
  let text = haystacks.get(entry.id);
  if (text === undefined) {
    const parts = [entry.title, entry.component];
    parts.push(entry.author);
    for (const type of entry.types) parts.push(type.name, type.description);
    text = normalizeText(parts.join('\n'));
    haystacks.set(entry.id, text);
  }
  return text;
}

function matches(entry: CatalogEntry, terms: string[]): boolean {
  const text = haystack(entry);
  return terms.every((term) => text.includes(term));
}

function card(entry: CatalogEntry): HTMLAnchorElement {
  const link = el('a', 'card');
  link.href = entryRoute(entry);
  link.append(
    el('span', 'card-thumb'),
    el('span', 'card-name', entry.title),
    el('span', 'card-meta', typeCount(entry.types.length)),
  );
  if (entry.author) link.append(el('span', 'card-author', entry.author));
  return link;
}

function grid(cards: HTMLElement[]): HTMLElement {
  const box = el('div', 'card-grid');
  box.append(...cards);
  return box;
}

export const galleryPage: Page = (shell, route: Route, context) => {
  if (route.name !== 'all' && route.name !== 'folder') throw new Error('galleryPage needs a gallery route');
  const folder = route.name === 'folder' ? route.folder : null;
  const routeKey = folder ?? '';
  let alive = true;

  shell.setLayout('gallery');
  shell.setActive(folder ?? 'all');
  setTitle(folder ? folderLabel(folder) : undefined);
  setPageState('loading');

  const page = el('div', 'gallery');
  const h1 = el('h1', 'sr-only', folder ? t.gallery.headingFolder(folderLabel(folder)) : t.gallery.headingAll);

  const bar = el('div', 'searchbar');
  const label = el('label', 'sr-only', t.gallery.searchLabel);
  label.htmlFor = 'search';
  const input = el('input', 'search-input');
  input.id = 'search';
  input.type = 'search';
  input.placeholder = t.gallery.searchPlaceholder;
  input.autocomplete = 'off';
  input.spellcheck = false;
  input.setAttribute('aria-keyshortcuts', '/');
  input.value = query;
  const count = el('span', 'search-count');
  count.setAttribute('aria-live', 'polite');
  bar.append(label, input, count);

  const body = el('div', 'gallery-body');
  page.append(h1, bar, body);
  shell.main.append(page);

  const loader = new ThumbnailLoader();
  let catalog: Catalog | null = null;
  const cards = new Map<string, HTMLAnchorElement>();

  function cardFor(entry: CatalogEntry): HTMLAnchorElement {
    let node = cards.get(entry.id);
    if (!node) {
      node = card(entry);
      cards.set(entry.id, node);
      loader.observe(node, entry);
    }
    return node;
  }

  function render(): void {
    if (!catalog) return;
    const scope = folder ? catalog.entries.filter((e) => e.folder === folder) : catalog.entries;
    const terms = normalizeText(query).split(/\s+/).filter(Boolean);
    const found = terms.length ? scope.filter((e) => matches(e, terms)) : scope;
    count.textContent = terms.length ? t.gallery.countOf(found.length, scope.length) : String(scope.length);

    if (found.length === 0) {
      const empty = el('div', 'empty');
      empty.append(el('p', undefined, t.gallery.empty(query.trim())));
      const clear = el('button', 'button', t.gallery.clear);
      clear.type = 'button';
      clear.addEventListener('click', () => {
        setQuery('');
        input.focus();
      });
      empty.append(clear);
      body.replaceChildren(empty);
      return;
    }

    if (!folder && !terms.length) {
      const sections: HTMLElement[] = [];
      for (const info of FOLDERS) {
        const entries = found.filter((e) => e.folder === info.id);
        if (!entries.length) continue;
        const section = el('section', 'folder-section');
        const headingId = `folder-${info.id}`;
        section.setAttribute('aria-labelledby', headingId);
        const heading = el('h2', 'section-head');
        heading.id = headingId;
        heading.append(el('span', 'display', info.label), el('span', 'section-count', String(entries.length)));
        section.append(heading, grid(entries.map(cardFor)));
        sections.push(section);
      }
      body.replaceChildren(...sections);
    } else {
      body.replaceChildren(grid(found.map(cardFor)));
    }
  }

  function setQuery(next: string): void {
    query = next;
    if (input.value !== next) input.value = next;
    render();
  }

  input.addEventListener('input', () => {
    loader.noteInput();
    setQuery(input.value);
  });

  const onKey = (event: KeyboardEvent) => {
    if (event.key === '/' && !hasModifier(event) && !isTyping(event)) {
      event.preventDefault();
      input.focus();
      input.select();
    } else if (event.key === 'Escape' && event.target === input) {
      event.preventDefault();
      setQuery('');
    }
  };
  document.addEventListener('keydown', onKey);

  loadCatalog().then(
    (loaded) => {
      if (!alive) return;
      catalog = loaded;
      render();
      const saved = scrollMemory.get(routeKey);
      if (context.previous?.name === 'component' && saved !== undefined) window.scrollTo(0, saved);
      setPageState('ready');
    },
    (error: unknown) => {
      if (!alive) return;
      bar.remove();
      body.replaceChildren(errorElement(describeError(error, 'catalog.json')));
      setPageState('error');
    },
  );

  return () => {
    alive = false;
    scrollMemory.set(routeKey, window.scrollY);
    document.removeEventListener('keydown', onKey);
    loader.dispose();
    setTitle();
  };
};
