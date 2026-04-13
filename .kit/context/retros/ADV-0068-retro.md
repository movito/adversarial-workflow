## ADV-0068 — Migrate to .kit/ Directory Layout (PR #64)

**Date**: 2026-04-13
**Agent**: feature-developer-v5
**Scorecard**: 13 threads (excl. summary), 0 regressions, 2 fix rounds, 5 commits

### What Worked

1. **Python bulk replacement script** — Using a Python script instead of raw sed for path replacements gave precise control over replacement order (most-specific-first) and clear reporting of which files changed. Caught 58 files in one pass.
2. **Careful CLI-behavior separation** — Identifying that `README.md`, `QUICK_START.md`, `SETUP.md`, and `docs/` describe CLI behavior (which still uses `.agent-context/`/`delegation/`) prevented incorrect rewrites. Reverting those early saved a bot round.
3. **`git mv` for history preservation** — All file moves used `git mv`, confirmed by GitHub showing `rename` status in the diff. Only 2 files were untracked (ADV-0068 handoff, ADV-0062 task) and handled via plain `mv`.
4. **Handoff file was comprehensive** — The ADV-0068 handoff listed exact line numbers in `scripts/core/project` (67, 130, 150, 1062), which caught the 3 `Path()` concatenation refs that the string-based bulk replacement missed.

### What Was Surprising

1. **`git add -A` committed stale files** — `.aider.*`, `.dispatch/`, and `planner2.md` were untracked and got swept up. Required a follow-up commit to remove them and update `.gitignore`. Should have used specific file adds.
2. **Blind sed on `active/` paths** — The bulk replacement converted `delegation/tasks/active/` to `.kit/tasks/active/`, but no `active/` folder exists under `.kit/tasks/` (project uses numbered folders). BugBot caught this — 4 workflow files affected.
3. **CodeRabbit found stale refs inside moved files** — The bulk script only targeted `.claude/`, `scripts/`, and root docs, but skipped `.kit/context/` root files like `agent-handoffs.json` and `README.md`. These needed a second pass.

### What Should Change

1. **Bulk replacement should include destination directories** — The migration script excluded `.kit/` from its target list, but files moved INTO `.kit/` (agent-handoffs.json, README.md, workflows, templates) also needed path updates. Future migrations should run the replacement script on the destination after moves.
2. **Add `.aider.*` and `.dispatch/` to `.gitignore` in upstream kit** — These are common dev artifacts. The `.gitignore` template should include them by default so they're never accidentally committed.
3. **`git add` should be explicit, not `-A`** — For large migrations, stage files by category (`git add .kit/` then `git add .claude/` etc.) rather than using `git add -A` which picks up untracked junk.

### Permission Prompts Hit

1. `./scripts/core/wait-for-bots.sh 64` — user rejected (wanted to proceed to fixing directly). No delay, user redirected immediately.
2. No other permission blocks during the session.

### Process Actions Taken

- [ ] Add `.aider.*` and `.dispatch/` to upstream kit `.gitignore` template
- [ ] Consider adding `active/` → numbered-folder mapping to migration playbook for future projects
- [ ] Update migration playbook: run bulk replacement on destination dirs after moves, not just source-adjacent files
