# Adversarial Workflow - Project Overview

## Purpose
A multi-stage AI code review system that prevents "phantom work" (AI claiming to implement but not delivering) through adversarial verification using independent review stages.

## Current Version
v0.5.0 (as of pyproject.toml)

## Core Workflow (The Adversarial Pattern)
1. **Phase 1: Plan Evaluation** - AI evaluates implementation plan before coding
2. **Phase 2: Implementation** - Author implements (using any method)
3. **Phase 3: Code Review** - AI reviews git diff against plan
4. **Phase 4: Test Validation** - AI analyzes test results
5. **Phase 5: Final Approval** - Author reviews artifacts and commits

## Tech Stack
- **Language**: Python 3.10+ (3.12 recommended)
- **CLI Entry Point**: `adversarial` command
- **Core Dependency**: `aider-chat` (bundled) - GPT-4o via aider for evaluation
- **Config Format**: YAML (`.adversarial/config.yml`)
- **Package Manager**: pip, setuptools

## Key Dependencies
- `pyyaml>=6.0`
- `python-dotenv>=0.19.0`
- `aider-chat>=0.86.0`

## Project Structure
```
adversarial_workflow/
├── __init__.py          # Package version
├── cli.py               # Main CLI (2800+ lines - refactor target)
├── __main__.py          # Entry point
├── utils/               # Utility modules
└── templates/           # Template files

tests/
├── conftest.py          # Shared fixtures
├── test_cli.py          # CLI tests
├── test_config.py       # Config tests
├── test_evaluate.py     # Evaluation tests
└── fixtures/            # Test fixtures

.adversarial/            # Workflow files (in user projects)
├── scripts/             # Bash scripts
├── config.yml           # Configuration
└── logs/                # Evaluation logs
```

## CLI Commands
- `adversarial init` - Initialize in project
- `adversarial quickstart` - Quick start with wizard
- `adversarial evaluate task.md` - Phase 1: Evaluate plan
- `adversarial review` - Phase 3: Review implementation
- `adversarial validate "pytest"` - Phase 4: Validate tests
- `adversarial check` - Validate setup
- `adversarial health` - Comprehensive health check
- `adversarial split` - Split large files
- `adversarial agent onboard` - Set up agent coordination

## Refactoring Priorities
The main `cli.py` is a monolith (~2800 lines). Target extractions:
1. `config.py` - Configuration loading
2. `evaluate.py` - Evaluation logic
3. `utils.py` - Utility functions
4. `commands/` - Individual command implementations
