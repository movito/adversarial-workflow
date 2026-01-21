# ADV-0017 Task Starter

## Quick Context

You are implementing the generic evaluator runner that works with any EvaluatorConfig. This eliminates ~200 lines of duplicated code from `evaluate()` and `proofread()` functions and enables custom evaluators.

**Branch**: `feature/adv-0017-generic-evaluator-runner`
**Base**: `main`
**Depends On**: ADV-0015 (EvaluatorConfig), ADV-0016 (discovery) - both merged
**Target Version**: v0.6.0

## Create Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/adv-0017-generic-evaluator-runner
```

## Files to Create/Modify

### 1. Create `adversarial_workflow/utils/__init__.py`

```python
"""Shared utilities for adversarial-workflow."""

from .colors import RESET, BOLD, GREEN, YELLOW, RED, CYAN, GRAY
from .config import load_config
from .validation import validate_evaluation_output

__all__ = [
    "RESET", "BOLD", "GREEN", "YELLOW", "RED", "CYAN", "GRAY",
    "load_config",
    "validate_evaluation_output",
]
```

### 2. Create `adversarial_workflow/utils/colors.py`

```python
"""Terminal color constants."""

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"
```

### 3. Create `adversarial_workflow/utils/config.py`

```python
"""Configuration loading utilities."""

from __future__ import annotations

import os
from typing import Dict

import yaml


def load_config(config_path: str = ".adversarial/config.yml") -> Dict:
    """Load configuration from YAML file with environment variable overrides."""
    # Default configuration
    config = {
        "evaluator_model": "gpt-4o",
        "task_directory": "tasks/",
        "test_command": "pytest",
        "log_directory": ".adversarial/logs/",
        "artifacts_directory": ".adversarial/artifacts/",
    }

    # Load from file if exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            file_config = yaml.safe_load(f) or {}
            config.update(file_config)

    # Override with environment variables
    env_overrides = {
        "ADVERSARIAL_EVALUATOR_MODEL": "evaluator_model",
        "ADVERSARIAL_TEST_COMMAND": "test_command",
        "ADVERSARIAL_LOG_DIR": "log_directory",
    }

    for env_var, config_key in env_overrides.items():
        value = os.getenv(env_var)
        if value:
            config[config_key] = value

    return config
```

### 4. Create `adversarial_workflow/utils/validation.py`

```python
"""Output validation utilities."""

from __future__ import annotations

import os
import re
from typing import Optional, Tuple


def validate_evaluation_output(
    log_file_path: str,
) -> Tuple[bool, Optional[str], str]:
    """
    Validate that evaluation log contains actual evaluation content.

    Args:
        log_file_path: Path to the evaluation log file

    Returns:
        (is_valid, verdict, message):
            - is_valid: True if valid evaluation, False if failed
            - verdict: "APPROVED", "NEEDS_REVISION", "REJECTED", or None
            - message: Descriptive message about validation result
    """
    if not os.path.exists(log_file_path):
        return False, None, f"Log file not found: {log_file_path}"

    with open(log_file_path, "r") as f:
        content = f.read()

    # Check minimum content size
    if len(content) < 500:
        return (
            False,
            None,
            f"Log file too small ({len(content)} bytes) - evaluation likely failed",
        )

    # Check for evaluation markers
    evaluation_markers = [
        "Verdict:",
        "APPROVED",
        "NEEDS_REVISION",
        "REJECTED",
        "Evaluation Summary",
        "Strengths",
        "Concerns",
    ]

    has_evaluation_content = any(marker in content for marker in evaluation_markers)
    if not has_evaluation_content:
        return (
            False,
            None,
            "Log file missing evaluation content - no verdict or analysis found",
        )

    # Extract verdict
    verdict = None
    verdict_patterns = [
        r"Verdict:\s*(APPROVED|NEEDS_REVISION|REJECTED)",
        r"\*\*Verdict\*\*:\s*(APPROVED|NEEDS_REVISION|REJECTED)",
        r"^(APPROVED|NEEDS_REVISION|REJECTED)\s*$",
    ]

    for pattern in verdict_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            verdict = match.group(1).upper()
            break

    if verdict:
        return True, verdict, f"Valid evaluation with verdict: {verdict}"
    else:
        # Has content but no clear verdict
        return True, None, "Evaluation complete (verdict not detected)"
```

### 5. Create `adversarial_workflow/evaluators/builtins.py`

```python
"""Built-in evaluator configurations."""

