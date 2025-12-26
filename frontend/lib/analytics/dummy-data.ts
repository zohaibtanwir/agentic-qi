/**
 * Analytics Dashboard Dummy Data
 * Static mock data for Phase 1 (UI-only implementation)
 */

import {
  AnalyticsSummary,
  TimeSeriesDataPoint,
  TokenUsageByAgent,
  ResponseTimeByAgent,
  TimeGranularity,
} from './types';

// ============================================================================
// Main Analytics Summary Data
// ============================================================================

export const DUMMY_ANALYTICS: AnalyticsSummary = {
  dateRange: {
    start: '2024-12-18',
    end: '2024-12-24',
    label: 'Last 7 Days',
  },

  overview: {
    totalRequests: {
      value: 1247,
      formattedValue: '1,247',
      change: 12,
      changeDirection: 'up',
    },
    testCasesGenerated: {
      value: 1842,
      formattedValue: '1,842',
      change: 8,
      changeDirection: 'up',
    },
    totalTokens: {
      value: 141730,
      formattedValue: '142K',
      change: 15,
      changeDirection: 'up',
    },
    estimatedCost: {
      value: 4.25,
      formattedValue: '$4.25',
      change: 10,
      changeDirection: 'up',
    },
    avgLatency: {
      value: 12.3,
      formattedValue: '12.3s',
      change: -5,
      changeDirection: 'down',
    },
  },

  byAgent: [
    {
      agent: 'requirement_analysis',
      requests: 247,
      requestsChange: 12,
      tokens: 45230,
      tokensChange: 14,
      avgTokensPerRequest: 183,
      avgResponseTime: 14.2,
      successRate: 98.4,
      errorRate: 1.6,
    },
    {
      agent: 'test_cases',
      requests: 523,
      requestsChange: 8,
      tokens: 68450,
      tokensChange: 11,
      avgTokensPerRequest: 131,
      avgResponseTime: 12.8,
      successRate: 99.1,
      errorRate: 0.9,
    },
    {
      agent: 'test_data',
      requests: 312,
      requestsChange: 15,
      tokens: 18200,
      tokensChange: 18,
      avgTokensPerRequest: 58,
      avgResponseTime: 8.4,
      successRate: 99.7,
      errorRate: 0.3,
    },
    {
      agent: 'domain',
      requests: 165,
      requestsChange: 5,
      tokens: 9850,
      tokensChange: 7,
      avgTokensPerRequest: 60,
      avgResponseTime: 2.1,
      successRate: 99.9,
      errorRate: 0.1,
    },
  ],

  requestsOverTime: [
    { date: '2024-12-18', requirementAnalysis: 32, testCases: 68, testData: 41, domain: 22 },
    { date: '2024-12-19', requirementAnalysis: 38, testCases: 75, testData: 45, domain: 25 },
    { date: '2024-12-20', requirementAnalysis: 45, testCases: 82, testData: 52, domain: 28 },
    { date: '2024-12-21', requirementAnalysis: 28, testCases: 55, testData: 35, domain: 18 },
    { date: '2024-12-22', requirementAnalysis: 22, testCases: 48, testData: 30, domain: 15 },
    { date: '2024-12-23', requirementAnalysis: 35, testCases: 78, testData: 48, domain: 24 },
    { date: '2024-12-24', requirementAnalysis: 47, testCases: 117, testData: 61, domain: 33 },
  ],

  qualityDistribution: [
    { grade: 'A', count: 42, percentage: 17 },
    { grade: 'B', count: 68, percentage: 28 },
    { grade: 'C', count: 85, percentage: 34 },
    { grade: 'D', count: 38, percentage: 15 },
    { grade: 'F', count: 14, percentage: 6 },
  ],

  recentActivity: [
    {
      id: 'act-001',
      timestamp: '2024-12-24T12:34:00Z',
      agent: 'requirement_analysis',
      action: 'Analyzed',
      title: 'Guest Checkout Feature',
      metric: '72/100',
      tokens: 2340,
    },
    {
      id: 'act-002',
      timestamp: '2024-12-24T12:30:00Z',
      agent: 'test_cases',
      action: 'Generated',
      title: 'Product Reviews',
      metric: '8 cases',
      tokens: 1820,
    },
    {
      id: 'act-003',
      timestamp: '2024-12-24T12:28:00Z',
      agent: 'test_data',
      action: 'Generated',
      title: 'Customer Entity',
      metric: '50 records',
      tokens: 420,
    },
    {
      id: 'act-004',
      timestamp: '2024-12-24T12:25:00Z',
      agent: 'domain',
      action: 'Queried',
      title: 'Payment Workflow',
      tokens: 180,
    },
    {
      id: 'act-005',
      timestamp: '2024-12-24T12:20:00Z',
      agent: 'requirement_analysis',
      action: 'Analyzed',
      title: 'Wishlist Feature',
      metric: '85/100',
      tokens: 2150,
    },
    {
      id: 'act-006',
      timestamp: '2024-12-24T12:15:00Z',
      agent: 'test_cases',
      action: 'Generated',
      title: 'Apply Promo Code',
      metric: '12 cases',
      tokens: 2890,
    },
    {
      id: 'act-007',
      timestamp: '2024-12-24T12:10:00Z',
      agent: 'test_data',
      action: 'Generated',
      title: 'Order Entity',
      metric: '25 records',
      tokens: 380,
    },
    {
      id: 'act-008',
      timestamp: '2024-12-24T12:05:00Z',
      agent: 'requirement_analysis',
      action: 'Analyzed',
      title: 'Return & Refund Policy',
      metric: '68/100',
      tokens: 2560,
    },
  ],
};

