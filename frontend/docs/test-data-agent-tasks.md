# Test Data Agent UI - Implementation Tasks

> **Usage:** Implementation tasks for integrating Test Data Agent into the central QA Platform frontend, matching the standalone UI exactly.

---

## Task Checklist

### Phase 1: Foundation
- [ ] Task 1.1: Generate protobuf types from test_data.proto
- [ ] Task 1.2: Create testDataClient.ts with gRPC-Web client
- [ ] Task 1.3: Implement mock data generators
- [ ] Task 1.4: Create page route at /test-data
- [ ] Task 1.5: Set up Zustand stores (generator + history)

### Phase 2: Layout Components
- [ ] Task 2.1: Create TestDataHeader component
- [ ] Task 2.2: Create TestDataSidebar component
- [ ] Task 2.3: Create TestDataLayout (3-column)
- [ ] Task 2.4: Create shared components

### Phase 3: Generator Components
- [ ] Task 3.1: Create GeneratorForm container
- [ ] Task 3.2: Create BasicConfig component
- [ ] Task 3.3: Create ContextEditor component
- [ ] Task 3.4: Create ScenarioBuilder component
- [ ] Task 3.5: Create OptionsPanel component
- [ ] Task 3.6: Create GenerateButton component

### Phase 4: Preview Components
- [ ] Task 4.1: Create DataPreview container
- [ ] Task 4.2: Create JsonViewer (Monaco)
- [ ] Task 4.3: Create CsvViewer
- [ ] Task 4.4: Create SqlViewer
- [ ] Task 4.5: Create MetadataBar

### Phase 5: Integration
- [ ] Task 5.1: Connect components with Zustand
- [ ] Task 5.2: Implement gRPC-Web calls
- [ ] Task 5.3: Add history persistence
- [ ] Task 5.4: Update Header navigation
- [ ] Task 5.5: Update Home page AgentCard
- [ ] Task 5.6: Update Envoy proxy config

### Phase 6: Polish
- [ ] Task 6.1: Loading states
- [ ] Task 6.2: Error handling
- [ ] Task 6.3: Toast notifications
- [ ] Task 6.4: Keyboard shortcuts
- [ ] Task 6.5: Final testing

---

## Phase 1: Foundation

### Task 1.1: Generate Protobuf Types

```
Generate TypeScript types from test_data.proto using @bufbuild/protobuf.

Location: frontend/lib/grpc/generated/test_data.ts

Steps:
1. Use existing proto generation setup from test_cases
2. Generate types for testdata.v1 package
3. Export all message types and enums

Key types to generate:
- GenerateRequest / GenerateResponse
- GetSchemasRequest / GetSchemasResponse
- HealthCheckRequest / HealthCheckResponse
- Schema, Field, FieldType, FieldConstraint
- Scenario, GenerationMethod, OutputFormat
- GenerationMetadata, DataChunk, SchemaInfo

Acceptance Criteria:
- [ ] Types compile without errors
- [ ] All message types exported
- [ ] Enums properly typed
```

---

### Task 1.2: Create gRPC-Web Client

```
Create the gRPC-Web client for Test Data Agent.

Location: frontend/lib/grpc/testDataClient.ts

Follow the same pattern as testCasesClient.ts:
- Binary protobuf with gRPC-Web framing
- encodeGrpcWebRequest / decodeGrpcWebResponse helpers
- grpcWebUnaryCall generic function

Methods to implement:
- generateData(request: GenerateRequest): Promise<GenerateResponse>
- getSchemas(domain?: string): Promise<GetSchemasResponse>
- healthCheck(): Promise<HealthCheckResponse>

Environment:
- GRPC_WEB_URL: http://localhost:8085
- USE_MOCK: fallback to mock data

Acceptance Criteria:
- [ ] Client connects to Envoy proxy
- [ ] generateData works
- [ ] getSchemas works
- [ ] healthCheck works
- [ ] Mock mode fallback works
```

---

### Task 1.3: Implement Mock Data Generators

