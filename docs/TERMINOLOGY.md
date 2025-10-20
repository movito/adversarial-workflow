# Adversarial Workflow Terminology

**Version**: 2.0 (Author/Evaluator)
**Last Updated**: 2025-10-19
**Status**: Official Standards

---

## Purpose

This document defines the official terminology for the adversarial-workflow package. Use these terms consistently across all documentation, code, and user-facing content.

---

## Core Concepts

### ✅ Official Terms (Use These)

#### Author

**Definition**: The person or tool that creates work products (plans, code, implementations).

**Use When**:
- Describing who creates implementation plans
- Describing who writes code
- Describing the creator role in the workflow

**Examples**:
- ✅ "The Author creates an implementation plan"
- ✅ "You (the Author) implement according to the plan"
- ✅ "The Author addresses feedback from the review"

**Technical Reality**:
- Could be you (manual coding)
- Could be Claude Code, Cursor, Copilot, aider
- Could be any AI assistant or development tool
- Could be any combination of the above
- Just means: whoever writes the files

---

#### Evaluator

**Definition**: The independent analysis stage that evaluates the Author's work for quality and correctness.

**Use When**:
- Describing the quality evaluation function
- Describing plan evaluation
- Describing test validation

**Examples**:
- ✅ "The Evaluator (aider + GPT-4o) analyzes the plan"
- ✅ "Aider evaluates your git diff for completeness"
- ✅ "The Evaluator validates test results"

**Technical Reality**:
- This is aider running with a specific prompt
- Command: `aider --model gpt-4o --message "review prompt"`
- NOT a persistent agent or special software
- NOT infrastructure you need to configure
- Different prompt for each phase (evaluate, review, validate)

---

#### Author-Evaluator Workflow

**Definition**: The multi-stage verification pattern where the Author creates work and the Evaluator independently analyzes it.

**Use When**:
- Describing the overall pattern
- Explaining the adversarial aspect
- Documenting workflow phases

**Examples**:
- ✅ "The Author-Evaluator workflow prevents phantom work"
- ✅ "Multi-stage Author-Evaluator verification"
- ✅ "Independent evaluation at each stage"

**Why "Adversarial"**:
- The Evaluator is incentivized to find problems
- Independent perspective catches issues the Author might miss
- Multiple verification stages prevent incomplete work
- "Adversarial" describes the relationship, not hostility

---

## Evaluator vs document-reviewer

**CRITICAL DISTINCTION**: These are completely separate concepts in different systems!

### Evaluator (adversarial-workflow QA role)

**What it is**:
- The aider-powered quality check in adversarial-workflow
- A simple CLI command: `aider --model gpt-4o --message "review prompt"`
- Provides critical feedback on plans, implementations, and tests

**What it is NOT**:
- NOT an agent or infrastructure
- NOT a persistent system
- NOT related to multi-agent coordination
- NOT the same as "document-reviewer" agent

**When to use this term**:
- Describing the adversarial-workflow QA phases
- Explaining plan evaluation, code review, test validation
- Technical documentation about the package

**Examples**:
- ✅ "The Evaluator analyzes your plan for completeness"
- ✅ "Run `adversarial evaluate` to get Evaluator feedback"
- ✅ "Evaluator uses GPT-4o to critique your implementation"

---

### document-reviewer (agent coordination role)

**What it is**:
- An agent role in the multi-agent coordination system
- Entry in agent-handoffs.json (one of 8 roles)
- Handles documentation quality and consistency in agent-based projects

**What it is NOT**:
- NOT part of adversarial-workflow QA
- NOT related to the Evaluator role
- NOT the same as "code review" or "plan evaluation"

**When to use this term**:
- Referring to agent coordination context
- Describing agent roles in agent-handoffs.json
- Discussing multi-agent task delegation

**Examples**:
- ✅ "Assign this task to the document-reviewer agent"
- ✅ "document-reviewer specializes in documentation quality"
- ✅ "Update agent-handoffs.json with document-reviewer status"

---

### Why This Distinction Matters

**The Problem (v0.2.0-v0.3.1)**:
- Used "Reviewer" for aider QA role
- Created ambiguity: "Reviewer" vs "document-reviewer" agent
- Users confused about which "reviewer" was being discussed
- Generic "Reviewer" term lacked precision

**The Solution (v0.3.2+)**:
- Use "Evaluator" for aider QA (specific, precise)
- Keep "document-reviewer" for agent role (unchanged)
- Clear separation between concepts
- Aligns with technical naming (EVALUATOR_MODEL)

