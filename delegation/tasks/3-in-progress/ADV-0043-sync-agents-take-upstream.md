# ADV-0043: Upstream Sync — Agents (Take Upstream)

**Status**: In Progress
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 15 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Replace 11 agent definition files with their upstream versions. These agents
have upstream improvements (model bumps, evaluator language updates, branch
workflow enhancements) and we have no significant local customizations.

## Scope

### Files to Replace (from upstream `.claude/agents/`)

1. `AGENT-TEMPLATE.md`
2. `OPERATIONAL-RULES.md`
3. `TASK-STARTER-TEMPLATE.md`
4. `agent-creator.md`
5. `ci-checker.md`
6. `document-reviewer.md`
7. `feature-developer.md` (v1, distinct from our feature-developer-v3)
8. `onboarding.md`
9. `planner.md` (v1, distinct from our planner2)
10. `security-reviewer.md`
11. `test-runner.md`

### Integration Notes

- Copy verbatim from upstream
- These are template/reference agents — our active agents are
  feature-developer-v3, planner2, and code-reviewer (preserved in ADV-0042)
- Bot findings about markdown formatting in these files are upstream's concern

## Source

Upstream directory: `/private/tmp/agentive-starter-kit/.claude/agents/`

## PR Template

```
Title: sync: Update 11 agent definitions from upstream (ADV-0043)

Body:
## Summary
Replaces 11 agent definition files with upstream versions from
agentive-starter-kit@0c68f0f. Includes model bumps, evaluator
language updates, and branch workflow improvements.

Upstream sync — copied verbatim. Bot findings about these files
are upstream's responsibility.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] All 11 agent files replaced with upstream versions
- [ ] CI passes
- [ ] PR created and merged
