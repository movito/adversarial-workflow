# adversarial-workflow

A multi-stage AI code review CLI tool with adversarial evaluation, published to PyPI.
Provides specialized agents, task management, TDD infrastructure, and architectural
decision records. Built on the agentive-starter-kit foundation. For full details,
see `README.md`.

## Directory Structure

```
adversarial_workflow/  Python package (CLI, evaluators, config, resolver)
.claude/agents/       Agent definitions (feature-developer-v3, planner, ci-checker, etc.)
.claude/commands/     Slash commands (start-task, commit-push-pr, check-ci, check-bots, etc.)
.claude/skills/       Skills (pre-implementation, self-review, bot-triage, review-handoff, code-review-evaluator)
.agent-context/       Agent coordination: handoffs, reviews, patterns.yml, workflows/
.adversarial/         Adversarial evaluation system (config, scripts, docs)
.serena/              Serena MCP configuration (semantic code navigation)
agents/               Agent launcher scripts (launch, onboarding, preflight)
delegation/tasks/     Task specs by status: 1-backlog/ through 9-reference/
docs/                 Documentation, ADRs, proposals, guides
scripts/core/         Project management and CI scripts (14 files)
scripts/local/        Local-only scripts (gitignored)
tests/                pytest test suite
```

## Project Rules

### Python (v3.10-3.12)

- **Formatter**: Ruff (line-length=100)
- **Import sorting**: Ruff (isort-compatible rules)
- **Linting**: Ruff (E, F, W, I, N, B, SIM, ARG, UP, S, RUF rules)
- **Custom lint**: pattern_lint.py (DK001-DK004 defensive coding rules)
- **Testing**: pytest with TDD workflow (write tests before implementation)
- **Coverage target**: 80% for new code (`fail_under` in pyproject.toml)
- **Pre-commit hooks**: trailing-whitespace, end-of-file-fixer, yaml/toml checks,
  ruff (lint + format), pattern-lint (DK rules), validate-task-status, pytest-fast

### Branching and CI

- Feature branches: `feature/<TASK-ID>-short-description`
- Run `./scripts/core/ci-check.sh` before pushing
- Verify CI on GitHub after push (`/check-ci` or `./scripts/core/verify-ci.sh`)
- All PRs require passing CI and code review before merge

### Task Workflow

- Task prefix: `ADV-NNNN`
- Status flow: `2-todo` -> `3-in-progress` -> `4-in-review` -> `5-done`
- Task files live in `delegation/tasks/<status-folder>/`
- Use `./scripts/core/project start|move|complete <TASK-ID>` to manage status

### Defensive Coding

- Consult `.agent-context/patterns.yml` before writing new utility functions
- Use `==` for identifier comparison (not `in` unless justified with comment)
- Use `str.removesuffix()` for extension removal (never `.replace()`)
- Follow error strategy by layer: domain modules raise, CLI modules return empty,
  fire-and-forget modules log and continue (see `patterns.yml` -> `error_strategies`)
- Run `python3 scripts/core/pattern_lint.py <files>` to check for pattern violations

## Agent Context

### Key Agents

| Agent | Role |
|-------|------|
| `planner` / `planner2` | Planning and task orchestration |
| `feature-developer-v3` | Implementation with gated workflow |
| `ci-checker` | CI/CD verification |
| `code-reviewer` | Code quality review |
| `test-runner` / `powertest-runner` | TDD and testing |
| `pypi-publisher` | PyPI package releases |
| `document-reviewer` | Documentation quality review |
| `security-reviewer` | Security analysis |
| `onboarding` | First-run project setup |
| `agent-creator` | Interactive agent creation |

Full listing: `.claude/agents/` -- see `AGENT-TEMPLATE.md` for creating new agents.

### Workflow Reference

| Workflow | Location |
|----------|----------|
| Commit protocol | `.agent-context/workflows/COMMIT-PROTOCOL.md` |
| Testing | `.agent-context/workflows/TESTING-WORKFLOW.md` |
| Review fixes | `.agent-context/workflows/REVIEW-FIX-WORKFLOW.md` |
| PR sizing | `.agent-context/workflows/PR-SIZE-WORKFLOW.md` |
| Workflow freeze | `.agent-context/workflows/WORKFLOW-FREEZE-POLICY.md` |
| Coverage | `.agent-context/workflows/COVERAGE-WORKFLOW.md` |
| Task completion | `.agent-context/workflows/TASK-COMPLETION-PROTOCOL.md` |

## Key Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/core/project start <ID>` | Move task to in-progress |
| `./scripts/core/project move <ID> <status>` | Move task to any status |
| `./scripts/core/project complete <ID>` | Move task to done |
| `./scripts/core/project linearsync` | Sync tasks to Linear (optional) |
| `./scripts/core/ci-check.sh` | Full CI check (local) |
| `./scripts/core/verify-ci.sh` | Verify CI status on GitHub |
| `./scripts/core/pattern_lint.py` | Check for defensive coding violations |
| `agents/launch` | Interactive agent launcher |

## Version

See `pyproject.toml` for the current version.
