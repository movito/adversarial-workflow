# Adversarial Evaluation Workflow

**Created**: 2025-11-01
**Updated**: 2026-03-10 (rewrite: library evaluators are primary, built-ins deprecated)
**Purpose**: Complete guide to using the adversarial evaluation workflow
**Audience**: All agents (especially Planner)
**Tool**: `adversarial` CLI (v0.9.9+)
**Evaluator**: External AI via adversarial-workflow (library + custom evaluators)

> **DEPRECATION NOTICE**: The built-in evaluators (`adversarial evaluate`,
> `adversarial proofread`, `adversarial review`) are **deprecated**. Use library
> or custom evaluators instead — they support multiple providers (OpenAI, Google,
> Anthropic, Mistral), configurable models, and role-specific evaluation.
>
> **Quick migration**:
> - `adversarial evaluate <file>` → `adversarial architecture-planner <file>` or `adversarial architecture-planner-fast <file>`
> - `adversarial review <file>` → `adversarial code-reviewer <file>` or `adversarial code-reviewer-fast <file>`
> - `adversarial proofread <file>` → no direct replacement yet; use `adversarial gemini-flash <file>`
>
> Run `adversarial list-evaluators` to see all available evaluators.

---

## Table of Contents

- [Overview](#overview)
- [Quick Command Reference](#quick-command-reference)
- [Available Evaluators](#available-evaluators)
- [Discovering Evaluators](#discovering-evaluators)
- [Evaluator Installation](#evaluator-installation)
- [Custom Evaluators](#custom-evaluators)
- [What It Is (and Isn't)](#what-it-is-and-isnt)
- [Workflows](#workflows)
  - [Plan Evaluation](#plan-evaluation-workflow)
  - [Code Review](#code-review-workflow)
  - [Proofreading](#proofreading-workflow)
- [Evaluation Criteria](#evaluation-criteria)
- [Verdict Types](#verdict-types)
- [Cost Expectations](#cost-expectations)
- [Iteration Guidance](#iteration-guidance)
- [Known Issues](#known-issues)
- [Best Practices](#best-practices)
- [Legacy Built-in Evaluators](#legacy-built-in-evaluators)
- [Documentation References](#documentation-references)

---

## Overview

The adversarial workflow provides independent quality assurance using **external AI** for three types of content:

1. **Plan Evaluation** — Review implementation plans and architectural decisions
2. **Code Review** — Review implemented code for quality and correctness
3. **Proofreading** — Review teaching/documentation content quality

Evaluators are invoked via the `adversarial` CLI, which calls external AI APIs (OpenAI, Google, Mistral) through Aider. Output is saved to `.adversarial/logs/`.

**Key Benefit**: Catch issues early—design flaws in plans, bugs in code, clarity problems in docs—before they compound.

### Three categories of evaluators

| Category | Source | Example |
|----------|--------|---------|
| **Library** (22) | Installed via `adversarial library install` from [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library) | `code-reviewer-fast`, `gemini-flash`, `openai-o3` |
| **Custom** (4) | Project-specific, in `.adversarial/evaluators/custom/` | `architecture-planner`, `spec-compliance` |
| **Built-in** (3) | Shipped with CLI (deprecated) | `evaluate`, `proofread`, `review` |

Library-installed evaluators are **gitignored** (installed per-environment, like `node_modules`). Custom evaluators are committed to the repository.

---

## Quick Command Reference

```bash
# Task plan / architecture evaluation (RECOMMENDED)
adversarial architecture-planner <task-file>           # Deep reasoning (o1, ~$0.20)
adversarial architecture-planner-fast <task-file>      # Fast check (Gemini Flash, ~$0.005)

# Code review
adversarial code-reviewer <input-file>                 # Deep reasoning (o1, ~$0.20)
adversarial code-reviewer-fast <input-file>            # Fast check (Gemini Flash, ~$0.005)

# Architecture review (existing code)
adversarial architecture-reviewer <input-file>         # Deep reasoning (o1)

# Spec compliance
adversarial spec-compliance <input-file>               # Gemini Flash (~$0.004)

# Discovery
adversarial list-evaluators              # Show all available evaluators

# Output is always in .adversarial/logs/<input-name>-<evaluator-suffix>.md

# System Commands
adversarial --version                    # Check CLI version
adversarial check                        # Validate setup and dependencies

# DEPRECATED (use library/custom evaluators above instead):
# adversarial evaluate <file>     → use architecture-planner
# adversarial review <file>       → use code-reviewer
# adversarial proofread <file>    → no direct replacement yet
```

---

## Available Evaluators

### Library evaluators (installed via `adversarial library install`)

**OpenAI providers** (require `OPENAI_API_KEY`):
- `openai-o3`, `openai-gpt4o`, `openai-gpt4o-mini`, `openai-gpt52`
- `code-reviewer`, `code-reviewer-fast`

**Google providers** (require `GEMINI_API_KEY`):
- `gemini-flash`, `gemini-pro`, `gemini-deep`

**Mistral providers** (require `MISTRAL_API_KEY`):
- `mistral-fast`, `mistral-content`, `codestral-code`

### Custom evaluators (committed, in `.adversarial/evaluators/custom/`)

| Evaluator | Model | Purpose | Cost |
|-----------|-------|---------|------|
| `architecture-planner` | o1 | Forward-looking plan evaluation | ~$0.20 |
| `architecture-planner-fast` | Gemini 2.5 Flash | Quick plan sanity check | ~$0.005 |
| `architecture-reviewer` | o1 | Deep review of existing code | ~$0.20 |
| `spec-compliance` | Gemini 2.5 Flash | Verify implementation matches spec | ~$0.004 |

### Quick Decision Guide

| Content Type | Evaluator | Why |
|--------------|-----------|-----|
| Task specification | `architecture-planner` or `-fast` | Forward-looking plan review |
| Architecture decision | `architecture-planner` | Technical design review |
| Completed feature | `code-reviewer` or `-fast` | Correctness review |
| Bug fix before merge | `code-reviewer-fast` | Quick verification |
| Spec compliance check | `spec-compliance` | Acceptance criteria audit |
| Pull request changes | `code-reviewer` | Pre-merge quality check |

**Rule of thumb:**
- **Planning code?** → `architecture-planner`
- **Code already written?** → `code-reviewer`
- **Checking spec match?** → `spec-compliance`

---

## Discovering Evaluators

```bash
adversarial list-evaluators
```

Shows all available evaluators across all categories (built-in, library, custom).

---

## Evaluator Installation

### Library evaluators

```bash
# Install from the evaluator library (v0.5.3)
./scripts/core/project install-evaluators

# Or install a specific version
./scripts/core/project install-evaluators --ref v0.6.0

# Reinstall (force)
./scripts/core/project install-evaluators --force
```

Library evaluators are installed to `.adversarial/evaluators/` and gitignored.

### Custom evaluators

Custom evaluators live in `.adversarial/evaluators/custom/` and are committed to the repo. After installing library evaluators, link custom evaluators so the CLI finds them:

```bash
.adversarial/evaluators/custom/link-custom.sh
```

This creates symlinks from `.adversarial/evaluators/<name>.yml` → `custom/<name>.yml`.

### API keys

Each provider requires its own API key (set in `.env`):
- `OPENAI_API_KEY` — OpenAI evaluators (o1, gpt-4o, etc.)
- `GEMINI_API_KEY` — Google evaluators (Gemini Flash, Pro, Deep)
- `MISTRAL_API_KEY` — Mistral evaluators

---

## Custom Evaluators

Custom evaluators are YAML files in `.adversarial/evaluators/custom/`.

### Creating a Custom Evaluator

Create a file like `.adversarial/evaluators/custom/my-evaluator.yml`:

```yaml
name: my-evaluator
description: What this evaluator does
model: gemini/gemini-2.5-flash
api_key_env: GEMINI_API_KEY
model_requirement:
  family: gemini
  tier: flash
  min_version: "2.5"
output_suffix: -my-evaluator.md
timeout: 180

prompt: |
  You are an expert reviewer. The document to evaluate will be appended below.

  ## Review Protocol
  [Your structured review instructions here]

  ## Output Format
  [Your expected output structure here]

  ## Verdict
  - **APPROVED**: [when to approve]
  - **NEEDS_REVISION**: [when to request revision]
```

### Schema

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Command name (lowercase, hyphenated) |
| `description` | Yes | Short description shown in `list-evaluators` |
| `model` | Yes | AI model ID (see aider docs for formats) |
| `api_key_env` | Yes | Environment variable for API key |
| `model_requirement` | No | Structured model requirements (family/tier/min_version) |
| `output_suffix` | No | Suffix for output files (default: `-EVALUATION.md`) |
| `timeout` | No | Timeout in seconds (default: 180) |
| `prompt` | Yes | System prompt — file content is appended automatically |

**Important**: The CLI appends the evaluated file's content after the prompt automatically. Do not use `{content}` or other placeholder tokens in prompts.

### Linking custom evaluators

After creating or modifying custom evaluators, run:

```bash
.adversarial/evaluators/custom/link-custom.sh
```

---

## What It Is (and Isn't)

### What It IS:
- **External AI evaluator** invoked via `adversarial <evaluator-name> <file>` CLI commands
- Uses Aider to call external AI APIs (OpenAI, Google, Mistral, etc.)
- Saves output to `.adversarial/logs/` as markdown
- Independent critical review from a different AI model (external evaluator, not Claude)

### What It is NOT:
- **NOT** Claude in a new UI tab (that's for manual user review)
- **NOT** a Claude Code Task tool agent
- **NOT** a Claude Code subagent (evaluators are external, via CLI)
- **NOT** a replacement for human review (it's a complement)

---

## Workflows

### Plan Evaluation Workflow

**1. Planner creates task specification**

```bash
delegation/tasks/2-todo/TASK-XXXX-description.md
```

**2. Planner runs evaluation**

```bash
# Recommended: fast check first
adversarial architecture-planner-fast delegation/tasks/2-todo/TASK-XXXX-description.md

# For important tasks: deep evaluation
adversarial architecture-planner delegation/tasks/2-todo/TASK-XXXX-description.md

# For large files (>500 lines):
echo y | adversarial architecture-planner delegation/tasks/2-todo/TASK-XXXX-description.md
```

**3. Read evaluation output**

```bash
cat .adversarial/logs/TASK-XXXX-description-architecture-planner.md
```

**4. Address CRITICAL and HIGH priority feedback**, then repeat if NEEDS_REVISION.

**5. If PROCEED (or planner override): Assign to specialized agent.**

---

### Code Review Workflow

**1. Implementation is complete and tests pass**

```bash
pytest tests/ -v
```

**2. Run code review**

```bash
# Fast check
adversarial code-reviewer-fast src/feature/new_module.py

# Deep review (for critical code)
adversarial code-reviewer src/feature/new_module.py

# Spec compliance (pass both spec and implementation)
adversarial spec-compliance src/feature/new_module.py --context delegation/tasks/3-in-progress/TASK-0001.md
```

**3. Read review output and address findings**

```bash
cat .adversarial/logs/new_module-code-reviewer.md
```

**4. If NEEDS_REVISION: fix and re-run. If APPROVED: proceed to merge.**

---

### Proofreading Workflow

No dedicated proofreading evaluator yet. Use a general-purpose evaluator:

```bash
adversarial gemini-flash docs/guide.md
```

---

## Evaluation Criteria

### Plan Evaluation (architecture-planner)

1. **Plan Clarity** — Goal stated? Acceptance criteria testable? Ambiguities?
2. **Architectural Fit** — Respects dependency rules and module boundaries?
3. **Dependencies** — Satisfied? Hidden or circular?
4. **Risk Assessment** — Edge cases? Scope appropriate? Breaking changes?
5. **Test Strategy** — Right things tested? Coverage gaps?

### Code Review (code-reviewer)

1. **Input Boundary Analysis** — Empty/null/missing inputs? Boundary values? Malformed data?
2. **State & Concurrency** — Inconsistent state? Race conditions? Resource cleanup?
3. **Error Handling** — All error paths tested? Exceptions leak info? Silent swallowing?
4. **Logic & Semantics** — Off-by-one? Operator precedence? Dead code? Type confusion?
5. **Test Gaps** — Missing tests for critical paths?

### Spec Compliance (spec-compliance)

1. **Acceptance Criteria Audit** — Each criterion: implemented? Where? Tested?
2. **Spec Drift** — Features added/changed beyond spec? Implicit requirements?
3. **Contract Verification** — Signatures match? Return types? Error behaviors?
4. **Test Coverage** — Each criterion has at least one test?

---

## Verdict Types

Each evaluator may use slightly different verdict names, but they map to three outcomes:

| Outcome | Custom Evaluator Verdicts | Action |
|---------|--------------------------|--------|
| **Pass** | APPROVED, PROCEED, COMPLIANT, PASS | Proceed to next step |
| **Revise** | NEEDS_REVISION, MOSTLY_COMPLIANT, REVISION_SUGGESTED, CONCERNS | Address feedback, re-run |
| **Reject** | REJECTED, RETHINK, RESTRUCTURE_NEEDED, NON_COMPLIANT, FAIL | Major rework needed |

**Always check the log file** for the actual verdict — the CLI wrapper may report a different status.

---

## Cost Expectations

| Evaluator | Cost per run | Typical workflow |
|-----------|-------------|-----------------|
| `architecture-planner` (o1) | ~$0.20 | $0.40-0.60 (2-3 rounds) |
| `architecture-planner-fast` (Gemini Flash) | ~$0.005 | $0.01-0.015 |
| `code-reviewer` (o1) | ~$0.20 | $0.20-0.40 (1-2 rounds) |
| `code-reviewer-fast` (Gemini Flash) | ~$0.005 | $0.005-0.01 |
| `spec-compliance` (Gemini Flash) | ~$0.004 | $0.004 (usually 1 round) |

**File Size Limit**: Files >500 lines may hit rate limits on Tier 1 OpenAI accounts (30k TPM limit).

---

## Iteration Guidance

### Plan Evaluation: 2-3 Rounds Optimal

**When to Stop:**
1. All CRITICAL/HIGH concerns addressed
2. Evaluator asking for implementation-level details (beyond planning scope)
3. Diminishing returns on planning detail
4. Manual planner approval (planner override)

### Code Review: 1-2 Rounds Optimal

**When to Stop:**
1. All CRITICAL/HIGH concerns addressed
2. Code is correct and tests pass
3. Remaining issues are style preferences

**Override**: Planner/agent can approve NEEDS_REVISION when remaining issues are minor or implementation-level details that will be resolved during coding.

---

## Known Issues

### 1. Wrapper Verdict Bug
**Issue**: CLI wrapper may report "Evaluation approved!" even when actual verdict is NEEDS_REVISION.
**Solution**: Always check the log file for the actual verdict.

### 2. Large Files & Rate Limiting
**Issue**: Files >500 lines may fail on Tier 1 OpenAI accounts.
**Solution**: Break into smaller files, or use Gemini Flash evaluators (higher token limits).

### 3. Interactive Mode
**Issue**: Large files require interactive confirmation.
**Solution**: Use `echo y | adversarial <evaluator> <file>`.

---

## Best Practices

### DO:
- Use library/custom evaluators instead of deprecated built-ins
- Choose the right evaluator: `architecture-planner` for plans, `code-reviewer` for code
- Always check `.adversarial/logs/` for the actual verdict
- Start with `-fast` variants for iterative refinement, use deep (o1) for final check

### DON'T:
- Don't use Task tool to invoke evaluators (they are external via CLI)
- Don't confuse "new tabs" instruction (for manual review) with adversarial workflow
- Don't skip evaluation for complex/risky content
- Don't ignore CRITICAL concerns

---

## Legacy Built-in Evaluators

> **Deprecated** — these use hardcoded shell scripts and only support OpenAI.
> Use library/custom evaluators instead.

| Command | Replacement |
|---------|-------------|
| `adversarial evaluate <file>` | `adversarial architecture-planner <file>` |
| `adversarial review <file>` | `adversarial code-reviewer <file>` |
| `adversarial proofread <file>` | `adversarial gemini-flash <file>` |

The built-in evaluators still work but receive no updates.

---

## Documentation References

### Configuration:
- **Config file**: `.adversarial/config.yml`
- **Evaluator library**: https://github.com/movito/adversarial-evaluator-library

### Related Documentation:
- **Evaluator library docs**: `.adversarial/evaluators/README.md`
- **Evaluation logs**: `.adversarial/logs/`
- **ADR**: `docs/decisions/adr/ADR-0011-adversarial-workflow-integration.md`

---

**Last Updated**: 2026-03-10
**Maintained By**: Planner and feature-developer agents
