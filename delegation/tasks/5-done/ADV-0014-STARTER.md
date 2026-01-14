# ADV-0014 Task Starter

## Quick Context

You are addressing review feedback from CodeRabbit and Cursor/Bugbot on PR #6.

**Branch**: `feature/plugin-architecture` (already checked out)
**PR**: https://github.com/movito/adversarial-workflow/pull/6

## Files to Edit

1. `delegation/tasks/2-todo/ADV-0013-plugin-architecture-phase1.md`
2. `docs/roadmap/v0.6.0-ROADMAP.md`

## Changes Required

### 1. Fix alias-skipping logic (Critical)

In ADV-0013, around line 155-168, replace the flawed CLI integration code:

```python
# REPLACE THIS:
for name, config in evaluators.items():
    if name in config.aliases:
        continue

# WITH THIS:
registered_configs = set()
for name, config in evaluators.items():
    if id(config) in registered_configs:
        continue  # Skip aliases (same config object)
    registered_configs.add(id(config))

    eval_parser = subparsers.add_parser(
        name,
        help=config.description,
        aliases=config.aliases
    )
    eval_parser.add_argument("file", help="File to evaluate")
    eval_parser.set_defaults(evaluator_config=config)
```

### 2. Add Security Considerations section (Major)

Add after "Non-Functional Requirements" section in ADV-0013:

```markdown
### Security Considerations

1. **Trust Model**: Local `.adversarial/evaluators/` files are trusted, same as `.adversarial/scripts/`
2. **User Responsibility**: Do not clone untrusted repositories and run evaluators without review
3. **Override Warning**: When a local evaluator overrides a built-in, log a warning at startup
4. **Future**: Consider `--no-local-evaluators` flag for restricted environments
```

### 3. Replace hardcoded path (Minor)

Line 17 in ADV-0013, change:

```markdown
**Reference Document**: /Users/broadcaster_three/Github/ombruk/docs/proposals/ADVERSARIAL-WORKFLOW-PLUGIN-ARCHITECTURE.md
```

To:

```markdown
**Reference Document**: See original proposal from ombruk-idrettsbygg project (external)
```

### 4. Document fallback_model behavior (Minor)

In ADV-0013 "Execution" section (around line 56-60), add:

```markdown
- If primary model fails (API error, rate limit), retry with `fallback_model` if specified
- Fallback is optional; without it, model failure is final
```

### 5. Add missing function definitions (Minor)

In ADV-0013 after the discovery module code (around line 144), add:

```python
class EvaluatorParseError(Exception):
    """Raised when evaluator YAML is invalid."""
    pass

def parse_evaluator_yaml(yml_file: Path) -> EvaluatorConfig:
    """Parse a YAML file into an EvaluatorConfig."""
    data = yaml.safe_load(yml_file.read_text())
    required = ["name", "model", "api_key_env", "prompt", "output_suffix"]
    for field in required:
        if field not in data:
            raise EvaluatorParseError(f"Missing required field: {field}")
    return EvaluatorConfig(**data)
```

### 6. Fix Markdown formatting (Trivial)

- Ensure blank lines before and after fenced code blocks
- Add language specifiers where missing (use `text` for CLI output)

## Commit & Push

After all changes:

```bash
git add -A
git commit -m "docs: Address PR #6 review feedback from CodeRabbit and Bugbot

- Fix alias-skipping logic in CLI integration code sketch
- Add Security Considerations section
- Replace hardcoded local path with generic reference
- Document fallback_model behavior
- Add missing parse_evaluator_yaml() and EvaluatorParseError definitions
- Fix Markdown formatting issues

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

## Verify

Check that reviewers are satisfied:

```bash
gh pr view 6 --json reviews --jq '.reviews[] | {author: .author.login, state: .state}'
```
