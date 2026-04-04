# Scaffold Prompt: adversarial-eval-mcp

**Purpose**: Give this prompt to a Claude Code session opened in a fresh clone of
`agentive-starter-kit`. It transforms the starter kit into the `adversarial-eval-mcp`
project — a Python MCP server for adversarial evaluation of text content.

**Prerequisites**: The repo has already been created via:
```bash
gh repo create movito/adversarial-eval-mcp --template agentive-starter-kit/agentive-starter-kit --private --clone
cd adversarial-eval-mcp
```

---

## Prompt

You are setting up a new project called **adversarial-eval-mcp** — a Python MCP
server that evaluates text content (research writing, essays, reports) against
configurable criteria using multiple LLM APIs, returning structured verdicts.

This repo was cloned from `agentive-starter-kit`. Your job is to transform it
into the MCP server project. Follow each section in order.

### 1. Read the spec

Read `docs/proposals/adversarial-eval-mcp-spec.md` if it exists in this repo.
If it doesn't, here is the full design:

- **4 MCP tools**: `evaluate`, `evaluate_file`, `list_evaluators`, (and `batch_evaluate` deferred to V2)
- **Python MCP server** using `mcp` SDK, stdio transport
- **Direct API calls** to Anthropic and Google (no aider dependency)
- **Content-specific evaluator YAMLs** in `evaluators/` directory
- **Append-only JSONL audit log** at `~/.adversarial-eval-mcp/evaluations.jsonl`
- **Token estimation** warns if content exceeds evaluator's `max_content_tokens`

### 2. Rename the Python package

Rename the main package directory and update all references:

```
adversarial_workflow/ → adversarial_eval_mcp/
```

The package should have this structure:

```
adversarial_eval_mcp/
├── __init__.py          # Package version, minimal
├── server.py            # MCP server entry point, tool registration
├── evaluator.py         # Load YAML configs, substitute placeholders, parse verdicts
├── api_client.py        # Provider registry, API dispatch (Anthropic, Google)
├── logger.py            # Append-only JSONL evaluation audit log
└── types.py             # Pydantic models: EvaluatorConfig, Verdict, ApiResponse
```

**Delete everything from the old package** (`cli.py`, `evaluators/`, `library/`,
`utils/`, `templates/`, `__main__.py`). This is a completely different project —
do not carry over any code.

### 3. Update pyproject.toml

Replace the project metadata and dependencies:

```toml
[project]
name = "adversarial-eval-mcp"
version = "0.1.0"
description = "MCP server for adversarial evaluation of text content"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = [
    "mcp>=1.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "anthropic>=0.40",
    "google-genai>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=3.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.14",
]

[project.scripts]
adversarial-eval-mcp = "adversarial_eval_mcp.server:main"
```

Remove the old `[project.scripts]` entry for `adversarial`. Keep the Ruff
config, pytest config, and pre-commit settings — just update paths from
`adversarial_workflow` to `adversarial_eval_mcp`.

### 4. Create the evaluator YAML directory

```
evaluators/
├── argument-strength/
│   └── evaluator.yml
├── clarity-concision/
│   └── evaluator.yml
├── factual-accuracy/
│   └── evaluator.yml
└── structure-flow/
    └── evaluator.yml
```

Each evaluator YAML follows this schema:

```yaml
name: <evaluator-name>
description: <one-line description>
category: <reasoning|style|accuracy|structure|domain>

model: <model-id>          # e.g. claude-sonnet-4-6, gemini-2.5-flash
api_key_env: <env-var>     # e.g. ANTHROPIC_API_KEY, GEMINI_API_KEY
timeout: <seconds>         # default 120
max_content_tokens: <int>  # warn threshold, e.g. 30000

verdicts:
  approve: [APPROVED, ...]
  revise: [NEEDS_REVISION, ...]
  reject: [REJECTED, ...]

prompt: |
  <evaluation prompt with {content} and {context} placeholders>
```

#### Evaluator 1: argument-strength

```yaml
name: argument-strength
description: Evaluate logical coherence, evidence quality, and argument structure
category: reasoning

model: claude-sonnet-4-6
api_key_env: ANTHROPIC_API_KEY
timeout: 120
max_content_tokens: 30000

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

  Begin with a single-word verdict on its own line: APPROVED, NEEDS_REVISION, or REJECTED.

  Then provide:

  ### Strengths
  - (bullet list)

  ### Issues
  - (numbered list with specific locations and quotes from the text)

  ### Recommendations
  - (actionable suggestions for improvement)
```

