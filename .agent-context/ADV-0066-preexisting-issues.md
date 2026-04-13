# ADV-0066: Pre-Existing Issues Found During Implementation

These issues were identified during ADV-0066 (aider remnant removal) but are
pre-existing — not introduced by this PR. They should be turned into a separate
task for future cleanup.

## 1. Dead verdict handling in cli.evaluate()

**Location**: `adversarial_workflow/cli.py:1774-1800`

`run_evaluator()` already extracts verdicts and returns exit codes (0 for
APPROVED, 1 for NEEDS_REVISION/REJECTED). When it returns 0, `cli.evaluate()`
proceeds to extract the verdict *again* from the log file via
`validate_evaluation_output()`. The NEEDS_REVISION and REJECTED branches in
`cli.evaluate()` are effectively dead code — if `run_evaluator` returned 0, the
verdict was already APPROVED (or unknown).

**Recommendation**: Remove the redundant verdict extraction in `cli.evaluate()`
and `cli.review()`, or simplify to only handle the APPROVED case after
`run_evaluator` returns 0.

## 2. Empty test_command edge case in validate()

**Location**: `adversarial_workflow/cli.py:1895-1897`

If `test_command` is an empty string, `shlex.split("")` returns `[]`, which
causes `subprocess.run([])` to raise `ValueError`. The Click CLI layer
validates the argument before it reaches `validate()`, so this is unlikely in
practice. However, for robustness, an explicit guard would be better.

**Recommendation**: Add `if not test_command or not test_command.strip():` guard
before `shlex.split()`.

## 3. Evaluator output_suffix could be empty string

**Location**: `adversarial_workflow/cli.py:1738`

The fallback `builtin_config.output_suffix or "EVALUATE"` correctly handles
`None` but an empty string `""` would bypass the fallback and match all `.md`
files. All current builtins have non-empty suffixes, so this is theoretical.

**Recommendation**: No action needed unless custom evaluators with empty
suffixes become possible.

## 4. cli.evaluate() duplicate verdict extraction (design smell)

Both `run_evaluator()` and `cli.evaluate()` independently extract and act on
verdicts. This violates single-responsibility. The CLI layer should either
trust `run_evaluator`'s exit code entirely, or `run_evaluator` should return
the verdict as data rather than encoding it in the exit code.

**Recommendation**: Refactor as part of a broader evaluator API cleanup.

---

**Created**: 2026-04-13 during ADV-0066
**Source**: CodeRabbit review threads + code-reviewer-fast evaluator findings
