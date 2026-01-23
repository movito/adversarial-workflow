# Issue Report: Environment Variable Loading in adversarial-workflow

**From**: ombruk-idrettsbygg project
**To**: adversarial-workflow maintainers
**Date**: 2026-01-23
**Version**: adversarial-workflow 0.6.0

---

## Summary

When using custom evaluators with non-OpenAI models (e.g., Gemini), the `api_key_env` configuration requires the environment variable to be explicitly exported. The tool does not automatically load `.env` files.

## Issue Encountered

### Setup

We created a custom evaluator using the v0.6.0 plugin architecture:

```yaml
# .adversarial/evaluators/athena.yml
name: athena
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
# ...
```

Our `.env` file contains:

```bash
GEMINI_API_KEY=AIzaSy...
```

### Expected Behavior

```bash
adversarial athena task.md
# Should work if GEMINI_API_KEY is in .env
```

### Actual Behavior

```bash
adversarial athena task.md
# Error: GEMINI_API_KEY not set
#    Set in .env or export GEMINI_API_KEY=your-key
```

The error message mentions `.env` but the tool doesn't actually load it.

### Workaround

We must explicitly export the variable:

```bash
export $(grep GEMINI_API_KEY .env | xargs) && adversarial athena task.md
# Works
```

Or:

```bash
source <(grep -v '^#' .env | sed 's/^/export /') && adversarial athena task.md
# Works
```

## Analysis

### Current Behavior

The tool checks `os.environ.get(api_key_env)` but doesn't load `.env` files. This is inconsistent with:

1. The error message which suggests using `.env`
2. The legacy shell scripts which do load `.env`:
   ```bash
   # From evaluate_knowledge.sh (legacy)
   if [ -f .env ]; then
     export $(grep -v '^#' .env | xargs)
   fi
   ```
3. Common Python CLI patterns (click + python-dotenv)

### Impact

- Users who configure API keys in `.env` (standard practice) get confusing errors
- The error message is misleading—it suggests `.env` works when it doesn't
- Workaround requires shell scripting knowledge

## Suggested Fix

### Option A: Auto-load .env (Recommended)

Add python-dotenv integration at CLI startup:

```python
# In cli.py or __init__.py
from dotenv import load_dotenv

def main():
    load_dotenv()  # Load .env before any commands run
    # ... rest of CLI setup
```

This is a common pattern and python-dotenv is likely already a dependency (or trivial to add).

### Option B: Update Error Message

If auto-loading is not desired, update the error message to be accurate:

```python
# Current (misleading)
print(f"Error: {api_key_env} not set")
print(f"   Set in .env or export {api_key_env}=your-key")

# Better (accurate)
print(f"Error: {api_key_env} not set in environment")
print(f"   Export it: export {api_key_env}=your-key")
print(f"   Or add to shell profile for persistence")
```

### Option C: Add --env-file Flag

```bash
adversarial athena task.md --env-file .env
```

## Recommendation

**Option A** (auto-load .env) provides the best user experience and matches expectations set by the error message. Most Python CLI tools that use API keys support this pattern.

## Test Case

```bash
# Setup
mkdir -p .adversarial/evaluators
echo "GEMINI_API_KEY=test-key" > .env
cat > .adversarial/evaluators/test.yml << 'EOF'
name: test
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
prompt: "Say hello"
EOF

# Current behavior (fails)
unset GEMINI_API_KEY
adversarial test /dev/null
# Expected: Error about GEMINI_API_KEY

# With fix (should work)
# adversarial test /dev/null
# Should find key from .env
```

---

**Document Version**: 1.0.0
**Related**: Plugin architecture implementation (v0.6.0)
