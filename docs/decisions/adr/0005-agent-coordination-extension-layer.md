# ADR-0005: Agent Coordination Extension Layer

**Status**: Accepted

**Date**: 2025-10-17 (v0.3.0)

**Deciders**: Fredrik Matheson

## Context

The adversarial workflow (ADR-0001) provides code quality gates for any development approach. However, some projects use multiple AI agents working in parallel, each handling different aspects of development (testing, documentation, feature implementation, etc.).

These multi-agent projects need:
- Task assignment and tracking across agents
- Status coordination (who's working on what)
- Handoff documentation (what needs to happen next)
- Project state snapshot (for new agents joining)
- Structured task management (active, completed, blocked)

### The Integration Challenge

When developing adversarial-workflow itself, the need for agent coordination became apparent:
- 7 different agent roles (coordinator, test-runner, document-reviewer, etc.)
- Parallel work on multiple tasks
- Frequent agent context switching
- Need to track: current focus, deliverables, blockers, status

**Initial approach** (manual coordination):
- Ad-hoc task files in `tasks/`
- No structured agent status tracking
- Context rebuilt from scratch each session
- ~500+ tokens per context reload

**Problems:**
1. **No central coordination**: Each agent rebuilt context independently
2. **Lost context**: Switching agents required re-explaining project state
3. **Unclear status**: Hard to know what's active, blocked, or completed
4. **Inefficient**: Repeated context loading across sessions

### Forces at Play

**Core Workflow Independence:**
- Adversarial workflow should work standalone
- Most users don't use multi-agent development
- Adding mandatory agent coordination would be overkill
- Core functionality (evaluate, review, validate) doesn't need agents

**Multi-Agent Project Needs:**
- Complex projects benefit from specialized agents
- Agent coordination reduces token waste
- Structured task management improves clarity
- Status tracking prevents duplicate work

**Package Philosophy:**
- Keep core simple and focused
- Make extensions optional
- Allow users to adopt incrementally
- Avoid feature bloat

**Future Flexibility:**
- May want to extract agent coordination as separate package
- Different projects may need different coordination systems
- Some users might have their own agent systems

### Problem Statement

How do we:
1. Provide agent coordination for projects that need it
2. Keep core workflow simple for projects that don't
3. Allow clean separation between concerns
4. Enable future package splitting if needed
5. Prevent mandatory dependency on agent infrastructure

## Decision

Implement agent coordination as an **optional extension layer** that builds on top of the core adversarial-workflow system.

### Layered Architecture

**Layer 1: Core Adversarial Workflow** (mandatory)
```
adversarial init
├── .adversarial/
│   ├── config.yml           # Configuration
│   ├── scripts/             # Workflow scripts
│   ├── logs/                # Execution logs
│   └── artifacts/           # Phase outputs
└── tasks/                   # Task files (optional location)
```

**Purpose**: Multi-stage code quality gates (evaluate, review, validate)

**Layer 2: Agent Coordination** (optional extension)
```
adversarial agent onboard
├── .agent-context/          # Agent coordination
│   ├── agent-handoffs.json  # Central status tracking
│   ├── current-state.json   # Project snapshot
│   ├── README.md            # Coordination guide
│   └── session-logs/        # Agent activity logs
├── delegation/
│   ├── tasks/
│   │   ├── active/          # Active work
│   │   ├── completed/       # Done tasks
│   │   ├── archived/        # Historical tasks
│   │   └── analysis/        # Task breakdowns
│   ├── handoffs/            # Agent handoff docs
│   └── decisions/           # Decision records
└── agents/
    └── tools/               # Agent helper scripts
```

**Purpose**: Multi-agent task management and coordination

**Updates**: `.adversarial/config.yml` task_directory → `delegation/tasks/`

### Extension Layer Characteristics

**1. Prerequisite Check**

```python
def agent_onboard():
    # Check Layer 1 exists
    if not os.path.exists(".adversarial/config.yml"):
        error("""
        Agent coordination extends adversarial-workflow core.
        You must initialize the core workflow first.

        FIX: adversarial init
        """)
```

**Why**: Agent coordination is meaningless without core workflow

**2. Builds on Existing**

Extension integrates with core instead of replacing:
- Uses existing `.adversarial/config.yml`
- References existing task files
- Leverages existing log directory
- Updates `task_directory` to point to `delegation/tasks/`

**Why**: Single source of truth, no duplication

**3. Completely Optional**

Core workflow works perfectly without extension:
```bash
# Works fine - no agents needed
adversarial init
adversarial evaluate tasks/feature.md
# ... implement ...
adversarial review
adversarial validate "npm test"
```

**Why**: Core value proposition is quality gates, not agent coordination

**4. Separable Concerns**

Clear boundaries between layers:

| Concern | Layer 1 (Core) | Layer 2 (Extension) |
|---------|----------------|---------------------|
| **Purpose** | Code quality gates | Agent coordination |
| **When to use** | All projects | Multi-agent projects only |
| **Dependencies** | Python, Git, Aider, Bash | Core + multi-agent need |
| **Commands** | evaluate, review, validate | agent onboard |
| **Directory** | .adversarial/ | .agent-context/, delegation/ |

**5. Future Package Separation**

Extension could become separate package:
```python
# Future vision (v0.4.0+)
pip install adversarial-workflow         # Core only
pip install adversarial-agent-coord      # Extension (optional)
pip install adversarial-delegation       # Task management (optional)
```

**Why**: Clean separation enables independent evolution

### Integration Points

**Configuration Update:**
```yaml
# .adversarial/config.yml
task_directory: delegation/tasks/  # Updated by agent onboard
```

**Health Check Integration:**
```bash
adversarial health
# Checks both:
# - Core workflow (config, scripts, API keys)
# - Agent coordination (if present: agent-handoffs.json, delegation/)
```

**Template System:**
```
adversarial_workflow/templates/
├── [core templates]           # Layer 1
└── agent-context/             # Layer 2 templates
    ├── agent-handoffs.json.template
    ├── current-state.json.template
    └── README.md.template
```

## Consequences

### Positive

**Core Simplicity:**
- ✅ **Focused core**: Core workflow remains simple and standalone
- ✅ **Easy adoption**: Users start with core, add coordination if needed
- ✅ **Lower barrier**: Don't need to understand agents to use workflow
- ✅ **Clear value**: Quality gates work immediately without setup overhead

**Extension Flexibility:**
- ✅ **Optional adoption**: Only multi-agent projects need it
- ✅ **Incremental setup**: Add agent coordination when ready
- ✅ **Future-proof**: Can extract as separate package later
- ✅ **Customizable**: Projects can adapt agent structure to needs

**Clean Architecture:**
- ✅ **Separation of concerns**: Quality gates vs task management
- ✅ **Clear dependencies**: Extension depends on core, not vice versa
- ✅ **Testable isolation**: Can test core without extension
- ✅ **Independent evolution**: Core and extension can improve separately

**Token Efficiency:**
- ✅ **Reduced context**: Agent handoffs use ~50-150 tokens vs 500+
- ✅ **Persistent state**: current-state.json for quick onboarding
- ✅ **Structured tracking**: Clear status without lengthy explanations

**Real-World Benefits:**
- ✅ **Proven in practice**: Used successfully in adversarial-workflow development
- ✅ **3h → 5min setup**: `adversarial agent onboard` automates coordination setup
- ✅ **Multi-agent coordination**: 7 agents working in parallel on package development

### Negative

**Conceptual Complexity:**
- ⚠️ **Two-layer model**: Users must understand core vs extension
- ⚠️ **When to use**: Not obvious when agent coordination is beneficial
- ⚠️ **Documentation burden**: Must explain both layers and relationship
- ⚠️ **Decision fatigue**: "Do I need agent coordination?"

**Setup Overhead:**
- ⚠️ **Two commands**: `adversarial init` then `adversarial agent onboard`
- ⚠️ **More directories**: .agent-context/, delegation/, agents/ (vs just .adversarial/)
- ⚠️ **Configuration updates**: Changes task_directory in config.yml
- ⚠️ **Learning curve**: More concepts to understand

**Maintenance:**
- ⚠️ **Two systems**: Core and extension must stay compatible
- ⚠️ **Integration testing**: Must test both standalone and combined
- ⚠️ **Version coordination**: Extension templates must match core expectations
- ⚠️ **Migration paths**: Updates must handle both configurations

**Edge Cases:**
- ⚠️ **Partial setup**: What if user creates .agent-context/ manually?
- ⚠️ **Removal**: How to remove agent coordination cleanly?
- ⚠️ **Conflicts**: What if existing delegation/ directory exists?
- ⚠️ **Health checks**: Must handle both with/without extension

### Neutral

**When to Use Extension:**
- 📊 Multi-agent development (multiple AI tools working in parallel)
- 📊 Complex projects with many active tasks
- 📊 Long-running projects needing historical tracking
- 📊 Teams with specialized roles (testing, docs, security, etc.)

**When Core Alone Suffices:**
- 📊 Solo development with single AI assistant
- 📊 Simple projects with few concurrent tasks
- 📊 Short-term projects or prototypes
- 📊 Users who prefer their own task management

**Future Vision:**
- 📊 v0.3.0: Extension included in core package
- 📊 v0.4.0+: Potentially separate packages
- 📊 Community packages: Third-party coordination systems possible

## Alternatives Considered

### Alternative 1: Mandatory Agent Coordination

**Structure:** All users get agent coordination system

```bash
adversarial init
# Always creates .agent-context/, delegation/, agents/
```

**Rejected because:**
- ❌ **Feature bloat**: Most users don't need multi-agent coordination
- ❌ **Complexity**: Forces all users to understand agent system
- ❌ **Overhead**: Extra directories and setup for no benefit
- ❌ **Confusing**: "What are these agents?" for solo developers
- ❌ **Against philosophy**: Core should be minimal and focused

### Alternative 2: Separate Package from Start

**Structure:** Two packages from v0.1.0

```bash
pip install adversarial-workflow        # Core only
pip install adversarial-agent-coord     # Separate package
```

**Rejected because:**
- ❌ **Premature optimization**: Don't know if separation is needed yet
- ❌ **Integration complexity**: Two packages must stay perfectly synchronized
- ❌ **Version hell**: Users might install incompatible versions
- ❌ **Development overhead**: Maintain two release cycles
- ❌ **Discovery problem**: Users might not find agent-coord package

### Alternative 3: Plugin System

**Structure:** Generic plugin architecture for extensions

```python
# .adversarial/plugins/agent-coord/
# User installs plugins separately
```

**Rejected because:**
- ❌ **Over-engineering**: Only one extension exists (agent coordination)
- ❌ **YAGNI**: "You Aren't Gonna Need It" - premature abstraction
- ❌ **Complexity**: Plugin system adds significant complexity
- ❌ **Performance**: Plugin loading adds overhead
- ❌ **Security**: Plugin system opens attack vectors

### Alternative 4: Configuration Flag Only

**Structure:** Agent coordination enabled via config flag

```yaml
# .adversarial/config.yml
enable_agents: true  # Creates directories when true
```

**Rejected because:**
- ❌ **Implicit setup**: Directories appear "magically" from flag
- ❌ **No validation**: Can't validate setup was successful
- ❌ **Poor UX**: Flag doesn't explain what it does
- ❌ **No templates**: How do agent-handoffs.json templates get created?
- ❌ **Confusing**: Flag exists even if user doesn't use agents

### Alternative 5: No Agent Coordination in Package

**Structure:** Leave agent coordination to users/external tools

**Rejected because:**
- ❌ **Lost opportunity**: Agent coordination works well with adversarial workflow
- ❌ **Redundant work**: Every project would reinvent coordination
- ❌ **Inconsistency**: No standard way to coordinate agents
- ❌ **Our own need**: adversarial-workflow itself needed it during development
- ❌ **Token inefficiency**: Missed opportunity for context optimization

## Real-World Results

### adversarial-workflow Package Development

**Before agent coordination:**
- Ad-hoc task tracking in various files
- ~500+ tokens to rebuild context per session
- Unclear which agent last worked on what
- Duplicate work due to lack of coordination

**After agent onboard (v0.3.0):**
- 7 agents coordinated via agent-handoffs.json
- ~50-150 tokens for context sync (85% reduction)
- Clear status tracking and deliverables
- Parallel agent work without conflicts
- 3-hour manual setup → 5-minute automated setup

**Tasks completed with agent coordination:**
- TASK-SETUP-001 through TASK-SETUP-005 (10+ hours work)
- Multiple agents working in parallel
- Clear handoffs documented
- Zero duplicate work

## Related Decisions

- ADR-0001: Adversarial workflow pattern (what the core layer provides)
- ADR-0004: Template-based initialization (how both layers install)
- ADR-0006: Directory structure separation (why delegation/ vs .agent-context/)
- ADR-0009: Interactive onboarding (how `adversarial agent onboard` works)

## References

- [TASK-SETUP-001](../../../delegation/tasks/completed/TASK-SETUP-001-INTERACTIVE-SETUP-WIZARD.md) - Extension layer design
- [.agent-context/README.md](../../../.agent-context/README.md) - Coordination system documentation
- [cli.py:1806-2044](../../../adversarial_workflow/cli.py#L1806-L2044) - agent_onboard implementation
- [README.md:118-185](../../../README.md#L118-L185) - Quick Setup for AI Agents section

## Revision History

- 2025-10-17: Initial decision (v0.3.0)
- 2025-10-20: Documented as ADR-0005
