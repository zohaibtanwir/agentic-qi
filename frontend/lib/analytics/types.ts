/**
 * Analytics Dashboard TypeScript Types
 * Based on PRD: frontend/docs/analytics_dashboard_prd.md
 */

// ============================================================================
// Core Types
// ============================================================================

export type AgentType =
  | 'requirement_analysis'
  | 'test_cases'
  | 'test_data'
  | 'domain';

export type DateRange =
  | 'today'
  | 'last_7_days'
  | 'last_30_days'
  | 'last_90_days'
  | 'this_month'
  | 'last_month'
  | 'custom';

export type TimeGranularity = 'hour' | 'day' | 'week' | 'month';

export type QualityGrade = 'A' | 'B' | 'C' | 'D' | 'F';

export type ChangeDirection = 'up' | 'down' | 'neutral';

// ============================================================================
// Metric Types
// ============================================================================

export interface MetricData {
  value: number;
  formattedValue: string;
  change: number;
  changeDirection: ChangeDirection;
}

export interface AgentMetrics {
  agent: AgentType;
  requests: number;
  requestsChange: number;
  tokens: number;
  tokensChange: number;
  avgTokensPerRequest: number;
  avgResponseTime: number;
  successRate: number;
  errorRate: number;
}

// ============================================================================
// Time Series Types
// ============================================================================

export interface TimeSeriesDataPoint {
  date: string;
  requirementAnalysis: number;
  testCases: number;
  testData: number;
  domain: number;
}

// ============================================================================
// Quality Distribution Types
// ============================================================================

export interface QualityDistribution {
  grade: QualityGrade;
  count: number;
  percentage: number;
}

// ============================================================================
// Token Usage Types
// ============================================================================

export interface TokenUsageByAgent {
  agent: string;
  tokens: number;
  percentage: number;
  color: string;
}

// ============================================================================
// Response Time Types
// ============================================================================

export interface ResponseTimeByAgent {
  agent: string;
  avgTime: number;
  p50: number;
  p95: number;
  p99: number;
}

// ============================================================================
// Activity Types
// ============================================================================

export interface ActivityItem {
  id: string;
  timestamp: string;
  agent: AgentType;
  action: string;
  title: string;
  metric?: string;
  tokens: number;
}

// ============================================================================
// Overview Types
// ============================================================================

export interface OverviewMetrics {
  totalRequests: MetricData;
  testCasesGenerated: MetricData;
  totalTokens: MetricData;
  estimatedCost: MetricData;
  avgLatency: MetricData;
}

// ============================================================================
// Date Range Types
// ============================================================================

export interface DateRangeInfo {
  start: string;
  end: string;
  label: string;
}

// ============================================================================
// Analytics Summary (Main Data Structure)
// ============================================================================

export interface AnalyticsSummary {
  dateRange: DateRangeInfo;
  overview: OverviewMetrics;
  byAgent: AgentMetrics[];
  requestsOverTime: TimeSeriesDataPoint[];
  qualityDistribution: QualityDistribution[];
  recentActivity: ActivityItem[];
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface OverviewCardProps {
  title: string;
  value: string | number;
  change: number;
  changeDirection: ChangeDirection;
  changeLabel?: string;
  icon?: React.ReactNode;
}

export interface DateRangeSelectorProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
}

export interface RequestsOverTimeChartProps {
  data: TimeSeriesDataPoint[];
  granularity: TimeGranularity;
  onGranularityChange?: (granularity: TimeGranularity) => void;
}

export interface TokenUsageChartProps {
  data: TokenUsageByAgent[];
  totalTokens: number;
}

export interface RequestsByAgentChartProps {
  data: {
    agent: string;
    requests: number;
    change: number;
  }[];
}

export interface QualityScoreChartProps {
  data: QualityDistribution[];
  averageScore: number;
  averageGrade: string;
}

export interface ResponseTimeChartProps {
  data: ResponseTimeByAgent[];
  platformAvg: number;
}

export interface AgentDetailsTableProps {
  data: AgentMetrics[];
}

export interface RecentActivityProps {
  items: ActivityItem[];
  limit?: number;
}

export interface ExportButtonProps {
  onExport: (format: 'csv' | 'pdf') => void;
  data: AnalyticsSummary;
}

// ============================================================================
// Hook Return Types
// ============================================================================

export interface UseAnalyticsReturn {
  data: AnalyticsSummary;
  isLoading: boolean;
  error: Error | null;
  getTimeSeriesData: (granularity: TimeGranularity) => TimeSeriesDataPoint[];
  setDateRange: (range: DateRange) => void;
  dateRange: DateRange;
}
