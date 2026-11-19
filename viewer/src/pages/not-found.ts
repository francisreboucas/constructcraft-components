// "Page not found", for unknown routes and unknown components.

import { ALL_ROUTE } from '../catalog';
import type { Shell } from '../shell';
import { el, setPageState, setTitle, type Page } from './page';

/** Render the not-found content into the shell (also used by the detail page). */
export function showNotFound(shell: Shell): void {
  shell.setLayout('plain');
  const box = el('div', 'not-found');
  const h1 = el('h1', 'display', 'Página não encontrada');
  const text = el('p', undefined, 'Este endereço não corresponde a nenhum componente da biblioteca.');
  const link = el('a', 'text-link', '← Ver todos os componentes');
  link.href = ALL_ROUTE;
  box.append(h1, text, link);
  shell.main.replaceChildren(box);
  setTitle('Página não encontrada');
  // A finished page, not a failure: tests treat it as ready.
  setPageState('ready');
}

export const notFoundPage: Page = (shell) => {
  shell.setActive(null);
  showNotFound(shell);
  return () => setTitle();
};
