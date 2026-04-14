# ADV-0062: Preflight Auto-Type from Task Spec — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-03-18
**From**: Planner
**To**: feature-developer-v3
**Task**: `delegation/tasks/2-todo/ADV-0062-preflight-auto-type-from-task-spec.md`
**Status**: Ready for implementation
**Evaluation**: N/A (small, well-scoped enhancement)

---

## Task Summary

Add auto-detection of task type from the task spec's `**Type**` frontmatter field to `scripts/core/preflight-check.sh`. Currently, when `--type` is omitted, the script auto-detects based on whether the branch has code changes (code vs docs). This enhancement adds a middle priority: if `--type` is not provided, first try to read `**Type**` from the task file, then fall back to the existing code-changes heuristic.

## Current Situation

ADV-0060 added task-type modes (`code`, `docs`, `sync`) to preflight. Agents must pass `--type sync` or `--type docs` manually. The task spec already has a `**Type**` field (e.g., `Upstream Sync`, `Documentation`, `Enhancement`). We can use this to auto-detect, saving agents a flag.

## Your Mission

### Phase 1: Tests (TDD)
Write tests for the auto-detection logic. The preflight script is bash, so tests should go in `tests/test_preflight_auto_type.py` using subprocess calls or by testing a helper function.

**Recommended approach**: Since the auto-type logic is a small bash snippet, the cleanest test strategy is:
- Create a test that runs the preflight script with a mock task file and verifies the `MODE:` output line
- Use `--task` to point at a temp task file with known `**Type**` values
- The script will fail on Gates 1-7 (no PR context), but it prints `MODE:` before any gates run — that's what we test

### Phase 2: Implementation
Insert the auto-detection block in `scripts/core/preflight-check.sh` between the task-ID derivation (line ~145) and the existing type validation/auto-detection (line ~186).

**Exact insertion point** — after line 145 (`fi` closing the task-ID derivation) and before line 186 (`if [ -n "$TASK_TYPE" ]; then`):

```bash
# ─── Auto-detect task type from task spec ────────────────────────────
# Priority: explicit --type > task spec **Type** field > code-changes heuristic
if [ -z "$TASK_TYPE" ]; then
    TASK_FILE_FOR_TYPE=$(find delegation/tasks -name "${TASK_ID}-*" -o -name "${TASK_ID}.*" 2>/dev/null | head -1 || true)
    if [ -n "$TASK_FILE_FOR_TYPE" ]; then
        SPEC_TYPE=$(grep '^\*\*Type\*\*:' "$TASK_FILE_FOR_TYPE" | sed 's/.*: *//')
        case "$SPEC_TYPE" in
            "Upstream Sync") TASK_TYPE="sync" ;;
            "Documentation") TASK_TYPE="docs" ;;
            # All other values (Enhancement, Bug Fix, etc.) fall through
            # to the code-changes heuristic below
        esac
    fi
fi
```

**Key design decisions**:
1. **Variable name**: Use `TASK_FILE_FOR_TYPE` to avoid colliding with `TASK_FILE` used in Gate 7 (which only searches `3-in-progress`/`4-in-review`)
2. **Find scope**: Search all of `delegation/tasks/` (not just specific status folders) — the task could be in any folder when preflight runs
3. **No default `code`**: If spec type is `Enhancement` or anything unmapped, leave `TASK_TYPE` empty so the existing code-changes heuristic runs. Only set it for types that map to non-default modes
4. **Explicit `--type` wins**: The `if [ -z "$TASK_TYPE" ]` guard ensures the flag always overrides

### Phase 3: Verification
- Run `./scripts/core/ci-check.sh` to verify no regressions
- Test manually with a task file that has `**Type**: Upstream Sync` and verify `MODE:sync`
- Test with explicit `--type code` override and verify it takes precedence

## Acceptance Criteria (Must Have)

- [ ] **Auto-detect**: Preflight reads `**Type**` from task file when `--type` is not provided
- [ ] **Override**: Explicit `--type` flag overrides auto-detection
- [ ] **Fallback**: Falls back to code-changes heuristic for unmapped type values
- [ ] **No regression**: Existing behavior unchanged when `--type` is provided or no task file found
- [ ] **Tests**: At least 3 test cases (auto-detect sync, auto-detect docs, explicit override)
- [ ] **CI passes**: `./scripts/core/ci-check.sh` green

## Success Metrics

**Quantitative**:
- 3+ test cases covering auto-detection scenarios
- 0 regressions in existing preflight behavior
- CI green

**Qualitative**:
- Agents no longer need to remember `--type` for sync/docs tasks
- Code is clean, minimal, and well-commented

## Resources for Implementation

- **Preflight script**: `scripts/core/preflight-check.sh` (lines 186-203 = current auto-detect)
- **Task spec example**: `delegation/tasks/2-todo/ADV-0062-preflight-auto-type-from-task-spec.md` (has `**Type**: Enhancement`)
- **ADV-0060 PR**: PR #52 (introduced task-type modes)
- **Patterns**: `.agent-context/patterns.yml` (check before writing utilities)

## Time Estimate

**Estimated**: 30-45 minutes
- Tests: 15 min
- Implementation: 10 min
- Verification: 5-10 min

## Starting Point

1. Create feature branch: `git checkout -b feature/ADV-0062-preflight-auto-type`
2. Start task: `./scripts/core/project start ADV-0062`
3. Read `scripts/core/preflight-check.sh` lines 130-205 (the section between task-ID derivation and gate 1)
4. Write tests first, then implement

## Success Looks Like

Running `./scripts/core/preflight-check.sh --task ADV-0062` (without `--type`) on a task spec with `**Type**: Upstream Sync` prints `MODE:sync` instead of requiring `--type sync`.

---

**Task File**: `delegation/tasks/2-todo/ADV-0062-preflight-auto-type-from-task-spec.md`
**Handoff Date**: 2026-03-18
**Coordinator**: Planner
