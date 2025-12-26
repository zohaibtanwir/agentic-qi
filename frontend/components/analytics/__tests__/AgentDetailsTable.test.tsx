/**
 * Unit tests for AgentDetailsTable Component
 */

import { render, screen } from '@testing-library/react';
import { AgentDetailsTable } from '../AgentDetailsTable';
import { AgentMetrics } from '@/lib/analytics/types';
import { DUMMY_ANALYTICS } from '@/lib/analytics/dummy-data';

describe('AgentDetailsTable', () => {
  const sampleData: AgentMetrics[] = DUMMY_ANALYTICS.byAgent;

  describe('Rendering', () => {
    it('should render the table', () => {
      render(<AgentDetailsTable data={sampleData} />);
      const table = screen.getByRole('table', { name: /agent details/i });
      expect(table).toBeInTheDocument();
    });

    it('should render all table headers', () => {
      render(<AgentDetailsTable data={sampleData} />);
      expect(screen.getByText('Agent')).toBeInTheDocument();
      expect(screen.getByText('Requests')).toBeInTheDocument();
      expect(screen.getByText('Tokens')).toBeInTheDocument();
      expect(screen.getByText('Avg Tokens')).toBeInTheDocument();
      expect(screen.getByText('Avg Time')).toBeInTheDocument();
      expect(screen.getByText('Success Rate')).toBeInTheDocument();
    });

    it('should render all 4 agents', () => {
      render(<AgentDetailsTable data={sampleData} />);
      expect(screen.getByText('Requirement Analysis')).toBeInTheDocument();
      expect(screen.getByText('Test Cases')).toBeInTheDocument();
      expect(screen.getByText('Test Data')).toBeInTheDocument();
      expect(screen.getByText('Domain Agent')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <AgentDetailsTable data={sampleData} className="custom-class" />
      );
      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Data Display', () => {
    it('should display request counts', () => {
      render(<AgentDetailsTable data={sampleData} />);
      expect(screen.getByText('247')).toBeInTheDocument();
      expect(screen.getByText('523')).toBeInTheDocument();
    });

    it('should display change badges', () => {
      render(<AgentDetailsTable data={sampleData} />);
      expect(screen.getByText('+12%')).toBeInTheDocument();
      expect(screen.getByText('+8%')).toBeInTheDocument();
    });

    it('should display response times with unit', () => {
      render(<AgentDetailsTable data={sampleData} />);
      expect(screen.getByText('14.2s')).toBeInTheDocument();
      expect(screen.getByText('12.8s')).toBeInTheDocument();
    });

    it('should display success rate badges', () => {
      render(<AgentDetailsTable data={sampleData} />);
      expect(screen.getByText('98.4%')).toBeInTheDocument();
      expect(screen.getByText('99.1%')).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('should show loading skeleton when isLoading is true', () => {
      render(<AgentDetailsTable data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading table/i);
      expect(skeleton).toBeInTheDocument();
    });

    it('should have aria-busy when loading', () => {
      render(<AgentDetailsTable data={sampleData} isLoading />);
      const skeleton = screen.getByLabelText(/loading table/i);
      expect(skeleton).toHaveAttribute('aria-busy', 'true');
    });

    it('should not render table content when loading', () => {
      render(<AgentDetailsTable data={sampleData} isLoading />);
      expect(screen.queryByRole('table')).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should show empty state when data is empty', () => {
      render(<AgentDetailsTable data={[]} />);
      const emptyState = screen.getByRole('status', { name: /no data available/i });
      expect(emptyState).toBeInTheDocument();
    });

    it('should show empty state message', () => {
      render(<AgentDetailsTable data={[]} />);
      expect(screen.getByText(/no agent data available/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="table" with aria-label', () => {
      render(<AgentDetailsTable data={sampleData} />);
      const table = screen.getByRole('table');
      expect(table).toHaveAttribute('aria-label', 'Agent details');
    });
  });

  describe('Success Rate Styling', () => {
    it('should apply green style for high success rates (>=99%)', () => {
      const { container } = render(<AgentDetailsTable data={sampleData} />);
      const greenBadges = container.querySelectorAll('.text-green-600.bg-green-50');
      expect(greenBadges.length).toBeGreaterThan(0);
    });

    it('should handle different success rate ranges', () => {
      const customData: AgentMetrics[] = [
        { ...sampleData[0], successRate: 99.5 }, // Green
        { ...sampleData[1], successRate: 96.0 }, // Yellow
        { ...sampleData[2], successRate: 90.0 }, // Red
        { ...sampleData[3], successRate: 100 }, // Green
      ];
      const { container } = render(<AgentDetailsTable data={customData} />);

      // Should have multiple styled badges
      const badges = container.querySelectorAll('[class*="bg-"]');
      expect(badges.length).toBeGreaterThan(0);
    });
  });
});
