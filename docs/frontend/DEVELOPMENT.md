# Frontend Development Guide

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout with Header/Footer
│   ├── page.tsx             # Landing page with agent cards
│   └── test-cases/
│       └── page.tsx         # Test Cases Agent page
├── components/
│   ├── layout/
│   │   ├── Header.tsx       # Navigation header
│   │   └── Footer.tsx       # Page footer
│   ├── AgentCard.tsx        # Agent card for landing page
│   └── test-cases/
│       ├── GenerationForm.tsx    # Main form orchestrator
│       ├── UserStoryTab.tsx      # User story input
│       ├── ApiSpecTab.tsx        # API spec input
│       ├── FreeFormTab.tsx       # Free-form input
│       ├── ConfigPanel.tsx       # Generation settings
│       ├── TestCaseCard.tsx      # Test case display card
│       └── TestCaseDetail.tsx    # Full test case modal
├── hooks/
│   └── useGenerateTestCases.ts   # Generation state hook
├── lib/
│   └── grpc/
│       ├── testCasesClient.ts    # gRPC-Web client
│       └── generated/            # Proto-generated types
│           └── test_cases.ts
├── scripts/
│   └── generate-proto.sh         # Proto compilation
└── package.json
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run proto:gen` | Regenerate proto types |

## Styling

### Design System

Uses Macy's brand colors via CSS variables:

```css
:root {
  --accent-default: #CE0037;    /* Macy's Red */
  --accent-hover: #A8002D;
  --text-primary: #1a1a1a;
  --text-secondary: #4a4a4a;
  --text-muted: #6b7280;
  --bg-secondary: #f5f5f5;
  --border-default: #e5e5e5;
}
```

### Tailwind Classes

```tsx
// Primary button
<button className="bg-[var(--accent-default)] text-white hover:bg-[var(--accent-hover)]">

// Card
<div className="bg-white rounded-lg border border-[var(--border-default)] p-6">

// Status badge
<span className="px-2 py-1 text-xs rounded bg-green-100 text-green-800">
```

## Component Patterns

### Form Input

```tsx
<div>
  <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
    Label <span className="text-red-500">*</span>
  </label>
  <input
    className="w-full px-4 py-3 rounded-lg border border-[var(--border-default)]
               focus:ring-2 focus:ring-[var(--accent-default)]"
    required
  />
</div>
```

### Loading State

```tsx
{loading ? (
  <button disabled className="opacity-50 cursor-not-allowed">
    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0..." />
    </svg>
    Loading...
  </button>
) : (
  <button>Submit</button>
)}
```

### Error Display

```tsx
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
    <svg className="w-5 h-5 text-red-500">...</svg>
    <div>
      <h4 className="font-medium text-red-800">Error</h4>
      <p className="text-sm text-red-600">{error}</p>
    </div>
  </div>
)}
```

## State Management

### Local State with Hooks

```tsx
// Form state
const [story, setStory] = useState('');
const [testTypes, setTestTypes] = useState<TestType[]>([TestType.FUNCTIONAL]);

// Generation state via custom hook
const { generateTestCases, loading, error, testCases } = useGenerateTestCases();
```

### Form Data Interface

```typescript
interface GenerateFormData {
  inputType: 'user_story' | 'api_spec' | 'free_form';

  // User Story
  story?: string;
  acceptanceCriteria?: string[];

  // API Spec
  apiSpec?: string;
  specFormat?: 'openapi' | 'graphql';

  // Free Form
  freeFormText?: string;

  // Config
  outputFormat: OutputFormat;
  coverageLevel: CoverageLevel;
  testTypes: TestType[];
  maxTestCases: number;
}
```

## Proto Types

### Regenerating Types

After modifying `/protos/test_cases.proto`:

```bash
npm run proto:gen
```

### Using Enums

```typescript
import { TestType, OutputFormat, CoverageLevel } from '@/lib/grpc/generated/test_cases';

// As values (not types)
const defaultTypes = [TestType.FUNCTIONAL, TestType.NEGATIVE];

// Type-only imports
import type { TestCase, GenerationMetadata } from '@/lib/grpc/generated/test_cases';
```

## Adding New Features

### 1. New Input Tab

```tsx
// components/test-cases/NewTab.tsx
interface NewTabProps {
  value: string;
  onChange: (value: string) => void;
}

export function NewTab({ value, onChange }: NewTabProps) {
  return (
    <div>
      <textarea value={value} onChange={e => onChange(e.target.value)} />
    </div>
  );
}
```

### 2. New Configuration Option

1. Add to `GenerateFormData` interface in hook
2. Add UI in `ConfigPanel.tsx`
3. Map to proto in `useGenerateTestCases.ts`

### 3. New Page

```tsx
// app/new-feature/page.tsx
export default function NewFeaturePage() {
  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      <h1>New Feature</h1>
    </main>
  );
}
```

## Testing

### Running Tests

```bash
npm test              # Run all tests
npm test -- --watch   # Watch mode
```

### Testing Components

```tsx
import { render, screen } from '@testing-library/react';
import { TestCaseCard } from '@/components/test-cases/TestCaseCard';

test('renders test case title', () => {
  render(<TestCaseCard testCase={mockTestCase} outputFormat={OutputFormat.TRADITIONAL} />);
  expect(screen.getByText(mockTestCase.title)).toBeInTheDocument();
});
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_GRPC_WEB_URL` | `http://localhost:8080` | Envoy proxy URL |
| `NEXT_PUBLIC_USE_MOCK` | `true` | Enable mock mode |
| `NEXT_PUBLIC_TEST_DATA_AGENT_URL` | `http://localhost:3001` | Test Data Agent URL |

## Troubleshooting

### Build Errors

**"Cannot use TestType as value"**
```typescript
// Wrong
import type { TestType } from './generated/test_cases';

// Correct
import { TestType } from './generated/test_cases';
```

**"lib/ directory ignored"**
```bash
git add -f lib/grpc/generated/
```

### Runtime Errors

**"Service unavailable"**
- Check if backend is running on port 9003
- Check if Envoy is running on port 8080
- Try mock mode: `NEXT_PUBLIC_USE_MOCK=true`

**"Port 3000 in use"**
```bash
lsof -i :3000
kill -9 <PID>
```

## Best Practices

1. **Use TypeScript strictly** - No `any` types
2. **Prefer Server Components** - Use 'use client' only when needed
3. **Keep components small** - Extract logic to hooks
4. **Use CSS variables** - Maintain design consistency
5. **Handle all states** - Loading, error, empty, success
