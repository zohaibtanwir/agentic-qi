# Requirement Analysis Agent - PRD

## Overview

The Requirement Analysis Agent is a Python gRPC microservice that analyzes requirements from multiple input formats (Jira stories, free-form text, meeting transcripts), assesses their quality, identifies gaps, and prepares structured output for downstream test case generation.

**Dual Purpose:**
1. **Improve Requirement Quality** - Score, identify gaps, generate clarifying questions
2. **Prepare for Test Generation** - Extract structure, generate ACs, feed to Test Cases Agent

---

## Project Info

| Item | Value |
|------|-------|
| Repository | `qa-platform/agents/requirement-analysis-agent` |
| Language | Python 3.11+ |
| Framework | gRPC (grpcio) + FastAPI (health endpoints) |
| Default LLM | Claude Sonnet 4 (`claude-sonnet-4-20250514`) |
| Alternative LLMs | OpenAI GPT-4, Google Gemini Pro |
| Issue Tracking | Beads (`bd`) |
| gRPC Port | 9004 |
| HTTP Port | 8084 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REQUIREMENT ANALYSIS AGENT                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INPUTS                                                                     │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐                 │
│   │ Jira Story  │  │ Free-Form   │  │ Teams Transcript    │                 │
│   │ (JSON)      │  │ Text        │  │ (Speaker Labels)    │                 │
│   └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘                 │
│          │                │                     │                            │
│          └────────────────┼─────────────────────┘                            │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      INPUT PARSER                                    │   │
│   │  • Detect input type                                                │   │
│   │  • Normalize to common format                                       │   │
│   │  • Extract transcript decisions/requirements                        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                           │                                                  │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    ANALYSIS ENGINE                                   │   │
│   │                                                                      │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│   │  │ Quality      │  │ Gap          │  │ Structure    │               │   │
│   │  │ Scorer       │  │ Detector     │  │ Extractor    │               │   │
│   │  │              │  │              │  │              │               │   │
│   │  │ • Clarity    │  │ • Missing AC │  │ • Actor      │               │   │
│   │  │ • Complete   │  │ • Ambiguity  │  │ • Action     │               │   │
│   │  │ • Testable   │  │ • Undefined  │  │ • Object     │               │   │
│   │  │ • Consistent │  │ • Edge Cases │  │ • Outcome    │               │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│   │                                                                      │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│   │  │ Question     │  │ AC           │  │ Domain       │               │   │
│   │  │ Generator    │  │ Generator    │  │ Validator    │               │   │
│   │  │              │  │              │  │              │               │   │
│   │  │ • Priority   │  │ • From gaps  │  │ • Entity map │               │   │
│   │  │ • Impact     │  │ • From struct│  │ • Rule check │               │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                           │                                                  │
│                           ▼                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         OUTPUTS                                      │   │
│   │                                                                      │   │
│   │  ┌──────────────────────┐    ┌──────────────────────┐               │   │
│   │  │   Analysis Report    │    │  Structured Output   │               │   │
│   │  │                      │    │                      │               │   │
│   │  │  • Quality Scores    │    │  • Clean Requirement │               │   │
│   │  │  • Gaps Found        │    │  • Generated ACs     │               │   │
│   │  │  • Questions         │    │  • Domain Mapping    │               │   │
│   │  │  • Recommendations   │    │  • Ready for TCA     │               │   │
│   │  │                      │    │                      │               │   │
│   │  │  Export: Text, JSON  │    │  Feed: Test Cases    │               │   │
│   │  └──────────────────────┘    └──────────────────────┘               │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   INTEGRATIONS                                                               │
│   ┌─────────────────────┐  ┌─────────────────────┐                          │
│   │ eCommerce Domain    │  │ Test Cases Agent    │                          │
│   │ Agent (:9002)       │  │ (:9003)             │                          │
│   │                     │  │                     │                          │
│   │ • Validate entities │  │ • Forward analyzed  │                          │
│   │ • Get business rules│  │   requirement       │                          │
│   └─────────────────────┘  └─────────────────────┘                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Input Formats

### 1. Jira Story (JSON)

