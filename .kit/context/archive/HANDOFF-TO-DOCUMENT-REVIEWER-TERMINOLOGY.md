# Handoff to Document Reviewer: Terminology Reversion Task

**From**: Coordinator
**To**: Document Reviewer
**Date**: 2025-10-19
**Task**: TASK-TERMINOLOGY-001-REVERT-TO-EVALUATOR.md
**Priority**: MEDIUM
**Estimated Effort**: 2-3 hours

---

## Mission

Revert the v0.2.0 terminology change from "Evaluator" → "Reviewer" back to "Evaluator" in adversarial-workflow documentation and user-facing text.

**Why this matters**: The current "Reviewer" terminology conflicts with the "document-reviewer" agent role (you!), creating ambiguity. "Evaluator" is more precise and aligns with technical naming.

---

## What You're Changing

### Change This:
- "Reviewer" (referring to aider-powered QA) → "Evaluator"
- "Author-Reviewer workflow" → "Author-Evaluator workflow"
- "The Reviewer analyzes" → "The Evaluator analyzes"

### Don't Change:
- "document-reviewer" (that's your agent role name!)
- `EVALUATOR_MODEL` (already correct)
- Historical documents (EVALUATOR-QA-*.md, archived tasks)
- Generic usage ("code review", "pull request review")

---

## The Irony

You (document-reviewer agent) are fixing the very ambiguity that affects your own role name!

**The problem**: When docs say "Reviewer" for the aider QA role, it's confusing with "document-reviewer" agent.

**The solution**: Use "Evaluator" for aider QA, keep "document-reviewer" for you.

---

## Quick Context

### History of This Terminology

**v0.1.0**: Used "Coordinator/Evaluator"
- Problem: Implied agent infrastructure

**v0.2.0**: Changed to "Author/Reviewer"
- Rationale: Match GitHub PR terminology
- Implementation: 73 fixes across 11 files
- Decision: delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md

**v0.3.2 (this task)**: Reverting to "Author/Evaluator"
- Problem: "Reviewer" conflicts with "document-reviewer" agent
- Solution: "Evaluator" is more precise and less ambiguous
- User feedback: People naturally say "Evaluator"

### What "Evaluator" Actually Is

**NOT** an agent or infrastructure. It's just:
```bash
aider --model gpt-4o --message "review this plan"
```

A simple CLI command that provides critical feedback. That's it!

---

## Files to Update

### Primary Documentation (~20-30 occurrences)
1. `README.md` - Main docs
2. `QUICK_START.md` - Getting started
3. `docs/TERMINOLOGY.md` - **Most important** - define Author/Evaluator
4. `docs/EXAMPLES.md` - Workflow examples
5. `docs/WORKFLOW_PHASES.md` - Phase descriptions
6. `docs/INTERACTION_PATTERNS.md` - Patterns

### Templates (~10-15 occurrences)
7. `adversarial_workflow/templates/*.template` - Script comments

### Code (~2-3 occurrences)
8. `adversarial_workflow/cli.py` - Line 322 and user-facing messages

---

## Step-by-Step Approach

### Step 1: Read Context (15 min)
Read these to understand the full story:
1. Your task file: `delegation/tasks/active/TASK-TERMINOLOGY-001-REVERT-TO-EVALUATOR.md`
2. Original decision: `delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md`
3. The QA that started it: `EVALUATOR-QA-RESPONSE.txt`

### Step 2: Automated Search (30 min)
Use grep to find all "Reviewer" references:
```bash
# Find all instances (excluding archives)
grep -rn "Reviewer" docs/*.md README.md QUICK_START.md adversarial_workflow/cli.py | \
  grep -v "document-reviewer" | \
  grep -v "code review"
```

Then carefully change appropriate ones to "Evaluator".

### Step 3: Context-Dependent Updates (60 min)
Manually review and update:
- README.md workflow descriptions
- QUICK_START.md examples
- docs/TERMINOLOGY.md (add Evaluator vs document-reviewer section)
- Templates (script comments and echo messages)
- cli.py line 322

### Step 4: Create Decision Document (15 min)
Write `delegation/decisions/TASK-TERMINOLOGY-001-REVERT-DECISION.md` explaining:
- Why we're reverting
- The Evaluator vs document-reviewer distinction
- Full terminology history

### Step 5: Verify (30 min)
Run verification checks:
```bash
# Should find mostly agent roles and generic usage
grep -rn "Reviewer" docs/ README.md QUICK_START.md

# Should find Author-Evaluator consistently
grep -rn "Author.*Evaluator" docs/ README.md

# Technical vars should be unchanged
grep -rn "EVALUATOR_MODEL" adversarial_workflow/
```

---

## Key Distinctions to Document

When you update `docs/TERMINOLOGY.md`, make these distinctions crystal clear:

### Evaluator (aider-powered QA)
- **What**: CLI command that reviews work products
- **Technical**: `aider --model gpt-4o --message "..."`
- **Role**: Critical analysis, quality checking
- **Not**: An agent, infrastructure, or special software
- **When**: Used in adversarial-workflow phases

### document-reviewer (agent role)
- **What**: Agent role in multi-agent coordination
- **Technical**: Entry in agent-handoffs.json
- **Role**: Documentation quality, consistency checking
- **Not**: Related to Evaluator (different system)
- **When**: Used in agent coordination context

These are **completely separate concepts** in different systems!

---

## Testing Your Changes

### Readability Test
Read updated sections aloud. Does "Evaluator" flow naturally?

### Ambiguity Test
When you see "Evaluator", is it clear it means aider QA (not document-reviewer)?

### Consistency Test
Are all workflow examples using "Author-Evaluator" pattern?

### Technical Test
Are all `EVALUATOR_MODEL` references unchanged?

---

## Watch Out For

### Common Pitfalls

1. **Don't change "document-reviewer"** anywhere
   - It's an agent role name (proper noun)
   - Appears in agent-handoffs.json templates
   - Should never become "document-evaluator"

2. **Don't modify archived files**
   - delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md
   - delegation/tasks/archived/TASK-PACKAGING-001-PHASE-6-EVALUATOR-FIXES.md
   - These are historical records

3. **Don't change technical variables**
   - `EVALUATOR_MODEL` stays as-is
   - `evaluator_model` in config files stays as-is
   - These are already correct!

4. **Preserve generic usage**
   - "code review" (generic term) stays unchanged
   - "pull request review" (generic term) stays unchanged
   - Only change when referring to the adversarial-workflow QA role

---

## Example Changes

### README.md

**Before**:
```markdown
The Reviewer (aider + GPT-4o) analyzes your plan for completeness and flags issues.

This Author-Reviewer workflow prevents phantom work.
```

**After**:
```markdown
The Evaluator (aider + GPT-4o) analyzes your plan for completeness and flags issues.

This Author-Evaluator workflow prevents phantom work.
```

### docs/TERMINOLOGY.md

**Add new section**:
```markdown
## Evaluator vs document-reviewer

### Evaluator (adversarial-workflow QA role)
The Evaluator is the aider-powered quality check in adversarial-workflow. It's
a simple CLI command (`aider --model gpt-4o`) that provides critical feedback
on plans, implementations, and tests. Not an agent or infrastructure.

### document-reviewer (agent coordination role)
The document-reviewer is an agent role in the multi-agent coordination system
(agent-handoffs.json). Completely separate from the Evaluator. Handles
documentation quality and consistency in agent-based projects.

**Key point**: These are different systems. Don't confuse them!
```

### cli.py line 322

**Before**:
```python
f"  Reviewer: {'GPT-4o (OpenAI)' if openai_key else 'Claude 3.5 Sonnet (Anthropic)' if anthropic_key else 'Not configured'}",
```

**After**:
```python
f"  Evaluator: {'GPT-4o (OpenAI)' if openai_key else 'Claude 3.5 Sonnet (Anthropic)' if anthropic_key else 'Not configured'}",
```

---

## Deliverables Checklist

- [ ] README.md updated
- [ ] QUICK_START.md updated
- [ ] docs/TERMINOLOGY.md updated with Evaluator vs document-reviewer section
- [ ] docs/EXAMPLES.md updated
- [ ] docs/WORKFLOW_PHASES.md updated
- [ ] docs/INTERACTION_PATTERNS.md updated
- [ ] Templates updated (*.template files)
- [ ] cli.py updated (line 322 and user-facing messages)
- [ ] Decision document created (delegation/decisions/TASK-TERMINOLOGY-001-REVERT-DECISION.md)
- [ ] CHANGELOG.md entry added for v0.3.2
- [ ] Verification checks passed (grep tests)
- [ ] All changes committed with provided commit message

---

## Commit Message (Use This Exactly)

See the commit message template in your task file:
`delegation/tasks/active/TASK-TERMINOLOGY-001-REVERT-TO-EVALUATOR.md`

It's comprehensive and pre-written for you!

---

## Questions?

Refer to the "Questions?" section in your task file. It covers:
- Generic "review" usage (don't change)
- EVALUATOR_MODEL variables (don't change)
- CHANGELOG.md (add v0.3.2 entry)
- Historical documents (don't modify)
- Agent role names (never change)

---

## Timeline

Total estimated: 2.5-3 hours

- Reading context: 15 min
- Automated search: 30 min
- Context-dependent updates: 60 min
- Decision document: 15 min
- Verification: 30 min
- Commit & cleanup: 15 min

---

## Success Looks Like

When you're done:
1. ✅ All user-facing docs say "Author-Evaluator workflow"
2. ✅ "document-reviewer" agent role name unchanged
3. ✅ Technical variables (EVALUATOR_MODEL) unchanged
4. ✅ Clear distinction documented in TERMINOLOGY.md
5. ✅ No ambiguity between Evaluator and document-reviewer
6. ✅ Historical context preserved
7. ✅ Clean commit with comprehensive message

---

**You've got this!** This is exactly the kind of careful documentation work you excel at.

The irony: You're fixing the confusion about "Reviewer" that affects your own role name. Meta! 🎭

**Questions or blockers?** Document them in the task file or agent-handoffs.json.

**Good luck!**

— Coordinator
