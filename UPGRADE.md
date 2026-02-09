# Upgrade Guide

## Upgrading to v0.9.4

### Quick Upgrade (2 commands)

```bash
# 1. Upgrade the package
pip install --upgrade adversarial-workflow

# 2. Update local scripts (required - scripts now include --no-browser fix)
adversarial init --force
```

### Verify Upgrade

```bash
# Check everything is up-to-date
adversarial check
```

You should see:

```
✅ Scripts up-to-date (v0.9.4)
```

If you see a warning like this, run `adversarial init --force`:

```
⚠️ [WARNING] Scripts outdated (package v0.9.4): evaluate_plan.sh (v0.9.3)
   Fix: Run: adversarial init --force
```

### What's Fixed in v0.9.4

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
# 1. Upgrade package
pip install --upgrade adversarial-workflow

# 2. Check if scripts need updating
adversarial check

# 3. If scripts are outdated, update them
adversarial init --force

# 4. Verify
adversarial check
```

The `adversarial check` command will tell you if your local scripts are outdated compared to the installed package version.

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for full version history.
