# Task: Prepare v0.2.0 Release

**Status**: Planning
**Priority**: High
**Estimated Duration**: 2-3 hours

## Context

Phase 6 has been completed with significant documentation and UX improvements. We need to package these improvements as v0.2.0 and prepare for PyPI publication.

## Current State

- **Phase 6 Complete**: All documentation, terminology, platform support, and UX improvements done
- **Current Version**: Files show inconsistent versions (pyproject.toml: 0.1.0, __init__.py: 1.0.0)
- **Existing Dist**: v0.1.0 distribution files exist in dist/ directory
- **Git Status**: Clean working directory, main branch
- **No CHANGELOG**: No changelog file exists

## Objectives

1. **Version Consistency**: Fix version mismatches and update to 0.2.0
2. **Changelog**: Create CHANGELOG.md documenting Phase 6 improvements
3. **Distribution**: Build clean v0.2.0 distribution packages
4. **Validation**: Verify package quality with twine and test installation
5. **Git Tagging**: Create proper v0.2.0 git tag for release

## Requirements

### 1. Version Updates
- Update `pyproject.toml` version from 0.1.0 → 0.2.0
- Update `adversarial_workflow/__init__.py` version from 1.0.0 → 0.2.0
- Ensure consistency across all version references

### 2. CHANGELOG.md Creation
Create comprehensive changelog following Keep a Changelog format:
- **[0.2.0] - 2025-10-16** section
- Document all Phase 6 improvements:
  - Terminology standardization (73 fixes across 11 files)
  - Platform support enhancements (Windows detection, WSL guidance)
  - Enhanced error messages (ERROR/WHY/FIX/HELP pattern)
  - New examples (iteration, legacy code, monorepo, cost optimization)
  - Interactive onboarding improvements
- Link to Phase 6 completion summary
- Include breaking changes section (none for this release)

### 3. Distribution Build
- Clean old dist/ files (remove v0.1.0 artifacts)
- Build using `python -m build`:
  - Source distribution (.tar.gz)
  - Wheel distribution (.whl)
- Validate with `twine check dist/*`

### 4. Testing
- Create fresh virtual environment
- Test installation: `pip install dist/adversarial_workflow-0.2.0-py3-none-any.whl`
- Verify CLI commands work: `adversarial --version`, `adversarial --help`
- Test basic functionality: `adversarial check`

### 5. Git Release Process
- Commit all changes with message: "chore: Release v0.2.0 with Phase 6 improvements"
- Create annotated git tag: `git tag -a v0.2.0 -m "Release v0.2.0 - Phase 6 documentation & UX improvements"`
- Update .agent-context/agent-handoffs.json with release status

## Acceptance Criteria

- [ ] All version numbers consistent at 0.2.0
- [ ] CHANGELOG.md created with comprehensive Phase 6 documentation
- [ ] Old v0.1.0 dist files removed
- [ ] New v0.2.0 wheel and source distributions built successfully
- [ ] `twine check` passes with zero warnings
- [ ] Fresh venv installation works correctly
- [ ] All CLI commands functional in test environment
- [ ] Git commit created with clear message
- [ ] Git tag v0.2.0 created
- [ ] Zero breaking changes from v0.1.0

## Non-Goals

- PyPI publication (preparing for later)
- GitHub repository creation (user will create manually)
- CI/CD setup (future enhancement)
- Automated testing suite (future enhancement)

## Implementation Notes

- Follow semantic versioning (0.2.0 = minor version bump)
- Use Keep a Changelog format for CHANGELOG.md
- Test in fresh environment to catch dependency issues
- Validate all Phase 6 features work in packaged version

## Success Metrics

- Package builds without errors
- twine validation passes
- Installation works in clean environment
- Version consistency across all files
- Comprehensive changelog for users

## References

- Phase 6 Completion Summary: `PHASE-6-COMPLETION-SUMMARY.md`
- Current pyproject.toml: version 0.1.0
- Current __init__.py: version 1.0.0 (needs fix)
- Semantic Versioning: https://semver.org/
- Keep a Changelog: https://keepachangelog.com/
