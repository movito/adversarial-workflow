# Quick Agent Setup

**TL;DR**: This project uses a structured agent coordination system. Read `.agent-context/AGENT-SYSTEM-GUIDE.md` for full details.

---

## 5-Minute Setup

```bash
# 1. Verify directories exist
ls .agent-context/
ls delegation/tasks/

# 2. Check agent handoffs
cat .agent-context/agent-handoffs.json

# 3. Launch an agent
./agents/launch
```

---

## Core Concepts

### 1. Agent Identity Header (Required)

**Always** start responses with:
```
[EMOJI] **AGENT-NAME** | Task: [task-name]
```

Examples:
- `📋 **PLANNER** | Task: phase-planning`
- `🛠️ **FEATURE-DEVELOPER** | Task: ADV-0001`
- `🧪 **TEST-RUNNER** | Task: verification`

---

### 2. Update agent-handoffs.json (Frequently)

Location: `.agent-context/agent-handoffs.json`

Update when:
- Starting a new task
- Completing a task
- Handing off to another agent
- Encountering blockers

---

### 3. Task Folder Structure

```
delegation/tasks/
├── 1-backlog/     # Planned but not started
├── 2-todo/        # Ready to work on
├── 3-in-progress/ # Currently being worked on
├── 4-in-review/   # Awaiting review
├── 5-done/        # Completed
├── 6-canceled/    # Won't be implemented
├── 7-blocked/     # Waiting on dependencies
├── 8-archive/     # Historical reference
└── 9-reference/   # Templates and docs
```

---

## Available Agents

| Agent | Icon | Purpose |
|-------|------|---------|
| planner | 📋 | Coordination, task management |
| feature-developer | 🛠️ | TDD implementation |
| test-runner | 🧪 | Quality assurance |
| pypi-publisher | 📦 | Package releases |

---

## Quick Commands

```bash
# Launch agent menu
./agents/launch

# Launch specific agent
./agents/launch planner
./agents/launch feature-developer

# Run tests
source .venv/bin/activate
pytest tests/ -v

# Run evaluation
adversarial evaluate delegation/tasks/2-todo/ADV-XXXX.md
```

---

## Task Prefix

All tasks use the `ADV-` prefix (Adversarial):
- `ADV-0001-test-infrastructure.md`
- `ADV-0002-feature-name.md`

---

## More Information

- **Full Guide**: `.agent-context/AGENT-SYSTEM-GUIDE.md`
- **Agent Definitions**: `.claude/agents/`
- **Task Template**: `delegation/tasks/9-reference/templates/task-template.md`
