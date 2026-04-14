# Upgrade Guide

## Python Version Requirement

**Python 3.10+ required**

---

## Upgrading to v1.0.0

### What Changed

- **Aider dependency removed** — evaluators now use LiteLLM directly instead of shelling out to `aider-chat`. No more `pip install aider-chat`, no more Python <3.13 constraint.
- Python 3.13+ is now supported.

### Migration Steps

1. Upgrade the package: `pip install --upgrade adversarial-workflow`
2. Remove aider if no longer needed: `pip uninstall aider-chat`
3. Re-run `adversarial init` to update project files (optional — `.aider.conf.yml` is no longer created)
4. Ensure your API key is set: `export OPENAI_API_KEY=sk-...` (or `ANTHROPIC_API_KEY`)

---

## Upgrading to v0.9.9

### What's Fixed

- **Double `.md.md` extension in evaluator output filenames** — all evaluator outputs were getting `.md.md` instead of `.md`. This affected every project using library evaluators. ([#30](https://github.com/movito/adversarial-workflow/issues/30))

### Quick Upgrade

```bash
# Upgrade the package (pinned to release tag)
pip install --upgrade git+https://github.com/movito/adversarial-workflow.git@v0.9.9
```

No `adversarial init --force` needed — this is a Python-only fix, no shell script changes.

### Verify

```bash
adversarial --version
# Should show: 0.9.9
```

### Cleaning Up Old `.md.md` Files

Existing evaluator outputs in `.adversarial/logs/` will have the double extension. New runs will produce correct filenames.

To bulk-rename existing files:

```bash
cd .adversarial/logs/
for f in *.md.md; do mv "$f" "${f%.md}"; done
```

Or delete them if you don't need old outputs:

```bash
rm -f .adversarial/logs/*.md.md
```

> **Note:** If handoff files or task specs reference `.md.md` paths, those will need manual correction.

---

## Upgrading to v0.9.6

### Quick Upgrade (2 commands)

```bash
# 1. Upgrade the package
pip install --upgrade adversarial-workflow

# 2. Update local scripts (--force skips confirmation prompt)
adversarial init --force
```

### Verify Upgrade

```bash
# Check everything is up-to-date
adversarial check
```

You should see:

```
✅ Scripts up-to-date (v0.9.6)
```

If you see a warning like this, run `adversarial init --force`:

```
⚠️ [WARNING] Scripts outdated (package v0.9.6): evaluate_plan.sh (v0.9.3)
   Fix: Run: adversarial init --force
```

### What's Fixed in v0.9.6

- **Browser no longer opens** during evaluations (no more `platform.openai.com/api-keys` popups)
- Works properly in CI/CD and headless environments
- New script version checking warns you when local scripts are outdated

### Why Two Steps?

The adversarial-workflow package has two parts:

| Component | Location | Update Method |
|-----------|----------|---------------|
| Python code | Site-packages | `pip install --upgrade` |
| Shell scripts | `.adversarial/scripts/` | `adversarial init --force` |

The `--no-browser` fix is in both, so you need both steps.

### Library Evaluators (v0.4.0)

If you use evaluators from the [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library), also update them:

```bash
# Check for available updates
adversarial library check-updates

# Update all installed evaluators
adversarial library update --all
```

**What's new in library v0.4.0:**
- Cross-provider evaluation support (Anthropic models via litellm)
- Updated model IDs: `anthropic/claude-opus-4-6`, `anthropic/claude-sonnet-4-5`
- Requires workflow v0.9.3+ (model field priority fix)

See the [library changelog](https://github.com/movito/adversarial-evaluator-library/blob/main/CHANGELOG.md) for details.

---

## General Upgrade Process

For any future upgrades, follow this pattern:

```bash
# 1. Upgrade package (pin to a release tag)
pip install --upgrade git+https://github.com/movito/adversarial-workflow.git@v<VERSION>

# 2. Check if scripts need updating
adversarial check

# 3. If scripts are outdated, update them
adversarial init --force

# 4. Verify
adversarial check
```

The `adversarial check` command will tell you if your local scripts are outdated compared to the installed package version.

Available release tags: https://github.com/movito/adversarial-workflow/tags

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for full version history.
