// Scene colours derived from the design tokens (see src/theme.ts).

import { Color } from 'three';
import { theme } from '../theme';

export interface ScenePalette {
  paper: Color;
  ink: Color;
  inkSoft: Color;
  rule: Color;
  accent: Color;
  /** CSS strings, for HTML overlays. */
  css: { paper: string; ink: string; accent: string; dataFont: string };
}

let cached: ScenePalette | null = null;

export function scenePalette(): ScenePalette {
  if (cached) return cached;
  const t = theme();
  cached = {
    paper: new Color(t.colors.paper),
    ink: new Color(t.colors.ink),
    inkSoft: new Color(t.colors.inkSoft),
    rule: new Color(t.colors.rule),
    accent: new Color(t.colors.accent),
    css: { paper: t.colors.paper, ink: t.colors.ink, accent: t.colors.accent, dataFont: t.fonts.data },
  };
  return cached;
}

/** Opacity of the feature edges drawn over the parts. */
export const EDGE_OPACITY = 0.35;
