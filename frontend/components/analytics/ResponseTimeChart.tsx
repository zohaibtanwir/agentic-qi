'use client';

/**
 * ResponseTimeChart Component
 * Horizontal bar chart showing response time by agent.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { ResponseTimeByAgent } from '@/lib/analytics/types';
import { AGENT_CONFIG } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface ResponseTimeChartProps {
  /**
   * Response time data by agent
   */
  data: ResponseTimeByAgent[];
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
  /**
   * Which metric to display (avg, p50, p95, p99)
   */
  metric?: 'avgTime' | 'p50' | 'p95' | 'p99';
}

// ============================================================================
// Constants
// ============================================================================

const AGENT_COLORS: Record<string, string> = {
  'Requirement Analysis': AGENT_CONFIG.requirement_analysis.color,
  'Test Cases': AGENT_CONFIG.test_cases.color,
  'Test Data': AGENT_CONFIG.test_data.color,
  Domain: AGENT_CONFIG.domain.color,
};

// ============================================================================
// Custom Tooltip
// ============================================================================

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: ResponseTimeByAgent;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div className="bg-white p-3 rounded-lg shadow-lg border border-[var(--border-default)]">
      <p className="text-sm font-medium text-[var(--text-primary)] mb-2">
        {data.agent}
      </p>
      <div className="space-y-1 text-sm">
        <div className="flex justify-between gap-4">
          <span className="text-[var(--text-secondary)]">Average:</span>
          <span className="font-medium text-[var(--text-primary)]">{data.avgTime}s</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-[var(--text-secondary)]">P50:</span>
          <span className="text-[var(--text-primary)]">{data.p50}s</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-[var(--text-secondary)]">P95:</span>
          <span className="text-[var(--text-primary)]">{data.p95}s</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-[var(--text-secondary)]">P99:</span>
          <span className="text-[var(--text-primary)]">{data.p99}s</span>
        </div>
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
      className="animate-pulse bg-gray-100 rounded-lg flex flex-col justify-around p-4"
      style={{ height }}
      aria-busy="true"
      aria-label="Loading chart"
    >
      <div className="flex items-center gap-4">
        <div className="w-20 h-4 bg-gray-200 rounded" />
        <div className="flex-1 h-6 bg-gray-200 rounded" style={{ width: '80%' }} />
      </div>
      <div className="flex items-center gap-4">
        <div className="w-20 h-4 bg-gray-200 rounded" />
        <div className="flex-1 h-6 bg-gray-200 rounded" style={{ width: '70%' }} />
      </div>
      <div className="flex items-center gap-4">
        <div className="w-20 h-4 bg-gray-200 rounded" />
        <div className="flex-1 h-6 bg-gray-200 rounded" style={{ width: '50%' }} />
      </div>
      <div className="flex items-center gap-4">
        <div className="w-20 h-4 bg-gray-200 rounded" />
        <div className="flex-1 h-6 bg-gray-200 rounded" style={{ width: '20%' }} />
      </div>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function ResponseTimeChart({
  data,
  height = 250,
  className = '',
  isLoading = false,
  metric = 'avgTime',
}: ResponseTimeChartProps) {
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

  const metricLabel = {
    avgTime: 'Average',
    p50: 'P50',
    p95: 'P95',
    p99: 'P99',
  }[metric];

  return (
    <div
      className={className}
      role="img"
      aria-label={`Horizontal bar chart showing ${metricLabel} response time by agent`}
    >
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 20, left: 80, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#E5E7EB' }}
            tickFormatter={(value) => `${value}s`}
          />
          <YAxis
            type="category"
            dataKey="agent"
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#E5E7EB' }}
            width={75}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }} />
          <Bar dataKey={metric} radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={AGENT_COLORS[entry.agent] || '#6B7280'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ResponseTimeChart;
