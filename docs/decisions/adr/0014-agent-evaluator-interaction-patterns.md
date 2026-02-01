# ADR-0014: Agent-Evaluator Interaction Patterns

**Status**: Accepted

**Date**: 2026-02-01 (v0.7.0)

**Deciders**: Fredrik Matheson, feature-developer agent

## Context

As adversarial-workflow has evolved to support multi-agent coordination, the interaction patterns between agents and the Evaluator have become a core architectural concern. New agents joining a project need to understand how these systems interact without reading the entire codebase.

This ADR documents the established interaction patterns as a permanent reference.

## Decision

### The Evaluator: A Stateless Verification Process

The Evaluator is **not an agent**. It is a stateless process that reviews work at specific phases:

| Phase | Command | Input | Purpose |
|-------|---------|-------|---------|
| Plan Evaluation | `adversarial evaluate task.md` | Task specification | Verify plan before implementation |
| Code Review | `adversarial review` | Git diff | Verify implementation against plan |
| Test Validation | `adversarial validate "pytest"` | Test output | Verify tests pass and cover requirements |

**Key characteristics:**
- Invoked via Aider with GPT-4o (or configured model)
- Sees minimal context (only task file or diff, not full codebase)
- Produces verdicts: `APPROVED` / `NEEDS_REVISION` / `REJECT`
- Each evaluation is independent - no memory between invocations
- Cannot be "gamed" because it doesn't see implementation context

**Execution flow:**
```
Agent implements → git add → adversarial review → Verdict
                                    ↓
                    Evaluator sees ONLY the diff
                    (not the surrounding code)
```

### Agent Coordination: File-Based State

Agents coordinate through files, not shared memory or persistent connections:

```
.agent-context/
├── agent-handoffs.json      # Central status hub
├── current-state.json       # Project snapshot
├── workflows/               # Standard procedures
└── [TASK-ID]-HANDOFF-*.md   # Handoff documents
```

**agent-handoffs.json structure:**
```json
{
  "agent-role": {
    "current_focus": "TASK-ID - Description",
    "status": "in_progress | task_complete | blocked",
    "deliverables": ["Item 1", "Item 2"],
    "technical_notes": "Decisions made, rationale",
    "last_updated": "YYYY-MM-DD Description"
  }
}
```

**Protocol:**
1. Agent reads `agent-handoffs.json` on startup
2. Agent updates status when starting/finishing work
3. Agent creates handoff document for next agent
4. Planner reviews and archives completed tasks

### Task Lifecycle

Tasks flow through numbered folders in `delegation/tasks/`:

```
1-backlog/      → Ideas, not yet planned
2-todo/         → Ready to work on
3-in-progress/  → Currently being implemented
4-in-review/    → Awaiting review
5-done/         → Completed
6-canceled/     → Won't implement
7-blocked/      → Waiting on dependencies
8-archive/      → Historical reference
```

**Move tasks with:** `./scripts/project start <TASK-ID>`

### Standard Workflow Pattern

```
1. Planner creates task in 2-todo/
2. Agent runs: ./scripts/project start TASK-ID
   → Task moves to 3-in-progress/
3. Agent implements, writes tests
4. Agent requests plan evaluation: adversarial evaluate task.md
   → If NEEDS_REVISION: iterate on plan
   → If APPROVED: continue
5. Agent implements code
6. Agent requests code review: adversarial review
   → If NEEDS_REVISION: fix issues
   → If APPROVED: continue
7. Agent runs tests: adversarial validate "pytest"
   → If NEEDS_REVISION: fix tests
   → If APPROVED: continue
8. Agent creates review starter for code-reviewer
9. Code-reviewer reviews implementation
   → If CHANGES_REQUESTED: agent fixes
   → If APPROVED: task complete
10. Task moves to 5-done/
```

### Interaction Patterns

**Pattern 1: Sequential Task Execution**
```
Planner → Create Task → Feature-Developer → Implement → Complete
                              ↓
                    Update agent-handoffs.json
                              ↓
                    Create HANDOFF.md
```

**Pattern 2: Task with Adversarial Verification**
```
Feature-Developer → Implement → adversarial review → Fix → Approved
                                      ↓
                              Independent Evaluator
                              (minimal context)
```

**Pattern 3: Multi-Agent Review**
```
Feature-Developer → Implement → Code-Reviewer → Security-Reviewer
                                     ↓                  ↓
                              Review Report      Security Report
                                     ↓
                              Planner Approval
```

**Pattern 4: Investigation-First (Complex Tasks)**
```
Planner → Phase 0 Investigation → Feature-Developer
                                       ↓
                              Investigate & Document
                                       ↓
                              INVESTIGATION-FINDINGS.md
                                       ↓
Planner → Create Implementation Task → Feature-Developer
```

## Consequences

### Positive

- **Token efficiency**: Agent context via JSON (~50-100 tokens) vs full reload (~500+ tokens)
- **Clear separation**: Evaluator is independent, cannot be influenced by agent context
- **Stateless verification**: Each evaluation is fresh, preventing accumulated bias
- **Explicit handoffs**: No assumed context, everything documented
- **Layered architecture**: Core workflow works without agents; agents are optional

### Negative

- **File-based coordination**: Requires discipline to update JSON/handoffs
- **Multiple tools**: Agents must understand both agent-context and evaluator systems
- **Learning curve**: New agents need this ADR to understand interaction patterns

### Neutral

- **Evaluator is external**: Uses Aider + GPT-4o, not the implementing agent's model
- **Verdicts are final**: No negotiation with Evaluator, just fix and re-submit

## Key Principles for Agents

1. **Read agent-handoffs.json first** - Know what others are doing
2. **Update your status** - Mark tasks in_progress/complete promptly
3. **Create handoff docs** - Next agent needs full context
4. **Evaluator is independent** - Don't try to "game" it, just do good work
5. **Minimal context is intentional** - Evaluator's limited view prevents bias
6. **Explicit over implicit** - Document decisions, don't assume context carries over

## Related Decisions

- ADR-0001: Adversarial workflow pattern
- ADR-0005: Agent coordination extension layer
- ADR-0008: Author-Evaluator terminology
- ADR-0012: Multi-agent task channels

## References

- `.agent-context/PROCEDURAL-KNOWLEDGE-INDEX.md` - Agent procedures
- `.agent-context/workflows/` - Standard workflow definitions
- `docs/TERMINOLOGY.md` - Official terminology
