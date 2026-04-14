# ADV-0069 Retro: Root Declutter + Manifest Upgrade

**Date**: 2026-04-14
**PR**: #65 (merged)
**Agent**: feature-developer-v5
**Duration**: ~45 min active (excluding bot wait time)
**Bot rounds**: 1 round, 2 threads (CodeRabbit + BugBot), both fixed

## What Went Well

1. **Clean execution** — housekeeping task with no code changes went smoothly. The task spec and handoff were thorough enough to execute without ambiguity.
2. **Upstream manifest cross-reference** — reading the upstream manifest directly ensured our v2.0.0 manifest matched the canonical structure, adjusted for files we actually have.
3. **Link audit was comprehensive** — grep caught all active references that needed updating; historical references correctly left as-is.

## What Could Be Better

1. **`project move` + git staging gap** — the `project move` script moves the filesystem file but doesn't `git rm` the old path when you stage the new file separately. BugBot caught a duplicate task file in two status directories. **Lesson**: after `project move`, always `git rm` the old path or use `git mv` instead.
2. **`wrap-up.md` in manifest** — upstream doesn't list `wrap-up.md` in `commands_optional` but we have it. Added it to our manifest since we use it. This divergence from upstream should be documented if it matters for future syncs.

## Learnings for Future Tasks

- For file-move PRs, always verify `git ls-files` after filesystem moves to catch tracking mismatches.
- The `--type docs` preflight mode correctly skips CI/evaluator/review-starter gates for housekeeping tasks.

## Metrics

| Metric | Value |
|--------|-------|
| Commits | 4 |
| Files changed | 19 |
| Bot threads | 2 (2 fixed, 0 unresolved) |
| Root files | 15 → 9 |
| Manifest version | 1.2.0 → 2.0.0 |
