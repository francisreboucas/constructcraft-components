// The component page, `#/<folder>/<name>`: the 3D stage with its toolbar and
// the data panel. The panel is drawn from the catalog entry at once and
// enriched by the loaded component (connectors, parameter kinds, errors).

import { edgesForFolder, folderLabel, folderRoute, loadCatalog, type CatalogEntry, type Route } from '../catalog';
import { libraryUrl, loadComponent, type Component } from '../engine';
import { deviceLabel, formatDecimal, formatParamValue, systemLabel } from '../format';
import { Viewport, VIEW_NAMES, type ViewName } from '../scene';
import type { Shell } from '../shell';
import { describeError } from './errors';
import { showNotFound } from './not-found';
import { el, hasModifier, isTyping, setPageState, setTitle, type Page } from './page';

const VIEW_LABELS: Record<ViewName, string> = {
  iso: 'Isométrica',
  front: 'Frontal',
  top: 'Superior',
  side: 'Lateral',
};

function section(title: string, className?: string): HTMLElement {
  const box = el('section', className ? `panel-section ${className}` : 'panel-section');
  const heading = el('h2', 'panel-head display', title);
  box.append(heading);
  return box;
}

function definitionList(rows: [string, string][]): HTMLElement {
  const dl = el('dl', 'facts');
  for (const [term, value] of rows) {
    const row = el('div', 'fact');
    row.append(el('dt', undefined, term), el('dd', undefined, value));
    dl.append(row);
  }
  return dl;
}

