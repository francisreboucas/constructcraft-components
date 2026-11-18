// Smoke test: build, serve dist locally, open a few routes in headless
// Chromium and fail on console errors, page errors, external requests or a
// blank 3D view. Screenshots go to viewer/.smoke/.
//
//   npm run smoke

import { mkdir, rm, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { build, preview } from 'vite';

const root = fileURLToPath(new URL('..', import.meta.url));
const outDir = fileURLToPath(new URL('../.smoke/', import.meta.url));
const PORT = 4317;
const ORIGIN = `http://127.0.0.1:${PORT}`;
const TIMEOUT = 30_000;

const DETAIL_ROUTES = ['plumbing/pia-cozinha', 'lighting/pendente', 'planting/ipe-amarelo', 'doors/porta-abrir'];
const VIEW_ROUTE = 'plumbing/pia-cozinha';
const VIEWS = ['iso', 'front', 'top', 'side'];

const failures = [];
const fail = (message) => {
  failures.push(message);
  console.error(`  FAIL ${message}`);
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

/** Fraction of non-transparent pixels of each thumbnail <img> on the page. */
async function thumbnailCoverage(page) {
  return page.$$eval('.thumb-strip img', (imgs) =>
    imgs.map((img) => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
      let opaque = 0;
      for (let i = 3; i < data.length; i += 4) if (data[i] > 16) opaque++;
      return { alt: img.alt, coverage: opaque / (data.length / 4) };
    }),
  );
}

function watch(page, label) {
  page.on('console', (msg) => {
    if (msg.type() === 'error') fail(`${label}: console error: ${msg.text()}`);
  });
  page.on('pageerror', (error) => fail(`${label}: page error: ${error.message}`));
  page.on('request', (request) => {
    const url = request.url();
    if (!url.startsWith(ORIGIN) && !url.startsWith('data:') && !url.startsWith('blob:')) {
      fail(`${label}: external request to ${url}`);
    }
  });
  page.on('requestfailed', (request) => fail(`${label}: request failed: ${request.url()}`));
}

async function waitReady(page, label) {
  await page.waitForSelector('html[data-state="ready"], html[data-state="error"]', { timeout: TIMEOUT });
  const state = await page.getAttribute('html', 'data-state');
  if (state !== 'ready') {
    const message = await page.textContent('.error').catch(() => null);
    fail(`${label}: page state is ${state}${message ? ` (${message})` : ''}`);
    return false;
  }
  return true;
}

async function waitStill(page) {
  await page.waitForSelector('.detail-viewport[data-rendered="true"]:not([data-moving])', { timeout: TIMEOUT });
  // Two more frames so the label overlay has caught up with the last camera move.
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
}

async function checkCanvas(page, label, file) {
  const viewport = page.locator('.detail-viewport');
  const png = await viewport.screenshot();
  await writeFile(`${outDir}${file}`, png);
  const coverage = await inkCoverage(page, png, [0xe9, 0xee, 0xf2], 60);
  console.log(`  ${label}: ${(coverage * 100).toFixed(1)}% drawn -> .smoke/${file}`);
  if (coverage < 0.005) fail(`${label}: the 3D view looks blank (${(coverage * 100).toFixed(2)}% drawn)`);
}

async function main() {
  await rm(outDir, { recursive: true, force: true });
  await mkdir(outDir, { recursive: true });

  console.log('Building...');
  await build({ root, logLevel: 'warn' });

  const server = await preview({ root, logLevel: 'warn', preview: { port: PORT, strictPort: true, host: '127.0.0.1' } });
  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });

    // Home: links and the thumbnail strip.
    {
      const label = '#/';
      console.log(label);
      const page = await context.newPage();
      watch(page, label);
      await page.goto(`${ORIGIN}/#/`);
      if (await waitReady(page, label)) {
        const links = await page.locator('main li a').count();
        if (links !== 74) fail(`${label}: expected 74 component links, found ${links}`);
        const thumbs = await thumbnailCoverage(page);
        if (thumbs.length !== 12) fail(`${label}: expected 12 thumbnails, found ${thumbs.length}`);
        for (const t of thumbs) if (t.coverage < 0.01) fail(`${label}: thumbnail "${t.alt}" looks blank`);
        await page.screenshot({ path: `${outDir}home.png`, fullPage: true });
        console.log(`  ${links} links, ${thumbs.length} thumbnails -> .smoke/home.png`);
      }
      await page.close();
    }

    // Detail pages.
    for (const route of DETAIL_ROUTES) {
      const label = `#/${route}`;
      console.log(label);
      const page = await context.newPage();
      watch(page, label);
      await page.goto(`${ORIGIN}/#/${route}`);
      if (await waitReady(page, label)) {
        await waitStill(page);
        const name = route.replace('/', '--');
        await checkCanvas(page, label, `${name}.png`);
        await page.screenshot({ path: `${outDir}${name}--page.png` });

        if (route === VIEW_ROUTE) {
          for (const view of VIEWS) {
            await page.click(`.detail-bar button[data-view="${view}"]`);
            await page.waitForSelector(`.detail-viewport[data-view="${view}"]`, { timeout: TIMEOUT });
            await waitStill(page);
            await checkCanvas(page, `${label} view ${view}`, `${name}--${view}.png`);
          }
        }
      }
      await page.close();
    }

    // Thumbnail renderer: every catalog entry through the one shared renderer, watching GPU memory.
    {
      const label = 'thumbnails (all entries)';
      console.log(label);
      const page = await context.newPage();
      watch(page, label);
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
      await page.close();
    }

    await context.close();
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