from __future__ import annotations

from .config import EvaluatorConfig

# Built-in evaluators use shell scripts - prompts are in the scripts
BUILTIN_EVALUATORS: dict[str, EvaluatorConfig] = {
    "evaluate": EvaluatorConfig(
        name="evaluate",
        description="Plan evaluation (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="",  # Prompt is in shell script
        output_suffix="PLAN-EVALUATION",
        source="builtin",
    ),
    "proofread": EvaluatorConfig(
        name="proofread",
        description="Teaching content review (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="",  # Prompt is in shell script
        output_suffix="PROOFREADING",
        source="builtin",
    ),
    "review": EvaluatorConfig(
        name="review",
        description="Code review (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="",  # Prompt is in shell script
        output_suffix="CODE-REVIEW",
        source="builtin",
    ),
}
```

### 6. Create `adversarial_workflow/evaluators/runner.py`

```python
"""Generic evaluator runner."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from .config import EvaluatorConfig
from ..utils.colors import RESET, BOLD, GREEN, YELLOW, RED
from ..utils.config import load_config
from ..utils.validation import validate_evaluation_output


def run_evaluator(config: EvaluatorConfig, file_path: str, timeout: int = 180) -> int:
    """Run an evaluator on a file.

    Args:
        config: Evaluator configuration
        file_path: Path to file to evaluate
        timeout: Timeout in seconds (default: 180)

    Returns:
        0 on success, non-zero on failure
    """
    prefix = config.log_prefix or config.name.upper()
    print(f"{prefix}: Evaluating {file_path}")
    print()

    # 1. Validate file exists
    if not os.path.exists(file_path):
        print(f"{RED}Error: File not found: {file_path}{RESET}")
        return 1

    # 2. Load project config
    try:
        project_config = load_config()
    except FileNotFoundError:
        print(f"{RED}Error: Not initialized. Run 'adversarial init' first.{RESET}")
        return 1

    # 3. Check aider available
    if not shutil.which("aider"):
        print(f"{RED}Error: Aider not found{RESET}")
        _print_aider_help()
        return 1

    # 4. Check API key
    api_key = os.environ.get(config.api_key_env)
    if not api_key:
        print(f"{RED}Error: {config.api_key_env} not set{RESET}")
        print(f"   Set in .env or export {config.api_key_env}=your-key")
        return 1

    # 5. Pre-flight file size check
    line_count, estimated_tokens = _check_file_size(file_path)
    if line_count > 500 or estimated_tokens > 20000:
        _warn_large_file(line_count, estimated_tokens)
        if line_count > 700:
            if not _confirm_continue():
                print("Evaluation cancelled.")
                return 0

    # 6. Determine execution method
    if config.source == "builtin":
        return _run_builtin_evaluator(config, file_path, project_config, timeout)
    else:
        return _run_custom_evaluator(config, file_path, project_config, timeout)


def _run_builtin_evaluator(
    config: EvaluatorConfig,
    file_path: str,
    project_config: dict,
    timeout: int,
) -> int:
    """Run a built-in evaluator using existing shell scripts."""
    script_map = {
        "evaluate": ".adversarial/scripts/evaluate_plan.sh",
        "proofread": ".adversarial/scripts/proofread_content.sh",
        "review": ".adversarial/scripts/code_review.sh",
    }

    script = script_map.get(config.name)
    if not script or not os.path.exists(script):
        print(f"{RED}Error: Script not found: {script}{RESET}")
        print("   Fix: Run 'adversarial init' to reinstall scripts")
        return 1

    return _execute_script(script, file_path, config, project_config, timeout)


def _run_custom_evaluator(
    config: EvaluatorConfig,
    file_path: str,
    project_config: dict,
    timeout: int,
) -> int:
    """Run a custom evaluator by invoking aider directly."""
    # Prepare output path
    logs_dir = Path(project_config["log_directory"])
    logs_dir.mkdir(parents=True, exist_ok=True)

    file_basename = Path(file_path).stem
    output_file = logs_dir / f"{file_basename}-{config.output_suffix}.md"

    # Read input file
    file_content = Path(file_path).read_text()

    # Build full prompt
    full_prompt = f"""{config.prompt}

---

## Document to Evaluate

**File**: {file_path}

