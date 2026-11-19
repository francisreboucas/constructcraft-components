// Formatting of numbers and labels in the page's language, and the text
// normalisation used by the gallery search.

import { DECIMAL_SEPARATOR, t } from './i18n';

/** A decimal with the language's separator (a comma in pt-BR), between `minDecimals` and `maxDecimals` places (trailing zeros trimmed). */
export function formatDecimal(value: number, maxDecimals = 3, minDecimals = 0): string {
  let text = value.toFixed(maxDecimals);
  if (text.includes('.')) {
    let [int, frac] = text.split('.') as [string, string];
    while (frac.length > minDecimals && frac.endsWith('0')) frac = frac.slice(0, -1);
    text = frac ? `${int}.${frac}` : int;
  }
  if (text === '-0') text = '0';
  return text.replace('.', DECIMAL_SEPARATOR);
}

/** A length in metres: up to 3 decimals, at least 2 (`0,60`, `1,205`). */
export function formatLength(metres: number): string {
  return formatDecimal(metres, 3, 2);
}

/** A parameter value formatted by its kind (`Length` when unknown). */
export function formatParamValue(value: number | undefined, kind = 'Length'): string {
  if (value === undefined || !Number.isFinite(value)) return '—';
  switch (kind) {
    case 'Length':
      return formatLength(value);
    case 'Angle':
      return `${formatDecimal(value, 1)}°`;
    case 'Boolean':
      return value ? t.common.yes : t.common.no;
    default:
      return formatDecimal(value, 3);
  }
}

/** "1 tipo" / "N tipos". */
export function typeCount(n: number): string {
  return t.common.typeCount(n);
}

/** Lowercase without diacritics, for case- and accent-insensitive matching. */
export function normalizeText(text: string): string {
  return text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();
}

export function deviceLabel(device: string): string {
  return t.devices[device] ?? device;
}

export function systemLabel(system: string): string {
  return t.systems[system] ?? system;
}
