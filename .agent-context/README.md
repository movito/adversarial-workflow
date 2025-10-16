# Agent Context Directory

**Version**: 1.0.0
**Purpose**: Universal agent coordination system for adversarial-workflow project
**Created**: 2025-10-16

---

## Overview

This directory contains the coordination infrastructure for the multi-agent development system used in the adversarial-workflow project. It provides a lightweight, token-efficient method for agents to maintain context, coordinate work, and track project state.

---

## Directory Structure

```
.agent-context/
├── README.md                    # This file
├── agent-handoffs.json          # Central agent status and coordination
├── current-state.json           # Project state snapshot
└── session-logs/                # Agent activity logs
    ├── coordinator-YYYYMMDD.log
    ├── test-runner-YYYYMMDD.log
    └── ...
```

---

## Core Files

### agent-handoffs.json

**Purpose**: Central coordination file tracking all agent status, current work, and blockers.

**Structure**:
- `meta`: Project metadata and last check timestamps
- `<agent-role>`: Individual agent entries with:
  - `current_focus`: What the agent is working on
  - `status`: available | working | blocked | completed | pending
  - `last_updated`: ISO 8601 timestamp (UTC)
  - `task_file`: Path to active task file
  - `technical_notes`: Implementation details
  - `completed_work`: Array of completed items
  - `blockers`: Array of blocking issues

**Agent Roles**:
- `coordinator` - Task management, project planning, documentation maintenance
- `api-developer` - API integration and backend systems
- `format-developer` - File format and data export systems
- `media-processor` - Media processing and validation
- `test-runner` - Testing and quality assurance
- `document-reviewer` - Documentation review and quality
- `feature-developer` - Feature implementation and code development

**Update Protocol**:
All agents MUST update their status before ending their session:
```bash
agents/tools/update-status.sh <agent-role> <status> [task-file] [notes]
```

**Staleness Monitoring**:
The coordinator agent monitors for stale updates (>2 days old):
```bash
agents/tools/check-stale-status.sh
```

---

### current-state.json

**Purpose**: Comprehensive project state snapshot for quick onboarding and context.

**Contains**:
- Project metadata (version, type, repository)
- Development phase information
- Active tasks summary with status
- Project metrics (lines of code, test coverage)
- Technology stack
- Agent system status
- Git status
- Key documentation references
- Next steps (immediate, short-term, long-term)

**Update Frequency**: Updated by coordinator when project state changes significantly.

---

### session-logs/

**Purpose**: Daily activity logs for each agent, automatically created by update-status.sh.

**Format**: `<agent-role>-YYYYMMDD.log`

**Entry Format**:
```
[YYYY-MM-DD HH:MM:SS UTC] Status: <status> | Task: <task-file> | Notes: <notes>
```

**Retention**: Logs are kept for historical reference. Clean up old logs as needed.

---

## Agent Identity Protocol

All agents MUST start every response with an identity header:

```
<icon> <AGENT-NAME> | [current-task] | [current-status]
```

**Examples**:
- `📋 COORDINATOR | Project Onboarding | Working`
- `🧪 TEST-RUNNER | Phase 4 Testing | Available`
- `📖 DOCUMENT-REVIEWER | Terminology Audit | Blocked`

This ensures:
- Clear agent identification in conversation history
- Immediate status visibility
- Token-efficient context (50-150 tokens vs 500+ for full context)

---

## Agent Coordination Tools

Located in `agents/tools/`:

### check-stale-status.sh

Monitors agent-handoffs.json for outdated status (>2 days):
```bash
./agents/tools/check-stale-status.sh
```

**Output**:
- ✓ Current agents (updated recently)
- ⚠ Getting old (1-2 days)
- 🚨 Stale agents (>2 days)

**Exit Codes**:
- 0: All agents current
- 1: Stale agents detected

---

### update-status.sh

Standardized way for agents to update their status:
```bash
./agents/tools/update-status.sh <agent-role> <status> [task-file] [notes]
```

**Features**:
- Updates agent-handoffs.json
- Creates session log entry
- Interactive prompts for details
- Automatic backup of handoffs file
- Handles blocked status with dependency tracking

**Example**:
```bash
./agents/tools/update-status.sh test-runner working TASK-PACKAGING-001-PHASE-4-TEST-PLAN.md "Running macOS tests"
```

---

### sync-context.sh

Synchronizes context between different development environments (if needed).

---

## Usage Examples

### Starting Work as an Agent

1. Check current project state:
   ```bash
   cat .agent-context/current-state.json
   ```

2. Check agent status:
   ```bash
   cat .agent-context/agent-handoffs.json | jq '.test-runner'
   ```

