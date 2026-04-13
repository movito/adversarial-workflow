# Task Handoff: Merge URL Scraping Fix & Release

**From**: gas-taxes project (Planner Agent)
**To**: adversarial-workflow project (Planner Agent)
**Date**: 2026-01-29
**PR**: https://github.com/movito/adversarial-workflow/pull/17

---

## Context

During evaluation runs in the gas-taxes project, we discovered that aider was automatically scraping URLs found in task files. This caused:
- Unexpected timeouts during evaluations
- Wasted API tokens on irrelevant web content
- Confusion about whether the issue was model-specific (it wasn't)

**Root Cause**: The `--yes` flag (required for non-interactive mode) auto-confirms all prompts, including URL scraping requests.

**Solution**: Add `--no-detect-urls` flag to disable URL detection during evaluations.

---

## PR Summary (#17)

**Branch**: `fix/disable-url-scraping`
**Files Changed**: 3 scripts, 3 insertions

```diff
# All three scripts get the same 1-line addition after --yes:
+  --no-detect-urls \
```

**Scripts Updated**:
| Script | Phase | Line |
|--------|-------|------|
| `evaluate_plan.sh` | Phase 1: Plan Evaluation | ~59 |
| `review_implementation.sh` | Phase 3: Implementation Review | ~102 |
| `validate_tests.sh` | Phase 4: Test Validation | ~89 |

---

## Recommended Actions

### 1. Review & Merge PR

```bash
# Review the changes
gh pr view 17
gh pr diff 17

# If satisfied, merge
gh pr merge 17 --squash
```

### 2. Update CHANGELOG.md

Add under `## [Unreleased]`:

```markdown
### Fixed
- **URL auto-scraping disabled** - Added `--no-detect-urls` flag to prevent aider from scraping URLs in task files during evaluations
```

### 3. Decide on Release Strategy

**Option A: Patch Release (Recommended)**
- Bump to v0.6.4
- This is a bug fix with no breaking changes
- Users benefit immediately

**Option B: Bundle with Other Changes**
- If other changes are pending, bundle into next minor release
- Document in release notes

### 4. Release Process (if releasing)

```bash
# Update version in pyproject.toml
# version = "0.6.4"

# Update CHANGELOG.md - move [Unreleased] to [0.6.4]

# Commit release
git add CHANGELOG.md pyproject.toml
git commit -m "chore: Release v0.6.4 - Fix URL auto-scraping"

# Tag and push
git tag -a v0.6.4 -m "v0.6.4 - Fix URL auto-scraping during evaluations"
git push origin main && git push origin v0.6.4

# Publish to PyPI (if applicable)
python -m build
twine upload dist/*
```

### 5. Update Documentation (Optional)

Consider adding a note to docs about the `--no-detect-urls` behavior:

```markdown
## Non-Interactive Mode

When running evaluations non-interactively (`--yes`), URL detection is
automatically disabled to prevent unwanted web scraping. If you need
URL scraping during evaluations, you can override this in your local
scripts by removing the `--no-detect-urls` flag.
```

---

## Testing Verification

The fix was tested in the gas-taxes project:

```bash
# Test command used:
echo "Content with URL: https://docs.mistral.ai/" | \
  aider --no-detect-urls --yes --no-git --model gpt-4o-mini \
  --message "Say OK"

# Result: No URL scraping, model responds "OK" normally
# Cost: $0.00010 (minimal)
```

---

## References

- **Aider Documentation**: https://aider.chat/docs/config/options.html
- **Aider Issue #2187**: https://github.com/Aider-AI/aider/issues/2187 (original feature request)
- **Research Findings**: gas-taxes project `.agent-context/GTX-0003-research-findings.md`

---

## Downstream Impact

After release, projects using adversarial-workflow should:

1. Upgrade: `pip install --upgrade adversarial-workflow`
2. Re-initialize: `adversarial init` (to get updated scripts)
3. Verify: Run an evaluation on a task with URLs to confirm no scraping

---

## Questions / Decisions Needed

1. **Release timing**: Immediate patch or bundle with other changes?
2. **PyPI publish**: Is the package published to PyPI, or just GitHub releases?
3. **Deprecation**: Should we add a config option to re-enable URL scraping for users who want it?

---

**This handoff is complete. The PR is ready for review and merge.**
