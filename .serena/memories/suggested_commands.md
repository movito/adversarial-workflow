# Suggested Commands for Development

## Virtual Environment
```bash
# Activate virtual environment (Python 3.11 required for aider)
source .venv/bin/activate
```

## Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_cli.py -v

# Run specific test
pytest tests/test_cli.py::TestCLISmoke::test_version_flag -v

# Run tests with coverage
pytest tests/ -v --cov=adversarial_workflow --cov-report=term-missing

# Run tests excluding slow ones
pytest tests/ -v -m "not slow"

# Run tests with max failures
pytest tests/ -v --maxfail=3
```

## Code Formatting
```bash
# Format with black
black adversarial_workflow/ tests/ --line-length=88

# Sort imports
isort adversarial_workflow/ tests/ --profile=black --line-length=88

# Lint with flake8
flake8 adversarial_workflow/ tests/ --max-line-length=88
```

## Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run all hooks
pre-commit run --all-files

# Skip tests during commit
SKIP_TESTS=1 git commit -m "WIP"
```

## Git Commands
```bash
# Standard git operations
git status
git diff
git add -A
git commit -m "message"
git push
```

## CLI Testing (after installation)
```bash
# Installed command
adversarial --version
adversarial --help
adversarial check
adversarial health

# Run evaluation
adversarial evaluate path/to/task.md

# Review implementation
adversarial review

# Validate tests
adversarial validate "pytest tests/"
```

## Building/Installing
```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Build distribution
python -m build
```

## System Commands (macOS/Darwin)
```bash
# List files
ls -la

# Find files
find . -name "*.py" -type f

# Search in files
grep -r "pattern" adversarial_workflow/

# View file
cat filename
```
