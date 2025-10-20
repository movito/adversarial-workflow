# Decision: Revert "Reviewer" → "Evaluator" Terminology (v0.3.2)

**Date**: 2025-10-19
**Status**: APPROVED
**Decision Maker**: document-reviewer agent + coordinator
**Impact**: Documentation-wide terminology change (~20-30 occurrences)

---

## Decision

Revert the v0.2.0 terminology change from "Evaluator" → "Reviewer" back to "Evaluator" for the aider-powered QA role in adversarial-workflow.

**New official terminology**: Author-Evaluator workflow

---

## Context

### Version History

| Version | Terminology | Rationale | Issue |
|---------|-------------|-----------|-------|
| v0.1.0 | Coordinator/Evaluator | Original design | Implied agent infrastructure |
| v0.2.0 | Author/Reviewer | Universal clarity | Created new ambiguity with agent roles |
| v0.3.2 | Author/Evaluator | Precision + agent clarity | **Current** |

### The v0.2.0 Change

In v0.2.0, we changed "Evaluator" → "Reviewer" based on Evaluator QA feedback (2025-10-15):

**Rationale**:
- "Reviewer" is universally understood (GitHub PRs, code reviews)
- "Evaluator" seemed ambiguous (evaluating what?)
- Goal: Make terminology accessible to all developers

**Implementation**:
- 73 fixes across 11 files
- Documented in: `delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md`
- Considered successful at the time

---

## Problem Statement

The "Reviewer" terminology created a **new, more serious ambiguity**:

### 1. Conflict with Agent Roles

**The Issue**:
- adversarial-workflow uses "Reviewer" for aider QA role
- Multi-agent coordination uses "document-reviewer" as an agent role name
- Both terms contain "reviewer", causing confusion

**User Confusion**:
- "Which reviewer are they talking about?"
- "Is the Reviewer an agent or just aider?"
- "Should I assign this to the document-reviewer agent?"

**Example of Ambiguity**:
```markdown
❌ CONFUSING:
"The Reviewer analyzes your documentation."
(Which reviewer? The aider QA? The document-reviewer agent?)

✅ CLEAR:
"The Evaluator analyzes your plan."
(Obviously the aider QA, not an agent)
```

### 2. Less Precise Terminology

**"Reviewer" is generic**:
- Could mean: code review, document review, PR review, peer review
- Doesn't specify WHAT is being reviewed or WHY

**"Evaluator" is specific**:
- Clearly indicates quality evaluation
- Evaluates for correctness, completeness, quality
- More precise about the role's function

### 3. Technical Misalignment

**Current state**:
- Environment variable: `EVALUATOR_MODEL` (not `REVIEWER_MODEL`)
- Config key: `evaluator_model` (not `reviewer_model`)
- Documentation says: "Reviewer"
- **Inconsistency**: Docs and code don't align

### 4. User Feedback

**Observation from coordinator**:
> "Other agents are referring to it as 'Evaluator'"

**Why?**
- "Evaluator" is the more natural, precise term
- People naturally use "evaluator" when describing quality checks
- "Reviewer" feels like a forced oversimplification

---

## Decision Rationale

### Why "Evaluator" is Better

| Factor | Reviewer | Evaluator | Winner |
|--------|----------|-----------|--------|
| **Precision** | Generic | Specific: evaluates quality | Evaluator |
| **Agent Ambiguity** | Conflicts with "document-reviewer" | No conflict | Evaluator |
| **Technical Alignment** | Misaligned (EVALUATOR_MODEL) | Aligned | Evaluator |
| **Natural Usage** | Forced, generic | Natural, precise | Evaluator |
| **Role Clarity** | Vague | Clear: evaluates for correctness | Evaluator |

### Multi-Agent Systems Context

**The Reality**:
- adversarial-workflow is increasingly used in multi-agent projects
- Agent roles have standard names: document-reviewer, test-runner, api-developer
- Using "Reviewer" for aider QA creates namespace collision

**The Solution**:
- "Evaluator" is distinct from all agent role names
- No ambiguity with document-reviewer, code-reviewer, etc.
- Clear separation: Evaluator (QA) vs document-reviewer (agent)

---

## Implementation

### Scope

**Files Updated** (~20-30 occurrences):
1. **High Priority** (7 files):
   - README.md - Main package docs
   - docs/TERMINOLOGY.md - Official standards (+ new Evaluator vs document-reviewer section)
   - QUICK_START.md - Getting started
   - docs/EXAMPLES.md - Workflow examples
   - docs/WORKFLOW_PHASES.md - Phase descriptions
   - docs/INTERACTION_PATTERNS.md - Pattern documentation
   - docs/TROUBLESHOOTING.md - Error documentation

2. **Medium Priority** (5 files):
   - adversarial_workflow/__init__.py - Package description
   - adversarial_workflow/cli.py - User-facing output (line 322)
   - adversarial_workflow/templates/README.template
   - adversarial_workflow/templates/review_implementation.sh.template
   - adversarial_workflow/templates/validate_tests.sh.template

3. **Not Changed**:
   - `EVALUATOR_MODEL` environment variable (already correct)
   - `evaluator_model` config key (already correct)
   - Agent role names: "document-reviewer" (unchanged)
   - Historical documents (preserved with notes)

