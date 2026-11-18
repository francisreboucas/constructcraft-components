// Colours for the 3D scene, read once from the CSS custom properties in
// styles/tokens.css so the page and the scene share one source of truth.

export interface ThemeColors {
  paper: string;
  paperRaised: string;
  ink: string;
  inkSoft: string;
  rule: string;
  accent: string;
}

export interface ThemeFonts {
  display: string;
  body: string;
  data: string;
}

export interface Theme {
  colors: ThemeColors;
  fonts: ThemeFonts;
}

let cached: Theme | null = null;

function readVar(style: CSSStyleDeclaration, name: string): string {
  const value = style.getPropertyValue(name).trim();
  if (!value) {
    throw new Error(`Design token ${name} is not defined; is styles/tokens.css loaded?`);
  }
  return value;
}

/** The design tokens the scene needs. Requires styles/tokens.css to be loaded. */
export function theme(): Theme {
  if (cached) return cached;
  const style = getComputedStyle(document.documentElement);
  cached = {
    colors: {
      paper: readVar(style, '--paper'),
      paperRaised: readVar(style, '--paper-raised'),
      ink: readVar(style, '--ink'),
      inkSoft: readVar(style, '--ink-soft'),
      rule: readVar(style, '--rule'),
      accent: readVar(style, '--accent'),
    },
    fonts: {
      display: readVar(style, '--font-display'),
      body: readVar(style, '--font-body'),
      data: readVar(style, '--font-data'),
    },
  };
  return cached;
}
