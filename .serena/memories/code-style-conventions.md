# Code Style and Conventions

## Formatting
- **Line length**: 88 characters (black default)
- **Formatter**: Black
- **Import sorter**: isort (profile=black)
- **Linter**: flake8

## Python Version
- Minimum: Python 3.10
- Recommended: Python 3.12
- Target versions: py310, py311, py312

## Type Hints
- Use type hints for function signatures
- Example from codebase:
```python
def load_config(config_path: str = ".adversarial/config.yml") -> Dict:
    """Load configuration from YAML file with environment variable overrides."""
```

## Docstrings
- Use triple-quoted docstrings
- Brief one-line summary for simple functions
- Multi-line docstrings for complex functions with:
  - Summary line
  - Args section (if needed)
  - Returns section (if needed)

## Naming Conventions
- Functions: `snake_case` (e.g., `load_config`, `validate_api_key`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `RESET`, `BOLD`, `GREEN`)
- Classes: `PascalCase` (e.g., `TestCLISmoke`)
- Test functions: `test_` prefix (e.g., `test_version_flag`)

## Testing Patterns
- Framework: pytest
- Test class prefix: `Test` (e.g., `TestCLISmoke`)
- Test function prefix: `test_` (e.g., `test_version_flag`)
- Use fixtures from `conftest.py`
- Mock external services (subprocess, APIs)

## Test Fixtures (from conftest.py)
- `tmp_project` - Temporary project directory
- `sample_task_content` - Sample task file content
- `sample_task_file` - Sample task file
- `mock_subprocess` - Mock subprocess.run
- `mock_openai_api` - Mock OpenAI API
- `sample_config` - Sample configuration dict
- `change_test_dir` (autouse) - Changes to temp dir

## File Organization
- Main code in `adversarial_workflow/`
- Tests in `tests/`
- One test file per module (e.g., `test_cli.py` for `cli.py`)
- Shared fixtures in `conftest.py`

## CLI Patterns
- CLI functions are decorated/called from `main()`
- Use `argparse` for CLI parsing
- Return appropriate exit codes
- Print colored output using ANSI constants
