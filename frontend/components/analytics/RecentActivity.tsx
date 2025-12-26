'use client';

/**
 * RecentActivity Component
 * List of recent analytics activity items.
 */

import { ActivityItem } from '@/lib/analytics/types';
import { getAgentDisplayName, getAgentIcon, getAgentColor, formatTimestamp, formatNumber } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface RecentActivityProps {
  /**
   * Activity items
   */
  data: ActivityItem[];
  /**
   * Maximum number of items to display
   */
  maxItems?: number;
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

function ActivitySkeleton({ count }: { count: number }) {
  return (
    <div className="animate-pulse space-y-3" aria-busy="true" aria-label="Loading activities">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
          <div className="w-8 h-8 bg-gray-200 rounded-full" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4" />
            <div className="h-3 bg-gray-200 rounded w-1/2" />
          </div>
          <div className="h-4 bg-gray-200 rounded w-12" />
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// Activity Item Component
// ============================================================================

interface ActivityItemCardProps {
  item: ActivityItem;
}

function ActivityItemCard({ item }: ActivityItemCardProps) {
  const displayName = getAgentDisplayName(item.agent);
  const icon = getAgentIcon(item.agent);
  const color = getAgentColor(item.agent);

  return (
    <div className="flex items-start gap-3 p-3 bg-white rounded-lg border border-[var(--border-light)] hover:border-[var(--border-default)] transition-colors">
      {/* Icon */}
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: `${color}20` }}
        aria-hidden="true"
      >
        <span className="text-sm">{icon}</span>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="text-sm font-medium text-[var(--text-primary)] truncate">
            {item.action} {item.title}
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
          <span>{displayName}</span>
          {item.metric && (
            <>
              <span>•</span>
              <span className="text-[var(--accent-default)]">{item.metric}</span>
            </>
          )}
          <span>•</span>
          <span>{formatNumber(item.tokens)} tokens</span>
        </div>
      </div>

      {/* Time */}
      <div className="text-xs text-[var(--text-muted)] flex-shrink-0">
        {formatTimestamp(item.timestamp)}
      </div>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function RecentActivity({
  data,
  maxItems = 8,
  className = '',
  isLoading = false,
}: RecentActivityProps) {
  if (isLoading) {
    return (
      <div className={className}>
        <ActivitySkeleton count={maxItems} />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-50 rounded-lg p-8 ${className}`}
        role="status"
        aria-label="No recent activity"
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
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p>No recent activity</p>
        </div>
      </div>
    );
  }

  const displayedItems = data.slice(0, maxItems);

  return (
    <div className={className} role="list" aria-label="Recent activity">
      <div className="space-y-2">
        {displayedItems.map((item) => (
          <ActivityItemCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}

export default RecentActivity;
