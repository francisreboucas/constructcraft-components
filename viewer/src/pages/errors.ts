// User-facing error messages, in the page's language.

import { CatalogError } from '../catalog';
import { ComponentLoadError } from '../engine';
import { t } from '../i18n';

function detail(error: unknown): string {
  const cause = error instanceof Error && error.cause instanceof Error ? error.cause.message : null;
  if (error instanceof ComponentLoadError && error.kind === 'parse' && cause) return cause;
  return error instanceof Error ? error.message : String(error);
}

export function describeError(error: unknown, file: string): string {
  if (error instanceof ComponentLoadError) {
    switch (error.kind) {
      case 'network':
        return t.errors.network(error.file, detail(error));
      case 'parse':
        return t.errors.parse(error.file, detail(error));
      case 'engine':
        return t.errors.engine(error.file, detail(error));
    }
  }
  if (error instanceof CatalogError) return t.errors.catalog(detail(error));
  return t.errors.other(file, detail(error));
}

export function errorElement(message: string): HTMLElement {
  const p = document.createElement('p');
  p.className = 'error';
  p.setAttribute('role', 'alert');
  p.textContent = message;
  return p;
}