```json
{
  "key": "ECOM-1234",
  "summary": "Add Apple Pay support to checkout",
  "description": "As a customer, I want to pay using Apple Pay so that I can checkout faster on my iPhone.",
  "acceptanceCriteria": [
    "Apple Pay button visible on payment step",
    "Clicking Apple Pay opens native payment sheet"
  ],
  "storyPoints": 5,
  "labels": ["checkout", "payments", "mobile"],
  "components": ["payment-service"],
  "priority": "High",
  "reporter": "john.smith@company.com",
  "assignee": "jane.doe@company.com"
}
```

**Fields to Analyze (V1 - Core):**
- `summary` - Clarity, specificity
- `description` - User story format, completeness
- `acceptanceCriteria` - Testability, coverage

**Fields to Analyze (V2 - TODO):**
- `storyPoints` - Complexity alignment
- `labels`, `components` - Domain mapping
- `linkedIssues` - Dependencies
- `comments` - Additional context
- `attachments` - Specs, mockups

---

### 2. Free-Form Text

```text
We need to add Apple Pay to the checkout flow. Customers should be able to 
select Apple Pay as a payment method when checking out on iOS devices. 
The button should appear alongside other payment options. When tapped, it 
should open the Apple Pay sheet. If payment succeeds, complete the order. 
If it fails, show an error message.
```

---

### 3. Teams Meeting Transcript

**Format:** Plain text with speaker labels

```text
[10:00] PM: Let's discuss the Apple Pay feature for checkout.

[10:01] Dev Lead: Sure. What's the scope?

[10:02] PM: We need Apple Pay on mobile checkout. It should work on iPhone and iPad.

[10:03] QA: What about Mac with Touch ID?

[10:04] PM: Good question. Let's include that too. Any device with Apple Pay capability.

[10:05] Dev Lead: How do we handle payment failures?

[10:06] PM: Show an error message and let them retry or choose another payment method.

[10:07] QA: How many retries before we give up?

[10:08] PM: Let's say 3 attempts, then suggest they contact support or use a different method.

[10:09] Dev Lead: What about the UI? Where does the button go?

[10:10] PM: It should appear with other payment options - credit card, PayPal, etc.

[10:11] Designer: I'll create mockups. Should it have the official Apple Pay styling?

[10:12] PM: Yes, we need to follow Apple's guidelines for the button.

[10:13] QA: Do we need to handle the case where Apple Pay isn't available on the device?

[10:14] PM: Yes, hide the button if Apple Pay isn't supported.

[10:15] Dev Lead: What about order confirmation? Any changes there?

[10:16] PM: Show "Paid with Apple Pay" in the payment method section of the confirmation.

[10:17] PM: Alright, I think we've covered the main points. Any other questions?

[10:18] QA: What's the expected go-live date?

[10:19] PM: We're targeting end of Q1, so about 6 weeks.

[10:20] PM: Great, let's wrap up. I'll document this in Jira.
```

**What to Extract:**

| Category | Extracted Items |
|----------|-----------------|
| **Requirements** | Apple Pay on mobile checkout, support iPhone/iPad/Mac with Touch ID |
| **Decisions Made** | 3 retry attempts, follow Apple guidelines for button, hide if not supported |
| **Acceptance Criteria** | Button with other payment options, error on failure, retry up to 3 times, show in confirmation |
| **Open Questions** | (None remaining - all answered) |
| **Scope** | All Apple Pay capable devices |
| **Timeline** | End of Q1 (~6 weeks) |
| **Action Items** | Designer to create mockups, PM to document in Jira |

---

## Quality Scoring

### Dimensions

| Dimension | Weight | Description | Scoring Criteria |
|-----------|--------|-------------|------------------|
| **Clarity** | 25% | Is it unambiguous? | No vague terms, specific language |
| **Completeness** | 30% | Is it fully specified? | All scenarios covered, no gaps |
| **Testability** | 25% | Can it be tested? | Measurable outcomes, clear pass/fail |
| **Consistency** | 20% | No contradictions? | Aligned with domain, no conflicts |

### Score Ranges

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | A | Excellent - Ready for development/testing |
| 80-89 | B | Good - Minor improvements recommended |
| 70-79 | C | Acceptable - Some gaps to address |
| 60-69 | D | Needs Work - Significant issues |
| 0-59 | F | Poor - Major revision required |

