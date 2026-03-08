# ADV-0040: Upstream Sync — Slash Commands

**Status**: In Progress
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 15 minutes
**Created**: 2026-03-07
**Updated**: 2026-03-08 (source changed to dispatch-kit v0.4.2)
**Parent**: ADV-0039

## Summary

Copy all slash commands from dispatch-kit v0.4.2 into `.claude/commands/`.
These are additive — no existing files to conflict with. These commands enable
efficient bot triage, CI checking, and task management workflows.

## Scope

### Files to Copy (from dispatch-kit `.claude/commands/`)

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

### Integration Notes

- Copy verbatim from dispatch-kit — no modifications needed
- These commands reference agent workflows that will exist after the full sync
- `start-task.md` includes preflight checks (clean working tree, task exists)

## Source

dispatch-kit v0.4.2: `.claude/commands/` directory
Local path: `/Users/broadcaster_three/Github/dispatch-kit/.claude/commands/`

## PR Template

```
Title: sync: Add slash commands from dispatch-kit (ADV-0040)

Body:
## Summary
Copies 11 slash commands from dispatch-kit v0.4.2. Enables /check-bots,
/triage-threads, /check-ci, /start-task, and other workflow commands.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] All 11 command files copied to `.claude/commands/`
- [ ] `start-task.md` includes preflight checks
- [ ] CI passes
- [ ] PR created and merged