#### Evaluator 2: clarity-concision

```yaml
name: clarity-concision
description: Assess readability, concision, and audience-appropriateness
category: style

model: gemini-2.5-flash
api_key_env: GEMINI_API_KEY
timeout: 90
max_content_tokens: 40000

verdicts:
  approve: [APPROVED, CLEAR, READABLE]
  revise: [NEEDS_REVISION, VERBOSE, UNCLEAR]
  reject: [REJECTED, INCOMPREHENSIBLE]

prompt: |
  You are a writing editor evaluating a piece of text for clarity and concision.

  {context}

  ## Content to Evaluate

  {content}

  ## Evaluation Criteria

  1. **Sentence clarity**: Can each sentence be understood on first reading?
     Flag any that require re-reading.
  2. **Concision**: Are there unnecessary words, redundant phrases, or filler?
     Quote specific examples.
  3. **Audience fit**: Is the vocabulary and tone appropriate for the stated
     audience? (If no audience is specified, assume an educated general reader.)
  4. **Jargon handling**: Is technical terminology explained or used
     appropriately?
  5. **Paragraph focus**: Does each paragraph have a clear point?

  ## Response Format

  Begin with a single-word verdict on its own line: APPROVED, NEEDS_REVISION, or REJECTED.

  Then provide:

  ### Strengths
  - (bullet list)

  ### Issues
  - (numbered list, quote the problematic passage and suggest a revision)

  ### Recommendations
  - (overall suggestions)
```

#### Evaluator 3: factual-accuracy

```yaml
name: factual-accuracy
description: Check claims for accuracy, source quality, and appropriate hedging
category: accuracy

model: claude-sonnet-4-6
api_key_env: ANTHROPIC_API_KEY
timeout: 150
max_content_tokens: 30000

verdicts:
  approve: [APPROVED, ACCURATE, VERIFIED]
  revise: [NEEDS_REVISION, QUESTIONABLE, CHECK_SOURCES]
  reject: [REJECTED, INACCURATE, MISLEADING]

prompt: |
  You are a fact-checker evaluating a piece of writing for factual accuracy.

  {context}

  ## Content to Evaluate

  {content}

  ## Evaluation Criteria

  1. **Factual claims**: Identify all factual claims. For each, assess whether
     it is accurate, plausible but unverifiable, or likely incorrect. If you
     are uncertain, say so explicitly.
  2. **Source quality**: Are sources cited? Are they appropriate (primary vs.
     secondary, recency, authority)?
  3. **Hedging**: Are uncertain claims appropriately hedged? Are confident
     claims warranted?
  4. **Omissions**: Are there important facts or context missing that would
     change the reader's understanding?
  5. **Numerical accuracy**: Check any statistics, dates, or quantities
     for plausibility.

  ## Important

  Do NOT fabricate corrections. If you cannot verify a claim, say
  "Unable to verify: [claim]" rather than asserting it is wrong.

  ## Response Format

  Begin with a single-word verdict on its own line: APPROVED, NEEDS_REVISION, or REJECTED.

  Then provide:

  ### Verified Claims
  - (claims you can confirm as accurate)

  ### Flagged Claims
  - (claims that need checking, with your concern and confidence level)

  ### Recommendations
  - (suggestions for strengthening factual basis)
```

#### Evaluator 4: structure-flow

