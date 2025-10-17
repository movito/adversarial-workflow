# Integration Examples

This document provides **real-world integration examples** for different project types, languages, and test frameworks.

## Table of Contents

- [Python Projects](#python-projects)
- [JavaScript/TypeScript Projects](#javascripttypescript-projects)
- [Multi-Language Projects](#multi-language-projects)
- [CI/CD Integration](#cicd-integration)
- [Custom Configurations](#custom-configurations)
- [Advanced Patterns](#advanced-patterns)

---

## Python Projects

### Example 1: Python with pytest (Recommended)

**Project structure**:
```
my-python-project/
├── src/
│   ├── __init__.py
│   ├── validation.py
│   └── models.py
├── tests/
│   ├── __init__.py
│   ├── test_validation.py
│   └── test_models.py
├── tasks/
│   └── TASK-001-add-validation.md
├── requirements.txt
├── pytest.ini
└── .git/
```

#### Step 1: Initialize

```bash
cd my-python-project/
adversarial init

# Output:
# 🔧 Initializing adversarial workflow...
# ✓ Created .adversarial/ directory
# ✓ Copied workflow scripts
# ✓ Created config.yml
# ✓ Created .env.example
```

#### Step 2: Configure for pytest

Edit `.adversarial/config.yml`:

```yaml
# Adversarial Workflow Configuration

# Model Configuration
evaluator_model: gpt-4o

# Directory Structure
task_directory: tasks/
log_directory: .adversarial/logs/
artifacts_directory: .adversarial/artifacts/

# Test Configuration
test_command: pytest tests/ -v --tb=short

# Workflow Settings
auto_run: false
git_integration: true
save_artifacts: true
```

#### Step 3: Create Task with Plan

`tasks/TASK-001-add-validation.md`:

```markdown
# TASK-001: Add Clip Validation

## Problem
Clip objects can be created with invalid data (empty name, invalid timecode format, start >= end).
No validation exists to catch these errors early.

## Requirements
1. Create `validate_clip()` function in `src/validation.py`
2. Check name is non-empty
3. Validate timecode format (SMPTE)
4. Ensure start_timecode < end_timecode
5. Return ValidationResult with errors list

## Implementation Plan

**Files to create/modify**:
1. `src/validation.py` - New file with validation logic
2. `tests/test_validation.py` - New test file

**Changes**:

### File: `src/validation.py` (NEW)
```python
from dataclasses import dataclass
from typing import List
from src.models import Clip

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]

def validate_clip(clip: Clip) -> ValidationResult:
    """Validate Clip object according to business rules."""
    errors = []
    
    # Check 1: Name non-empty
    if not clip.name or not clip.name.strip():
        errors.append("Clip name cannot be empty")
    
    # Check 2: Valid timecode format
    if not _is_valid_smpte_timecode(clip.start_timecode):
        errors.append(f"Invalid start timecode: {clip.start_timecode}")
    
    if not _is_valid_smpte_timecode(clip.end_timecode):
        errors.append(f"Invalid end timecode: {clip.end_timecode}")
    
    # Check 3: Start < End
    if _is_valid_smpte_timecode(clip.start_timecode) and _is_valid_smpte_timecode(clip.end_timecode):
        start_frames = _timecode_to_frames(clip.start_timecode, 24)
        end_frames = _timecode_to_frames(clip.end_timecode, 24)
        if start_frames >= end_frames:
            errors.append("Start timecode must be before end timecode")
    
    return ValidationResult(valid=len(errors) == 0, errors=errors)

def _is_valid_smpte_timecode(tc: str) -> bool:
    """Check if string matches HH:MM:SS:FF format."""
    # Implementation here...
    pass

def _timecode_to_frames(tc: str, fps: int) -> int:
    """Convert timecode to frame number."""
    # Implementation here...
    pass
```

### File: `tests/test_validation.py` (NEW)
```python
import pytest
from src.models import Clip
from src.validation import validate_clip

def test_valid_clip():
    """Test that valid clip passes validation."""
    clip = Clip(
        name="Test Clip",
        start_timecode="00:00:00:00",
        end_timecode="00:00:10:00"
    )
    result = validate_clip(clip)
    assert result.valid
    assert len(result.errors) == 0

def test_empty_name():
    """Test that empty name fails validation."""
    clip = Clip(
        name="",
        start_timecode="00:00:00:00",
        end_timecode="00:00:10:00"
    )
    result = validate_clip(clip)
    assert not result.valid
    assert "name cannot be empty" in result.errors[0].lower()

# ... more tests ...
```

**Acceptance Criteria**:
- All 6 validation tests pass
- pytest exit code 0
- No regressions in existing tests
```

#### Step 4: Run Workflow

```bash
# Phase 1: Evaluate plan
adversarial evaluate tasks/TASK-001-add-validation.md

# Review evaluation
cat .adversarial/logs/TASK-001-PLAN-EVALUATION.md

# If APPROVED, proceed to Phase 2 (implementation)
# ... implement code ...

# Phase 3: Review implementation
git add src/validation.py tests/test_validation.py
git commit -m "feat: Add clip validation logic"

adversarial review

# Phase 4: Validate with tests
adversarial validate "pytest tests/test_validation.py -v"

# Phase 5: Final approval
# Review all artifacts, create final commit
```

#### Results

**Typical output**:

```bash
$ adversarial validate "pytest tests/test_validation.py -v"

Running tests: pytest tests/test_validation.py -v
========================= test session starts =========================
tests/test_validation.py::test_valid_clip PASSED                 [ 16%]
tests/test_validation.py::test_empty_name PASSED                 [ 33%]
tests/test_validation.py::test_invalid_start_timecode PASSED     [ 50%]
tests/test_validation.py::test_invalid_end_timecode PASSED       [ 66%]
tests/test_validation.py::test_start_after_end PASSED            [ 83%]
tests/test_validation.py::test_complex_validation PASSED         [100%]

========================== 6 passed in 0.12s ==========================

✓ Validation PASS - All requirements met
```

**Cost**: ~$0.45 (Phase 1: $0.08 + Phase 3: $0.15 + Phase 4: $0.07)

---

### Example 2: Python with unittest

**Configuration** (`.adversarial/config.yml`):

```yaml
evaluator_model: gpt-4o
task_directory: tasks/
test_command: python -m unittest discover tests -v
log_directory: .adversarial/logs/
```

**Task structure**: Same as pytest example

**Test file** (`tests/test_validation.py`):

```python
import unittest
from src.models import Clip
from src.validation import validate_clip

class TestClipValidation(unittest.TestCase):
    def test_valid_clip(self):
        """Test that valid clip passes validation."""
        clip = Clip(
            name="Test Clip",
            start_timecode="00:00:00:00",
            end_timecode="00:00:10:00"
        )
        result = validate_clip(clip)
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_empty_name(self):
        """Test that empty name fails validation."""
        clip = Clip(
            name="",
            start_timecode="00:00:00:00",
            end_timecode="00:00:10:00"
        )
        result = validate_clip(clip)
        self.assertFalse(result.valid)
        self.assertIn("name", result.errors[0].lower())

if __name__ == '__main__':
    unittest.main()
```

**Run validation**:

```bash
adversarial validate "python -m unittest discover tests -v"
```

---

## JavaScript/TypeScript Projects

### Example 3: Node.js with Jest

**Project structure**:
```
my-node-project/
├── src/
│   ├── validation.js
│   └── models.js
├── tests/
│   └── validation.test.js
├── tasks/
│   └── TASK-001-add-validation.md
├── package.json
├── jest.config.js
└── .git/
```

#### Configuration

`.adversarial/config.yml`:

```yaml
evaluator_model: gpt-4o
task_directory: tasks/
test_command: npm test -- --coverage
log_directory: .adversarial/logs/
artifacts_directory: .adversarial/artifacts/
```

#### Task File

`tasks/TASK-001-add-validation.md`:

```markdown
# TASK-001: Add Clip Validation (JavaScript)

## Implementation Plan

**Files**:
1. `src/validation.js` - Validation logic
2. `tests/validation.test.js` - Jest tests

**Changes**:

### File: `src/validation.js` (NEW)
```javascript
class ValidationResult {
  constructor(valid, errors = []) {
    this.valid = valid;
    this.errors = errors;
  }
}

function validateClip(clip) {
  const errors = [];
  
  // Check name
  if (!clip.name || clip.name.trim() === '') {
    errors.push('Clip name cannot be empty');
  }
  
  // Check timecodes
  if (!isValidSMPTETimecode(clip.startTimecode)) {
    errors.push(`Invalid start timecode: ${clip.startTimecode}`);
  }
  
  if (!isValidSMPTETimecode(clip.endTimecode)) {
    errors.push(`Invalid end timecode: ${clip.endTimecode}`);
  }
  
  // Check start < end
  if (isValidSMPTETimecode(clip.startTimecode) && 
      isValidSMPTETimecode(clip.endTimecode)) {
    const startFrames = timecodeToFrames(clip.startTimecode, 24);
    const endFrames = timecodeToFrames(clip.endTimecode, 24);
    if (startFrames >= endFrames) {
      errors.push('Start timecode must be before end timecode');
    }
  }
  
  return new ValidationResult(errors.length === 0, errors);
}

module.exports = { validateClip, ValidationResult };
```

### File: `tests/validation.test.js` (NEW)
```javascript
const { validateClip } = require('../src/validation');
const { Clip } = require('../src/models');

describe('Clip Validation', () => {
  test('valid clip passes validation', () => {
    const clip = new Clip({
      name: 'Test Clip',
      startTimecode: '00:00:00:00',
      endTimecode: '00:00:10:00'
    });
    
    const result = validateClip(clip);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });
  
  test('empty name fails validation', () => {
    const clip = new Clip({
      name: '',
      startTimecode: '00:00:00:00',
      endTimecode: '00:00:10:00'
    });
    
    const result = validateClip(clip);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toMatch(/name cannot be empty/i);
  });
  
  // ... more tests ...
});
```

**Acceptance**: 6 Jest tests passing, coverage > 80%
```

#### Run Workflow

```bash
# Phase 1: Evaluate
adversarial evaluate tasks/TASK-001-add-validation.md

# Phase 2: Implement
# ... write code ...

# Phase 3: Review
git add src/validation.js tests/validation.test.js
git commit -m "feat: Add clip validation"
adversarial review

# Phase 4: Validate
adversarial validate "npm test"

# Or with coverage:
adversarial validate "npm test -- --coverage"
```

#### Jest Output

```bash
$ npm test

> my-node-project@1.0.0 test
> jest

 PASS  tests/validation.test.js
  Clip Validation
    ✓ valid clip passes validation (3 ms)
    ✓ empty name fails validation (1 ms)
    ✓ invalid start timecode fails validation (2 ms)
    ✓ invalid end timecode fails validation (1 ms)
    ✓ start after end fails validation (2 ms)
    ✓ complex validation scenario (3 ms)

Test Suites: 1 passed, 1 total
Tests:       6 passed, 6 total
Snapshots:   0 total
Time:        1.234 s

Ran all test suites.
```

---

### Example 4: TypeScript with Vitest

**Configuration** (`.adversarial/config.yml`):

```yaml
evaluator_model: gpt-4o
task_directory: tasks/
test_command: npx vitest run
log_directory: .adversarial/logs/
```

**Test file** (`tests/validation.test.ts`):

```typescript
import { describe, test, expect } from 'vitest';
import { validateClip } from '../src/validation';
import { Clip } from '../src/models';

describe('Clip Validation', () => {
  test('valid clip passes validation', () => {
    const clip: Clip = {
      name: 'Test Clip',
      startTimecode: '00:00:00:00',
      endTimecode: '00:00:10:00'
    };
    
    const result = validateClip(clip);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });
  
  // ... more tests ...
});
```

**Run**:

```bash
adversarial validate "npx vitest run"
```

---

## Multi-Language Projects

### Example 5: Python + Rust

**Project with multiple test suites**:

```
my-hybrid-project/
├── python/
│   ├── src/
│   └── tests/
├── rust/
│   ├── src/
│   └── tests/
├── tasks/
└── .adversarial/
```

#### Configuration

`.adversarial/config.yml`:

```yaml
evaluator_model: gpt-4o
task_directory: tasks/

# Default test command (can override per task)
test_command: make test

log_directory: .adversarial/logs/
artifacts_directory: .adversarial/artifacts/
```

#### Makefile

```makefile
.PHONY: test test-python test-rust

test: test-python test-rust

test-python:
	cd python && pytest tests/ -v

test-rust:
	cd rust && cargo test --verbose
```

#### Task-Specific Test Commands

For Python-only tasks:

```bash
adversarial validate "cd python && pytest tests/ -v"
```

For Rust-only tasks:

```bash
adversarial validate "cd rust && cargo test"
```

For full integration:

```bash
adversarial validate "make test"
```

---

### Example 6: Monorepo with Multiple Packages

**Structure**:

```
monorepo/
├── packages/
│   ├── api/
│   │   ├── src/
│   │   ├── tests/
│   │   └── package.json
│   ├── ui/
│   │   ├── src/
│   │   ├── tests/
│   │   └── package.json
│   └── shared/
│       ├── src/
│       ├── tests/
│       └── package.json
├── tasks/
├── .adversarial/
└── package.json (root)
```

#### Configuration

`.adversarial/config.yml`:

```yaml
evaluator_model: gpt-4o
task_directory: tasks/

# Run all package tests
test_command: npm run test:all

log_directory: .adversarial/logs/
artifacts_directory: .adversarial/artifacts/
```

#### Root package.json

```json
{
  "scripts": {
    "test:all": "npm run test --workspaces",
    "test:api": "npm run test --workspace=packages/api",
    "test:ui": "npm run test --workspace=packages/ui",
    "test:shared": "npm run test --workspace=packages/shared"
  },
  "workspaces": [
    "packages/*"
  ]
}
```

#### Package-Specific Validation

```bash
# For API-only changes
adversarial validate "npm run test:api"

# For UI-only changes
adversarial validate "npm run test:ui"

# For changes affecting multiple packages
adversarial validate "npm run test:all"
```

---

## CI/CD Integration

### Example 7: GitHub Actions

**Workflow file** (`.github/workflows/adversarial-review.yml`):

```yaml
name: Adversarial Code Review

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  review:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for git diff
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install adversarial-workflow
          pip install aider-chat
          pip install -r requirements.txt
      
      - name: Run code review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          # Review PR changes
          adversarial review
      
      - name: Upload review artifacts
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: adversarial-review
          path: .adversarial/logs/
      
      - name: Comment on PR
        uses: actions/github-script@v6
        if: always()
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('.adversarial/logs/CODE-REVIEW.md', 'utf8');
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🤖 Adversarial Code Review\n\n${review}`
            });
```

### Example 8: GitLab CI

**GitLab CI config** (`.gitlab-ci.yml`):

```yaml
stages:
  - review
  - test

adversarial_review:
  stage: review
  image: python:3.11
  
  before_script:
    - pip install adversarial-workflow aider-chat
    - pip install -r requirements.txt
  
  script:
    - adversarial review
  
  artifacts:
    paths:
      - .adversarial/logs/
    expire_in: 1 week
  
  only:
    - merge_requests
  
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY

test_validation:
  stage: test
  image: python:3.11
  
  script:
    - pip install -r requirements.txt
    - pytest tests/ -v
  
  only:
    - merge_requests
```

### Example 9: Pre-commit Hook (Local)

**Setup pre-commit hook** (`.git/hooks/pre-commit`):

```bash
#!/bin/bash
# Pre-commit hook to run adversarial review

echo "🔍 Running adversarial code review..."

# Check if there are changes
if ! git diff --cached --quiet; then
  # Save staged changes
  git diff --cached > /tmp/staged-changes.diff
  
  # Run quick review
  aider \
    --model gpt-4o \
    --yes \
    --read /tmp/staged-changes.diff \
    --message "Quick review: Any obvious bugs or issues in this diff? 
                Answer in 2-3 sentences." \
    --no-auto-commits
  
  echo ""
  read -p "Proceed with commit? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Commit aborted."
    exit 1
  fi
fi

exit 0
```

**Make executable**:

```bash
chmod +x .git/hooks/pre-commit
```

---

## Custom Configurations

### Example 10: Custom Task Directory Structure

**Non-standard structure**:

```
my-project/
├── docs/
│   └── tasks/        # ← Custom location
│       ├── active/
│       └── completed/
├── src/
└── tests/
```

**Configuration** (`.adversarial/config.yml`):

```yaml
evaluator_model: gpt-4o
task_directory: docs/tasks/active/
log_directory: docs/tasks/logs/
artifacts_directory: docs/tasks/artifacts/
test_command: pytest tests/ -v
```

**Usage** (paths relative to project root):

```bash
adversarial evaluate docs/tasks/active/TASK-001.md
```

### Example 11: Multi-Agent Workflows

If you're using multiple AI agents for development (Claude Code, Cursor, Aider, etc.), you can set up **agent coordination** to manage tasks across agents:

#### Setup Agent Coordination

```bash
# Initialize adversarial workflow first
cd my-project/
adversarial init --interactive

# Then set up agent coordination (optional)
adversarial agent onboard

# Follow the prompts:
# Q1: Use delegation/tasks/ structure? (Y/n) → Y
# Q2: Organize root docs into docs/? (y/N) → n
```

**What gets created**:

```
my-project/
├── .adversarial/           # Core workflow (code review)
├── .agent-context/         # NEW: Agent coordination
│   ├── agent-handoffs.json # Agent status tracking
│   ├── current-state.json  # Project state
│   ├── README.md           # Quick guide
│   └── AGENT-SYSTEM-GUIDE.md  # Full documentation
├── delegation/             # NEW: Structured task management
│   ├── tasks/
│   │   ├── active/         # Current tasks
│   │   ├── completed/      # Done tasks
│   │   └── analysis/       # Research/planning
│   └── handoffs/           # Agent transitions
├── agents/                 # NEW: Agent tools/scripts
│   ├── tools/              # Shared utilities
│   └── launchers/          # Agent startup scripts
└── src/                    # Your code (unchanged)
```

#### Agent Roles

The system initializes 7 specialized agents in `agent-handoffs.json`:

1. **coordinator** - Task planning and project management
2. **api-developer** - Backend API integration
3. **format-developer** - Data format and export systems
4. **media-processor** - Media processing (if applicable)
5. **test-runner** - Test execution and QA
6. **document-reviewer** - Documentation quality
7. **feature-developer** - Feature implementation

**Each agent has**:
- `current_focus`: What they're working on
- `task_file`: Path to their active task
- `status`: available | working | blocked | completed
- `deliverables`: Track completed work

#### Usage Pattern 1: Solo Developer with AI Assistants

Use different AI tools for different phases:

```bash
# Phase 1: Planning (you + coordinator)
cat > delegation/tasks/active/TASK-001-add-auth.md <<'EOF'
# TASK-001: Add User Authentication

## Requirements
- JWT-based auth
- Login/logout endpoints
- Password hashing

## Assigned: feature-developer
## Reviewer: api-developer
EOF

# Phase 2: Implementation (Claude Code / Aider)
# Open task in your AI assistant, implement
# The assistant reads: delegation/tasks/active/TASK-001-add-auth.md

# Phase 3: Review (adversarial workflow)
adversarial review  # Independent code review

# Phase 4: Testing (test-runner role)
adversarial validate "pytest tests/"

# Phase 5: Documentation (document-reviewer)
# Update agent-handoffs.json to track completion
```

#### Usage Pattern 2: Multi-Agent Team

Coordinate between multiple AI agents working in parallel:

```bash
# Coordinator creates tasks
cat > delegation/tasks/active/TASK-001-api.md <<'EOF'
# TASK-001: API Endpoints
**Assigned**: api-developer
**Blocks**: TASK-003 (frontend needs API first)
EOF

cat > delegation/tasks/active/TASK-002-tests.md <<'EOF'
# TASK-002: Test Infrastructure
**Assigned**: test-runner
**Parallel**: Can work alongside TASK-001
EOF

# Agent 1: API Developer (Aider session)
aider --read delegation/tasks/active/TASK-001-api.md --architect-mode
# ... implements API endpoints ...
adversarial review  # Code review

# Agent 2: Test Runner (separate session)
aider --read delegation/tasks/active/TASK-002-tests.md
# ... writes tests ...
adversarial validate "pytest tests/"

# Coordinator: Update agent-handoffs.json
# Track progress, dependencies, blockers
```

#### Check System Health

Monitor overall project and agent coordination health:

```bash
adversarial health --verbose

# Output:
# 🏥 Adversarial Workflow Health Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Configuration:
#   ✅ .adversarial/config.yml - Valid YAML
#   ✅ evaluator_model: gpt-4o
#   ✅ task_directory: delegation/tasks/ (exists)
#
# Dependencies:
#   ✅ Git: 2.42.0 (working tree clean)
#   ✅ Python: 3.11.5 (compatible)
#   ✅ Aider: 0.37.0 (functional)
#
# API Keys:
#   ✅ OPENAI_API_KEY: Set (from .env) [sk-proj-...Xy4z]
#   ✅ ANTHROPIC_API_KEY: Set (from .env) [sk-ant-...Ab1c]
#
# Agent Coordination:
#   ✅ .agent-context/ directory exists
#   ✅ agent-handoffs.json - Valid JSON (7 agents)
#   ✅ current-state.json - Valid JSON
#   ✅ AGENT-SYSTEM-GUIDE.md - Present (34KB)
#   ℹ️  Last updated: 2025-10-17
#
# Workflow Scripts:
#   ✅ evaluate_plan.sh - Executable, valid
#   ✅ review_implementation.sh - Executable, valid
#   ✅ validate_tests.sh - Executable, valid
#
# Tasks:
#   ℹ️  3 active tasks in delegation/tasks/active/
#
# Permissions:
#   ✅ .env - Secure (600)
#   ✅ All 3 scripts executable
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# ✅ System is healthy! (Health: 95%)
#    42 checks passed, 2 warnings, 0 errors
```

#### Integration with Adversarial Workflow

The two systems work together:

| System | Purpose | Commands |
|--------|---------|----------|
| **Adversarial Workflow** | Code quality gates | `adversarial evaluate/review/validate` |
| **Agent Coordination** | Task management | `adversarial agent onboard`, `adversarial health` |

**Combined workflow**:

```bash
# 1. Coordinator plans task (agent coordination)
vim delegation/tasks/active/TASK-005-refactor.md

# 2. Evaluate plan (adversarial workflow)
adversarial evaluate delegation/tasks/active/TASK-005-refactor.md

# 3. Feature developer implements (agent coordination)
# Update agent-handoffs.json: feature-developer status = working

# 4. Review implementation (adversarial workflow)
adversarial review

# 5. Test runner validates (agent coordination)
adversarial validate "pytest tests/"

# 6. Move to completed (agent coordination)
mv delegation/tasks/active/TASK-005-refactor.md delegation/tasks/completed/
```

#### Benefits

**Without agent coordination**:
- Tasks scattered across `tasks/`, unclear structure
- No visibility into agent status or blockers
- Manual tracking in separate docs
- Difficult to coordinate parallel work

**With agent coordination**:
- ✅ Structured task management (`active/`, `completed/`)
- ✅ Clear agent assignments and status
- ✅ Dependency tracking between tasks
- ✅ Health monitoring across the system
- ✅ Coordination guide at `.agent-context/AGENT-SYSTEM-GUIDE.md`

#### When to Use Agent Coordination

**✅ Use it when**:
- Working with multiple AI agents/assistants
- Need structured task assignment
- Managing complex projects with dependencies
- Want visibility into development status

**❌ Skip it when**:
- Solo development without agents
- Simple projects with few tasks
- Already have robust task management
- Just want code review (adversarial workflow alone is enough)

#### Configuration

Agent coordination updates `.adversarial/config.yml` to use delegation structure:

```yaml
# Before: adversarial init
task_directory: tasks/

# After: adversarial agent onboard (if you chose delegation)
task_directory: delegation/tasks/
```

This makes both systems work with the same structured task directory.

#### Learn More

- **Quick guide**: `.agent-context/README.md`
- **Full documentation**: `.agent-context/AGENT-SYSTEM-GUIDE.md`
- **Health check**: `adversarial health --verbose`

---

### Example 12: Multiple Test Environments

**Configuration for different environments**:

```yaml
# .adversarial/config.yml
evaluator_model: gpt-4o
task_directory: tasks/

# Default to unit tests
test_command: pytest tests/unit/ -v

log_directory: .adversarial/logs/
```

**Override for integration tests**:

```bash
# Use environment variable
export ADVERSARIAL_TEST_COMMAND="pytest tests/integration/ -v --slow"
adversarial validate "$ADVERSARIAL_TEST_COMMAND"
```

**Or specify directly**:

```bash
adversarial validate "pytest tests/integration/ -v"
```

### Example 13: Custom Reviewer Model

**For different use cases**:

```yaml
# .adversarial/config.yml

# Use GPT-4 Turbo for faster reviews (slightly lower quality)
evaluator_model: gpt-4-turbo

# Or use GPT-4o-mini for cost savings (basic reviews only)
# evaluator_model: gpt-4o-mini

# Or use latest GPT-4 for highest quality
# evaluator_model: gpt-4

task_directory: tasks/
test_command: pytest tests/ -v
```

**Cost comparison** (per task):

| Model | Cost/Task | Quality | Speed |
|-------|-----------|---------|-------|
| gpt-4o-mini | $0.10-0.30 | Good | Fast |
| gpt-4-turbo | $0.25-0.75 | Very Good | Fast |
| gpt-4o | $0.30-1.00 | Excellent | Medium |
| gpt-4 | $0.50-2.00 | Excellent | Slower |

**Recommendation**: Start with `gpt-4o` (best balance), downgrade to `gpt-4o-mini` if cost is concern.

---

## Advanced Patterns

### Example 14: Task Templates

**Create task template** (`tasks/TEMPLATE.md`):

```markdown
# TASK-XXX-[title]

## Problem
[What's broken or missing?]

## Current State
- [Relevant metrics, test counts, etc.]

## Requirements
1. [Specific requirement]
2. [Another requirement]

## Implementation Plan

**Scope**: [Brief scope summary]

**Files**:
- `path/to/file.py` (EDIT/NEW)

**Changes**:

### File: `path/to/file.py`
```python
# SEARCH:
[old code]

# REPLACE:
[new code]
```

**Acceptance Criteria**:
- [Specific test outcomes]
- [Metrics targets]
- Exit code 0

**Time Estimate**: [X hours]

**Risks**:
- [Potential issues]
```

**Usage**:

```bash
# Create new task from template
cp tasks/TEMPLATE.md tasks/TASK-042-fix-validation.md
# Edit task-042...

# Run workflow
adversarial evaluate tasks/TASK-042-fix-validation.md
```

### Example 15: Batch Processing

**Process multiple tasks**:

```bash
#!/bin/bash
# batch-evaluate.sh - Evaluate all pending tasks

for task in tasks/pending/TASK-*.md; do
  echo "=== Evaluating $task ==="
  adversarial evaluate "$task"
  
  # Check if approved
  task_num=$(basename "$task" .md)
  if grep -q "Verdict: APPROVED" ".adversarial/logs/${task_num}-PLAN-EVALUATION.md"; then
    echo "✓ $task APPROVED"
    mv "$task" "tasks/approved/"
  else
    echo "⚠ $task NEEDS_REVISION"
  fi
  echo ""
done

echo "Batch evaluation complete."
echo "Approved tasks moved to tasks/approved/"
```

### Example 16: Custom Review Criteria

**Add project-specific checks** by extending the review script:

```bash
# .adversarial/scripts/review_implementation_custom.sh

# ... standard review code ...

# Custom checks
echo ""
echo "=== Running custom project checks ==="

# Check 1: No hardcoded credentials
if git diff | grep -i "password\|api_key\|secret"; then
  echo "❌ WARNING: Potential hardcoded credentials detected!"
  git diff | grep -i "password\|api_key\|secret"
fi

# Check 2: All new functions have docstrings
if git diff | grep "^+def " | grep -v '"""'; then
  echo "⚠️ WARNING: New functions without docstrings"
  git diff | grep "^+def "
fi

# Check 3: No print() statements in production code
if git diff -- src/ | grep "^+.*print("; then
  echo "⚠️ WARNING: print() statements in production code"
  git diff -- src/ | grep "^+.*print("
fi

echo "Custom checks complete."
```

### Example 17: Integration with Task Management

**Sync with GitHub Issues**:

```bash
#!/bin/bash
# create-task-from-issue.sh - Convert GitHub issue to task file

ISSUE_NUM="$1"

# Fetch issue details
gh issue view "$ISSUE_NUM" --json title,body > /tmp/issue-${ISSUE_NUM}.json

# Extract details
TITLE=$(jq -r '.title' /tmp/issue-${ISSUE_NUM}.json)
BODY=$(jq -r '.body' /tmp/issue-${ISSUE_NUM}.json)

# Create task file
cat > "tasks/TASK-${ISSUE_NUM}-${TITLE// /-}.md" <<EOF
# TASK-${ISSUE_NUM}: ${TITLE}

## Problem
${BODY}

## Implementation Plan
[TODO: Add implementation details]

**Acceptance Criteria**:
- Resolves #${ISSUE_NUM}

EOF

echo "Created task file: tasks/TASK-${ISSUE_NUM}-${TITLE// /-}.md"
```

**Usage**:

```bash
# Create task from issue #42
./create-task-from-issue.sh 42

# Edit task file
vim tasks/TASK-42-*.md

# Run workflow
adversarial evaluate tasks/TASK-42-*.md
```

---

## Tips for Different Project Types

### For Web Applications

```yaml
# .adversarial/config.yml
test_command: npm run test:e2e && npm run test:unit

# Run both end-to-end and unit tests
```

**Consider**: Running visual regression tests, accessibility tests.

### For Data Science Projects

```yaml
# .adversarial/config.yml
test_command: pytest tests/ -v && python scripts/validate_model.py

# Run unit tests + model validation
```

**Consider**: Checking model accuracy, data quality, reproducibility.

### For CLI Tools

```yaml
# .adversarial/config.yml
test_command: pytest tests/ -v && ./tests/integration/run_cli_tests.sh

# Run unit tests + CLI integration tests
```

**Consider**: Testing error messages, help output, edge cases.

### For Libraries

```yaml
# .adversarial/config.yml
test_command: pytest tests/ --cov=src --cov-report=term-missing

# Require high code coverage
```

**Consider**: Testing public API, backward compatibility, documentation examples.

---

## Conclusion

The adversarial workflow adapts to:

- **Any language**: Python, JavaScript, TypeScript, Rust, Go, etc.
- **Any test framework**: pytest, unittest, Jest, Vitest, Mocha, etc.
- **Any project structure**: Monorepo, multi-language, custom layouts
- **Any CI/CD system**: GitHub Actions, GitLab CI, Jenkins, etc.

**Key principles**:

1. Configure `test_command` to match your project
2. Organize tasks in a way that makes sense for you
3. Customize workflows to fit your team's process
4. Integrate with existing tools and systems

**The workflow is flexible** - adapt it to your needs, don't force your project to fit the workflow.

For more examples, see:
- [thematic-cuts](https://github.com/movito/thematic-cuts) - Real production usage
- [GitHub discussions](https://github.com/movito/adversarial-workflow/discussions) - Community examples
