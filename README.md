# QA Platform

Multi-agent system for QA Intelligence, built for the Macy's QE Transformation Program.

## Overview

This monorepo contains three AI agents that work together to provide comprehensive test automation support:

| Agent | Purpose | Port |
|-------|---------|------|
| **Test Data Agent** | Generates realistic test data using LLMs | 9001 |
| **eCommerce Domain Agent** | Provides eCommerce domain knowledge, business rules, edge cases | 9002 |
| **Test Cases Agent** | Generates test case specifications from requirements | 9003 |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         QA Platform                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────┐         ┌─────────────────┐                   │
│   │  Test Data      │         │  eCommerce      │                   │
│   │  Agent          │◄────────│  Domain Agent   │                   │
│   │  :9001          │         │  :9002          │                   │
│   └────────┬────────┘         └────────┬────────┘                   │
│            │                           │                             │
│            │         gRPC              │                             │
│            └───────────┬───────────────┘                             │
│                        │                                             │
│                        ▼                                             │
│            ┌─────────────────────┐                                   │
│            │  Test Cases Agent   │                                   │
│            │  :9003              │                                   │
│            └─────────────────────┘                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- [Beads CLI](https://github.com/steveyegge/beads) (`bd`)

### Setup

```bash
# Clone the repo
git clone <repo-url>
cd qa-platform

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Initialize beads
bd init --quiet

# Start all agents
make up

# Check health
make health
```

### Access Points

| Service | URL |
|---------|-----|
| Test Data Agent UI | http://localhost:3000 |
| eCommerce Domain Agent UI | http://localhost:3001 |
| Test Cases Agent UI | http://localhost:3002 |

## Development

### For AI Agents

See [AGENTS.md](./AGENTS.md) for instructions on working with this codebase.

Key commands:
```bash
bd ready                    # Find work with no blockers
bd list                     # List all issues
bd create "Title" -t task   # Create issue
bd close <id>               # Complete issue
bd sync                     # Sync to git
```

### For Humans

```bash
# Regenerate protos after changes
make proto

# Run tests
make test

# Check linting
make lint

# View logs
make logs
```

### Current State

See [SHARED_CONTEXT.md](./SHARED_CONTEXT.md) for:
- Proto versions and changes
- Design system themes
- Port allocations
- Recent decisions
- Integration map

## Repository Structure

```
qa-platform/
├── AGENTS.md               # Instructions for AI agents
├── SHARED_CONTEXT.md       # Current state (living document)
├── Makefile                # Cross-agent commands
├── docker-compose.yml      # Run all agents
│
├── protos/                 # Shared gRPC contracts
│   ├── test_data.proto
│   ├── ecommerce_domain.proto
│   └── test_cases.proto
│
├── packages/
│   └── design-system/      # Shared UI tokens & components
│
├── agents/
│   ├── test-data-agent/
│   │   ├── service/        # Python gRPC service
│   │   ├── ui/             # Next.js UI
│   │   └── docs/           # PRD, tasks
│   ├── ecommerce-domain-agent/
│   │   └── ...
│   └── test-cases-agent/
│       └── ...
│
├── docs/
│   └── ADR/                # Architecture Decision Records
│
└── .beads/                 # Issue tracking
```

## Issue Tracking

This project uses [Beads](https://github.com/steveyegge/beads) for issue tracking.

```bash
# View ready work
bd ready

# View all issues
bd list

# Create cross-agent issue
bd create "Proto: Added field X" \
  -l "proto-change,affects:test-cases-agent"
```

## Contributing

1. Check `bd ready` for available work
2. Create a branch
3. Make changes
4. Update `SHARED_CONTEXT.md` if changing shared resources
5. Create beads issues for follow-up work
6. Submit PR

## License

Proprietary - Zensar Technologies
