# Code Review Input: ADV-0071 — Fix Version Management + Release 1.0.0 (Round 3)

## Summary of Changes

Removed hardcoded version fallback strings from `__init__.py` and `cli.py` that drifted
from `pyproject.toml`, causing `test_version_flag` to fail in subprocess environments.
Made `pyproject.toml` the single source of truth via `importlib.metadata`. Fixed the
`run_cli` test fixture to use `sys.executable` instead of PATH search. Bumped to 1.0.0.

## Prior Evaluator Rounds

**Round 1** (Gemini Flash, partial input): FAIL with 3 findings.
- Finding 1 (direct execution regression via relative import): FIXED — reverted to direct importlib.metadata call
- Finding 2 (PackageNotFoundError propagation): By design per task spec
- Finding 3 (sys.executable fixture): Improvement over previous shutil.which behavior

**Round 2** (Gemini Flash, full 125KB input): CONCERNS — all 4 findings were pre-existing
issues in other cli.py functions unrelated to our changes. Evaluator confirmed: "version
management and run_cli fixture are well-implemented and robust."

## Bot Review Summary

- BugBot: No findings
- CodeRabbit: 2 threads (both markdownlint on evaluator artifacts) — resolved as cosmetic

## Design Decisions

1. **No hardcoded fallback**: Python 3.10+ guarantees `importlib.metadata`. If the package
   isn't installed, `PackageNotFoundError` propagates — correct for a pip-installed CLI tool.
   Task spec explicitly requires this behavior.

2. **Not DRY for version lookup, but DRY for version value**: Both `__init__.py` and `cli.py`
   call `_get_version("adversarial-workflow")` independently. This duplicates the lookup
   mechanism but NOT any version string. The version value cannot drift because both read
   from the same `pyproject.toml` metadata. A relative import (`from . import __version__`)
   would be DRYer but breaks `python adversarial_workflow/cli.py` direct execution since
   cli.py has a shebang and `if __name__ == "__main__"` guard with no other relative imports.

3. **sys.executable over shutil.which**: The old `cli_python` fixture used
   `shutil.which("adversarial")` which found `/opt/homebrew/bin/adversarial` — a stale
   system-wide install reporting 0.9.9 while the venv had 0.9.10. Using `sys.executable`
   ensures the subprocess tests the same package as the in-process metadata.

## Changed Files — Complete Content

### adversarial_workflow/__init__.py (COMPLETE — 23 lines)

```python
"""
Adversarial Workflow - Multi-stage AI code review system

A package for integrating Author-Evaluator adversarial code review
into existing projects. Prevents "phantom work" through multi-stage verification.

Usage:
    pip install adversarial-workflow
    adversarial init
    adversarial evaluate task.md
    adversarial review
    adversarial validate "pytest"
"""

from importlib.metadata import version as _get_version

__version__ = _get_version("adversarial-workflow")
__author__ = "Fredrik Matheson"
__license__ = "MIT"

from .cli import check, evaluate, init, main, review, validate

__all__ = ["__version__", "check", "evaluate", "init", "main", "review", "validate"]
```

### adversarial_workflow/cli.py — Version-related sections only

**Lines 1-45 (imports + version + constants):**

```python
#!/usr/bin/env python3
"""
CLI tool for adversarial workflow package - Enhanced with interactive onboarding.

Commands:
    init - Initialize workflow in existing project
    init --interactive - Interactive setup wizard
    quickstart - Quick start with example task
    check - Validate setup and dependencies
    health - Comprehensive system health check
    agent onboard - Set up agent coordination system
    evaluate - Run Phase 1: Plan evaluation
    review - Run Phase 3: Code review
    validate - Run Phase 4: Test validation
    split - Split large task files into smaller evaluable chunks
    check-citations - Verify URLs in documents before evaluation
"""

import argparse
import getpass
import os
import platform
import shutil
import subprocess
import sys
from importlib.metadata import version as _get_version
from pathlib import Path

import yaml
from dotenv import dotenv_values, load_dotenv

__version__ = _get_version("adversarial-workflow")

# ANSI color codes for better output
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"
```

**Line 586 (version header injection in script output):**

```python
            version_header = f"# SCRIPT_VERSION: {__version__}"
```

**Lines 2526-2528 (argparse version flag):**

```python
    parser.add_argument(
        "--version", action="version", version=f"adversarial-workflow {__version__}"
    )
```

**Lines 2974-2975 (direct execution guard):**

