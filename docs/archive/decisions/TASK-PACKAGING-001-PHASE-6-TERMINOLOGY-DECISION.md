# TASK-PACKAGING-001-PHASE-6: Terminology Decision Record

**Date**: 2025-10-15
**Decision**: Author / Reviewer terminology ✅
**Status**: APPROVED - Ready for execution

---

## Terminology Selection

After analyzing 8 options, selected **"Author / Reviewer"** terminology.

### Rejected Options
1. ❌ Proposer / Evaluator
2. ❌ Developer / Reviewer
3. ❌ Builder / Inspector
4. ❌ Creator / Critic
5. ❌ Implementer / Validator
6. ❌ No paired roles (phase-only language)
7. ❌ Drafter / Reviewer
8. ❌ Hybrid approach (different terms per phase)

### Selected: Author / Reviewer ✅

**Rationale**:
- ✅ Universal recognition (GitHub PRs, code reviews, academic papers)
- ✅ Tool-agnostic (no software or infrastructure assumptions)
- ✅ Clear separation of roles with no overlap
- ✅ Works naturally in all workflow phases
- ✅ Zero agent/persistence connotation
- ✅ Industry-standard terminology
- ✅ Memorable and concise

---

## Terminology Definitions

### Author
**Definition**: The person or tool that creates work products (plans, code, implementations).

**In practice**:
- Could be you (manual coding)
- Could be Claude Code (AI-assisted implementation)
- Could be Cursor, Copilot, aider, or any development tool
- Could be any combination of tools and methods

**Technical reality**: Whoever writes the files.

**Examples**:
- "The Author creates an implementation plan"
- "You (the Author) implement the changes"
- "The Author addresses feedback from the previous review"

### Reviewer
**Definition**: The independent analysis stage that critiques the Author's work.

**In practice**:
- This is aider running with GPT-4o or Claude
- Executed via command: `aider --model gpt-4o --message "review prompt"`
- NOT a persistent agent or special software
- NOT infrastructure you need to set up or configure

**Technical reality**: Aider CLI with different review prompts at each workflow phase.

**Examples**:
- "The Reviewer (aider + GPT-4o) analyzes the plan"
- "Aider reviews your git diff for completeness"
- "The Reviewer validates test results"

---

## Global Replacements Strategy

### Safe Replacements (Automated)

These can be done with find/replace:

```bash
# In all documentation files (*.md)
s/Coordinator agent/Author/g
s/feature-developer agent/Author/g
s/implementation agent/Author/g
s/Evaluator agent/Reviewer/g
```

### Context-Dependent Replacements (Manual Review Required)

These need human judgment:

1. **"Coordinator"** → Context determines replacement:
   - When referring to plan creator → "Author"
   - When addressing user directly → "You"
   - In historical/contrast contexts → Keep with clarification

2. **"Evaluator"** → Context determines replacement:
   - When referring to review role → "Reviewer"
   - When referring to technical tool → "aider"
   - In variable names → Can keep (see below)

### Technical Variable Names (Backward Compatibility)

**Can stay unchanged** for configuration compatibility:
- `EVALUATOR_MODEL` (environment variable)
- `evaluator_model` (config.yml key)
- `$EVALUATOR_MODEL` (bash script variable)

**Rationale**: These are technical identifiers, not user-facing language. Changing them would break existing configurations.

---

## Implementation Phases

### Files Requiring Updates

**Documentation** (7 files):
- `README.md` - Main package documentation
- `docs/EXAMPLES.md` - Usage examples
- `docs/WORKFLOW_PHASES.md` - Phase descriptions
- `docs/INTERACTION_PATTERNS.md` - Workflow patterns
- `docs/TOKEN_OPTIMIZATION.md` - Cost optimization
- `docs/TROUBLESHOOTING.md` - Common issues
- `docs/TERMINOLOGY.md` - NEW: Standards document

**Templates** (7 files):
- `templates/evaluate_plan.sh.template`
- `templates/review_implementation.sh.template`
- `templates/validate_tests.sh.template`
- `templates/config.yml.template`
- `templates/README.template`
- `templates/.env.example.template`
- `templates/example-task.md.template`

