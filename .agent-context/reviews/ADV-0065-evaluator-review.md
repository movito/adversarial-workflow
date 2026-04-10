# ADV-0065 Evaluator Review

**Task**: ADV-0065 — Replace Aider Transport with LiteLLM
**Evaluator**: code-reviewer-fast (gemini/gemini-2.5-flash)
**Verdict**: FAIL (triaged below — most findings are false positives or out of scope)
**Date**: 2026-04-09

## Triage

### 1. Unhandled LiteLLM Model Configuration Errors — WON'T FIX (out of scope)
The generic `Exception` handler at line 185-186 catches ALL unhandled litellm exceptions
including `ModelNotFoundError` and `BadRequestError`. The error message includes the
exception text which contains the model name. Adding specific handlers for every litellm
exception type would be over-engineering — the generic catch already provides clear output.

### 2. Ambiguous API Key Error Messaging — FALSE POSITIVE
This is already fixed. The `resolved_api_key_env` parameter was added specifically to
address this (commit ead35a5). Tests `test_authentication_error` and
`test_authentication_error_with_model_requirement` verify the correct key name appears
in the error message. The "API key" fallback only triggers if both fields are empty,
which can't happen in practice because `ModelResolver.resolve()` always returns a valid
`api_key_env`.

### 3. Breaking Change for Custom Evaluators — FALSE POSITIVE
Custom evaluators never "relied on aider being in PATH". The old code called
`subprocess.run(["aider", ...])` internally — custom evaluators are YAML configs that
specify a model and prompt, they don't call aider themselves. The `EvaluatorConfig`
contract (model, prompt, output_suffix) is preserved identically.

### 4. Untested Python 3.13 — ACKNOWLEDGED (deferred)
Valid observation but out of scope for this PR. The classifier was added because Python
3.13 compatibility was a motivation for removing aider-chat (which pins to <3.13). CI
matrix expansion is a separate task. Noted as area of concern in PR description.

### 5. Subtle Prompt Regression — LOW RISK (accepted)
Prompts were hand-extracted from shell scripts. The shell scripts used `cat <<'PROMPT'`
heredocs with no variable expansion, so the content is identical. The only change was
fixing `REJECT` → `REJECTED` to match the verdict parser (which was a bug fix, not a
regression). Functional testing would require real LLM calls.

## Action Items

None — all findings are either false positives, already fixed, or acknowledged out-of-scope.

## Bot Review Summary

- **Round 1**: 14 threads (cursor + CodeRabbit)
- **Round 2**: 0 new threads after fixes
- All 14 threads resolved
- CI: GREEN (all Python versions pass)