**Key Point**: If you see "Evaluator" in adversarial-workflow docs, it means the aider-powered QA. If you see "document-reviewer", it means the agent role. Never confuse them!

---

### ❌ Deprecated Terms (Do Not Use)

**These terms were used in earlier versions but are now deprecated:**

| Deprecated Term | Replace With | Why Deprecated |
|----------------|--------------|----------------|
| Coordinator | Author or You | Implied agent system |
| Coordinator agent | Author | Explicitly referenced agents |
| Reviewer (for QA role) | Evaluator | Ambiguous with document-reviewer agent |
| Feature-developer | Author or Developer | Implied agent system |
| Implementation agent | Author | Explicitly referenced agents |
| Coordinator-Evaluator pattern | Author-Evaluator workflow | Used deprecated Coordinator term |
| Author-Reviewer workflow | Author-Evaluator workflow | Ambiguous with agent roles |

**Historical Context**:
- v0.1.0 and earlier used "Coordinator" and "Evaluator"
- v0.2.0-v0.3.1 used "Author" and "Reviewer"
- User feedback indicated confusion (thought Coordinator/Evaluator were agents)
- v0.2.0 changed to "Author/Reviewer" for universal clarity
- v0.3.2 reverted to "Author/Evaluator" to avoid conflict with "document-reviewer" agent role
- "Evaluator" is more precise: evaluates quality/correctness vs generic "review"

---

## Usage Guidelines

### Rule 1: First Mention - Always Clarify

When introducing a role for the first time in a document, always clarify what it means.

**Examples**:

✅ **GOOD** (clear on first mention):
```markdown
The Author (you, or your AI assistant) creates an implementation plan.
The Evaluator (aider with GPT-4o) analyzes it critically.
```

❌ **BAD** (assumes understanding):
```markdown
The Author creates an implementation plan.
The Evaluator analyzes it.
```

---

### Rule 2: Subsequent Mentions - Context Clear

After roles are introduced, you can use them without qualification if context is clear.

**Examples**:

✅ **GOOD** (context established):
```markdown
# After introducing roles above:
The Author implements according to the approved plan.
The Evaluator checks for phantom work in the git diff.
The Author addresses any issues found.
```

---

### Rule 3: Technical Docs - Use Explicit Terms

In technical documentation, code examples, and troubleshooting, prefer explicit terms over metaphorical roles.

**Examples**:

✅ **GOOD** (explicit):
```markdown
You create tasks/feature.md with your implementation plan.
Run: adversarial evaluate tasks/feature.md
This executes: aider --model gpt-4o --read tasks/feature.md --message "review..."
```

❌ **BAD** (too abstract):
```markdown
The Author creates a task.
The Evaluator evaluates it.
```

---

### Rule 4: User-Facing - Use "You" When Appropriate

When addressing the user directly, "You" is often clearer than "Author".

**Examples**:

✅ **GOOD** (direct):
```markdown
You implement the changes using your preferred method.
Aider reviews your implementation in the next phase.
```

⚠️ **ACCEPTABLE** (when describing the pattern):
```markdown
The Author implements the changes using their preferred method.
The Reviewer analyzes the implementation.
```

**When to use which**:
- "You" → Instructions, tutorials, direct guidance
- "Author" → Pattern descriptions, workflow explanations, role definitions

---

## Writing Patterns

### ✅ Preferred Patterns

**Pattern 1: Role Introduction**
```markdown
The Author (you, or your AI assistant) creates something.
The Evaluator (aider + GPT-4o) analyzes it.
```

**Pattern 2: Direct Instruction**
```markdown
You create an implementation plan in tasks/feature.md.
Run `adversarial evaluate tasks/feature.md` to get feedback.
```

**Pattern 3: Workflow Description**
```markdown
The Author-Evaluator workflow consists of five phases:
1. Author creates plan
2. Evaluator critiques plan
3. Author implements code
4. Evaluator analyzes implementation
5. You (Author) finalize and commit
```

**Pattern 4: Technical Explanation**
```markdown
When you run `adversarial review`, the package executes:
- Captures git diff of your changes
- Runs aider with a code review prompt
- Aider analyzes your diff for completeness
- Results are displayed and saved
```

---

### ❌ Anti-Patterns (Avoid These)

**Anti-Pattern 1: Agent Language**
```markdown
❌ The Coordinator agent creates a plan
❌ The Evaluator agent reviews it
❌ The feature-developer agent implements changes
```

**Anti-Pattern 2: Unqualified Roles (First Mention)**
```markdown
❌ The Author creates a plan. The Reviewer analyzes it.
   (On first mention, always clarify what these mean)
```

