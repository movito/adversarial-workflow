#!/bin/bash
# Local CI check - mirrors GitHub Actions test.yml
# Run this BEFORE pushing to catch issues early
#
# Usage: ./scripts/core/ci-check.sh
#
# This script runs a subset of GitHub Actions checks locally:
#   1. Ruff format check
#   2. Ruff lint check
#   3. Pattern lint (DK rules, scoped to adversarial_workflow/ — advisory only)
#   4. Full test suite with coverage report (no threshold — Codecov gates coverage)
#
# Run this before every push to prevent CI failures.

set -e  # Exit on first error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running local CI checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Track overall status
FAILED=0

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Try to activate local venv
    if [ -f ".venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source .venv/bin/activate
    elif [ -f "venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "WARNING: No virtual environment found. Using system Python."
    fi
fi

echo "Python: $(which python)"
echo

# 1. Ruff format check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1/4 Checking formatting with Ruff..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ruff format --check . 2>/dev/null; then
    echo "OK: Ruff format: All files formatted correctly"
else
    echo "FAIL: Ruff format: Formatting issues found"
    echo "   Run: ruff format . to fix"
    FAILED=1
fi
echo

# 2. Ruff lint check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2/4 Linting with Ruff..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ruff check . 2>/dev/null; then
    echo "OK: Ruff check: No lint errors"
else
    echo "FAIL: Ruff check: Lint errors found"
    echo "   Run: ruff check --fix . to auto-fix"
    FAILED=1
fi
echo

# 3. Pattern lint (project-specific DK rules)
# NOTE: Advisory only — pre-commit gates this for changed files;
#       GitHub Actions does not run pattern lint. Violations are
#       reported but do not block the build.
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3/4 Running pattern lint (DK rules)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -d "adversarial_workflow/" ]; then
    echo "WARNING: adversarial_workflow/ directory not found — skipping pattern lint"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    if find adversarial_workflow/ -name '*.py' -print0 2>/dev/null | xargs -0 python3 "$SCRIPT_DIR/pattern_lint.py" 2>&1; then
        echo "OK: Pattern lint: No DK violations"
    else
        echo "WARN: Pattern lint: DK violations found (advisory — pre-commit gates new code)"
    fi
fi
echo

# 4. Full test suite with coverage
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4/4 Running full test suite with coverage..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pytest tests/ -v --cov=adversarial_workflow --cov-report=term-missing; then
    echo "OK: Tests: All tests pass"
else
    echo "FAIL: Tests: Test failures detected"
    FAILED=1
fi
echo

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
    echo "All CI checks passed!"
    echo "   Safe to push: git push origin $(git branch --show-current)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
else
    echo "CI checks failed!"
    echo "   Fix the issues above before pushing."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi
