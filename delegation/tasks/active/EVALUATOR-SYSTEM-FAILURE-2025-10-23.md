# Evaluator System Failure Diagnostic Report

**Date**: 2025-10-23
**Reporter**: coordinator agent
**Severity**: MEDIUM (system reports success but produces no evaluation)
**Impact**: Evaluator reviews appear to succeed but contain no actual review content

---

## Executive Summary

The `adversarial evaluate` command is encountering a git repository issue that causes Aider (the underlying tool) to fail silently. The command exits with "✅ Evaluation approved!" but the log file contains only git warnings, not the actual GPT-4o evaluation content. This creates a false positive - the system thinks the evaluation succeeded when it actually failed to run.

---

## Symptom

**Command**: `adversarial evaluate delegation/tasks/active/TASK-2025-026-aaf-export.md`

**Expected Output** (based on working examples):
```
Warning: Input is not a terminal (fd=0).
────────────────────────────────────────────────────────────────────────────────
Aider v0.86.1
Main model: gpt-4o with diff edit format
Weak model: gpt-4o-mini
Git repo: none
Repo-map: disabled
Added <task-file> to the chat (read-only).
Added <prompt-file> to the chat (read-only).

OVERALL ASSESSMENT
APPROVED

EXECUTIVE SUMMARY
[Actual evaluation content from GPT-4o...]

[... full evaluation ...]

Tokens: 11k sent, 474 received. Cost: $0.03 message, $0.03 session.
```

**Actual Output** (current broken behavior):
```
Warning: Input is not a terminal (fd=0).
────────────────────────────────────────────────────────────────────────────────
Unable to list files in git repo: BadObject:
b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'
Is your git repo corrupted?
Unable to read git repository, it may be corrupt?
BadObject: b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'

=== Plan evaluation complete ===

Evaluation saved to: .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md

Next steps:
1. Review evaluation output above
2. Plan author addresses feedback and updates plan
3. Run this script again if NEEDS_REVISION
4. Proceed to implementation if APPROVED

📝 Evaluating plan: delegation/tasks/active/TASK-2025-026-aaf-export.md

✅ Evaluation approved!
```

**Log File Content** (.adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md):
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

---

## Root Cause Analysis

### Issue 1: Git Repository BadObject Error

**Problem**: Aider is encountering a git object that it cannot read.

**Evidence**:
```bash
$ git cat-file -t 4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892
tree
```

The object exists and is valid (type: tree). Git fsck shows dangling objects but no corruption:
```bash
$ git fsck --full | grep -i corrupt
[no output - repo is not corrupt]
```

**Hypothesis**: Aider is trying to list files in the git repo for context and encountering a dangling tree object from a rebased/deleted branch. Instead of gracefully handling this, it exits early.

### Issue 2: Aider Git Repo Mode Misconfiguration

**Evidence from working evaluation** (TASK-2025-017-investigation-evaluation.log:6):
```
Git repo: none
Repo-map: disabled
```

This suggests Aider should be running with `--no-git` mode to avoid git scanning issues.

**Current behavior**: The adversarial evaluate script may not be passing `--no-git` flag to aider, causing it to attempt git repo scanning.

### Issue 3: False Positive Success Reporting

**Problem**: The adversarial evaluate wrapper script reports "✅ Evaluation approved!" even when aider fails to produce output.

**Evidence**:
- Script exits with success status
- Log file is created (but empty of evaluation content)
- No error detection for missing evaluation output

**Expected behavior**: Script should:
1. Check log file for evaluation content (OVERALL ASSESSMENT, EXECUTIVE SUMMARY, etc.)
2. If missing, report FAILURE not success
3. Exit with non-zero status code if evaluation didn't run

---

## Impact Assessment

**Severity**: MEDIUM

**User Impact**:
- Users believe their plans have been reviewed when they haven't
- False confidence in task specifications
- Wasted time discovering issues during implementation instead of planning

**Frequency**:
- TASK-2025-022: Failed (2025-10-21)
- TASK-2025-026: Failed (2025-10-23)
- Appears to have started recently (prior tasks like TASK-2025-017 worked)

**Workaround**: Manual review by coordinator agent (what was done for TASK-2025-026)

---

## Diagnostic Commands Run

```bash
# 1. Verify git object exists (PASS)
$ git cat-file -t 4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892
tree

# 2. Check git repo integrity (PASS)
$ git fsck --full 2>&1 | head -30
[Shows only dangling objects, no corruption]

# 3. Check adversarial CLI version
$ adversarial --version
# [No version flag available]

$ which adversarial
/Library/Frameworks/Python.framework/Versions/3.11/bin/adversarial

# 4. Check adversarial evaluate usage
$ adversarial evaluate --help
usage: adversarial evaluate [-h] task_file

positional arguments:
  task_file   Task file to evaluate

options:
  -h, --help  show this help message and exit

# 5. Compare working vs broken log files
# Working: .adversarial/logs/TASK-2025-017-investigation-evaluation.log (4760 bytes)
# Broken:  .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md (505 bytes)
```

---

## Recommended Fixes

### Fix 1: Add --no-git Flag to Aider (HIGH PRIORITY)

**File**: `adversarial-workflow/adversarial_workflow/commands/evaluate.py` (or wherever evaluate script lives)

**Change**: Add `--no-git` flag to aider invocation

**Before**:
```python
aider_cmd = [
    "aider",
    "--model", "gpt-4o",
    # ... other flags ...
]
```

**After**:
```python
aider_cmd = [
    "aider",
    "--model", "gpt-4o",
    "--no-git",  # <-- ADD THIS
    # ... other flags ...
]
```

**Rationale**: Working evaluations show "Git repo: none", indicating --no-git mode is expected. This prevents git scanning issues.

