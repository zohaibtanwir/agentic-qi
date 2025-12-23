# Test Data Agent - Central UI Integration PRD

## Overview

This PRD defines the integration of the Test Data Agent into the QA Platform's central frontend, matching the exact features and design of the standalone Test Data Agent UI.

**Current State**: Test Data Agent is listed as an external link to `localhost:3001`
**Target State**: Fully integrated within the central frontend at `/test-data` route with identical functionality

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                      QA Platform Frontend                        │
│                      (Next.js 14 - Port 3000)                    │
├─────────────────────────────────────────────────────────────────┤
│  /                    → Home (Agent Cards)                       │
│  /test-cases          → Test Cases Agent                         │
│  /test-data           → Test Data Agent (NEW)                    │
│  /test-data/schemas   → Schemas Browser                          │
│  /test-data/history   → Generation History                       │
│  /test-data/templates → Data Templates                           │
│  /test-data/docs      → API Documentation                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Envoy Proxy (Port 8085)                     │
│                      gRPC-Web Translation                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│   Test Cases Agent            │   │   Test Data Agent              │
│   gRPC (Port 9003)            │   │   gRPC (Port 9001)             │
└───────────────────────────────┘   └───────────────────────────────┘
```

---

## Design System

### Color Palette (Light Macy's Theme)

```css
:root {
  /* Macy's Brand Colors */
  --macys-red: #CE0037;
  --macys-red-dark: #A8002C;
  --macys-red-light: #E53E3E;
  --macys-black: #000000;
  --macys-gray-dark: #333333;
  --macys-gray: #666666;
  --macys-gray-light: #999999;
  --macys-gray-lighter: #E5E5E5;
  --macys-white: #FFFFFF;

  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F7F7F7;
  --bg-tertiary: #E5E5E5;
  --bg-elevated: #FFFFFF;

  /* Borders */
  --border-default: #E5E5E5;
  --border-light: #F0F0F0;

  /* Text */
  --text-primary: #000000;
  --text-secondary: #333333;
  --text-muted: #666666;

  /* Accent (Macy's Red) */
  --accent-default: #CE0037;
  --accent-hover: #A8002C;
  --accent-muted: rgba(206, 0, 55, 0.1);
  --accent-foreground: #FFFFFF;

  /* Status */
  --warning: #FFB000;
  --error: #CE0037;
  --success: #10B981;
  --info: #0062CC;
}
```

### Typography

```css
/* UI Text */
font-family: 'Plus Jakarta Sans', sans-serif;

