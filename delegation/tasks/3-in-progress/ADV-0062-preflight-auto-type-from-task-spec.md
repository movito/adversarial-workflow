# ADV-0062: Preflight Auto-Detection from Task Spec Type Field

**Status**: In Progress
**Priority**: Low
**Type**: Enhancement
**Estimated Effort**: 30 minutes
**Created**: 2026-03-17
**Depends On**: ADV-0060

## Summary

Teach `preflight-check.sh` to auto-detect `--type` from the task spec's existing
`**Type**` frontmatter field, so agents don't need to remember to pass `--type`
manually.

## Proposed Mapping

| Task `**Type**` value | Preflight mode |
|---|---|
| `Upstream Sync` | `sync` |
| `Documentation` | `docs` |
| Everything else | `code` |

## Implementation

When `--type` is not provided and `--task` resolves to a task file:

```bash
if [ -z "$TASK_TYPE" ] && [ -n "$TASK_FILE" ]; then
    SPEC_TYPE=$(grep '^\*\*Type\*\*:' "$TASK_FILE" | sed 's/.*: *//')
    case "$SPEC_TYPE" in
        "Upstream Sync") TASK_TYPE="sync" ;;
        "Documentation") TASK_TYPE="docs" ;;
        *) TASK_TYPE="code" ;;
    esac
fi
```

The explicit `--type` flag remains as an override.

## Acceptance Criteria

- [ ] Preflight reads `**Type**` from task file when `--type` is not provided
- [ ] Explicit `--type` flag overrides auto-detection
- [ ] Falls back to `code` for unknown type values
- [ ] No regression when `--type` is provided or no task file found

## Notes

- Originated from ADV-0060 retro proposal #2
- Uses existing `**Type**` field — no task template changes needed
- Alternative considered: adding a new `**Preflight**:` frontmatter field. Rejected
  as unnecessary — `**Type**` already carries the information.
