# Plan: Extract Agent Coordination System into Standalone Package (REVISED)

**Version**: 2.0
**Created**: 2025-10-17
**Last Updated**: 2025-10-17
**Status**: CONDITIONAL GO - Validation Required
**Risk Level**: MEDIUM-HIGH
**Author**: Coordinator Agent
**Reviewed By**: Reviewer Agent

---

## Changes from v1.0

**Critical Revisions Based on Review**:
1. ✅ Added Phase -1: Discovery & Validation (MUST complete before Phase 0)
2. ✅ Revised timeline: 40h → 80-90h realistic (or scope down to 35h minimal)
3. ✅ Scoped down Phase 0 to minimal extraction
4. ✅ Added testing strategy
5. ✅ Revised success metrics (realistic expectations)
6. ✅ Added migration plan for existing users
7. ✅ Removed Phase 3 (Advanced Features) - premature scope creep
8. ✅ Removed Python API from v0.1.0 - defer to v0.2.0 if requested
9. ✅ Added decision gates after each phase
10. ✅ Added exit criteria and deprecation plan

**Core Recommendation from Review**: Keep in adversarial-workflow until 50+ users request extraction

---

## Executive Summary

### Vision (Unchanged)

Create **`agent-coordinate`** - a PyPI package that provides structured multi-agent coordination for Claude Code projects.

### Problem Statement (Revised)

Currently, agent coordination is:
- **Embedded** in adversarial-workflow (extension layer, not standalone)
- **Manual** (bash scripts, JSON files, markdown guides)
- **Used by ~5-10 people** (unvalidated market size)
- **Not reusable** without copying files
- **Potentially solving for too small an audience**

### Solution (Refined)

A **minimal** standalone package that provides:
- **JSON schemas** for agent coordination (agent-handoffs.json, current-state.json)
- **CLI tool** with 3 core commands: `init`, `validate`, `health`
- **Standard conventions** for agent context
- **Template system** for project initialization
- **PyPI distribution** for easy installation

**What's DEFERRED to v0.2.0** (if v0.1.0 succeeds):
- Python library API
- Bash launcher scripts
- Advanced CLI commands (tasks, context management)
- Health monitoring dashboard
- CI/CD integration

---

## CRITICAL: Decision Framework

### Phase -1: Discovery & Validation (REQUIRED)

**MUST complete BEFORE starting Phase 0**

**Success Criteria**:
- ✅ Interview 5 adversarial-workflow users about multi-agent workflows
- ✅ Find 5+ people who say "I would use this as standalone package"
- ✅ Validate pain points are real (not just theoretical)
- ✅ Confirm willingness to install separate package

**Timeline**: 1 week (3-5 hours)

**If Validation FAILS (<5 interested users)**:
→ **STOP. DO NOT EXTRACT.**
→ Keep agent coordination in adversarial-workflow v0.4.0
→ Improve documentation instead (1/10th the effort, same value)

### Phase 0: Minimal Extraction (CONDITIONAL)

**Proceed ONLY if Phase -1 succeeds**

**Success Criteria**:
- ✅ Extraction works in isolated environment
- ✅ 2 beta users successfully use package
- ✅ Health check validates setup
- ✅ No critical bugs found

**Timeline**: 2-3 weeks (15-20 hours, time-boxed)

**If Phase 0 FAILS**:
→ Fold back into adversarial-workflow
→ Archive extraction branch
→ Document lessons learned

### Phase 1-2: Full Package (CONDITIONAL)

**Proceed ONLY if Phase 0 succeeds**

**Success Criteria**:
- ✅ Test coverage >70%
- ✅ PyPI package published
- ✅ Documentation complete
- ✅ 3+ beta users validate

**Timeline**: 6-8 weeks (55-70 hours)

---

## Current State Analysis (Unchanged)

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

#### **2. Integration with adversarial-workflow**
```python
# cli.py:1692-2044 (~350 lines)
def agent_onboard(project_path: str = ".") -> int:
    """Set up agent coordination system (Extension Layer)."""
    # Creates .agent-context/, delegation/, agents/
    # Renders templates
    # Updates config
```

**Quality**: ✅ Working implementation
**Reusability**: ⚠️ Tightly coupled (15-20h extraction effort)
**Testing**: ❌ Zero tests for agent coordination features