### Scoring Output

```json
{
  "overallScore": 78,
  "overallGrade": "C",
  "dimensions": {
    "clarity": {
      "score": 85,
      "grade": "B",
      "issues": [
        "Term 'fast checkout' is subjective - define expected time"
      ]
    },
    "completeness": {
      "score": 65,
      "grade": "D",
      "issues": [
        "Missing error handling for network failures",
        "No mention of accessibility requirements",
        "Edge case: What if cart is empty?"
      ]
    },
    "testability": {
      "score": 80,
      "grade": "B",
      "issues": [
        "Success criteria 'works well' needs specific metrics"
      ]
    },
    "consistency": {
      "score": 90,
      "grade": "A",
      "issues": []
    }
  },
  "recommendation": "Address completeness gaps before development. Focus on error handling and edge cases."
}
```

---

## Gap Detection

### Gap Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Missing AC** | Acceptance criteria not specified | "No AC for error scenarios" |
| **Ambiguous Term** | Vague or undefined language | "'Fast' is not quantified" |
| **Undefined Term** | Domain term not explained | "'SKU validation' not defined" |
| **Missing Error Handling** | No failure scenarios | "What happens if payment times out?" |
| **Missing Edge Case** | Boundary conditions not covered | "What if quantity is 0?" |
| **Missing Precondition** | Assumed state not specified | "Assumes user is logged in" |
| **Missing Postcondition** | End state not defined | "Final cart state unclear" |
| **Contradiction** | Conflicting statements | "Says both 'required' and 'optional'" |

### Gap Output

```json
{
  "gaps": [
    {
      "id": "GAP-001",
      "category": "missing_error_handling",
      "severity": "high",
      "description": "No specification for payment timeout scenario",
      "location": "Acceptance Criteria",
      "suggestion": "Add AC: 'If payment times out after 30 seconds, show timeout error and allow retry'"
    },
    {
      "id": "GAP-002", 
      "category": "ambiguous_term",
      "severity": "medium",
      "description": "Term 'fast' is subjective",
      "location": "Description - 'checkout faster'",
      "suggestion": "Define expected checkout time, e.g., 'complete checkout in under 10 seconds'"
    }
  ],
  "gapSummary": {
    "total": 5,
    "high": 2,
    "medium": 2,
    "low": 1
  }
}
```

---

## Structure Extraction

### Extracted Elements

| Element | Description | Example |
|---------|-------------|---------|
| **Actor** | Who performs the action | "Customer", "Admin", "System" |
| **Action** | What is being done | "Add to cart", "Pay", "Checkout" |
| **Object** | What is acted upon | "Product", "Order", "Payment" |
| **Outcome** | Why / expected result | "So that I can purchase items" |
| **Preconditions** | Required starting state | "User is logged in", "Cart has items" |
| **Postconditions** | Expected end state | "Order is created", "Payment is processed" |
| **Triggers** | What initiates the action | "User clicks button", "Timer expires" |
| **Constraints** | Limitations or rules | "Maximum 10 items", "Only on iOS" |

### Structure Output

```json
{
  "structure": {
    "actor": {
      "primary": "Customer",
      "secondary": ["System"]
    },
    "action": "Pay using Apple Pay",
    "object": "Order/Payment",
    "outcome": "Complete checkout faster on iOS devices",
    "preconditions": [
      "Customer is on checkout page",
      "Cart contains at least one item",
      "Device supports Apple Pay",
      "Customer has Apple Pay configured"
    ],
    "postconditions": [
      "Payment is processed",
      "Order is created",
      "Confirmation is displayed"
    ],
    "triggers": [
      "Customer taps Apple Pay button"
    ],
    "constraints": [
      "Only available on Apple Pay supported devices",
      "Must follow Apple Pay UI guidelines"
    ]
  }
}
```

---

## Clarifying Questions

### Question Generation

Questions are generated based on detected gaps and domain knowledge.

