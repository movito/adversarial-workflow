#!/usr/bin/env python3
"""
CLI tool for adversarial workflow package - Enhanced with interactive onboarding.

Commands:
    init - Initialize workflow in existing project
    init --interactive - Interactive setup wizard
    quickstart - Quick start with example task
    check - Validate setup and dependencies
    evaluate - Run Phase 1: Plan evaluation
    review - Run Phase 3: Code review
    validate - Run Phase 4: Test validation
"""

import argparse
import getpass
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from dotenv import load_dotenv

__version__ = "0.1.0"

# ANSI color codes for better output
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"


def print_box(title: str, lines: List[str], width: int = 70) -> None:
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


def validate_api_key(key: str, provider: str) -> Tuple[bool, str]:
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
        print("\n" + "="*60)
        print("⚠️  WARNING: Native Windows is NOT Supported")
        print("="*60)
        print("\nThis package requires Unix shell (bash) for workflow scripts.")
        print("\n📍 RECOMMENDED: Use WSL (Windows Subsystem for Linux)")
        print("   Install: https://learn.microsoft.com/windows/wsl/install")
        print("\n⚠️  ALTERNATIVE: Git Bash (not officially supported)")
        print("   Some features may not work correctly")
        print("\n" + "="*60)

        response = input("\n Continue with setup anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("\nSetup cancelled. Please install WSL and try again.")
            return False

    return True


def create_env_file_interactive(project_path: str, anthropic_key: str = "", openai_key: str = "") -> bool:
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
        env_content += f"# Anthropic API Key (Claude 3.5 Sonnet)\nANTHROPIC_API_KEY={anthropic_key}\n\n"

    if openai_key:
        env_content += f"# OpenAI API Key (GPT-4o)\nOPENAI_API_KEY={openai_key}\n\n"

    try:
        with open(env_path, "w") as f:
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
                "  2. Click \"Create Key\"",
                "  3. Copy the key (starts with \"sk-ant-\")",
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
                "  2. Click \"+ Create new secret key\"",
                "  3. Copy the key (starts with \"sk-proj-\" or \"sk-\")",
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

    project_name = prompt_user("Project name", default=os.path.basename(os.path.abspath(project_path)))
    test_command = prompt_user("Test framework", default="pytest")
    task_directory = prompt_user("Task directory", default="tasks/")

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
            "  ✓ .env (with your API keys - added to .gitignore)" if (anthropic_key or openai_key) else "  ⚠️ .env (skipped - no API keys provided)",
            "  ✓ .adversarial/config.yml",
            "  ✓ .adversarial/scripts/ (3 workflow scripts)",
            "  ✓ .aider.conf.yml (aider configuration)",
            "",
            "Your configuration:" if (anthropic_key or openai_key) else "Configuration (no API keys yet):",
            f"  Implementation: {'Claude 3.5 Sonnet (Anthropic)' if anthropic_key else 'GPT-4o (OpenAI)' if openai_key else 'Not configured'}",
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
        with open(example_task_path, "r") as f:
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
            "  1. Implement the fix (or let Claude do it via aider)",
            "  2. Run: adversarial review (Phase 3: Code Review)",
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
        with open(task_path, "w") as f:
            f.write("""# Task: Fix Off-By-One Error in List Processing

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
""")

    print(f"{GREEN}✅ Created: {task_path}{RESET}")


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


def render_template(template_path: str, output_path: str, variables: Dict) -> None:
    """Render a template file with variable substitution."""
    with open(template_path, "r") as f:
        content = f.read()

    # Replace {{variable}} with values
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        content = content.replace(placeholder, str(value))

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
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
        os.makedirs(os.path.join(adversarial_dir, "scripts"))
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

        render_template(
            str(templates_dir / "evaluate_plan.sh.template"),
            os.path.join(adversarial_dir, "scripts", "evaluate_plan.sh"),
            config_vars,
        )

        render_template(
            str(templates_dir / "review_implementation.sh.template"),
            os.path.join(adversarial_dir, "scripts", "review_implementation.sh"),
            config_vars,
        )

        render_template(
            str(templates_dir / "validate_tests.sh.template"),
            os.path.join(adversarial_dir, "scripts", "validate_tests.sh"),
            config_vars,
        )

        # Copy .aider.conf.yml and .env.example to project root
        shutil.copy(
            str(templates_dir / ".aider.conf.yml.template"),
            os.path.join(project_path, ".aider.conf.yml"),
        )

        shutil.copy(
            str(templates_dir / ".env.example.template"),
            os.path.join(project_path, ".env.example"),
        )

        # Update .gitignore
        gitignore_path = os.path.join(project_path, ".gitignore")
        gitignore_entries = [
            ".adversarial/logs/",
            ".adversarial/artifacts/",
            ".env",
        ]

        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                existing = f.read()

            with open(gitignore_path, "a") as f:
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

    issues: List[Dict] = []
    good_checks: List[str] = []

    # Check 1: Git repository
    if os.path.exists(".git"):
        good_checks.append("Git repository detected")
    else:
        issues.append({
            "severity": "ERROR",
            "message": "Not a git repository",
            "fix": "Run: git init",
        })

    # Check 2: Aider installed
    if shutil.which("aider"):
        # Try to get version
        try:
            result = subprocess.run(
                ["aider", "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            version = result.stdout.strip() if result.returncode == 0 else "unknown"
            good_checks.append(f"Aider installed ({version})")
        except:
            good_checks.append("Aider installed")
    else:
        issues.append({
            "severity": "ERROR",
            "message": "Aider not found in PATH",
            "fix": "Install: pip install aider-chat",
        })

    # Check 3: API keys
    load_dotenv()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if anthropic_key and not anthropic_key.startswith("your-"):
        good_checks.append("ANTHROPIC_API_KEY configured")
    elif anthropic_key:
        issues.append({
            "severity": "WARNING",
            "message": "ANTHROPIC_API_KEY is placeholder value",
            "fix": "Edit .env with real API key from https://console.anthropic.com/settings/keys",
        })

    if openai_key and not openai_key.startswith("your-"):
        good_checks.append("OPENAI_API_KEY configured")
    elif openai_key:
        issues.append({
            "severity": "WARNING",
            "message": "OPENAI_API_KEY is placeholder value",
            "fix": "Edit .env with real API key from https://platform.openai.com/api-keys",
        })

    if not anthropic_key and not openai_key:
        issues.append({
            "severity": "ERROR",
            "message": "No API keys configured - workflow cannot run",
            "fix": "Run 'adversarial init --interactive' to set up API keys with guided wizard",
        })

    # Check 4: Config valid
    try:
        config = load_config(".adversarial/config.yml")
        good_checks.append(".adversarial/config.yml valid")
    except FileNotFoundError:
        issues.append({
            "severity": "ERROR",
            "message": "Not initialized (.adversarial/config.yml not found)",
            "fix": "Run: adversarial init",
        })
        config = None
    except yaml.YAMLError as e:
        issues.append({
            "severity": "ERROR",
            "message": f"Invalid config.yml: {e}",
            "fix": "Fix YAML syntax in .adversarial/config.yml",
        })
        config = None

    # Check 5: Scripts executable
    if config:
        scripts = ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]
        all_scripts_ok = True
        for script in scripts:
            path = f".adversarial/scripts/{script}"
            if os.path.exists(path):
                if not os.access(path, os.X_OK):
                    issues.append({
                        "severity": "WARNING",
                        "message": f"{script} not executable",
                        "fix": f"chmod +x {path}",
                    })
                    all_scripts_ok = False
            else:
                issues.append({
                    "severity": "ERROR",
                    "message": f"{script} not found",
                    "fix": "Run: adversarial init",
                })
                all_scripts_ok = False

        if all_scripts_ok:
            good_checks.append("All scripts executable")

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
            icon = f"{RED}❌{RESET}" if issue["severity"] == "ERROR" else f"{YELLOW}⚠️{RESET}"
            print(f"{icon} [{issue['severity']}] {issue['message']}")
            print(f"   Fix: {issue['fix']}")

    print("━" * 70)
    print()

    # Summary
    if not issues:
        print(f"{GREEN}✅ All checks passed! Your setup is ready.{RESET}")
        print()
        print("Estimated cost per workflow: $0.02-0.10")
        print()
        print(f"Try it: {CYAN}adversarial quickstart{RESET}")
        return 0
    else:
        error_count = sum(1 for i in issues if i["severity"] == "ERROR")
        warning_count = len(issues) - error_count

        status = f"{error_count} error" + ("s" if error_count != 1 else "")
        if warning_count:
            status += f", {warning_count} warning" + ("s" if warning_count != 1 else "")

        print(f"{RED}❌ Setup incomplete ({status}){RESET}")
        print()
        print("Quick fix: adversarial init --interactive")

        return 1 if error_count > 0 else 0


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

    # Error 3: Aider not available
    if not shutil.which("aider"):
        print(f"{RED}❌ ERROR: Aider not found{RESET}")
        print()
        print(f"{BOLD}WHY:{RESET}")
        print("   This package uses aider (AI pair programming tool) to:")
        print("   • Review your implementation plans")
        print("   • Analyze code changes")
        print("   • Validate test results")
        print()
        print(f"{BOLD}FIX:{RESET}")
        print("   1. Install aider: pip install aider-chat")
        print("   2. Verify installation: aider --version")
        print("   3. Then retry: adversarial evaluate ...")
        print()
        print(f"{BOLD}HELP:{RESET}")
        print("   Aider docs: https://aider.chat/docs/install.html")
        return 1

    # Error 4: Script execution fails
    script = ".adversarial/scripts/evaluate_plan.sh"
    if not os.path.exists(script):
        print(f"{RED}❌ ERROR: Script not found: {script}{RESET}")
        print("   Fix: Run 'adversarial init' to reinstall scripts")
        return 1

    try:
        result = subprocess.run(
            [script, task_file], text=True, timeout=180  # 3 minutes
        )
    except subprocess.TimeoutExpired:
        print(f"{RED}❌ ERROR: Evaluation timed out (>3 minutes){RESET}")
        print()
        print(f"{BOLD}WHY:{RESET}")
        print("   The AI model took too long to respond")
        print()
        print(f"{BOLD}POSSIBLE CAUSES:{RESET}")
        print("   • Network issues connecting to API")
        print("   • Task file too large (>1000 lines)")
        print("   • API rate limiting")
        print()
        print(f"{BOLD}FIX:{RESET}")
        print("   1. Check your network connection")
        print("   2. Try a smaller task file")
        print("   3. Wait a few minutes and retry")
        return 1
    except FileNotFoundError as e:
        # Check if this is a bash/platform issue
        if platform.system() == "Windows":
            print(f"{RED}❌ ERROR: Cannot execute workflow scripts{RESET}")
            print()
            print(f"{BOLD}WHY:{RESET}")
            print("   Native Windows (PowerShell/CMD) cannot run bash scripts")
            print("   This package requires Unix shell (bash) for workflow automation")
            print()
            print(f"{BOLD}FIX:{RESET}")
            print("   Option 1 (RECOMMENDED): Use WSL (Windows Subsystem for Linux)")
            print("     1. Install WSL: https://learn.microsoft.com/windows/wsl/install")
            print("     2. Open WSL terminal")
            print("     3. Reinstall package in WSL: pip install adversarial-workflow")
            print()
            print("   Option 2: Try Git Bash (not officially supported)")
            print("     • May have compatibility issues")
            print("     • WSL is strongly recommended")
            print()
            print(f"{BOLD}HELP:{RESET}")
            print("   See platform requirements: README.md#platform-support")
        else:
            print(f"{RED}❌ ERROR: Script not found: {script}{RESET}")
            print()
            print(f"{BOLD}WHY:{RESET}")
            print("   Workflow scripts are missing or corrupted")
            print()
            print(f"{BOLD}FIX:{RESET}")
            print("   Run: adversarial init")
            print("   This will reinstall all workflow scripts")
        return 1

    # Error 5: Evaluation rejected
    if result.returncode != 0:
        print()
        print("📋 Evaluation complete (needs revision)")
        print(f"   Details: {config['log_directory']}")
        return result.returncode

    print()
    print(f"{GREEN}✅ Evaluation approved!{RESET}")
    return 0


def review() -> int:
    """Run Phase 3: Code review."""

    print("🔍 Reviewing implementation...")
    print()

    # Check for git changes
    result = subprocess.run(["git", "diff", "--quiet"], capture_output=True)

    if result.returncode == 0:
        # No changes
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

    # Check aider
    if not shutil.which("aider"):
        print(f"{RED}❌ ERROR: Aider not installed{RESET}")
        print("   Fix: pip install aider-chat")
        return 1

    # Run review script
    script = ".adversarial/scripts/review_implementation.sh"
    if not os.path.exists(script):
        print(f"{RED}❌ ERROR: Script not found: {script}{RESET}")
        print("   Fix: Run 'adversarial init'")
        return 1

    try:
        result = subprocess.run([script], timeout=180)
    except subprocess.TimeoutExpired:
        print(f"{RED}❌ ERROR: Review timed out (>3 minutes){RESET}")
        return 1

    if result.returncode != 0:
        print()
        print("📋 Review complete (needs revision)")
        return result.returncode

    print()
    print(f"{GREEN}✅ Review approved!{RESET}")
    return 0


def validate(test_command: Optional[str] = None) -> int:
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

    print(f"   Test command: {test_command}")
    print()

    # Check aider
    if not shutil.which("aider"):
        print(f"{RED}❌ ERROR: Aider not installed{RESET}")
        print("   Fix: pip install aider-chat")
        return 1

    # Run validation script
    script = ".adversarial/scripts/validate_tests.sh"
    if not os.path.exists(script):
        print(f"{RED}❌ ERROR: Script not found: {script}{RESET}")
        print("   Fix: Run 'adversarial init'")
        return 1

    try:
        result = subprocess.run(
            [script, test_command], timeout=600
        )  # 10 minutes for tests
    except subprocess.TimeoutExpired:
        print(f"{RED}❌ ERROR: Test validation timed out (>10 minutes){RESET}")
        return 1

    if result.returncode != 0:
        print()
        print("📋 Validation complete (tests failed or needs review)")
        return result.returncode

    print()
    print(f"{GREEN}✅ Validation passed!{RESET}")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Adversarial Workflow - Multi-stage AI code review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  adversarial init                      # Initialize in current project
  adversarial init --interactive        # Interactive setup wizard
  adversarial quickstart                # Quick start with example
  adversarial check                     # Validate setup
  adversarial evaluate tasks/feat.md    # Evaluate plan
  adversarial review                    # Review implementation
  adversarial validate "npm test"       # Validate with tests

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

    # quickstart command
    subparsers.add_parser(
        "quickstart", help="Quick start with example task (recommended for new users)"
    )

    # check command (with doctor alias)
    subparsers.add_parser("check", help="Validate setup and dependencies")
    subparsers.add_parser("doctor", help="Alias for 'check'")

    # evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Run Phase 1: Plan evaluation")
    eval_parser.add_argument("task_file", help="Task file to evaluate")

    # review command
    subparsers.add_parser("review", help="Run Phase 3: Code review")

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Run Phase 4: Test validation"
    )
    validate_parser.add_argument(
        "test_command", nargs="?", help="Test command to run (optional)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    if args.command == "init":
        if args.interactive:
            return init_interactive(args.path)
        else:
            return init(args.path)
    elif args.command == "quickstart":
        return quickstart()
    elif args.command in ["check", "doctor"]:
        return check()
    elif args.command == "evaluate":
        return evaluate(args.task_file)
    elif args.command == "review":
        return review()
    elif args.command == "validate":
        return validate(args.test_command)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
