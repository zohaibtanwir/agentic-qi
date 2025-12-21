# Product Requirements Document: QA Platform Frontend UI

**Version**: 1.0
**Date**: December 21, 2025
**Status**: Draft
**Phase**: Phase 1 - MVP

---

## 1. Executive Summary

### 1.1 Product Overview
The QA Platform Frontend UI is a web-based interface that enables QA engineers, developers, and product managers to generate, view, and manage AI-powered test cases. Phase 1 focuses on the Test Cases Agent interface with mock data, providing a foundation for future agent integrations.

### 1.2 Goals
- **Primary**: Enable users to generate comprehensive test cases from requirements using AI
- **Secondary**: Provide intuitive UI for viewing and managing generated test cases
- **Tertiary**: Establish design system and architecture for future agent integrations

### 1.3 Success Metrics
- Users can successfully generate test cases from all 3 input types (User Story, API Spec, Free Form)
- Test case generation form completion rate > 80%
- User can view full test case details within 2 clicks
- Page load time < 2 seconds
- Mobile responsive (works on tablet and desktop)

---

## 2. Target Users

### 2.1 Primary Personas

**QA Engineer (Primary)**
- Needs to create test cases from user stories and requirements
- Values comprehensive coverage and different test types
- Familiar with Gherkin and traditional test case formats
- Works with JIRA, TestRail, or similar tools

**Developer (Secondary)**
- Needs quick test cases for API endpoints
- Prefers structured formats (OpenAPI specs)
- Values functional and negative test scenarios
- Integrates with CI/CD pipelines

**Product Manager (Tertiary)**
- Reviews test coverage for features
- Needs to validate requirements are testable
- Less technical, prefers visual representation
- Focuses on acceptance criteria

---

## 3. Functional Requirements

## 3.1 Landing Page (`/`)

### 3.1.1 Overview
Dashboard view showing all available agents with navigation cards.

### 3.1.2 Components

**Agent Cards** (3 cards in grid layout)
1. **Test Data Agent**
   - Name, icon, description
   - Status: "Operational" (green indicator)
   - Link to external Test Data Agent UI
   - Quick stats: "5,678 records generated"

2. **Test Cases Agent**
   - Name, icon, description
   - Status: "Operational" (green indicator)
   - "Open" button → navigates to `/test-cases`
   - Quick stats: "1,234 test cases generated"

3. **eCommerce Domain Agent**
   - Name, icon, description
   - Status: "Coming Soon" (gray indicator)
   - Disabled state (no click action)
   - Quick stats: "89 domain rules"

**Platform Stats Dashboard**
- Total test cases generated: 1,234
- Total test data records: 5,678
- Domain rules available: 89
- Last activity timestamp

**Mock Data Structure**:
```json
{
  "agents": [
    {
      "id": "test-data-agent",
      "name": "Test Data Agent",
      "description": "Generate realistic test data using AI",
      "status": "operational",
      "link": "/test-data",
      "isExternal": true,
      "stats": { "recordsGenerated": 5678 }
    },
    {
      "id": "test-cases-agent",
      "name": "Test Cases Agent",
      "description": "Generate comprehensive test cases from requirements",
      "status": "operational",
      "link": "/test-cases",
      "isExternal": false,
      "stats": { "testCasesGenerated": 1234 }
    },
    {
      "id": "ecommerce-domain-agent",
      "name": "eCommerce Domain Agent",
      "description": "Domain-specific context and business rules",
      "status": "coming-soon",
      "link": "#",
      "isExternal": false,
      "stats": { "domainRules": 89 }
    }
  ]
}
```

---

## 3.2 Test Cases Agent Page (`/test-cases`)

### 3.2.1 Page Layout

**Header Section**
- Agent name: "Test Cases Agent"
- Status badge: "Operational" (green)
- Quick action: "New Generation" button (scrolls to form)
- Breadcrumb: Home > Test Cases Agent

**Main Content** (Two-column layout)
- Left: Generation Form (60% width)
- Right: Configuration Panel (40% width)

**Results Section** (Below form, appears after generation)
- Generated test cases list
- Metadata display
- Export options (future)

---

### 3.2.2 Generation Form

#### 3.2.2.1 Input Type Selection
**Tab Interface** (3 tabs, mutually exclusive)

