# Proposal: Plugin Architecture for adversarial-workflow

**Author**: ombruk-idrettsbygg project
**Date**: 2026-01-14
**Status**: Proposal
**Target**: adversarial-workflow v0.6+

## Executive Summary

This proposal suggests adding a plugin architecture to adversarial-workflow that allows projects to define custom evaluators without modifying the installed package. This emerged from implementing "Athena" - a knowledge evaluator using Gemini 2.5 Pro.

## Background

### The Problem We Encountered

When implementing OIB-0006 (Athena Knowledge Evaluator), we faced a challenge:

1. **adversarial-workflow** is installed system-wide via pip
2. We needed a new evaluator type (`athena`) with different model and prompt
3. Options were:
   - Modify installed package (breaks on upgrade)
   - Fork the package (maintenance burden)
   - Wait for upstream release (blocks progress)

### What We Built

We successfully added `adversarial athena` by:
1. Modifying the installed CLI directly
2. Adding evaluation logic to the package
3. Creating local documentation

**This works, but isn't sustainable.**

## Proposed Solution: Local Evaluator Definitions

### Concept

Allow projects to define evaluators in `.adversarial/evaluators/*.yml` that the CLI discovers automatically.

### Directory Structure

```
.adversarial/
├── config.yml                 # Existing global config
├── evaluators/                # NEW: Local evaluator definitions
│   ├── athena.yml            # Knowledge evaluator (Gemini)
│   ├── legal-reviewer.yml    # Project-specific evaluator
│   └── security-audit.yml    # Another custom evaluator
├── scripts/                   # Existing scripts (legacy support)
└── logs/                      # Existing logs
```

### Evaluator Definition Format

```yaml
# .adversarial/evaluators/athena.yml
name: athena
description: Knowledge evaluation using Gemini 2.5 Pro
version: 1.0.0

# Model configuration
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
fallback_model: deepseek-r1  # Optional fallback

# Output configuration
output_suffix: KNOWLEDGE-EVALUATION
log_prefix: "🦉 ATHENA"

# Evaluation focus (for documentation/help text)
focus:
  - source_validity
  - verifiability
  - maintainability
  - audience_fit
  - practical_applicability

# What this evaluator explicitly ignores
ignores:
  - error_handling
  - file_names
  - test_coverage
  - code_architecture

# The prompt template
prompt: |
  You are Athena, a knowledge evaluation specialist.

  ## Your Role
  You evaluate knowledge work - research, documentation, knowledge bases.
  You do NOT focus on code concepts like error handling or test coverage.

  ## Evaluation Criteria

  ### 1. SOURCE VALIDITY
  - Are sources authoritative and reliable?
  - Is the source hierarchy correct (primary > secondary > tertiary)?
  - Is there clear distinction between facts and interpretation?

  ### 2. VERIFIABILITY
  - Can claims be traced to primary sources?
  - Are references complete and correct?
  - Can information be independently verified?

  ### 3. SCOPE AND BOUNDARIES
  - Is the scope realistic for estimated time?
  - Are important areas missing?
  - Are boundaries clearly communicated?

  ### 4. MAINTAINABILITY
  - Can content be kept updated over time?
  - Is there a revision strategy?
  - Is dating and versioning in place?

  ### 5. AUDIENCE FIT
  - Is content written for the right audience?
  - Is jargon explained where necessary?
  - Is complexity level appropriate?

  ### 6. PRACTICAL APPLICABILITY
  - Can information be used to make decisions?
  - Are there concrete examples?
  - Are processes and steps clear?

  ## Output Format

  ## Athena Evaluation Summary

  **Document**: [filename]
  **Evaluated**: [date]
  **Verdict**: [APPROVED / NEEDS_REVISION / REJECT]
  **Confidence**: [HIGH / MEDIUM / LOW]

  ## Strengths
  - [What the document does well]

  ## Concerns
  - [CRITICAL] [Source problems, factual errors]
  - [HIGH] [Missing coverage, unclear scope]
  - [MEDIUM] [Maintenance challenges]
  - [LOW] [Formulations, structure]

  ## Recommendations
  1. [Concrete, actionable improvement]
  2. [Alternative approach]

  ## Approval Conditions
  [What's needed for approval if NEEDS_REVISION]

# Optional: aliases for this evaluator
aliases:
  - knowledge
  - research
```

### CLI Behavior

```bash
# Discovers local evaluators automatically
adversarial athena file.md          # Uses .adversarial/evaluators/athena.yml
adversarial knowledge file.md       # Alias works too
adversarial evaluate file.md        # Built-in (GPT-4o)

# List available evaluators
adversarial list-evaluators
# Output:
#   Built-in:
#     evaluate    - Plan evaluation (GPT-4o)
#     proofread   - Teaching content review (GPT-4o)
#     review      - Code review (GPT-4o)
#
#   Local (.adversarial/evaluators/):
#     athena      - Knowledge evaluation using Gemini 2.5 Pro
#     knowledge   - (alias for athena)

# Help shows local evaluators
adversarial --help
# Shows athena in command list with description from yml
```

### Implementation Sketch

