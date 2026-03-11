# ADV-0041: Upstream Sync — Skills

**Status**: In Progress
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 20 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Copy all new skill directories from upstream agentive-starter-kit into
`.claude/skills/`. One fix required: the pre-implementation skill is missing
4 GitHub Actions conclusion values.

## Scope

### Directories to Copy (from upstream `.claude/skills/`)

1. `bot-triage/SKILL.md`
2. `code-review-evaluator/SKILL.md`
3. `pre-implementation/SKILL.md`
4. `review-handoff/SKILL.md`
5. `self-review/SKILL.md`

### Required Fix (Our Integration)

In `pre-implementation/SKILL.md`, the GitHub Actions conclusion values list
is incomplete. The upstream version only lists 4 values:

```
conclusion: "success" | "failure" | "cancelled" | "skipped" | null
```

Must be expanded to the full 8:

```
conclusion: "success" | "failure" | "cancelled" | "skipped" | "action_required" | "neutral" | "stale" | "timed_out" | null
```

This was identified as a Critical finding by CodeRabbit on PR #34.

## Source

Upstream directory: `/private/tmp/agentive-starter-kit/.claude/skills/`

## PR Template

```
Title: sync: Add upstream skills with CI conclusion fix (ADV-0041)

Body:
## Summary
Copies 5 skill directories from agentive-starter-kit@0c68f0f.

Includes one integration fix: adds 4 missing GitHub Actions conclusion
values to pre-implementation/SKILL.md (action_required, neutral, stale,
timed_out). This was a Critical CodeRabbit finding on #34.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] All 5 skill directories copied to `.claude/skills/`
- [ ] pre-implementation/SKILL.md has all 8 conclusion values + null
- [ ] CI passes
- [ ] PR created and merged