---

## Product Strategy (Revised)

### Name (Unchanged)

**`agent-coordinate`** - Clear, action-oriented, memorable

### Target Audience (Revised)

#### **Primary**: Claude Code Power Users (Estimated: 50-200 people globally)
- Running multi-agent workflows
- Managing complex codebases (10k+ LOC)
- Need coordination across 3+ specialized agents
- **Already using adversarial-workflow** (most likely path)

#### **Reality Check**: Market size is **unknown and likely small**
- No public Claude Code usage stats
- Multi-agent workflows are advanced/niche
- May be <20 potential users
- **This is HIGH RISK**

### Value Proposition (Refined)

**For Claude Code Users**:
> "Stop losing context across Claude sessions. `agent-coordinate` gives you structured coordination for multi-agent workflows."

**Key Benefits** (Same):
- 📋 **Clarity**: Role-based agents with clear responsibilities
- 🔄 **Continuity**: Context persists across sessions
- 📊 **Tracking**: Full audit trail of decisions and progress

**Proven Results** (thematic-cuts):
- 85.1% → 94.0% test pass rate improvement
- **Sample size: 1 project** (needs more validation)

### Positioning (Simplified)

**"Structured Coordination for AI-Powered Development"**

NOT "Git for Agent Context" - too ambitious, implies scale we don't have

---

## Technical Architecture (Revised)

### Package Structure (Simplified)

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
│   ├── cli.py                     # Command-line interface (3 commands)
│   ├── core.py                    # Core logic (init, validate)
│   ├── health.py                  # Health monitoring
│   ├── schemas.py                 # JSON schema validation
│   └── templates/                 # Project templates
│       ├── agent-handoffs.json.template
│       ├── current-state.json.template
│       ├── README.md.template
│       └── AGENT-SYSTEM-GUIDE.md
│
├── tests/                         # Test suite
│   ├── test_cli.py
│   ├── test_core.py
│   ├── test_health.py
│   ├── test_schemas.py
│   └── fixtures/
│
├── docs/                          # Documentation
│   ├── quickstart.md
│   ├── user-guide.md
│   ├── migration-guide.md         # NEW: For adversarial-workflow users
│   └── api-reference.md
│
└── examples/                      # Example projects
    └── minimal-project/
```

**What's REMOVED from v1.0**:
- ❌ Python library API (agents.py, tasks.py, context.py, config.py) - defer to v0.2.0
- ❌ Bash launcher scripts (launchers/) - too platform-specific
- ❌ Advanced examples - keep it minimal

### Core Components (v0.1.0 - Minimal)

#### **1. CLI Tool** (3 Commands Only)

```bash
# Initialization
agent-coordinate init                  # Initialize coordination in project

# Validation
agent-coordinate validate              # Validate JSON schemas and setup

# Health Monitoring
agent-coordinate health                # System health check
agent-coordinate health --verbose      # Detailed diagnostics
```

**DEFERRED to v0.2.0** (if users request):
```bash
# Agent Management (future)
agent-coordinate agents list
agent-coordinate agents status <role>

# Task Management (future)
agent-coordinate tasks list
agent-coordinate tasks create <name>

# Context Management (future)
agent-coordinate context sync
agent-coordinate context status
```

#### **2. Schema Validation**

```python
# agent_coordinate/schemas.py
from jsonschema import validate

def validate_agent_handoffs(data: dict) -> tuple[bool, list[str]]:
    """Validate agent-handoffs.json against schema."""
    # Returns (is_valid, errors)

def validate_current_state(data: dict) -> tuple[bool, list[str]]:
    """Validate current-state.json against schema."""
    # Returns (is_valid, errors)
```

**Key Features**:
- Schema versioning: `"schema_version": "1.0"`
- Clear error messages
- Migration warnings if schema outdated

#### **3. Health Monitoring**

```python
# agent_coordinate/health.py
class HealthCheck:
    def run_all_checks(self) -> HealthResult:
        """Run all health checks."""
        return HealthResult(
            score=85,
            checks=[
                Check("Configuration valid", passed=True),
                Check("Schemas valid", passed=True),
                Check("Agent status fresh (<2 days)", passed=False,
                      fix="Update agent status"),
            ]
        )

