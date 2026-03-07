# ADV-0040: Upstream Sync — Slash Commands

**Status**: Todo
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 15 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Copy all new slash commands from upstream agentive-starter-kit into
`.claude/commands/`. These are additive — no existing files to conflict with.

## Scope

### Files to Copy (from upstream `.claude/commands/`)

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

### Integration Notes

- Copy verbatim from upstream — no modifications needed
- These commands reference agent workflows that will exist after the full sync
- The `start-task.md` command should include the clean working tree check
  (added in the monolithic PR)

## Source

Upstream directory: `/private/tmp/agentive-starter-kit/.claude/commands/`

## PR Template

```
Title: sync: Add upstream slash commands (ADV-0040)

Body:
## Summary
Copies 10 new slash commands from agentive-starter-kit@0c68f0f.

Upstream sync — copied verbatim. Bot findings about these files
are upstream's responsibility.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] All 10 command files copied to `.claude/commands/`
- [ ] `start-task.md` includes clean working tree check
- [ ] CI passes
- [ ] PR created and merged
