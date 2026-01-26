# ADR 0013: Agentive Starter Kit Alignment

## Status

**In Progress** - Comprehensive comparison completed 2025-01-25

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
| `agents/` (launch scripts) | ✅ | ❌ | **Missing** |
| `scripts/` (utilities) | ✅ | ❌ | **Missing** |
| `delegation/` | ✅ | ✅ | Aligned |
| `docs/` | ✅ | ✅ | Aligned |
| `tests/` | ✅ | ✅ | Aligned |
| `SETUP.md` | ✅ | ❌ | **Missing** |
| `CHANGELOG.md` | ✅ | ✅ | Aligned |
| `conftest.py` (root) | ✅ | ❌ | **Missing** |

### .agent-context/ Structure

| Component | Starter Kit | adversarial-workflow | Status |
|-----------|-------------|---------------------|--------|
| `agent-handoffs.json` | ✅ | ✅ | Aligned |
| `current-state.json` | ✅ | ❌ | **Missing** |
| `README.md` | ✅ | ❌ | **Missing** |
| `REVIEW-INSIGHTS.md` | ✅ | ❌ | Optional |
| `archive/` | ✅ | ✅ | Aligned |
| `reviews/` | ✅ | ✅ | Aligned |
| `templates/` | ✅ | ❌ | **Missing** |
| `workflows/` | ✅ | ❌ | **Missing** |

### .agent-context/templates/

| Template | Starter Kit | adversarial-workflow | Status |
|----------|-------------|---------------------|--------|
| `review-starter-template.md` | ✅ | ❌ | **Missing** |
| `review-template.md` | ✅ | ❌ | **Missing** |

### .agent-context/workflows/

| Workflow | Starter Kit | adversarial-workflow | Status |
|----------|-------------|---------------------|--------|
| `ADR-CREATION-WORKFLOW.md` | ✅ | ❌ | **Missing** |
| `AGENT-CREATION-WORKFLOW.md` | ✅ | ❌ | **Missing** |
| `COMMIT-PROTOCOL.md` | ✅ | ❌ | **Missing** |
| `COVERAGE-WORKFLOW.md` | ✅ | ❌ | **Missing** |
| `REVIEW-FIX-WORKFLOW.md` | ✅ | ❌ | **Missing** |
| `TASK-COMPLETION-PROTOCOL.md` | ✅ | ❌ | **Missing** |
| `TEST-SUITE-WORKFLOW.md` | ✅ | ❌ | **Missing** |
| `TESTING-WORKFLOW.md` | ✅ | ❌ | **Missing** |

### agents/ (Root Launch Scripts)

| Script | Starter Kit | adversarial-workflow | Status |
|--------|-------------|---------------------|--------|
| `launch` | ✅ | ❌ | **Missing** |
| `onboarding` | ✅ | ❌ | **Missing** |
| `preflight` | ✅ | ❌ | **Missing** |

### scripts/ (Utilities)

| Script | Starter Kit | adversarial-workflow | Status |
|--------|-------------|---------------------|--------|
| `ci-check.sh` | ✅ | ❌ | **Missing** |
| `project` | ✅ | ❌ | **Missing** |
| `verify-ci.sh` | ✅ | ❌ | **Missing** |
| `verify-setup.sh` | ✅ | ❌ | **Missing** |
| `validate_task_status.py` | ✅ | ❌ | **Missing** (referenced in pre-commit) |
| `linear_sync_utils.py` | ✅ | N/A | Optional (Linear integration) |
| `sync_tasks_to_linear.py` | ✅ | N/A | Optional (Linear integration) |
| `logging_config.py` | ✅ | ❌ | **Missing** |

### .claude/agents/ (Agent Definitions)

