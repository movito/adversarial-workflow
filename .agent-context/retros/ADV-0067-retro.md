## ADV-0067 — Fix Pre-Existing CLI Issues (PR #63)

**Date**: 2026-04-13
**Agent**: feature-developer-v5
**Scorecard**: 4 threads, 0 regressions, 2 fix rounds, 3 commits

### What Worked

1. **Task spec precision saved time** — The handoff file pinpointed exact line numbers and the target pattern (`review()` lines 1861-1869). No exploration needed; went straight to implementation.
2. **TDD caught the validate() bug immediately** — Writing `validate("")` test first confirmed the IndexError crash before any code change. The red-green cycle was textbook clean.
3. **Bot findings were genuinely useful** — Both BugBot and CodeRabbit independently identified that `run_evaluator()` returns 0 for UNKNOWN verdicts and cancellations, not just APPROVED. This was a real semantic bug the task spec didn't anticipate.
4. **Dead code cleanup in round 2 was thorough** — Bots caught that removing the verdict block orphaned 4 helper functions and `import re`. Cleaning all of them in one commit was cleaner than leaving them for a separate task.

### What Was Surprising

1. **Bot-watcher agent type doesn't exist** — The workflow references a `bot-watcher` subagent type but it's not in the available agent list. Had to fall back to `ci-checker` which worked fine but required more prompt engineering.
2. **Scope grew from ~55 lines removed to ~420 lines removed** — The task spec estimated "~55 lines removed, ~10 added" but the cascading dead code cleanup (4 functions + their tests + `import re`) nearly 8x'd the deletion count. The spec's Step 4 mentioned this but didn't account for it in the estimate.
3. **Both bots auto-resolved their own threads** — After pushing the fix commit, threads were already resolved before I could manually resolve them. This is a nice ergonomic feature.

### What Should Change

1. **Task specs should account for cascading cleanup** — When a spec says "delete block X", the estimate should include all orphaned code that block X was the sole caller of. ADV-0067 estimated 2 hours but the cleanup cascade was straightforward and added minimal time.
2. **Add `run_evaluator()` return value semantics to patterns.yml** — The fact that `run_evaluator()` returns 0 for both APPROVED and UNKNOWN verdicts is a footgun. Document this contract so future code that calls `run_evaluator()` doesn't assume 0 means "approved".
3. **Register `bot-watcher` as an actual agent type or update workflow docs** — The feature-developer-v5 workflow references `bot-watcher` as a subagent_type but it doesn't exist. Either create it or update the workflow to use `ci-checker`.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Document `run_evaluator()` return value semantics in `patterns.yml` (0 = pass/unknown, 1 = revision/rejected)
- [ ] Update feature-developer-v5 workflow to reference `ci-checker` instead of `bot-watcher`
- [ ] Consider whether `run_evaluator()` should distinguish APPROVED from UNKNOWN at the return-code level
