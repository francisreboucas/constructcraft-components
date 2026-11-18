// Placeholder detail page: the component full-window with the four preset
// views. Replaced by the detail UI.

import { edgesForFolder, loadCatalog, type Route } from '../catalog';
import { loadComponent } from '../engine';
import { Viewport, VIEW_NAMES, type ViewName } from '../scene';
import { describeError, errorElement } from './errors';
import { setPageState, type Page } from './page';

const VIEW_LABELS: Record<ViewName, string> = {
  iso: 'Isométrica',
  front: 'Frontal',
  top: 'Superior',
  side: 'Lateral',
};

export const detailPage: Page = (root, route: Route) => {
  if (route.name !== 'component') throw new Error('detailPage needs a component route');
  let alive = true;
  let viewport: Viewport | null = null;

  const section = document.createElement('section');
  section.className = 'detail';
  const stage = document.createElement('div');
  stage.className = 'detail-viewport';
  const bar = document.createElement('div');
  bar.className = 'detail-bar';
  const back = document.createElement('a');
  back.href = '#/';
  back.textContent = 'Voltar';
  const title = document.createElement('h1');
  title.className = 'display';
  title.textContent = route.slug;
  bar.append(back, title);
  section.append(stage, bar);
  root.append(section);

  const file = `components/${route.id}.ccomp`;

  (async () => {
    try {
      const catalog = await loadCatalog();
      const entry = catalog.byId.get(route.id);
      if (!alive) return;
      if (!entry) {
        bar.append(errorElement(`O componente ${file} não está no catálogo.`));
        setPageState('error');
        return;
      }
      title.textContent = entry.component;
      document.title = `${entry.component} · Componentes ConstructCraft`;
      const component = await loadComponent(entry.file);
      if (!alive) return;

      viewport = new Viewport(stage);
      viewport.setComponent(component, { edges: edgesForFolder(entry.folder), view: 'iso' });

      const buttons = VIEW_NAMES.map((view) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.view = view;
        button.textContent = VIEW_LABELS[view];
        button.addEventListener('click', () => {
          viewport?.setView(view);
          sync();
        });
        return button;
      });
      const sync = () => {
        for (const b of buttons) b.setAttribute('aria-pressed', String(viewport?.view === b.dataset.view));
      };
      // The user orbiting leaves the preset; reflect it on the buttons.
      stage.addEventListener('pointerup', () => requestAnimationFrame(sync));
      sync();
      bar.append(...buttons);
      setPageState('ready');
    } catch (error) {
      if (!alive) return;
      bar.append(errorElement(describeError(error, file)));
      setPageState('error');
    }
  })();

  return () => {
    alive = false;
    viewport?.dispose();
    document.title = 'Componentes ConstructCraft';
  };
};
