// Smoke test: build, serve dist locally, drive the gallery and detail pages in
// headless Chromium at desktop (1280x800) and mobile (390x844) sizes, and fail
// on console errors, page errors, external requests, a blank 3D view, blank
// thumbnails, horizontal overflow on mobile or leaked WebGL contexts and
// listeners. Screenshots go to viewer/.smoke/.
//
//   npm run smoke
//   npm run smoke -- --no-build   (test the dist/ already built by `npm run build`)

import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { build, preview } from 'vite';

const root = fileURLToPath(new URL('..', import.meta.url));
const outDir = fileURLToPath(new URL('../.smoke/', import.meta.url));
const PORT = 4317;
const ORIGIN = `http://127.0.0.1:${PORT}`;
const TIMEOUT = 30_000;
// The gallery shows every catalog entry.
const TOTAL = JSON.parse(await readFile(new URL('../../catalog.json', import.meta.url), 'utf8')).components.length;

const VIEW_ROUTE = 'plumbing/pia-cozinha';
const DETAIL_ROUTES = [VIEW_ROUTE, 'electrical/tug-100va', 'planting/ipe-amarelo', 'lighting/pendente'];
const VIEWS = ['iso', 'front', 'top', 'side'];

const DEVICES = {
  desktop: { viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 },
  mobile: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true },
};

const failures = [];
const fail = (message) => {
  failures.push(message);
  console.error(`  FAIL ${message}`);
};

// Counts WebGL contexts (created minus lost) and window/document listeners, for leak checks.
const INSTRUMENT = () => {
  const contexts = new Set();
  const getContext = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (type, ...rest) {
    const ctx = getContext.call(this, type, ...rest);
    if (ctx && String(type).startsWith('webgl') && !contexts.has(this)) {
      contexts.add(this);
      this.addEventListener('webglcontextlost', () => contexts.delete(this), { once: true });
    }
    return ctx;
  };
  const listeners = new Map([
    [window, new Set()],
    [document, new Set()],
  ]);
  const add = EventTarget.prototype.addEventListener;
  const remove = EventTarget.prototype.removeEventListener;
  const key = (type, fn, options) => {
    const capture = typeof options === 'boolean' ? options : Boolean(options?.capture);
    return { type, fn, capture };
  };
  const find = (set, k) => [...set].find((e) => e.type === k.type && e.fn === k.fn && e.capture === k.capture);
  EventTarget.prototype.addEventListener = function (type, fn, options) {
    const set = listeners.get(this);
    if (set && fn && !(typeof options === 'object' && options?.once)) {
      const k = key(type, fn, options);
      if (!find(set, k)) set.add(k);
    }
    return add.call(this, type, fn, options);
  };
  EventTarget.prototype.removeEventListener = function (type, fn, options) {
    const set = listeners.get(this);
    if (set) {
      const hit = find(set, key(type, fn, options));
      if (hit) set.delete(hit);
    }
    return remove.call(this, type, fn, options);
  };
  window.__leaks = () => ({
    contexts: contexts.size,
    listeners: [...listeners.values()].reduce((n, s) => n + s.size, 0),
  });
};

/** Fraction of pixels of a PNG that differ from `background` by more than `threshold` (decoded in the page). */
async function inkCoverage(page, png, background, threshold) {
  return page.evaluate(
    async ({ b64, background, threshold }) => {
      const img = new Image();
      img.src = `data:image/png;base64,${b64}`;
      await img.decode();
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
      let hits = 0;
      for (let i = 0; i < data.length; i += 4) {
        const d = Math.max(
          Math.abs(data[i] - background[0]),
          Math.abs(data[i + 1] - background[1]),
          Math.abs(data[i + 2] - background[2]),
        );
        if (d > threshold) hits++;
      }
      return hits / (data.length / 4);
    },
    { b64: png.toString('base64'), background, threshold },
  );
}

/** Fraction of non-transparent pixels of each loaded card thumbnail. */
async function thumbnailCoverage(page) {
  return page.$$eval('.card[data-thumb="ready"] .card-thumb img', (imgs) =>
    imgs.map((img) => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
      let opaque = 0;
      for (let i = 3; i < data.length; i += 4) if (data[i] > 16) opaque++;
      const name = img.closest('.card')?.querySelector('.card-name')?.textContent ?? '?';
      return { name, coverage: opaque / (data.length / 4) };
    }),
  );
}

