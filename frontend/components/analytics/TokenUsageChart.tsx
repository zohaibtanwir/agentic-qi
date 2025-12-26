'use client';

/**
 * TokenUsageChart Component
 * Donut chart showing token usage distribution by agent.
 */

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { TokenUsageByAgent } from '@/lib/analytics/types';
import { formatNumber } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface TokenUsageChartProps {
  /**
   * Token usage data by agent
   */
  data: TokenUsageByAgent[];
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
   * Show legend
   */
  showLegend?: boolean;
}

// ============================================================================
// Custom Tooltip
// ============================================================================

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: TokenUsageByAgent;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div className="bg-white p-3 rounded-lg shadow-lg border border-[var(--border-default)]">
      <div className="flex items-center gap-2 mb-1">
        <div
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: data.color }}
        />
        <span className="text-sm font-medium text-[var(--text-primary)]">
          {data.agent}
        </span>
      </div>
      <div className="text-sm text-[var(--text-secondary)]">
        <span className="font-medium">{formatNumber(data.tokens)}</span> tokens
        <span className="ml-2">({data.percentage}%)</span>
      </div>
    </div>
  );
}

// ============================================================================
// Custom Legend
// ============================================================================

interface CustomLegendProps {
  payload?: Array<{
    value: string;
    color: string;
    payload: TokenUsageByAgent;
  }>;
}

function CustomLegend({ payload }: CustomLegendProps) {
  if (!payload) return null;

  return (
    <ul className="flex flex-wrap justify-center gap-4 mt-4">
      {payload.map((entry, index) => (
        <li key={index} className="flex items-center gap-2 text-sm">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-[var(--text-secondary)]">{entry.value}</span>
          <span className="text-[var(--text-muted)]">
            ({entry.payload.percentage}%)
          </span>
        </li>
      ))}
    </ul>
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
      <div className="w-32 h-32 rounded-full bg-gray-200" />
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function TokenUsageChart({
  data,
  height = 300,
  className = '',
  isLoading = false,
  showLegend = true,
}: TokenUsageChartProps) {
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

  const totalTokens = data.reduce((sum, entry) => sum + entry.tokens, 0);

  return (
    <div
      className={className}
      role="img"
      aria-label={`Donut chart showing token usage by agent. Total: ${formatNumber(totalTokens)} tokens`}
    >
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            dataKey="tokens"
            nameKey="agent"
            paddingAngle={2}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          {showLegend && <Legend content={<CustomLegend />} />}
        </PieChart>
      </ResponsiveContainer>

      {/* Center Label */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="text-center">
          <div className="text-2xl font-bold text-[var(--text-primary)]">
            {formatNumber(totalTokens)}
          </div>
          <div className="text-xs text-[var(--text-muted)]">Total Tokens</div>
        </div>
      </div>
    </div>
  );
}

export default TokenUsageChart;
