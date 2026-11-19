// Serves the component library (catalog.json, components/**/*.ccomp and the
// pre-rendered thumbnails/**/*.png from the repository root) under `library/`
// in dev, and copies the same files into `dist/library/` on build, so nothing
// is duplicated in git. The thumbnails are optional: thumbnails/ may be absent,
// and its manifest.json is bookkeeping that is neither served nor copied.

import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, posix, resolve } from 'node:path';
import type { Plugin } from 'vite';

const URL_PREFIX = '/library/';
const ALLOWED =
  /^(catalog\.json|components\/[a-z0-9-]+\/[a-z0-9-]+\.ccomp|thumbnails\/[a-z0-9-]+\/[a-z0-9-]+\.png)$/;

function contentType(path: string): string {
  if (path.endsWith('.json')) return 'application/json; charset=utf-8';
  if (path.endsWith('.png')) return 'image/png';
  return 'text/plain; charset=utf-8';
}

/** The allowed files in `<dir>/<folder>/*`, as paths relative to the repository root. */
function listFolderFiles(repoRoot: string, dir: string): string[] {
  const files: string[] = [];
  const dirPath = join(repoRoot, dir);
  for (const folder of readdirSync(dirPath).sort()) {
    const folderPath = join(dirPath, folder);
    if (!statSync(folderPath).isDirectory()) continue;
    for (const name of readdirSync(folderPath).sort()) {
      const rel = posix.join(dir, folder, name);
      if (ALLOWED.test(rel)) files.push(rel);
    }
  }
  return files;
}

/** Every library file, as paths relative to the repository root with `/` separators. */
function listLibraryFiles(repoRoot: string): string[] {
  const files = ['catalog.json', ...listFolderFiles(repoRoot, 'components')];
  if (existsSync(join(repoRoot, 'thumbnails'))) files.push(...listFolderFiles(repoRoot, 'thumbnails'));
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
