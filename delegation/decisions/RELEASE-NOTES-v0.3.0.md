# Release Notes: v0.3.0 - PyPI Upload Instructions

**Status**: Built ✅ | Upload Pending ⏸️

**Date**: 2025-10-17

## Build Complete

Distribution packages successfully built:
- **Wheel**: `dist/adversarial_workflow-0.3.0-py3-none-any.whl` (58KB)
- **Source**: `dist/adversarial_workflow-0.3.0.tar.gz` (57KB)

All templates included (12 files including new agent-context/ templates).

Git tag created and pushed: `v0.3.0`

---

## PyPI Upload Instructions

### Option 1: Manual Upload (Recommended)

```bash
cd /Users/broadcaster_three/Github/adversarial-workflow
twine upload dist/adversarial_workflow-0.3.0*
```

**Credentials when prompted:**
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-...`)

### Option 2: Environment Variable

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...your-token-here...
twine upload dist/adversarial_workflow-0.3.0*
```

---

## Getting a PyPI API Token

If you don't have a token yet:

1. Go to: https://pypi.org/manage/account/token/
2. Click "Add API token"
3. **Name**: `adversarial-workflow-upload`
4. **Scope**: Project: adversarial-workflow
5. Click "Create token"
6. **⚠️ Copy immediately** (you can't see it again!)

---

## Pre-Upload Verification (Optional)

Test the wheel locally:

```bash
# Install from local wheel
pip install dist/adversarial_workflow-0.3.0-py3-none-any.whl --force-reinstall

# Verify version
adversarial --version
# Expected: adversarial-workflow 0.3.0

# Test health check
adversarial health

# Test new agent onboard command
adversarial agent onboard --help
```

---

## What Happens After Upload

Once `twine upload` succeeds:

- ✅ **Available worldwide** within seconds
- ✅ **Install command**: `pip install adversarial-workflow==0.3.0`
- ✅ **Package page**: https://pypi.org/project/adversarial-workflow/0.3.0/
- ✅ **Latest version**: PyPI automatically marks 0.3.0 as latest
- ✅ **Upgrade command**: `pip install --upgrade adversarial-workflow`

---

## v0.3.0 Release Summary

### Major Features

1. **Agent Coordination System** (`adversarial agent onboard`)
   - Extension layer on top of core workflow
   - Creates `.agent-context/`, `delegation/`, `agents/` structures
   - 7 specialized agent roles initialized
   - Safe task migration with backups
   - Interactive setup wizard

2. **Health Check Command** (`adversarial health`)
   - 7 check categories (Configuration, Dependencies, API Keys, Agent Coordination, Scripts, Tasks, Permissions)
   - Health scoring: >90% healthy, 70-90% degraded, <70% critical
   - `--verbose` flag for detailed diagnostics
   - `--json` flag for CI/CD integration

3. **AGENT-SYSTEM-GUIDE.md** Packaged
   - 34KB comprehensive guide
   - Automatically copied to `.agent-context/` during init
   - Fully offline-capable

4. **Pre-flight Check Script** (`agents/tools/preflight-check.sh`)
   - 4 scan categories: Project Structure, Prerequisites, Configuration, Active Work
   - Bash 3.2+ compatible (macOS/Linux)
   - Completes in <5 seconds

### Code Quality

- **Terminology standardization**: Fixed final straggler (cli.py:322 'Evaluator' → 'Reviewer')
- **Smoke tests**: All passed (version, health 83%, agent onboard)
- **Acceptance criteria**: All Must Have + Should Have met (12/12)

### Documentation

- **README.md**: Added "Quick Setup for AI Agents" section (lines 87-118)
- **EXAMPLES.md**: Added Example 11: Multi-Agent Workflows (~250 lines)
- **QUICK_START.md**: Added health check and agent coordination sections
- **CHANGELOG.md**: Comprehensive 88-line v0.3.0 entry

### Development Effort

- **5 SETUP tasks**: ~21.5-22.5 hours total implementation
- **Release preparation**: ~2 hours (version bumps, CHANGELOG, audit, tests, cleanup)
- **Task cleanup**: 4 PACKAGING-001 tasks reorganized (2 archived, 1 backlog, 1 decisions/)

---

## Post-Upload Checklist

After successful PyPI upload:

- [ ] Verify package page: https://pypi.org/project/adversarial-workflow/0.3.0/
- [ ] Test fresh install: `pip install adversarial-workflow==0.3.0`
- [ ] Announce release (GitHub Releases, Twitter, etc.)
- [ ] Update project status in `.agent-context/current-state.json`
- [ ] Return to thematic-cuts for Phase 2A tasks (if applicable)

---

## Troubleshooting

### Upload fails with "File already exists"

PyPI doesn't allow re-uploading the same version. If you need to fix something:

1. Bump version to 0.3.1 (pyproject.toml, cli.py)
2. Update CHANGELOG
3. Rebuild: `pyproject-build`
4. Upload: `twine upload dist/adversarial_workflow-0.3.1*`

### Upload fails with authentication error

- Ensure username is exactly `__token__` (not your PyPI username)
- Ensure token starts with `pypi-` and is copied correctly
- Check token scope includes "adversarial-workflow" project

### Package page doesn't update

- PyPI can take 1-2 minutes to update search index
- Direct URL works immediately: https://pypi.org/project/adversarial-workflow/0.3.0/
- CDN cache may take 5-10 minutes globally

---

## Contact

- **GitHub**: https://github.com/movito/adversarial-workflow
- **Issues**: https://github.com/movito/adversarial-workflow/issues

---

**Generated**: 2025-10-17 by Feature Developer Agent
**Commit**: 42aa8c3
**Tag**: v0.3.0
