# Plan: Extract Agent Coordination System into Standalone Package

**Created**: 2025-10-17
**Author**: Feature Developer
**Context**: adversarial-workflow v0.3.0 includes basic agent coordination. Time to extract it into a standalone, reusable package.

---

## Executive Summary

### Vision

Create **`agent-coordinate`** - a PyPI package that provides structured multi-agent coordination for Claude Code projects, enabling teams to manage complex development workflows with multiple AI agents working in parallel.

### Problem Statement

Currently, agent coordination is:
- **Embedded** in adversarial-workflow (extension layer, not standalone)
- **Manual** (bash scripts, JSON files, markdown guides)
- **Undocumented** as a product (just implementation artifacts)
- **Not reusable** across projects without copying files
- **Inconsistent** (each project adapts differently)

### Solution

A standalone package that provides:
- **CLI tool** (`agent-coordinate`) for setup and management
- **Python library** for programmatic access
- **Standard conventions** for agent coordination
- **Template system** for project initialization
- **Health monitoring** for coordination quality
- **PyPI distribution** for easy installation

---

## Current State Analysis

### What You Have Now

#### **1. Core Coordination Files**
```
.agent-context/
├── agent-handoffs.json          # Agent status tracking
├── current-state.json            # Project state
├── AGENT-SYSTEM-GUIDE.md         # 34KB comprehensive guide
└── session-logs/                 # Historical records
```

**Quality**: ✅ Production-tested (thematic-cuts, adversarial-workflow)
**Reusability**: ⚠️ Manual copying required

#### **2. Agent Launcher Scripts**
```
agents/
├── universal-agent-launcher.sh   # 8.7KB launcher
├── ca (convenience wrapper)      # Quick agent launcher
├── MULTI-SESSION-GUIDE.md        # Parallel session coordination
├── AGENT-IDENTITY-STANDARD.md    # Identity headers
├── ROLES.md                      # Agent role definitions
├── [role]-developer.sh           # 7 specialized launchers
└── tools/
    ├── preflight-check.sh        # Project validation
    ├── check-stale-status.sh     # Status monitoring
    ├── sync-context.sh           # Context sync
    └── update-status.sh          # Status updates
```

**Quality**: ✅ Functional, tested
**Reusability**: ⚠️ Bash-specific, hardcoded paths

#### **3. Task Management Structure**
```
delegation/
├── tasks/
│   ├── active/                   # Current work
│   ├── completed/                # Archived tasks
│   ├── analysis/                 # Planning docs
│   └── logs/                     # Execution logs
└── handoffs/                     # Agent transitions
```

**Quality**: ✅ Well-organized
**Reusability**: ✅ Easily replicated

#### **4. Integration with adversarial-workflow**
```python
# cli.py:1692-2044
def agent_onboard(project_path: str = ".") -> int:
    """Set up agent coordination system (Extension Layer)."""
    # Creates .agent-context/, delegation/, agents/
    # Renders templates
    # Updates config
```

**Quality**: ✅ Working implementation
**Reusability**: ⚠️ Tightly coupled to adversarial-workflow

### Gaps to Fill

1. **No standalone package** - embedded in adversarial-workflow
2. **No Python library** - just bash scripts and JSON
3. **No package manager** for agent tools
4. **No versioning** for coordination conventions
5. **No CLI beyond adversarial agent onboard**
6. **No monitoring dashboard** or status UI
7. **No cross-project coordination** (multiple projects)
8. **No CI/CD integration** patterns
9. **No conflict resolution** for parallel agents
10. **No advanced orchestration** (dependencies, pipelines)

---

## Product Strategy

### Name Options

1. **`agent-coordinate`** - Clear, action-oriented ✅ **RECOMMENDED**
2. **`claude-coordinate`** - Claude-specific
3. **`multi-agent-coord`** - Descriptive but verbose
4. **`agent-orchestrate`** - Implies more complexity
5. **`agent-mesh`** - Modern but unclear

**Decision**: `agent-coordinate` - Simple, memorable, action-oriented

