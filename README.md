# Adversarial Workflow

**Multi-stage AI code review system preventing phantom work**

Prevent "phantom work" (AI claiming to implement but not delivering) through adversarial verification using independent review stages. A battle-tested workflow from the [thematic-cuts](https://github.com/movito/thematic-cuts) project that achieved 96.9% test pass rate improvement.

**🎯 100% Standalone** - No special IDE or agent system required. Works with any development workflow.

## Features

- 🔍 **Multi-stage verification**: Plan → Implement → Review → Test → Approve
- 🤖 **Adversarial review**: Independent AI reviews your implementation
- 💰 **Token-efficient**: 10-20x reduction vs. standard Aider usage
- 🔌 **Non-destructive**: Integrates into existing projects without changes
- ⚙️ **Configurable**: Works with any test framework, task system, language
- 🎯 **Tool-agnostic**: Use with Claude Code, Cursor, Aider, manual coding, or any workflow
- ✨ **Interactive onboarding**: Guided setup wizard gets you started in <5 minutes

## Quick Start

> **⚠️ Platform Requirements**: This package requires Unix-like systems (macOS/Linux) or **WSL** on Windows. Native Windows (PowerShell/CMD) is not supported. [Platform details →](#platform-support)

### Interactive Setup (Recommended)

```bash
# Install
pip install adversarial-workflow

# Quick start with guided setup
cd my-project/
adversarial quickstart

# Follow the interactive wizard:
# - Choose your API setup (Anthropic + OpenAI recommended)
# - Paste your API keys (validated automatically)
# - Run your first evaluation in <5 minutes!
```

### Manual Setup

```bash
# Install
pip install adversarial-workflow

# Initialize in your project
cd my-project/
adversarial init --interactive  # Interactive wizard
# OR
adversarial init                # Standard init

# Verify setup
adversarial check

# Use the workflow
adversarial evaluate tasks/feature.md  # Phase 1: Plan evaluation
# ... implement your feature (any method) ...
adversarial review                     # Phase 3: Code review
adversarial validate "npm test"        # Phase 4: Test validation
```

## The Adversarial Pattern

Traditional AI coding suffers from "phantom work" - where AI claims implementation is complete but only adds comments or TODOs. This workflow prevents that through **multiple independent verification gates**:

### Phase 1: Plan Evaluation
**Reviewer** (aider + GPT-4o or Claude) reviews your implementation plan before coding begins.
- Catches design flaws early
- Validates completeness
- Identifies missing edge cases
- Reduces wasted implementation effort

### Phase 2: Implementation
**Author** (you, or your AI assistant) implements according to approved plan.
- Use any method: Claude Code, Cursor, Aider, manual coding, etc.
- Clear roadmap reduces confusion
- Plan adherence is verifiable
- Deviations are intentional and documented

### Phase 3: Code Review
**Reviewer** (aider) reviews actual git diff against plan.
- **Phantom work detection**: Checks for real code vs. TODOs
- Verifies plan adherence
- Catches implementation bugs early
- Provides specific, actionable feedback

### Phase 4: Test Validation
**Reviewer** (aider) analyzes test results objectively.
- Proves functionality works (not just looks right)
- Catches regressions immediately
- Validates all requirements met
- Provides detailed failure analysis

### Phase 5: Final Approval
**Author** (you) reviews all artifacts and commits with audit trail.

## Package Independence

This package is **completely standalone** and works with any development workflow:

✅ **No Claude Code required** - Works with any editor/IDE
✅ **No special agent system required** - Just aider + API keys
✅ **Integrates into existing projects** - Doesn't change your workflow
✅ **Tool-agnostic** - Use with your preferred development tools

**You can implement using:**
- **Claude Code** (what thematic-cuts project uses)
- **Cursor** / **GitHub Copilot** / any AI coding assistant
- **Aider directly** (`aider --architect-mode`)
- **Manual coding** with AI review
- **Any combination** of the above

**The adversarial workflow reviews your implementation**, regardless of how you create it.

### What "Author" and "Reviewer" Actually Mean

**THESE ARE METAPHORS, NOT TECHNICAL COMPONENTS.**

- **"Author"**: Whoever creates the work (plan or code)
  - METAPHOR for: The person or tool that writes implementation plans and code
  - In practice: You, Claude Code, Cursor, Copilot, aider, manual coding
  - Technical reality: Just whoever writes the files

- **"Reviewer"**: Independent analysis stage that critiques the Author's work
  - METAPHOR for: Independent review perspective
  - Technical reality: `aider --model gpt-4o --message "review prompt"`
  - NOT a persistent agent or special software
  - Different prompt for each phase (plan evaluation, code review, test validation)

**No agents, no infrastructure, no special setup** - just aider with different review prompts at each verification stage!

**Historical note**: Earlier versions used "Coordinator" and "Evaluator" terminology, which caused confusion. We've updated to "Author/Reviewer" for universal clarity.

## Token Optimization

Key to avoiding excessive costs:

```bash
# ❌ Standard Aider (expensive)
aider --files src/**/*.py    # Adds all files to context

# ✅ Adversarial pattern (efficient)
aider --read task.md --read diff.txt --message "review this"
# Only reads specific files, doesn't add to context
```

**Result**: 20-40k tokens per task vs. 100-500k with full context = **10-20x savings**

## Integration with Existing Projects

Works with your existing task management, test framework, and workflow:

### Before
```
my-project/
├── tasks/current/
├── src/
├── tests/
└── README.md
```

### After `adversarial init`
```
my-project/
├── tasks/current/          # ← UNCHANGED
├── .adversarial/           # ← NEW (workflow files)
│   ├── scripts/
│   ├── config.yml
│   └── logs/
├── src/                    # ← UNCHANGED
├── tests/                  # ← UNCHANGED
└── README.md               # ← UNCHANGED
```

**Configuration** (`.adversarial/config.yml`):
```yaml
evaluator_model: gpt-4o            # AI model for Reviewer (aider)
task_directory: tasks/current/    # Your existing tasks
test_command: npm test             # Your test command
log_directory: .adversarial/logs/
```

## Commands

```bash
adversarial init              # Initialize in current project
adversarial init --path /other/project  # Initialize elsewhere

adversarial check             # Validate setup (aider, API keys, config)

adversarial evaluate task.md  # Phase 1: Evaluate plan
adversarial review            # Phase 3: Review implementation
adversarial validate "pytest" # Phase 4: Validate with tests
```

## Configuration

### Option 1: YAML Config (persistent)
`.adversarial/config.yml`:
```yaml
evaluator_model: gpt-4o
task_directory: tasks/
test_command: pytest tests/
log_directory: .adversarial/logs/
```

### Option 2: Environment Variables (temporary overrides)
```bash
export ADVERSARIAL_EVALUATOR_MODEL=gpt-4-turbo
export ADVERSARIAL_TEST_COMMAND="npm run test:integration"
```

**Precedence**: Environment variables > YAML config > defaults

## Requirements

### Platform Support

**✅ Supported Platforms**:
- **macOS**: Fully supported (tested on macOS 10.15+)
- **Linux**: Fully supported (tested on Ubuntu 22.04, Debian 11+, CentOS 8+)
  - Works on any Unix-like system with bash 3.2+

**⚠️ Windows**:
- **Native Windows**: Not supported (Bash scripts are Unix-specific)
- **WSL (Windows Subsystem for Linux)**: ✅ Fully supported (recommended)
- **Git Bash**: ⚠️ May work but not officially tested

**Why Unix-only?** This package uses Bash scripts for workflow automation. While Python is cross-platform, the workflow scripts (`.adversarial/scripts/*.sh`) are designed for Unix-like shells.

#### Windows Users: WSL Setup (5 minutes)

If you're on Windows, install WSL for the best experience:

```powershell
# Run in PowerShell (Administrator)
wsl --install

# After restart, set up Ubuntu (default)
# Then install Python and pip in WSL:
sudo apt update
sudo apt install python3 python3-pip

# Install the package in WSL
pip install adversarial-workflow
```

**Official WSL guide**: https://learn.microsoft.com/windows/wsl/install

#### Git Bash Limitations

While Git Bash *may* work, be aware of:
- Script compatibility issues with Windows paths
- Potential ANSI color rendering problems
- Some commands may behave differently
- **Not officially supported** - use at your own risk

#### Platform Detection

The CLI automatically detects Windows and shows an interactive warning:
- `adversarial init --interactive` checks platform before setup
- `adversarial quickstart` checks platform before onboarding
- You can choose to continue anyway (for WSL/Git Bash users)

#### Troubleshooting

**"Command not found: adversarial"** (WSL)
- Make sure you installed in WSL, not Windows: `which adversarial`
- Add to PATH: `export PATH="$HOME/.local/bin:$PATH"`

**Scripts fail with "bad interpreter"** (Git Bash)
- Line ending issue - convert to Unix: `dos2unix .adversarial/scripts/*.sh`
- Or switch to WSL (recommended)

**Permission denied on scripts** (macOS/Linux)
- Make scripts executable: `chmod +x .adversarial/scripts/*.sh`
- Or run: `adversarial init` again to reset permissions

### Software Requirements

- **Python**: 3.8 or later (Python 3.12 recommended)
- **Bash**: 3.2 or later (included with macOS/Linux)
- **Git**: Repository required (workflow uses git diff)
- **Aider**: `pip install aider-chat`
- **API Keys**: OpenAI and/or Anthropic (see interactive setup)

## Usage Examples

### Example 1: Manual Coding with AI Review

Perfect for developers who prefer manual coding but want AI quality checks:

```bash
# 1. Create your task plan
cat > tasks/add-user-auth.md << 'EOF'
# Task: Add User Authentication

## Requirements
- JWT-based authentication
- Login/logout endpoints
- Password hashing with bcrypt

## Acceptance Criteria
- All tests pass
- No security vulnerabilities
EOF

# 2. Get plan reviewed
adversarial evaluate tasks/add-user-auth.md
# AI reviews plan, suggests improvements

# 3. Implement manually (your preferred editor)
vim src/auth.py
vim src/routes.py
vim tests/test_auth.py

# 4. Get implementation reviewed
git add -A
adversarial review
# AI reviews your git diff for issues

# 5. Validate with tests
adversarial validate "pytest tests/test_auth.py"
# AI analyzes test results
```

### Example 2: With Aider for Implementation

Use aider for coding, adversarial workflow for quality gates:

```bash
# 1. Create and evaluate plan
echo "# Task: Refactor database layer" > tasks/refactor-db.md
adversarial evaluate tasks/refactor-db.md

# 2. Implement with aider
aider --architect-mode src/database.py
# ... make changes with aider ...

# 3. Review implementation
adversarial review
# Independent AI reviews what aider did

# 4. Validate
adversarial validate "npm test"
```

### Example 3: With Cursor/Copilot

Works great with any AI coding assistant:

```bash
# 1. Get plan approved
adversarial evaluate tasks/new-feature.md

# 2. Code in Cursor/VS Code with Copilot
# ... use your AI assistant as normal ...

# 3. Get adversarial review
adversarial review
# Catches issues your coding assistant might miss

# 4. Validate
adversarial validate "cargo test"
```

### Example 4: JavaScript/TypeScript Project

```bash
# Setup
cd my-react-app
adversarial init --interactive

# Configure for Node.js
cat > .adversarial/config.yml << 'EOF'
evaluator_model: gpt-4o
task_directory: tasks/
test_command: npm test
log_directory: .adversarial/logs/
EOF

# Use workflow
adversarial evaluate tasks/add-dark-mode.md
# ... implement feature ...
adversarial review
adversarial validate "npm test"
```

### Example 5: Python Project with pytest

```bash
# Setup
cd my-python-app
adversarial quickstart  # Interactive setup

# Use workflow
adversarial evaluate tasks/optimize-queries.md
# ... implement with any method ...
adversarial review
adversarial validate "pytest tests/ -v"
```

### Example 6: Go Project

```bash
# Setup
cd my-go-service
adversarial init --interactive

# Configure
cat > .adversarial/config.yml << 'EOF'
evaluator_model: gpt-4o
task_directory: docs/tasks/
test_command: go test ./...
log_directory: .adversarial/logs/
EOF

# Use workflow
adversarial evaluate docs/tasks/add-grpc-endpoint.md
# ... implement ...
adversarial review
adversarial validate "go test ./..."
```

### Example 7: Handling Review Feedback (Iteration)

What to do when the reviewer requests changes:

```bash
# 1. Create and evaluate plan
adversarial evaluate tasks/add-caching.md
# Reviewer: "APPROVED - plan looks good"

# 2. Implement feature
# ... write code ...
git add -A

# 3. Review implementation
adversarial review
# Reviewer: "NEEDS_REVISION - Missing error handling in cache.get()"

# 4. Address feedback (iterate)
# ... fix the issues mentioned ...
git add -A

# 5. Review again
adversarial review
# Reviewer: "APPROVED - error handling looks good now"

# 6. Validate with tests
adversarial validate "pytest tests/"
# All checks passed - ready to commit!
```

**Key Points**:
- Review failures are normal and helpful
- Each iteration makes code better
- Git diff shows only your changes (not whole codebase)
- Reviewer feedback is specific and actionable

### Example 8: Project Without Tests (Legacy Code)

Working with projects that don't have tests yet:

```bash
# Setup
cd legacy-project
adversarial init --interactive

# Configure without tests
cat > .adversarial/config.yml << 'EOF'
evaluator_model: gpt-4o
task_directory: tasks/
test_command: echo "No tests yet - manual verification required"
log_directory: .adversarial/logs/
EOF

# Use workflow (skip validation phase)
adversarial evaluate tasks/fix-bug-123.md
# ... implement fix ...
adversarial review  # Still get code review!

# Skip test validation (no tests)
# Manually verify the fix works

# Optional: Ask reviewer to suggest tests
cat > tasks/add-tests-for-bug-123.md << 'EOF'
# Task: Add Tests for Bug Fix #123

## Goal
Add regression tests for the bug fix in src/payment.py

## Acceptance Criteria
- Test the failing case (bug reproduction)
- Test the fixed case (verify fix works)
EOF

adversarial evaluate tasks/add-tests-for-bug-123.md
```

**Benefits Even Without Tests**:
- Code review still catches issues
- Reviewer suggests test cases
- Helps you add tests incrementally
- Better than no review at all

### Example 9: Monorepo / Multi-Package Project

Working with monorepos or projects with multiple services:

```bash
# Setup in monorepo root
cd my-monorepo
adversarial init --interactive

# Configure for specific package
cat > .adversarial/config.yml << 'EOF'
evaluator_model: gpt-4o
task_directory: tasks/
test_command: npm run test:all  # Runs tests for all packages
log_directory: .adversarial/logs/
EOF

# Workflow for specific package
adversarial evaluate tasks/api-add-endpoint.md

# Implement in specific package
cd packages/api
# ... make changes ...
cd ../..

git add packages/api/

# Review only API package changes
adversarial review
# Reviewer sees only packages/api/ in git diff

# Run all tests (monorepo-wide)
adversarial validate "npm run test:all"

# Alternative: Test only affected package
adversarial validate "npm run test --workspace=@myapp/api"
```

**Monorepo Tips**:
- Review works on git diff (any subset of files)
- Use workspace-specific test commands
- Task files can specify which package
- One .adversarial/ setup for whole monorepo

### Example 10: Cost Optimization (Large Projects)

For large projects where full runs are expensive:

```bash
# Configure with cheaper model for reviews
cat > .adversarial/config.yml << 'EOF'
evaluator_model: gpt-4o-mini  # Cheaper alternative
task_directory: tasks/
test_command: pytest tests/
log_directory: .adversarial/logs/
EOF

# Strategy 1: Review only changed files
git add src/module.py tests/test_module.py  # Not "git add -A"
adversarial review
# Reviewer sees minimal diff - cheaper

# Strategy 2: Split large tasks into smaller ones
# Instead of:
#   tasks/refactor-entire-app.md (huge)
# Use:
#   tasks/refactor-auth-module.md (small)
#   tasks/refactor-api-module.md (small)
#   tasks/refactor-db-module.md (small)

# Strategy 3: Use test subsets
adversarial validate "pytest tests/test_module.py -v"  # Not all tests

# Strategy 4: Only validate on final review
adversarial evaluate tasks/feature.md  # Phase 1
# ... implement ...
adversarial review  # Phase 3
# Skip validation during iteration
# Run full validation only when review passes
adversarial validate "pytest tests/"  # Phase 4 (final)
```

**Cost Breakdown**:
- GPT-4o: ~$0.005-0.02 per review (input + output)
- GPT-4o-mini: ~$0.001-0.005 per review (70% cheaper)
- Smaller diffs = fewer tokens = lower cost
- Strategic validation = fewer test runs

## Real-World Results

From the [thematic-cuts](https://github.com/movito/thematic-cuts) project:

- **Before**: 85.1% test pass rate (298/350 tests)
- **After**: 96.9% test pass rate (339/350 tests)
- **Improvement**: +41 tests fixed, +11.8% pass rate
- **Phantom work incidents**: 0 (after implementing this workflow)
- **Tasks completed**: 5 major refactors using this system

## Documentation

- **Interaction Patterns**: How Author-Reviewer collaboration works
- **Token Optimization**: Detailed Aider configuration guide
- **Workflow Phases**: Step-by-step guide for each phase
- **Troubleshooting**: Common issues and solutions
- **Examples**: Real integration scenarios
- **Terminology**: Official standards for Author/Reviewer concepts

See `docs/` directory for comprehensive guides.

## CI/CD Integration

Example GitHub Actions:
```yaml
name: Adversarial Code Review
on: pull_request
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install adversarial-workflow
      - run: adversarial review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Contributing

Contributions welcome! This package is extracted from real-world usage in [thematic-cuts](https://github.com/movito/thematic-cuts).

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)

## Credits

Developed by [broadcaster_one](https://github.com/movito) and refined through months of production use on the thematic-cuts project.

**Inspired by**: The realization that AI needs AI to keep it honest.
