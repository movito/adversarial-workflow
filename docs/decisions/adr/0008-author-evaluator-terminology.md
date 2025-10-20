# ADR-0008: Author-Evaluator Terminology (Reversion from "Reviewer")

**Status**: Accepted

**Date**: 2025-10-19 (v0.3.2)

**Deciders**: Fredrik Matheson (with recommendations from document-reviewer agent via dogfooding)

## Context

### Terminology Evolution

The workflow pattern has undergone terminology changes across versions:

| Version | Terminology | Issue |
|---------|-------------|-------|
| v0.1.0 | Coordinator/Evaluator | Implied agent infrastructure |
| v0.2.0 | Author/Reviewer | Created ambiguity with agent roles |
| v0.3.2 | **Author/Evaluator** | Current |

### The v0.2.0 Change

In v0.2.0 (2025-10-16), we changed "Evaluator" → "Reviewer" to improve accessibility:

**Rationale:**
- "Reviewer" is universally understood (GitHub PRs, code review culture)
- "Evaluator" seemed potentially ambiguous
- Goal: Make terminology accessible to all developers

**Implementation:** 73 fixes across 11 files, documented in `TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md`

### Problem with "Reviewer"

The v0.2.0 change introduced a **new, more serious ambiguity** that became apparent after v0.3.0 added agent coordination:

**1. Namespace Collision with Agent Roles**

adversarial-workflow v0.3.0+ includes optional agent coordination with standard agent roles like:
- `coordinator` - Task management
- `document-reviewer` - Documentation review
- `test-runner` - Test execution
- etc.

When documentation says "Reviewer," it's unclear whether this refers to:
- The aider-powered QA role in the adversarial workflow, OR
- The `document-reviewer` agent role in multi-agent coordination

**Example of ambiguity:**
```markdown
❌ CONFUSING:
"The Reviewer analyzes your documentation."
(The aider QA? The document-reviewer agent?)

✅ CLEAR:
"The Evaluator analyzes your plan."
(Obviously the aider QA, not an agent)
```

**2. Loss of Precision**

- "Reviewer" is generic: Could mean code review, document review, PR review, peer review
- "Evaluator" is specific: Evaluates for quality, correctness, completeness
- "Reviewer" doesn't specify WHAT is reviewed or WHY

**3. Technical Misalignment**

The codebase already uses "Evaluator" in technical naming:
- Environment variable: `EVALUATOR_MODEL` (not `REVIEWER_MODEL`)
- Config key: `evaluator_model` (not `reviewer_model`)
- Documentation (v0.2.0): "Reviewer"

This created inconsistency between code and documentation.

**4. Natural Usage Patterns**

User observation during dogfooding:
> "Other agents are referring to it as 'Evaluator'"

Developers naturally gravitate toward "Evaluator" when describing the quality evaluation role, suggesting "Reviewer" felt forced.

### Forces at Play

**Clarity Requirements:**
- Must avoid ambiguity with agent role names
- Need precise terminology that indicates function
- Should align with technical implementation

**Consistency Requirements:**
- Documentation should match code variable names
- Terminology should work in single-agent and multi-agent contexts
- Must maintain backward compatibility

**Usability Requirements:**
- Should be easily understood by new users
- Must not create confusion with other roles
- Should feel natural in conversation

## Decision

Revert "Reviewer" → "Evaluator" for the aider-powered QA role in adversarial-workflow.

**Official terminology:** **Author-Evaluator workflow**

### Key Changes

**Updated files** (~20-30 occurrences across 12 files):
- Core docs: README.md, QUICK_START.md, docs/TERMINOLOGY.md
- Workflow docs: docs/EXAMPLES.md, docs/WORKFLOW_PHASES.md, docs/INTERACTION_PATTERNS.md, docs/TROUBLESHOOTING.md
- Code: adversarial_workflow/__init__.py, adversarial_workflow/cli.py (line 322)
- Templates: README.template, review_implementation.sh.template, validate_tests.sh.template

**Preserved** (for backward compatibility):
- Config key: `evaluator_model` (unchanged)
- Environment variable: `EVALUATOR_MODEL` (unchanged)
- Command names: `adversarial evaluate` (unchanged)
- Agent role names: `document-reviewer` (unchanged)

**Added** (to prevent future confusion):
- New section in docs/TERMINOLOGY.md: "Evaluator vs document-reviewer"
- Explains distinction between Evaluator (aider QA) and document-reviewer (agent role)
- Clarifies these are separate systems with different purposes

## Consequences

### Positive