// ============================================================================
// Token Usage by Agent (for Donut Chart)
// ============================================================================

export const TOKEN_USAGE_BY_AGENT: TokenUsageByAgent[] = [
  { agent: 'Requirement Analysis', tokens: 45230, percentage: 32, color: '#E21A2C' },
  { agent: 'Test Cases', tokens: 68450, percentage: 48, color: '#1E3A5F' },
  { agent: 'Test Data', tokens: 18200, percentage: 13, color: '#2E7D32' },
  { agent: 'Domain', tokens: 9850, percentage: 7, color: '#F59E0B' },
];

// ============================================================================
// Response Time by Agent (for Horizontal Bar Chart)
// ============================================================================

export const RESPONSE_TIME_BY_AGENT: ResponseTimeByAgent[] = [
  { agent: 'Requirement Analysis', avgTime: 14.2, p50: 12.5, p95: 22.3, p99: 28.1 },
  { agent: 'Test Cases', avgTime: 12.8, p50: 11.2, p95: 19.8, p99: 25.4 },
  { agent: 'Test Data', avgTime: 8.4, p50: 7.1, p95: 14.2, p99: 18.5 },
  { agent: 'Domain', avgTime: 2.1, p50: 1.8, p95: 3.5, p99: 4.2 },
];

// ============================================================================
// Weekly Time Series Data
// ============================================================================

export const WEEKLY_DATA: TimeSeriesDataPoint[] = [
  { date: 'Week 48', requirementAnalysis: 180, testCases: 420, testData: 280, domain: 140 },
  { date: 'Week 49', requirementAnalysis: 210, testCases: 480, testData: 310, domain: 155 },
  { date: 'Week 50', requirementAnalysis: 195, testCases: 445, testData: 290, domain: 148 },
  { date: 'Week 51', requirementAnalysis: 247, testCases: 523, testData: 312, domain: 165 },
];

// ============================================================================
// Monthly Time Series Data
// ============================================================================

export const MONTHLY_DATA: TimeSeriesDataPoint[] = [
  { date: 'Sep 2024', requirementAnalysis: 720, testCases: 1650, testData: 1100, domain: 550 },
  { date: 'Oct 2024', requirementAnalysis: 810, testCases: 1820, testData: 1200, domain: 610 },
  { date: 'Nov 2024', requirementAnalysis: 880, testCases: 1950, testData: 1280, domain: 645 },
  { date: 'Dec 2024', requirementAnalysis: 950, testCases: 2100, testData: 1350, domain: 680 },
];

// ============================================================================
// Extended Data for Different Date Ranges
// ============================================================================

