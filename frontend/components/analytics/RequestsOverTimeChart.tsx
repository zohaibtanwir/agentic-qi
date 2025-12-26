'use client';

/**
 * RequestsOverTimeChart Component
 * Line chart showing requests over time for each agent.
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TimeSeriesDataPoint, TimeGranularity } from '@/lib/analytics/types';
import { AGENT_CONFIG } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface RequestsOverTimeChartProps {
  /**
   * Time series data points
   */
  data: TimeSeriesDataPoint[];
  /**
   * Current granularity (for display purposes)
   */
  granularity?: TimeGranularity;
  /**
   * Height of the chart
   */
  height?: number;
  /**
   * Optional CSS class name
   */
  className?: string;
  /**
   * Loading state
   */
  isLoading?: boolean;
}

// ============================================================================
// Constants
// ============================================================================

const AGENT_LINES = [
  {
    dataKey: 'requirementAnalysis',
    name: 'Requirement Analysis',
    color: AGENT_CONFIG.requirement_analysis.color,
  },
  {
    dataKey: 'testCases',
    name: 'Test Cases',
    color: AGENT_CONFIG.test_cases.color,
  },
  {
    dataKey: 'testData',
    name: 'Test Data',
    color: AGENT_CONFIG.test_data.color,
  },
  {
    dataKey: 'domain',
    name: 'Domain',
    color: AGENT_CONFIG.domain.color,
  },
];

// ============================================================================
// Custom Tooltip
// ============================================================================

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    dataKey: string;
    value: number;
    color: string;
    name: string;
  }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const total = payload.reduce((sum, entry) => sum + entry.value, 0);

  return (
    <div className="bg-white p-3 rounded-lg shadow-lg border border-[var(--border-default)]">
      <p className="text-sm font-medium text-[var(--text-primary)] mb-2">
        {label}
      </p>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex items-center justify-between gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-[var(--text-secondary)]">{entry.name}</span>
          </div>
          <span className="font-medium text-[var(--text-primary)]">
            {entry.value}
          </span>
        </div>
      ))}
      <div className="mt-2 pt-2 border-t border-[var(--border-light)] flex items-center justify-between text-sm">
        <span className="text-[var(--text-secondary)]">Total</span>
        <span className="font-bold text-[var(--text-primary)]">{total}</span>
      </div>
    </div>
  );
}

// ============================================================================
// Loading Skeleton
// ============================================================================

function ChartSkeleton({ height }: { height: number }) {
  return (
    <div
      className="animate-pulse bg-gray-100 rounded-lg flex items-center justify-center"
      style={{ height }}
      aria-busy="true"
      aria-label="Loading chart"
    >
      <div className="text-center">
        <svg
          className="w-12 h-12 text-gray-300 mx-auto mb-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
        <span className="text-gray-400 text-sm">Loading chart...</span>
      </div>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function RequestsOverTimeChart({
  data,
  granularity = 'day',
  height = 300,
  className = '',
  isLoading = false,
}: RequestsOverTimeChartProps) {
  if (isLoading) {
    return (
      <div className={className}>
        <ChartSkeleton height={height} />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-50 rounded-lg ${className}`}
        style={{ height }}
        role="img"
        aria-label="No data available"
      >
        <div className="text-center text-[var(--text-muted)]">
          <svg
            className="w-12 h-12 mx-auto mb-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M20 12H4"
            />
          </svg>
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={className}
      role="img"
      aria-label={`Line chart showing requests over time by agent for ${data.length} ${granularity}s`}
    >
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="date"
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            tickLine={{ stroke: '#E5E7EB' }}
            axisLine={{ stroke: '#E5E7EB' }}
          />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            tickLine={{ stroke: '#E5E7EB' }}
            axisLine={{ stroke: '#E5E7EB' }}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="circle"
            iconSize={8}
          />
          {AGENT_LINES.map((line) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              name={line.name}
              stroke={line.color}
              strokeWidth={2}
              dot={{ fill: line.color, strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5, strokeWidth: 0 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default RequestsOverTimeChart;
