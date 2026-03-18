# ADV-0045: Upstream Sync — Settings & Config

**Status**: Done
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 15 minutes
**Created**: 2026-03-07
**Updated**: 2026-03-11 (revised after ADV-0053 Ruff migration)
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Merge upstream permission settings with our existing setup and add two
pre-commit hooks. Scope reduced after review — Black/isort/flake8 are gone
(replaced by Ruff in ADV-0053).

## Scope

### 1. `.claude/settings.json` — Merge

**Current state**: Explicit Serena tool list (17 individual tools), no Bash
permissions, no deny list.

**Target state**: Consolidate Serena to wildcard, add Bash permissions and deny
list from upstream.

**Allow list** (merged):
```json
[
  "Bash(git *)", "Bash(gh *)", "Bash(pytest *)", "Bash(./scripts/*)",
  "Bash(python* scripts/*.py*)", "Bash(adversarial *)", "Bash(ruff *)",
  "Bash(pre-commit *)",
  "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Skill", "WebFetch", "Task",
  "mcp__serena__*"
]
```

**Deny list** (from upstream):
```json
[
  "Bash(git push --force*)", "Bash(git push -f*)", "Bash(git reset --hard*)",
  "Bash(git clean*)", "Bash(git branch -D*)", "Bash(rm -rf*)", "Bash(rm -r *)",
  "Bash(gh repo delete*)", "Bash(pip install*)", "Bash(uv add*)",
  "Bash(curl*|*curl*)", "Bash(wget*)"
]
```

**Changes from original spec**:
- Removed `Bash(black *)`, `Bash(isort *)`, `Bash(flake8 *)` — these tools
  were replaced by Ruff in ADV-0053
- Serena wildcard (`mcp__serena__*`) replaces 17 explicit entries — intentional
  simplification, all Serena tools are safe read/navigation operations

**Note**: The `Bash(pip install*)` deny rule blocks bare pip installs. Agents
should use `./scripts/core/project setup` or `.venv/bin/pip`.

### 2. `.pre-commit-config.yaml` — Add Hooks

**Do NOT change existing hooks** — Ruff config is already correct from ADV-0053.

Add two new local hooks:
- `pattern-lint` hook (`language: system`, runs
  `python3 scripts/core/pattern_lint.py adversarial/ tests/`)
- `validate-task-status` hook (`language: system`, runs
  `python3 scripts/core/validate_task_status.py`)

Both must use `language: system` (not `language: python`).

### What NOT to Do

- Do NOT bump Black — we use Ruff now (ADV-0053)
- Do NOT add Black/isort/flake8 hooks — already removed
- Do NOT change existing Ruff pre-commit hooks

## PR Template

```
Title: sync: Merge settings.json permissions and add pre-commit hooks (ADV-0045)

Body:
## Summary
Merges upstream Bash permissions and deny list into settings.json.
Consolidates 17 explicit Serena tool entries to wildcard.
Adds pattern-lint and validate-task-status pre-commit hooks.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] settings.json has merged allow/deny lists
- [ ] Serena wildcard replaces explicit tool list
- [ ] No references to Black/isort/flake8 in settings
- [ ] pattern-lint pre-commit hook added with `language: system`
- [ ] validate-task-status pre-commit hook added with `language: system`
- [ ] Existing Ruff hooks unchanged
- [ ] `pre-commit run --all-files` passes
- [ ] CI passes
- [ ] PR created and merged
