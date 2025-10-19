# TASK-TERMINOLOGY-001: Revert "Reviewer" → "Evaluator" Terminology

**Created**: 2025-10-19
**Status**: READY_TO_START
**Priority**: MEDIUM
**Assigned**: document-reviewer
**Estimated Effort**: 2-3 hours
**Type**: Documentation update (search & replace with context verification)

---

## Overview

Revert the v0.2.0 terminology change from "Evaluator" → "Reviewer" back to "Evaluator" for the aider-powered quality check role in adversarial-workflow.

**Goal**: Eliminate ambiguity between "Reviewer" (aider-powered QA) and "document-reviewer" (agent role) by using clearer, more precise terminology.

---

## Context

### Why We Changed to "Reviewer" (v0.2.0)

In v0.2.0, we changed "Evaluator" → "Reviewer" based on Evaluator QA feedback:
- **Rationale**: "Reviewer" is universally understood (GitHub PRs, code reviews)
- **Implementation**: 73 fixes across 11 files
- **Documented**: delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md

### Why We're Reverting to "Evaluator" (v0.3.2)

The "Reviewer" terminology created a NEW conflict:
1. **Ambiguity with agent roles**: "Reviewer" vs "document-reviewer" agent
2. **Technical inconsistency**: Code uses `EVALUATOR_MODEL` (not `REVIEWER_MODEL`)
3. **Less precise**: "Reviewer" is generic; "Evaluator" is specific (evaluates quality/correctness)
4. **Multi-agent systems**: "Evaluator" is a recognized role; "Reviewer" conflicts with document review

**User observation**: "Other agents are referring to it as 'Evaluator'" - because that's the more natural term!

---

## Objectives

1. Change "Reviewer" → "Evaluator" in user-facing documentation
2. Preserve backward compatibility (technical variable names unchanged)
3. Update examples and usage patterns
4. Maintain clarity about what Evaluator role does (aider-powered QA, not infrastructure)
5. Keep historical references intact (EVALUATOR-QA-*.md, CHANGELOG, etc.)

---

## Success Criteria

### Must Have
- ✅ All user-facing "Reviewer" references changed to "Evaluator" (except agent roles)
- ✅ Technical variables unchanged (`EVALUATOR_MODEL`, `evaluator_model`)
- ✅ Examples updated with "Evaluator" terminology
- ✅ TERMINOLOGY.md updated to explain Author/Evaluator pattern
- ✅ No new ambiguity introduced
- ✅ Historical documents preserved (archives, decision records)

### Should Have
- ✅ CLI output messages updated (cli.py user-facing strings only)
- ✅ Template files updated (evaluate_plan.sh.template, etc.)
- ✅ QUICK_START.md updated with Evaluator terminology
- ✅ EXAMPLES.md workflow examples use Evaluator

### Nice to Have
- ✅ Decision document created explaining the reversion
- ✅ CHANGELOG entry for v0.3.2

---

## Files to Update

### High Priority (User-Facing Documentation)

**Core Documentation** (~20-30 occurrences):
1. `README.md` - Main package documentation
   - Line 257: Update historical note to explain both changes
   - Search for "Reviewer" in workflow descriptions

2. `docs/TERMINOLOGY.md` - Terminology standards
   - Update "Author/Reviewer" → "Author/Evaluator"
   - Add section explaining the reversion and why
   - Distinguish "Evaluator" (aider QA) from "document-reviewer" (agent role)

3. `QUICK_START.md` - Getting started guide
   - Update workflow phase descriptions
   - Change "Reviewer" → "Evaluator" in examples

4. `docs/EXAMPLES.md` - Usage examples
   - Update all workflow examples
   - Change "Reviewer analyzes" → "Evaluator analyzes"

5. `docs/WORKFLOW_PHASES.md` - Phase descriptions
   - Update phase terminology consistently

6. `docs/INTERACTION_PATTERNS.md` - Workflow patterns
   - Update pattern descriptions

### Medium Priority (Templates & Scripts)

**Template Files** (~10-15 occurrences):
1. `adversarial_workflow/templates/config.yml.template`
   - Comments and descriptions (technical vars stay as `evaluator_model`)

2. `adversarial_workflow/templates/README.template`
   - User-facing descriptions

3. `adversarial_workflow/templates/evaluate_plan.sh.template`
   - Script comments and echo messages

4. `adversarial_workflow/templates/review_implementation.sh.template`
   - Script comments and echo messages

5. `adversarial_workflow/templates/validate_tests.sh.template`
   - Script comments and echo messages

### Low Priority (Code & Historical)

**Python Code** (selective changes):
1. `adversarial_workflow/cli.py`
   - Line 322: "Reviewer:" → "Evaluator:" in check() output
   - Other user-facing messages only
   - **DO NOT CHANGE**: Variable names, config keys

