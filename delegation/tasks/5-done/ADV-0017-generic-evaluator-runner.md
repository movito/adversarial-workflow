# ADV-0017: Generic Evaluator Runner

**Status**: Todo
**Priority**: High
**Estimated Effort**: 4-5 hours
**Target Version**: v0.6.0
**Parent Epic**: ADV-0013
**Depends On**: ADV-0015, ADV-0016
**Branch**: `feature/plugin-architecture`

## Summary

Extract common evaluation logic from `evaluate()` and `proofread()` into a generic `run_evaluator()` function that works with any `EvaluatorConfig`. This eliminates ~200 lines of duplicated code and enables custom evaluators.

## Background

Current state: `evaluate()` and `proofread()` in `cli.py` are nearly identical (~220 lines each), differing only in:
- Script path
- Log file suffix
- Terminal messages

This duplication makes maintenance error-prone and prevents custom evaluators.

## Architectural Decisions

### Circular Import Prevention

To avoid circular imports between `cli.py` and `runner.py`:

1. **Move shared utilities to `utils/config.py`**:
   - `load_config()` - loads `.adversarial/config.yml`
   - `validate_evaluation_output()` - checks evaluation output format

2. **Move color constants to `utils/colors.py`**:
   - RESET, BOLD, GREEN, YELLOW, RED, CYAN, GRAY

3. **Import path**: `runner.py` imports from `utils/`, not `cli.py`

### Built-in vs Custom Evaluator Execution

**Built-in evaluators** (`evaluate`, `proofread`, `review`):
- Continue using existing shell scripts in `.adversarial/scripts/`
- Prompts remain in shell scripts (no extraction needed for v0.6.0)
- Runner calls shell scripts via subprocess

**Custom evaluators** (from `.adversarial/evaluators/*.yml`):
- Prompt is in YAML file
- Runner invokes aider directly (no shell script)

This hybrid approach minimizes changes to existing functionality while enabling custom evaluators.

## Requirements

### New File Structure

```text
adversarial_workflow/
├── utils/
│   ├── __init__.py
│   ├── config.py       # MOVED: load_config()
│   ├── validation.py   # MOVED: validate_evaluation_output()
│   └── colors.py       # NEW: Shared color constants
└── evaluators/
    ├── __init__.py     # Updated exports
    ├── config.py       # From ADV-0015
    ├── discovery.py    # From ADV-0016
    └── runner.py       # NEW: Generic runner
```

### Runner Implementation

```python
# adversarial_workflow/evaluators/runner.py

import os
import shutil
import subprocess
import platform
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
        print(f"{RED}❌ ERROR: File not found: {file_path}{RESET}")
        return 1

    # 2. Load project config
    try:
        project_config = load_config()
    except FileNotFoundError:
        print(f"{RED}❌ ERROR: Not initialized. Run 'adversarial init' first.{RESET}")
        return 1

    # 3. Check aider available
    if not shutil.which("aider"):
        print(f"{RED}❌ ERROR: Aider not found{RESET}")
        _print_aider_help()
        return 1

    # 4. Check API key
    api_key = os.environ.get(config.api_key_env)
    if not api_key:
        print(f"{RED}❌ ERROR: {config.api_key_env} not set{RESET}")
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
    # Map config name to script
    script_map = {
        "evaluate": ".adversarial/scripts/evaluate_plan.sh",
        "proofread": ".adversarial/scripts/proofread_content.sh",
        "review": ".adversarial/scripts/code_review.sh",
    }

    script = script_map.get(config.name)
    if not script or not os.path.exists(script):
        print(f"{RED}❌ ERROR: Script not found: {script}{RESET}")
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
    import tempfile
    from datetime import datetime

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
        # validate_evaluation_output already imported at top of file
        is_valid, verdict, message = validate_evaluation_output(str(output_file))

        if not is_valid:
            print(f"{RED}❌ Evaluation failed: {message}{RESET}")
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

    if result.returncode != 0:
        print()
        print(f"📋 Evaluation complete (needs revision)")
        print(f"   Details: {project_config['log_directory']}")
        return result.returncode

    # Validate output
    file_basename = Path(file_path).stem
    log_file = Path(project_config["log_directory"]) / f"{file_basename}-{config.output_suffix}.md"

    # validate_evaluation_output imported at top from utils.validation
    is_valid, verdict, message = validate_evaluation_output(str(log_file))

    if not is_valid:
        print(f"{RED}❌ Evaluation failed: {message}{RESET}")
        return 1

    return _report_verdict(verdict, log_file, config)


def _report_verdict(verdict: str, log_file: Path, config: EvaluatorConfig) -> int:
    """Report the evaluation verdict to terminal."""
    print()
    if verdict == "APPROVED":
        print(f"{GREEN}✅ {config.name.title()} APPROVED!{RESET}")
        print(f"   Review output: {log_file}")
        return 0
    elif verdict == "NEEDS_REVISION":
        print(f"{YELLOW}⚠️  {config.name.title()} NEEDS_REVISION{RESET}")
        print(f"   Details: {log_file}")
        return 1
    elif verdict == "REJECTED":
        print(f"{RED}❌ {config.name.title()} REJECTED{RESET}")
        print(f"   Details: {log_file}")
        return 1
    else:
        print(f"{YELLOW}⚠️  Evaluation complete (verdict: {verdict}){RESET}")
        print(f"   Review output: {log_file}")
        return 0


# Helper functions (extracted from evaluate/proofread)
def _check_file_size(file_path: str) -> tuple[int, int]:
    """Return (line_count, estimated_tokens)."""
    with open(file_path, "r") as f:
        lines = f.readlines()
        f.seek(0)
        content = f.read()
    return len(lines), len(content) // 4


def _warn_large_file(line_count: int, tokens: int) -> None:
    """Print large file warning."""
    print(f"{YELLOW}⚠️  Large file detected:{RESET}")
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
    print(f"{RED}❌ ERROR: API rate limit exceeded{RESET}")
    print()
    print(f"{BOLD}SOLUTIONS:{RESET}")
    print("   1. Split into smaller documents (<500 lines)")
    print("   2. Upgrade your API tier")
    print("   3. Wait and retry")


def _print_timeout_error(timeout: int) -> None:
    """Print timeout error."""
    print(f"{RED}❌ ERROR: Evaluation timed out (>{timeout}s){RESET}")


def _print_platform_error() -> None:
    """Print platform compatibility error."""
    if platform.system() == "Windows":
        print(f"{RED}❌ ERROR: Windows not supported{RESET}")
        print("   Use WSL (Windows Subsystem for Linux)")
    else:
        print(f"{RED}❌ ERROR: Script not found{RESET}")
        print("   Run: adversarial init")
```

### Define Built-in Evaluators

```python
# adversarial_workflow/evaluators/builtins.py

from .config import EvaluatorConfig

# These prompts are extracted from existing shell scripts
EVALUATE_PROMPT = """..."""  # From evaluate_plan.sh
PROOFREAD_PROMPT = """..."""  # From proofread_content.sh
REVIEW_PROMPT = """..."""  # From code_review.sh

BUILTIN_EVALUATORS: dict[str, EvaluatorConfig] = {
    "evaluate": EvaluatorConfig(
        name="evaluate",
        description="Plan evaluation (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt=EVALUATE_PROMPT,
        output_suffix="PLAN-EVALUATION",
        source="builtin",
    ),
    "proofread": EvaluatorConfig(
        name="proofread",
        description="Teaching content review (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt=PROOFREAD_PROMPT,
        output_suffix="PROOFREADING",
        source="builtin",
    ),
    "review": EvaluatorConfig(
        name="review",
        description="Code review (GPT-4o)",
        model="gpt-4o",
        api_key_env="OPENAI_API_KEY",
        prompt=REVIEW_PROMPT,
        output_suffix="CODE-REVIEW",
        source="builtin",
    ),
}
```

### Update Module Exports

```python
# adversarial_workflow/evaluators/__init__.py
from .config import EvaluatorConfig
from .discovery import discover_local_evaluators, parse_evaluator_yaml, EvaluatorParseError
from .runner import run_evaluator
from .builtins import BUILTIN_EVALUATORS

def get_all_evaluators() -> dict[str, EvaluatorConfig]:
    """Get all available evaluators (built-in + local)."""
    evaluators = BUILTIN_EVALUATORS.copy()
    local = discover_local_evaluators()

    # Warn about overrides
    for name in local:
        if name in BUILTIN_EVALUATORS:
            import warnings
            warnings.warn(f"Local evaluator '{name}' overrides built-in")

    evaluators.update(local)
    return evaluators

__all__ = [
    "EvaluatorConfig",
    "run_evaluator",
    "get_all_evaluators",
    "discover_local_evaluators",
    "BUILTIN_EVALUATORS",
    "EvaluatorParseError",
]
```

## Testing Requirements

Create `tests/test_evaluator_runner.py`:

### Unit Tests (Mocked)

```python
def test_run_evaluator_file_not_found(tmp_path):
    """Error when file doesn't exist."""
    config = EvaluatorConfig(...)
    result = run_evaluator(config, "/nonexistent/file.md")
    assert result == 1

def test_run_evaluator_no_api_key(tmp_path, monkeypatch):
    """Error when API key not set."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = EvaluatorConfig(api_key_env="OPENAI_API_KEY", ...)
    # Create test file
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test")
    result = run_evaluator(config, str(test_file))
    assert result == 1

def test_run_evaluator_no_aider(tmp_path, monkeypatch):
    """Error when aider not installed."""
    monkeypatch.setattr(shutil, "which", lambda x: None)
    # ...
```

### Integration Test (Optional, Requires API Key)

```python
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="No API key")
def test_run_evaluator_real():
    """End-to-end test with real API call."""
    # Use smallest possible test file
    # ...
```

## Acceptance Criteria

- [ ] `run_evaluator()` works for built-in evaluators
- [ ] `run_evaluator()` works for custom evaluators
- [ ] File validation before execution
- [ ] API key validation with helpful error
- [ ] Timeout handling
- [ ] Rate limit detection
- [ ] Platform compatibility checks
- [ ] Output validation
- [ ] Verdict reporting (APPROVED/NEEDS_REVISION/REJECTED)
- [ ] Unit tests cover error paths
- [ ] Existing `evaluate` and `proofread` functionality preserved

## Migration Notes

After this task, the existing `evaluate()` and `proofread()` functions in `cli.py` can be simplified to:

```python
def evaluate(task_file: str) -> int:
    """Run Phase 1: Plan evaluation."""
    from .evaluators import BUILTIN_EVALUATORS, run_evaluator
    return run_evaluator(BUILTIN_EVALUATORS["evaluate"], task_file)
```

This simplification happens in ADV-0018 (CLI integration).

## References

- Parent Epic: ADV-0013-plugin-architecture-epic.md
- Depends On: ADV-0015, ADV-0016
- Current `evaluate()`: cli.py:1861-2085 (~220 lines)
- Current `proofread()`: cli.py:2088-2306 (~220 lines)
