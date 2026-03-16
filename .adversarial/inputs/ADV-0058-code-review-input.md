# Code Review Input: ADV-0058 — Fix ci-check.sh / GitHub Actions Parity

**PR**: https://github.com/movito/adversarial-workflow/pull/50
**Branch**: `feature/ADV-0058-fix-ci-check-parity`
**Commits**: 3

## What Changed

ci-check.sh claimed to "mirror GitHub Actions" but disagreed on coverage thresholds,
lint scope, and produced false failures every run. Flagged in 4 of 6 retros. Also fixes
a permission gap that blocked agents from using `SKIP_TESTS=1 git commit`.

### `scripts/core/ci-check.sh`
- Removed `--cov-fail-under=80` (GitHub Actions doesn't enforce it; Codecov gates coverage)
- Changed pattern lint scope from `scripts/ tests/` to `adversarial_workflow/` (matches pre-commit)
- Fixed unquoted `$PY_FILES` with `find -print0 | xargs -0`
- Made pattern lint advisory (non-blocking) — 34 pre-existing DK002 violations tracked in ADV-0061
- Added directory existence guard for `adversarial_workflow/`
- Updated header comment to accurately describe checks

### `.claude/settings.json`
- Added `Bash(SKIP_TESTS=1 git *)` to allow list (scoped to git only per BugBot review)

### `delegation/tasks/1-backlog/ADV-0061-fix-dk002-adversarial-workflow.md` (new)
- Backlog task to fix 34 DK002 violations and promote pattern lint back to blocking

## Key Design Decision

Pattern lint is **advisory** (warn, not fail) because:
1. GitHub Actions doesn't run pattern lint at all
2. Pre-commit gates it for staged files
3. 34 pre-existing violations would cause false failures
4. ADV-0061 tracks the cleanup; once done, lint becomes blocking again

## Bot Review Summary

- **Round 1**: 3 threads (1 High, 1 Low, 1 Trivial) — all fixed and resolved
- **Round 2**: No new threads
- **CodeRabbit**: APPROVED
- **BugBot**: No remaining findings

## Diff

```diff
diff --git a/.claude/settings.json b/.claude/settings.json
index 6e6f263..d5e9381 100644
--- a/.claude/settings.json
+++ b/.claude/settings.json
@@ -8,6 +8,7 @@
       "Bash(python* scripts/*.py*)",
       "Bash(adversarial *)",
       "Bash(ruff *)",
+      "Bash(SKIP_TESTS=1 git *)",
       "Bash(pre-commit *)",
       "Read",
       "Write",
diff --git a/scripts/core/ci-check.sh b/scripts/core/ci-check.sh
index 80119b0..7b65f5f 100755
--- a/scripts/core/ci-check.sh
+++ b/scripts/core/ci-check.sh
@@ -4,11 +4,11 @@
 #
 # Usage: ./scripts/core/ci-check.sh
 #
-# This script runs the SAME checks as GitHub Actions:
+# This script runs a subset of GitHub Actions checks locally:
 #   1. Ruff format check
 #   2. Ruff lint check
-#   3. Pattern lint (project-specific DK rules)
-#   4. Full test suite with coverage (80% threshold)
+#   3. Pattern lint (DK rules, scoped to adversarial_workflow/ — advisory only)
+#   4. Full test suite with coverage report (no threshold — Codecov gates coverage)
 #
 # Run this before every push to prevent CI failures.

@@ -66,21 +66,21 @@ fi
 echo

 # 3. Pattern lint (project-specific DK rules)
+# NOTE: Advisory only — pre-commit gates this for changed files;
+#       GitHub Actions does not run pattern lint. Violations are
+#       reported but do not block the build.
 echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
 echo "3/4 Running pattern lint (DK rules)..."
 echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
-PY_FILES=$(find scripts/ tests/ -name '*.py' 2>/dev/null)
-if [ -n "$PY_FILES" ]; then
+if [ ! -d "adversarial_workflow/" ]; then
+    echo "WARNING: adversarial_workflow/ directory not found — skipping pattern lint"
+else
     SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
-    if python3 "$SCRIPT_DIR/pattern_lint.py" $PY_FILES 2>&1; then
+    if find adversarial_workflow/ -name '*.py' -print0 2>/dev/null | xargs -0 python3 "$SCRIPT_DIR/pattern_lint.py" 2>&1; then
         echo "OK: Pattern lint: No DK violations"
     else
-        echo "FAIL: Pattern lint: DK violations found"
-        echo "   Fix violations or add # noqa: DKxxx to suppress"
-        FAILED=1
+        echo "WARN: Pattern lint: DK violations found (advisory — pre-commit gates new code)"
     fi
-else
-    echo "WARNING: No Python files found in scripts/ or tests/"
 fi
 echo

@@ -88,10 +88,10 @@ echo
 echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
 echo "4/4 Running full test suite with coverage..."
 echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
-if pytest tests/ -v --cov=adversarial_workflow --cov-report=term-missing --cov-fail-under=80; then
-    echo "OK: Tests: All tests pass with coverage >=80%"
+if pytest tests/ -v --cov=adversarial_workflow --cov-report=term-missing; then
+    echo "OK: Tests: All tests pass"
 else
-    echo "FAIL: Tests: Test failures or coverage below 80%"
+    echo "FAIL: Tests: Test failures detected"
     FAILED=1
 fi
 echo
```
