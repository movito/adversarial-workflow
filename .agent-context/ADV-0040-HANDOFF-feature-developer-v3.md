# ADV-0040 Handoff: Upstream Sync — Slash Commands

**Task File**: `delegation/tasks/2-todo/ADV-0040-sync-slash-commands.md`
**Agent**: feature-developer-v3
**Created**: 2026-03-08

## RULES — Read Before Anything Else

1. **Do NOT spawn sub-agents.** Never use the Agent/Task tool. Do all work yourself.
2. **Do NOT modify the copied files.** These are upstream-authored. Copy verbatim.
3. **First action**: Create branch and start task (see Implementation below).

## What You're Doing

Copy 11 slash command files from dispatch-kit v0.4.2 into `.claude/commands/`.
These are additive — no existing files to conflict with.

## Source Location

The upstream files are at: `/Users/broadcaster_three/Github/dispatch-kit/.claude/commands/`

All 11 files:
1. `check-bots.md` — Check bot review status on PRs
2. `check-ci.md` — Check CI/CD pipeline status
3. `check-spec.md` — Verify implementation against spec
4. `commit-push-pr.md` — Commit, push, and create PR
5. `preflight.md` — Pre-push validation checklist
6. `retro.md` — Session retrospective
7. `start-task.md` — Create branch and start a task
8. `status.md` — Show project status
9. `triage-threads.md` — Triage bot review threads on PRs
10. `wait-for-bots.md` — Wait for bot reviews to complete
11. `wrap-up.md` — Finalize session with retro and completion

## Implementation

```bash
# 1. Create feature branch
git checkout -b feature/ADV-0040-sync-slash-commands

# 2. Start the task (moves to 3-in-progress/)
./scripts/project start ADV-0040

# 3. Copy all 11 command files
cp /Users/broadcaster_three/Github/dispatch-kit/.claude/commands/*.md .claude/commands/

# 4. Verify all 11 files exist
ls -la .claude/commands/

# 5. Run CI
pytest tests/ -v
```

## Verification

After copying, confirm:

1. All 11 files exist in `.claude/commands/`
2. `start-task.md` includes preflight checks (Step 2 should have "Verify not
   already on a feature branch" and "Verify task exists in 2-todo/")
3. CI passes (`pytest tests/ -v`)

## PR Details

- **Branch**: `feature/ADV-0040-sync-slash-commands`
- **Title**: `sync: Add slash commands from dispatch-kit (ADV-0040)`
- **Body**:
  ```
  ## Summary
  Copies 11 slash commands from dispatch-kit v0.4.2. Enables /check-bots,
  /triage-threads, /check-ci, /start-task, and other workflow commands.

  These are upstream-authored markdown instruction files, copied verbatim.
  Part of ADV-0039 (upstream sync).
  ```

## Notes

- These are markdown instruction files, not executable code — CI risk is zero
- Bot reviews may flag markdown issues in the command files. These are upstream
  authored — dismiss with "upstream sync, copied verbatim"
- The commands reference workflows/agents that will exist after the full sync.
  This is expected — they'll work once ADV-0041–0050 are merged
