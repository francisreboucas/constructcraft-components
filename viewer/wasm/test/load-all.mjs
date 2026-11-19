#!/usr/bin/env node
// Loads every components/**/*.ccomp (and any .ccomp paths given as
// arguments) through the built viewer/wasm-pkg and checks the result:
//
//   node viewer/wasm/test/load-all.mjs [extra.ccomp ...]
//
// Each file must load without throwing, with no piece errors, at least one
// part, whole finite triangles with unit normals wound counter-clockwise
// about them, and a box of some size in every direction that holds the
// triangles. A few files are also checked against values worked out by hand.
// One line per file; the exit code is 1 when any check fails.

import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, '..', '..', '..');
const pkg = resolve(here, '..', '..', 'wasm-pkg');

const wasm = await import(pathToFileURL(join(pkg, 'ccomp_viewer.js')).href);
wasm.initSync({ module: readFileSync(join(pkg, 'ccomp_viewer_bg.wasm')) });

function ccompFiles(dir) {
  const out = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...ccompFiles(path));
    else if (entry.isFile() && entry.name.toLowerCase().endsWith('.ccomp')) out.push(path);
  }
  return out.sort();
}

const near = (a, b, tol) => Math.abs(a - b) <= tol;
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const vertex = (arr, i) => [arr[3 * i], arr[3 * i + 1], arr[3 * i + 2]];

/** Volume enclosed by a part's triangles (positive when they face outwards). */
function volume(part) {
  const p = part.positions;
  let v = 0;
  for (let t = 0; t < p.length / 9; t++) {
    const [a, b, c] = [vertex(p, 3 * t), vertex(p, 3 * t + 1), vertex(p, 3 * t + 2)];
    v += dot(a, cross(b, c)) / 6;
  }
  return v;
}

/** The volume of a prism over a regular n-gon of circumradius r and height h. */
const ngonPrism = (n, r, h) => (n / 2) * r * r * Math.sin((2 * Math.PI) / n) * h;
/** A frustum between regular n-gons of circumradii r1 and r2, h apart. */
const ngonFrustum = (n, r1, r2, h) => ((h / 3) * (n / 2) * Math.sin((2 * Math.PI) / n)) * (r1 * r1 + r1 * r2 + r2 * r2);

// Values worked out by hand from the files' parameters (first type). Cylinders
// have 24 sides, revolutions 48 per turn; boxes are in meters.
const KNOWN = {
  // 0.45 wide, 0.5 deep, 0.9 tall, centered on the origin in plan.
  'components/furniture/cadeira.ccomp': {
    bounds: { min: [-0.225, -0.25, 0], max: [0.225, 0.25, 0.9] },
  },
  // A Ø0.9 top 0.03 thick at 0.72, a Ø0.1 column from 0.03 to 0.72 and a Ø0.45 base 0.03 thick.
  'components/furniture/mesa-redonda.ccomp': {
    bounds: { min: [-0.45, -0.45, 0], max: [0.45, 0.45, 0.75] },
    volumes: { Tampo: ngonPrism(24, 0.45, 0.03), Coluna: ngonPrism(24, 0.05, 0.69), Base: ngonPrism(24, 0.225, 0.03) },
  },
  // The pot: the profile (0,0) (0.152,0) (0.2,0.4) (0,0.4) turned a full turn about u = 0.
  'components/planting/vaso-planta-40.ccomp': {
    partBounds: { Vaso: { min: [-0.2, -0.2, 0], max: [0.2, 0.2, 0.4] } },
    volumes: { Vaso: ngonFrustum(48, 0.152, 0.2, 0.4), Terra: ngonPrism(24, 0.18, 0.01) },
  },
};