```
Create mock data generators for development without backend.

Location: frontend/lib/grpc/testDataClient.ts (inside USE_MOCK block)

Mock functions:
1. mockGenerateData(request):
   - Generate fake cart/order/user data
   - Respect count and scenarios
   - Return realistic metadata

2. mockGetSchemas(domain):
   - Return predefined schemas:
     - cart (ecommerce)
     - order (ecommerce)
     - payment (ecommerce)
     - user (core)
     - review (ecommerce)
     - address (core)

3. mockHealthCheck():
   - Return healthy status

Mock data structure for cart:
{
  cart_id: "CRT-2025-XXXXX",
  customer_id: "USR-XXXXX",
  items: [...],
  total: number,
  status: string,
  created_at: ISO date
}

Acceptance Criteria:
- [ ] Mock data looks realistic
- [ ] Respects request parameters
- [ ] Returns proper metadata
```

---

### Task 1.4: Create Page Route

```
Create the Test Data page route.

Location: frontend/app/test-data/page.tsx

Initial implementation:
- Import TestDataPage component (to be created)
- Set metadata (title, description)
- Server component wrapper

export const metadata = {
  title: 'Test Data Agent | QA Platform',
  description: 'Generate realistic, schema-compliant test data',
};

export default function TestDataRoute() {
  return <TestDataPage />;
}

Acceptance Criteria:
- [ ] Route accessible at /test-data
- [ ] Metadata set correctly
- [ ] No errors on load
```

---

### Task 1.5: Set Up Zustand Stores

```
Create Zustand stores for Test Data Agent.

Location: frontend/stores/testDataGeneratorStore.ts
Location: frontend/stores/testDataHistoryStore.ts

Generator Store:
- Form state (domain, entity, count, context, scenarios, etc.)
- Result state (result, isLoading, error)
- All actions from PRD

History Store:
- entries array (HistoryEntry[])
- persist to localStorage
- addEntry, removeEntry, clearHistory
- Max 20 entries

Use zustand/middleware for persistence.

Acceptance Criteria:
- [ ] Generator store works
- [ ] History persists to localStorage
- [ ] All actions implemented
```

---

## Phase 2: Layout Components

### Task 2.1: Create TestDataHeader

```
Create header component with status indicator.

Location: frontend/components/test-data/layout/TestDataHeader.tsx

Features:
- Logo: Zap icon in emerald gradient box
- Title: "Test<span class='text-accent'>Data</span>Agent"
- Status indicator polling health endpoint
- API Docs button
- Settings button

Status states:
- connected (green): "Service Connected"
- disconnected (red): "Disconnected"
- checking (yellow, pulsing): "Checking..."

Poll interval: 30 seconds

Acceptance Criteria:
- [ ] Logo renders correctly
- [ ] Status polls and updates
- [ ] Buttons styled correctly
```

---

### Task 2.2: Create TestDataSidebar

```
Create sidebar with schemas, quick generate, and recent.

Location: frontend/components/test-data/layout/TestDataSidebar.tsx

Sections:
1. SCHEMAS - List from API with icons
2. QUICK GENERATE - 4 preset buttons
3. RECENT - History entries

Schema icons (lucide-react):
- cart: ShoppingCart
- order: Package
- payment: CreditCard
- user: User
- review: Star
- address: MapPin

Quick actions:
- Sample Carts (10)
- Sample Orders (10)
- Sample Users (25)
- Edge Cases (20)

Props:
- schemas: SchemaInfo[]
- selectedSchema: string | null
- onSchemaSelect: (name) => void
- onQuickGenerate: (type) => void
- historyEntries: HistoryEntry[]
- onHistorySelect: (entry) => void

Acceptance Criteria:
- [ ] Schemas list with selection
- [ ] Quick generate buttons work
- [ ] Recent shows history
```

---

### Task 2.3: Create TestDataLayout