| Agent | Starter Kit | adversarial-workflow | Status |
|-------|-------------|---------------------|--------|
| `AGENT-TEMPLATE.md` | ✅ (10.7KB) | ✅ (1.9KB) | **Outdated** |
| `OPERATIONAL-RULES.md` | ✅ (3.3KB) | ✅ (2.9KB) | Similar |
| `TASK-STARTER-TEMPLATE.md` | ✅ | ❌ | **Missing** |
| `agent-creator.md` | ✅ (15.7KB) | ✅ (11.3KB) | **Outdated** |
| `ci-checker.md` | ✅ (7.6KB) | ✅ (7.2KB) | Similar |
| `code-reviewer.md` | ✅ (10.1KB) | ✅ (12.0KB) | **Ours larger** |
| `document-reviewer.md` | ✅ | ❌ | **Missing** |
| `feature-developer.md` | ✅ (16.6KB) | ✅ (5.5KB) | **Outdated** |
| `onboarding.md` | ✅ | ❌ | **Missing** |
| `planner.md` | ✅ (23.0KB) | ✅ (10.2KB) | **Outdated** |
| `powertest-runner.md` | ✅ | ❌ | **Missing** |
| `security-reviewer.md` | ✅ | ❌ | **Missing** |
| `test-runner.md` | ✅ (7.0KB) | ✅ (3.6KB) | **Outdated** |
| `tycho.md` | ✅ | ❌ | **Missing** |
| `pypi-publisher.md` | ❌ | ✅ | **Ours only** |

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

## Summary: What We're Missing

### High Priority (Infrastructure)

1. **`agents/` launch scripts** - `launch`, `onboarding`, `preflight`
2. **`scripts/` utilities** - `validate_task_status.py`, `verify-setup.sh`, `ci-check.sh`
3. **`.agent-context/current-state.json`** - Project metrics tracking
4. **`.agent-context/templates/`** - Standardized review templates
5. **`.agent-context/workflows/`** - 8 workflow documentation files
6. **`TASK-STARTER-TEMPLATE.md`** - Standardized handoff format

### Medium Priority (Agent Updates)

1. **Update `planner.md`** - Ours is 10KB, starter kit is 23KB
2. **Update `feature-developer.md`** - Ours is 5.5KB, starter kit is 16.6KB
3. **Update `AGENT-TEMPLATE.md`** - Ours is 1.9KB, starter kit is 10.7KB
4. **Add `document-reviewer.md`**
5. **Add `security-reviewer.md`**
6. **Add `onboarding.md`**

### Low Priority (Nice to Have)

1. `SETUP.md` - Setup documentation
2. `conftest.py` at root
3. `powertest-runner.md`, `tycho.md` agents
4. Linear sync integration

### What We Have That's Unique

1. **13 ADRs** - Comprehensive architectural documentation
2. **`pypi-publisher.md`** - PyPI release automation agent
3. **`docs/` structure** - guides, proposals, reference, internal
4. **`.adversarial/`** - Custom CLI configuration
5. **`evaluations/` folder** - GPT-4o evaluation integration

## Migration Options

### Option A: Copy Missing Files (Incremental)

Copy missing infrastructure files from starter kit:
- Preserves our unique content
- Lower risk
- Can be done incrementally

### Option B: Fresh Start from Starter Kit

Start new repo from starter kit, migrate code:
- Cleaner structure
- Loses git history
- Higher effort

### Option C: Hybrid - Selective Sync

Create a sync script that:
1. Pulls agent definitions from starter kit
2. Preserves our unique files
3. Merges where appropriate

## Recommended Approach

**Option A (Incremental)** with priority order:

1. Copy `scripts/validate_task_status.py` (fixes pre-commit warning)
2. Copy `.agent-context/templates/` folder
3. Copy `.agent-context/workflows/` folder
4. Add `.agent-context/current-state.json`
5. Update agent definitions one by one
6. Copy `agents/` launch scripts

## Action Items

- [ ] Create task to copy missing infrastructure files
- [ ] Create task to update agent definitions
- [ ] Decide on Linear integration (yes/no)
- [ ] Add starter kit as git remote for easy comparison

## References

- **agentive-starter-kit**: https://github.com/movito/agentive-starter-kit
  ```bash
  git clone git@github.com:movito/agentive-starter-kit.git ~/Github/agentive-starter-kit
  ```
- **adversarial-workflow**: https://github.com/movito/adversarial-workflow
  ```bash
  git clone git@github.com:movito/adversarial-workflow.git ~/Github/adversarial-workflow
  ```
