import './styles/fonts';
import './styles/tokens.css';
import './styles/base.css';
import { parseRoute } from './catalog';
import { detailPage } from './pages/detail';
import { errorElement } from './pages/errors';
import { homePage } from './pages/home';
import { setPageState } from './pages/page';

const root = document.getElementById('app');
if (!root) throw new Error('#app is missing');
const app: HTMLElement = root;

let cleanup: (() => void) | null = null;

function navigate(): void {
  cleanup?.();
  cleanup = null;
  app.replaceChildren();
  setPageState('loading');
  const route = parseRoute(location.hash);
  switch (route.name) {
    case 'home':
    case 'folder': // No folder page yet: the home lists every folder.
      cleanup = homePage(app, route);
      break;
    case 'component':
      cleanup = detailPage(app, route);
      break;
    case 'not-found': {
      const main = document.createElement('main');
      main.className = 'page';
      main.append(errorElement(`Página não encontrada: ${route.hash}`));
      app.append(main);
      setPageState('error');
      break;
    }
  }
  window.scrollTo(0, 0);
}

window.addEventListener('hashchange', navigate);
navigate();

// Test hooks for `npm run smoke` (separate chunk, never loaded otherwise).
if (new URLSearchParams(location.search).has('smoke')) void import('./smoke-hooks');
