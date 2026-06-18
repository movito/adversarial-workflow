# Code Review: ADV-0049 — DK003 Chained-In Bugfix + Pattern Lint Tests

## Task Summary

ADV-0049 is an upstream sync task that:
1. Fixes a bug in `check_dk003()` where chained `in` comparisons (`a in b in c`) incorrectly reused `node.left` for all comparisons instead of tracking the evolving left operand
2. Adds 44 tests for the pattern_lint module (DK001-DK004 rules) — previously untested

The fix introduces a `current_left` variable that advances through each comparator in the chain, ensuring `a in b in c` correctly checks `(a in b)` and `(b in c)` rather than `(a in b)` and `(a in c)`.

## Key Files Changed

- `scripts/core/pattern_lint.py` — Bugfix: track `current_left` through DK003 comparison loop
- `tests/test_pattern_lint.py` — New: 44 tests covering all 4 lint rules + integration tests

## Diff

```diff
diff --git a/scripts/core/pattern_lint.py b/scripts/core/pattern_lint.py
index 48aa80c..9ea571e 100644
--- a/scripts/core/pattern_lint.py
+++ b/scripts/core/pattern_lint.py
@@ -218,29 +218,35 @@ def check_dk003(tree: ast.AST, source_lines: list[str], path: str) -> list[Viola
         if not isinstance(node, ast.Compare):
             continue

+        current_left = node.left
         for op, comparator in zip(node.ops, node.comparators, strict=False):
             if not isinstance(op, ast.In):
+                current_left = comparator
                 continue

             # Skip collection literals — set, list, tuple, dict on the right
             if isinstance(comparator, (ast.Set, ast.List, ast.Tuple, ast.Dict)):
+                current_left = comparator
                 continue
             # Skip set/frozenset/list/dict/tuple constructor calls
             if isinstance(comparator, ast.Call):
                 func_name = _extract_name(comparator.func)
                 if func_name in {"set", "frozenset", "list", "dict", "tuple"}:
+                    current_left = comparator
                     continue

-            left = node.left
+            left = current_left
             left_name = _extract_name(left)
             right_name = _extract_name(comparator)

             if not left_name or not right_name:
+                current_left = comparator
                 continue

             # Skip if right side looks like a collection variable
             right_lower = right_name.lower().split(".")[-1]  # last segment
             if any(right_lower.endswith(s) for s in collection_suffixes):
+                current_left = comparator
                 continue

             # Both sides must look like identifier variables
@@ -248,12 +254,14 @@ def check_dk003(tree: ast.AST, source_lines: list[str], path: str) -> list[Viola
             right_is_id = any(hint in right_name.lower() for hint in identifier_hints)

             if not (left_is_id and right_is_id):
+                current_left = comparator
                 continue

             line = source_lines[node.lineno - 1] if node.lineno <= len(source_lines) else ""

             # Suppressed by '# substring:' comment
             if "# substring:" in line or "# noqa: DK003" in line:
+                current_left = comparator
                 continue

             violations.append(
@@ -269,6 +277,8 @@ def check_dk003(tree: ast.AST, source_lines: list[str], path: str) -> list[Viola
                 )
             )

+            current_left = comparator
+
     return violations
```

```diff
diff --git a/tests/test_pattern_lint.py b/tests/test_pattern_lint.py
new file mode 100644
index 0000000..d3fa8c7
--- /dev/null
+++ b/tests/test_pattern_lint.py
@@ -0,0 +1,383 @@
+"""Tests for scripts/pattern_lint.py — project-specific lint rules."""
+# 44 tests across 5 test classes:
+# - TestDK001 (7 tests): str.replace for extension removal
+# - TestDK002 (12 tests): missing encoding= in file I/O
+# - TestDK003 (12 tests): 'in' for identifier comparison (incl. chained-in)
+# - TestDK004 (10 tests): bare except Exception with pass/empty body
+# - TestIntegration (2 tests): multi-rule and clean-code scenarios
+# Uses sys.path.insert to import from scripts/core/ (not a Python package)
```

## Review Focus Areas

1. **Bugfix correctness**: Does `current_left` advance correctly at every exit point in the loop?
2. **Test coverage**: Are chained-in edge cases adequately tested?
3. **Import approach**: `sys.path.insert` for scripts/core/ — acceptable for non-package code?
4. **No regressions**: All 44 tests pass, existing tests unaffected
