# Code Review Input: ADV-0071 — Fix Version Management + Release 1.0.0 (Round 2)

## Summary of Changes

Removed hardcoded version fallback strings from `__init__.py` and `cli.py` that drifted
from `pyproject.toml`, causing `test_version_flag` to fail in subprocess environments.
Made `pyproject.toml` the single source of truth via `importlib.metadata`. Fixed the
`run_cli` test fixture to use `sys.executable` instead of PATH search. Bumped to 1.0.0.

## Round 1 Evaluator Findings and Response

Round 1 (code-reviewer-fast / Gemini Flash) returned FAIL with 3 findings:

1. **FIXED — Direct execution regression**: `from . import __version__` was the first
   relative import in cli.py, breaking `python adversarial_workflow/cli.py` direct execution.
   Reverted to direct `importlib.metadata.version()` call — no relative import, no hardcoded
   fallback, preserves shebang + `if __name__ == "__main__"` usage.

2. **By design — PackageNotFoundError propagation**: Task spec explicitly requires this:
   "If the package isn't installed, `_get_version()` raises `PackageNotFoundError` — this
   should propagate (not be silently swallowed), since an uninstalled package can't run anyway."

3. **Improvement — sys.executable fixture**: The old `shutil.which("adversarial")` found
   `/opt/homebrew/bin/adversarial` (stale 0.9.9 system install) while the venv had 0.9.10.
   Using `sys.executable` ensures subprocess tests the same package as in-process metadata.

## Bot Review Summary

- BugBot: No findings
- CodeRabbit: 2 threads (both markdownlint on evaluator input/output artifacts) — resolved as cosmetic on non-shipped content

## All Changed Files (complete content)

### adversarial_workflow/__init__.py (COMPLETE FILE)

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

### adversarial_workflow/cli.py (COMPLETE FILE — 2975 lines)

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


def print_box(title: str, lines: list[str], width: int = 70) -> None:
    """Print a nice box with content."""
    print()
    print("━" * width)
    if title:
        print(f"{BOLD}{title}{RESET}")
        print("━" * width)
    for line in lines:
        print(line)
    print("━" * width)
    print()


def prompt_user(prompt: str, default: str = "", secret: bool = False) -> str:
    """Prompt user for input with optional default."""
    if default:
        display_prompt = f"{prompt} [{GRAY}{default}{RESET}]: "
    else:
        display_prompt = f"{prompt}: "

    if secret:
        value = getpass.getpass(display_prompt)
    else:
        value = input(display_prompt).strip()

    return value if value else default


def validate_api_key(key: str, provider: str) -> tuple[bool, str]:
    """
    Validate an API key by checking its format.

    Returns: (is_valid, message)
    """
    if not key or key.startswith("your-") or key == "":
        return False, "Key is empty or placeholder"

    if provider == "openai":
        if not (key.startswith("sk-") or key.startswith("sk-proj-")):
            return False, "OpenAI keys should start with 'sk-' or 'sk-proj-'"
        if len(key) < 20:
            return False, "Key seems too short"
        return True, "Format looks valid"

    elif provider == "anthropic":
        if not key.startswith("sk-ant-"):
            return False, "Anthropic keys should start with 'sk-ant-'"
        if len(key) < 20:
            return False, "Key seems too short"
        return True, "Format looks valid"

    return True, "Format looks valid"


def check_platform_compatibility() -> bool:
    """Check if platform is supported and warn Windows users."""
    system = platform.system()

    if system == "Windows":
        print("\n" + "=" * 60)
        print("⚠️  WARNING: Native Windows is NOT Supported")
        print("=" * 60)
        print("\nThis package requires Unix shell (bash) for workflow scripts.")
        print("\n📍 RECOMMENDED: Use WSL (Windows Subsystem for Linux)")
        print("   Install: https://learn.microsoft.com/windows/wsl/install")
        print("\n⚠️  ALTERNATIVE: Git Bash (not officially supported)")
        print("   Some features may not work correctly")
        print("\n" + "=" * 60)

        response = input("\n Continue with setup anyway? (y/N): ").strip().lower()
        if response != "y":
            print("\nSetup cancelled. Please install WSL and try again.")
            return False

    return True


def create_env_file_interactive(
    project_path: str, anthropic_key: str = "", openai_key: str = ""
) -> bool:
    """
    Interactively create .env file with API keys.

    Returns: True if created successfully
    """
    env_path = os.path.join(project_path, ".env")

    # Check if .env already exists
    if os.path.exists(env_path):
        print(f"\n{YELLOW}⚠️  .env file already exists{RESET}")
        overwrite = prompt_user("Overwrite", default="n")
        if overwrite.lower() != "y":
            print("Skipping .env creation.")
            return False

    print_box(
        "Create .env File",
        [
            "I'll create a .env file with your API keys.",
            "",
            "This file will:",
            "  ✓ Store your API keys securely",
            "  ✓ Be added to .gitignore (won't be committed)",
            "  ✓ Be loaded automatically by the workflow",
        ],
    )

    create = prompt_user("Create .env file?", default="Y")

    if create.lower() not in ["y", "yes", ""]:
        print()
        print(f"{CYAN}No problem! Create .env manually:{RESET}")
        print()
        print("  1. Copy the example:")
        print("     cp .env.example .env")
        print()
        print("  2. Edit .env and add your keys:")
        print()
        print("     # Anthropic API (for Claude 3.5 Sonnet)")
        print("     ANTHROPIC_API_KEY=sk-ant-your-key-here")
        print()
        print("     # OpenAI API (for GPT-4o)")
        print("     OPENAI_API_KEY=sk-proj-your-key-here")
        print()
        print("  3. Verify setup:")
        print("     adversarial check")
        print()
        print("Get API keys:")
        print("  - Anthropic: https://console.anthropic.com/settings/keys")
        print("  - OpenAI: https://platform.openai.com/api-keys")
        print()
        return False

    # Create .env file
    env_content = "# Adversarial Workflow - API Keys\n"
    env_content += "# Generated by: adversarial init --interactive\n"
    env_content += "# DO NOT COMMIT THIS FILE\n\n"

    if anthropic_key:
        env_content += (
            f"# Anthropic API Key (Claude 3.5 Sonnet)\nANTHROPIC_API_KEY={anthropic_key}\n\n"
        )

    if openai_key:
        env_content += f"# OpenAI API Key (GPT-4o)\nOPENAI_API_KEY={openai_key}\n\n"

    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
        print(f"\n{GREEN}✅ Created .env with your API keys{RESET}")
        print(f"{GREEN}✅ Added .env to .gitignore{RESET}")
        print()
        print("Your API keys are safe and won't be committed to git.")
        return True
    except Exception as e:
        print(f"\n{RED}❌ Failed to create .env: {e}{RESET}")
        return False


def init_interactive(project_path: str = ".") -> int:
    """Interactive initialization wizard with API key setup."""

    # Check platform compatibility first
    if not check_platform_compatibility():
        return 1

    print(f"\n{BOLD}{CYAN}🚀 Welcome to Adversarial Workflow!{RESET}")
    print()
    print("This tool helps you write better code using AI-powered code review.")
    print()

    # Explain the two-API approach
    print(f"{BOLD}Why two AI APIs?{RESET}")
    print("  • You write code (or AI helps you)")
    print("  • A DIFFERENT AI reviews your work (catches issues)")
    print("  • Like having a second pair of eyes - reduces blind spots")
    print()

    print_box(
        "Step 1 of 4: Choose Your Setup",
        [
            "Which API keys do you have?",
            "",
            f"  {BOLD}1. Both Anthropic + OpenAI (RECOMMENDED){RESET}",
            "     Cost: ~$0.02-0.10 per workflow | Best quality & independence",
            "",
            "  2. OpenAI only (simpler setup)",
            "     Cost: ~$0.05-0.15 per workflow | One provider, still effective",
            "",
            "  3. Anthropic only (alternative)",
            "     Cost: ~$0.05-0.15 per workflow | One provider, still effective",
            "",
            "  4. I'll configure later (skip API setup)",
            "     You can add API keys manually in .env file",
        ],
    )

    choice = prompt_user("Your choice", default="1")

    anthropic_key = ""
    openai_key = ""

    # Anthropic API Key setup
    if choice in ["1", "3"]:
        print_box(
            "Step 2: Anthropic API Key",
            [
                "Claude 3.5 Sonnet will write your code (implementation agent).",
                "",
                "Need an API key?",
                "  1. Go to: https://console.anthropic.com/settings/keys",
                '  2. Click "Create Key"',
                '  3. Copy the key (starts with "sk-ant-")',
            ],
        )

        anthropic_key = prompt_user("Paste your Anthropic API key (or Enter to skip)", secret=True)

        if anthropic_key:
            is_valid, message = validate_api_key(anthropic_key, "anthropic")
            if is_valid:
                print(f"{GREEN}✅ API key format validated!{RESET}")
            else:
                print(f"{YELLOW}⚠️  Warning: {message}{RESET}")
                print("Continuing anyway...")

    # OpenAI API Key setup
    if choice in ["1", "2"]:
        print_box(
            "Step 3: OpenAI API Key",
            [
                "GPT-4o will review your code (evaluator agent).",
                "",
                "Need an API key?",
                "  1. Go to: https://platform.openai.com/api-keys",
                '  2. Click "+ Create new secret key"',
                '  3. Copy the key (starts with "sk-proj-" or "sk-")',
            ],
        )

        openai_key = prompt_user("Paste your OpenAI API key (or Enter to skip)", secret=True)

        if openai_key:
            is_valid, message = validate_api_key(openai_key, "openai")
            if is_valid:
                print(f"{GREEN}✅ API key format validated!{RESET}")
            else:
                print(f"{YELLOW}⚠️  Warning: {message}{RESET}")
                print("Continuing anyway...")

    # Configuration
    print_box(
        "Step 4: Configuration",
        [
            "Let's configure your project settings:",
        ],
    )

    _project_name = prompt_user(
        "Project name", default=os.path.basename(os.path.abspath(project_path))
    )
    _test_command = prompt_user("Test framework", default="pytest")
    _task_directory = prompt_user("Task directory", default="tasks/")

    # Now run the standard init
    result = init(project_path, interactive=False)

    if result != 0:
        return result

    # Create .env file if we have keys
    if anthropic_key or openai_key:
        create_env_file_interactive(project_path, anthropic_key, openai_key)

    # Success message
    print_box(
        f"{GREEN}✅ Setup Complete!{RESET}",
        [
            "Created:",
            (
                "  ✓ .env (with your API keys - added to .gitignore)"
                if (anthropic_key or openai_key)
                else "  ⚠️ .env (skipped - no API keys provided)"
            ),
            "  ✓ .adversarial/config.yml",
            "  ✓ .adversarial/ (configuration and logs)",
            "",
            (
                "Your configuration:"
                if (anthropic_key or openai_key)
                else "Configuration (no API keys yet):"
            ),
            f"  Author (implementation): {'Claude 3.5 Sonnet (Anthropic)' if anthropic_key else 'GPT-4o (OpenAI)' if openai_key else 'Not configured'}",
            f"  Evaluator: {'GPT-4o (OpenAI)' if openai_key else 'Claude 3.5 Sonnet (Anthropic)' if anthropic_key else 'Not configured'}",
            f"  Cost per workflow: {'~$0.02-0.10' if (anthropic_key and openai_key) else '~$0.05-0.15' if (anthropic_key or openai_key) else 'N/A'}",
            "",
            "Next steps:",
            "  1. Run: adversarial quickstart",
            "     (creates example task and runs first workflow)",
            "",
            "  2. Or create your own:",
            "     - Create: tasks/my-first-task.md",
            "     - Run: adversarial evaluate tasks/my-first-task.md",
            "",
            "  3. Read the guide: https://github.com/movito/adversarial-workflow",
            "",
            "Need help? Run: adversarial check",
        ],
    )

    return 0


