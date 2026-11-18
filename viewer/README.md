# ConstructCraft Components viewer

A static web viewer for this component library: a gallery of every component with search, and a page per component with its 3D model (dimensions, four views), its types, MEP data, connectors and a download link. It runs entirely in the browser: the `.ccomp` files are parsed and meshed by the ConstructCraft geometry engine compiled to WebAssembly, and drawn with three.js. It is published to GitHub Pages at <https://francisreboucas.github.io/constructcraft-components/> by the [`Viewer`](../.github/workflows/pages.yml) workflow on every push to `main`.

## Requirements

- Node.js 24 and npm.
- For `npm run smoke`: Playwright's Chromium (`npx playwright install chromium`, plus `--with-deps` on a fresh Linux machine).
- Rust is **not** needed unless you change the geometry core (see below).

## Commands

Run them inside `viewer/`:

```sh
npm ci              # install the exact dependencies
npm run dev         # dev server with hot reload
npm run build       # static site in dist/
npm run typecheck   # TypeScript, app and build scripts
npm run smoke       # build, serve dist/ and check every page in headless Chromium
```

`npm run smoke -- --no-build` tests the `dist/` you already built. Screenshots of each page at desktop and mobile size go to `.smoke/`.

The built site uses relative URLs only (`base: './'`), so `dist/` works from any subpath, such as the GitHub Pages project URL.

## Library files

The viewer reads the library from the repository root, without a copy in git: [`build/library-plugin.ts`](build/library-plugin.ts) serves `catalog.json` and `components/<folder>/<name>.ccomp` under `library/` in the dev server, and copies the same files to `dist/library/` on build. The app fetches them relative to the page (`library/catalog.json`, `library/components/...`), and the download buttons link to those copies. New components show up after the next build, with nothing to change here.

## The geometry core

[`wasm/`](wasm) is a small Rust crate that wraps the engine's `cc_core` and `cc_geom` crates (without Lua) and exposes them to JavaScript with `wasm-bindgen`. Its build output, [`wasm-pkg/`](wasm-pkg), is committed, so the site builds with Node alone and CI never compiles Rust. Rebuild it by hand only when the crate or the engine changes, and commit the new `wasm-pkg/`.

You need `cargo` with the `wasm32-unknown-unknown` target and the wasm-bindgen CLI at exactly the version pinned in [`wasm/Cargo.toml`](wasm/Cargo.toml), currently 0.2.130:

```sh
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli --version 0.2.130

# from the repository root
CCAD_SRC=/path/to/constructcraft node viewer/wasm/build.mjs
node viewer/wasm/test/load-all.mjs   # load every component through the new build
```

`CCAD_SRC` names a local git checkout of the [ConstructCraft engine](https://github.com/francisreboucas/constructcraft); the build patches the engine dependencies to it. Without it, cargo fetches them from GitHub. The crate currently depends on the engine branch `feat/geom-without-lua`, which builds the geometry without the Lua runtime; it will be switched to a release tag once that change ships.

## Known limits

- The 3D model shows the first type of each component; the other types are listed with their values.
- Pieces scripted in Lua are not rendered (the page says how many were left out).
- 3D only: no plan or elevation drawings.

## License

The viewer code in `viewer/` is licensed under the [GNU General Public License v3.0 or later](LICENSE), because it links the GPL-3.0 ConstructCraft engine. The components it shows stay under [CC BY 4.0](../LICENSE).