```yaml
name: structure-flow
description: Evaluate document organization, transitions, and narrative arc
category: structure

model: gemini-2.5-flash
api_key_env: GEMINI_API_KEY
timeout: 90
max_content_tokens: 40000

verdicts:
  approve: [APPROVED, WELL_STRUCTURED, COHERENT]
  revise: [NEEDS_REVISION, DISJOINTED, RESTRUCTURE]
  reject: [REJECTED, INCOHERENT, NO_STRUCTURE]

prompt: |
  You are a structural editor evaluating the organization and flow of a document.

  {context}

  ## Content to Evaluate

  {content}

  ## Evaluation Criteria

  1. **Overall structure**: Is there a clear introduction, body, and conclusion?
     Does the structure serve the content's purpose?
  2. **Section ordering**: Are sections in a logical sequence? Would reordering
     improve comprehension?
  3. **Transitions**: Do paragraphs and sections connect smoothly? Flag any
     jarring jumps.
  4. **Narrative arc**: Does the document build toward its conclusion?
     Is there a sense of progression?
  5. **Balance**: Are sections proportionate to their importance? Is any
     section too long or too short relative to the others?

  ## Response Format

  Begin with a single-word verdict on its own line: APPROVED, NEEDS_REVISION, or REJECTED.

  Then provide:

  ### Structure Map
  - (outline the document's current structure with brief notes on each section)

  ### Issues
  - (numbered list of structural problems)

  ### Suggested Restructure
  - (if applicable, propose an alternative ordering or organization)
```

### 5. Implement the Python package

#### `adversarial_eval_mcp/types.py`

Define these Pydantic models:

```python
from pydantic import BaseModel

class EvaluatorConfig(BaseModel):
    name: str
    description: str
    category: str
    model: str
    api_key_env: str
    timeout: int = 120
    max_content_tokens: int = 30000
    verdicts: dict[str, list[str]]  # {"approve": [...], "revise": [...], "reject": [...]}
    prompt: str

class EvaluatorInfo(BaseModel):
    """Returned by list_evaluators."""
    name: str
    description: str
    model: str
    category: str

class Verdict(BaseModel):
    evaluator: str
    model: str
    verdict: str           # Normalized: APPROVED | NEEDS_REVISION | REJECTED
    confidence: str        # high | medium | low (extracted or default "medium")
    findings: str          # Full evaluator response text
    token_usage: dict      # {"input": N, "output": N} if available
    content_hash: str      # SHA-256 of evaluated content
    timestamp: str         # ISO 8601
```

#### `adversarial_eval_mcp/api_client.py`

Implement a provider registry pattern:

```python
class ApiProvider:
    """Base class for API providers."""
    async def complete(self, model: str, prompt: str, timeout: int) -> tuple[str, dict]:
        """Returns (response_text, usage_dict)."""
        raise NotImplementedError

class AnthropicProvider(ApiProvider):
    """Calls Anthropic API using the anthropic SDK."""
    ...

class GoogleProvider(ApiProvider):
    """Calls Google Generative AI API using google-genai SDK."""
    ...

# Registry maps api_key_env patterns to providers
PROVIDERS = {
    "ANTHROPIC_API_KEY": AnthropicProvider,
    "GEMINI_API_KEY": GoogleProvider,
}

async def call_evaluator(config: EvaluatorConfig, prompt: str) -> tuple[str, dict]:
    """Dispatch to the correct provider based on config.api_key_env."""
    ...
```

The provider interface should make adding OpenAI later a single new class.

#### `adversarial_eval_mcp/evaluator.py`

Core logic:

```python
import yaml
from pathlib import Path

def load_evaluators(evaluators_dir: Path) -> dict[str, EvaluatorConfig]:
    """Scan evaluators/ directory, parse YAMLs, return name->config map."""
    ...

def build_prompt(config: EvaluatorConfig, content: str, context: str = "") -> str:
    """Substitute {content} and {context} into the evaluator prompt."""
    ...

def estimate_tokens(text: str) -> int:
    """Simple heuristic: len(text) / 4."""
    return len(text) // 4

def parse_verdict(config: EvaluatorConfig, response: str) -> tuple[str, str]:
    """Extract normalized verdict and confidence from evaluator response.
    Returns (verdict, confidence) where verdict is APPROVED|NEEDS_REVISION|REJECTED."""
    ...
```

#### `adversarial_eval_mcp/logger.py`

Append-only JSONL log:

