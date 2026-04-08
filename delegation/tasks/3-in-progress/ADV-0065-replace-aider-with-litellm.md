# ADV-0065: Replace Aider Transport Layer with LiteLLM

**Status**: In Progress
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 4-6 hours
**Created**: 2026-04-08
**GitHub Issue**: #59

## Related Tasks

**Depends On**: None
**Blocks**: None (but unblocks Python 3.13+ support)

## Overview

Replace the Aider subprocess transport layer with direct LiteLLM library calls. The `adversarial` CLI currently shells out to Aider as its LLM pipe, but only uses it as a dumb message-in/text-out transport — explicitly disabling all Aider features (`--no-git`, `--no-auto-commits`, `--no-browser`, `--no-detect-urls`). This creates unnecessary dependency weight (~50+ transitive packages), pins Python to <3.13, and adds a fragile subprocess chain.

LiteLLM is the natural replacement because the codebase already uses LiteLLM-style model strings (`gemini/gemini-2.5-pro`, `anthropic/claude-sonnet-4-5`, `mistral/mistral-large-latest`) and the `ModelResolver` already produces them. This is cutting out a middleman.

**Context**: The evaluator YAML files, `ModelResolver`, and `API_KEY_MAP` are already transport-agnostic. The change is isolated to `runner.py` (custom evaluators), `builtins.py` + shell scripts (built-in evaluators), and `pyproject.toml` (dependency swap).

## Requirements

### Functional Requirements
1. Replace `subprocess.run(["aider", ...])` in `_run_custom_evaluator()` with `litellm.completion()` call
2. Migrate or remove the 3 built-in evaluator shell scripts (`evaluate_plan.sh`, `review_implementation.sh`, `validate_tests.sh`) — convert to custom evaluator YAML format using `litellm.completion()`
3. Remove `aider-chat` dependency from `pyproject.toml`, add `litellm>=1.40.0`
4. Maintain identical prompt construction (system prompt + document content appended)
5. Preserve all verdict parsing via `validate_evaluation_output()` — output format must remain markdown with verdict patterns
6. Handle API errors (rate limits, auth failures, timeouts) via LiteLLM exceptions instead of stdout parsing
7. Remove `_print_aider_help()` and the `shutil.which("aider")` check
8. Update Python version classifier to include 3.13 (`requires-python = ">=3.10"` stays, add `3.13` classifier)

### Non-Functional Requirements
- [ ] Performance: LLM call latency should be comparable (no added overhead)
- [ ] Reliability: Proper Python exception handling replaces fragile stdout parsing
- [ ] Maintainability: Fewer lines of code, no subprocess/tempfile complexity

## TDD Workflow (Mandatory)

**Test-Driven Development Approach**:

1. **Red**: Write failing tests for LiteLLM-based evaluator execution
2. **Green**: Implement `litellm.completion()` calls
3. **Refactor**: Clean up removed Aider artifacts
4. **Commit**: Pre-commit hook runs tests automatically

### Test Requirements
- [ ] Unit tests for LiteLLM completion call (mock `litellm.completion`)
- [ ] Error handling: rate limit exception → proper error message
- [ ] Error handling: auth failure → proper error message
- [ ] Error handling: timeout → proper error message
- [ ] Output writing: response content written to log file with header
- [ ] Verdict parsing: unchanged behavior (existing tests should pass)
- [ ] Built-in evaluator migration tests (if converted to YAML)
- [ ] Coverage: 80%+ for modified code

**Test files to modify/create**:
- `tests/test_evaluator_runner.py` — Update mocks from `subprocess.run` to `litellm.completion`
- `tests/test_litellm_transport.py` — New: focused transport layer tests

## Implementation Plan

### Files to Modify

1. `adversarial_workflow/evaluators/runner.py` — Core change
   - Function: `_run_custom_evaluator()` — Replace subprocess with `litellm.completion()`
   - Function: `run_evaluator()` — Remove `shutil.which("aider")` check
   - Remove: `_print_aider_help()` function
   - Update: error handling from stdout parsing to exception catching
   - Remove: `import shutil, subprocess, tempfile` (subprocess/tempfile no longer needed for custom evaluators)

2. `adversarial_workflow/evaluators/builtins.py` — Migrate built-in evaluators
   - Convert 3 built-in evaluators from shell-script backed to inline prompts
   - Extract prompts from shell scripts into the `EvaluatorConfig` objects
   - Change `source="builtin"` to `source="local"` (or keep as a category marker)

3. `adversarial_workflow/evaluators/runner.py` — Remove `_run_builtin_evaluator()` and `_execute_script()`
   - After migration, built-ins use the same `_run_custom_evaluator()` path

4. `pyproject.toml` — Dependency and metadata changes
   - Remove: `"aider-chat>=0.86.0"`
   - Add: `"litellm>=1.40.0"`
   - Update: `keywords` — remove `"aider"`, add `"litellm"`
   - Add: `"Programming Language :: Python :: 3.13"` classifier

5. `tests/test_evaluator_runner.py` — Update test mocks

### Files to Remove

