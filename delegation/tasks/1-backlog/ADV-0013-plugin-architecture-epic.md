# ADV-0013: Plugin Architecture - Phase 1 (Local Evaluator Definitions)

**Status**: Todo
**Priority**: High
**Estimated Effort**: 3-4 days
**Target Version**: v0.6.0
**Branch**: `feature/plugin-architecture`

## Summary

Implement a plugin architecture that allows projects to define custom evaluators in `.adversarial/evaluators/*.yml` files. The CLI will discover these at runtime and make them available as subcommands alongside built-in evaluators.

## Background

Based on learnings from the ombruk-idrettsbygg project's "Athena" evaluator implementation. Teams need domain-specific evaluators (knowledge/research, legal, security, etc.) without modifying the installed package.

**Reference Document**: See original proposal from ombruk-idrettsbygg project (external)

## Requirements

### Functional Requirements

1. **Evaluator Discovery**
   - Scan `.adversarial/evaluators/*.yml` on CLI startup
   - Parse YAML evaluator definitions
   - Register as CLI subcommands dynamically
   - Support aliases (e.g., `athena` and `knowledge` point to same evaluator)

2. **Evaluator Definition Format**
   ```yaml
   name: athena                    # Required: Command name
   description: Knowledge eval     # Required: Help text
   version: 1.0.0                  # Optional: Evaluator version

   model: gemini-2.5-pro          # Required: Model to use
   api_key_env: GEMINI_API_KEY    # Required: Env var for API key
   fallback_model: deepseek-r1    # Optional: Fallback model

   output_suffix: KNOWLEDGE-EVAL  # Required: Log file suffix
   log_prefix: "🦉 ATHENA"        # Optional: CLI output prefix

   prompt: |                      # Required: The evaluation prompt
     You are Athena...

   aliases:                       # Optional: Alternative command names
     - knowledge
     - research
   ```

3. **CLI Integration**
   - `adversarial <evaluator-name> <file>` - Run any evaluator
   - `adversarial list-evaluators` - List all available evaluators
   - `adversarial --help` shows local evaluators in command list
   - Graceful error handling for invalid YAML definitions

4. **Execution**
   - Read API key from specified environment variable
   - Run via aider with configured model and prompt
   - Write output to `.adversarial/logs/<basename>-<output_suffix>.md`
   - Support same timeout/rate-limit handling as built-in evaluators
   - If primary model fails (API error, rate limit), retry with `fallback_model` if specified
   - Fallback is optional; without it, model failure is final

### Non-Functional Requirements

1. **Backwards Compatible**: Built-in `evaluate`, `proofread`, `review` unchanged
2. **No New Dependencies**: Use existing `pyyaml` (already a dependency)
3. **Fast Discovery**: Evaluator scanning should add <100ms to startup
4. **Clear Errors**: Invalid evaluator definitions show helpful messages

### Security Considerations

1. **Trust Model**: Local `.adversarial/evaluators/` files are trusted, same as `.adversarial/scripts/`
2. **User Responsibility**: Do not clone untrusted repositories and run evaluators without review
3. **Override Warning**: When a local evaluator overrides a built-in, log a warning at startup
4. **Future**: Consider `--no-local-evaluators` flag for restricted environments

## Technical Design

### 1. Refactor: Generic Evaluator Runner

Extract common code from `evaluate()` and `proofread()` into a generic runner:

```python
# adversarial_workflow/evaluators/runner.py

@dataclass
class EvaluatorConfig:
    name: str
    description: str
    model: str
    api_key_env: str
    prompt: str
    output_suffix: str
    log_prefix: str = ""
    fallback_model: str | None = None
    aliases: list[str] = field(default_factory=list)

def run_evaluator(config: EvaluatorConfig, file_path: str) -> int:
    """Generic evaluator runner - handles all common logic."""
    # 1. Validate file exists
    # 2. Load project config
    # 3. Check aider available
    # 4. Pre-flight file size check
    # 5. Check API key from config.api_key_env
    # 6. Generate/run aider command with config.model and config.prompt
    # 7. Handle timeouts, rate limits, platform issues
    # 8. Validate output and return verdict
```

### 2. Evaluator Discovery Module

