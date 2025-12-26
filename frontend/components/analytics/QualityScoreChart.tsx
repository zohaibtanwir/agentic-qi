'use client';

/**
 * QualityScoreChart Component
 * Bar chart showing quality distribution by grade.
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
import { QualityDistribution } from '@/lib/analytics/types';
import { GRADE_CONFIG } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface QualityScoreChartProps {
  /**
   * Quality distribution data
   */
  data: QualityDistribution[];
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
// Custom Tooltip
// ============================================================================

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: QualityDistribution;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const data = payload[0].payload;
  const config = GRADE_CONFIG[data.grade];

  return (
    <div className="bg-white p-3 rounded-lg shadow-lg border border-[var(--border-default)]">
      <div className="flex items-center gap-2 mb-1">
        <div
          className="w-3 h-3 rounded"
          style={{ backgroundColor: config.color }}
        />
        <span className="text-sm font-medium text-[var(--text-primary)]">
          Grade {data.grade}
        </span>
      </div>
      <p className="text-sm text-[var(--text-secondary)]">
        <span className="font-medium">{data.count}</span> analyses ({data.percentage}%)
      </p>
      <p className="text-xs text-[var(--text-muted)]">{config.label}</p>
    </div>
  );
}

// ============================================================================
// Loading Skeleton
// ============================================================================

function ChartSkeleton({ height }: { height: number }) {
  return (
    <div
      className="animate-pulse bg-gray-100 rounded-lg flex items-end justify-around px-4 pb-4"
      style={{ height }}
      aria-busy="true"
      aria-label="Loading chart"
    >
      <div className="w-10 h-1/6 bg-gray-200 rounded" />
      <div className="w-10 h-1/4 bg-gray-200 rounded" />
      <div className="w-10 h-2/4 bg-gray-200 rounded" />
      <div className="w-10 h-1/3 bg-gray-200 rounded" />
      <div className="w-10 h-1/5 bg-gray-200 rounded" />
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function QualityScoreChart({
  data,
  height = 250,
  className = '',
  isLoading = false,
}: QualityScoreChartProps) {
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

  const totalCount = data.reduce((sum, entry) => sum + entry.count, 0);

  return (
    <div
      className={className}
      role="img"
      aria-label={`Bar chart showing quality distribution. Total: ${totalCount} analyses`}
    >
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="grade"
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#E5E7EB' }}
          />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#E5E7EB' }}
            width={35}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={GRADE_CONFIG[entry.grade]?.color || '#6B7280'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default QualityScoreChart;
