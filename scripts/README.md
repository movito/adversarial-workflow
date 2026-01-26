# Scripts Directory

Utility scripts for development and CI/CD operations.

## Available Scripts

### `verify-setup.sh`

Verifies project setup is complete and working:
- Python version check (3.9+)
- Virtual environment status
- Dependencies installed (pytest, pre-commit)
- Pre-commit hooks installed
- Tests directory exists

**Usage:**
```bash
./scripts/verify-setup.sh
```

### `verify-ci.sh`

Checks GitHub Actions CI status for a branch:
- Lists recent workflow runs
- Shows pass/fail status
- Provides commands to watch specific runs

**Usage:**
```bash
./scripts/verify-ci.sh [branch-name]
# Default: current branch
```

**Prerequisites:** GitHub CLI (`gh`) must be installed and authenticated.

## Adding New Scripts

1. Create script in this directory
2. Add shebang: `#!/bin/bash`
3. Make executable: `chmod +x scripts/your-script.sh`
4. Add documentation to this README
5. Test on fresh clone if possible

## Common Patterns

### Exit on Error
```bash
set -e  # Exit immediately if a command fails
```

### Check for Dependencies
```bash
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not installed"
    exit 1
fi
```

### Color Output
```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'  # No Color
echo -e "${GREEN}✅ Success${NC}"
```
