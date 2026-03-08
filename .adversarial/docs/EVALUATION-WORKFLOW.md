# Adversarial Evaluation Workflow

**Created**: 2025-11-01
**Updated**: 2026-03-08 (port evaluator setup from dispatch-kit v0.4.2)
**Purpose**: Complete guide to using the adversarial evaluation workflow
**Audience**: All agents (especially Planner)
**Tool**: `adversarial` CLI (v0.9.9+)

> **DEPRECATION NOTICE**: The default built-in presets behind
> `adversarial evaluate <file>`, `adversarial proofread <file>`, and
> `adversarial review <file>` are **deprecated**. Use the named evaluators
> instead (e.g., `adversarial architecture-planner-fast <file>`) — they support
> multiple providers (OpenAI, Google, Anthropic, Mistral), configurable models,
> and role-specific evaluation.
>
> **Quick migration**:
> - `adversarial evaluate <file>` -> `adversarial architecture-planner-fast <file>`
> - `adversarial review <file>` -> `adversarial code-reviewer-fast <file>`
> - For deep analysis: `adversarial architecture-planner <file>` or `adversarial code-reviewer <file>`
>
> Run `adversarial list-evaluators` to see all available evaluators.

---

## Available Evaluators

### Custom Evaluators (Project-Specific)

These are tailored for our workflow in `.adversarial/evaluators/custom/`:

| Evaluator | Model | Cost | Use Case |
|-----------|-------|------|----------|
| `architecture-planner` | o1 | ~$0.10 | Deep task plan evaluation before implementation |
| `architecture-planner-fast` | Gemini Flash | ~$0.004 | Quick task plan sanity check |
| `architecture-reviewer` | o1 | ~$0.10 | Post-implementation architecture review |
| `code-reviewer` | o1 | ~$0.10 | Adversarial correctness review (finds bugs bots miss) |
| `spec-compliance` | Gemini Flash | ~$0.004 | Verify implementation matches task spec |

### Library Evaluators (Installed)

| Evaluator | Model | Use Case |
|-----------|-------|----------|
| `arch-review-fast` | Gemini Flash | Fast architectural review |
| `code-reviewer-fast` | Gemini Flash | Fast adversarial correctness check |

### Provider Evaluators

Organized by vendor in `.adversarial/evaluators/<provider>/`:

**Anthropic**: `claude-adversarial` (Opus 4.6), `claude-code` (Sonnet 4.5), `claude-quick` (Haiku 4.5)
**Google**: `arch-review-fast`, `code-reviewer-fast`, `gemini-code`, `gemini-deep`, `gemini-flash`, `gemini-pro`
**OpenAI**: `arch-review` (o1), `code-reviewer` (o1), `fast-check`, `gpt4o-code`, `gpt5-diversity`, `gpt5-synthesis`, `gpt52-reasoning`, `o1-code-review`, `o1-mini-code`, `o3-chain`
**Mistral**: `codestral-code`, `mistral-content`, `mistral-fast`

### Built-in Evaluators (Deprecated)

| Command | Model | Status |
|---------|-------|--------|
| `adversarial evaluate` | GPT-4o | Deprecated — use `architecture-planner-fast` |
| `adversarial review` | GPT-4o | Deprecated — use `code-reviewer-fast` |
| `adversarial proofread` | GPT-4o | Deprecated — use `gemini-flash` |

---

## Fast/Deep Pairs Pattern

Most evaluation needs have a fast (cheap) and deep (thorough) option:

| Need | Fast (~$0.004) | Deep (~$0.10) |
|------|----------------|---------------|
| Task plan evaluation | `architecture-planner-fast` | `architecture-planner` |
| Code review | `code-reviewer-fast` | `code-reviewer` |
| Architecture review | `arch-review-fast` | `architecture-reviewer` |

**Rule of thumb**: Use fast for iteration and small tasks. Use deep for complex/critical tasks before assignment.

---

## When to Run Evaluation

### Task Plan Evaluation (Planner)

- Before assigning complex tasks (>500 lines) to implementation agents
- Tasks with critical dependencies or architectural risks
- After creating new task specifications

```bash
# Quick check (~$0.004):
adversarial architecture-planner-fast delegation/tasks/2-todo/TASK-FILE.md

# Deep analysis (~$0.10):
adversarial architecture-planner delegation/tasks/2-todo/TASK-FILE.md
```

### Code Review (Post-Implementation)

- After implementation, before merge
- When bot reviews (CodeRabbit, BugBot) are insufficient

```bash
# Quick check:
adversarial code-reviewer-fast path/to/file.py

# Deep adversarial review:
adversarial code-reviewer path/to/file.py
```

### Spec Compliance (Post-Implementation)

- Verify implementation matches task specification

```bash
adversarial spec-compliance delegation/tasks/3-in-progress/TASK-FILE.md
```

---

## Iteration Guidance

- Max 2-3 evaluations per task
- Address CRITICAL/HIGH findings; use judgment on MEDIUM/LOW
- After 2 NEEDS_REVISION verdicts, escalate to user
- Coordinator can approve despite evaluator verdict when appropriate

---

## API Keys Required

Evaluators require API keys set as environment variables:

| Provider | Variable | Required For |
|----------|----------|-------------|
| OpenAI | `OPENAI_API_KEY` | o1, o3, GPT-4o, GPT-5 evaluators |
| Google | `GEMINI_API_KEY` | Gemini Flash/Pro evaluators |
| Anthropic | `ANTHROPIC_API_KEY` | Claude evaluators |
| Mistral | `MISTRAL_API_KEY` | Mistral/Codestral evaluators |

Missing keys are handled gracefully — the evaluator will error with a clear message.

---

## Output

All evaluation results are written to `.adversarial/logs/`:

```
.adversarial/logs/<input-filename>-<evaluator-name>.md
```

---

## Managing Evaluators

```bash
# List all available evaluators:
adversarial list-evaluators

# Re-link custom evaluators after changes:
.adversarial/evaluators/custom/link-custom.sh
```

---

## Source

Evaluators ported from [dispatch-kit v0.4.2](https://github.com/movito/dispatch-kit/releases/tag/v0.4.2).
