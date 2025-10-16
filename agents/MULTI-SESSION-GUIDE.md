# Multi-Session Agent Coordination Guide v1.0.0

## Problem Solved
This guide addresses the core workflow issue: **subagent calls blocking the coordinator thread** while maintaining project context across parallel sessions.

## Solution Overview
Enable coordinators to work in main thread while specialized agents operate in parallel sessions with full context synchronization.

## Workflow Models

### Model 1: Traditional (Blocking)
```
Main Thread (Coordinator)
├── @media-processor (blocks main thread)
│   ├── Work on precision fix
│   └── Return control to coordinator
└── Continue coordination work
```
**Problem**: Coordinator cannot work while agent is active.

### Model 2: Enhanced (Non-Blocking)
```
Main Thread (Coordinator)          Parallel Session (Agent)
├── Delegate TASK-P3-001          ┌── Launch media-processor
├── Continue coordination work    ├── 🎵 **MEDIA-PROCESSOR** | Working
├── Monitor via status updates   ├── Pull context, work on task
└── Receive completion notice     └── Push updates, complete task
```
**Solution**: Coordinator maintains oversight without thread blocking.

## Implementation Steps

### For Coordinators (Main Thread)

#### 1. Delegate Tasks (No Change)
```bash
# Continue using existing delegation
# Tasks automatically assigned in agent-handoffs.json
# No workflow changes required
```

### Usage Examples for Coordinators

#### 2. Monitor Progress (Enhanced)
```bash
# Quick status check (non-blocking)
./agents/tools/check-stale-status.sh

# Detailed monitoring
./agents/tools/sync-context.sh status
```

#### 3. Context Monitoring (New)
```bash
# Watch for updates in background
./agents/tools/sync-context.sh watch &
```

### For Agents (Parallel Sessions)

#### 1. Launch Agent in New Terminal
```bash
# Open new terminal/session
cd /path/to/thematic-cuts

# Launch specific agent
./agents/ca 3  # Media Processor example
```

#### 2. Sync Context Before Starting
```bash
# Agent should pull latest context
./agents/tools/sync-context.sh pull
```

#### 3. Work With Identity Headers
```
🎵 **MEDIA-PROCESSOR** | Task: TASK-P3-001 | Status: working

I'm now working on the precision fix. Let me examine the current implementation...
```

#### 4. Update Progress Regularly
```bash
# Major milestones
./agents/tools/update-status.sh media-processor working TASK-P3-001.md "Fixed float arithmetic"

# Context sync
./agents/tools/sync-context.sh push "Precision fix 75% complete"
```

#### 5. Complete and Report
```bash
# Final status update
./agents/tools/update-status.sh media-processor completed TASK-P3-001.md "100% test pass rate achieved"
```

## Context Synchronization Protocol

### Automatic Context Loading
Agent launchers automatically provide:
- Project brief and current state
- Agent-specific handoff information
- Recent session activity
- Task dependencies and priorities

### Manual Context Sync (Parallel Sessions)
```bash
# Before starting work
./agents/tools/sync-context.sh pull

# During work (major updates)
./agents/tools/sync-context.sh push "Updated API implementation"

# Monitoring (background)
./agents/tools/sync-context.sh watch
```

### Context Components
1. **Project State** (current-state.json)
   - Active phase and tasks
   - Completion status
   - Dependencies and blockers

2. **Agent Handoffs** (agent-handoffs.json)
   - Current assignments
   - Status and progress
   - Inter-agent dependencies

3. **Session Logs** (session-logs/)
   - Recent activity by agent
   - Status update history
   - Context sync events

## Identity Header Benefits

### Immediate Recognition
```
🔌 **API-DEVELOPER** | Task: TASK-P3-002 | Status: ready_pending_p3001
Ready to begin API implementation once precision fix is complete...

🎵 **MEDIA-PROCESSOR** | Task: TASK-P3-001 | Status: working
Running final validation tests. 90% pass rate achieved...
```

### Session Differentiation
Multiple terminals can show different agents working simultaneously:
```
Terminal 1: 📋 **COORDINATOR** | Monitoring progress
Terminal 2: 🎵 **MEDIA-PROCESSOR** | Implementing precision fix
Terminal 3: 🧪 **TEST-RUNNER** | Running validation suite
```

## Coordination Patterns

### Pattern 1: Sequential Handoff
```
Coordinator → Media Processor (P3-001) → API Developer (P3-002) → Test Runner (validation)
```

### Pattern 2: Parallel Development
```
Coordinator monitoring:
├── Media Processor (P3-001) - Critical path
├── Format Developer (P3-004) - Enhancement
└── Document Reviewer (P3-005) - Validation prep
```

### Pattern 3: Consultation Model
```
Main work: Media Processor (P3-001)
Consulting: Format Developer (precision requirements)
Validation: Test Runner (continuous testing)
```

## Best Practices

### For Efficient Coordination
1. **Delegate early** - Assign tasks before agents start
2. **Monitor passively** - Use status checks instead of direct queries
3. **Trust the process** - Agents report progress via status updates
4. **Intervene minimally** - Let agents complete assigned work

### For Agent Sessions
1. **Start with context sync** - Always pull before beginning work
2. **Update status regularly** - Use status update tools for milestones
3. **Push major updates** - Keep project state current
4. **Complete fully** - Ensure handoff to next agent is clean

### For Context Management
1. **Keep sessions short** - Avoid long-running parallel sessions
2. **Sync frequently** - Push updates at logical breakpoints
3. **Monitor conflicts** - Watch for simultaneous edits
4. **Document clearly** - Use descriptive sync messages

## Troubleshooting

### Context Out of Sync
```bash
# Check current sync status
./agents/tools/sync-context.sh status

# Pull latest updates
./agents/tools/sync-context.sh pull

# Check for stale agent status
./agents/tools/check-stale-status.sh
```

### Agent Status Confusion
```bash
# View all agent current status
cat .agent-context/agent-handoffs.json | jq '.[] | {focus: .current_focus, status: .status}'

# Update specific agent
./agents/tools/update-status.sh <agent-role> <new-status>
```

### Parallel Session Issues
1. **Always sync context** before making changes
2. **Use atomic updates** via status update tools
3. **Coordinate critical changes** through main coordinator
4. **Test in single session first** before going parallel

## Performance Considerations

### Token Efficiency
- Identity headers: **8-12 tokens** per response
- Context sync: **50-150 tokens** vs **500+** for full context reload
- Overall reduction: **~70%** in coordination overhead

### Session Management
- Parallel sessions maintain **independent context**
- Context sync provides **shared state awareness**
- Status monitoring enables **lightweight coordination**

## Migration Strategy

### Phase 1: Enhanced Single Session (Current)
- All agents show identity headers
- Improved status monitoring
- Better coordination visibility

### Phase 2: Parallel Session Support (Next)
- Context sync tools available
- Multi-session workflow documented
- Training for parallel coordination

### Phase 3: Advanced Coordination (Future)
- Automated conflict resolution
- Real-time session monitoring
- Advanced workflow orchestration

---

**Status**: ✅ Implementation Complete
**Validation**: Ready for TASK-P3-005 testing
**Production**: Awaiting test-runner validation
