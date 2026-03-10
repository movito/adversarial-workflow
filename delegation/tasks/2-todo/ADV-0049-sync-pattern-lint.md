# ADV-0049: Upstream Sync — pattern_lint + Tests

**Status**: Todo
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 20 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Add the pattern_lint defensive coding linter and its test suite from upstream.
Includes one critical fix for chained `in` comparison handling (already
developed in the monolithic PR).

## Scope

### Files to Add

1. `scripts/core/pattern_lint.py` — Defensive coding pattern linter (DK001-DK004)
2. `tests/test_pattern_lint.py` — Test suite (31 tests)

### Critical Fix Required

CodeRabbit identified a real bug in the DK003 check: chained `in` comparisons
like `a in b in c` are handled incorrectly. The loop always reuses `node.left`,
causing it to check `(a in b)` and then `(a in c)` instead of `(a in b)` and
`(b in c)`.

**Fix** (already developed, commit 4e328e2 on the sync branch):

Track `current_left` through the loop:
```python
current_left = node.left
for op, comparator in zip(node.ops, node.comparators, strict=False):
    if not isinstance(op, ast.In):
        current_left = comparator
        continue
    # ... existing logic, but use current_left instead of node.left ...
    left = current_left
    left_name = _extract_name(left)
    # ... rest of checks ...
    current_left = comparator
```

### Test Notes

- The test file uses `sys.path.insert` to import pattern_lint — this is
  acceptable since `scripts/` is not a Python package
- Do NOT copy upstream's `tests/conftest.py` — it would overwrite our
  project-specific fixtures
- Do NOT copy `tests/test_create_agent.py` or `tests/test_project_script.py` —
  they depend on upstream fixtures not present in our test suite

## Source

- Upstream: `agentive-starter-kit/scripts/core/pattern_lint.py`
- Fix reference: commit 4e328e2 on branch `sync/adv-0039-upstream-sync`

## PR Template

```
Title: sync: Add pattern_lint linter with chained-in fix (ADV-0049)

Body:
## Summary
Adds the DK001-DK004 defensive coding pattern linter and 31 tests.

Includes critical fix: DK003 now correctly handles chained `in`
comparisons by tracking current_left through the loop.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] pattern_lint.py added to `scripts/core/`
- [ ] test_pattern_lint.py added to `tests/`
- [ ] Chained `in` comparison fix applied (current_left tracking)
- [ ] All 31 tests pass
- [ ] conftest.py NOT overwritten
- [ ] CI passes
- [ ] PR created and merged
