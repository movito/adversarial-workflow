# Handoff to Feature-Developer: TASK-SETUP-002

**Date**: 2025-10-16
**From**: Coordinator
**To**: Feature-Developer
**Priority**: HIGH (Priority #2 after TASK-SETUP-003 completion)

---

## Mission

Implement **TASK-SETUP-002: Pre-flight Check Script** - a comprehensive bash script that agents run before starting work to get a complete project snapshot.

---

## Context

### What Just Happened
- ✅ **TASK-SETUP-003 completed** (1.5 hours) - `adversarial check` now loads .env file correctly
- ✅ **5 setup improvement tasks created** from setup experience analysis
- ✅ **4 tasks approved**, 1 needs revision (TASK-SETUP-001)
- 📋 **Coordinator is discussing TASK-SETUP-001 with user** in parallel

### Why This Task Matters
During universal agent system integration (2025-10-16), the coordinator agent made several mistakes due to incomplete project discovery:
- Created structure without discovering existing `agents/` directory
- Didn't notice loose documentation files until after first commit
- Didn't check for aider installation before attempting to use it
- Made assumptions about directory structure instead of scanning first

**Impact**: This script eliminates 90%+ of discovery mistakes for agents by providing systematic pre-flight checks.

---

## Your Assignment

### Task File
**Location**: `delegation/tasks/active/TASK-SETUP-002-PREFLIGHT-CHECK-SCRIPT.md`

**Status**: APPROVED (2025-10-16 - Coordinator review based on pattern analysis)

**Estimated Effort**: 5 hours

### What You're Building

A bash script at `agents/tools/preflight-check.sh` that:

1. **Scans Project Structure**
   - Checks for `.agent-context/`, `agents/`, `delegation/`, `tasks/` directories
   - Detects loose documentation files in root
   - Reports on project organization

2. **Verifies Prerequisites**
   - Git (installed, version, clean working tree?)
   - Python (version, 3.8+ compatible?)
   - Aider (installed, version?)
   - Bash version (3.2 vs 4.x differences)

3. **Validates Configuration**
   - `.adversarial/config.yml` (exists, valid YAML?)
   - `.env` file (exists, in .gitignore?)
   - `.aider.conf.yml` (exists?)
   - Security check: .env in .gitignore?

4. **Reports Active Work**
   - Git status (uncommitted changes?)
   - Active task count
   - Stale agent status (>2 days old in agent-handoffs.json)

5. **Provides Recommendations**
   - Prioritized: HIGH > MEDIUM > LOW > INFO
   - Actionable (tell agent what to do, not just what's wrong)
   - Context-aware

### Key Requirements

**Must Have**:
- Script at `agents/tools/preflight-check.sh` (executable)
- All 4 scan categories working
- Color-coded output (✅ green, ⚠️ yellow, ❌ red, ℹ️ blue)
- Prioritized recommendations
- Appropriate exit codes (0/1/2)
- Completes in < 5 seconds
- Works on macOS and Linux

**Output Format Example**:
```
🔍 Project Pre-flight Check
==========================

Project Structure:
  ✅ .agent-context/ exists
  ✅ agents/ directory exists
  ⚠️  delegation/ not found (using tasks/ at root)
  ⚠️  Loose files in root: PHASE-1-SUMMARY.md

Prerequisites:
  ✅ Git: 2.39.0 (working tree clean)
  ✅ Python: 3.11.0
  ✅ Aider: 0.86.1
  ℹ️  Bash: 3.2.57 (macOS default)

Configuration:
  ✅ .adversarial/config.yml - Valid YAML
  ✅ .env file exists (2 API keys detected)
  ❌ .env NOT in .gitignore (SECURITY RISK!)

Active Work:
  ✅ Git working tree clean
  ℹ️  5 active tasks in delegation/tasks/active/

📋 Recommendations:
  1. HIGH: Add .env to .gitignore immediately
  2. MEDIUM: Organize loose root files into docs/
  3. INFO: Consider using delegation/ structure

✅ 8 checks passed, 2 warnings, 1 error
```

### Implementation Approach

The task file has **complete bash implementation** (~300 lines) in the Technical Approach section. You can:

1. **Use the provided implementation** (recommended - it's complete and tested conceptually)
2. **Adapt/improve it** (if you see better approaches)
3. **Implement from scratch** (if you prefer, following requirements)

### Files You'll Work With

**Primary**:
- `agents/tools/preflight-check.sh` (NEW - create this, ~300 lines)

**Secondary**:
- `agents/README.md` (UPDATE - add preflight-check usage)
- `QUICK_START.md` (UPDATE - add to "Before You Start" section)
- `.agent-context/AGENT-SYSTEM-GUIDE.md` (UPDATE - reference as recommended practice)

**Testing**:
- Test in this project (should pass with some warnings)
- Test in fresh git repo (should warn appropriately)
- Test with missing .gitignore entry (should catch security issue)
- Test with invalid YAML (should detect)

### Exit Codes

- `0`: All checks passed (warnings allowed)
- `1`: Critical errors found (e.g., no git, .env not in .gitignore)
- `2`: Major issues found (e.g., stale status, missing config)

### Integration Points

**Complements**:
- ✅ TASK-SETUP-003 (completed) - check command now loads .env
- 🔜 TASK-SETUP-001 (needs revision) - setup wizard will eventually run this
- 🔜 TASK-SETUP-004 (approved) - health check will use similar logic

**Uses**:
- Existing `.adversarial/config.yml` structure
- Existing `.agent-context/agent-handoffs.json` structure
- Standard bash tools (no external dependencies)

---

## Current Project State

### Recent Completion (TASK-SETUP-003)
The `adversarial check` command was just fixed to load .env files. You can reference this implementation in `adversarial_workflow/cli.py` lines 747-966 for patterns like:
- How to detect and load .env
- How to show source indicators
- How to format status messages

### Active Coordination
Coordinator is currently discussing TASK-SETUP-001 revision with user. This doesn't block your work on TASK-SETUP-002 (pure bash script, no integration conflicts).

### Project Structure
```
adversarial-workflow/
├── .agent-context/          # Agent coordination (exists)
│   ├── agent-handoffs.json  # Your status goes here
│   └── current-state.json
├── .adversarial/            # Workflow config (exists)
│   ├── config.yml
│   └── scripts/
├── agents/                  # Agent tools (exists)
│   ├── tools/              # Your script goes here
│   └── config/
├── delegation/              # Task structure (exists)
│   └── tasks/active/       # Your task file is here
└── adversarial_workflow/   # Python package (exists)
```

---

## Acceptance Criteria Checklist

Before marking complete, verify:

- [ ] `agents/tools/preflight-check.sh` exists and is executable (`chmod +x`)
- [ ] Script checks all 4 categories (Structure, Prerequisites, Config, Active Work)
- [ ] Color-coded output works (✅ ⚠️ ❌ ℹ️)
- [ ] Recommendations are prioritized and actionable
- [ ] Exit codes are correct (0/1/2)
- [ ] Completes in < 5 seconds
- [ ] Works on macOS (test in this project)
- [ ] Documentation updated (agents/README.md, QUICK_START.md)
- [ ] Tested in multiple scenarios:
  - [ ] Fully configured project (this one)
  - [ ] Fresh git repo (warnings)
  - [ ] .env without .gitignore entry (security error)
  - [ ] Invalid YAML config (detects error)

---

## When You're Done

### Update Your Status

Edit `.agent-context/agent-handoffs.json` feature-developer section:

```json
"current_focus": "✅ TASK-SETUP-002 COMPLETED - Pre-flight check script implemented",
"deliverables": [
  "✅ TASK-SETUP-002: Pre-flight Check Script - COMPLETED (2025-10-16)",
  "  - Created agents/tools/preflight-check.sh (~300 lines)",
  "  - Implements 4 scan categories with color-coded output",
  "  - Provides prioritized recommendations",
  "  - Tested on macOS in multiple scenarios",
  "  - Updated documentation (agents/README.md, QUICK_START.md)"
]
```

### Report Back

When complete, provide:
1. ✅ What was implemented
2. 🧪 Test results (show actual output)
3. 📄 Files modified
4. ⏱️ Time taken vs estimate (5 hours)
5. 🔜 Recommended next task (TASK-SETUP-005 or TASK-SETUP-004)

---

## Questions?

If you encounter issues or need clarification:
- Task file has complete implementation details
- TASK-SETUP-003 implementation (just completed) shows similar patterns
- Coordinator is available in main thread

---

## Timeline

**Estimated**: 5 hours
**Priority**: HIGH (Priority #2 in setup improvements sequence)
**Target**: v0.3.0 release

---

**Good luck! This script will save agents hours of discovery time going forward.** 🚀

---

**Coordinator Note**: Feature-developer will be launched manually via `./agents/ca`. This handoff document provides complete context for autonomous work.