```python
# In adversarial_workflow/cli.py

from pathlib import Path
import yaml

BUILTIN_EVALUATORS = {
    "evaluate": {...},
    "proofread": {...},
    "review": {...},
}

def discover_evaluators() -> dict:
    """Discover built-in and local evaluators."""
    evaluators = BUILTIN_EVALUATORS.copy()

    local_dir = Path(".adversarial/evaluators")
    if local_dir.exists():
        for yml_file in local_dir.glob("*.yml"):
            try:
                config = yaml.safe_load(yml_file.read_text())
                name = config.get("name")
                if name:
                    evaluators[name] = {
                        "type": "local",
                        "config_file": yml_file,
                        "config": config,
                    }
                    # Register aliases
                    for alias in config.get("aliases", []):
                        evaluators[alias] = evaluators[name]
            except Exception as e:
                print(f"Warning: Could not load {yml_file}: {e}")

    return evaluators

def run_evaluator(name: str, file_path: str):
    """Run an evaluator by name."""
    evaluators = discover_evaluators()

    if name not in evaluators:
        print(f"Unknown evaluator: {name}")
        print(f"Available: {', '.join(evaluators.keys())}")
        return 1

    eval_config = evaluators[name]

    if eval_config.get("type") == "local":
        return run_local_evaluator(eval_config["config"], file_path)
    else:
        return run_builtin_evaluator(name, file_path)

def run_local_evaluator(config: dict, file_path: str):
    """Run a locally-defined evaluator."""
    model = config["model"]
    api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
    prompt = config["prompt"]
    output_suffix = config.get("output_suffix", "EVALUATION")

    # Check API key
    api_key = os.environ.get(api_key_env)
    if not api_key:
        print(f"Error: {api_key_env} not set in environment")
        return 1

    # Run via aider
    # ... (similar to existing evaluate_plan logic)
```

## Benefits

### For Project Teams

1. **No fork needed** - Define evaluators locally
2. **Upgrade-safe** - Local definitions survive `pip upgrade`
3. **Version controlled** - `.adversarial/evaluators/` commits to git
4. **Shareable** - Copy evaluator definitions between projects
5. **Domain-specific** - Create evaluators for your domain (legal, medical, etc.)

### For adversarial-workflow Maintainers

1. **Reduced feature requests** - Projects can self-serve
2. **Community contributions** - Share evaluator definitions as examples
3. **Cleaner core** - Keep built-in evaluators focused
4. **Easier testing** - Test plugin system separately from evaluators

### For the Ecosystem

1. **Evaluator marketplace** - Share definitions via gists/repos
2. **Best practices emerge** - Community develops patterns
3. **Model diversity** - Easy to try different models per task type

## Migration Path

### Phase 1: Support Local Definitions (v0.6)

- Add evaluator discovery
- Support `.adversarial/evaluators/*.yml`
- Document format
- Keep all built-ins

### Phase 2: Migrate Built-ins to Plugin Format (v0.7)

- Convert `evaluate`, `proofread`, `review` to yml format internally
- Ship as "bundled evaluators"
- Same behavior, cleaner architecture

### Phase 3: Evaluator Registry (v0.8+)

- `adversarial install-evaluator <name>` from community registry
- Version management for evaluators
- Dependency handling (e.g., "requires aider >= 0.85")

## Real-World Validation

This proposal is based on actual implementation experience:

| Aspect | Our Experience |
|--------|----------------|
| **Use case** | Knowledge evaluator (Athena) using Gemini 2.5 Pro |
| **Problem** | Couldn't add without modifying installed package |
| **Solution** | Modified installed CLI (not ideal) |
| **Result** | Works great, but won't survive upgrades |
| **Validation** | Athena gave APPROVED on task that GPT-4o marked NEEDS_REVISION with irrelevant feedback |

### Comparative Results

```
Task: OIB-0005 (Knowledge base documentation task)

GPT-4o (evaluate):
  Verdict: NEEDS_REVISION
  Focus: "Missing error handling", "edge cases in script"
  Relevance: LOW (code concepts on research task)

Gemini 2.5 Pro (athena):
  Verdict: APPROVED
  Focus: Source validity, maintainability, audience fit
  Relevance: HIGH (knowledge-appropriate feedback)
```

This demonstrates why different evaluators for different task types is valuable.

## Open Questions

1. **Prompt templating** - Should we support variables in prompts (e.g., `{{file_name}}`)?
2. **Validation** - Should we validate yml schema on load?
3. **Inheritance** - Should evaluators be able to extend others?
4. **Secrets** - How to handle API keys in shared evaluator definitions?

## Appendix: Athena Implementation Files

For reference, here are the files we created for Athena:

- `.adversarial/scripts/evaluate_knowledge.sh` - Evaluation script
- `.claude/agents/athena.md` - Agent definition
- `.adversarial/docs/EVALUATION-WORKFLOW.md` - Updated documentation
- `.adversarial/config.yml` - Added `knowledge_evaluator_model`

These would be consolidated into a single `.adversarial/evaluators/athena.yml` with the proposed architecture.

---

**Submitted by**: ombruk-idrettsbygg project
**Contact**: [project maintainer]
**Related**: OIB-0006 task implementation
