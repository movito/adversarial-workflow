# Operational Rules for All Agents

**Version**: 1.0
**Last Updated**: 2025-11-28
**Applies To**: ALL agents in adversarial-workflow

---

## Project Overview

**adversarial-workflow** is a Python CLI tool published to PyPI that enables adversarial evaluation of task specifications using GPT-4o via aider.

- **Package**: `adversarial-workflow` on PyPI
- **CLI**: `adversarial` command
- **Core Dependency**: `aider-chat` (bundled)
- **Python**: 3.11 required (aider-chat compatibility)

---

## Agent Roster

| Agent | Role | Primary Tools |
|-------|------|---------------|
| **planner** | Coordination, task management, version tracking | All |
| **feature-developer** | TDD implementation, code changes | Write, Edit, Bash |
| **test-runner** | Quality assurance, test execution | Bash, Read |
| **pypi-publisher** | Package releases, version updates | Bash, Edit |

---

## Serena Activation

All agents should activate Serena for semantic code navigation:

```
mcp__serena__activate_project("adversarial-workflow")
```

This enables:
- Go-to-definition
- Find references
- Symbol search
- Efficient code exploration (70-98% token savings)

---

## TDD Requirements

**All code changes MUST follow TDD:**

1. Write failing test first
2. Run test to verify it fails
3. Implement code to pass test
4. Run all tests
5. Refactor while keeping tests green
6. Commit

**Test Commands**:
```bash
source .venv/bin/activate
pytest tests/ -v
```

---

## Version Management

**Three locations must stay in sync:**

1. `pyproject.toml` - `version = "X.Y.Z"`
2. `adversarial_workflow/__init__.py` - `__version__ = "X.Y.Z"`
3. `adversarial_workflow/cli.py` - `__version__ = "X.Y.Z"`

**Only pypi-publisher should update versions.**

---

## Task Management

Tasks use prefix `ADV-` and live in `delegation/tasks/`:

| Folder | Status |
|--------|--------|
| `1-backlog/` | Planned |
| `2-todo/` | Ready |
| `3-in-progress/` | Active |
| `4-in-review/` | Review |
| `5-done/` | Complete |

---

## Evaluation Workflow

Request GPT-4o evaluation for complex tasks:

```bash
adversarial evaluate delegation/tasks/2-todo/ADV-XXXX-task.md
cat .adversarial/logs/ADV-*-PLAN-EVALUATION.md
```

**Cost**: ~$0.04 per evaluation

---

## Commit Protocol

```bash
git add <files>
git commit -m "$(cat <<'EOF'
type(scope): description

Details here.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Types**: feat, fix, docs, test, refactor, chore

---

## Python Environment

**Always use the virtual environment:**

```bash
# Create (if needed)
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

---

## Questions?

Escalate to planner for:
- Task prioritization decisions
- Cross-agent coordination
- Version release decisions
- Unclear requirements
