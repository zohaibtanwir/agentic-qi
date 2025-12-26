'use client';

/**
 * DateRangeSelector Component
 * Dropdown selector for choosing analytics date ranges.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { DateRange } from '@/lib/analytics/types';
import { DATE_RANGE_OPTIONS } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export interface DateRangeSelectorProps {
  /**
   * Currently selected date range
   */
  value: DateRange;
  /**
   * Callback when date range changes
   */
  onChange: (range: DateRange) => void;
  /**
   * Optional CSS class name
   */
  className?: string;
  /**
   * Disabled state
   */
  disabled?: boolean;
}

// ============================================================================
// Component
// ============================================================================

export function DateRangeSelector({
  value,
  onChange,
  className = '',
  disabled = false,
}: DateRangeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Get the label for the current value
  const currentLabel =
    DATE_RANGE_OPTIONS.find((opt) => opt.value === value)?.label ?? 'Select Range';

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Close dropdown on escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);

  // Handle option selection
  const handleSelect = useCallback(
    (optionValue: string) => {
      onChange(optionValue as DateRange);
      setIsOpen(false);
      buttonRef.current?.focus();
    },
    [onChange]
  );

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (disabled) return;

      switch (event.key) {
        case 'Enter':
        case ' ':
          event.preventDefault();
          setIsOpen((prev) => !prev);
          break;
        case 'ArrowDown':
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
          } else {
            const currentIndex = DATE_RANGE_OPTIONS.findIndex(
              (opt) => opt.value === value
            );
            const nextIndex = Math.min(
              currentIndex + 1,
              DATE_RANGE_OPTIONS.length - 1
            );
            onChange(DATE_RANGE_OPTIONS[nextIndex].value as DateRange);
          }
          break;
        case 'ArrowUp':
          event.preventDefault();
          if (isOpen) {
            const currentIndex = DATE_RANGE_OPTIONS.findIndex(
              (opt) => opt.value === value
            );
            const prevIndex = Math.max(currentIndex - 1, 0);
            onChange(DATE_RANGE_OPTIONS[prevIndex].value as DateRange);
          }
          break;
      }
    },
    [disabled, isOpen, value, onChange]
  );

  return (
    <div ref={dropdownRef} className={`relative inline-block ${className}`}>
      {/* Trigger Button */}
      <button
        ref={buttonRef}
        type="button"
        onClick={() => !disabled && setIsOpen((prev) => !prev)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label="Select date range"
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg border
          bg-white text-sm font-medium
          transition-all duration-200
          ${
            disabled
              ? 'text-gray-400 border-gray-200 cursor-not-allowed'
              : 'text-[var(--text-primary)] border-[var(--border-default)] hover:border-[var(--accent-default)] hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:ring-opacity-50'
          }
        `}
      >
        {/* Calendar Icon */}
        <svg
          className="w-4 h-4 text-[var(--text-muted)]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>

        {/* Current Value */}
        <span>{currentLabel}</span>

        {/* Chevron Icon */}
        <svg
          className={`w-4 h-4 text-[var(--text-muted)] transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          role="listbox"
          aria-label="Date range options"
          className="
            absolute right-0 mt-2 w-48 py-1
            bg-white rounded-lg border border-[var(--border-default)]
            shadow-lg z-50
            animate-fade-in
          "
        >
          {DATE_RANGE_OPTIONS.map((option) => {
            const isSelected = option.value === value;
            return (
              <button
                key={option.value}
                role="option"
                aria-selected={isSelected}
                onClick={() => handleSelect(option.value)}
                className={`
                  w-full px-4 py-2 text-left text-sm
                  transition-colors duration-150
                  ${
                    isSelected
                      ? 'bg-[var(--accent-light)] text-[var(--accent-default)] font-medium'
                      : 'text-[var(--text-secondary)] hover:bg-gray-50'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <span>{option.label}</span>
                  {isSelected && (
                    <svg
                      className="w-4 h-4 text-[var(--accent-default)]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default DateRangeSelector;
