# Quick Start Guide

**Get started with adversarial-workflow in under 5 minutes**

This guide walks you through installing and running your first adversarial code review workflow.

---

## What You'll Need

Before starting, make sure you have:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Git** installed and a git repository ([Git Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))
- **API Key** from [Anthropic](https://console.anthropic.com/settings/keys) or [OpenAI](https://platform.openai.com/api-keys)
  - Anthropic: Claude 3.5 Sonnet (recommended)
  - OpenAI: GPT-4o
  - Both APIs: Best results (~$0.02-0.10 per workflow)
  - One API: Still works well (~$0.05-0.15 per workflow)

**Platform Requirements:**
- ✅ macOS / Linux: Fully supported
- ✅ Windows WSL: Fully supported ([Setup WSL](https://learn.microsoft.com/windows/wsl/install))
- ❌ Native Windows: Not supported (use WSL)

---

## Step 1: Install aider

adversarial-workflow uses [aider](https://aider.chat/) for AI code review.

```bash
pip install aider-chat
```

**Verify installation:**
```bash
aider --version
```

Expected output: `aider version X.Y.Z`

**Troubleshooting:**
- If `aider` command not found: Check your PATH or use `python -m aider`
- If pip fails: Try `pip install --user aider-chat`

---

## Step 2: Install adversarial-workflow

```bash
pip install adversarial-workflow
```

**Verify installation:**
```bash
adversarial --version
```

Expected output: `adversarial-workflow 0.2.3` (or later)

**Alternative verification:**
```bash
python -m adversarial_workflow --version
```

---

## Step 3: Initialize in Your Project

Navigate to your project directory:

```bash
cd /path/to/your/project
```

**Option A: Interactive Setup (Recommended for First Time)**

```bash
adversarial quickstart
```

This will:
1. Guide you through setup
2. Ask for your API keys
3. Create an example task
4. Run your first evaluation

**Option B: Manual Setup**

```bash
adversarial init --interactive
```

Follow the prompts to:
- Choose your API setup (both/Anthropic only/OpenAI only)
- Enter your API keys
- Configure project settings

**Option C: Non-Interactive Setup**

```bash
adversarial init
```

Then manually edit:
- `.env` (add your API keys)
- `.adversarial/config.yml` (customize settings)

---

## Step 4: Verify Setup

```bash
adversarial check
```

Expected output:
```
🔍 Checking adversarial workflow setup...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ .env file found and loaded (2 variables)
✅ Git repository detected
✅ Aider installed (version X.Y.Z)
✅ ANTHROPIC_API_KEY configured (from .env) [sk-ant-a...xyzA]
✅ OPENAI_API_KEY configured (from .env) [sk-proj-...xyzA]
✅ .adversarial/config.yml valid
✅ All scripts executable
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ All checks passed! Your setup is ready.

Estimated cost per workflow: $0.02-0.10

Try it: adversarial quickstart
```

The check command now shows:
- Whether .env file was loaded and how many variables it contains
- The source of each API key: `(from .env)` or `(from environment)`
- A preview of your API key (first 8 + last 4 characters) for verification

**If checks fail**, follow the suggested fixes in the output.

### Comprehensive Health Check

For a more detailed system health check, use:

```bash
adversarial health
```

This provides comprehensive validation across 7 categories:
- **Configuration**: Checks `.adversarial/config.yml`, model settings, directories
- **Dependencies**: Git, Python, Aider, Bash versions and status
- **API Keys**: Format validation, source tracking (.env vs environment)
- **Agent Coordination**: Validates `.agent-context/`, JSON files, guide presence
- **Workflow Scripts**: Executable status, shebang validation, syntax checks
- **Tasks**: Directory structure, active task counts
- **Permissions**: `.env` security, script permissions, log directory access

**Health Score:** Shows system health as a percentage (>90% = healthy, 70-90% = degraded, <70% = critical)

**Useful flags:**
```bash
# Detailed diagnostics with fix commands
adversarial health --verbose

# Machine-readable JSON output
adversarial health --json
```

**Example output:**
```
🏥 Adversarial Workflow Health Check
======================================================================

Configuration:
  ✅ .adversarial/config.yml - Valid YAML
  ✅ evaluator_model: gpt-4o
  ✅ task_directory: tasks/ (exists)
  ✅ log_directory: .adversarial/logs/ (writable)

Dependencies:
  ✅ Git: 2.39.0 (working tree clean)
  ✅ Python: 3.11.0 (compatible)
  ✅ Aider: 0.86.1 (functional)

API Keys:
  ✅ OPENAI_API_KEY: Set (from .env) [sk-proj-...xyz]
  ✅ ANTHROPIC_API_KEY: Set (from .env) [sk-ant-...xyz]

Agent Coordination:
  ✅ .agent-context/ directory exists
  ✅ agent-handoffs.json - Valid JSON (8 agents)
  ✅ AGENT-SYSTEM-GUIDE.md - Present (33KB)

Workflow Scripts:
  ✅ evaluate_plan.sh - Executable, valid
  ✅ review_implementation.sh - Executable, valid
  ✅ validate_tests.sh - Executable, valid

Tasks:
  ✅ tasks/ directory exists
  ℹ️  5 active tasks in tasks/active/

Permissions:
  ✅ .env - Secure (600)
  ✅ All 3 scripts executable

======================================================================

✅ System is healthy! (Health: 95%)
   18 checks passed, 0 warnings, 0 errors

Ready to:
  • Evaluate task plans: adversarial evaluate <task-file>
  • Review implementations: adversarial review
  • Validate tests: adversarial validate
```

Use `adversarial health` periodically to ensure your system remains properly configured.

### Optional: Agent Coordination System

If you're using AI agents to work on this project, you can set up a comprehensive agent coordination system:

```bash
adversarial agent onboard
```

This interactive command will:
1. **Choose agent template** (optional - default: standard):
   - **Standard (8 roles)**: coordinator, feature-developer, api-developer, format-developer, test-runner, document-reviewer, security-reviewer, media-processor
   - **Minimal (3 roles)**: coordinator, developer, reviewer
   - **Custom URL**: Load from `https://raw.githubusercontent.com/your-org/your-template/main/agent-handoffs.json`
   - **Skip**: Set up manually later

2. **Create directory structure**:
   - `.agent-context/` - Agent coordination files (agent-handoffs.json, current-state.json, README.md, AGENT-SYSTEM-GUIDE.md)
   - `delegation/` - Task management (tasks/active/, tasks/completed/, handoffs/)
   - `agents/` - Agent tools and scripts

3. **Configure task management**:
   - Optionally migrate existing tasks from `tasks/` → `delegation/tasks/active/`
   - Updates `.adversarial/config.yml` to use new task directory
   - Creates backup before migration

**What's included:**
- **agent-handoffs.json** - Agent role definitions, current status, task assignments
- **current-state.json** - Project state tracking (version, tasks, metrics, git status)
- **AGENT-SYSTEM-GUIDE.md** - Comprehensive agent coordination guide (~34KB)
- **README.md** - Quick reference for the agent coordination system
- Agent roles, handoff protocols, task management patterns
- Production-ready methodology validated through real projects

**Pre-flight Check:**
Agents can run a comprehensive pre-flight check before starting:

```bash
./agents/tools/preflight-check.sh
```

This provides agents with:
- Complete project structure scan
- Prerequisites verification (Git, Python, Aider versions)
- Configuration validation (.adversarial/config.yml, .env security)
- Active work summary (tasks, git status)
- Prioritized recommendations

**Benefits for agents:**
- Eliminates 90%+ of discovery-phase mistakes
- Provides complete project context upfront
- Catches configuration issues before starting work
- Security checks (e.g., .env in .gitignore)
- Structured handoff tracking between different agent roles
- Clear task assignment and completion tracking

**Template Selection Guide:**
- **Use standard** if your project has specialized needs (API development, media processing, comprehensive testing)
- **Use minimal** if you're just getting started or want a simpler structure (3 roles covers 90% of use cases)
- **Use custom URL** if you have your own template repository or want to share templates across multiple projects
- **Skip** if you want to manually create the agent coordination files yourself

See `agents/tools/README.md` and `.agent-context/AGENT-SYSTEM-GUIDE.md` for full details.

---

## Step 5: Run Your First Workflow

### Method A: Use the Quickstart (Easiest)

```bash
adversarial quickstart
```

This creates an example task and walks you through the workflow.

### Method B: Manual Workflow (Full Control)

#### 5.1 Create a Task File

Create `tasks/my-first-feature.md`:

```markdown
# Task: Add User Profile Feature

**Type**: Feature
**Priority**: Medium

## Requirements
- Display user name and email
- Edit profile button
- Save changes to database

## Implementation Plan
1. Create ProfileView component
2. Add GET /api/profile endpoint
3. Add PUT /api/profile endpoint
4. Add profile form with validation
5. Add tests for profile endpoints

## Acceptance Criteria
- [ ] User can view their profile
- [ ] User can edit name and email
- [ ] Changes persist after page refresh
- [ ] All tests pass
```

#### 5.2 Evaluate the Plan (Phase 1)

```bash
adversarial evaluate tasks/my-first-feature.md
```

The AI reviewer will analyze your plan and either:
- ✅ **APPROVE**: Plan looks good, proceed with implementation
- ❌ **NEEDS_REVISION**: Suggests improvements to the plan

**If approved**, proceed to implementation.
**If revision needed**, update your task file based on feedback and run `evaluate` again.

#### 5.3 Implement the Feature (Phase 2)

Use your preferred method:
- **Claude Code**: Let Claude implement via the IDE
- **Cursor / Copilot**: Use AI coding assistants
- **Aider**: `aider --architect-mode src/profile.py`
- **Manual coding**: Write code yourself in your editor

The adversarial workflow is **tool-agnostic** - it reviews the result, not how you create it.

#### 5.4 Review Implementation (Phase 3)

Once you've made changes:

```bash
git add .
adversarial review
```

The AI reviewer will:
- Analyze your git diff
- Check for phantom work (code vs. TODOs)
- Verify implementation matches plan
- Catch bugs or issues

**Output:**
- ✅ **APPROVED**: Code looks good
- ❌ **NEEDS_REVISION**: Specific issues to fix

If revision needed, fix the issues and run `adversarial review` again.

#### 5.5 Validate with Tests (Phase 4)

```bash
adversarial validate "pytest tests/"
```

Replace `"pytest tests/"` with your test command:
- Python: `"pytest tests/"`
- JavaScript: `"npm test"`
- Go: `"go test ./..."`
- Rust: `"cargo test"`

The AI reviewer analyzes test results and provides feedback.

#### 5.6 Final Approval (Phase 5)

If all phases pass:

```bash
git commit -m "feat: Add user profile feature"
```

Include the workflow results in your commit message or PR description for audit trail.

---

## Common Workflows

### Workflow 1: Bug Fix

```bash
# 1. Create task
cat > tasks/fix-login-bug.md << 'EOF'
# Task: Fix Login Redirect Bug

## Problem
Users redirected to wrong page after login

## Fix Plan
1. Check redirect logic in auth.py
2. Update redirect URL to /dashboard
3. Add test for correct redirect

## Acceptance
- [ ] Users redirect to /dashboard after login
- [ ] Test coverage added
EOF

# 2. Get plan reviewed
adversarial evaluate tasks/fix-login-bug.md

# 3. Implement fix
vim src/auth.py  # or use your preferred method

# 4. Review implementation
git add src/auth.py tests/test_auth.py
adversarial review

# 5. Validate
adversarial validate "pytest tests/test_auth.py"

# 6. Commit
git commit -m "fix: Redirect to /dashboard after login"
```

### Workflow 2: Refactoring

```bash
# 1. Create refactoring task
cat > tasks/refactor-database.md << 'EOF'
# Task: Refactor Database Layer

## Goal
Extract database logic into separate module

## Plan
1. Create db/ module
2. Move query functions to db/queries.py
3. Update imports throughout codebase
4. Ensure all tests still pass

## Acceptance
- [ ] All database logic in db/ module
- [ ] No duplicate code
- [ ] All tests pass (no regressions)
EOF

# 2-6. Same workflow as above
```

### Workflow 3: With Aider for Implementation

```bash
# 1. Get plan approved
adversarial evaluate tasks/add-api-endpoint.md

# 2. Implement with aider
aider --architect-mode src/api.py

# ... use aider to implement ...

# 3. Independent review (different AI)
adversarial review  # Catches what aider might miss

# 4-6. Validate and commit
```

---

## Configuration

### Customize .adversarial/config.yml

```yaml
# Which AI model for reviews
evaluator_model: gpt-4o  # or claude-3-5-sonnet-20241022

# Where you keep tasks
task_directory: tasks/

# Your test command
test_command: pytest tests/ -v

# Where logs are stored
log_directory: .adversarial/logs/
```

### Environment Variables (Temporary Overrides)

```bash
# Use different model temporarily
export ADVERSARIAL_EVALUATOR_MODEL=gpt-4-turbo
adversarial evaluate tasks/my-task.md

# Use different test command
export ADVERSARIAL_TEST_COMMAND="npm run test:integration"
adversarial validate
```

---

## Tips & Best Practices

### 1. Keep Tasks Focused

✅ **Good**: Small, specific tasks
```
tasks/add-user-auth.md          # One feature
tasks/fix-validation-bug.md     # One bug
tasks/refactor-api-module.md    # One module
```

❌ **Bad**: Huge, vague tasks
```
tasks/improve-entire-app.md     # Too broad
```

### 2. Update Plans Based on Feedback

If the evaluator suggests improvements, **update your task file** before implementing.

### 3. Commit Often

Run `adversarial review` after small changes rather than huge batches.

Smaller diffs = Better reviews = Lower cost

### 4. Use Workflow for Iterations

If review fails:
```bash
# Fix the issues
vim src/myfile.py

# Review again
git add src/myfile.py
adversarial review
```

Iterate until approved.

### 5. Task Files are Documentation

Keep your task files - they serve as:
- Historical record of decisions
- Onboarding documentation
- Audit trail of changes

---

## Troubleshooting

### "Command not found: adversarial"

**Solution:**
```bash
# Check if installed
pip list | grep adversarial

# Use python -m instead
python -m adversarial_workflow --version

# Or add to PATH (bash/zsh)
export PATH="$HOME/.local/bin:$PATH"
```

### "ERROR: Not a git repository"

**Solution:**
```bash
git init
git add .
git commit -m "Initial commit"
adversarial init
```

### "ERROR: Aider not found"

**Solution:**
```bash
pip install aider-chat
aider --version
```

### "ERROR: No API keys configured"

**Solution:**
```bash
# Edit .env file
cp .env.example .env
vim .env  # Add your actual API keys

# Verify
adversarial check
```

### "WARNING: No git changes detected"

This means you haven't staged any changes. The review needs a git diff to analyze.

**Solution:**
```bash
git add .
adversarial review
```

### Workflow Scripts Not Executable

**Solution:**
```bash
chmod +x .adversarial/scripts/*.sh
```

Or just run `adversarial init` again to reset permissions.

---

## Cost Optimization

### Strategy 1: Use Cheaper Models

```yaml
# .adversarial/config.yml
evaluator_model: gpt-4o-mini  # 70% cheaper than gpt-4o
```

### Strategy 2: Review Only Changed Files

```bash
git add src/module.py tests/test_module.py  # Only these files
adversarial review  # Smaller diff = lower cost
```

### Strategy 3: Validate Subsets

```bash
# Instead of all tests
adversarial validate "pytest tests/test_module.py"
```

### Strategy 4: Skip Validation During Iteration

```bash
adversarial evaluate task.md    # Phase 1
# ... implement ...
adversarial review              # Phase 3 (cheap)
# Fix issues, review again
adversarial validate "pytest"   # Phase 4 (only when review passes)
```

**Typical Costs:**
- Plan evaluation: $0.01-0.03
- Code review: $0.005-0.02
- Test validation: $0.01-0.05
- **Total per workflow**: $0.02-0.10

---

## Next Steps

### Learn More

- **Full Documentation**: [README.md](README.md)
- **Usage Examples**: See [README.md#usage-examples](README.md#usage-examples)
- **For AI Agents**: [AGENT_INTEGRATION.md](AGENT_INTEGRATION.md)
- **Troubleshooting**: [README.md#troubleshooting](README.md#troubleshooting)

### Try Advanced Features

- **CI/CD Integration**: Run reviews in GitHub Actions
- **Monorepo Workflows**: Review specific packages
- **Custom Test Commands**: Adapt to any framework
- **Cost Optimization**: Advanced token-saving strategies

### Get Help

- **GitHub Issues**: https://github.com/movito/adversarial-workflow/issues
- **Documentation**: https://github.com/movito/adversarial-workflow

---

**Happy reviewing! 🎉**

Remember: Adversarial workflows help you catch issues early, save debugging time, and ship better code. The small API cost is worth the quality improvement.
