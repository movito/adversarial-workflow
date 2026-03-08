# ADV-0040 Handoff: Upstream Sync — Slash Commands

**Task File**: `delegation/tasks/2-todo/ADV-0040-sync-slash-commands.md`
**Agent**: feature-developer-v3
**Created**: 2026-03-08

## What You're Doing

Copy 10 slash command files from the upstream agentive-starter-kit into
`.claude/commands/`. These are additive — no existing files to conflict with.

## Source Location

The upstream files are at: `/private/tmp/agentive-starter-kit/.claude/commands/`

All 10 files exist and are ready to copy:
1. `check-bots.md`
2. `check-ci.md`
3. `check-spec.md`
4. `commit-push-pr.md`
5. `preflight.md`
6. `retro.md`
7. `start-task.md`
8. `status.md`
9. `triage-threads.md`
10. `wait-for-bots.md`

## Implementation

This is a straightforward copy operation:

```bash
cp /private/tmp/agentive-starter-kit/.claude/commands/*.md .claude/commands/
```

## Verification

After copying:

1. Confirm all 10 files exist in `.claude/commands/`
2. Verify `start-task.md` includes the preflight checks (Step 2 in the file
   should have "Verify not already on a feature branch" and "Verify task exists
   in 2-todo/")
3. Run CI: `pytest tests/ -v`

## PR Details

- **Branch**: `feature/ADV-0040-sync-slash-commands`
- **Title**: `sync: Add upstream slash commands (ADV-0040)`
- **Body**: Upstream sync — copied verbatim from agentive-starter-kit@0c68f0f.
  Bot findings about these files are upstream's responsibility.
  Part of ADV-0039 (upstream sync).

## Notes

- These are markdown instruction files, not executable code — CI risk is zero
- Bot reviews may flag markdown issues in the command files. These are upstream
  authored — dismiss with "upstream sync, copied verbatim"
- The commands reference workflows/agents that will exist after the full sync.
  This is expected — they'll work once ADV-0041–0050 are merged
