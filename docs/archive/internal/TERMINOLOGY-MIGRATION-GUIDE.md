# Terminology Migration Guide: v0.3.2

**For projects using adversarial-workflow**

This guide helps you update your project after the v0.3.2 terminology change from "Reviewer" → "Evaluator".

---

## What Changed in v0.3.2?

### Terminology Reversion

| Old (v0.2.0-v0.3.1) | New (v0.3.2+) | Applies To |
|---------------------|---------------|------------|
| Author-Reviewer workflow | Author-Evaluator workflow | Documentation, discussions |
| "Reviewer" (for QA) | "Evaluator" (for QA) | When referring to aider-powered quality checks |
| "Reviewer analyzes..." | "Evaluator analyzes..." | Workflow descriptions |

### What Didn't Change (No Action Required)

✅ **Config files** - No changes needed:
```yaml
# .adversarial/config.yml - SAME AS BEFORE
evaluator_model: gpt-4o  # ← Still called evaluator_model
```

✅ **Environment variables** - No changes needed:
```bash
# Still EVALUATOR_MODEL (was never REVIEWER_MODEL)
export EVALUATOR_MODEL=gpt-4o
```

✅ **Commands** - No changes needed:
```bash
adversarial evaluate   # ← Still called "evaluate"
adversarial review     # ← Still called "review"
adversarial validate   # ← Still called "validate"
```

✅ **Agent role names** - No changes needed:
```json
{
  "document-reviewer": {  // ← Unchanged
    "status": "available"
  }
}
```

---

## Upgrade Instructions

### Step 1: Update Package

```bash
# Upgrade adversarial-workflow to v0.3.2+
pip install --upgrade adversarial-workflow

# Or with pipx
pipx upgrade adversarial-workflow
```

### Step 2: Update Your Project Documentation (Optional)

If your project's documentation mentions the adversarial workflow, update terminology:

