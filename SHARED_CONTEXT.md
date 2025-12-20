# QA Platform - Shared Context

> **Last Updated:** 2024-12-20
> 
> This document tracks the current state of all agents, shared contracts, and recent decisions. Agents should read this at session start and update it when making cross-agent changes.

---

## Agents Overview

| Agent | Purpose | Status | Owner |
|-------|---------|--------|-------|
| Test Data Agent | Generates realistic test data using LLMs | ✅ Active | - |
| eCommerce Domain Agent | Provides eCommerce domain knowledge | ✅ Active | - |
| Test Cases Agent | Generates test case specifications | 🚧 In Development | - |

---

## Port Allocation

| Agent | gRPC | HTTP Health | UI | Weaviate |
|-------|------|-------------|-----|----------|
| Test Data Agent | 9001 | 8081 | 3000 | - |
| eCommerce Domain Agent | 9002 | 8082 | 3001 | 8081 |
| Test Cases Agent | 9003 | 8083 | 3002 | 8084 |

---

## Proto Versions

### test_data.proto (v1.0)

**Location:** `/protos/test_data.proto`
**Server:** Test Data Agent
**Clients:** Test Cases Agent

| Date | Change | Breaking |
|------|--------|----------|
| 2024-12-18 | Initial version with GenerateData, GetSchemas, HealthCheck | - |
| 2024-12-18 | Added `inline_schema` field to GenerateRequest | No |

**Key Messages:**
- `GenerateRequest` - 15 fields including entity, count, context, scenarios, inline_schema
- `GenerateResponse` - success, data, record_count, metadata
- `GenerationMetadata` - generation_path, tokens_used, coherence_score

### ecommerce_domain.proto (v1.0)

**Location:** `/protos/ecommerce_domain.proto`
**Server:** eCommerce Domain Agent
**Clients:** Test Cases Agent

| Date | Change | Breaking |
|------|--------|----------|
| 2024-12-20 | Initial version | - |

**Key RPCs:**
- `GetDomainContext` - Get context for test generation
- `GetEntity` - Get entity details with rules, relationships, edge cases
- `GetWorkflow` - Get workflow with steps and validations
- `GetEdgeCases` - Get edge cases for entity/workflow
- `GenerateTestData` - Proxy to Test Data Agent with domain context

### test_cases.proto (v1.0)

**Location:** `/protos/test_cases.proto`
**Server:** Test Cases Agent
**Clients:** (none yet)

| Date | Change | Breaking |
|------|--------|----------|
| 2024-12-20 | Initial version | - |

**Key RPCs:**
- `GenerateTestCases` - Generate from user story, API spec, or free-form
- `GetTestCase` - Get specific test case
- `ListTestCases` - List with filters
- `StoreTestCases` - Store for learning
- `AnalyzeCoverage` - Analyze requirement coverage

---

## Design System

### Themes

| Theme | Used By | Background | Primary | Text |
|-------|---------|------------|---------|------|
| Dark | Test Data Agent, eCommerce Domain Agent | #1a1a2e | #4ade80 (green) | #e2e8f0 |
| Macy's | Test Cases Agent | #FFFFFF | #E21A2C (red) | #000000 |

### Theme Details

**Dark Theme:**
```css
--bg-primary: #1a1a2e
--bg-secondary: #16162a
--bg-tertiary: #0f0f1a
--text-primary: #e2e8f0
--text-secondary: #94a3b8
--accent: #4ade80
```

**Macy's Theme:**
```css
--bg-primary: #FFFFFF
--bg-secondary: #F8F8F8
--text-primary: #000000
--text-secondary: #666666
--accent: #E21A2C (Macy's Red)
--font: Arial, Avenir
```

### Shared Components

| Component | Location | Used By |
|-----------|----------|---------|
| Header | `packages/design-system/src/components/Header` | All |
| Sidebar | `packages/design-system/src/components/Sidebar` | All |
| DataTable | `packages/design-system/src/components/DataTable` | All |
| LoadingSpinner | `packages/design-system/src/components/LoadingSpinner` | All |

---

## LLM Configuration

All agents support multiple LLM providers:

