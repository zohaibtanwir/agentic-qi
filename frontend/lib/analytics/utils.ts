/**
 * Analytics Dashboard Utilities
 * Contains agent configuration, grade configuration, and formatting functions
 */

import { AgentType, QualityGrade, ChangeDirection } from './types';

// ============================================================================
// Agent Configuration
// ============================================================================

export interface AgentConfig {
  displayName: string;
  shortName: string;
  icon: string;
  color: string;
  bgColor: string;
}

export const AGENT_CONFIG: Record<AgentType, AgentConfig> = {
  requirement_analysis: {
    displayName: 'Requirement Analysis',
    shortName: 'Req Analysis',
    icon: '🔍',
    color: '#E21A2C', // Macy's Red
    bgColor: '#FCECED',
  },
  test_cases: {
    displayName: 'Test Cases',
    shortName: 'Test Cases',
    icon: '🧪',
    color: '#1E3A5F', // Navy
    bgColor: '#E8EDF2',
  },
  test_data: {
    displayName: 'Test Data',
    shortName: 'Test Data',
    icon: '📦',
    color: '#2E7D32', // Green
    bgColor: '#E8F5E9',
  },
  domain: {
    displayName: 'Domain Agent',
    shortName: 'Domain',
    icon: '🏢',
    color: '#F59E0B', // Amber
    bgColor: '#FEF3C7',
  },
};

// ============================================================================
// Grade Configuration
// ============================================================================

export interface GradeConfig {
  color: string;
  bgColor: string;
  label: string;
  minScore: number;
  maxScore: number;
}

export const GRADE_CONFIG: Record<QualityGrade, GradeConfig> = {
  A: {
    color: '#22C55E', // Green
    bgColor: '#DCFCE7',
    label: 'Excellent',
    minScore: 90,
    maxScore: 100,
  },
  B: {
    color: '#84CC16', // Lime
    bgColor: '#ECFCCB',
    label: 'Good',
    minScore: 80,
    maxScore: 89,
  },
  C: {
    color: '#F59E0B', // Amber
    bgColor: '#FEF3C7',
    label: 'Acceptable',
    minScore: 70,
    maxScore: 79,
  },
  D: {
    color: '#F97316', // Orange
    bgColor: '#FFEDD5',
    label: 'Needs Work',
    minScore: 60,
    maxScore: 69,
  },
  F: {
    color: '#EF4444', // Red
    bgColor: '#FEE2E2',
    label: 'Poor',
    minScore: 0,
    maxScore: 59,
  },
};

// ============================================================================
// Formatting Functions
// ============================================================================

/**
 * Format a number with K/M suffixes for large values
 */
