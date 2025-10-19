# Quick Update Guide

**For maintainers of adversarial-workflow**

This guide shows the fastest way to release updates and integrate them into consumer projects.

---

## TL;DR - Release & Update Flow

```bash
# === 1. Make changes in adversarial-workflow ===
cd ~/Github/adversarial-workflow
vim adversarial_workflow/cli.py
git commit -am "feat: Add new feature"

# === 2. Release new version ===
git tag v0.3.1
git push origin main
git push origin v0.3.1

# === 3. Update consumer projects ===
cd ~/Github/thematic-cuts/adversarial-workflow
git pull origin main
# Changes are immediate if installed in editable mode!

# OR for other projects with git dependency:
cd ~/Github/other-project
# Edit pyproject.toml: @v0.3.0 → @v0.3.1
pip install -e ".[adversarial]" --force-reinstall --no-deps
```

---

## Detailed Workflows

### Workflow A: Minor Update (Patch/Minor)

**When**: Bug fixes, small features, documentation updates

```bash
# 1. Make changes
cd adversarial-workflow
vim adversarial_workflow/cli.py

# 2. Update version in pyproject.toml
vim pyproject.toml  # version = "0.3.1"

# 3. Update CHANGELOG.md
cat >> CHANGELOG.md << 'EOF'
## [0.3.1] - 2025-10-18

### Added
- New feature X

### Fixed
- Bug Y
EOF

# 4. Commit and tag
git add .
git commit -m "release: v0.3.1 - Description"
git tag v0.3.1
git push origin main
git push origin v0.3.1

# 5. Update consumers (see below)
```

### Workflow B: Major Update (Breaking Changes)

**When**: API changes, major refactors, breaking changes

```bash
# Follow Workflow A, but:
# - Bump major or minor version (0.3.1 → 0.4.0)
# - Add migration notes to CHANGELOG.md
# - Update documentation for breaking changes
# - Consider deprecation warnings before breaking

# Example CHANGELOG.md entry:
## [0.4.0] - 2025-10-18

### BREAKING CHANGES
- Changed X to Y (migration: do Z)

### Added
- New feature A
```

### Workflow C: Quick Hotfix

**When**: Critical bug, security fix, urgent patch

```bash
# 1. Make minimal change
vim adversarial_workflow/cli.py

# 2. Quick commit and tag
git commit -am "fix: Critical bug in X (v0.3.2)"
git tag v0.3.2
git push origin main v0.3.2

# 3. Immediately update consumers
# (skip CHANGELOG.md for now, update later)
```

---

## Updating Consumer Projects

### Method 1: Nested Repo with Editable Install (thematic-cuts)

```bash
cd ~/Github/thematic-cuts/adversarial-workflow
git pull origin main
# Done! Changes are immediate with editable install
adversarial --version  # Verify new version
```

**No reinstall needed!** This is the beauty of editable mode.

### Method 2: Git Dependency (Other Projects)

```bash
# 1. Check current version
pip show adversarial-workflow

# 2. Update pyproject.toml
vim pyproject.toml
# Change: ...@v0.3.0 → ...@v0.3.1

# 3. Reinstall
pip install -e ".[adversarial]" --force-reinstall --no-deps

# 4. Verify
adversarial --version

# 5. Commit the update
git add pyproject.toml
git commit -m "chore: Update adversarial-workflow to v0.3.1"
```

### Method 3: Test Before Updating pyproject.toml

```bash
# Install specific version without editing pyproject.toml
pip install git+https://github.com/movito/adversarial-workflow.git@v0.3.1 --force-reinstall

# Test it
adversarial --version
adversarial check

# If good, update pyproject.toml permanently
# If bad, reinstall from pyproject.toml to rollback
```

---

## Version Numbering Guide

Follow **Semantic Versioning** (semver.org):

```
MAJOR.MINOR.PATCH
  |     |     |
  |     |     +-- Bug fixes (0.3.0 → 0.3.1)
  |     +-------- New features, backwards compatible (0.3.1 → 0.4.0)
  +-------------- Breaking changes (0.4.0 → 1.0.0)
```

**Examples**:
- `0.3.0 → 0.3.1` - Fixed validation bug
- `0.3.1 → 0.4.0` - Added new `health` command
- `0.4.0 → 1.0.0` - Changed CLI interface (breaking)

**Pre-release tags**:
- `v0.4.0-alpha.1` - Early testing
- `v0.4.0-beta.1` - Feature complete, testing
- `v0.4.0-rc.1` - Release candidate

---

## Checklist Before Releasing

- [ ] Tests pass (if you have tests)
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] Breaking changes documented
- [ ] README.md updated (if needed)
- [ ] Commit message follows convention
- [ ] Tag matches version in pyproject.toml

---

## Troubleshooting

### "adversarial --version shows old version after update"

```bash
# Reinstall with force
pip install -e adversarial-workflow/ --force-reinstall --no-deps

# Or uninstall and reinstall
pip uninstall adversarial-workflow
pip install -e adversarial-workflow/
```

### "Changes not reflected in consumer project"

```bash
# If using editable install
pip show adversarial-workflow  # Check if really editable
# Should show: Editable project location: /path/to/adversarial-workflow

# If using git dependency
pip install -e ".[adversarial]" --force-reinstall --no-deps
```

### "Multiple versions installed"

```bash
# Clean slate
pip uninstall adversarial-workflow -y
pip cache purge

# Reinstall
pip install -e adversarial-workflow/  # For editable
# OR
pip install -e ".[adversarial]"  # For git dependency
```

---

## Quick Commands Reference

```bash
# Check what's installed
pip show adversarial-workflow
adversarial --version

# View git tags
git tag -l
git ls-remote --tags https://github.com/movito/adversarial-workflow.git

# Create tag
git tag v0.3.1
git push origin v0.3.1

# Delete tag (if mistake)
git tag -d v0.3.1                    # Local
git push origin :refs/tags/v0.3.1   # Remote

# Update nested repo
cd adversarial-workflow && git pull

# Reinstall from git
pip install git+https://github.com/movito/adversarial-workflow.git@v0.3.1 --force-reinstall
```

---

## See Also

- [INTEGRATION-GUIDE.md](./INTEGRATION-GUIDE.md) - Full integration documentation
- [README.md](../README.md) - Main project README
- [CHANGELOG.md](../CHANGELOG.md) - Version history
