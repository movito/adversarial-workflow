# ADV-0014 Review Starter (Round 2)

## Quick Context

Review round 2 changes addressing findings from first code review.

**Branch**: `feature/plugin-architecture`
**PR**: https://github.com/movito/adversarial-workflow/pull/6
**Commits**:
- `c072c1f` - "docs: Address PR #6 review feedback from CodeRabbit and Bugbot"
- `84cad6f` - "docs: Address code review findings (round 2)"

## Files Changed

1. `delegation/tasks/2-todo/ADV-0013-plugin-architecture-phase1.md`

## Round 1 Items (Previously Verified ✅)

These were verified in the first review and should still be correct:

1. ✅ Alias-skipping logic fix (Critical)
2. ✅ Security considerations section (Major)
3. ✅ Hardcoded path replacement (Minor)
4. ✅ Fallback model documentation (Minor)
5. ✅ Missing function definitions (Minor)
6. ✅ Markdown formatting fixes (Trivial)

## Round 2 Review Checklist

### 1. CLI Registration Logic (HIGH)

Verify line ~203 uses `config.name` instead of dict key `name`:

```python
# OLD (flawed):
eval_parser = subparsers.add_parser(
    name,  # Could be an alias key
    help=config.description,
    aliases=config.aliases
)

# NEW (correct):
eval_parser = subparsers.add_parser(
    config.name,  # Always the canonical name
    help=config.description,
    aliases=config.aliases
)
```

**Review questions**:
- Does this ensure the canonical name is always registered as primary?
- Will aliases still work correctly via `config.aliases`?

### 2. Exception Handling (HIGH)

Verify line ~143 catches all relevant exceptions:

```python
# OLD (incomplete):
except EvaluatorParseError as e:
    print(f"Warning: Skipping {yml_file}: {e}")

# NEW (comprehensive):
except (EvaluatorParseError, yaml.YAMLError, TypeError) as e:
    print(f"Warning: Skipping {yml_file}: {e}")
```

**Review questions**:
- Does this handle malformed YAML files gracefully?
- Does this handle empty YAML files (TypeError from None)?

### 3. Enhanced parse_evaluator_yaml (MEDIUM)

Verify lines ~153-177 include all enhancements:

```python
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

    # Normalize aliases to list (handle missing or None)
    data["aliases"] = data.get("aliases") or []

    # Filter to only known EvaluatorConfig fields
    known_fields = {
        "name", "description", "model", "api_key_env", "prompt",
        "output_suffix", "log_prefix", "fallback_model", "aliases", "version"
    }
    filtered_data = {k: v for k, v in data.items() if k in known_fields}

    return EvaluatorConfig(**filtered_data)
```

**Review questions**:
- Is "description" now in the required fields list?
- Does aliases normalization handle None and missing cases?
- Does field filtering prevent unexpected kwargs errors?

## Commands

```bash
# View round 2 changes only
git show 84cad6f

# View full diff from main
git diff main...feature/plugin-architecture -- delegation/tasks/2-todo/ADV-0013-plugin-architecture-phase1.md

# Check PR status
gh pr view 6 --json state,reviews

# View latest review comments
gh pr view 6 --web
```

## Expected Outcome

- All 3 round 2 items verified as correctly implemented
- Round 1 items still intact (no regressions)
- PR ready for approval
