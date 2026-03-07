# ADV-0051: Port Evaluator Setup from dispatch-kit

**Status**: Todo
**Priority**: High
**Type**: Enhancement
**Estimated Effort**: 30 minutes
**Created**: 2026-03-07
**Source**: dispatch-kit project (.adversarial/evaluators/)

## Summary

Port the advanced evaluator setup from dispatch-kit into adversarial-workflow.
dispatch-kit has 25 evaluators across 4 providers; we only have the 3 built-in
GPT-4o evaluators. This task adds custom project evaluators and installs
library evaluators to enable proper task evaluation and code review.

## Scope

### 1. Custom Evaluators — Copy from dispatch-kit

Create `.adversarial/evaluators/custom/` with these project-specific evaluators:

1. **architecture-planner.yml** — Forward-looking task plan evaluation (o1)
2. **architecture-planner-fast.yml** — Fast task plan check (Gemini Flash, ~$0.004/run)
3. **architecture-reviewer.yml** — Backward-looking architecture review (o1)
4. **code-reviewer.yml** — Adversarial correctness review (o1)
5. **spec-compliance.yml** — Verify implementation matches spec (Gemini Flash)

Copy these verbatim from `/Users/broadcaster_three/Github/dispatch-kit/.adversarial/evaluators/custom/`.

Also copy `link-custom.sh` and run it to symlink into the evaluators root.

### 2. Provider Evaluators — Copy from dispatch-kit

Copy these provider subdirectories from dispatch-kit:

- `anthropic/` — claude-adversarial (Opus 4.6), claude-code (Sonnet 4.5), claude-quick (Haiku 4.5)
- `google/` — gemini-code, gemini-deep, gemini-flash, gemini-pro
- `openai/` — fast-check, gpt4o-code, gpt5-diversity, gpt5-synthesis, gpt52-reasoning, o1-code-review, o1-mini-code, o3-chain
- `mistral/` — codestral-code, mistral-content, mistral-fast

Each provider evaluator is a directory with `evaluator.yml`, `README.md`, and `CHANGELOG.md`.

### 3. Library Evaluators — Install

Install library evaluators (these have `_meta:` headers):

- `arch-review-fast` (Gemini Flash)
- `code-reviewer-fast` (Gemini Flash)

Copy these from dispatch-kit's `.adversarial/evaluators/` root:
- `google-arch-review-fast.yml`
- `google-code-reviewer-fast.yml`

### 4. Update EVALUATION-WORKFLOW.md

Update `.adversarial/docs/EVALUATION-WORKFLOW.md` to reflect the new evaluators.
Reference dispatch-kit's version as a guide. Key changes:

- Add deprecation notice for built-in evaluators
- Document custom evaluators and their use cases
- Document fast/deep pairs pattern
- Update "When to Use" guidance

### Integration Notes

- All evaluators use `{content}` placeholder in prompts — this is the standard pattern
- API keys needed: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `MISTRAL_API_KEY`
- Not all keys need to be present — evaluators gracefully skip if their key is missing
- The `link-custom.sh` script symlinks `custom/*.yml` to the evaluators root

## Source

dispatch-kit evaluators: `/Users/broadcaster_three/Github/dispatch-kit/.adversarial/evaluators/`

## PR Template

```
Title: feat: Port evaluator setup from dispatch-kit (ADV-0051)

Body:
## Summary
Ports the advanced evaluator setup from dispatch-kit. Adds 5 custom
evaluators (architecture-planner, code-reviewer, spec-compliance),
18 provider evaluators (Anthropic, Google, OpenAI, Mistral), and
2 library evaluators.

Enables proper task evaluation and adversarial code review with
fast/deep pairs across multiple AI providers.
```

## Acceptance Criteria

- [ ] `.adversarial/evaluators/custom/` contains 5 evaluator YMLs + link-custom.sh
- [ ] Custom evaluators symlinked to evaluators root
- [ ] Provider evaluator directories (anthropic/, google/, openai/, mistral/) copied
- [ ] Library evaluators (arch-review-fast, code-reviewer-fast) installed
- [ ] `adversarial list-evaluators` shows all new evaluators
- [ ] EVALUATION-WORKFLOW.md updated
- [ ] CI passes
- [ ] PR created and merged