function check(path) {
  const problems = [];
  const notes = [];
  let c;
  try {
    c = wasm.load_component(readFileSync(path, 'utf8'));
  } catch (e) {
    return { problems: [`throws: ${e?.message ?? e}`], notes, summary: '' };
  }
  if (c.errors.length) problems.push(`piece errors: ${c.errors.map((e) => `${e.name}: ${e.message}`).join('; ')}`);
  if (!(c.parts.length > 0)) problems.push('no parts');
  // Every other type resolves too, with as many parts and no more piece errors than the first.
  for (let t = 1; t < c.types.length; t++) {
    try {
      const other = wasm.load_component(readFileSync(path, 'utf8'), t);
      if (other.type_index !== t) problems.push(`type ${t}: shows type ${other.type_index}`);
      if (!(other.parts.length > 0)) problems.push(`type ${t} ("${other.types[t].name}"): no parts`);
      if (other.errors.length > c.errors.length) {
        problems.push(`type ${t} ("${other.types[t].name}"): ${other.errors.map((e) => `${e.name}: ${e.message}`).join('; ')}`);
      }
    } catch (e) {
      problems.push(`type ${t}: throws: ${e?.message ?? e}`);
    }
  }
  let triangles = 0;
  const lo = [Infinity, Infinity, Infinity];
  const hi = [-Infinity, -Infinity, -Infinity];
  for (const part of c.parts) {
    const { positions: p, normals: n } = part;
    const tag = `part "${part.name}"`;
    if (!(p instanceof Float32Array) || !(n instanceof Float32Array)) {
      problems.push(`${tag}: positions and normals must be Float32Arrays`);
      continue;
    }
    if (p.length === 0 || p.length % 9 !== 0) problems.push(`${tag}: ${p.length} positions is not whole triangles`);
    if (n.length !== p.length) problems.push(`${tag}: ${n.length} normals for ${p.length} positions`);
    if (!p.every(Number.isFinite) || !n.every(Number.isFinite)) problems.push(`${tag}: non-finite numbers`);
    if (part.color.length !== 3 || !part.color.every((v) => Number.isInteger(v) && v >= 0 && v <= 255)) {
      problems.push(`${tag}: bad color ${part.color}`);
    }
    if (!(part.transparency >= 0 && part.transparency <= 1)) problems.push(`${tag}: bad transparency`);
    const e = part.edges;
    if (!(e instanceof Float32Array) || e.length % 6 !== 0 || !e.every(Number.isFinite)) {
      problems.push(`${tag}: edges must be a Float32Array of whole finite segments`);
    }
    let notUnit = 0;
    let wound = 0;
    for (let i = 0; i < n.length / 3; i++) {
      if (!near(Math.hypot(...vertex(n, i)), 1, 1e-3)) notUnit++;
    }
    for (let t = 0; t < p.length / 9; t++) {
      const [a, b, cc] = [vertex(p, 3 * t), vertex(p, 3 * t + 1), vertex(p, 3 * t + 2)];
      const g = cross(sub(b, a), sub(cc, a));
      if (Math.hypot(...g) < 1e-12) continue;
      const shade = [0, 1, 2].map((k) => n[9 * t + k] + n[9 * t + 3 + k] + n[9 * t + 6 + k]);
      if (dot(g, shade) <= 0) wound++;
    }
    if (notUnit) problems.push(`${tag}: ${notUnit} normals are not unit length`);
    if (wound) problems.push(`${tag}: ${wound} triangles wound against their normals`);
    // A closed piece wound outwards encloses a positive volume.
    if (!(volume(part) > 0)) notes.push(`${tag} encloses volume ${volume(part).toExponential(3)} (inside out or open)`);
    triangles += p.length / 9;
    for (let i = 0; i < p.length; i++) {
      lo[i % 3] = Math.min(lo[i % 3], p[i]);
      hi[i % 3] = Math.max(hi[i % 3], p[i]);
    }
  }
  const b = c.bounds;
  if (!b) problems.push('no bounds');
  else {
    const size = [0, 1, 2].map((k) => b.max[k] - b.min[k]);
    if (!size.every((s) => Number.isFinite(s) && s > 0)) problems.push(`degenerate bounds ${JSON.stringify(b)}`);
    if (c.parts.length && ![0, 1, 2].every((k) => near(b.min[k], lo[k], 1e-6) && near(b.max[k], hi[k], 1e-6))) {
      problems.push(`bounds ${JSON.stringify(b)} are not the triangles' box`);
    }
  }
  const known = KNOWN[relative(repo, path).replace(/\\/g, '/')];
  if (known) problems.push(...againstKnown(c, known));
  const size = b ? [0, 1, 2].map((k) => (b.max[k] - b.min[k]).toFixed(3)).join(' x ') : '-';
  return {
    problems,
    notes,
    summary: `${c.kind.padEnd(10)} parts ${String(c.parts.length).padStart(3)}  triangles ${String(triangles).padStart(6)}  size ${size} m${known ? '  (checked by hand)' : ''}`,
  };
}

function againstKnown(c, known) {
  const problems = [];
  const sameBox = (got, want, what) => {
    if (!got || ![0, 1, 2].every((k) => near(got.min[k], want.min[k], 1e-6) && near(got.max[k], want.max[k], 1e-6))) {
      problems.push(`${what} ${JSON.stringify(got)}, expected ${JSON.stringify(want)}`);
    }
  };
  if (known.bounds) sameBox(c.bounds, known.bounds, 'bounds');
  for (const [name, want] of Object.entries(known.partBounds ?? {})) {
    const part = c.parts.find((p) => p.name === name);
    if (!part) {
      problems.push(`no part "${name}"`);
      continue;
    }
    const p = part.positions;
    const box = { min: [0, 1, 2].map((k) => Math.min(...p.filter((_, i) => i % 3 === k))), max: [0, 1, 2].map((k) => Math.max(...p.filter((_, i) => i % 3 === k))) };
    sameBox(box, want, `part "${name}" box`);
  }
  for (const [name, want] of Object.entries(known.volumes ?? {})) {
    const parts = c.parts.filter((p) => p.name === name);
    const got = parts.reduce((v, p) => v + volume(p), 0);
    if (!parts.length || !near(got, want, 1e-6 + 1e-5 * want)) {
      problems.push(`part "${name}" volume ${got.toFixed(7)}, expected ${want.toFixed(7)}`);
    }
  }
  return problems;
}

const files = [...ccompFiles(join(repo, 'components')), ...process.argv.slice(2).map((p) => resolve(p))];
let failed = 0;
let noted = 0;
for (const path of files) {
  const name = relative(repo, path).replace(/\\/g, '/');
  const { problems, notes, summary } = check(path);
  console.log(`${problems.length ? 'FAIL' : 'ok  '} ${name.padEnd(50)} ${summary}`);
  for (const p of problems) console.log(`       ${p}`);
  for (const n of notes) console.log(`       note: ${n}`);
  if (problems.length) failed++;
  if (notes.length) noted++;
}
console.log(`\n${files.length} files: ${files.length - failed} passed, ${failed} failed; ${noted} with notes`);
process.exit(failed ? 1 : 0);
