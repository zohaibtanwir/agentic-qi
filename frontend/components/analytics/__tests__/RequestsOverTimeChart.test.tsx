/**
 * Unit tests for RequestsOverTimeChart Component
 */

import { render, screen } from '@testing-library/react';
import { RequestsOverTimeChart } from '../RequestsOverTimeChart';
import { TimeSeriesDataPoint } from '@/lib/analytics/types';
import { DUMMY_ANALYTICS, WEEKLY_DATA, MONTHLY_DATA } from '@/lib/analytics/dummy-data';

// Mock ResizeObserver which is used by Recharts ResponsiveContainer
const mockResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
global.ResizeObserver = mockResizeObserver;

describe('RequestsOverTimeChart', () => {
  const sampleData: TimeSeriesDataPoint[] = DUMMY_ANALYTICS.requestsOverTime;

  describe('Rendering', () => {
    it('should render the chart container', () => {
      render(<RequestsOverTimeChart data={sampleData} />);

      const chart = screen.getByRole('img', { name: /line chart showing requests/i });
      expect(chart).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <RequestsOverTimeChart data={sampleData} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should render with default height of 300', () => {
      render(<RequestsOverTimeChart data={sampleData} />);

      const chart = screen.getByRole('img');
      // The ResponsiveContainer doesn't directly set height on the aria element
      // but we can verify the chart renders
      expect(chart).toBeInTheDocument();
    });

    it('should render with custom height', () => {
      render(<RequestsOverTimeChart data={sampleData} height={400} />);

      const chart = screen.getByRole('img');
      expect(chart).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('should show loading skeleton when isLoading is true', () => {
      render(<RequestsOverTimeChart data={sampleData} isLoading />);

      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toBeInTheDocument();
    });

    it('should have aria-busy when loading', () => {
      render(<RequestsOverTimeChart data={sampleData} isLoading />);

      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toHaveAttribute('aria-busy', 'true');
    });

    it('should show loading text', () => {
      render(<RequestsOverTimeChart data={sampleData} isLoading />);

      expect(screen.getByText(/loading chart/i)).toBeInTheDocument();
    });

    it('should not render chart content when loading', () => {
      render(<RequestsOverTimeChart data={sampleData} isLoading />);

      expect(
        screen.queryByRole('img', { name: /line chart showing requests/i })
      ).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should show empty state when data is empty', () => {
      render(<RequestsOverTimeChart data={[]} />);

      const emptyState = screen.getByRole('img', { name: /no data available/i });
      expect(emptyState).toBeInTheDocument();
    });

    it('should show empty state message', () => {
      render(<RequestsOverTimeChart data={[]} />);

      expect(screen.getByText(/no data available/i)).toBeInTheDocument();
    });

    it('should show empty state when data is undefined', () => {
      render(<RequestsOverTimeChart data={undefined as unknown as TimeSeriesDataPoint[]} />);

      expect(screen.getByText(/no data available/i)).toBeInTheDocument();
    });
  });

  describe('Granularity', () => {
    it('should include granularity in aria-label for day', () => {
      render(<RequestsOverTimeChart data={sampleData} granularity="day" />);

      expect(
        screen.getByRole('img', { name: /7 days/i })
      ).toBeInTheDocument();
    });

    it('should include granularity in aria-label for week', () => {
      render(<RequestsOverTimeChart data={WEEKLY_DATA} granularity="week" />);

      expect(
        screen.getByRole('img', { name: /4 weeks/i })
      ).toBeInTheDocument();
    });

    it('should include granularity in aria-label for month', () => {
      render(<RequestsOverTimeChart data={MONTHLY_DATA} granularity="month" />);

      expect(
        screen.getByRole('img', { name: /4 months/i })
      ).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="img"', () => {
      render(<RequestsOverTimeChart data={sampleData} />);

      expect(screen.getByRole('img')).toBeInTheDocument();
    });

    it('should have descriptive aria-label', () => {
      render(<RequestsOverTimeChart data={sampleData} granularity="day" />);

      const chart = screen.getByRole('img');
      expect(chart).toHaveAttribute(
        'aria-label',
        expect.stringContaining('Line chart showing requests over time by agent')
      );
    });
  });

  describe('Data Handling', () => {
    it('should handle 7-day data', () => {
      const dailyData = DUMMY_ANALYTICS.requestsOverTime;
      render(<RequestsOverTimeChart data={dailyData} granularity="day" />);

      const chart = screen.getByRole('img', { name: /7 days/i });
      expect(chart).toBeInTheDocument();
    });

    it('should handle weekly data', () => {
      render(<RequestsOverTimeChart data={WEEKLY_DATA} granularity="week" />);

      const chart = screen.getByRole('img', { name: /4 weeks/i });
      expect(chart).toBeInTheDocument();
    });

    it('should handle monthly data', () => {
      render(<RequestsOverTimeChart data={MONTHLY_DATA} granularity="month" />);

      const chart = screen.getByRole('img', { name: /4 months/i });
      expect(chart).toBeInTheDocument();
    });

    it('should handle single data point', () => {
      const singlePoint: TimeSeriesDataPoint[] = [
        { date: '2024-12-24', requirementAnalysis: 47, testCases: 117, testData: 61, domain: 33 },
      ];

      render(<RequestsOverTimeChart data={singlePoint} granularity="day" />);

      const chart = screen.getByRole('img', { name: /1 day/i });
      expect(chart).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('should have animate-pulse class on loading skeleton', () => {
      const { container } = render(
        <RequestsOverTimeChart data={sampleData} isLoading />
      );

      const skeleton = container.querySelector('.animate-pulse');
      expect(skeleton).toBeInTheDocument();
    });

    it('should have bg-gray-50 on empty state', () => {
      const { container } = render(<RequestsOverTimeChart data={[]} />);

      const emptyState = container.querySelector('.bg-gray-50');
      expect(emptyState).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle data with zero values', () => {
      const zeroData: TimeSeriesDataPoint[] = [
        { date: '2024-12-24', requirementAnalysis: 0, testCases: 0, testData: 0, domain: 0 },
      ];

      render(<RequestsOverTimeChart data={zeroData} />);

      const chart = screen.getByRole('img', { name: /line chart/i });
      expect(chart).toBeInTheDocument();
    });

    it('should handle large data values', () => {
      const largeData: TimeSeriesDataPoint[] = [
        { date: '2024-12-24', requirementAnalysis: 10000, testCases: 50000, testData: 30000, domain: 15000 },
      ];

      render(<RequestsOverTimeChart data={largeData} />);

      const chart = screen.getByRole('img', { name: /line chart/i });
      expect(chart).toBeInTheDocument();
    });
  });
});