**Anti-Pattern 3: Mixing Old and New**
```markdown
❌ The Coordinator (Author) creates a plan
❌ The Reviewer now called Evaluator analyzes it
   (Don't reference deprecated terms)
```

**Anti-Pattern 4: Implying Persistence**
```markdown
❌ Configure your Evaluator agent
❌ The Author agent needs setup
❌ Start the Evaluator service
   (These are not agents, services, or persistent systems)
```

---

## Technical Variable Names

### Keep As-Is (Backward Compatibility)

These technical identifiers remain unchanged to preserve backward compatibility with existing user configurations:

**Configuration Keys**:
- `evaluator_model` (in config.yml)
- `EVALUATOR_MODEL` (environment variable)
- `$EVALUATOR_MODEL` (bash script variable)

**Rationale**: Changing these would break existing `.adversarial/config.yml` files.

**In Documentation**:
- When referencing these config keys, use them as-is
- Add clarification: "evaluator_model (the Evaluator's AI model)"

**Example**:
```yaml
# .adversarial/config.yml
evaluator_model: gpt-4o  # AI model for Evaluator (aider)
```

---

## Phase-Specific Terminology

### Phase 1: Plan Evaluation

**Preferred Terms**:
- "Plan evaluation" or "Plan review"
- "The Evaluator analyzes your plan"
- "Aider critiques the implementation plan"

**Avoid**:
- ❌ "Reviewer reviews plan" (ambiguous with agent roles)
- ❌ "Coordinator's plan is evaluated"

---

### Phase 2: Implementation

**Preferred Terms**:
- "You implement" or "The Author implements"
- "Implementation phase"
- "Code according to the plan"

**Avoid**:
- ❌ "Coordinator implements"
- ❌ "Feature-developer agent executes"

---

### Phase 3: Code Review

**Preferred Terms**:
- "Code review" or "Implementation review"
- "The Evaluator analyzes your git diff"
- "Aider checks for phantom work"

**Avoid**:
- ❌ "Reviewer reviews code" (ambiguous with agent roles)
- ❌ "Coordinator's implementation is reviewed"

---

### Phase 4: Test Validation

**Preferred Terms**:
- "Test validation" or "Test analysis"
- "The Evaluator validates test results"
- "Aider analyzes your test output"

**Avoid**:
- ❌ "Test-runner agent validates"
- ❌ "Reviewer checks tests" (ambiguous with agent roles)

---

### Phase 5: Final Approval

**Preferred Terms**:
- "You review all artifacts"
- "Final approval phase"
- "Author commits the changes"

**Avoid**:
- ❌ "Coordinator approves"
- ❌ "Final agent review"

---

## Common Scenarios

### Scenario 1: Explaining the Package

**Good**:
> This package provides an Author-Evaluator workflow for code quality.
> You (the Author) create plans and code. Aider (the Evaluator) independently
> analyzes your work at each stage. This prevents phantom work through
> multiple verification gates.

**Bad**:
> This package provides a Coordinator-Reviewer pattern. The Coordinator
> agent creates code and the Reviewer agent reviews it.

---

### Scenario 2: Quick Start Instructions

**Good**:
> Create an implementation plan in `tasks/feature.md`. Then run
> `adversarial evaluate tasks/feature.md` to get feedback from aider.

**Bad**:
> The Coordinator creates a plan. The Evaluator reviews it via adversarial evaluate.

---

### Scenario 3: Troubleshooting

**Good**:
> **Issue**: Evaluator says "NEEDS_REVISION" but I think my plan is complete.
>
> **Solution**: The Evaluator (aider) uses a critical analysis prompt. Review
> the feedback carefully - it often catches real issues. Address the concerns
> and run evaluation again.

**Bad**:
> **Issue**: Reviewer agent always rejects my plan.
>
> **Solution**: The Reviewer agent is configured to be critical. Fix issues.

---

### Scenario 4: API Documentation

**Good**:
```python
def evaluate_plan(task_file: str) -> ReviewResult:
    """
    Runs plan evaluation using aider (the Evaluator).

    Args:
        task_file: Path to implementation plan created by you (the Author)

    Returns:
        ReviewResult containing feedback from aider's analysis
    """
```

**Bad**:
```python
def evaluate_plan(task_file: str) -> ReviewResult:
    """
    Reviewer agent reviews Coordinator's plan.
    """
```

---

## Migration Guide

### For Documentation Writers

