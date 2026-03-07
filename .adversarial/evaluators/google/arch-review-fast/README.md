# arch-review-fast

Fast architectural review using Gemini 2.5 Flash extended reasoning.

## Overview

A lighter, faster alternative to `arch-review` for quick architectural sanity checks. Uses Gemini 2.5 Flash's extended reasoning to evaluate structural quality: coupling, cohesion, API design, pattern consistency, and growth readiness — all at a fraction of the cost and time of the o1-based evaluator.

## Use Cases

- **Quick sanity check**: Run before a deeper `arch-review` to catch obvious structural issues
- **Pre-merge gate**: Fast architectural check as part of the review workflow
- **During development**: Get rapid feedback on structural decisions while coding
- **Routine PRs**: Architectural check for standard feature work

## Model

- **Model**: `gemini/gemini-2.5-flash`
- **Provider**: Google
- **Category**: arch-review
- **Timeout**: 180s

## Cost Estimate

~$0.003-0.01 per review. Roughly 30x cheaper than `arch-review`.

## Example Usage

```bash
# Quick architectural check during development
adversarial evaluate --evaluator arch-review-fast src/dispatch_kit/bus.py

# Run on multiple files
adversarial evaluate --evaluator arch-review-fast src/dispatch_kit/models/event.py
```

## Output

The evaluator produces:

1. **Quick Assessment Table** — ratings across 6 dimensions (responsibility, coupling, cohesion, API, patterns, growth)
2. **Findings** — categorized as COUPLING, COHESION, API, PATTERN, or RISK
3. **What's Good** — decisions worth preserving
4. **Verdict**: APPROVED, REVISION_SUGGESTED, or RESTRUCTURE_NEEDED

## When to Use

| Scenario | Use arch-review-fast? |
|----------|----------------------|
| Routine PR review | Yes |
| Quick check during development | Yes |
| Pre-merge gate | Yes |
| Foundational/critical components | No, use arch-review |
| Security-focused review | No, use claude-code or o1-code-review |
| Line-level bug finding | No, use gpt4o-code |

## See Also

- [arch-review](../../openai/arch-review/) - Deep architectural review using o1 (slower, more thorough)
- [gemini-code](../gemini-code/) - Line-level code review using Gemini 3 Pro
- [gemini-deep](../gemini-deep/) - General extended reasoning analysis
