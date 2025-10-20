# Handoff: Integrate adversarial-workflow v0.3.0 into thematic-cuts

**From**: Feature Developer (adversarial-workflow v0.3.0 release)
**To**: Agent working on thematic-cuts
**Date**: 2025-10-17
**Context**: adversarial-workflow v0.3.0 is complete and ready to integrate back into thematic-cuts

---

## Background

The **adversarial-workflow** package was extracted from thematic-cuts to create a standalone, reusable tool for AI-powered code review. It has now reached **v0.3.0** with major new features and is ready to be integrated back into thematic-cuts for dogfooding and Phase 2 development.

**Key Achievement**: adversarial-workflow v0.3.0 introduces an **agent coordination system** that thematic-cuts already partially uses. This integration will:
1. Replace the old nested `adversarial-workflow/` directory with the v0.3.0 package
2. Leverage new features (health check, agent onboard command)
3. Continue using the existing agent coordination setup in thematic-cuts

---

## Current State

### adversarial-workflow v0.3.0 Status
- ✅ **Version**: 0.3.0 (released 2025-10-17)
- ✅ **Git tag**: v0.3.0 pushed to GitHub
- ✅ **Distribution**: Built (wheel + source in `dist/`)
- ⏸️ **PyPI**: Upload pending (see `RELEASE-NOTES-v0.3.0.md`)
- 📍 **Location**: `/Users/broadcaster_three/Github/adversarial-workflow/`

### thematic-cuts Current State
- **Version**: v1.0.2 (released 2025-10-10)
- **Phase**: Phase 1 Complete → Phase 2A: 25% complete (1/4 core tasks)
- **Agent coordination**: ✅ Already set up (`.agent-context/`, `delegation/`, `agents/`)
- **Active tasks**: 10+ tasks in `delegation/tasks/active/`
- **Old adversarial-workflow**: Nested directory at `adversarial-workflow/` (needs cleanup)
- 📍 **Location**: `/Users/broadcaster_three/Github/thematic-cuts/`

---

## Integration Goals

### 1. **Install adversarial-workflow v0.3.0 Package**

Replace the old nested directory approach with the proper package:

```bash
cd /Users/broadcaster_three/Github/thematic-cuts

# Install the v0.3.0 package locally (development mode)
pip install -e /Users/broadcaster_three/Github/adversarial-workflow/

# Or install from built wheel (faster)
pip install /Users/broadcaster_three/Github/adversarial-workflow/dist/adversarial_workflow-0.3.0-py3-none-any.whl
```

**Why this matters**: thematic-cuts can now use `adversarial` commands directly instead of managing scripts manually.

### 2. **Initialize Core Workflow** (if not already done)

Check if `.adversarial/` exists:

```bash
ls -la .adversarial/
```

If **NOT present**, initialize:

```bash
adversarial init --interactive
```

If **already present**, verify health:

```bash
adversarial health --verbose
```

Expected output: Health score >70%, scripts executable, API keys configured.

### 3. **Verify Agent Coordination Integration**

thematic-cuts already has `.agent-context/` and `delegation/` from the universal agent system. Verify it's compatible with v0.3.0:

```bash
adversarial health | grep -A 10 "Agent Coordination"
```

Expected output:
```
Agent Coordination:
  ✅ .agent-context/ directory exists
  ✅ agent-handoffs.json - Valid JSON (7 agents)
  ✅ current-state.json - Valid JSON
  ✅ AGENT-SYSTEM-GUIDE.md - Present (33KB)
```

If any checks fail:

```bash
# Refresh agent coordination templates
adversarial agent onboard
# Answer "n" to avoid overwriting existing setup
```

### 4. **Update Configuration** (if needed)

Check `.adversarial/config.yml`:

```bash
cat .adversarial/config.yml
```

Ensure `task_directory` points to the right location:

```yaml
evaluator_model: gpt-4o
task_directory: delegation/tasks/  # Should match your active tasks location
test_command: pytest tests/ -v
log_directory: .adversarial/logs/
artifacts_directory: .adversarial/artifacts/
```

If `task_directory` is wrong, update it:

```bash
# Edit config
vim .adversarial/config.yml

# Or use sed
sed -i '' 's|task_directory: tasks/|task_directory: delegation/tasks/|' .adversarial/config.yml
```

### 5. **Clean Up Old adversarial-workflow Directory**

The nested `adversarial-workflow/` directory is now obsolete:

```bash
# Check what's in it first
ls -la adversarial-workflow/

# If it's the old standalone repo (has .git/), remove it
rm -rf adversarial-workflow/

# Update .gitignore if needed
echo "adversarial-workflow/" >> .gitignore
```

**⚠️ Important**: Make sure this is the old standalone directory, NOT a symbolic link or critical dependency!