**Clarity:**
- ✅ **No ambiguity** with agent role names (document-reviewer, code-reviewer, etc.)
- ✅ **Precise terminology**: "Evaluator" clearly indicates quality evaluation
- ✅ **Natural usage**: Aligns with how people actually refer to the role
- ✅ **Multi-agent ready**: Works cleanly in projects using agent coordination

**Consistency:**
- ✅ **Technical alignment**: Documentation now matches code (`EVALUATOR_MODEL`)
- ✅ **Single source of truth**: TERMINOLOGY.md comprehensively defines all terms
- ✅ **Clear distinctions**: New section explicitly differentiates Evaluator from agent roles

**Maintainability:**
- ✅ **Future-proof**: Considered multi-agent context from the start
- ✅ **No breaking changes**: Config, environment, commands unchanged
- ✅ **Smooth upgrade**: Users can upgrade to v0.3.2 without any configuration changes

### Negative

**Transition Costs:**
- ⚠️ **Second terminology change**: May confuse users who learned v0.2.0 terminology
- ⚠️ **Documentation churn**: Updated ~20-30 references across 12 files
- ⚠️ **Learning curve**: Users must update mental model if they read v0.2.0 docs

**Perception:**
- ⚠️ **Indecisiveness appearance**: Two terminology changes in quick succession
- ⚠️ **Complexity perception**: Some users might find "Evaluator" less immediately intuitive than "Reviewer"

### Neutral

**Version History:**
- 📊 v0.1.0: Coordinator/Evaluator
- 📊 v0.2.0: Author/Reviewer (4 days)
- 📊 v0.3.2: Author/Evaluator (current)

**Documentation:**
- 📊 TERMINOLOGY.md v2.0 includes comprehensive evolution history
- 📊 CHANGELOG entry explains rationale for reversion
- 📊 Historical documents preserved with notes

## Alternatives Considered

### Alternative 1: Keep "Reviewer", Rename Agent Roles

**Considered:** Change `document-reviewer` → `doc-agent` or similar

**Rejected because:**
- Agent role names are standard across projects
- Would break existing agent coordination setups
- "document-reviewer" is clear and established
- The problem is with the generic "Reviewer" term, not agent names

### Alternative 2: Use "Reviewer (aider)" Everywhere

**Considered:** Always qualify as "Reviewer (aider)" to disambiguate

**Rejected because:**
- Verbose and repetitive throughout documentation
- Doesn't solve technical variable name misalignment
- Still less precise than "Evaluator"
- Adds cognitive load without improving clarity

### Alternative 3: Introduce New Term

**Considered:** "Validator", "Critic", "Analyst", etc.

**Rejected because:**
- "Evaluator" already exists in codebase and is correct
- Technical variables already use EVALUATOR_MODEL
- Would require more extensive breaking changes
- "Evaluator" is precise, well-understood, and accurate

## Lessons Learned

### What We Missed in v0.2.0

- ❌ Didn't anticipate multi-agent system integration (v0.3.0 added agent coordination)
- ❌ Didn't check for namespace collisions with agent role names
- ❌ Prioritized perceived accessibility over precision
- ❌ Didn't align documentation with existing technical naming

### Improvements Applied in v0.3.2

- ✅ Consider multi-agent context explicitly
- ✅ Check for naming conflicts across all systems
- ✅ Align documentation with technical implementation
- ✅ Prioritize precision over perceived simplicity
- ✅ Document distinctions explicitly (new TERMINOLOGY.md section)
- ✅ Preserve backward compatibility (config/env/commands unchanged)

### Process Note

This decision emerged from dogfooding adversarial-workflow on itself:
- document-reviewer agent identified the ambiguity during multi-agent work
- coordinator agent validated the concern
- Implemented using the same adversarial workflow the tool provides
- **Irony:** The `document-reviewer` agent fixed confusion about its own name!

## Related Decisions

- ADR-0001: Adversarial workflow pattern (why Author/Evaluator roles exist)
- ADR-0005: Agent coordination extension layer (introduced agent role names)
- Previous decision: `delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md` (v0.2.0 change to "Reviewer")

## References

- [v0.2.0 terminology decision](../archive/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md)
- [TERMINOLOGY.md](../../TERMINOLOGY.md) - Official terminology standards (v2.0)
- [CHANGELOG.md](../../../CHANGELOG.md) - v0.3.2 entry
- [Multi-agent agent coordination](../../AGENT_INTEGRATION.md)

## Revision History

- 2025-10-19: Initial decision (v0.3.2)
- 2025-10-20: Converted to ADR-0008 format
