# ADV-0007: Release v0.5.0 to PyPI

**Status**: Todo
**Priority**: high
**Assigned To**: pypi-publisher
**Estimated Effort**: 30-45 minutes
**Created**: 2025-11-29

## Related Tasks

**Depends On**: ADV-0006 (Python 3.10 fix - complete)
**Blocks**: Users getting new features
**Related**: ADV-0003 (file splitting), ADV-0005 (Python version)

## Overview

Release version 0.5.0 to PyPI with new features and fixes since v0.4.0. Includes README updates to document new capabilities and correct Python version requirements.

**Context**: Significant changes since v0.4.0 warrant a new minor release:
- New `adversarial split` command (ADV-0003)
- Python 3.10+ requirement (ADV-0005)
- Python 3.10 compatibility fix (ADV-0006)

## Requirements

### Functional Requirements
1. Update version to 0.5.0 in all locations
2. Update README with new features and corrected Python version
3. Update CHANGELOG.md with release notes
4. Build and publish to PyPI
5. Create GitHub release

### Non-Functional Requirements
- [ ] All CI/CD tests passing before release
- [ ] Version consistent across all files
- [ ] README accurate and up-to-date

## Implementation Plan

### Step 1: Update README.md

**Python version fixes** (4 locations):
```markdown
# Prerequisites section:
- **Python 3.10+** (Python 3.12 recommended)

# Software Requirements section:
- **Python**: 3.10 or later (Python 3.12 recommended)
```

**Add `split` command to Commands section**:
```markdown
# Workflow
adversarial evaluate task.md            # Phase 1: Evaluate plan
adversarial split task.md               # Split large files into parts
adversarial split task.md --dry-run     # Preview split without creating
adversarial review                      # Phase 3: Review implementation
adversarial validate "pytest"           # Phase 4: Validate with tests
```

**Update File Size Guidelines**:
```markdown
**Solutions for large specifications**:
1. Use `adversarial split` to automatically split files (recommended)
2. Manually split into multiple task files
3. Upgrade your OpenAI organization tier
```

### Step 2: Update Version (3 files)

```bash
# pyproject.toml
version = "0.5.0"

# adversarial_workflow/__init__.py
__version__ = "0.5.0"

# adversarial_workflow/cli.py
__version__ = "0.5.0"
```

### Step 3: Update CHANGELOG.md

```markdown
## [0.5.0] - 2025-11-29

### Added
- New `adversarial split` command for splitting large task files
  - Split by markdown sections (default)
  - Split by implementation phases (`--strategy phases`)
  - Dry-run preview (`--dry-run`)
  - Configurable line limits (`--max-lines`)
- Comprehensive test suite (72+ tests)
- CI/CD pipeline with GitHub Actions

### Changed
- **BREAKING**: Python version requirement changed from 3.8+ to 3.10+
  - Required by aider-chat dependency
  - Python 3.8 and 3.9 no longer supported
- Updated documentation for new features

### Fixed
- Python 3.10 compatibility (tomllib fallback to tomli)
- CI/CD now passes on all supported Python versions (3.10-3.12)
```

### Step 4: Build and Publish

```bash
# Ensure clean state
git status  # Should be clean after commits

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/adversarial_workflow-0.5.0*

# Verify
pip install --upgrade adversarial-workflow
adversarial --version  # Should show 0.5.0
```

### Step 5: Create GitHub Release

```bash
# Tag the release
git tag -a v0.5.0 -m "Release v0.5.0: File splitting, Python 3.10+"

# Push tag
git push origin v0.5.0

# Create release via gh CLI
gh release create v0.5.0 \
  --title "v0.5.0: File Splitting & Python 3.10+" \
  --notes "$(cat <<'EOF'
## What's New

### New Features
- **`adversarial split` command** - Split large task files into smaller, evaluable chunks
  - Automatic section-based splitting
  - Phase-based splitting for implementation plans
  - Dry-run preview mode
  - Configurable line limits

### Changes
- **Python 3.10+ required** (was 3.8+) - aligns with aider-chat requirements
- Comprehensive test suite (72+ tests)
- CI/CD pipeline with multi-platform testing

### Fixes
- Python 3.10 compatibility for tomllib module

## Upgrade

\`\`\`bash
pip install --upgrade adversarial-workflow
\`\`\`

## Full Changelog
See CHANGELOG.md for details.
EOF
)"
```

## Acceptance Criteria

### Must Have
- [ ] Version 0.5.0 in pyproject.toml, __init__.py, cli.py
- [ ] README updated with Python 3.10+ and split command
- [ ] CHANGELOG.md updated with release notes
- [ ] Package published to PyPI
- [ ] `pip install adversarial-workflow` gets v0.5.0

### Should Have
- [ ] GitHub release created with tag v0.5.0
- [ ] Release notes document breaking changes

## Pre-Release Checklist

- [ ] All CI/CD tests passing
- [ ] Version numbers consistent
- [ ] README accurate
- [ ] CHANGELOG complete
- [ ] No uncommitted changes

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Update README | 10 min | [ ] |
| Update versions | 5 min | [ ] |
| Update CHANGELOG | 10 min | [ ] |
| Build & publish | 10 min | [ ] |
| GitHub release | 5 min | [ ] |
| Verify | 5 min | [ ] |
| **Total** | **45 min** | [ ] |

## References

- **PyPI**: https://pypi.org/project/adversarial-workflow/
- **Current version**: 0.4.0
- **Target version**: 0.5.0
- **Semantic versioning**: Minor bump for new features

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-29