```json
{
  "questions": [
    {
      "id": "Q-001",
      "priority": "high",
      "category": "error_handling",
      "question": "What should happen if the Apple Pay payment times out?",
      "context": "No timeout handling specified in requirements",
      "suggestedAnswers": [
        "Show error message and allow retry",
        "Automatically retry once then show error",
        "Fall back to card payment form"
      ]
    },
    {
      "id": "Q-002",
      "priority": "medium",
      "category": "scope",
      "question": "Should Apple Pay be available on desktop Safari with Touch ID?",
      "context": "Requirement mentions 'mobile' but Apple Pay works on Mac",
      "suggestedAnswers": [
        "Yes, all Apple Pay capable devices",
        "No, mobile only (iPhone/iPad)",
        "Phase 2 - mobile first"
      ]
    },
    {
      "id": "Q-003",
      "priority": "low",
      "category": "ux",
      "question": "Should the Apple Pay button position be above or below other payment options?",
      "context": "No UI positioning specified",
      "suggestedAnswers": [
        "Above - as primary option",
        "Below - after credit card",
        "Same level - equal prominence"
      ]
    }
  ],
  "summary": {
    "total": 5,
    "byPriority": { "high": 1, "medium": 2, "low": 2 },
    "byCategory": { "error_handling": 1, "scope": 2, "ux": 2 }
  }
}
```

---

## AC Generation

When acceptance criteria are missing or incomplete, the agent generates suggestions.

```json
{
  "generatedACs": [
    {
      "id": "AC-GEN-001",
      "source": "gap_detection",
      "confidence": 0.9,
      "text": "Given a device that does not support Apple Pay, the Apple Pay button should not be displayed",
      "gherkin": "Given a device without Apple Pay capability\nWhen the payment page loads\nThen the Apple Pay button should not be visible"
    },
    {
      "id": "AC-GEN-002",
      "source": "domain_knowledge",
      "confidence": 0.85,
      "text": "Given a payment failure, the customer should see an error message and be able to retry or choose another payment method",
      "gherkin": "Given the customer initiates Apple Pay payment\nWhen the payment fails\nThen an error message should be displayed\nAnd the customer should be able to retry\nAnd the customer should be able to choose another payment method"
    },
    {
      "id": "AC-GEN-003",
      "source": "structure_extraction",
      "confidence": 0.8,
      "text": "Given a successful Apple Pay payment, the order confirmation should display 'Paid with Apple Pay'",
      "gherkin": "Given the customer completes Apple Pay payment\nWhen the order confirmation page loads\nThen the payment method should show 'Paid with Apple Pay'"
    }
  ],
  "summary": {
    "generated": 5,
    "highConfidence": 3,
    "mediumConfidence": 2
  }
}
```

---

## Domain Validation

Integration with eCommerce Domain Agent to validate entities and rules.

### Validation Process

```
Requirement Text ──▶ Entity Extraction ──▶ Domain Agent Query ──▶ Validation Report
```

### Validation Output

```json
{
  "domainValidation": {
    "valid": true,
    "entitiesFound": [
      {
        "term": "checkout",
        "mappedEntity": "Checkout",
        "confidence": 0.95,
        "domainDescription": "Process of completing a purchase"
      },
      {
        "term": "payment",
        "mappedEntity": "Payment",
        "confidence": 0.92,
        "domainDescription": "Financial transaction for order"
      },
      {
        "term": "Apple Pay",
        "mappedEntity": "PaymentMethod",
        "confidence": 0.88,
        "domainDescription": "Digital wallet payment type"
      }
    ],
    "rulesApplicable": [
      {
        "ruleId": "PAY-001",
        "rule": "Payment must be validated before order creation",
        "relevance": "high"
      },
      {
        "ruleId": "PAY-002",
        "rule": "Failed payments must be logged for audit",
        "relevance": "medium"
      }
    ],
    "warnings": [
      {
        "type": "missing_entity",
        "message": "Requirement mentions 'refund' but no refund flow specified",
        "suggestion": "Consider adding refund handling for failed Apple Pay charges"
      }
    ]
  }
}
```

---

## Output Formats

### 1. Analysis Report (Text)

