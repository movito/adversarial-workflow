## ADV-0058 — Fix ci-check.sh / GitHub Actions Parity (PR #50)

**Date**: 2026-03-16
**Agent**: feature-developer-v3
**Scorecard**: 3 threads, 0 regressions, 1 fix round, 4 commits

### What Worked

1. **BugBot caught a real security gap** — `SKIP_TESTS=1 *` would have bypassed all deny rules. Scoping to `SKIP_TESTS=1 git *` was the right fix. This is exactly the kind of finding that justifies the bot review gate.
2. **Splitting DK002 cleanup into ADV-0061** — Kept this PR focused on the 2-file fix instead of expanding to 34 mechanical violations across 5 files. The advisory pattern lint approach bridges the gap cleanly.
3. **Fast turnaround** — Simple task, 1 bot round, code-reviewer-fast found no issues. Total wall-clock under 45 minutes including bot review.

### What Was Surprising

1. **Memory said DK002 violations in adversarial_workflow/ were resolved — they weren't** — 34 violations still present. The memory entry was stale/wrong. This caused the task spec's assumption ("exits 0 on main") to be incorrect, requiring the advisory lint workaround.
2. **GitHub Actions didn't trigger at all** — The paths filter (`adversarial_workflow/`, `tests/`, `pyproject.toml`) excludes `scripts/` and `.claude/`. This is the exact gap ADV-0059 exists to fix, but it meant Gate 1 (CI green) was unverifiable for this PR.
3. **Pre-commit hook ran by `git commit` modified ADV-0061 task file** — The DK004 note was expanded by the hook. Minor but unexpected side effect.

### What Should Change

1. **Fix stale memory about DK002 violations** — The memory entry claiming "DK002 violations in adversarial_workflow/: resolved" is wrong. Should be updated to reflect 34 violations remain, tracked in ADV-0061.
2. **ADV-0059 should be prioritized** — Without `scripts/` in the GitHub Actions paths filter, ci-check.sh changes can't be CI-verified. This undermines the whole parity goal.
3. **Task specs should verify assumptions** — ADV-0058 assumed `adversarial_workflow/` had zero pattern lint violations. A pre-task verification step ("run the proposed command on main and check exit code") would have caught this.

### Permission Prompts Hit

None. All commands matched existing allow patterns.

### Process Actions Taken

- [ ] Update memory: DK002 violations in adversarial_workflow/ are NOT resolved (34 remain, tracked in ADV-0061)
- [ ] Prioritize ADV-0059 (GitHub Actions paths alignment) as next task in trilogy
- [ ] Consider adding "verify assumptions on main" as a pre-implementation checklist item
