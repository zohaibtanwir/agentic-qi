# QA Platform - Claude Memory

## Task Tracking

**Beads is the single source of truth for all tasks.** Use `bd` commands to manage issues:
- `bd list` - List open issues
- `bd list --all` - List all issues
- `bd add "title" --priority P1 --type feature` - Create issue
- `bd close <id>` - Close issue

## Completed: Original Input Display (2026-01-16)

### Feature
Display the original requirement text when viewing analysis results from history.

### Changes
- **Proto**: Added `OriginalInput` message to `protos/requirement_analysis.proto`
- **Backend**: Extract and save original input in `servicer.py`
- **Frontend**: Added `OriginalInputCard` component to `AnalysisResults.tsx`
- **Store**: Updated `requirement-analysis-store.ts` to handle originalInput state

### Behavior
- New analyses display "Original Requirement" card with title, text, and input type
- Old analyses (before this feature) don't have original input data - expected behavior
- Beads issue: `qa-platform-a9d` (closed)
- Git commit: `4c261c1`

## Completed: History Sorting Fix (2026-01-15)

History entries in Requirement Analysis Agent now sorted chronologically (newest first).
- Added `Sort.by_property("created_at", ascending=False)` to `weaviate_client.py`
- Beads issue: `qa-platform-c8s` (closed)

## Completed: Data Masking Feature (2026-01-13)

PII protection for Test Data Agent with partial masking (e.g., `j***@e****.com`).
- Backend masking module with PII detection
- Frontend Masking tab and masked/unmasked toggle
- All 14 Beads tasks closed (qa-platform-e31 through qa-platform-dsg)

## Completed: Full Agent Integration Testing (2026-01-14)

All three agents verified with real gRPC backend and LLM:
| Agent | URL | Key Output |
|-------|-----|------------|
| Test Data Agent | /test-data | 10 records, 94.4% coherence |
| Requirement Analysis Agent | /requirement-analysis | 11 gaps, 4 ACs |
| Test Cases Agent | /test-cases | 10 test cases |

## Project Structure

- `frontend/` - Next.js frontend (port 3000)
- `agents/test-data-agent/` - Python gRPC backend (port 9091 gRPC, 8091 HTTP)
- `agents/requirement-analysis-agent/` - Python gRPC backend (port 9004 gRPC, 8084 HTTP)
- `agents/test-cases-agent/` - Python gRPC backend
- `protos/` - Protocol Buffer definitions
- `.beads/` - Beads issue tracking