```python
# adversarial_workflow/evaluators/discovery.py

BUILTIN_EVALUATORS: dict[str, EvaluatorConfig] = {
    "evaluate": EvaluatorConfig(
        name="evaluate",
        description="Plan evaluation (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt=EVALUATE_PROMPT,
        output_suffix="PLAN-EVALUATION",
    ),
    "proofread": EvaluatorConfig(...),
    "review": EvaluatorConfig(...),
}

def discover_local_evaluators() -> dict[str, EvaluatorConfig]:
    """Discover evaluators from .adversarial/evaluators/*.yml"""
    evaluators = {}
    local_dir = Path(".adversarial/evaluators")

    if not local_dir.exists():
        return evaluators

    for yml_file in local_dir.glob("*.yml"):
        try:
            config = parse_evaluator_yaml(yml_file)
            evaluators[config.name] = config
            for alias in config.aliases:
                evaluators[alias] = config
        except (EvaluatorParseError, yaml.YAMLError, TypeError) as e:
            print(f"Warning: Skipping {yml_file}: {e}")

    return evaluators


class EvaluatorParseError(Exception):
    """Raised when evaluator YAML is invalid."""
    pass


def parse_evaluator_yaml(yml_file: Path) -> EvaluatorConfig:
    """Parse a YAML file into an EvaluatorConfig."""
    import yaml  # pyyaml is already a dependency

    data = yaml.safe_load(yml_file.read_text())
    if data is None:
        raise EvaluatorParseError("Empty or invalid YAML file")

    required = ["name", "description", "model", "api_key_env", "prompt", "output_suffix"]
    for field in required:
        if field not in data:
            raise EvaluatorParseError(f"Missing required field: {field}")

    # Normalize aliases to list (handle missing, None, or single string)
    aliases = data.get("aliases")
    if aliases is None:
        data["aliases"] = []
    elif isinstance(aliases, str):
        data["aliases"] = [aliases]  # Convert single string to list
    elif not isinstance(aliases, list):
        raise EvaluatorParseError(f"aliases must be a string or list, got {type(aliases).__name__}")

    # Filter to only known EvaluatorConfig fields
    known_fields = {
        "name", "description", "model", "api_key_env", "prompt",
        "output_suffix", "log_prefix", "fallback_model", "aliases", "version"
    }
    filtered_data = {k: v for k, v in data.items() if k in known_fields}

    return EvaluatorConfig(**filtered_data)

def get_all_evaluators() -> dict[str, EvaluatorConfig]:
    """Get built-in + local evaluators. Local overrides built-in."""
    evaluators = BUILTIN_EVALUATORS.copy()
    local_evals = discover_local_evaluators()

    # Warn about overrides per security requirement
    for name in local_evals:
        if name in BUILTIN_EVALUATORS:
            print(f"Warning: Local evaluator '{name}' overrides built-in evaluator")

    evaluators.update(local_evals)
    return evaluators
```

### 3. CLI Integration

```python
# In main() - dynamic subparser registration

def main():
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(...)

    # Register all evaluators dynamically
    evaluators = get_all_evaluators()
    registered_configs = set()
    for name, config in evaluators.items():
        if id(config) in registered_configs:
            continue  # Skip aliases (same config object)
        registered_configs.add(id(config))

        eval_parser = subparsers.add_parser(
            config.name,
            help=config.description,
            aliases=config.aliases
        )
        eval_parser.add_argument("file", help="File to evaluate")
        eval_parser.set_defaults(evaluator_config=config)

    # ... rest of main()

    if hasattr(args, 'evaluator_config'):
        return run_evaluator(args.evaluator_config, args.file)
```

### 4. New CLI Command: list-evaluators

```text
$ adversarial list-evaluators

Built-in Evaluators:
  evaluate     Plan evaluation (GPT-4o)
  proofread    Teaching content review (GPT-4o)
  review       Code review (GPT-4o)

Local Evaluators (.adversarial/evaluators/):
  athena       Knowledge evaluation (Gemini 2.5 Pro)
    aliases: knowledge, research
```

## File Structure Changes

```text
adversarial_workflow/
├── __init__.py
├── cli.py                    # Simplified, delegates to evaluators
├── __main__.py
├── utils/
│   └── file_splitter.py
├── evaluators/               # NEW module
│   ├── __init__.py
│   ├── runner.py             # Generic evaluator execution
│   ├── discovery.py          # Evaluator discovery
│   ├── config.py             # EvaluatorConfig dataclass
│   └── prompts.py            # Built-in evaluator prompts
└── templates/
    └── ...
```

## Testing Requirements

### Unit Tests

1. `test_evaluator_config_parsing.py`
   - Valid YAML parsing
   - Required field validation
   - Optional field defaults
   - Invalid YAML handling

2. `test_evaluator_discovery.py`
   - Discover from `.adversarial/evaluators/`
   - Handle missing directory
   - Handle invalid files gracefully
   - Alias registration

3. `test_evaluator_runner.py`
   - API key validation
   - File existence checks
   - Timeout handling
   - Output validation

### Integration Tests

1. `test_cli_dynamic_commands.py`
   - Local evaluators appear in `--help`
   - Local evaluators are executable
   - `list-evaluators` shows correct output

2. `test_backwards_compatibility.py`
   - `adversarial evaluate` still works
   - `adversarial proofread` still works
   - `adversarial review` still works

## Migration Notes

- Existing projects continue working (no breaking changes)
- New feature is opt-in: only activated when `.adversarial/evaluators/` exists
- Documentation should include example evaluator definitions

## Acceptance Criteria

- [ ] `.adversarial/evaluators/*.yml` files are discovered on CLI startup
- [ ] Local evaluators appear as subcommands in `adversarial --help`
- [ ] `adversarial <custom-evaluator> <file>` runs the custom evaluator
- [ ] `adversarial list-evaluators` shows built-in and local evaluators
- [ ] Invalid evaluator YAML shows helpful error message
- [ ] All existing tests pass (backwards compatibility)
- [ ] New unit and integration tests added
- [ ] Documentation updated with evaluator definition format

## Open Questions

1. **Prompt templating**: Should we support `{{file_name}}` variables in prompts?
   - Recommendation: Phase 2 feature, keep Phase 1 simple

2. **Schema validation**: How strict should YAML validation be?
   - Recommendation: Validate required fields, warn on unknown fields

3. **Override built-ins**: Should local `evaluate.yml` override built-in?
   - Recommendation: Yes, allows customization without renaming

## References

- Proposal: `ombruk/docs/proposals/ADVERSARIAL-WORKFLOW-PLUGIN-ARCHITECTURE.md`
- Current CLI: `adversarial_workflow/cli.py`
- Current templates: `adversarial_workflow/templates/`
