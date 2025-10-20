# ADR-0003: Multi-Stage Workflow Design

**Status**: Accepted

**Date**: 2025-10-15 (v0.1.0)

**Deciders**: Fredrik Matheson

## Context

The adversarial workflow pattern (ADR-0001) requires a concrete implementation structure to:
1. Prevent phantom work through multiple verification points
2. Control AI token costs (models charge per token, ~$5-15 per 1M tokens)
3. Provide clear decision points for proceeding or iterating
4. Create an audit trail of all decisions and reviews

### The Token Cost Problem

AI development with full codebase context is expensive:

**Standard Aider pattern** (loading entire codebase):
- Typical codebase: ~100 files = 200,000 tokens
- 10-message conversation: 200K tokens × 10 = 2M tokens input
- Cost: ~$10-15 per task
- **20 tasks/month = $200-300/month**

**The core problem**: Repeated full-codebase context in every AI interaction.

### The Phantom Work Problem

Different types of phantom work emerge at different stages:

**Planning stage**: Incomplete or unrealistic plans that seem thorough
**Implementation stage**: Code with TODOs/comments instead of real functionality
**Review stage**: Missing the above because same AI reviews its own work
**Testing stage**: Explaining away test failures instead of acknowledging issues

### Forces at Play

**Quality Requirements:**
- Need multiple verification points to catch different types of issues
- Want independent review (not same AI reviewing its own work)
- Must validate that code actually works (not just looks right)
- Require clear pass/fail criteria at each stage

**Cost Requirements:**
- Minimize token usage per phase
- Avoid repeated full-codebase context
- Single-shot AI invocations (not long conversations)
- Only send the context each phase actually needs

**Developer Experience:**
- Clear progression through workflow stages
- Obvious decision points (proceed vs iterate)
- Flexibility to use any implementation method
- Reasonable time investment per task

**Workflow Integration:**
- Must work with existing git workflows
- Should integrate with existing test frameworks
- Compatible with any task management system
- Non-disruptive to current development practices

### Why Not Simpler Approaches?

**Single-pass review** (Plan → Implement → Review → Done):
- ❌ No objective validation (tests could be ignored)
- ❌ No pre-implementation design review
- ❌ Test failures often "explained away" without seeing actual output

**Two-stage** (Implement → Review):
- ❌ No plan evaluation before implementation
- ❌ Catch design flaws after code is written (waste)
- ❌ No separate test validation

**Seven+ stages**:
- ❌ Diminishing returns on additional verification
- ❌ Process becomes bureaucratic
- ❌ Developer fatigue and process abandonment

## Decision

Implement a **five-stage workflow** with explicit phase gates and token-optimized single-shot invocations.

### Five Phases

**Phase 0: Investigation (Optional)**
- **Who**: Author (developer or AI)
- **Input**: Task requirements
- **Output**: Investigation findings document
- **Purpose**: Research complex bugs, clarify unclear requirements
- **When to use**: Complex tasks, unfamiliar code, unclear requirements
- **Token cost**: Varies (codebase exploration, ~20-100K tokens)
- **Time**: 15-60 minutes

**Phase 1: Plan Evaluation**
- **Who**: Evaluator (independent AI via aider)
- **Input**: Task description + proposed implementation plan
- **Output**: Plan approval with critique and suggestions
- **Purpose**: Catch architectural issues before implementation
- **Command**: `adversarial evaluate tasks/feature.md`
- **Token cost**: ~5-15K tokens (plan only, no codebase)
- **Time**: 5-15 minutes
- **Gate**: Must address Evaluator feedback before implementing

