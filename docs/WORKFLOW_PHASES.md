# Workflow Phases: Complete Guide

This document provides a **detailed phase-by-phase guide** to the adversarial workflow, with examples, error handling, and best practices for each stage.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Phase 0: Investigation (Optional)](#phase-0-investigation-optional)
- [Phase 1: Plan Evaluation](#phase-1-plan-evaluation)
- [Phase 2: Implementation](#phase-2-implementation)
- [Phase 3: Code Review](#phase-3-code-review)
- [Phase 4: Test Validation](#phase-4-test-validation)
- [Phase 5: Final Approval](#phase-5-final-approval)
- [Error Recovery](#error-recovery)
- [Workflow Variations](#workflow-variations)

---

## Quick Reference

| Phase | Who | Input | Output | Duration | Command |
|-------|-----|-------|--------|----------|---------|
| 0 | Author | Task spec | Investigation doc | 15-60min | Manual research |
| 1 | Reviewer | Task + Plan | Evaluation | 5-15min | `adversarial evaluate` |
| 2 | Author | Approved plan | Git commits | 30-120min | Manual implementation |
| 3 | Reviewer | Git diff + Plan | Code review | 5-15min | `adversarial review` |
| 4 | Reviewer | Test results | Validation | 5-10min | `adversarial validate` |
| 5 | Author | All artifacts | Final commit | 10-20min | Manual finalization |

**Typical total time**: 1.5-4 hours per task

**Success rate**: 95%+ when all phases completed

---

## Phase 0: Investigation (Optional)

**When to use**: Complex bugs, unclear requirements, unfamiliar codebase areas.

**When to skip**: Simple tasks with clear requirements, familiar code.

### Goals

1. Understand current state
2. Identify root causes
3. Clarify scope and requirements
4. Gather evidence for planning

### Process

#### Step 1: Define Investigation Questions

Create investigation document:

```markdown
# TASK-2025-015-INVESTIGATION-FINDINGS.md

## Investigation Questions

1. What is the current Clip API?
   - Constructor parameters?
   - Public methods?
   - Property vs methods?

2. What are tests expecting?
   - Which parameters do they use?
   - What errors are occurring?

3. How many files affected?
   - Just tests or production code too?
   - Other test files using same API?

4. What's the correct fix?
   - Update tests to match API?
   - Or update API to match tests?
```

#### Step 2: Gather Evidence

Use grep, code inspection, git history:

```bash
# Inspect the API
cat thematic_cuts/shared/data_models.py | grep -A 30 "class Clip"

# Find all usages
grep -r "Clip(" tests/

# Check git history for context
git log --oneline -20 -- thematic_cuts/shared/data_models.py

# Look for related documentation
grep -r "Clip API" docs/
```

#### Step 3: Document Findings

```markdown
## Findings

### 1. Current Clip API

**Constructor** (data_models.py:45-52):
```python
@dataclass
class Clip:
    name: str                    # REQUIRED
    start_timecode: str          # NOT "start"!
    end_timecode: str            # NOT "end"!
    description: str = ""
```

**Methods**:
- `duration_frames` - Property (no parameters)
- `duration_frames_otio(fps)` - Method (takes fps parameter)

### 2. Test Expectations

**File**: `tests/test_otio_integration/test_critical_precision.py`

**Lines 188-190** (WRONG):
```python
clip = Clip(start="00:01:00:00", end="00:02:00:00")
#           ^^^^^^ Wrong parameter names
#           Missing 'name=' parameter
```

**Lines 197** (WRONG):
```python
frames = clip.duration_frames(fps)
#                              ^^^ duration_frames is property, not method
```

### 3. Scope Analysis

**Files affected**: 1 file only
- `tests/test_otio_integration/test_critical_precision.py`

**Production code affected**: ZERO
```bash
$ grep -r 'Clip(start=' thematic_cuts/ --include="*.py"
# (no results - only in tests!)
```

**Other test files**: ZERO
```bash
$ grep -r 'Clip(start=' tests/ --include="*.py"
tests/test_otio_integration/test_critical_precision.py:188:    clip = Clip(start=...
tests/test_otio_integration/test_critical_precision.py:212:    clip = Clip(start=...
# Only 2 instances in 1 file
```

### 4. Recommended Fix

**Approach**: Update test to match production API

**Why NOT update API**:
- API is correct (matches SMPTE conventions)
- Used throughout codebase correctly
- Only these 2 test calls are wrong
- Smaller scope (8 lines vs 50+ files)

**Confidence**: 99% (evidence-based)
```

#### Step 4: Create Plan from Findings

Use investigation to write detailed implementation plan:

```markdown
## Implementation Plan

**Scope**: 8 line changes in 1 file

**File**: `tests/test_otio_integration/test_critical_precision.py`

**Changes**:

1. **Line 188-190**: Fix Clip constructor
   ```python
   # SEARCH:
   clip = Clip(start="00:01:00:00", end="00:02:00:00", description="Test")
   
   # REPLACE:
   clip = Clip(
       name="test_validation",
       start_timecode="00:01:00:00",
       end_timecode="00:02:00:00",
       description="Test"
   )
   ```

2. **Line 197**: Fix duration_frames call
   ```python
   # SEARCH:
   frames = clip.duration_frames(fps)
   
   # REPLACE:
   frames = clip.duration_frames_otio(fps)
   ```

[Continue with all 6 fixes...]

**Acceptance Criteria**:
- 4 xfailed tests in `test_critical_precision.py` now pass
- 0 regressions in other tests
- Exit code 0
```

### Example Output

See real example: [TASK-2025-015-INVESTIGATION-FINDINGS.md](https://github.com/movito/thematic-cuts/blob/main/delegation/tasks/active/TASK-2025-015-INVESTIGATION-FINDINGS.md)

### Tips

**Good investigation**:
- Evidence-based (code quotes, grep results)
- Quantified (X files, Y lines, Z instances)
- Confidence levels stated
- Clear recommendation

**Poor investigation**:
- Assumptions without verification
- "Probably" and "might be"
- No code evidence
- Unclear scope

### Time Investment

- **Simple bug**: 15-30 minutes
- **Complex issue**: 45-90 minutes

**ROI**: Investigation time saves 2-3x in implementation and debugging.

---

## Phase 1: Plan Evaluation

**Required for**: All tasks except trivial fixes (<5 lines)

**Who**: Reviewer (aider + GPT-4o)

**Goal**: Catch design flaws BEFORE coding begins

### Process

#### Step 1: Create Task File with Plan

Your task file should include:

```markdown
# TASK-2025-016-consistent-assembly-api-fixes.md

## Problem
7 tests in test_consistent_assembly.py are xfailed due to ThematicList API mismatch.

## Current State
- 7/35 tests xfailed
- Tests use old `create_from_clips(clips)` API
- New API is `create_from_clips(clips, metadata)`

## Implementation Plan

**Scope**: Update 7 test functions

**Files**:
- `tests/test_consistent_assembly.py` (EDIT)

**Changes**:

1. `test_empty_list` (line 45)
   - Add `metadata={}` parameter
   
2. `test_single_clip` (line 67)
   - Add `metadata={"theme": "test"}`
   
[... continue for all 7 tests]

**Acceptance Criteria**:
- 7 xfailed tests now pass (35/35 total)
- 0 regressions in other tests
- Exit code 0
- Pass rate: 85.1% → 87.1%

**Risks**:
- Other tests might use same API (grep verification needed)
- Metadata format might be wrong
- Edge cases (empty clips, None values)

**Time Estimate**: 45 minutes
```

#### Step 2: Run Evaluation

```bash
cd my-project/
adversarial evaluate tasks/TASK-2025-016-consistent-assembly-api-fixes.md
```

**What happens**:
1. Evaluator reads task file
2. Applies evaluation criteria (completeness, design, risks, etc.)
3. Writes evaluation to `.adversarial/logs/TASK-2025-016-PLAN-EVALUATION.md`
4. Displays verdict: APPROVED / NEEDS_REVISION / REJECT

#### Step 3: Review Evaluation

```bash
cat .adversarial/logs/TASK-2025-016-PLAN-EVALUATION.md
```

**Example evaluation output**:

```markdown
## Evaluation Summary
**Verdict:** NEEDS_REVISION
**Confidence:** MEDIUM
**Estimated Implementation Time:** 1.5 hours (not 45min)

## Strengths
- Clear problem statement
- Specific file and line numbers
- Good acceptance criteria with metrics
- Risks identified

## Concerns & Risks
- [CRITICAL] Plan doesn't verify grep for other usages of `create_from_clips`
  → If other tests use this API, they'll break too
- [MEDIUM] No specification of metadata structure
  → What keys are required? Optional?
- [LOW] No error handling plan for invalid metadata

## Missing or Unclear
- Grep verification step missing from plan
- Metadata schema undefined
- No test for error cases (invalid metadata)

## Specific Recommendations
1. Add grep step: `grep -r 'create_from_clips' tests/`
2. Document metadata structure (required keys, types)
3. Consider adding 1 error test (invalid metadata → raises error)

## Questions for Author
1. Should all 7 tests use same metadata or different themes?
2. Is metadata schema documented anywhere?

## Approval Conditions
- Add grep verification to ensure all usages covered
- Specify metadata structure explicitly
- Update time estimate to 1-1.5 hours

Once these are addressed → APPROVED
```

#### Step 4: Address Feedback

Update your task file:

```markdown
## Implementation Plan (REVISED)

**Pre-implementation verification**:
```bash
# Verify all usages of create_from_clips
grep -r 'create_from_clips' tests/
# Expected: Only 7 instances in test_consistent_assembly.py
```

**Metadata Schema** (from data_models.py:ThematicList):
```python
{
    "theme": str,        # Required
    "description": str,  # Optional
    "tags": List[str]    # Optional
}
```

**Changes**:

1. `test_empty_list` (line 45)
   ```python
   # SEARCH:
   result = create_from_clips([])
   
   # REPLACE:
   result = create_from_clips([], metadata={"theme": "empty"})
   ```

[... all changes with proper metadata]

**Time Estimate**: 1.5 hours (increased from 45min based on feedback)
```

#### Step 5: Re-evaluate (if needed)

```bash
adversarial evaluate tasks/TASK-2025-016-consistent-assembly-api-fixes.md
```

**Evaluation output (second iteration)**:

```markdown
## Evaluation Summary
**Verdict:** APPROVED
**Confidence:** HIGH
**Estimated Implementation Time:** 1.5 hours

## Strengths
- Addressed all feedback from previous review ✅
- Grep verification added
- Metadata schema clearly specified
- Realistic time estimate

## Approval Conditions
- Watch for edge cases during implementation
- If grep reveals other usages, expand scope
- Verify metadata schema against latest code

Proceed to implementation phase.
```

### Evaluation Criteria

The evaluator checks:

1. **Completeness**
   - All requirements addressed?
   - Edge cases identified?
   - Error handling specified?

2. **Clarity**
   - Specific files and lines?
   - SEARCH/REPLACE blocks?
   - Clear acceptance criteria?

3. **Feasibility**
   - Approach technically sound?
   - Time estimate realistic?
   - Risks identified?

4. **Testability**
   - How to verify completion?
   - Metrics specified?
   - Test cases clear?

### Common Feedback Patterns

**"Too vague"**:
- Problem: "Fix the validation logic"
- Solution: "Add 3 checks to validate_clip(): name non-empty (line 45), valid timecode format (line 52), start < end (line 58)"

**"Missing verification"**:
- Problem: "Update all tests"
- Solution: "Grep verification: `grep -r 'old_api' tests/` to find all instances"

**"Unclear acceptance"**:
- Problem: "Tests should pass"
- Solution: "7 xfailed tests → passing, exit code 0, pass rate 85.1% → 87.1%"

**"Risks not addressed"**:
- Problem: "Change API signature"
- Solution: "Risk: Breaking change. Mitigation: Grep all usages, update or deprecate gracefully"

### Time Investment

- **First evaluation**: 5-10 minutes
- **Iteration (if NEEDS_REVISION)**: 3-5 minutes per iteration
- **Typical iterations**: 1-3

**ROI**: 15-30 minutes planning saves 1-2 hours of implementation rework.

---

## Phase 2: Implementation

**Who**: Author (you, or your AI assistant)

**Input**: Approved plan from Phase 1

**Goal**: Deliver working code according to plan

### Process

#### Step 1: Set Up Environment

```bash
# Create feature branch
git checkout -b feature/task-2025-016

# Ensure tests run
pytest tests/test_consistent_assembly.py

# Note baseline
# 28/35 passed, 7 xfailed
```

#### Step 2: Implement According to Plan

**Option A: Manual implementation**
```bash
# Edit files directly
vim tests/test_consistent_assembly.py

# Make changes per plan
# Test incrementally
pytest tests/test_consistent_assembly.py::test_empty_list -v
```

**Option B: Aider-assisted implementation**
```bash
aider --files tests/test_consistent_assembly.py \
      --read tasks/TASK-2025-016-api-fixes.md \
      --read .adversarial/logs/TASK-2025-016-PLAN-EVALUATION.md \
      --message "Implement the 7 API fixes according to the approved plan.

Follow the SEARCH/REPLACE blocks exactly.
After all changes, ensure pytest runs without errors." \
      --yes
```

**Benefits of aider approach**:
- Faster for mechanical changes
- Less typos
- Plan adherence automatic
- Still review git diff after

#### Step 3: Verify Implementation

```bash
# Check what changed
git diff

# Verify changes match plan
# Count: should be 7 changes as planned
grep -c 'metadata=' tests/test_consistent_assembly.py
# Expected: 7
```

#### Step 4: Test Incrementally

```bash
# Run affected tests
pytest tests/test_consistent_assembly.py -v

# Expected outcome from plan:
# 35/35 passed, 0 xfailed
```

#### Step 5: Commit (if tests pass)

```bash
git add tests/test_consistent_assembly.py
git commit -m "feat: Update ThematicList API calls in consistent assembly tests

- Updated 7 test functions to use new metadata parameter
- Fixed: test_empty_list, test_single_clip, test_multiple_clips, etc.
- All 7 xfailed tests now passing (35/35 total)

Task: TASK-2025-016
Approved plan: .adversarial/logs/TASK-2025-016-PLAN-EVALUATION.md"
```

**Note**: This is a work-in-progress commit. Final commit happens in Phase 5.

### Best Practices

**DO**:
- Follow approved plan closely
- Document any deviations in commit message
- Test incrementally (don't wait until end)
- Commit working states frequently
- Keep changes focused (one task per branch)

**DON'T**:
- Add unrelated changes ("while I'm here...")
- Skip testing until end
- Ignore plan without documenting why
- Leave TODOs/FIXMEs in core logic
- Commit broken code

### Handling Deviations

**What if plan doesn't work?**

1. **Minor adjustment** (implementation detail):
   - Make change
   - Document in commit message
   - Proceed

2. **Significant issue** (approach wrong):
   - Stop implementation
   - Document issue
   - Return to Phase 1 (revise plan)
   - Don't proceed with broken approach

**Example deviation**:

```bash
git commit -m "feat: Update ThematicList API calls (6 of 7 working)

Implemented 6 fixes successfully per plan.

DEVIATION: test_complex_metadata (line 145) requires different approach.
Plan assumed metadata structure, but test needs nested metadata.

Documented in TASK-2025-016-DEVIATION-NOTES.md
Will address in Phase 3 review."
```

### Time Investment

- **Simple fix** (mechanical changes): 15-45 minutes
- **Feature implementation**: 1-3 hours
- **Complex refactor**: 2-6 hours

**Factors**:
- Quality of plan (good plan = faster)
- Codebase familiarity
- Tool assistance (aider vs manual)
- Test complexity

---

## Phase 3: Code Review

**Who**: Reviewer (aider + GPT-4o)

**Input**: Git diff + approved plan + task file

**Goal**: Verify real code was delivered (not phantom work)

### Process

#### Step 1: Capture Implementation Artifacts

```bash
# Generate diff
git diff HEAD~1 > .adversarial/artifacts/TASK-2025-016-implementation.diff

# Generate stats
git diff HEAD~1 --stat > .adversarial/artifacts/TASK-2025-016-stats.txt

# Capture file status
git status --short > .adversarial/artifacts/TASK-2025-016-files.txt
```

**Why save artifacts?**
- Consistent review (same diff)
- Audit trail
- Can re-review later
- Token efficiency (reuse files)

#### Step 2: Run Code Review

```bash
adversarial review
```

**What happens**:
1. Reads git diff (actual changes)
2. Reads approved plan (expected changes)
3. Reads task file (requirements)
4. Checks for phantom work
5. Verifies plan adherence
6. Writes review to `.adversarial/logs/TASK-2025-016-CODE-REVIEW.md`

#### Step 3: Review Feedback

```bash
cat .adversarial/logs/TASK-2025-016-CODE-REVIEW.md
```

**Example: APPROVED review**

```markdown
## Review Summary
**Verdict:** APPROVED
**Implementation Quality:** EXCELLENT
**Phantom Work Risk:** NONE
**Test Coverage:** ADEQUATE

## What Was Actually Implemented

**File**: `tests/test_consistent_assembly.py`

**7 test functions updated** (all as planned):
1. `test_empty_list` (line 45) - Added `metadata={"theme": "empty"}`
2. `test_single_clip` (line 67) - Added `metadata={"theme": "single"}`
3. `test_multiple_clips` (line 89) - Added `metadata={"theme": "multiple"}`
4. `test_ordered_sequence` (line 112) - Added `metadata={"theme": "ordered"}`
5. `test_reverse_order` (line 134) - Added `metadata={"theme": "reverse"}`
6. `test_duplicate_clips` (line 156) - Added `metadata={"theme": "duplicates"}`
7. `test_complex_metadata` (line 178) - Added `metadata={"theme": "complex", "tags": ["test"]}`

**All changes are REAL CODE** - no TODOs, no comments, no stubs.

## Verification Checklist
- [x] Real code changes (not just comments/TODOs)
- [x] All requirements addressed (7 test updates)
- [x] Plan followed exactly
- [x] Tests updated as specified
- [x] No obvious bugs
- [x] Production ready

## Strengths
- Perfect plan adherence (all 7 fixes exactly as specified)
- Consistent metadata themes (good test naming)
- Clean implementation (no extra changes)
- Git history clean (one focused commit)

## Issues Found
### CRITICAL (must fix before approval)
- None

### MEDIUM (should fix)
- None

### LOW (nice to have)
- None

## Plan Deviation Analysis
**No deviations** - Implementation matches approved plan exactly.

## Approval Conditions
✅ All conditions met. Proceed to Phase 4 (test validation).
```

**Example: NEEDS_REVISION review**

```markdown
## Review Summary
**Verdict:** NEEDS_REVISION
**Implementation Quality:** POOR
**Phantom Work Risk:** HIGH
**Test Coverage:** MISSING

## What Was Actually Implemented

**File**: `tests/test_consistent_assembly.py`

**Lines 45-200**: Only comments and TODOs added:
```python
def test_empty_list():
    # TODO: Add metadata parameter
    # Need to figure out what metadata structure is
    result = create_from_clips([])  # FIXME: Update this call
```

**NO REAL CODE CHANGES** - This is phantom work.

## Verification Checklist
- [ ] Real code changes (❌ Only TODOs)
- [ ] All requirements addressed (❌ 0 of 7 tests fixed)
- [ ] Plan followed (❌ No implementation)
- [ ] Tests updated (❌ No actual changes)
- [ ] No obvious bugs (N/A - no code)
- [ ] Production ready (❌ Not functional)

## Issues Found
### CRITICAL (must fix before approval)
- **PHANTOM WORK DETECTED**: Git diff shows only comments and TODOs
- **NO ACTUAL CHANGES**: All 7 tests still use old API
- **PLAN NOT FOLLOWED**: Approved plan had specific SEARCH/REPLACE blocks

## Specific Improvements Needed
1. **Implement actual changes** (not TODOs)
   - Use SEARCH/REPLACE blocks from approved plan
   - Verify each change with grep after applying
   
2. **Remove all TODOs/FIXMEs** from core logic
   - TODOs are planning artifacts, not implementation
   
3. **Follow plan exactly** or document deviations
   - Plan specified 7 exact changes
   - Implement all 7

## Approval Conditions
❌ REJECT - Return to Phase 2 (implementation)

DO NOT proceed to testing. No real code was delivered.
```

#### Step 4: Address Feedback (if NEEDS_REVISION)

**If APPROVED**: Proceed to Phase 4

**If NEEDS_REVISION**:
1. Review specific issues listed
2. Fix each issue
3. Commit fixes
4. Re-run Phase 3 review

**If REJECT**:
1. Understand why (phantom work? wrong approach?)
2. Return to Phase 2 or Phase 1 (if approach wrong)
3. Start over with correct implementation

### Review Criteria

Reviewer checks for:

1. **Phantom Work** (CRITICAL)
   - TODOs instead of code?
   - Comments describing future work?
   - Stubs that don't implement logic?

2. **Plan Adherence**
   - Changes match approved plan?
   - Deviations documented?
   - Unexpected changes explained?

3. **Completeness**
   - All requirements from task addressed?
   - Edge cases handled?
   - Error handling present?

4. **Code Quality**
   - No obvious bugs?
   - Follows project conventions?
   - Appropriate variable/function names?

5. **Test Coverage**
   - New tests for new features?
   - Tests look meaningful (not stubs)?

### Common Issues

**Phantom work patterns**:
```python
# ❌ Pattern 1: TODO instead of code
def validate_clip(clip):
    # TODO: Implement validation logic
    pass

# ❌ Pattern 2: Comments describing future work
def validate_clip(clip):
    # This function should:
    # 1. Check name is non-empty
    # 2. Validate timecode format
    # 3. Ensure start < end
    return True  # FIXME

# ❌ Pattern 3: Stub that doesn't work
def validate_clip(clip):
    errors = []
    # Validation logic here
    return ValidationResult(valid=True, errors=errors)  # Always returns True!
```

**Real implementation**:
```python
# ✅ Actual logic
def validate_clip(clip):
    errors = []
    if not clip.name or not clip.name.strip():
        errors.append("Name required")
    if not is_valid_timecode(clip.start_timecode):
        errors.append(f"Invalid start: {clip.start_timecode}")
    if not is_valid_timecode(clip.end_timecode):
        errors.append(f"Invalid end: {clip.end_timecode}")
    # ... more checks ...
    return ValidationResult(valid=len(errors) == 0, errors=errors)
```

### Time Investment

- **Review execution**: 5-15 minutes
- **Addressing feedback** (if needed): 15-60 minutes

---

## Phase 4: Test Validation

**Who**: Reviewer (aider + GPT-4o)

**Input**: Test output + implementation + task requirements

**Goal**: Prove functionality works through tests

### Process

#### Step 1: Run Tests

```bash
# Run tests specified in task
pytest tests/test_consistent_assembly.py -v > .adversarial/artifacts/TASK-2025-016-test-output.txt 2>&1

# Capture exit code
echo $? > .adversarial/artifacts/TASK-2025-016-exit-code.txt

# Also capture summary
pytest tests/test_consistent_assembly.py --tb=short > .adversarial/artifacts/TASK-2025-016-test-summary.txt 2>&1
```

**Why save output?**
- Consistent analysis
- Audit trail
- Can re-analyze later

#### Step 2: Run Validation

```bash
adversarial validate "pytest tests/test_consistent_assembly.py -v"
```

**What happens**:
1. Reads test output
2. Reads task requirements
3. Parses pass/fail counts
4. Checks for regressions
5. Verifies acceptance criteria met
6. Writes analysis to `.adversarial/logs/TASK-2025-016-TEST-VALIDATION.md`

#### Step 3: Review Validation Results

```bash
cat .adversarial/logs/TASK-2025-016-TEST-VALIDATION.md
```

**Example: PASS validation**

```markdown
## Validation Summary
**Verdict:** PASS
**Test Status:** ALL_PASS
**Exit Code:** 0
**Regressions Detected:** NO

## Test Results Breakdown
**Total Tests:** 35
**Passed:** 35 ✓
**Failed:** 0 ✗
**Skipped:** 0 ⊘
**XFailed:** 0 (expected failures)

## Requirement Verification
From task file: "7 xfailed tests should now pass (35/35 total)"

- [x] test_empty_list → PASSED ✓
- [x] test_single_clip → PASSED ✓
- [x] test_multiple_clips → PASSED ✓
- [x] test_ordered_sequence → PASSED ✓
- [x] test_reverse_order → PASSED ✓
- [x] test_duplicate_clips → PASSED ✓
- [x] test_complex_metadata → PASSED ✓
- [x] All specified tests passing: YES ✅

## Failed Tests Analysis
No failures. ✅

## Regression Analysis
- **Baseline pass rate:** 28/35 (80.0%)
- **Current pass rate:** 35/35 (100.0%)
- **Change:** +7 tests
- **New failures:** None ✅

## Code Coverage Assessment
- **Files modified:** `tests/test_consistent_assembly.py`
- **Tests exercising changes:** All 7 updated tests
- **Coverage adequate:** YES
- **Missing test cases:** None (comprehensive coverage)

## Performance Metrics
- **Test execution time:** 2.3s
- **Acceptable:** YES (< 10s for this suite)
- **Slow tests:** None

## Approval Decision

### PASS
✓ All requirements met
✓ Tests confirm implementation works
✓ No regressions detected
✓ Ready for final approval (Phase 5)

## Recommendations
1. Merge to main after Phase 5 approval
2. Update project pass rate metrics (80% → 100% for this suite)
3. Consider this approach for other API migrations
```

**Example: FAIL validation**

```markdown
## Validation Summary
**Verdict:** FAIL
**Test Status:** MULTIPLE_FAILURES
**Exit Code:** 1
**Regressions Detected:** YES

## Test Results Breakdown
**Total Tests:** 35
**Passed:** 33 ✓
**Failed:** 2 ✗
**Skipped:** 0 ⊘

## Requirement Verification
From task file: "7 xfailed tests should now pass (35/35 total)"

- [x] test_empty_list → PASSED ✓
- [x] test_single_clip → FAILED ✗ (REGRESSION)
- [x] test_multiple_clips → PASSED ✓
- [x] test_ordered_sequence → PASSED ✓
- [x] test_reverse_order → PASSED ✓
- [x] test_duplicate_clips → FAILED ✗ (REGRESSION)
- [x] test_complex_metadata → PASSED ✓

**Requirements partially met:** 5/7 targets passing, but 2 regressions ❌

## Failed Tests Analysis

### Test: test_single_clip
- **Location:** tests/test_consistent_assembly.py:67
- **Error:** `TypeError: create_from_clips() got an unexpected keyword argument 'metadata'`
- **Root Cause:** ThematicList.create_from_clips() doesn't accept metadata parameter (API mismatch)
- **Fix Needed:** Either update API or use different creation method

### Test: test_duplicate_clips
- **Location:** tests/test_consistent_assembly.py:156
- **Error:** Same as above
- **Root Cause:** Same API mismatch

## Regression Analysis
- **Baseline:** 28/35 passing (80.0%)
- **Current:** 33/35 passing (94.3%)
- **Change:** +5 tests (BUT 2 NEW failures)
- **New failures:** test_single_clip, test_duplicate_clips

**Root cause of regressions:** Investigation showed wrong API used.

## Approval Decision

### FAIL
✗ Target requirement NOT fully met (5/7 instead of 7/7)
✗ Regressions introduced (2 new failures)
✗ Exit code 1 (tests failed)

**Recommendation:** RETURN TO PHASE 2 (implementation)

## Specific Actions Needed
1. Investigate actual ThematicList.create_from_clips() signature
2. Fix API calls in test_single_clip and test_duplicate_clips
3. Re-run tests to verify 35/35 passing
4. Re-run Phase 4 validation
```

#### Step 4: Take Action Based on Verdict

**If PASS**:
- Proceed to Phase 5 (final approval)
- Document success metrics

**If CONDITIONAL_PASS**:
- Review caveats carefully
- Decide: acceptable trade-off or fix now?
- If acceptable: Create follow-up task, proceed to Phase 5
- If not acceptable: Return to Phase 2

**If FAIL**:
- Review failure analysis
- Fix identified issues
- Re-run tests
- Re-run Phase 4 validation
- **Do NOT proceed** until PASS or CONDITIONAL_PASS

### Validation Criteria

Test-runner checks:

1. **Test Execution**
   - Exit code 0? (success)
   - All tests ran?
   - No crashes/hangs?

2. **Requirement Coverage**
   - Task said "fix 7 tests" → are those 7 passing?
   - Metrics specified → are they achieved?

3. **Regressions**
   - New test failures?
   - Pass rate decreased?
   - Working features broken?

4. **Test Quality**
   - Tests actually exercising code?
   - Assertions meaningful?
   - Not just stubs?

### Common Issues

**False positives**:
```python
# ❌ Test passes but doesn't verify anything
def test_validation():
    clip = Clip(name="test", start_timecode="00:00:00:00", end_timecode="00:00:01:00")
    result = validate_clip(clip)
    # No assertion! Test always passes
```

**Regressions**:
```python
# Implementation changed API
# Old tests now fail

# ❌ Before: This worked
clip.get_duration()

# After your changes: This breaks
clip.get_duration()  # Now requires fps parameter!
```

**Flaky tests**:
```python
# ❌ Test fails randomly
def test_timing():
    start = time.time()
    process()
    duration = time.time() - start
    assert duration < 0.1  # Flaky! Depends on system load
```

### Time Investment

- **Test execution**: 1-10 minutes (depends on test suite)
- **Validation analysis**: 5-10 minutes
- **Fixing failures** (if needed): 15-60 minutes

---

## Phase 5: Final Approval

**Who**: Author (you)

**Input**: All previous phase artifacts

**Goal**: Create final commit with full audit trail

### Process

#### Step 1: Review All Artifacts

```bash
# Phase 1 artifacts
cat .adversarial/logs/TASK-2025-016-PLAN-EVALUATION.md

# Phase 3 artifacts
cat .adversarial/logs/TASK-2025-016-CODE-REVIEW.md

# Phase 4 artifacts
cat .adversarial/logs/TASK-2025-016-TEST-VALIDATION.md
```

**Verify**:
- [ ] Plan: APPROVED
- [ ] Code review: APPROVED or acceptable feedback addressed
- [ ] Test validation: PASS or CONDITIONAL_PASS with documented caveats

**If any not met**: Do NOT proceed. Return to appropriate phase.

#### Step 2: Create Final Commit

```bash
# Stage all changes
git add -A

# Create comprehensive commit message
git commit -m "$(cat <<'EOF'
feat: Fix ThematicList API calls in consistent assembly tests

Updated 7 test functions to use new create_from_clips(clips, metadata)
API signature. All xfailed tests now passing.

## Changes
- test_empty_list: Added metadata={"theme": "empty"}
- test_single_clip: Added metadata={"theme": "single"}
- test_multiple_clips: Added metadata={"theme": "multiple"}
- test_ordered_sequence: Added metadata={"theme": "ordered"}
- test_reverse_order: Added metadata={"theme": "reverse"}
- test_duplicate_clips: Added metadata={"theme": "duplicates"}
- test_complex_metadata: Added metadata with tags

## Results
- Tests: 35/35 passing (was 28/35)
- Pass rate: 100.0% (was 80.0%)
- Regressions: 0
- Exit code: 0

## Task Workflow
Task: TASK-2025-016-consistent-assembly-api-fixes
Phase 1: Plan approved (1 iteration)
Phase 3: Code review APPROVED - Real code, no phantom work
Phase 4: Test validation PASS - All requirements met

## Artifacts
- Plan evaluation: .adversarial/logs/TASK-2025-016-PLAN-EVALUATION.md
- Code review: .adversarial/logs/TASK-2025-016-CODE-REVIEW.md
- Test validation: .adversarial/logs/TASK-2025-016-TEST-VALIDATION.md
- Implementation diff: .adversarial/artifacts/TASK-2025-016-implementation.diff
EOF
)"
```

**Why such detailed commits?**
- **Audit trail**: Future you knows exactly what happened
- **Searchable**: grep for task numbers, metrics
- **Reproducible**: Links to all artifacts
- **Professional**: Clear documentation for team/reviewers

#### Step 3: Update Project Tracking

```markdown
# delegation/project-status.md (or similar)

## Recent Completions

### TASK-2025-016: Consistent Assembly API Fixes
**Completed:** 2025-10-14
**Status:** ✅ Complete
**Pass Rate Change:** 80.0% → 100.0% (+20.0%)
**Time Invested:** 2.5 hours (0.5h planning + 1h implementation + 0.5h review + 0.5h testing)
**Cost:** $0.42 (Phase 1: $0.08 + Phase 3: $0.14 + Phase 4: $0.06)
**Notes:** Perfect execution, no iterations needed
```

#### Step 4: Push and Create PR (if using pull requests)

```bash
# Push to remote
git push origin feature/task-2025-016

# Create pull request (if using gh CLI)
gh pr create --title "Fix ThematicList API in consistent assembly tests" \
             --body "$(cat <<'EOF'
## Summary
Updated 7 test functions in `test_consistent_assembly.py` to use new ThematicList API with metadata parameter.

## Results
- ✅ All 7 target tests now passing (35/35 total)
- ✅ Pass rate: 100.0% (was 80.0%)
- ✅ Zero regressions
- ✅ Exit code: 0

## Workflow
This task followed the adversarial workflow pattern:
- **Phase 1**: Plan evaluation (APPROVED, 1 iteration)
- **Phase 2**: Implementation (per approved plan)
- **Phase 3**: Code review (APPROVED, no phantom work)
- **Phase 4**: Test validation (PASS, all requirements met)
- **Phase 5**: Final approval with audit trail

## Artifacts
All phase artifacts available in:
- `.adversarial/logs/TASK-2025-016-*.md`
- `.adversarial/artifacts/TASK-2025-016-*`

## Testing
```bash
pytest tests/test_consistent_assembly.py -v
# 35 passed in 2.3s
```

## Task Reference
Task file: `tasks/TASK-2025-016-consistent-assembly-api-fixes.md`

Closes #16
EOF
)"
```

#### Step 5: Celebrate! 🎉

You've completed a full adversarial workflow cycle with:
- Evidence-based planning
- Independent verification
- Real code delivery (no phantom work)
- Proven functionality through tests
- Complete audit trail

### Commit Message Template

```
<type>: <short summary (72 chars max)>

<detailed description of what changed and why>

## Changes
- <change 1>
- <change 2>
...

## Results
- Tests: <current>/<total> passing (was <previous>/<total>)
- Pass rate: <current>% (was <previous>%)
- Regressions: <count>
- Exit code: <0 or 1>

## Task Workflow
Task: <TASK-ID>
Phase 1: <Plan status> (<iterations> iteration[s])
Phase 3: <Review status> - <key feedback>
Phase 4: <Validation status> - <key result>

## Artifacts
- Plan evaluation: .adversarial/logs/<TASK-ID>-PLAN-EVALUATION.md
- Code review: .adversarial/logs/<TASK-ID>-CODE-REVIEW.md
- Test validation: .adversarial/logs/<TASK-ID>-TEST-VALIDATION.md

[Optional: Breaking changes, migration notes, follow-up tasks]
```

**Types**: feat, fix, refactor, test, docs, chore

### Time Investment

- **Artifact review**: 5-10 minutes
- **Commit creation**: 5-10 minutes
- **PR creation**: 5-10 minutes
- **Total**: 15-30 minutes

---

## Error Recovery

### When Plan Gets NEEDS_REVISION (Phase 1)

**Don't panic!** This is **success** - you found issues before coding.

**Steps**:
1. Read evaluator feedback carefully
2. Address each concern (add details, clarify, etc.)
3. Update task file
4. Re-run evaluation
5. Repeat until APPROVED (typically 1-3 iterations)

**Time cost**: 15-45 minutes
**Time saved**: 1-3 hours of implementation rework

### When Code Review Detects Phantom Work (Phase 3)

**This is why we have Phase 3!**

**Steps**:
1. Acknowledge: AI delivered TODOs instead of code
2. Review what ACTUAL implementation looks like (see examples in review)
3. Return to Phase 2
4. Implement REAL CODE (not comments)
5. Re-run Phase 3

**Time cost**: 30-90 minutes to re-implement
**Time saved**: Avoided wasting time testing broken code

### When Tests Fail (Phase 4)

**Common causes**:
1. Implementation bug
2. Test itself is wrong
3. API mismatch
4. Regression introduced

**Steps**:
1. Read test output carefully
2. Identify root cause (which test? why fail?)
3. Fix issue (code or test)
4. Re-run tests
5. Re-run Phase 4 validation

**Time cost**: 15-60 minutes
**Alternative**: Wasted hours debugging after merge

### When You Want to Skip Phases

**Temptation**: "This is simple, I'll just implement it..."

**Risk**: Phantom work, regressions, wasted time

**Safe shortcuts**:
- **Can skip Phase 0**: If problem is clear and simple
- **Cannot skip Phase 1**: Always evaluate plan (even 5min is worth it)
- **Cannot skip Phase 3**: Phantom work detection is critical
- **Cannot skip Phase 4**: Tests prove it works
- **Can streamline Phase 5**: Simple commit message if task is trivial

**Rule of thumb**: If task < 5 lines, you can streamline. If task > 5 lines, follow all phases.

---

## Workflow Variations

### Quick Fix (< 10 lines)

```bash
# Simplified workflow for trivial fixes
1. Create simple plan in task file
2. Run adversarial evaluate (quick approval)
3. Implement
4. Run adversarial review (quick check)
5. Run tests + adversarial validate
6. Commit with basic message
```

**Time**: 30-60 minutes

### Complex Feature (100+ lines, multiple files)

```bash
# Extended workflow with Phase 0
0. Investigation (30-90 minutes)
   - Create findings document
   - Gather evidence
1. Plan evaluation (may take 2-4 iterations)
2. Implementation in stages
   - Implement module A
   - Test module A
   - Implement module B
   - Test module B
3. Combined code review
4. Full test validation
5. Comprehensive final commit
```

**Time**: 4-12 hours

### Emergency Hotfix

```bash
# Minimal workflow (use only when necessary!)
1. Quick plan (5 min)
2. Implement
3. Manual review (you review, not AI)
4. Test carefully
5. Deploy

# Follow up AFTER deployment:
- Run full adversarial review on the fix
- Document in retrospective
- Ensure no phantom work snuck in
```

**Time**: 15-30 minutes (but risky!)

**When appropriate**: Production down, customer blocked, security issue

**When NOT appropriate**: Regular development (follow full workflow)

---

## Conclusion

The adversarial workflow phases provide:

1. **Phase 0**: Understanding through investigation
2. **Phase 1**: Quality through planning
3. **Phase 2**: Focus through approved roadmap
4. **Phase 3**: Verification through objective review
5. **Phase 4**: Proof through testing
6. **Phase 5**: Documentation through audit trail

**Result**: Predictable, high-quality delivery with minimal rework.

**Key insight**: Time invested in early phases (0-1) pays off 10x in later phases (2-4).

The workflow is a system, not a checklist. Each phase builds on previous phases. Skipping phases breaks the system and reintroduces the problems (phantom work, regressions, wasted time) that the workflow solves.
