'use client';

/**
 * ExportButton Component
 * Dropdown button for exporting analytics data in various formats.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { exportToCSV } from '@/lib/analytics/utils';

// ============================================================================
// Types
// ============================================================================

export type ExportFormat = 'csv' | 'json' | 'pdf';

export interface ExportOption {
  format: ExportFormat;
  label: string;
  icon: React.ReactNode;
}

export interface ExportButtonProps {
  /**
   * Data to export (array of objects)
   */
  data: Record<string, unknown>[];
  /**
   * Filename (without extension)
   */
  filename?: string;
  /**
   * Available export formats
   */
  formats?: ExportFormat[];
  /**
   * Callback when export is triggered
   */
  onExport?: (format: ExportFormat) => void;
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
// Constants
// ============================================================================

const EXPORT_OPTIONS: ExportOption[] = [
  {
    format: 'csv',
    label: 'Export as CSV',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
    ),
  },
  {
    format: 'json',
    label: 'Export as JSON',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
        />
      </svg>
    ),
  },
  {
    format: 'pdf',
    label: 'Export as PDF',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
        />
      </svg>
    ),
  },
];

// ============================================================================
// Helper Functions
// ============================================================================

function downloadAsJSON(data: Record<string, unknown>[], filename: string): void {
  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.json`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function downloadAsPDF(): void {
  // PDF export is a placeholder - would require a library like jsPDF
  // For Phase 1, we show a message that this feature is coming soon
  alert('PDF export will be available in a future update.');
}

// ============================================================================
// Component
// ============================================================================

export function ExportButton({
  data,
  filename = 'analytics-export',
  formats = ['csv', 'json'],
  onExport,
  className = '',
  disabled = false,
}: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Filter available options based on formats prop
  const availableOptions = EXPORT_OPTIONS.filter((opt) =>
    formats.includes(opt.format)
  );

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

  // Handle export action
  const handleExport = useCallback(
    async (format: ExportFormat) => {
      if (data.length === 0) {
        return;
      }

      setIsExporting(true);
      setIsOpen(false);

      try {
        const timestampedFilename = `${filename}-${new Date().toISOString().split('T')[0]}`;

        switch (format) {
          case 'csv':
            exportToCSV(data, timestampedFilename);
            break;
          case 'json':
            downloadAsJSON(data, timestampedFilename);
            break;
          case 'pdf':
            downloadAsPDF();
            break;
        }

        onExport?.(format);
      } catch (error) {
        console.error('Export failed:', error);
      } finally {
        setIsExporting(false);
        buttonRef.current?.focus();
      }
    },
    [data, filename, onExport]
  );

  // If only one format, show simple button
  if (availableOptions.length === 1) {
    const option = availableOptions[0];
    return (
      <button
        ref={buttonRef}
        type="button"
        onClick={() => handleExport(option.format)}
        disabled={disabled || isExporting || data.length === 0}
        aria-label={option.label}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg border
          bg-white text-sm font-medium
          transition-all duration-200
          ${
            disabled || data.length === 0
              ? 'text-gray-400 border-gray-200 cursor-not-allowed'
              : 'text-[var(--text-primary)] border-[var(--border-default)] hover:border-[var(--accent-default)] hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:ring-opacity-50'
          }
          ${className}
        `}
      >
        {isExporting ? (
          <svg
            className="w-4 h-4 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : (
          option.icon
        )}
        <span>Export</span>
      </button>
    );
  }

  // Multiple formats - show dropdown
  return (
    <div ref={dropdownRef} className={`relative inline-block ${className}`}>
      {/* Trigger Button */}
      <button
        ref={buttonRef}
        type="button"
        onClick={() => !disabled && setIsOpen((prev) => !prev)}
        disabled={disabled || isExporting || data.length === 0}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        aria-label="Export options"
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg border
          bg-white text-sm font-medium
          transition-all duration-200
          ${
            disabled || data.length === 0
              ? 'text-gray-400 border-gray-200 cursor-not-allowed'
              : 'text-[var(--text-primary)] border-[var(--border-default)] hover:border-[var(--accent-default)] hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-default)] focus:ring-opacity-50'
          }
        `}
      >
        {/* Download Icon */}
        {isExporting ? (
          <svg
            className="w-4 h-4 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : (
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
        )}

        <span>Export</span>

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
          role="menu"
          aria-label="Export format options"
          className="
            absolute right-0 mt-2 w-48 py-1
            bg-white rounded-lg border border-[var(--border-default)]
            shadow-lg z-50
            animate-fade-in
          "
        >
          {availableOptions.map((option) => (
            <button
              key={option.format}
              role="menuitem"
              onClick={() => handleExport(option.format)}
              className="
                w-full px-4 py-2 text-left text-sm
                text-[var(--text-secondary)]
                transition-colors duration-150
                hover:bg-gray-50
                flex items-center gap-3
              "
            >
              <span className="text-[var(--text-muted)]">{option.icon}</span>
              <span>{option.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default ExportButton;