### Target Audience

#### **Primary**: Claude Code Power Users
- Running multi-agent workflows
- Managing complex codebases (10k+ LOC)
- Working on multi-phase projects
- Need coordination across 3+ specialized agents

#### **Secondary**: Development Teams
- Using AI agents for development
- Want structured coordination
- Need audit trails and context persistence
- Require handoff protocols

#### **Tertiary**: Solo Developers
- Exploring multi-agent workflows
- Want structured project management
- Learning coordination patterns

### Value Proposition

**For Claude Code Users**:
> "Turn chaotic multi-agent development into a structured, trackable workflow. Never lose context, never duplicate work, always know who's doing what."

**Key Benefits**:
- 📋 **Clarity**: Role-based agents with clear responsibilities
- 🔄 **Continuity**: Context persists across sessions
- 📊 **Tracking**: Full audit trail of decisions and progress
- 🤝 **Coordination**: Smooth handoffs between agents
- 📚 **Memory**: Project knowledge doesn't get lost

**Proven Results** (from thematic-cuts):
- 85.1% → 94.0% test pass rate improvement
- 87.5% efficiency gain through structured coordination
- Zero phantom work incidents with multi-agent workflows

### Positioning

**NOT a replacement for**:
- Project management tools (Jira, Linear)
- Git workflow (GitHub, GitLab)
- CI/CD systems (GitHub Actions)
- Task automation (Make, just)

**IS a complement for**:
- Claude Code multi-agent workflows
- AI-powered development coordination
- Context management across AI sessions
- Handoff protocols between specialized agents

**Unique angle**: **"Git for Agent Context"** - Version-controlled agent coordination

---

## Technical Architecture

### Package Structure

```
agent-coordinate/
├── pyproject.toml                 # Package metadata
├── README.md                      # User-facing docs
├── LICENSE                        # MIT License
├── CHANGELOG.md                   # Version history
│
├── agent_coordinate/              # Python package
│   ├── __init__.py
│   ├── __main__.py                # CLI entry point
│   ├── cli.py                     # Command-line interface
│   ├── core.py                    # Core coordination logic
│   ├── config.py                  # Configuration management
│   ├── agents.py                  # Agent abstraction
│   ├── tasks.py                   # Task management
│   ├── context.py                 # Context sync
│   ├── health.py                  # Health monitoring
│   ├── templates/                 # Project templates
│   │   ├── agent-handoffs.json.template
│   │   ├── current-state.json.template
│   │   ├── README.md.template
│   │   └── AGENT-SYSTEM-GUIDE.md
│   └── launchers/                 # Agent launcher scripts
│       ├── universal-launcher.sh
│       ├── coordinator.sh
│       └── [role]-agent.sh
│
├── tests/                         # Test suite
│   ├── test_cli.py
│   ├── test_core.py
│   ├── test_agents.py
│   └── fixtures/
│
├── docs/                          # Documentation
│   ├── quickstart.md
│   ├── user-guide.md
│   ├── api-reference.md
│   ├── architecture.md
│   └── examples/
│       ├── basic-coordination.md
│       ├── parallel-agents.md
│       └── ci-cd-integration.md
│
└── examples/                      # Example projects
    ├── minimal-project/
    ├── multi-agent-project/
    └── advanced-coordination/
```

### Core Components

#### **1. CLI Tool** (`agent-coordinate`)

```bash
# Initialization
agent-coordinate init                  # Initialize coordination in project
agent-coordinate init --minimal        # Minimal setup (just essentials)
agent-coordinate init --full           # Full setup (all features)

# Agent Management
agent-coordinate agents list           # List all agents and status
agent-coordinate agents add <role>     # Add a new agent role
agent-coordinate agents assign <role> <task>  # Assign task to agent
agent-coordinate agents status <role>  # Show agent status

# Task Management
agent-coordinate tasks create <name>   # Create new task
agent-coordinate tasks list            # List active tasks
agent-coordinate tasks complete <id>   # Mark task complete
agent-coordinate tasks archive <id>    # Archive completed task

# Context Management
agent-coordinate context sync          # Sync context across sessions
agent-coordinate context status        # Show context health
agent-coordinate context reset         # Reset to clean state

# Health & Monitoring
agent-coordinate health                # System health check
agent-coordinate health --verbose      # Detailed diagnostics
agent-coordinate health --watch        # Continuous monitoring

# Utilities
agent-coordinate export                # Export coordination data
agent-coordinate import <file>         # Import coordination data
agent-coordinate validate              # Validate setup
agent-coordinate doctor                # Fix common issues
```

