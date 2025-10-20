# ADR-0001: Adversarial Workflow Pattern

**Status**: Accepted

**Date**: 2025-10-15 (v0.1.0)

**Deciders**: Fredrik Matheson

## Context

When using AI coding assistants (like Claude Code, Cursor, Aider, or GPT-4), a critical quality problem emerges: **phantom work**. This occurs when:

1. **AI claims to implement features** but produces non-functional code
2. **Code looks convincing** with proper structure, comments, and naming
3. **Developers trust the output** without sufficient verification
4. **Problems only surface later** during testing or production use
5. **Token costs accumulate** from lengthy context windows with trial-and-error debugging

This problem became apparent during the development of the [thematic-cuts](https://github.com/movito/thematic-cuts) project, where initial test pass rates were only 85.1% despite AI assertions that implementations were complete and correct.

### Forces at Play

Several competing concerns influenced this decision:

**Quality Requirements:**
- Need to prevent non-functional code from being committed
- Must catch "phantom work" before it accumulates
- Want objective verification independent of implementation claims
- Require systematic approach that scales across projects

**Efficiency Requirements:**
- AI assistants can be extremely productive when guided correctly
- Token costs for large codebases can be prohibitive ($0.50-$2.00 per evaluation with full context)
- Multiple rounds of debugging waste time and money
- Need to reduce context window size without losing quality

**Workflow Requirements:**
- Must integrate with existing development practices (git, tests, task management)
- Should work with any AI tool or manual coding
- Cannot require specialized IDE or proprietary agent systems
- Must be non-destructive to existing projects

**Human Factors:**
- Developers naturally trust convincing-looking code
- Easy to skip verification steps without enforcement
- Need clear feedback loops and decision points
- Must balance rigor with developer experience

### Problem Statement

How do we systematically prevent phantom work while maintaining development velocity and controlling token costs?

Single-pass AI development approaches fail because:
- **No independent verification**: Same AI that produced the code reviews it
- **Context explosion**: Full codebase context on every interaction
- **No phase gates**: Easy to skip validation steps
- **No audit trail**: Hard to identify where problems originated

## Decision

Implement an **adversarial multi-stage workflow** that separates **implementation (Author)** from **verification (Evaluator)** across five distinct phases with explicit approval gates.

### Core Principles

1. **Adversarial Separation**: Implementation and review use **different AI models** (or same model with fresh context) to ensure independent verification
2. **Phase Gates**: Each phase produces artifacts that must be approved before proceeding
3. **Minimal Context**: Each phase uses only the context it needs (plan, diff, test results) rather than full codebase
4. **Git-Centric**: All verification happens through git diffs and conventional development artifacts
5. **Tool-Agnostic**: Works with any coding method (AI assistants, manual coding, etc.)

### Five-Phase Structure

**Phase 0: Investigation (Optional)**
- **Who**: Author (any developer or AI)
- **Input**: Task requirements
- **Output**: Investigation findings document
- **Purpose**: Research and clarify before planning

**Phase 1: Plan Evaluation**
- **Who**: Evaluator (independent AI)
- **Input**: Task description + proposed implementation plan
- **Output**: Plan approval or critique with revisions
- **Purpose**: Catch architectural issues before implementation starts
- **Command**: `adversarial evaluate tasks/feature.md`

**Phase 2: Implementation**
- **Who**: Author (any developer or AI)
- **Input**: Approved plan
- **Output**: Git commits with working code
- **Purpose**: Implement according to approved plan
- **Method**: Any approach (Claude Code, Cursor, Aider, manual coding)

**Phase 3: Code Review**
- **Who**: Evaluator (independent AI)
- **Input**: Git diff + original plan
- **Output**: Code review with phantom work detection
- **Purpose**: Verify implementation matches plan and actually works
- **Command**: `adversarial review`

**Phase 4: Test Validation**
- **Who**: Evaluator (independent AI)
- **Input**: Test execution results
- **Output**: Test analysis and approval
- **Purpose**: Objective analysis of test outcomes
- **Command**: `adversarial validate "npm test"`

**Phase 5: Final Approval**
- **Who**: Author (human developer)
- **Input**: All phase artifacts (plan, review, tests)
- **Output**: Final commit or iteration decision
- **Purpose**: Human judgment on whether to ship or iterate

### Token Efficiency Strategy

Each phase uses **minimal context**:
- Phase 1: Task + plan only (~2K tokens)
- Phase 3: Diff + plan only (~5K-10K tokens, not full codebase)
- Phase 4: Test results only (~1K-5K tokens)

**Result**: 10-20x token reduction vs. standard Aider usage with full codebase context.

### Adversarial Independence

Two approaches for independence:

1. **Different Models** (recommended):
   - Author: Anthropic Claude 3.5 Sonnet (implementation strength)
   - Evaluator: OpenAI GPT-4o (critical analysis strength)
   - Cost: ~$0.02-0.10 per complete workflow

2. **Same Model, Fresh Context**:
   - Use one API key but fresh aider sessions per phase
   - No shared context between phases
   - Cost: ~$0.05-0.15 per complete workflow

## Consequences

### Positive

**Quality Improvements:**
- ✅ **96.9% test pass rate** achieved in thematic-cuts (up from 85.1%)
- ✅ **Phantom work detection**: Independent review catches non-functional code
- ✅ **Early error detection**: Plan evaluation prevents architectural mistakes before implementation
- ✅ **Objective test analysis**: No AI "explaining away" test failures

**Efficiency Improvements:**
- ✅ **10-20x token reduction**: Minimal context per phase vs. full codebase
- ✅ **Faster iterations**: Catching issues early reduces rework
- ✅ **Clear decision points**: Know when to proceed vs. iterate
- ✅ **Audit trail**: Complete record of decisions and reviews

**Developer Experience:**
- ✅ **Tool-agnostic**: Works with any coding method
- ✅ **Non-destructive**: Integrates without changing project structure
- ✅ **Git-centric**: Uses familiar development artifacts
- ✅ **Configurable**: Adapts to any test framework or task system

### Negative

**Process Overhead:**
- ⚠️ **More steps**: 5 phases vs. single-pass development
- ⚠️ **Multiple commands**: Must run evaluate, review, validate explicitly
- ⚠️ **Context switching**: Switching between Author and Evaluator sessions
- ⚠️ **Learning curve**: Understanding when/how to use each phase

**Resource Requirements:**
- ⚠️ **Two API keys recommended**: Better results with Anthropic + OpenAI
- ⚠️ **Cost per workflow**: $0.02-0.15 per complete cycle (though much cheaper than debugging phantom work)
- ⚠️ **Bash requirement**: Scripts use Bash (no native Windows support)
- ⚠️ **Aider dependency**: Requires aider-chat for AI interactions

**Workflow Changes:**
- ⚠️ **Discipline required**: Easy to skip phases without enforcement
- ⚠️ **Initial setup**: Requires API keys, configuration, aider installation
- ⚠️ **Documentation**: Must document plans before implementation

### Neutral

**Architectural Implications:**
- 📊 Scripts are bash-based (see ADR-0002)
- 📊 Configuration uses YAML + .env pattern (see ADR-0007)
- 📊 Templates for initialization (see ADR-0004)
- 📊 Platform limited to Unix-like systems (macOS, Linux, WSL)

**Adoption Patterns:**
- 📊 Can adopt gradually (use some phases, not all)
- 📊 Works alongside existing workflows (doesn't replace current tools)
- 📊 Scales from solo developers to teams

## Real-World Results

### thematic-cuts Project (Primary Case Study)

**Before adversarial-workflow:**
- Test pass rate: 85.1%
- Frequent phantom work issues
- High token costs from debugging cycles
- Unclear when features were "really done"

**After adversarial-workflow:**
- Test pass rate: 96.9% (+11.8 percentage points)
- Phantom work caught in Phase 3 review
- 10-20x token cost reduction
- Clear quality gates and audit trail

**Project stats:**
- ~15,000 lines of Python code
- Complex media processing (FFmpeg, audio analysis)
- Multi-agent development with coordinator oversight
- 3 months of active development

## Related Decisions

- ADR-0002: Bash and Aider foundation (technical implementation)
- ADR-0003: Multi-stage workflow design (detailed phase structure)
- ADR-0004: Template-based initialization (setup approach)
- ADR-0005: Agent coordination extension layer (optional multi-agent support)

## References

- [thematic-cuts project](https://github.com/movito/thematic-cuts) - Primary dogfooding case study
- [Aider documentation](https://aider.chat/docs/) - AI pair programming tool
- Michael Nygard's "Documenting Architecture Decisions" - ADR format inspiration
- ["Phantom work" patterns](docs/TROUBLESHOOTING.md) - Common failure modes

## Revision History

- 2025-10-15: Initial decision (v0.1.0)
- 2025-10-20: Documented as ADR-0001
