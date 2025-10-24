# TASK-2025-027: Fix Evaluator False-Positive Bug

**Status**: `ready_for_implementation`
**Priority**: `high`
**Assigned**: `feature-developer`
**Created**: 2025-10-24
**Target Completion**: 2025-10-24 (same day)
**Estimated Time**: 30-45 minutes

---

## Executive Summary

Fix critical bug in `adversarial evaluate` command that reports "✅ Evaluation approved!" when no actual evaluation occurred. The command exits with success status but produces empty log files containing only git warnings, creating false confidence that plans were reviewed.

## Business Context

### Current State
- ✅ adversarial-workflow system installed and operational
- ✅ Evaluation prompt templates working correctly
- ❌ `adversarial evaluate` reports success with empty output (false positive)
- ❌ No validation that GPT-4o actually reviewed the plan
- ❌ Users proceed with unreviewed plans, discovering issues during implementation

### Problem Discovery
- **First Failure**: TASK-2025-022 (2025-10-21)
- **Confirmed Failure**: TASK-2025-026 (2025-10-23)
- **Last Working**: TASK-2025-017 (prior to 2025-10-21)

### Impact
- **Severity**: HIGH - Undermines core value proposition of adversarial workflow
- **User Impact**: False confidence in unreviewed task specifications
- **Frequency**: 100% failure rate since 2025-10-21 (2/2 evaluations)
- **Workaround**: Manual coordinator reviews (time-consuming, inconsistent)

## Technical Architecture

### Root Cause Analysis

#### Issue 1: Aider Git Scanning Failure
**Problem**: Aider attempts to scan git repository for context, encounters dangling tree object from rebased branch, exits early without running GPT-4o evaluation.

**Evidence**:
```bash
$ adversarial evaluate delegation/tasks/active/TASK-2025-026-aaf-export.md

Warning: Input is not a terminal (fd=0).
────────────────────────────────────────────────────────────────────────────────
Unable to list files in git repo: BadObject:
b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'
Is your git repo corrupted?
Unable to read git repository, it may be corrupt?
BadObject: b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'

=== Plan evaluation complete ===
✅ Evaluation approved!
```

**Git Object Verification**:
```bash
$ git cat-file -t 4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892
tree  # Object exists and is valid

$ git fsck --full 2>&1 | grep -i corrupt
# No output - repo is not corrupted, just has dangling objects from rebases
```

**Working Example** (TASK-2025-017, 4760 bytes of content):
```
Aider v0.86.1
Main model: gpt-4o with diff edit format
Weak model: gpt-4o-mini
Git repo: none  ← KEY DIFFERENCE
Repo-map: disabled

OVERALL ASSESSMENT
APPROVED

EXECUTIVE SUMMARY
[... full GPT-4o evaluation ...]

Tokens: 11k sent, 474 received. Cost: $0.03 message, $0.03 session.
```

**Broken Example** (TASK-2025-026, 505 bytes, warnings only):
```
Warning: Input is not a terminal (fd=0).
────────────────────────────────────────────────────────────────────────────────
Unable to list files in git repo: BadObject:
b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'
Is your git repo corrupted?
Unable to read git repository, it may be corrupt?
BadObject: b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'

[END OF FILE - NO EVALUATION CONTENT]
```

#### Issue 2: Missing Output Validation
**Problem**: Evaluation wrapper script doesn't validate that Aider produced actual evaluation content. It sees "script finished" and reports success regardless of whether GPT-4o ran.

**Expected Behavior**:
- Check log file for required sections: `OVERALL ASSESSMENT`, `EXECUTIVE SUMMARY`, `DETAILED FINDINGS`
- If missing, report FAILURE not success
- Exit with non-zero status code if evaluation didn't run

**Current Behavior**:
- Creates empty log file
- Reports "✅ Evaluation approved!"
- Exits with status code 0 (success)

### Repository Location

**Target Repository**: `adversarial-workflow` (separate from thematic-cuts)

**Installation Location**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/adversarial`

**Likely Implementation Files**:
- `adversarial_workflow/commands/evaluate.py` - Main evaluation command
- OR `scripts/evaluate_plan.sh` - Shell script wrapper
- `adversarial_workflow/core/` - Core evaluation logic

**Find Command**:
```bash
# Locate adversarial-workflow repository
$ which adversarial
/Library/Frameworks/Python.framework/Versions/3.11/bin/adversarial

# Find installation directory
$ python3.11 -c "import adversarial_workflow; print(adversarial_workflow.__file__)"