---

## Testing the Integration

### 1. **Version Check**

```bash
adversarial --version
```

Expected: `adversarial-workflow 0.3.0`

### 2. **Health Check**

```bash
adversarial health
```

Expected: Health score >70%, all critical checks passing.

### 3. **Evaluate a Task**

Pick an active task and run evaluation:

```bash
# List active tasks
ls delegation/tasks/active/

# Evaluate one
adversarial evaluate delegation/tasks/active/TASK-2025-006-semantic-parser-compound-instructions.md
```

Expected: Reviewer provides feedback, no errors.

### 4. **Test Agent Coordination**

Check agent handoffs:

```bash
cat .agent-context/agent-handoffs.json | jq '.coordinator.status'
```

Expected: JSON parses successfully, shows current agent status.

---

## New v0.3.0 Features You Can Use

### 1. **Health Check Command**

Comprehensive system diagnostics:

```bash
# Basic health check
adversarial health

# Detailed diagnostics
adversarial health --verbose

# JSON output (for CI/CD)
adversarial health --json > health-report.json
```

**Use cases**:
- Pre-flight checks before starting work
- Debugging setup issues
- CI/CD validation

### 2. **Agent Onboard Command**

Refresh or set up agent coordination:

```bash
# Full setup wizard
adversarial agent onboard

# Dry run (check what would be created)
adversarial agent onboard --path /tmp/test-project
```

**Use cases**:
- New contributors setting up their environment
- Refreshing templates after updates
- Migrating tasks to delegation/ structure

### 3. **Improved Error Messages**

v0.3.0 has enhanced error messages following the **ERROR/WHY/FIX/HELP** pattern. If something fails, the output will guide you to the solution.

### 4. **API Key Detection**