def quickstart() -> int:
    """Quick start: create example task and guide user through first workflow."""

    # Check platform compatibility first
    if not check_platform_compatibility():
        return 1

    print(f"\n{BOLD}{CYAN}🚀 Quick Start: Your First Adversarial Workflow{RESET}")
    print()
    print("Let me guide you through your first workflow in 3 steps.")

    # Check if initialized
    if not os.path.exists(".adversarial/config.yml"):
        print_box(
            f"{YELLOW}⚠️  Not Initialized{RESET}",
            [
                "Adversarial workflow is not initialized in this project.",
                "",
                "Let's set it up now (takes 2 minutes):",
            ],
        )

        result = init_interactive(".")
        if result != 0:
            return result

    # Check for API keys
    load_dotenv()
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    if not has_openai and not has_anthropic:
        print_box(
            f"{YELLOW}⚠️  API Keys Not Configured{RESET}",
            [
                "You need at least one API key to run workflows.",
                "",
                "Run: adversarial init --interactive",
                "",
                "Or manually edit .env file (copy from .env.example)",
            ],
        )
        return 1

    # Create tasks directory if needed
    tasks_dir = "tasks"
    os.makedirs(tasks_dir, exist_ok=True)

    # Create example task
    example_task_path = os.path.join(tasks_dir, "example-bug-fix.md")

    if os.path.exists(example_task_path):
        print(f"\n{YELLOW}⚠️  Example task already exists: {example_task_path}{RESET}")
        overwrite = prompt_user("Overwrite", default="n")
        if overwrite.lower() != "y":
            print(f"\nUsing existing task: {example_task_path}")
        else:
            create_example_task(example_task_path)
    else:
        create_example_task(example_task_path)

    # Show the task
    print_box(
        "Step 1: Example Task Created",
        [
            f"Created: {example_task_path}",
            "",
            "This is a sample bug fix task that demonstrates:",
            "  • Clear problem statement",
            "  • Expected behavior",
            "  • Implementation plan",
            "  • Test coverage",
            "  • Acceptance criteria",
        ],
    )

    # Offer to show the task
    show_task = prompt_user("View the task file?", default="y")
    if show_task.lower() in ["y", "yes", ""]:
        print()
        print(f"{GRAY}{'─' * 70}{RESET}")
        with open(example_task_path, encoding="utf-8") as f:
            for line in f:
                print(f"{GRAY}{line.rstrip()}{RESET}")
        print(f"{GRAY}{'─' * 70}{RESET}")

    # Step 2: Evaluate
    print_box(
        "Step 2: Evaluate the Plan",
        [
            "Now let's run Phase 1: Plan Evaluation",
            "",
            f"This will ask {'GPT-4o' if has_openai else 'Claude 3.5 Sonnet'} to review the task plan.",
            "It takes ~10-30 seconds and costs ~$0.01-0.03.",
        ],
    )

    run_eval = prompt_user("Run evaluation now?", default="y")

    if run_eval.lower() in ["y", "yes", ""]:
        print()
        print(f"{CYAN}Running: adversarial evaluate {example_task_path}{RESET}")
        print()
        result = evaluate(example_task_path)

        if result == 0:
            print_box(
                f"{GREEN}✅ Evaluation Complete!{RESET}",
                [
                    "The evaluator approved your plan.",
                    "",
                    "What you learned:",
                    "  ✓ How to create a task file",
                    "  ✓ How to run plan evaluation",
                    "  ✓ How the evaluator provides feedback",
                ],
            )
        else:
            print_box(
                f"{YELLOW}📋 Evaluation Needs Revision{RESET}",
                [
                    "The evaluator provided feedback on your plan.",
                    "Check the output above for suggestions.",
                ],
            )

    # Step 3: Next steps
    print_box(
        "Step 3: Next Steps",
        [
            "You've completed your first adversarial workflow evaluation! 🎉",
            "",
            "Try the full workflow:",
            "  1. Implement the fix (or let an AI assistant do it)",
            "  2. Run: adversarial review <task_file> (Phase 3: Code Review)",
            "  3. Run: adversarial validate (Phase 4: Test Validation)",
            "",
            "Learn more:",
            "  - Read: docs/USAGE.md",
            "  - Help: adversarial --help",
            "  - Guide: https://github.com/movito/adversarial-workflow",
        ],
    )

    return 0


def create_example_task(task_path: str) -> None:
    """Create example task file."""
    package_dir = Path(__file__).parent
    template_path = package_dir / "templates" / "example-task.md.template"

    if template_path.exists():
        shutil.copy(str(template_path), task_path)
    else:
        # Fallback: create basic example
        with open(task_path, "w", encoding="utf-8") as f:
            f.write(
                """# Task: Fix Off-By-One Error in List Processing

**Type**: Bug Fix
**Priority**: Medium

## Problem

The `process_items()` function has an off-by-one error.

## Implementation Plan

1. Fix the range in the for loop
2. Add test for edge case

## Acceptance Criteria

- [x] All items processed including last one
- [x] Tests pass
"""
            )

    print(f"{GREEN}✅ Created: {task_path}{RESET}")


def load_config(config_path: str = ".adversarial/config.yml") -> dict:
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
        with open(config_path, encoding="utf-8") as f:
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


def render_template(template_path: str, output_path: str, variables: dict) -> None:
    """Render a template file with variable substitution."""
    with open(template_path, encoding="utf-8") as f:
        content = f.read()

    # Replace {{variable}} with values
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        content = content.replace(placeholder, str(value))

    # Inject version header for shell scripts (after shebang line)
    if output_path.endswith(".sh"):
        lines = content.split("\n", 1)
        if lines[0].startswith("#!"):
            # Insert version after shebang
            version_header = f"# SCRIPT_VERSION: {__version__}"
            content = f"{lines[0]}\n{version_header}\n{lines[1] if len(lines) > 1 else ''}"

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Make scripts executable
    if output_path.endswith(".sh"):
        os.chmod(output_path, 0o755)


def init(project_path: str = ".", interactive: bool = True) -> int:
    """Initialize adversarial workflow in project."""

    if not interactive:
        print("🔧 Initializing adversarial workflow...")

    # Error 1: Not a git repository
    if not os.path.exists(os.path.join(project_path, ".git")):
        print(f"{RED}❌ ERROR: Not a git repository{RESET}")
        print()
        print(f"{BOLD}WHY:{RESET}")
        print("   Adversarial workflow needs git to:")
        print("   • Track code changes for review (git diff)")
        print("   • Detect phantom work (code vs. comments)")
        print("   • Create audit trail of improvements")
        print()
        print(f"{BOLD}FIX:{RESET}")
        print("   1. Initialize git: git init")
        print("   2. Make first commit: git add . && git commit -m 'Initial commit'")
        print("   3. Then run: adversarial init")
        print()
        print(f"{BOLD}HELP:{RESET}")
        print("   New to git? https://git-scm.com/book/en/v2/Getting-Started-Installing-Git")
        return 1

    # Pre-flight validation: Check package integrity
    package_dir = Path(__file__).parent
    templates_dir = package_dir / "templates"

    required_templates = [
        "config.yml.template",
        ".env.example.template",
    ]

    missing_templates = []
    for template in required_templates:
        if not (templates_dir / template).exists():
            missing_templates.append(template)

    if missing_templates:
        print(f"{RED}❌ ERROR: Package installation incomplete{RESET}")
        print()
        print(f"{BOLD}WHY:{RESET}")
        print("   Required template files are missing from the package distribution.")
        print("   This is a package bug, not a user configuration error.")
        print()
        print(f"{BOLD}MISSING TEMPLATES:{RESET}")
        for template in missing_templates:
            print(f"   • {template}")
        print()
        print(f"{BOLD}FIX:{RESET}")
        print("   1. Report this issue: https://github.com/movito/adversarial-workflow/issues")
        print(
            "   2. Or try reinstalling: pip install --upgrade --force-reinstall adversarial-workflow"
        )
        print()
        print(f"{BOLD}WORKAROUND:{RESET}")
        print("   Create missing files manually:")
        print("   - .env.example: Create with API key placeholders")
        return 1

    # Error 2: Already initialized
    adversarial_dir = os.path.join(project_path, ".adversarial")
    if os.path.exists(adversarial_dir):
        if interactive:
            print(f"\n{YELLOW}⚠️  WARNING: {adversarial_dir} already exists.{RESET}")
            response = input("   Overwrite? (y/N): ")
            if response.lower() != "y":
                print("   Aborted.")
                return 0
        shutil.rmtree(adversarial_dir)

    # Error 3: Can't write to directory
    try:
        os.makedirs(adversarial_dir)
        os.makedirs(os.path.join(adversarial_dir, "logs"))
        os.makedirs(os.path.join(adversarial_dir, "artifacts"))
    except PermissionError:
        print(f"{RED}❌ ERROR: Permission denied creating {adversarial_dir}{RESET}")
        print(f"   Fix: chmod +w {project_path}")
        return 1

    # Error 4: Template rendering fails
    try:
        # Get package directory
        package_dir = Path(__file__).parent
        templates_dir = package_dir / "templates"

        # Render configuration
        config_vars = {
            "EVALUATOR_MODEL": "gpt-4o",
            "TASK_DIRECTORY": "tasks/",
            "TEST_COMMAND": "pytest",
            "LOG_DIRECTORY": ".adversarial/logs/",
            "ARTIFACTS_DIRECTORY": ".adversarial/artifacts/",
        }

        # Copy template files
        render_template(
            str(templates_dir / "config.yml.template"),
            os.path.join(adversarial_dir, "config.yml"),
            config_vars,
        )

        # Copy .env.example to project root
        shutil.copy(
            str(templates_dir / ".env.example.template"),
            os.path.join(project_path, ".env.example"),
        )

        # Copy AGENT-SYSTEM-GUIDE.md if available (for agent coordination setup)
        agent_guide_template = templates_dir / "agent-context" / "AGENT-SYSTEM-GUIDE.md"
        agent_context_dir = Path(project_path) / ".agent-context"
        agent_guide_dest = agent_context_dir / "AGENT-SYSTEM-GUIDE.md"

        if agent_guide_template.exists() and not agent_guide_dest.exists():
            try:
                agent_context_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(str(agent_guide_template), str(agent_guide_dest))
                if interactive:
                    print("  ✓ Agent coordination guide installed")
            except OSError as e:
                # Non-critical failure - agent guide is optional
                if interactive:
                    print(f"  ⚠️  Could not install agent guide: {e}")

        # Update .gitignore
        gitignore_path = os.path.join(project_path, ".gitignore")
        gitignore_entries = [
            ".adversarial/logs/",
            ".adversarial/artifacts/",
            ".env",
        ]

        if os.path.exists(gitignore_path):
            with open(gitignore_path, encoding="utf-8") as f:
                existing = f.read()

            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write("\n# Adversarial Workflow\n")
                for entry in gitignore_entries:
                    if entry not in existing:
                        f.write(f"{entry}\n")

    except Exception as e:
        print(f"{RED}❌ ERROR: Template rendering failed: {e}{RESET}")
        print("   Fix: Check config.yml syntax")
        # Cleanup partial initialization
        if os.path.exists(adversarial_dir):
            shutil.rmtree(adversarial_dir)
        return 1

    if interactive:
        print(f"\n{GREEN}✅ Adversarial workflow initialized successfully!{RESET}")
        print()
        print("📋 Next steps:")
        print("   1. Edit .env with your API keys (copy from .env.example)")
        print("   2. Run 'adversarial check' to verify setup")
        print("   3. Customize .adversarial/config.yml for your project")
        print()

    return 0