**Tab 1: User Story**
```
Fields:
- Story Text (textarea, required)
  Placeholder: "As a customer, I want to add items to cart so that I can purchase multiple products..."
  Validation: Min 20 characters

- Acceptance Criteria (multi-line input, dynamic add/remove)
  Placeholder: "Given..., When..., Then..."
  Validation: At least 1 criterion required

- Additional Context (textarea, optional)
  Placeholder: "Business rules, constraints, related features..."
```

**Tab 2: API Specification**
```
Fields:
- Specification Format (dropdown, required)
  Options: OpenAPI, GraphQL
  Default: OpenAPI

- Spec Content (code editor textarea, required)
  Placeholder: "Paste your OpenAPI/GraphQL spec here (JSON or YAML)..."
  Validation: Valid JSON/YAML format
  Syntax highlighting: Yes

- Endpoints to Test (multi-select chips, optional)
  Placeholder: "Leave empty to test all endpoints"
  Example: /api/cart/add, /api/cart/remove
```

**Tab 3: Free Form Requirements**
```
Fields:
- Requirement Text (rich textarea, required)
  Placeholder: "Describe the feature or functionality to test..."
  Validation: Min 50 characters

- Context Information (key-value pairs, optional)
  Format: Key | Value (dynamic add/remove rows)
  Example:
    - Key: "Feature", Value: "Shopping Cart"
    - Key: "Priority", Value: "High"
```

#### 3.2.2.2 Configuration Panel

**Output Format Section**
```
Label: Test Case Format
Type: Radio buttons (horizontal)
Options:
  - Traditional (default)
    Description: "Step-by-step with actions and expected results"
  - Gherkin
    Description: "Given-When-Then BDD format"
  - JSON
    Description: "Structured data format"
```

**Coverage Level Section**
```
Label: Coverage Level
Type: Segmented control / Pills
Options:
  - Quick (default)
    Tooltip: "Happy path + critical negatives"
  - Standard
    Tooltip: "Comprehensive functional + negative tests"
  - Exhaustive
    Tooltip: "All scenarios including edge cases"
```

**Test Types Section**
```
Label: Test Types to Include
Type: Multi-select checkboxes (scrollable, max-height)
Default selected: Functional, Negative
Options (with icons):
  ✓ Functional (default checked)
  ✓ Negative (default checked)
  ☐ Boundary
  ☐ Edge Case
  ☐ Security
  ☐ Performance
  ☐ Integration
  ☐ API
  ... (show top 10, "Show more" link to expand)
```

**Advanced Options Section** (Collapsible, collapsed by default)
```
Label: Advanced Settings (click to expand)

Fields:
- Max Test Cases (number input)
  Default: 10
  Min: 1, Max: 50

- Priority Focus (dropdown, optional)
  Options: All (default), Critical, High, Medium, Low
  Description: "Focus generation on specific priority level"

- Detail Level (radio buttons)
  Options: Low, Medium (default), High
  Description: "Level of detail in test case steps"
```

**Action Buttons**
```
Primary: "Generate Test Cases" (Macy's red, full width)
Secondary: "Reset Form" (ghost button, below primary)
```

---

### 3.2.3 Generation Results Display

#### 3.2.3.1 Loading State
```
- Animated spinner with Macy's red accent
- Message: "Generating test cases..."
- Sub-message: "This may take 10-30 seconds"
- Progress indicator (if possible from backend)
```

#### 3.2.3.2 Results Header
```
Title: "Generated Test Cases"
Metadata badges:
  - Test cases generated: 8
  - Coverage level: Standard
  - Format: Traditional
  - Generation time: 12.5s
```

#### 3.2.3.3 Test Case Cards (List View)

**Card Layout** (Stack of cards, scrollable)
```
Each card displays:

┌─────────────────────────────────────────┐
│ [Icon] TC-001                    [Badge]│
│ ✓ Functional | ⚠ High Priority         │
│                                         │
│ User successfully adds item to cart    │
│                                         │
│ Preconditions: User logged in, ...     │
│ Steps: 3 steps                          │
│ Tags: cart, checkout, functional        │
│                                         │
│ [View Details] button                   │
└─────────────────────────────────────────┘

Card Properties:
- ID: TC-001, TC-002, etc.
- Type icon + label (colored)
- Priority badge (colored: Critical=red, High=orange, Medium=blue, Low=gray)
- Title (truncated to 2 lines)
- Preview: First precondition + step count
- Tags (max 3 visible, +N more)
- "View Details" button (secondary style)
```

