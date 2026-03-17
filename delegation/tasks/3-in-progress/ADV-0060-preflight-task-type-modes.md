# ADV-0060: Preflight Task-Type Modes

**Status**: In Progress
**Priority**: Medium
**Type**: Enhancement
**Estimated Effort**: 1-2 hours
**Created**: 2026-03-15
**Depends On**: ADV-0058
**Part Of**: Quality Gate Alignment (ADV-0058, ADV-0059, ADV-0060)

## Architectural Context

Layer 4 (preflight-check.sh) is the workflow gate that checks all 7 conditions
before a PR goes to human review. Currently it applies all 7 gates uniformly
regardless of task type, causing false failures for docs-only and upstream sync
tasks.

**Evidence**: 3 of 6 retros flagged this:
- ADV-0041: "Gate 1 (CI) should pass when Gates 2/3 detect no code changes"
- ADV-0043: "sync tasks should skip spec-check/evaluator gates"
- ADV-0046: "doesn't account for docs-only tasks that skip evaluation"

## Current Behavior

| Gate | Description | Docs/Sync tasks |
|------|-------------|-----------------|
| 1. CI green | GH Actions passing | **FAIL** — no workflow triggered (no code changes) |
| 2. CodeRabbit reviewed | Bot reviewed code | PASS — auto-detected via `NO_CODE_CHANGES` |
| 3. BugBot reviewed | Bot reviewed code | PASS — auto-detected via `NO_CODE_CHANGES` |
| 4. Zero unresolved threads | All threads resolved | PASS |
| 5. Evaluator review | `.agent-context/reviews/` file exists | **FAIL** — not run for docs tasks |
| 6. Review starter | `.agent-context/REVIEW-STARTER.md` exists | **FAIL** — often skipped for sync |
| 7. Task in correct folder | `3-in-progress` or `4-in-review` | PASS |

Gates 1, 5, and 6 always fail for non-code tasks, making preflight unusable for
~40% of our tasks (6 of 15 recent tasks were docs/sync).

## Proposed Behavior

Add a `--type` flag with three modes:

```bash
# Default — all 7 gates (for feature/bug-fix tasks)
./scripts/core/preflight-check.sh

# Docs mode — skip CI + evaluator + review starter
./scripts/core/preflight-check.sh --type docs

# Sync mode — skip evaluator + review starter (CI still required if code changes)
./scripts/core/preflight-check.sh --type sync
```

### Gate matrix by type

| Gate | `code` (default) | `docs` | `sync` |
|------|-------------------|--------|--------|
| 1. CI green | Required | **Skip** | Auto (skip if no code changes) |
| 2. CodeRabbit | Required | Skip if no code | Skip if no code |
| 3. BugBot | Required | Skip if no code | Skip if no code |
| 4. Threads | Required | Required | Required |
| 5. Evaluator | Required | **Skip** | **Skip** |
| 6. Review starter | Required | **Skip** | **Skip** |
| 7. Task folder | Required | Required | Required |

### Auto-detection (optional, nice-to-have)

If `--type` is not provided, the script could auto-detect based on changed files:

```bash
CODE_FILES=$(git diff --name-only origin/main...HEAD -- \
    ':!*.md' ':!.agent-context/' ':!delegation/' 2>/dev/null)

if [ -z "$CODE_FILES" ]; then
    TYPE="docs"  # No code changes → docs mode
fi
```

This would make `--type` optional for the common case.

### Output format

Skipped gates should report clearly:

```
GATE:1:CI:SKIP:docs mode — no CI required
GATE:5:Evaluator:SKIP:docs mode — evaluator not required
```

The exit code should be 0 if all non-skipped gates pass.

## Acceptance Criteria

- [ ] `--type docs` skips gates 1, 5, 6
- [ ] `--type sync` skips gates 5, 6; auto-handles gate 1 based on code changes
- [ ] `--type code` (or no flag) behaves exactly as today (no regression)
- [ ] Skipped gates report `SKIP` status with reason
- [ ] Exit code 0 when all non-skipped gates pass
- [ ] `--help` documents the `--type` flag and modes
- [ ] Gate 1 uses existing `NO_CODE_CHANGES` detection for `sync` mode

## Should Have

- [ ] Auto-detection of task type when `--type` is omitted
- [ ] `/preflight` skill updated to pass `--type` when task is known to be docs/sync

## Backward Compatibility

- No `--type` flag = `code` mode = exact current behavior. Zero regression risk.
- Scripts that call `preflight-check.sh` without `--type` continue to work unchanged.
- The `/preflight` skill (`.claude/commands/preflight.md`) should be updated to
  document the `--type` option and suggest it for docs/sync tasks.

## Files to Modify

1. `scripts/core/preflight-check.sh` — add `--type` flag, gate skip logic
2. `.claude/commands/preflight.md` or `.claude/skills/*/SKILL.md` — document `--type` usage

## Error Handling

Invalid `--type` values should produce a clear error and exit 1:

```bash
case "$TYPE" in
    code|docs|sync) ;;
    *)
        echo "ERROR: Invalid --type '$TYPE'. Must be: code, docs, or sync"
        exit 1
        ;;
esac
```

If auto-detection is implemented and fails (can't determine file changes), default
to `code` mode (strictest). Never silently skip gates.

## Testing Strategy

Test manually on existing PRs:
1. Run with `--type code` on a feature PR — all 7 gates checked (no regression)
2. Run with `--type docs` on a docs PR — gates 1, 5, 6 show SKIP
3. Run with `--type sync` on a sync PR — gates 5, 6 show SKIP, gate 1 auto-detects
4. Run with `--type invalid` — error message, exit 1
5. Run with no `--type` flag — behaves exactly as today

## Implementation Sketch

Add `--type` to the argument parser (after existing `--task` case):

```bash
--type)
    if [ -z "${2:-}" ] || [[ "$2" == -* ]]; then
        echo "ERROR: --type requires a value (code, docs, sync)"
        exit 1
    fi
    TASK_TYPE="$2"
    shift 2
    ;;
```

Default: `TASK_TYPE="code"`

Before each gate, check skip conditions:

```bash
# Gate 1
if [ "$TASK_TYPE" = "docs" ]; then
    echo "GATE:1:CI:SKIP:docs mode — no CI required"
elif [ "$TASK_TYPE" = "sync" ] && [ "$NO_CODE_CHANGES" = true ]; then
    echo "GATE:1:CI:SKIP:sync mode — no code changes, CI not required"
else
    # ... existing gate 1 logic ...
fi
```

## Notes

- This depends on ADV-0058 (ci-check.sh must be reliable first)
- ADV-0059 (GH Actions paths) may change when Gate 1 triggers, but the preflight
  logic is independent — it checks whether a run exists and passed
- The `NO_CODE_CHANGES` detection already works for gates 2-3; this task extends
  it to gate 1 and adds the type-based skip for gates 5-6
- Consider whether `--type` should also affect thread resolution (gate 4) — probably
  not, since even docs PRs get bot comments that should be resolved
- Update `--help` output to document the new flag (add to the Options section and
  show gate behavior per type)
