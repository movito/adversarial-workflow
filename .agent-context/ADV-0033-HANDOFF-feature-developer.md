# ADV-0033 Handoff: Feature Developer

**Created**: 2026-02-07
**Task**: CLI Core Commands Test Coverage
**Branch**: `feat/adv-0033-cli-core-test-coverage`

---

## Quick Context

The CLI (`cli.py`) has 37% test coverage - the largest gap in the codebase. This task focuses on adding comprehensive tests for the core commands: `evaluate`, `init`, `check`, and `split`.

**Goal**: Increase cli.py coverage from 37% to 50%+

---

## Existing Test Infrastructure

### Current Test Files
- `tests/test_cli.py` - Basic smoke tests (CliRunner pattern)
- `tests/test_cli_dynamic_commands.py` - Dynamic command tests
- `tests/test_evaluate.py` - Some evaluate tests
- `tests/test_split_command.py` - Split command tests

### Key Fixture (conftest.py)

```python
@pytest.fixture
def run_cli():
    """Run CLI commands via subprocess."""
    def _run(args):
        return subprocess.run(
            ["adversarial"] + args,
            capture_output=True,
            text=True
        )
    return _run
```

### Click CliRunner Pattern

```python
from click.testing import CliRunner
from adversarial_workflow.cli import main

@pytest.fixture
def cli_runner():
    return CliRunner()

def test_example(cli_runner):
    result = cli_runner.invoke(main, ["evaluate", "--help"])
    assert result.exit_code == 0
```

---

## Implementation Guide

### 1. Create/Extend Test File

Create `tests/test_cli_core.py` or extend existing `tests/test_cli.py`:

```python
"""Tests for CLI core commands (ADV-0033)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from adversarial_workflow.cli import main


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with .adversarial config."""
    config_dir = tmp_path / ".adversarial"
    config_dir.mkdir()
    (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")
    return tmp_path
```

### 2. Test Cases by Command

#### evaluate command (Lines 60-201)

```python
class TestEvaluateCommand:
    def test_evaluate_help(self, cli_runner):
        result = cli_runner.invoke(main, ["evaluate", "--help"])
        assert result.exit_code == 0
        assert "--evaluator" in result.output

    def test_evaluate_missing_file(self, cli_runner):
        result = cli_runner.invoke(main, ["evaluate", "nonexistent.md"])
        assert result.exit_code != 0

    def test_evaluate_with_evaluator_flag(self, cli_runner, temp_project):
        # Mock aider to avoid actual execution
        with patch("shutil.which", return_value="/usr/bin/aider"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                # Create test file
                test_file = temp_project / "test.md"
                test_file.write_text("# Test")

                result = cli_runner.invoke(
                    main,
                    ["evaluate", str(test_file), "--evaluator", "gpt4o-quick"],
                    env={"OPENAI_API_KEY": "test-key"}
                )
                # Check behavior

    def test_evaluate_dry_run(self, cli_runner, temp_project):
        test_file = temp_project / "test.md"
        test_file.write_text("# Test")
        result = cli_runner.invoke(
            main,
            ["evaluate", str(test_file), "--dry-run"]
        )
        assert result.exit_code == 0
        assert "dry run" in result.output.lower() or "would" in result.output.lower()
```

#### init command (Lines 208-356)

```python
class TestInitCommand:
    def test_init_fresh(self, cli_runner, tmp_path):
        with cli_runner.isolated_filesystem(temp_dir=tmp_path):
            result = cli_runner.invoke(main, ["init"])
            assert result.exit_code == 0
            assert Path(".adversarial").exists()

    def test_init_existing_warns(self, cli_runner, temp_project):
        os.chdir(temp_project)
        result = cli_runner.invoke(main, ["init"])
        # Should warn or skip if already initialized
        assert "already" in result.output.lower() or result.exit_code == 0

    def test_init_force(self, cli_runner, temp_project):
        os.chdir(temp_project)
        result = cli_runner.invoke(main, ["init", "--force"])
        assert result.exit_code == 0
```

#### check command (Lines 363-503)

```python
class TestCheckCommand:
    def test_check_valid_config(self, cli_runner, temp_project):
        os.chdir(temp_project)
        result = cli_runner.invoke(main, ["check"])
        assert result.exit_code == 0

    def test_check_missing_config(self, cli_runner, tmp_path):
        os.chdir(tmp_path)
        result = cli_runner.invoke(main, ["check"])
        assert result.exit_code != 0 or "not found" in result.output.lower()
```

#### split command (Lines 508-590)

```python
class TestSplitCommand:
    def test_split_basic(self, cli_runner, tmp_path):
        # Create a large file
        large_file = tmp_path / "large.md"
        large_file.write_text("# Header\n" + "Content\n" * 1000)

        result = cli_runner.invoke(main, ["split", str(large_file)])
        assert result.exit_code == 0

    def test_split_custom_chunk_size(self, cli_runner, tmp_path):
        large_file = tmp_path / "large.md"
        large_file.write_text("# Header\n" + "Content\n" * 1000)

        result = cli_runner.invoke(
            main,
            ["split", str(large_file), "--chunk-size", "500"]
        )
        assert result.exit_code == 0

    def test_split_missing_file(self, cli_runner):
        result = cli_runner.invoke(main, ["split", "nonexistent.md"])
        assert result.exit_code != 0
```

---

## Mocking Patterns

### Mock aider execution

```python
@pytest.fixture
def mock_aider(mocker):
    mocker.patch("shutil.which", return_value="/usr/bin/aider")
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    return mock_run
```

### Mock environment variables

```python
def test_with_env(cli_runner, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # ... test code
```

---

## Verification

```bash
# Run tests with coverage
pytest tests/test_cli_core.py -v --cov=adversarial_workflow.cli --cov-report=term-missing

# Check overall cli.py coverage
pytest tests/ --cov=adversarial_workflow.cli --cov-report=term-missing | grep cli.py

# Target: cli.py coverage >= 50%
```

---

## Files to Create/Modify

- `tests/test_cli_core.py` (new or extend existing)
- Possibly `tests/conftest.py` (add fixtures if needed)

---

## After Implementation

1. Run tests: `pytest tests/test_cli_core.py -v`
2. Check coverage: `pytest tests/ --cov=adversarial_workflow.cli`
3. Verify coverage >= 50%
4. Run full CI: `./scripts/ci-check.sh`
5. Commit and push