**List Features**
- Filter by type (dropdown)
- Filter by priority (dropdown)
- Sort by: Priority (default), ID, Type
- Pagination: 10 cards per page

#### 3.2.3.4 Metadata Panel (Below cards)
```
Generation Metadata:
- LLM Provider: Anthropic Claude
- Model: claude-3.5-sonnet
- Tokens used: 1,234
- Coverage breakdown:
  - Functional: 5 test cases
  - Negative: 2 test cases
  - Boundary: 1 test case
```

---

### 3.2.4 Test Case Detail View

#### 3.2.4.1 Navigation
```
Trigger: Click "View Details" on any card
Action: Navigate to /test-cases/[id] OR open modal/side panel
Preferred: Side panel (keeps context)
```

#### 3.2.4.2 Detail Panel Layout

**Header**
```
┌─────────────────────────────────────────┐
│ ← Back to Results                       │
│                                         │
│ TC-001                          [Badge] │
│ ✓ Functional Test | ⚠ High Priority    │
│                                         │
│ User successfully adds item to cart    │
│                                         │
│ Tags: cart, checkout, functional        │
└─────────────────────────────────────────┘
```

**Content Sections** (Vertical scroll)

**1. Description**
```
Label: Description
Content: Full test case description text
```

**2. Preconditions**
```
Label: Preconditions
Content: Bulleted list
Example:
  • User is logged in
  • Product is in stock
  • Shopping cart is empty
```

**3. Test Steps** (for Traditional format)
```
Label: Test Steps
Format: Numbered list with table layout

┌────┬──────────────────────┬──────────────────────┐
│ #  │ Action               │ Expected Result      │
├────┼──────────────────────┼──────────────────────┤
│ 1  │ Navigate to product  │ Product page loads   │
│    │ page                 │ with details         │
├────┼──────────────────────┼──────────────────────┤
│ 2  │ Click "Add to Cart"  │ Item added to cart,  │
│    │ button               │ cart count updates   │
└────┴──────────────────────┴──────────────────────┘

Styling:
- Alternating row colors
- Hover state
- Step number in gray circle
```

**4. Gherkin** (for Gherkin format)
```
Label: Gherkin Scenario
Format: Code block with syntax highlighting

Given user is logged in
And product "iPhone 14" is in stock
When user navigates to product page
And user clicks "Add to Cart" button
Then product is added to cart
And cart count increases by 1
And cart total updates correctly
```

**5. Test Data** (if available)
```
Label: Test Data
Format: Key-value pairs or table

┌──────────────┬──────────────────┐
│ Field        │ Value            │
├──────────────┼──────────────────┤
│ User ID      │ user123          │
│ Product ID   │ prod456          │
│ Quantity     │ 1                │
│ Price        │ $999.99          │
└──────────────┴──────────────────┘
```

**6. Expected Results**
```
Label: Expected Results
Content: Summary text
Example: "User should see cart with 1 item, total price updated, success message displayed"
```

**7. Postconditions**
```
Label: Postconditions
Content: Bulleted list
Example:
  • Cart contains 1 item
  • Inventory decremented by 1
  • Session state updated
```

**Action Buttons** (Sticky footer)
```
- Copy to Clipboard (copy entire test case as text)
- Export (download as JSON/YAML/Markdown)
- Edit (future - opens edit mode)
- Close / Back to Results
```

---

## 3.3 Mock Data Strategy (Phase 1)

### 3.3.1 Generation Form Behavior
```
When user clicks "Generate Test Cases":
1. Show loading state (2-3 seconds delay to simulate API call)
2. Return predefined mock test cases from JSON file
3. Vary results slightly based on:
   - Input type selected (different titles/descriptions)
   - Coverage level (Quick: 3-5 cases, Standard: 5-10, Exhaustive: 10-15)
   - Test types selected (filter mock data by types)
```