function watch(page, label) {
  page.on('console', (msg) => {
    if (msg.type() === 'error') fail(`${label()}: console error: ${msg.text()}`);
  });
  page.on('pageerror', (error) => fail(`${label()}: page error: ${error.message}`));
  page.on('request', (request) => {
    const url = request.url();
    if (!url.startsWith(ORIGIN) && !url.startsWith('data:') && !url.startsWith('blob:')) {
      fail(`${label()}: external request to ${url}`);
    }
  });
  page.on('requestfailed', (request) => fail(`${label()}: request failed: ${request.url()}`));
}

async function frames(page, n = 2) {
  await page.evaluate(
    (n) =>
      new Promise((resolve) => {
        const step = (left) => (left ? requestAnimationFrame(() => step(left - 1)) : resolve());
        step(n);
      }),
    n,
  );
}

async function go(page, hash) {
  await page.evaluate((h) => {
    document.documentElement.dataset.state = 'navigating';
    location.hash = h;
  }, hash);
}

async function waitReady(page, label) {
  await page.waitForSelector('html[data-state="ready"], html[data-state="error"]', { timeout: TIMEOUT });
  const state = await page.getAttribute('html', 'data-state');
  if (state !== 'ready') {
    const message = await page.textContent('.error, .stage-message').catch(() => null);
    fail(`${label}: page state is ${state}${message ? ` (${message})` : ''}`);
    return false;
  }
  return true;
}

/** Wait until every card on screen has its thumbnail (or its "Sem prévia"). */
async function waitThumbs(page) {
  await page.waitForFunction(
    () =>
      [...document.querySelectorAll('.card')].every((card) => {
        const r = card.getBoundingClientRect();
        const onScreen = r.bottom > 0 && r.top < innerHeight;
        return !onScreen || card.dataset.thumb !== 'pending';
      }),
    null,
    { timeout: 90_000 },
  );
  await frames(page, 3);
}

async function waitStill(page) {
  await page.waitForSelector('.detail-viewport[data-rendered="true"]:not([data-moving])', { timeout: TIMEOUT });
  // Two more frames so the label overlay has caught up with the last camera move.
  await frames(page, 2);
}

async function checkCanvas(page, label, file) {
  const png = await page.locator('.detail-viewport').screenshot();
  await writeFile(`${outDir}${file}`, png);
  const coverage = await inkCoverage(page, png, [0xe9, 0xee, 0xf2], 60);
  if (coverage < 0.005) fail(`${label}: the 3D view looks blank (${(coverage * 100).toFixed(2)}% drawn)`);
  return coverage;
}

/** Dimension labels must sit inside the 3D view, never under the toolbar or panel. */
async function checkLabelsInside(page, label) {
  const outside = await page.evaluate(() => {
    const view = document.querySelector('.detail-viewport').getBoundingClientRect();
    const labels = [...document.querySelectorAll('.cota-label')].filter((l) => l.offsetParent !== null);
    return {
      shown: labels.length,
      outside: labels
        .map((l) => l.getBoundingClientRect())
        .filter((r) => r.left < view.left - 1 || r.right > view.right + 1 || r.top < view.top - 1 || r.bottom > view.bottom + 1)
        .length,
    };
  });
  if (outside.outside > 0) fail(`${label}: ${outside.outside} of ${outside.shown} dimension labels fall outside the 3D view`);
  return outside.shown;
}

async function checkOverflow(page, label) {
  const { scroll, width } = await page.evaluate(() => ({
    scroll: document.documentElement.scrollWidth,
    width: document.documentElement.clientWidth,
  }));
  if (scroll > width) fail(`${label}: horizontal overflow (${scroll}px content in ${width}px)`);
}

async function shot(page, device, name, options = {}) {
  const file = `${device}--${name}.png`;
  await page.screenshot({ path: `${outDir}${file}`, ...options });
  return file;
}

