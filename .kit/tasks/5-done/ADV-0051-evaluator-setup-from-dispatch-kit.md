# ADV-0051: Install Evaluator Library + Custom Evaluators

**Status**: Done
**Priority**: High
**Type**: Enhancement
**Estimated Effort**: 20 minutes
**Created**: 2026-03-07
**Updated**: 2026-03-08 (revised approach — use library install, not file copy)
**Depends On**: ADV-0040 (slash commands for bot triage)

## Summary

Install evaluators using `adversarial library install` for provider evaluators,
and copy only the 5 custom project evaluators from dispatch-kit. Previous
attempts (PR #36, #37) copied 60+ files from dispatch-kit which triggered
endless bot review cycles on upstream-authored content.

## Revised Approach

### Why the change

The CLI already has `adversarial library install` which installs clean, versioned
evaluator YMLs with `_meta:` headers — one file per evaluator, no READMEs or
CHANGELOGs for bots to nitpick. Previous approach of copying dispatch-kit's
installed snapshot (with its provider subdirectories, stale metadata, and
project-specific paths) was pulling from the wrong layer.

### Architecture

```
adversarial-evaluator-library  <-- install from here (22 provider evaluators)
dispatch-kit                   <-- copy only custom/ from here (5 evaluators)
```

## Scope

### 1. Install Provider Evaluators via Library

```bash
adversarial library install --force --yes \
  google/gemini-flash google/gemini-pro google/gemini-deep google/gemini-code \
  google/code-reviewer-fast google/arch-review-fast \
  openai/arch-review openai/code-reviewer openai/o1-code-review \
  openai/o1-mini-code openai/gpt4o-code openai/fast-check \
  openai/o3-chain openai/gpt5-diversity openai/gpt5-synthesis \
  openai/gpt52-reasoning \
  anthropic/claude-adversarial anthropic/claude-code anthropic/claude-quick \
  mistral/codestral-code mistral/mistral-content mistral/mistral-fast
```

This installs 22 evaluators as single YML files in `.adversarial/evaluators/`.

### 2. Custom Evaluators — Copy from dispatch-kit

Copy only the 5 custom evaluator YMLs + link script from dispatch-kit v0.4.2:

1. `architecture-planner.yml` — Forward-looking task plan evaluation (o1)
2. `architecture-planner-fast.yml` — Fast task plan check (Gemini Flash)
3. `architecture-reviewer.yml` — Backward-looking architecture review (o1)
4. `code-reviewer.yml` — Adversarial correctness review (o1)
5. `spec-compliance.yml` — Verify implementation matches spec (Gemini Flash)
6. `link-custom.sh` — Symlinks custom evaluators to evaluators root

Source: dispatch-kit v0.4.2 `.adversarial/evaluators/custom/`

### 3. Create EVALUATION-WORKFLOW.md

Create `.adversarial/docs/EVALUATION-WORKFLOW.md` documenting:
- Deprecation notice for built-in evaluators
- Custom evaluators and their use cases
- Fast/deep pairs pattern
- API key requirements
- Source reference (library + dispatch-kit v0.4.2)

### 4. .gitignore Library Evaluators

Add `.adversarial/evaluators/*.yml` (but NOT `custom/`) to `.gitignore`.
Library-installed evaluators should not be committed — they're installed per-environment
like node_modules. Only custom evaluators are committed.

Alternative: commit them. Decide based on team preference.

## PR Template

```
Title: feat: Install evaluator library + custom evaluators (ADV-0051)

Body:
## Summary
Installs 22 provider evaluators via `adversarial library install` and
adds 5 custom project evaluators from dispatch-kit v0.4.2.

Replaces the file-copy approach from PRs #36/#37 with proper library
installation.
```

## Acceptance Criteria

- [ ] 22 provider evaluators installed via `adversarial library install`
- [ ] 5 custom evaluators in `.adversarial/evaluators/custom/`
- [ ] Custom evaluators symlinked to evaluators root
- [ ] `adversarial list-evaluators` shows all evaluators
- [ ] EVALUATION-WORKFLOW.md created
- [ ] CI passes
- [ ] PR created and merged

## History

- PR #36: Closed — copied from dispatch-kit v0.4.1, 14 bot findings
- PR #37: Closed — updated to v0.4.2, still 30+ bot findings on upstream files
- Lesson: Use library install for provider evaluators, copy only custom ones
