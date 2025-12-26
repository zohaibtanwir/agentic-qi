# Analytics Dashboard - PRD

## Overview

The Analytics Dashboard provides insights into QA Platform usage across all four agents. It displays request volumes, token consumption, quality metrics, performance data, and cost tracking.

**Implementation Approach:** UI-first with dummy data. Backend integration in Phase 2.

---

## Project Info

| Item | Value |
|------|-------|
| Location | `qa-platform/frontend/src/app/analytics` |
| Framework | Next.js 14 (App Router) |
| Charts | Recharts |
| Styling | Tailwind CSS (Macy's theme) |
| Phase 1 | UI with dummy data |
| Phase 2 | Backend integration (future) |

---

## Architecture

### Phase 1: UI Only (Current Scope)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                       │
│                                                                          │
│   Analytics Page                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                                                                   │  │
│   │   Components ──────▶ Dummy Data Store ──────▶ UI Render          │  │
│   │                      (static JSON)                                │  │
│   │                                                                   │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 2: With Backend (Future)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                       │
│                                                                          │
│   Analytics Page                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                                                                   │  │
│   │   Components ──────▶ React Query ──────▶ API Routes ────────────┼──┼─┐
│   │                                                                   │  │ │
│   └──────────────────────────────────────────────────────────────────┘  │ │
│                                                                          │ │
└─────────────────────────────────────────────────────────────────────────┘ │
                                                                             │
┌─────────────────────────────────────────────────────────────────────────┐ │
│                        BACKEND (Phase 2)                                 │ │
│                                                                          │ │
│   ┌────────────────┐    ┌────────────────┐    ┌────────────────┐       │ │
│   │ Analytics DB   │◀───│ Analytics API  │◀───│ BFF Route      │◀──────┘ │
│   │ (PostgreSQL)   │    │ (New Service)  │    │ /api/analytics │         │
│   └────────────────┘    └────────────────┘    └────────────────┘         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Page Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌─────┐                                                                    │
│  │ ☰   │  Analytics                              [Last 7 Days ▼]  [Export]  │
│  └─────┘                                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  OVERVIEW CARDS                                                             │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐    │
│  │ Total     │ │ Test Cases│ │ Total     │ │ Est. Cost │ │ Avg       │    │
│  │ Requests  │ │ Generated │ │ Tokens    │ │           │ │ Latency   │    │
│  │   1,247   │ │   1,842   │ │   142K    │ │   $4.25   │ │   12.3s   │    │
│  │  ▲ 12%    │ │  ▲ 8%     │ │  ▲ 15%    │ │  ▲ 10%    │ │  ▼ 5%     │    │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  REQUESTS OVER TIME                                    [Day ▼]      │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │                         📈 Line Chart                          │  │   │
│  │  │     Req Analysis ── Test Cases ── Test Data ── Domain         │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌────────────────────────────────┐  ┌────────────────────────────────┐   │
│  │  TOKEN USAGE BY AGENT          │  │  REQUESTS BY AGENT             │   │
│  │  ┌──────────────────────────┐  │  │  ┌──────────────────────────┐  │   │
│  │  │                          │  │  │  │                          │  │   │
│  │  │     🍩 Donut Chart       │  │  │  │     📊 Bar Chart         │  │   │
│  │  │                          │  │  │  │                          │  │   │
│  │  └──────────────────────────┘  │  │  └──────────────────────────┘  │   │
│  │  ▪ Req Analysis    45K (32%)   │  │  ▪ Req Analysis    247        │   │
│  │  ▪ Test Cases      68K (48%)   │  │  ▪ Test Cases      523        │   │
│  │  ▪ Test Data       18K (13%)   │  │  ▪ Test Data       312        │   │
│  │  ▪ Domain          10K (7%)    │  │  ▪ Domain          165        │   │
│  └────────────────────────────────┘  └────────────────────────────────┘   │
│                                                                             │
│  ┌────────────────────────────────┐  ┌────────────────────────────────┐   │
│  │  QUALITY SCORES (Req Analysis) │  │  AVG RESPONSE TIME BY AGENT    │   │
│  │  ┌──────────────────────────┐  │  │  ┌──────────────────────────┐  │   │
│  │  │                          │  │  │  │                          │  │   │
│  │  │     📊 Bar Chart         │  │  │  │     📊 Horizontal Bar    │  │   │
│  │  │     A  B  C  D  F        │  │  │  │                          │  │   │
│  │  └──────────────────────────┘  │  │  └──────────────────────────┘  │   │
│  │  Avg Score: 76 (C+)            │  │  Platform Avg: 11.2s           │   │
│  └────────────────────────────────┘  └────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  AGENT DETAILS                                                      │   │
│  │  ┌─────────────────┬─────────────────┬─────────────────┬──────────┐ │   │
│  │  │ Agent           │ Requests        │ Tokens          │ Avg Time │ │   │
│  │  ├─────────────────┼─────────────────┼─────────────────┼──────────┤ │   │
│  │  │ Req Analysis    │ 247 (▲12%)      │ 45,230          │ 14.2s    │ │   │
│  │  │ Test Cases      │ 523 (▲8%)       │ 68,450          │ 12.8s    │ │   │
│  │  │ Test Data       │ 312 (▲15%)      │ 18,200          │ 8.4s     │ │   │
│  │  │ Domain          │ 165 (▲5%)       │ 9,850           │ 2.1s     │ │   │
│  │  └─────────────────┴─────────────────┴─────────────────┴──────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  RECENT ACTIVITY                                          [View All] │   │
│  │  ───────────────────────────────────────────────────────────────────│   │
│  │  🔍 12:34  Requirement Analysis  "Guest Checkout"    72/100   2.3K  │   │
│  │  🧪 12:30  Test Cases Generated  "Product Reviews"   8 cases  1.8K  │   │
│  │  📦 12:28  Test Data Generated   "Customer Entity"   50 recs  0.4K  │   │
│  │  🏢 12:25  Domain Query          "Payment Workflow"  --       0.2K  │   │
│  │  🔍 12:20  Requirement Analysis  "Wishlist Feature"  85/100   2.1K  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
frontend/src/
├── app/
│   └── analytics/
│       ├── page.tsx                    # Main analytics page
│       └── loading.tsx                 # Loading skeleton
│
├── components/
│   └── analytics/
│       ├── OverviewCards.tsx           # Top metric cards
│       ├── RequestsOverTimeChart.tsx   # Line chart
│       ├── TokenUsageChart.tsx         # Donut chart
│       ├── RequestsByAgentChart.tsx    # Bar chart
│       ├── QualityScoreChart.tsx       # Bar chart for A/B/C/D/F
│       ├── ResponseTimeChart.tsx       # Horizontal bar chart
│       ├── AgentDetailsTable.tsx       # Summary table
│       ├── RecentActivity.tsx          # Activity feed
│       ├── DateRangeSelector.tsx       # Date filter dropdown
│       └── ExportButton.tsx            # Export functionality
│
├── lib/
│   └── analytics/
│       ├── dummy-data.ts               # All dummy data
│       ├── types.ts                    # TypeScript types
│       └── utils.ts                    # Helper functions
│
└── hooks/
    └── useAnalytics.ts                 # Data fetching hook (dummy for now)
```

---

## Components Specification

### 1. OverviewCards

Displays 5 key metrics at the top.

```tsx
interface OverviewCardProps {
  title: string;
  value: string | number;
  change: number;          // Percentage change
  changeLabel: string;     // e.g., "vs last period"
  icon?: React.ReactNode;
}

interface OverviewCardsProps {
  data: {
    totalRequests: MetricData;
    testCasesGenerated: MetricData;
    totalTokens: MetricData;
    estimatedCost: MetricData;
    avgLatency: MetricData;
  };
}
```

**Cards:**
| Card | Value Format | Icon |
|------|--------------|------|
| Total Requests | Number (1,247) | 📊 |
| Test Cases Generated | Number (1,842) | 🧪 |
| Total Tokens | Number with K/M (142K) | 🎫 |
| Estimated Cost | Currency ($4.25) | 💰 |
| Avg Latency | Seconds (12.3s) | ⏱️ |

---

### 2. RequestsOverTimeChart

Line chart showing request volume over time.

```tsx
interface RequestsOverTimeProps {
  data: {
    date: string;
    requirementAnalysis: number;
    testCases: number;
    testData: number;
    domain: number;
  }[];
  granularity: 'day' | 'week' | 'month';
}
```

**Features:**
- Toggle granularity (Day/Week/Month)
- Hover tooltip with exact values
- Legend with color coding
- Responsive sizing

---

### 3. TokenUsageChart

Donut chart showing token distribution by agent.

```tsx
interface TokenUsageChartProps {
  data: {
    agent: string;
    tokens: number;
    percentage: number;
    color: string;
  }[];
  totalTokens: number;
}
```

**Colors (Macy's theme):**
| Agent | Color |
|-------|-------|
| Requirement Analysis | `#E21A2C` (Macy's Red) |
| Test Cases | `#1E3A5F` (Navy) |
| Test Data | `#2E7D32` (Green) |
| Domain | `#F59E0B` (Amber) |

---

### 4. RequestsByAgentChart

Vertical bar chart showing request counts.

```tsx
interface RequestsByAgentChartProps {
  data: {
    agent: string;
    requests: number;
    change: number;
  }[];
}
```

---

### 5. QualityScoreChart

Bar chart showing distribution of quality grades (Requirement Analysis only).

```tsx
interface QualityScoreChartProps {
  data: {
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
    count: number;
    percentage: number;
  }[];
  averageScore: number;
  averageGrade: string;
}
```

**Grade Colors:**
| Grade | Color | Range |
|-------|-------|-------|
| A | `#22C55E` (Green) | 90-100 |
| B | `#84CC16` (Lime) | 80-89 |
| C | `#F59E0B` (Amber) | 70-79 |
| D | `#F97316` (Orange) | 60-69 |
| F | `#EF4444` (Red) | 0-59 |

---

### 6. ResponseTimeChart

Horizontal bar chart comparing agent response times.

```tsx
interface ResponseTimeChartProps {
  data: {
    agent: string;
    avgTime: number;      // seconds
    p50: number;
    p95: number;
    p99: number;
  }[];
  platformAvg: number;
}
```

---

### 7. AgentDetailsTable

Summary table with all agent metrics.

```tsx
interface AgentDetailsTableProps {
  data: {
    agent: string;
    requests: number;
    requestsChange: number;
    tokens: number;
    avgTokensPerRequest: number;
    avgTime: number;
    successRate: number;
  }[];
}
```

**Columns:**
| Column | Format |
|--------|--------|
| Agent | Name with icon |
| Requests | Number with % change |
| Tokens | Number |
| Tokens/Request | Number |
| Avg Time | Seconds |
| Success Rate | Percentage |

---

### 8. RecentActivity

Feed showing latest platform activity.

```tsx
interface ActivityItem {
  id: string;
  timestamp: string;
  agent: 'requirement_analysis' | 'test_cases' | 'test_data' | 'domain';
  action: string;
  title: string;
  metric?: string;        // e.g., "72/100" or "8 cases"
  tokens: number;
}

interface RecentActivityProps {
  items: ActivityItem[];
  limit?: number;
}
```

**Icons by Agent:**
| Agent | Icon |
|-------|------|
| Requirement Analysis | 🔍 |
| Test Cases | 🧪 |
| Test Data | 📦 |
| Domain | 🏢 |

---

### 9. DateRangeSelector

Dropdown for selecting time range.

```tsx
interface DateRangeSelectorProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
}

type DateRange = 'today' | 'last_7_days' | 'last_30_days' | 'last_90_days' | 'this_month' | 'last_month' | 'custom';
```

**Options:**
- Today
- Last 7 Days (default)
- Last 30 Days
- Last 90 Days
- This Month
- Last Month
- Custom Range (date picker)

---

### 10. ExportButton

Export analytics data.

```tsx
interface ExportButtonProps {
  onExport: (format: 'csv' | 'pdf') => void;
}
```

**Phase 1:** Export to CSV only (client-side generation from dummy data)
**Phase 2:** Add PDF export with backend support

---

## TypeScript Types

```typescript
// lib/analytics/types.ts

export interface MetricData {
  value: number;
  formattedValue: string;
  change: number;
  changeDirection: 'up' | 'down' | 'neutral';
}

export interface AgentMetrics {
  agent: AgentType;
  requests: number;
  requestsChange: number;
  tokens: number;
  tokensChange: number;
  avgTokensPerRequest: number;
  avgResponseTime: number;
  successRate: number;
  errorRate: number;
}

export type AgentType = 
  | 'requirement_analysis' 
  | 'test_cases' 
  | 'test_data' 
  | 'domain';

export interface TimeSeriesDataPoint {
  date: string;
  requirementAnalysis: number;
  testCases: number;
  testData: number;
  domain: number;
}

export interface QualityDistribution {
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  count: number;
  percentage: number;
}

export interface ActivityItem {
  id: string;
  timestamp: string;
  agent: AgentType;
  action: string;
  title: string;
  metric?: string;
  tokens: number;
}

export interface AnalyticsSummary {
  dateRange: {
    start: string;
    end: string;
    label: string;
  };
  overview: {
    totalRequests: MetricData;
    testCasesGenerated: MetricData;
    totalTokens: MetricData;
    estimatedCost: MetricData;
    avgLatency: MetricData;
  };
  byAgent: AgentMetrics[];
  requestsOverTime: TimeSeriesDataPoint[];
  qualityDistribution: QualityDistribution[];
  recentActivity: ActivityItem[];
}
```

---

## Dummy Data

```typescript
// lib/analytics/dummy-data.ts

import { AnalyticsSummary, TimeSeriesDataPoint, ActivityItem } from './types';

export const DUMMY_ANALYTICS: AnalyticsSummary = {
  dateRange: {
    start: '2024-12-18',
    end: '2024-12-24',
    label: 'Last 7 Days',
  },
  
  overview: {
    totalRequests: {
      value: 1247,
      formattedValue: '1,247',
      change: 12,
      changeDirection: 'up',
    },
    testCasesGenerated: {
      value: 1842,
      formattedValue: '1,842',
      change: 8,
      changeDirection: 'up',
    },
    totalTokens: {
      value: 141730,
      formattedValue: '142K',
      change: 15,
      changeDirection: 'up',
    },
    estimatedCost: {
      value: 4.25,
      formattedValue: '$4.25',
      change: 10,
      changeDirection: 'up',
    },
    avgLatency: {
      value: 12.3,
      formattedValue: '12.3s',
      change: -5,
      changeDirection: 'down',
    },
  },
  
  byAgent: [
    {
      agent: 'requirement_analysis',
      requests: 247,
      requestsChange: 12,
      tokens: 45230,
      tokensChange: 14,
      avgTokensPerRequest: 183,
      avgResponseTime: 14.2,
      successRate: 98.4,
      errorRate: 1.6,
    },
    {
      agent: 'test_cases',
      requests: 523,
      requestsChange: 8,
      tokens: 68450,
      tokensChange: 11,
      avgTokensPerRequest: 131,
      avgResponseTime: 12.8,
      successRate: 99.1,
      errorRate: 0.9,
    },
    {
      agent: 'test_data',
      requests: 312,
      requestsChange: 15,
      tokens: 18200,
      tokensChange: 18,
      avgTokensPerRequest: 58,
      avgResponseTime: 8.4,
      successRate: 99.7,
      errorRate: 0.3,
    },
    {
      agent: 'domain',
      requests: 165,
      requestsChange: 5,
      tokens: 9850,
      tokensChange: 7,
      avgTokensPerRequest: 60,
      avgResponseTime: 2.1,
      successRate: 99.9,
      errorRate: 0.1,
    },
  ],
  
  requestsOverTime: [
    { date: '2024-12-18', requirementAnalysis: 32, testCases: 68, testData: 41, domain: 22 },
    { date: '2024-12-19', requirementAnalysis: 38, testCases: 75, testData: 45, domain: 25 },
    { date: '2024-12-20', requirementAnalysis: 45, testCases: 82, testData: 52, domain: 28 },
    { date: '2024-12-21', requirementAnalysis: 28, testCases: 55, testData: 35, domain: 18 },
    { date: '2024-12-22', requirementAnalysis: 22, testCases: 48, testData: 30, domain: 15 },
    { date: '2024-12-23', requirementAnalysis: 35, testCases: 78, testData: 48, domain: 24 },
    { date: '2024-12-24', requirementAnalysis: 47, testCases: 117, testData: 61, domain: 33 },
  ],
  
  qualityDistribution: [
    { grade: 'A', count: 42, percentage: 17 },
    { grade: 'B', count: 68, percentage: 28 },
    { grade: 'C', count: 85, percentage: 34 },
    { grade: 'D', count: 38, percentage: 15 },
    { grade: 'F', count: 14, percentage: 6 },
  ],
  
  recentActivity: [
    {
      id: 'act-001',
      timestamp: '2024-12-24T12:34:00Z',
      agent: 'requirement_analysis',
      action: 'Analyzed',
      title: 'Guest Checkout Feature',
      metric: '72/100',
      tokens: 2340,
    },
    {
      id: 'act-002',
      timestamp: '2024-12-24T12:30:00Z',
      agent: 'test_cases',
      action: 'Generated',
      title: 'Product Reviews',
      metric: '8 cases',
      tokens: 1820,
    },
    {
      id: 'act-003',
      timestamp: '2024-12-24T12:28:00Z',
      agent: 'test_data',
      action: 'Generated',
      title: 'Customer Entity',
      metric: '50 records',
      tokens: 420,
    },
    {
      id: 'act-004',
      timestamp: '2024-12-24T12:25:00Z',
      agent: 'domain',
      action: 'Queried',
      title: 'Payment Workflow',
      metric: '',
      tokens: 180,
    },
    {
      id: 'act-005',
      timestamp: '2024-12-24T12:20:00Z',
      agent: 'requirement_analysis',
      action: 'Analyzed',
      title: 'Wishlist Feature',
      metric: '85/100',
      tokens: 2150,
    },
    {
      id: 'act-006',
      timestamp: '2024-12-24T12:15:00Z',
      agent: 'test_cases',
      action: 'Generated',
      title: 'Apply Promo Code',
      metric: '12 cases',
      tokens: 2890,
    },
    {
      id: 'act-007',
      timestamp: '2024-12-24T12:10:00Z',
      agent: 'test_data',
      action: 'Generated',
      title: 'Order Entity',
      metric: '25 records',
      tokens: 380,
    },
    {
      id: 'act-008',
      timestamp: '2024-12-24T12:05:00Z',
      agent: 'requirement_analysis',
      action: 'Analyzed',
      title: 'Return & Refund Policy',
      metric: '68/100',
      tokens: 2560,
    },
  ],
};

// Token usage by agent for donut chart
export const TOKEN_USAGE_BY_AGENT = [
  { agent: 'Requirement Analysis', tokens: 45230, percentage: 32, color: '#E21A2C' },
  { agent: 'Test Cases', tokens: 68450, percentage: 48, color: '#1E3A5F' },
  { agent: 'Test Data', tokens: 18200, percentage: 13, color: '#2E7D32' },
  { agent: 'Domain', tokens: 9850, percentage: 7, color: '#F59E0B' },
];

// Response time by agent
export const RESPONSE_TIME_BY_AGENT = [
  { agent: 'Requirement Analysis', avgTime: 14.2, p50: 12.5, p95: 22.3, p99: 28.1 },
  { agent: 'Test Cases', avgTime: 12.8, p50: 11.2, p95: 19.8, p99: 25.4 },
  { agent: 'Test Data', avgTime: 8.4, p50: 7.1, p95: 14.2, p99: 18.5 },
  { agent: 'Domain', avgTime: 2.1, p50: 1.8, p95: 3.5, p99: 4.2 },
];

// Weekly data for week view
export const WEEKLY_DATA: TimeSeriesDataPoint[] = [
  { date: 'Week 48', requirementAnalysis: 180, testCases: 420, testData: 280, domain: 140 },
  { date: 'Week 49', requirementAnalysis: 210, testCases: 480, testData: 310, domain: 155 },
  { date: 'Week 50', requirementAnalysis: 195, testCases: 445, testData: 290, domain: 148 },
  { date: 'Week 51', requirementAnalysis: 247, testCases: 523, testData: 312, domain: 165 },
];

// Monthly data for month view
export const MONTHLY_DATA: TimeSeriesDataPoint[] = [
  { date: 'Sep 2024', requirementAnalysis: 720, testCases: 1650, testData: 1100, domain: 550 },
  { date: 'Oct 2024', requirementAnalysis: 810, testCases: 1820, testData: 1200, domain: 610 },
  { date: 'Nov 2024', requirementAnalysis: 880, testCases: 1950, testData: 1280, domain: 645 },
  { date: 'Dec 2024', requirementAnalysis: 950, testCases: 2100, testData: 1350, domain: 680 },
];
```

---

## Agent Display Names & Icons

```typescript
// lib/analytics/utils.ts

export const AGENT_CONFIG = {
  requirement_analysis: {
    displayName: 'Requirement Analysis',
    shortName: 'Req Analysis',
    icon: '🔍',
    color: '#E21A2C',
    bgColor: '#FCECED',
  },
  test_cases: {
    displayName: 'Test Cases',
    shortName: 'Test Cases',
    icon: '🧪',
    color: '#1E3A5F',
    bgColor: '#E8EDF2',
  },
  test_data: {
    displayName: 'Test Data',
    shortName: 'Test Data',
    icon: '📦',
    color: '#2E7D32',
    bgColor: '#E8F5E9',
  },
  domain: {
    displayName: 'Domain Agent',
    shortName: 'Domain',
    icon: '🏢',
    color: '#F59E0B',
    bgColor: '#FEF3C7',
  },
};

export const GRADE_CONFIG = {
  A: { color: '#22C55E', bgColor: '#DCFCE7', label: 'Excellent' },
  B: { color: '#84CC16', bgColor: '#ECFCCB', label: 'Good' },
  C: { color: '#F59E0B', bgColor: '#FEF3C7', label: 'Acceptable' },
  D: { color: '#F97316', bgColor: '#FFEDD5', label: 'Needs Work' },
  F: { color: '#EF4444', bgColor: '#FEE2E2', label: 'Poor' },
};

export function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`;
  return num.toLocaleString();
}