async function runDevice(browser, device) {
  const context = await browser.newContext(DEVICES[device]);
  await context.addInitScript(INSTRUMENT);
  const page = await context.newPage();
  let current = device;
  watch(page, () => current);
  const step = (label) => {
    current = `[${device}] ${label}`;
    console.log(current);
    return current;
  };
  const mobile = device === 'mobile';
  const afterPage = async (label) => {
    if (!mobile) return;
    await checkOverflow(page, label);
    // The narrowest supported width.
    await page.setViewportSize({ width: 360, height: 800 });
    await frames(page, 2);
    await checkOverflow(page, `${label} at 360 px`);
    await page.setViewportSize(DEVICES.mobile.viewport);
    await frames(page, 2);
  };

  // Gallery: every folder, grouped.
  {
    const label = step('#/');
    await page.goto(`${ORIGIN}/#/`);
    if (await waitReady(page, label)) {
      const cards = await page.locator('.card').count();
      if (cards !== TOTAL) fail(`${label}: expected ${TOTAL} cards, found ${cards}`);
      const sections = await page.locator('.folder-section').count();
      if (sections !== 8) fail(`${label}: expected 8 folder sections, found ${sections}`);
      const h1 = await page.locator('h1').count();
      if (h1 !== 1) fail(`${label}: expected one h1, found ${h1}`);
      const count = (await page.textContent('.search-count'))?.trim();
      if (count !== String(TOTAL)) fail(`${label}: count reads "${count}"`);
      await waitThumbs(page);
      const thumbs = await thumbnailCoverage(page);
      for (const t of thumbs) if (t.coverage < 0.01) fail(`${label}: thumbnail "${t.name}" looks blank`);
      const failed = await page.locator('.card[data-thumb="failed"]').count();
      if (failed) fail(`${label}: ${failed} thumbnails failed`);
      const active = await page.textContent('.nav-item[aria-current="page"] .nav-label');
      if (active !== 'Todos') fail(`${label}: active nav item is "${active}"`);
      console.log(`  ${cards} cards, ${thumbs.length} thumbnails on screen -> ${await shot(page, device, 'home')}`);
      await afterPage(label);
    }
  }

  // Scroll position and query survive a visit to a component (desktop only: same logic on mobile).
  if (!mobile) {
    const label = step('#/ scroll restore');
    await page.evaluate(() => window.scrollTo(0, 1400));
    await frames(page);
    const before = await page.evaluate(() => window.scrollY);
    await go(page, '#/plumbing/pia-cozinha');
    await page.waitForSelector('.detail-viewport');
    await page.evaluate(() => (document.documentElement.dataset.state = 'navigating'));
    await page.goBack();
    await waitReady(page, label);
    await frames(page);
    const after = await page.evaluate(() => window.scrollY);
    if (Math.abs(after - before) > 2) fail(`${label}: scroll was ${before}, restored to ${after}`);
    else console.log(`  restored scrollY ${after}`);
    await page.evaluate(() => window.scrollTo(0, 0));
  }

  // One folder.
  {
    const label = step('#/plumbing');
    await go(page, '#/plumbing');
    if (await waitReady(page, label)) {
      const cards = await page.locator('.card').count();
      const count = (await page.textContent('.search-count'))?.trim();
      const navCount = (await page.textContent('.nav-item[aria-current="page"] .nav-count'))?.trim();
      if (String(cards) !== count || count !== navCount) fail(`${label}: ${cards} cards, count "${count}", nav "${navCount}"`);
      if ((await page.locator('.folder-section').count()) !== 0) fail(`${label}: folder page should be a flat grid`);
      const title = await page.title();
      if (title !== 'Hidrossanitário · Componentes ConstructCraft') fail(`${label}: title "${title}"`);
      await waitThumbs(page);
      console.log(`  ${cards} cards -> ${await shot(page, device, 'plumbing')}`);
      await afterPage(label);
    }
  }

  // Search across every folder.
  {
    const label = step('#/ search "porta"');
    await go(page, '#/');
    await waitReady(page, label);
    await page.fill('#search', 'PORTA');
    const count = (await page.textContent('.search-count'))?.trim();
    const cards = await page.locator('.card').count();
    if (count !== `${cards} de ${TOTAL}` || cards === 0) fail(`${label}: count "${count}" with ${cards} cards`);
    await waitThumbs(page);
    console.log(`  "${count}" -> ${await shot(page, device, 'search-porta')}`);
    await afterPage(label);

    // Accent-insensitive: "hidraulico" must match the same as "hidráulico".
    await page.fill('#search', 'luminaria');
    const plain = await page.locator('.card').count();
    await page.fill('#search', 'LUMINÁRIA');
    const accented = await page.locator('.card').count();
    if (plain === 0 || plain !== accented) fail(`${label}: accent-insensitive search gave ${plain} vs ${accented}`);

    // The query survives opening a component and coming back.
    await page.fill('#search', 'porta');
    await page.locator('.card').first().click();
    await page.waitForSelector('.detail-viewport');
    await page.evaluate(() => (document.documentElement.dataset.state = 'navigating'));
    await page.goBack();
    await waitReady(page, label);
    const kept = await page.inputValue('#search');
    if (kept !== 'porta') fail(`${label}: query after coming back is "${kept}"`);
  }

  // Empty search.
  {
    const label = step('#/ empty search');
    await page.fill('#search', 'zzzzqx');
    const text = await page.textContent('.empty p');
    if (text !== 'Nenhum componente encontrado para “zzzzqx”.') fail(`${label}: empty message "${text}"`);
    console.log(`  -> ${await shot(page, device, 'search-empty')}`);
    await afterPage(label);
    await page.click('.empty button');
    const count = (await page.textContent('.search-count'))?.trim();
    if (count !== String(TOTAL)) fail(`${label}: after "Limpar busca" count is "${count}"`);
    if (!mobile) {
      // "/" focuses the search, Esc clears it.
      await page.locator('.nav-item').first().focus();
      await page.keyboard.press('/');
      await page.keyboard.type('pia');
      const typed = await page.inputValue('#search');
      await page.keyboard.press('Escape');
      const cleared = await page.inputValue('#search');
      if (typed !== 'pia' || cleared !== '') fail(`${label}: "/" then Esc gave "${typed}" then "${cleared}"`);
    } else {
      await page.fill('#search', '');
    }
  }

  // Component pages.
  for (const route of DETAIL_ROUTES) {
    const label = step(`#/${route}`);
    await go(page, `#/${route}`);
    if (!(await waitReady(page, label))) continue;
    await waitStill(page);
    const name = route.replace('/', '--');
    const coverage = await checkCanvas(page, label, `${device}--${name}--canvas.png`);
    const labels = await checkLabelsInside(page, label);
    const h1 = await page.locator('h1').count();
    if (h1 !== 1) fail(`${label}: expected one h1, found ${h1}`);
    const title = await page.title();
    const heading = await page.textContent('.panel-title');
    if (title !== `${heading} · Componentes ConstructCraft`) fail(`${label}: title "${title}"`);
    const href = await page.getAttribute('.button-primary', 'href');
    if (!href?.endsWith(`library/components/${route}.ccomp`)) fail(`${label}: download link is ${href}`);
    if (mobile) {
      const touch = await page.$eval('.detail-viewport canvas', (c) => getComputedStyle(c).touchAction);
      if (touch !== 'none') fail(`${label}: canvas touch-action is ${touch}`);
      const scrolls = await page.evaluate(() => document.documentElement.scrollHeight > innerHeight);
      if (!scrolls) fail(`${label}: page does not scroll past the 3D view`);
    }
    const file = await shot(page, device, name, mobile ? { fullPage: true } : {});
    console.log(`  ${(coverage * 100).toFixed(1)}% drawn, ${labels} dimension labels -> ${file}`);
    await afterPage(label);

    if (route === VIEW_ROUTE) {
      for (const [index, view] of VIEWS.entries()) {
        const viewLabel = step(`#/${route} view ${view}`);
        if (index % 2 === 0) await page.click(`.segment[data-view="${view}"]`);
        else {
          // Keys 1-4 switch views too.
          await page.locator('.back-link').focus();
          await page.keyboard.press(String(index + 1));
        }
        await page.waitForSelector(`.detail-viewport[data-view="${view}"]`, { timeout: TIMEOUT });
        await waitStill(page);
        const pressed = await page.getAttribute(`.segment[data-view="${view}"]`, 'aria-pressed');
        if (pressed !== 'true') fail(`${viewLabel}: button not pressed`);
        await checkCanvas(page, viewLabel, `${device}--${name}--${view}--canvas.png`);
        await checkLabelsInside(page, viewLabel);
        console.log(`  -> ${await shot(page, device, `${name}--${view}`)}`);
      }
      const cotasLabel = step(`#/${route} cotas off`);
      await page.click('.segment[data-view="iso"]');
      await waitStill(page);
      await page.click('.check input');
      await waitStill(page);
      const shown = await page.evaluate(
        () => [...document.querySelectorAll('.cota-label')].filter((l) => l.offsetParent !== null).length,
      );
      if (shown) fail(`${cotasLabel}: ${shown} dimension labels still shown`);
      await checkCanvas(page, cotasLabel, `${device}--${name}--nocotas--canvas.png`);
      console.log(`  -> ${await shot(page, device, `${name}--nocotas`)}`);
      await page.click('.check input');
    }
  }

  // Unknown route.
  {
    const label = step('#/nao-existe');
    await go(page, '#/nao-existe/de-jeito-nenhum');
    if (await waitReady(page, label)) {
      const h1 = await page.textContent('h1');
      if (h1 !== 'Página não encontrada') fail(`${label}: h1 is "${h1}"`);
      console.log(`  -> ${await shot(page, device, 'not-found')}`);
      await afterPage(label);
    }
  }

  // Leaks: 10 navigations through component pages and the gallery.
  if (!mobile) {
    const label = step('leaks across 10 navigations');
    await go(page, '#/');
    await waitReady(page, label);
    const baseline = await page.evaluate(() => window.__leaks());
    const hashes = ['#/plumbing/pia-cozinha', '#/', '#/lighting/pendente', '#/electrical', '#/doors/porta-abrir'];
    for (let i = 0; i < 10; i++) {
      await go(page, hashes[i % hashes.length]);
      await waitReady(page, label);
      if (hashes[i % hashes.length].split('/').length === 3) await waitStill(page);
    }
    await go(page, '#/');
    await waitReady(page, label);
    await page.waitForTimeout(300); // context-lost events are dispatched asynchronously
    const end = await page.evaluate(() => window.__leaks());
    console.log(`  WebGL contexts ${baseline.contexts} -> ${end.contexts}, listeners ${baseline.listeners} -> ${end.listeners}`);
    if (end.contexts > Math.max(1, baseline.contexts)) fail(`${label}: ${end.contexts} live WebGL contexts on the gallery`);
    if (end.listeners > baseline.listeners) fail(`${label}: window/document listeners grew ${baseline.listeners} -> ${end.listeners}`);
  }

  await context.close();
}

