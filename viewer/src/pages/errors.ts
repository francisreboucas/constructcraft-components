// User-facing (pt-BR) error messages.

import { CatalogError } from '../catalog';
import { ComponentLoadError } from '../engine';

function detail(error: unknown): string {
  const cause = error instanceof Error && error.cause instanceof Error ? error.cause.message : null;
  if (error instanceof ComponentLoadError && error.kind === 'parse' && cause) return cause;
  return error instanceof Error ? error.message : String(error);
}

export function describeError(error: unknown, file: string): string {
  if (error instanceof ComponentLoadError) {
    switch (error.kind) {
      case 'network':
        return `Não foi possível baixar ${error.file} (${detail(error)}).`;
      case 'parse':
        return `Não foi possível ler ${error.file}: ${detail(error)}`;
      case 'engine':
        return `O motor geométrico não iniciou ao abrir ${error.file}: ${detail(error)}`;
    }
  }
  if (error instanceof CatalogError) return `Não foi possível carregar catalog.json: ${detail(error)}`;
  return `Erro ao abrir ${file}: ${detail(error)}`;
}

export function errorElement(message: string): HTMLElement {
  const p = document.createElement('p');
  p.className = 'error';
  p.setAttribute('role', 'alert');
  p.textContent = message;
  return p;
}
