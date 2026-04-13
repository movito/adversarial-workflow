# ADV-0018 Code Review Starter

## PR Information
- **PR**: #10 - feat(cli): Add dynamic evaluator command registration
- **Branch**: `feature/adv-0018-cli-dynamic-commands`
- **URL**: https://github.com/movito/adversarial-workflow/pull/10

## Summary

This PR implements dynamic CLI command registration for evaluators, replacing hardcoded subparsers with a discovery-based system.

## Files Changed

### 1. `adversarial_workflow/cli.py` (main implementation)
- Modified `main()` function (lines ~3043-3240)
- Added imports for evaluators module
- Added `STATIC_COMMANDS` set to protect core commands
- Added dynamic evaluator registration loop
- Added alias filtering against static commands
- Kept `review` as static command (reviews git changes, no file arg)

### 2. `tests/test_cli_dynamic_commands.py` (new file)
- 23 comprehensive tests covering:
  - Built-in evaluators in help
  - Local evaluator discovery
  - Static command protection
  - Evaluator execution routing
  - Alias support and filtering
  - Backwards compatibility
  - Graceful degradation
  - Review command backwards compatibility

## Key Implementation Details

### Dynamic Registration Loop
```python
for name, config in evaluators.items():
    if name in STATIC_COMMANDS:
        registered_configs.add(id(config))  # Mark to prevent alias re-registration
        continue
    if id(config) in registered_configs:
        continue
    registered_configs.add(id(config))

    # Filter aliases against static commands
    aliases = [a for a in (config.aliases or []) if a not in STATIC_COMMANDS]

    eval_parser = subparsers.add_parser(config.name, aliases=aliases, ...)
    eval_parser.set_defaults(evaluator_config=config)
```

### Command Dispatch
```python
if hasattr(args, "evaluator_config"):
    return run_evaluator(args.evaluator_config, args.file, timeout=args.timeout)
# Then static commands...
```

## Review Focus Areas

1. **Static Command Protection**
   - Is `STATIC_COMMANDS` set complete? Should any commands be added/removed?
   - Is the alias filtering logic correct?

2. **Review Command Handling**
   - `review` is kept as static (no file arg required)
   - Is this the right approach vs. making file optional?

3. **Error Handling**
   - Discovery failures fall back to built-ins
   - Conflicting names/aliases are logged and skipped
   - Is the logging level appropriate (warning)?

4. **Test Coverage**
   - 23 tests covering main scenarios
   - Are there edge cases missing?

5. **Backwards Compatibility**
   - `evaluate` and `proofread` now use `file` arg instead of `task_file`/`doc_file`
   - Is this acceptable or breaking?

## Bot Review Status

### CodeRabbit
- Initial: CHANGES_REQUESTED
- Issues fixed in follow-up commit

### BugBot
- Found 3 issues (all fixed):
  1. Alias collision with static commands ✅
  2. Review command requires file (breaking) ✅
  3. Skipped config not marked as registered ✅

## Test Results

```
========================= 160 passed in 2.71s =========================
```

*(Verified 2026-01-22)*

## Commits

1. `06e9347` - feat(cli): Add dynamic evaluator command registration (ADV-0018)
2. `bf9f606` - fix(cli): Address CodeRabbit and BugBot review feedback

## Dependencies

This PR depends on (all merged):
- ADV-0015: EvaluatorConfig dataclass
- ADV-0016: YAML parsing and evaluator discovery
- ADV-0017: Generic evaluator runner