#### **2. Python Library** (Programmatic API)

```python
from agent_coordinate import Coordinator, Agent, Task, Context

# Initialize coordination
coordinator = Coordinator(project_path=".")
coordinator.init()

# Create and assign agent
agent = Agent(role="feature-developer", name="John")
task = Task(
    id="TASK-2025-001",
    title="Implement user authentication",
    assignee=agent
)
coordinator.assign(task)

# Update agent status
agent.update_status(
    current_focus="Implementing OAuth flow",
    status="in_progress",
    deliverables=["✅ Database schema", "🔄 API endpoints"]
)

# Context management
context = Context(project_path=".")
context.sync()
context.get_agent_status("feature-developer")

# Health monitoring
health = coordinator.health()
print(f"Health score: {health.score}%")
print(f"Issues: {health.issues}")
```

#### **3. Template System**

```python
# Template rendering with variables
from agent_coordinate.templates import render_template

render_template(
    "agent-handoffs.json",
    output_path=".agent-context/agent-handoffs.json",
    variables={
        "PROJECT_NAME": "my-project",
        "DATE": "2025-10-17",
        "AGENTS": ["coordinator", "feature-developer", "test-runner"]
    }
)
```

#### **4. Health Monitoring**

```python
from agent_coordinate.health import HealthCheck

health = HealthCheck()
result = health.run_all_checks()

# Check categories
# - Configuration validity
# - Agent status freshness
# - Task organization
# - Context sync health
# - File permissions
# - Git integration
# - Coordination patterns

print(f"Overall health: {result.score}%")
for check in result.failed:
    print(f"❌ {check.name}: {check.message}")
    print(f"   Fix: {check.fix}")
```

---

## Development Roadmap

### **Phase 0: Foundation** (Week 1, ~8 hours)

**Goals**: Extract core functionality, create package structure

**Tasks**:
1. Create new GitHub repo: `github.com/movito/agent-coordinate`
2. Set up package structure (pyproject.toml, __init__.py)
3. Extract coordination logic from adversarial-workflow
4. Port templates to package
5. Write basic CLI (`init`, `health`)
6. Add README with quick start

**Deliverables**:
- ✅ GitHub repo created
- ✅ Basic package installable via pip
- ✅ `agent-coordinate init` works
- ✅ `agent-coordinate health` validates setup
- ✅ Documentation covers basic usage

**Success Criteria**: Can install and initialize in a fresh project

---

### **Phase 1: Core Features** (Week 2-3, ~20 hours)

**Goals**: Full CLI, Python library, documentation

**Tasks**:
1. Implement full CLI (agents, tasks, context commands)
2. Build Python library API
3. Port launcher scripts to package
4. Create template system
5. Write comprehensive docs
6. Add examples

**Deliverables**:
- ✅ Complete CLI tool
- ✅ Python library for programmatic use
- ✅ Agent launcher scripts packaged
- ✅ Template rendering system
- ✅ User guide + API docs
- ✅ 3 example projects

**Success Criteria**: Can manage full multi-agent workflow via CLI or Python

---

### **Phase 2: Polish & Release** (Week 4, ~12 hours)

**Goals**: Testing, packaging, PyPI release

**Tasks**:
1. Write test suite (pytest)
2. Add CI/CD (GitHub Actions)
3. Create CHANGELOG
4. Package for PyPI
5. Write release notes
6. Publish v0.1.0

