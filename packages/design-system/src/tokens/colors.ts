/**
 * QA Platform Color Tokens
 * 
 * Shared color definitions used across all agents.
 * Import specific themes from ./themes/ directory.
 */

export const colors = {
  // Neutral palette
  white: '#FFFFFF',
  black: '#000000',
  
  // Gray scale
  gray: {
    50: '#F8F8F8',
    100: '#F0F0F0',
    200: '#E5E5E5',
    300: '#CCCCCC',
    400: '#999999',
    500: '#666666',
    600: '#4A4A4A',
    700: '#333333',
    800: '#1A1A1A',
    900: '#0F0F0F',
  },
  
  // Brand colors
  macysRed: '#E21A2C',
  macysRedDark: '#B91425',
  macysRedLight: '#FCECED',
  
  // Status colors
  success: {
    light: '#22C55E',
    dark: '#4ADE80',
  },
  error: {
    light: '#E21A2C',
    dark: '#F87171',
  },
  warning: {
    light: '#F59E0B',
    dark: '#FBBF24',
  },
  info: {
    light: '#3B82F6',
    dark: '#60A5FA',
  },
  
  // Dark theme specific
  darkBg: {
    primary: '#1a1a2e',
    secondary: '#16162a',
    tertiary: '#0f0f1a',
  },
  
  darkText: {
    primary: '#e2e8f0',
    secondary: '#94a3b8',
    tertiary: '#64748b',
  },
  
  darkAccent: {
    green: '#4ade80',
    blue: '#60a5fa',
    purple: '#a78bfa',
  },
} as const;

export type ColorKey = keyof typeof colors;