# Search for evaluation code
$ grep -r "Plan evaluation complete" <adversarial-workflow-path>/
$ grep -r "Evaluation approved" <adversarial-workflow-path>/
```

## Implementation Plan

### Phase 1: Repository Location & Investigation (5-10 minutes)

1. **Locate adversarial-workflow repository**
   ```bash
   # Find package installation
   python3.11 -c "import adversarial_workflow; print(adversarial_workflow.__file__)"

   # Or search common locations
   ls ~/Github/adversarial-workflow
   ls ~/adversarial-workflow
   ```

2. **Find evaluation command implementation**
   ```bash
   cd <adversarial-workflow-repo>
   grep -r "adversarial evaluate" .
   grep -r "Plan evaluation complete" .
   grep -r "Evaluation approved" .
   ```

3. **Identify Aider invocation**
   ```bash
   grep -r "aider" . | grep -v ".git"
   grep -r "--model gpt-4o" .
   ```

### Phase 2: Fix 1 - Add --no-git Flag (10 minutes)

**Objective**: Prevent Aider from scanning git repository

**File**: `adversarial_workflow/commands/evaluate.py` (or equivalent)

**Before**:
```python
aider_cmd = [
    "aider",
    "--model", "gpt-4o",
    "--yes-always",
    # ... other flags ...
]
```

**After**:
```python
aider_cmd = [
    "aider",
    "--model", "gpt-4o",
    "--yes-always",
    "--no-git",  # CRITICAL FIX: Prevent git scanning issues
    # ... other flags ...
]
```

**Verification**:
- Run evaluation, check log for "Git repo: none"
- Should NOT see "Unable to list files in git repo" errors

### Phase 3: Fix 2 - Add Output Validation (15-20 minutes)

**Objective**: Detect when evaluation failed to produce content

**File**: Same as Phase 2

**Implementation**:
```python
def validate_evaluation_output(log_file_path: str) -> tuple[bool, str]:
    """
    Validate that evaluation log contains actual GPT-4o evaluation content.

    Returns:
        (is_valid, message): True if valid evaluation, False if failed
    """
    with open(log_file_path, 'r') as f:
        content = f.read()

    # Check minimum content size (working evaluations are >1000 bytes)
    if len(content) < 500:
        return False, f"Log file too small ({len(content)} bytes), likely failed"

    # Check for required evaluation sections
    required_sections = [
        "OVERALL ASSESSMENT",
        "EXECUTIVE SUMMARY"
    ]

    missing_sections = [s for s in required_sections if s not in content]
    if missing_sections:
        return False, f"Missing evaluation sections: {', '.join(missing_sections)}"

    # Check for known failure patterns
    failure_patterns = [
        ("Unable to list files in git repo", "Git repository scanning failed"),
        ("Is your git repo corrupted", "Git repository error"),
        ("BadObject", "Git object error")
    ]

    for pattern, description in failure_patterns:
        if pattern in content and len(content) < 1000:
            # Small file with error pattern = evaluation didn't run
            return False, f"Aider failed: {description}"

    # Check for token usage (indicates GPT-4o actually ran)
    if "Tokens:" not in content and "tokens" not in content.lower():
        return False, "No token usage found - GPT-4o may not have run"

    return True, "Evaluation output valid"


# In main evaluation function, after aider runs:
def evaluate_plan(task_file: str) -> int:
    # ... existing code to run aider ...

    # CRITICAL: Validate output before reporting success
    is_valid, message = validate_evaluation_output(log_file_path)

    if not is_valid:
        print(f"❌ Evaluation failed: {message}")
        print(f"Log file: {log_file_path}")
        print("\nPlease check the log file for details.")
        return 1  # Non-zero exit code
    else:
        print("✅ Evaluation completed successfully!")
        print(f"Review output in: {log_file_path}")
        return 0
```

**Verification**:
- Should catch empty log files with git errors
- Should catch logs missing required sections
- Should only approve logs with actual GPT-4o evaluation content

### Phase 4: Testing (5-10 minutes)

**Test Case 1: Current Broken State**
```bash
# Should now FAIL explicitly instead of false positive
$ adversarial evaluate delegation/tasks/active/TASK-2025-026-aaf-export.md

# Expected output:
❌ Evaluation failed: Missing evaluation sections: OVERALL ASSESSMENT, EXECUTIVE SUMMARY
Log file: .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md
```

**Test Case 2: After --no-git Fix**
```bash
# Should now SUCCEED with actual evaluation content
$ adversarial evaluate delegation/tasks/active/TASK-2025-026-aaf-export.md

# Expected output:
✅ Evaluation completed successfully!
Review output in: .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md

# Verify log file contains evaluation
$ wc -l .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md
# Should be >50 lines with OVERALL ASSESSMENT, EXECUTIVE SUMMARY, etc.
```

**Test Case 3: Regression Check**
```bash
# Test with a known working evaluation
$ adversarial evaluate delegation/tasks/active/TASK-2025-025-srt-transcript-analyzer.md

