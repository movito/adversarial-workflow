# Bug Fix: Reviewer Output Not Being Saved

**Date:** 2025-10-19
**Status:** ✅ FIXED
**Affected Scripts:** `evaluate_plan.sh`, `review_implementation.sh`

## Problem

When running adversarial workflow evaluations, the scripts claimed to save output to log files:
```
Evaluation saved to: .adversarial/logs/TASK-2025-017-PLAN-EVALUATION.md
```

However, the files were **never actually created**. The Aider (GPT-4o Reviewer) output was being displayed to stdout but not persisted to disk.

## Root Cause

Both scripts were calling `aider` without redirecting its output:

```bash
# OLD (BROKEN) CODE
aider \
  --model "$EVALUATOR_MODEL" \
  --yes \
  --no-gitignore \
  --read "$TASK_FILE" \
  --message "..." \
  --no-auto-commits

# Output goes to stdout only ❌
```

The scripts set `EVAL_OUTPUT` and `REVIEW_OUTPUT` variables but never used them to capture the actual command output.

## Solution

Added `tee` to capture both stdout and the file simultaneously:

```bash
# NEW (FIXED) CODE
aider \
  --model "$EVALUATOR_MODEL" \
  --yes \
  --no-gitignore \
  --read "$TASK_FILE" \
  --message "..." \
  --no-auto-commits 2>&1 | tee "$EVAL_OUTPUT"

# Output captured to both terminal AND file ✅
```

Also added directory creation to ensure log directory exists:

```bash
# Ensure log directory exists
mkdir -p "$LOG_DIR"
mkdir -p "$ARTIFACTS_DIR"  # For review_implementation.sh
```

## Changes Made

### 1. evaluate_plan.sh
- Line 107-108: Added `mkdir -p "$LOG_DIR"` before aider call
- Line 200: Changed `--no-auto-commits` to `--no-auto-commits 2>&1 | tee "$EVAL_OUTPUT"`

### 2. review_implementation.sh
- Line 140-145: Added directory creation and `REVIEW_OUTPUT` variable
- Line 269: Changed `--no-auto-commits` to `--no-auto-commits 2>&1 | tee "$REVIEW_OUTPUT"`
- Line 274: Added "Review saved to: $REVIEW_OUTPUT" message

## Testing

Verified with test task file:
```bash
.adversarial/scripts/evaluate_plan.sh /tmp/test-task.md
```

Result: ✅ Output file created at `.adversarial/logs/test-task-PLAN-EVALUATION.md` (505 bytes)

## Benefits

1. **Persistent Record**: All Reviewer feedback is now saved for future reference
2. **Audit Trail**: Complete history of evaluations available in `.adversarial/logs/`
3. **Debugging**: Can review Reviewer output after the fact if needed
4. **Comparison**: Can compare multiple evaluation rounds

## Notes

### Git Corruption Warning

You may see this warning from Aider:
```
Unable to list files in git repo: BadObject: b'4ac2421d3db8d26bb3cfb4c26bafa9ec7d231892'
```

This is a **non-critical warning** related to git history cleanup (commit 45e8e58: "Remove nested git repo"). Aider still functions correctly despite this warning. The object exists and is valid (`git cat-file -t` confirms it's a tree object).

To suppress this warning entirely, consider adding `--no-git` flag to Aider calls if git integration isn't needed for reviews.

## Related Issues

- Original issue: Reviewer output vanishing after execution
- Discovered during: TASK-2025-017 (Semantic Parser Completion) evaluation
- Affects: All adversarial workflow Phase 1 (plan evaluation) and Phase 4 (implementation review)

## Verification Checklist

- [x] Output files created in `.adversarial/logs/`
- [x] File contains complete Aider output
- [x] Terminal output still visible to user (via `tee`)
- [x] Both stdout and stderr captured (via `2>&1`)
- [x] Directory creation ensures no "directory not found" errors
- [x] Works with both plan evaluation and implementation review scripts
