/**
 * Unit tests for RequestsByAgentChart Component
 */

import { render, screen } from '@testing-library/react';
import { RequestsByAgentChart, AgentRequestData } from '../RequestsByAgentChart';
import { getRequestsByAgent } from '@/lib/analytics/dummy-data';

// Mock ResizeObserver
const mockResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
global.ResizeObserver = mockResizeObserver;

describe('RequestsByAgentChart', () => {
  const sampleData: AgentRequestData[] = getRequestsByAgent();

  describe('Rendering', () => {
    it('should render the chart container', () => {
      render(<RequestsByAgentChart data={sampleData} />);
      const chart = screen.getByRole('img', { name: /bar chart showing requests/i });
      expect(chart).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <RequestsByAgentChart data={sampleData} className="custom-class" />
      );
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should include total requests in aria-label', () => {
      render(<RequestsByAgentChart data={sampleData} />);
      const chart = screen.getByRole('img');
      expect(chart.getAttribute('aria-label')).toContain('Total:');
    });
  });

  describe('Loading State', () => {
    it('should show loading skeleton when isLoading is true', () => {
      render(<RequestsByAgentChart data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toBeInTheDocument();
    });

    it('should have aria-busy when loading', () => {
      render(<RequestsByAgentChart data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading chart/i);
      expect(skeleton).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('Empty State', () => {
    it('should show empty state when data is empty', () => {
      render(<RequestsByAgentChart data={[]} />);
      const emptyState = screen.getByRole('img', { name: /no data available/i });
      expect(emptyState).toBeInTheDocument();
    });

    it('should show empty state message', () => {
      render(<RequestsByAgentChart data={[]} />);
      expect(screen.getByText(/no data available/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="img"', () => {
      render(<RequestsByAgentChart data={sampleData} />);
      expect(screen.getByRole('img')).toBeInTheDocument();
    });

    it('should have descriptive aria-label', () => {
      render(<RequestsByAgentChart data={sampleData} />);
      const chart = screen.getByRole('img');
      expect(chart).toHaveAttribute('aria-label', expect.stringContaining('Bar chart'));
    });
  });

  describe('Data Handling', () => {
    it('should handle 4 agents', () => {
      render(<RequestsByAgentChart data={sampleData} />);
      const chart = screen.getByRole('img', { name: /bar chart/i });
      expect(chart).toBeInTheDocument();
    });

    it('should handle single agent', () => {
      const singleAgent: AgentRequestData[] = [
        { agent: 'Test', requests: 100, change: 5 },
      ];
      render(<RequestsByAgentChart data={singleAgent} />);
      expect(screen.getByRole('img', { name: /bar chart/i })).toBeInTheDocument();
    });
  });
});
