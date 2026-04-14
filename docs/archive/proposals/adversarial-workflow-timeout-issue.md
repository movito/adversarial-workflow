# Feature Request: Configurable Timeout per Evaluator

**Component**: adversarial-workflow
**Priority**: Medium
**Requested by**: gas-taxes project team
**Date**: 2026-01-28

---

## Summary

The current hardcoded 180-second timeout for evaluator execution is too short for large documents with slower models (particularly Mistral Large). We need configurable timeouts per evaluator.

## Current Behavior

adversarial-workflow has an internal 180-second timeout that applies to all evaluator executions. When an evaluation exceeds this limit, the process is killed and returns a timeout error.

**Location** (likely): The timeout is applied somewhere in the evaluation execution path, possibly in the aider integration or the subprocess handling.

## Problem

Different models have vastly different response times:

| Model | Small Doc (~1K) | Medium Doc (~3K) | Large Doc (~6.8K) |
|-------|-----------------|------------------|-------------------|
| GPT-5.2 | ~15s | ~45s | ~90s |
| Mistral Large | 29s | 87s | **>180s (TIMEOUT)** |
| Mistral Small | 7s | 44s | 173s |

Mistral Large produces excellent quality reviews (5/5 on medium docs) but cannot complete large document reviews within the 180-second window.

**Impact**: Users cannot use Mistral Large for documents >5K words, limiting model diversity for critical policy document review.

## Proposed Solution

Add an optional `timeout` field to evaluator YAML configuration:

```yaml
# .adversarial/evaluators/mistral-content.yml
name: mistral-content
description: Content review using Mistral Large
model: mistral/mistral-large-latest
api_key_env: MISTRAL_API_KEY
timeout: 300  # <-- NEW: timeout in seconds (default: 180)
output_suffix: -mistral-content.md

prompt: |
  ...
```

### Behavior

- If `timeout` is not specified, use current default (180s)
- If `timeout` is specified, use that value
- Consider a reasonable maximum (e.g., 600s / 10 minutes) to prevent runaway processes

### Implementation Notes

1. Parse `timeout` field from evaluator YAML (integer, seconds)
2. Pass timeout value to the execution subprocess/aider call
3. Update documentation to describe the new field
4. Consider adding `--timeout` CLI flag as override: `adversarial evaluate --timeout 300 ...`

## Test Case

```bash
# Should complete successfully with 300s timeout
adversarial evaluate --evaluator mistral-content large-doc.md

# Where large-doc.md is ~6K words and mistral-content.yml has timeout: 300
```

## Workaround (Current)

We're using GPT-5.2 for large documents and Mistral Small for small/medium documents. This works but reduces model diversity for adversarial review of critical documents.

## References

- Test results: `gas-taxes/.agent-context/GTX-0002-test-results.md`
- ADR documenting the issue: `gas-taxes/docs/decisions/adr/ADR-003-mistral-evaluator-timeout.md`

---

**Contact**: Fredrik (gas-taxes project lead)