export const DUMMY_ANALYTICS_30_DAYS: AnalyticsSummary = {
  ...DUMMY_ANALYTICS,
  dateRange: {
    start: '2024-11-25',
    end: '2024-12-24',
    label: 'Last 30 Days',
  },
  overview: {
    totalRequests: {
      value: 4988,
      formattedValue: '4,988',
      change: 18,
      changeDirection: 'up',
    },
    testCasesGenerated: {
      value: 7368,
      formattedValue: '7,368',
      change: 12,
      changeDirection: 'up',
    },
    totalTokens: {
      value: 566920,
      formattedValue: '567K',
      change: 22,
      changeDirection: 'up',
    },
    estimatedCost: {
      value: 17.01,
      formattedValue: '$17.01',
      change: 15,
      changeDirection: 'up',
    },
    avgLatency: {
      value: 11.8,
      formattedValue: '11.8s',
      change: -8,
      changeDirection: 'down',
    },
  },
};

export const DUMMY_ANALYTICS_90_DAYS: AnalyticsSummary = {
  ...DUMMY_ANALYTICS,
  dateRange: {
    start: '2024-09-26',
    end: '2024-12-24',
    label: 'Last 90 Days',
  },
  overview: {
    totalRequests: {
      value: 14964,
      formattedValue: '14,964',
      change: 25,
      changeDirection: 'up',
    },
    testCasesGenerated: {
      value: 22104,
      formattedValue: '22,104',
      change: 20,
      changeDirection: 'up',
    },
    totalTokens: {
      value: 1700760,
      formattedValue: '1.7M',
      change: 28,
      changeDirection: 'up',
    },
    estimatedCost: {
      value: 51.02,
      formattedValue: '$51.02',
      change: 22,
      changeDirection: 'up',
    },
    avgLatency: {
      value: 11.5,
      formattedValue: '11.5s',
      change: -12,
      changeDirection: 'down',
    },
  },
};

// ============================================================================
// Helper Functions for Getting Data
// ============================================================================

/**
 * Get analytics data for a specific date range
 */
export function getAnalyticsDataForRange(range: string): AnalyticsSummary {
  switch (range) {
    case 'last_30_days':
      return DUMMY_ANALYTICS_30_DAYS;
    case 'last_90_days':
      return DUMMY_ANALYTICS_90_DAYS;
    case 'last_7_days':
    default:
      return DUMMY_ANALYTICS;
  }
}

/**
 * Get time series data for a specific granularity
 */
export function getTimeSeriesDataForGranularity(
  granularity: TimeGranularity
): TimeSeriesDataPoint[] {
  switch (granularity) {
    case 'hour':
      // For hourly data, return a subset of daily data (simulated)
      return DUMMY_ANALYTICS.requestsOverTime.slice(0, 6);
    case 'week':
      return WEEKLY_DATA;
    case 'month':
      return MONTHLY_DATA;
    case 'day':
    default:
      return DUMMY_ANALYTICS.requestsOverTime;
  }
}

/**
 * Get requests by agent data for charts
 */
export function getRequestsByAgent(): { agent: string; requests: number; change: number }[] {
  return DUMMY_ANALYTICS.byAgent.map((agent) => ({
    agent: agent.agent === 'requirement_analysis' ? 'Req Analysis' :
           agent.agent === 'test_cases' ? 'Test Cases' :
           agent.agent === 'test_data' ? 'Test Data' : 'Domain',
    requests: agent.requests,
    change: agent.requestsChange,
  }));
}

/**
 * Calculate total tokens from all agents
 */
export function getTotalTokens(): number {
  return TOKEN_USAGE_BY_AGENT.reduce((sum, agent) => sum + agent.tokens, 0);
}

/**
 * Calculate platform average response time
 */
export function getPlatformAvgResponseTime(): number {
  const times = RESPONSE_TIME_BY_AGENT.map((a) => a.avgTime);
  return Number((times.reduce((a, b) => a + b, 0) / times.length).toFixed(1));
}

/**
 * Get quality distribution average score
 */
export function getQualityAverageScore(): { score: number; grade: string } {
  const distribution = DUMMY_ANALYTICS.qualityDistribution;
  const gradeScores: Record<string, number> = { A: 95, B: 85, C: 75, D: 65, F: 50 };

  let totalScore = 0;
  let totalCount = 0;

  distribution.forEach((d) => {
    totalScore += gradeScores[d.grade] * d.count;
    totalCount += d.count;
  });

  const avgScore = Math.round(totalScore / totalCount);
  const grade = avgScore >= 90 ? 'A' : avgScore >= 80 ? 'B' : avgScore >= 70 ? 'C' : avgScore >= 60 ? 'D' : 'F';

  return { score: avgScore, grade: `${grade}+` };
}