export function formatCurrency(amount: number): string {
  return `$${amount.toFixed(2)}`;
}

export function formatDuration(seconds: number): string {
  return `${seconds.toFixed(1)}s`;
}

export function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });
}
```

---

## Data Hook (Phase 1)

```typescript
// hooks/useAnalytics.ts

import { useState, useMemo } from 'react';
import { 
  DUMMY_ANALYTICS, 
  WEEKLY_DATA, 
  MONTHLY_DATA 
} from '@/lib/analytics/dummy-data';
import { AnalyticsSummary, DateRange, TimeSeriesDataPoint } from '@/lib/analytics/types';

export function useAnalytics(dateRange: DateRange = 'last_7_days') {
  const [isLoading, setIsLoading] = useState(false);
  
  // In Phase 1, always return dummy data
  // In Phase 2, this will fetch from API based on dateRange
  
  const data = useMemo(() => {
    // Simulate different data for different ranges
    const analytics = { ...DUMMY_ANALYTICS };
    
    if (dateRange === 'last_30_days') {
      analytics.dateRange.label = 'Last 30 Days';
      // Scale up the numbers
      analytics.overview.totalRequests.value *= 4;
      analytics.overview.totalRequests.formattedValue = '4,988';
    }
    
    return analytics;
  }, [dateRange]);
  
  const getTimeSeriesData = (granularity: 'day' | 'week' | 'month'): TimeSeriesDataPoint[] => {
    switch (granularity) {
      case 'week':
        return WEEKLY_DATA;
      case 'month':
        return MONTHLY_DATA;
      default:
        return data.requestsOverTime;
    }
  };
  
  return {
    data,
    isLoading,
    error: null,
    getTimeSeriesData,
  };
}
```

---

## Responsive Behavior

| Breakpoint | Layout Changes |
|------------|----------------|
| Desktop (≥1280px) | Full layout as shown |
| Tablet (768-1279px) | 2-column grid for charts |
| Mobile (<768px) | Single column, stacked cards |

---

## Phase 1 Deliverables

| Component | Status |
|-----------|--------|
| OverviewCards | To build |
| RequestsOverTimeChart | To build |
| TokenUsageChart | To build |
| RequestsByAgentChart | To build |
| QualityScoreChart | To build |
| ResponseTimeChart | To build |
| AgentDetailsTable | To build |
| RecentActivity | To build |
| DateRangeSelector | To build |
| ExportButton (CSV only) | To build |
| Dummy Data | Defined above |
| Types | Defined above |

---

## Phase 2 Scope (Future - Not This PRD)

| Feature | Description |
|---------|-------------|
| Backend API | `/api/analytics` endpoints |
| Database | PostgreSQL analytics_events table |
| Real-time data | Replace dummy data with live queries |
| PDF Export | Server-side PDF generation |
| Custom date picker | Calendar UI for custom ranges |
| Drill-down views | Click chart to see details |
| Agent-specific pages | Dedicated analytics per agent |
| Cost tracking integration | Real LLM cost calculations |

---

## Dependencies

```json
{
  "dependencies": {
    "recharts": "^2.10.0",
    "date-fns": "^3.0.0"
  }
}
```

---

## Success Metrics (Phase 1)

| Metric | Target |
|--------|--------|
| Page load time | < 1s (dummy data) |
| All charts render | 100% |
| Responsive on mobile | Yes |
| Date range switching | Works with dummy data |
| CSV export | Generates valid file |