**Deliverables**:
- ✅ Test coverage >80%
- ✅ CI/CD pipeline passing
- ✅ PyPI package published
- ✅ Release notes written
- ✅ Examples validated

**Success Criteria**: Available on PyPI, documented, tested

---

### **Phase 3: Advanced Features** (Future, ~40 hours)

**Goals**: Advanced coordination, integrations, tooling

**Features**:
1. **Dashboard UI** (web-based status monitor)
2. **Cross-project coordination** (multiple projects)
3. **CI/CD integration** (GitHub Actions, GitLab CI)
4. **Conflict resolution** (parallel agent coordination)
5. **Advanced orchestration** (task dependencies, pipelines)
6. **Plugin system** (extensibility)
7. **Cloud sync** (optional remote context)
8. **Metrics & analytics** (coordination efficiency)

**Timeline**: v0.2.0+ (based on user feedback)

---

## Integration with adversarial-workflow

### Strategy: Two Packages, One Workflow

**adversarial-workflow** (existing):
- **Core mission**: AI code review workflow
- **Features**: Plan evaluation, code review, test validation
- **Coordination**: Uses agent-coordinate as dependency

**agent-coordinate** (new):
- **Core mission**: Multi-agent coordination
- **Features**: Agent management, task tracking, context sync
- **Agnostic**: Works with any Claude Code workflow

### Migration Path

#### **Step 1: Extract to Separate Package**

```bash
# Create new repo
gh repo create movito/agent-coordinate --public

# Extract coordination code
cp -r adversarial-workflow/.agent-context/templates agent-coordinate/agent_coordinate/templates/
cp -r adversarial-workflow/agents/tools agent-coordinate/agent_coordinate/launchers/

# Remove from adversarial-workflow
git rm adversarial-workflow/adversarial_workflow/templates/agent-context/
```

#### **Step 2: Make adversarial-workflow Depend on agent-coordinate**

```toml
# adversarial-workflow/pyproject.toml
[project]
dependencies = [
    "pyyaml>=6.0",
    "python-dotenv>=0.19.0",
    "agent-coordinate>=0.1.0",  # NEW
]
```

#### **Step 3: Update adversarial-workflow CLI**

```python
# adversarial-workflow/cli.py
def agent_onboard(project_path: str = ".") -> int:
    """Set up agent coordination (delegates to agent-coordinate)."""
    import agent_coordinate

    coordinator = agent_coordinate.Coordinator(project_path)
    coordinator.init()

    print("Agent coordination set up!")
    print("Use 'agent-coordinate' commands for management.")
    return 0
```

#### **Step 4: Update Documentation**

```markdown
# adversarial-workflow/README.md

## Agent Coordination (Optional)

adversarial-workflow uses `agent-coordinate` for multi-agent workflows.

Install:
```bash
pip install agent-coordinate
```

Setup:
```bash
agent-coordinate init
```

See: https://github.com/movito/agent-coordinate for full docs.
```

### Compatibility

**Backward compatibility**:
- `adversarial agent onboard` still works (delegates to agent-coordinate)
- Existing .agent-context/ files remain valid
- No breaking changes for users

**Forward compatibility**:
- New features in agent-coordinate available to all users
- adversarial-workflow benefits from improvements automatically
- Other tools can use agent-coordinate independently

---

## Market Analysis

### Competitors

#### **1. Multi-Agent Frameworks**
- **AutoGPT, LangChain Agents, CrewAI**: Research/experimental focus
- **Differentiation**: We're Claude Code-specific, production-tested

#### **2. Project Management Tools**
- **Jira, Linear, Asana**: Human team coordination
- **Differentiation**: We're AI agent-specific, context-aware

#### **3. Task Automation**
- **Make, just, Task**: Build automation
- **Differentiation**: We're coordination-focused, not execution

#### **4. Claude Code Workflows**
- **None**: No established patterns yet
- **Opportunity**: First-mover advantage

### Unique Selling Points

