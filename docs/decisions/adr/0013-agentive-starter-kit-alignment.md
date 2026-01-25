# ADR 0013: Agentive Starter Kit Alignment

## Status

**Proposed** - Tracking alignment with agentive-starter-kit conventions

## Context

The `adversarial-workflow` project predates `agentive-starter-kit` and has been retrofitting conventions as they're established. This ADR tracks what we have vs. what the starter kit provides, to ensure we don't miss important infrastructure.

## Comparison Matrix

### Directory Structure

| Component | Starter Kit | adversarial-workflow | Status |
|-----------|-------------|---------------------|--------|
| `.agent-context/` | ✅ | ✅ | Aligned |
| `.agent-context/archive/` | ✅ | ✅ | Aligned |
| `.agent-context/reviews/` | ✅ | ✅ | Aligned |
| `.agent-context/agent-handoffs.json` | ✅ | ✅ | Aligned |
| `.agent-context/current-state.json` | ✅ | ❓ | Check if needed |
| `delegation/tasks/` | ✅ | ✅ | Aligned |
| `delegation/tasks/1-backlog/` | ✅ | ✅ | Aligned |
| `delegation/tasks/2-todo/` | ✅ | ✅ | Aligned |
| `delegation/tasks/3-in-progress/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `delegation/tasks/4-in-review/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `delegation/tasks/5-done/` | ✅ | ✅ | Aligned |
| `delegation/tasks/6-canceled/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `delegation/tasks/7-blocked/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `delegation/tasks/8-archive/` | ✅ | ✅ | Aligned |
| `delegation/tasks/9-reference/` | ✅ | ✅ | Aligned |
| `delegation/tasks/evaluations/` | ✅ | ✅ | Fixed (added .gitkeep) |
| `.gitkeep` in empty folders | ✅ | ✅ | Fixed (2025-01-25) |

### Agent Configuration

| Component | Starter Kit | adversarial-workflow | Status |
|-----------|-------------|---------------------|--------|
| `planner` agent | ✅ | ✅ | Aligned |
| `feature-developer` agent | ✅ | ✅ | Aligned |
| `code-reviewer` agent | ✅ | ✅ | Aligned |
| `test-runner` agent | ✅ | ✅ | Aligned |
| Agent system prompts | ✅ | ❓ | Check for updates |

### File Conventions

| Convention | Starter Kit | adversarial-workflow | Status |
|------------|-------------|---------------------|--------|
| Task specs in `delegation/tasks/[folder]/` | ✅ | ✅ | Aligned |
| Handoffs in `.agent-context/` | ✅ | ✅ | Aligned |
| Review starters in `.agent-context/` | ✅ | ✅ | Aligned |
| Archive completed handoffs | ✅ | ✅ | Aligned |
| Task ID prefix (ADV-) | Project-specific | ADV-XXXX | N/A |

### Workflow Features

| Feature | Starter Kit | adversarial-workflow | Status |
|---------|-------------|---------------------|--------|
| Task lifecycle (backlog → done) | ✅ | ✅ | Aligned |
| Code review workflow | ✅ | ✅ | Aligned |
| Handoff protocol | ✅ | ✅ | Aligned |
| Evaluation before assignment | ❓ | ✅ | adversarial-specific |

### Documentation

| Component | Starter Kit | adversarial-workflow | Status |
|-----------|-------------|---------------------|--------|
| ADR folder structure | ✅ | ✅ | Aligned |
| Agent README/guides | ❓ | ❓ | Check |
| CLAUDE.md conventions | ❓ | ❓ | Check |

## Items to Verify

The following items need manual comparison with agentive-starter-kit:

1. **Agent system prompts** - Are our agent definitions up to date?
2. **current-state.json** - Do we need this file?
3. **CLAUDE.md** - Any project-level conventions we're missing?
4. **Hooks** - Any git hooks or automation scripts?
5. **CI/CD templates** - GitHub Actions workflows?

## Decision

Track alignment in this ADR. Update the status column as items are verified or implemented.

## Action Items

- [ ] Clone/review agentive-starter-kit for full comparison
- [ ] Update agent system prompts if needed
- [ ] Add any missing infrastructure files
- [ ] Document project-specific deviations (e.g., `adversarial evaluate`)

## Consequences

### Positive
- Clear tracking of what's aligned vs. missing
- Easier onboarding for developers familiar with starter kit
- Consistent conventions across projects

### Negative
- Maintenance overhead to keep in sync
- Some conventions may not apply to this project

## References

- agentive-starter-kit repository (TODO: add link)
- ADR 0012: Multi-agent task channels
- `.agent-context/agent-handoffs.json` conventions
