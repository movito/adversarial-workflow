# ADV-0065 Review Starter

**PR**: #60
**Branch**: `feature/ADV-0065-replace-aider-with-litellm`
**Task**: Replace Aider subprocess transport with direct LiteLLM library calls

## What Changed

### Core Transport Rewrite (`runner.py`)
- `subprocess.run(["aider", ...])` → `litellm.completion(model=..., messages=[...], timeout=...)`
- Removed: `shutil.which("aider")` check, `_run_builtin_evaluator()`, `_execute_script()`, `_print_aider_help()`, `_print_platform_error()`, `import platform/shutil/subprocess/tempfile`
- Added: `import litellm`, LiteLLM exception handling (RateLimitError, AuthenticationError, Timeout)
- `_run_custom_evaluator()` gains `resolved_api_key_env` param for better auth error messages
- All evaluators (built-in + custom) now flow through the same code path

### Built-in Prompts (`builtins.py`)
- 3 prompt constants inlined from shell scripts: `_PLAN_EVALUATION_PROMPT`, `_CODE_REVIEW_PROMPT`, `_PROOFREAD_PROMPT`
- Shell scripts kept on disk for CLI backward compatibility (they have pre-processing logic beyond just LLM calls)
- Fixed `REJECT` → `REJECTED` to match `_REJECT_VERDICTS` set

### Dependencies (`pyproject.toml`)
- `aider-chat>=0.86.0` → `litellm>=1.40.0`
- Added Python 3.13 classifier (motivation: aider-chat pinned to <3.13)
- Keywords updated

### Tests
- `test_evaluator_runner.py`: All mocks migrated from subprocess to litellm
- `test_litellm_transport.py`: New file, 13 dedicated transport tests

## Review Focus Areas

1. **Auth error fallback chain** (runner.py:178) — `resolved_api_key_env or config.api_key_env or "API key"`
2. **Prompt fidelity** — compare `builtins.py` prompts with original shell scripts if concerned
3. **Python 3.13 classifier** — CI matrix only covers 3.10-3.12; reviewer decides if classifier is premature

## Bot Review Summary

- **14 threads** total (cursor[bot] + CodeRabbit), **all resolved**
- 4 commits: e29ff04 (impl), ead35a5 (cursor fixes), 1cfeca9 (CodeRabbit fixes), 52a6067 (ruff format)
- CI: GREEN on all Python versions

## Evaluator Review

- **code-reviewer-fast** returned FAIL — all 5 findings triaged as false positive or out-of-scope
- See `.agent-context/reviews/ADV-0065-evaluator-review.md` for full triage