{file_content}
"""

    # Create temp file for prompt
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(full_prompt)
        prompt_file = f.name

    prefix = config.log_prefix or config.name.upper()

    try:
        print(f"{prefix}: Using model {config.model}")

        # Build aider command
        cmd = [
            "aider",
            "--model", config.model,
            "--yes",
            "--no-git",
            "--no-auto-commits",
            "--message-file", prompt_file,
            "--read", file_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ,
        )

        # Check for errors
        output = result.stdout + result.stderr
        if "RateLimitError" in output or "tokens per min" in output:
            _print_rate_limit_error(file_path)
            return 1

        # Write output
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"""# {config.output_suffix.replace('-', ' ').replace('_', ' ').title()}

**Source**: {file_path}
**Evaluator**: {config.name}
**Model**: {config.model}
**Generated**: {timestamp}

---

"""
        output_file.write_text(header + result.stdout)

        print(f"{prefix}: Output written to {output_file}")

        # Validate output and determine verdict
        is_valid, verdict, message = validate_evaluation_output(str(output_file))

        if not is_valid:
            print(f"{RED}Evaluation failed: {message}{RESET}")
            return 1

        return _report_verdict(verdict, output_file, config)

    except subprocess.TimeoutExpired:
        _print_timeout_error(timeout)
        return 1
    except FileNotFoundError:
        _print_platform_error()
        return 1
    finally:
        Path(prompt_file).unlink(missing_ok=True)


def _execute_script(
    script: str,
    file_path: str,
    config: EvaluatorConfig,
    project_config: dict,
    timeout: int,
) -> int:
    """Execute a shell script evaluator."""
    try:
        result = subprocess.run(
            [script, file_path],
            text=True,
            capture_output=True,
            timeout=timeout,
        )

        # Check for rate limit errors
        output = result.stdout + result.stderr
        if "RateLimitError" in output or "tokens per min" in output:
            _print_rate_limit_error(file_path)
            return 1

    except subprocess.TimeoutExpired:
        _print_timeout_error(timeout)
        return 1
    except FileNotFoundError:
        _print_platform_error()
        return 1

    # Validate output
    file_basename = Path(file_path).stem
    log_file = Path(project_config["log_directory"]) / f"{file_basename}-{config.output_suffix}.md"

    is_valid, verdict, message = validate_evaluation_output(str(log_file))

    if not is_valid:
        print(f"{RED}Evaluation failed: {message}{RESET}")
        return 1

    return _report_verdict(verdict, log_file, config)


def _report_verdict(verdict: str | None, log_file: Path, config: EvaluatorConfig) -> int:
    """Report the evaluation verdict to terminal."""
    print()
    if verdict == "APPROVED":
        print(f"{GREEN}Evaluation APPROVED!{RESET}")
        print(f"   Review output: {log_file}")
        return 0
    elif verdict == "NEEDS_REVISION":
        print(f"{YELLOW}Evaluation NEEDS_REVISION{RESET}")
        print(f"   Details: {log_file}")
        return 1
    elif verdict == "REJECTED":
        print(f"{RED}Evaluation REJECTED{RESET}")
        print(f"   Details: {log_file}")
        return 1
    else:
        print(f"{YELLOW}Evaluation complete (verdict: {verdict}){RESET}")
        print(f"   Review output: {log_file}")
        return 0


# Helper functions
def _check_file_size(file_path: str) -> tuple[int, int]:
    """Return (line_count, estimated_tokens)."""
    with open(file_path, "r") as f:
        lines = f.readlines()
        f.seek(0)
        content = f.read()
    return len(lines), len(content) // 4


def _warn_large_file(line_count: int, tokens: int) -> None:
    """Print large file warning."""
    print(f"{YELLOW}Large file detected:{RESET}")
    print(f"   Lines: {line_count:,}")
    print(f"   Estimated tokens: ~{tokens:,}")
    print()


def _confirm_continue() -> bool:
    """Ask user to confirm continuing with large file."""
    response = input("Continue anyway? [y/N]: ").strip().lower()
    return response in ["y", "yes"]


def _print_aider_help() -> None:
    """Print aider installation help."""
    print()
    print(f"{BOLD}FIX:{RESET}")
    print("   1. Install aider: pip install aider-chat")
    print("   2. Verify: aider --version")


def _print_rate_limit_error(file_path: str) -> None:
    """Print rate limit error with suggestions."""
    print(f"{RED}Error: API rate limit exceeded{RESET}")
    print()
    print(f"{BOLD}SOLUTIONS:{RESET}")
    print("   1. Split into smaller documents (<500 lines)")
    print("   2. Upgrade your API tier")
    print("   3. Wait and retry")


def _print_timeout_error(timeout: int) -> None:
    """Print timeout error."""
    print(f"{RED}Error: Evaluation timed out (>{timeout}s){RESET}")


def _print_platform_error() -> None:
    """Print platform compatibility error."""
    if platform.system() == "Windows":
        print(f"{RED}Error: Windows not supported{RESET}")
        print("   Use WSL (Windows Subsystem for Linux)")
    else:
        print(f"{RED}Error: Script not found{RESET}")
        print("   Run: adversarial init")
```

### 7. Update `adversarial_workflow/evaluators/__init__.py`

```python
"""Evaluators module for adversarial-workflow plugin architecture."""

from .config import EvaluatorConfig
from .discovery import (
    discover_local_evaluators,
    parse_evaluator_yaml,
    EvaluatorParseError,
)
from .runner import run_evaluator
from .builtins import BUILTIN_EVALUATORS


def get_all_evaluators() -> dict[str, EvaluatorConfig]:
    """Get all available evaluators (built-in + local).

    Local evaluators override built-in evaluators with the same name.
    Aliases are also included in the returned dictionary.
    """
    import logging
    logger = logging.getLogger(__name__)

    evaluators: dict[str, EvaluatorConfig] = {}

    # Add built-in evaluators first
    evaluators.update(BUILTIN_EVALUATORS)

    # Discover and add local evaluators (may override built-ins)
    local = discover_local_evaluators()
    for name, config in local.items():
        if name in BUILTIN_EVALUATORS:
            logger.info("Local evaluator '%s' overrides built-in", name)
        evaluators[name] = config

    return evaluators


__all__ = [
    "EvaluatorConfig",
    "EvaluatorParseError",
    "run_evaluator",
    "get_all_evaluators",
    "discover_local_evaluators",
    "parse_evaluator_yaml",
    "BUILTIN_EVALUATORS",
]
```

### 8. Create `tests/test_evaluator_runner.py`

```python
"""Tests for the generic evaluator runner."""

import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from adversarial_workflow.evaluators.config import EvaluatorConfig
from adversarial_workflow.evaluators.runner import (
    run_evaluator,
    _check_file_size,
    _report_verdict,
)


@pytest.fixture
def sample_config():
    """Create a sample evaluator config for testing."""
    return EvaluatorConfig(
        name="test",
        description="Test evaluator",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="Test prompt",
        output_suffix="TEST-EVAL",
        source="custom",
    )


@pytest.fixture
def builtin_config():
    """Create a built-in evaluator config for testing."""
    return EvaluatorConfig(
        name="evaluate",
        description="Plan evaluation",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt="",
        output_suffix="PLAN-EVALUATION",
        source="builtin",
    )


class TestRunEvaluatorErrors:
    """Test error handling in run_evaluator."""

    def test_file_not_found(self, sample_config, capsys):
        """Error when file doesn't exist."""
        result = run_evaluator(sample_config, "/nonexistent/file.md")
        assert result == 1
        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_not_initialized(self, sample_config, tmp_path, monkeypatch, capsys):
        """Error when project not initialized."""
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        # Change to tmp_path (no .adversarial directory)
        monkeypatch.chdir(tmp_path)

        result = run_evaluator(sample_config, str(test_file))
        assert result == 1
        captured = capsys.readouterr()
        assert "Not initialized" in captured.out or "init" in captured.out.lower()

    def test_no_api_key(self, sample_config, tmp_path, monkeypatch, capsys):
        """Error when API key not set."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        result = run_evaluator(sample_config, str(test_file))
        assert result == 1
        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.out

    def test_no_aider(self, sample_config, tmp_path, monkeypatch, capsys):
        """Error when aider not installed."""
        # Create test file and config
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        config_dir = tmp_path / ".adversarial"
        config_dir.mkdir()
        (config_dir / "config.yml").write_text("log_directory: .adversarial/logs/")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setattr(shutil, "which", lambda x: None)

        result = run_evaluator(sample_config, str(test_file))
        assert result == 1
        captured = capsys.readouterr()
        assert "Aider not found" in captured.out


class TestCheckFileSize:
    """Test file size checking."""

    def test_small_file(self, tmp_path):
        """Small file returns correct counts."""
        test_file = tmp_path / "small.md"
        test_file.write_text("Line 1\nLine 2\nLine 3")

        lines, tokens = _check_file_size(str(test_file))
        assert lines == 3
        assert tokens > 0

    def test_large_file(self, tmp_path):
        """Large file returns correct counts."""
        test_file = tmp_path / "large.md"
        content = "x" * 10000  # 10k characters
        test_file.write_text(content)

        lines, tokens = _check_file_size(str(test_file))
        assert tokens == 2500  # 10000 / 4


class TestReportVerdict:
    """Test verdict reporting."""

    def test_approved(self, sample_config, tmp_path, capsys):
        """APPROVED verdict returns 0."""
        log_file = tmp_path / "test.md"
        log_file.write_text("test")

        result = _report_verdict("APPROVED", log_file, sample_config)
        assert result == 0
        captured = capsys.readouterr()
        assert "APPROVED" in captured.out

    def test_needs_revision(self, sample_config, tmp_path, capsys):
        """NEEDS_REVISION verdict returns 1."""
        log_file = tmp_path / "test.md"
        log_file.write_text("test")

        result = _report_verdict("NEEDS_REVISION", log_file, sample_config)
        assert result == 1
        captured = capsys.readouterr()
        assert "NEEDS_REVISION" in captured.out

    def test_rejected(self, sample_config, tmp_path, capsys):
        """REJECTED verdict returns 1."""
        log_file = tmp_path / "test.md"
        log_file.write_text("test")

        result = _report_verdict("REJECTED", log_file, sample_config)
        assert result == 1
        captured = capsys.readouterr()
        assert "REJECTED" in captured.out

    def test_unknown_verdict(self, sample_config, tmp_path, capsys):
        """Unknown verdict returns 0."""
        log_file = tmp_path / "test.md"
        log_file.write_text("test")

        result = _report_verdict(None, log_file, sample_config)
        assert result == 0


class TestBuiltinEvaluators:
    """Test built-in evaluator configurations."""

    def test_builtin_evaluators_exist(self):
        """All built-in evaluators are defined."""
        from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS

        assert "evaluate" in BUILTIN_EVALUATORS
        assert "proofread" in BUILTIN_EVALUATORS
        assert "review" in BUILTIN_EVALUATORS

    def test_builtin_evaluators_are_builtin_source(self):
        """Built-in evaluators have source='builtin'."""
        from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS

        for name, config in BUILTIN_EVALUATORS.items():
            assert config.source == "builtin", f"{name} should have source='builtin'"


class TestGetAllEvaluators:
    """Test get_all_evaluators function."""

    def test_returns_builtins(self, tmp_path, monkeypatch):
        """Returns built-in evaluators when no local evaluators."""
        monkeypatch.chdir(tmp_path)

        from adversarial_workflow.evaluators import get_all_evaluators
        evaluators = get_all_evaluators()

        assert "evaluate" in evaluators
        assert "proofread" in evaluators
        assert "review" in evaluators

    def test_local_overrides_builtin(self, tmp_path, monkeypatch):
        """Local evaluator overrides built-in with same name."""
        # Create local evaluator that overrides 'evaluate'
        eval_dir = tmp_path / ".adversarial" / "evaluators"
        eval_dir.mkdir(parents=True)
        (eval_dir / "evaluate.yml").write_text("""