async function thumbnailStress(browser) {
  const label = 'thumbnails (all entries)';
  console.log(label);
  const context = await browser.newContext(DEVICES.desktop);
  const page = await context.newPage();
  watch(page, () => label);
  await page.goto(`${ORIGIN}/?smoke#/not-a-folder`);
  await page.waitForFunction(() => window.__smoke !== undefined, null, { timeout: TIMEOUT });
  const result = await page.evaluate(() => window.__smoke.thumbnailStress(128));
  for (const f of result.failures) fail(`${label}: ${f}`);
  const maxGeometries = Math.max(...result.geometries);
  const lastGeometries = result.geometries.at(-1);
  const lastTextures = result.textures.at(-1);
  console.log(
    `  rendered ${result.rendered}, GPU geometries after each: max ${maxGeometries}, last ${lastGeometries}; textures last ${lastTextures}`,
  );
  // three.js keeps one shared lookup texture for MeshStandardMaterial; it must not grow.
  const firstTextures = result.textures[0];
  if (lastGeometries > 0 || lastTextures > firstTextures) {
    fail(`${label}: GPU resources left after rendering (${lastGeometries} geometries, textures ${firstTextures} -> ${lastTextures})`);
  }
  await context.close();
}

async function main() {
  await rm(outDir, { recursive: true, force: true });
  await mkdir(outDir, { recursive: true });

  if (process.argv.includes('--no-build')) {
    console.log('Using the existing dist/ (--no-build)');
  } else {
    console.log('Building...');
    await build({ root, logLevel: 'warn' });
  }

  const server = await preview({ root, logLevel: 'warn', preview: { port: PORT, strictPort: true, host: '127.0.0.1' } });
  const browser = await chromium.launch();
  try {
    await runDevice(browser, 'desktop');
    await runDevice(browser, 'mobile');
    await thumbnailStress(browser);
  } finally {
    await browser.close();
    await new Promise((resolve) => server.httpServer.close(resolve));
  }

  if (failures.length) {
    console.error(`\nSmoke test failed (${failures.length} problem${failures.length > 1 ? 's' : ''}).`);
    process.exit(1);
  }
  console.log(`\nSmoke test passed. Screenshots in ${outDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
