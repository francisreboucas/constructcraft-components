// pt-BR formatting of numbers and labels, and the text normalisation used by
// the gallery search.

/** A decimal with a decimal comma, between `minDecimals` and `maxDecimals` places (trailing zeros trimmed). */
export function formatDecimal(value: number, maxDecimals = 3, minDecimals = 0): string {
  let text = value.toFixed(maxDecimals);
  if (text.includes('.')) {
    let [int, frac] = text.split('.') as [string, string];
    while (frac.length > minDecimals && frac.endsWith('0')) frac = frac.slice(0, -1);
    text = frac ? `${int}.${frac}` : int;
  }
  if (text === '-0') text = '0';
  return text.replace('.', ',');
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
      return value ? 'sim' : 'não';
    default:
      return formatDecimal(value, 3);
  }
}

/** "1 tipo" / "N tipos". */
export function typeCount(n: number): string {
  return n === 1 ? '1 tipo' : `${n} tipos`;
}

/** Lowercase without diacritics, for case- and accent-insensitive matching. */
export function normalizeText(text: string): string {
  return text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();
}

const DEVICE_LABELS: Record<string, string> = {
  Outlet: 'Tomada de uso geral',
  DedicatedOutlet: 'Tomada de uso específico',
  Switch: 'Interruptor',
  CeilingLight: 'Luminária de teto',
  WallLight: 'Luminária de parede',
  Panel: 'Quadro de distribuição',
};

export function deviceLabel(device: string): string {
  return DEVICE_LABELS[device] ?? device;
}

const SYSTEM_LABELS: Record<string, string> = {
  ColdWater: 'Água fria',
  HotWater: 'Água quente',
  Sanitary: 'Esgoto',
  Power: 'Elétrica',
};

export function systemLabel(system: string): string {
  return SYSTEM_LABELS[system] ?? system;
}
