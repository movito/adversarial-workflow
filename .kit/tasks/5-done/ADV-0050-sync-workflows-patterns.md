# ADV-0050: Upstream Sync — Workflows & Patterns

**Status**: Done
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 15 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Add new workflow documentation and the patterns.yml defensive coding reference
from upstream.

## Scope

### Files to Add (from upstream `.agent-context/workflows/`)

1. `EVALUATOR-LIBRARY-WORKFLOW.md` — How to use library evaluators
2. `PR-SIZE-WORKFLOW.md` — PR size management guidelines
3. `RESEARCH-QUALITY-STANDARDS.md` — Research document quality standards
4. `WORKFLOW-FREEZE-POLICY.md` — When and how to freeze workflow changes

### Files to Add (from upstream `.agent-context/`)

5. `patterns.yml` — Defensive coding patterns reference (DK001-DK004 rules,
   error strategies by layer, identifier comparison guidelines)

### Integration Notes

- All files are documentation/configuration — no code changes
- `patterns.yml` is referenced by CLAUDE.md (ADV-0046) and pattern_lint.py
  (ADV-0049), but doesn't depend on them being merged first
- These files are additive — no conflicts expected

## Source

Upstream directories:
- `/private/tmp/agentive-starter-kit/.agent-context/workflows/`
- `/private/tmp/agentive-starter-kit/.agent-context/patterns.yml`

## PR Template

```
Title: sync: Add workflow docs and patterns.yml (ADV-0050)

Body:
## Summary
Adds 4 workflow documents and the patterns.yml defensive coding
reference from agentive-starter-kit@0c68f0f.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] All 4 workflow files added to `.agent-context/workflows/`
- [ ] patterns.yml added to `.agent-context/`
- [ ] CI passes
- [ ] PR created and merged
