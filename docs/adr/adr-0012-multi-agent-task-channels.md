# ADR-0012: Multi-Agent Task Channels

**Status**: Proposed

**Date**: 2025-01-22

**Deciders**: Fredrik, Claude

## Context

Our current workflow uses a single feature-developer agent working on tasks, following Linear's flow through folder-based status tracking. Tasks move through `1-backlog` → `2-todo` → `3-in-progress` → `4-in-review` → `5-done`, with automated review from BugBot and CodeRabbit on PR creation.

This approach works but has limitations:

1. **Single perspective**: One agent may miss issues that a differently-trained model would catch
2. **Sequential critique**: Verification happens only after implementation (at PR stage)
3. **Lost reasoning**: The agent's decision-making process isn't captured for later reference
4. **No internal debate**: Trade-offs aren't explicitly challenged before commitment

Research from Anthropic and projects like Miriad Systems suggest that multiple agents collaborating—especially from different model families—produce qualitatively different work: more robust, with fewer blind spots, and with emergent behaviors like genuine critique and disagreement.

We want to enable multi-agent collaboration while:

- Preserving our existing task/folder structure
- Maintaining compatibility with Linear
- Supporting both local models (via Mac Studio) and frontier models (via API)
- Capturing the reasoning and decisions for future reference
- Allowing future extension toward more autonomous agent interaction

## Decision

We will introduce **task channels**—shared conversation spaces where multiple agents collaborate on a task before PR creation.

### Core Architecture

Each active task (in `3-in-progress` or `4-in-review`) gains a corresponding channel:

```
tasks/
├── 3-in-progress/
│   └── TASK-123-implement-caching.md
├── .channels/
│   └── TASK-123/
│       ├── channel.md          # Conversation log
│       ├── briefing.md         # Current state summary
│       ├── checkpoints/        # Periodic extractions
│       └── adr-drafts/         # Proposed decisions
└── .channels-archive/          # Completed channels
```

### Agent Roles

Tasks specify which agents participate via configuration in the task file:

- **Architect** (Claude Opus 4.5): Proposes approaches, synthesizes discussion
- **Builder** (Codestral + Serena): Implements code — *note: requires validation that Codestral quality matches requirements*
- **Reviewer** (Codex + Serena): Internal code review
- **Devil's Advocate** (GPT-4o): Challenges assumptions
- **Custodian**: Manages channel lifecycle, checkpoints, and external integrations

### Workflow Integration

1. Task moves to `3-in-progress` → Channel created, agents spawned
2. Agents collaborate in channel (orchestrated via @mentions in Phase 1)
3. Internal review passes → PR created, task moves to `4-in-review`
4. External feedback (BugBot, CodeRabbit) flows back to channel
5. PR merged → Task moves to `5-done`, channel archived

### Lifecycle Management

Agents are long-running to avoid repeated Serena startup costs. The Custodian:

- Monitors context window usage per agent
- Triggers graceful handoffs when agents approach limits (~80%)
- Extracts checkpoints periodically and at retirement
- Promotes significant decisions to ADR drafts

### Phase 1: Orchestrated Mode

Initially, agents respond only when explicitly addressed (@mentioned). This is predictable and easier to debug. The Custodian or agents themselves direct the conversation flow.

### Future: Phase 2 Autonomous Mode

The architecture supports future extension where agents autonomously decide when to contribute. This requires only:

- Adding a `should_i_contribute()` evaluation to the agent loop
- Adjusting role prompts to grant autonomy
- Adding guardrails (cooldowns, rate limits, custodian intervention)

No structural changes to channels, checkpoints, or task integration required.

## Consequences

### Positive

- **Multiple perspectives**: Different models catch different issues before PR stage
- **Captured reasoning**: Channel logs preserve why decisions were made
- **ADR generation**: Architectural decisions emerge naturally from agent discussion
- **Flexible model mix**: Can use local models for bulk work, frontier models for critique
- **Incremental adoption**: Can enable per-task; existing single-agent workflow still works
- **Future-proof**: Path to autonomous collaboration without refactoring

### Negative

- **Increased complexity**: More moving parts than single-agent approach
- **Higher token costs**: Multiple agents consume more API credits
- **New failure modes**: Agent coordination issues, context management, handoff bugs
- **Learning curve**: Team must understand channel dynamics and agent roles

### Neutral

- **Storage growth**: Channel archives accumulate but are compressible text
- **Tooling investment**: Need to build Custodian and agent harness (one-time cost)
- **Workflow adjustment**: Human checkpoints shift from "review PR" to "approve approach + review PR"

## Open Questions

- [ ] Validate that Codestral/Devstral quality meets requirements for Builder role (may need Claude Opus 4.5 fallback)
- [ ] Determine optimal checkpoint frequency for different task types
- [ ] Establish token budget guidelines per task complexity level

## References

- [Miriad Systems](https://miriad.systems) — Multi-agent collaboration research by Sanity
- ADR-0001: Adversarial Workflow Pattern
- ADR-0005: Agent Coordination Extension Layer
- ADR-0008: Author-Evaluator Terminology
