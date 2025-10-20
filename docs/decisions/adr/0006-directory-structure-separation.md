# ADR-0006: Directory Structure Separation

**Status**: Accepted

**Date**: 2025-10-17 (v0.3.0)

**Deciders**: Fredrik Matheson

## Context

The agent coordination extension (ADR-0005) requires storing both runtime coordination data and work artifacts. During initial implementation, both types of data were stored in a single directory, leading to confusion about organization and purpose.

### The Confusion Problem

**Initial approach** (single directory):
```
.agent-context/
├── agent-handoffs.json      # Runtime: Agent status
├── current-state.json        # Runtime: Project snapshot
├── TASK-001.md              # Artifact: Task file
├── TASK-002.md              # Artifact: Task file
├── HANDOFF-DOC.md           # Artifact: Handoff document
└── session-logs/            # Runtime: Activity logs
```

**Problems identified:**
1. **Mixed concerns**: Runtime coordination files mixed with work artifacts
2. **Version control confusion**: Which files should be committed? Which are ephemeral?
3. **Unclear boundaries**: Is `.agent-context/` for coordination or task storage?
4. **Organizational ambiguity**: Where do completed tasks go? Decision records? Analysis docs?
5. **Naming collision risk**: Task files might conflict with coordination files

### Forces at Play

