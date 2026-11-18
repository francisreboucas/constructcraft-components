#!/usr/bin/env node
// Builds the viewer's geometry core (this crate) to WebAssembly and writes the
// JavaScript bindings to ../wasm-pkg with the wasm-bindgen CLI.
//
//   node viewer/wasm/build.mjs
//   CCAD_SRC=/path/to/constructcraft node viewer/wasm/build.mjs
//
// CCAD_SRC names a local git checkout of the engine (the workspace root, with
// crates/cc_core and crates/cc_geom): the engine's git dependencies are then
// patched to its working tree, and the branch they name is fetched from that
// checkout instead of GitHub, so it need not be pushed.
//
// Needs cargo with the wasm32-unknown-unknown target and the wasm-bindgen CLI
// of the exact version in Cargo.lock (cargo install wasm-bindgen-cli --version <it>).

import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ENGINE_GIT = 'https://github.com/francisreboucas/constructcraft';
const ENGINE_CRATES = ['cc_core', 'cc_geom'];
const CRATE = 'ccomp_viewer';
const TARGET = 'wasm32-unknown-unknown';

const here = dirname(fileURLToPath(import.meta.url));
const out = resolve(here, '..', 'wasm-pkg');

function fail(message) {
  console.error(`build.mjs: ${message}`);
  process.exit(1);
}

function run(command, args, env = process.env) {
  console.log(`> ${command} ${args.join(' ')}`);
  const r = spawnSync(command, args, { cwd: here, stdio: 'inherit', env });
  if (r.error) fail(`could not run ${command}: ${r.error.message}`);
  if (r.status !== 0) fail(`${command} failed (exit code ${r.status})`);
}

/** The version of wasm-bindgen in Cargo.lock, or null without a lock file. */
function lockedBindgen() {
  const lock = join(here, 'Cargo.lock');
  if (!existsSync(lock)) return null;
  const text = readFileSync(lock, 'utf8').replace(/\r\n/g, '\n');
  const m = text.match(/\[\[package\]\]\nname = "wasm-bindgen"\nversion = "([^"]+)"/);
  if (!m) fail('Cargo.lock has no wasm-bindgen package');
  return m[1];
}

/** Fail unless the wasm-bindgen CLI is the version the crate is locked to. */
function checkBindgen(locked) {
  const r = spawnSync('wasm-bindgen', ['--version'], { encoding: 'utf8' });
  if (r.error || r.status !== 0) {
    fail(`the wasm-bindgen CLI was not found; install it with: cargo install wasm-bindgen-cli --version ${locked}`);
  }
  const cli = (r.stdout.match(/(\d+\.\d+\.\d+\S*)/) || [])[1];
  if (cli !== locked) {
    fail(
      `wasm-bindgen CLI ${cli ?? r.stdout.trim()} differs from the wasm-bindgen ${locked} in Cargo.lock; ` +
        `install the matching one with: cargo install wasm-bindgen-cli --version ${locked}`,
    );
  }
}

// Fail fast when the lock file already says which wasm-bindgen it needs.
const before = lockedBindgen();
if (before) checkBindgen(before);

const cargo = ['build', '--release', '--target', TARGET];
const env = { ...process.env };
const src = process.env.CCAD_SRC;
if (src) {
  const root = resolve(src).replace(/\\/g, '/');
  for (const crate of ENGINE_CRATES) {
    const dir = `${root}/crates/${crate}`;
    if (!existsSync(join(dir, 'Cargo.toml'))) fail(`CCAD_SRC=${src} has no crates/${crate}/Cargo.toml`);
    cargo.push('--config', `patch."${ENGINE_GIT}".${crate}.path=${JSON.stringify(dir)}`);
  }
  // Cargo still resolves the patched git dependency's branch, so it fetches
  // the engine's repository from the checkout instead of GitHub (where the
  // branch may not be yet): git, run by cargo, reads the URL rewrite from the
  // environment.
  if (!existsSync(join(root, '.git'))) fail(`CCAD_SRC=${src} is not a git checkout of the engine`);
  const n = Number.parseInt(env.GIT_CONFIG_COUNT ?? '0', 10) || 0;
  env[`GIT_CONFIG_KEY_${n}`] = `url.file:///${root.replace(/^\/+/, '')}.insteadOf`;
  env[`GIT_CONFIG_VALUE_${n}`] = ENGINE_GIT;
  env.GIT_CONFIG_COUNT = String(n + 1);
  cargo.push('--config', 'net.git-fetch-with-cli=true');
  console.log(`Engine crates from ${root}`);
}
run('cargo', cargo, env);

const locked = lockedBindgen();
if (!locked) fail('cargo wrote no Cargo.lock');
checkBindgen(locked);

const wasm = join(here, 'target', TARGET, 'release', `${CRATE}.wasm`);
if (!existsSync(wasm)) fail(`cargo built no ${wasm}`);
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });
run('wasm-bindgen', [
  '--target',
  'web',
  '--out-dir',
  out,
  '--remove-name-section',
  '--remove-producers-section',
  wasm,
]);

for (const name of readdirSync(out).sort()) {
  console.log(`${String(statSync(join(out, name)).size).padStart(9)}  ${join('viewer', 'wasm-pkg', name)}`);
}
