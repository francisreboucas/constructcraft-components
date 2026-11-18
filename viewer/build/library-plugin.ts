// Serves the component library (catalog.json and components/**/*.ccomp from the
// repository root) under `library/` in dev, and copies the same files into
// `dist/library/` on build, so nothing is duplicated in git.

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, posix, resolve } from 'node:path';
import type { Plugin } from 'vite';

const URL_PREFIX = '/library/';
const ALLOWED = /^(catalog\.json|components\/[a-z0-9-]+\/[a-z0-9-]+\.ccomp)$/;

function contentType(path: string): string {
  return path.endsWith('.json') ? 'application/json; charset=utf-8' : 'text/plain; charset=utf-8';
}

/** Every library file, as paths relative to the repository root with `/` separators. */
function listLibraryFiles(repoRoot: string): string[] {
  const files = ['catalog.json'];
  const componentsDir = join(repoRoot, 'components');
  for (const folder of readdirSync(componentsDir).sort()) {
    const folderPath = join(componentsDir, folder);
    if (!statSync(folderPath).isDirectory()) continue;
    for (const name of readdirSync(folderPath).sort()) {
      const rel = posix.join('components', folder, name);
      if (ALLOWED.test(rel)) files.push(rel);
    }
  }
  return files;
}

export function libraryPlugin(options: { repoRoot: string }): Plugin {
  const repoRoot = resolve(options.repoRoot);
  return {
    name: 'ccomp-library',

    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url ?? '';
        if (!url.startsWith(URL_PREFIX)) return next();
        let rel: string;
        try {
          rel = decodeURIComponent(url.slice(URL_PREFIX.length).split(/[?#]/)[0] ?? '');
        } catch {
          rel = '';
        }
        if (!ALLOWED.test(rel)) {
          res.statusCode = 404;
          res.end('Not found');
          return;
        }
        let body: Buffer;
        try {
          body = readFileSync(join(repoRoot, rel));
        } catch {
          res.statusCode = 404;
          res.end('Not found');
          return;
        }
        res.setHeader('Content-Type', contentType(rel));
        res.setHeader('Cache-Control', 'no-cache');
        res.end(body);
      });
    },

    generateBundle() {
      for (const rel of listLibraryFiles(repoRoot)) {
        this.emitFile({
          type: 'asset',
          fileName: `library/${rel}`,
          source: readFileSync(join(repoRoot, rel)),
        });
      }
    },
  };
}