```python
import json
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_LOG_DIR = Path.home() / ".adversarial-eval-mcp"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "evaluations.jsonl"

def log_evaluation(verdict: Verdict, log_file: Path = DEFAULT_LOG_FILE) -> None:
    """Append a verdict to the JSONL log."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": verdict.timestamp,
        "evaluator": verdict.evaluator,
        "model": verdict.model,
        "verdict": verdict.verdict,
        "content_hash": verdict.content_hash,
        "token_usage": verdict.token_usage,
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

#### `adversarial_eval_mcp/server.py`

MCP server with 3 tools:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("adversarial-eval-mcp")

# On startup: load evaluators from evaluators/ directory
# Register 3 tools: evaluate, evaluate_file, list_evaluators

# evaluate: takes content, evaluator name, optional context
#   1. Look up evaluator config
#   2. Estimate tokens, include warning in response if over limit
#   3. Build prompt with content + context
#   4. Call API via api_client
#   5. Parse verdict from response
#   6. Log to JSONL
#   7. Return Verdict as JSON

# evaluate_file: takes file_path, evaluator name, optional context
#   1. Read file
#   2. Delegate to evaluate logic

# list_evaluators: no params
#   1. Return list of EvaluatorInfo objects

def main():
    """Entry point."""
    import asyncio
    asyncio.run(run_server())

async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
```

### 6. Write tests

Create minimal but real tests:

```
tests/
├── conftest.py              # Fixtures: sample evaluator config, mock API responses
├── test_evaluator.py        # load_evaluators, build_prompt, estimate_tokens, parse_verdict
├── test_api_client.py       # Provider registry, dispatch logic (mocked API calls)
├── test_logger.py           # JSONL append, file creation
└── test_types.py            # Pydantic model validation
```

Focus on:
- `test_evaluator.py`: Loading YAMLs from the `evaluators/` directory, placeholder
  substitution, verdict parsing for all three tiers, token estimation
- `test_api_client.py`: Provider selection based on `api_key_env`, mock API calls
- `test_logger.py`: JSONL append creates dir and file, entries are valid JSON

### 7. Clean up starter kit artifacts

**Delete** (these are starter-kit / adversarial-workflow specific):
- `adversarial_workflow/` (entire old package, if rename didn't handle it)
- `.adversarial/` (code evaluation system — not needed)
- `agents/launch`, `agents/onboarding`, `agents/preflight` (starter kit launchers)
- `setup.py` (use pyproject.toml only)
- `SETUP.md`, `QUICK_START.md`, `UPGRADE.md`, `AGENT_INTEGRATION.md` (starter kit docs)
- `delegation/tasks/` contents (keep the folder structure, clear the task files)
- `.serena/` (not needed for this project)

**Keep and update**:
- `.claude/agents/` — trim to relevant agents (planner, feature-developer, test-runner, code-reviewer)
- `.claude/settings.json` — update permissions for the new project
- `.github/workflows/` — update CI to run the new package's tests
- `CLAUDE.md` — rewrite for this project
- `README.md` — rewrite based on the spec
- `.pre-commit-config.yaml` — keep, update paths
- `docs/` — clear and add the spec as `docs/DESIGN.md`
- `tests/` — replace with new tests

### 8. Create .env.example

```
# Anthropic API key (for argument-strength, factual-accuracy evaluators)
ANTHROPIC_API_KEY=

# Google Gemini API key (for clarity-concision, structure-flow evaluators)
GEMINI_API_KEY=

# Optional: custom log file path (default: ~/.adversarial-eval-mcp/evaluations.jsonl)
# EVAL_LOG_FILE=
```

### 9. Create MCP registration snippet

Document how to register in `~/.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "adversarial-eval": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/adversarial-eval-mcp", "adversarial-eval-mcp"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-...",
        "GEMINI_API_KEY": "..."
      }
    }
  }
}
```

### 10. Commit and push

After all changes are in place and tests pass:

```bash
git add -A
git commit -m "feat: Initial scaffold — MCP server for content evaluation

Transform agentive-starter-kit into adversarial-eval-mcp.
Python MCP server with 3 tools (evaluate, evaluate_file, list_evaluators),
4 content evaluators, JSONL audit logging, and provider registry pattern."
git push origin main
```

### Summary of what you're building

A **Python MCP server** that:
1. Loads content evaluator configs from YAML files on startup
2. Exposes `evaluate`, `evaluate_file`, and `list_evaluators` as MCP tools
3. Calls Anthropic or Google APIs directly (no aider)
4. Parses structured verdicts (APPROVED / NEEDS_REVISION / REJECTED)
5. Logs every evaluation to a local JSONL file
6. Warns when content exceeds an evaluator's token limit

The primary consumer is a **Dispatch agent** that calls the MCP tools to evaluate
research writing before sending it to reMarkable or other destinations.