### 3.3.2 Mock Test Cases Data Structure
```json
{
  "requestId": "req-12345",
  "success": true,
  "testCases": [
    {
      "id": "TC-001",
      "title": "User successfully adds item to cart",
      "description": "Verify that logged-in user can add product to shopping cart",
      "type": "FUNCTIONAL",
      "priority": "HIGH",
      "tags": ["cart", "checkout", "functional"],
      "requirementId": "REQ-CART-001",
      "preconditions": [
        "User is logged in",
        "Product is in stock",
        "Shopping cart is empty"
      ],
      "steps": [
        {
          "order": 1,
          "action": "Navigate to product page",
          "expectedResult": "Product details page loads successfully",
          "testData": "productId: prod456"
        },
        {
          "order": 2,
          "action": "Click 'Add to Cart' button",
          "expectedResult": "Item added to cart, cart count updates to 1"
        },
        {
          "order": 3,
          "action": "Verify cart contents",
          "expectedResult": "Cart displays product with correct price and quantity"
        }
      ],
      "gherkin": "Feature: Shopping Cart\n  Scenario: Add item to cart\n    Given user is logged in\n    And product 'iPhone 14' is in stock\n    When user navigates to product page\n    And user clicks 'Add to Cart' button\n    Then product is added to cart\n    And cart count increases by 1",
      "testData": {
        "items": [
          {"field": "userId", "value": "user123", "description": "Test user"},
          {"field": "productId", "value": "prod456", "description": "Product ID"},
          {"field": "quantity", "value": "1", "description": "Quantity to add"}
        ]
      },
      "expectedResult": "Product successfully added to cart with correct quantity and price",
      "postconditions": [
        "Cart contains 1 item",
        "Product inventory decremented by 1",
        "Cart session updated"
      ],
      "status": "DRAFT"
    },
    {
      "id": "TC-002",
      "title": "User cannot add out-of-stock item to cart",
      "description": "Verify error handling when user attempts to add unavailable product",
      "type": "NEGATIVE",
      "priority": "HIGH",
      "tags": ["cart", "error-handling", "negative"],
      "requirementId": "REQ-CART-002",
      "preconditions": [
        "User is logged in",
        "Product is out of stock"
      ],
      "steps": [
        {
          "order": 1,
          "action": "Navigate to out-of-stock product page",
          "expectedResult": "Product page loads with 'Out of Stock' message",
          "testData": "productId: prod789"
        },
        {
          "order": 2,
          "action": "Attempt to click 'Add to Cart' button",
          "expectedResult": "'Add to Cart' button is disabled"
        },
        {
          "order": 3,
          "action": "Verify error message",
          "expectedResult": "Error message displayed: 'This item is currently out of stock'"
        }
      ],
      "gherkin": "Feature: Shopping Cart\n  Scenario: Cannot add out-of-stock item\n    Given user is logged in\n    And product 'iPhone 14' is out of stock\n    When user navigates to product page\n    Then 'Add to Cart' button is disabled\n    And error message 'Out of Stock' is displayed",
      "testData": {
        "items": [
          {"field": "userId", "value": "user123", "description": "Test user"},
          {"field": "productId", "value": "prod789", "description": "Out of stock product"}
        ]
      },
      "expectedResult": "User cannot add item, appropriate error message shown",
      "postconditions": [
        "Cart remains unchanged",
        "Error message visible to user"
      ],
      "status": "DRAFT"
    }
  ],
  "metadata": {
    "llmProvider": "anthropic",
    "llmModel": "claude-3.5-sonnet",
    "llmTokensUsed": 1234,
    "generationTimeMs": 12500,
    "testCasesGenerated": 8,
    "duplicatesFound": 0,
    "coverage": {
      "functionalCount": 5,
      "negativeCount": 2,
      "boundaryCount": 1,
      "edgeCaseCount": 0,
      "uncoveredAreas": [
        "Concurrent cart updates",
        "Cart persistence across sessions"
      ]
    },
    "domainContextUsed": ""
  }
}
```

### 3.3.3 Multiple Mock Data Sets
Create 3-4 mock response files for different scenarios:
- `mock-cart-tests.json` (shopping cart scenarios)
- `mock-api-tests.json` (API endpoint tests)
- `mock-login-tests.json` (authentication scenarios)
- `mock-search-tests.json` (search functionality)

