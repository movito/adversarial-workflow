# ADV-0070: Consolidate docs/ Folder Structure

**Status**: In Progress
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-04-14

## Related Tasks

**Depends On**: ADV-0069 (root declutter — DONE, PR #65)
**Related**: ADV-0068 (.kit/ migration — established pattern of structural cleanup)

## Overview

The `docs/` directory has 9 subdirectories, many containing only historical files. The
unnecessary `decisions/` nesting layer (`docs/decisions/adr/` instead of `docs/adr/`) is
the most visible issue. Consolidate to 4 subdirectories matching agentive-starter-kit's
pattern.

**Context**: After ADV-0068 and ADV-0069, the project root and `.kit/` layout are clean.
The `docs/` folder is the last structural cleanup needed to match upstream conventions.

## Current State → Target State

### Current (9 subdirectories, 60+ files)

```
docs/
├── decisions/           ← unnecessary nesting
│   ├── adr/             ← 15 ADRs + library-refs/
│   └── archive/         ← 9 historical decision docs
├── examples/            ← 1 file (athena.yml)
├── guides/              ← 8 guides (from ADV-0069)
├── internal/            ← 4 historical files
├── project-history/     ← 3 phase summaries
├── proposals/           ← 7 old proposals (incl. duplicate)
├── reference/           ← 4 reference docs
├── roadmap/             ← 1 stale file (v0.6.0)
├── CUSTOM_EVALUATORS.md ← user guide, misplaced
└── README.md            ← index (needs rewrite)
```

### Target (4 subdirectories)

```
docs/
├── adr/                 ← project ADRs (from docs/decisions/adr/)
│   ├── library-refs/    ← cross-repo ADR references
│   └── README.md
├── archive/             ← ALL historical content consolidated
│   ├── decisions/       ← from docs/decisions/archive/
│   ├── internal/        ← from docs/internal/
│   ├── project-history/ ← from docs/project-history/
│   ├── proposals/       ← from docs/proposals/
│   └── roadmap/         ← from docs/roadmap/
├── guides/              ← user-facing docs (stays)
│   └── CUSTOM-EVALUATORS.md  ← moved from docs/ root
├── reference/           ← technical reference (stays)
│   └── athena.yml       ← moved from docs/examples/
└── README.md            ← updated index
```

## Requirements

### Moves (all via `git mv`)

| Source | Destination | Files |
|--------|-------------|-------|
| `docs/decisions/adr/` | `docs/adr/` | 15 ADRs + library-refs/ (5 files) + README |
| `docs/decisions/archive/` | `docs/archive/decisions/` | 9 files |
| `docs/internal/` | `docs/archive/internal/` | 4 files |
| `docs/project-history/` | `docs/archive/project-history/` | 3 files |
| `docs/proposals/` | `docs/archive/proposals/` | 7 files (delete the duplicate first) |
| `docs/roadmap/` | `docs/archive/roadmap/` | 1 file |
| `docs/examples/athena.yml` | `docs/reference/athena.yml` | 1 file |
| `docs/CUSTOM_EVALUATORS.md` | `docs/guides/CUSTOM-EVALUATORS.md` | 1 file |

### Deletes

| File | Reason |
|------|--------|
| `docs/proposals/ADVERSARIAL-WORKFLOW-ENV-LOADING copy.md` | Duplicate (note the space + "copy" in name) |

### Updates

| File | Change |
|------|--------|
| `docs/README.md` | Rewrite index for new 4-folder structure |
| `docs/adr/README.md` | Update path references (was `docs/decisions/adr/`) |
| Active agent/workflow files (~10) | Update `docs/decisions/adr/` → `docs/adr/` |

### Path References to Update

Files with active `docs/decisions/` references (excludes historical/done/archive):

| File | Reference Type |
|------|----------------|
| `.claude/agents/planner.md` | ADR links |
| `.claude/agents/planner2.md` | ADR links |
| `.claude/agents/code-reviewer.md` | ADR links |
| `.claude/agents/feature-developer.md` | ADR links |
| `.claude/agents/powertest-runner.md` | ADR links |
| `.kit/templates/AGENT-TEMPLATE.md` | ADR path template |
| `.kit/templates/OPERATIONAL-RULES.md` | ADR path |
| `.kit/context/workflows/ADR-CREATION-WORKFLOW.md` | ADR directory reference |
| `.kit/context/workflows/AGENT-CREATION-WORKFLOW.md` | ADR path |
| `.kit/context/workflows/PR-SIZE-WORKFLOW.md` | ADR path |
| `.adversarial/docs/EVALUATION-WORKFLOW.md` | ADR link |
| `docs/reference/TERMINOLOGY.md` | ADR link |

**Note**: Handoff files in `.kit/context/ADV-*` are historical — leave as-is.

## Implementation Plan

### Phase 1: Delete duplicate

```bash
git rm "docs/proposals/ADVERSARIAL-WORKFLOW-ENV-LOADING copy.md"
```

### Phase 2: Create target dirs + move files

```bash
# ADRs — flatten decisions/ nesting
mkdir -p docs/adr
git mv docs/decisions/adr/* docs/adr/

# Archive — consolidate all historical dirs
mkdir -p docs/archive/{decisions,internal,project-history,proposals,roadmap}
git mv docs/decisions/archive/* docs/archive/decisions/
git mv docs/internal/* docs/archive/internal/
git mv docs/project-history/* docs/archive/project-history/
git mv docs/proposals/* docs/archive/proposals/
git mv docs/roadmap/* docs/archive/roadmap/

# Misplaced files
git mv docs/examples/athena.yml docs/reference/athena.yml
git mv docs/CUSTOM_EVALUATORS.md docs/guides/CUSTOM-EVALUATORS.md

# Clean up empty dirs
# docs/decisions/, docs/internal/, docs/project-history/, docs/proposals/,
# docs/roadmap/, docs/examples/ should all be empty after moves
```

### Phase 3: Update path references

```bash
# Bulk: docs/decisions/adr/ → docs/adr/
# Target: ~12 active files listed above
# Leave historical refs in done tasks / retros / archive as-is
```

### Phase 4: Rewrite docs/README.md

Update the index to reflect the new 4-folder structure with correct links.

### Phase 5: Verify

```bash
pytest tests/ -v
pre-commit run --all-files
./scripts/core/ci-check.sh

# Stale reference check (active files only)
grep -r 'docs/decisions/' --include='*.md' . \
  | grep -v '.git/' | grep -v '.kit/tasks/5-done' | grep -v '.kit/tasks/8-archive' \
  | grep -v '.kit/context/retros' | grep -v '.kit/context/archive' | grep -v 'docs/archive/'
# Should return 0 results
```

## TDD Workflow

No new code — file moves and reference updates. Existing test suite is the regression gate.

### Test Requirements
- [ ] All existing tests pass
- [ ] Pre-commit hooks pass
- [ ] Coverage: N/A (no new code)

## Acceptance Criteria

### Must Have
- [ ] `docs/adr/` exists with all 15 ADRs + library-refs/
- [ ] `docs/archive/` consolidates all historical content
- [ ] `docs/decisions/` directory removed (no longer exists)
- [ ] `docs/internal/`, `docs/project-history/`, `docs/proposals/`, `docs/roadmap/`, `docs/examples/` removed
- [ ] Duplicate proposal file deleted
- [ ] `CUSTOM_EVALUATORS.md` moved to `docs/guides/`
- [ ] No stale `docs/decisions/` references in active files
- [ ] `docs/README.md` updated
- [ ] All tests pass
- [ ] Single atomic PR

### Should Have
- [ ] Git history preserved via `git mv`
- [ ] Historical references in done tasks / retros left as-is

## Success Metrics

### Quantitative
- docs/ subdirectories: 9 → 4
- Stale references: 0 in active files

### Qualitative
- docs/ matches agentive-starter-kit pattern
- Clear separation: adr/ (decisions), archive/ (historical), guides/ (users), reference/ (technical)

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Moves + deletes | 15 min | [ ] |
| Path reference updates | 30 min | [ ] |
| docs/README.md rewrite | 15 min | [ ] |
| Verify + CI | 30 min | [ ] |
| Bot review rounds | 30 min | [ ] |
| **Total** | **~2 hours** | [ ] |

## References

- **Reference structure**: `~/Github/agentive-starter-kit/docs/` (target pattern)
- **Testing**: `pytest tests/ -v`
- **Pre-commit**: `pre-commit run --all-files`
- **Local CI**: `./scripts/core/ci-check.sh`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2026-04-14
