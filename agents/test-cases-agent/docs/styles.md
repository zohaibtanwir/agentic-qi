# QA Platform - Design System & Styling Guide

> Based on the Test Data Agent UI implementation

## Overview

The QA Platform uses a clean, professional design system inspired by the Macy's brand, built with Next.js 14, Tailwind CSS, and shadcn/ui components.

## Color Palette

### Brand Colors (Macy's)

```css
/* Primary Red */
--macys-red: #CE0037           /* Main brand color */
--macys-red-dark: #A8002C      /* Hover states */
--macys-red-light: #E53E3E     /* Light accent */

/* Neutrals */
--macys-black: #000000
--macys-gray-dark: #333333
--macys-gray: #666666
--macys-gray-light: #999999
--macys-gray-lighter: #E5E5E5
--macys-white: #FFFFFF
```

### Application Colors

```css
/* Backgrounds */
--bg-primary: #FFFFFF          /* Main background */
--bg-secondary: #F7F7F7        /* Secondary panels */
--bg-tertiary: #E5E5E5         /* Disabled/inactive */
--bg-elevated: #FFFFFF         /* Cards, modals */

/* Borders */
--border-default: #E5E5E5      /* Standard borders */
--border-light: #F0F0F0        /* Subtle dividers */

/* Text */
--text-primary: #000000        /* Main content */
--text-secondary: #333333      /* Secondary text */
--text-muted: #666666          /* Hints, labels */

/* Accent (Interactive elements) */
--accent-default: #CE0037      /* Buttons, links */
--accent-hover: #A8002C        /* Hover state */
--accent-muted: rgba(206, 0, 55, 0.1)  /* Light background */
--accent-foreground: #FFFFFF   /* Text on accent */

/* Status Colors */
--warning: #FFB000
--error: #CE0037
--success: #10B981
--info: #0062CC
```

## Typography

### Font Families

```css
/* Primary Sans-serif */
font-family: 'Plus Jakarta Sans', sans-serif;

/* Monospace (code, technical content) */
font-family: 'JetBrains Mono', monospace;

/* Alternative (local fonts) */
font-family: 'Geist Sans', sans-serif;
font-family: 'Geist Mono', monospace;
```

### Font Sizes & Weights

```css
/* Headings */
.text-4xl: 2.25rem  /* Page titles */
.text-3xl: 1.875rem /* Section titles */
.text-2xl: 1.5rem   /* Card titles */
.text-xl: 1.25rem   /* Subsection titles */
.text-lg: 1.125rem  /* Large body */

/* Body */
.text-base: 1rem    /* Default */
.text-sm: 0.875rem  /* Small text, labels */
.text-xs: 0.75rem   /* Captions */

/* Weights */
.font-normal: 400
.font-medium: 500
.font-semibold: 600
.font-bold: 700
```

## Spacing & Layout

### Container Widths

```css
/* Max widths */
.max-w-7xl: 80rem    /* Main content area */
.max-w-6xl: 72rem    /* Standard container */
.max-w-4xl: 56rem    /* Narrow content */
```

### Spacing Scale (Tailwind)

```css
.space-1: 0.25rem   /* 4px */
.space-2: 0.5rem    /* 8px */
.space-3: 0.75rem   /* 12px */
.space-4: 1rem      /* 16px */
.space-6: 1.5rem    /* 24px */
.space-8: 2rem      /* 32px */
.space-12: 3rem     /* 48px */
```

### Padding & Margins

```css
/* Common patterns */
.p-4: padding 1rem
.p-6: padding 1.5rem
.px-6: padding-left/right 1.5rem
.py-4: padding-top/bottom 1rem

/* Page layout */
main: px-6 py-8
section: mb-8
card: p-6
```

## Border Radius

```css
--radius: 0.5rem          /* Default (8px) */

.rounded: 6px             /* Default */
.rounded-lg: 8px          /* Large */
.rounded-xl: 12px         /* Extra large */
.rounded-md: 6px          /* Medium */
.rounded-sm: 4px          /* Small */
```

## Shadows

```css
/* Elevation levels */
.shadow-sm: box-shadow 0 1px 2px rgba(0, 0, 0, 0.05)
.shadow: box-shadow 0 1px 3px rgba(0, 0, 0, 0.1)
.shadow-md: box-shadow 0 4px 6px rgba(0, 0, 0, 0.1)
.shadow-lg: box-shadow 0 10px 15px rgba(0, 0, 0, 0.1)

/* Common usage */
header: shadow-sm
card: shadow-sm
modal: shadow-lg
dropdown: shadow-md
```

## Component Patterns

### Header

```tsx
/* Fixed header with brand colors */
<header className="fixed top-0 w-full h-16 bg-white border-b border-border-default shadow-sm z-50">
  <div className="flex items-center justify-between h-full px-6">
    {/* Logo and title */}
    <div className="flex items-center space-x-4">
      <Logo className="h-8 w-auto" />
      <span className="text-lg font-semibold text-gray-700">Agent Name</span>
    </div>

    {/* Actions/Status */}
    <div className="flex items-center space-x-4">
      <Badge variant="outline">Status</Badge>
    </div>
  </div>
</header>
```

### Sidebar

```tsx
/* Side navigation */
<aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-bg-secondary border-r border-border-default">
  <nav className="p-4 space-y-2">
    {/* Navigation items */}
  </nav>
</aside>
```

### Cards

