import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import { libraryPlugin } from './build/library-plugin.ts';

const repoRoot = fileURLToPath(new URL('..', import.meta.url));

export default defineConfig({
  // Relative asset URLs so the site works under a GitHub Pages subpath.
  base: './',
  plugins: [libraryPlugin({ repoRoot })],
  build: {
    target: 'es2022',
    chunkSizeWarningLimit: 800,
  },
});
