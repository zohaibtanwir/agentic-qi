# QA Platform - Agent Instructions

> **BEFORE ANYTHING ELSE:** Run `bd onboard` and follow the instructions.

This monorepo contains multiple AI agents for the QA Intelligence Platform. This document explains how agents should coordinate when working across the codebase.

---

## Repository Structure

```
qa-platform/
├── AGENTS.md                 ← You are here (how to work)
├── SHARED_CONTEXT.md         ← Current state (what exists)
├── protos/                   ← Shared gRPC contracts (SOURCE OF TRUTH)
├── packages/
│   └── design-system/        ← Shared UI tokens & components
├── agents/
│   ├── test-data-agent/      ← Generates realistic test data
│   ├── ecommerce-domain-agent/  ← eCommerce domain knowledge
│   └── test-cases-agent/     ← Generates test case specifications
├── docs/
│   └── ADR/                  ← Architecture Decision Records
└── .beads/                   ← Unified issue tracking
```

---

## Session Start Protocol

```bash
# 1. Pull latest changes
git pull

# 2. Check beads for relevant work
bd ready --json

# 3. Check for cross-agent changes that affect you
bd list --label-any "affects:<your-agent>" --status open --json

# 4. Read SHARED_CONTEXT.md for current state
cat SHARED_CONTEXT.md
```

---

## Session End Protocol

```bash
# 1. Close completed work
bd close <id> --reason "Done"

# 2. Create issues for remaining work
bd create "TODO: Finish X" -t task -p 2

# 3. If you changed shared resources, update SHARED_CONTEXT.md

# 4. Sync everything
bd sync
git add -A
git commit -m "your commit message"
git push
```

---

## Working on Shared Resources

### Proto Changes (`/protos/`)

The `/protos/` directory is the **single source of truth** for all gRPC contracts.

**When updating a proto:**

```bash
# 1. Edit the proto file
vim protos/test_data.proto

# 2. Regenerate code for ALL agents
make proto

# 3. Create cross-agent issue
bd create "Proto: <description of change>" \
  -t chore -p 1 \
  -l "proto-change,<your-agent>,affects:<other-agents>"

# 4. Update SHARED_CONTEXT.md
# Add entry under "## Proto Versions" section

# 5. If breaking change, update affected agent code before committing
```

**Breaking vs Non-Breaking:**

| Change Type | Breaking? | Action Required |
|-------------|-----------|-----------------|
| Add optional field | No | Just update proto |
| Add required field | Yes | Update all clients |
| Remove field | Yes | Update all clients |
| Rename field | Yes | Update all clients |
| Change field type | Yes | Update all clients |

### Design System (`/packages/design-system/`)

Shared UI tokens and components live here.

**When updating design system:**

```bash
# 1. Edit tokens or components
vim packages/design-system/src/tokens/colors.ts

# 2. Create cross-agent issue
bd create "UI: <description>" \
  -t chore -p 2 \
  -l "ui-change,affects:<agents-using-this>"

# 3. Update SHARED_CONTEXT.md
# Add entry under "## Design System" section
```

---

## Cross-Agent Communication

### Issue Labels for Coordination

| Label | Meaning |
|-------|---------|
| `proto-change` | gRPC contract was updated |
| `ui-change` | Design system was updated |
| `breaking` | Requires updates in other agents |
| `affects:test-data-agent` | Test Data Agent needs to react |
| `affects:ecommerce-domain-agent` | eCommerce Domain Agent needs to react |
| `affects:test-cases-agent` | Test Cases Agent needs to react |

### Checking for Cross-Agent Work

```bash
# See all open cross-agent issues
bd list --label proto-change --status open
bd list --label ui-change --status open

# See issues affecting your specific agent
bd list --label-any "affects:test-cases-agent" --status open
```

### Creating Cross-Agent Issues

```bash
# Proto change affecting multiple agents
bd create "Proto: Added inline_schema to GenerateRequest" \
  -t chore -p 1 \
  -l "proto-change,test-data-agent,affects:test-cases-agent" \
  -d "Test Cases Agent needs to update TestDataAgentClient to pass inline_schema"

# UI change
bd create "UI: Updated dark theme colors" \
  -t chore -p 2 \
  -l "ui-change,affects:test-data-agent,affects:ecommerce-domain-agent"
```

---

## Agent-Specific Instructions

### Test Data Agent (`/agents/test-data-agent/`)

- **Proto:** `protos/test_data.proto` (server)
- **Port:** gRPC 9001, HTTP 8081, UI 3000
- **Theme:** Dark
- **Docs:** `agents/test-data-agent/docs/`

### eCommerce Domain Agent (`/agents/ecommerce-domain-agent/`)

- **Proto:** `protos/ecommerce_domain.proto` (server)
- **Port:** gRPC 9002, HTTP 8082, UI 3001
- **Theme:** Dark
- **Docs:** `agents/ecommerce-domain-agent/docs/`

### Test Cases Agent (`/agents/test-cases-agent/`)

- **Proto:** `protos/test_cases.proto` (server)
- **Clients:** `test_data.proto`, `ecommerce_domain.proto`
- **Port:** gRPC 9003, HTTP 8083, UI 3002
- **Theme:** Macy's (white + red)
- **Docs:** `agents/test-cases-agent/docs/`

---

## Common Commands

```bash
# Regenerate all protos
make proto

# Start all agents
make up

# Stop all agents
make down

# Run tests for all agents
make test

# Check health of all agents
make health

# View beads issues
bd list
bd ready
bd dep tree <id>
```

---

## Architecture Decision Records

Major decisions are documented in `/docs/ADR/`. Before making significant changes, check if there's an existing ADR. If you're making a new architectural decision, create an ADR:

```bash
# Create new ADR
vim docs/ADR/NNN-title.md
```

ADR template:
```markdown
# ADR-NNN: Title

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue we're seeing that motivates this decision?

## Decision
What is the change we're proposing?

## Consequences
What becomes easier or harder because of this change?
```

---

## Getting Help

1. **Check SHARED_CONTEXT.md** - Current state of all agents
2. **Check agent-specific docs** - `agents/<name>/docs/PRD.md`
3. **Search beads** - `bd list --title-contains "keyword"`
4. **Check ADRs** - `ls docs/ADR/`