```tsx
/* Content card */
<div className="bg-white rounded-lg border border-border-default p-6 shadow-sm">
  <h3 className="text-xl font-semibold mb-4">Card Title</h3>
  {/* Content */}
</div>

/* Elevated card (hover state) */
<div className="bg-white rounded-lg border border-border-default p-6 shadow-sm hover:shadow-md transition-shadow">
  {/* Content */}
</div>
```

### Buttons

```tsx
/* Primary (accent color) */
<button className="bg-accent text-white px-4 py-2 rounded-md hover:bg-accent-hover transition-colors font-medium">
  Primary Action
</button>

/* Secondary */
<button className="bg-bg-secondary text-text-primary px-4 py-2 rounded-md hover:bg-bg-tertiary transition-colors">
  Secondary Action
</button>

/* Outline */
<button className="border border-border-default bg-white px-4 py-2 rounded-md hover:bg-bg-secondary transition-colors">
  Outline Button
</button>
```

### Form Inputs

```tsx
/* Text input */
<input
  className="w-full px-3 py-2 border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
  type="text"
  placeholder="Enter text..."
/>

/* Select */
<select className="w-full px-3 py-2 border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent">
  <option>Option 1</option>
</select>

/* Textarea */
<textarea
  className="w-full px-3 py-2 border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
  rows={4}
/>
```

### Badges & Status Indicators

```tsx
/* Status badge */
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-accent-muted text-accent">
  Active
</span>

/* With dot indicator */
<span className="inline-flex items-center gap-2">
  <span className="w-2 h-2 rounded-full bg-green-500" />
  <span className="text-sm">Healthy</span>
</span>
```

## Layout Structure

### Main Application Layout

```tsx
<div className="min-h-screen bg-bg-primary">
  {/* Header - Fixed */}
  <Header />

  {/* Main Content Area */}
  <div className="flex pt-16">
    {/* Sidebar - Fixed (optional) */}
    <Sidebar />

    {/* Page Content */}
    <main className="flex-1 p-6 lg:p-8">
      {children}
    </main>
  </div>
</div>
```

### Page Layout Pattern

```tsx
<div className="max-w-7xl mx-auto space-y-8">
  {/* Page Header */}
  <div className="mb-8">
    <h1 className="text-4xl font-bold text-text-primary mb-2">Page Title</h1>
    <p className="text-text-muted">Page description</p>
  </div>

  {/* Content Sections */}
  <section className="space-y-6">
    {/* Cards, forms, etc. */}
  </section>
</div>
```

## Dark Mode (Optional Future Feature)

Currently using light mode only. Dark mode support can be added using:

```tsx
/* tailwind.config.ts */
darkMode: ["class"]

/* CSS variables for dark mode */
.dark {
  --background: 0 0% 10%;
  --foreground: 0 0% 98%;
  /* ... other dark mode colors */
}
```

## Animation & Transitions

### Hover Transitions

```css
/* Standard transition */
.transition-colors: transition-property: background-color, color;
.transition-shadow: transition-property: box-shadow;
.duration-200: transition-duration: 200ms;

/* Common pattern */
.hover:bg-accent-hover.transition-colors.duration-200
```

### Loading States

```tsx
/* Pulse animation */
<div className="animate-pulse">
  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
</div>

/* Spin animation */
<svg className="animate-spin h-5 w-5 text-accent">
  {/* Spinner icon */}
</svg>
```

## Accessibility

### Focus States

```css
/* Focus ring */
.focus:outline-none
.focus:ring-2
.focus:ring-accent
.focus:ring-offset-2
```

### Color Contrast

- Primary text (#000000) on white background: AAA compliant
- Accent red (#CE0037) on white: AA compliant for large text
- Secondary text (#666666) on white: AA compliant

## Component Library

Using **shadcn/ui** components:
- Button
- Card
- Badge
- Input
- Select
- Textarea
- Dialog
- Tabs
- Alert
- Progress
- Slider
- Checkbox
- Switch
- Table
- Tooltip
- Dropdown Menu

## Usage Guidelines

1. **Consistency**: Use the defined color variables, not hardcoded colors
2. **Spacing**: Follow the Tailwind spacing scale
3. **Typography**: Use semantic heading levels (h1-h6)
4. **Responsiveness**: Mobile-first approach with Tailwind breakpoints
5. **Accessibility**: Always include proper ARIA labels and focus states

## Responsive Breakpoints

```css
sm: 640px   /* Small devices */
md: 768px   /* Medium devices */
lg: 1024px  /* Large devices */
xl: 1280px  /* Extra large */
2xl: 1536px /* 2X Extra large */
```

## Examples

### Dashboard Card

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div className="bg-white p-6 rounded-lg border border-border-default shadow-sm">
    <h3 className="text-lg font-semibold mb-2">Test Cases Generated</h3>
    <p className="text-3xl font-bold text-accent">1,234</p>
    <p className="text-sm text-text-muted mt-2">+12% from last month</p>
  </div>
</div>
```

### Form Section

```tsx
<div className="bg-white p-6 rounded-lg border border-border-default">
  <h2 className="text-2xl font-semibold mb-4">Generate Test Cases</h2>

  <div className="space-y-4">
    <div>
      <label className="block text-sm font-medium text-text-primary mb-2">
        Requirement
      </label>
      <textarea
        className="w-full px-3 py-2 border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent"
        rows={4}
        placeholder="Enter your requirement..."
      />
    </div>

    <button className="bg-accent text-white px-6 py-2 rounded-md hover:bg-accent-hover transition-colors font-medium">
      Generate
    </button>
  </div>
</div>
```

---

**Last Updated**: December 21, 2025
**Version**: 1.0.0
**Based On**: Test Data Agent UI Implementation
