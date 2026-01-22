# ADV-0017 Review Starter for Code-Reviewer

## PR Information
- **PR**: https://github.com/movito/adversarial-workflow/pull/9
- **Branch**: `feature/adv-0017-generic-evaluator-runner`
- **Task**: ADV-0017 - Generic Evaluator Runner
- **Target Version**: v0.6.0

## Summary

This PR implements a generic `run_evaluator()` function that works with any `EvaluatorConfig`. It creates the foundation for the plugin architecture by:

1. Extracting shared utilities into `utils/` module
2. Creating a unified runner for built-in and custom evaluators
3. Defining `BUILTIN_EVALUATORS` for evaluate, proofread, review
4. Adding `get_all_evaluators()` to combine built-in and local evaluators

## Files to Review

### New Files (Core Implementation)
| File | Lines | Purpose |
|------|-------|---------|
| `adversarial_workflow/utils/colors.py` | 8 | Terminal color constants |
| `adversarial_workflow/utils/config.py` | 43 | Configuration loading with YAML + env overrides |
| `adversarial_workflow/utils/validation.py` | 75 | Evaluation output validation, verdict extraction |
| `adversarial_workflow/evaluators/builtins.py` | 36 | BUILTIN_EVALUATORS dict |
| `adversarial_workflow/evaluators/runner.py` | 240 | Generic run_evaluator() function |

### Modified Files
| File | Purpose |
|------|---------|
| `adversarial_workflow/utils/__init__.py` | Export new utilities |
| `adversarial_workflow/evaluators/__init__.py` | Export runner, builtins, get_all_evaluators() |

### Test Files
| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_evaluator_runner.py` | 17 | Runner errors, verdicts, builtins, get_all_evaluators |
| `tests/test_utils_validation.py` | 8 | Validation function, verdict extraction |

## Review Checklist

### Architecture & Design
- [ ] Does `run_evaluator()` properly handle both built-in and custom evaluators?
- [ ] Is the separation between `utils/` and `evaluators/` appropriate?
- [ ] Does `get_all_evaluators()` correctly merge built-in and local evaluators?

### Error Handling
- [ ] File not found → returns 1 with clear message
- [ ] Not initialized → checks config file existence before loading
- [ ] Missing API key → helpful error with env var name
- [ ] Aider not found → installation guidance
- [ ] Rate limit → suggestions for resolution
- [ ] Timeout → configurable, default 180s

### Security Considerations
- [ ] Subprocess calls use list arguments (no shell=True)
- [ ] User-supplied `file_path` is validated for existence
- [ ] Note: Bandit S603 warning exists but mitigated by shell=False

### Code Quality
- [ ] Modern typing used (dict, tuple, str | None)
- [ ] `__all__` exports are alphabetically sorted
- [ ] Docstrings present and accurate
- [ ] No unused variables (fixed in review feedback commit)

### Test Coverage
- [ ] Error paths tested (file not found, no API key, no aider, not initialized)
- [ ] Verdict reporting tested (APPROVED, NEEDS_REVISION, REJECTED, None)
- [ ] Built-in evaluators verified
- [ ] Local override behavior tested
- [ ] Case-insensitive verdict extraction tested

## Key Implementation Details

### run_evaluator() Flow
```
1. Validate file exists
2. Check project initialized (.adversarial/config.yml exists)
3. Check aider available
4. Check API key set
5. Pre-flight file size check (warn >500 lines, confirm >700 lines)
6. Route to built-in (shell script) or custom (direct aider) execution
7. Validate output and extract verdict
8. Report result with colored output
```

### Built-in vs Custom Evaluators
- **Built-in** (`source="builtin"`): Execute existing shell scripts in `.adversarial/scripts/`
- **Custom** (`source="local"`): Invoke aider directly with prompt from YAML config

### Verdict Extraction
Supports patterns:
- `Verdict: APPROVED`
- `**Verdict**: APPROVED`
- `APPROVED` (on its own line)

Case-insensitive matching, returns uppercase.

## Bot Feedback (Already Addressed)

The following issues from BugBot and CodeRabbit have been fixed in commit `c1c5668`:

1. ✅ Dead code: init check now uses explicit file existence check
2. ✅ Case-sensitive markers: now uses lowercase comparison
3. ✅ YAML type validation: added isinstance check
4. ✅ Timezone-aware timestamps: using UTC
5. ✅ Modern typing: Dict→dict, Tuple→tuple
6. ✅ Sorted __all__
7. ✅ Fixed unused variables in tests

## Dependencies

- **ADV-0015** (EvaluatorConfig) - merged ✅
- **ADV-0016** (discovery) - merged ✅

## Next Steps (After Merge)

ADV-0018 will simplify `cli.py` by replacing ~200 lines in `evaluate()` and `proofread()` with calls to `run_evaluator()`.

## Test Command

```bash
source .venv/bin/activate
pytest tests/test_evaluator_runner.py tests/test_utils_validation.py -v
```

All 137 project tests pass.