```markdown
# Requirement Analysis Report

**Input:** Teams Meeting Transcript
**Analyzed:** 2024-12-20 14:30:00
**Request ID:** REQ-2024-001

---

## Quality Assessment

| Dimension | Score | Grade |
|-----------|-------|-------|
| Clarity | 85 | B |
| Completeness | 65 | D |
| Testability | 80 | B |
| Consistency | 90 | A |
| **Overall** | **78** | **C** |

**Recommendation:** Address completeness gaps before development.

---

## Extracted Requirement

**Title:** Add Apple Pay to Checkout

**Description:**
As a customer, I want to pay using Apple Pay so that I can complete 
checkout faster on my Apple devices.

**Actors:** Customer, System
**Domain Entities:** Checkout, Payment, PaymentMethod, Order

---

## Acceptance Criteria

### Original (from transcript)
1. Apple Pay button visible with other payment options
2. Tapping opens Apple Pay payment sheet
3. Success completes the order
4. Failure shows error with retry option

### Generated (suggested additions)
5. ⚠️ Apple Pay button hidden on unsupported devices
6. ⚠️ Maximum 3 retry attempts before suggesting support
7. ⚠️ Order confirmation shows "Paid with Apple Pay"

---

## Gaps Identified

| # | Severity | Gap | Suggestion |
|---|----------|-----|------------|
| 1 | 🔴 High | No timeout handling | Add 30-second timeout with error message |
| 2 | 🟡 Medium | Retry limit undefined | Specify maximum 3 retries |
| 3 | 🟡 Medium | Unsupported device handling | Hide button if Apple Pay unavailable |

---

## Clarifying Questions

**High Priority:**
1. What should happen if Apple Pay payment times out?

**Medium Priority:**
2. Should Apple Pay work on desktop Safari with Touch ID?
3. What analytics events should be tracked?

---

## Domain Validation

✅ All entities map to eCommerce domain model
✅ Payment rules PAY-001, PAY-002 applicable
⚠️ Consider refund flow for failed charges

---

## Ready for Test Generation?

**Status:** ⚠️ NOT READY - Address high-severity gaps first

**Next Steps:**
1. Answer clarifying questions
2. Add missing error handling
3. Re-analyze after updates
4. Then forward to Test Cases Agent
```

### 2. Analysis Report (JSON)

```json
{
  "meta": {
    "requestId": "REQ-2024-001",
    "inputType": "teams_transcript",
    "analyzedAt": "2024-12-20T14:30:00Z",
    "agentVersion": "1.0.0"
  },
  "qualityScore": {
    "overall": 78,
    "grade": "C",
    "dimensions": {
      "clarity": { "score": 85, "grade": "B" },
      "completeness": { "score": 65, "grade": "D" },
      "testability": { "score": 80, "grade": "B" },
      "consistency": { "score": 90, "grade": "A" }
    },
    "recommendation": "Address completeness gaps before development"
  },
  "extractedRequirement": {
    "title": "Add Apple Pay to Checkout",
    "description": "As a customer, I want to pay using Apple Pay...",
    "structure": {
      "actor": "Customer",
      "action": "Pay using Apple Pay",
      "object": "Order",
      "outcome": "Complete checkout faster"
    }
  },
  "acceptanceCriteria": {
    "original": [...],
    "generated": [...]
  },
  "gaps": [...],
  "questions": [...],
  "domainValidation": {...},
  "readyForTestGeneration": false,
  "blockers": ["High-severity gaps not addressed"]
}
```

### 3. Structured Output (for Test Cases Agent)

```json
{
  "structuredRequirement": {
    "id": "REQ-2024-001",
    "title": "Add Apple Pay to Checkout",
    "description": "As a customer, I want to pay using Apple Pay so that I can complete checkout faster on my Apple devices.",
    "acceptanceCriteria": [
      "Apple Pay button visible with other payment options on checkout page",
      "Clicking Apple Pay opens native Apple Pay payment sheet",
      "Successful payment completes the order",
      "Failed payment shows error message with retry option",
      "Apple Pay button hidden on unsupported devices",
      "Maximum 3 retry attempts then suggest alternative payment",
      "Order confirmation displays 'Paid with Apple Pay'"
    ],
    "domain": "ecommerce",
    "entities": ["Checkout", "Payment", "PaymentMethod", "Order"],
    "preconditions": [
      "Customer is on checkout page",
      "Cart contains at least one item",
      "Device supports Apple Pay"
    ],
    "additionalContext": "Follow Apple Pay UI guidelines. Support all Apple Pay capable devices including Mac with Touch ID."
  },
  "analysisMetadata": {
    "qualityScore": 78,
    "gapsAddressed": true,
    "questionsAnswered": true
  }
}
```