Rotate or select based on input type/keywords detected in form.

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Page load time: < 2 seconds
- Form submission (mock): < 3 seconds
- Smooth animations (60 FPS)
- Image/asset optimization
- Lazy loading for test case cards (if > 20 cases)

### 4.2 Responsive Design
**Breakpoints** (Tailwind defaults)
- Mobile: 640px (single column, stacked form)
- Tablet: 768px (single column, form sections stacked)
- Desktop: 1024px+ (two-column layout, side-by-side)

**Mobile Adaptations**:
- Form configuration: Accordion instead of side panel
- Test case cards: Full width, simplified view
- Detail view: Full screen modal instead of side panel
- Navigation: Hamburger menu for agent selection

### 4.3 Accessibility (WCAG AA)
- All interactive elements keyboard navigable
- Focus states visible (Macy's red outline)
- ARIA labels for all form controls
- Screen reader announcements for dynamic content
- Color contrast ratios: 4.5:1 minimum
- Skip to content links
- Error messages in `role="alert"` regions

### 4.4 Browser Support
- Chrome 100+ (primary)
- Firefox 100+
- Safari 15+
- Edge 100+
- No IE11 support required

### 4.5 Internationalization
- **Phase 1**: English only
- **Future**: Prepare for i18n with string externalization
- Date/time formatting: ISO 8601 → localized display
- Number formatting: Locale-aware

---

## 5. Design System Reference

### 5.1 Design System Location
All design specifications are documented in:
```
/docs/frontend/styles.md
```

### 5.2 Key Design Elements

**Colors**
- Primary: Macy's Red (#CE0037)
- Background: White (#FFFFFF), Light Gray (#F7F7F7)
- Text: Black (#000000), Gray (#666666)
- Status: Green (#10B981), Orange (#FFB000), Red (#CE0037)

**Typography**
- Heading: Plus Jakarta Sans (600/700 weight)
- Body: Plus Jakarta Sans (400/500 weight)
- Code: JetBrains Mono

**Component Library**
- shadcn/ui components (Button, Card, Input, Select, Tabs, Badge, etc.)
- Custom components built following Macy's theme

**Spacing**
- Tailwind spacing scale (4px base unit)
- Section padding: `p-6` (24px)
- Card margins: `mb-6` (24px)

---

## 6. API Integration (Mock in Phase 1)

### 6.1 API Endpoints to Mock

#### 6.1.1 GenerateTestCases
```
Endpoint: /api/test-cases/generate (mocked)
Method: POST
Request Body: {
  requestId: string
  input: UserStoryInput | ApiSpecInput | FreeFormInput
  generationConfig: {
    outputFormat: 'TRADITIONAL' | 'GHERKIN' | 'JSON'
    coverageLevel: 'QUICK' | 'STANDARD' | 'EXHAUSTIVE'
    testTypes: TestType[]
    maxTestCases: number
    priorityFocus?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
    detailLevel?: 'low' | 'medium' | 'high'
  }
}

Response: GenerateTestCasesResponse (see mock data structure above)

Mock Behavior:
- Delay: 2-3 seconds (simulate LLM call)
- Return data from mock JSON file
- Filter by test types selected
- Adjust count based on coverage level
```

#### 6.1.2 GetTestCase
```
Endpoint: /api/test-cases/{id} (mocked)
Method: GET
Path Parameter: id (string)

Response: {
  testCase: TestCase
}

Mock Behavior:
- Return full test case from mock data by ID
- 404 if ID not found
```

### 6.2 Mock Implementation Strategy

**Option 1: Client-side mock (Phase 1 preference)**
```typescript
// lib/api/mock/testCasesApi.ts
export async function generateTestCases(request: GenerateRequest) {
  await sleep(2500); // Simulate API delay
  const mockData = await import('./data/mock-cart-tests.json');
  return filterAndTransform(mockData, request);
}

export async function getTestCase(id: string) {
  const mockData = await import('./data/mock-cart-tests.json');
  return mockData.testCases.find(tc => tc.id === id);
}
```

**Option 2: Next.js API routes (for future real backend)**
```
/app/api/test-cases/generate/route.ts
/app/api/test-cases/[id]/route.ts
```

Phase 1: Use Option 1 (simpler, no server needed)
Phase 2: Switch to Option 2 and replace mock with real gRPC calls

---

## 7. User Flows

### 7.1 Primary Flow: Generate Test Cases from User Story

```
1. User lands on homepage (/)
2. User clicks "Open" on Test Cases Agent card
3. User navigates to /test-cases
4. User sees generation form with "User Story" tab selected
5. User enters:
   - Story: "As a customer, I want to add items to cart..."
   - Acceptance Criteria: 3 criteria added
6. User selects configuration:
   - Format: Traditional
   - Coverage: Standard
   - Test Types: Functional, Negative (checked)
7. User clicks "Generate Test Cases"
8. Loading spinner appears (2-3 seconds)
9. Results section appears with 8 test case cards
10. User reviews list, sees TC-001 "User successfully adds item to cart"
11. User clicks "View Details" on TC-001
12. Side panel opens showing full test case with steps
13. User reviews preconditions, steps, expected results
14. User closes detail panel or navigates to another test case
```

### 7.2 Alternative Flow: Generate from API Spec

```
1-3. Same as primary flow
4. User clicks "API Specification" tab
5. User selects "OpenAPI" format
6. User pastes OpenAPI spec (JSON)
7. User optionally specifies endpoints to test
8-14. Same as primary flow
```

### 7.3 Error Flow: Invalid Input

```
1-5. User fills form with invalid data (e.g., story < 20 characters)
6. User clicks "Generate Test Cases"
7. Form validation errors appear in red
8. Fields with errors highlighted with red border
9. Error message below field: "Story must be at least 20 characters"
10. Submit button remains clickable but validation prevents submission
11. User corrects errors
12. Validation errors clear
13. User submits successfully
```

---

## 8. Out of Scope (Phase 1)

### 8.1 Features Deferred to Phase 2+
- Real backend API integration (gRPC/REST)
- Domain Agent integration (DomainConfig)
- Test Data Agent integration (TestDataConfig)
- `ListTestCases` API (historical view)
- `StoreTestCases` API (persistence)
- `AnalyzeCoverage` API (coverage analysis)
- User authentication/authorization
- Export functionality (download test cases)
- Edit test cases
- Test case execution/results
- Test case versioning
- Collaboration features (comments, sharing)

### 8.2 Technical Debt Accepted
- Mock data instead of real API calls
- No state management library (use React hooks)
- No data persistence (refresh loses data)
- Limited error handling (basic validation only)
- No retry logic for failed generations

---

## 9. Technical Stack (Finalized)

### 9.1 Frontend Framework
- **Next.js 14** (App Router)
- **TypeScript** 5.x
- **React** 18.x

### 9.2 Styling
- **Tailwind CSS** 3.x
- **shadcn/ui** components
- **Plus Jakarta Sans** (heading/body font)
- **JetBrains Mono** (code/monospace font)

### 9.3 Data Fetching
- **Phase 1**: Client-side mock functions
- **Phase 2**: TBD (gRPC-Web / REST API routes / Server Components)

### 9.4 State Management
- **React hooks** (useState, useContext)
- **No Redux/Zustand** for Phase 1

### 9.5 Form Management
- **React Hook Form** (optional, or plain React state)
- **Zod** for schema validation (optional)

### 9.6 Code Quality
- **ESLint** + **Prettier**
- **TypeScript strict mode**
- **Husky** for pre-commit hooks (optional)

---

## 10. Project Structure

```
qa-platform/
├── frontend/                    # Frontend Next.js app (to be created)
│   ├── app/
│   │   ├── layout.tsx          # Root layout with header
│   │   ├── page.tsx            # Landing page (/)
│   │   ├── test-cases/
│   │   │   ├── page.tsx        # Test cases agent page
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Test case detail page
│   │   └── api/                # API routes (Phase 2)
│   │       └── test-cases/
│   │           ├── generate/
│   │           └── [id]/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── test-cases/
│   │   │   ├── GenerationForm.tsx
│   │   │   ├── UserStoryTab.tsx
│   │   │   ├── ApiSpecTab.tsx
│   │   │   ├── FreeFormTab.tsx
│   │   │   ├── ConfigPanel.tsx
│   │   │   ├── TestCaseCard.tsx
│   │   │   ├── TestCaseList.tsx
│   │   │   └── TestCaseDetail.tsx
│   │   ├── landing/
│   │   │   ├── AgentCard.tsx
│   │   │   └── StatsPanel.tsx
│   │   └── ui/                 # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── tabs.tsx
│   │       └── ...
│   ├── lib/
│   │   ├── api/
│   │   │   ├── mock/
│   │   │   │   ├── testCasesApi.ts    # Mock API functions
│   │   │   │   └── data/
│   │   │   │       ├── mock-cart-tests.json
│   │   │   │       ├── mock-api-tests.json
│   │   │   │       └── mock-login-tests.json
│   │   │   └── types.ts        # TypeScript interfaces from proto
│   │   └── utils/
│   │       ├── formatters.ts
│   │       └── validators.ts
│   ├── types/
│   │   └── test-cases.ts       # Proto-generated types (manual for Phase 1)
│   ├── public/
│   │   ├── images/
│   │   └── icons/
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── package.json
│   └── tsconfig.json
├── docs/
│   └── frontend/
│       ├── PRD.md              # This document
│       ├── FRONTEND_REQUIREMENTS.md
│       └── styles.md
└── protos/
    └── test_cases.proto        # API contract reference
```

---

## 11. Development Phases

### Phase 1.1: Setup & Foundation (Week 1)
**Deliverables**:
- Initialize Next.js 14 project
- Install dependencies (Tailwind, shadcn/ui, fonts)
- Set up project structure (folders, base files)
- Create layout components (Header, Footer)
- Implement landing page with mock agent cards
- Set up Tailwind config with Macy's theme

**Tasks** (from Beads):
- Task 7.1: Initialize Next.js Project
- Task 7.2: Create Project Structure
- Task 7.3: Create Layout Components
- Task 7.4: Build Landing Page

### Phase 1.2: Generation Form (Week 2)
**Deliverables**:
- Test Cases Agent page layout
- All 3 input tabs (User Story, API Spec, Free Form)
- Configuration panel (format, coverage, test types)
- Form validation
- Mock API integration

**Tasks** (from Beads):
- Task 7.5: Build Test Cases Agent Page - Form

### Phase 1.3: Results Display (Week 2-3)
**Deliverables**:
- Loading state animation
- Test case card list view
- Filtering and sorting
- Mock data integration
- Results metadata display

**Tasks** (from Beads):
- Task 7.6: Build Test Cases Agent Page - Results Display

### Phase 1.4: Detail View (Week 3)
**Deliverables**:
- Test case detail side panel/modal
- All sections (preconditions, steps, test data, etc.)
- Format-aware display (Traditional vs Gherkin)
- Navigation between test cases
- Close/back functionality

**Tasks** (from Beads):
- Task 7.7: Build Test Case Detail View

### Phase 1.5: Polish & Testing (Week 4)
**Deliverables**:
- Error handling and loading states
- Responsive design fixes
- Accessibility improvements
- Cross-browser testing
- Performance optimization

**Tasks** (from Beads):
- Task 7.8: Add Error Handling & Loading States
- Task 7.9: Responsive Design Testing

---

## 12. Testing Strategy

### 12.1 Manual Testing Checklist

**Landing Page**
- [ ] All agent cards display correctly
- [ ] Status indicators show correct colors
- [ ] Stats display with proper formatting
- [ ] Test Cases Agent link navigates to `/test-cases`
- [ ] Test Data Agent link opens external URL
- [ ] eCommerce Agent card is disabled
- [ ] Responsive on mobile/tablet/desktop

**Test Cases Form**
- [ ] All 3 input tabs work correctly
- [ ] Tab switching preserves configuration
- [ ] User Story tab: all fields validate
- [ ] API Spec tab: format selector works
- [ ] Free Form tab: context key-value pairs add/remove
- [ ] Configuration panel: all options selectable
- [ ] Advanced settings expand/collapse
- [ ] Generate button triggers loading state
- [ ] Reset button clears form

**Results Display**
- [ ] Loading spinner appears for 2-3 seconds
- [ ] Test case cards display with correct data
- [ ] Filtering by type works
- [ ] Sorting by priority works
- [ ] Pagination works (if > 10 cases)
- [ ] Metadata panel shows correct stats
- [ ] View Details button opens panel

**Detail View**
- [ ] Side panel/modal opens correctly
- [ ] All sections display (preconditions, steps, etc.)
- [ ] Traditional format: steps in table
- [ ] Gherkin format: code block with syntax
- [ ] Test data table displays
- [ ] Navigation: Back to Results works
- [ ] Close button closes panel
- [ ] Keyboard ESC closes panel

### 12.2 Automated Testing (Future)
- Unit tests with Jest + React Testing Library
- E2E tests with Playwright
- Visual regression with Percy/Chromatic

---

## 13. Success Criteria

### 13.1 Must Have (Phase 1 Complete)
✅ Landing page displays all 3 agent cards with correct status
✅ Test Cases Agent page has all 3 input types functional
✅ User can configure output format, coverage level, test types
✅ Generate button returns mock test cases
✅ Test case cards display in list view with filtering
✅ Detail view shows complete test case information
✅ Responsive design works on mobile, tablet, desktop
✅ Design matches Macy's theme (styles.md)
✅ Page loads in < 2 seconds

### 13.2 Should Have
⚠ Form validation with helpful error messages
⚠ Loading states for all async operations
⚠ Keyboard navigation works throughout
⚠ WCAG AA accessibility compliance

### 13.3 Nice to Have (Future)
🔮 Export test cases to JSON/YAML/Markdown
🔮 Copy test case to clipboard
🔮 Search/filter within results
🔮 Dark mode support

---

## 14. Open Questions & Decisions Needed

### 14.1 Resolved
✅ **Q**: Which API communication method?
**A**: Deferred to Phase 2 (mock data for Phase 1)

✅ **Q**: State management library?
**A**: React hooks only (no Redux/Zustand)

✅ **Q**: Detail view: modal or side panel?
**A**: Side panel (keeps context visible)

### 14.2 Pending
❓ **Q**: Should we use React Hook Form or plain state?
**Decision by**: Before Phase 1.2 starts

❓ **Q**: TypeScript interfaces: manual or proto-generated?
**Decision by**: Before Phase 1.1 starts
**Context**: Need proto compiler setup for TS types

❓ **Q**: Export functionality: Phase 1 or Phase 2?
**Decision by**: During Phase 1.4
**Context**: Easy to add, might be valuable early

---

## 15. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Design system inconsistency | Medium | Medium | Reference styles.md for all components |
| Mock data feels too fake | Low | High | Create realistic, varied mock data sets |
| Proto types don't match UI needs | Medium | Low | Manual review of proto file before coding |
| Form complexity overwhelming | High | Medium | Progressive disclosure, good defaults |
| Performance issues with large lists | Medium | Low | Pagination + virtualization if needed |
| Accessibility overlooked | High | Medium | ARIA labels from start, test with screen reader |

---

## 16. Appendix

### 16.1 Proto File Reference
Location: `/protos/test_cases.proto`

**Key Messages Used**:
- `GenerateTestCasesRequest`
- `GenerateTestCasesResponse`
- `TestCase`
- `TestStep`
- `TestData`
- `GenerationConfig`
- `GenerationMetadata`
- `CoverageAnalysis`

**Enums Used**:
- `OutputFormat`: TRADITIONAL, GHERKIN, JSON
- `CoverageLevel`: QUICK, STANDARD, EXHAUSTIVE
- `TestType`: FUNCTIONAL, NEGATIVE, BOUNDARY, etc. (23 types)
- `Priority`: CRITICAL, HIGH, MEDIUM, LOW
- `TestCaseStatus`: DRAFT, READY, IN_PROGRESS, PASSED, FAILED, BLOCKED, SKIPPED

### 16.2 Design Assets
- Macy's logo/icon: TBD
- Agent icons: TBD (use emoji or generic icons for Phase 1)
- Status indicator colors defined in styles.md

### 16.3 External Dependencies
- Test Data Agent UI: Existing, link from landing page
- eCommerce Domain Agent: Not yet built (show as "Coming Soon")

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-21 | Claude (AI) | Initial draft based on requirements gathering |

**Approval Required From**:
- [ ] Product Owner (User/Client)
- [ ] Tech Lead
- [ ] UX/Design Lead

**Next Steps After Approval**:
1. Create Beads task updates to match PRD scope
2. Sync PRD with development team
3. Begin Phase 1.1 implementation