/* Code & Data */
font-family: 'JetBrains Mono', monospace;
```

---

## UI Layout

### Full Page Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HEADER (fixed, 64px) - White bg, bottom border                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ [Macy's Logo] │ Test Data Agent │ ● Service healthy │ AI-Powered...   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
├─────────────────────┬───────────────────────────────────────────────────────┤
│  SIDEBAR (collaps.) │  MAIN CONTENT                                         │
│  264px / 64px       │                                                       │
│                     │  ┌──────────────────────────────────────────────────┐ │
│  ┌───────────────┐  │  │ Test Data Generator                              │ │
│  │ [←]           │  │  │ Generate realistic test data using AI-powered... │ │
│  │               │  │  └──────────────────────────────────────────────────┘ │
│  │ ✨ Generator  │  │                                                       │
│  │ 🗃️ Schemas    │  │  ┌────────────────────────┐ ┌────────────────────────┐│
│  │ 🕒 History    │  │  │  GENERATOR FORM        │ │  DATA PREVIEW          ││
│  │ 📄 Templates  │  │  │                        │ │                        ││
│  │ 📖 Documentation│ │  │  [Domain ▼] [Entity ▼] │ │  Generated Data        ││
│  │ ⚙️ Settings   │  │  │                        │ │  ─────────────────────  ││
│  │               │  │  │  Generation Path       │ │  [JSON] [Table] [Stats]││
│  │ ──────────── │  │  │  [Auto ▼]              │ │                        ││
│  │               │  │  │                        │ │  {                     ││
│  │ GENERATION    │  │  │  Records: ────●─── 50 │ │    "cart_id": "...",   ││
│  │ PATHS         │  │  │                        │ │    "items": [...]      ││
│  │               │  │  │  Context [textarea]    │ │  }                     ││
│  │ 🔵 Traditional│  │  │                        │ │                        ││
│  │ 🔴 LLM        │  │  │  ────────────────────  │ │  ─────────────────────  ││
│  │ 🟢 RAG        │  │  │  [Options][Scenarios]  │ │  [Copy] [Download]     ││
│  │ 🟡 Hybrid     │  │  │  [Schema][Output]      │ │                        ││
│  │               │  │  │                        │ │  LLM │ 1.2s │ 0.95    ││
│  └───────────────┘  │  │  [✨ Generate Data]    │ │  Path  Time   Score    ││
│                     │  └────────────────────────┘ └────────────────────────┘│
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

## Component Specifications

### Directory Structure

```
frontend/
├── app/
│   └── test-data/
│       ├── page.tsx              # Main Generator page
│       ├── schemas/page.tsx      # Schemas browser
│       ├── history/page.tsx      # Generation history
│       ├── templates/page.tsx    # Data templates
│       └── docs/page.tsx         # API documentation
├── components/
│   └── test-data/
│       ├── TestDataPage.tsx      # Main page container
│       ├── layout/
│       │   ├── TestDataHeader.tsx    # Header with Macy's logo
│       │   ├── TestDataSidebar.tsx   # Collapsible navigation
│       │   └── TestDataLayout.tsx    # Layout wrapper
│       ├── generator/
│       │   ├── GeneratorForm.tsx     # Main form card
│       │   ├── ScenarioManager.tsx   # Scenario list management
│       │   └── SchemaEditor.tsx      # Schema field editor
│       ├── preview/
│       │   ├── DataPreview.tsx       # Preview card
│       │   ├── JsonView.tsx          # JSON syntax view
│       │   ├── TableView.tsx         # Tabular data view
│       │   └── StatsView.tsx         # Generation statistics
│       └── ui/
│           └── macys-logo.tsx        # Macy's star logo
├── lib/
│   └── grpc/
│       ├── generated/
│       │   └── test_data.ts          # Generated protobuf types
│       └── testDataClient.ts         # gRPC-Web client
├── stores/
│   └── generator-store.ts            # Zustand store
└── hooks/
    └── useTestDataHealth.ts
```

---

### 1. Header Component (`TestDataHeader.tsx`)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [★ Macy's Logo] │ Test Data Agent │ ● Service healthy │ AI-Powered Test... │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Macy's star logo (MacysLogo component)
- "Test Data Agent" title with separator
- Service status badge polling `/health` endpoint
  - Green: "Service healthy"
  - Yellow (pulsing): "Service degraded"
  - Red: "Service unhealthy"
- Tagline: "AI-Powered Test Data Generation"

**Styling:**
- `bg-white` background
- `border-b border-border-default` bottom border
- `shadow-sm` subtle shadow
- Fixed position, `h-16`, `z-50`

---

### 2. Sidebar Component (`TestDataSidebar.tsx`)

**Features:**
- Collapsible (264px expanded / 64px collapsed)
- Toggle button (ChevronLeft/ChevronRight)
- Navigation items with icons
- Generation Paths legend at bottom

**Navigation Items:**
| Icon | Label | Path | Description |
|------|-------|------|-------------|
| Sparkles | Generator | `/test-data` | Main generator page |
| Database | Schemas | `/test-data/schemas` | Browse available schemas |
| History | History | `/test-data/history` | Past generations |
| FileJson | Templates | `/test-data/templates` | Saved configurations |
| BookOpen | Documentation | `/test-data/docs` | API docs |
| Settings | Settings | `/test-data/settings` | Configuration |

**Generation Paths Legend:**
| Icon | Color | Path |
|------|-------|------|
| Code2 | `text-info` | Traditional |
| Sparkles | `text-macys-red` | LLM |
| GitBranch | `text-green-600` | RAG |
| Layers | `text-warning` | Hybrid |

**Active State:**
- `bg-macys-red/10 text-macys-red`

**Styling:**
- `bg-bg-secondary` (#F7F7F7)
- `border-r border-border-default`

---

### 3. Generator Form (`GeneratorForm.tsx`)

Card containing all generation configuration.

**Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│ ✨ Test Data Generator                                          │
│ Configure your test data generation parameters                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ Domain              │  │ Entity              │              │
│  │ [E-commerce ▼]      │  │ [Cart ▼]            │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ CUSTOM ENTITY (when entity=custom)                          ││
│  │ Custom Entity Name: [_______________________]               ││
│  │ JSON Schema:                                                 ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ { "type": "object", "properties": {...} }               │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Generation Path                    [Choose how to generate]   │
│  [Auto ▼]                                                      │
│                                                                 │
│  Number of Records                                         [50]│
│  ─────────────────────────●────────────────────────────────────│
│  1                       500                              1000 │
│                                                                 │
│  Context (Optional)                                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Provide additional context for more realistic data...      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌───────────┬───────────┬───────────┬───────────┐             │
│  │  Options  │ Scenarios │  Schema   │  Output   │             │
│  └───────────┴───────────┴───────────┴───────────┘             │
│                                                                 │
│  [Options Tab Content - Switch toggles]                        │
│                                                                 │
│                                    [✨ Generate Data]          │
└─────────────────────────────────────────────────────────────────┘
```

