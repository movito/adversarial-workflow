#!/bin/bash
# Local CI check - mirrors GitHub Actions test.yml
# Run this BEFORE pushing to catch issues early
#
# Usage: ./scripts/core/ci-check.sh
#
# This script runs the SAME checks as GitHub Actions:
#   1. Ruff format check
#   2. Ruff lint check
#   3. Pattern lint (project-specific DK rules)
#   4. Full test suite with coverage (80% threshold)
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
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3/4 Running pattern lint (DK rules)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PY_FILES=$(find scripts/ tests/ -name '*.py' 2>/dev/null)
if [ -n "$PY_FILES" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    if python3 "$SCRIPT_DIR/pattern_lint.py" $PY_FILES 2>&1; then
        echo "OK: Pattern lint: No DK violations"
    else
        echo "FAIL: Pattern lint: DK violations found"
        echo "   Fix violations or add # noqa: DKxxx to suppress"
        FAILED=1
    fi
else
    echo "WARNING: No Python files found in scripts/ or tests/"
fi
echo

# 4. Full test suite with coverage
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4/4 Running full test suite with coverage..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if pytest tests/ -v --cov=adversarial_workflow --cov-report=term-missing --cov-fail-under=80; then
    echo "OK: Tests: All tests pass with coverage >=80%"
else
    echo "FAIL: Tests: Test failures or coverage below 80%"
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