**Python Code** (1 file):
- `adversarial_workflow/cli.py` - User-facing messages only (not variable names)

**Analysis** (1 file):
- `delegation/tasks/analysis/ADVERSARIAL-WORKFLOW-INDEPENDENCE-ANALYSIS.md`

**Total**: ~16 files requiring updates

---

## Writing Guidelines

### ✅ GOOD Examples

**Clear role identification**:
- "The Author creates an implementation plan in tasks/feature.md"
- "The Reviewer (aider + GPT-4o) provides critical feedback"
- "You (the Author) implement using any method you prefer"

**Technical clarity**:
- "Run `adversarial evaluate tasks/feature.md` to start review"
- "This executes: `aider --model gpt-4o --read tasks/feature.md`"
- "Aider (the Reviewer) analyzes your git diff"

**Workflow description**:
- "The Author-Reviewer workflow prevents phantom work"
- "Multiple verification stages with independent review"

### ❌ BAD Examples

**Agent language** (deprecated):
- ❌ "The Coordinator agent creates a plan"
- ❌ "The Evaluator agent reviews it"
- ❌ "The feature-developer implements changes"
- ❌ "Coordinator-Evaluator pattern"

**Ambiguous language**:
- ❌ "The system creates a plan" (Who? What system?)
- ❌ "AI reviews the code" (Which AI? How?)
- ❌ "Automatic validation" (What's the mechanism?)

---

## Clarity Rules

### Rule 1: First Mention - Always Clarify

When introducing a role for the first time in a document:

```markdown
✅ "The Author (you, or your AI assistant) creates a plan"
✅ "The Reviewer (aider with GPT-4o) analyzes it"
```

### Rule 2: Subsequent Mentions - Context Should Be Clear

After roles are introduced:

```markdown
✅ "The Author implements according to the approved plan"
✅ "The Reviewer checks for phantom work"
```

### Rule 3: Technical Docs - Use Explicit Terms

In technical documentation, prefer explicit over metaphorical:

```markdown
✅ "You create tasks/feature.md"
✅ "Run: adversarial evaluate tasks/feature.md"
✅ "This executes: aider --model gpt-4o --read tasks/feature.md"
```

---

## Deprecation Notice

### Deprecated Terminology (Do Not Use)

The following terms are **deprecated** as of Phase 6:

| Deprecated Term | Replace With | Context |
|----------------|--------------|---------|
| Coordinator | Author | Plan/code creator |
| Coordinator agent | Author | Plan/code creator |
| Evaluator | Reviewer | Review role |
| Evaluator agent | Reviewer | Review role |
| Feature-developer agent | Author or Developer | Implementation |
| Implementation agent | Author | Implementation |
| Coordinator-Evaluator pattern | Author-Reviewer workflow | Workflow description |

**Exception**: Technical variable names (`EVALUATOR_MODEL`, `evaluator_model`) remain for backward compatibility.

---

## Expected Impact

### Documentation Clarity
- **Before**: "Coordinator and Evaluator" - unclear if these are agents/infrastructure
- **After**: "Author and Reviewer" - clear these are roles, not technical requirements

### User Onboarding
- **Before**: Users might think they need special agent setup
- **After**: Users understand they just need aider + API keys

### Consistency
- **Before**: Mixed terminology across docs (Coordinator, Plan Author, You)
- **After**: Consistent Author/Reviewer language throughout

### Confusion Risk
- **Before**: HIGH - Evaluator flagged as critical issue
- **After**: LOW - Universal, familiar terminology

---

## Next Steps

1. ✅ **Decision made**: Author / Reviewer
2. ✅ **Plan updated**: TASK-PACKAGING-001-PHASE-6-EVALUATOR-FIXES.md
3. 🔄 **Ready for execution**: Phase 6A (Comprehensive Documentation Audit)

---

## Approval

**Approved by**: User
**Date**: 2025-10-15
**Ready to execute**: YES ✅

---

**Document Status**: FINAL
**Next Action**: Execute Phase 6A - Comprehensive Documentation Audit
