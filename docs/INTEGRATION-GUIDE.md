# Integration Guide: Using Adversarial-Workflow in Active Development

**Status**: Pre-release (v0.3.x) - Under active development
**Audience**: Developers integrating adversarial-workflow into their own projects
**Last Updated**: 2025-10-18

---

## Overview

This guide explains how to integrate `adversarial-workflow` into your projects **while the package is still under active development**. Since this is not yet published to PyPI, you'll install it directly from GitHub using git tags for version control.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Integration Approaches](#integration-approaches)
3. [Release-Based Workflow](#release-based-workflow)
4. [Simultaneous Development](#simultaneous-development)
5. [Version Management](#version-management)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Option 1: Install from GitHub (Recommended for Stable Use)

Add to your project's `pyproject.toml`:

```toml
[project.optional-dependencies]
adversarial = [
    "adversarial-workflow @ git+https://github.com/movito/adversarial-workflow.git@v0.3.0",
]
```

Install:
```bash
pip install -e ".[adversarial]"
adversarial --version
```

### Option 2: Local Editable Install (Recommended for Active Development)

```bash
# Clone both repositories side-by-side
cd ~/Github
git clone https://github.com/movito/adversarial-workflow.git
git clone https://github.com/your-org/your-project.git

# Install adversarial-workflow in editable mode
cd your-project
pip install -e ../adversarial-workflow

# Changes in adversarial-workflow are immediately available
adversarial --version
```

---

## Integration Approaches

### Approach A: Git Dependency (Portable, Version-Controlled)

**Best for**: Multiple projects, team collaboration, reproducible builds

**Setup**:
```toml
# your-project/pyproject.toml
[project.optional-dependencies]
adversarial = [
    "adversarial-workflow @ git+https://github.com/movito/adversarial-workflow.git@v0.3.0",
]
```

**Workflow**:
```bash
# Install
pip install -e ".[adversarial]"

# Update to new version
# 1. Edit pyproject.toml: @v0.3.0 → @v0.3.1
# 2. Reinstall
pip install -e ".[adversarial]" --force-reinstall --no-deps

# Commit the version update
git add pyproject.toml
git commit -m "chore: Update adversarial-workflow to v0.3.1"
```

**Pros**:
- ✅ Version pinning for reproducibility
- ✅ Works across multiple projects
- ✅ Easy to rollback (change tag)
- ✅ Clean separation of concerns

**Cons**:
- ⚠️ Requires reinstall after updates
- ⚠️ Slower iteration during development

---

### Approach B: Local Editable Install (Fast Iteration)

**Best for**: Active development on both projects simultaneously

**Setup**:
```bash
# Directory structure
~/Github/
├── adversarial-workflow/     ← Source repository
└── your-project/             ← Your project

# Install from local path
cd your-project
pip install -e ~/Github/adversarial-workflow
```

**Workflow**:
```bash
# Make changes in adversarial-workflow
cd ~/Github/adversarial-workflow
vim adversarial_workflow/cli.py

# Changes are immediately available in your-project
cd ~/Github/your-project
adversarial --help  # Reflects your changes instantly!
```

**Pros**:
- ✅ Instant changes (no reinstall)
- ✅ Perfect for rapid iteration
- ✅ Easy to test new features

**Cons**:
- ⚠️ Only works on your local machine
- ⚠️ Must document for team members
- ⚠️ Need to remember which version is installed

---

### Approach C: Hybrid (Recommended for Active Development)

**Best for**: Active development with occasional releases

**Setup**:
```bash
# 1. Clone adversarial-workflow inside your project
cd your-project
git clone https://github.com/movito/adversarial-workflow.git

# 2. Add to .gitignore
echo "adversarial-workflow/" >> .gitignore

# 3. Install in editable mode
pip install -e adversarial-workflow/

# 4. Also add to pyproject.toml for documentation
```

**pyproject.toml**:
```toml
[project.optional-dependencies]
adversarial = [
    # For production/CI: install from GitHub
    # For local dev: pip install -e adversarial-workflow/
    "adversarial-workflow @ git+https://github.com/movito/adversarial-workflow.git@v0.3.0",
]
```

**Workflow**:
```bash
# Local development (instant changes)
cd adversarial-workflow/
git pull
# Changes available immediately

# CI/Production (from GitHub)
pip install -e ".[adversarial]"  # Uses git dependency
```

**Pros**:
- ✅ Best of both worlds
- ✅ Instant local changes
- ✅ Clean production installs
- ✅ Easy context switching

**Cons**:
- ⚠️ More complex setup
- ⚠️ Need to document for team

---

## Release-Based Workflow

### Creating a Release in adversarial-workflow

```bash
cd adversarial-workflow

# 1. Make changes
vim adversarial_workflow/cli.py

# 2. Update version in pyproject.toml
vim pyproject.toml  # version = "0.3.1"

# 3. Update CHANGELOG.md
vim CHANGELOG.md

# 4. Commit changes
git add .
git commit -m "feat: Add new validation features"

# 5. Create and push tag
git tag v0.3.1
git push origin main
git push origin v0.3.1
```

### Updating Consumer Projects

```bash
cd your-project

# Option A: Update pyproject.toml (permanent)
# Edit: @v0.3.0 → @v0.3.1
pip install -e ".[adversarial]" --force-reinstall --no-deps

# Option B: Test new version without editing pyproject.toml
pip install --force-reinstall git+https://github.com/movito/adversarial-workflow.git@v0.3.1

# Verify
adversarial --version  # Should show v0.3.1

# If satisfied, commit
git add pyproject.toml
git commit -m "chore: Update adversarial-workflow to v0.3.1"
```

---

## Simultaneous Development

When working on both repositories at the same time:

### Method 1: Temporary Editable Install

```bash
# Switch to local editable version
cd your-project
pip install -e ~/Github/adversarial-workflow

# Make changes in adversarial-workflow
cd ~/Github/adversarial-workflow
vim adversarial_workflow/cli.py

# Test in your-project
cd ~/Github/your-project
adversarial --help  # Sees changes immediately

# When ready, create release
cd ~/Github/adversarial-workflow
git tag v0.3.2 && git push origin v0.3.2

# Switch back to GitHub version
cd ~/Github/your-project
pip install -e ".[adversarial]" --force-reinstall
```

### Method 2: Nested Repository

```bash
# Clone inside project (ignored by parent git)
cd your-project
git clone https://github.com/movito/adversarial-workflow.git
echo "adversarial-workflow/" >> .gitignore

# Install
pip install -e adversarial-workflow/

# Work on both simultaneously
cd adversarial-workflow/
git pull  # Get updates
vim adversarial_workflow/cli.py  # Make changes

# Changes are immediate in parent project
cd ..
adversarial --help  # Reflects changes

# Push changes
cd adversarial-workflow/
git add . && git commit -m "feat: New feature"
git tag v0.3.2 && git push origin v0.3.2
```

---

## Version Management

### Checking Installed Version

```bash
# Check via pip
pip show adversarial-workflow

# Check via CLI
adversarial --version

# Check installation method
pip list | grep adversarial-workflow
# Shows: adversarial-workflow @ git+https://... (editable install)
```

### Version Pinning Strategies

```toml
# Pin to specific version (recommended)
"adversarial-workflow @ git+https://github.com/movito/adversarial-workflow.git@v0.3.0"

# Use latest release (less stable)
"adversarial-workflow @ git+https://github.com/movito/adversarial-workflow.git@main"

# Pin to specific commit (for testing)
"adversarial-workflow @ git+https://github.com/movito/adversarial-workflow.git@abc123def"
```

### Updating Dependencies

```bash
# Force reinstall (preserves version from pyproject.toml)
pip install -e ".[adversarial]" --force-reinstall --no-deps

# Install specific version without editing pyproject.toml
pip install git+https://github.com/movito/adversarial-workflow.git@v0.3.1

# Upgrade to latest tag
git ls-remote --tags https://github.com/movito/adversarial-workflow.git
# Edit pyproject.toml with latest tag
pip install -e ".[adversarial]" --force-reinstall --no-deps
```

---

## Troubleshooting

### Issue: "adversarial command not found"

**Solution**:
```bash
# Verify installation
pip show adversarial-workflow

# Reinstall if missing
pip install -e ".[adversarial]"

# Check if in correct virtual environment
which python
which adversarial
```

### Issue: Changes not reflected after editing

**Solution**:
```bash
# If installed via git dependency
pip install -e ".[adversarial]" --force-reinstall --no-deps

# If installed via editable mode
# Changes should be instant - check you're in correct environment
which adversarial
pip show adversarial-workflow
```

### Issue: Version mismatch between pyproject.toml and installed

**Solution**:
```bash
# Check what's installed
adversarial --version
pip show adversarial-workflow

# Reinstall from pyproject.toml
pip uninstall adversarial-workflow
pip install -e ".[adversarial]"
```

### Issue: Multiple versions installed

**Solution**:
```bash
# Remove all versions
pip uninstall adversarial-workflow

# Reinstall from desired source
# Option A: From pyproject.toml
pip install -e ".[adversarial]"

# Option B: From local path
pip install -e /path/to/adversarial-workflow
```

---

## Summary: Which Approach Should I Use?

| Use Case | Recommended Approach | Install Command |
|----------|---------------------|-----------------|
| **Production/CI** | Git Dependency (Approach A) | `pip install -e ".[adversarial]"` |
| **Active development** | Editable Install (Approach B) | `pip install -e ~/Github/adversarial-workflow` |
| **Both simultaneously** | Hybrid (Approach C) | `pip install -e adversarial-workflow/` |
| **Testing new features** | Temporary editable install | `pip install -e /path/to/adversarial-workflow` |
| **Multiple projects** | Git Dependency with tags | Add to each `pyproject.toml` |

---

## Complete Example Workflow

```bash
# === INITIAL SETUP ===

# 1. Clone repositories
cd ~/Github
git clone https://github.com/movito/adversarial-workflow.git
git clone https://github.com/your-org/your-project.git

# 2. Configure your-project
cd your-project
cat >> pyproject.toml << 'EOF'
[project.optional-dependencies]
adversarial = [
    "adversarial-workflow @ git+https://github.com/movito/adversarial-workflow.git@v0.3.0",
]
EOF

# 3. Install
pip install -e ".[adversarial]"
adversarial init

# === DEVELOPMENT CYCLE ===

# 4. Make changes in adversarial-workflow
cd ~/Github/adversarial-workflow
vim adversarial_workflow/cli.py
git commit -am "feat: Add new feature"

# 5. Test locally before releasing
cd ~/Github/your-project
pip install -e ~/Github/adversarial-workflow  # Temporary editable install
adversarial --help  # Test changes

# 6. Release new version
cd ~/Github/adversarial-workflow
git tag v0.3.1
git push origin main
git push origin v0.3.1

# 7. Update your-project
cd ~/Github/your-project
# Edit pyproject.toml: @v0.3.0 → @v0.3.1
pip install -e ".[adversarial]" --force-reinstall --no-deps
git add pyproject.toml
git commit -m "chore: Update adversarial-workflow to v0.3.1"
```

---

## Next Steps

- See [QUICK_START.md](../QUICK_START.md) for basic usage
- See [README.md](../README.md) for feature overview
- See [AGENT_INTEGRATION.md](../AGENT_INTEGRATION.md) for Claude Code agent integration

---

## Questions?

- File an issue: https://github.com/movito/adversarial-workflow/issues
- Check the changelog: [CHANGELOG.md](../CHANGELOG.md)
