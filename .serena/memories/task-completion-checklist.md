# Task Completion Checklist

Run these steps after completing any task:

## 1. Code Quality Checks
```bash
# Activate virtual environment
source .venv/bin/activate

# Format code
black adversarial_workflow/ tests/ --line-length=88

# Sort imports
isort adversarial_workflow/ tests/ --profile=black --line-length=88

# Lint
flake8 adversarial_workflow/ tests/ --max-line-length=88 --extend-ignore=E203,W503
```

## 2. Run Tests
```bash
# Run all tests (required before commit)
pytest tests/ -v

# With coverage (optional)
pytest tests/ -v --cov=adversarial_workflow --cov-report=term-missing
```

## 3. Pre-commit Hooks
```bash
# Run all pre-commit hooks
pre-commit run --all-files
```

## 4. Git Commit
```bash
# Stage changes
git add -A

# Commit (pre-commit will run automatically)
git commit -m "feat/fix/chore: descriptive message"
```

## Commit Message Format
- `feat:` - New feature
- `fix:` - Bug fix
- `chore:` - Maintenance tasks
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes

## TDD Workflow (For Feature Development)
1. **Write failing test first**
2. Run test to verify it fails
3. Implement feature
4. Run test to verify it passes
5. Run all tests
6. Refactor if needed
7. Commit

## Skip Tests (Use Sparingly)
```bash
# For WIP commits only
SKIP_TESTS=1 git commit -m "WIP: work in progress"
```
