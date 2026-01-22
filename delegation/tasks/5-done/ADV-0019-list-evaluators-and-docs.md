# ADV-0019: List-Evaluators Command and Documentation

**Status**: Done
**Priority**: Medium
**Estimated Effort**: 2-3 hours
**Target Version**: v0.6.0
**Parent Epic**: ADV-0013
**Depends On**: ADV-0015, ADV-0016, ADV-0018
**Branch**: `feature/plugin-architecture`

## Summary

Add the `adversarial list-evaluators` command and update documentation for the plugin architecture. This is the final task in the v0.6.0 plugin implementation.

## Requirements

### list-evaluators Command

```text
$ adversarial list-evaluators

Built-in Evaluators:
  evaluate       Plan evaluation (GPT-4o)
  proofread      Teaching content review (GPT-4o)
  review         Code review (GPT-4o)

Local Evaluators (.adversarial/evaluators/):
  athena         Knowledge evaluation (Gemini 2.5 Pro)
    aliases: knowledge, research
    model: gemini-2.5-pro
    version: 1.0.0

No local evaluators? Create .adversarial/evaluators/*.yml to add custom evaluators.
See: https://github.com/movito/adversarial-workflow#custom-evaluators
```

### Implementation

```python
# In cli.py

def list_evaluators() -> int:
    """List all available evaluators."""
    from adversarial_workflow.evaluators import (
        get_all_evaluators,
        BUILTIN_EVALUATORS,
        discover_local_evaluators,
    )

    # Get all evaluators
    all_evaluators = get_all_evaluators()
    local_evaluators = discover_local_evaluators()

    # Print built-in
    print(f"{BOLD}Built-in Evaluators:{RESET}")
    for name, config in sorted(BUILTIN_EVALUATORS.items()):
        print(f"  {name:14} {config.description}")

    print()

    # Print local
    if local_evaluators:
        print(f"{BOLD}Local Evaluators{RESET} (.adversarial/evaluators/):")

        # Group by primary name (skip aliases)
        seen_configs = set()
        for name, config in sorted(local_evaluators.items()):
            if id(config) in seen_configs:
                continue
            seen_configs.add(id(config))

            print(f"  {config.name:14} {config.description}")
            if config.aliases:
                print(f"    aliases: {', '.join(config.aliases)}")
            print(f"    model: {config.model}")
            if config.version != "1.0.0":
                print(f"    version: {config.version}")
    else:
        print(f"{GRAY}No local evaluators found.{RESET}")
        print()
        print("Create .adversarial/evaluators/*.yml to add custom evaluators.")
        print("See: https://github.com/movito/adversarial-workflow#custom-evaluators")

    return 0


# Register in main()
subparsers.add_parser(
    "list-evaluators",
    help="List all available evaluators (built-in and local)"
)

# In command dispatch
elif args.command == "list-evaluators":
    return list_evaluators()
```

### Documentation Updates

#### README.md - Add Custom Evaluators Section

```markdown
## Custom Evaluators

Starting with v0.6.0, you can define project-specific evaluators without modifying the package.

### Creating a Custom Evaluator

1. Create the evaluators directory:
   ```bash
   mkdir -p .adversarial/evaluators
   ```

2. Create a YAML definition:
   ```yaml
   # .adversarial/evaluators/athena.yml
   name: athena
   description: Knowledge evaluation using Gemini 2.5 Pro
   model: gemini-2.5-pro
   api_key_env: GEMINI_API_KEY
   output_suffix: KNOWLEDGE-EVALUATION
   prompt: |
     You are Athena, a knowledge evaluation specialist...

   # Optional
   aliases:
     - knowledge
   ```

3. Use it like any built-in evaluator:
   ```bash
   adversarial athena docs/research-plan.md
   ```

### Evaluator YAML Schema

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Command name |
| `description` | Yes | Help text shown in CLI |
| `model` | Yes | Model to use (e.g., `gpt-4o`, `gemini-2.5-pro`) |
| `api_key_env` | Yes | Environment variable for API key |
| `output_suffix` | Yes | Log file suffix (e.g., `KNOWLEDGE-EVAL`) |
| `prompt` | Yes | The evaluation prompt |
| `aliases` | No | Alternative command names |
| `log_prefix` | No | CLI output prefix |
| `fallback_model` | No | Fallback model if primary fails |
| `version` | No | Evaluator version (default: 1.0.0) |

### Listing Available Evaluators

```bash
adversarial list-evaluators
```

### Example: Athena Knowledge Evaluator

See [docs/examples/athena.yml](docs/examples/athena.yml) for a complete example of a knowledge-focused evaluator using Gemini 2.5 Pro.
```

