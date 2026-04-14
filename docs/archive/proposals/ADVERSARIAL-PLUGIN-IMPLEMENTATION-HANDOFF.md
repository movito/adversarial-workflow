# Implementation Handoff: Plugin Architecture for adversarial-workflow

**From**: ombruk-idrettsbygg project (planner)
**To**: adversarial-workflow developer agent
**Date**: 2026-01-21
**Target Version**: v0.6.0

---

## Executive Summary

Implement a plugin architecture that allows projects to define custom evaluators in `.adversarial/evaluators/*.yml` files. The CLI should auto-discover these and register them as subcommands alongside built-in evaluators.

**Why**: We built "Athena" (a knowledge evaluator using Gemini 2.5 Pro) by modifying the installed package directly. This works but breaks on upgrade. A plugin architecture makes custom evaluators upgrade-safe and shareable.

**Validation**: Athena has been in production use - it correctly evaluates knowledge/research tasks where GPT-4o gives irrelevant code-focused feedback.

---

## What Success Looks Like

After implementation:

```bash
# List shows both built-in and local evaluators
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

# Local evaluator works like built-in
adversarial athena task-file.md
# Uses config from .adversarial/evaluators/athena.yml
# Outputs to .adversarial/logs/<task>-KNOWLEDGE-EVALUATION.md
```

---

## Implementation Steps

### Step 1: Define the YAML Schema

Create evaluator definition format. Proposed schema:

```yaml
# .adversarial/evaluators/athena.yml
name: athena
description: Knowledge evaluation using Gemini 2.5 Pro
version: 1.0.0

# Model configuration
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY        # Environment variable name
fallback_model: null                # Optional fallback

# Output configuration
output_suffix: KNOWLEDGE-EVALUATION # Creates <task>-KNOWLEDGE-EVALUATION.md
log_prefix: "ATHENA"                # For console output

# Optional aliases (register as additional subcommands)
aliases:
  - knowledge

# The evaluation prompt (full prompt template)
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
```

### Step 2: Implement Evaluator Discovery

Add function to discover evaluators from both built-in and local sources:

```python
# In adversarial_workflow/evaluators.py (new file) or cli.py

from pathlib import Path
import yaml
from typing import Dict, Any, Optional

BUILTIN_EVALUATORS = {
    "evaluate": {
        "type": "builtin",
        "description": "Plan evaluation (GPT-4o)",
        "handler": "evaluate_plan",
    },
    "proofread": {
        "type": "builtin",
        "description": "Teaching content review (GPT-4o)",
        "handler": "proofread_content",
    },
    "review": {
        "type": "builtin",
        "description": "Code review (GPT-4o)",
        "handler": "review_code",
    },
}

def discover_local_evaluators(base_path: Path = None) -> Dict[str, Any]:
    """Discover evaluators defined in .adversarial/evaluators/*.yml"""
    if base_path is None:
        base_path = Path.cwd()

    evaluators = {}
    local_dir = base_path / ".adversarial" / "evaluators"

    if not local_dir.exists():
        return evaluators

    for yml_file in local_dir.glob("*.yml"):
        try:
            config = yaml.safe_load(yml_file.read_text())
            name = config.get("name")

            if not name:
                print(f"Warning: {yml_file} missing 'name' field, skipping")
                continue

            evaluators[name] = {
                "type": "local",
                "config_file": yml_file,
                "config": config,
                "description": config.get("description", "Local evaluator"),
            }

            # Register aliases
            for alias in config.get("aliases", []):
                evaluators[alias] = {
                    **evaluators[name],
                    "is_alias": True,
                    "alias_of": name,
                }

        except yaml.YAMLError as e:
            print(f"Warning: Could not parse {yml_file}: {e}")
        except Exception as e:
            print(f"Warning: Could not load {yml_file}: {e}")

    return evaluators

def get_all_evaluators() -> Dict[str, Any]:
    """Get all available evaluators (built-in + local)"""
    evaluators = BUILTIN_EVALUATORS.copy()
    evaluators.update(discover_local_evaluators())
    return evaluators
```

### Step 3: Implement Local Evaluator Runner

Add function to run a locally-defined evaluator:

```python
import os
import subprocess
from datetime import datetime

def run_local_evaluator(config: dict, file_path: str, verbose: bool = False) -> int:
    """Run a locally-defined evaluator via aider."""

    # Extract config
    model = config.get("model", "gpt-4o")
    api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
    prompt = config.get("prompt", "")
    output_suffix = config.get("output_suffix", "EVALUATION")
    log_prefix = config.get("log_prefix", "EVALUATOR")

    # Validate API key
    api_key = os.environ.get(api_key_env)
    if not api_key:
        print(f"Error: {api_key_env} not set in environment")
        print(f"Set it in .env or export {api_key_env}=your-key")
        return 1

    # Validate input file
    input_path = Path(file_path)
    if not input_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    # Prepare output path
    logs_dir = Path(".adversarial/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    task_name = input_path.stem
    output_file = logs_dir / f"{task_name}-{output_suffix}.md"

    # Read input file
    file_content = input_path.read_text()

    # Build full prompt
    full_prompt = f"""{prompt}

---

## Document to Evaluate

**File**: {file_path}

{file_content}
"""

    # Create temp file for prompt
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(full_prompt)
        prompt_file = f.name

    try:
        print(f"{log_prefix}: Evaluating {file_path}")
        print(f"{log_prefix}: Using model {model}")

        # Run aider
        cmd = [
            "aider",
            "--model", model,
            "--yes",
            "--no-git",
            "--no-auto-commits",
            "--message-file", prompt_file,
            "--read", file_path,
        ]

        if verbose:
            print(f"{log_prefix}: Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, api_key_env: api_key}
        )

        # Extract evaluation from aider output
        # (This part may need adjustment based on how aider outputs)
        evaluation_output = result.stdout

        # Write output
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"""# {output_suffix.replace('-', ' ').title()}

**Source**: {file_path}
**Evaluator**: {config.get('name', 'local')}
**Model**: {model}
**Generated**: {timestamp}

---

"""
        output_file.write_text(header + evaluation_output)

        print(f"{log_prefix}: Output written to {output_file}")
        return 0

    finally:
        # Cleanup temp file
        Path(prompt_file).unlink(missing_ok=True)
```