3. Start your response with identity:
   ```
   🧪 TEST-RUNNER | Phase 4 Testing | Starting Work
   ```

4. Do your work...

5. Update status before ending:
   ```bash
   ./agents/tools/update-status.sh test-runner completed TASK-PACKAGING-001-PHASE-4-TEST-PLAN.md "All 47 tests passed"
   ```

---

### Coordinator Monitoring

Check for stale agents daily:
```bash
./agents/tools/check-stale-status.sh
```

Update project state when major changes occur:
```bash
# Edit current-state.json manually or via automation
# Update meta.last_checked and updated_by fields
```

---

## Integration with Existing Systems

### Delegation System (tasks/)

The `.agent-context/` system COMPLEMENTS the existing `tasks/` directory:

- **tasks/active/**: Detailed task specifications
- **tasks/completed/**: Task archives
- **tasks/analysis/**: Strategic planning
- **.agent-context/**: Real-time agent coordination

**Workflow**:
1. Tasks are defined in `tasks/active/`
2. Agents reference task files in their status
3. Agent coordination happens via `.agent-context/`
4. Completed tasks are archived to `tasks/completed/`

**DO NOT**:
- Duplicate task definitions in both systems
- Create new coordination directories outside `.agent-context/`
- Modify task status in both places (use task files as source of truth)

---

### Agent Launcher Scripts (agents/)

Agent launcher scripts in `agents/` use `.agent-context/` for initialization:

```bash
# Example from universal-agent-launcher.sh
CONTEXT_DIR="$PROJECT_ROOT/.agent-context"
HANDOFFS_FILE="$CONTEXT_DIR/agent-handoffs.json"

# Load current agent status
AGENT_STATUS=$(cat "$HANDOFFS_FILE" | jq -r ".$AGENT_ROLE.status")
```

---

## Token Optimization

The `.agent-context/` system is designed for token efficiency:

**Traditional Approach** (500+ tokens):
- Full project context repeated in every prompt
- Complete task history
- Verbose status updates

**Agent Context Approach** (50-150 tokens):
- Identity header: 10-20 tokens
- Quick context check via JSON: 30-50 tokens
- Status update: 10-30 tokens
- **Total**: 50-100 tokens per interaction

**Savings**: 80-90% token reduction for context management

---

## Maintenance

### Regular Tasks

**Daily** (Coordinator):
- Run `check-stale-status.sh`
- Review new session logs
- Update agent-handoffs.json for long-running tasks

**Weekly** (Coordinator):
- Update current-state.json with progress
- Archive old session logs (>30 days)
- Review and close completed tasks

**Monthly** (Coordinator):
- Audit agent-handoffs.json for accuracy
- Clean up stale entries
- Update documentation if workflows change

---

### Backup and Recovery

**Automatic Backups**:
- `update-status.sh` creates timestamped backups before modifications
- Location: `.agent-context/agent-handoffs.json.backup.YYYYMMDD_HHMMSS`

**Manual Backup**:
```bash
cp .agent-context/agent-handoffs.json .agent-context/agent-handoffs.json.backup.$(date +%Y%m%d)
```

**Recovery**:
```bash
cp .agent-context/agent-handoffs.json.backup.YYYYMMDD_HHMMSS .agent-context/agent-handoffs.json
```

---

## Troubleshooting

### Agent status not updating

**Symptom**: agent-handoffs.json shows old timestamps

**Cause**: Agent forgot to update status before ending session

**Fix**:
```bash
./agents/tools/update-status.sh <agent-role> <correct-status> [task-file] [notes]
```

---

### JSON syntax errors

**Symptom**: Tools fail with JSON parse errors

**Cause**: Manual edits broke JSON syntax

**Fix**:
```bash
# Validate JSON
cat .agent-context/agent-handoffs.json | jq .

# If invalid, restore from backup
cp .agent-context/agent-handoffs.json.backup.* .agent-context/agent-handoffs.json
```

---

### Stale status warnings

**Symptom**: `check-stale-status.sh` reports stale agents

**Cause**: Agent hasn't updated status in >2 days

**Fix**:
1. Review agent's last known task
2. Manually update status if agent is no longer active
3. Reassign task if needed

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-16 | Initial .agent-context system setup |

---

## References

- **Agent Role Definitions**: `agents/config/agent-roles.json`
- **Agent Launchers**: `agents/*.sh`
- **Task Management**: `tasks/active/`, `tasks/completed/`
- **Project Documentation**: `README.md`, `docs/`

---

**Last Updated**: 2025-10-16
**Maintained By**: coordinator
**Status**: Active