def check() -> int:
    """Validate setup and dependencies."""

    print(f"\n{BOLD}🔍 Checking adversarial workflow setup...{RESET}")
    print()

    issues: list[dict] = []
    good_checks: list[str] = []

    # Check for .env file (note: already loaded by main() at startup)
    env_file = Path(".env")
    env_loaded = False

    if env_file.exists():
        try:
            # Count variables by reading file directly (works even if already loaded)
            env_vars = dotenv_values(env_file)
            var_count = len([k for k, v in env_vars.items() if v is not None])

            # Still load to ensure environment is set
            load_dotenv(env_file)
            env_loaded = True
            good_checks.append(f".env file found and loaded ({var_count} variables)")
        except (FileNotFoundError, PermissionError) as e:
            # File access errors
            issues.append(
                {
                    "severity": "WARNING",
                    "message": f".env file found but could not be read: {e}",
                    "fix": "Check .env file permissions",
                }
            )
        except (OSError, ValueError) as e:
            # Covers UnicodeDecodeError (ValueError subclass) and other OS errors
            issues.append(
                {
                    "severity": "WARNING",
                    "message": f".env file found but could not be parsed: {e}",
                    "fix": "Check .env file encoding (should be UTF-8)",
                }
            )
    else:
        issues.append(
            {
                "severity": "INFO",
                "message": ".env file not found (optional - can use environment variables)",
                "fix": "Create .env file: cp .env.example .env (or run: adversarial init --interactive)",
            }
        )

    # Check 1: Git repository
    if os.path.exists(".git"):
        good_checks.append("Git repository detected")
    else:
        issues.append(
            {
                "severity": "ERROR",
                "message": "Not a git repository",
                "fix": "Run: git init",
            }
        )

    # Check 2: API keys (with source tracking)
    # Track which keys existed before and after .env loading
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Determine source of each key
    def get_key_source(key_name: str, env_was_loaded: bool) -> str:
        """Determine if key came from .env or environment."""
        if not env_was_loaded:
            return "from environment"
        # Check if key was in environment before loading .env
        # If .env was loaded and key exists, it likely came from .env
        # This is a heuristic since we can't definitively know the source
        return "from .env" if env_file.exists() else "from environment"

    # Helper function to format partial key
    def format_key_preview(key: str) -> str:
        """Format API key showing first 8 and last 4 characters."""
        if len(key) > 12:
            return f"{key[:8]}...{key[-4:]}"
        else:
            return "***"

    # Check Anthropic API key
    if anthropic_key and not anthropic_key.startswith("your-"):
        source = get_key_source("ANTHROPIC_API_KEY", env_loaded)
        preview = format_key_preview(anthropic_key)
        good_checks.append(f"ANTHROPIC_API_KEY configured ({source}) [{preview}]")
    elif anthropic_key:
        issues.append(
            {
                "severity": "WARNING",
                "message": "ANTHROPIC_API_KEY is placeholder value",
                "fix": "Edit .env with real API key from https://console.anthropic.com/settings/keys",
            }
        )

    # Check OpenAI API key
    if openai_key and not openai_key.startswith("your-"):
        source = get_key_source("OPENAI_API_KEY", env_loaded)
        preview = format_key_preview(openai_key)
        good_checks.append(f"OPENAI_API_KEY configured ({source}) [{preview}]")
    elif openai_key:
        issues.append(
            {
                "severity": "WARNING",
                "message": "OPENAI_API_KEY is placeholder value",
                "fix": "Edit .env with real API key from https://platform.openai.com/api-keys",
            }
        )

    # Check if at least one API key is configured
    if not anthropic_key and not openai_key:
        issues.append(
            {
                "severity": "ERROR",
                "message": "No API keys configured - workflow cannot run",
                "fix": "Run 'adversarial init --interactive' to set up API keys with guided wizard",
            }
        )

    # Check 4: Config valid
    if not os.path.exists(".adversarial/config.yml"):
        issues.append(
            {
                "severity": "ERROR",
                "message": "Not initialized (.adversarial/config.yml not found)",
                "fix": "Run: adversarial init",
            }
        )
        config = None
    else:
        try:
            config = load_config(".adversarial/config.yml")
            good_checks.append(".adversarial/config.yml valid")
        except FileNotFoundError:
            issues.append(
                {
                    "severity": "ERROR",
                    "message": "Not initialized (.adversarial/config.yml not found)",
                    "fix": "Run: adversarial init",
                }
            )
            config = None
        except yaml.YAMLError as e:
            issues.append(
                {
                    "severity": "ERROR",
                    "message": f"Invalid config.yml: {e}",
                    "fix": "Fix YAML syntax in .adversarial/config.yml",
                }
            )
            config = None

    # Print results
    print("━" * 70)

    # Show good checks
    if good_checks:
        for check in good_checks:
            print(f"{GREEN}✅{RESET} {check}")

    # Show issues
    if issues:
        print()
        for issue in issues:
            # Choose icon based on severity
            if issue["severity"] == "ERROR":
                icon = f"{RED}❌{RESET}"
            elif issue["severity"] == "WARNING":
                icon = f"{YELLOW}⚠️{RESET}"
            else:  # INFO
                icon = f"{CYAN}ℹ️{RESET}"
            print(f"{icon} [{issue['severity']}] {issue['message']}")
            print(f"   Fix: {issue['fix']}")

    print("━" * 70)
    print()

    # Summary
    error_count = sum(1 for i in issues if i["severity"] == "ERROR")
    warning_count = sum(1 for i in issues if i["severity"] == "WARNING")
    info_count = sum(1 for i in issues if i["severity"] == "INFO")

    if error_count == 0 and warning_count == 0:
        print(f"{GREEN}✅ All checks passed! Your setup is ready.{RESET}")
        print()
        print("Estimated cost per workflow: $0.02-0.10")
        print()
        print(f"Try it: {CYAN}adversarial quickstart{RESET}")
        return 0
    else:
        status_parts = []
        if error_count > 0:
            status_parts.append(f"{error_count} error" + ("s" if error_count != 1 else ""))
        if warning_count > 0:
            status_parts.append(f"{warning_count} warning" + ("s" if warning_count != 1 else ""))
        if info_count > 0:
            status_parts.append(f"{info_count} info")

        status = ", ".join(status_parts)

        if error_count > 0:
            print(f"{RED}❌ Setup incomplete ({status}){RESET}")
        else:
            print(f"{YELLOW}⚠️ Setup has warnings ({status}){RESET}")
        print()
        print("Quick fix: adversarial init --interactive")

        return 1 if error_count > 0 else 0


