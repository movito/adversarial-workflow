# ADV-0027 Task Starter

## Quick Context

Copy missing infrastructure files from `agentive-starter-kit` to align project conventions. This is file copying with minor customization - no complex code changes.

**Branch**: `fix/adv-0024-0025-env-loading-v2` (continue on current branch)
**Source**: `~/Github/agentive-starter-kit`
**Reference**: ADR-0013 at `docs/decisions/adr/0013-agentive-starter-kit-alignment.md`

## Phase 1: Scripts & Launch Utilities (High Priority)

### 1.1 Create scripts/ folder

```bash
mkdir -p scripts
```

### 1.2 Copy script files

```bash
cp ~/Github/agentive-starter-kit/scripts/validate_task_status.py scripts/
cp ~/Github/agentive-starter-kit/scripts/verify-setup.sh scripts/
cp ~/Github/agentive-starter-kit/scripts/ci-check.sh scripts/
cp ~/Github/agentive-starter-kit/scripts/logging_config.py scripts/
cp ~/Github/agentive-starter-kit/scripts/README.md scripts/
```

### 1.3 Create agents/ folder (launch scripts)

```bash
mkdir -p agents
cp ~/Github/agentive-starter-kit/agents/launch agents/
cp ~/Github/agentive-starter-kit/agents/onboarding agents/
cp ~/Github/agentive-starter-kit/agents/preflight agents/
chmod +x agents/*
```

### 1.4 Verify pre-commit works

```bash
pre-commit run validate-task-status --all-files
```

## Phase 2: Agent Context Infrastructure (High Priority)

### 2.1 Create templates folder

```bash
mkdir -p .agent-context/templates
cp ~/Github/agentive-starter-kit/.agent-context/templates/review-starter-template.md .agent-context/templates/
cp ~/Github/agentive-starter-kit/.agent-context/templates/review-template.md .agent-context/templates/
```

### 2.2 Create workflows folder

```bash
mkdir -p .agent-context/workflows
cp ~/Github/agentive-starter-kit/.agent-context/workflows/*.md .agent-context/workflows/
```

### 2.3 Create current-state.json

Create `.agent-context/current-state.json` with this content (customized for our project):

```json
{
  "project": {
    "name": "adversarial-workflow",
    "version": "0.6.2",
    "description": "Multi-stage AI code review CLI tool",
    "created": "2024-10-20",
    "languages": ["python"]
  },
  "configuration": {
    "serena_enabled": true,
    "evaluator_enabled": true,
    "linear_enabled": false,
    "task_prefix": "ADV"
  },
  "metrics": {
    "tasks_created": 27,
    "tasks_completed": 21,
    "agents_active": 1,
    "test_pass_rate": null,
    "coverage": null
  },
  "recent_activity": [
    "ADV-0022: Fix check() .env variable count",
    "ADV-0024: Custom evaluator .env loading",
    "ADV-0025: Suppress built-in evaluator warning"
  ]
}
```

### 2.4 Create README for .agent-context

Copy and adapt:
```bash
cp ~/Github/agentive-starter-kit/.agent-context/README.md .agent-context/
```

Edit to reflect our project structure.

## Phase 3: Agent Definition Updates (Medium Priority)

### 3.1 Update existing agents

For each file below, copy from starter kit but **review before committing**:

```bash
# These need updating (ours are outdated)
cp ~/Github/agentive-starter-kit/.claude/agents/AGENT-TEMPLATE.md .claude/agents/
cp ~/Github/agentive-starter-kit/.claude/agents/TASK-STARTER-TEMPLATE.md .claude/agents/
cp ~/Github/agentive-starter-kit/.claude/agents/planner.md .claude/agents/
cp ~/Github/agentive-starter-kit/.claude/agents/feature-developer.md .claude/agents/
cp ~/Github/agentive-starter-kit/.claude/agents/test-runner.md .claude/agents/
cp ~/Github/agentive-starter-kit/.claude/agents/agent-creator.md .claude/agents/
```

### 3.2 Add new agents

```bash
cp ~/Github/agentive-starter-kit/.claude/agents/document-reviewer.md .claude/agents/
cp ~/Github/agentive-starter-kit/.claude/agents/security-reviewer.md .claude/agents/
cp ~/Github/agentive-starter-kit/.claude/agents/onboarding.md .claude/agents/
```

### 3.3 DO NOT overwrite these (ours are better/unique)

- `.claude/agents/code-reviewer.md` - Ours is larger and customized
- `.claude/agents/pypi-publisher.md` - Unique to our project
- `.claude/agents/ci-checker.md` - Similar, keep ours

## Phase 4: Root Files (Low Priority)

### 4.1 Create SETUP.md

Copy and adapt:
```bash
cp ~/Github/agentive-starter-kit/SETUP.md ./
```

Edit to reflect our project setup (pip install, .env configuration, etc.)

## Verification Checklist

After each phase, verify:

### Phase 1 Check
```bash
ls scripts/  # Should have 5 files
ls agents/   # Should have 3 files
pre-commit run --all-files  # Should pass
```

### Phase 2 Check
```bash
ls .agent-context/templates/   # Should have 2 files
ls .agent-context/workflows/   # Should have 8 files
cat .agent-context/current-state.json  # Should be valid JSON
```

### Phase 3 Check
```bash
ls -la .claude/agents/  # Should have ~14 files
```

### Full Test
```bash
.venv/bin/python -m pytest tests/ -v  # All tests pass
```

## Commit Strategy

Commit after each phase:

```bash
# After Phase 1
git add scripts/ agents/
git commit -m "feat: Add scripts and launch utilities from starter kit (ADV-0027 Phase 1)"

# After Phase 2
git add .agent-context/templates/ .agent-context/workflows/ .agent-context/current-state.json .agent-context/README.md
git commit -m "feat: Add agent-context templates and workflows (ADV-0027 Phase 2)"

# After Phase 3
git add .claude/agents/
git commit -m "feat: Update agent definitions from starter kit (ADV-0027 Phase 3)"

# After Phase 4
git add SETUP.md
git commit -m "docs: Add SETUP.md (ADV-0027 Phase 4)"
```

## Files to NEVER Overwrite

These are unique to adversarial-workflow:

- `docs/decisions/adr/*` - Our 13 ADRs
- `docs/guides/*`, `docs/proposals/*`, `docs/reference/*`
- `.adversarial/*` - CLI configuration
- `delegation/tasks/evaluations/`
- `.claude/agents/pypi-publisher.md`
- `.claude/agents/code-reviewer.md`
- `adversarial_workflow/*` - Our actual code

## Acceptance Criteria

- [ ] `scripts/` folder with 5 files
- [ ] `agents/` folder with 3 executable launch scripts
- [ ] `.agent-context/templates/` with 2 templates
- [ ] `.agent-context/workflows/` with 8 workflow docs
- [ ] `.agent-context/current-state.json` customized for our project
- [ ] 6 agent definitions updated
- [ ] 3 new agents added
- [ ] Pre-commit hooks pass
- [ ] All tests pass

## Resources

- **Task spec**: `delegation/tasks/1-backlog/ADV-0027-starter-kit-alignment.md`
- **ADR**: `docs/decisions/adr/0013-agentive-starter-kit-alignment.md`
- **Source**: `~/Github/agentive-starter-kit`
