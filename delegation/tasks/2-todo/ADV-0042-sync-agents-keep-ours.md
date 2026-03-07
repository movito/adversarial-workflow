# ADV-0042: Upstream Sync — Agents (Keep Ours)

**Status**: Todo
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 10 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

For agents where we have significant local customizations, explicitly keep our
versions and skip the upstream update. This PR documents the decision and makes
any minor alignment changes needed.

## Scope

### Agents to Keep (Our Version)

1. **code-reviewer.md** — Ours is larger, has custom PR comment integration,
   venv instructions, and project-specific review criteria
2. **feature-developer-v3.md** — Only 2-line diff from upstream (Serena project
   name). Keep ours.
3. **planner2.md** — Only 2-line diff from upstream (Serena project name).
   Keep ours. Note: planner2 is our custom addition, not in upstream.

### Agent to Remove

4. **tycho.md** — If present, remove. Superseded by planner2.

### No-Op Verification

This PR verifies that our versions of these agents are intentionally preserved.
The only code change may be removing tycho.md if it exists on main.

## PR Template

```
Title: sync: Preserve custom agents, remove tycho (ADV-0042)

Body:
## Summary
Documents that code-reviewer, feature-developer-v3, and planner2 are
intentionally preserved over upstream versions. Removes tycho.md
(superseded by planner2).

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] tycho.md removed (if present)
- [ ] code-reviewer.md unchanged (our version preserved)
- [ ] feature-developer-v3.md unchanged (our version preserved)
- [ ] planner2.md unchanged (our version preserved)
- [ ] CI passes
- [ ] PR created and merged
