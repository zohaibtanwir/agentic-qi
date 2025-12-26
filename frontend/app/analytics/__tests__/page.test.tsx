/**
 * Unit tests for Analytics Dashboard Page
 */

import { render, screen, fireEvent } from '@testing-library/react';
import AnalyticsPage from '../page';
import { useAnalytics } from '@/hooks/useAnalytics';

// Mock ResizeObserver for Recharts
const mockResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
global.ResizeObserver = mockResizeObserver;

// Mock useAnalytics hook
jest.mock('@/hooks/useAnalytics');
const mockUseAnalytics = jest.mocked(useAnalytics);

// Create complete mock data matching AnalyticsSummary type
const mockAnalyticsSummary = {
  dateRange: {
    start: '2024-12-18',
    end: '2024-12-24',
    label: 'Last 7 Days',
  },
  overview: {
    totalRequests: {
      value: 1523,
      formattedValue: '1,523',
      change: 12,
      changeDirection: 'up' as const,
    },
    testCasesGenerated: {
      value: 2450,
      formattedValue: '2,450',
      change: 8,
      changeDirection: 'up' as const,
    },
    totalTokens: {
      value: 2450000,
      formattedValue: '2.45M',
      change: 15,
      changeDirection: 'up' as const,
    },
    estimatedCost: {
      value: 7.35,
      formattedValue: '$7.35',
      change: 10,
      changeDirection: 'up' as const,
    },
    avgLatency: {
      value: 12.4,
      formattedValue: '12.4s',
      change: -5,
      changeDirection: 'down' as const,
    },
  },
  byAgent: [
    {
      agent: 'requirement_analysis' as const,
      requests: 247,
      requestsChange: 12,
      tokens: 856000,
      tokensChange: 15,
      avgTokensPerRequest: 3465,
      avgResponseTime: 14.2,
      successRate: 98.4,
      errorRate: 1.6,
    },
    {
      agent: 'test_cases' as const,
      requests: 523,
      requestsChange: 8,
      tokens: 724000,
      tokensChange: 5,
      avgTokensPerRequest: 1384,
      avgResponseTime: 12.8,
      successRate: 99.1,
      errorRate: 0.9,
    },
  ],
  requestsOverTime: [
    {
      date: '2024-12-18',
      requirementAnalysis: 45,
      testCases: 67,
      testData: 23,
      domain: 12,
    },
  ],
  qualityDistribution: [
    { grade: 'A' as const, count: 245, percentage: 45 },
    { grade: 'B' as const, count: 180, percentage: 33 },
    { grade: 'C' as const, count: 78, percentage: 14 },
    { grade: 'D' as const, count: 20, percentage: 8 },
  ],
  recentActivity: [
    {
      id: '1',
      agent: 'requirement_analysis' as const,
      action: 'Analyzed',
      title: 'Guest Checkout Feature',
      timestamp: new Date().toISOString(),
      tokens: 4250,
      metric: '72/100',
    },
  ],
};

// Default mock return value
const defaultMockReturn = {
  dateRange: 'last_7_days' as const,
  setDateRange: jest.fn(),
  granularity: 'day' as const,
  setGranularity: jest.fn(),
  data: mockAnalyticsSummary,
  timeSeriesData: mockAnalyticsSummary.requestsOverTime,
  getTimeSeriesData: jest.fn(),
  tokenUsageByAgent: [
    { agent: 'requirement_analysis', tokens: 856000, percentage: 35, color: '#E21A2C' },
    { agent: 'test_cases', tokens: 724000, percentage: 30, color: '#1E3A5F' },
  ],
  responseTimeByAgent: [
    { agent: 'Requirement Analysis', avgTime: 14.2, p50: 12.0, p95: 18.5, p99: 22.0 },
    { agent: 'Test Cases', avgTime: 12.8, p50: 11.0, p95: 16.0, p99: 19.5 },
  ],
  requestsByAgent: [],
  totalTokens: 0,
  avgResponseTime: 0,
  qualityScore: { score: 0, grade: 'A' },
  isLoading: false,
  error: null,
  refresh: jest.fn(),
};

