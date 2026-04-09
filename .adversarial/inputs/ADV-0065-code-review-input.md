# Code Review Input: ADV-0065 Replace Aider Transport with LiteLLM

## Task Summary

Replace the Aider subprocess transport layer with direct LiteLLM library calls in the evaluator runner. All evaluators (built-in and custom) now use `litellm.completion()` instead of `subprocess.run(["aider", ...])`. Built-in evaluator prompts are migrated from shell scripts to inline Python constants.

## Requirements Checklist

1. Replace `subprocess.run(["aider", ...])` with `litellm.completion()` - DONE
2. Migrate 3 built-in evaluator shell scripts to inline prompts - DONE
3. Swap `aider-chat` dependency for `litellm>=1.40.0` - DONE
4. Maintain identical prompt construction - DONE
5. Preserve verdict parsing via `validate_evaluation_output()` - DONE
6. Handle API errors via LiteLLM exceptions - DONE
7. Remove `_print_aider_help()` and `shutil.which("aider")` check - DONE
8. Add Python 3.13 classifier - DONE

## Changed Files

### Source Code

- `adversarial_workflow/evaluators/runner.py` — Core transport rewrite
  - Removed: `subprocess.run`, `shutil.which`, `tempfile`, `_run_builtin_evaluator()`, `_execute_script()`, `_print_aider_help()`, `_print_platform_error()`
  - Added: `litellm.completion()` call with proper exception handling
  - `_run_custom_evaluator()` now accepts `resolved_api_key_env` parameter for error messages
  - Auth error uses fallback chain: `resolved_api_key_env or config.api_key_env or "API key"`

- `adversarial_workflow/evaluators/builtins.py` — Inline prompts
  - Added 3 prompt constants: `_PLAN_EVALUATION_PROMPT`, `_CODE_REVIEW_PROMPT`, `_PROOFREAD_PROMPT`
  - Prompts extracted from shell scripts (`evaluate_plan.sh`, `review_implementation.sh`, `validate_tests.sh`)
  - Verdict tokens aligned with `_REJECT_VERDICTS` set (REJECTED not REJECT)

- `pyproject.toml` — Dependency and metadata
  - `aider-chat>=0.86.0` replaced with `litellm>=1.40.0`
  - Added Python 3.13 classifier
  - Updated keywords

### Test Code

- `tests/test_evaluator_runner.py` — Migrated all mocks from subprocess to litellm
- `tests/test_litellm_transport.py` — New dedicated transport tests (13 tests)

## Diff

```diff
"""See PR #60 for full diff — 6 files, +1149/-514 lines"""
```

## Areas of Concern

1. Shell scripts kept on disk for CLI backward compatibility but no longer called by Python
2. Python 3.13 classifier added but CI matrix only covers 3.10-3.12
3. Built-in evaluator prompts are long inline strings (could be external files)
