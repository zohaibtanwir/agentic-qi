/**
 * Unit tests for ResponseTimeChart Component
 */

import { render, screen } from '@testing-library/react';
import { ResponseTimeChart } from '../ResponseTimeChart';
import { ResponseTimeByAgent } from '@/lib/analytics/types';
import { RESPONSE_TIME_BY_AGENT } from '@/lib/analytics/dummy-data';

// Mock ResizeObserver
const mockResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
global.ResizeObserver = mockResizeObserver;

describe('ResponseTimeChart', () => {
  const sampleData: ResponseTimeByAgent[] = RESPONSE_TIME_BY_AGENT;

  describe('Rendering', () => {
    it('should render the chart container', () => {
      render(<ResponseTimeChart data={sampleData} />);
      const chart = screen.getByRole('img', { name: /bar chart showing.*response time/i });
      expect(chart).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <ResponseTimeChart data={sampleData} className="custom-class" />
      );
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should render with default metric (avgTime)', () => {
      render(<ResponseTimeChart data={sampleData} />);
      const chart = screen.getByRole('img');
      expect(chart.getAttribute('aria-label')).toContain('Average');
    });
  });

  describe('Metric Selection', () => {
    it('should render with p50 metric', () => {
      render(<ResponseTimeChart data={sampleData} metric="p50" />);
      const chart = screen.getByRole('img');
      expect(chart.getAttribute('aria-label')).toContain('P50');
    });

    it('should render with p95 metric', () => {
      render(<ResponseTimeChart data={sampleData} metric="p95" />);
      const chart = screen.getByRole('img');
      expect(chart.getAttribute('aria-label')).toContain('P95');
    });

    it('should render with p99 metric', () => {
      render(<ResponseTimeChart data={sampleData} metric="p99" />);
      const chart = screen.getByRole('img');
      expect(chart.getAttribute('aria-label')).toContain('P99');
    });
  });

  describe('Loading State', () => {
    it('should show loading skeleton when isLoading is true', () => {
      render(<ResponseTimeChart data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toBeInTheDocument();
    });

    it('should have aria-busy when loading', () => {
      render(<ResponseTimeChart data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('Empty State', () => {
    it('should show empty state when data is empty', () => {
      render(<ResponseTimeChart data={[]} />);
      const emptyState = screen.getByRole('img', { name: /no data available/i });
      expect(emptyState).toBeInTheDocument();
    });

    it('should show empty state message', () => {
      render(<ResponseTimeChart data={[]} />);
      expect(screen.getByText(/no data available/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="img"', () => {
      render(<ResponseTimeChart data={sampleData} />);
      expect(screen.getByRole('img')).toBeInTheDocument();
    });

    it('should have descriptive aria-label', () => {
      render(<ResponseTimeChart data={sampleData} />);
      const chart = screen.getByRole('img');
      expect(chart).toHaveAttribute('aria-label', expect.stringContaining('response time'));
    });
  });

  describe('Data Handling', () => {
    it('should handle 4 agents', () => {
      render(<ResponseTimeChart data={sampleData} />);
      const chart = screen.getByRole('img', { name: /bar chart/i });
      expect(chart).toBeInTheDocument();
    });

    it('should handle single agent', () => {
      const singleAgent: ResponseTimeByAgent[] = [
        { agent: 'Test', avgTime: 5.0, p50: 4.0, p95: 8.0, p99: 10.0 },
      ];
      render(<ResponseTimeChart data={singleAgent} />);
      expect(screen.getByRole('img', { name: /bar chart/i })).toBeInTheDocument();
    });
  });
});
