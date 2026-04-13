# ADV-0045 Handoff: Settings & Pre-commit Config

## Task

1. Merge upstream Bash permissions and deny list into `.claude/settings.json`
2. Add two pre-commit hooks (pattern-lint, validate-task-status)

## Part 1: `.claude/settings.json`

**Current state** (17 explicit Serena tools, no Bash permissions):
```json
{
  "permissions": {
    "allow": [
      "mcp__serena__activate_project",
      "mcp__serena__read_file",
      "mcp__serena__list_dir",
      ... (17 individual tools)
    ]
  }
}
```

**Target state** (wildcard Serena + Bash permissions + deny list):
```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(gh *)",
      "Bash(pytest *)",
      "Bash(./scripts/*)",
      "Bash(python* scripts/*.py*)",
      "Bash(adversarial *)",
      "Bash(ruff *)",
      "Bash(pre-commit *)",
      "Read",
      "Write",
      "Edit",
      "MultiEdit",
      "Glob",
      "Grep",
      "Skill",
      "WebFetch",
      "Task",
      "mcp__serena__*"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(git push -f*)",
      "Bash(git reset --hard*)",
      "Bash(git clean*)",
      "Bash(git branch -D*)",
      "Bash(rm -rf*)",
      "Bash(rm -r *)",
      "Bash(gh repo delete*)",
      "Bash(pip install*)",
      "Bash(uv add*)",
      "Bash(curl*|*curl*)",
      "Bash(wget*)"
    ]
  }
}
```

**Important**:
- Do NOT include `Bash(black *)`, `Bash(isort *)`, or `Bash(flake8 *)` — we use Ruff
- The `mcp__serena__*` wildcard replaces all 17 explicit Serena entries — intentional
- `Bash(pip install*)` deny is intentional — agents should use `./scripts/core/project setup`

## Part 2: `.pre-commit-config.yaml`

**Do NOT change existing hooks** (pre-commit-hooks, ruff, ruff-format, pytest-fast).

Add two new hooks to the existing `repo: local` section, after the `pytest-fast` hook:

```yaml
      - id: pattern-lint
        name: Defensive coding patterns (DK001-DK004)
        entry: python3 scripts/core/pattern_lint.py adversarial/ tests/
        language: system
        pass_filenames: false
        types: [python]

      - id: validate-task-status
        name: Validate task status fields
        entry: python3 scripts/core/validate_task_status.py
        language: system
        pass_filenames: false
        always_run: true
```

Both MUST use `language: system` (not `language: python`).

## Implementation

```bash
# 1. Create branch
git checkout -b feature/ADV-0045-settings-config

# 2. Start task
./scripts/core/project start ADV-0045

# 3. Edit .claude/settings.json (replace entire content with target state above)

# 4. Edit .pre-commit-config.yaml (add two hooks to local repo section)

# 5. Verify pre-commit works
pre-commit run --all-files

# 6. Run CI
./scripts/core/ci-check.sh

# 7. Commit, push, create PR
```

## PR Details

**Title**: `sync: Merge settings.json permissions and add pre-commit hooks (ADV-0045)`

**Body**:
```
## Summary
Merges upstream Bash permissions and deny list into settings.json.
Consolidates 17 explicit Serena tool entries to wildcard. Adds
pattern-lint and validate-task-status pre-commit hooks.

Part of ADV-0039 (upstream sync).

## Test plan
- [ ] settings.json has allow + deny lists
- [ ] No references to Black/isort/flake8
- [ ] `pre-commit run --all-files` passes
- [ ] CI passes
```
