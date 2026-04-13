# ADV-0065: Replace Aider Transport Layer with LiteLLM - Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-04-08
**From**: Planner
**To**: feature-developer-v5
**Task**: `delegation/tasks/2-todo/ADV-0065-replace-aider-with-litellm.md`
**Status**: Ready for implementation
**Evaluation**: ✅ APPROVED by arch-review (o1) — no blocking concerns

---

## Task Summary

Replace `subprocess.run(["aider", ...])` calls with `litellm.completion()` calls across the evaluator system. Aider is used as a dumb LLM pipe — all its features are disabled. LiteLLM is the natural replacement since model strings are already LiteLLM-compatible.

## Current Situation

The codebase has ONE function that calls Aider: `_run_custom_evaluator()` in `runner.py` (lines 117-228). It:
1. Writes the prompt to a temp file
2. Invokes `aider --no-browser --model X --no-git --message-file prompt.md --read file.md`
3. Captures stdout as the evaluation output
4. Parses stdout for rate limit errors via string matching

Additionally, 3 built-in evaluators delegate to shell scripts that also invoke Aider.

## Your Mission

### Phase 1: Write Tests (Red)
- Mock `litellm.completion()` in new test file `tests/test_litellm_transport.py`
- Test: correct model string passed, prompt constructed, response extracted
- Test: `litellm.RateLimitError` → proper error message + return 1
- Test: `litellm.AuthenticationError` → proper error message + return 1
- Test: `litellm.Timeout` → proper error message + return 1
- Test: output written to log file with header

### Phase 2: Implement (Green)
- Replace Aider subprocess in `_run_custom_evaluator()` with `litellm.completion()`
- Remove `shutil.which("aider")` check and `_print_aider_help()`
- Replace stdout string matching with proper exception handling
- Remove tempfile usage (no longer need to write prompt to disk)

### Phase 3: Migrate Built-ins
- Extract prompts from 3 shell scripts into `builtins.py` inline
- Remove `_run_builtin_evaluator()` and `_execute_script()` — all evaluators use same path
- Delete shell scripts from `.adversarial/scripts/`

### Phase 4: Clean Up
- Update `pyproject.toml`: swap `aider-chat` for `litellm`, update classifiers/keywords
- Update existing tests that mock `subprocess.run`
- Run full test suite

## Acceptance Criteria (Must Have)

- [ ] `litellm.completion()` replaces all Aider subprocess calls
- [ ] All evaluator YAML files work without changes (model strings are already LiteLLM-native)
- [ ] Verdict parsing unchanged (`validate_evaluation_output()` untouched)
- [ ] Rate limit, timeout, auth errors properly caught via LiteLLM exceptions
- [ ] `aider-chat` removed from `pyproject.toml` dependencies
- [ ] `litellm` added to `pyproject.toml` dependencies
- [ ] Built-in evaluators migrated from shell scripts to inline prompts
- [ ] All tests passing, 80%+ coverage on modified code
- [ ] No regressions

## Critical Implementation Details

### 1. The Core Transform (runner.py `_run_custom_evaluator`)

```python
# BEFORE (lines 166-188):
cmd = ["aider", "--no-browser", "--model", resolved_model, ...]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
output = result.stdout

# AFTER:
import litellm
response = litellm.completion(
    model=resolved_model,
    messages=[{"role": "user", "content": full_prompt}],
    timeout=timeout,
)
output = response.choices[0].message.content
```

### 2. Error Handling Transform

```python
# BEFORE (stdout string matching):
output = result.stdout + result.stderr
if "RateLimitError" in output or "tokens per min" in output:
    _print_rate_limit_error(file_path)

# AFTER (proper exceptions):
try:
    response = litellm.completion(...)
    output = response.choices[0].message.content
except litellm.RateLimitError:
    _print_rate_limit_error(file_path)
    return 1
except litellm.AuthenticationError:
    print(f"{RED}Error: Invalid API key for {resolved_api_key_env}{RESET}")
    return 1
except litellm.Timeout:
    _print_timeout_error(timeout)
    return 1
```

### 3. Prompt Construction Stays the Same

