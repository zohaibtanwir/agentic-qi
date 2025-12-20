/**
 * Macy's Theme
 * 
 * Used by: Test Cases Agent
 * 
 * Based on Macy's brand guidelines:
 * - White background
 * - Macy's Red (#E21A2C) as primary accent
 * - Arial/Avenir typography
 */

import { colors } from '../colors';

export const macysTheme = {
  name: 'macys',
  
  // Background
  bgPrimary: colors.white,
  bgSecondary: colors.gray[50],
  bgTertiary: colors.gray[100],
  
  // Text
  textPrimary: colors.black,
  textSecondary: colors.gray[500],
  textTertiary: colors.gray[400],
  textInverse: colors.white,
  
  // Accent (Macy's Red)
  accent: colors.macysRed,
  accentHover: colors.macysRedDark,
  accentLight: colors.macysRedLight,
  
  // Borders
  border: colors.gray[200],
  borderStrong: colors.gray[300],
  
  // Status
  success: colors.success.light,
  error: colors.macysRed,  // Use brand red for errors
  warning: colors.warning.light,
  info: colors.info.light,
  
  // Shadows
  shadowSm: '0 1px 2px rgba(0, 0, 0, 0.05)',
  shadowMd: '0 4px 6px rgba(0, 0, 0, 0.07)',
  shadowLg: '0 10px 15px rgba(0, 0, 0, 0.1)',
  
  // Typography
  fontFamily: "'Arial', 'Helvetica', sans-serif",
  fontDisplay: "'Avenir', 'Arial', sans-serif",
  fontMono: "'Monaco', 'Consolas', monospace",
  
  // Macy's specific
  logo: 'https://assets.macysassets.com/app/navigation-wgl/static/images/logo.svg',
} as const;

// CSS Variables export
export const macysThemeCSSVariables = `
  :root {
    --bg-primary: ${macysTheme.bgPrimary};
    --bg-secondary: ${macysTheme.bgSecondary};
    --bg-tertiary: ${macysTheme.bgTertiary};
    
    --text-primary: ${macysTheme.textPrimary};
    --text-secondary: ${macysTheme.textSecondary};
    --text-tertiary: ${macysTheme.textTertiary};
    --text-inverse: ${macysTheme.textInverse};
    
    --accent: ${macysTheme.accent};
    --accent-hover: ${macysTheme.accentHover};
    --accent-light: ${macysTheme.accentLight};
    
    --border: ${macysTheme.border};
    --border-strong: ${macysTheme.borderStrong};
    
    --success: ${macysTheme.success};
    --error: ${macysTheme.error};
    --warning: ${macysTheme.warning};
    --info: ${macysTheme.info};
    
    --shadow-sm: ${macysTheme.shadowSm};
    --shadow-md: ${macysTheme.shadowMd};
    --shadow-lg: ${macysTheme.shadowLg};
    
    --font-family: ${macysTheme.fontFamily};
    --font-display: ${macysTheme.fontDisplay};
    --font-mono: ${macysTheme.fontMono};
  }
`;

export type MacysTheme = typeof macysTheme;
