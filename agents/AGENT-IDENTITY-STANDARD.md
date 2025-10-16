# Agent Identity Presentation Standard v1.0.0

## Overview
Standardized identity system for agent coordination in multi-session workflows.

## Identity Header Format

### Standard Pattern
```
🎯 **[AGENT-TYPE]** | Task: [CURRENT-TASK] | Status: [CURRENT-STATUS]
```

### Agent-Specific Headers

| Agent Type | Icon | Header Format |
|------------|------|---------------|
| API Developer | 🔌 | `🔌 **API-DEVELOPER** \| Task: [task] \| Status: [status]` |
| Format Developer | 📝 | `📝 **FORMAT-DEVELOPER** \| Task: [task] \| Status: [status]` |
| Media Processor | 🎵 | `🎵 **MEDIA-PROCESSOR** \| Task: [task] \| Status: [status]` |
| Test Runner | 🧪 | `🧪 **TEST-RUNNER** \| Task: [task] \| Status: [status]` |
| Coordinator | 📋 | `📋 **COORDINATOR** \| Task: [task] \| Status: [status]` |
| Document Reviewer | 📖 | `📖 **DOCUMENT-REVIEWER** \| Task: [task] \| Status: [status]` |

## Implementation Requirements

### 1. Mandatory Display
- **Every agent response** must begin with identity header
- **No exceptions** - applies to all response types
- **Dynamic content** - task and status from actual agent-handoffs.json

### 2. Content Sources
- **Task**: Extract from `current_focus` or `task_file` in agent-handoffs.json
- **Status**: Use exact `status` field value from agent-handoffs.json
- **Real-time**: Read current state, don't cache values

### 3. Token Efficiency
- Headers average **8-12 tokens** per response
- **Minimal impact** on conversation context
- **High value** for coordination visibility

## Status Values

### Standard Status Types
- `urgent` - Critical blocker requiring immediate attention
- `working` - Actively implementing assigned task
- `ready_pending_X` - Ready to start, waiting for dependency
- `blocked` - Cannot proceed due to external dependency
- `available` - Ready for new task assignment
- `completed` - Task finished successfully
- `coordinating` - Managing project coordination (coordinator only)

### Status Color Coding (Terminal Display)
- 🔴 `urgent` - Critical path blocker
- 🟡 `working` - Active development
- 🟢 `available` - Ready for assignment
- ⚪ `ready_pending_X` - Waiting for dependency
- 🔵 `coordinating` - Project management

## Context Synchronization

### Multi-Session Support
Agents operating in parallel sessions must:

1. **Pull context** before starting work:
   ```bash
   ./agents/tools/sync-context.sh pull
   ```

2. **Push updates** when completing milestones:
   ```bash
   ./agents/tools/sync-context.sh push "Completed API integration"
   ```

3. **Monitor changes** for coordination:
   ```bash
   ./agents/tools/sync-context.sh watch
   ```

### Conflict Resolution
- **Last-write-wins** for non-critical updates
- **Explicit coordination** for critical path changes
- **Status update tools** handle atomic updates

## Benefits

### For Coordinators
- **Instant visibility** into active agent work
- **No thread blocking** for status checks
- **Clear task assignment** tracking
- **Multi-session awareness**

### For Agents
- **Session identity** clear in all contexts
- **Context preservation** across parallel work
- **Coordination awareness** without manual sync
- **Professional presentation** consistency

## Example Usage

### Single Session
```
User: @media-processor start working on precision fix

🎵 **MEDIA-PROCESSOR** | Task: TASK-P3-001 | Status: working
I'm starting the precision fix implementation. Let me examine the current timecode utilities...
```

### Parallel Session
```
Terminal 1 (Coordinator):
📋 **COORDINATOR** | Task: Phase-3-Coordination | Status: coordinating
Monitoring progress on TASK-P3-001...

Terminal 2 (Media Processor):
🎵 **MEDIA-PROCESSOR** | Task: TASK-P3-001 | Status: working
Fixed float arithmetic in _get_rate() function. Running tests...
```

### Context Sync Example
```bash
# Agent in parallel session pulls latest context
$ ./agents/tools/sync-context.sh pull

🔄 Pulling latest project context...
Project Phase: quality_first_development_phase_3_precision_fix
Active Tasks:
  - TASK-P3-001
  - TASK-P3-004
  - TASK-P3-005

Agent Status Summary:
  media-processor: working - URGENT - Core Precision Engine Fix - Phase 3.1
  format-developer: implementing - Assigned TASK-P3-004: Agent Identity System Implementation

✓ Context synchronized
```

## Implementation Checklist

### Phase 1: Core Identity ✅
- [x] Updated agent system prompts with identity requirements
- [x] Defined standard header format
- [x] Implemented dynamic task/status extraction
- [x] Ensured token efficiency

### Phase 2: Context Sync ✅
- [x] Created sync-context.sh tool
- [x] Implemented pull/push/status/watch commands
- [x] Designed conflict resolution approach
- [x] Added session logging integration

### Phase 3: Documentation ✅
- [x] Created identity presentation standard
- [x] Documented multi-session workflow
- [x] Provided usage examples
- [x] Established validation criteria

## Testing Requirements

The identity system must pass validation by test-runner including:
- Header consistency across all agents
- Dynamic content accuracy
- Token overhead measurement
- Multi-session coordination testing
- No regression in agent functionality

## Migration Path

Existing workflows remain compatible:
- Identity headers add value without breaking changes
- Context sync is opt-in for parallel sessions
- Single session workflows work unchanged
- Status update tools integrate seamlessly

---

**Implementation Status**: ✅ Complete
**Next Step**: Validation by test-runner (TASK-P3-005)
