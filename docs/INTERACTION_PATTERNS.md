# Interaction Patterns: Adversarial Workflow

This document explains the **Author-Evaluator adversarial workflow** and how to use it effectively to prevent phantom work and improve AI code quality.

## Table of Contents

- [The Problem: Phantom Work](#the-problem-phantom-work)
- [The Solution: Adversarial Verification](#the-solution-adversarial-verification)
- [Core Principles](#core-principles)
- [Interaction Patterns](#interaction-patterns)
- [Real-World Examples](#real-world-examples)
- [Success Metrics](#success-metrics)

---

## The Problem: Phantom Work

**Phantom work** occurs when AI assistants claim to implement features but actually deliver:
- Comments describing what should happen (not actual code)
- TODO markers promising future implementation
- Stub functions that return placeholder values
- Changes that look right superficially but don't work

### Example of Phantom Work

**Task**: "Implement validation for Clip objects"

**What AI Claims**:
> ✅ I've implemented comprehensive validation for Clip objects with error handling.

**What Was Actually Delivered**:
```python
def validate_clip(clip):
    """
    Validates a Clip object.
    TODO: Implement validation logic
    - Check timecode format
    - Verify start < end
    - Validate name is non-empty
    """
    pass  # TODO: Add validation
```

**Impact**:
- Tests still fail
- You wasted time reviewing non-code
- You have to re-request the same work
- Project timeline slips

---

## The Solution: Adversarial Verification

The adversarial pattern introduces **independent verification gates** where a different AI model critically evaluates work before it proceeds.

### Key Insight

**Single AI agents suffer from confirmation bias** - they believe their own output is correct. By introducing a **second, adversarial agent**, we force objective evaluation.

### The Pattern

```
┌─────────────┐
│   Author    │ ──┐ Creates plan
└─────────────┘   │
                  ▼
┌─────────────┐   Plan
│  Evaluator  │ ──┐ Critiques critically
└─────────────┘   │
                  ▼
               Approved?
                 Yes │
                     ▼
┌─────────────┐   Implementation
│   Author    │ ──┐ Writes code
└─────────────┘   │
                  ▼
┌─────────────┐   Git Diff
│  Evaluator  │ ──┐ Reviews ACTUAL changes
└─────────────┘   │
                  ▼
               Real Code?
                 Yes │
                     ▼
┌─────────────┐   Test Results
│  Evaluator  │ ──┐ Validates functionality
└─────────────┘   │
                  ▼
                 DONE
```

**Why This Works**:
1. **Different models** = Different biases, blind spots
2. **Different roles** = Evaluator incentivized to find problems
3. **Objective artifacts** = Git diff proves real work happened
4. **Measurable outcomes** = Tests prove functionality works

---

## Core Principles

### 1. Separation of Concerns

**Author** (you, or your AI assistant like Claude Code, Cursor, aider):
- Plans implementation strategy
- Writes actual code
- Responds to feedback
- Makes final commits

**Evaluator** (aider + GPT-4o or Claude):
- Reviews plans for completeness
- Checks code for phantom work
- Verifies test coverage
- Provides critical feedback
- Analyzes test results objectively
- Identifies regressions
- Validates requirements met

### 2. Evidence-Based Review

Every review must examine **concrete artifacts**:

- **Plan Review**: Reads task specification
- **Code Review**: Reads git diff (actual changes)
- **Test Review**: Reads test output (actual results)

**Never** rely on AI's self-reporting. **Always** verify with git/tests.

### 3. Multi-Stage Gates

Each phase has **approval conditions**:

| Phase | Gate | Approval Criteria |
|-------|------|-------------------|
| 0 | Investigation | Findings documented, root cause clear |
| 1 | Plan | All requirements addressed, approach sound |
| 3 | Code Review | Real code present, no TODOs, plan followed |
| 4 | Tests | All target tests pass, no regressions |
| 5 | Final | All artifacts complete, audit trail clear |

**If any gate fails** → Fix and repeat. **Never** skip gates.

### 4. Critical Feedback Culture

The Evaluator must be **adversarial**, not friendly:

❌ **Wrong Evaluator Mindset**:
> "Great job! The plan looks good. Maybe consider edge cases."

✅ **Right Evaluator Mindset**:
> "NEEDS_REVISION: Plan doesn't specify error handling for invalid timecodes.
> What happens when start > end? Missing test cases for boundary conditions.
> Implementation steps too vague - which functions need changes?"

**Constructive** but **critical**. The goal is to **find problems** before code is written.

---

## Interaction Patterns

### Phase 0: Investigation (Optional)

**When to use**: Complex bugs, unclear requirements, unknown codebase areas.

**Pattern**:
```bash
# Author investigates
# (you, or your AI assistant)
grep -r "validate" thematic_cuts/
cat thematic_cuts/shared/data_models.py

# Documents findings
# Investigation reveals 3 validation functions exist but...

# Creates investigation document
TASK-2025-015-INVESTIGATION-FINDINGS.md
```

**Output**: Clear understanding of current state, root causes, scope.

### Phase 1: Plan Evaluation

**Pattern**:
```bash
# Author creates plan in task file
TASK-2025-016-api-fixes.md
  - Problem: Tests use old API
  - Solution: Update 6 test calls
  - Files: test_otio_integration.py
  - Acceptance: 4 xfailed tests pass

# Evaluator analyzes plan
adversarial evaluate TASK-2025-016-api-fixes.md

# Evaluator response saved to:
.adversarial/logs/TASK-2025-016-PLAN-EVALUATION.md
```

**Evaluator checks**:
- [ ] All requirements from task addressed?
- [ ] Edge cases identified?
- [ ] Files/functions specified clearly?
- [ ] Acceptance criteria measurable?
- [ ] Risks assessed?

**Possible verdicts**:
- `APPROVED` → Proceed to implementation
- `NEEDS_REVISION` → Author updates plan, re-evaluate
- `REJECT` → Fundamental approach wrong, start over

### Phase 2: Implementation

**Pattern**:
```bash
# Author implements according to plan
# (you, using any method: manual coding, AI assistant, etc.)

# Example: Using aider with plan context
aider --files test_otio_integration.py --read TASK-2025-016-api-fixes.md
```

**Key practices**:
- Follow approved plan closely
- Document any deviations and why
- Commit frequently with clear messages
- Add tests for new functionality

### Phase 3: Code Review

**Pattern**:
```bash
# Capture implementation artifacts
git diff > .adversarial/artifacts/TASK-2025-016-implementation.diff
git diff --stat > .adversarial/artifacts/TASK-2025-016-changes.txt

# Evaluator analyzes ACTUAL changes
adversarial review

# Reads: task file, approved plan, git diff
# Writes: .adversarial/logs/TASK-2025-016-CODE-REVIEW.md
```

**Evaluator checks for phantom work**:
```python
# ❌ PHANTOM WORK (reject)
def validate_clip(clip):
    # TODO: Implement validation
    pass

# ✅ REAL WORK (approve)
def validate_clip(clip):
    if not clip.name:
        return ValidationResult(valid=False, errors=["Name required"])
    if not is_valid_timecode(clip.start_timecode):
        return ValidationResult(valid=False, errors=["Invalid start"])
    return ValidationResult(valid=True, errors=[])
```

**Possible verdicts**:
- `APPROVED` → Proceed to testing
- `NEEDS_REVISION` → List specific fixes needed
- `REJECT` → Mostly TODOs/comments, start over

### Phase 4: Test Validation

**Pattern**:
```bash
# Run tests and capture output
pytest tests/test_shared/test_validation.py > .adversarial/artifacts/test-output.txt

# Evaluator analyzes results
adversarial validate "pytest tests/test_shared/test_validation.py"

# Reads: task file, test output, implementation diff
# Writes: .adversarial/logs/TASK-2025-016-TEST-VALIDATION.md
```

**Evaluator checks**:
- Exit code 0 (tests passed)?
- Specific tests mentioned in task now passing?
- No new failures introduced (regressions)?
- Test output shows real assertions passing?

**Example analysis**:
```
Task requirement: "Fix 6 xfailed tests in test_validation.py"

Test output shows:
- 35/35 tests in test_validation.py PASSED ✅
- 6 tests moved from xfailed → passed ✅
- 0 new failures ✅
- Exit code: 0 ✅

Verdict: PASS
```

### Phase 5: Final Approval

**Pattern**:
```bash
# Author (you) reviews all artifacts
1. Approved plan (Phase 1)
2. Code review approval (Phase 3)
3. Test validation pass (Phase 4)

# Creates final commit with full context
git add -A
git commit -m "feat: Fix Clip API in OTIO tests - 6 fixes, 4/4 tests passing

Task: TASK-2025-016
Plan: Approved 2025-10-13
Review: APPROVED - Real code, no phantom work
Tests: 4/4 xfailed→passing, 0 regressions
Pass rate: 85.1% → 86.9% (+1.8%)

Artifacts:
- Plan eval: .adversarial/logs/TASK-2025-016-PLAN-EVALUATION.md
- Code review: .adversarial/logs/TASK-2025-016-CODE-REVIEW.md
- Test results: .adversarial/logs/TASK-2025-016-TEST-VALIDATION.md"

# Push to branch for PR
git push origin feature/task-2025-016
```

---

## Real-World Examples

### Example 1: Phantom Work Detection (TASK-2025-014)

**Initial submission**:
```python
# First attempt by Author
def validate_clip(clip):
    """Validates Clip according to specification."""
    # TODO: Check name is non-empty
    # TODO: Verify timecode format
    # TODO: Ensure start < end
    return ValidationResult(valid=True)  # FIXME
```

**Evaluator verdict**: `REJECT - Phantom Work Detected`

**Feedback**:
> This is NOT implementation. These are TODOs describing future work.
> Requirement was "implement validation" not "plan validation".
> Git diff shows comments added, not logic.
> REJECT - Return to implementation phase.

**Second attempt** (after feedback):
```python
def validate_clip(clip):
    """Validates Clip according to specification."""
    errors = []
    
    if not clip.name or not clip.name.strip():
        errors.append("Clip name cannot be empty")
    
    if not is_valid_smpte_timecode(clip.start_timecode):
        errors.append(f"Invalid start timecode: {clip.start_timecode}")
    
    if not is_valid_smpte_timecode(clip.end_timecode):
        errors.append(f"Invalid end timecode: {clip.end_timecode}")
    
    if is_valid_smpte_timecode(clip.start_timecode) and is_valid_smpte_timecode(clip.end_timecode):
        if timecode_to_frames(clip.start_timecode) >= timecode_to_frames(clip.end_timecode):
            errors.append("Start timecode must be before end timecode")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )
```

**Evaluator verdict**: `APPROVED`

**Impact**: Prevented wasted testing time, ensured real implementation delivered.

### Example 2: Plan Improvement Through Iteration (TASK-2025-015)

**Original plan** (too vague):
> Fix the OTIO integration tests to use the correct API.

**Evaluator feedback**: `NEEDS_REVISION`
> What is "the correct API"? Which tests? Which functions?
> Need specific SEARCH/REPLACE blocks or file:line references.

**Revised plan** (specific):
> **File**: `tests/test_otio_integration/test_critical_precision.py`
> 
> **Changes** (6 fixes):
> 1. Line 188: `Clip(start=..., end=...)` → `Clip(name=..., start_timecode=..., end_timecode=...)`
> 2. Line 197: `clip.duration_frames(fps)` → `clip.duration_frames_otio(fps)`
> 3-6: [Similar specific changes]
> 
> **Acceptance**: 4 xfailed tests in `test_critical_precision.py` → passing

**Evaluator verdict**: `APPROVED`

**Outcome**: Implementation took 10 minutes instead of 2 hours of trial-and-error.

### Example 3: Test Validation Catches Regression (TASK-2025-016)

**Task**: Fix 7 consistent assembly tests.

**Implementation**: Author fixes tests, reports success.

**Test validation**:
```bash
pytest tests/test_consistent_assembly.py

# Output:
7 passed, 2 failed  # Wait, 2 new failures?
```

**Evaluator analysis**: `CONDITIONAL_PASS`
> Target requirement met: 7 tests now passing ✅
> However, 2 regressions introduced: test_empty_list, test_single_clip ⚠️
> 
> Root cause: API change to ThematicList broke edge cases.
> 
> Recommendation: Fix regressions before approval OR accept with follow-up task.

**Decision**: Created TASK-2025-016-FOLLOWUP, main task approved with caveat.

**Impact**: Regressions caught before merge, technical debt documented and tracked.

---

## Success Metrics

From the [thematic-cuts](https://github.com/movito/thematic-cuts) project (6 months of usage):

### Before Adversarial Workflow
- **Test pass rate**: 85.1% (298/350 tests)
- **Phantom work incidents**: ~2-3 per month
- **Average task completion time**: 3-5 hours (with rework)
- **Regressions introduced**: 1-2 per task
- **Cost per task**: $15-30 (many retries with full context)

### After Adversarial Workflow
- **Test pass rate**: 96.9% (339/350 tests)
- **Phantom work incidents**: 0 (caught by evaluator every time)
- **Average task completion time**: 2-3 hours (less rework)
- **Regressions introduced**: 0-1 per task (caught in Phase 4)
- **Cost per task**: $3-8 (single-shot, targeted context)

### Key Improvements

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Test pass rate | 85.1% | 96.9% | **+11.8%** |
| Phantom work | 2-3/month | 0/month | **100% reduction** |
| Task time | 3-5 hrs | 2-3 hrs | **40% faster** |
| Cost per task | $15-30 | $3-8 | **70% cheaper** |
| Regressions | 1-2/task | 0-1/task | **50% reduction** |

### Real Task Results

**TASK-2025-012**: OTIO API Wrapper
- Phantom work detected in Phase 3 (TODOs only) → NEEDS_REVISION
- Second attempt: Real implementation → APPROVED
- Tests: 8/8 passing, 0 regressions → PASS
- **Outcome**: ✅ Success

**TASK-2025-014**: Validation Framework
- Plan: 3 iterations to get specific enough → APPROVED
- Implementation: Real code, clean separation → APPROVED
- Tests: 35/35 passing BUT 4 new failures → CONDITIONAL_PASS
- Follow-up: TASK-2025-014-FOLLOWUP created
- **Outcome**: ✅ Success with documented trade-off

**TASK-2025-015**: OTIO Integration Fixes
- Investigation: Phase 0 with 30min research → Clear scope
- Plan: Approved on first try (good investigation) → APPROVED
- Implementation: 6/6 fixes, evaluator auto-implemented → APPROVED
- Tests: 4/4 xfailed→passing, 0 regressions → PASS
- **Outcome**: ✅ Perfect execution

**TASK-2025-016**: Consistent Assembly API
- Plan: Good initial plan → APPROVED
- Implementation: 7 test fixes → APPROVED
- Tests: 7 passing BUT 2 regressions → CONDITIONAL_PASS
- Follow-up: Issues tracked, acceptable trade-off
- **Outcome**: ✅ Success with known debt

**TASK-2025-017**: Semantic Parser
- Plan: Too vague → NEEDS_REVISION (2 iterations)
- Implementation: Good code → APPROVED
- Tests: All passing → PASS
- **Outcome**: ✅ Success (plan iteration saved implementation time)

---

## Best Practices

### 1. Invest in Planning
Spend 30-60 minutes on Phase 1 (planning + evaluation). This saves 2-3 hours of implementation rework.

### 2. Document Investigations
For complex bugs, create a Phase 0 investigation document. Evaluator can verify your understanding before planning.

### 3. Be Specific in Plans
Bad: "Fix the validation logic"
Good: "Add 3 checks to validate_clip(): name non-empty, valid timecode format, start < end"

### 4. Embrace Criticism
If Evaluator says NEEDS_REVISION, that's **success** - you found problems before writing code.

### 5. Use Real Artifacts
Always review git diff, never trust AI's description of what it did.

### 6. Track Technical Debt
If you accept a CONDITIONAL_PASS, immediately create a follow-up task for the issues.

---

## Anti-Patterns to Avoid

### ❌ Skipping Plan Review
> "The plan is simple, I'll just implement it."

**Result**: Missed edge cases, incomplete implementation, rework needed.

**Fix**: Always run Phase 1, even for "simple" tasks. Takes 5 minutes.

### ❌ Arguing with Evaluator
> "The evaluator is wrong, my implementation is fine!"

**Result**: You skip to testing, tests fail, you waste time debugging.

**Fix**: Address Evaluator feedback first, THEN test. Evaluator often catches real issues.

### ❌ Accepting TODOs
> "I'll finish the TODOs in the next iteration."

**Result**: TODOs accumulate, nothing actually works.

**Fix**: REJECT any code with TODOs/FIXMEs in core logic. TODOs only acceptable in comments for future enhancements.

### ❌ Trusting Test Descriptions
> "AI says tests pass, good enough."

**Result**: Tests might not actually run, or pass for wrong reasons.

**Fix**: Always examine actual test output. Look for pass counts, specific test names.

### ❌ Ignoring Regressions
> "2 new failures, but 7 tests fixed, net positive!"

**Result**: You break working features to fix broken ones.

**Fix**: Track regressions as technical debt. Create follow-up tasks. Consider reverting if regressions are critical.

---

## Conclusion

The adversarial workflow pattern transforms AI coding from "hope it works" to "proven to work" through:

1. **Multiple independent verification gates**
2. **Evidence-based review** (git diff, test output)
3. **Critical evaluation culture**
4. **Measurable success criteria**

The result: **Higher quality, lower cost, faster delivery**.

The key insight: **AI needs AI to keep it honest**.
