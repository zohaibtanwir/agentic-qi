'use client';

/**
 * RequestsByAgentChart Component
 * Bar chart showing requests by agent.
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
import { AGENT_CONFIG } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface AgentRequestData {
  agent: string;
  requests: number;
  change: number;
}

export interface RequestsByAgentChartProps {
  /**
   * Requests data by agent
   */
  data: AgentRequestData[];
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

const AGENT_COLORS: Record<string, string> = {
  'Req Analysis': AGENT_CONFIG.requirement_analysis.color,
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
    payload: AgentRequestData;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const data = payload[0].payload;
  const changeColor = data.change >= 0 ? 'text-green-600' : 'text-red-600';
  const changePrefix = data.change >= 0 ? '+' : '';

  return (
    <div className="bg-white p-3 rounded-lg shadow-lg border border-[var(--border-default)]">
      <p className="text-sm font-medium text-[var(--text-primary)] mb-1">
        {data.agent}
      </p>
      <p className="text-sm text-[var(--text-secondary)]">
        <span className="font-medium">{data.requests.toLocaleString()}</span> requests
      </p>
      <p className={`text-xs ${changeColor}`}>
        {changePrefix}{data.change}% vs. previous
      </p>
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
      <div className="w-12 h-1/4 bg-gray-200 rounded" />
      <div className="w-12 h-2/4 bg-gray-200 rounded" />
      <div className="w-12 h-1/3 bg-gray-200 rounded" />
      <div className="w-12 h-1/6 bg-gray-200 rounded" />
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function RequestsByAgentChart({
  data,
  height = 300,
  className = '',
  isLoading = false,
}: RequestsByAgentChartProps) {
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

  const totalRequests = data.reduce((sum, entry) => sum + entry.requests, 0);

  return (
    <div
      className={className}
      role="img"
      aria-label={`Bar chart showing requests by agent. Total: ${totalRequests.toLocaleString()} requests`}
    >
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="agent"
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#E5E7EB' }}
          />
          <YAxis
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#E5E7EB' }}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }} />
          <Bar dataKey="requests" radius={[4, 4, 0, 0]}>
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

export default RequestsByAgentChart;