---

## User Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER WORKFLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │   1. INPUT   │
     │              │
     │ Jira / Text  │
     │ / Transcript │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │  2. ANALYZE  │
     │              │
     │  Agent runs  │
     │  analysis    │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐      ┌──────────────────────────────────────┐
     │  3. REVIEW   │      │  Analysis Report:                    │
     │              │◀────▶│  • Quality Score: 78/100 (C)         │
     │  View report │      │  • 3 Gaps Found                      │
     │              │      │  • 2 Questions to Answer             │
     └──────┬───────┘      └──────────────────────────────────────┘
            │
            ▼
     ┌──────────────┐
     │ 4. DECISION  │
     │              │
     │ Good enough? │
     └──────┬───────┘
            │
       ┌────┴────┐
       │         │
       ▼         ▼
    ┌──────┐  ┌──────┐
    │  NO  │  │  YES │
    └──┬───┘  └──┬───┘
       │         │
       ▼         │
┌──────────────┐ │
│   5. FIX     │ │
│              │ │
│ Edit/Answer  │ │
│ Questions    │ │
└──────┬───────┘ │
       │         │
       ▼         │
┌──────────────┐ │
│ 6. RE-ANALYZE│ │
│              │ │
│  Run again   │─┘
└──────────────┘
       │
       │ (Loop until ready)
       ▼
┌──────────────┐
│  7. ACCEPT   │
│              │
│  Mark ready  │
└──────┬───────┘
       │
       ├─────────────────────────────┐
       │                             │
       ▼                             ▼
┌──────────────┐            ┌──────────────┐
│  8a. EXPORT  │            │ 8b. FORWARD  │
│              │            │              │
│ Text / JSON  │            │ Test Cases   │
│ Report       │            │ Agent        │
└──────────────┘            └──────────────┘
```

---

## gRPC Service Definition

```protobuf
syntax = "proto3";

package requirementanalysis.v1;

service RequirementAnalysisService {
  // Analyze a requirement from any input type
  rpc AnalyzeRequirement(AnalyzeRequest) returns (AnalyzeResponse);
  
  // Re-analyze with updates (questions answered, edits made)
  rpc ReanalyzeRequirement(ReanalyzeRequest) returns (AnalyzeResponse);
  
  // Export analysis report
  rpc ExportAnalysis(ExportRequest) returns (ExportResponse);
  
  // Forward to Test Cases Agent
  rpc ForwardToTestCases(ForwardRequest) returns (ForwardResponse);
  
  // Health check
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}

// ============ Analyze ============

message AnalyzeRequest {
  string request_id = 1;
  
  oneof input {
    JiraStoryInput jira_story = 2;
    FreeFormInput free_form = 3;
    TranscriptInput transcript = 4;
  }
  
  AnalysisConfig config = 5;
}

message JiraStoryInput {
  string key = 1;
  string summary = 2;
  string description = 3;
  repeated string acceptance_criteria = 4;
  int32 story_points = 5;
  repeated string labels = 6;
  repeated string components = 7;
  string priority = 8;
  string raw_json = 9;  // Full Jira JSON if available
}

message FreeFormInput {
  string text = 1;
  string context = 2;  // Optional context about the requirement
}

message TranscriptInput {
  string transcript = 1;  // Plain text with speaker labels
  string meeting_title = 2;
  string meeting_date = 3;
  repeated string participants = 4;
}

message AnalysisConfig {
  bool include_domain_validation = 1;  // Validate against Domain Agent
  bool generate_acceptance_criteria = 2;  // Auto-generate missing ACs
  bool generate_questions = 3;  // Generate clarifying questions
  string llm_provider = 4;  // anthropic, openai, gemini
}