`adversarial check` now:
- Loads `.env` automatically
- Shows API key source (environment vs .env file)
- Displays partial key preview for verification
- Handles INFO-level messages properly (doesn't fail)

---

## Phase 2 Development with adversarial-workflow

### Recommended Workflow

For each Phase 2 task in thematic-cuts:

#### **Phase 1: Plan Evaluation**

```bash
# Create task file in delegation/tasks/active/
vim delegation/tasks/active/TASK-2025-XXX-my-feature.md

# Evaluate the plan
adversarial evaluate delegation/tasks/active/TASK-2025-XXX-my-feature.md
```

The Reviewer (GPT-4o) will:
- Check for completeness
- Identify edge cases
- Flag potential issues
- Suggest improvements

#### **Phase 2: Implementation**

Implement the feature using your preferred method:
- Claude Code (aider)
- Cursor
- Manual coding

Commit changes when done.

#### **Phase 3: Code Review**

```bash
# Review implementation against plan
adversarial review
```

The Reviewer will:
- Compare git diff to plan
- Check for phantom work (plan items not implemented)
- Verify edge cases were handled
- Validate tests cover acceptance criteria

#### **Phase 4: Test Validation**

```bash
# Validate tests objectively
adversarial validate pytest
```

The Reviewer will:
- Run tests
- Analyze failures objectively
- Identify root causes
- Recommend fixes (without implementing)

#### **Phase 5: Final Approval**

If all phases pass, commit and move to next task:

```bash
git add .
git commit -m "feat: Complete TASK-2025-XXX"
git mv delegation/tasks/active/TASK-2025-XXX-my-feature.md delegation/tasks/completed/
```

---

## Dogfooding Opportunities

thematic-cuts is the perfect testbed for adversarial-workflow. Here's what to watch for:

### 1. **Package Quality**

As you use adversarial-workflow v0.3.0:
- **File bugs**: https://github.com/movito/adversarial-workflow/issues
- **Suggest improvements**: UX friction, confusing messages, missing features
- **Test edge cases**: Large repos, complex diffs, non-standard setups

### 2. **Agent Coordination Integration**

thematic-cuts uses the agent coordination system that v0.3.0 now includes. Feedback areas:
- **agent-handoffs.json**: Is it easy to update? Clear structure?
- **current-state.json**: Useful for tracking project state?
- **AGENT-SYSTEM-GUIDE.md**: Comprehensive enough?
- **Health check**: Does it catch real issues?

### 3. **Documentation Gaps**

If you get confused or stuck:
- **Note it**: What was unclear?
- **Suggest fix**: What would have helped?
- **Contribute**: Submit PR or issue

### 4. **Performance Issues**

Watch for:
- **Slow commands**: Health check should be <2s, evaluate <30s
- **Token usage**: Check `.adversarial/logs/` for token costs
- **Hanging scripts**: Timeouts, unresponsive aider calls

---

## Common Issues & Solutions

### Issue: `adversarial: command not found`

**Solution**: Package not installed or not in PATH

```bash
# Check if installed
pip list | grep adversarial

# Install if missing
pip install /Users/broadcaster_three/Github/adversarial-workflow/dist/adversarial_workflow-0.3.0-py3-none-any.whl

# Or in development mode
pip install -e /Users/broadcaster_three/Github/adversarial-workflow/
```

### Issue: `Not initialized (.adversarial/config.yml not found)`

**Solution**: Run init command

```bash
adversarial init --interactive
```

### Issue: `No API keys configured`

**Solution**: Set up .env file

```bash
# Copy example
cp .env.example .env

# Edit with your keys
vim .env

# Verify
adversarial check
```

### Issue: `Task directory not found: delegation/tasks/`

**Solution**: Update config.yml

```bash
# Edit config
vim .adversarial/config.yml

# Set correct path
task_directory: delegation/tasks/
```

### Issue: Health check shows "degraded" (70-90%)

**Solution**: Check verbose output for specifics

```bash
adversarial health --verbose
```

Common causes:
- Missing evaluator_model in config (add `evaluator_model: gpt-4o`)
- .env file permissions too open (run `chmod 600 .env`)
- Log directory not created (auto-created on first use, not critical)

---

## File Cleanup Checklist

After integration, clean up obsolete files in thematic-cuts:

- [ ] Remove nested `adversarial-workflow/` directory (if it's the old repo)
- [ ] Verify `.adversarial/` uses v0.3.0 templates
- [ ] Update any hardcoded paths in scripts
- [ ] Check `.gitignore` includes `.adversarial/logs/` and `.adversarial/artifacts/`
- [ ] Update thematic-cuts `README.md` to reference adversarial-workflow v0.3.0

---

## Communication Channels

### For adversarial-workflow Issues
- **GitHub Issues**: https://github.com/movito/adversarial-workflow/issues
- **Source Code**: https://github.com/movito/adversarial-workflow
- **Package**: (PyPI pending upload - see RELEASE-NOTES-v0.3.0.md)

### For thematic-cuts Integration Issues
- **Context File**: `.agent-context/current-state.json`
- **Task Files**: `delegation/tasks/active/`
- **Agent Coordination**: `.agent-context/agent-handoffs.json`

---

## Success Criteria

Integration is successful when:

✅ **Core Functionality**
- [ ] `adversarial --version` shows 0.3.0
- [ ] `adversarial health` shows >70% health score
- [ ] `adversarial evaluate` successfully reviews a task
- [ ] `adversarial review` works with git diffs
- [ ] `adversarial validate pytest` runs tests objectively

✅ **Agent Coordination**
- [ ] `.agent-context/` structure intact
- [ ] `agent-handoffs.json` valid JSON with all agents
- [ ] `current-state.json` reflects project status
- [ ] Health check validates agent coordination

✅ **Workflow Integration**
- [ ] Tasks in `delegation/tasks/active/` accessible
- [ ] Config points to correct directories
- [ ] Logs written to `.adversarial/logs/`
- [ ] Scripts executable and functional

✅ **Dogfooding**
- [ ] Complete at least 1 Phase 2 task using the workflow
- [ ] Identify 2-3 improvement opportunities
- [ ] File feedback (issues or notes)

---

## Quick Start Commands

```bash
# Navigate to thematic-cuts
cd /Users/broadcaster_three/Github/thematic-cuts

# Install adversarial-workflow v0.3.0
pip install /Users/broadcaster_three/Github/adversarial-workflow/dist/adversarial_workflow-0.3.0-py3-none-any.whl

# Verify installation
adversarial --version

# Run health check
adversarial health --verbose

# Test with a task
adversarial evaluate delegation/tasks/active/TASK-2025-006-semantic-parser-compound-instructions.md

# Check agent coordination
cat .agent-context/agent-handoffs.json | jq '.meta'
```

---

## Next Steps

1. **Install v0.3.0** in thematic-cuts environment
2. **Run health check** to validate setup
3. **Pick a Phase 2A task** from `delegation/tasks/active/`
4. **Run full workflow** (evaluate → implement → review → validate)
5. **Document feedback** for adversarial-workflow improvements
6. **Continue Phase 2** development with confidence

---

**Questions?** Check:
- adversarial-workflow docs: `README.md`, `QUICK_START.md`, `docs/EXAMPLES.md`
- Health diagnostics: `adversarial health --verbose`
- Agent guide: `.agent-context/AGENT-SYSTEM-GUIDE.md`

**Ready to proceed!** 🚀

---

**Generated**: 2025-10-17 by Feature Developer Agent
**adversarial-workflow Version**: 0.3.0
**thematic-cuts Version**: 1.0.2 (Phase 2A in progress)