#### Domain Dropdown

| Value | Label |
|-------|-------|
| ecommerce | E-commerce |
| financial | Financial |
| social_media | Social Media |
| healthcare | Healthcare |
| education | Education |
| logistics | Logistics |

#### Entity Dropdown

| Value | Label |
|-------|-------|
| cart | Cart |
| order | Order |
| product | Product |
| user | User |
| payment | Payment |
| review | Review |
| custom | Custom Entity... |

#### Generation Path Selector (Prominent)

| Value | Label | Description |
|-------|-------|-------------|
| auto | Auto | System decides best approach |
| traditional | Traditional | Fast rule-based generation |
| llm | LLM (AI) | Creative AI-generated data |
| rag | RAG | Pattern-based with context |
| hybrid | Hybrid | Combined approach |

#### Count Slider

- Range: 1-1000
- Step: 1
- Macy's red slider track/thumb
- Badge showing current value

#### Advanced Tabs

**Options Tab:**
| Label | Key | Description |
|-------|-----|-------------|
| Use Cache | useCache | Speed up generation with cached patterns |
| Learn from History | learnFromHistory | Use previous generation patterns |
| Defect Triggering | defectTriggering | Include edge cases and anomalies |
| Production-like | productionLike | Generate realistic production data |

Each option is a Switch toggle with label and description.

**Scenarios Tab:**
- ScenarioManager component
- Add/remove scenarios with name and count
- Shows warning if totals mismatch

**Schema Tab:**
- SchemaEditor component
- Field list with types and constraints

**Output Tab:**
| Format | Description |
|--------|-------------|
| JSON | JavaScript Object Notation |
| CSV | Comma Separated Values |
| SQL | SQL INSERT statements |
| YAML | YAML format |
| XML | XML format |

#### Generate Button

- Macy's red: `bg-macys-red hover:bg-macys-red-dark`
- Sparkles icon
- Loading state: Loader2 spinning + "Generating..."
- Disabled when invalid or generating

---

### 4. Data Preview (`DataPreview.tsx`)

**Empty State:**
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    📄                                           │
│              No data generated yet                              │
│    Configure parameters and click Generate to see results      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**With Data:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Generated Data                                      ✓ Success   │
│ 50 records generated in 1.23s                                   │
│                                              [LLM] [Score: 0.95]│
├─────────────────────────────────────────────────────────────────┤
│ [📄 JSON] [📊 Table] [📈 Stats]              [Copy] [Download] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [                                                              │
│    {                                                            │
│      "cart_id": "CRT-2025-847291",                             │
│      "customer_id": "USR-4829173",                             │
│      "items": [                                                 │
│        {                                                        │
│          "sku": "NKE-RUN-BLK-10",                              │
│          "name": "Nike Air Zoom Pegasus",                      │
│          "quantity": 1,                                         │
│          "price": 129.99                                        │
│        }                                                        │
│      ],                                                         │
│      "total": 228.34                                            │
│    },                                                           │
│    ...                                                          │
│  ]                                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Tabs:**
| Tab | Icon | Component |
|-----|------|-----------|
| JSON | FileJson | JsonView - syntax highlighted JSON |
| Table | Table2 | TableView - tabular data display |
| Stats | BarChart3 | StatsView - generation statistics |

