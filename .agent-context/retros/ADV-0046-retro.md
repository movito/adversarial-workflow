## ADV-0046 — Upstream Sync: CLAUDE.md & Documentation (PR #49)

**Date**: 2026-03-15
**Agent**: feature-developer-v3
**Scorecard**: 2 threads, 0 regressions, 2 fix rounds, 2 commits

### What Worked

1. **Handoff file was comprehensive** — The detailed table of what the sync branch got wrong (Black→Ruff, scripts/→scripts/core/) meant zero research time. Every fix was pre-identified.
2. **Batch approach to ADR-0013 updates** — Updating all comparison matrix rows in one pass was efficient. Using the task-to-PR mapping from memory made the sync history table accurate on first try.
3. **Fast bot turnaround** — Both CodeRabbit findings were genuinely useful (missing CLAUDE.md in path filter, missing PR number). Fixed in one commit, clean rescan.

### What Was Surprising

1. **Preflight script false negatives** — Gate 1 (CI green) failed because the script looks for GitHub Actions workflow runs, but this repo uses CodeRabbit/BugBot checks instead. Gate 5 (evaluator) and Gate 6 (review starter) also failed but are sequencing/scope issues. The preflight script doesn't account for docs-only tasks that skip evaluation.
2. **ci-check.sh exit code 1 from tests/ DK002 violations** — The local CI script runs pattern_lint on all Python files including tests/, but pre-commit scopes it to `adversarial_workflow/` only. This discrepancy has been a known issue across multiple tasks but hasn't been fixed.

### What Should Change

1. **Preflight script should support skip flags** — Allow `--skip-evaluator` or detect docs-only PRs (no .py changes) and auto-skip Gate 5. Would eliminate false negatives on tasks like this one.
2. **ci-check.sh should scope pattern_lint to adversarial_workflow/** — Match the pre-commit config scope. The tests/ DK002 violations cause a misleading exit code 1 on every run.
3. **Task spec should include PR number placeholder** — The ADR sync history table used `—` for ADV-0046's PR number, which CodeRabbit correctly flagged. Future sync tasks should note "fill in PR number after creation."

### Permission Prompts Hit

None. `SKIP_TESTS=1 git commit` worked without blocks. All `gh` commands auto-approved.

### Process Actions Taken

- [ ] Fix ci-check.sh to scope pattern_lint to adversarial_workflow/ (matches pre-commit)
- [ ] Add --skip-evaluator flag or docs-only detection to preflight-check.sh
- [ ] Move ADV-0046 to 5-done after merge confirmation
- [ ] Move parent ADV-0039 to 5-done (epic complete)
