'use client';

/**
 * Analytics Dashboard Page
 * Phase 1: UI with dummy data
 * Displays comprehensive analytics for all QA platform agents.
 */

import { useState } from 'react';
import { useAnalytics } from '@/hooks/useAnalytics';
import {
  DateRangeSelector,
  ExportButton,
  OverviewCards,
  RequestsOverTimeChart,
  TokenUsageChart,
  RequestsByAgentChart,
  QualityScoreChart,
  ResponseTimeChart,
  AgentDetailsTable,
  RecentActivity,
} from '@/components/analytics';
import { TimeGranularity } from '@/lib/analytics/types';

// ============================================================================
// Granularity Selector Component
// ============================================================================

interface GranularitySelectorProps {
  value: TimeGranularity;
  onChange: (granularity: TimeGranularity) => void;
}

function GranularitySelector({ value, onChange }: GranularitySelectorProps) {
  const options: { value: TimeGranularity; label: string }[] = [
    { value: 'hour', label: 'Hour' },
    { value: 'day', label: 'Day' },
    { value: 'week', label: 'Week' },
  ];

  return (
    <div className="flex items-center gap-1 bg-[var(--surface-secondary)] rounded-lg p-1" role="radiogroup" aria-label="Time granularity">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
            value === option.value
              ? 'bg-white text-[var(--text-primary)] shadow-sm'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          role="radio"
          aria-checked={value === option.value}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

// ============================================================================
// Response Time Metric Selector
// ============================================================================

type ResponseTimeMetric = 'avgTime' | 'p50' | 'p95' | 'p99';

interface MetricSelectorProps {
  value: ResponseTimeMetric;
  onChange: (metric: ResponseTimeMetric) => void;
}

function MetricSelector({ value, onChange }: MetricSelectorProps) {
  const options: { value: ResponseTimeMetric; label: string }[] = [
    { value: 'avgTime', label: 'Avg' },
    { value: 'p50', label: 'P50' },
    { value: 'p95', label: 'P95' },
    { value: 'p99', label: 'P99' },
  ];

  return (
    <div className="flex items-center gap-1" role="radiogroup" aria-label="Response time metric">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
            value === option.value
              ? 'bg-[var(--accent-default)] text-white'
              : 'text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)]'
          }`}
          role="radio"
          aria-checked={value === option.value}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

// ============================================================================
// Section Header Component
// ============================================================================

interface SectionHeaderProps {
  title: string;
  actions?: React.ReactNode;
}

function SectionHeader({ title, actions }: SectionHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h2>
      {actions}
    </div>
  );
}

// ============================================================================
// Card Wrapper Component
// ============================================================================

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-[var(--surface-primary)] rounded-xl border border-[var(--border-default)] p-6 ${className}`}>
      {children}
    </div>
  );
}

// ============================================================================
// Main Page Component
// ============================================================================

export default function AnalyticsPage() {
  const {
    dateRange,
    setDateRange,
    granularity,
    setGranularity,
    data,
    timeSeriesData,
    tokenUsageByAgent,
    responseTimeByAgent,
    isLoading,
  } = useAnalytics();

  const [responseTimeMetric, setResponseTimeMetric] = useState<ResponseTimeMetric>('avgTime');

  // Prepare export data - flatten for CSV/JSON export
  const exportData = data.byAgent.map((agent) => ({
    agent: agent.agent,
    requests: agent.requests,
    requestsChange: agent.requestsChange,
    tokens: agent.tokens,
    tokensChange: agent.tokensChange,
    avgTokensPerRequest: agent.avgTokensPerRequest,
    avgResponseTime: agent.avgResponseTime,
    successRate: agent.successRate,
  }));

  // Transform data for RequestsByAgentChart
  const requestsByAgentData = data.byAgent.map((agent) => ({
    agent: agent.agent,
    requests: agent.requests,
    change: agent.requestsChange,
  }));

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-[var(--accent-default)] rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                Analytics Dashboard
              </h1>
              <p className="text-sm text-[var(--text-muted)] mt-0.5">
                Platform usage and performance metrics
              </p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-3">
            <DateRangeSelector
              value={dateRange}
              onChange={setDateRange}
            />
            <ExportButton
              data={exportData}
              filename="qa-platform-analytics"
              formats={['csv', 'json']}
            />
          </div>
        </div>
      </div>

      {/* Overview Cards */}
      <section className="mb-8" aria-labelledby="overview-heading">
        <h2 id="overview-heading" className="sr-only">Overview Metrics</h2>
        <OverviewCards metrics={data.overview} isLoading={isLoading} />
      </section>

      {/* Charts Section - Row 1 */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6" aria-labelledby="charts-heading">
        <h2 id="charts-heading" className="sr-only">Analytics Charts</h2>

        {/* Requests Over Time - Takes 2 columns */}
        <Card className="lg:col-span-2">
          <SectionHeader
            title="Requests Over Time"
            actions={
              <GranularitySelector
                value={granularity}
                onChange={setGranularity}
              />
            }
          />
          <RequestsOverTimeChart
            data={timeSeriesData}
            granularity={granularity}
            height={300}
            isLoading={isLoading}
          />
        </Card>

        {/* Token Usage */}
        <Card>
          <SectionHeader title="Token Usage by Agent" />
          <TokenUsageChart
            data={tokenUsageByAgent}
            height={300}
            isLoading={isLoading}
          />
        </Card>
      </section>

      {/* Charts Section - Row 2 */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Requests by Agent */}
        <Card>
          <SectionHeader title="Requests by Agent" />
          <RequestsByAgentChart
            data={requestsByAgentData}
            height={280}
            isLoading={isLoading}
          />
        </Card>

        {/* Quality Distribution */}
        <Card>
          <SectionHeader title="Quality Distribution" />
          <QualityScoreChart
            data={data.qualityDistribution}
            height={280}
            isLoading={isLoading}
          />
        </Card>

        {/* Response Time */}
        <Card>
          <SectionHeader
            title="Response Time"
            actions={
              <MetricSelector
                value={responseTimeMetric}
                onChange={setResponseTimeMetric}
              />
            }
          />
          <ResponseTimeChart
            data={responseTimeByAgent}
            metric={responseTimeMetric}
            height={280}
            isLoading={isLoading}
          />
        </Card>
      </section>

      {/* Data Tables Section */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6" aria-labelledby="details-heading">
        <h2 id="details-heading" className="sr-only">Detailed Data</h2>

        {/* Agent Details Table - Takes 2 columns */}
        <Card className="lg:col-span-2">
          <SectionHeader title="Agent Details" />
          <AgentDetailsTable
            data={data.byAgent}
            isLoading={isLoading}
          />
        </Card>

        {/* Recent Activity */}
        <Card>
          <SectionHeader title="Recent Activity" />
          <RecentActivity
            data={data.recentActivity}
            maxItems={6}
            isLoading={isLoading}
          />
        </Card>
      </section>
    </main>
  );
}
