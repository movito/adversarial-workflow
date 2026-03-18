# ADV-0056: `adversarial upgrade` Command

**Status**: Backlog
**Priority**: Medium
**Type**: Feature
**Estimated Effort**: 4-6 hours
**Created**: 2026-03-15
**Depends On**: ADV-0054
**Related**: ADV-0055 (health check enhancements — can be folded into this task)

## Summary

Add an `adversarial upgrade` command that brings a project's `.adversarial/` scripts and
config up to date with the installed package version. This solves the "duplicated project
inherits stale scripts" problem that caused the RMM-0001 incident.

## Background

Projects are often created by duplicating an existing project (e.g., epistemic-drift →
research-method-matrix) rather than running `adversarial init`. When the `adversarial`
package is updated, these duplicated projects retain old scripts with known bugs. There is
currently no mechanism to update them short of manually re-running `adversarial init`
(which overwrites config) or hand-editing the scripts.

## Proposed Behavior

```bash
# Show what would change (safe, read-only)
adversarial upgrade --dry-run

# Apply updates
adversarial upgrade

# Force overwrite without prompts
adversarial upgrade --force
```

### Dry-run output example

```
🔄 Adversarial Workflow Upgrade Check
  Package version: 0.9.10
  Project scripts: 0.9.8

Scripts:
  ⚠️  review_implementation.sh — v0.9.8 → v0.9.10 (3 changes)
     + mkdir -p before artifact writes
     + Branch-aware git diff
     + Updated SCRIPT_VERSION
  ✅ evaluate_plan.sh — v0.9.10 (up to date)
  ⚠️  validate_tests.sh — v0.9.8 → v0.9.10 (1 change)

Config:
  ⚠️  Missing field: artifacts_directory (will add with default)

Run 'adversarial upgrade' to apply changes.
```

### Upgrade behavior

1. **Scripts** (`*.sh`):
   - Re-render templates using current config values
   - Preserve `SCRIPT_VERSION` tag for future comparisons
   - If local script has custom modifications not in the template, warn and ask (or skip with `--force`)

2. **Config** (`config.yml`):
   - Add missing fields with defaults (never remove existing fields)
   - Don't change existing values

3. **Directories**:
   - Create missing directories (`artifacts/`, `logs/`) via `mkdir -p`

### What it does NOT do

- Overwrite `.claude/` agents, skills, or commands (those are project-specific)
- Modify `.agent-context/` files
- Change task files or delegation structure
- Touch `.env` or API keys

## Acceptance Criteria

- [ ] `adversarial upgrade --dry-run` shows what would change without modifying files
- [ ] `adversarial upgrade` re-renders scripts from templates with current config
- [ ] `adversarial upgrade` adds missing config fields with defaults
- [ ] `adversarial upgrade` creates missing directories
- [ ] `adversarial upgrade --force` skips interactive prompts
- [ ] Detects and warns about local script customizations
- [ ] Preserves existing config values (only adds, never removes or changes)
- [ ] Test coverage for upgrade logic
- [ ] CLI help text and `--help` output

### Health check enhancements (from ADV-0055)

- [ ] `adversarial health` reports script version vs. package version mismatch
- [ ] `adversarial health` checks artifacts directory exists and is writable
- [ ] `adversarial health` warns on missing config fields with defaults
- [ ] `adversarial health` suggests `adversarial upgrade` when scripts are stale

## Design Considerations

### Custom script detection

To detect local modifications, compare the local script against what the template would
generate with the current config. If they differ beyond the `SCRIPT_VERSION` line, the
script has local customizations.

Options for handling:
1. **Warn and skip** (safest) — "review_implementation.sh has local changes, skipping. Use --force to overwrite."
2. **Show diff** — Display what would change and ask for confirmation
3. **Backup and overwrite** — Copy old script to `*.sh.bak` before replacing

Recommend option 1 as default, option 3 with `--force`.

### Template rendering

The existing `render_template()` function in `cli.py` handles variable substitution.
`adversarial upgrade` should:
1. Load current `config.yml`
2. Build the same `config_vars` dict that `init` uses
3. Re-render each template
4. Compare rendered output against local file
5. Write if different

## Files to Create/Modify

1. `adversarial_workflow/cli.py` — new `upgrade()` function + subparser registration
2. Tests — new test file or test class for upgrade logic

## Notes

- This command is the natural counterpart to `adversarial init` — init creates, upgrade updates
- ADV-0055 (health check enhancement) provides the script version comparison logic that this command builds on
- Consider whether `adversarial upgrade` should also update `.adversarial/evaluators/*.yml` from the library — probably not in v1, but worth noting for future
- The `--dry-run` flag is essential — users need to see what will change before committing to it