1. **Production-Tested**: Validated on real projects (thematic-cuts)
2. **Claude Code Native**: Built specifically for Claude workflows
3. **Git-Integrated**: Version-controlled agent context
4. **Proven Results**: Documented efficiency gains
5. **Simple**: No complex infrastructure, just structured files

---

## Go-to-Market Strategy

### Launch Plan

#### **Phase 0: Soft Launch** (Week 1)
- Publish to GitHub (public repo)
- Share in adversarial-workflow README
- Test with thematic-cuts integration

#### **Phase 1: PyPI Release** (Week 4)
- Publish v0.1.0 to PyPI
- Announce on Twitter/X
- Post to r/ClaudeAI, r/ChatGPT
- Write launch blog post

#### **Phase 2: Community Building** (Ongoing)
- Create documentation site (GitHub Pages)
- Gather feedback from early adopters
- Iterate based on usage patterns
- Build example projects

### Marketing Messages

**For Developer Audiences**:
> "Stop losing context across Claude sessions. `agent-coordinate` gives you git-like version control for multi-agent workflows."

**For AI Enthusiasts**:
> "Turn Claude Code into a coordinated team. Manage multiple AI agents with clear roles, trackable progress, and zero context loss."

**For Enterprise**:
> "Production-tested multi-agent coordination. Audit trails, handoff protocols, and structured workflows for AI-powered development."

### Content Strategy

**Blog Posts**:
1. "Introducing agent-coordinate: Git for AI Agent Context"
2. "How We Improved Test Pass Rates 9% with Structured Agent Coordination"
3. "Multi-Agent Development: Lessons from 20+ Hours of Coordination"
4. "When to Use Multiple AI Agents (and When Not To)"

**Documentation**:
- Quick Start (5 minutes)
- User Guide (comprehensive)
- API Reference (developers)
- Best Practices (patterns)
- Examples (copy-paste ready)

**Community**:
- GitHub Discussions for Q&A
- Issue templates for bug reports
- Contributing guide
- Code of conduct

---

## Success Metrics

### v0.1.0 Goals (First 3 Months)

**Adoption**:
- 🎯 100+ GitHub stars
- 🎯 50+ PyPI downloads/week
- 🎯 10+ production users
- 🎯 5+ community contributions

**Quality**:
- 🎯 Test coverage >80%
- 🎯 Zero critical bugs in production
- 🎯 Documentation completeness >90%
- 🎯 Health check reliability >95%

**Community**:
- 🎯 10+ GitHub issues/PRs
- 🎯 5+ example projects shared
- 🎯 3+ blog posts written
- 🎯 50+ Twitter mentions

### Long-Term Vision (12 Months)

**Adoption**:
- 500+ GitHub stars
- 1000+ PyPI downloads/week
- 100+ production projects
- 20+ contributors

**Features**:
- Web dashboard for monitoring
- CI/CD integrations (GitHub Actions)
- Plugin ecosystem
- Cloud sync option

**Recognition**:
- Referenced in Claude docs
- Featured in AI development blogs
- Conference talks/demos
- Enterprise adoption

---

## Technical Debt & Risks

### Known Issues

1. **Bash-only launchers**: Need cross-platform solution (Python rewrites)
2. **Manual JSON editing**: Need programmatic API
3. **No conflict resolution**: Parallel agents can conflict
4. **Single-project focus**: No multi-project coordination
5. **File-based only**: No database option for scale

### Risks

**Technical**:
- ⚠️ **Coupling with Claude Code**: What if Claude changes workflows?
  - *Mitigation*: Keep core concepts agnostic (roles, tasks, context)
- ⚠️ **File corruption**: JSON files can be edited incorrectly
  - *Mitigation*: Validation, backups, health checks
- ⚠️ **Git conflicts**: Multiple agents editing same files
  - *Mitigation*: Atomic updates, conflict detection, locking

**Product**:
- ⚠️ **Market too niche**: Not enough multi-agent users
  - *Mitigation*: Start with adversarial-workflow users, expand gradually
