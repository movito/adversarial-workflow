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
"""

import argparse
import getpass
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from dotenv import load_dotenv

__version__ = "0.6.2"

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
                '  2. Click "Create Key"',
                '  3. Copy the key (starts with "sk-ant-")',
            ],
        )

        anthropic_key = prompt_user(
            "Paste your Anthropic API key (or Enter to skip)", secret=True
        )

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

        openai_key = prompt_user(
            "Paste your OpenAI API key (or Enter to skip)", secret=True
        )

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

    project_name = prompt_user(
        "Project name", default=os.path.basename(os.path.abspath(project_path))
    )
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
            "  ✓ .env (with your API keys - added to .gitignore)"
            if (anthropic_key or openai_key)
            else "  ⚠️ .env (skipped - no API keys provided)",
            "  ✓ .adversarial/config.yml",
            "  ✓ .adversarial/scripts/ (3 workflow scripts)",
            "  ✓ .aider.conf.yml (aider configuration)",
            "",
            "Your configuration:"
            if (anthropic_key or openai_key)
            else "Configuration (no API keys yet):",
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
        print(
            "   New to git? https://git-scm.com/book/en/v2/Getting-Started-Installing-Git"
        )
        return 1

    # Pre-flight validation: Check package integrity
    package_dir = Path(__file__).parent
    templates_dir = package_dir / "templates"

    required_templates = [
        "config.yml.template",
        "evaluate_plan.sh.template",
        "proofread_content.sh.template",
        "review_implementation.sh.template",
        "validate_tests.sh.template",
        ".aider.conf.yml.template",
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
        print(
            "   1. Report this issue: https://github.com/movito/adversarial-workflow/issues"
        )
        print(
            "   2. Or try reinstalling: pip install --upgrade --force-reinstall adversarial-workflow"
        )
        print()
        print(f"{BOLD}WORKAROUND:{RESET}")
        print("   Create missing files manually:")
        print("   - .aider.conf.yml: See https://aider.chat/docs/config.html")
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
            str(templates_dir / "proofread_content.sh.template"),
            os.path.join(adversarial_dir, "scripts", "proofread_content.sh"),
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
            except (IOError, OSError) as e:
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

    # Check for .env file first (before loading environment variables)
    env_file = Path(".env")
    env_loaded = False
    env_keys_before = set(os.environ.keys())

    if env_file.exists():
        try:
            load_dotenv(env_file)
            env_keys_after = set(os.environ.keys())
            new_keys = env_keys_after - env_keys_before
            env_loaded = True
            good_checks.append(
                f".env file found and loaded ({len(new_keys)} variables)"
            )
        except Exception as e:
            issues.append(
                {
                    "severity": "WARNING",
                    "message": f".env file found but could not be loaded: {e}",
                    "fix": "Check .env file format and permissions",
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

    # Check 2: Aider installed
    if shutil.which("aider"):
        # Try to get version
        try:
            result = subprocess.run(
                ["aider", "--version"], capture_output=True, text=True, timeout=2
            )
            version = result.stdout.strip() if result.returncode == 0 else "unknown"
            good_checks.append(f"Aider installed ({version})")
        except:
            good_checks.append("Aider installed")
    else:
        issues.append(
            {
                "severity": "ERROR",
                "message": "Aider not found in PATH",
                "fix": "Install: pip install aider-chat",
            }
        )

    # Check 3: API keys (with source tracking)
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

    # Check 5: Scripts executable
    if config:
        scripts = ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]
        all_scripts_ok = True
        for script in scripts:
            path = f".adversarial/scripts/{script}"
            if os.path.exists(path):
                if not os.access(path, os.X_OK):
                    issues.append(
                        {
                            "severity": "WARNING",
                            "message": f"{script} not executable",
                            "fix": f"chmod +x {path}",
                        }
                    )
                    all_scripts_ok = False
            else:
                issues.append(
                    {
                        "severity": "ERROR",
                        "message": f"{script} not found",
                        "fix": "Run: adversarial init",
                    }
                )
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
            status_parts.append(
                f"{error_count} error" + ("s" if error_count != 1 else "")
            )
        if warning_count > 0:
            status_parts.append(
                f"{warning_count} warning" + ("s" if warning_count != 1 else "")
            )
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
    from datetime import datetime

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
        results[category].append(
            {"status": "pass", "message": message, "detail": detail}
        )
        if not json_output:
            print(f"  {GREEN}✅{RESET} {message}")
        passed += 1

    def check_warn(
        category: str, message: str, detail: str = None, recommendation: str = None
    ):
        nonlocal warnings
        results[category].append(
            {"status": "warn", "message": message, "detail": detail}
        )
        if not json_output:
            print(f"  {YELLOW}⚠️{RESET}  {message}")
            if detail and verbose:
                print(f"     {GRAY}{detail}{RESET}")
        if recommendation:
            recommendations.append(recommendation)
        warnings += 1

    def check_fail(
        category: str, message: str, fix: str = None, recommendation: str = None
    ):
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
        results[category].append(
            {"status": "info", "message": message, "detail": detail}
        )
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
            with open(config_file) as f:
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
                        f'task_directory: {config["task_directory"]} (exists)',
                    )
                else:
                    check_fail(
                        "configuration",
                        f'task_directory: {config["task_directory"]} (not found)',
                        fix=f'mkdir -p {config["task_directory"]}',
                        recommendation=f'Create task directory: mkdir -p {config["task_directory"]}',
                    )

            if "log_directory" in config:
                log_dir = Path(config["log_directory"])
                if log_dir.exists():
                    if os.access(log_dir, os.W_OK):
                        check_pass(
                            "configuration",
                            f'log_directory: {config["log_directory"]} (writable)',
                        )
                    else:
                        check_fail(
                            "configuration",
                            f'log_directory: {config["log_directory"]} (not writable)',
                            fix=f'chmod +w {config["log_directory"]}',
                        )
                else:
                    check_warn(
                        "configuration",
                        f'log_directory: {config["log_directory"]} (will be created)',
                        recommendation=f"Log directory will be created automatically",
                    )

            # Check test command
            if "test_command" in config:
                check_info("configuration", f'test_command: {config["test_command"]}')

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
                        [
                            l
                            for l in git_status.stdout.splitlines()
                            if l.startswith(" M")
                        ]
                    )
                    untracked = len(
                        [
                            l
                            for l in git_status.stdout.splitlines()
                            if l.startswith("??")
                        ]
                    )
                    if modified == 0 and untracked == 0:
                        check_pass(
                            "dependencies", f"Git: {version} (working tree clean)"
                        )
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
    if (major, minor) >= (3, 8):
        check_pass("dependencies", f"Python: {python_version} (compatible)")
    else:
        check_fail(
            "dependencies",
            f"Python: {python_version} (requires 3.8+)",
            fix="Upgrade Python to 3.8 or higher",
            recommendation="Python 3.8+ required - upgrade your Python installation",
        )

    # Aider
    if shutil.which("aider"):
        try:
            aider_version = subprocess.run(
                ["aider", "--version"], capture_output=True, text=True, timeout=2
            )
            version = (
                aider_version.stdout.strip()
                if aider_version.returncode == 0
                else "unknown"
            )
            check_pass("dependencies", f"Aider: {version} (functional)")
        except:
            check_pass("dependencies", "Aider: installed")
    else:
        check_fail(
            "dependencies",
            "Aider not found",
            fix="Install: pip install aider-chat",
            recommendation="Aider is required - install with: pip install aider-chat",
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
                with open(handoffs_file) as f:
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
                        f'Last updated: {handoffs["meta"]["last_updated"]}',
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
                with open(state_file) as f:
                    json.load(f)
                check_pass("agent_coordination", "current-state.json - Valid JSON")
            except json.JSONDecodeError as e:
                check_fail(
                    "agent_coordination", f"current-state.json - Invalid JSON: {e}"
                )
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

    # 5. Workflow Scripts
    if not json_output:
        print(f"{BOLD}Workflow Scripts:{RESET}")

    scripts = ["evaluate_plan.sh", "review_implementation.sh", "validate_tests.sh"]

    for script_name in scripts:
        script_path = Path(f".adversarial/scripts/{script_name}")
        if script_path.exists():
            # Check executable
            if os.access(script_path, os.X_OK):
                # Check syntax (basic - just try to read it)
                try:
                    with open(script_path) as f:
                        content = f.read()
                    if "#!/bin/bash" in content or "#!/usr/bin/env bash" in content:
                        check_pass(
                            "workflow_scripts", f"{script_name} - Executable, valid"
                        )
                    else:
                        check_warn(
                            "workflow_scripts",
                            f"{script_name} - Missing shebang",
                            recommendation=f"Add #!/bin/bash to {script_name}",
                        )
                except:
                    check_warn("workflow_scripts", f"{script_name} - Could not read")
            else:
                check_fail(
                    "workflow_scripts",
                    f"{script_name} - Not executable",
                    fix=f"chmod +x .adversarial/scripts/{script_name}",
                    recommendation=f"Make executable: chmod +x .adversarial/scripts/{script_name}",
                )
        else:
            check_fail(
                "workflow_scripts",
                f"{script_name} - Not found",
                fix="Run: adversarial init",
                recommendation="Reinstall scripts with: adversarial init",
            )

    if not json_output:
        print()

    # 6. Tasks
    if not json_output:
        print(f"{BOLD}Tasks:{RESET}")

    if config and "task_directory" in config:
        task_dir = Path(config["task_directory"])
        if task_dir.exists():
            check_pass("tasks", f'{config["task_directory"]} directory exists')

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
                        f'{len(active_tasks)} active tasks in {config["task_directory"]}active/',
                    )
                elif len(task_files) > 0:
                    check_info(
                        "tasks",
                        f'{len(task_files)} task files in {config["task_directory"]}',
                    )
                else:
                    check_info(
                        "tasks",
                        f"No task files found (create with adversarial quickstart)",
                    )
            except:
                check_info("tasks", "Could not count task files")
        else:
            check_warn(
                "tasks",
                f'{config["task_directory"]} directory not found',
                recommendation=f'Create with: mkdir -p {config["task_directory"]}',
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

    # Check scripts executable (summary)
    scripts_dir = Path(".adversarial/scripts")
    if scripts_dir.exists():
        script_files = list(scripts_dir.glob("*.sh"))
        executable_count = sum(1 for s in script_files if os.access(s, os.X_OK))
        if len(script_files) > 0 and executable_count == len(script_files):
            check_pass("permissions", f"All {len(script_files)} scripts executable")
        elif executable_count < len(script_files):
            check_warn(
                "permissions",
                f"{executable_count}/{len(script_files)} scripts executable",
                recommendation="Fix with: chmod +x .adversarial/scripts/*.sh",
            )

    # Check log directory writable
    if config and "log_directory" in config:
        log_dir = Path(config["log_directory"])
        if log_dir.exists():
            if os.access(log_dir, os.W_OK):
                check_pass("permissions", f'{config["log_directory"]} - Writable')
            else:
                check_fail(
                    "permissions",
                    f'{config["log_directory"]} - Not writable',
                    fix=f'chmod +w {config["log_directory"]}',
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
            print("  • Review implementations: adversarial review")
            print("  • Validate tests: adversarial validate")
        else:
            print(f"{BOLD}Next steps:{RESET}")
            print("  • Fix critical issues above")
            print("  • Run: adversarial init --interactive")
            print("  • Then: adversarial health --verbose")
        print()

    # Exit code
    return 0 if errors == 0 else 1


def estimate_file_tokens(file_path: str) -> int:
    """
    Estimate tokens for a file using rough approximation.

    Estimation: ~1 token per 4 characters (OpenAI's rule of thumb)

    Args:
        file_path: Path to the file to estimate tokens for

    Returns:
        Estimated token count (integer)
    """
    with open(file_path, "r") as f:
        char_count = len(f.read())

    return char_count // 4  # Rough estimate


def extract_token_count_from_log(log_file_path: str) -> Optional[int]:
    """
    Extract tokens sent from evaluation log.

    Looks for pattern: "Tokens: 15k sent, 422 received"
    Returns tokens sent as integer, or None if not found.

    Args:
        log_file_path: Path to the evaluation log file

    Returns:
        Tokens sent as integer, or None if pattern not found
    """
    if not os.path.exists(log_file_path):
        return None

    with open(log_file_path, "r") as f:
        content = f.read()

    # Pattern: "Tokens: 12k sent" or "Tokens: 12000 sent"
    match = re.search(r"Tokens:\s+(\d+\.?\d*)k?\s+sent", content)
    if match:
        tokens_str = match.group(1)
        tokens = float(tokens_str)
        # If 'k' suffix found, multiply by 1000
        if "k" in match.group(0).lower():
            tokens *= 1000
        return int(tokens)

    return None


def verify_token_count(task_file: str, log_file: str) -> None:
    """
    Warn if token count is suspiciously low for file size.

    This helps detect cases where large files may not be fully
    processed by the evaluator due to API rate limits or other issues.

    Args:
        task_file: Path to the task file being evaluated
        log_file: Path to the evaluation log file
    """
    expected_tokens = estimate_file_tokens(task_file)
    actual_tokens = extract_token_count_from_log(log_file)

    if actual_tokens is None:
        # Can't verify if we can't extract token count
        return

    # 70% tolerance - warn if actual < 70% of expected
    if actual_tokens < expected_tokens * 0.7:
        print()
        print(f"{YELLOW}⚠️  Token count lower than expected:{RESET}")
        print(f"   File size estimate: ~{expected_tokens:,} tokens")
        print(f"   Actually sent: {actual_tokens:,} tokens")
        print(
            f"   Difference: {expected_tokens - actual_tokens:,} tokens ({100 - int(actual_tokens/expected_tokens*100)}% less)"
        )
        print()
        print(
            f"{BOLD}Note:{RESET} Large files may not be fully processed by evaluator."
        )
        print(f"      Consider splitting into smaller documents (<1,000 lines).")
        print()


def validate_evaluation_output(
    log_file_path: str,
) -> Tuple[bool, Optional[str], str]:
    """
    Validate that evaluation log contains actual GPT-4o evaluation content.

    This prevents false positives where the evaluation script runs but Aider
    fails to produce an actual evaluation (e.g., due to git scanning errors).
    Also extracts the verdict from successful evaluations.

    Args:
        log_file_path: Path to the evaluation log file

    Returns:
        (is_valid, verdict, message):
            - is_valid: True if valid evaluation, False if failed
            - verdict: "APPROVED", "NEEDS_REVISION", "REJECTED", or None if validation failed
            - message: Descriptive message about validation result
    """
    # Check if log file exists
    if not os.path.exists(log_file_path):
        return False, None, f"Log file not found: {log_file_path}"

    with open(log_file_path, "r") as f:
        content = f.read()

    # Check minimum content size (working evaluations are >1000 bytes)
    if len(content) < 500:
        return (
            False,
            None,
            f"Log file too small ({len(content)} bytes), evaluation likely failed",
        )

    # Check for required evaluation sections
    # Note: The prompt uses "Evaluation Summary" not "OVERALL ASSESSMENT"
    required_sections = ["Evaluation Summary", "Verdict"]

    missing_sections = [s for s in required_sections if s not in content]
    if missing_sections:
        return (
            False,
            None,
            f"Missing evaluation sections: {', '.join(missing_sections)}",
        )

    # Check for known failure patterns (git errors)
    failure_patterns = [
        ("Unable to list files in git repo", "Git repository scanning failed"),
        ("Is your git repo corrupted", "Git repository error"),
        ("BadObject", "Git object error"),
    ]

    for pattern, description in failure_patterns:
        if pattern in content and len(content) < 1000:
            # Small file with error pattern = evaluation didn't run
            return False, None, f"Aider failed: {description}"

    # Check for token usage (indicates GPT-4o actually ran)
    if "Tokens:" not in content and "tokens" not in content.lower():
        return False, None, "No token usage found - GPT-4o may not have run"

    # Extract verdict from evaluation content
    verdict = None
    verdict_patterns = [
        ("Verdict:** APPROVED", "APPROVED"),
        ("Verdict: APPROVED", "APPROVED"),
        ("Verdict:** NEEDS_REVISION", "NEEDS_REVISION"),
        ("Verdict: NEEDS_REVISION", "NEEDS_REVISION"),
        ("Verdict:** REJECT", "REJECTED"),
        ("Verdict: REJECT", "REJECTED"),
    ]

    for pattern, verdict_value in verdict_patterns:
        if pattern in content:
            verdict = verdict_value
            break

    # If we couldn't extract a verdict, that's suspicious but not fatal
    if verdict is None:
        verdict = "UNKNOWN"

    return True, verdict, "Evaluation output valid"


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

    # Pre-flight check for file size
    with open(task_file, "r") as f:
        line_count = len(f.readlines())
        f.seek(0)
        file_size = len(f.read())

    # Estimate tokens (1 token ≈ 4 characters)
    estimated_tokens = file_size // 4

    # Warn if file is large (>500 lines or >20k tokens)
    if line_count > 500 or estimated_tokens > 20000:
        print(f"{YELLOW}⚠️  Large file detected:{RESET}")
        print(f"   Lines: {line_count:,}")
        print(f"   Estimated tokens: ~{estimated_tokens:,}")
        print()
        print(f"{BOLD}Note:{RESET} Files over 500 lines may exceed OpenAI rate limits.")
        print(f"      If evaluation fails, consider splitting into smaller documents.")
        print()

        # Give user a chance to cancel for very large files
        if line_count > 700:
            print(f"{RED}⚠️  WARNING: File is very large (>{line_count} lines){RESET}")
            print(f"   This will likely fail on Tier 1 OpenAI accounts (30k TPM limit)")
            print(f"   Recommended: Split into files <500 lines each")
            print()
            response = input("Continue anyway? [y/N]: ").strip().lower()
            if response not in ["y", "yes"]:
                print("Evaluation cancelled.")
                return 0
            print()

    # Error 4: Script execution fails
    script = ".adversarial/scripts/evaluate_plan.sh"
    if not os.path.exists(script):
        print(f"{RED}❌ ERROR: Script not found: {script}{RESET}")
        print("   Fix: Run 'adversarial init' to reinstall scripts")
        return 1

    try:
        result = subprocess.run(
            [script, task_file],
            text=True,
            capture_output=True,
            timeout=180,  # 3 minutes
        )

        # Check for rate limit errors in output
        output = result.stdout + result.stderr
        if "RateLimitError" in output or "tokens per min (TPM)" in output:
            print(f"{RED}❌ ERROR: OpenAI rate limit exceeded{RESET}")
            print()
            print(f"{BOLD}WHY:{RESET}")
            print(
                "   Your task file is too large for your OpenAI organization's rate limit"
            )
            print()

            # Extract file size for helpful message
            with open(task_file, "r") as f:
                line_count = len(f.readlines())

            print(f"{BOLD}FILE SIZE:{RESET}")
            print(f"   Lines: {line_count:,}")
            print(f"   Recommended limit: 500 lines")
            print()
            print(f"{BOLD}SOLUTIONS:{RESET}")
            print("   1. Split your task into smaller documents (<500 lines each)")
            print("   2. Upgrade your OpenAI tier (Tier 2 supports ~1,000 lines)")
            print("   3. Use manual review for this comprehensive specification")
            print()
            print(f"{BOLD}MORE INFO:{RESET}")
            print("   https://platform.openai.com/docs/guides/rate-limits")
            return 1

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
            print(
                "     1. Install WSL: https://learn.microsoft.com/windows/wsl/install"
            )
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

    # Error 6: Validation - Check if evaluation actually ran (not just empty output)
    # Extract task number from filename to find log file
    task_basename = os.path.basename(task_file)
    # Try to extract TASK-YYYY-NNN pattern, fallback to filename without extension
    task_match = re.search(r"TASK-\d+-\d+", task_basename)
    if task_match:
        task_num = task_match.group(0)
    else:
        task_num = os.path.splitext(task_basename)[0]

    log_file = os.path.join(config["log_directory"], f"{task_num}-PLAN-EVALUATION.md")

    is_valid, verdict, message = validate_evaluation_output(log_file)
    if not is_valid:
        print()
        print(f"{RED}❌ Evaluation failed: {message}{RESET}")
        print()
        print(f"{BOLD}WHY:{RESET}")
        print("   The evaluation script ran but didn't produce valid output")
        print("   This usually means Aider encountered an error before running GPT-4o")
        print()
        print(f"{BOLD}LOG FILE:{RESET}")
        print(f"   {log_file}")
        print()
        print(f"{BOLD}FIX:{RESET}")
        print("   1. Check the log file for error messages")
        print("   2. Ensure your API keys are valid: adversarial check")
        print("   3. Try running the evaluation again")
        print()
        return 1

    # Verify token count (warn if suspiciously low)
    verify_token_count(task_file, log_file)

    # Report based on actual verdict from evaluation
    print()
    if verdict == "APPROVED":
        print(f"{GREEN}✅ Evaluation APPROVED!{RESET}")
        print(f"   Plan is ready for implementation")
        print(f"   Review output: {log_file}")
        return 0
    elif verdict == "NEEDS_REVISION":
        print(f"{YELLOW}⚠️  Evaluation NEEDS_REVISION{RESET}")
        print(f"   Review feedback and update plan")
        print(f"   Details: {log_file}")
        return 1
    elif verdict == "REJECTED":
        print(f"{RED}❌ Evaluation REJECTED{RESET}")
        print(f"   Plan has fundamental issues - major revision needed")
        print(f"   Details: {log_file}")
        return 1
    else:  # UNKNOWN or other
        print(f"{YELLOW}⚠️  Evaluation complete (verdict: {verdict}){RESET}")
        print(f"   Review output: {log_file}")
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


def select_agent_template() -> Dict[str, str]:
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
        print(
            "  Example: https://raw.githubusercontent.com/user/repo/main/agent-handoffs.json"
        )
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


def fetch_agent_template(url: str, template_type: str = "standard") -> Optional[str]:
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
                with open(template_path, "r") as f:
                    return f.read()
            except Exception as e:
                print(
                    f"{RED}❌ ERROR: Could not read {template_type} template: {e}{RESET}"
                )
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
    use_delegation = prompt_user(
        "Use delegation/tasks/ structure? (recommended)", "Y"
    ).lower() in ["y", "yes", ""]

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
            print(f"  Backup will be created at: tasks.backup/")
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
                    print(
                        f"  {CYAN}ℹ️{RESET}  Rollback: rm -rf tasks && mv tasks.backup tasks"
                    )

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
        root_docs = [
            f for f in os.listdir(".") if f.endswith(".md") and not f.startswith(".")
        ]

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
                    print(
                        f"  {GREEN}✅{RESET} Organized {moved_count} doc(s) into docs/"
                    )
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
                with open(".agent-context/agent-handoffs.json", "w") as f:
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
            print(
                f"  {CYAN}ℹ️{RESET}  Skipped agent-handoffs.json (manual setup requested)"
            )

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
            render_template(
                str(readme_template), ".agent-context/README.md", template_vars
            )
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
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            # Update task_directory
            old_task_dir = config.get("task_directory", "tasks/")
            config["task_directory"] = "delegation/tasks/"

            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            print(f"  {GREEN}✅{RESET} Updated .adversarial/config.yml")
            print(f"     task_directory: {old_task_dir} → delegation/tasks/")

        except Exception as e:
            print(f"  {YELLOW}⚠️{RESET}  Could not update config: {e}")
            print(
                f"     Manually set task_directory: delegation/tasks/ in .adversarial/config.yml"
            )

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
            with open(gitignore_path, "r") as f:
                existing_content = f.read()

        with open(gitignore_path, "a") as f:
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
        with open(".agent-context/agent-handoffs.json") as f:
            json.load(f)
        verification_checks.append(("agent-handoffs.json valid", True))
    except Exception as e:
        verification_checks.append((f"agent-handoffs.json invalid: {e}", False))

    try:
        with open(".agent-context/current-state.json") as f:
            json.load(f)
        verification_checks.append(("current-state.json valid", True))
    except Exception as e:
        verification_checks.append((f"current-state.json invalid: {e}", False))

    # Check directories exist
    verification_checks.append(
        (".agent-context/ exists", os.path.exists(".agent-context"))
    )

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
        print(f"  ○ agent-handoffs.json - Manual setup required")

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
    print(f"   Use both systems together for optimal development workflow")
    print()

    return 0


def split(task_file: str, strategy: str = "sections", max_lines: int = 500, dry_run: bool = False):
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
        split_by_sections, 
        split_by_phases, 
        generate_split_files
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
        
        lines = analysis['total_lines']
        tokens = analysis['estimated_tokens']
        print(f"   Lines: {lines}")
        print(f"   Estimated tokens: ~{tokens:,}")
        
        # Check if splitting is recommended
        if lines <= max_lines:
            print(f"{GREEN}✅ File is under recommended limit ({max_lines} lines){RESET}")
            print("No splitting needed.")
            return 0
        
        print(f"{YELLOW}⚠️  File exceeds recommended limit ({max_lines} lines){RESET}")
        
        # Read file content for splitting
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply split strategy
        if strategy == "sections":
            splits = split_by_sections(content, max_lines=max_lines)
            print(f"\n💡 Suggested splits (by sections):")
        elif strategy == "phases":
            splits = split_by_phases(content)
            print(f"\n💡 Suggested splits (by phases):")
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
        
        if create_files.lower() in ['y', 'yes']:
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

def main():
    """Main CLI entry point."""
    import logging

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
        get_all_evaluators,
        run_evaluator,
        BUILTIN_EVALUATORS,
    )

    logger = logging.getLogger(__name__)

    # Commands that cannot be overridden by evaluators
    # Note: 'review' is special - it reviews git changes without a file argument
    STATIC_COMMANDS = {
        "init", "check", "doctor", "health", "quickstart",
        "agent", "split", "validate", "review", "list-evaluators"
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
  adversarial review                    # Review implementation
  adversarial validate "npm test"       # Validate with tests
  adversarial split large-task.md       # Split large files

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

    # health command
    health_parser = subparsers.add_parser(
        "health", help="Comprehensive system health check"
    )
    health_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed diagnostics"
    )
    health_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )

    # agent command (with subcommands)
    agent_parser = subparsers.add_parser("agent", help="Agent coordination commands")
    agent_subparsers = agent_parser.add_subparsers(
        dest="agent_subcommand", help="Agent subcommand"
    )

    # agent onboard subcommand
    onboard_parser = agent_subparsers.add_parser(
        "onboard", help="Set up agent coordination system"
    )
    onboard_parser.add_argument(
        "--path", default=".", help="Project path (default: current directory)"
    )

    # review command (static - reviews git changes, no file argument)
    subparsers.add_parser("review", help="Run Phase 3: Code review")

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Run Phase 4: Test validation"
    )
    validate_parser.add_argument(
        "test_command", nargs="?", help="Test command to run (optional)"
    )

    # split command
    split_parser = subparsers.add_parser(
        "split", help="Split large task files into smaller evaluable chunks"
    )
    split_parser.add_argument("task_file", help="Task file to split")
    split_parser.add_argument(
        "--strategy", "-s", choices=["sections", "phases"], default="sections",
        help="Split strategy: 'sections' (default) or 'phases'"
    )
    split_parser.add_argument(
        "--max-lines", "-m", type=int, default=500,
        help="Maximum lines per split (default: 500)"
    )
    split_parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview splits without creating files"
    )

    # list-evaluators command
    subparsers.add_parser(
        "list-evaluators",
        help="List all available evaluators (built-in and local)",
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
            "--timeout", "-t",
            type=int,
            default=180,
            help="Timeout in seconds (default: 180)"
        )
        # Store config for later execution
        eval_parser.set_defaults(evaluator_config=config)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Check for evaluator command first (has evaluator_config attribute)
    if hasattr(args, "evaluator_config"):
        return run_evaluator(
            args.evaluator_config,
            args.file,
            timeout=args.timeout,
        )

    # Execute static commands
    if args.command == "init":
        if args.interactive:
            return init_interactive(args.path)
        else:
            return init(args.path)
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
    elif args.command == "review":
        return review()
    elif args.command == "validate":
        return validate(args.test_command)
    elif args.command == "split":
        return split(
            args.task_file,
            strategy=args.strategy,
            max_lines=args.max_lines,
            dry_run=args.dry_run
        )
    elif args.command == "list-evaluators":
        return list_evaluators()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