# Check categories (v0.1.0):
# 1. Configuration validity (.agent-context/ exists, files present)
# 2. Schema validation (JSON files match schema)
# 3. Agent status freshness (updated within 2 days)
# 4. File permissions (readable/writable)
```

**DEFERRED to v0.2.0**:
- Task organization checks
- Context sync health
- Git integration checks
- Advanced coordination patterns

---

## Testing Strategy (NEW)

### Unit Tests (~40% of test time)

**test_cli.py**:
- `test_init_command()`: Creates expected files
- `test_validate_command()`: Detects schema errors
- `test_health_command()`: Runs checks

**test_schemas.py**:
- `test_agent_handoffs_validation()`: Valid/invalid schemas
- `test_current_state_validation()`: Required fields
- `test_schema_versioning()`: Version compatibility

**test_core.py**:
- `test_project_initialization()`: Directory creation
- `test_template_rendering()`: Variable substitution
- `test_error_handling()`: Missing files, corrupt JSON

**test_health.py**:
- `test_health_checks()`: Each check category
- `test_health_scoring()`: Score calculation

### Integration Tests (~30% of test time)

**test_full_workflow.py**:
```python
def test_init_validate_health_flow():
    # 1. Initialize project
    # 2. Validate setup
    # 3. Run health check
    # 4. Verify all pass
```

### Manual Testing (~30% of test time)

**Manual Test Plan**:
1. Install package in fresh virtualenv
2. Run `agent-coordinate init` in empty project
3. Validate created files
4. Modify JSON files (test validation)
5. Run health check
6. Test error scenarios (corrupt JSON, missing files)

### CI/CD

**GitHub Actions**:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e .[dev]
      - run: pytest --cov=agent_coordinate --cov-report=xml
      - run: python -m agent_coordinate init --help
```

**Target Coverage**: 70% (realistic, not 80%)

---

## Development Roadmap (REVISED)

### **Phase -1: Discovery & Validation** (Week 1, 3-5 hours) **REQUIRED**

**Goals**: Validate demand before building

**Tasks**:
1. Post in Claude Code communities: "How do you manage multi-agent workflows?"
2. Interview 5 adversarial-workflow users
   - Do they use `adversarial agent onboard`?
   - Would they use standalone package?
   - What pain points do they have?
3. Search for existing solutions (GitHub, PyPI, forums)
4. Write pain point blog post to validate problem

**Deliverables**:
- ✅ User research document (5+ interviews)
- ✅ Pain point validation (confirmed by users)
- ✅ Interest validation (5+ potential users)

**Success Criteria**: Find 5+ people who say "I would use this"

**DECISION GATE**: If <5 interested users → **STOP, DO NOT EXTRACT**

---

### **Phase 0: Minimal Extraction** (Week 2-3, 15-20 hours) **CONDITIONAL**

**Goals**: Extract core functionality, validate extraction works

**Tasks**:
1. Create new GitHub repo: `github.com/movito/agent-coordinate`
2. Set up minimal package structure (pyproject.toml, __init__.py, cli.py, core.py)
3. Extract JSON schemas only (not full coordination logic)
4. Build 3 CLI commands: `init`, `validate`, `health`
5. Write minimal README with quick start
6. Test extraction in isolated environment (not in adversarial-workflow)

**Deliverables**:
- ✅ GitHub repo created
- ✅ Minimal package installable via pip
- ✅ `agent-coordinate init` creates .agent-context/
- ✅ `agent-coordinate validate` checks JSON schemas
- ✅ `agent-coordinate health` runs basic checks
- ✅ README covers 5-minute setup

**Success Criteria**:
- Works independently of adversarial-workflow
- 2 beta users successfully use package
- No critical bugs found

**DECISION GATE**: If beta testing fails → **FOLD BACK into adversarial-workflow**

---

### **Phase 1: Core Features** (Week 4-7, 35-45 hours) **CONDITIONAL**

**Goals**: Complete CLI, testing, documentation

**Tasks**:
1. Add schema validation (jsonschema library)
2. Implement health monitoring (all checks)
3. Write test suite (pytest, 70% coverage)
4. Create comprehensive user guide
5. Add examples (minimal-project/)
6. Write migration guide for adversarial-workflow users
7. Set up CI/CD (GitHub Actions)

