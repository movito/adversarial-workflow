# code-reviewer-fast

Fast adversarial correctness check using Gemini Flash.

## Overview

This is the fast variant of [code-reviewer](../../openai/code-reviewer/). Same adversarial
mindset (find bugs, not verify acceptance criteria), but with a condensed protocol optimized
for speed and cost.

Use this for small changes, iteration cycles, or as a pre-push sanity check. Use the full
`code-reviewer` for substantial PRs with new logic.

## Use Cases

- **Quick edge case scan** for changes under 50 lines
- **Iteration cycles** — re-run after fixing evaluator findings
- **Pre-push check** — catch obvious boundary issues before bots see the code
- **Cost-sensitive reviews** — ~100x cheaper than the o1 variant

## When to Use

| Scenario | Use code-reviewer-fast? |
|----------|------------------------|
| Small feature PR (<50 lines) | ✅ Yes |
| Re-checking after fixes | ✅ Yes |
| Pre-push sanity check | ✅ Yes |
| Large feature PR (>100 lines) | ❌ Use code-reviewer |
| Security-critical code | ❌ No (use o1-code-review) |

## Model

- **Model**: `gemini/gemini-2.5-flash`
- **Provider**: Google
- **Category**: code-review
- **Timeout**: 180s

## Cost Estimate

~$0.003–0.01 per review. Extremely cost-effective for iteration.

## Example Usage

```bash
# Quick check on a small change
adversarial code-reviewer-fast .adversarial/inputs/TASK-001-code-review-input.md

# Read findings
cat .adversarial/logs/TASK-001-code-review-input--code-reviewer-fast.md
```

## Output

The evaluator produces:

1. **Findings** — categorized as CORRECTNESS, ROBUSTNESS, or TESTING
2. **Test Gap Summary** — table of edge cases and coverage status
3. **Verdict**: PASS, CONCERNS, or FAIL

## See Also

- [code-reviewer](../../openai/code-reviewer/) — Full adversarial review using o1
- [gemini-code](../gemini-code/) — Security-focused code review
- [gpt4o-code](../../openai/gpt4o-code/) — Fast general code review
