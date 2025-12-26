/**
 * Unit tests for useAnalytics Hook
 */

import { renderHook, act } from '@testing-library/react';
import { useAnalytics, UseAnalyticsReturn } from '@/hooks/useAnalytics';
import {
  DUMMY_ANALYTICS,
  DUMMY_ANALYTICS_30_DAYS,
  DUMMY_ANALYTICS_90_DAYS,
  WEEKLY_DATA,
  MONTHLY_DATA,
  TOKEN_USAGE_BY_AGENT,
  RESPONSE_TIME_BY_AGENT,
} from '@/lib/analytics/dummy-data';

describe('useAnalytics Hook', () => {
  describe('Initial State', () => {
    it('should initialize with default values', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.dateRange).toBe('last_7_days');
      expect(result.current.granularity).toBe('day');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should accept custom initial date range', () => {
      const { result } = renderHook(() =>
        useAnalytics({ initialDateRange: 'last_30_days' })
      );

      expect(result.current.dateRange).toBe('last_30_days');
    });

    it('should accept custom initial granularity', () => {
      const { result } = renderHook(() =>
        useAnalytics({ initialGranularity: 'week' })
      );

      expect(result.current.granularity).toBe('week');
    });

    it('should accept both custom initial values', () => {
      const { result } = renderHook(() =>
        useAnalytics({
          initialDateRange: 'last_90_days',
          initialGranularity: 'month',
        })
      );

      expect(result.current.dateRange).toBe('last_90_days');
      expect(result.current.granularity).toBe('month');
    });
  });

  describe('Date Range Management', () => {
    it('should update date range when setDateRange is called', () => {
      const { result } = renderHook(() => useAnalytics());

      act(() => {
        result.current.setDateRange('last_30_days');
      });

      expect(result.current.dateRange).toBe('last_30_days');
    });

    it('should return 7 day data for last_7_days', () => {
      const { result } = renderHook(() =>
        useAnalytics({ initialDateRange: 'last_7_days' })
      );

      expect(result.current.data.dateRange.label).toBe('Last 7 Days');
      expect(result.current.data.overview.totalRequests.value).toBe(
        DUMMY_ANALYTICS.overview.totalRequests.value
      );
    });

    it('should return 30 day data for last_30_days', () => {
      const { result } = renderHook(() =>
        useAnalytics({ initialDateRange: 'last_30_days' })
      );

      expect(result.current.data.dateRange.label).toBe('Last 30 Days');
      expect(result.current.data.overview.totalRequests.value).toBe(
        DUMMY_ANALYTICS_30_DAYS.overview.totalRequests.value
      );
    });

    it('should return 90 day data for last_90_days', () => {
      const { result } = renderHook(() =>
        useAnalytics({ initialDateRange: 'last_90_days' })
      );

      expect(result.current.data.dateRange.label).toBe('Last 90 Days');
      expect(result.current.data.overview.totalRequests.value).toBe(
        DUMMY_ANALYTICS_90_DAYS.overview.totalRequests.value
      );
    });

    it('should update data when date range changes', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.data.dateRange.label).toBe('Last 7 Days');

      act(() => {
        result.current.setDateRange('last_30_days');
      });

      expect(result.current.data.dateRange.label).toBe('Last 30 Days');
    });
  });

  describe('Granularity Management', () => {
    it('should update granularity when setGranularity is called', () => {
      const { result } = renderHook(() => useAnalytics());

      act(() => {
        result.current.setGranularity('week');
      });

      expect(result.current.granularity).toBe('week');
    });

    it('should return daily time series data for day granularity', () => {
      const { result } = renderHook(() =>
        useAnalytics({ initialGranularity: 'day' })
      );

      expect(result.current.timeSeriesData).toHaveLength(7);
      expect(result.current.timeSeriesData[0].date).toMatch(/\d{4}-\d{2}-\d{2}/);
    });

    it('should return weekly time series data for week granularity', () => {
      const { result } = renderHook(() =>
        useAnalytics({ initialGranularity: 'week' })
      );

      expect(result.current.timeSeriesData).toHaveLength(4);
      expect(result.current.timeSeriesData[0].date).toContain('Week');
    });

    it('should return monthly time series data for month granularity', () => {
      const { result } = renderHook(() =>
        useAnalytics({ initialGranularity: 'month' })
      );

      expect(result.current.timeSeriesData).toHaveLength(4);
      expect(result.current.timeSeriesData[0].date).toMatch(/\w+ \d{4}/);
    });

    it('should update time series data when granularity changes', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.timeSeriesData).toHaveLength(7); // day

      act(() => {
        result.current.setGranularity('week');
      });

      expect(result.current.timeSeriesData).toHaveLength(4); // week
    });
  });

  describe('getTimeSeriesData Function', () => {
    it('should return data for any granularity without changing state', () => {
      const { result } = renderHook(() => useAnalytics());

      const weeklyData = result.current.getTimeSeriesData('week');
      const monthlyData = result.current.getTimeSeriesData('month');

      expect(weeklyData).toHaveLength(4);
      expect(monthlyData).toHaveLength(4);

      // State should still be day
      expect(result.current.granularity).toBe('day');
      expect(result.current.timeSeriesData).toHaveLength(7);
    });

    it('should return same data as WEEKLY_DATA for week', () => {
      const { result } = renderHook(() => useAnalytics());

      const weeklyData = result.current.getTimeSeriesData('week');
      expect(weeklyData).toEqual(WEEKLY_DATA);
    });

    it('should return same data as MONTHLY_DATA for month', () => {
      const { result } = renderHook(() => useAnalytics());

      const monthlyData = result.current.getTimeSeriesData('month');
      expect(monthlyData).toEqual(MONTHLY_DATA);
    });
  });

  describe('Static Data Accessors', () => {
    it('should return token usage by agent', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.tokenUsageByAgent).toEqual(TOKEN_USAGE_BY_AGENT);
      expect(result.current.tokenUsageByAgent).toHaveLength(4);
    });

    it('should return response time by agent', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.responseTimeByAgent).toEqual(RESPONSE_TIME_BY_AGENT);
      expect(result.current.responseTimeByAgent).toHaveLength(4);
    });

    it('should return requests by agent with formatted names', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.requestsByAgent).toHaveLength(4);
      const names = result.current.requestsByAgent.map((a) => a.agent);
      expect(names).toContain('Req Analysis');
      expect(names).toContain('Test Cases');
      expect(names).toContain('Test Data');
      expect(names).toContain('Domain');
    });

    it('should return total tokens', () => {
      const { result } = renderHook(() => useAnalytics());

      const expectedTotal = TOKEN_USAGE_BY_AGENT.reduce(
        (sum, a) => sum + a.tokens,
        0
      );
      expect(result.current.totalTokens).toBe(expectedTotal);
    });

    it('should return average response time', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.avgResponseTime).toBeGreaterThan(0);
      expect(result.current.avgResponseTime).toBeLessThan(20);
    });

    it('should return quality score and grade', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.qualityScore).toHaveProperty('score');
      expect(result.current.qualityScore).toHaveProperty('grade');
      expect(result.current.qualityScore.score).toBeGreaterThanOrEqual(0);
      expect(result.current.qualityScore.score).toBeLessThanOrEqual(100);
    });
  });

  describe('Data Structure', () => {
    it('should return data with all required overview metrics', () => {
      const { result } = renderHook(() => useAnalytics());

      const { overview } = result.current.data;
      expect(overview).toHaveProperty('totalRequests');
      expect(overview).toHaveProperty('testCasesGenerated');
      expect(overview).toHaveProperty('totalTokens');
      expect(overview).toHaveProperty('estimatedCost');
      expect(overview).toHaveProperty('avgLatency');
    });

    it('should return data with 4 agents in byAgent', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.data.byAgent).toHaveLength(4);
    });

    it('should return data with quality distribution', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.data.qualityDistribution).toHaveLength(5);
    });

    it('should return data with recent activity', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.data.recentActivity).toHaveLength(8);
    });
  });

  describe('Loading and Error States', () => {
    it('should start with isLoading false', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.isLoading).toBe(false);
    });

    it('should start with error null', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.error).toBeNull();
    });

    it('should have refresh function', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(typeof result.current.refresh).toBe('function');
    });

    it('should call refresh without errors', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(() => {
        act(() => {
          result.current.refresh();
        });
      }).not.toThrow();
    });
  });

  describe('Memoization', () => {
    it('should maintain referential equality for static data across renders', () => {
      const { result, rerender } = renderHook(() => useAnalytics());

      const tokenUsage1 = result.current.tokenUsageByAgent;
      const responseTime1 = result.current.responseTimeByAgent;

      rerender();

      // These should be the same reference (memoized)
      expect(result.current.tokenUsageByAgent).toBe(tokenUsage1);
      expect(result.current.responseTimeByAgent).toBe(responseTime1);
    });

    it('should update data reference when date range changes', () => {
      const { result } = renderHook(() => useAnalytics());

      const data1 = result.current.data;

      act(() => {
        result.current.setDateRange('last_30_days');
      });

      const data2 = result.current.data;

      // Data should be different (new reference)
      expect(data2).not.toBe(data1);
      expect(data2.dateRange.label).not.toBe(data1.dateRange.label);
    });
  });

  describe('Return Type Completeness', () => {
    it('should return all expected properties', () => {
      const { result } = renderHook(() => useAnalytics());

      const expectedKeys: (keyof UseAnalyticsReturn)[] = [
        'dateRange',
        'setDateRange',
        'granularity',
        'setGranularity',
        'data',
        'timeSeriesData',
        'getTimeSeriesData',
        'tokenUsageByAgent',
        'responseTimeByAgent',
        'requestsByAgent',
        'totalTokens',
        'avgResponseTime',
        'qualityScore',
        'isLoading',
        'error',
        'refresh',
      ];

      expectedKeys.forEach((key) => {
        expect(result.current).toHaveProperty(key);
      });
    });
  });
});
