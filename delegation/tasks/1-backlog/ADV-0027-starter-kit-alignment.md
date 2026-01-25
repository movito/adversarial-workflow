# ADV-0027: Agentive Starter Kit Alignment

**Status**: Backlog
**Priority**: Medium
**Type**: Infrastructure
**Created**: 2025-01-25
**Reference**: ADR-0013

## Summary

Copy missing infrastructure files from `agentive-starter-kit` to align project conventions and tooling. This is an incremental migration that preserves our unique content while adopting proven infrastructure.

## Background

`adversarial-workflow` predates `agentive-starter-kit`. A comprehensive comparison (ADR-0013) identified gaps in infrastructure, templates, workflows, and agent definitions.

## Scope

### Phase 1: Critical Infrastructure (High Priority)

#### 1.1 Scripts Folder
Copy from `~/Github/agentive-starter-kit/scripts/`:
- [ ] `validate_task_status.py` - Fixes pre-commit hook reference
- [ ] `verify-setup.sh` - Setup verification
- [ ] `ci-check.sh` - CI verification
- [ ] `logging_config.py` - Logging utilities
- [ ] `README.md` - Scripts documentation

**Skip** (Linear-specific):
- `linear_sync_utils.py`
- `sync_tasks_to_linear.py`

#### 1.2 Agent Launch Scripts
Copy from `~/Github/agentive-starter-kit/agents/`:
- [ ] `launch` - Agent launcher
- [ ] `onboarding` - Project onboarding
- [ ] `preflight` - Pre-flight checks

### Phase 2: Agent Context (High Priority)

#### 2.1 Templates
Create `.agent-context/templates/` and copy:
- [ ] `review-starter-template.md`
- [ ] `review-template.md`

#### 2.2 Workflows
Create `.agent-context/workflows/` and copy:
- [ ] `ADR-CREATION-WORKFLOW.md`
- [ ] `AGENT-CREATION-WORKFLOW.md`
- [ ] `COMMIT-PROTOCOL.md`
- [ ] `COVERAGE-WORKFLOW.md`
- [ ] `REVIEW-FIX-WORKFLOW.md`
- [ ] `TASK-COMPLETION-PROTOCOL.md`
- [ ] `TEST-SUITE-WORKFLOW.md`
- [ ] `TESTING-WORKFLOW.md`

#### 2.3 State Tracking
- [ ] Create `.agent-context/current-state.json` (customize for our project)
- [ ] Create `.agent-context/README.md`

### Phase 3: Agent Definitions (Medium Priority)

Update `.claude/agents/` with newer versions:

| Agent | Action | Notes |
|-------|--------|-------|
| `AGENT-TEMPLATE.md` | Update | 1.9KB → 10.7KB |
| `TASK-STARTER-TEMPLATE.md` | Add | New file |
| `planner.md` | Update | 10KB → 23KB |
| `feature-developer.md` | Update | 5.5KB → 16.6KB |
| `test-runner.md` | Update | 3.6KB → 7KB |
| `agent-creator.md` | Update | 11KB → 15.7KB |
| `document-reviewer.md` | Add | New agent |
| `security-reviewer.md` | Add | New agent |
| `onboarding.md` | Add | New agent |

**Preserve** (ours is better/unique):
- `code-reviewer.md` - Ours is larger (12KB vs 10KB)
- `pypi-publisher.md` - Unique to our project

**Skip** (not needed):
- `powertest-runner.md`
- `tycho.md`

### Phase 4: Root Files (Low Priority)

- [ ] Create `SETUP.md` (adapt from starter kit)
- [ ] Create `conftest.py` at root (if needed)

## Implementation Notes

### File Copy Commands

```bash
# Phase 1.1: Scripts
mkdir -p scripts
cp ~/Github/agentive-starter-kit/scripts/validate_task_status.py scripts/
cp ~/Github/agentive-starter-kit/scripts/verify-setup.sh scripts/
cp ~/Github/agentive-starter-kit/scripts/ci-check.sh scripts/
cp ~/Github/agentive-starter-kit/scripts/logging_config.py scripts/
cp ~/Github/agentive-starter-kit/scripts/README.md scripts/

# Phase 1.2: Launch scripts
mkdir -p agents
cp ~/Github/agentive-starter-kit/agents/launch agents/
cp ~/Github/agentive-starter-kit/agents/onboarding agents/
cp ~/Github/agentive-starter-kit/agents/preflight agents/

# Phase 2.1: Templates
mkdir -p .agent-context/templates
cp ~/Github/agentive-starter-kit/.agent-context/templates/* .agent-context/templates/

# Phase 2.2: Workflows
mkdir -p .agent-context/workflows
cp ~/Github/agentive-starter-kit/.agent-context/workflows/* .agent-context/workflows/
```

### Customization Required

After copying, these files need project-specific edits:

1. **`current-state.json`** - Update project name, task prefix (ADV), metrics
2. **`scripts/validate_task_status.py`** - Verify path references
3. **`agents/launch`** - Update project paths if hardcoded
4. **Agent definitions** - Review for project-specific context

### Preserve Our Unique Content

Do NOT overwrite:
- `docs/decisions/adr/` - Our 13 ADRs
- `docs/guides/`, `docs/proposals/`, `docs/reference/`
- `.adversarial/` - CLI configuration
- `delegation/tasks/evaluations/` - GPT-4o integration
- `.claude/agents/pypi-publisher.md`
- `.claude/agents/code-reviewer.md`

## Acceptance Criteria

### Phase 1
- [ ] `scripts/` folder exists with 5 files
- [ ] `agents/` folder exists with 3 launch scripts
- [ ] Pre-commit hook runs without "validate_task_status.py not found" error

### Phase 2
- [ ] `.agent-context/templates/` exists with 2 templates
- [ ] `.agent-context/workflows/` exists with 8 workflow docs
- [ ] `.agent-context/current-state.json` exists and is customized
- [ ] `.agent-context/README.md` exists

### Phase 3
- [ ] 6 agent definitions updated
- [ ] 3 new agents added
- [ ] `pypi-publisher.md` and `code-reviewer.md` preserved

### Phase 4
- [ ] `SETUP.md` exists
- [ ] All tests pass

## Testing

```bash
# Verify pre-commit works
pre-commit run --all-files

# Verify scripts are executable
./agents/preflight
./scripts/verify-setup.sh

# Run test suite
.venv/bin/python -m pytest tests/ -v
```

## Dependencies

- ADV-0022 should be completed first (current blocker)
- No code changes required, purely file additions

## References

- ADR-0013: `docs/decisions/adr/0013-agentive-starter-kit-alignment.md`
- Starter kit: `~/Github/agentive-starter-kit`
