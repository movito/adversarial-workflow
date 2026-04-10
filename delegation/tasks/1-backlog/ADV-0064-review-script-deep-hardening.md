# ADV-0064: Review Script Deep Hardening

**Status**: Backlog
**Priority**: Low
**Type**: Enhancement
**Estimated Effort**: 2-3 hours
**Created**: 2026-03-21
**Origin**: ADV-0057 evaluator findings (Gemini Flash + OpenAI o1)

## Summary

During ADV-0057, two adversarial evaluators (Gemini Flash code-reviewer-fast and
OpenAI o1 code-reviewer) identified additional pre-existing robustness gaps in
`review_implementation.sh` and `cli.py`. None are bugs — all are latent edge
cases that only trigger under unusual environments or inputs.

## Issues to Address

### From Gemini Flash (code-reviewer-fast)

1. **Whitespace in config paths** (Medium)
   Config values with leading/trailing whitespace could create misnamed directories.
   Consider trimming after parsing.

2. **Ambiguous git references** (Low)
   If both a branch and tag share the same name (e.g. `main`), `git rev-parse --verify`
   may resolve to the wrong one. Consider using `refs/heads/$DEFAULT_BRANCH`.

3. **Non-fatal git warnings not surfaced** (Low)
   When `git diff` returns 0 or 1 but emits warnings to stderr, those are silently
   discarded by the CLI.

4. **Inconsistent `$TASK_FILE` quoting** (Medium)
   The validation step quotes `$TASK_FILE`, but other usages in the script may not.
   Audit all `$TASK_FILE` references for proper quoting.

### From OpenAI o1 (code-reviewer)

5. **Non-writable default directories** (Medium)
   If `.adversarial/artifacts/` or `.adversarial/logs/` exist but are read-only,
   `mkdir -p` succeeds but subsequent writes fail without a clear message.

6. **Missing git / detached HEAD** (Low)
   Script doesn't check for git availability or handle detached HEAD gracefully.

7. **Non-markdown task file** (Low)
   Script validates file existence but not file type — a binary or directory path
   could be passed.

8. **Non-standard branch names** (Low)
   Repos using branch names other than `main`/`master` (e.g. `development`) with
   no `origin/HEAD` set will hit the fallback error. (Note: ADV-0057 Fix 2 already
   reports this clearly — this is about improving the UX further.)

## Acceptance Criteria

- [ ] Config path values trimmed after parsing
- [ ] `$TASK_FILE` consistently quoted throughout script
- [ ] `mkdir -p` failures detected and reported
- [ ] Reasonable handling for detached HEAD / missing git
- [ ] Template and script remain in sync
- [ ] All existing tests pass

## Notes

- All items are pre-existing, not regressions
- Low priority — normal usage paths are unaffected
- Evaluator reviews: `.adversarial/logs/ADV-0057-review-script-robustness--code-reviewer-fast.md`
  and `.adversarial/logs/ADV-0057-review-script-robustness--code-reviewer.md`
- Items 2, 3, 6, 7, 8 are Low severity and could be deferred or dropped