1. `.adversarial/scripts/evaluate_plan.sh` — Migrated to inline prompt
2. `.adversarial/scripts/review_implementation.sh` — Migrated to inline prompt
3. `.adversarial/scripts/validate_tests.sh` — Migrated to inline prompt

### Approach

**Step 1: Write Transport Layer Tests (Red Phase)**

Write tests that mock `litellm.completion()` and verify:
- Correct model string passed through
- Prompt constructed correctly (system message + user message with document)
- Response content extracted from `choices[0].message.content`
- Rate limit exception caught and reported
- Timeout exception caught and reported
- Auth error caught and reported

**TDD cycle**:
1. Write tests in `tests/test_litellm_transport.py`
2. Run tests (should fail): `pytest tests/test_litellm_transport.py -v`
3. Implement: Replace `_run_custom_evaluator()` internals
4. Run tests (should pass): `pytest tests/test_litellm_transport.py -v`

**Step 2: Replace Aider with LiteLLM in `_run_custom_evaluator()`**

The core transformation:

```python
# BEFORE (subprocess to aider)
cmd = ["aider", "--no-browser", "--model", resolved_model, ...]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
output = result.stdout

# AFTER (direct litellm call)
import litellm
response = litellm.completion(
    model=resolved_model,
    messages=[
        {"role": "user", "content": full_prompt}
    ],
    timeout=timeout,
)
output = response.choices[0].message.content
```

Error handling transformation:
```python
# BEFORE (string matching on stdout)
if "RateLimitError" in output:
    _print_rate_limit_error(file_path)

# AFTER (proper exception handling)
except litellm.RateLimitError:
    _print_rate_limit_error(file_path)
except litellm.AuthenticationError:
    print(f"{RED}Error: Invalid API key for {resolved_api_key_env}{RESET}")
except litellm.Timeout:
    _print_timeout_error(timeout)
```

**Step 3: Migrate Built-in Evaluators**

Extract prompts from the 3 shell scripts and inline them into `builtins.py`. This eliminates the `_run_builtin_evaluator()` / `_execute_script()` code path entirely — all evaluators (built-in and custom) use the same LiteLLM transport.

**Step 4: Clean Up**

- Remove shell scripts from `.adversarial/scripts/`
- Remove `shutil.which("aider")` check and `_print_aider_help()`
- Remove `_run_builtin_evaluator()` and `_execute_script()` functions
- Update `pyproject.toml` dependencies
- Run full test suite

**Step 5: Version Bump**

This is a breaking change (removes Aider dependency). Options:
- **v1.0.0** — Signals maturity + breaking change (recommended)
- **v0.10.0** — Minor bump with breaking note

Decision deferred to human review.

## Acceptance Criteria

### Must Have
- [ ] `litellm.completion()` replaces all Aider subprocess calls
- [ ] All existing evaluator YAML files work without changes
- [ ] Model string format unchanged (LiteLLM-native already)
- [ ] API key resolution unchanged (`API_KEY_MAP` + `api_key_env`)
- [ ] Verdict parsing unchanged (`validate_evaluation_output()`)
- [ ] Rate limit, timeout, auth errors properly caught and reported
- [ ] `aider-chat` removed from dependencies
- [ ] `litellm` added to dependencies
- [ ] All tests passing
- [ ] Coverage targets met (80%+ new code)
- [ ] No regressions in existing tests

### Should Have
- [ ] Built-in evaluators migrated from shell scripts to inline prompts
- [ ] Python 3.13 classifier added
- [ ] Error messages are clear and actionable
- [ ] `adversarial init` no longer creates shell scripts (or creates them as legacy stubs)

### Nice to Have
- [ ] Streaming support (print LLM output as it arrives)
- [ ] Retry with fallback_model on primary model failure

## Success Metrics

### Quantitative
- Test pass rate: 100%
- Dependency count: reduced by ~50 transitive packages
- Lines of code: net reduction of ~100-150 lines
- Python version support: 3.10-3.13+

### Qualitative
- No more "why does this need Aider?" confusion
- Cleaner error handling (exceptions vs stdout parsing)
- Simpler mental model (library call vs subprocess chain)

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Write failing tests (transport + error handling) | 1 hour | [ ] |
| Implement LiteLLM transport in runner.py | 1.5 hours | [ ] |
| Migrate built-in evaluators from shell scripts | 1 hour | [ ] |
| Clean up: remove Aider artifacts, update deps | 0.5 hours | [ ] |
| Full test suite + refactor | 1 hour | [ ] |
| **Total** | **5 hours** | [ ] |

## PR Plan

This is a single-PR task (~300 lines changed, ~200 removed). No splitting needed.

**Single PR**: `feature/ADV-0065-replace-aider-with-litellm`

## References

- **GitHub Issue**: https://github.com/movito/adversarial-workflow/issues/59
- **LiteLLM Docs**: https://docs.litellm.ai/
- **Current transport**: `adversarial_workflow/evaluators/runner.py` lines 117-228
- **Model resolver**: `adversarial_workflow/evaluators/resolver.py`
- **Testing**: `pytest tests/ -v`
- **Coverage**: `pytest tests/ --cov=adversarial_workflow`
- **Pre-commit**: `pre-commit run --all-files`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2026-04-08
