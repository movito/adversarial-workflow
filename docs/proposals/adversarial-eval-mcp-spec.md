# Adversarial Eval MCP Server — Project Specification

**Status**: Draft (rev 2 — incorporates Dispatch feedback)
**Date**: 2026-04-04
**Author**: planner2 (with user input)
**Origin**: Dispatch agent proposal for content evaluation tooling
**Reviewed by**: Dispatch agent (2026-04-04)

---

## 1. Problem Statement

The existing `adversarial-workflow` CLI evaluates **code and task specifications**
using aider as an execution bridge. It is not suited for evaluating **research
writing, essays, reports, and other text content** because:

- Aider is a code-editing tool — unnecessary overhead for text evaluation
- The evaluator prompts are code-review-oriented (git diffs, task specs, test coverage)
- The CLI workflow (plan → implement → review → test) doesn't map to content production
- Dispatch agents need MCP tool access, not a CLI subprocess

**Goal**: A lightweight Python MCP server that evaluates text content against
configurable criteria using multiple LLM APIs, returning structured verdicts.

## 2. Project Identity

- **Repo**: `adversarial-eval-mcp` (new, separate from `adversarial-workflow`)
- **Language**: Python 3.10+
- **Interface**: MCP server (stdio transport)
- **Registration**: `~/.claude/mcp_settings.json` (alongside existing MCP servers)
- **No dependency on**: aider, adversarial-workflow, or the evaluator-library repo

## 3. MCP Tools

### 3.1 `evaluate`

The core tool. Sends content to an evaluator and returns a structured verdict.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content` | string | yes | The text to evaluate |
| `evaluator` | string | yes | Evaluator name (e.g. `"argument-strength"`) |
| `context` | string | no | Additional context for the evaluator (e.g. "This is a research report on German design theory for an academic audience") |

**Returns:**

```json
{
  "evaluator": "argument-strength",
  "model": "claude-sonnet-4-6",
  "verdict": "NEEDS_REVISION",
  "confidence": "high",
  "findings": "## Findings\n\n### Strengths\n- ...\n\n### Issues\n1. ...",
  "timestamp": "2026-04-04T14:30:00Z"
}
```

### 3.2 `evaluate_file`

Convenience wrapper. Reads a file from disk and delegates to `evaluate`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | yes | Absolute path to the file to evaluate |
| `evaluator` | string | yes | Evaluator name |
| `context` | string | no | Additional context |

**Returns:** Same schema as `evaluate`.

### 3.3 `list_evaluators`

Discovery tool. Returns available evaluators with metadata.

**Parameters:** None.

**Returns:**

```json
[
  {
    "name": "argument-strength",
    "description": "Evaluate logical coherence, evidence quality, and argument structure",
    "model": "claude-sonnet-4-6",
    "category": "reasoning"
  },
  {
    "name": "clarity-concision",
    "description": "Assess readability, concision, and audience-appropriateness",
    "model": "gemini-2.5-flash",
    "category": "style"
  }
]
```

### 3.4 `batch_evaluate` (V2 — defer)

Runs multiple evaluators in parallel on the same content. Deferred to V2 because
it requires error handling for partial failures (e.g., one API times out) that's
worth getting right rather than shipping half-baked.

**V2 Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content` | string | yes | The text to evaluate |
| `evaluators` | string[] | yes | Array of evaluator names |
| `context` | string | no | Additional context |

**V2 Returns:** Array of verdict objects + summary.

## 4. Evaluator YAML Format

Each evaluator lives in `evaluators/<name>/evaluator.yml` within the MCP server
repo. The format is inspired by but distinct from `adversarial-workflow` evaluators.

