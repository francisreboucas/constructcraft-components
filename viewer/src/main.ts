import './styles/fonts';
import './styles/tokens.css';
import './styles/base.css';
import './styles/app.css';
import './styles/home.css';
import { parseRoute, type Route } from './catalog';
import { detailPage } from './pages/detail';
import { galleryPage } from './pages/gallery';
import { homePage } from './pages/home';
import { notFoundPage } from './pages/not-found';
import type { Page } from './pages/page';
import { createShell } from './shell';

const root = document.getElementById('app');
if (!root) throw new Error('#app is missing');

if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

const shell = createShell(root);
let cleanup: (() => void) | null = null;
let previous: Route | null = null;

function pageFor(route: Route): Page {
  switch (route.name) {
    case 'home':
      return homePage;
    case 'all':
    case 'folder':
      return galleryPage;
    case 'component':
      return detailPage;
    case 'not-found':
      return notFoundPage;
  }
}

function navigate(): void {
  // Cleanup first: pages save their scroll position before the content goes.
  cleanup?.();
  cleanup = null;
  shell.main.replaceChildren();
  window.scrollTo(0, 0);
  const route = parseRoute(location.hash);
  cleanup = pageFor(route)(shell, route, { previous });
  previous = route;
}

window.addEventListener('hashchange', navigate);
navigate();

// Test hooks for `npm run smoke` (separate chunk, never loaded otherwise).
if (new URLSearchParams(location.search).has('smoke')) void import('./smoke-hooks');