message AnalyzeResponse {
  string request_id = 1;
  bool success = 2;
  
  QualityScore quality_score = 3;
  ExtractedRequirement extracted_requirement = 4;
  repeated Gap gaps = 5;
  repeated ClarifyingQuestion questions = 6;
  repeated GeneratedAC generated_acs = 7;
  DomainValidation domain_validation = 8;
  
  bool ready_for_test_generation = 9;
  repeated string blockers = 10;
  
  AnalysisMetadata metadata = 11;
  string error = 12;
}

message QualityScore {
  int32 overall_score = 1;
  string overall_grade = 2;
  DimensionScore clarity = 3;
  DimensionScore completeness = 4;
  DimensionScore testability = 5;
  DimensionScore consistency = 6;
  string recommendation = 7;
}

message DimensionScore {
  int32 score = 1;
  string grade = 2;
  repeated string issues = 3;
}

message ExtractedRequirement {
  string title = 1;
  string description = 2;
  RequirementStructure structure = 3;
  repeated string original_acs = 4;
}

message RequirementStructure {
  string actor = 1;
  string action = 2;
  string object = 3;
  string outcome = 4;
  repeated string preconditions = 5;
  repeated string postconditions = 6;
  repeated string triggers = 7;
  repeated string constraints = 8;
}

message Gap {
  string id = 1;
  string category = 2;
  string severity = 3;  // high, medium, low
  string description = 4;
  string location = 5;
  string suggestion = 6;
}

message ClarifyingQuestion {
  string id = 1;
  string priority = 2;
  string category = 3;
  string question = 4;
  string context = 5;
  repeated string suggested_answers = 6;
  string answer = 7;  // Filled in during reanalysis
}

message GeneratedAC {
  string id = 1;
  string source = 2;  // gap_detection, domain_knowledge, structure_extraction
  float confidence = 3;
  string text = 4;
  string gherkin = 5;
  bool accepted = 6;  // User can accept/reject
}

message DomainValidation {
  bool valid = 1;
  repeated EntityMapping entities_found = 2;
  repeated ApplicableRule rules_applicable = 3;
  repeated string warnings = 4;
}

message EntityMapping {
  string term = 1;
  string mapped_entity = 2;
  float confidence = 3;
  string domain_description = 4;
}

message ApplicableRule {
  string rule_id = 1;
  string rule = 2;
  string relevance = 3;
}

message AnalysisMetadata {
  string llm_provider = 1;
  string llm_model = 2;
  int32 tokens_used = 3;
  float analysis_time_ms = 4;
  string input_type = 5;
}

// ============ Reanalyze ============

message ReanalyzeRequest {
  string request_id = 1;
  string original_request_id = 2;  // Link to original analysis
  
  // Updated content
  string updated_description = 3;
  repeated string updated_acs = 4;
  
  // Answered questions
  repeated AnsweredQuestion answered_questions = 5;
  
  // Accepted/rejected generated ACs
  repeated ACDecision ac_decisions = 6;
  
  AnalysisConfig config = 7;
}

message AnsweredQuestion {
  string question_id = 1;
  string answer = 2;
}

message ACDecision {
  string ac_id = 1;
  bool accepted = 2;
  string modified_text = 3;  // If user edited the generated AC
}

// ============ Export ============

message ExportRequest {
  string request_id = 1;
  string format = 2;  // text, json
}

message ExportResponse {
  string request_id = 1;
  string format = 2;
  string content = 3;  // The exported report
  string filename = 4;
}

// ============ Forward to Test Cases ============

message ForwardRequest {
  string request_id = 1;
  bool include_generated_acs = 2;  // Include agent-generated ACs
  TestCasesConfig test_cases_config = 3;  // Config for Test Cases Agent
}

message TestCasesConfig {
  string output_format = 1;
  string coverage_level = 2;
  repeated string test_types = 3;
  string llm_provider = 4;
}

message ForwardResponse {
  string request_id = 1;
  bool success = 2;
  string test_cases_request_id = 3;  // Request ID from Test Cases Agent
  int32 test_cases_generated = 4;
  string error = 5;
}

// ============ Health ============

message HealthCheckRequest {}