**Deliverables**:
- ✅ Complete CLI tool (3 commands, robust)
- ✅ Schema validation with clear errors
- ✅ Health monitoring (4 check categories)
- ✅ Test coverage >70%
- ✅ User guide + API docs
- ✅ 1 example project
- ✅ Migration guide for existing users

**Success Criteria**:
- All tests pass
- 3+ beta users validate
- Documentation is clear
- No critical bugs

---

### **Phase 2: Polish & Release** (Week 8-10, 20-25 hours) **CONDITIONAL**

**Goals**: Packaging, release, initial launch

**Tasks**:
1. Finalize test coverage (address gaps)
2. Create CHANGELOG
3. Package for PyPI (build, twine)
4. Write release notes
5. Publish v0.1.0 to PyPI
6. Update adversarial-workflow README (link to agent-coordinate)
7. Launch blog post + Reddit post

**Deliverables**:
- ✅ PyPI package published
- ✅ Release notes written
- ✅ adversarial-workflow integration documented
- ✅ Launch blog post
- ✅ Social media posts

**Success Criteria**:
- Available on PyPI
- Installation works on clean systems
- Documentation is complete
- Initial users can onboard successfully

---

### **v0.2.0+ Features** (Future, IF v0.1.0 succeeds)

**ONLY if v0.1.0 gets 10+ weekly downloads for 3+ months**

**Potential Features** (user-driven):
1. Python library API (if requested)
2. Advanced CLI commands (tasks, context, agents)
3. Cross-platform launcher (Python, not bash)
4. CI/CD integration patterns
5. Migration tools for schema updates

**Timeline**: 6+ months after v0.1.0 launch

**DO NOT COMMIT TO THESE NOW** - wait for user feedback

---

## Integration with adversarial-workflow (REVISED)

### Strategy: Clean Separation with Optional Integration

**adversarial-workflow v0.4.0** (future):
- **Option A (Recommended)**: Remove `adversarial agent onboard` entirely
  - Users who want coordination install `agent-coordinate` separately
  - adversarial-workflow README links to agent-coordinate
  - No tight coupling, no version hell
  - **Cleanest approach**

- **Option B**: Keep `adversarial agent onboard` as wrapper
  - Check if `agent-coordinate` installed
  - If yes: delegate to it
  - If no: offer to install or run embedded version
  - **More user-friendly but adds complexity**

**Recommendation**: **Option A** (clean break) unless user feedback strongly prefers Option B

### Migration Path for Existing Users

**For users with adversarial-workflow v0.3.0 + agent coordination**:

1. **If they want standalone agent-coordinate**:
   ```bash
   pip install agent-coordinate
   cd project
   agent-coordinate validate  # Check if existing setup is compatible
   # Existing .agent-context/ continues working (backward compatible)
   ```

2. **If they want to stay with adversarial-workflow**:
   ```bash
   # No action needed - adversarial-workflow v0.3.0 continues working
   # agent-coordinate is optional, not required
   ```

**Key Principle**: Existing setups MUST continue working. No forced migration.

### Compatibility Strategy

**Backward Compatibility**:
- agent-coordinate v0.1.0 MUST be compatible with adversarial-workflow v0.3.0 schemas
- Schema changes MUST be additive only (no breaking changes)
- If breaking changes needed → major version bump (v2.0.0)

**Version Matrix**:
```
adversarial-workflow v0.3.0 → Compatible with agent-coordinate v0.1.x, v0.2.x
adversarial-workflow v0.4.0 → Compatible with agent-coordinate v0.1.x+
```

---

## Success Metrics (REALISTIC)

### v0.1.0 Goals (3 Months Post-Launch)

| Metric | v1.0 Plan | v2.0 Realistic |
|--------|-----------|----------------|
| PyPI downloads/week | 50+ | **10-20** |
| Production users | 10+ | **3-5** |
| GitHub stars | 100+ | **25-50** |
| Community contributions | 5+ | **0-2** |

**Qualitative Success**: **3 users say "This solved a real problem for me"**

**If you hit 10 weekly downloads consistently, consider it a win.**

### Red Flags That Mean "STOP"

