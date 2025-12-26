'use client';

/**
 * useAnalytics Hook
 * Manages analytics data state and provides data access methods.
 * Phase 1: Uses dummy data; Phase 2 will integrate with real APIs.
 */

import { useState, useCallback, useMemo } from 'react';
import {
  DateRange,
  TimeGranularity,
  AnalyticsSummary,
  TimeSeriesDataPoint,
  TokenUsageByAgent,
  ResponseTimeByAgent,
} from '@/lib/analytics/types';
import {
  getAnalyticsDataForRange,
  getTimeSeriesDataForGranularity,
  getRequestsByAgent,
  getTotalTokens,
  getPlatformAvgResponseTime,
  getQualityAverageScore,
  TOKEN_USAGE_BY_AGENT,
  RESPONSE_TIME_BY_AGENT,
} from '@/lib/analytics/dummy-data';

// ============================================================================
// Types
// ============================================================================

export interface UseAnalyticsOptions {
  /**
   * Initial date range to load data for
   */
  initialDateRange?: DateRange;
  /**
   * Initial time granularity for time series data
   */
  initialGranularity?: TimeGranularity;
}

export interface UseAnalyticsReturn {
  /**
   * Current date range selection
   */
  dateRange: DateRange;
  /**
   * Set the date range
   */
  setDateRange: (range: DateRange) => void;
  /**
   * Current time granularity for charts
   */
  granularity: TimeGranularity;
  /**
   * Set the time granularity
   */
  setGranularity: (granularity: TimeGranularity) => void;
  /**
   * Main analytics summary data
   */
  data: AnalyticsSummary;
  /**
   * Time series data for the current granularity
   */
  timeSeriesData: TimeSeriesDataPoint[];
  /**
   * Get time series data for a specific granularity
   */
  getTimeSeriesData: (granularity: TimeGranularity) => TimeSeriesDataPoint[];
  /**
   * Token usage breakdown by agent
   */
  tokenUsageByAgent: TokenUsageByAgent[];
  /**
   * Response time breakdown by agent
   */
  responseTimeByAgent: ResponseTimeByAgent[];
  /**
   * Requests by agent with formatted names
   */
  requestsByAgent: { agent: string; requests: number; change: number }[];
  /**
   * Total tokens used
   */
  totalTokens: number;
  /**
   * Platform average response time
   */
  avgResponseTime: number;
  /**
   * Quality average score and grade
   */
  qualityScore: { score: number; grade: string };
  /**
   * Loading state (for future API integration)
   */
  isLoading: boolean;
  /**
   * Error state (for future API integration)
   */
  error: string | null;
  /**
   * Refresh data (for future API integration)
   */
  refresh: () => void;
}

// ============================================================================
// Hook Implementation
// ============================================================================

export function useAnalytics(options: UseAnalyticsOptions = {}): UseAnalyticsReturn {
  const {
    initialDateRange = 'last_7_days',
    initialGranularity = 'day',
  } = options;

  // State
  const [dateRange, setDateRange] = useState<DateRange>(initialDateRange);
  const [granularity, setGranularity] = useState<TimeGranularity>(initialGranularity);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get analytics data based on current date range
  const data = useMemo(() => {
    return getAnalyticsDataForRange(dateRange);
  }, [dateRange]);

  // Get time series data based on current granularity
  const timeSeriesData = useMemo(() => {
    return getTimeSeriesDataForGranularity(granularity);
  }, [granularity]);

  // Function to get time series data for any granularity
  const getTimeSeriesData = useCallback((g: TimeGranularity) => {
    return getTimeSeriesDataForGranularity(g);
  }, []);

  // Static data (doesn't change with date range in Phase 1)
  const tokenUsageByAgent = useMemo(() => TOKEN_USAGE_BY_AGENT, []);
  const responseTimeByAgent = useMemo(() => RESPONSE_TIME_BY_AGENT, []);
  const requestsByAgent = useMemo(() => getRequestsByAgent(), []);
  const totalTokens = useMemo(() => getTotalTokens(), []);
  const avgResponseTime = useMemo(() => getPlatformAvgResponseTime(), []);
  const qualityScore = useMemo(() => getQualityAverageScore(), []);

  // Handle date range change
  const handleSetDateRange = useCallback((range: DateRange) => {
    setDateRange(range);
    // In Phase 2, this would trigger an API call
    // For now, data is immediately available from dummy data
  }, []);

  // Handle granularity change
  const handleSetGranularity = useCallback((g: TimeGranularity) => {
    setGranularity(g);
  }, []);

  // Refresh function (for future API integration)
  const refresh = useCallback(() => {
    setIsLoading(true);
    setError(null);

    // Simulate API call delay
    setTimeout(() => {
      setIsLoading(false);
      // Data is already available from useMemo
    }, 0);
  }, []);

  return {
    dateRange,
    setDateRange: handleSetDateRange,
    granularity,
    setGranularity: handleSetGranularity,
    data,
    timeSeriesData,
    getTimeSeriesData,
    tokenUsageByAgent,
    responseTimeByAgent,
    requestsByAgent,
    totalTokens,
    avgResponseTime,
    qualityScore,
    isLoading,
    error,
    refresh,
  };
}

export default useAnalytics;