**Phase 2: Implementation**
- **Who**: Author (developer or AI assistant)
- **Input**: Approved plan from Phase 1
- **Output**: Git commits with working code
- **Purpose**: Implement according to validated plan
- **Method**: Any approach (Claude Code, Cursor, Aider, manual)
- **Token cost**: Varies by method (Author's choice)
- **Time**: 30-120 minutes
- **Gate**: Must have clean git commits before review

**Phase 3: Code Review**
- **Who**: Evaluator (independent AI via aider)
- **Input**: Git diff + original plan
- **Output**: Code review with phantom work detection
- **Purpose**: Verify implementation matches plan and is complete
- **Command**: `adversarial review`
- **Token cost**: ~10-25K tokens (diff + plan, no full codebase)
- **Time**: 5-15 minutes
- **Gate**: Must address review findings before testing

**Phase 4: Test Validation**
- **Who**: Evaluator (independent AI via aider)
- **Input**: Test execution results
- **Output**: Test analysis and approval
- **Purpose**: Objective validation that code works
- **Command**: `adversarial validate "npm test"`
- **Token cost**: ~5-15K tokens (test output only)
- **Time**: 5-10 minutes
- **Gate**: Tests must pass or clear plan for fixes

**Phase 5: Final Approval**
- **Who**: Author (human developer)
- **Input**: All phase artifacts (plan, review, tests, logs)
- **Output**: Final commit decision or iteration plan
- **Purpose**: Human judgment on shipping vs. iterating
- **Time**: 10-20 minutes
- **Gate**: Developer satisfaction with all outputs

### Token Efficiency Strategy

Each phase uses **minimal context** through three techniques:

**1. Single-Shot Invocations**

No multi-message conversations. One prompt, one response:

```bash
# ❌ EXPENSIVE: Interactive conversation (repeats context)
aider --files task.md
> "Review the plan"
> "What about edge cases?"
> "Any security concerns?"
# Cost: 3× the tokens

# ✅ CHEAP: Single comprehensive prompt
aider --read task.md --message "Review this plan for:
1. Completeness (all requirements covered)
2. Edge cases (error handling)
3. Security concerns (validation, auth)
Provide specific feedback." --yes
# Cost: 1× the tokens
```

**2. Read-Only Context (--read vs --files)**

Use `--read` for reference materials (not edited):

```bash
# Phase 1: Evaluate plan
aider --read tasks/feature.md \
      --message "Evaluate this implementation plan..." \
      --yes
# Plan is read-only reference, not in edit context

# Phase 3: Review implementation
aider --read tasks/feature.md \
      --read implementation.diff \
      --message "Review this implementation against plan..." \
      --yes
# Both files read-only, no persistent context
```

**Benefits**:
- Files sent once, not repeated per message
- No accumulating context across conversation
- ~10-20x cheaper than --files

**3. Minimal Necessary Context**

Only send what each phase needs:

| Phase | Context Sent | Token Count | What's Excluded |
|-------|--------------|-------------|-----------------|
| 1 | Plan only | 5-15K | No codebase |
| 3 | Diff + plan | 10-25K | No full codebase, only changed lines |
| 4 | Test output | 5-15K | No code, just results |

**Total per task**: 20-40K tokens (~$0.20-0.40)

**Compare to standard**: 100-500K tokens (~$1-5) = **10-20x savings**

### Why Five Phases Specifically?

**Why not fewer:**
- **No Phase 1**: Design flaws caught after implementation (wasted effort)
- **No Phase 3**: No code review means phantom work undetected
- **No Phase 4**: Tests could pass but AI doesn't verify objectively
- **Combine 3+4**: Different concerns (code quality vs functionality)

**Why not more:**
- **Security review**: Can be part of Phase 3 code review
- **Performance testing**: Can be part of Phase 4 validation
- **Integration testing**: Can be part of Phase 4 validation
- **Documentation review**: Can be part of Phase 3 or separate if needed

**Five phases hit the sweet spot**: Enough gates to catch issues, not so many that process becomes burdensome.

### Phase Gate Pattern

Each phase has explicit **approval gates**:

```
Phase 1 (Evaluate) → [GATE: Address feedback] → Phase 2 (Implement)
Phase 2 (Implement) → [GATE: Clean commits] → Phase 3 (Review)
Phase 3 (Review) → [GATE: Fix issues] → Phase 4 (Validate)
Phase 4 (Validate) → [GATE: Tests pass] → Phase 5 (Approve)
Phase 5 (Approve) → [GATE: Developer OK] → Final commit
```

**Benefits:**
- Clear decision points (can't skip ahead)
- Prevents rushing through process
- Creates audit trail
- Forces addressing issues before proceeding

**Flexibility:**
- Can iterate within any phase
- Can go backwards if needed
- Optional Phase 0 for complex tasks
- Can run multiple cycles if first attempt fails

## Consequences

### Positive

**Quality Improvements:**
- ✅ **Multiple verification points**: Catches different issue types at optimal stages
- ✅ **Phantom work detection**: Phase 3 explicitly checks for TODOs vs real code
- ✅ **Objective test validation**: Phase 4 prevents "explaining away" failures
- ✅ **Early design review**: Phase 1 catches architectural issues before coding
- ✅ **96.9% test pass rate**: Proven in thematic-cuts (up from 85.1%)

**Cost Efficiency:**
- ✅ **10-20x token reduction**: Minimal context per phase vs full codebase
- ✅ **Single-shot invocations**: No multi-message conversations
- ✅ **$0.20-0.40 per task**: Vs $1-5 with standard approaches
- ✅ **Predictable costs**: Clear token budgets per phase

**Developer Experience:**
- ✅ **Clear progression**: Five discrete stages with obvious transitions
- ✅ **Explicit gates**: Know when to proceed vs iterate
- ✅ **Flexible implementation**: Phase 2 uses any coding method
- ✅ **Reasonable time**: 1.5-4 hours total per task

**Process Benefits:**
- ✅ **Audit trail**: Complete record of all phases in logs
- ✅ **Decision documentation**: Why proceed or iterate captured
- ✅ **Git-centric**: Uses familiar git diff and commits
- ✅ **Tool-agnostic**: Works with any implementation approach

### Negative

**Process Overhead:**
- ⚠️ **Five stages**: More steps than single-pass development
- ⚠️ **Manual phase transitions**: Must explicitly run each command
- ⚠️ **Discipline required**: Easy to skip phases without enforcement
- ⚠️ **Learning curve**: Understanding when/how to use each phase

**Time Investment:**
- ⚠️ **1.5-4 hours per task**: Longer than "quick fix" approaches
- ⚠️ **Context switching**: Moving between Author and Evaluator sessions
- ⚠️ **Multiple reviews**: Plan, code, and tests all reviewed separately

**Complexity:**
- ⚠️ **Five commands to remember**: `evaluate`, `review`, `validate` plus manual phases
- ⚠️ **Log management**: Must track multiple log files per task
- ⚠️ **Phase coordination**: Keeping track of which phase you're in

**Not Always Necessary:**
- ⚠️ **Overkill for tiny tasks**: Trivial fixes don't need all phases
- ⚠️ **Urgent hotfixes**: Five phases may be too slow for production incidents
- ⚠️ **Experimental code**: Prototypes don't need full rigor

### Neutral

**When to Use All Phases:**
- 📊 Feature development
- 📊 Bug fixes affecting multiple files
- 📊 Refactoring efforts
- 📊 Any code going to production

**When to Skip Phases:**
- 📊 Trivial fixes (typos, comments)
- 📊 Urgent hotfixes (use judgment)
- 📊 Experimental prototypes
- 📊 Documentation-only changes

**Adaptation Patterns:**
- 📊 Can iterate within phases (multiple reviews OK)
- 📊 Can combine Phase 0+1 for simple tasks
- 📊 Can add specialized phases if needed (security, performance)
- 📊 Can automate phase transitions (future enhancement)

## Alternatives Considered

### Alternative 1: Three-Phase Workflow (Plan → Implement → Review)

**Structure:**
- Phase 1: Plan and implement together
- Phase 2: Code review
- Phase 3: Final approval

**Rejected because:**
- ❌ No separate plan evaluation (catch design issues late)
- ❌ No objective test validation (tests could be ignored)
- ❌ Combines planning and implementation (less clear separation)
- ❌ Review phase must catch both design and implementation issues

### Alternative 2: Seven-Phase Workflow

**Structure:**
- Phase 0: Investigation
- Phase 1: Plan design
- Phase 2: Plan review
- Phase 3: Implementation
- Phase 4: Code review
- Phase 5: Test implementation
- Phase 6: Test validation
- Phase 7: Final approval

**Rejected because:**
- ❌ Too many phases (developer fatigue)
- ❌ Diminishing returns (Phases 5+6 vs just Phase 4)
- ❌ Process becomes bureaucratic
- ❌ Longer time investment per task
- ❌ Phases 1+2 can be combined (evaluate includes review)

### Alternative 3: Continuous Conversation (No Phases)

**Structure:**
- Single long aider conversation with full codebase context
- AI reviews its own work as it goes

**Rejected because:**
- ❌ Massive token costs (200K+ tokens × messages)
- ❌ No independent review (AI reviews its own work)
- ❌ No clear decision points
- ❌ Phantom work often undetected
- ❌ $10-15 per task vs $0.20-0.40

### Alternative 4: Two-Phase (Implement → Review)

**Structure:**
- Phase 1: Implement feature
- Phase 2: Review and test

**Rejected because:**
- ❌ No pre-implementation plan review
- ❌ Waste effort on poorly designed implementations
- ❌ No separate test validation
- ❌ Review + testing combined (different concerns)

## Real-World Results

### thematic-cuts Project

**Before adversarial workflow:**
- Single-pass implementation with review
- Test pass rate: 85.1%
- Frequent phantom work issues
- High rework due to design issues discovered late

**After five-phase workflow:**
- Phase 1 catches design issues early
- Phase 3 detects phantom work
- Phase 4 validates functionality objectively
- Test pass rate: 96.9% (+11.8 percentage points)
- 10-20x token cost reduction

**Typical task timeline:**
- Phase 0: 30 min (investigation, when needed)
- Phase 1: 10 min (plan evaluation)
- Phase 2: 60 min (implementation)
- Phase 3: 10 min (code review)
- Phase 4: 10 min (test validation)
- Phase 5: 15 min (final review)
- **Total: ~2 hours with high confidence in quality**

## Related Decisions

- ADR-0001: Adversarial workflow pattern (why independent verification)
- ADR-0002: Bash and Aider foundation (how phases are implemented)
- ADR-0004: Template-based initialization (how phase scripts are installed)
- ADR-0007: YAML + .env configuration (how phase behavior is configured)

## References

- [WORKFLOW_PHASES.md](../../WORKFLOW_PHASES.md) - Detailed phase documentation
- [TOKEN_OPTIMIZATION.md](../../TOKEN_OPTIMIZATION.md) - Token efficiency strategies
- [thematic-cuts project](https://github.com/movito/thematic-cuts) - Real-world case study
- [Aider --read documentation](https://aider.chat/docs/usage/modes.html) - Read-only file access

## Revision History

- 2025-10-15: Initial decision (v0.1.0)
- 2025-10-20: Documented as ADR-0003