**3 months post-launch, if you see 2+ of these**:
- 🚩 <5 weekly downloads
- 🚩 Zero GitHub issues or questions
- 🚩 No community engagement
- 🚩 Only you using it

→ **Archive the repo. Fold features back into adversarial-workflow. Move on.**

### Exit Criteria

**When to deprecate**:
- 6 months post-launch: <5 weekly downloads
- No community engagement after 6 months
- Maintenance burden exceeds value
- Better alternatives emerge

**Deprecation Process**:
1. Announce deprecation (README, PyPI, GitHub)
2. Give users 6 months notice
3. Archive repo
4. Fold core features back into adversarial-workflow (if valuable)

---

## Risk Mitigation (NEW)

### Risk 1: Timeline Underestimation (90% probability)

**Original Plan**: 40 hours
**Realistic**: 80-90 hours

**Mitigation**:
- Time-box Phase 0 to 20 hours. If exceeded, reassess scope.
- Accept 80+ hour reality OR scope down to minimal package (schemas + validation only, ~35 hours)
- Allocate 2-3 months, not 4 weeks

### Risk 2: Low Adoption (70% probability)

**What if**: <5 downloads/week after 3 months?

**Mitigation**:
- Define exit criteria upfront (see above)
- Build in public (share progress weekly → builds audience)
- Have backup plan: Fold back into adversarial-workflow

### Risk 3: Maintenance Burden (80% probability)

**What if**: Two packages to maintain forever?

**Mitigation**:
- Label as "experimental" for first 6 months
- Clear expectations: "Best-effort support"
- Consider monorepo if burden becomes high

### Risk 4: Breaking Changes in Dependencies (40% probability)

**What if**: Claude Code changes, Python 3.13 breaks something?

**Mitigation**:
- Pin Python support: 3.8-3.12 for v0.1.0
- Abstract Claude Code specifics behind interface
- Use dependabot for dependency monitoring

---

## Effort Estimation (REALISTIC)

### v1.0 Plan vs v2.0 Realistic

| Phase | v1.0 Estimate | v2.0 Realistic | Notes |
|-------|---------------|----------------|-------|
| Phase -1: Validation | 0h | **3-5h** | NEW - user research |
| Phase 0: Foundation | 8h | **15-20h** | Extraction complexity |
| Phase 1: Core Features | 20h | **35-45h** | Testing, docs take longer |
| Phase 2: Release | 12h | **20-25h** | PyPI issues, debugging |
| **TOTAL** | **40h** | **73-95h** | 82% more realistic |

### Alternative: Minimal Scope (35 hours total)

**If you want to stay in 40-hour budget**:
- Phase -1: 5h (validation)
- Phase 0: 15h (schemas + 3 CLI commands only)
- Phase 1: Skip (no advanced features)
- Phase 2: 15h (minimal testing, quick launch)
- **Total**: 35 hours

**Trade-off**: Ship ultra-minimal package (just schemas + validation), add features in v0.2.0 if users request

---

## Open Questions (REVISED)

### Question 1: Should we extract at all?

**v1.0 Answer**: Yes, natural evolution
**v2.0 Answer**: **Only if Phase -1 validates demand (5+ interested users)**

**Recommendation**: Don't extract until 50+ users actively use adversarial-workflow agent coordination

### Question 2: Timeline - Full or Minimal?

**Option A**: Accept 80-90h reality, plan for 10-12 weeks
**Option B**: Scope down to 35h, ship minimal package

**Recommendation**: **Option B** (minimal scope) - faster to market, lower risk

### Question 3: Integration with adversarial-workflow?

**Option A**: Clean break (separate tools)
**Option B**: Tight integration (dependency)

**Recommendation**: **Option A** (clean break) - simpler, less coupling

### Question 4: What if validation fails?

**If <5 interested users in Phase -1**:
→ Keep agent coordination in adversarial-workflow v0.4.0
→ Improve documentation (1/10th effort, same value)
→ Revisit extraction in 6-12 months if adoption grows

**Recommendation**: **Don't extract yet** - wait for organic demand

---

## Honest Questions to Answer Before Proceeding

