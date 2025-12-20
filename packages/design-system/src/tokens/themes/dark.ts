/**
 * Dark Theme
 * 
 * Used by: Test Data Agent, eCommerce Domain Agent
 */

import { colors } from '../colors';

export const darkTheme = {
  name: 'dark',
  
  // Background
  bgPrimary: colors.darkBg.primary,
  bgSecondary: colors.darkBg.secondary,
  bgTertiary: colors.darkBg.tertiary,
  
  // Text
  textPrimary: colors.darkText.primary,
  textSecondary: colors.darkText.secondary,
  textTertiary: colors.darkText.tertiary,
  textInverse: colors.black,
  
  // Accent (customizable per agent)
  accent: colors.darkAccent.green,
  accentHover: '#22c55e',
  accentLight: 'rgba(74, 222, 128, 0.1)',
  
  // Borders
  border: 'rgba(148, 163, 184, 0.2)',
  borderStrong: 'rgba(148, 163, 184, 0.4)',
  
  // Status
  success: colors.success.dark,
  error: colors.error.dark,
  warning: colors.warning.dark,
  info: colors.info.dark,
  
  // Shadows
  shadowSm: '0 1px 2px rgba(0, 0, 0, 0.3)',
  shadowMd: '0 4px 6px rgba(0, 0, 0, 0.4)',
  shadowLg: '0 10px 15px rgba(0, 0, 0, 0.5)',
  
  // Typography
  fontFamily: "'Inter', 'SF Pro Display', -apple-system, sans-serif",
  fontMono: "'JetBrains Mono', 'Fira Code', monospace",
} as const;

// CSS Variables export
export const darkThemeCSSVariables = `
  :root {
    --bg-primary: ${darkTheme.bgPrimary};
    --bg-secondary: ${darkTheme.bgSecondary};
    --bg-tertiary: ${darkTheme.bgTertiary};
    
    --text-primary: ${darkTheme.textPrimary};
    --text-secondary: ${darkTheme.textSecondary};
    --text-tertiary: ${darkTheme.textTertiary};
    --text-inverse: ${darkTheme.textInverse};
    
    --accent: ${darkTheme.accent};
    --accent-hover: ${darkTheme.accentHover};
    --accent-light: ${darkTheme.accentLight};
    
    --border: ${darkTheme.border};
    --border-strong: ${darkTheme.borderStrong};
    
    --success: ${darkTheme.success};
    --error: ${darkTheme.error};
    --warning: ${darkTheme.warning};
    --info: ${darkTheme.info};
    
    --shadow-sm: ${darkTheme.shadowSm};
    --shadow-md: ${darkTheme.shadowMd};
    --shadow-lg: ${darkTheme.shadowLg};
    
    --font-family: ${darkTheme.fontFamily};
    --font-mono: ${darkTheme.fontMono};
  }
`;

export type DarkTheme = typeof darkTheme;