### Key Addition: Evaluator vs document-reviewer Section

**Added to docs/TERMINOLOGY.md**:
- Clear distinction between two concepts
- Explains Evaluator (aider QA) vs document-reviewer (agent role)
- Why they're different systems
- When to use each term
- Examples of correct usage

This section is **critical** - it prevents future confusion!

---

## Alternatives Considered

### Alternative 1: Keep "Reviewer", Rename "document-reviewer" Agent

**Rejected because**:
- Agent role names are standard across projects
- Would break existing agent coordination setups
- "document-reviewer" is clear and established
- The problem is with generic "Reviewer", not agent names

### Alternative 2: Use "Reviewer (aider)" Every Time

**Rejected because**:
- Verbose and repetitive
- Doesn't solve technical variable misalignment
- Still less precise than "Evaluator"
- Adds cognitive load

### Alternative 3: Create New Term (e.g., "Validator", "Critic")

**Rejected because**:
- "Evaluator" already exists and is correct
- Technical variables already use "Evaluator"
- Would require more breaking changes
- "Evaluator" is precise and well-understood

---

## Migration Strategy

### Backward Compatibility

**Preserved**:
- ✅ Config file keys unchanged (`evaluator_model`)
- ✅ Environment variables unchanged (`EVALUATOR_MODEL`)
- ✅ Command names unchanged (`adversarial evaluate`)
- ✅ File structures unchanged
- ✅ API unchanged

**Changed**:
- User-facing documentation
- Output messages (cli.py line 322)
- Template comments

**Result**: Users can upgrade without any changes to their setup!

### Communication

**CHANGELOG v0.3.2 entry**:
- Explains the reversion
- Notes the Evaluator vs document-reviewer distinction
- Clarifies no breaking changes

**Historical Note**:
- Updated README.md with terminology history
- Preserves context for future developers
- Explains full evolution: Coordinator/Evaluator → Author/Reviewer → Author/Evaluator

---

## Success Criteria

### Must Have ✅

- [x] All user-facing "Reviewer" references changed to "Evaluator"
- [x] Evaluator vs document-reviewer distinction documented
- [x] Technical variables unchanged (EVALUATOR_MODEL)
- [x] Examples updated with "Evaluator" terminology
- [x] No new ambiguity introduced
- [x] Historical documents preserved

### Should Have ✅

- [x] CLI output updated (cli.py:322)
- [x] Template files updated
- [x] TERMINOLOGY.md updated comprehensively
- [x] QUICK_START.md uses Evaluator
- [x] EXAMPLES.md workflow examples use Evaluator

### Nice to Have ✅

- [x] Decision document created (this file)
- [x] CHANGELOG entry for v0.3.2

---

## Risks & Mitigation

### Risk 1: User Confusion During Transition

**Risk**: Users reading old docs find "Reviewer", new docs say "Evaluator"

**Mitigation**:
- Historical note in README.md explains full history
- CHANGELOG documents the change clearly
- TERMINOLOGY.md explains evolution
- No breaking changes to commands or config

### Risk 2: Future Terminology Drift

**Risk**: Another terminology change in v0.4.0?

**Mitigation**:
- TERMINOLOGY.md v2.0 is comprehensive
- Evaluator vs document-reviewer section prevents agent confusion
- Technical alignment (EVALUATOR_MODEL) reinforces consistency
- Multi-agent context considered

---

## Lessons Learned

### What Worked (v0.2.0)

- ✅ Systematic terminology audit
- ✅ Comprehensive documentation updates
- ✅ Clear decision record
- ✅ Backward compatibility preservation

### What We Missed (v0.2.0)

- ❌ Didn't anticipate multi-agent system integration
- ❌ Didn't consider agent role namespace collision
- ❌ Focused on universal understanding, lost precision
- ❌ Didn't align documentation with technical naming

### Improvements (v0.3.2)

- ✅ Consider multi-agent context from the start
- ✅ Check for naming conflicts across all systems
- ✅ Align documentation with technical variable names
- ✅ Prioritize precision over perceived simplicity
- ✅ Document distinctions explicitly (Evaluator vs document-reviewer)

---

## Conclusion

**Decision**: APPROVED

**Effective Date**: 2025-10-19 (v0.3.2)

**Summary**:
- Reverting "Reviewer" → "Evaluator" eliminates ambiguity with agent roles
- "Evaluator" is more precise and aligns with technical naming
- No breaking changes - fully backward compatible
- Comprehensive documentation update including new Evaluator vs document-reviewer section

**Irony**: This decision was made by the document-reviewer agent, fixing the very confusion about its own name! 📖

---

## References

- **v0.2.0 Decision**: `delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md`
- **Task File**: `delegation/tasks/active/TASK-TERMINOLOGY-001-REVERT-TO-EVALUATOR.md`
- **Handoff Document**: `delegation/handoffs/HANDOFF-TO-DOCUMENT-REVIEWER-TERMINOLOGY.md`
- **Evaluator QA (2025-10-15)**: `EVALUATOR-QA-RESPONSE.txt`
- **Terminology Audit**: `audit-results/6A2-TERMINOLOGY-AUDIT.md`

---

**Document Owner**: document-reviewer agent
**Approved By**: coordinator
**Implementation**: document-reviewer agent (2025-10-19)
**Status**: ✅ COMPLETE
