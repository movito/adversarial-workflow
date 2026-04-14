# ADV-0046: Upstream Sync — CLAUDE.md & Documentation

**Status**: Done
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 20 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Create the project-level `CLAUDE.md` adapted from upstream, and update sync
tracking documentation.

## Scope

### 1. `CLAUDE.md` (Root) — Create/Update

Adapt upstream's CLAUDE.md for adversarial-workflow. Key customizations:

- **Project name**: adversarial-workflow (not agentive-starter-kit)
- **Package directory**: `adversarial_workflow/` in directory structure
- **Task prefix**: `ADV-NNNN` (not ASK-NNNN)
- **Agent table**: Include pypi-publisher (ours only), exclude tycho
- **Scripts table**: Include our project-specific scripts
- **Version reference**: Point to pyproject.toml

Use the version created in the monolithic PR (branch
`sync/adv-0039-upstream-sync`) as the starting point — it was already
adapted and reviewed.

### 2. `.agent-context/current-state.json` — Update

Update sync tracking metadata:
- `last_synced`: 2026-03-07 (or date of merge)
- `source_commit`: 0c68f0f
- `components`: list of synced component categories

### 3. `docs/decisions/adr/0013-agentive-starter-kit-alignment.md` — Update

Add sync history entry for ADV-0039 with the decomposed approach details.

## PR Template

```
Title: sync: Add CLAUDE.md and update sync documentation (ADV-0046)

Body:
## Summary
Creates project-level CLAUDE.md adapted from upstream. Updates
current-state.json sync metadata and ADR-0013 history.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] CLAUDE.md exists at repo root with adversarial-workflow branding
- [ ] Agent table includes pypi-publisher, excludes tycho
- [ ] Task prefix is ADV-NNNN throughout
- [ ] current-state.json has updated sync metadata
- [ ] ADR-0013 has sync history entry
- [ ] CI passes
- [ ] PR created and merged
