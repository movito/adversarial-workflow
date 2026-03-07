# arch-review

Deep architectural review using OpenAI o1 reasoning.

## Overview

This evaluator uses OpenAI's o1 model with extended reasoning to perform architectural-level code review. Unlike line-level code review (security bugs, style issues), this evaluator focuses on structural quality: coupling, cohesion, API design, pattern consistency, and growth readiness.

## Use Cases

- **Design doc conformance**: Verify implementations match their design documents
- **Coupling analysis**: Detect tight coupling, circular dependencies, dependency direction violations
- **API surface review**: Evaluate whether public APIs are minimal, intuitive, and consistent
- **Pattern consistency**: Check if new code follows established project conventions
- **Growth assessment**: Predict how well the current structure will hold under increasing complexity

## Model

- **Model**: `o1`
- **Provider**: OpenAI
- **Category**: arch-review
- **Timeout**: 600s (extended for deep reasoning)

## Cost Estimate

~$0.10-0.30 per review depending on code size.

Use this evaluator for foundational components where structural quality matters more than speed.

## Example Usage

```bash
# Review a core module's architecture
adversarial evaluate --evaluator arch-review src/dispatch_kit/bus.py

# Review a data model's structure
adversarial evaluate --evaluator arch-review src/models/event.py

# Review an entire package
adversarial evaluate --evaluator arch-review src/dispatch_kit/
```

## Output

The evaluator produces:

1. **Architecture Summary** — what the code does and overall assessment
2. **Design Adherence Table** — ratings for concept independence, API quality, coupling, cohesion, pattern consistency
3. **Architectural Findings** — categorized as STRUCTURAL, COUPLING, API, or PATTERN
4. **Positive Decisions** — structural choices worth preserving
5. **Growth Risk Assessment** — low/medium/high-risk areas
6. **Verdict**: APPROVED, REVISION_SUGGESTED, or RESTRUCTURE_NEEDED

## When to Use

| Scenario | Use arch-review? |
|----------|------------------|
| Foundational modules (data models, core abstractions) | Yes |
| Pre-merge review of architectural components | Yes |
| After major refactors | Yes |
| Quick PR review | No, use arch-review-fast |
| Security-focused review | No, use o1-code-review |
| Line-level bug finding | No, use gpt4o-code |

## See Also

- [arch-review-fast](../../google/arch-review-fast/) - Faster/cheaper alternative using Gemini
- [o1-code-review](../o1-code-review/) - Line-level security and correctness review
- [gpt4o-code](../gpt4o-code/) - Fast general code review
