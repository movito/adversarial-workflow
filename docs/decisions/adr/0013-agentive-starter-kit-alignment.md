# ADR 0013: Agentive Starter Kit Alignment

## Status

**Accepted** - Initial comparison 2025-01-25, full sync completed 2026-03-15 (ADV-0039)

## Context

The `adversarial-workflow` project predates `agentive-starter-kit` and has been retrofitting conventions. This ADR tracks alignment to ensure consistent infrastructure across projects.

## Comparison Matrix

### Root Directory Structure

| Component | Starter Kit | adversarial-workflow | Status |
|-----------|-------------|---------------------|--------|
| `.adversarial/` | ✅ | ✅ | Aligned (project-specific) |
| `.agent-context/` | ✅ | ✅ | Aligned |
| `.claude/` | ✅ | ✅ | Aligned |
| `.serena/` | ✅ | ✅ | Aligned |
| `.github/` | ✅ | ✅ | Aligned |
| `.pre-commit-config.yaml` | ✅ | ✅ | **Aligned** |
| `agents/` (launch scripts) | ✅ | ✅ | **Aligned** (ADV-0052) |
| `scripts/` (utilities) | ✅ | ✅ | **Aligned** (ADV-0052) |
| `delegation/` | ✅ | ✅ | Aligned |
| `docs/` | ✅ | ✅ | Aligned |
| `tests/` | ✅ | ✅ | Aligned |
| `SETUP.md` | ✅ | ❌ | Skipped (not needed) |
| `CHANGELOG.md` | ✅ | ✅ | Aligned |
| `conftest.py` (root) | ✅ | ✅ | **Aligned** |

### .agent-context/ Structure

| Component | Starter Kit | adversarial-workflow | Status |
|-----------|-------------|---------------------|--------|
| `agent-handoffs.json` | ✅ | ✅ | Aligned |
| `current-state.json` | ✅ | ✅ | **Aligned** |
| `README.md` | ✅ | ❌ | Skipped (not needed) |
| `REVIEW-INSIGHTS.md` | ✅ | ❌ | Optional |
| `archive/` | ✅ | ✅ | Aligned |
| `reviews/` | ✅ | ✅ | Aligned |
| `templates/` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `workflows/` | ✅ | ✅ | **Aligned** (ADV-0041/0050) |

### .agent-context/templates/

| Template | Starter Kit | adversarial-workflow | Status |
|----------|-------------|---------------------|--------|
| `review-starter-template.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `review-template.md` | ✅ | ✅ | **Aligned** (ADV-0041) |

### .agent-context/workflows/

| Workflow | Starter Kit | adversarial-workflow | Status |
|----------|-------------|---------------------|--------|
| `ADR-CREATION-WORKFLOW.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `AGENT-CREATION-WORKFLOW.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `COMMIT-PROTOCOL.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `COVERAGE-WORKFLOW.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `REVIEW-FIX-WORKFLOW.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `TASK-COMPLETION-PROTOCOL.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `TEST-SUITE-WORKFLOW.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `TESTING-WORKFLOW.md` | ✅ | ✅ | **Aligned** (ADV-0041) |

### agents/ (Root Launch Scripts)

| Script | Starter Kit | adversarial-workflow | Status |
|--------|-------------|---------------------|--------|
| `launch` | ✅ | ✅ | **Aligned** (ADV-0052) |
| `onboarding` | ✅ | ✅ | **Aligned** (ADV-0052) |
| `preflight` | ✅ | ✅ | **Aligned** (ADV-0052) |

### scripts/ (Utilities)

| Script | Starter Kit | adversarial-workflow | Status |
|--------|-------------|---------------------|--------|
| `ci-check.sh` | ✅ | ✅ | **Aligned** (ADV-0052) |
| `project` | ✅ | ✅ | **Aligned** (ADV-0048/0052) |
| `verify-ci.sh` | ✅ | ✅ | **Aligned** (ADV-0052) |
| `verify-setup.sh` | ✅ | ✅ | **Aligned** (ADV-0052) |
| `validate_task_status.py` | ✅ | ✅ | **Aligned** (ADV-0052) |
| `linear_sync_utils.py` | ✅ | N/A | Skipped (Linear integration) |
| `sync_tasks_to_linear.py` | ✅ | N/A | Skipped (Linear integration) |
| `logging_config.py` | ✅ | ✅ | **Aligned** (ADV-0052) |