**Path Badge Colors:**
| Path | Style |
|------|-------|
| traditional | `bg-blue-100 text-blue-700 border-blue-200` |
| llm | `bg-macys-red/10 text-macys-red border-macys-red/20` |
| rag | `bg-green-100 text-green-700 border-green-200` |
| hybrid | `bg-orange-100 text-orange-700 border-orange-200` |

---

## State Management

### Generator Store (Zustand)

```typescript
interface GeneratorState {
  // Form fields
  domain: string;
  entity: string;
  count: number;
  context: string;
  outputFormat: 'JSON' | 'CSV' | 'SQL' | 'YAML' | 'XML';
  generationPath: 'auto' | 'traditional' | 'llm' | 'rag' | 'hybrid';
  inlineSchema: string;
  scenarios: Scenario[];
  options: GenerationOptions;

  // Result
  result: GenerateResponse | null;
  error: string | null;

  // Actions
  setDomain: (domain: string) => void;
  setEntity: (entity: string) => void;
  setCount: (count: number) => void;
  setContext: (context: string) => void;
  setOutputFormat: (format: OutputFormat) => void;
  setGenerationPath: (path: GenerationPath) => void;
  setInlineSchema: (schema: string) => void;
  toggleOption: (key: keyof GenerationOptions) => void;
  setResult: (result: GenerateResponse | null) => void;
  setError: (error: string | null) => void;
  getRequestBody: () => GenerateRequest;
  reset: () => void;
}

interface GenerationOptions {
  useCache: boolean;
  learnFromHistory: boolean;
  defectTriggering: boolean;
  productionLike: boolean;
}

interface Scenario {
  name: string;
  count: number;
  description?: string;
  overrides?: Record<string, string>;
}
```

---

## Constants

```typescript
// lib/constants/testData.ts

export const DOMAINS = [
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'financial', label: 'Financial' },
  { value: 'social_media', label: 'Social Media' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'education', label: 'Education' },
  { value: 'logistics', label: 'Logistics' },
] as const;

export const ENTITIES = [
  { value: 'cart', label: 'Cart' },
  { value: 'order', label: 'Order' },
  { value: 'product', label: 'Product' },
  { value: 'user', label: 'User' },
  { value: 'payment', label: 'Payment' },
  { value: 'review', label: 'Review' },
  { value: 'custom', label: 'Custom Entity...' },
] as const;

export const OUTPUT_FORMATS = [
  { value: 'JSON', label: 'JSON' },
  { value: 'CSV', label: 'CSV' },
  { value: 'SQL', label: 'SQL' },
  { value: 'YAML', label: 'YAML' },
  { value: 'XML', label: 'XML' },
] as const;

export const GENERATION_PATHS = [
  { value: 'auto', label: 'Auto', description: 'System decides best approach' },
  { value: 'traditional', label: 'Traditional', description: 'Fast rule-based generation' },
  { value: 'llm', label: 'LLM (AI)', description: 'Creative AI-generated data' },
  { value: 'rag', label: 'RAG', description: 'Pattern-based with context' },
  { value: 'hybrid', label: 'Hybrid', description: 'Combined approach' },
] as const;

export const GENERATION_OPTIONS = [
  { key: 'useCache', label: 'Use Cache', description: 'Speed up generation with cached patterns' },
  { key: 'learnFromHistory', label: 'Learn from History', description: 'Use previous generation patterns' },
  { key: 'defectTriggering', label: 'Defect Triggering', description: 'Include edge cases and anomalies' },
  { key: 'productionLike', label: 'Production-like', description: 'Generate realistic production data' },
] as const;

export const SIDEBAR_NAVIGATION = [
  { name: 'Generator', href: '/test-data', icon: 'Sparkles' },
  { name: 'Schemas', href: '/test-data/schemas', icon: 'Database' },
  { name: 'History', href: '/test-data/history', icon: 'History' },
  { name: 'Templates', href: '/test-data/templates', icon: 'FileJson' },
  { name: 'Documentation', href: '/test-data/docs', icon: 'BookOpen' },
  { name: 'Settings', href: '/test-data/settings', icon: 'Settings' },
] as const;

export const GENERATION_PATH_COLORS = [
  { name: 'Traditional', icon: 'Code2', color: 'text-info' },
  { name: 'LLM', icon: 'Sparkles', color: 'text-macys-red' },
  { name: 'RAG', icon: 'GitBranch', color: 'text-green-600' },
  { name: 'Hybrid', icon: 'Layers', color: 'text-warning' },
] as const;
```