```yaml
name: argument-strength
description: Evaluate logical coherence, evidence quality, and argument structure
category: reasoning  # reasoning | style | accuracy | structure | domain

model: claude-sonnet-4-6
api_key_env: ANTHROPIC_API_KEY
timeout: 120  # seconds
max_content_tokens: 30000  # warn if content exceeds this (model-dependent)

# Verdict configuration
verdicts:
  approve: [APPROVED, STRONG, SOUND]
  revise: [NEEDS_REVISION, WEAK_POINTS, MIXED]
  reject: [REJECTED, UNSOUND, INCOHERENT]

prompt: |
  You are an expert evaluator assessing the strength of argumentation
  in a piece of writing.

  {context}

  ## Content to Evaluate

  {content}

  ## Evaluation Criteria

  Assess the following dimensions:

  1. **Logical coherence**: Are arguments internally consistent?
     Do conclusions follow from premises?
  2. **Evidence quality**: Are claims supported? Is evidence relevant
     and sufficient?
  3. **Counterargument awareness**: Does the author acknowledge and
     address opposing viewpoints?
  4. **Assumption transparency**: Are key assumptions stated explicitly?

  ## Response Format

  Begin with a single-word verdict: APPROVED, NEEDS_REVISION, or REJECTED.

  Then provide:
  ### Strengths
  - (bullet list)

  ### Issues
  - (numbered list with specific locations/quotes)

  ### Recommendations
  - (actionable suggestions)
```

### Key differences from adversarial-workflow evaluators

| Feature | adversarial-workflow | adversarial-eval-mcp |
|---------|---------------------|----------------------|
| Execution | Via aider subprocess | Direct API call |
| Placeholders | `{content}` only (file passed via `--read`) | `{content}` + `{context}` |
| `model_requirement` | Complex resolver with family/tier/version | Direct model ID (simpler) |
| `output_suffix` | Yes (log file naming) | No (caller handles persistence) |
| Verdict parsing | Hardcoded pass/revise/reject lists | Configurable per evaluator |
| Category | Not present | `reasoning`, `style`, `accuracy`, `structure`, `domain` |

## 5. Architecture

```
adversarial-eval-mcp/
├── src/
│   └── adversarial_eval_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server setup, tool registration
│       ├── evaluator.py       # Load YAML, substitute placeholders, parse verdicts
│       ├── api_client.py      # Unified API dispatch (Anthropic, OpenAI, Google)
│       ├── logger.py          # Append-only JSONL evaluation audit log
│       └── types.py           # Pydantic models: EvaluatorConfig, Verdict, etc.
├── evaluators/                # Content evaluator YAMLs
│   ├── argument-strength/
│   │   └── evaluator.yml
│   ├── clarity-concision/
│   │   └── evaluator.yml
│   ├── factual-accuracy/
│   │   └── evaluator.yml
│   └── structure-flow/
│       └── evaluator.yml
├── tests/
│   ├── test_evaluator.py
│   ├── test_api_client.py
│   └── test_server.py
├── pyproject.toml
├── README.md
└── .env.example
```

### Component responsibilities

**`server.py`** — MCP server entry point. Registers tools, handles stdio transport.
Uses `mcp` Python SDK. Loads evaluators on startup.

**`evaluator.py`** — Reads evaluator YAML configs, substitutes `{content}` and
`{context}` placeholders into the prompt, parses the model response for verdict
keywords. Before calling the API, estimates token count and warns if content
exceeds the evaluator model's practical context limit.

**`api_client.py`** — Thin wrapper over API clients. Takes a model ID and prompt,
routes to the correct API (Anthropic, OpenAI, Google) based on model prefix or
`api_key_env`. Returns raw text response and token usage. Handles timeouts.
Uses a provider registry pattern so adding OpenAI (or any other provider) is a
single new class implementing a `complete(model, prompt) -> (text, usage)` interface.

**`types.py`** — Pydantic models for config and responses. Provides validation
and serialization.

**`logger.py`** — Append-only JSONL evaluation log. Every evaluation writes one
line to `~/.adversarial-eval-mcp/evaluations.jsonl` containing: timestamp,
evaluator name, model, verdict, content hash (SHA-256, not the content itself),
and token usage. This gives a persistent audit trail that survives ephemeral
Dispatch sessions. The log path is configurable via environment variable.

### Dependency budget

```
mcp                    # MCP Python SDK (stdio server)
pyyaml                 # Evaluator YAML parsing
pydantic               # Config/response validation
anthropic              # Anthropic API client
openai                 # OpenAI API client
google-genai           # Google Generative AI client
```