**Historical/Archive** (READ ONLY - do not modify):
- `EVALUATOR-QA-REQUEST.md` - Keep as-is (historical)
- `EVALUATOR-QA-RESPONSE.txt` - Keep as-is (historical)
- `delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md` - Keep as-is (decision record)
- `delegation/tasks/archived/TASK-PACKAGING-001-PHASE-6-EVALUATOR-FIXES.md` - Keep as-is (archived task)
- `CHANGELOG.md` - Add new entry for v0.3.2, preserve historical entries

---

## Implementation Strategy

### Phase 1: Automated Search & Replace (~30 min)

**Safe Global Replacements** (in documentation only):

```bash
# In docs/*.md and root *.md (exclude CHANGELOG.md, archives, decisions)
# Manual verification recommended for each match

"The Reviewer" → "The Evaluator"
"Reviewer (aider" → "Evaluator (aider"
"Author-Reviewer workflow" → "Author-Evaluator workflow"
"Author/Reviewer" → "Author/Evaluator"
```

**DO NOT replace**:
- "document-reviewer" (agent role name)
- "code reviewer" (generic term)
- Technical variables (`EVALUATOR_MODEL`, `evaluator_model`)
- Historical documents in delegation/decisions/, delegation/tasks/archived/

### Phase 2: Context-Dependent Updates (~60 min)

**Requires manual review**:

1. **cli.py**:
   - Line 322: `"Reviewer:"` → `"Evaluator:"`
   - Check all `print()` and `f"..."` strings for user-facing "Reviewer"
   - Leave variable names unchanged

2. **Template files**:
   - Update comments: `# Reviewer analyzes` → `# Evaluator analyzes`
   - Update echo messages in bash scripts
   - Preserve technical config keys

3. **Examples in docs/EXAMPLES.md**:
   - Update workflow narratives
   - Ensure examples use "Evaluator" consistently

### Phase 3: Verification & Documentation (~30 min)

1. **Create decision document**: `delegation/decisions/TASK-TERMINOLOGY-001-REVERT-DECISION.md`
   - Explain why we're reverting
   - Document the Author/Evaluator pattern
   - Clarify distinction from agent roles

2. **Update TERMINOLOGY.md**:
   - Add section on "Evaluator vs. Reviewer distinction"
   - Explain when to use each term
   - Document the full history (v0.1: Evaluator, v0.2: Reviewer, v0.3.2: Evaluator)

3. **Grep verification**:
   ```bash
   # Verify no unintended "Reviewer" references remain
   grep -rn "Reviewer" docs/*.md README.md QUICK_START.md | grep -v "document-reviewer" | grep -v "code review"

   # Verify "Evaluator" is used consistently
   grep -rn "Author.*Reviewer" docs/ README.md
   ```

---

## Guidelines for Implementation

### ✅ DO:
- Change "Reviewer" → "Evaluator" when referring to aider-powered QA role
- Keep "document-reviewer" unchanged (agent role name)
- Preserve technical variable names (`EVALUATOR_MODEL`)
- Add clarifying context when first introducing "Evaluator" in docs
- Update historical note in README.md to explain both changes (v0.2 and v0.3.2)

### ❌ DON'T:
- Change agent role names in agent-handoffs.json templates
- Modify archived tasks or decision documents
- Change technical config keys or environment variable names
- Remove historical references in CHANGELOG.md
- Change "code review" or "pull request review" (generic usage)

### Example Updates:

**Before** (v0.2.0-v0.3.1):
```markdown
The Reviewer (aider + GPT-4o) analyzes the plan for completeness.

Author-Reviewer workflow ensures quality.
```

**After** (v0.3.2):
```markdown
The Evaluator (aider + GPT-4o) analyzes the plan for completeness.

Author-Evaluator workflow ensures quality.
```

**Preserve** (agent context):
```json
{
  "document-reviewer": {
    "current_focus": "Available for assignment"
  }
}
```

---

## Testing & Verification

### Pre-commit Checks

1. **Grep for conflicts**:
   ```bash
   # Should find only agent role references and generic usage
   grep -rn "Reviewer" docs/ README.md QUICK_START.md adversarial_workflow/
   ```

2. **Check consistency**:
   ```bash
   # Should find Author-Evaluator pattern consistently
   grep -rn "Author.*Evaluator" docs/ README.md
   ```

3. **Verify technical vars unchanged**:
   ```bash
   # Should still use EVALUATOR_MODEL
   grep -rn "EVALUATOR_MODEL" adversarial_workflow/ .adversarial/
   ```

### Smoke Tests

1. **Documentation reads naturally**: Read updated sections aloud - does "Evaluator" flow well?
2. **No ambiguity**: Is it clear "Evaluator" = aider QA, not agent infrastructure?
3. **Historical context preserved**: Can readers understand the terminology evolution?

---

## Deliverables

### Required Files