- ⚠️ **Complexity**: Users don't want another tool
  - *Mitigation*: Make setup trivial (<5 minutes), provide clear value

**Business**:
- ⚠️ **No monetization path**: Open source only
  - *Mitigation*: Not needed initially, future SaaS option (cloud sync, dashboard)

---

## Open Questions

1. **Should launchers be Python or Bash?**
   - Bash: Simpler, already working
   - Python: Cross-platform, easier to maintain
   - **Decision**: Start with Bash (port to Python in v0.2.0)

2. **Web dashboard or CLI-only?**
   - CLI: Lightweight, scriptable
   - Web: Better UX, real-time updates
   - **Decision**: CLI for v0.1.0, web dashboard in v0.3.0

3. **Cloud sync or local-only?**
   - Local: Simple, private, no infrastructure
   - Cloud: Team coordination, remote access
   - **Decision**: Local for v0.1.0, optional cloud in v0.4.0

4. **Paid tier or fully open source?**
   - Open source: Community, adoption
   - Paid: Sustainability, support
   - **Decision**: Open source for now, SaaS option later if demand exists

5. **Name: agent-coordinate or something else?**
   - agent-coordinate: Clear, action-oriented ✅
   - claude-coordinate: Claude-specific
   - multi-agent-coord: Descriptive but verbose
   - **Decision**: agent-coordinate (can expand beyond Claude later)

---

## Next Steps

### Immediate Actions (This Week)

1. **Create GitHub repo**: `movito/agent-coordinate`
2. **Set up package structure**: pyproject.toml, __init__.py
3. **Extract templates**: Copy from adversarial-workflow
4. **Write basic CLI**: `init` and `health` commands
5. **Document quick start**: README with 5-minute setup

### Short-Term (Next 2 Weeks)

6. **Port launcher scripts**: Make them packageable
7. **Build Python library**: Core API for programmatic use
8. **Write user guide**: Comprehensive documentation
9. **Create examples**: 3 example projects
10. **Set up CI/CD**: GitHub Actions for testing

### Medium-Term (Next Month)

11. **Write test suite**: pytest, >80% coverage
12. **Package for PyPI**: Build, test, publish
13. **Announce v0.1.0**: Blog post, social media
14. **Gather feedback**: Early adopters, iterate
15. **Plan v0.2.0**: Advanced features based on usage

---

## Conclusion

**agent-coordinate** fills a clear gap: **structured multi-agent coordination for Claude Code projects**.

**Why it will succeed**:
- ✅ Proven results (thematic-cuts validation)
- ✅ Clear value proposition (context persistence, zero duplication)
- ✅ First-mover advantage (no competitors in this space)
- ✅ Easy adoption (pip install, 5-minute setup)
- ✅ Natural integration (complements adversarial-workflow)

**Timeline**: v0.1.0 in ~4 weeks (~40 hours total effort)

**Effort breakdown**:
- Week 1: Foundation (8h) - Extract, structure, basic CLI
- Week 2-3: Features (20h) - Full CLI, Python lib, docs
- Week 4: Polish (12h) - Tests, packaging, release

**Go/No-Go Decision Factors**:
- ✅ Do you have 40 hours in next month?
- ✅ Do you want to maintain another package?
- ✅ Is there demand from adversarial-workflow users?
- ✅ Can you dogfood it on thematic-cuts?

**Recommendation**: ✅ **GO** - Clear value, proven concept, natural extraction from adversarial-workflow

---

**Next Step**: Create GitHub repo and start Phase 0 (Foundation)

```bash
gh repo create movito/agent-coordinate --public --description "Multi-agent coordination for Claude Code projects"
cd agent-coordinate
mkdir -p agent_coordinate/templates
cp -r ../adversarial-workflow/.agent-context/AGENT-SYSTEM-GUIDE.md agent_coordinate/templates/
# Begin extraction...
```

---

**Document Created**: 2025-10-17
**Status**: Ready for review and decision
**Estimated Effort**: 40 hours over 4 weeks
**Risk Level**: LOW (proven concept, clear path)
