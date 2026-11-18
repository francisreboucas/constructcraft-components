// Lazy gallery thumbnails.
//
// Cards register with a `ThumbnailLoader`; an IntersectionObserver tracks the
// ones near the viewport and the loader renders them one at a time through the
// shared thumbnail renderer, closest to the viewport first. A card that scrolls
// away before its turn is skipped (and picked up again when it comes back).
// Between renders the loader yields to the main thread, and it waits while the
// user is typing, so the search box stays responsive.
//
// Object URLs are cached per component id for the session and revoked only
// when the page unloads.

import { edgesForFolder, type CatalogEntry } from './catalog';
import { loadComponent } from './engine';
import { renderThumbnail } from './scene';

type ThumbState = 'pending' | 'ready' | 'failed';

const urls = new Map<string, string>();
const inflight = new Map<string, Promise<string | null>>();
let unloadHooked = false;

function hookUnload(): void {
  if (unloadHooked) return;
  unloadHooked = true;
  window.addEventListener('pagehide', (event) => {
    if (event.persisted) return;
    for (const url of urls.values()) URL.revokeObjectURL(url);
    urls.clear();
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

interface SchedulerLike {
  yield?: () => Promise<void>;
}

/** Let input events and rendering run before continuing. */
function yieldToMain(): Promise<void> {
  const scheduler = (globalThis as { scheduler?: SchedulerLike }).scheduler;
  if (scheduler?.yield) return scheduler.yield();
  return sleep(0);
}

/** The thumbnail of an entry as an object URL, or null when it cannot be drawn. Shared and cached. */
function produce(entry: CatalogEntry, sizePx: number): Promise<string | null> {
  const cached = urls.get(entry.id);
  if (cached) return Promise.resolve(cached);
  let promise = inflight.get(entry.id);
  if (promise) return promise;
  hookUnload();
  promise = (async () => {
    try {
      const component = await loadComponent(entry.file);
      await yieldToMain();
      const blob = await renderThumbnail(component, sizePx, { edges: edgesForFolder(entry.folder) });
      const url = URL.createObjectURL(blob);
      urls.set(entry.id, url);
      return url;
    } catch {
      return null;
    } finally {
      inflight.delete(entry.id);
    }
  })();
  inflight.set(entry.id, promise);
  return promise;
}

/** Pause after the last keystroke before rendering the next thumbnail, ms. */
const TYPING_PAUSE_MS = 250;

export class ThumbnailLoader {
  private readonly observer: IntersectionObserver;
  private readonly entries = new Map<HTMLElement, CatalogEntry>();
  private readonly near = new Set<HTMLElement>();
  private readonly sizePx: number;
  private running = false;
  private disposed = false;
  private lastInput = 0;

  constructor() {
    this.sizePx = Math.round(240 * Math.min(window.devicePixelRatio || 1, 2));
    this.observer = new IntersectionObserver(
      (records) => {
        for (const record of records) {
          const card = record.target as HTMLElement;
          if (record.isIntersecting) this.near.add(card);
          else this.near.delete(card);
        }
        void this.pump();
      },
      { rootMargin: '300px 0px' },
    );
  }

  /** Track a card. It needs a `.card-thumb` child, where the image goes. */
  observe(card: HTMLElement, entry: CatalogEntry): void {
    const url = urls.get(entry.id);
    if (url) {
      this.apply(card, url);
      return;
    }
    setState(card, 'pending');
    this.entries.set(card, entry);
    this.observer.observe(card);
  }

  /** Call on every keystroke in the search box: rendering waits until typing pauses. */
  noteInput(): void {
    this.lastInput = performance.now();
  }

  dispose(): void {
    this.disposed = true;
    this.observer.disconnect();
    this.entries.clear();
    this.near.clear();
  }

  /** The tracked card nearest the top of the viewport. */
  private next(): HTMLElement | null {
    let best: HTMLElement | null = null;
    let bestScore = Infinity;
    for (const card of this.near) {
      if (!card.isConnected) continue;
      const rect = card.getBoundingClientRect();
      const score = rect.bottom < 0 ? window.innerHeight - rect.bottom : Math.max(0, rect.top);
      if (score < bestScore) {
        bestScore = score;
        best = card;
      }
    }
    return best;
  }

  private async pump(): Promise<void> {
    if (this.running) return;
    this.running = true;
    try {
      for (;;) {
        const since = performance.now() - this.lastInput;
        if (since < TYPING_PAUSE_MS) await sleep(TYPING_PAUSE_MS - since);
        if (this.disposed) return;
        const card = this.next();
        if (!card) return;
        const entry = this.entries.get(card);
        this.near.delete(card);
        this.observer.unobserve(card);
        this.entries.delete(card);
        if (!entry) continue;
        const url = await produce(entry, this.sizePx);
        if (this.disposed) return;
        if (url) this.apply(card, url);
        else fail(card);
        await yieldToMain();
      }
    } finally {
      this.running = false;
    }
  }

  private apply(card: HTMLElement, url: string): void {
    const box = card.querySelector<HTMLElement>('.card-thumb');
    if (!box) return;
    const img = document.createElement('img');
    img.alt = '';
    img.decoding = 'async';
    img.src = url;
    box.append(img);
    img.decode().then(
      () => setState(card, 'ready'),
      () => {
        img.remove();
        fail(card);
      },
    );
  }
}

function setState(card: HTMLElement, state: ThumbState): void {
  card.dataset.thumb = state;
}

function fail(card: HTMLElement): void {
  setState(card, 'failed');
  const box = card.querySelector<HTMLElement>('.card-thumb');
  if (!box || box.querySelector('.card-thumb-fail')) return;
  const note = document.createElement('span');
  note.className = 'card-thumb-fail';
  note.textContent = 'Sem prévia';
  box.append(note);
}