name: evaluate
description: Custom evaluate
model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
prompt: Custom prompt
output_suffix: CUSTOM-EVAL
""")

        monkeypatch.chdir(tmp_path)

        from adversarial_workflow.evaluators import get_all_evaluators
        evaluators = get_all_evaluators()

        # Should have the local version
        assert evaluators["evaluate"].model == "gpt-4o-mini"
        assert evaluators["evaluate"].source == "local"


class TestUtilsModule:
    """Test utils module exports."""

    def test_colors_import(self):
        """Color constants are importable."""
        from adversarial_workflow.utils.colors import (
            RESET, BOLD, GREEN, YELLOW, RED, CYAN, GRAY
        )
        assert RESET == "\033[0m"
        assert BOLD == "\033[1m"

    def test_config_import(self):
        """load_config is importable."""
        from adversarial_workflow.utils.config import load_config
        assert callable(load_config)

    def test_validation_import(self):
        """validate_evaluation_output is importable."""
        from adversarial_workflow.utils.validation import validate_evaluation_output
        assert callable(validate_evaluation_output)
```

### 9. Create `tests/test_utils_validation.py`

```python
"""Tests for validation utilities."""

import pytest
from adversarial_workflow.utils.validation import validate_evaluation_output


class TestValidateEvaluationOutput:
    """Test validate_evaluation_output function."""

    def test_file_not_found(self):
        """Returns invalid when file doesn't exist."""
        is_valid, verdict, message = validate_evaluation_output("/nonexistent.md")
        assert is_valid is False
        assert verdict is None
        assert "not found" in message.lower()

    def test_file_too_small(self, tmp_path):
        """Returns invalid when file is too small."""
        log_file = tmp_path / "small.md"
        log_file.write_text("tiny")

        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        assert is_valid is False
        assert verdict is None
        assert "too small" in message.lower()

    def test_missing_evaluation_content(self, tmp_path):
        """Returns invalid when no evaluation markers found."""
        log_file = tmp_path / "no_eval.md"
        log_file.write_text("x" * 600)  # Big enough but no markers

        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        assert is_valid is False
        assert verdict is None

    def test_approved_verdict(self, tmp_path):
        """Extracts APPROVED verdict correctly."""
        log_file = tmp_path / "approved.md"
        log_file.write_text("""
# Evaluation Summary

**Verdict**: APPROVED

## Strengths
- Good implementation
""" + "x" * 500)

        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "APPROVED"

    def test_needs_revision_verdict(self, tmp_path):
        """Extracts NEEDS_REVISION verdict correctly."""
        log_file = tmp_path / "needs_rev.md"
        log_file.write_text("""
# Evaluation Summary

Verdict: NEEDS_REVISION

## Concerns
- Missing tests
""" + "x" * 500)

        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "NEEDS_REVISION"

    def test_rejected_verdict(self, tmp_path):
        """Extracts REJECTED verdict correctly."""
        log_file = tmp_path / "rejected.md"
        log_file.write_text("""
# Evaluation Summary

Verdict: REJECTED

## Critical Issues
- Security vulnerability
""" + "x" * 500)

        is_valid, verdict, message = validate_evaluation_output(str(log_file))
        assert is_valid is True
        assert verdict == "REJECTED"