def health(verbose: bool = False, json_output: bool = False) -> int:
    """
    Comprehensive system health check.

    Goes beyond basic 'check' to validate agent coordination,
    workflow scripts, permissions, and provide actionable diagnostics.

    Args:
        verbose: Show detailed diagnostics and fix commands
        json_output: Output in JSON format for machine parsing

    Returns:
        0 if healthy (>90% checks pass), 1 if degraded or critical
    """
    import json

    # Initialize results tracking
    results = {
        "configuration": [],
        "dependencies": [],
        "api_keys": [],
        "agent_coordination": [],
        "workflow_scripts": [],
        "tasks": [],
        "permissions": [],
    }

    passed = 0
    warnings = 0
    errors = 0
    recommendations = []

    # Helper functions for tracking check results
    def check_pass(category: str, message: str, detail: str = None):
        nonlocal passed
        results[category].append({"status": "pass", "message": message, "detail": detail})
        if not json_output:
            print(f"  {GREEN}✅{RESET} {message}")
        passed += 1

    def check_warn(category: str, message: str, detail: str = None, recommendation: str = None):
        nonlocal warnings
        results[category].append({"status": "warn", "message": message, "detail": detail})
        if not json_output:
            print(f"  {YELLOW}⚠️{RESET}  {message}")
            if detail and verbose:
                print(f"     {GRAY}{detail}{RESET}")
        if recommendation:
            recommendations.append(recommendation)
        warnings += 1

    def check_fail(category: str, message: str, fix: str = None, recommendation: str = None):
        nonlocal errors
        results[category].append({"status": "fail", "message": message, "fix": fix})
        if not json_output:
            print(f"  {RED}❌{RESET} {message}")
            if fix and verbose:
                print(f"     {GRAY}Fix: {fix}{RESET}")
        if recommendation:
            recommendations.append(recommendation)
        errors += 1

    def check_info(category: str, message: str, detail: str = None):
        results[category].append({"status": "info", "message": message, "detail": detail})
        if not json_output:
            print(f"  {CYAN}ℹ️{RESET}  {message}")
            if detail and verbose:
                print(f"     {GRAY}{detail}{RESET}")

    # Print header
    if not json_output:
        print()
        print(f"{BOLD}🏥 Adversarial Workflow Health Check{RESET}")
        print("=" * 70)
        print()

    # 1. Configuration Checks
    if not json_output:
        print(f"{BOLD}Configuration:{RESET}")

    config_file = Path(".adversarial/config.yml")
    config = None

    if config_file.exists():
        try:
            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
            check_pass("configuration", ".adversarial/config.yml - Valid YAML")

            # Check required fields
            if "evaluator_model" in config:
                model = config["evaluator_model"]
                supported_models = ["gpt-4o", "claude-sonnet-4-5", "claude-3-5-sonnet"]
                if any(m in model for m in ["gpt-4", "claude"]):
                    check_pass("configuration", f"evaluator_model: {model}")
                else:
                    check_warn(
                        "configuration",
                        f"evaluator_model: {model} (unrecognized)",
                        recommendation="Check model name in config.yml",
                    )
            else:
                check_warn(
                    "configuration",
                    "evaluator_model not set",
                    recommendation="Add evaluator_model to config.yml",
                )

            # Check directories
            if "task_directory" in config:
                task_dir = Path(config["task_directory"])
                if task_dir.exists():
                    check_pass(
                        "configuration",
                        f"task_directory: {config['task_directory']} (exists)",
                    )
                else:
                    check_fail(
                        "configuration",
                        f"task_directory: {config['task_directory']} (not found)",
                        fix=f"mkdir -p {config['task_directory']}",
                        recommendation=f"Create task directory: mkdir -p {config['task_directory']}",
                    )

            if "log_directory" in config:
                log_dir = Path(config["log_directory"])
                if log_dir.exists():
                    if os.access(log_dir, os.W_OK):
                        check_pass(
                            "configuration",
                            f"log_directory: {config['log_directory']} (writable)",
                        )
                    else:
                        check_fail(
                            "configuration",
                            f"log_directory: {config['log_directory']} (not writable)",
                            fix=f"chmod +w {config['log_directory']}",
                        )
                else:
                    check_warn(
                        "configuration",
                        f"log_directory: {config['log_directory']} (will be created)",
                        recommendation="Log directory will be created automatically",
                    )

            # Check test command
            if "test_command" in config:
                check_info("configuration", f"test_command: {config['test_command']}")

        except yaml.YAMLError as e:
            check_fail(
                "configuration",
                f".adversarial/config.yml - Invalid YAML: {e}",
                fix="Fix YAML syntax in .adversarial/config.yml",
                recommendation="Check YAML syntax - look for indentation or special character issues",
            )
        except Exception as e:
            check_fail("configuration", f".adversarial/config.yml - Error reading: {e}")
    else:
        check_fail(
            "configuration",
            ".adversarial/config.yml not found",
            fix="Run: adversarial init",
            recommendation="Initialize project with: adversarial init --interactive",
        )

    if not json_output:
        print()

    # 2. Dependencies
    if not json_output:
        print(f"{BOLD}Dependencies:{RESET}")

    # Git
    if shutil.which("git"):
        try:
            git_version = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=2
            )
            if git_version.returncode == 0:
                version = (
                    git_version.stdout.split()[2]
                    if len(git_version.stdout.split()) > 2
                    else "unknown"
                )

                # Check git status
                git_status = subprocess.run(
                    ["git", "status", "--short"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if git_status.returncode == 0:
                    modified = len(
                        [l for l in git_status.stdout.splitlines() if l.startswith(" M")]
                    )
                    untracked = len(
                        [l for l in git_status.stdout.splitlines() if l.startswith("??")]
                    )
                    if modified == 0 and untracked == 0:
                        check_pass("dependencies", f"Git: {version} (working tree clean)")
                    else:
                        check_info(
                            "dependencies",
                            f"Git: {version} ({modified} modified, {untracked} untracked)",
                        )
                else:
                    check_pass("dependencies", f"Git: {version}")
        except:
            check_pass("dependencies", "Git: installed")
    else:
        check_fail(
            "dependencies",
            "Git not found",
            fix="Install: https://git-scm.com/downloads",
            recommendation="Git is required - install from git-scm.com",
        )

    # Python
    python_version = sys.version.split()[0]
    major, minor = map(int, python_version.split(".")[:2])
    if (major, minor) >= (3, 10):
        check_pass("dependencies", f"Python: {python_version} (compatible)")
    else:
        check_fail(
            "dependencies",
            f"Python: {python_version} (requires 3.10+)",
            fix="Upgrade Python to 3.10 or higher",
            recommendation="Python 3.10+ required - upgrade your Python installation",
        )

    # Bash
    try:
        bash_version = subprocess.run(
            ["bash", "--version"], capture_output=True, text=True, timeout=2
        )
        if bash_version.returncode == 0:
            version_line = bash_version.stdout.split("\n")[0]
            if "version 3" in version_line:
                check_info(
                    "dependencies",
                    f"Bash: {version_line.split()[3]} (macOS default - limited features)",
                )
            else:
                check_pass("dependencies", f"Bash: {version_line.split()[3]}")
    except:
        check_info("dependencies", "Bash: present")

    if not json_output:
        print()

    # 3. API Keys
    if not json_output:
        print(f"{BOLD}API Keys:{RESET}")

    # Load .env
    env_file = Path(".env")
    env_loaded = False
    if env_file.exists():
        try:
            load_dotenv(env_file)
            env_loaded = True
            check_info("api_keys", ".env file loaded")
        except:
            check_warn("api_keys", ".env file found but could not be loaded")

    # Check keys
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key and openai_key.startswith(("sk-proj-", "sk-")):
        preview = f"{openai_key[:8]}...{openai_key[-4:]}"
        source = "from .env" if env_loaded else "from environment"
        check_pass("api_keys", f"OPENAI_API_KEY: Set ({source}) [{preview}]")
    elif openai_key:
        check_warn(
            "api_keys",
            "OPENAI_API_KEY: Invalid format",
            recommendation='OpenAI keys should start with "sk-" or "sk-proj-"',
        )
    else:
        check_warn(
            "api_keys",
            "OPENAI_API_KEY: Not set",
            recommendation="Add OPENAI_API_KEY to .env file",
        )

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key.startswith("sk-ant-"):
        preview = f"{anthropic_key[:8]}...{anthropic_key[-4:]}"
        source = "from .env" if env_loaded else "from environment"
        check_pass("api_keys", f"ANTHROPIC_API_KEY: Set ({source}) [{preview}]")
    elif anthropic_key:
        check_warn(
            "api_keys",
            "ANTHROPIC_API_KEY: Invalid format",
            recommendation='Anthropic keys should start with "sk-ant-"',
        )
    else:
        check_info("api_keys", "ANTHROPIC_API_KEY: Not set (optional)")

    # Check if at least one key is configured
    if not (openai_key and openai_key.startswith(("sk-", "sk-proj-"))) and not (
        anthropic_key and anthropic_key.startswith("sk-ant-")
    ):
        check_fail(
            "api_keys",
            "No valid API keys configured",
            fix="Run: adversarial init --interactive",
            recommendation="At least one API key required - use adversarial init --interactive",
        )

    if not json_output:
        print()

    # 4. Agent Coordination
    if not json_output:
        print(f"{BOLD}Agent Coordination:{RESET}")

    agent_context = Path(".agent-context")
    if agent_context.exists():
        check_pass("agent_coordination", ".agent-context/ directory exists")

        # Check agent-handoffs.json
        handoffs_file = agent_context / "agent-handoffs.json"
        if handoffs_file.exists():
            try:
                with open(handoffs_file, encoding="utf-8") as f:
                    handoffs = json.load(f)
                agent_count = len([k for k in handoffs.keys() if k != "meta"])
                check_pass(
                    "agent_coordination",
                    f"agent-handoffs.json - Valid JSON ({agent_count} agents)",
                )

                # Check for stale status (optional - would need datetime parsing)
                if "meta" in handoffs and "last_updated" in handoffs["meta"]:
                    check_info(
                        "agent_coordination",
                        f"Last updated: {handoffs['meta']['last_updated']}",
                    )

            except json.JSONDecodeError as e:
                check_fail(
                    "agent_coordination",
                    f"agent-handoffs.json - Invalid JSON: {e}",
                    fix="Fix JSON syntax in .agent-context/agent-handoffs.json",
                )
            except Exception as e:
                check_fail("agent_coordination", f"agent-handoffs.json - Error: {e}")
        else:
            check_warn(
                "agent_coordination",
                "agent-handoffs.json not found",
                recommendation="Initialize agent coordination system",
            )

        # Check current-state.json
        state_file = agent_context / "current-state.json"
        if state_file.exists():
            try:
                with open(state_file, encoding="utf-8") as f:
                    json.load(f)
                check_pass("agent_coordination", "current-state.json - Valid JSON")
            except json.JSONDecodeError as e:
                check_fail("agent_coordination", f"current-state.json - Invalid JSON: {e}")
        else:
            check_info("agent_coordination", "current-state.json not found (optional)")

        # Check AGENT-SYSTEM-GUIDE.md
        guide_file = agent_context / "AGENT-SYSTEM-GUIDE.md"
        if guide_file.exists():
            file_size = guide_file.stat().st_size
            check_pass(
                "agent_coordination",
                f"AGENT-SYSTEM-GUIDE.md - Present ({file_size // 1024}KB)",
            )
        else:
            check_warn(
                "agent_coordination",
                "AGENT-SYSTEM-GUIDE.md not found",
                recommendation="Run adversarial init to install agent guide",
            )
    else:
        check_info(
            "agent_coordination",
            ".agent-context/ not found (optional)",
            detail="Agent coordination is optional for basic workflows",
        )

    if not json_output:
        print()

    # 5. Tasks
    if not json_output:
        print(f"{BOLD}Tasks:{RESET}")

    if config and "task_directory" in config:
        task_dir = Path(config["task_directory"])
        if task_dir.exists():
            check_pass("tasks", f"{config['task_directory']} directory exists")

            # Count tasks
            try:
                task_files = list(task_dir.glob("**/*.md"))
                active_tasks = (
                    list((task_dir / "active").glob("*.md"))
                    if (task_dir / "active").exists()
                    else []
                )

                if len(active_tasks) > 0:
                    check_info(
                        "tasks",
                        f"{len(active_tasks)} active tasks in {config['task_directory']}active/",
                    )
                elif len(task_files) > 0:
                    check_info(
                        "tasks",
                        f"{len(task_files)} task files in {config['task_directory']}",
                    )
                else:
                    check_info(
                        "tasks",
                        "No task files found (create with adversarial quickstart)",
                    )
            except Exception:
                check_info("tasks", "Could not count task files")
        else:
            check_warn(
                "tasks",
                f"{config['task_directory']} directory not found",
                recommendation=f"Create with: mkdir -p {config['task_directory']}",
            )
    else:
        check_info("tasks", "Task directory not configured")

    if not json_output:
        print()

    # 7. Permissions
    if not json_output:
        print(f"{BOLD}Permissions:{RESET}")

    # Check .env permissions
    if env_file.exists():
        stat_info = env_file.stat()
        perms = oct(stat_info.st_mode)[-3:]
        if perms in ["600", "400"]:
            check_pass("permissions", f".env - Secure ({perms})")
        elif perms == "644":
            check_warn(
                "permissions",
                f".env - Readable by others ({perms})",
                recommendation="Secure .env file: chmod 600 .env",
            )
        else:
            check_warn(
                "permissions",
                f".env - Permissions {perms}",
                recommendation="Secure .env file: chmod 600 .env",
            )

    # Check log directory writable
    if config and "log_directory" in config:
        log_dir = Path(config["log_directory"])
        if log_dir.exists():
            if os.access(log_dir, os.W_OK):
                check_pass("permissions", f"{config['log_directory']} - Writable")
            else:
                check_fail(
                    "permissions",
                    f"{config['log_directory']} - Not writable",
                    fix=f"chmod +w {config['log_directory']}",
                )

    if not json_output:
        print()

    # Calculate health score
    total = passed + warnings + errors
    health_score = int((passed / total) * 100) if total > 0 else 0

    # Output results
    if json_output:
        output = {
            "health_score": health_score,
            "summary": {
                "passed": passed,
                "warnings": warnings,
                "errors": errors,
                "total": total,
            },
            "results": results,
            "recommendations": recommendations,
        }
        print(json.dumps(output, indent=2))
    else:
        # Text output summary
        print("=" * 70)
        print()

        # Status line
        if health_score > 90:
            status_emoji = "✅"
            status_text = "healthy"
            status_color = GREEN
        elif health_score > 70:
            status_emoji = "⚠️"
            status_text = "degraded"
            status_color = YELLOW
        else:
            status_emoji = "❌"
            status_text = "critical"
            status_color = RED

        print(
            f"{status_emoji} {status_color}System is {status_text}!{RESET} (Health: {health_score}%)"
        )
        print(f"   {passed} checks passed, {warnings} warnings, {errors} errors")
        print()

        # Recommendations
        if recommendations:
            print(f"{BOLD}Recommendations:{RESET}")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                print(f"  {i}. {rec}")
            if len(recommendations) > 5:
                print(f"  ... and {len(recommendations) - 5} more")
            print()

        # Ready to section
        if health_score > 70:
            print(f"{BOLD}Ready to:{RESET}")
            print("  • Evaluate task plans: adversarial evaluate <task-file>")
            print("  • Review implementations: adversarial review <task_file>")
            print("  • Validate tests: adversarial validate")
        else:
            print(f"{BOLD}Next steps:{RESET}")
            print("  • Fix critical issues above")
            print("  • Run: adversarial init --interactive")
            print("  • Then: adversarial health --verbose")
        print()

    # Exit code
    return 0 if errors == 0 else 1


def evaluate(task_file: str) -> int:
    """Run Phase 1: Plan evaluation."""

    print(f"📝 Evaluating plan: {task_file}")
    print()

    # Error 1: Task file not found
    if not os.path.exists(task_file):
        print(f"{RED}❌ ERROR: Task file not found: {task_file}{RESET}")
        print("   Usage: adversarial evaluate <task_file>")
        print("   Example: adversarial evaluate tasks/feature-auth.md")
        return 1

    # Error 2: Config not loaded
    try:
        config = load_config()
    except FileNotFoundError:
        print(f"{RED}❌ ERROR: Not initialized. Run 'adversarial init' first.{RESET}")
        return 1

    # Use the built-in 'evaluate' evaluator via LiteLLM
    # Note: run_evaluator() handles large-file warnings and confirmation prompts
    from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS
    from adversarial_workflow.evaluators.runner import run_evaluator

    builtin_config = BUILTIN_EVALUATORS.get("evaluate")
    if builtin_config is None:
        print(f"{RED}❌ ERROR: Built-in 'evaluate' evaluator not found{RESET}")
        return 1

    eval_result = run_evaluator(builtin_config, task_file)
    if eval_result != 0:
        print()
        print("📋 Evaluation complete (needs revision)")
        print(f"   Details: {config.get('log_directory', '.adversarial/logs/')}")
        return eval_result

    print()
    print(f"{GREEN}✅ Evaluation complete!{RESET}")
    return 0


def review(task_file: str) -> int:
    """Run Phase 3: Code review."""

    print("🔍 Reviewing implementation...")
    print()

    # Check for git changes (branch-aware: committed, staged, or unstaged)
    default_branch = subprocess.run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        capture_output=True,
        text=True,
    )
    base = (
        default_branch.stdout.strip().removeprefix("origin/")
        if default_branch.returncode == 0
        else "main"
    )
    branch_diff = subprocess.run(
        ["git", "diff", "--quiet", f"{base}...HEAD"], capture_output=True, text=True
    )

    # Fix 3 (ADV-0057): git diff returns 1 for "has changes", but values >= 128
    # indicate a git error (e.g. invalid ref). Catch and report before proceeding.
    if branch_diff.returncode >= 128:
        print(f"{RED}❌ ERROR: Cannot compare against base branch '{base}'{RESET}")
        stderr_msg = branch_diff.stderr.strip() if branch_diff.stderr else ""
        if stderr_msg:
            print(f"   Git error: {stderr_msg}")
        print("   Fix: Ensure origin/HEAD is set, or that 'main' branch exists.")
        print("   Run: git remote set-head origin --auto")
        return 1

    staged_diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    unstaged_diff = subprocess.run(["git", "diff", "--quiet"], capture_output=True)

    if (
        branch_diff.returncode == 0
        and staged_diff.returncode == 0
        and unstaged_diff.returncode == 0
    ):
        # No changes at all
        print(f"{YELLOW}⚠️  WARNING: No git changes detected!{RESET}")
        print("   This might indicate PHANTOM WORK.")
        print("   Aborting review to save tokens.")
        return 1

    # Load config
    try:
        config = load_config()
    except FileNotFoundError:
        print(f"{RED}❌ ERROR: Not initialized. Run 'adversarial init' first.{RESET}")
        return 1

    # Use the built-in 'review' evaluator via LiteLLM
    from adversarial_workflow.evaluators.builtins import BUILTIN_EVALUATORS
    from adversarial_workflow.evaluators.runner import run_evaluator

    builtin_config = BUILTIN_EVALUATORS.get("review")
    if builtin_config is None:
        print(f"{RED}❌ ERROR: Built-in 'review' evaluator not found{RESET}")
        print("   Install a review evaluator: adversarial library install <name>")
        print("   Or use: adversarial <evaluator-name> <task-file>")
        return 1

    eval_result = run_evaluator(builtin_config, task_file)
    if eval_result != 0:
        print()
        print("📋 Review complete (needs revision)")
        return eval_result

    print()
    print(f"{GREEN}✅ Review complete!{RESET}")
    return 0


def validate(test_command: str | None = None) -> int:
    """Run Phase 4: Test validation."""

    print("🧪 Validating with tests...")
    print()

    # Load config
    try:
        config = load_config()
    except FileNotFoundError:
        print(f"{RED}❌ ERROR: Not initialized. Run 'adversarial init' first.{RESET}")
        return 1

    # Use provided test command or config default
    if test_command is None:
        test_command = config.get("test_command", "pytest")

    # Guard against empty test command (shlex.split("") returns [], causing IndexError)
    if not test_command or not test_command.strip():
        print(f"{RED}❌ ERROR: Test command is empty{RESET}")
        print("   Fix: Provide a test command or set test_command in .adversarial/config.yml")
        return 1

    print(f"   Test command: {test_command}")
    print()

    # Run test command directly (no shell script needed)
    import shlex

    try:
        result = subprocess.run(
            shlex.split(test_command),
            timeout=600,  # 10 minutes for tests
        )
    except subprocess.TimeoutExpired:
        print(f"{RED}❌ ERROR: Test validation timed out (>10 minutes){RESET}")
        return 1
    except FileNotFoundError:
        print(f"{RED}❌ ERROR: Test command not found: {test_command}{RESET}")
        print("   Fix: Ensure the test runner is installed and on PATH")
        return 1

    if result.returncode != 0:
        print()
        print("📋 Validation complete (tests failed or needs review)")
        return result.returncode

    print()
    print(f"{GREEN}✅ Validation passed!{RESET}")
    return 0


def select_agent_template() -> dict[str, str]:
    """
    Prompt user for agent template selection.

    Returns:
        Dict with 'type' ('standard', 'minimal', 'custom', 'skip') and 'url' (if custom)
    """
    print(f"{BOLD}Agent Roles:{RESET}")
    print("  Standard setup includes 8 agent roles:")
    print("    • coordinator (task management)")
    print("    • feature-developer, api-developer, format-developer")
    print("    • test-runner, document-reviewer, security-reviewer, media-processor")
    print()
    print("  Minimal setup includes 3 agent roles:")
    print("    • coordinator, developer, reviewer")
    print()

    customize = prompt_user("Customize agent roles?", default="n")

    if customize.lower() not in ["y", "yes"]:
        return {"type": "standard", "url": None}

    # Show customization options
    print()
    print(f"{BOLD}Agent Template Options:{RESET}")
    print("  1. Standard (8 roles) - Recommended for complex projects")
    print("  2. Minimal (3 roles) - Simple projects or getting started")
    print("  3. Custom URL - Load from your own template repository")
    print("  4. Skip - Set up manually later")
    print()

    choice = prompt_user("Your choice", default="1")

    if choice == "2":
        return {"type": "minimal", "url": None}
    elif choice == "3":
        print()
        print(f"{CYAN}Custom Template URL:{RESET}")
        print("  Example: https://raw.githubusercontent.com/user/repo/main/agent-handoffs.json")
        print()
        url = prompt_user("Template URL")
        if url:
            return {"type": "custom", "url": url}
        else:
            print(f"{YELLOW}No URL provided, using standard template{RESET}")
            return {"type": "standard", "url": None}
    elif choice == "4":
        return {"type": "skip", "url": None}
    else:  # Default to standard
        return {"type": "standard", "url": None}


def fetch_agent_template(url: str, template_type: str = "standard") -> str | None:
    """
    Fetch agent template from URL or package templates.

    Args:
        url: URL to fetch from (if custom), or None for package template
        template_type: 'standard', 'minimal', or 'custom'

    Returns:
        Template content as string, or None on failure
    """
    if template_type in ["standard", "minimal"]:
        # Load from package templates
        package_dir = Path(__file__).parent
        template_name = (
            "agent-handoffs.json.template"
            if template_type == "standard"
            else "agent-handoffs-minimal.json.template"
        )
        template_path = package_dir / "templates" / "agent-context" / template_name

        if template_path.exists():
            try:
                with open(template_path, encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"{RED}❌ ERROR: Could not read {template_type} template: {e}{RESET}")
                return None
        else:
            print(f"{RED}❌ ERROR: {template_type} template not found in package{RESET}")
            return None

    elif template_type == "custom" and url:
        # Fetch from custom URL
        try:
            import urllib.request

            print(f"  Fetching template from: {url}")

            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read().decode("utf-8")

            # Validate it's JSON
            import json

            json.loads(content)

            print(f"  {GREEN}✅{RESET} Template fetched successfully")
            return content

        except urllib.error.URLError as e:
            print(f"{RED}❌ ERROR: Could not fetch template: {e}{RESET}")
            print("  Using standard template instead")
            return fetch_agent_template(None, "standard")
        except json.JSONDecodeError as e:
            print(f"{RED}❌ ERROR: Template is not valid JSON: {e}{RESET}")
            print("  Using standard template instead")
            return fetch_agent_template(None, "standard")
        except Exception as e:
            print(f"{RED}❌ ERROR: Unexpected error: {e}{RESET}")
            print("  Using standard template instead")
            return fetch_agent_template(None, "standard")

    return None


def agent_onboard(project_path: str = ".") -> int:
    """
    Set up agent coordination system (Extension Layer).

    Prerequisites:
        - adversarial-workflow init must be run first

    Creates:
        - .agent-context/ (agent coordination)
        - agents/ (agent tools and launchers)
        - delegation/ (task management)

    Updates:
        - .adversarial/config.yml (task_directory → delegation/tasks/)

    Returns:
        0 on success, 1 on failure
    """
    import glob
    import json
    from datetime import datetime

    # 1. Check prerequisite (Layer 1 must exist)
    if not os.path.exists(".adversarial/config.yml"):
        print(f"\n{RED}✗ Adversarial workflow not initialized{RESET}")
        print()
        print(f"{BOLD}WHY:{RESET}")
        print("   Agent coordination extends the adversarial-workflow core system.")
        print("   You must initialize the core workflow first.")
        print()
        print(f"{BOLD}FIX:{RESET}")
        print("   1. Run: adversarial init")
        print("   2. Or run: adversarial init --interactive (guided setup)")
        print("   3. Then run: adversarial agent onboard")
        print()
        return 1

    print(f"\n{BOLD}{CYAN}🤖 Agent Coordination System Setup{RESET}")
    print(f"{CYAN}ℹ️{RESET}  Extends adversarial-workflow with agent coordination")
    print()

    # 2. Pre-flight discovery
    existing_agent_context = os.path.exists(".agent-context")
    existing_delegation = os.path.exists("delegation")
    existing_tasks = os.path.exists("tasks")
    existing_agents = os.path.exists("agents")

    print(f"{BOLD}Current project structure:{RESET}")
    print(f"  {'✓' if existing_agent_context else '○'} .agent-context/")
    print(f"  {'✓' if existing_delegation else '○'} delegation/")
    print(f"  {'✓' if existing_agents else '○'} agents/")
    print(f"  {'✓' if existing_tasks else '○'} tasks/")
    print()

    # Check if already set up
    if existing_agent_context and existing_delegation:
        print(f"{YELLOW}⚠️  Agent coordination appears to be already set up{RESET}")
        overwrite = prompt_user("Overwrite existing setup?", default="n")
        if overwrite.lower() not in ["y", "yes"]:
            print("Setup cancelled.")
            return 0

    # 3. Interactive questions (4 max)
    use_delegation = prompt_user("Use delegation/tasks/ structure? (recommended)", "Y").lower() in [
        "y",
        "yes",
        "",
    ]

    organize_docs = prompt_user("Organize root docs into docs/?", "n").lower() in [
        "y",
        "yes",
    ]

    print()

    # 3a. Template selection (optional)
    template_config = select_agent_template()
    template_type = template_config["type"]
    template_url = template_config["url"]

    print()
    print(f"{BOLD}Setting up agent coordination...{RESET}")
    print()

    # 4. Create extension structure
    try:
        # Create .agent-context/
        os.makedirs(".agent-context/session-logs", exist_ok=True)
        print(f"  {GREEN}✅{RESET} Created .agent-context/ directory")

        # Create delegation/ structure if requested
        if use_delegation:
            os.makedirs("delegation/tasks/active", exist_ok=True)
            os.makedirs("delegation/tasks/completed", exist_ok=True)
            os.makedirs("delegation/tasks/analysis", exist_ok=True)
            os.makedirs("delegation/tasks/logs", exist_ok=True)
            os.makedirs("delegation/handoffs", exist_ok=True)
            print(f"  {GREEN}✅{RESET} Created delegation/ directory structure")

        # Create agents/ structure
        os.makedirs("agents/tools", exist_ok=True)
        os.makedirs("agents/launchers", exist_ok=True)
        print(f"  {GREEN}✅{RESET} Created agents/ directory structure")

    except Exception as e:
        print(f"\n{RED}❌ ERROR: Failed to create directories: {e}{RESET}")
        return 1

    # 5. Migrate tasks if needed
    if use_delegation and existing_tasks:
        print()
        print(f"{BOLD}Task Migration:{RESET}")

        # Count task files
        task_files = glob.glob("tasks/**/*.md", recursive=True)

        if len(task_files) > 0:
            print(f"  Found {len(task_files)} task file(s) in tasks/")
            print("  Backup will be created at: tasks.backup/")
            print()

            migrate = prompt_user("Migrate tasks/ → delegation/tasks/active/?", "Y")

            if migrate.lower() in ["y", "yes", ""]:
                try:
                    # Create backup
                    if not os.path.exists("tasks.backup"):
                        shutil.copytree("tasks", "tasks.backup")
                        print(f"  {GREEN}✅{RESET} Backup created: tasks.backup/")

                    # Move task files to delegation/tasks/active/
                    for task_file in task_files:
                        dest_file = os.path.join(
                            "delegation/tasks/active", os.path.basename(task_file)
                        )
                        shutil.copy2(task_file, dest_file)

                    print(
                        f"  {GREEN}✅{RESET} Migrated {len(task_files)} task(s) to delegation/tasks/active/"
                    )
                    print(
                        f"  {CYAN}ℹ️{RESET}  Original tasks/ preserved (remove manually if desired)"
                    )
                    print(f"  {CYAN}ℹ️{RESET}  Rollback: rm -rf tasks && mv tasks.backup tasks")

                except Exception as e:
                    print(f"  {RED}❌{RESET} Migration failed: {e}")
                    print(f"  {YELLOW}⚠️{RESET}  Continuing without migration...")
        else:
            print(f"  {CYAN}ℹ️{RESET}  No task files found in tasks/")

    # 6. Organize documentation
    if organize_docs:
        print()
        print(f"{BOLD}Documentation Organization:{RESET}")

        # Find markdown files in root
        root_docs = [f for f in os.listdir(".") if f.endswith(".md") and not f.startswith(".")]

        if len(root_docs) > 0:
            print(f"  Found {len(root_docs)} markdown file(s) in root")

            try:
                os.makedirs("docs", exist_ok=True)
                moved_count = 0

                for doc in root_docs:
                    # Skip README.md
                    if doc.upper() == "README.MD":
                        continue

                    dest = os.path.join("docs", doc)
                    if not os.path.exists(dest):
                        shutil.move(doc, dest)
                        moved_count += 1

                if moved_count > 0:
                    print(f"  {GREEN}✅{RESET} Organized {moved_count} doc(s) into docs/")
                else:
                    print(f"  {CYAN}ℹ️{RESET}  No docs needed organizing")

            except Exception as e:
                print(f"  {YELLOW}⚠️{RESET}  Could not organize docs: {e}")

    # 7. Render agent coordination templates
    print()
    print(f"{BOLD}Installing agent coordination files...{RESET}")

    try:
        package_dir = Path(__file__).parent
        templates_dir = package_dir / "templates" / "agent-context"

        # Get template variables
        project_name = os.path.basename(os.path.abspath(project_path))
        current_date = datetime.now().strftime("%Y-%m-%d")
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        template_vars = {
            "PROJECT_NAME": project_name,
            "DATE": current_date,
            "PYTHON_VERSION": python_version,
        }

        # Render agent-handoffs.json with selected template
        if template_type != "skip":
            # Fetch the selected template
            template_content = fetch_agent_template(template_url, template_type)

            if template_content:
                # Perform variable substitution
                for key, value in template_vars.items():
                    placeholder = f"{{{{{key}}}}}"
                    template_content = template_content.replace(placeholder, str(value))

                # Write to file
                with open(".agent-context/agent-handoffs.json", "w", encoding="utf-8") as f:
                    f.write(template_content)

                template_name = {
                    "standard": "8 agents",
                    "minimal": "3 agents",
                    "custom": "custom template",
                }[template_type]
                print(
                    f"  {GREEN}✅{RESET} Created .agent-context/agent-handoffs.json ({template_name})"
                )
            else:
                print(f"  {RED}❌{RESET} Failed to fetch agent template")
                return 1
        else:
            print(f"  {CYAN}ℹ️{RESET}  Skipped agent-handoffs.json (manual setup requested)")

        # Render current-state.json
        current_state_template = templates_dir / "current-state.json.template"
        if current_state_template.exists():
            render_template(
                str(current_state_template),
                ".agent-context/current-state.json",
                template_vars,
            )
            print(f"  {GREEN}✅{RESET} Created .agent-context/current-state.json")

        # Render README.md
        readme_template = templates_dir / "README.md.template"
        if readme_template.exists():
            render_template(str(readme_template), ".agent-context/README.md", template_vars)
            print(f"  {GREEN}✅{RESET} Created .agent-context/README.md")

        # Copy AGENT-SYSTEM-GUIDE.md if it exists and isn't already there
        guide_template = templates_dir / "AGENT-SYSTEM-GUIDE.md"
        guide_dest = Path(".agent-context/AGENT-SYSTEM-GUIDE.md")

        if guide_template.exists() and not guide_dest.exists():
            shutil.copy(str(guide_template), str(guide_dest))
            print(f"  {GREEN}✅{RESET} Installed .agent-context/AGENT-SYSTEM-GUIDE.md")
        elif guide_dest.exists():
            print(f"  {CYAN}ℹ️{RESET}  AGENT-SYSTEM-GUIDE.md already exists")

    except Exception as e:
        print(f"\n{RED}❌ ERROR: Failed to render templates: {e}{RESET}")
        return 1

    # 8. Update core config to use delegation
    if use_delegation:
        print()
        print(f"{BOLD}Updating configuration...{RESET}")

        try:
            config_path = ".adversarial/config.yml"
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Update task_directory
            old_task_dir = config.get("task_directory", "tasks/")
            config["task_directory"] = "delegation/tasks/"

            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            print(f"  {GREEN}✅{RESET} Updated .adversarial/config.yml")
            print(f"     task_directory: {old_task_dir} → delegation/tasks/")

        except Exception as e:
            print(f"  {YELLOW}⚠️{RESET}  Could not update config: {e}")
            print("     Manually set task_directory: delegation/tasks/ in .adversarial/config.yml")

    # 9. Update .gitignore
    print()
    print(f"{BOLD}Updating .gitignore...{RESET}")

    try:
        gitignore_path = ".gitignore"
        gitignore_entries = [
            ".agent-context/session-logs/",
            "tasks.backup/",
        ]

        existing_content = ""
        if os.path.exists(gitignore_path):
            with open(gitignore_path, encoding="utf-8") as f:
                existing_content = f.read()

        with open(gitignore_path, "a", encoding="utf-8") as f:
            if existing_content and not existing_content.endswith("\n"):
                f.write("\n")

            f.write("\n# Agent Coordination System\n")
            for entry in gitignore_entries:
                if entry not in existing_content:
                    f.write(f"{entry}\n")

        print(f"  {GREEN}✅{RESET} Updated .gitignore")

    except Exception as e:
        print(f"  {YELLOW}⚠️{RESET}  Could not update .gitignore: {e}")

    # 10. Verify setup
    print()
    print(f"{BOLD}Verifying setup...{RESET}")

    verification_checks = []

    # Check JSON files are valid
    try:
        with open(".agent-context/agent-handoffs.json", encoding="utf-8") as f:
            json.load(f)
        verification_checks.append(("agent-handoffs.json valid", True))
    except Exception as e:
        verification_checks.append((f"agent-handoffs.json invalid: {e}", False))

    try:
        with open(".agent-context/current-state.json", encoding="utf-8") as f:
            json.load(f)
        verification_checks.append(("current-state.json valid", True))
    except Exception as e:
        verification_checks.append((f"current-state.json invalid: {e}", False))

    # Check directories exist
    verification_checks.append((".agent-context/ exists", os.path.exists(".agent-context")))

    if use_delegation:
        verification_checks.append(
            (
                "delegation/tasks/active/ exists",
                os.path.exists("delegation/tasks/active"),
            )
        )

    # Print verification results
    all_passed = True
    for check, passed in verification_checks:
        if passed:
            print(f"  {GREEN}✅{RESET} {check}")
        else:
            print(f"  {RED}❌{RESET} {check}")
            all_passed = False

    if not all_passed:
        print()
        print(f"{YELLOW}⚠️  Some verification checks failed{RESET}")
        print("   Review errors above and run 'adversarial health' for details")
        return 1

    # 11. Success message
    print()
    print(f"{GREEN}✅ Agent coordination setup complete!{RESET}")
    print()
    print(f"{BOLD}What was created:{RESET}")
    print("  ✓ .agent-context/ - Agent coordination files")

    if template_type != "skip":
        agent_count = {
            "standard": "8 agents",
            "minimal": "3 agents",
            "custom": "custom agents",
        }[template_type]
        print(f"  ✓ agent-handoffs.json - {agent_count} initialized")
    else:
        print("  ○ agent-handoffs.json - Manual setup required")

    print("  ✓ current-state.json - Project state tracking")
    print("  ✓ AGENT-SYSTEM-GUIDE.md - Comprehensive guide")
    if use_delegation:
        print("  ✓ delegation/ - Task management structure")
        print("  ✓ Updated .adversarial/config.yml → delegation/tasks/")
    print("  ✓ agents/ - Agent tools and launchers")
    print()
    print(f"{BOLD}Next steps:{RESET}")
    print("  1. Review: .agent-context/AGENT-SYSTEM-GUIDE.md")
    print("  2. Check status: adversarial health")
    print("  3. Create tasks in: delegation/tasks/active/")
    print("  4. Assign agents in: .agent-context/agent-handoffs.json")
    print()
    print(f"{CYAN}ℹ️{RESET}  Agent coordination extends adversarial-workflow core")
    print("   Use both systems together for optimal development workflow")
    print()

    return 0


def split(
    task_file: str,
    strategy: str = "sections",
    max_lines: int = 500,
    dry_run: bool = False,
):
    """Split large task files into smaller evaluable chunks.

    Args:
        task_file: Path to the task file to split
        strategy: Split strategy ('sections', 'phases', or 'manual')
        max_lines: Maximum lines per split (default: 500)
        dry_run: Preview splits without creating files

    Returns:
        Exit code (0 for success, 1 for error)
    """
    from .utils.file_splitter import (
        analyze_task_file,
        generate_split_files,
        split_by_phases,
        split_by_sections,
    )

    try:
        print_box("File Splitting Utility", CYAN)

        # Validate file exists
        if not os.path.exists(task_file):
            print(f"{RED}Error: File not found: {task_file}{RESET}")
            return 1

        # Analyze file
        print(f"📄 Analyzing task file: {task_file}")
        analysis = analyze_task_file(task_file)

        lines = analysis["total_lines"]
        tokens = analysis["estimated_tokens"]
        print(f"   Lines: {lines}")
        print(f"   Estimated tokens: ~{tokens:,}")

        # Check if splitting is recommended
        if lines <= max_lines:
            print(f"{GREEN}✅ File is under recommended limit ({max_lines} lines){RESET}")
            print("No splitting needed.")
            return 0

        print(f"{YELLOW}⚠️  File exceeds recommended limit ({max_lines} lines){RESET}")

        # Read file content for splitting
        with open(task_file, encoding="utf-8") as f:
            content = f.read()

        # Apply split strategy
        if strategy == "sections":
            splits = split_by_sections(content, max_lines=max_lines)
            print("\n💡 Suggested splits (by sections):")
        elif strategy == "phases":
            splits = split_by_phases(content)
            print("\n💡 Suggested splits (by phases):")
        else:
            print(f"{RED}Error: Unknown strategy '{strategy}'. Use 'sections' or 'phases'.{RESET}")
            return 1

        # Display split preview
        for i, split in enumerate(splits, 1):
            filename = f"{Path(task_file).stem}-part{i}{Path(task_file).suffix}"
            print(f"   - {filename} ({split['line_count']} lines)")

        # Dry run mode
        if dry_run:
            print(f"\n{CYAN}📋 Dry run mode - no files created{RESET}")
            return 0

        # Prompt user for confirmation
        create_files = prompt_user(f"\nCreate {len(splits)} files?", default="n")

        if create_files.lower() in ["y", "yes"]:
            # Create output directory
            output_dir = os.path.join(os.path.dirname(task_file), "splits")

            # Generate split files
            created_files = generate_split_files(task_file, splits, output_dir)

            print(f"{GREEN}✅ Created {len(created_files)} files:{RESET}")
            for file_path in created_files:
                print(f"   {file_path}")

            print(f"\n{CYAN}💡 Tip: Evaluate each split file independently:{RESET}")
            for file_path in created_files:
                rel_path = os.path.relpath(file_path)
                print(f"   adversarial evaluate {rel_path}")
        else:
            print("Cancelled - no files created.")

        return 0

    except Exception as e:
        print(f"{RED}Error during file splitting: {e}{RESET}")
        return 1


def list_evaluators() -> int:
    """List all available evaluators (built-in and local)."""
    from adversarial_workflow.evaluators import (
        BUILTIN_EVALUATORS,
        discover_local_evaluators,
    )

    # Print built-in evaluators
    print(f"{BOLD}Built-in Evaluators:{RESET}")
    for name, config in sorted(BUILTIN_EVALUATORS.items()):
        print(f"  {name:14} {config.description}")

    print()

    # Print local evaluators
    local_evaluators = discover_local_evaluators()
    if local_evaluators:
        print(f"{BOLD}Local Evaluators{RESET} (.adversarial/evaluators/):")

        # Group by primary name (skip aliases)
        seen_configs = set()
        for _, config in sorted(local_evaluators.items()):
            if id(config) in seen_configs:
                continue
            seen_configs.add(id(config))

            print(f"  {config.name:14} {config.description}")
            if config.aliases:
                print(f"    aliases: {', '.join(config.aliases)}")
            print(f"    model: {config.model}")
            if config.version != "1.0.0":
                print(f"    version: {config.version}")
    else:
        print(f"{GRAY}No local evaluators found.{RESET}")
        print()
        print("Create .adversarial/evaluators/*.yml to add custom evaluators.")
        print("See: https://github.com/movito/adversarial-workflow#custom-evaluators")

    return 0


def check_citations(
    file_path: str,
    output_tasks: str | None = None,
    mark_inline: bool = False,
    concurrency: int = 10,
    timeout: int = 10,
) -> int:
    """
    Check citations (URLs) in a document.

    Args:
        file_path: Path to document to check
        output_tasks: Optional path to write blocked URL tasks
        mark_inline: Whether to mark URLs inline with status badges
        concurrency: Maximum concurrent URL checks
        timeout: Timeout per URL in seconds

    Returns:
        0 on success, 1 on error
    """
    from adversarial_workflow.utils.citations import (
        URLStatus,
        check_urls,
        extract_urls,
        generate_blocked_tasks,
        mark_urls_inline,
        print_verification_summary,
    )

    # Check file exists
    if not os.path.exists(file_path):
        print(f"{RED}Error: File not found: {file_path}{RESET}")
        return 1

    # Validate parameters
    if concurrency < 1:
        print(f"{RED}Error: Concurrency must be at least 1, got {concurrency}{RESET}")
        return 1
    if timeout < 1:
        print(f"{RED}Error: Timeout must be at least 1 second, got {timeout}{RESET}")
        return 1

    print(f"🔗 Checking citations in: {file_path}")
    print()

    # Read document
    with open(file_path, encoding="utf-8") as f:
        document = f.read()

    # Extract URLs
    extracted = extract_urls(document)
    urls = [e.url for e in extracted]

    if not urls:
        print(f"{YELLOW}No URLs found in document.{RESET}")
        return 0

    print(f"   Found {len(urls)} URLs to check")
    print(f"   Checking with concurrency={concurrency}, timeout={timeout}s...")
    print()

    # Check URLs
    results = check_urls(
        urls,
        concurrency=concurrency,
        timeout=timeout,
    )

    # Print summary
    print_verification_summary(results)

    # Count blocked/broken
    blocked_count = sum(1 for r in results if r.status in (URLStatus.BLOCKED, URLStatus.BROKEN))

    # Mark document inline if requested
    if mark_inline and results:
        marked_document = mark_urls_inline(document, results)
        if marked_document != document:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(marked_document)
            print("\n   ✅ Updated document with status badges")

    # Generate blocked tasks if requested or if there are blocked URLs
    if blocked_count > 0:
        if output_tasks:
            output_path = Path(output_tasks)
        else:
            # Default to .adversarial/blocked-citations/
            output_dir = Path.cwd() / ".adversarial" / "blocked-citations"
            output_dir.mkdir(parents=True, exist_ok=True)
            base_name = Path(file_path).stem
            output_path = output_dir / f"{base_name}-blocked-urls.md"

        task_content = generate_blocked_tasks(results, file_path, output_path)
        if task_content:
            print(f"   📋 Blocked URL tasks: {output_path}")

    return 0


def main():
    """Main CLI entry point."""
    import logging
    import sys

    # Load .env file before any commands run
    # Wrapped in try/except so CLI remains usable even with malformed .env
    try:
        load_dotenv()
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}", file=sys.stderr)

    # Load .env file before any commands run
    # Use explicit path to ensure we find .env in current working directory
    # (load_dotenv() without args can fail to find .env in some contexts)
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        try:
            load_dotenv(env_file)
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: Could not load .env file: {e}", file=sys.stderr)

    from adversarial_workflow.evaluators import (
        BUILTIN_EVALUATORS,
        discover_local_evaluators,
        get_all_evaluators,
        run_evaluator,
    )

    logger = logging.getLogger(__name__)

    # Commands that cannot be overridden by evaluators
    # Note: 'review' is special - it reviews git changes without a file argument
    STATIC_COMMANDS = {
        "init",
        "check",
        "doctor",
        "health",
        "quickstart",
        "agent",
        "library",
        "split",
        "validate",
        "review",
        "list-evaluators",
        "check-citations",
    }

    parser = argparse.ArgumentParser(
        description="Adversarial Workflow - Multi-stage AI code review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  adversarial init                      # Initialize in current project
  adversarial init --interactive        # Interactive setup wizard
  adversarial quickstart                # Quick start with example
  adversarial check                     # Validate setup
  adversarial agent onboard             # Set up agent coordination
  adversarial evaluate tasks/feat.md    # Evaluate plan
  adversarial proofread docs/guide.md   # Proofread teaching content
  adversarial review <task_file>         # Review implementation
  adversarial validate "npm test"       # Validate with tests
  adversarial split large-task.md       # Split large files
  adversarial check-citations doc.md    # Verify URLs in document
  adversarial library list              # Browse available evaluators
  adversarial library install google/gemini-flash  # Install evaluator

For more information: https://github.com/movito/adversarial-workflow
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"adversarial-workflow {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize workflow in project")
    init_parser.add_argument(
        "--path", default=".", help="Project path (default: current directory)"
    )
    init_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive setup wizard"
    )
    init_parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing config without prompting"
    )

    # quickstart command
    subparsers.add_parser(
        "quickstart", help="Quick start with example task (recommended for new users)"
    )

    # check command (with doctor alias)
    subparsers.add_parser("check", help="Validate setup and dependencies")
    subparsers.add_parser("doctor", help="Alias for 'check'")

    # health command
    health_parser = subparsers.add_parser("health", help="Comprehensive system health check")
    health_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed diagnostics"
    )
    health_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # agent command (with subcommands)
    agent_parser = subparsers.add_parser("agent", help="Agent coordination commands")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_subcommand", help="Agent subcommand")

    # agent onboard subcommand
    onboard_parser = agent_subparsers.add_parser("onboard", help="Set up agent coordination system")
    onboard_parser.add_argument(
        "--path", default=".", help="Project path (default: current directory)"
    )

    # library command (with subcommands)
    library_parser = subparsers.add_parser(
        "library", help="Browse and install evaluators from the community library"
    )
    library_subparsers = library_parser.add_subparsers(
        dest="library_subcommand", help="Library subcommand"
    )

    # library list subcommand
    library_list_parser = library_subparsers.add_parser(
        "list", help="List available evaluators from the library"
    )
    library_list_parser.add_argument(
        "--provider", "-p", help="Filter by provider (e.g., google, openai)"
    )
    library_list_parser.add_argument(
        "--category", "-c", help="Filter by category (e.g., quick-check, deep-reasoning)"
    )
    library_list_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed information"
    )
    library_list_parser.add_argument(
        "--no-cache", action="store_true", help="Bypass cache and fetch fresh data"
    )

    # library info subcommand
    library_info_parser = library_subparsers.add_parser(
        "info", help="Show detailed information about an evaluator"
    )
    library_info_parser.add_argument(
        "evaluator_spec", help="Evaluator to show info for (format: provider/name)"
    )

    # library install subcommand
    library_install_parser = library_subparsers.add_parser(
        "install", help="Install evaluator(s) from the library"
    )
    library_install_parser.add_argument(
        "evaluators", nargs="*", help="Evaluator(s) to install (format: provider/name)"
    )
    library_install_parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing files"
    )
    library_install_parser.add_argument(
        "--skip-validation", action="store_true", help="Skip YAML validation (advanced)"
    )
    library_install_parser.add_argument(
        "--dry-run", action="store_true", help="Preview without making changes"
    )
    library_install_parser.add_argument("--category", help="Install all evaluators in a category")
    library_install_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompts (required for CI/CD)"
    )

    # library check-updates subcommand
    library_check_parser = library_subparsers.add_parser(
        "check-updates", help="Check for updates to installed evaluators"
    )
    library_check_parser.add_argument(
        "name", nargs="?", help="Specific evaluator to check (optional)"
    )
    library_check_parser.add_argument(
        "--no-cache", action="store_true", help="Bypass cache and fetch fresh data"
    )

    # library update subcommand
    library_update_parser = library_subparsers.add_parser(
        "update", help="Update installed evaluator(s) to newer versions"
    )
    library_update_parser.add_argument("name", nargs="?", help="Evaluator name to update")
    library_update_parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        dest="all_evaluators",
        help="Update all outdated evaluators",
    )
    library_update_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompts"
    )
    library_update_parser.add_argument(
        "--diff-only", action="store_true", help="Show diff without applying changes"
    )
    library_update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without making changes (same as --diff-only)",
    )
    library_update_parser.add_argument(
        "--no-cache", action="store_true", help="Bypass cache and fetch fresh data"
    )

    # review command
    review_parser = subparsers.add_parser("review", help="Run Phase 3: Code review")
    review_parser.add_argument("task_file", help="Task file path")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Run Phase 4: Test validation")
    validate_parser.add_argument("test_command", nargs="?", help="Test command to run (optional)")

    # split command
    split_parser = subparsers.add_parser(
        "split", help="Split large task files into smaller evaluable chunks"
    )
    split_parser.add_argument("task_file", help="Task file to split")
    split_parser.add_argument(
        "--strategy",
        "-s",
        choices=["sections", "phases"],
        default="sections",
        help="Split strategy: 'sections' (default) or 'phases'",
    )
    split_parser.add_argument(
        "--max-lines",
        "-m",
        type=int,
        default=500,
        help="Maximum lines per split (default: 500)",
    )
    split_parser.add_argument(
        "--dry-run", action="store_true", help="Preview splits without creating files"
    )

    # list-evaluators command
    subparsers.add_parser(
        "list-evaluators",
        help="List all available evaluators (built-in and local)",
    )

    # check-citations command
    citations_parser = subparsers.add_parser(
        "check-citations",
        help="Verify URLs in a document before evaluation",
    )
    citations_parser.add_argument("file", help="Document to check citations in")
    citations_parser.add_argument(
        "--output-tasks",
        "-o",
        help="Output file for blocked URL tasks (markdown)",
    )
    citations_parser.add_argument(
        "--mark-inline",
        action="store_true",
        default=False,
        help="Mark URLs inline with status badges (modifies document)",
    )
    citations_parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=10,
        help="Maximum concurrent URL checks (default: 10)",
    )
    citations_parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=10,
        help="Timeout per URL in seconds (default: 10)",
    )

    # Dynamic evaluator registration
    try:
        evaluators = get_all_evaluators()
    except Exception as e:
        logger.warning("Evaluator discovery failed: %s", e)
        evaluators = BUILTIN_EVALUATORS

    registered_configs = set()  # Track by id() to avoid duplicate alias registration

    for name, config in evaluators.items():
        # Skip if name conflicts with static command
        if name in STATIC_COMMANDS:
            # Only warn for user-defined evaluators, not built-ins
            # Built-in conflicts are intentional (e.g., 'review' command vs 'review' evaluator)
            if getattr(config, "source", None) != "builtin":
                logger.warning("Evaluator '%s' conflicts with CLI command; skipping", name)
            # Mark as registered to prevent alias re-registration attempts
            registered_configs.add(id(config))
            continue

        # Skip if this config was already registered (aliases share config object)
        if id(config) in registered_configs:
            continue
        registered_configs.add(id(config))

        # Filter aliases that conflict with static commands
        aliases = [a for a in (config.aliases or []) if a not in STATIC_COMMANDS]
        if config.aliases and len(aliases) != len(config.aliases):
            skipped = [a for a in config.aliases if a in STATIC_COMMANDS]
            logger.warning(
                "Skipping evaluator aliases that conflict with static commands: %s",
                skipped,
            )

        # Create subparser for this evaluator
        eval_parser = subparsers.add_parser(
            config.name,
            help=config.description,
            aliases=aliases,
        )
        eval_parser.add_argument("file", help="File to evaluate")
        eval_parser.add_argument(
            "--timeout",
            "-t",
            type=int,
            default=None,
            help="Timeout in seconds (default: from evaluator config or 180, max: 600)",
        )
        eval_parser.add_argument(
            "--check-citations",
            action="store_true",
            help="Verify URLs in document before evaluation",
        )
        # Add --evaluator flag for the "evaluate" command only
        # This allows selecting a library-installed evaluator
        if config.name == "evaluate":
            eval_parser.add_argument(
                "--evaluator",
                "-e",
                metavar="NAME",
                help="Use a specific evaluator from .adversarial/evaluators/",
            )
        # Store config for later execution
        eval_parser.set_defaults(evaluator_config=config)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Check for evaluator command first (has evaluator_config attribute)
    if hasattr(args, "evaluator_config"):
        # Default to the command's evaluator config
        config_to_use = args.evaluator_config

        # Check if --evaluator flag was specified (only on evaluate command)
        evaluator_override = getattr(args, "evaluator", None)
        if evaluator_override:
            local_evaluators = discover_local_evaluators()

            if not local_evaluators:
                print(f"{RED}Error: No evaluators installed.{RESET}")
                print("Install evaluators with: adversarial library install <name>")
                return 1

            if evaluator_override not in local_evaluators:
                print(f"{RED}Error: Evaluator '{evaluator_override}' not found.{RESET}")
                print()
                print("Available evaluators:")
                # Show unique evaluators (avoid duplicates from aliases)
                seen = set()
                for _, cfg in sorted(local_evaluators.items()):
                    if id(cfg) not in seen:
                        print(f"  {cfg.name}")
                        if cfg.aliases:
                            print(f"    aliases: {', '.join(cfg.aliases)}")
                        seen.add(id(cfg))
                return 1

            config_to_use = local_evaluators[evaluator_override]
            print(f"Using evaluator: {config_to_use.name}")

        # Determine timeout: CLI flag > YAML config > default (180s)
        if args.timeout is not None:
            timeout = args.timeout
            source = "CLI override"
        elif config_to_use.timeout != 180:
            timeout = config_to_use.timeout
            source = "evaluator config"
        else:
            timeout = config_to_use.timeout  # 180 (default)
            source = "default"

        # Validate CLI timeout (consistent with YAML validation)
        if timeout <= 0:
            print(f"{RED}Error: Timeout must be positive (> 0), got {timeout}{RESET}")
            return 1
        if timeout > 600:
            print(
                f"{YELLOW}Warning: Timeout {timeout}s exceeds maximum (600s), clamping to 600s{RESET}"
            )
            timeout = 600

        # Log actual timeout and source
        print(f"Using timeout: {timeout}s ({source})")

        # Check citations first if requested (read-only, doesn't modify file)
        if getattr(args, "check_citations", False):
            print()
            result = check_citations(args.file, mark_inline=False)
            if result != 0:
                print(
                    f"{YELLOW}Warning: Citation check had issues, continuing with evaluation...{RESET}"
                )
            print()

        return run_evaluator(
            config_to_use,
            args.file,
            timeout=timeout,
        )

    # Execute static commands
    if args.command == "init":
        if args.interactive:
            return init_interactive(args.path)
        else:
            # --force skips confirmation prompts
            return init(args.path, interactive=not args.force)
    elif args.command == "quickstart":
        return quickstart()
    elif args.command in ["check", "doctor"]:
        return check()
    elif args.command == "health":
        return health(verbose=args.verbose, json_output=args.json)
    elif args.command == "agent":
        if args.agent_subcommand == "onboard":
            return agent_onboard(args.path)
        else:
            # No subcommand provided
            print(f"{RED}Error: agent command requires a subcommand{RESET}")
            print("Usage: adversarial agent onboard")
            return 1
    elif args.command == "library":
        from adversarial_workflow.library import (
            library_check_updates,
            library_info,
            library_install,
            library_list,
            library_update,
        )

        if args.library_subcommand == "list":
            return library_list(
                provider=args.provider,
                category=args.category,
                verbose=args.verbose,
                no_cache=args.no_cache,
            )
        elif args.library_subcommand == "info":
            return library_info(
                evaluator_spec=args.evaluator_spec,
            )
        elif args.library_subcommand == "install":
            return library_install(
                evaluator_specs=args.evaluators,
                force=args.force,
                skip_validation=args.skip_validation,
                dry_run=args.dry_run,
                category=args.category,
                yes=args.yes,
            )
        elif args.library_subcommand == "check-updates":
            return library_check_updates(
                name=args.name,
                no_cache=args.no_cache,
            )
        elif args.library_subcommand == "update":
            return library_update(
                name=args.name,
                all_evaluators=args.all_evaluators,
                yes=args.yes,
                diff_only=args.diff_only,
                no_cache=args.no_cache,
                dry_run=args.dry_run,
            )
        else:
            # No subcommand provided
            print(f"{RED}Error: library command requires a subcommand{RESET}")
            print("Usage:")
            print("  adversarial library list")
            print("  adversarial library info <provider>/<name>")
            print("  adversarial library install <provider>/<name>")
            print("  adversarial library check-updates")
            print("  adversarial library update <name>")
            return 1
    elif args.command == "review":
        return review(args.task_file)
    elif args.command == "validate":
        return validate(args.test_command)
    elif args.command == "split":
        return split(
            args.task_file,
            strategy=args.strategy,
            max_lines=args.max_lines,
            dry_run=args.dry_run,
        )
    elif args.command == "list-evaluators":
        return list_evaluators()
    elif args.command == "check-citations":
        return check_citations(
            args.file,
            output_tasks=args.output_tasks,
            mark_inline=args.mark_inline,
            concurrency=args.concurrency,
            timeout=args.timeout,
        )
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### pyproject.toml (COMPLETE FILE)

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "adversarial-workflow"