**Step 1**: Search and replace with context review:
```bash
# Find all occurrences
grep -rn "Coordinator" docs/
grep -rn "Reviewer" docs/

# Replace following the rules above
# "Coordinator" → "Author" or "You" (context dependent)
# "Reviewer" → "Evaluator" (when referring to aider QA role)
```

**Step 2**: Verify first mentions have clarification

**Step 3**: Check technical contexts (keep variable names)

---

### For Code Comments

**Before**:
```python
# Coordinator creates implementation plan
# Reviewer analyzes for completeness
```

**After**:
```python
# Author creates implementation plan
# Evaluator (aider) analyzes for completeness
```

---

### For User Messages

**Before**:
```python
print("Coordinator-Reviewer workflow initialized")
```

**After**:
```python
print("Author-Evaluator workflow initialized")
```

---

## Questions & Answers

### Q: Why not just use "Developer" and "Reviewer"?

**A**: "Developer" implies the implementer is always a person, but it could be any tool (Claude Code, Cursor, manual coding). "Author" is tool-agnostic.

---

### Q: Why "Evaluator" instead of "Reviewer"?

**A**: "Evaluator" is more precise and specific - it evaluates quality and correctness. "Reviewer" is generic and creates ambiguity with the "document-reviewer" agent role in multi-agent systems. "Evaluator" also aligns with technical naming (EVALUATOR_MODEL environment variable).

---

### Q: Can I still use "Reviewer" to refer to the QA role?

**A**: Only when the context is crystal clear (e.g., "code review" as a generic term). In prose, documentation, and user-facing text referring to the adversarial-workflow QA role, always use "Evaluator" to avoid ambiguity with agent roles.

---

### Q: What about "Coordinator" or "Reviewer" in historical documents?

**A**: Historical documents can keep old terminology with a note: "Historical: This document predates the Author/Evaluator terminology update (2025-10-19)."

---

### Q: Should I update code variable names?

**A**:
- ✅ Update: User-facing strings, comments, docstrings, print statements
- ❌ Don't update: Internal variable names, configuration keys, API parameters (breaking change)

---

## Version History

### Version 2.0 (2025-10-19) - Author/Evaluator (Current)

**Changes**:
- Reverted from "Reviewer" back to "Evaluator" for QA role
- Added "Evaluator vs document-reviewer" distinction section
- Updated all documentation to use Author/Evaluator pattern
- Deprecated "Reviewer" (when referring to QA role)

**Rationale**:
- "Reviewer" created ambiguity with "document-reviewer" agent role
- "Evaluator" is more precise: evaluates quality/correctness
- Aligns with technical naming (EVALUATOR_MODEL environment variable)
- User feedback: people naturally refer to it as "Evaluator"
- Multi-agent systems need clear distinction between roles

---

### Version 1.0 (2025-10-15) - Author/Reviewer (Historical)

**Changes**:
- Established "Author" and "Reviewer" as official terms
- Deprecated "Coordinator" and "Evaluator"
- Created this terminology standards document

**Rationale**:
- Evaluator QA (2025-10-15) identified terminology confusion as critical issue
- User feedback indicated "Coordinator/Evaluator" implied agent infrastructure
- "Author/Reviewer" provided universal clarity without tool assumptions

**Deprecated**: 2025-10-19 (v2.0 reverted to "Evaluator")

---

### Version 0.x (Historical) - Coordinator/Evaluator

**Terms Used**:
- Coordinator (now: Author)
- Evaluator (v0.1), then Reviewer (v1.0), now Evaluator again (v2.0)
- Coordinator-Evaluator pattern (now: Author-Evaluator workflow)

**Deprecated**: 2025-10-15

---

## Enforcement

**Required**:
- All new documentation MUST use Author/Evaluator terminology
- All updated documentation SHOULD migrate to Author/Evaluator
- All user-facing strings MUST use new terminology

**Optional**:
- Historical documents MAY keep old terminology with a note
- Internal code MAY keep old variable names (not user-facing)

**Validation**:
- Automated grep checks for deprecated terms in docs
- Terminology audits will verify consistency
- "Evaluator" used for aider QA, "document-reviewer" for agent role

---

## References

- **v0.3.2 Decision Record**: `delegation/decisions/TASK-TERMINOLOGY-001-REVERT-DECISION.md`
- **v0.2.0 Decision Record**: `delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md`
- **Terminology Audit**: `audit-results/6A2-TERMINOLOGY-AUDIT.md`
- **Evaluator QA**: `EVALUATOR-QA-RESPONSE.txt`

---

**Document Status**: Official Standards v2.0
**Effective Date**: 2025-10-19
**Next Review**: When introducing new concepts requiring terminology