**Runtime Coordination Needs:**
- Agent status tracking (who's working on what right now)
- Project state snapshot (current situation)
- Session activity logs (historical record)
- Frequent updates (multiple times per day)
- Relatively ephemeral (less important historically)

**Work Artifact Needs:**
- Task specifications and planning
- Completed work documentation
- Decision records
- Handoff documentation between agents
- Permanent record (important historically)
- Structured organization (active, completed, archived)

**Git Workflow Considerations:**
- Runtime state changes frequently (noisy git history)
- Work artifacts change deliberately (meaningful commits)
- Some files should always be committed
- Some files should sometimes be ignored
- Clear `.gitignore` patterns needed

**Mental Model Clarity:**
- Developers need clear expectations about each directory
- New agents need to understand where to look
- Directory names should indicate purpose
- Structure should scale as project grows

### Problem Statement

How do we:
1. Separate runtime coordination from work artifacts
2. Make purpose clear from directory names
3. Support proper git workflow (commit artifacts, optionally track state)
4. Enable structured organization of work products
5. Prevent confusion about where files belong

## Decision

Use **two separate directories** with distinct purposes:

**`.agent-context/`** for **runtime coordination** (state)

**`delegation/`** for **work artifacts** (content)

### Directory Structure

**`.agent-context/` - Runtime Coordination**
```
.agent-context/
├── README.md                # Coordination guide
├── AGENT-SYSTEM-GUIDE.md    # Universal agent system documentation
├── agent-handoffs.json      # Real-time agent status (JSON)
├── current-state.json       # Project snapshot (JSON)
├── INTEGRATION-VERIFICATION.md # Setup verification doc
└── session-logs/            # Agent activity logs
    ├── coordinator-20251020.log
    ├── test-runner-20251020.log
    └── ...
```

**Purpose**: Active coordination and runtime state
**Update Frequency**: Multiple times per day (per agent session)
**Version Control**: Optional (useful but not required)
**Lifetime**: Current project state

**`delegation/` - Work Artifacts**
```
delegation/
├── tasks/
│   ├── active/              # Currently active tasks
│   │   └── TASK-001.md
│   ├── completed/           # Finished tasks
│   │   └── TASK-002.md
│   ├── archived/            # Historical/cancelled tasks
│   │   └── TASK-003.md
│   ├── backlog/             # Future work
│   │   └── TASK-004.md
│   ├── analysis/            # Task breakdowns
│   │   └── ANALYSIS-001.md
│   └── logs/                # Task-specific logs
├── handoffs/                # Agent handoff documents
│   └── HANDOFF-TO-AGENT.md
└── decisions/               # Decision records
    └── DECISION-001.md
```

**Purpose**: Permanent work artifacts and documentation
**Update Frequency**: Deliberate changes (new tasks, completions, decisions)
**Version Control**: Yes, always committed
**Lifetime**: Permanent project history

### Separation of Concerns

| Concern | .agent-context/ | delegation/ |
|---------|-----------------|-------------|
| **Primary purpose** | Coordination state | Work content |
| **Data type** | JSON + logs | Markdown documents |
| **Update pattern** | Frequent, automatic | Deliberate, manual |
| **Lifetime** | Current state | Historical record |
| **Git tracking** | Optional | Required |
| **Audience** | Agents (runtime) | Humans + agents (reference) |
| **Examples** | Agent status, session logs | Tasks, handoffs, decisions |

### Why These Names?

**`.agent-context/`**:
- Prefix `.` indicates tool/system directory (convention)
- "agent" makes purpose obvious
- "context" suggests runtime state/coordination
- Parallel to `.adversarial/` (core system directory)

**`delegation/`**:
- No `.` prefix (not a hidden system directory)
- "delegation" indicates task assignment and management
- Clear semantic meaning (work delegation)
- Professional/formal connotation matches artifact importance

### Integration Pattern

**Task references in coordination:**
```json
// .agent-context/agent-handoffs.json
{
  "coordinator": {
    "current_focus": "ADR Documentation",
    "task_file": "delegation/tasks/active/TASK-ADR-SYSTEM.md",
    "status": "working"
  }
}
```

**Config integration:**
```yaml
# .adversarial/config.yml
task_directory: delegation/tasks/  # Points to delegation
```

**Health check integration:**
```bash
adversarial health
# Checks both:
# - .agent-context/ (coordination system health)
# - delegation/tasks/ (task structure validity)
```

### Git Workflow Recommendations

**Always commit:**
```gitignore
# Commit work artifacts
delegation/**
!delegation/tasks/logs/
```

**Optional commit:**
```gitignore
# Optional: Track agent coordination state
.agent-context/agent-handoffs.json
.agent-context/current-state.json

# Skip: Session logs (too noisy)
.agent-context/session-logs/
```

**Why optional for coordination?**
- Useful for multi-machine/multi-developer setups
- Provides historical context
- But frequent updates create noisy git history
- Each project can decide based on needs

## Consequences

### Positive

**Clarity:**
- ✅ **Clear separation**: State vs content, runtime vs permanent
- ✅ **Obvious purpose**: Directory names indicate function
- ✅ **Mental model**: Easy to understand where files belong
- ✅ **Onboarding**: New agents know where to look

**Organization:**
- ✅ **Structured tasks**: active/completed/archived/backlog hierarchy
- ✅ **Logical grouping**: Related artifacts together (tasks, handoffs, decisions)
- ✅ **Scalability**: Structure supports growing project
- ✅ **Flexibility**: Can add new categories as needed

**Git Workflow:**
- ✅ **Clean commits**: Artifacts committed deliberately
- ✅ **Optional state tracking**: Choose whether to track coordination
- ✅ **Clear .gitignore**: Easy to configure what's tracked
- ✅ **Meaningful history**: Commits show actual work, not state churn

**Technical:**
- ✅ **Naming collision prevention**: Task files won't conflict with agent-handoffs.json
- ✅ **Tool integration**: Clear paths for tools to reference
- ✅ **Backup/sync**: Can backup directories independently
- ✅ **Permissions**: Can set different permissions if needed

### Negative

**Complexity:**
- ⚠️ **Two directories**: More to understand than single directory
- ⚠️ **Path complexity**: Longer paths to task files
- ⚠️ **Mental overhead**: Must remember which directory for what
- ⚠️ **Documentation burden**: Need to explain both directories

**Navigation:**
- ⚠️ **More typing**: `delegation/tasks/active/TASK.md` vs `.agent-context/TASK.md`
- ⚠️ **Directory depth**: 3-4 levels deep for tasks
- ⚠️ **Search across directories**: Finding files spans multiple locations

**Confusion Risk:**
- ⚠️ **Initial confusion**: "Why two directories?"
- ⚠️ **Placement decisions**: "Where does this file go?"
- ⚠️ **Duplicate concepts**: agent-handoffs.json vs handoffs/ directory
- ⚠️ **Naming similarity**: "agent-context" vs "delegation" not obviously contrasting

**Migration:**
- ⚠️ **Existing setups**: Projects with `.agent-context/` tasks need migration
- ⚠️ **Breaking change**: Paths change from v0.2.x to v0.3.0
- ⚠️ **Documentation updates**: Must update all references

### Neutral

**When Separation Helps Most:**
- 📊 Large projects (many tasks, long history)
- 📊 Multiple agents working in parallel
- 📊 Long-running projects (months/years)
- 📊 Teams that value historical record

**When Single Directory Might Suffice:**
- 📊 Small projects (few tasks)
- 📊 Solo development (one agent)
- 📊 Short-term projects (weeks)
- 📊 Informal coordination

**Alternative Organizations:**
- 📊 Could further subdivide delegation/ (e.g., delegation/sprints/)
- 📊 Could add delegation/metrics/ for project analytics
- 📊 Could add .agent-context/checkpoints/ for state snapshots

## Alternatives Considered

### Alternative 1: Single Directory (.agent-context/)

**Structure:** All files in `.agent-context/`

```
.agent-context/
├── agent-handoffs.json
├── current-state.json
├── session-logs/
├── tasks/
│   ├── active/
│   ├── completed/
│   └── archived/
├── handoffs/
└── decisions/
```

**Rejected because:**
- ❌ **Mixed concerns**: Runtime coordination and work artifacts together
- ❌ **Git confusion**: What should be committed?
- ❌ **Naming collision**: TASK files near agent-handoffs.json is confusing
- ❌ **Hidden work**: `.agent-context/tasks/` feels like system internals, not primary content
- ❌ **Semantic mismatch**: "agent context" doesn't describe task files

### Alternative 2: Three Directories

**Structure:** Split further into coordination, tasks, and artifacts

```
.agent-context/     # Coordination only
coordination/       # Just agent-handoffs.json
tasks/              # Task files
artifacts/          # Other documents
```

**Rejected because:**
- ❌ **Over-engineering**: Three directories for simple needs
- ❌ **Naming confusion**: "artifacts" is vague, "tasks" too narrow
- ❌ **More complexity**: Additional directory to understand
- ❌ **Unclear boundaries**: Where do handoffs go? Decisions?
- ❌ **YAGNI**: Don't need three-way split yet

### Alternative 3: Flat Structure

**Structure:** Everything in project root

```
/
├── agent-handoffs.json
├── current-state.json
├── TASK-001.md
├── TASK-002.md
└── ...
```

**Rejected because:**
- ❌ **Root clutter**: Too many files in project root
- ❌ **No organization**: Can't separate active/completed
- ❌ **Naming pollution**: TASK-* files mixed with source code
- ❌ **No hierarchy**: Can't group related artifacts
- ❌ **Scaling problems**: Unworkable with many tasks

### Alternative 4: Mirror Structure

**Structure:** Identical subdirectories in both

```
.agent-context/
├── tasks/
├── handoffs/
└── decisions/

delegation/
├── tasks/
├── handoffs/
└── decisions/
```

**Rejected because:**
- ❌ **Confusing redundancy**: Why duplicate structure?
- ❌ **Unclear purpose**: Which directory for what?
- ❌ **Mental overhead**: Must remember subtle differences
- ❌ **Risk of misplacement**: Easy to put files in wrong place

### Alternative 5: By Agent Role

**Structure:** Directories per agent

```
agents/
├── coordinator/
├── test-runner/
├── document-reviewer/
└── ...
```

**Rejected because:**
- ❌ **Wrong granularity**: Too fine-grained
- ❌ **Cross-cutting tasks**: Many tasks involve multiple agents
- ❌ **Rigid structure**: Adding agents requires new directories
- ❌ **No central coordination**: Where's the project-wide view?

## Real-World Results

### adversarial-workflow Development

**Before separation** (single .agent-context/):
- Confusion about what to commit
- Unclear where completed tasks should go
- Task files mixed with system files
- Difficult to find historical decisions

**After separation** (v0.3.0):
- Clear: `.agent-context/` for runtime state
- Clear: `delegation/` for work artifacts
- Easy task lifecycle: active → completed → archived
- Structured decision records in `delegation/decisions/`
- No naming conflicts

**Migration experience:**
- Moved 5 task files from `tasks/` to `delegation/tasks/active/`
- Updated `.adversarial/config.yml` task_directory
- No data loss, smooth transition
- Agents adapted immediately

## Related Decisions

- ADR-0005: Agent coordination extension layer (why these directories exist)
- ADR-0004: Template-based initialization (how directories are created)
- ADR-0001: Adversarial workflow pattern (task-driven development approach)

## References

- [.agent-context/README.md](../../../.agent-context/README.md) - Coordination directory documentation
- [cli.py:1806-2044](../../../adversarial_workflow/cli.py#L1806-L2044) - Directory creation in agent_onboard
- TASK-SETUP-001 - Original implementation task (extension layer design)

## Revision History

- 2025-10-17: Initial decision (v0.3.0)
- 2025-10-20: Documented as ADR-0006
