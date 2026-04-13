# Review Starter: ADV-0037

**Task**: ADV-0037 - Suppress Browser Opening During Evaluation
**Task File**: `delegation/tasks/4-in-review/ADV-0037-suppress-browser-opening.md`
**Branch**: feat/adv-0037-suppress-browser-opening → main
**PR**: https://github.com/movito/adversarial-workflow/pull/27

## Implementation Summary
- Added `--no-browser` flag to all aider invocations
- This prevents browser from opening to `platform.openai.com/api-keys` during evaluations
- Quick fix with minimal risk - just adds one flag to each aider command

## Files Changed
- `adversarial_workflow/evaluators/runner.py` (modified) - Add flag to Python runner
- `.adversarial/scripts/evaluate_plan.sh` (modified) - Add flag to shell script
- `.adversarial/scripts/review_implementation.sh` (modified) - Add flag to shell script
- `.adversarial/scripts/validate_tests.sh` (modified) - Add flag to shell script
- `tests/test_evaluator_runner.py` (modified) - Add test for --no-browser flag

## Test Results
- 481 tests passing (1 new test added)
- All CI jobs pass (12/12)

## Areas for Review Focus
- Verify `--no-browser` is correct aider flag (confirmed via `aider --help`)
- Verify placement of flag in command is correct
- Simple change with low risk

## Related ADRs
- None (simple bug fix)

---
**Ready for code-reviewer agent in new tab**