```
Create 3-column layout container.

Location: frontend/components/test-data/layout/TestDataLayout.tsx

Structure:
- Header (fixed, 60px)
- Body (flex):
  - Sidebar (260px, left)
  - Main content (flexible, center)
  - Preview panel (400px, right)

Props:
- children: ReactNode (main content)
- preview: ReactNode (preview panel)
- sidebar props passed through

Use dark theme colors from PRD.

Acceptance Criteria:
- [ ] 3-column layout works
- [ ] Proper widths
- [ ] Dark theme applied
```

---

### Task 2.4: Create Shared Components

```
Create shared components for Test Data Agent.

Location: frontend/components/test-data/shared/

Components:
1. LoadingSpinner.tsx
   - Sizes: sm, md, lg
   - Emerald accent color

2. EmptyState.tsx
   - Icon, title, description props
   - Centered layout

3. ErrorMessage.tsx
   - Error icon (AlertCircle)
   - Title, message
   - Retry button

Acceptance Criteria:
- [ ] All components styled for dark theme
- [ ] Consistent with design system
```

---

## Phase 3: Generator Components

### Task 3.1: Create GeneratorForm Container

```
Create main form container.

Location: frontend/components/test-data/generator/GeneratorForm.tsx

Contains:
- Header with title and schema badge
- BasicConfig section
- ContextEditor section
- ScenarioBuilder section
- OptionsPanel section
- GenerateButton section

Uses generator store for state.

Props:
- schemas: SchemaInfo[]
- onGenerate: () => Promise<void>

Acceptance Criteria:
- [ ] All sections rendered
- [ ] Connected to store
```

---

### Task 3.2: Create BasicConfig

```
Create basic configuration section.

Location: frontend/components/test-data/generator/BasicConfig.tsx

Fields:
1. Domain dropdown (from DOMAINS constant)
2. Entity dropdown (filtered by domain from schemas)
3. Count number input (1-1000)
4. Format dropdown (JSON, CSV, SQL)

2x2 grid layout.
Use shadcn Select, Input components.

Acceptance Criteria:
- [ ] All fields work
- [ ] Entity filters by domain
- [ ] Count validates range
```

---

### Task 3.3: Create ContextEditor

```
Create context textarea.

Location: frontend/components/test-data/generator/ContextEditor.tsx

Features:
- Label with MessageSquare icon
- Textarea with placeholder
- Helper text below
- Monospace font (JetBrains Mono)
- Resizable

Placeholder: "e.g., Generate shopping carts for ApplePay checkout testing..."

Acceptance Criteria:
- [ ] Textarea styled correctly
- [ ] Value syncs with store
```

---

### Task 3.4: Create ScenarioBuilder

```
Create scenario management component.

Location: frontend/components/test-data/generator/ScenarioBuilder.tsx

Features:
- List of scenarios with name, count, remove button
- Add new scenario (input + button)
- Warning when total != count
- Can't remove last scenario
- Enter to add

Each scenario row:
- Editable name input
- Count number input
- Remove (X) button

Acceptance Criteria:
- [ ] Add/remove/edit scenarios
- [ ] Warning shows correctly
- [ ] Enter key works
```

---

### Task 3.5: Create OptionsPanel

```
Create generation options panel.

Location: frontend/components/test-data/generator/OptionsPanel.tsx

Options (2x2 grid):
1. Coherent items (LLM) - useCache key
2. Learn from history (RAG) - learnFromHistory
3. Defect-triggering - defectTriggering
4. Production-like - productionLike

Each option card:
- Clickable whole card
- Checkbox
- Label
- Description
- Active state: accent bg, accent border

Acceptance Criteria:
- [ ] All 4 options render
- [ ] Click toggles
- [ ] Active state styled
```

---

### Task 3.6: Create GenerateButton

```
Create generate button with path selector.

Location: frontend/components/test-data/generator/GenerateButton.tsx

Features:
- Large button with emerald gradient
- Zap icon + "Generate Data"
- Loading: Spinner + "Generating..."
- Disabled when loading or count < 1
- Path dropdown next to button

Path options:
- Auto (Router decides)
- Traditional (Faker)
- LLM (Claude)
- RAG (Patterns)
- Hybrid (RAG + LLM)

Acceptance Criteria:
- [ ] Button styled correctly
- [ ] Loading state works
- [ ] Path selector works
```

