# ADV-0046 Handoff: CLAUDE.md & Documentation Sync

## Context

This is the **last sub-task** of ADV-0039 (upstream sync epic, 10 of 11 done). It creates
the project-level `CLAUDE.md` and updates sync tracking documentation. No code changes —
docs/config only.

## Implementation Guide

### 1. Create `CLAUDE.md` at repo root

Start from the adapted version in the sync branch:
```bash
git show sync/adv-0039-upstream-sync:CLAUDE.md
```

**Critical updates needed** (the sync branch version is stale on these):

| Section | Sync branch says | Should say |
|---------|-----------------|------------|
| Formatter | Black (line-length=88) | **Ruff** (line-length=100) — see `pyproject.toml` |
| Import sorting | isort (profile=black) | **Ruff** (handles imports) |
| Linting | Ruff + flake8 | **Ruff only** (ADV-0053 migrated from flake8) |
| Script paths | `./scripts/project`, `./scripts/ci-check.sh` | `./scripts/core/project`, `./scripts/core/ci-check.sh` (ADV-0052 restructured) |
| pattern_lint path | `scripts/pattern_lint.py` | `scripts/core/pattern_lint.py` |
| create-agent path | `./scripts/create-agent.sh` | `./scripts/optional/create-agent.sh` |
| Pre-commit hooks | black, isort, flake8 | **ruff-check, ruff-format** (see `.pre-commit-config.yaml`) |

**Also add to Scripts table**:
- `./scripts/core/project linearsync` — Sync tasks to Linear (optional)
- `./scripts/core/verify-ci.sh` — Verify CI status on GitHub

**Agent table**: Include `pypi-publisher` (ours), exclude `tycho` (upstream only). This is already correct in the sync branch version.

### 2. Update `.agent-context/current-state.json`

Update the `starter_kit_sync` section:

```json
{
  "starter_kit_sync": {
    "last_synced": "2026-03-15",
    "source_repo": "~/Github/agentive-starter-kit",
    "source_commit": "0c68f0f",
    "source_date": "2026-03-07",
    "synced_components": [
      ".claude/commands/ (slash commands — ADV-0040)",
      ".claude/skills/ + .agent-context/workflows/ + patterns.yml (ADV-0041/0050)",
      ".claude/agents/ (11 take-upstream — ADV-0043)",
      ".claude/settings.json + .pre-commit-config.yaml (ADV-0045)",
      "scripts/core/ (14 files — ADV-0047/0048/0052)",
      "CLAUDE.md (ADV-0046)"
    ],
    "preserved_ours": [
      ".claude/agents/code-reviewer.md",
      ".claude/agents/pypi-publisher.md",
      ".claude/agents/ci-checker.md"
    ],
    "skipped": [
      "scripts/linear_sync_utils.py (Linear-specific)",
      "scripts/sync_tasks_to_linear.py (Linear-specific)",
      ".claude/agents/tycho.md (upstream only)"
    ],
    "check_for_updates": "cd ~/Github/agentive-starter-kit && git log --oneline --since='2026-03-07' -- .claude/ scripts/ .agent-context/"
  }
}
```

Also update:
- `"version": "0.9.9"` (currently says `0.6.2`)
- `"tasks_created"` and `"tasks_completed"` — count from `delegation/tasks/`
- `"recent_activity"` — update with recent completions

### 3. Update ADR-0013

Add a sync history entry at the end of `docs/decisions/adr/0013-agentive-starter-kit-alignment.md`:

```markdown
## Sync History

### ADV-0039: March 2026 Upstream Sync

**Date**: 2026-03-07 through 2026-03-15
**Source**: agentive-starter-kit@0c68f0f (74 commits since last sync)
**Approach**: Decomposed into 11 independent PRs by component category

| PR | Task | Component |
|----|------|-----------|
| #45 | ADV-0041/0050 | Skills, workflows, patterns.yml |
| #43 | ADV-0043 | Agent definitions (take upstream) |
| #47 | ADV-0045 | Settings, pre-commit hooks |
| #46 | ADV-0048 | scripts/core/project patch |
| #44 | ADV-0049 | pattern_lint + tests |
| #40 | ADV-0051 | Evaluator library install |
| #42 | ADV-0052 | Scripts restructure |
| #41 | ADV-0053 | Ruff migration |
| — | ADV-0046 | CLAUDE.md & docs (this PR) |
| — | ADV-0040, 0042, 0044, 0047 | No-ops (already synced or skipped) |

**Outcome**: Full alignment with upstream v0.4.0+ conventions. Monolithic PR #34
(68 bot threads) was replaced with focused PRs averaging 8 threads each.
```

Also update the comparison matrix — many items previously marked **Missing** are now
**Aligned** after the sync. Update at least: `agents/` launch scripts, `scripts/`,
`.agent-context/workflows/`, `.agent-context/templates/`, `conftest.py`, pre-commit.

### 4. Verify and update ADR status

Change ADR-0013 status from "In Progress" to "Accepted" (sync is complete).

## Resources

- Task spec: `delegation/tasks/2-todo/ADV-0046-sync-claude-md-docs.md`
- Upstream CLAUDE.md: `~/Github/agentive-starter-kit/CLAUDE.md`
- Sync branch adapted version: `git show sync/adv-0039-upstream-sync:CLAUDE.md`
- Ruff config: `pyproject.toml` (`[tool.ruff]` section)
- Pre-commit config: `.pre-commit-config.yaml`
- Scripts layout: `scripts/core/` (14 files), `scripts/local/`, `scripts/optional/`
