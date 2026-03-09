# ADV-0039: Upstream Sync from agentive-starter-kit (March 2026)

**Status**: Todo
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 3-4 hours (across multiple agents)
**Created**: 2026-03-07
**Source Commit**: agentive-starter-kit@0c68f0f (74 commits since last sync)

## Summary

Pull updates from the upstream agentive-starter-kit into adversarial-workflow.
This is a **decomposed sync** — broken into ~11 independent PRs by component
category, each small enough to review in one pass.

### Why Decomposed?

A monolithic PR (#34, now closed) generated 68 bot review threads, most about
upstream-authored code we copied verbatim. It was impossible to review
effectively or distinguish our integration issues from upstream bugs.

### Principles

1. **One PR per category** — each reviewable in minutes, not hours
2. **Upstream-authored PRs get a pass** — tag as "upstream sync, copied
   verbatim" and dismiss bot findings about upstream code
3. **Our integration work gets proper review** — settings merge, CLAUDE.md,
   find_task_file patch
4. **Upstream bugs are upstream's problem** — file issues upstream, don't fix
   in our sync PRs

## Reference

- **Closed monolithic PR**: #34 (preserved for reference)
- **Sync branch** (preserved): `sync/adv-0039-upstream-sync`
- **ADR**: `docs/decisions/adr/0013-agentive-starter-kit-alignment.md`
- **Upstream repo**: `/private/tmp/agentive-starter-kit`

## Sub-Tasks

Each sub-task is one PR. They are **independent** and can be executed in
parallel by different agents. Order shown is suggested but not required (except
where noted).

| Sub-Task | PR Title | Task ID |
|----------|----------|---------|
| 1. Slash commands | ADV-0040 | `ADV-0040` |
| 2. Skills | ADV-0041 | `ADV-0041` |
| 3. Agent updates (keep ours) | ADV-0042 | `ADV-0042` |
| 4. Agent updates (take upstream) | ADV-0043 | `ADV-0043` |
| 5. New agents | ADV-0044 | `ADV-0044` |
| 6. Settings & config | ADV-0045 | `ADV-0045` |
| 7. CLAUDE.md & docs | ADV-0046 | `ADV-0046` |
| 8. Upstream scripts (as-is) | ADV-0047 | `ADV-0047` |
| 9. scripts/core/project patch | ADV-0048 | `ADV-0048` |
| 10. pattern_lint + tests | ADV-0049 | `ADV-0049` |
| 11. Workflows & patterns | ADV-0050 | `ADV-0050` |

## Completion Criteria

- [ ] All 11 sub-task PRs merged
- [ ] `.agent-context/current-state.json` updated with sync metadata
- [ ] ADR-0013 updated with sync history entry
- [ ] All tests pass on main after final merge
- [ ] No regressions in existing functionality
