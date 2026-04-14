# ADV-0054 Review Starter: Fix review_implementation.sh Bugs

**PR**: https://github.com/movito/adversarial-workflow/pull/48
**Branch**: `feature/ADV-0054-fix-review-script-bugs`
**Commits**: 3

## What Changed

4 bugs fixed in the adversarial review pipeline, discovered during real downstream usage (RMM-0001):

1. **mkdir crash** (Bug 1): Added `mkdir -p` for artifacts/log dirs before first file write
2. **Wrong diff** (Bug 2): Replaced bare `git diff` with `git diff <default-branch>...HEAD` + staged/unstaged capture
3. **Broken CLI** (Bug 3): Added required `task_file` argument to `adversarial review` subparser
4. **Bad command ref** (Bug 4): Updated `/check-spec` to use `adversarial evaluate --evaluator spec-compliance`

## Files Modified

| File | Changes |
|------|---------|
| `adversarial_workflow/cli.py` | `review()` signature, branch-aware pre-check, required arg, 3 usage examples |
| `adversarial_workflow/templates/review_implementation.sh.template` | mkdir, DEFAULT_BRANCH detection, staged/unstaged capture |
| `.adversarial/scripts/review_implementation.sh` | Same as template (kept in sync) |
| `.claude/commands/check-spec.md` | Fixed command reference |

## Bot Review Summary

- **8 threads** across 3 rounds (BugBot + CodeRabbit)
- **7 fixed**, **1 resolved without fixing** (LINES_CHANGED cosmetic display)
- Key bot-driven improvements: branch-aware CLI pre-check, staged change capture, DEFAULT_BRANCH fallback fix, required task_file

## Spec Deviation (Intentional)

`task_file` made **required** instead of spec's `nargs="?"` (optional). Reason: the underlying script exits with error when no argument is provided, so making it optional in the CLI creates a guaranteed failure path. CodeRabbit flagged this as Major; we agreed and fixed it.

## Review Focus Areas

1. **Shell logic**: DEFAULT_BRANCH detection fallback chain (`--short` + `${VAR:-main}`)
2. **CLI pre-check**: Now checks branch diff + staged + unstaged (all must be clean to abort)
3. **Staged/unstaged capture**: Appended to artifacts with section headers

## Evaluator Verdict

**MOSTLY_COMPLIANT** — All bugs fixed. Two noted gaps: intentional `task_file` deviation (explained above) and no new unit tests for bash script fixes (not feasible without mocking git/filesystem).

## How to Review

```bash
git checkout feature/ADV-0054-fix-review-script-bugs
pytest tests/ -v                    # 493 pass
adversarial review --help           # Shows required task_file
```
