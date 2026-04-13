## ADV-0066 — Remove Aider Remnants from Codebase (PR #61)

**Date**: 2026-04-13
**Agent**: feature-developer-v5
**Scorecard**: 15 threads, 0 regressions, 4 fix rounds, 6 commits

### What Worked

1. **Systematic file deletion first** — Removing 16 dead files early gave a clean baseline. The remaining work was focused on live code updates without confusion about which scripts still existed.
2. **run_evaluator() integration pattern** — Rewiring evaluate(), review(), validate() to use the new evaluator runner was clean. The builtin evaluator config pattern (`BUILTIN_EVALUATORS.get("evaluate")`) is simple and maintainable.
3. **Log file selection by output_suffix** — CodeRabbit correctly flagged the race-prone "newest *.md" glob. The fix (filtering by `builtin_config.output_suffix`) is more reliable and was straightforward to implement.
4. **Pre-existing issues capture** — Creating `.agent-context/ADV-0066-preexisting-issues.md` per user request cleanly separates "found during this task" from "introduced by this task."

### What Was Surprising

1. **CodeRabbit false positives on Python imports** — Two threads were wrong: one claimed `BUILTIN_EVALUATORS` didn't have a "review" key (it does, line 226), another said patching at the source module wouldn't work for local imports (it does, because local imports re-execute each call). Both required manual verification to dismiss.
2. **Test mock correctness surfaced by bots** — The `glob.glob` returning `[]` bypass (thread round 4) was a genuine issue — tests passed but didn't exercise the validation path. This is a subtle class of test bug that's easy to miss during initial implementation.
3. **4 bot rounds** — For a cleanup/deletion task, 4 rounds of bot triage was more than expected. Most rounds had valid findings though, so the time was well spent.

### What Should Change

1. **Add glob mock audit to self-review checklist** — When a test mocks `glob.glob` to return `[]`, explicitly verify this doesn't skip the path being tested. Add to `.agent-context/workflows/TESTING-WORKFLOW.md`.
2. **Evaluator key registry documentation** — The confusion between "review" (builtin key) and "code-review" (custom evaluator name) suggests the naming convention needs documentation. A comment in `builtins.py` or entry in `patterns.yml` would prevent future confusion.
3. **code-reviewer-fast evaluator accuracy** — The evaluator returned FAIL with 7 findings, but 5 were false positives (code already handled FileNotFoundError, returncode checks, file existence). The evaluator only sees the input summary, not the actual code, which limits its ability to verify existing guards.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Add glob mock audit pattern to TESTING-WORKFLOW.md
- [ ] Document builtin evaluator key naming convention (builtins.py or patterns.yml)
- [ ] Create follow-up task from `.agent-context/ADV-0066-preexisting-issues.md` (dead verdict handling, empty test_command edge case)
- [ ] Consider improving code-reviewer-fast to accept actual code diffs, not just summaries