message HealthCheckResponse {
  string status = 1;
  map<string, string> components = 2;
}
```

---

## Directory Structure

```
requirement-analysis-agent/
├── README.md
├── Dockerfile
├── pyproject.toml
├── .env.example
│
├── protos/                           # Symlink to /qa-platform/protos
│   ├── requirement_analysis.proto
│   ├── ecommerce_domain.proto
│   └── test_cases.proto
│
├── src/
│   └── requirement_analysis_agent/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       │
│       ├── proto/                    # Generated protobuf code
│       │   └── ...
│       │
│       ├── server/
│       │   ├── __init__.py
│       │   ├── grpc_server.py
│       │   └── health.py
│       │
│       ├── parser/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── jira_parser.py
│       │   ├── freeform_parser.py
│       │   └── transcript_parser.py
│       │
│       ├── analyzer/
│       │   ├── __init__.py
│       │   ├── engine.py             # Main orchestrator
│       │   ├── quality_scorer.py
│       │   ├── gap_detector.py
│       │   ├── structure_extractor.py
│       │   ├── question_generator.py
│       │   └── ac_generator.py
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   └── validator.py          # Domain Agent integration
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── router.py
│       │   ├── anthropic_client.py
│       │   ├── openai_client.py
│       │   └── gemini_client.py
│       │
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── quality_scoring.py
│       │   ├── gap_detection.py
│       │   ├── structure_extraction.py
│       │   ├── question_generation.py
│       │   ├── ac_generation.py
│       │   └── transcript_analysis.py
│       │
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── domain_agent.py
│       │   └── test_cases_agent.py
│       │
│       ├── export/
│       │   ├── __init__.py
│       │   ├── text_exporter.py
│       │   └── json_exporter.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── requirement.py
│       │   ├── analysis.py
│       │   └── quality.py
│       │
│       └── utils/
│           ├── __init__.py
│           └── logging.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── sample_jira.json
│   │   ├── sample_freeform.txt
│   │   └── sample_transcript.txt
│   ├── unit/
│   │   ├── test_jira_parser.py
│   │   ├── test_transcript_parser.py
│   │   ├── test_quality_scorer.py
│   │   ├── test_gap_detector.py
│   │   └── ...
│   └── integration/
│       ├── test_grpc_server.py
│       └── test_full_pipeline.py
│
└── docs/
    ├── PRD.md
    └── TASKS.md
```

---

## Integration with Existing Agents

### Calls Domain Agent (Port 9002)

```python
# Validate entities against domain model
domain_context = await domain_agent.get_domain_context(
    entity="Payment",
    workflow="Checkout"
)

# Check business rules
entity_details = await domain_agent.get_entity("PaymentMethod")
```

### Forwards to Test Cases Agent (Port 9003)

```python
# After analysis is complete and accepted
test_cases_response = await test_cases_agent.generate_test_cases(
    user_story=structured_requirement,
    domain_config={
        "domain": "ecommerce",
        "entity": "Payment",
        "workflow": "Checkout"
    },
    generation_config={
        "output_format": "gherkin",
        "coverage_level": "standard"
    }
)
```

---

## Port Summary

| Service | gRPC | HTTP |
|---------|------|------|
| Test Data Agent | 9001 | 8081 |
| eCommerce Domain Agent | 9002 | 8082 |
| Test Cases Agent | 9003 | 8083 |
| **Requirement Analysis Agent** | **9004** | **8084** |

---

## V2 Future Features (Out of Scope)

| Feature | Description |
|---------|-------------|
| Jira Webhook | Auto-trigger on new story creation |
| Jira Sync | Push updated ACs back to Jira |
| Image Analysis | Analyze mockups/wireframes in attachments |
| Audio Transcription | Convert meeting recordings to transcript |
| Confluence Integration | Pull requirements from Confluence pages |
| Slack Thread Analysis | Analyze requirement discussions in Slack |
| Bulk Analysis | Analyze multiple requirements at once |
| Comparison | Compare versions of requirements |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Analysis latency | < 20s for single requirement |
| Quality score accuracy | > 85% agreement with human review |
| Gap detection precision | > 80% (gaps found are real) |
| Gap detection recall | > 70% (find most real gaps) |
| AC generation acceptance | > 60% of generated ACs accepted |
| Forward success rate | 100% when marked ready |
