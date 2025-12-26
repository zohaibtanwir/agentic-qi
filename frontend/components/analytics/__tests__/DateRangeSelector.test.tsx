/**
 * Unit tests for DateRangeSelector Component
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DateRangeSelector } from '../DateRangeSelector';
import { DATE_RANGE_OPTIONS } from '@/lib/analytics/utils';

describe('DateRangeSelector', () => {
  const defaultProps = {
    value: 'last_7_days' as const,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the selector button', () => {
      render(<DateRangeSelector {...defaultProps} />);

      expect(
        screen.getByRole('button', { name: /select date range/i })
      ).toBeInTheDocument();
    });

    it('should display the current selected value label', () => {
      render(<DateRangeSelector {...defaultProps} value="last_30_days" />);

      expect(screen.getByText('Last 30 Days')).toBeInTheDocument();
    });

    it('should display calendar icon', () => {
      render(<DateRangeSelector {...defaultProps} />);

      // The SVG should be present (calendar icon)
      const button = screen.getByRole('button');
      expect(button.querySelector('svg')).toBeInTheDocument();
    });

    it('should not show dropdown initially', () => {
      render(<DateRangeSelector {...defaultProps} />);

      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <DateRangeSelector {...defaultProps} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Dropdown Behavior', () => {
    it('should open dropdown when clicked', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should close dropdown when clicking outside', async () => {
      const user = userEvent.setup();
      render(
        <div>
          <DateRangeSelector {...defaultProps} />
          <div data-testid="outside">Outside</div>
        </div>
      );

      // Open dropdown
      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);
      expect(screen.getByRole('listbox')).toBeInTheDocument();

      // Click outside
      await user.click(screen.getByTestId('outside'));
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should close dropdown when Escape is pressed', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      // Open dropdown
      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);
      expect(screen.getByRole('listbox')).toBeInTheDocument();

      // Press Escape
      await user.keyboard('{Escape}');
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should display all date range options', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);

      expect(screen.getByRole('listbox')).toBeInTheDocument();
      DATE_RANGE_OPTIONS.forEach((option) => {
        expect(
          screen.getByRole('option', { name: new RegExp(option.label) })
        ).toBeInTheDocument();
      });
    });

    it('should mark current selection with checkmark', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} value="last_7_days" />);

      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);

      // Find the selected option
      const selectedOption = screen.getByRole('option', { selected: true });
      expect(selectedOption).toHaveTextContent('Last 7 Days');
    });
  });

  describe('Selection', () => {
    it('should call onChange when an option is selected', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      render(<DateRangeSelector {...defaultProps} onChange={onChange} />);

      // Open dropdown
      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);

      // Select an option
      await user.click(screen.getByText('Last 30 Days'));

      expect(onChange).toHaveBeenCalledWith('last_30_days');
    });

    it('should close dropdown after selection', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      // Open dropdown
      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);

      // Select an option
      await user.click(screen.getByText('Last 30 Days'));

      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should allow selecting each date range option', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();

      for (const option of DATE_RANGE_OPTIONS) {
        onChange.mockClear();
        const { unmount } = render(
          <DateRangeSelector {...defaultProps} onChange={onChange} />
        );

        const button = screen.getByRole('button', { name: /select date range/i });
        await user.click(button);

        // Use role-based query to avoid matching button label
        const optionElement = screen.getByRole('option', {
          name: new RegExp(option.label),
        });
        await user.click(optionElement);

        expect(onChange).toHaveBeenCalledWith(option.value);
        unmount();
      }
    });
  });

  describe('Disabled State', () => {
    it('should not open when disabled', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} disabled />);

      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);

      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should have disabled attribute when disabled', () => {
      render(<DateRangeSelector {...defaultProps} disabled />);

      const button = screen.getByRole('button', { name: /select date range/i });
      expect(button).toBeDisabled();
    });

    it('should have disabled styling when disabled', () => {
      render(<DateRangeSelector {...defaultProps} disabled />);

      const button = screen.getByRole('button', { name: /select date range/i });
      expect(button).toHaveClass('cursor-not-allowed');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should open dropdown with Enter key', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });
      button.focus();
      await user.keyboard('{Enter}');

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should open dropdown with Space key', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });
      button.focus();
      await user.keyboard(' ');

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should navigate down with ArrowDown key', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      render(
        <DateRangeSelector
          {...defaultProps}
          value="last_7_days"
          onChange={onChange}
        />
      );

      const button = screen.getByRole('button', { name: /select date range/i });
      button.focus();
      await user.keyboard('{Enter}'); // Open dropdown
      await user.keyboard('{ArrowDown}');

      expect(onChange).toHaveBeenCalledWith('last_30_days');
    });

    it('should navigate up with ArrowUp key', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      render(
        <DateRangeSelector
          {...defaultProps}
          value="last_30_days"
          onChange={onChange}
        />
      );

      const button = screen.getByRole('button', { name: /select date range/i });
      button.focus();
      await user.keyboard('{Enter}'); // Open dropdown
      await user.keyboard('{ArrowUp}');

      expect(onChange).toHaveBeenCalledWith('last_7_days');
    });

    it('should not go beyond first option with ArrowUp', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      render(
        <DateRangeSelector
          {...defaultProps}
          value="today"
          onChange={onChange}
        />
      );

      const button = screen.getByRole('button', { name: /select date range/i });
      button.focus();
      await user.keyboard('{Enter}'); // Open dropdown
      await user.keyboard('{ArrowUp}');

      expect(onChange).toHaveBeenCalledWith('today');
    });

    it('should not go beyond last option with ArrowDown', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      render(
        <DateRangeSelector
          {...defaultProps}
          value="last_month"
          onChange={onChange}
        />
      );

      const button = screen.getByRole('button', { name: /select date range/i });
      button.focus();
      await user.keyboard('{Enter}'); // Open dropdown
      await user.keyboard('{ArrowDown}');

      expect(onChange).toHaveBeenCalledWith('last_month');
    });
  });

  describe('Accessibility', () => {
    it('should have aria-haspopup attribute', () => {
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });
      expect(button).toHaveAttribute('aria-haspopup', 'listbox');
    });

    it('should have aria-expanded attribute', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });
      expect(button).toHaveAttribute('aria-expanded', 'false');

      await user.click(button);
      expect(button).toHaveAttribute('aria-expanded', 'true');
    });

    it('should have aria-label on the button', () => {
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });
      expect(button).toHaveAttribute('aria-label', 'Select date range');
    });

    it('should have aria-label on the listbox', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);

      const listbox = screen.getByRole('listbox');
      expect(listbox).toHaveAttribute('aria-label', 'Date range options');
    });

    it('should have aria-selected on options', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} value="last_7_days" />);

      const button = screen.getByRole('button', { name: /select date range/i });
      await user.click(button);

      const options = screen.getAllByRole('option');
      const selectedOption = options.find(
        (opt) => opt.getAttribute('aria-selected') === 'true'
      );
      expect(selectedOption).toHaveTextContent('Last 7 Days');
    });
  });

  describe('Edge Cases', () => {
    it('should handle unknown value gracefully', () => {
      // TypeScript would normally prevent this, but testing runtime behavior
      const unknownValue = 'unknown_value' as unknown as typeof defaultProps.value;
      render(
        <DateRangeSelector
          {...defaultProps}
          value={unknownValue}
        />
      );

      expect(screen.getByText('Select Range')).toBeInTheDocument();
    });

    it('should toggle dropdown on repeated clicks', async () => {
      const user = userEvent.setup();
      render(<DateRangeSelector {...defaultProps} />);

      const button = screen.getByRole('button', { name: /select date range/i });

      // First click - open
      await user.click(button);
      expect(screen.getByRole('listbox')).toBeInTheDocument();

      // Second click - close
      await user.click(button);
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();

      // Third click - open again
      await user.click(button);
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });
  });
});