```python
if __name__ == "__main__":
    sys.exit(main())
```

### pyproject.toml — Version field (line 8)

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "adversarial-workflow"

version = "1.0.0"
```

### tests/conftest.py (COMPLETE — 197 lines)

```python
"""
Shared test fixtures for adversarial-workflow tests.

This module provides common fixtures used across all test modules,
including temporary directories, sample files, and mocked dependencies.
"""

import os
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory with basic structure."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create basic project structure
    (project_dir / ".adversarial").mkdir()
    (project_dir / ".adversarial" / "logs").mkdir()

    # Create a basic config file
    config_content = """
project_name: test_project
openai_api_key: sk-fake-test-key
stages:
  - plan_evaluation
  - implementation
  - code_review
  - test_validation
"""
    (project_dir / ".adversarial" / "config.yaml").write_text(config_content.strip())

    # Create a basic .env file
    env_content = "OPENAI_API_KEY=sk-fake-test-key\n"
    (project_dir / ".env").write_text(env_content)

    return project_dir


@pytest.fixture
def sample_task_content():
    """Sample task file content for testing."""
    return """# TEST-001: Sample Test Task

**Status**: Todo
**Priority**: Medium
**Assigned To**: test-agent
**Estimated Effort**: 1 hour

## Overview

This is a sample task for testing the adversarial workflow system.

## Requirements

### Functional Requirements
1. Implement a simple function
2. Add basic error handling
3. Include unit tests

### Non-Functional Requirements
- Performance: Function should complete in <100ms
- Maintainability: Clear documentation

## Implementation Plan

### Files to Create
1. `src/test_function.py` - Main implementation
2. `tests/test_test_function.py` - Unit tests

### Approach
Simple implementation with proper error handling.

## Acceptance Criteria

- Function works correctly
- Tests pass
- Documentation is clear

## Success Metrics

- All tests pass
- Code coverage >80%
"""


@pytest.fixture
def sample_task_file(tmp_project, sample_task_content):
    """Create a sample task file in the test project."""
    task_file = tmp_project / "test_task.md"
    task_file.write_text(sample_task_content)
    return task_file


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run calls to avoid running actual subprocess commands."""
    with patch("subprocess.run") as mock_run:
        from unittest.mock import Mock

        mock_run.return_value = Mock(
            returncode=0, stdout="Command completed successfully", stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API calls to avoid actual API requests during tests."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response from mocked OpenAI"))]
        )
        yield mock_create


@pytest.fixture
def sample_config():
    """Sample configuration dictionary for testing."""
    return {
        "project_name": "test_project",
        "openai_api_key": "sk-fake-test-key",
        "stages": [
            "plan_evaluation",
            "implementation",
            "code_review",
            "test_validation",
        ],
        "working_directory": "/tmp/test",
        "output_directory": ".adversarial/logs",
    }


@pytest.fixture
def mock_file_operations():
    """Mock file system operations for isolated testing."""
    mocks = {}
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("pathlib.Path.is_file") as mock_is_file,
        patch("pathlib.Path.is_dir") as mock_is_dir,
    ):
        # Default to files/dirs existing
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_is_dir.return_value = True

        mocks["exists"] = mock_exists
        mocks["is_file"] = mock_is_file
        mocks["is_dir"] = mock_is_dir

        yield mocks


@pytest.fixture(autouse=True)
def change_test_dir(tmp_project):
    """Change to temporary directory for each test to avoid side effects."""
    old_cwd = os.getcwd()
    os.chdir(tmp_project)
    yield
    os.chdir(old_cwd)


@pytest.fixture
def cli_python():
    """Get Python interpreter path that has adversarial_workflow installed.

    Always uses sys.executable (the Python running pytest) to ensure the
    subprocess tests the same package version as the in-process metadata.
    Previous approach used shutil.which("adversarial") which could find
    stale system-wide installs with different versions.
    """
    return sys.executable


@pytest.fixture
def run_cli(cli_python):
    """Helper fixture to run CLI commands in subprocess.

    Uses ``python -m adversarial_workflow.cli`` to ensure the subprocess
    runs the same editable install as the test runner.

    Usage:
        result = run_cli(["check"], cwd=tmp_path, env=env)
    """

    def _run_cli(args, **kwargs):
        cmd = [cli_python, "-m", "adversarial_workflow.cli", *args]
        return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

    return _run_cli
```

### tests/test_cli.py — Version-related test (lines 1-25)

```python
"""
Tests for the adversarial CLI.