```

## Update pyproject.toml

Add utils to the packages list if using explicit package discovery:

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["adversarial_workflow*"]
```

Or ensure auto-discovery is enabled (already done in ADV-0015).

## Verify

```bash
# Run all tests
pytest tests/ -v

# Run just the new tests
pytest tests/test_evaluator_runner.py tests/test_utils_validation.py -v

# Verify imports work
python -c "from adversarial_workflow.evaluators import run_evaluator, get_all_evaluators, BUILTIN_EVALUATORS; print('OK')"
python -c "from adversarial_workflow.utils import load_config, validate_evaluation_output; print('OK')"
```

## Commit and PR

```bash
git add .
git commit -m "feat(evaluators): Add generic evaluator runner (ADV-0017)

- Create utils/ module with colors, config, validation
- Add run_evaluator() supporting built-in and custom evaluators
- Define BUILTIN_EVALUATORS for evaluate, proofread, review
- Add get_all_evaluators() combining built-in and local
- Comprehensive test coverage

Co-Authored-By: Claude <noreply@anthropic.com>"

git push -u origin feature/adv-0017-generic-evaluator-runner

gh pr create --title "feat(evaluators): Add generic evaluator runner (ADV-0017)" --body "## Summary
- Creates \`utils/\` module with shared utilities (colors, config, validation)
- Adds \`run_evaluator()\` function that works with any EvaluatorConfig
- Defines BUILTIN_EVALUATORS for evaluate, proofread, review
- Adds \`get_all_evaluators()\` combining built-in and local evaluators

## Test Plan
- [ ] All existing tests pass
- [ ] New unit tests for runner error handling
- [ ] New tests for validation utilities
- [ ] Import verification

Part of plugin architecture epic (ADV-0013)
Depends on: ADV-0015, ADV-0016"
```

## Acceptance Checklist

- [ ] `adversarial_workflow/utils/` directory created with colors.py, config.py, validation.py
- [ ] `run_evaluator()` works for built-in evaluators
- [ ] `run_evaluator()` works for custom evaluators
- [ ] File validation before execution
- [ ] API key validation with helpful error
- [ ] Timeout handling
- [ ] Rate limit detection
- [ ] Output validation and verdict extraction
- [ ] Unit tests cover error paths
- [ ] All existing tests still pass