No aider. No adversarial-workflow. No LiteLLM (direct client calls are simpler
for 3 providers). Token estimation uses a simple heuristic (chars / 4) rather
than a tokenizer dependency — good enough for limit warnings.

## 6. Usage Pattern

Dispatch calls MCP directly. No intermediary, no skill definition needed — just
a convention the agent follows.

```
Dispatch drafts/receives content
  → calls evaluate tool with markdown content
  → if APPROVED: proceed (convert to PDF, send to reMarkable, etc.)
  → if NEEDS_REVISION: present findings to user, ask whether to revise or override
  → if user says revise: Dispatch revises in-context, re-evaluates
```

This is the only pattern for V1. If we find that Dispatch can't reliably handle
revision loops, we'll add a Claude Code orchestration layer — but the MCP server
design doesn't change either way.

## 7. Sample Evaluators (V1)

Four evaluators covering the primary dimensions of content quality:

| Name | Category | Model | Purpose |
|------|----------|-------|---------|
| `argument-strength` | reasoning | claude-sonnet-4-6 | Logical coherence, evidence, counterarguments |
| `clarity-concision` | style | gemini-2.5-flash | Readability, concision, audience fit |
| `factual-accuracy` | accuracy | claude-sonnet-4-6 | Claims verification, source quality, hedging |
| `structure-flow` | structure | gemini-2.5-flash | Organization, transitions, narrative arc |

Model choices: Sonnet for reasoning-heavy tasks, Gemini Flash for style/structure
(fast, cheap, good at surface-level analysis). These are starting points — swap
models based on empirical results.

## 8. Verdict Schema

Verdicts are normalized to three tiers regardless of the evaluator's raw output:

| Tier | Meaning | Action |
|------|---------|--------|
| `APPROVED` | Content meets criteria | Proceed |
| `NEEDS_REVISION` | Specific issues identified | Revise and re-evaluate |
| `REJECTED` | Fundamental problems | Major rework needed |

Each evaluator YAML defines synonym lists (`verdicts.approve`, `verdicts.revise`,
`verdicts.reject`) so domain-specific language maps to the standard tiers.

The `confidence` field (`high` / `medium` / `low`) is extracted from the evaluator
response if present, defaulting to `medium`. This helps callers decide whether
to auto-act or ask the user.

## 9. V1 Scope

### In scope
- MCP server with `evaluate`, `evaluate_file`, `list_evaluators`
- Direct API calls to Anthropic and Google (2 providers)
- Provider registry pattern (adding OpenAI is one new class)
- 4 content evaluators (argument, clarity, accuracy, structure)
- Structured verdict response with token usage
- Content token estimation and limit warnings
- Append-only JSONL evaluation log (`~/.adversarial-eval-mcp/evaluations.jsonl`)
- Registration in `~/.claude/mcp_settings.json`
- Basic tests

### Deferred to V2
- `batch_evaluate` (parallel multi-evaluator)
- OpenAI/Mistral providers (registry makes this trivial)
- Cost estimation from token usage data
- Claude Code orchestration skill (only if Dispatch can't handle revision loops)
- Evaluator prompt iteration based on real usage

## 10. Open Questions

1. ~~**Persistence**~~ — **Resolved**: Server logs to JSONL. Dispatch sessions
   are ephemeral; the server owns the audit trail.

2. ~~**Max content length**~~ — **Resolved**: Evaluator YAML declares
   `max_content_tokens`. Server estimates token count and warns in the response
   if content exceeds the limit (does not block — the caller decides).

3. **reMarkable integration**: The proposal mentions send-to-remarkable as the
   downstream action. Is that an existing MCP tool, a Dispatch skill, or something
   to build? (Out of scope for this project, but affects the end-to-end workflow.)

4. **Evaluator prompt tuning**: How do we iterate on evaluator prompts? For V1,
   manual YAML editing. The JSONL log provides data to assess evaluator quality
   over time (verdict distribution, revision rates).

---

*This spec will be refined based on discussion. Once agreed, it becomes the
project's design document and README foundation.*
