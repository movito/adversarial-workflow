# Agent Coordination Tools

## Overview
Comprehensive tools for agent status management, identity presentation, and multi-session coordination.

## Project Discovery Tools

### preflight-check.sh
Comprehensive pre-flight check that agents run before starting work.

**Usage:**
```bash
./agents/tools/preflight-check.sh          # Standard output
./agents/tools/preflight-check.sh --json   # JSON output (future)
```

**Scan Categories:**
1. **Project Structure**: Checks for `.agent-context/`, `agents/`, `delegation/`, `docs/`, loose files
2. **Prerequisites**: Verifies Git, Python, Aider, Bash versions
3. **Configuration**: Validates `.adversarial/config.yml`, `.env`, `.aider.conf.yml`
4. **Active Work**: Lists active tasks, checks agent status freshness

**Features:**
- Color-coded output (✅ pass, ⚠️ warning, ❌ error, ℹ️ info)
- Prioritized recommendations (HIGH > MEDIUM > LOW > INFO)
- Exit codes: 0 (pass), 1 (critical errors), 2 (major issues)
- Security checks (e.g., .env in .gitignore)
- Completes in < 5 seconds
- macOS and Linux compatible

**Example Output:**
```
🔍 Project Pre-flight Check
==========================

Project Structure:
  ✅ .agent-context/ exists
  ✅ agents/ directory exists
  ⚠️  Loose documentation files in root

Prerequisites:
  ✅ Git: 2.39.2 (working tree clean)
  ✅ Python: 3.13.7
  ✅ Aider: 0.86.1

Configuration:
  ✅ .adversarial/config.yml - Valid YAML
  ✅ .env file exists (3 API keys detected)
  ✅ .env in .gitignore

Active Work:
  ℹ️  5 active tasks in delegation/tasks/active/

📋 Recommendations:
  1. MEDIUM: Organize loose files into docs/ directory

Summary: ✅ 11 checks passed, ⚠️  1 warnings, ❌ 0 errors
```

## Status Management Tools

### update-status.sh
Standardized status update tool for all agents.

**Usage:**
```bash
./agents/tools/update-status.sh <agent-role> <status> [task-file] [notes]

# Examples:
./agents/tools/update-status.sh media-processor working TASK-P3-001.md "Fixing precision arithmetic"
./agents/tools/update-status.sh api-developer completed TASK-P3-002.md "API integration finished"
./agents/tools/update-status.sh test-runner blocked TASK-P3-001.md "Waiting for precision fix"
```

**Features:**
- Interactive prompts for additional context
- Automatic session logging
- JSON validation and backup
- Timestamp tracking

### check-stale-status.sh
Detects agents with outdated status information.

**Usage:**
```bash
./agents/tools/check-stale-status.sh
```

**Features:**
- Flags agents with >2 day old status
- Color-coded output (green=current, yellow=getting old, red=stale)
- Summary report
- Exit code indicates if action needed

## Context Synchronization Tools

### sync-context.sh (NEW)
Enables parallel session coordination with shared project state.

**Usage:**
```bash
./agents/tools/sync-context.sh <command> [options]

# Commands:
./agents/tools/sync-context.sh pull                    # Get latest project state
./agents/tools/sync-context.sh push "Updated API impl" # Push changes with message
./agents/tools/sync-context.sh status                  # Check sync status
./agents/tools/sync-context.sh watch                   # Monitor for changes
```

**Features:**
- Real-time project state synchronization
- Session activity monitoring
- Conflict detection and resolution
- Background change watching

## Identity System

### Agent Identity Headers (NEW)
All agents now display standardized identity headers:

```
🔌 **API-DEVELOPER** | Task: TASK-P3-002 | Status: ready_pending_p3001
🎵 **MEDIA-PROCESSOR** | Task: TASK-P3-001 | Status: working
🧪 **TEST-RUNNER** | Task: TASK-P3-005 | Status: ready_for_assignment
```

**Benefits:**
- Instant agent identification
- Current task visibility
- Status at a glance
- Multi-session coordination

## Session Logging

All status updates are automatically logged to:
`.agent-context/session-logs/<agent-role>-YYYYMMDD.log`

Format: `[TIMESTAMP] Status: <status> | Task: <file> | Notes: <notes>`

Context sync events logged to:
`.agent-context/session-logs/context-sync-YYYYMMDD.log`

## Multi-Session Workflow

### Single Session (Traditional)
```bash
./agents/ca 3                    # Launch agent (blocks main thread)
```

### Parallel Session (Enhanced)
```bash
# Terminal 1: Coordinator
./agents/tools/sync-context.sh watch &  # Background monitoring

# Terminal 2: Agent
./agents/ca 3                           # Launch agent
./agents/tools/preflight-check.sh       # Run pre-flight check FIRST
./agents/tools/sync-context.sh pull     # Sync context before work
# ... work with identity headers ...
./agents/tools/update-status.sh media-processor completed TASK-P3-001.md "Precision fix done"
```

## Integration with Agents

All agent system prompts now include:

1. **Identity Requirements**: Mandatory headers on every response
2. **Status Updates**: Use tools before ending sessions
3. **Context Awareness**: Read from agent-handoffs.json for current state
4. **Coordination Support**: Integration with sync tools

The coordinator agent has enhanced responsibilities:
- Monitor for stale status (>2 days old)
- Oversee multi-session coordination
- Maintain accurate project state
- Enable non-blocking agent oversight

## Workflow Comparison

### Before (Blocking)
```
Coordinator → @agent (blocks) → Work → Return → Continue
```

### After (Non-Blocking)
```
Coordinator (main) → Monitor status → Receive updates
Agent (parallel)   → Pull context → Work → Push updates
```

## Documentation

- **Agent Identity Standard**: `agents/AGENT-IDENTITY-STANDARD.md`
- **Multi-Session Guide**: `agents/MULTI-SESSION-GUIDE.md`
- **Tool Documentation**: This file

## Migration Path

✅ **Phase 1**: Identity headers active (immediate benefit)
🔄 **Phase 2**: Multi-session coordination available (opt-in)
⏳ **Phase 3**: Advanced workflow patterns (future enhancement)
