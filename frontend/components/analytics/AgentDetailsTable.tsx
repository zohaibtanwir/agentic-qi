'use client';

/**
 * AgentDetailsTable Component
 * Table showing detailed metrics for each agent.
 */

import { AgentMetrics } from '@/lib/analytics/types';
import { getAgentDisplayName, getAgentIcon, getAgentColor, formatNumber } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface AgentDetailsTableProps {
  /**
   * Agent metrics data
   */
  data: AgentMetrics[];
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
// Loading Skeleton
// ============================================================================

function TableSkeleton() {
  return (
    <div className="animate-pulse" aria-busy="true" aria-label="Loading table">
      <div className="bg-gray-100 rounded-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gray-200 h-12 flex items-center px-4 gap-4">
          <div className="h-4 bg-gray-300 rounded w-24" />
          <div className="h-4 bg-gray-300 rounded w-16" />
          <div className="h-4 bg-gray-300 rounded w-16" />
          <div className="h-4 bg-gray-300 rounded w-20" />
          <div className="h-4 bg-gray-300 rounded w-16" />
          <div className="h-4 bg-gray-300 rounded w-20" />
        </div>
        {/* Rows */}
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-14 flex items-center px-4 gap-4 border-b border-gray-200">
            <div className="h-4 bg-gray-200 rounded w-28" />
            <div className="h-4 bg-gray-200 rounded w-14" />
            <div className="h-4 bg-gray-200 rounded w-14" />
            <div className="h-4 bg-gray-200 rounded w-16" />
            <div className="h-4 bg-gray-200 rounded w-14" />
            <div className="h-4 bg-gray-200 rounded w-16" />
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Change Badge Component
// ============================================================================

interface ChangeBadgeProps {
  value: number;
}

function ChangeBadge({ value }: ChangeBadgeProps) {
  const isPositive = value >= 0;
  const colorClass = isPositive ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50';

  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${colorClass}`}>
      {isPositive ? '+' : ''}{value}%
    </span>
  );
}

// ============================================================================
// Success Rate Badge Component
// ============================================================================

interface SuccessRateBadgeProps {
  rate: number;
}

function SuccessRateBadge({ rate }: SuccessRateBadgeProps) {
  const colorClass =
    rate >= 99 ? 'text-green-600 bg-green-50' :
    rate >= 95 ? 'text-yellow-600 bg-yellow-50' :
    'text-red-600 bg-red-50';

  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${colorClass}`}>
      {rate.toFixed(1)}%
    </span>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function AgentDetailsTable({
  data,
  className = '',
  isLoading = false,
}: AgentDetailsTableProps) {
  if (isLoading) {
    return (
      <div className={className}>
        <TableSkeleton />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-50 rounded-lg p-8 ${className}`}
        role="status"
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
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <p>No agent data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-sm" role="table" aria-label="Agent details">
        <thead>
          <tr className="bg-gray-50 text-left">
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)]">Agent</th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)] text-right">Requests</th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)] text-right">Tokens</th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)] text-right">Avg Tokens</th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)] text-right">Avg Time</th>
            <th className="px-4 py-3 font-medium text-[var(--text-secondary)] text-right">Success Rate</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--border-light)]">
          {data.map((agent) => {
            const displayName = getAgentDisplayName(agent.agent);
            const icon = getAgentIcon(agent.agent);
            const color = getAgentColor(agent.agent);

            return (
              <tr
                key={agent.agent}
                className="hover:bg-gray-50 transition-colors"
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-2 h-2 rounded-full flex-shrink-0"
                      style={{ backgroundColor: color }}
                      aria-hidden="true"
                    />
                    <span className="mr-1" aria-hidden="true">{icon}</span>
                    <span className="font-medium text-[var(--text-primary)]">
                      {displayName}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <span className="text-[var(--text-primary)]">
                      {agent.requests.toLocaleString()}
                    </span>
                    <ChangeBadge value={agent.requestsChange} />
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <span className="text-[var(--text-primary)]">
                      {formatNumber(agent.tokens)}
                    </span>
                    <ChangeBadge value={agent.tokensChange} />
                  </div>
                </td>
                <td className="px-4 py-3 text-right text-[var(--text-primary)]">
                  {agent.avgTokensPerRequest}
                </td>
                <td className="px-4 py-3 text-right text-[var(--text-primary)]">
                  {agent.avgResponseTime}s
                </td>
                <td className="px-4 py-3 text-right">
                  <SuccessRateBadge rate={agent.successRate} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default AgentDetailsTable;
