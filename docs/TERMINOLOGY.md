# Adversarial Workflow Terminology

**Version**: 1.0 (Author/Reviewer)
**Last Updated**: 2025-10-15
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

#### Reviewer

**Definition**: The independent analysis stage that critiques the Author's work.

**Use When**:
- Describing the code review function
- Describing plan evaluation
- Describing test validation

**Examples**:
- ✅ "The Reviewer (aider + GPT-4o) analyzes the plan"
- ✅ "Aider reviews your git diff for completeness"
- ✅ "The Reviewer validates test results"

**Technical Reality**:
- This is aider running with a specific prompt
- Command: `aider --model gpt-4o --message "review prompt"`
- NOT a persistent agent or special software
- NOT infrastructure you need to configure
- Different prompt for each phase (evaluate, review, validate)

---

#### Author-Reviewer Workflow

**Definition**: The multi-stage verification pattern where the Author creates work and the Reviewer independently analyzes it.

**Use When**:
- Describing the overall pattern
- Explaining the adversarial aspect
- Documenting workflow phases

**Examples**:
- ✅ "The Author-Reviewer workflow prevents phantom work"
- ✅ "Multi-stage Author-Reviewer verification"
- ✅ "Independent review at each stage"

**Why "Adversarial"**:
- The Reviewer is incentivized to find problems
- Independent perspective catches issues the Author might miss
- Multiple verification stages prevent incomplete work
- "Adversarial" describes the relationship, not hostility

---

### ❌ Deprecated Terms (Do Not Use)

**These terms were used in earlier versions but are now deprecated:**

| Deprecated Term | Replace With | Why Deprecated |
|----------------|--------------|----------------|
| Coordinator | Author or You | Implied agent system |
| Coordinator agent | Author | Explicitly referenced agents |
| Evaluator | Reviewer | Lacked clarity (evaluating what?) |
| Evaluator agent | Reviewer | Explicitly referenced agents |
| Feature-developer | Author or Developer | Implied agent system |
| Implementation agent | Author | Explicitly referenced agents |
| Coordinator-Evaluator pattern | Author-Reviewer workflow | Used deprecated terms |

**Historical Context**:
- v0.1.0 and earlier used "Coordinator" and "Evaluator"
- User feedback indicated confusion (thought these were agents)
- Evaluator QA (2025-10-15) flagged as critical issue
- Updated to "Author/Reviewer" for universal clarity

---

## Usage Guidelines

### Rule 1: First Mention - Always Clarify

When introducing a role for the first time in a document, always clarify what it means.

**Examples**:

✅ **GOOD** (clear on first mention):
```markdown
The Author (you, or your AI assistant) creates an implementation plan.
The Reviewer (aider with GPT-4o) analyzes it critically.
```

❌ **BAD** (assumes understanding):
```markdown
The Author creates an implementation plan.
The Reviewer analyzes it.
```

---

### Rule 2: Subsequent Mentions - Context Clear

After roles are introduced, you can use them without qualification if context is clear.

**Examples**:

✅ **GOOD** (context established):
```markdown
# After introducing roles above:
The Author implements according to the approved plan.
The Reviewer checks for phantom work in the git diff.
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
The Reviewer evaluates it.
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
The Reviewer (aider + GPT-4o) analyzes it.
```

**Pattern 2: Direct Instruction**
```markdown
You create an implementation plan in tasks/feature.md.
Run `adversarial evaluate tasks/feature.md` to get feedback.
```

**Pattern 3: Workflow Description**
```markdown
The Author-Reviewer workflow consists of five phases:
1. Author creates plan
2. Reviewer critiques plan
3. Author implements code
4. Reviewer analyzes implementation
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
❌ The Evaluator now called Reviewer analyzes it
   (Don't reference deprecated terms)
```

