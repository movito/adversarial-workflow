"""Generic evaluator runner.

Supports dual-field model specification (ADV-0015):
- Legacy: model + api_key_env fields (backwards compatible)
- New: model_requirement field (resolved via ModelResolver)
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from ..utils.colors import BOLD, GREEN, RED, RESET, YELLOW
from ..utils.config import load_config
from ..utils.validation import validate_evaluation_output
from .config import EvaluatorConfig
from .resolver import ModelResolver, ResolutionError


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

    # 2. Load project config (check initialization first)
    config_path = Path(".adversarial/config.yml")
    if not config_path.exists():
        print(f"{RED}Error: Not initialized. Run 'adversarial init' first.{RESET}")
        return 1
    project_config = load_config()

    # 3. Resolve model (ADV-0015: dual-field support)
    resolver = ModelResolver()
    try:
        resolved_model, resolved_api_key_env = resolver.resolve(config)
    except ResolutionError as e:
        print(f"{RED}Error: {e}{RESET}")
        return 1

    # 4. Check aider available
    if not shutil.which("aider"):
        print(f"{RED}Error: Aider not found{RESET}")
        _print_aider_help()
        return 1

    # 5. Check API key (using resolved api_key_env)
    api_key = os.environ.get(resolved_api_key_env)
    if not api_key:
        print(f"{RED}Error: {resolved_api_key_env} not set{RESET}")
        print(f"   Set in .env or export {resolved_api_key_env}=your-key")
        return 1

    # 6. Pre-flight file size check
    line_count, estimated_tokens = _check_file_size(file_path)
    if line_count > 500 or estimated_tokens > 20000:
        _warn_large_file(line_count, estimated_tokens)
        if line_count > 700:
            if not _confirm_continue():
                print("Evaluation cancelled.")
                return 0

    # 7. Determine execution method
    if config.source == "builtin":
        return _run_builtin_evaluator(config, file_path, project_config, timeout)
    else:
        return _run_custom_evaluator(config, file_path, project_config, timeout, resolved_model)


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
    resolved_model: str,
) -> int:
    """Run a custom evaluator by invoking aider directly.

    Args:
        config: Evaluator configuration
        file_path: Path to file to evaluate
        project_config: Project configuration dict
        timeout: Timeout in seconds
        resolved_model: Resolved model ID from ModelResolver
    """
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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(full_prompt)
        prompt_file = f.name

    prefix = config.log_prefix or config.name.upper()

    try:
        print(f"{prefix}: Using model {resolved_model}")

        # Build aider command
        cmd = [
            "aider",
            "--model",
            resolved_model,
            "--yes",
            "--no-detect-urls",
            "--no-git",
            "--no-auto-commits",
            "--message-file",
            prompt_file,
            "--read",
            file_path,
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
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        header = f"""# {config.output_suffix.replace('-', ' ').replace('_', ' ').title()}

**Source**: {file_path}
**Evaluator**: {config.name}
**Model**: {resolved_model}
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