| Provider | Model | Default For | Env Variable |
|----------|-------|-------------|--------------|
| Anthropic | claude-sonnet-4-20250514 | All agents | `ANTHROPIC_API_KEY` |
| OpenAI | gpt-4-turbo-preview | Fallback | `OPENAI_API_KEY` |
| Gemini | gemini-pro | Fallback | `GEMINI_API_KEY` |

**Convention:** Anthropic Claude is the default. Others are available via config.

---

## Vector Database (Weaviate)

| Agent | Collections | Port |
|-------|-------------|------|
| eCommerce Domain Agent | Entities, Workflows, EdgeCases, BusinessRules | 8081 |
| Test Cases Agent | TestCases, TestPatterns, CoveragePatterns | 8084 |

---

## Integration Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   ┌─────────────────┐         ┌─────────────────┐                  │
│   │  Test Data      │         │  eCommerce      │                  │
│   │  Agent          │         │  Domain Agent   │                  │
│   │  :9001          │         │  :9002          │                  │
│   └────────┬────────┘         └────────┬────────┘                  │
│            │                           │                            │
│            │    gRPC clients           │                            │
│            └───────────┬───────────────┘                            │
│                        │                                            │
│                        ▼                                            │
│            ┌─────────────────────┐                                  │
│            │  Test Cases Agent   │                                  │
│            │  :9003              │                                  │
│            │                     │                                  │
│            │  Calls:             │                                  │
│            │  - TestDataService  │                                  │
│            │  - DomainService    │                                  │
│            └─────────────────────┘                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Recent Decisions

### 2024-12-20: Multi-LLM Support
- **Decision:** All agents support Anthropic (default), OpenAI, Gemini
- **Rationale:** Flexibility for cost/performance tradeoffs
- **Implementation:** LLM Router pattern with provider config per request

### 2024-12-20: Test Data Placement in Test Cases
- **Decision:** Support both embedded (in steps) AND separate section
- **Rationale:** Different use cases need different formats
- **Implementation:** `TestDataPlacement` enum: EMBEDDED, SEPARATE, BOTH

### 2024-12-20: Macy's Branding for Test Cases Agent
- **Decision:** Test Cases Agent uses Macy's white theme, others use dark
- **Rationale:** Client-specific branding requirement
- **Implementation:** Separate theme in design system

### 2024-12-20: Beads for Issue Tracking
- **Decision:** Use Beads (`bd`) for agent memory and task management
- **Rationale:** Persistent memory across sessions, cross-agent coordination
- **Implementation:** Single `.beads/` at monorepo root

### 2024-12-19: Jira Integration Deferred
- **Decision:** Jira webhook/export is V2, not V1
- **Rationale:** Focus on core generation first
- **Implementation:** TODO placeholders in Test Cases Agent tasks

---

## Pending Cross-Agent Work

Check beads for current items:
```bash
bd list --label-any "proto-change,ui-change" --status open
```

---

## Conventions

### Naming

| Item | Convention | Example |
|------|------------|---------|
| Proto package | `<domain>.<service>.v1` | `testdata.v1` |
| gRPC methods | PascalCase | `GenerateTestCases` |
| REST endpoints | kebab-case | `/api/test-cases` |
| Python modules | snake_case | `test_cases_agent` |
| TypeScript files | kebab-case | `test-case-preview.tsx` |

### File Locations

| Type | Location |
|------|----------|
| Proto definitions | `/protos/*.proto` |
| Agent code | `/agents/<name>/service/` |
| Agent UI | `/agents/<name>/ui/` |
| Agent docs | `/agents/<name>/docs/` |
| Shared UI | `/packages/design-system/` |
| Architecture docs | `/docs/ADR/` |

### Commit Messages

```
feat(agent): description     # New feature
fix(agent): description      # Bug fix
refactor(agent): description # Code refactoring
docs(agent): description     # Documentation
chore(agent): description    # Maintenance
proto: description           # Proto changes (cross-agent)
ui: description              # Design system changes
```

---

## Quick Reference

```bash
# Start all agents
make up

# View agent health
make health

# Regenerate protos
make proto

# Find ready work
bd ready

# Find cross-agent issues
bd list --label proto-change --status open
```