version = "1.0.0"

description = "Multi-stage AI evaluation system for task plans, code review, and test validation"
readme = "README.md"
authors = [
    {name = "Fredrik Matheson"}
]
license = {text = "MIT"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Software Development :: Testing",
]
keywords = ["code-review", "ai", "llm", "quality", "testing", "litellm"]
requires-python = ">=3.10"
dependencies = [
    "pyyaml>=6.0",
    "python-dotenv>=0.19.0",
    "litellm>=1.40.0",
    "aiohttp>=3.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=3.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.14.7",
    "tomli>=2.0; python_version < '3.11'",
]

[project.urls]
Homepage = "https://github.com/movito/adversarial-workflow"
Documentation = "https://github.com/movito/adversarial-workflow/blob/main/README.md"
Repository = "https://github.com/movito/adversarial-workflow"
Issues = "https://github.com/movito/adversarial-workflow/issues"

[project.scripts]
adversarial = "adversarial_workflow.cli:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["adversarial_workflow*"]

[tool.setuptools.package-data]
adversarial_workflow = ["templates/*", "templates/.*", "templates/agent-context/*"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
external = ["DK001", "DK002", "DK003", "DK004"]  # Custom pattern lint rules (scripts/pattern_lint.py)
select = [
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "W",      # pycodestyle warnings
    "I",      # isort (import sorting)
    "N",      # pep8-naming
    "B",      # flake8-bugbear (defensive coding)
    "SIM",    # flake8-simplify
    "ARG",    # unused arguments
    "UP",     # pyupgrade (modern Python)
    "S",      # flake8-bandit (security basics)
    "RUF",    # ruff-specific rules
]
ignore = [
    "E203",   # conflicts with Black-style formatting
    "S101",   # assert used -- fine in tests
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["ARG", "S", "F841", "SIM103", "SIM105", "SIM117", "RUF059"]
"scripts/**" = ["S603", "S607", "S110"]
"adversarial_workflow/cli.py" = ["E501", "E722", "E741", "SIM108", "SIM102", "SIM103", "SIM118", "N806", "S103", "S110", "S310", "S603", "S607", "ARG001", "F841", "RUF001", "RUF013"]
"adversarial_workflow/evaluators/runner.py" = ["ARG001"]
"adversarial_workflow/library/client.py" = ["S310"]
"adversarial_workflow/library/cache.py" = ["SIM105"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
markers = [
    "network: marks tests as requiring network access (deselect with '-m not network')",
]
```

### tests/conftest.py (COMPLETE FILE)

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

### tests/test_cli.py (COMPLETE FILE)

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

    def test_help_flag(self, run_cli):
        """Test that --help returns help text."""
        result = run_cli(["--help"])
        assert result.returncode == 0
        help_text = result.stdout.lower()
        assert any(cmd in help_text for cmd in ["evaluate", "init", "check", "health"])

    def test_no_command_shows_help(self, run_cli):
        """Test that no command shows help text."""
        result = run_cli([])
        assert result.returncode == 0
        help_text = result.stdout.lower()
        assert "usage" in help_text or "help" in help_text

    def test_evaluate_without_file_shows_error(self, run_cli):
        """Test that evaluate without a file shows an error."""
        result = run_cli(["evaluate"])
        # Should fail because no file was provided
        assert result.returncode != 0

    def test_init_help(self, run_cli):
        """Test that init command help works."""
        result = run_cli(["init", "--help"])
        assert result.returncode == 0
        assert "workflow" in result.stdout.lower() or "init" in result.stdout.lower()

    def test_check_help(self, run_cli):
        """Test that check command help works."""
        result = run_cli(["check", "--help"])
        assert result.returncode == 0
        assert "validate" in result.stdout.lower() or "check" in result.stdout.lower()

    def test_health_help(self, run_cli):
        """Test that health command help works."""
        result = run_cli(["health", "--help"])
        assert result.returncode == 0
        assert "health" in result.stdout.lower()


class TestCLIDirectImport:
    """Test CLI functions by importing them directly."""

    def test_main_function_exists(self):
        """Test that main function can be imported."""
        assert callable(main)

    def test_load_config_function_exists(self):
        """Test that load_config function can be imported."""
        assert callable(load_config)

    def test_check_function_exists(self):
        """Test that check function can be imported."""
        assert callable(check)

    def test_health_function_exists(self):
        """Test that health function can be imported."""
        assert callable(health)

    @patch("sys.argv", ["adversarial", "--version"])
    @patch("sys.exit")
    def test_main_with_version_arg(self, mock_exit):
        """Test main function with version argument."""
        with patch("builtins.print") as mock_print:
            try:
                main()
            except SystemExit:
                pass
        # Should have called print or exit
        assert mock_exit.called or mock_print.called

    @patch("sys.argv", ["adversarial"])
    def test_main_with_no_args(self):
        """Test main function with no arguments shows help."""
        result = main()
        # Should return 0 (showing help is not an error)
        assert result == 0

    @patch("os.path.exists", return_value=False)
    def test_load_config_missing_file(self, mock_exists):
        """Test load_config with missing config file."""
        result = load_config("nonexistent.yaml")
        # Should return default configuration for missing file
        assert isinstance(result, dict)
        assert "evaluator_model" in result

    @patch("subprocess.run")
    def test_check_function_basic(self, mock_run):
        """Test check function basic execution."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        # Should not raise an exception
        result = check()
        # check() function should return an integer exit code
        assert isinstance(result, int)

    @patch("subprocess.run")
    def test_health_function_basic(self, mock_run):
        """Test health function basic execution."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        # Should not raise an exception
        result = health()
        # health() function should return an integer exit code
        assert isinstance(result, int)


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    def test_invalid_command(self, run_cli):
        """Test that invalid command shows error."""
        result = run_cli(["invalid_command"])
        # Should show help (return code 1) for invalid command
        assert result.returncode != 0 or "usage" in result.stdout.lower()

    def test_evaluate_with_nonexistent_file(self, run_cli):
        """Test evaluate command with nonexistent file."""
        result = run_cli(["evaluate", "nonexistent.md"])
        # Should fail with appropriate error
        assert result.returncode != 0

    def test_agent_without_subcommand(self, run_cli):
        """Test agent command without subcommand shows error."""
        result = run_cli(["agent"])
        # Should fail and show usage
        assert result.returncode != 0
```

### CHANGELOG.md (first 50 lines — 1.0.0 section)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-04-14

### Changed
- **`.kit/` directory migration** — builder infrastructure moved into `.kit/` hierarchy (ADV-0068)
- **Root declutter** — root reduced from 15 to 9 files; manifest upgraded to v2.0.0 (ADV-0069)
- **docs/ consolidation** — 9 subdirectories → 4: adr/, archive/, guides/, reference/ (ADV-0070)
- **Agent definitions** — updated to latest models with standardized frontmatter metadata
- **Monitoring sub-agent** — now runs in worktree isolation with no-commit guardrail
- **Version management** — removed hardcoded fallback versions; single source of truth via pyproject.toml

### Removed
- 7 obsolete agent definitions (v1, v3, v4, sonnet-v3, planner, test-runner, ci-checker)
- `docs/decisions/` nesting layer — ADRs now at `docs/adr/` directly
- Historical docs directories consolidated into `docs/archive/`

### Fixed
- **Launcher scripts** — PROJECT_ROOT resolution fixed after .kit/ migration
- **Bot-watcher agent reference** — replaced non-existent agent type with general-purpose
- **Version fallback** — removed stale hardcoded version strings that caused test failures

## [0.9.10] - 2026-04-13

### Removed

- **Aider dependency** — all evaluators now use LiteLLM directly (ADV-0065, ADV-0066)
- Dead shell scripts (`.adversarial/scripts/`), templates, and investigation files
- `shutil.which("aider")` checks from CLI `init`, `check`, `evaluate`, `review`, `validate` commands
- `pip install aider-chat` from CI workflow
- Python <3.13 upper bound constraint (Python 3.13+ now supported)
- Aider references from README, SETUP, QUICK_START, and agent docs
- ~420 lines of dead/duplicate verdict-extraction code from `cli.evaluate()` (ADV-0067)
- Orphaned helper functions (`verify_token_count`, `extract_verdict`, `get_evaluation_summary`, `format_verdict_message`) and unused `import re`, `import glob`

### Changed

- `adversarial init` no longer creates `.aider.conf.yml`
- `adversarial check` no longer validates aider installation
- Updated user-facing docs to reference LiteLLM instead of aider
- `cli.evaluate()` now follows the same clean pattern as `cli.review()` — delegates fully to `run_evaluator()` (ADV-0067)

### Fixed
```

### README.md (last 10 lines — version footer)

```markdown

## Credits

Developed by [broadcaster_one](https://github.com/movito) and refined through months of production use on the thematic-cuts project.

**Inspired by**: The realization that AI needs AI to keep it honest.

---

*Version 1.0.0*
```

## Test Results

- 530/530 tests pass
- ci-check.sh fully green (format, lint, pattern lint, tests)
- CI green on GitHub for all commits
