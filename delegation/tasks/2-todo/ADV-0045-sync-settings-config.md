# ADV-0045: Upstream Sync — Settings & Config

**Status**: Todo
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 20 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f

## Summary

Merge upstream permission settings and pre-commit configuration with our
existing setup. This is one of the more integration-heavy PRs — it requires
careful merging, not just copying.

## Scope

### 1. `.claude/settings.json` — Merge

**Strategy**: Merge both permission sets. Our Serena wildcard + upstream's
expanded Bash permissions and deny list.

Final result should include:

**Allow list** (merged):
```json
[
  "Bash(git *)", "Bash(gh *)", "Bash(pytest *)", "Bash(./scripts/*)",
  "Bash(python* scripts/*.py*)", "Bash(black *)", "Bash(isort *)",
  "Bash(flake8 *)", "Bash(adversarial *)", "Bash(ruff *)", "Bash(pre-commit *)",
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

**Note**: The `Bash(pip install*)` deny rule blocks bare pip installs. This is
intentional — agents should use `./scripts/project setup` or `.venv/bin/pip`.

### 2. `.pre-commit-config.yaml` — Update

- Bump black from 23.12.1 to 26.1.0
- Add `pattern-lint` hook (`language: system`, runs `python3 scripts/pattern_lint.py`)
- Add `validate-task-status` hook (`language: system`)
- Both new hooks must use `language: system` (not `language: python`)

### Integration Notes

- BugBot flagged the `pip install` deny vs documented venv workflow conflict.
  Resolution: agent docs should reference `./scripts/project setup` and
  `.venv/bin/pip`, not bare `pip install`.
- CodeRabbit flagged the Serena wildcard replacing an explicit allowlist.
  This is intentional — the wildcard is simpler and Serena tools are all safe.

## PR Template

```
Title: sync: Merge settings.json and update pre-commit config (ADV-0045)

Body:
## Summary
Merges upstream Bash permissions/deny list with our Serena wildcard.
Updates pre-commit: bumps black, adds pattern-lint and
validate-task-status hooks.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] settings.json has merged allow/deny lists
- [ ] Serena wildcard preserved in allow list
- [ ] pre-commit-config.yaml has bumped black version
- [ ] pattern-lint hook added with `language: system`
- [ ] validate-task-status hook added with `language: system`
- [ ] CI passes
- [ ] PR created and merged