**Task files** (tasks/*.md):
```markdown
# Before (v0.2.0-v0.3.1)
The Reviewer will analyze this plan for completeness.

# After (v0.3.2+)
The Evaluator will analyze this plan for completeness.
```

**README/Documentation**:
```markdown
# Before
This project uses the Author-Reviewer adversarial workflow.

# After
This project uses the Author-Evaluator adversarial workflow.
```

**Code comments**:
```python
# Before
# Reviewer checks implementation against plan

# After
# Evaluator checks implementation against plan
```

### Step 3: No Config Changes Needed

Your `.adversarial/config.yml` already uses the correct terminology:

```yaml
# This is ALREADY correct - no changes needed
evaluator_model: gpt-4o
```

---

## What If I Don't Update My Docs?

**It still works!** This is a documentation-only change. Your workflow continues working exactly as before.

However, updating your docs helps with:
- ✅ Clarity in multi-agent projects (no confusion with "document-reviewer" agent)
- ✅ Alignment with official adversarial-workflow terminology
- ✅ More precise communication ("evaluator" is clearer than generic "reviewer")

---

## Search & Replace Guide

### Quick Update Script

For large codebases, use this approach:

```bash
# 1. Find all references to review in your docs
grep -rn "Reviewer" docs/ tasks/ README.md

# 2. Update (be careful not to change agent role names!)
# DO:
"The Reviewer analyzes" → "The Evaluator analyzes"
"Author-Reviewer workflow" → "Author-Evaluator workflow"

# DON'T:
"document-reviewer" → unchanged
"code review" → unchanged (generic term)
```

### Safe Replacements

**✅ Safe to replace**:
```markdown
Author-Reviewer → Author-Evaluator
The Reviewer (aider → The Evaluator (aider
Reviewer analyzes → Evaluator analyzes
Reviewer validates → Evaluator validates
Reviewer checks → Evaluator checks
```

**❌ DO NOT replace**:
```markdown
document-reviewer  # Agent role name
code review        # Generic term
pull request review  # Generic term
```

---

## Multi-Agent Projects

### Why This Change Matters

If your project uses agent coordination (`.agent-context/`):

**Before (v0.2.0-v0.3.1)** - Ambiguous:
```markdown
❌ "The Reviewer analyzes your documentation."
(Which reviewer? Aider QA? document-reviewer agent?)
```

**After (v0.3.2)** - Clear:
```markdown
✅ "The Evaluator analyzes your plan."
(Obviously the aider QA, not an agent)

✅ "Assign this to the document-reviewer agent."
(Obviously an agent, not the QA check)
```

### Agent Handoffs

No changes needed to your `agent-handoffs.json`:

```json
{
  "document-reviewer": {  // ← Keep as-is
    "current_focus": "Documentation quality",
    "status": "available"
  }
}
```

---

## Examples: Before & After

### Example 1: Task File

**Before (v0.2.0-v0.3.1)**:
```markdown
# Implementation Plan

The Reviewer will evaluate this plan for:
- Completeness
- Edge cases
- Implementation feasibility

After the Reviewer approves, I'll implement using Claude Code.
```

**After (v0.3.2)**:
```markdown
# Implementation Plan

The Evaluator will evaluate this plan for:
- Completeness
- Edge cases
- Implementation feasibility

After the Evaluator approves, I'll implement using Claude Code.
```

### Example 2: README.md

**Before**:
```markdown
## Workflow

This project uses the Author-Reviewer adversarial workflow:
1. Author creates plan
2. Reviewer critiques plan
3. Author implements
4. Reviewer verifies implementation
```

**After**:
```markdown
## Workflow

This project uses the Author-Evaluator adversarial workflow:
1. Author creates plan
2. Evaluator critiques plan
3. Author implements
4. Evaluator verifies implementation
```

### Example 3: Code Comments

**Before**:
```python
# Phase 3: Implementation Review
# Reviewer analyzes git diff for phantom work
def review_implementation(task_file, diff_file):
    # Reviewer uses GPT-4o to check for TODOs vs real code
    pass
```

**After**:
```python
# Phase 3: Implementation Review
# Evaluator analyzes git diff for phantom work
def review_implementation(task_file, diff_file):
    # Evaluator uses GPT-4o to check for TODOs vs real code
    pass
```

---

## FAQs

### Q: Do I need to update my config files?

**A**: No! Your `config.yml` already uses `evaluator_model`, which is correct.

### Q: Will my existing workflows break?

**A**: No! All commands, config keys, and functionality remain unchanged.

### Q: What if I have "Reviewer" in my task files?

**A**: They'll still work fine. Update them gradually for consistency, but there's no rush.

### Q: Should I update historical documents?

**A**: No, keep historical documents as-is. Only update actively-maintained docs.

### Q: What about the agent role "document-reviewer"?

**A**: Never change agent role names! This terminology change is specifically to avoid confusion with agent roles.

---

## Version Compatibility

| adversarial-workflow Version | Terminology | Compatibility |
|------------------------------|-------------|---------------|
| v0.1.x | Coordinator/Evaluator | Legacy |
| v0.2.0 - v0.3.1 | Author/Reviewer | Works, but outdated |
| v0.3.2+ | Author/Evaluator | **Current** ✅ |

All versions use the same config format - fully backward compatible!

---

## Getting Help

**Questions about the terminology change?**
- See: `docs/TERMINOLOGY.md` (official standards)
- See: `delegation/decisions/TASK-TERMINOLOGY-001-REVERT-DECISION.md` (full rationale)

**Need help updating your project?**
- Open an issue: https://github.com/movito/adversarial-workflow/issues
- Check examples: `docs/EXAMPLES.md`

---

## Summary

✅ **Upgrade**: `pip install --upgrade adversarial-workflow`
✅ **Update docs**: Replace "Reviewer" → "Evaluator" (for QA role)
✅ **No config changes**: Everything still works!
✅ **Optional**: Update terminology gradually for consistency

**Key Point**: This is a documentation clarity improvement, not a breaking change. Your workflows continue working immediately!

---

**Last Updated**: 2025-10-19 (v0.3.2)
