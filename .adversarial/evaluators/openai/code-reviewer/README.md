# code-reviewer

Adversarial correctness review — finds edge-case bugs that checklist reviews miss.

## Overview

This evaluator uses OpenAI's o1 model with extended reasoning to perform adversarial
correctness analysis. Unlike security-focused reviewers (`o1-code-review`, `gemini-code`),
this evaluator focuses on **logic correctness**: edge cases, boundary conditions, type
assumptions, and test gaps.

It thinks like a fuzzer, not a security auditor. For every function, it asks:
"How could this break?"

## Use Cases

- **Edge case analysis**: Empty inputs, prefix collisions, boundary values, type mismatches
- **Logic error detection**: Mental execution tracing through all code paths
- **Test gap identification**: Cross-referencing edge cases against test coverage
- **Interaction analysis**: Cross-function state sharing, order-of-operations bugs

## When to Use

Use this evaluator **after** automated bot reviews (BugBot, CodeRabbit) and **before**
human review. It complements bots by finding semantic issues that line-level analysis misses.

| Scenario | Use code-reviewer? |
|----------|-------------------|
| Feature PR with new logic | ✅ Yes |
| Bug fix with edge cases | ✅ Yes |
| Refactoring (no new logic) | ❌ Skip |
| Docs-only changes | ❌ Skip |
| Quick style fix | ❌ No (use code-reviewer-fast) |

## Model

- **Model**: `o1`
- **Provider**: OpenAI
- **Category**: code-review
- **Timeout**: 600s (extended for deep reasoning)

## Cost Estimate

~$0.15–0.50 per review depending on code size.

## Example Usage

```bash
# Prepare input with full source files (not diffs)
adversarial code-reviewer .adversarial/inputs/TASK-001-code-review-input.md

# Read findings
cat .adversarial/logs/TASK-001-code-review-input--code-reviewer.md
```

**Important**: Include FULL file content in the input, not diffs or excerpts. The evaluator
needs imports, error-handling context, and module-level state to reason correctly.

## Output

The evaluator produces:

1. **Summary** — what was reviewed, overall assessment
2. **Findings** — categorized as CORRECTNESS, ROBUSTNESS, TESTING, or INTERACTION
3. **Edge Cases Verified Clean** — shows the evaluator's work
4. **Test Gap Summary** — table of all identified edge cases and coverage status
5. **Verdict**: PASS, CONCERNS, or FAIL

## Verdict Meanings

| Verdict | Meaning | Action |
|---------|---------|--------|
| **PASS** | No correctness bugs. Adequate test coverage. | Proceed to human review |
| **CONCERNS** | No confirmed bugs, but untested edge cases. | Address gaps, then proceed |
| **FAIL** | Correctness bugs found. | Fix before merge |

## See Also

- [code-reviewer-fast](../../google/code-reviewer-fast/) — Fast variant using Gemini Flash
- [o1-code-review](../o1-code-review/) — Security-focused code review
- [gemini-code](../../google/gemini-code/) — General security + quality review