1. **Motivation**: Why extract this? For users, or for architecture satisfaction?
2. **Time**: Do you actually have 80-90 hours over next 2-3 months?
3. **Maintenance**: Willing to maintain two packages for 1-2 years?
4. **Adoption Risk**: Will you be okay if only 5 people use it?
5. **Opportunity Cost**: What else could you build with 80 hours? Is this highest-value?
6. **User Evidence**: Have you talked to anyone who said "I need this as separate package"?
7. **Alternative**: Could better documentation achieve the same value at 1/10th the cost?

**If answers reveal low confidence → RECONSIDER EXTRACTION**

---

## Recommendation: Three Paths Forward

### Path 1: DEFER EXTRACTION (Recommended)

**What**: Keep agent coordination in adversarial-workflow v0.4.0
**Why**: No evidence of demand yet, high execution risk
**Effort**: 0 hours extraction, 5-10 hours documentation improvement
**Timeline**: Revisit in 6-12 months if adoption grows

**Pros**: Zero risk, focus on adversarial-workflow adoption
**Cons**: Agent coordination stays coupled

**Choose if**: You're uncertain about demand or don't have 80+ hours

### Path 2: MINIMAL EXTRACTION (Conditional)

**What**: Ship ultra-minimal package (schemas + validation only)
**Why**: Fast to market, low risk, can iterate based on feedback
**Effort**: 35 hours over 4-6 weeks
**Timeline**: Phase -1 (5h) → Phase 0 (15h) → Phase 2 (15h)

**Pros**: Quick validation of concept, manageable scope
**Cons**: Less impressive, may not solve full problem

**Choose if**: Phase -1 validates demand AND you want to ship fast

### Path 3: FULL EXTRACTION (High Risk)

**What**: Full package as planned (schemas + CLI + health + docs + tests)
**Why**: Complete solution, polished product
**Effort**: 80-90 hours over 10-12 weeks
**Timeline**: Phase -1 (5h) → Phase 0 (20h) → Phase 1 (45h) → Phase 2 (25h)

**Pros**: Comprehensive tool, all features
**Cons**: High effort, unvalidated demand, maintenance burden

**Choose if**: Phase -1 validates demand AND Phase 0 succeeds AND you have 80+ hours

---

## Next Steps

### Immediate Action (Week 1): **START WITH PHASE -1**

**Do NOT start extraction until validation complete**

1. **User Research** (3-5 hours):
   - Interview 5 adversarial-workflow users
   - Post in Claude Code communities
   - Validate pain points
   - Find 5+ interested users

2. **Decision Gate**:
   - If <5 interested users: **STOP, DON'T EXTRACT**
   - If 5+ interested users: **Proceed to Phase 0**

### If Validation Succeeds (Week 2-3): **PHASE 0**

1. Create GitHub repo
2. Build minimal package (schemas + 3 CLI commands)
3. Test with 2 beta users
4. Decision gate: Continue or fold back?

### If Phase 0 Succeeds (Week 4-10): **PHASE 1-2**

1. Complete features
2. Write tests
3. Package for PyPI
4. Launch v0.1.0

---

## Conclusion

**agent-coordinate** is a well-conceived idea with proven value on 1 project, but significant execution risks:
- ❌ **Market demand is unvalidated** (may be <20 users)
- ❌ **Effort underestimated by 80%** (40h → 80-90h realistic)
- ❌ **Premature extraction** (wait for organic demand)
- ✅ **Architecture is sound** (if we build it)
- ✅ **Problem is real** (for those who use multi-agent workflows)

### Verdict: **CONDITIONAL GO - PHASE -1 ONLY**

1. **REQUIRED**: Complete Phase -1 (validation) before any extraction
2. **RECOMMENDED**: Path 1 (defer extraction) unless validation proves strong demand
3. **ACCEPTABLE**: Path 2 (minimal extraction) if Phase -1 succeeds
4. **CAUTION**: Path 3 (full extraction) is high risk without validation

### Core Principle

**Build demand first, extract second.**

Don't spend 80+ hours on a solution for <10 users. Validate first.

---

**Document Status**: READY FOR DECISION
**Next Step**: User research (Phase -1) OR Defer extraction (Path 1)
**Timeline**: 1 week for validation, then reassess
**Risk Level**: MEDIUM-HIGH (lowered from HIGH if validation completes)

---

*This plan incorporates critical feedback from Reviewer Agent. The goal is de-risking through validation, realistic planning, and honest assessment of market demand.*