### .claude/agents/ (Agent Definitions)

| Agent | Starter Kit | adversarial-workflow | Status |
|-------|-------------|---------------------|--------|
| `AGENT-TEMPLATE.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `OPERATIONAL-RULES.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `TASK-STARTER-TEMPLATE.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `agent-creator.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `ci-checker.md` | ✅ | ✅ | **Aligned** (preserved ours) |
| `code-reviewer.md` | ✅ | ✅ | **Aligned** (preserved ours) |
| `document-reviewer.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `feature-developer.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `onboarding.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `planner.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `powertest-runner.md` | ✅ | ✅ | **Aligned** (ADV-0041) |
| `security-reviewer.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `test-runner.md` | ✅ | ✅ | **Aligned** (ADV-0043) |
| `tycho.md` | ✅ | ❌ | Skipped (upstream only) |
| `pypi-publisher.md` | ❌ | ✅ | **Ours only** (preserved) |

### delegation/tasks/ Structure

| Folder | Starter Kit | adversarial-workflow | Status |
|--------|-------------|---------------------|--------|
| `1-backlog/` | ✅ | ✅ | Aligned |
| `2-todo/` | ✅ | ✅ | Aligned |
| `3-in-progress/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `4-in-review/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `5-done/` | ✅ | ✅ | Aligned |
| `6-canceled/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `7-blocked/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `8-archive/` | ✅ | ✅ | Aligned |
| `9-reference/` | ✅ | ✅ | Aligned |
| `evaluations/` | ❌ | ✅ | **Ours only** |
| `README.md` | ✅ | ✅ | Aligned |

### Documentation

| Component | Starter Kit | adversarial-workflow | Status |
|-----------|-------------|---------------------|--------|
| `docs/decisions/adr/` | ❌ | ✅ (13 ADRs) | **Ours richer** |
| `docs/guides/` | ❌ | ✅ | **Ours only** |
| `docs/proposals/` | ❌ | ✅ | **Ours only** |
| `docs/reference/` | ❌ | ✅ | **Ours only** |

## Summary: Current Alignment Status

After ADV-0039 (March 2026 upstream sync), alignment is essentially complete.

### Fully Aligned

All infrastructure, agents, scripts, workflows, templates, and pre-commit hooks
are now synced with upstream v0.4.0+ conventions.

### Intentionally Skipped

- `tycho.md` — upstream-only agent
- `SETUP.md` — not needed for this project
- Linear sync scripts — Linear integration not enabled

### What We Have That's Unique

1. **13 ADRs** — comprehensive architectural documentation
2. **`pypi-publisher.md`** — PyPI release automation agent
3. **`docs/` structure** — guides, proposals, reference, internal
4. **`.adversarial/`** — custom CLI configuration and evaluator system
5. **`evaluations/` folder** — evaluation tracking

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
| #48 | ADV-0054 | Fix review script bugs |
| #49 | ADV-0046 | CLAUDE.md & docs (this PR) |
| — | ADV-0040, 0042, 0044, 0047 | No-ops (already synced or skipped) |

**Outcome**: Full alignment with upstream v0.4.0+ conventions. Monolithic PR #34
(68 bot threads) was replaced with focused PRs averaging 8 threads each.

## References

- **agentive-starter-kit**: https://github.com/movito/agentive-starter-kit
  ```bash
  git clone git@github.com:movito/agentive-starter-kit.git ~/Github/agentive-starter-kit
  ```
- **adversarial-workflow**: https://github.com/movito/adversarial-workflow
  ```bash
  git clone git@github.com:movito/adversarial-workflow.git ~/Github/adversarial-workflow
  ```