---

## Phase 4: Preview Components

### Task 4.1: Create DataPreview Container

```
Create preview panel container.

Location: frontend/components/test-data/preview/DataPreview.tsx

States:
- Empty: EmptyState with BarChart3 icon
- Loading: Spinner + "Generating with LLM..."
- Error: ErrorMessage with retry
- Success: Data viewer + metadata

Header:
- "Generated Data" title
- Format tabs (JSON/CSV/SQL)
- Copy button
- Download button

Acceptance Criteria:
- [ ] All states handled
- [ ] Format tabs work
- [ ] Copy/download work
```

---

### Task 4.2: Create JsonViewer

```
Create Monaco-based JSON viewer.

Location: frontend/components/test-data/preview/JsonViewer.tsx

Features:
- Monaco editor (read-only)
- Custom dark theme
- JSON syntax highlighting
- Folding enabled
- JetBrains Mono font

Theme colors:
- background: #0a0f1a
- keys: #7dd3fc (light blue)
- string values: #86efac (light green)
- numbers: #fcd34d (yellow)

Acceptance Criteria:
- [ ] Monaco renders
- [ ] Theme applied
- [ ] JSON formatted
```

---

### Task 4.3: Create CsvViewer

```
Create CSV formatted viewer.

Location: frontend/components/test-data/preview/CsvViewer.tsx

Features:
- Convert JSON to CSV format
- Monospace pre block
- Handle nested objects
- Syntax highlighting (optional)

Acceptance Criteria:
- [ ] JSON to CSV conversion
- [ ] Readable format
```

---

### Task 4.4: Create SqlViewer

```
Create SQL formatted viewer.

Location: frontend/components/test-data/preview/SqlViewer.tsx

Features:
- Convert JSON to SQL INSERT statements
- Monospace pre block
- Table name from entity
- Proper escaping

Acceptance Criteria:
- [ ] JSON to SQL conversion
- [ ] Valid SQL syntax
```

---

### Task 4.5: Create MetadataBar

```
Create metadata stats bar.

Location: frontend/components/test-data/preview/MetadataBar.tsx

4-column grid:
1. Path (LLM/Traditional/RAG/Hybrid)
2. Tokens (formatted number)
3. Time (X.Xs format)
4. Coherence (0.00-1.00)

Styling:
- Large accent value
- Small muted label below
- Monospace numbers

Acceptance Criteria:
- [ ] 4 columns rendered
- [ ] Values formatted
- [ ] Dark theme styling
```

---

## Phase 5: Integration

### Task 5.1: Connect Components with Zustand

```
Wire up all components with the Zustand stores.

Main page (TestDataPage.tsx):
- Use useTestDataGeneratorStore
- Use useTestDataHistoryStore
- Pass state/actions to components
- Handle generate flow

Flow:
1. Schema select -> update domain/entity
2. Form changes -> update store
3. Generate click -> call API, update result
4. Success -> add to history

Acceptance Criteria:
- [ ] All state flows work
- [ ] History updates on generate
```

---

### Task 5.2: Implement gRPC-Web Calls

```
Connect UI to real gRPC backend.

In TestDataPage or custom hook:
- Call testDataClient.generateData on generate
- Call testDataClient.getSchemas on mount
- Call testDataClient.healthCheck for status

Handle errors gracefully.
Show loading states.

Acceptance Criteria:
- [ ] Generate calls backend
- [ ] Schemas load on mount
- [ ] Health status works
```

---

### Task 5.3: Add History Persistence

```
Ensure history persists across page reloads.

History store already uses zustand/persist.

On successful generation:
- Create label from context or entity
- Add entry with request config
- Limit to 20 entries

On history click:
- Load config into generator store
- Don't auto-generate

Acceptance Criteria:
- [ ] History survives refresh
- [ ] Entries have correct data
- [ ] Click loads config
```

---

### Task 5.4: Update Header Navigation