describe('AnalyticsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAnalytics.mockReturnValue(defaultMockReturn);
  });

  describe('Rendering', () => {
    it('should render the page header', () => {
      render(<AnalyticsPage />);
      expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Platform usage and performance metrics')).toBeInTheDocument();
    });

    it('should render the date range selector', () => {
      render(<AnalyticsPage />);
      expect(screen.getByRole('button', { name: /select date range/i })).toBeInTheDocument();
    });

    it('should render the export button', () => {
      render(<AnalyticsPage />);
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
    });

    it('should render the overview cards section', () => {
      render(<AnalyticsPage />);
      expect(screen.getByText('Total Requests')).toBeInTheDocument();
      // Multiple "Tokens" may appear (in cards and table), so check for at least one
      expect(screen.getAllByText(/Total Tokens|Tokens/).length).toBeGreaterThan(0);
    });

    it('should render chart sections', () => {
      render(<AnalyticsPage />);
      expect(screen.getByText('Requests Over Time')).toBeInTheDocument();
      expect(screen.getByText('Token Usage by Agent')).toBeInTheDocument();
      expect(screen.getByText('Requests by Agent')).toBeInTheDocument();
      expect(screen.getByText('Quality Distribution')).toBeInTheDocument();
      expect(screen.getByText('Response Time')).toBeInTheDocument();
    });

    it('should render the agent details table section', () => {
      render(<AnalyticsPage />);
      expect(screen.getByText('Agent Details')).toBeInTheDocument();
    });

    it('should render the recent activity section', () => {
      render(<AnalyticsPage />);
      expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    });
  });

  describe('Granularity Selector', () => {
    it('should render granularity options', () => {
      render(<AnalyticsPage />);
      expect(screen.getByRole('radio', { name: 'Hour' })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: 'Day' })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: 'Week' })).toBeInTheDocument();
    });

    it('should have Day selected by default', () => {
      render(<AnalyticsPage />);
      const dayButton = screen.getByRole('radio', { name: 'Day' });
      expect(dayButton).toHaveAttribute('aria-checked', 'true');
    });
  });

  describe('Response Time Metric Selector', () => {
    it('should render metric options', () => {
      render(<AnalyticsPage />);
      expect(screen.getByRole('radio', { name: 'Avg' })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: 'P50' })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: 'P95' })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: 'P99' })).toBeInTheDocument();
    });

    it('should have Avg selected by default', () => {
      render(<AnalyticsPage />);
      const avgButton = screen.getByRole('radio', { name: 'Avg' });
      expect(avgButton).toHaveAttribute('aria-checked', 'true');
    });

    it('should update selection on click', () => {
      render(<AnalyticsPage />);
      const p95Button = screen.getByRole('radio', { name: 'P95' });
      fireEvent.click(p95Button);
      expect(p95Button).toHaveAttribute('aria-checked', 'true');
    });
  });

  describe('Accessibility', () => {
    it('should have proper section headings', () => {
      render(<AnalyticsPage />);
      // Screen reader only headings
      expect(screen.getByText('Overview Metrics')).toBeInTheDocument();
      expect(screen.getByText('Analytics Charts')).toBeInTheDocument();
      expect(screen.getByText('Detailed Data')).toBeInTheDocument();
    });

    it('should have radiogroup for granularity', () => {
      render(<AnalyticsPage />);
      expect(screen.getByRole('radiogroup', { name: /time granularity/i })).toBeInTheDocument();
    });

    it('should have radiogroup for response time metric', () => {
      render(<AnalyticsPage />);
      expect(screen.getByRole('radiogroup', { name: /response time metric/i })).toBeInTheDocument();
    });
  });

  describe('Layout', () => {
    it('should use grid layout for charts', () => {
      const { container } = render(<AnalyticsPage />);
      const gridSections = container.querySelectorAll('.grid');
      expect(gridSections.length).toBeGreaterThan(0);
    });

    it('should have cards with proper styling', () => {
      const { container } = render(<AnalyticsPage />);
      const cards = container.querySelectorAll('.rounded-xl.border');
      expect(cards.length).toBeGreaterThan(0);
    });
  });
});

describe('AnalyticsPage Loading State', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAnalytics.mockReturnValue({
      ...defaultMockReturn,
      data: {
        dateRange: { start: '', end: '', label: '' },
        overview: {
          totalRequests: { value: 0, formattedValue: '0', change: 0, changeDirection: 'neutral' as const },
          testCasesGenerated: { value: 0, formattedValue: '0', change: 0, changeDirection: 'neutral' as const },
          totalTokens: { value: 0, formattedValue: '0', change: 0, changeDirection: 'neutral' as const },
          estimatedCost: { value: 0, formattedValue: '$0', change: 0, changeDirection: 'neutral' as const },
          avgLatency: { value: 0, formattedValue: '0s', change: 0, changeDirection: 'neutral' as const },
        },
        byAgent: [],
        requestsOverTime: [],
        qualityDistribution: [],
        recentActivity: [],
      },
      timeSeriesData: [],
      tokenUsageByAgent: [],
      responseTimeByAgent: [],
      isLoading: true,
    });
  });

  it('should pass isLoading to child components', () => {
    render(<AnalyticsPage />);
    // Loading skeletons should be present
    const loadingElements = screen.getAllByLabelText(/loading/i);
    expect(loadingElements.length).toBeGreaterThan(0);
  });
});
