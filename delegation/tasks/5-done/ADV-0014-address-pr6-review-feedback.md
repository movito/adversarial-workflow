# ADV-0014: Address PR #6 Review Feedback

**Status**: Todo
**Priority**: High
**Estimated Effort**: 1-2 hours
**Branch**: `feature/plugin-architecture`
**PR**: https://github.com/movito/adversarial-workflow/pull/6

## Summary

Address review feedback from CodeRabbit and Cursor/Bugbot on PR #6 (Plugin Architecture Proposal).

## Review Feedback

### Critical (Must Fix)

#### 1. Fix alias-skipping logic in CLI integration
**Source**: CodeRabbit | **File**: `ADV-0013-plugin-architecture-phase1.md:168`

The code sketch iterates over `evaluators.items()` which includes both main evaluator names and their aliases. The check `if name in config.aliases:` won't work correctly.

**Current (flawed)**:
```python
for name, config in evaluators.items():
    if name in config.aliases:
        continue  # This logic is broken
```

**Fix**: Track which configs have been registered, not names:
```python
registered_configs = set()
for name, config in evaluators.items():
    if id(config) in registered_configs:
        continue  # Skip aliases (same config object)
    registered_configs.add(id(config))
    # Register parser with aliases
    eval_parser = subparsers.add_parser(name, aliases=config.aliases, ...)
```

---

### Major (Should Fix)

#### 2. Document security implications of local overrides
**Source**: CodeRabbit | **File**: `ADV-0013-plugin-architecture-phase1.md:143`

The design allows local evaluators to override built-in evaluators. This provides flexibility but has security implications that should be documented.

**Fix**: Add a "Security Considerations" section to the task spec:
- Document that local `.adversarial/evaluators/` is trusted (same as `.adversarial/scripts/`)
- Warn users not to clone untrusted repos and run evaluators blindly
- Consider adding a `--no-local-evaluators` flag for paranoid mode

---

### Minor (Nice to Fix)

#### 3. Replace hardcoded absolute path
**Source**: CodeRabbit + Cursor | **File**: `ADV-0013-plugin-architecture-phase1.md:17`

The path `/Users/broadcaster_three/Github/ombruk/docs/proposals/...` exposes a developer username and won't work for other developers.

**Fix**: Change to a generic reference:
```markdown
**Reference Document**: See the original proposal in the ombruk-idrettsbygg project
```

#### 4. Document `fallback_model` behavior
**Source**: CodeRabbit | **File**: `ADV-0013-plugin-architecture-phase1.md:37`

The `fallback_model` field is defined but its behavior is not documented.

**Fix**: Add to the Execution section:
```markdown
- If primary model fails (API error, rate limit), retry with `fallback_model` if specified
- Fallback is optional; if not specified, failure is final
```

#### 5. Define missing functions and exception classes
**Source**: CodeRabbit | **File**: `ADV-0013-plugin-architecture-phase1.md:144`

The code references `parse_evaluator_yaml()` and `EvaluatorParseError` without defining them.

**Fix**: Add function signatures to the technical design:
```python
class EvaluatorParseError(Exception):
    """Raised when evaluator YAML is invalid."""
    pass

def parse_evaluator_yaml(yml_file: Path) -> EvaluatorConfig:
    """Parse a YAML file into an EvaluatorConfig."""
    data = yaml.safe_load(yml_file.read_text())
    # Validate required fields
    for field in ["name", "model", "api_key_env", "prompt", "output_suffix"]:
        if field not in data:
            raise EvaluatorParseError(f"Missing required field: {field}")
    return EvaluatorConfig(**data)
```

---

### Trivial (Optional)

#### 6. Fix Markdown formatting
**Source**: CodeRabbit | **Files**: Both

- Add blank lines around fenced code blocks
- Add language specifiers to code blocks (e.g., `text` for CLI output)

---

## Acceptance Criteria

- [ ] Alias-skipping logic corrected in code sketch
- [ ] Security considerations section added
- [ ] Hardcoded path replaced with generic reference
- [ ] `fallback_model` behavior documented
- [ ] Missing function signatures added
- [ ] Markdown formatting cleaned up
- [ ] Commit changes and push to PR #6
- [ ] Re-request review from CodeRabbit

## Testing

After changes:
```bash
# Verify markdown linting (optional)
npx markdownlint delegation/tasks/2-todo/ADV-0013-plugin-architecture-phase1.md
npx markdownlint docs/roadmap/v0.6.0-ROADMAP.md

# Push and verify reviewers are satisfied
git push
```

## References

- PR: https://github.com/movito/adversarial-workflow/pull/6
- Original task: `delegation/tasks/2-todo/ADV-0013-plugin-architecture-phase1.md`
- Roadmap: `docs/roadmap/v0.6.0-ROADMAP.md`