The `full_prompt` variable (lines 145-153) is already a pure string. It was written to a temp file for Aider's `--message-file` flag. With LiteLLM, pass it directly as message content. No temp file needed.

### 4. API Key Environment Variables

LiteLLM auto-reads API keys from environment variables with these names:
- `OPENAI_API_KEY` — used by gpt-*, o1, o3 models
- `ANTHROPIC_API_KEY` — used by claude-* models
- `GEMINI_API_KEY` — used by gemini/* models (LiteLLM also checks `GOOGLE_API_KEY`)
- `MISTRAL_API_KEY` — used by mistral/* models

The existing `API_KEY_MAP` in `resolver.py` already maps to these exact names. LiteLLM picks them up automatically — the explicit check in `run_evaluator()` (lines 73-78) can stay as a pre-flight validation, or be simplified.

### 5. Built-in Evaluator Shell Scripts

The 3 scripts in `.adversarial/scripts/` contain prompts hardcoded in bash. Extract these prompts and put them in the `BUILTIN_EVALUATORS` dict in `builtins.py`. Then all evaluators flow through `_run_custom_evaluator()`.

### 6. `adversarial init` Creates Shell Scripts

Check `adversarial_workflow/cli.py` for the `init` command — it likely copies these shell scripts. Update `init` to skip script creation (or remove that step entirely).

### 7. Ruff Ignores

`runner.py` has Ruff ignores for `S603` (subprocess calls). After removing subprocess usage, these ignores can be cleaned up in `pyproject.toml`.

## Resources for Implementation

- **Current runner**: `adversarial_workflow/evaluators/runner.py`
- **Config dataclass**: `adversarial_workflow/evaluators/config.py`
- **Model resolver**: `adversarial_workflow/evaluators/resolver.py`
- **Built-in configs**: `adversarial_workflow/evaluators/builtins.py`
- **Validation**: `adversarial_workflow/utils/validation.py`
- **Existing tests**: `tests/test_evaluator_runner.py`
- **Shell scripts**: `.adversarial/scripts/*.sh`
- **LiteLLM docs**: https://docs.litellm.ai/docs/completion/input
- **Evaluator arch-review**: `.adversarial/logs/ADV-0065-replace-aider-with-litellm--arch-review.md`

## Time Estimate

5 hours total:
- Phase 1 (Red — tests): 1 hour
- Phase 2 (Green — LiteLLM transport): 1.5 hours
- Phase 3 (Migrate built-ins): 1 hour
- Phase 4 (Cleanup + full suite): 1.5 hours

## Starting Point

1. `git checkout -b feature/ADV-0065-replace-aider-with-litellm`
2. `./scripts/core/project start ADV-0065`
3. Read `adversarial_workflow/evaluators/runner.py` — focus on `_run_custom_evaluator()`
4. Read `tests/test_evaluator_runner.py` — understand existing mocks
5. Create `tests/test_litellm_transport.py` — write failing tests first

## Evaluation History

- **arch-review (o1)**: APPROVED — "sound, well-scoped architectural shift that reduces complexity"
- Cost: $0.26
- No CRITICAL or HIGH findings
- Advisory: Consider explicit config injection for API keys (not blocking)

## Success Looks Like

```bash
$ adversarial arch-review-fast some-file.md
ARCH-REVIEW-FAST: Evaluating some-file.md
ARCH-REVIEW-FAST: Using model gemini/gemini-2.5-flash
ARCH-REVIEW-FAST: Output written to .adversarial/logs/some-file--arch-review-fast.md
Evaluation APPROVED!

$ pip show adversarial-workflow | grep Requires
Requires: litellm, python-dotenv, pyyaml, aiohttp
# (no aider-chat!)

$ python -c "import sys; print(sys.version)"
3.13.x  # Works!
```

---

**Task File**: `delegation/tasks/2-todo/ADV-0065-replace-aider-with-litellm.md`
**Evaluation Log**: `.adversarial/logs/ADV-0065-replace-aider-with-litellm--arch-review.md`
**Handoff Date**: 2026-04-08
**Coordinator**: Planner