#### Create docs/CUSTOM_EVALUATORS.md

Full documentation for plugin architecture:

```markdown
# Custom Evaluators

This guide explains how to create and use custom evaluators with adversarial-workflow.

## Overview

Custom evaluators allow you to:
- Use different AI models (Gemini, Claude, local models)
- Create domain-specific evaluation criteria
- Share evaluators across projects

## Quick Start

1. Create `.adversarial/evaluators/my-evaluator.yml`
2. Define your evaluator configuration
3. Run: `adversarial my-evaluator file.md`

## Full Schema Reference

[Include complete schema documentation]

## Examples

### Legal Document Evaluator
[Example for legal review]

### Security Audit Evaluator
[Example for security review]

### Teaching Content Evaluator
[Example for educational content]

## Troubleshooting

### API Key Issues
...

### Model Compatibility
...
```

#### Create docs/examples/athena.yml

```yaml
# Athena - Knowledge Evaluation Specialist
#
# Use for research, documentation, and knowledge base tasks.
# This evaluator focuses on information quality rather than code quality.
#
# Requires: GEMINI_API_KEY environment variable
# Usage: adversarial athena docs/research.md

name: athena
description: Knowledge evaluation using Gemini 2.5 Pro
version: 1.0.0

model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY

output_suffix: KNOWLEDGE-EVALUATION
log_prefix: "🦉 ATHENA"

aliases:
  - knowledge
  - research

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

  ## What You Do NOT Evaluate
  - Error handling (code concept)
  - File names and function names
  - Test coverage
  - Implementation risk
  - Code architecture

  ## What You Focus On
  - Are sources trustworthy?
  - Can the reader verify claims?
  - Is scope realistic?
  - Can this be maintained over time?
  - Does it fit the audience?
  - Is it practically useful?
```

### CHANGELOG.md Update

```markdown
## [0.6.0] - Unreleased

### Added
- **Plugin Architecture**: Define custom evaluators in `.adversarial/evaluators/*.yml`
- `adversarial list-evaluators` command to show available evaluators
- Support for model aliases (e.g., `athena` and `knowledge` for same evaluator)
- Fallback model support for resilient evaluation
- Full documentation for custom evaluator creation

### Changed
- Refactored evaluator execution into `adversarial_workflow.evaluators` module
- Simplified built-in evaluator code (~400 lines removed)

### Technical
- New `EvaluatorConfig` dataclass for evaluator configuration
- Generic `run_evaluator()` function for all evaluator types
- Dynamic CLI subparser registration
```

## Testing Requirements

### list-evaluators Tests

```python
def test_list_evaluators_no_local(capsys):
    """Shows built-in only when no local evaluators."""
    result = list_evaluators()
    assert result == 0
    output = capsys.readouterr().out
    assert "Built-in Evaluators" in output
    assert "evaluate" in output
    assert "No local evaluators" in output

def test_list_evaluators_with_local(tmp_path, monkeypatch, capsys):
    """Shows local evaluators when present."""
    # Setup local evaluator
    eval_dir = tmp_path / ".adversarial" / "evaluators"
    eval_dir.mkdir(parents=True)
    (eval_dir / "test.yml").write_text("""
name: test
description: Test eval
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Test
output_suffix: TEST
aliases:
  - t
""")

    monkeypatch.chdir(tmp_path)
    result = list_evaluators()

    output = capsys.readouterr().out
    assert "Local Evaluators" in output
    assert "test" in output
    assert "aliases: t" in output
```

## Acceptance Criteria

- [ ] `adversarial list-evaluators` shows built-in evaluators
- [ ] `adversarial list-evaluators` shows local evaluators with details
- [ ] Helpful message when no local evaluators exist
- [ ] README.md updated with Custom Evaluators section
- [ ] docs/CUSTOM_EVALUATORS.md created with full documentation
- [ ] docs/examples/athena.yml created as reference
- [ ] CHANGELOG.md updated for v0.6.0
- [ ] Unit tests for list-evaluators command
- [ ] All existing tests pass

## References

- Parent Epic: ADV-0013-plugin-architecture-epic.md
- Depends On: ADV-0015, ADV-0016, ADV-0018
- Proposal: docs/proposals/ADVERSARIAL-PLUGIN-IMPLEMENTATION-HANDOFF.md
