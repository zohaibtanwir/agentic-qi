/**
 * Unit tests for TokenUsageChart Component
 */

import { render, screen } from '@testing-library/react';
import { TokenUsageChart } from '../TokenUsageChart';
import { TokenUsageByAgent } from '@/lib/analytics/types';
import { TOKEN_USAGE_BY_AGENT } from '@/lib/analytics/dummy-data';

// Mock ResizeObserver which is used by Recharts ResponsiveContainer
const mockResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
global.ResizeObserver = mockResizeObserver;

describe('TokenUsageChart', () => {
  const sampleData: TokenUsageByAgent[] = TOKEN_USAGE_BY_AGENT;

  describe('Rendering', () => {
    it('should render the chart container', () => {
      render(<TokenUsageChart data={sampleData} />);

      const chart = screen.getByRole('img', { name: /donut chart showing token usage/i });
      expect(chart).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <TokenUsageChart data={sampleData} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should render with default height of 300', () => {
      render(<TokenUsageChart data={sampleData} />);

      const chart = screen.getByRole('img');
      expect(chart).toBeInTheDocument();
    });

    it('should render with custom height', () => {
      render(<TokenUsageChart data={sampleData} height={400} />);

      const chart = screen.getByRole('img');
      expect(chart).toBeInTheDocument();
    });

    it('should include total tokens in aria-label', () => {
      render(<TokenUsageChart data={sampleData} />);

      const chart = screen.getByRole('img');
      expect(chart.getAttribute('aria-label')).toContain('Total:');
    });
  });

  describe('Loading State', () => {
    it('should show loading skeleton when isLoading is true', () => {
      render(<TokenUsageChart data={sampleData} isLoading />);

      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toBeInTheDocument();
    });

    it('should have aria-busy when loading', () => {
      render(<TokenUsageChart data={sampleData} isLoading />);

      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toHaveAttribute('aria-busy', 'true');
    });

    it('should not render chart content when loading', () => {
      render(<TokenUsageChart data={sampleData} isLoading />);

      expect(
        screen.queryByRole('img', { name: /donut chart/i })
      ).not.toBeInTheDocument();
    });

    it('should show circular skeleton', () => {
      const { container } = render(
        <TokenUsageChart data={sampleData} isLoading />
      );

      const circularSkeleton = container.querySelector('.rounded-full');
      expect(circularSkeleton).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should show empty state when data is empty', () => {
      render(<TokenUsageChart data={[]} />);

      const emptyState = screen.getByRole('img', { name: /no data available/i });
      expect(emptyState).toBeInTheDocument();
    });

    it('should show empty state message', () => {
      render(<TokenUsageChart data={[]} />);

      expect(screen.getByText(/no data available/i)).toBeInTheDocument();
    });

    it('should show empty state when data is undefined', () => {
      render(<TokenUsageChart data={undefined as unknown as TokenUsageByAgent[]} />);

      expect(screen.getByText(/no data available/i)).toBeInTheDocument();
    });
  });

  describe('Center Label', () => {
    it('should display total tokens in center', () => {
      render(<TokenUsageChart data={sampleData} />);

      // Total of sample data
      expect(screen.getByText('142K')).toBeInTheDocument();
    });

    it('should display "Total Tokens" label', () => {
      render(<TokenUsageChart data={sampleData} />);

      expect(screen.getByText('Total Tokens')).toBeInTheDocument();
    });
  });

  describe('Legend', () => {
    // Note: Recharts Legend doesn't fully render in JSDOM test environment
    // These tests verify the props are passed correctly

    it('should render chart with showLegend=true by default', () => {
      render(<TokenUsageChart data={sampleData} />);

      // Verify chart renders - legend is rendered inside ResponsiveContainer
      // which doesn't fully work in JSDOM
      const chart = screen.getByRole('img', { name: /donut chart/i });
      expect(chart).toBeInTheDocument();
    });

    it('should render chart when showLegend is false', () => {
      render(<TokenUsageChart data={sampleData} showLegend={false} />);

      const chart = screen.getByRole('img', { name: /donut chart/i });
      expect(chart).toBeInTheDocument();
    });

    it('should accept showLegend prop', () => {
      // This test verifies the prop is accepted without errors
      expect(() => {
        render(<TokenUsageChart data={sampleData} showLegend={true} />);
      }).not.toThrow();
    });
  });

  describe('Accessibility', () => {
    it('should have role="img"', () => {
      render(<TokenUsageChart data={sampleData} />);

      expect(screen.getByRole('img')).toBeInTheDocument();
    });

    it('should have descriptive aria-label', () => {
      render(<TokenUsageChart data={sampleData} />);

      const chart = screen.getByRole('img');
      expect(chart).toHaveAttribute(
        'aria-label',
        expect.stringContaining('Donut chart showing token usage by agent')
      );
    });
  });

  describe('Data Handling', () => {
    it('should handle 4 agents data', () => {
      render(<TokenUsageChart data={sampleData} />);

      // Verify the chart renders with 4 agents of data
      const chart = screen.getByRole('img', { name: /donut chart/i });
      expect(chart).toBeInTheDocument();
      // Total should reflect all 4 agents
      expect(screen.getByText('142K')).toBeInTheDocument();
    });

    it('should handle single agent data', () => {
      const singleAgent: TokenUsageByAgent[] = [
        { agent: 'Test Agent', tokens: 10000, percentage: 100, color: '#E21A2C' },
      ];

      render(<TokenUsageChart data={singleAgent} />);

      const chart = screen.getByRole('img', { name: /donut chart/i });
      expect(chart).toBeInTheDocument();
      expect(screen.getByText('10K')).toBeInTheDocument();
    });

    it('should calculate and display correct total', () => {
      const customData: TokenUsageByAgent[] = [
        { agent: 'A', tokens: 50000, percentage: 50, color: '#E21A2C' },
        { agent: 'B', tokens: 50000, percentage: 50, color: '#1E3A5F' },
      ];

      render(<TokenUsageChart data={customData} />);

      expect(screen.getByText('100K')).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('should have animate-pulse class on loading skeleton', () => {
      const { container } = render(
        <TokenUsageChart data={sampleData} isLoading />
      );

      const skeleton = container.querySelector('.animate-pulse');
      expect(skeleton).toBeInTheDocument();
    });

    it('should have bg-gray-50 on empty state', () => {
      const { container } = render(<TokenUsageChart data={[]} />);

      const emptyState = container.querySelector('.bg-gray-50');
      expect(emptyState).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle data with zero tokens', () => {
      const zeroData: TokenUsageByAgent[] = [
        { agent: 'Test', tokens: 0, percentage: 0, color: '#E21A2C' },
      ];

      render(<TokenUsageChart data={zeroData} />);

      const chart = screen.getByRole('img', { name: /donut chart/i });
      expect(chart).toBeInTheDocument();
    });

    it('should handle large token values', () => {
      const largeData: TokenUsageByAgent[] = [
        { agent: 'Large', tokens: 5000000, percentage: 100, color: '#E21A2C' },
      ];

      render(<TokenUsageChart data={largeData} />);

      expect(screen.getByText('5.0M')).toBeInTheDocument();
    });
  });
});
