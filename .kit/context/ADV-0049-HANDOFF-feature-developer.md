# ADV-0049 Handoff: pattern_lint Chained-In Fix + Tests

## Task

1. Apply the chained-`in` bugfix to `scripts/core/pattern_lint.py`
2. Add test suite `tests/test_pattern_lint.py` from upstream

## Bugfix: DK003 Chained `in` Comparisons

The DK003 check incorrectly handles chained `in` comparisons like `a in b in c`. The loop always reuses `node.left`, causing it to check `(a in b)` and then `(a in c)` instead of `(a in b)` and `(b in c)`.

**Fix**: Track `current_left` through the loop in the `check_dk003` function.

Find the loop in `check_dk003` that iterates over `zip(node.ops, node.comparators, ...)` and change it to track `current_left`:

```python
# Before (buggy):
for op, comparator in zip(node.ops, node.comparators, strict=False):
    if not isinstance(op, ast.In):
        continue
    left = node.left          # <-- always uses node.left (wrong for chained)
    left_name = _extract_name(left)
    ...

# After (fixed):
current_left = node.left
for op, comparator in zip(node.ops, node.comparators, strict=False):
    if not isinstance(op, ast.In):
        current_left = comparator
        continue
    left = current_left       # <-- uses tracked position (correct)
    left_name = _extract_name(left)
    ...
    current_left = comparator
```

**Important**: Maintain Ruff formatting (our version uses single-line ternaries that Ruff prefers). Do NOT reformat the file to match upstream's multi-line style.

## Test File

Copy from: `/Users/broadcaster_three/Github/agentive-starter-kit/tests/test_pattern_lint.py`
Copy to: `tests/test_pattern_lint.py`

**Notes**:
- Copy verbatim — do NOT modify
- The test file uses `sys.path.insert` to import pattern_lint — this is acceptable
- Do NOT copy or overwrite `tests/conftest.py`
- Run `pytest tests/test_pattern_lint.py -v` to verify all tests pass
- Run Ruff on the test file: `ruff check tests/test_pattern_lint.py` and `ruff format tests/test_pattern_lint.py`

## Implementation Steps

```bash
# 1. Create branch
git checkout -b feature/ADV-0049-pattern-lint-fix

# 2. Start task
./scripts/core/project start ADV-0049

# 3. Apply chained-in bugfix to scripts/core/pattern_lint.py
# (see fix details above — edit the check_dk003 function)

# 4. Copy test file
cp /Users/broadcaster_three/Github/agentive-starter-kit/tests/test_pattern_lint.py tests/

# 5. Format with Ruff
ruff format tests/test_pattern_lint.py
ruff check --fix tests/test_pattern_lint.py

# 6. Run tests
pytest tests/test_pattern_lint.py -v

# 7. Run pattern lint on codebase (should still pass)
python3 scripts/core/pattern_lint.py adversarial/ tests/

# 8. Run full CI check
./scripts/core/ci-check.sh

# 9. Commit, push, create PR
```

## PR Details

**Title**: `fix: DK003 chained-in comparison handling + add pattern_lint tests (ADV-0049)`

**Body**: Fixes a bug where chained `in` comparisons (`a in b in c`) were incorrectly evaluated. Adds 31-test suite from upstream. Part of ADV-0039 (upstream sync).
