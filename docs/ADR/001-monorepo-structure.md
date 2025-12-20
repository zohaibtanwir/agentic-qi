# ADR-001: Monorepo Structure for QA Platform

## Status

Accepted

## Context

The QA Platform consists of multiple AI agents that need to communicate via gRPC:
- Test Data Agent
- eCommerce Domain Agent
- Test Cases Agent

These agents share:
- Proto definitions (gRPC contracts)
- UI design tokens and components
- Issue tracking (Beads)
- Coding conventions

Previously, each agent was in a separate repository, leading to:
- Proto files duplicated across repos
- No single source of truth for contracts
- Difficulty coordinating cross-agent changes
- Agents couldn't easily discover each other's state

## Decision

Adopt a monorepo structure with:

```
qa-platform/
├── protos/                 # Shared gRPC contracts (source of truth)
├── packages/design-system/ # Shared UI tokens and components
├── agents/                 # Individual agent codebases
├── docs/                   # Shared documentation
├── .beads/                 # Unified issue tracking
├── AGENTS.md               # Instructions for AI agents
└── SHARED_CONTEXT.md       # Living document of current state
```

Key principles:
1. **Proto files in `/protos/`** are the single source of truth
2. **One Beads database** tracks all cross-agent work
3. **SHARED_CONTEXT.md** is updated when shared resources change
4. **Labels in Beads** communicate cross-agent impacts

## Consequences

### Positive
- Single source of truth for contracts
- AI agents can read SHARED_CONTEXT.md to understand current state
- Cross-agent changes are tracked in one place
- `make proto` regenerates all clients consistently
- Easier to run full system locally with `docker-compose`

### Negative
- Larger repository size
- All agents must be compatible with shared proto changes
- Requires discipline to update SHARED_CONTEXT.md

### Neutral
- CI/CD pipeline needs to detect which agents changed
- Need to migrate existing separate repos into monorepo

## References

- Beads: https://github.com/steveyegge/beads
- Proto versioning best practices: https://protobuf.dev/programming-guides/dos-donts/