export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${Math.round(num / 1000)}K`;
  }
  return num.toLocaleString();
}

/**
 * Format a number as currency (USD)
 */
export function formatCurrency(amount: number): string {
  return `$${amount.toFixed(2)}`;
}

/**
 * Format a duration in seconds
 */
export function formatDuration(seconds: number): string {
  return `${seconds.toFixed(1)}s`;
}

/**
 * Format an ISO timestamp to time string (HH:MM)
 */
export function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

/**
 * Format an ISO timestamp to date string (MMM DD)
 */
export function formatDate(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format an ISO timestamp to full date string (MMM DD, YYYY)
 */
export function formatFullDate(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Format percentage change with + or - prefix
 */
export function formatPercentageChange(change: number): string {
  const prefix = change >= 0 ? '+' : '';
  return `${prefix}${change}%`;
}

/**
 * Get change direction from numeric change value
 */
export function getChangeDirection(change: number): ChangeDirection {
  if (change > 0) return 'up';
  if (change < 0) return 'down';
  return 'neutral';
}

/**
 * Get grade from numeric score
 */
export function getGradeFromScore(score: number): QualityGrade {
  if (score >= 90) return 'A';
  if (score >= 80) return 'B';
  if (score >= 70) return 'C';
  if (score >= 60) return 'D';
  return 'F';
}

/**
 * Get average grade from array of scores
 */
export function getAverageGrade(scores: number[]): { score: number; grade: QualityGrade } {
  if (scores.length === 0) {
    return { score: 0, grade: 'F' };
  }
  const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  return { score: avgScore, grade: getGradeFromScore(avgScore) };
}

/**
 * Calculate estimated cost based on tokens used
 * Using approximate pricing: $3 per 1M input tokens, $15 per 1M output tokens
 * Simplified to $0.00003 per token (assuming 1:1 input/output ratio average)
 */
export function calculateEstimatedCost(tokens: number): number {
  const costPerToken = 0.00003;
  return tokens * costPerToken;
}

/**
 * Get agent display name from agent type
 */
export function getAgentDisplayName(agent: AgentType): string {
  return AGENT_CONFIG[agent].displayName;
}

/**
 * Get agent short name from agent type
 */
export function getAgentShortName(agent: AgentType): string {
  return AGENT_CONFIG[agent].shortName;
}

/**
 * Get agent icon from agent type
 */
export function getAgentIcon(agent: AgentType): string {
  return AGENT_CONFIG[agent].icon;
}

/**
 * Get agent color from agent type
 */
export function getAgentColor(agent: AgentType): string {
  return AGENT_CONFIG[agent].color;
}

/**
 * Get grade color from grade
 */
export function getGradeColor(grade: QualityGrade): string {
  return GRADE_CONFIG[grade].color;
}

/**
 * Get grade background color from grade
 */
export function getGradeBgColor(grade: QualityGrade): string {
  return GRADE_CONFIG[grade].bgColor;
}

/**
 * Get grade label from grade
 */
export function getGradeLabel(grade: QualityGrade): string {
  return GRADE_CONFIG[grade].label;
}

// ============================================================================
// Date Range Utilities
// ============================================================================

export interface DateRangeOption {
  value: string;
  label: string;
}

export const DATE_RANGE_OPTIONS: DateRangeOption[] = [
  { value: 'today', label: 'Today' },
  { value: 'last_7_days', label: 'Last 7 Days' },
  { value: 'last_30_days', label: 'Last 30 Days' },
  { value: 'last_90_days', label: 'Last 90 Days' },
  { value: 'this_month', label: 'This Month' },
  { value: 'last_month', label: 'Last Month' },
];

/**
 * Get date range bounds from date range type
 */
export function getDateRangeBounds(range: string): { start: Date; end: Date } {
  const now = new Date();
  const end = new Date(now);
  end.setHours(23, 59, 59, 999);

  const start = new Date(now);
  start.setHours(0, 0, 0, 0);

  switch (range) {
    case 'today':
      // start is already today
      break;
    case 'last_7_days':
      start.setDate(start.getDate() - 6);
      break;
    case 'last_30_days':
      start.setDate(start.getDate() - 29);
      break;
    case 'last_90_days':
      start.setDate(start.getDate() - 89);
      break;
    case 'this_month':
      start.setDate(1);
      break;
    case 'last_month':
      start.setMonth(start.getMonth() - 1, 1);
      end.setDate(0); // Last day of previous month
      break;
    default:
      start.setDate(start.getDate() - 6); // Default to last 7 days
  }

  return { start, end };
}

// ============================================================================
// Export Utilities
// ============================================================================

/**
 * Convert analytics data to CSV format
 */
export function exportToCSV(data: Record<string, unknown>[], filename: string): void {
  if (data.length === 0) return;

  const headers = Object.keys(data[0]);
  const csvRows = [
    headers.join(','),
    ...data.map((row) =>
      headers
        .map((header) => {
          const value = row[header];
          // Escape quotes and wrap in quotes if contains comma
          const stringValue = String(value ?? '');
          if (stringValue.includes(',') || stringValue.includes('"')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
          }
          return stringValue;
        })
        .join(',')
    ),
  ];

  const csvContent = csvRows.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
