// The interface language: Portuguese (the library's own language) or English.
//
// The choice comes from, in order: `?lang=pt|en` in the URL, the choice saved
// by the language switch, and the browser's languages (Portuguese when any of
// them is, else English). It is fixed for the life of the page: switching
// saves the choice and reloads.
//
// What comes from the `.ccomp` files stays as written there, in Portuguese:
// type names and parameter names are what ConstructCraft commands take, and
// the type descriptions are part of the file. Component names have English
// display names in i18n/components-en.ts.

import { en } from './i18n/en';
import { pt, type Strings } from './i18n/pt';

export type Lang = 'pt' | 'en';

export const LANGS: readonly { id: Lang; short: string; name: string }[] = [
  { id: 'pt', short: 'PT', name: 'Português' },
  { id: 'en', short: 'EN', name: 'English' },
];

const STORAGE_KEY = 'crafthouse-lang';

function asLang(value: string | null | undefined): Lang | null {
  const code = value?.toLowerCase().split('-')[0];
  return code === 'pt' || code === 'en' ? code : null;
}

function stored(): Lang | null {
  try {
    return asLang(localStorage.getItem(STORAGE_KEY));
  } catch {
    // Storage blocked: the browser's language decides.
    return null;
  }
}

function detect(): Lang {
  const fromUrl = asLang(new URLSearchParams(location.search).get('lang'));
  if (fromUrl) return fromUrl;
  const saved = stored();
  if (saved) return saved;
  const languages = navigator.languages?.length ? navigator.languages : [navigator.language];
  return languages.some((l) => asLang(l) === 'pt') ? 'pt' : 'en';
}

/** The language of this page load. */
export const lang: Lang = detect();

/** The interface strings in the page's language. */
export const t: Strings = lang === 'en' ? en : pt;

/** Decimal separator of the page's language. */
export const DECIMAL_SEPARATOR = lang === 'en' ? '.' : ',';

/** BCP 47 tag of the page's language, for `<html lang>` and `Intl`. */
export const LOCALE = lang === 'en' ? 'en' : 'pt-BR';

/** Save the choice and reload the page in that language, on the same route. */
export function setLang(next: Lang): void {
  if (next === lang) return;
  try {
    localStorage.setItem(STORAGE_KEY, next);
  } catch {
    // Storage blocked: the URL parameter below still carries the choice.
  }
  const url = new URL(location.href);
  // A `?lang=` in the URL would win over the saved choice; keep it only when storage failed.
  if (stored() === next) url.searchParams.delete('lang');
  else url.searchParams.set('lang', next);
  if (url.href === location.href) location.reload();
  else location.replace(url.href);
}

/** Apply the language to the document (`<html lang>`, the description). */
export function applyDocumentLanguage(): void {
  document.documentElement.lang = LOCALE;
  document.querySelector('meta[name="description"]')?.setAttribute('content', t.meta.description);
}