```
Update central header to use internal link.

Location: frontend/components/layout/Header.tsx

Change:
<a href="http://localhost:3001">Test Data</a>

To:
<Link href="/test-data">Test Data</Link>

Use Next.js Link component.

Acceptance Criteria:
- [ ] Link is internal
- [ ] Navigation works
```

---

### Task 5.5: Update Home Page AgentCard

```
Update AgentCard for Test Data Agent.

Location: frontend/app/page.tsx

Change:
<AgentCard
  name="Test Data Agent"
  link="http://localhost:3001"
  external
/>

To:
<AgentCard
  name="Test Data Agent"
  link="/test-data"
/>

Remove external prop.

Acceptance Criteria:
- [ ] Card links internally
- [ ] No external icon
```

---

### Task 5.6: Update Envoy Proxy Config

```
Add Test Data Agent cluster to Envoy.

Location: protos/envoy.yaml (or wherever config is)

Add cluster:
- name: test_data_agent
- address: host.docker.internal:9001

Add route:
- prefix: /testdata.v1.TestDataService/
- cluster: test_data_agent

Acceptance Criteria:
- [ ] Envoy routes to port 9001
- [ ] gRPC-Web requests work
```

---

## Phase 6: Polish

### Task 6.1: Loading States

```
Add loading states throughout.

Areas:
- Initial page load (schemas loading)
- Generate button (show spinner)
- Preview panel (generating message)
- Schema list (skeleton)

Use LoadingSpinner component.

Acceptance Criteria:
- [ ] No empty states during load
- [ ] Clear feedback to user
```

---

### Task 6.2: Error Handling

```
Add comprehensive error handling.

Areas:
- gRPC connection errors
- Generation failures
- Invalid input validation
- Network timeouts

Show ErrorMessage component with retry.
Log errors for debugging.

Acceptance Criteria:
- [ ] Errors shown to user
- [ ] Retry available
- [ ] Console logging
```

---

### Task 6.3: Toast Notifications

```
Add toast notifications for actions.

Events:
- Copy to clipboard: "Copied to clipboard"
- Download: "Downloaded test-data.json"
- Generation success: "Generated X records"
- Error: Error message

Use a toast library or simple custom toast.

Acceptance Criteria:
- [ ] Toasts appear
- [ ] Auto-dismiss
- [ ] Styled for dark theme
```

---

### Task 6.4: Keyboard Shortcuts

```
Add keyboard shortcuts.

Shortcuts:
- Cmd/Ctrl + Enter: Generate data
- Cmd/Ctrl + C (when preview focused): Copy
- Cmd/Ctrl + S: Download (prevent default)

Use useEffect with keydown listener.

Acceptance Criteria:
- [ ] Shortcuts work
- [ ] Don't conflict with browser
```

---

### Task 6.5: Final Testing

```
Comprehensive testing before release.

Test cases:
1. Full generation flow (mock mode)
2. Full generation flow (real backend)
3. Schema selection updates form
4. Scenario add/remove/edit
5. Options toggle correctly
6. History saves and loads
7. Format switching (JSON/CSV/SQL)
8. Copy and download
9. Error states
10. Navigation between agents

Acceptance Criteria:
- [ ] All flows work
- [ ] No console errors
- [ ] Performance acceptable
```

---

## Implementation Order

Recommended order for efficient development:

1. **Day 1**: Phase 1 (Foundation)
   - Tasks 1.1-1.5

2. **Day 2**: Phase 2 (Layout)
   - Tasks 2.1-2.4

3. **Day 3**: Phase 3 (Generator)
   - Tasks 3.1-3.6

4. **Day 4**: Phase 4 (Preview)
   - Tasks 4.1-4.5

5. **Day 5**: Phase 5 (Integration)
   - Tasks 5.1-5.6

6. **Day 6**: Phase 6 (Polish)
   - Tasks 6.1-6.5

---

## Dependencies to Install

```bash
# In frontend directory
npm install zustand @monaco-editor/react
```

Note: lucide-react and @bufbuild/protobuf should already be installed.
