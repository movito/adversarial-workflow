# Quick Agent Setup for Coordinator

**TL;DR**: This project uses a structured agent coordination system. Read `.agent-context/AGENT-SYSTEM-GUIDE.md` for full details.

---

## 5-Minute Setup

```bash
# 1. Create directories
mkdir -p .agent-context delegation/tasks/{active,completed,analysis,logs}

# 2. Initialize agent tracking
cat > .agent-context/agent-handoffs.json << 'EOF'
{
  "coordinator": {
    "current_focus": "Project initialization",
    "status": "active",
    "last_updated": "$(date +%Y-%m-%d)"
  }
}
EOF

# 3. Add to git
git add .agent-context/ delegation/
git commit -m "feat: Initialize agent coordination system"

# Done! Start using identity headers in responses.
```

---

## Core Concepts

### 1. Agent Identity Header (Required)

**Always** start responses with:
```
📋 COORDINATOR | [task-name] | [status]
```

Examples:
- `📋 COORDINATOR | phase-planning | active`
- `👨‍💻 FEATURE-DEVELOPER | TASK-001 | implementing`
- `🧪 TEST-RUNNER | verification | complete`

---

### 2. Update agent-handoffs.json (Frequently)

**When**:
- Starting new work
- Completing tasks
- Making progress
- End of session

**How**:
```json
{
  "coordinator": {
    "current_focus": "✅ TASK-001 COMPLETE - Feature implemented",
    "status": "task_complete",
    "deliverables": [
      "✅ Implementation done",
      "✅ Tests passing"
    ],
    "last_updated": "2025-10-16 Task complete"
  }
}
```

**Commit it**: `git commit -m "chore: Update coordinator status"`

---

### 3. Task Organization

```
delegation/tasks/
├── active/              # Current work
│   └── TASK-001-description.md
├── completed/           # Done
└── analysis/            # Planning
```

**Task naming**: `TASK-YYYY-NNN-short-description.md`

---

### 4. Handoff Documents (For Major Work)

Create when:
- Task >1 hour
- Complex changes
- Multiple files modified
- Handing off to another agent

**Location**: `delegation/handoffs/TASK-NNN-HANDOFF.md`

---

## Key Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `.agent-context/agent-handoffs.json` | Agent status | Every session |
| `.agent-context/current-state.json` | Project metrics | Major milestones |
| `delegation/tasks/active/*.md` | Task specs | As needed |
| `.agent-context/AGENT-SYSTEM-GUIDE.md` | Full reference | Read once |

---

## Common Patterns

### Pattern 1: Simple Task

```
1. Create task spec in delegation/tasks/active/
2. Update agent-handoffs.json (assign task)
3. Do the work
4. Update agent-handoffs.json (mark complete)
5. Move task to delegation/tasks/completed/
```

### Pattern 2: Investigation Before Implementation

```
1. Create investigation task
2. Research codebase (grep, read files)
3. Create FINDINGS.md document
4. Create implementation task (based on findings)
5. Implement with confidence
```

### Pattern 3: Multi-Stage Verification

```
1. Plan evaluation (review approach)
2. Implementation (write code)
3. Code review (check for phantom work)
4. Test validation (verify tests pass)
5. Final approval (merge)
```

---

## Status Emojis

Use in agent-handoffs.json and communications:

- ✅ Complete
- 🔄 In progress
- ⚠️ Blocked
- 🚀 Ready
- 📋 Planning
- 🧪 Testing
- 🎯 High priority

---

## Best Practices

1. **Always use identity headers** - User needs context
2. **Update agent-handoffs.json regularly** - It's project memory
3. **Create task specs before coding** - Prevents confusion
4. **Archive completed tasks** - Keep active/ clean
5. **Document decisions** - Use technical_notes field
6. **Commit context updates** - Git tracks project state

---

## Example Session

```bash
# Start session
📋 COORDINATOR | planning-v0.3.0 | active

# Update status
echo '{"coordinator": {"current_focus": "Planning v0.3.0 features", ...}}' > .agent-context/agent-handoffs.json

# Create task
cat > delegation/tasks/active/TASK-001-examples-system.md

# Assign to developer
# ... implementation work ...

# Mark complete
echo '{"coordinator": {"current_focus": "✅ TASK-001 COMPLETE", ...}}' > .agent-context/agent-handoffs.json

# Archive
mv delegation/tasks/active/TASK-001* delegation/tasks/completed/

# Commit
git add .agent-context/ delegation/
git commit -m "chore: Complete TASK-001 - Examples system"
```

---

## Full Documentation

**Read**: `.agent-context/AGENT-SYSTEM-GUIDE.md` (1300+ lines)

**Covers**:
- Complete agent system architecture
- All coordination patterns
- Setup for new projects
- Troubleshooting
- Real-world examples

---

## Questions?

Check:
1. `.agent-context/AGENT-SYSTEM-GUIDE.md` - Comprehensive reference
2. `delegation/tasks/` - Example task specifications
3. `.agent-context/agent-handoffs.json` - Current project state

---

**Version**: 1.0
**Source**: thematic-cuts agent coordination system
**Validated**: 85.1% → 94.0% test pass rate improvement
**Status**: Production-ready methodology

**Start with identity headers and agent-handoffs.json updates. The rest will follow naturally!** 📋✨
