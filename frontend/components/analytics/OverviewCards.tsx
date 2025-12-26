'use client';

/**
 * OverviewCards Component
 * Displays key analytics metrics in a row of cards.
 */

import { OverviewMetrics, MetricData, ChangeDirection } from '@/lib/analytics/types';
import { formatPercentageChange } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface MetricCardConfig {
  key: keyof OverviewMetrics;
  title: string;
  icon: React.ReactNode;
  /**
   * Whether an increase is good (default: true)
   * For latency, lower is better so this would be false
   */
  increaseIsGood?: boolean;
}

export interface OverviewCardsProps {
  /**
   * Overview metrics data
   */
  metrics: OverviewMetrics;
  /**
   * Loading state
   */
  isLoading?: boolean;
  /**
   * Optional CSS class name
   */
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const METRIC_CARDS: MetricCardConfig[] = [
  {
    key: 'totalRequests',
    title: 'Total Requests',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
    ),
    increaseIsGood: true,
  },
  {
    key: 'testCasesGenerated',
    title: 'Test Cases Generated',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
        />
      </svg>
    ),
    increaseIsGood: true,
  },
  {
    key: 'totalTokens',
    title: 'Total Tokens',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
        />
      </svg>
    ),
    increaseIsGood: true,
  },
  {
    key: 'estimatedCost',
    title: 'Estimated Cost',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    increaseIsGood: true, // Assuming more cost means more usage which is good
  },
  {
    key: 'avgLatency',
    title: 'Avg Latency',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    increaseIsGood: false, // Lower latency is better
  },
];

// ============================================================================
// Helper Components
// ============================================================================

interface ChangeIndicatorProps {
  change: number;
  direction: ChangeDirection;
  increaseIsGood: boolean;
}

function ChangeIndicator({ change, direction, increaseIsGood }: ChangeIndicatorProps) {
  // Determine if this change is positive (good) based on direction and context
  const isPositiveChange =
    (direction === 'up' && increaseIsGood) ||
    (direction === 'down' && !increaseIsGood);

  const colorClass = isPositiveChange
    ? 'text-green-600 bg-green-50'
    : direction === 'neutral'
    ? 'text-gray-600 bg-gray-50'
    : 'text-red-600 bg-red-50';

  const ArrowIcon =
    direction === 'up' ? (
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"
          clipRule="evenodd"
        />
      </svg>
    ) : direction === 'down' ? (
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z"
          clipRule="evenodd"
        />
      </svg>
    ) : null;

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${colorClass}`}
      aria-label={`${formatPercentageChange(change)} compared to previous period`}
    >
      {ArrowIcon}
      <span>{formatPercentageChange(change)}</span>
    </span>
  );
}

interface MetricCardProps {
  config: MetricCardConfig;
  metric: MetricData;
  isLoading?: boolean;
}

function MetricCard({ config, metric, isLoading }: MetricCardProps) {
  const { title, icon, increaseIsGood = true } = config;

  if (isLoading) {
    return (
      <div
        className="bg-white rounded-lg border border-[var(--border-default)] p-4 shadow-sm animate-pulse"
        aria-busy="true"
      >
        <div className="flex items-center gap-2 mb-2">
          <div className="w-5 h-5 bg-gray-200 rounded" />
          <div className="h-4 w-20 bg-gray-200 rounded" />
        </div>
        <div className="h-8 w-24 bg-gray-200 rounded mb-2" />
        <div className="h-5 w-16 bg-gray-200 rounded" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-[var(--border-default)] p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[var(--text-muted)]" aria-hidden="true">
          {icon}
        </span>
        <span className="text-sm font-medium text-[var(--text-secondary)]">
          {title}
        </span>
      </div>

      {/* Value */}
      <div
        className="text-2xl font-bold text-[var(--text-primary)] mb-2"
        aria-label={`${title}: ${metric.formattedValue}`}
      >
        {metric.formattedValue}
      </div>

      {/* Change Indicator */}
      <ChangeIndicator
        change={metric.change}
        direction={metric.changeDirection}
        increaseIsGood={increaseIsGood}
      />
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function OverviewCards({
  metrics,
  isLoading = false,
  className = '',
}: OverviewCardsProps) {
  return (
    <div
      className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 ${className}`}
      role="region"
      aria-label="Overview metrics"
    >
      {METRIC_CARDS.map((config) => (
        <MetricCard
          key={config.key}
          config={config}
          metric={metrics[config.key]}
          isLoading={isLoading}
        />
      ))}
    </div>
  );
}

export default OverviewCards;
