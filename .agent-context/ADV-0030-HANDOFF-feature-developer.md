# ADV-0030 Handoff: Feature Developer

**Created**: 2026-02-05
**Task**: BugBot Fixes for v0.8.1
**Branch**: `fix/v0.8.1-bugbot-issues` (already created, checkout required)

---

## Quick Context

Four bugs from Cursor BugBot need fixing for v0.8.1 patch. All are in the library module. Two affect CI/CD usage (MEDIUM), one is crash protection (MEDIUM), one is dead code (LOW).

---

## File-by-File Fixes

### File 1: `adversarial_workflow/library/commands.py`

#### Fix 1.1: Category confirmation (line ~409)

**Find**:
```python
        if not yes:
            response = input("Proceed? [y/N]: ").strip().lower()
```

**Replace with**:
```python
        # Skip confirmation for --yes or --dry-run (dry-run makes no changes)
        if not yes and not dry_run:
            response = input("Proceed? [y/N]: ").strip().lower()
```

#### Fix 1.2: Dry-run exit code (line ~544)

**Find**:
```python
    # Summary
    print()
    if dry_run:
        print(f"{CYAN}Dry run complete. Use without --dry-run to install.{RESET}")
    elif success_count == len(evaluator_specs):
```

**Replace with**:
```python
    # Summary
    print()
    if dry_run:
        if success_count == 0 and len(evaluator_specs) > 0:
            print(f"{RED}Dry run failed: No evaluators could be previewed.{RESET}")
            return 1
        print(f"{CYAN}Dry run complete. {success_count} evaluator(s) previewed successfully.{RESET}")
        return 0
    elif success_count == len(evaluator_specs):
```

---

### File 2: `adversarial_workflow/library/config.py`

#### Fix 2.1: Non-dict YAML crash (line ~41)

**Find**:
```python
            with open(config_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            lib_config = data.get("library", {})
```

**Replace with**:
```python
            with open(config_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            # Handle non-dict YAML (list, scalar, etc.) gracefully
            if not isinstance(data, dict):
                data = {}
            lib_config = data.get("library", {})
```

#### Fix 2.2: Wire up `ref` field (or remove dead code)

**Option A - Wire up (recommended)**:

In `client.py`, update `LibraryClient.__init__`:
```python
def __init__(self, ...):
    # Load config
    self._config = config or get_library_config()

    # Use config values
    self.base_url = base_url or self._config.url
    self.ref = self._config.ref  # NEW: Use ref from config

    # Update DEFAULT_LIBRARY_URL to use ref
    if self.base_url == DEFAULT_LIBRARY_URL or not base_url:
        self.base_url = f"https://raw.githubusercontent.com/movito/adversarial-evaluator-library/{self.ref}"
```

**Option B - Remove dead code**:

Remove `ref` and `enabled` from `LibraryConfig` and all references.

---

## Tests to Add

Add to `tests/test_library_enhancements.py`:

```python
def test_category_dry_run_skips_confirmation(self, mock_client, tmp_path):
    """Category + dry-run should not prompt for confirmation."""
    # Setup mock
    mock_client.return_value.fetch_index.return_value = (self.mock_index, False)

    # Run with --category --dry-run (simulates non-TTY)
    with patch('sys.stdin.isatty', return_value=False):
        result = library_install(
            evaluator_specs=[],
            category="test-category",
            dry_run=True,
            yes=False,
        )

    # Should not hang or fail on input()
    assert result == 0


def test_dry_run_returns_error_when_all_fail(self, mock_client, tmp_path):
    """Dry-run should return 1 when all previews fail."""
    mock_client.return_value.fetch_index.return_value = (self.mock_index, False)
    mock_client.return_value.fetch_evaluator.side_effect = NetworkError("Failed")

    result = library_install(
        evaluator_specs=["test/evaluator"],
        dry_run=True,
    )

    assert result == 1


def test_config_handles_non_dict_yaml(self, tmp_path):
    """Config should handle YAML files with non-dict content."""
    config_file = tmp_path / "config.yml"
    config_file.write_text('["this", "is", "a", "list"]')

    # Should not crash, should return defaults
    config = get_library_config(config_path=config_file)
    assert config.url == "https://github.com/movito/adversarial-evaluator-library"
```

---

## Verification Checklist

- [ ] Fix 1.1: `--category --dry-run` works without prompt in non-TTY
- [ ] Fix 1.2: Dry-run returns 1 when all evaluators fail to preview
- [ ] Fix 2.1: List/scalar YAML config doesn't crash
- [ ] Fix 2.2: `ref` field wired up OR dead code removed
- [ ] All 374+ existing tests pass
- [ ] New tests added and passing
- [ ] `./scripts/ci-check.sh` passes

---

## Commit Message Template

```
fix: Address BugBot issues for v0.8.1

- Fix category confirmation blocking --dry-run in non-TTY (r2770414329)
- Fix dry-run returning success when all previews fail (r2770414341)
- Fix config crash on non-dict YAML structure (r2770414385)
- Wire up ADVERSARIAL_LIBRARY_REF env var (r2770414349)

Closes BugBot issues from PR #22.
```

---

## After Fixes

1. Run full test suite: `pytest tests/ -v`
2. Run CI check: `./scripts/ci-check.sh`
3. Commit with message above
4. Push and create PR targeting `main`
5. After merge, tag as `v0.8.1`