---

## Implementation Phases

### Phase 1: Foundation
1. Generate protobuf types from `test_data.proto`
2. Create `testDataClient.ts` with gRPC-Web client
3. Implement mock data generators for development
4. Create page routes (`/test-data`, `/test-data/schemas`, etc.)
5. Set up Zustand store (`generator-store.ts`)

### Phase 2: Layout Components
1. `MacysLogo.tsx` - Macy's star logo
2. `TestDataHeader.tsx` - Header with status
3. `TestDataSidebar.tsx` - Collapsible navigation
4. `TestDataLayout.tsx` - Layout wrapper

### Phase 3: Generator Components
1. `GeneratorForm.tsx` - Main form card with tabs
2. `ScenarioManager.tsx` - Scenario list management
3. `SchemaEditor.tsx` - Schema field editor

### Phase 4: Preview Components
1. `DataPreview.tsx` - Preview card container
2. `JsonView.tsx` - JSON syntax highlighted view
3. `TableView.tsx` - Tabular data view
4. `StatsView.tsx` - Generation statistics

### Phase 5: Integration
1. Connect components with Zustand store
2. Implement gRPC-Web calls to backend
3. Update central Header navigation
4. Update Home page AgentCard
5. Update Envoy proxy config

### Phase 6: Polish
1. Loading states throughout
2. Error handling with alerts
3. Copy/Download functionality
4. Keyboard shortcuts

---

## Navigation Updates

### Header Update
Change Test Data link from external to internal:
```tsx
// Before (external)
<a href="http://localhost:3001">Test Data</a>

// After (internal)
<Link href="/test-data">Test Data</Link>
```

### Home Page Update
Change AgentCard from external to internal:
```tsx
// Before
<AgentCard
  name="Test Data Agent"
  link="http://localhost:3001"
  external
/>

// After
<AgentCard
  name="Test Data Agent"
  link="/test-data"
/>
```

---

## Envoy Proxy Configuration

Add to existing `envoy.yaml`:

```yaml
clusters:
  - name: test_data_agent
    connect_timeout: 5s
    type: LOGICAL_DNS
    lb_policy: ROUND_ROBIN
    http2_protocol_options: {}
    load_assignment:
      cluster_name: test_data_agent
      endpoints:
        - lb_endpoints:
            - endpoint:
                address:
                  socket_address:
                    address: host.docker.internal
                    port_value: 9001
```

Route:
```yaml
- match:
    prefix: "/testdata.v1.TestDataService/"
  route:
    cluster: test_data_agent
```

---

## Success Criteria

1. **Feature Parity**: All features from standalone UI available
2. **Visual Match**: Same Macy's light theme, colors, layout
3. **Functional**: Full generation flow works
4. **Integration**: Seamless navigation with Test Cases Agent
5. **Performance**: Generation completes quickly
6. **Reliability**: Graceful error handling

---

## Dependencies

- Next.js 14 (existing)
- @bufbuild/protobuf (existing)
- zustand (new)
- lucide-react (existing)
- shadcn/ui components (existing)
- Envoy Proxy (existing at port 8085)
- Test Data Agent gRPC service (port 9001)