### Fix 2: Add Evaluation Output Validation (HIGH PRIORITY)

**File**: `adversarial-workflow/adversarial_workflow/commands/evaluate.py`

**Change**: After aider runs, validate the log file contains actual evaluation content

**Implementation**:
```python
def validate_evaluation_output(log_file_path):
    """Check if evaluation log contains actual evaluation content."""
    with open(log_file_path, 'r') as f:
        content = f.read()

    # Check for key evaluation sections
    required_sections = [
        "OVERALL ASSESSMENT",
        "EXECUTIVE SUMMARY",
        "DETAILED FINDINGS"
    ]

    for section in required_sections:
        if section not in content:
            return False, f"Missing section: {section}"

    # Check for common failure patterns
    failure_patterns = [
        "Unable to list files in git repo",
        "Is your git repo corrupted",
        "BadObject"
    ]

    for pattern in failure_patterns:
        if pattern in content and len(content) < 1000:
            # If file is small and contains error, evaluation failed
            return False, f"Evaluation failed: {pattern}"

    return True, "Evaluation output valid"

# After aider runs:
is_valid, message = validate_evaluation_output(log_file)
if not is_valid:
    print(f"❌ Evaluation failed: {message}")
    sys.exit(1)
else:
    print("✅ Evaluation approved!")
```

### Fix 3: Improve Error Reporting (MEDIUM PRIORITY)

**Change**: Capture aider stderr separately and report errors explicitly

**Implementation**:
```python
result = subprocess.run(
    aider_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

if result.returncode != 0:
    print(f"❌ Aider failed with exit code {result.returncode}")
    print(f"Error: {result.stderr}")
    sys.exit(1)
```

### Fix 4: Add Smoke Test (LOW PRIORITY)

**File**: `adversarial-workflow/tests/test_evaluate.py` (create if needed)

**Test case**:
```python
def test_evaluate_detects_git_issues():
    """Verify evaluate command handles git repo issues gracefully."""
    # Create minimal task file
    # Run evaluate
    # Verify it either succeeds with content OR fails explicitly (not false positive)
```

---

## Temporary Workaround

Until fixes are implemented, use this manual validation:

```bash
# After running adversarial evaluate
$ wc -l .adversarial/logs/TASK-XXXX-PLAN-EVALUATION.md

# If < 50 lines, evaluation likely failed - manually inspect
$ cat .adversarial/logs/TASK-XXXX-PLAN-EVALUATION.md

# If only git warnings, use manual review as fallback
```

---

## Testing Plan

After implementing fixes:

1. **Test with current repo state** (has BadObject issue)
2. **Test with clean repo** (clone fresh, no dangling objects)
3. **Test with intentionally broken task file** (should report evaluation with issues)
4. **Test with good task file** (should approve)
5. **Verify log files contain full evaluation content**

---

## Related Files

**Likely location of evaluation script**:
- `adversarial-workflow/adversarial_workflow/commands/evaluate.py`
- OR `adversarial-workflow/scripts/evaluate_plan.sh`

**Log files for comparison**:
- Working: `.adversarial/logs/TASK-2025-017-investigation-evaluation.log` (4760 bytes, full content)
- Broken: `.adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md` (505 bytes, warnings only)

**Evaluation prompt format**:
- `.adversarial/artifacts/TASK-2025-017-investigation-review-prompt.txt`

---

## Questions for Investigation

1. **When did this start failing?** Check git history for when TASK-2025-022 was evaluated (2025-10-21) - was that the first failure?

2. **What changed in the repo?** Check git log between last working evaluation and first failure

3. **Is it repo-specific or system-wide?** Try evaluating a task in a different repo with adversarial-workflow

4. **Which script runs the evaluation?** Find and inspect:
   ```bash
   $ grep -r "adversarial evaluate" adversarial-workflow/
   $ grep -r "Plan evaluation complete" adversarial-workflow/
   ```

---

## Priority Assessment

**HIGH**: Fixes 1 & 2 (--no-git flag + output validation)
**MEDIUM**: Fix 3 (error reporting)
**LOW**: Fix 4 (smoke test)

**Estimated fix time**: 30-45 minutes for HIGH priority fixes

---

## Contact Information

**Reported by**: coordinator agent (Claude Code Sonnet 4.5)
**Date**: 2025-10-23
**Session context**: AAF export task evaluation (TASK-2025-026)
**Repository**: thematic-cuts @ /Users/broadcaster_three/Github/thematic-cuts

**Fallback strategy used**: Manual evaluation by coordinator (comprehensive review completed and documented)

---

## Appendix: Full Command Output

```
$ adversarial evaluate delegation/tasks/active/TASK-2025-026-aaf-export.md
╔════════════════════════════════════════════╗
║   PHASE 1: PLAN EVALUATION                 ║
╚════════════════════════════════════════════╝

Task File: delegation/tasks/active/TASK-2025-026-aaf-export.md
Task: TASK-2025-026
Model: gpt-4o

=== REVIEWER (gpt-4o) ANALYZING PLAN ===

Warning: Input is not a terminal (fd=0).
────────────────────────────────────────────────────────────────────────────────
Unable to list files in git repo: BadObject:
b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'
Is your git repo corrupted?
Unable to read git repository, it may be corrupt?
BadObject: b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'

=== Plan evaluation complete ===

Evaluation saved to: .adversarial/logs/TASK-2025-026-PLAN-EVALUATION.md

Next steps:
1. Review evaluation output above
2. Plan author addresses feedback and updates plan
3. Run this script again if NEEDS_REVISION
4. Proceed to implementation if APPROVED

📝 Evaluating plan: delegation/tasks/active/TASK-2025-026-aaf-export.md


✅ Evaluation approved!
```

**Exit code**: 0 (success) - INCORRECT, should be non-zero since evaluation didn't run