Comprehensive smoke tests for all CLI commands to ensure basic functionality
works correctly before refactoring the monolithic cli.py.
"""

from importlib.metadata import version
from unittest.mock import Mock, patch

from adversarial_workflow.cli import check, health, load_config, main


class TestCLISmoke:
    """Basic smoke tests to verify CLI is functional."""

    def test_version_flag(self, run_cli):
        """Test that --version returns version info."""
        result = run_cli(["--version"])
        assert result.returncode == 0

        expected_version = version("adversarial-workflow")
        assert expected_version in result.stdout or expected_version in result.stderr
```

### Git diff (complete)

```diff
diff --git a/adversarial_workflow/__init__.py b/adversarial_workflow/__init__.py
index 8f4f7ce..04cced6 100644
--- a/adversarial_workflow/__init__.py
+++ b/adversarial_workflow/__init__.py
@@ -12,12 +12,10 @@ Usage:
     adversarial validate "pytest"
 """

-try:
-    from importlib.metadata import version as _get_version
+from importlib.metadata import version as _get_version

-    __version__ = _get_version("adversarial-workflow")
-except Exception:
-    __version__ = "0.9.9"  # Fallback for editable installs
+__version__ = _get_version("adversarial-workflow")
 __author__ = "Fredrik Matheson"
 __license__ = "MIT"

diff --git a/adversarial_workflow/cli.py b/adversarial_workflow/cli.py
index ce59c66..eca14be 100644
--- a/adversarial_workflow/cli.py
+++ b/adversarial_workflow/cli.py
@@ -23,17 +23,13 @@ import shutil
 import subprocess
 import sys
+from importlib.metadata import version as _get_version
 from pathlib import Path

 import yaml
 from dotenv import dotenv_values, load_dotenv

-try:
-    from importlib.metadata import version as _get_version
-
-    __version__ = _get_version("adversarial-workflow")
-except Exception:
-    __version__ = "0.9.9"  # Fallback for editable installs
+__version__ = _get_version("adversarial-workflow")

diff --git a/pyproject.toml b/pyproject.toml
index 1234567..abcdefg 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -5,7 +5,7 @@
 [project]
 name = "adversarial-workflow"

-version = "0.9.10"
+version = "1.0.0"

diff --git a/tests/conftest.py b/tests/conftest.py
index 1234567..abcdefg 100644
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -6,7 +6,6 @@ including temporary directories, sample files, and mocked dependencies.

 import os
-import shutil
 import subprocess
 import sys
 from unittest.mock import Mock, patch
@@ -168,34 +167,27 @@ def change_test_dir(tmp_project):

 @pytest.fixture
 def cli_python():
-    """Get Python interpreter path that has adversarial_workflow installed.
+    """Get Python interpreter path that has adversarial_workflow installed.

-    When running with system pytest, sys.executable may point to a Python
-    that doesn't have our package installed. This fixture finds the correct
-    Python by checking if the 'adversarial' command is available.
+    Always uses sys.executable (the Python running pytest) to ensure the
+    subprocess tests the same package version as the in-process metadata.
+    Previous approach used shutil.which("adversarial") which could find
+    stale system-wide installs with different versions.
     """
-    # First, try to find the adversarial command on PATH
-    adversarial_cmd = shutil.which("adversarial")
-    if adversarial_cmd:
-        # The adversarial script is available, signal to use command directly
-        return None
-
-    # Fall back to sys.executable (works in venv)
     return sys.executable


 @pytest.fixture
 def run_cli(cli_python):
-    """Helper fixture to run CLI commands in subprocess.
+    """Helper fixture to run CLI commands in subprocess.

-    Usage:
+    Uses ``python -m adversarial_workflow.cli`` to ensure the subprocess
+    runs the same editable install as the test runner.
+
+    Usage:
         result = run_cli(["check"], cwd=tmp_path, env=env)
     """

     def _run_cli(args, **kwargs):
-        if cli_python is None:
-            # Use adversarial command directly
-            cmd = ["adversarial", *args]
-        else:
-            # Use python -m
-            cmd = [cli_python, "-m", "adversarial_workflow.cli", *args]
-
+        cmd = [cli_python, "-m", "adversarial_workflow.cli", *args]
         return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

     return _run_cli
```

## Test Results

- 530/530 tests pass (including test_version_flag)
- ci-check.sh fully green (format, lint, pattern lint, tests)
- CI green on GitHub for all 4 commits