function asNumber(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function mepSection(mep: Record<string, unknown>): HTMLElement | null {
  const rows: [string, string][] = [];
  for (const [key, raw] of Object.entries(mep)) {
    const data = (raw ?? {}) as Record<string, unknown>;
    if (key === 'Fixture') {
      const uhc = asNumber(data.drain_units);
      const weight = asNumber(data.supply_weight);
      rows.push(['Unidades Hunter (UHC)', uhc === null ? '—' : formatDecimal(uhc, 2)]);
      rows.push(['Peso relativo', weight === null ? '—' : formatDecimal(weight, 2)]);
      rows.push(['Água quente', data.hot_water ? 'sim' : 'não']);
    } else if (key === 'Device') {
      const power = asNumber(data.power);
      rows.push(['Dispositivo', deviceLabel(String(data.device ?? '—'))]);
      rows.push(['Potência', power === null ? '—' : `${formatDecimal(power, 1)} VA`]);
    } else {
      for (const [name, value] of Object.entries(data)) rows.push([`${key} · ${name}`, String(value)]);
    }
  }
  if (!rows.length) return null;
  const box = section('Instalações');
  box.append(definitionList(rows));
  return box;
}

interface TypesTable {
  element: HTMLElement;
  /** Re-format the value cells once the parameter kinds are known. */
  applyKinds(kinds: Map<string, string>): void;
}

function typesSection(entry: CatalogEntry): TypesTable {
  const box = section('Tipos');
  const scroller = el('div', 'table-scroll');
  scroller.tabIndex = 0;
  scroller.setAttribute('role', 'region');
  scroller.setAttribute('aria-label', 'Tipos do componente');
  const table = el('table', 'types-table');
  const head = el('thead');
  const headRow = el('tr');
  const nameHead = el('th', 'col-name', 'Tipo');
  nameHead.scope = 'col';
  headRow.append(nameHead);
  for (const param of entry.parameters) {
    const th = el('th', 'col-num', param);
    th.scope = 'col';
    headRow.append(th);
  }
  head.append(headRow);

  const cells: { cell: HTMLElement; param: string; value: number | undefined }[] = [];
  const tbody = el('tbody');
  entry.types.forEach((type, index) => {
    const row = el('tr');
    const name = el('th', 'col-name');
    name.scope = 'row';
    name.append(el('span', 'type-name', type.name));
    if (index === 0) {
      const tag = el('span', 'tag', 'no 3D');
      tag.title = 'O modelo 3D mostra este tipo';
      name.append(' ', tag);
    }
    row.append(name);
    for (const param of entry.parameters) {
      const value = type.values[param];
      const cell = el('td', 'col-num', formatParamValue(value));
      cells.push({ cell, param, value });
      row.append(cell);
    }
    tbody.append(row);
  });
  table.append(head, tbody);
  scroller.append(table);
  box.append(scroller);
  if (entry.parameters.length) box.append(el('p', 'panel-note', 'Medidas em metros.'));

  return {
    element: box,
    applyKinds(kinds) {
      for (const { cell, param, value } of cells) cell.textContent = formatParamValue(value, kinds.get(param));
    },
  };
}

function connectorsSection(component: Component): HTMLElement | null {
  if (!component.connectors.length) return null;
  const box = section('Conectores');
  const table = el('table', 'connectors-table');
  const tbody = el('tbody');
  for (const connector of component.connectors) {
    const row = el('tr');
    const name = el('th', 'col-name', connector.name);
    name.scope = 'row';
    const diameter =
      connector.diameter !== null && connector.diameter > 0 ? `Ø ${formatDecimal(connector.diameter * 1000, 1)} mm` : '';
    row.append(name, el('td', 'col-system', systemLabel(connector.system)), el('td', 'col-num', diameter));
    tbody.append(row);
  }
  table.append(tbody);
  box.append(table);
  return box;
}

function copyText(text: string, fallbackTarget: HTMLElement): Promise<boolean> {
  const selectFallback = () => {
    // No clipboard access: select the command so it can be copied by hand.
    const range = document.createRange();
    range.selectNodeContents(fallbackTarget);
    const selection = getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
    return false;
  };
  if (!navigator.clipboard?.writeText) return Promise.resolve(selectFallback());
  return navigator.clipboard.writeText(text).then(() => true, selectFallback);
}

function commandSection(entry: CatalogEntry): { element: HTMLElement; dispose(): void } {
  const box = section('No ConstructCraft');
  box.append(el('p', 'panel-text', 'Carregue o arquivo no projeto:'));
  const command = `ccad -p casa.ccad --save run component_load path=${entry.file}`;
  const block = el('div', 'command');
  const code = el('code', 'command-text', command);
  const button = el('button', 'button button-small', 'Copiar');
  button.type = 'button';
  let timer = 0;
  button.addEventListener('click', () => {
    void copyText(command, code).then((ok) => {
      if (!ok) return;
      button.textContent = 'Copiado';
      clearTimeout(timer);
      timer = window.setTimeout(() => (button.textContent = 'Copiar'), 2000);
    });
  });
  block.append(code, button);
  box.append(block);
  return { element: box, dispose: () => clearTimeout(timer) };
}

function buildPanel(entry: CatalogEntry) {
  const panel = el('aside', 'panel');
  panel.setAttribute('aria-label', 'Dados do componente');
  const notice = el('div', 'panel-notice-slot');
  const header = el('div', 'panel-header');
  header.append(el('p', 'eyebrow', folderLabel(entry.folder)), el('h1', 'panel-title display', entry.component));
  const description = entry.types[0]?.description;
  if (description) header.append(el('p', 'panel-text', description));
  const download = el('a', 'button-primary', 'Baixar .ccomp');
  download.href = libraryUrl(entry.file);
  download.setAttribute('download', `${entry.slug}.ccomp`);
  header.append(download);

  const types = typesSection(entry);
  const mep = entry.mep ? mepSection(entry.mep) : null;
  const connectorsSlot = el('div', 'panel-slot');
  const command = commandSection(entry);
  panel.append(notice, header, types.element);
  if (mep) panel.append(mep);
  panel.append(connectorsSlot, command.element);

  return {
    element: panel,
    enrich(component: Component) {
      const kinds = new Map(component.params.map((p) => [p.name, p.kind] as const));
      types.applyKinds(kinds);
      const connectors = connectorsSection(component);
      if (connectors) connectorsSlot.replaceChildren(connectors);
      const errors = component.errors.length;
      if (errors > 0) {
        const p = el(
          'p',
          'notice',
          errors === 1
            ? '1 peça não pôde ser exibida neste visualizador.'
            : `${errors} peças não puderam ser exibidas neste visualizador.`,
        );
        p.setAttribute('role', 'status');
        notice.replaceChildren(p);
      }
    },
    dispose: command.dispose,
  };
}

function renderDetail(shell: Shell, entry: CatalogEntry): () => void {
  let alive = true;
  let viewport: Viewport | null = null;
  let viewObserver: MutationObserver | null = null;
  let dimensionsOn = true;

  setTitle(entry.component);
  const page = el('div', 'detail');

  // Stage: back link, viewport, toolbar.
  const stage = el('section', 'stage');
  stage.setAttribute('aria-label', 'Modelo 3D');
  const back = el('a', 'back-link', `← ${folderLabel(entry.folder)}`);
  back.href = folderRoute(entry.folder);
  const view = el('div', 'stage-view detail-viewport');
  const status = el('div', 'stage-status');
  view.append(status);

  const toolbar = el('div', 'toolbar');
  const views = el('div', 'segmented');
  views.setAttribute('role', 'group');
  views.setAttribute('aria-label', 'Vista');
  const buttons = VIEW_NAMES.map((name, index) => {
    const button = el('button', 'segment', VIEW_LABELS[name]);
    button.type = 'button';
    button.dataset.view = name;
    button.setAttribute('aria-pressed', String(name === 'iso'));
    button.setAttribute('aria-keyshortcuts', String(index + 1));
    button.disabled = true;
    button.addEventListener('click', () => viewport?.setView(name));
    return button;
  });
  views.append(...buttons);
  const cotasLabel = el('label', 'check');
  const cotas = el('input');
  cotas.type = 'checkbox';
  cotas.checked = dimensionsOn;
  cotas.disabled = true;
  cotas.addEventListener('change', () => {
    dimensionsOn = cotas.checked;
    viewport?.setDimensionsVisible(dimensionsOn);
  });
  cotasLabel.append(cotas, el('span', undefined, 'Cotas'));
  const hint = el('span', 'toolbar-hint', 'Arraste para girar · role para aproximar');
  toolbar.append(views, cotasLabel, hint);
  stage.append(back, view, toolbar);

  const panel = buildPanel(entry);
  page.append(stage, panel.element);
  shell.main.append(page);

  const syncButtons = () => {
    const current = view.dataset.view;
    for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.view === current));
  };

  const showStatus = (message: string | null, retry = false) => {
    status.replaceChildren();
    status.hidden = message === null;
    if (message === null) return;
    status.append(el('p', 'stage-message', message));
    if (retry) {
      const button = el('button', 'button', 'Tentar de novo');
      button.type = 'button';
      button.addEventListener('click', () => void load());
      status.append(button);
    }
  };

  const load = async () => {
    setPageState('loading');
    showStatus('Carregando geometria…');
    status.setAttribute('role', 'status');
    try {
      const component = await loadComponent(entry.file);
      if (!alive) return;
      panel.enrich(component);
      if (!component.bounds) {
        showStatus('Este componente não tem geometria 3D.');
        setPageState('ready');
        return;
      }
      showStatus(null);
      viewport = new Viewport(view);
      viewport.setComponent(component, { edges: edgesForFolder(entry.folder), view: 'iso', dimensions: dimensionsOn });
      viewObserver = new MutationObserver(syncButtons);
      viewObserver.observe(view, { attributes: true, attributeFilter: ['data-view'] });
      syncButtons();
      for (const button of buttons) button.disabled = false;
      cotas.disabled = false;
      setPageState('ready');
    } catch (error) {
      if (!alive) return;
      status.setAttribute('role', 'alert');
      showStatus(describeError(error, entry.file), true);
      setPageState('error');
    }
  };

  const onKey = (event: KeyboardEvent) => {
    if (!viewport || hasModifier(event) || isTyping(event)) return;
    const index = ['1', '2', '3', '4'].indexOf(event.key);
    const name = VIEW_NAMES[index];
    if (index < 0 || !name) return;
    event.preventDefault();
    viewport.setView(name);
  };
  document.addEventListener('keydown', onKey);

  void load();

  return () => {
    alive = false;
    document.removeEventListener('keydown', onKey);
    viewObserver?.disconnect();
    viewport?.dispose();
    viewport = null;
    panel.dispose();
    setTitle();
  };
}

export const detailPage: Page = (shell, route: Route) => {
  if (route.name !== 'component') throw new Error('detailPage needs a component route');
  let alive = true;
  let cleanup: (() => void) | null = null;

  shell.setLayout('detail');
  shell.setActive(route.folder);
  setPageState('loading');

  loadCatalog().then(
    (catalog) => {
      if (!alive) return;
      const entry = catalog.byId.get(route.id);
      if (!entry) {
        showNotFound(shell);
        return;
      }
      cleanup = renderDetail(shell, entry);
    },
    (error: unknown) => {
      if (!alive) return;
      shell.setLayout('plain');
      const box = el('div', 'not-found');
      box.append(el('h1', 'display', 'Erro ao abrir o componente'), el('p', 'error', describeError(error, 'catalog.json')));
      shell.main.replaceChildren(box);
      setPageState('error');
    },
  );

  return () => {
    alive = false;
    cleanup?.();
    setTitle();
  };
};