1. **Updated documentation** (7-8 files):
   - README.md
   - QUICK_START.md
   - docs/TERMINOLOGY.md
   - docs/EXAMPLES.md
   - docs/WORKFLOW_PHASES.md
   - docs/INTERACTION_PATTERNS.md
   - docs/TROUBLESHOOTING.md (if needed)

2. **Updated templates** (3-5 files):
   - adversarial_workflow/templates/*.template files with user-facing text

3. **Updated code** (1 file):
   - adversarial_workflow/cli.py (user-facing messages only)

4. **Decision document**:
   - delegation/decisions/TASK-TERMINOLOGY-001-REVERT-DECISION.md

5. **CHANGELOG entry**:
   - Add v0.3.2 entry documenting the reversion

### Commit Message

```
docs: Revert "Reviewer" → "Evaluator" terminology for clarity (v0.3.2)

Terminology Reversion:
- Change "Reviewer" back to "Evaluator" for aider-powered QA role
- Eliminates ambiguity with "document-reviewer" agent role
- Aligns with technical naming (EVALUATOR_MODEL environment variable)
- "Evaluator" is more precise: evaluates quality/correctness vs generic "review"

Rationale:
- v0.2.0 changed "Evaluator" → "Reviewer" to match GitHub PR terminology
- This created new conflict with multi-agent "document-reviewer" role
- Users naturally refer to it as "Evaluator" (more precise term)
- Technical code already uses EVALUATOR_MODEL consistently

Updated Files (~20-30 occurrences):
- README.md: Author-Evaluator workflow pattern
- docs/TERMINOLOGY.md: Added Evaluator vs document-reviewer distinction
- QUICK_START.md: Updated workflow examples
- docs/EXAMPLES.md: Updated usage patterns
- docs/WORKFLOW_PHASES.md: Phase descriptions use Evaluator
- Templates: Script comments and messages updated
- cli.py: User-facing output messages (line 322)

Preserved:
- Agent role names (document-reviewer unchanged)
- Technical variables (EVALUATOR_MODEL, evaluator_model)
- Historical documents (EVALUATOR-QA-*.md, archived tasks)
- CHANGELOG history (v0.2.0 terminology change documented)

Decision Document: delegation/decisions/TASK-TERMINOLOGY-001-REVERT-DECISION.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Agent Assignment

**Assigned to**: `document-reviewer`

**Rationale**:
- This is primarily a documentation task (search & replace across docs)
- Requires careful reading to avoid unintended changes
- Document-reviewer agent specializes in documentation quality
- Ironic but appropriate: document-reviewer updates "Reviewer" → "Evaluator" to avoid confusion with itself!

**Skills Required**:
- Careful text search & replace
- Context-aware editing (don't change technical vars)
- Documentation consistency verification
- Writing clear decision documents

---

## Context for Agent

### Key Points to Understand

1. **What is "Evaluator"?**
   - The aider-powered quality check role in adversarial-workflow
   - NOT an agent, NOT infrastructure, NOT a persistent system
   - Technical reality: `aider --model gpt-4o --message "review prompt"`

2. **What is "document-reviewer"?**
   - An agent role in the multi-agent coordination system
   - One of 8 roles in agent-handoffs.json
   - Completely separate from Evaluator role

3. **Why the confusion?**
   - Both terms relate to "reviewing" but at different levels
   - "Reviewer" was too generic and created overlap
   - "Evaluator" is more specific and precise

4. **What are we changing?**
   - User-facing documentation: "Reviewer" → "Evaluator"
   - Keep technical names: `EVALUATOR_MODEL` (already correct)
   - Keep agent roles: "document-reviewer" (unchanged)

### Read These First

Before starting, read these files to understand context:
1. `delegation/decisions/TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md` - The v0.2.0 decision
2. `EVALUATOR-QA-RESPONSE.txt` - The QA that triggered v0.2.0 change
3. `docs/TERMINOLOGY.md` - Current terminology standards

---

## Timeline

- **Setup & Reading**: 15 min
- **Phase 1 (Automated)**: 30 min
- **Phase 2 (Context-dependent)**: 60 min
- **Phase 3 (Verification)**: 30 min
- **Decision Document**: 15 min
- **Total**: 2.5-3 hours

---

## Questions?

**Q: Should I change "code review" or "pull request review"?**
A: No. These are generic terms, not referring to the Evaluator role.

**Q: What about EVALUATOR_MODEL environment variable?**
A: Leave it unchanged. It's already correct and changing it would break backward compatibility.

**Q: Should I update CHANGELOG.md?**
A: Yes, add a new v0.3.2 entry. Don't modify existing v0.2.0 entry.

**Q: What about files in delegation/decisions/ and delegation/tasks/archived/?**
A: Don't modify them. They're historical records and should remain as-is.

**Q: How do I handle "document-reviewer" agent role?**
A: Never change it. It's a proper noun (agent role name), not the generic "Reviewer" we're replacing.

---

**Ready to start?** Begin with Phase 1 automated replacements, then carefully work through Phase 2 context-dependent changes.
