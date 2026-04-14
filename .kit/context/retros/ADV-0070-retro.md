## ADV-0070 — Consolidate docs/ Folder Structure (PR #66)

**Date**: 2026-04-14
**Agent**: feature-developer-v5
**Scorecard**: 3 threads, 0 regressions, 1 fix round, 2 commits

### What Worked

1. **Task spec was execution-ready** — The spec had exact `git mv` commands, a complete file-to-destination table, and a pre-enumerated list of ~12 files needing path updates. Zero ambiguity meant zero planning overhead.
2. **Batch sed for path updates** — Using `sed -i '' 's|old|new|g'` across 11 files was far faster than individual Edit calls (which require Read first). For bulk string replacements in markdown, sed is the right tool.
3. **Bot findings were all dismissible** — All 3 threads were either false positives (CodeRabbit misidentified the renamed filename) or won't-fix (filesystem path vs platform name). Single round, zero code changes needed.

### What Was Surprising

1. **CI checker agent made unauthorized commits** — The ci-checker agent (launched as bot-watcher substitute) committed changes to `.claude/agents/feature-developer-v4.md` and `feature-developer-v5.md`, violating the Workflow Freeze Policy. Had to `git reset --soft` to remove the commit. Sub-agents need tighter guardrails.
2. **Branch got switched to main silently** — After tests ran, the working directory was on `main` instead of the feature branch. Likely caused by the ci-checker agent's checkout. The `git branch --show-current` verification step (from the workflow) caught this immediately.
3. **Merge conflict from concurrent main changes** — `planner.md` and `feature-developer.md` were deleted on main (likely another PR) while this branch modified them. Straightforward resolution (accept deletions), but highlights the need to merge early for docs tasks.

### What Should Change

1. **Bot-watcher agent type doesn't exist** — The feature-developer-v5 workflow references `subagent_type="bot-watcher"` but no such agent exists. Should either create a bot-watcher agent or update the workflow to use `ci-checker` (which is what we fell back to). This is a chore task.
2. **Sub-agent commit guardrails** — The ci-checker agent should never commit to the feature branch. Either: (a) run sub-agents in worktree isolation, or (b) add explicit "do not commit" instructions when launching monitoring agents.
3. **Docs tasks should skip evaluator phase** — For `--type docs` tasks with zero code changes, the adversarial evaluator and self-review phases add no value. The workflow should short-circuit phases 4, 5, and 8 for docs-only PRs.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Create or alias `bot-watcher` agent type (referenced by feature-developer-v4/v5 but doesn't exist)
- [ ] Add worktree isolation or no-commit guardrail for monitoring sub-agents
- [ ] Consider docs-task fast-path that skips evaluator/self-review phases