**Anti-Pattern 4: Implying Persistence**
```markdown
❌ Configure your Reviewer agent
❌ The Author agent needs setup
❌ Start the Reviewer service
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
- Add clarification: "evaluator_model (the Reviewer's AI model)"

**Example**:
```yaml
# .adversarial/config.yml
evaluator_model: gpt-4o  # AI model for Reviewer (aider)
```

---

## Phase-Specific Terminology

### Phase 1: Plan Evaluation

**Preferred Terms**:
- "Plan evaluation" or "Plan review"
- "The Reviewer analyzes your plan"
- "Aider critiques the implementation plan"

**Avoid**:
- ❌ "Evaluator reviews plan"
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
- "The Reviewer analyzes your git diff"
- "Aider checks for phantom work"

**Avoid**:
- ❌ "Evaluator reviews code"
- ❌ "Coordinator's implementation is reviewed"

---

### Phase 4: Test Validation

**Preferred Terms**:
- "Test validation" or "Test analysis"
- "The Reviewer validates test results"
- "Aider analyzes your test output"

**Avoid**:
- ❌ "Test-runner agent validates"
- ❌ "Evaluator checks tests"

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
> This package provides an Author-Reviewer workflow for code quality.
> You (the Author) create plans and code. Aider (the Reviewer) independently
> analyzes your work at each stage. This prevents phantom work through
> multiple verification gates.

**Bad**:
> This package provides a Coordinator-Evaluator pattern. The Coordinator
> agent creates code and the Evaluator agent reviews it.

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
> **Issue**: Reviewer says "NEEDS_REVISION" but I think my plan is complete.
>
> **Solution**: The Reviewer (aider) uses a critical analysis prompt. Review
> the feedback carefully - it often catches real issues. Address the concerns
> and run evaluation again.

**Bad**:
> **Issue**: Evaluator agent always rejects my plan.
>
> **Solution**: The Evaluator agent is configured to be critical. Fix issues.

---

### Scenario 4: API Documentation

**Good**:
```python
def evaluate_plan(task_file: str) -> ReviewResult:
    """
    Runs plan evaluation using aider (the Reviewer).

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
    Evaluator agent reviews Coordinator's plan.
    """
```

---

## Migration Guide

### For Documentation Writers

**Step 1**: Search and replace with context review:
```bash
# Find all occurrences
grep -rn "Coordinator" docs/
grep -rn "Evaluator" docs/

# Replace following the rules above
# "Coordinator" → "Author" or "You" (context dependent)
# "Evaluator" → "Reviewer" (most cases)
```

**Step 2**: Verify first mentions have clarification

**Step 3**: Check technical contexts (keep variable names)

---

### For Code Comments

**Before**:
```python
# Coordinator creates implementation plan
# Evaluator analyzes for completeness
```

**After**:
```python
# Author creates implementation plan
# Reviewer (aider) analyzes for completeness
```

---

### For User Messages

**Before**:
```python
print("Coordinator-Evaluator workflow initialized")
```

**After**:
```python
print("Author-Reviewer workflow initialized")
```

---

## Questions & Answers

### Q: Why not just use "Developer" and "Reviewer"?

**A**: "Developer" implies the implementer is always a person, but it could be any tool (Claude Code, Cursor, manual coding). "Author" is tool-agnostic.

---

### Q: Why "Reviewer" instead of "Evaluator"?

**A**: "Reviewer" is universally understood (code reviews, pull request reviews). "Evaluator" was ambiguous (evaluating what? performance? quality?). "Reviewer" clearly indicates code review function.

---

### Q: Can I still use "Evaluator" in technical contexts?

**A**: Only for backward compatibility (config keys like `evaluator_model`). In prose, documentation, and user-facing text, always use "Reviewer".

---

### Q: What about "Coordinator" in historical documents?

**A**: Historical documents can keep old terminology with a note: "Historical: This document predates the Author/Reviewer terminology update (2025-10-15)."

---

### Q: Should I update code variable names?

**A**:
- ✅ Update: User-facing strings, comments, docstrings, print statements
- ❌ Don't update: Internal variable names, configuration keys, API parameters (breaking change)

---

## Version History

### Version 1.0 (2025-10-15) - Author/Reviewer

**Changes**:
- Established "Author" and "Reviewer" as official terms
- Deprecated "Coordinator" and "Evaluator"
- Created this terminology standards document

**Rationale**:
- Evaluator QA (2025-10-15) identified terminology confusion as critical issue
- User feedback indicated "Coordinator/Evaluator" implied agent infrastructure
- "Author/Reviewer" provides universal clarity without tool assumptions

---

### Version 0.x (Historical) - Coordinator/Evaluator

**Terms Used**:
- Coordinator (now: Author)
- Evaluator (now: Reviewer)
- Coordinator-Evaluator pattern (now: Author-Reviewer workflow)

**Deprecated**: 2025-10-15

---

## Enforcement

**Required**:
- All new documentation MUST use Author/Reviewer terminology
- All updated documentation SHOULD migrate to Author/Reviewer
- All user-facing strings MUST use new terminology

**Optional**:
- Historical documents MAY keep old terminology with a note
- Internal code MAY keep old variable names (not user-facing)

**Validation**:
- Phase 6F will validate terminology consistency
- Automated grep checks for deprecated terms in docs
- Second Evaluator review will verify improvements

---

## References

- **Decision Record**: `delegation/tasks/active/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md`
- **Terminology Audit**: `adversarial-workflow/audit-results/6A2-TERMINOLOGY-AUDIT.md`
- **Evaluator QA**: `adversarial-workflow/EVALUATOR-QA-RESPONSE.txt`

---

**Document Status**: Official Standards v1.0
**Effective Date**: 2025-10-15
**Next Review**: When introducing new concepts requiring terminology