# Should succeed and produce full evaluation
```

## Success Criteria

### Required (Must Have)
- ✅ Aider runs with `--no-git` flag (prevents git scanning issues)
- ✅ Output validation detects empty/invalid evaluations
- ✅ False positives eliminated (empty evals report FAILURE not success)
- ✅ Working evaluations still succeed (no regressions)
- ✅ Test Case 2 passes (TASK-2025-026 gets full evaluation)

### Optional (Nice to Have)
- Enhanced error messages showing exactly what failed
- Separate stderr capture for better error reporting
- Unit tests for validation logic
- Documentation of fix in adversarial-workflow changelog

## Risk Assessment

**Risk Level**: LOW

**Rationale**:
- Changes are additive (new flag, new validation)
- Not modifying core evaluation logic
- Easy to rollback if issues arise
- Well-tested failure scenario available for validation

**Mitigation**:
- Test with both broken and working scenarios
- Verify no regressions on existing evaluations
- Document changes for future maintainers

## Dependencies

**External**:
- adversarial-workflow repository access
- Python environment with adversarial-workflow installed

**Internal**:
- None - this is a fix for infrastructure tooling

**Blocking**:
- None - can be implemented immediately

**Blocked By**:
- None

## Deliverables

1. **Code Changes**
   - `adversarial_workflow/commands/evaluate.py` with `--no-git` flag
   - Validation function `validate_evaluation_output()`
   - Integration of validation into main evaluation flow

2. **Testing Evidence**
   - Test output showing broken state now fails explicitly
   - Test output showing fix produces full evaluation content
   - Log file comparison (broken 505 bytes → fixed >4000 bytes)

3. **Documentation**
   - Commit message explaining false-positive bug and fix
   - Optional: Update adversarial-workflow README with troubleshooting

## Verification Steps

```bash
# 1. Verify --no-git flag present
$ grep -r "no-git" <adversarial-workflow-repo>/adversarial_workflow/

# 2. Verify validation function exists
$ grep -r "validate_evaluation_output" <adversarial-workflow-repo>/

# 3. Run evaluation and check output
$ adversarial evaluate delegation/tasks/active/TASK-2025-026-aaf-export.md

# 4. Check log file size and content
$ wc -l .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md
$ grep "OVERALL ASSESSMENT" .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md
$ grep "Tokens:" .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md

# 5. Verify exit codes
$ adversarial evaluate <invalid-task>.md; echo "Exit code: $?"
# Should be non-zero for invalid/failed evaluations
```

## Related Documents

- **Diagnostic Report**: `delegation/handoffs/EVALUATOR-SYSTEM-FAILURE-2025-10-23.md` (comprehensive analysis)
- **Executive Summary**: `delegation/handoffs/EVALUATOR-FAILURE-EXECUTIVE-SUMMARY.md` (quick reference)
- **Working Example Log**: `.adversarial/logs/TASK-2025-017-investigation-evaluation.log` (4760 bytes)
- **Broken Example Log**: `.adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md` (505 bytes)

## Notes

### Why This Happened

The adversarial-workflow system was likely developed in a clean repository without dangling git objects. When deployed to thematic-cuts (which has rebased branches creating dangling objects), Aider's git scanning failed. The wrapper script assumed Aider success based on process completion, not output validation.

### Why --no-git Works

Working evaluations (TASK-2025-017) show `Git repo: none`, indicating Aider doesn't need git context for plan evaluation. The task file and prompt provide all necessary context. Disabling git scanning eliminates the failure point without losing functionality.

### Why Validation Matters

Even with --no-git fix, future issues could cause Aider to fail silently. Output validation provides defensive programming - if Aider fails for any reason, the wrapper script will detect it and report failure instead of false positive success.

---

## Agent Instructions

**For feature-developer agent**:

1. **Locate Repository**
   - Find adversarial-workflow installation directory
   - Confirm you can modify the code

2. **Implement Fixes**
   - Add `--no-git` to Aider command (5 min)
   - Add validation function (15 min)
   - Integrate validation into evaluation flow (5 min)

3. **Test Thoroughly**
   - Run on TASK-2025-026 (should produce full evaluation now)
   - Run on TASK-2025-025 (regression check)
   - Verify log files contain evaluation content

4. **Document**
   - Create commit with clear message
   - Update this task file with results
   - Note any deviations from plan

**Time Budget**: 45 minutes maximum

**Success Indicator**: Running `adversarial evaluate delegation/tasks/active/TASK-2025-026-aaf-export.md` produces log file >2000 bytes with OVERALL ASSESSMENT and EXECUTIVE SUMMARY sections.
