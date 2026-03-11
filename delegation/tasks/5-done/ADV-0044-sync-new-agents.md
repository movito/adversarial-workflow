# ADV-0044: Upstream Sync — New Agents

**Status**: Done
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 15 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Add new agent definitions from upstream that don't exist in our repo yet.

## Scope

### Files to Add (from upstream `.claude/agents/`)

1. **bootstrap.md** — Bootstrap/setup agent for new projects
2. **powertest-runner.md** — Comprehensive testing and TDD specialist

### Required Fix: powertest-runner.md

BugBot found that the task lifecycle section was missing the branch creation
step. The "Starting a Task" section must include `git checkout -b` as the
first mandatory step before `./scripts/core/project start`.

Also needs Serena project name set to `adversarial-workflow`:
```python
mcp__serena__activate_project("adversarial-workflow")
```

### Note on bootstrap.md

CodeRabbit flagged cross-platform `sed` issues and version hardcoding.
These are upstream concerns — copy as-is and defer to upstream for fixes.

## Source

Upstream directory: `/private/tmp/agentive-starter-kit/.claude/agents/`

## PR Template

```
Title: sync: Add bootstrap and powertest-runner agents (ADV-0044)

Body:
## Summary
Adds 2 new agent definitions from agentive-starter-kit@0c68f0f.

Integration fix: powertest-runner.md gets branch creation step
(BugBot finding) and correct Serena project name.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] bootstrap.md added to `.claude/agents/`
- [ ] powertest-runner.md added with branch creation fix
- [ ] powertest-runner.md has correct Serena project name
- [ ] CI passes
- [ ] PR created and merged