### Step 4: Register Dynamic CLI Subcommands

Modify the CLI setup to dynamically register discovered evaluators:

```python
# In cli.py - modify the CLI setup

import click

def create_local_evaluator_command(name: str, config: dict):
    """Create a Click command for a local evaluator."""

    @click.command(name=name, help=config.get("description", "Local evaluator"))
    @click.argument("file_path", type=click.Path(exists=True))
    @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
    def cmd(file_path, verbose):
        return run_local_evaluator(config["config"], file_path, verbose)

    return cmd

def setup_cli():
    """Set up CLI with all evaluators."""

    @click.group()
    @click.version_option()
    def cli():
        """Adversarial Workflow - Multi-stage AI code review"""
        pass

    # Add built-in commands
    # ... existing setup ...

    # Discover and add local evaluators
    local_evaluators = discover_local_evaluators()
    for name, eval_config in local_evaluators.items():
        if eval_config.get("is_alias"):
            continue  # Skip aliases, they'll be handled separately

        cmd = create_local_evaluator_command(name, eval_config)
        cli.add_command(cmd)

        # Add aliases
        for alias in eval_config.get("config", {}).get("aliases", []):
            alias_cmd = create_local_evaluator_command(alias, eval_config)
            cli.add_command(alias_cmd)

    return cli
```

### Step 5: Add list-evaluators Command

```python
@click.command("list-evaluators")
def list_evaluators():
    """List all available evaluators."""

    evaluators = get_all_evaluators()

    # Separate built-in and local
    builtin = {k: v for k, v in evaluators.items()
               if v.get("type") == "builtin"}
    local = {k: v for k, v in evaluators.items()
             if v.get("type") == "local" and not v.get("is_alias")}

    click.echo("Built-in:")
    for name, config in sorted(builtin.items()):
        click.echo(f"  {name:15} - {config.get('description', '')}")

    if local:
        click.echo("\nLocal (.adversarial/evaluators/):")
        for name, config in sorted(local.items()):
            aliases = config.get("config", {}).get("aliases", [])
            alias_str = f" (aliases: {', '.join(aliases)})" if aliases else ""
            click.echo(f"  {name:15} - {config.get('description', '')}{alias_str}")
    else:
        click.echo("\nNo local evaluators found.")
        click.echo("Create .adversarial/evaluators/*.yml to add custom evaluators.")
```

---

## Testing Strategy

### Test 1: Discovery

```bash
# Create test evaluator
mkdir -p .adversarial/evaluators
cat > .adversarial/evaluators/test.yml << 'EOF'
name: test
description: Test evaluator
model: gpt-4o-mini
prompt: "Just say 'Hello, this is a test'"
EOF

# Verify discovery
adversarial list-evaluators
# Should show "test" under Local
```

### Test 2: Execution

```bash
# Run test evaluator
echo "# Test Document" > /tmp/test.md
adversarial test /tmp/test.md
# Should create .adversarial/logs/test-EVALUATION.md
```

### Test 3: Real Evaluator (Athena)

Use the full Athena config from ombruk project to validate:

```bash
# Copy athena.yml to .adversarial/evaluators/
# Run against a knowledge task
adversarial athena some-research-task.md
# Should produce knowledge-focused evaluation
```

---

## Migration Notes

### Backward Compatibility

- All existing commands must continue to work unchanged
- `adversarial evaluate` stays as built-in GPT-4o evaluator
- No changes to existing config.yml behavior

### Current Athena Implementation

The current Athena was added by directly modifying the installed package. After this plugin architecture ships:

1. Remove hardcoded Athena from package
2. Projects use `.adversarial/evaluators/athena.yml` instead
3. Athena.yml can be distributed via starter-kit or copied between projects

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `adversarial_workflow/evaluators.py` | Create | Evaluator discovery and runner |
| `adversarial_workflow/cli.py` | Modify | Dynamic command registration |
| `README.md` | Update | Document plugin system |
| `docs/CUSTOM_EVALUATORS.md` | Create | Full documentation |

---

## Acceptance Criteria

1. **Discovery works**: `adversarial list-evaluators` shows local evaluators
2. **Execution works**: `adversarial <local-name> file.md` runs the evaluator
3. **Aliases work**: Defined aliases register as separate commands
4. **Backward compatible**: All existing commands unchanged
5. **Error handling**: Missing API key, bad YAML, missing model all handled gracefully
6. **Documentation**: README and docs updated

---

## Reference: Full Athena YAML

This is the complete Athena evaluator config to use for testing:

```yaml
name: athena
description: Knowledge evaluation using Gemini 2.5 Pro (research, documentation)
version: 1.0.0

model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY

output_suffix: KNOWLEDGE-EVALUATION
log_prefix: ATHENA

aliases:
  - knowledge

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

  ```
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
  ```

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

---

## Questions for Implementation

1. **How is aider currently invoked?** - Need to match existing patterns
2. **Where does the CLI entry point live?** - cli.py or __main__.py?
3. **Is Click used or argparse?** - Code samples assume Click
4. **Any existing plugin/extension patterns?** - Build on what exists

---

**Document Version**: 1.0.0
**Created**: 2026-01-21
**Source Project**: ombruk-idrettsbygg
