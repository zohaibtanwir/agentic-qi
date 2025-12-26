/**
 * Unit tests for OverviewCards Component
 */

import { render, screen } from '@testing-library/react';
import { OverviewCards } from '../OverviewCards';
import { OverviewMetrics } from '@/lib/analytics/types';
import { DUMMY_ANALYTICS } from '@/lib/analytics/dummy-data';

describe('OverviewCards', () => {
  const mockMetrics: OverviewMetrics = DUMMY_ANALYTICS.overview;

  describe('Rendering', () => {
    it('should render all 5 metric cards', () => {
      render(<OverviewCards metrics={mockMetrics} />);

      expect(screen.getByText('Total Requests')).toBeInTheDocument();
      expect(screen.getByText('Test Cases Generated')).toBeInTheDocument();
      expect(screen.getByText('Total Tokens')).toBeInTheDocument();
      expect(screen.getByText('Estimated Cost')).toBeInTheDocument();
      expect(screen.getByText('Avg Latency')).toBeInTheDocument();
    });

    it('should display formatted values', () => {
      render(<OverviewCards metrics={mockMetrics} />);

      expect(screen.getByText('1,247')).toBeInTheDocument();
      expect(screen.getByText('1,842')).toBeInTheDocument();
      expect(screen.getByText('142K')).toBeInTheDocument();
      expect(screen.getByText('$4.25')).toBeInTheDocument();
      expect(screen.getByText('12.3s')).toBeInTheDocument();
    });

    it('should display change percentages', () => {
      render(<OverviewCards metrics={mockMetrics} />);

      expect(screen.getByText('+12%')).toBeInTheDocument();
      expect(screen.getByText('+8%')).toBeInTheDocument();
      expect(screen.getByText('+15%')).toBeInTheDocument();
      expect(screen.getByText('+10%')).toBeInTheDocument();
      expect(screen.getByText('-5%')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <OverviewCards metrics={mockMetrics} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should have role="region" with aria-label', () => {
      render(<OverviewCards metrics={mockMetrics} />);

      const region = screen.getByRole('region', { name: /overview metrics/i });
      expect(region).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('should show loading skeletons when isLoading is true', () => {
      const { container } = render(
        <OverviewCards metrics={mockMetrics} isLoading />
      );

      // Check for pulse animation class (skeleton)
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBe(5);
    });

    it('should have aria-busy when loading', () => {
      const { container } = render(
        <OverviewCards metrics={mockMetrics} isLoading />
      );

      const loadingCards = container.querySelectorAll('[aria-busy="true"]');
      expect(loadingCards.length).toBe(5);
    });

    it('should not show metric values when loading', () => {
      render(<OverviewCards metrics={mockMetrics} isLoading />);

      expect(screen.queryByText('1,247')).not.toBeInTheDocument();
      expect(screen.queryByText('1,842')).not.toBeInTheDocument();
    });
  });

  describe('Change Direction Indicators', () => {
    it('should show green for positive changes on regular metrics', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      // Find the Total Requests card change indicator (+12%)
      const changeIndicators = container.querySelectorAll('.text-green-600');
      expect(changeIndicators.length).toBeGreaterThan(0);
    });

    it('should show green for negative latency change (lower is better)', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      // The latency card shows -5% which should be green since lower is better
      const greenIndicators = container.querySelectorAll('.text-green-600');
      // Should include the latency indicator
      expect(greenIndicators.length).toBe(5); // All 5 should be green in test data
    });

    it('should show red for negative changes on regular metrics', () => {
      const customMetrics: OverviewMetrics = {
        ...mockMetrics,
        totalRequests: {
          value: 1000,
          formattedValue: '1,000',
          change: -10,
          changeDirection: 'down',
        },
      };

      const { container } = render(<OverviewCards metrics={customMetrics} />);

      const redIndicators = container.querySelectorAll('.text-red-600');
      expect(redIndicators.length).toBeGreaterThan(0);
    });

    it('should show red for positive latency change (higher is worse)', () => {
      const customMetrics: OverviewMetrics = {
        ...mockMetrics,
        avgLatency: {
          value: 15.0,
          formattedValue: '15.0s',
          change: 10,
          changeDirection: 'up',
        },
      };

      const { container } = render(<OverviewCards metrics={customMetrics} />);

      // Latency increase should be red
      const redIndicators = container.querySelectorAll('.text-red-600');
      expect(redIndicators.length).toBeGreaterThan(0);
    });
  });

  describe('Icons', () => {
    it('should render icons for each card', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      const icons = container.querySelectorAll('svg');
      // 5 card icons + arrow icons for each change indicator
      expect(icons.length).toBeGreaterThanOrEqual(5);
    });

    it('should have aria-hidden on icons', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      const iconContainers = container.querySelectorAll('[aria-hidden="true"]');
      expect(iconContainers.length).toBeGreaterThan(0);
    });
  });

  describe('Grid Layout', () => {
    it('should use grid layout', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      expect(container.firstChild).toHaveClass('grid');
    });

    it('should have responsive grid columns', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      expect(container.firstChild).toHaveClass('grid-cols-1');
      expect(container.firstChild).toHaveClass('sm:grid-cols-2');
      expect(container.firstChild).toHaveClass('lg:grid-cols-5');
    });

    it('should have gap between cards', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      expect(container.firstChild).toHaveClass('gap-4');
    });
  });

  describe('Card Styling', () => {
    it('should have white background cards', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      const cards = container.querySelectorAll('.bg-white');
      expect(cards.length).toBe(5);
    });

    it('should have rounded borders', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      const cards = container.querySelectorAll('.rounded-lg');
      expect(cards.length).toBe(5);
    });

    it('should have shadow', () => {
      const { container } = render(<OverviewCards metrics={mockMetrics} />);

      const cards = container.querySelectorAll('.shadow-sm');
      expect(cards.length).toBe(5);
    });
  });

  describe('Accessibility', () => {
    it('should have accessible labels for values', () => {
      render(<OverviewCards metrics={mockMetrics} />);

      const totalRequestsLabel = screen.getByLabelText(/Total Requests: 1,247/i);
      expect(totalRequestsLabel).toBeInTheDocument();
    });

    it('should have accessible labels for change indicators', () => {
      render(<OverviewCards metrics={mockMetrics} />);

      const changeLabels = screen.getAllByLabelText(
        /compared to previous period/i
      );
      expect(changeLabels.length).toBe(5);
    });
  });

  describe('Edge Cases', () => {
    it('should handle zero values', () => {
      const zeroMetrics: OverviewMetrics = {
        totalRequests: {
          value: 0,
          formattedValue: '0',
          change: 0,
          changeDirection: 'neutral',
        },
        testCasesGenerated: {
          value: 0,
          formattedValue: '0',
          change: 0,
          changeDirection: 'neutral',
        },
        totalTokens: {
          value: 0,
          formattedValue: '0',
          change: 0,
          changeDirection: 'neutral',
        },
        estimatedCost: {
          value: 0,
          formattedValue: '$0.00',
          change: 0,
          changeDirection: 'neutral',
        },
        avgLatency: {
          value: 0,
          formattedValue: '0.0s',
          change: 0,
          changeDirection: 'neutral',
        },
      };

      render(<OverviewCards metrics={zeroMetrics} />);

      // Should render without errors
      expect(screen.getAllByText('0')).toHaveLength(3);
      expect(screen.getByText('$0.00')).toBeInTheDocument();
      expect(screen.getByText('0.0s')).toBeInTheDocument();
    });

    it('should handle large values', () => {
      const largeMetrics: OverviewMetrics = {
        ...mockMetrics,
        totalTokens: {
          value: 1500000,
          formattedValue: '1.5M',
          change: 100,
          changeDirection: 'up',
        },
      };

      render(<OverviewCards metrics={largeMetrics} />);

      expect(screen.getByText('1.5M')).toBeInTheDocument();
      expect(screen.getByText('+100%')).toBeInTheDocument();
    });

    it('should handle neutral changes', () => {
      const neutralMetrics: OverviewMetrics = {
        ...mockMetrics,
        totalRequests: {
          value: 1000,
          formattedValue: '1,000',
          change: 0,
          changeDirection: 'neutral',
        },
      };

      const { container } = render(<OverviewCards metrics={neutralMetrics} />);

      const grayIndicators = container.querySelectorAll('.text-gray-600');
      expect(grayIndicators.length).toBeGreaterThan(0);
    });
  });
});
