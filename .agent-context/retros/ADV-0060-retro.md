## ADV-0060 — Preflight Task-Type Modes (PR #52)

**Date**: 2026-03-17
**Agent**: feature-developer-v3
**Scorecard**: 3 threads, 0 regressions, 2 fix rounds, 4 commits

### What Worked

1. **Task spec with implementation sketch** — The spec included exact argument parsing code, gate skip patterns, and a gate matrix. Implementation was almost copy-paste from the spec, leading to a very fast first pass.
2. **Self-testing the feature during preflight** — Running `./scripts/core/preflight-check.sh --type sync` on this PR itself validated the feature end-to-end and demonstrated the SKIP output format working correctly.
3. **Catching both error format instances** — When fixing the `ERROR:` spacing inconsistency from round 1, proactively grepped for all instances and fixed both (arg parser + validation), preventing a follow-up thread.

### What Was Surprising

1. **Only 3 threads total** — Previous PRs in this trilogy (ADV-0058: 3 threads, ADV-0059: 7 threads) set expectations higher. The shell-only scope and clear spec likely reduced bot surface area.
2. **CodeRabbit flagged reverted-code edge case** — The `NO_CODE_CHANGES` history-based detection concern (thread #2, Major severity) was technically valid but practically irrelevant. Good reminder that bot severity labels don't always correlate with real-world impact.

### What Should Change

1. **Standardize error message format in templates** — The `ERROR:` vs `ERROR: ` inconsistency was inherited from the original script. The dispatch-kit template should pick one format and document it so downstream scripts don't diverge.
2. **Task type should be specifiable in task spec frontmatter** — If task files had a `type: docs|sync|code` field, the preflight auto-detection wouldn't need to guess. This would also help the planner assign the right workflow gates upfront.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Consider adding `type:` field to task spec template for preflight auto-detection
- [ ] Standardize `ERROR:` message format in dispatch-kit script templates
