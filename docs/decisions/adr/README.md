# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) documenting significant architectural and design decisions for adversarial-workflow.

## What are ADRs?

ADRs capture important architectural decisions along with their context and consequences. Each ADR describes:
- **Context**: The forces and factors influencing the decision
- **Decision**: What was decided and why
- **Consequences**: The positive, negative, and neutral implications

ADRs are **immutable** once accepted. If a decision changes, we create a new ADR that supersedes the old one, preserving the historical context.

## Format

We use [Michael Nygard's ADR format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions):

```markdown
# ADR-NNNN: Title

**Status**: Accepted | Deprecated | Superseded by ADR-XXXX

**Date**: YYYY-MM-DD

**Deciders**: [Decision makers]

## Context
[Forces, factors, and constraints influencing the decision]

## Decision
[What we decided and why]

## Consequences

### Positive
[What becomes easier or better]

### Negative
[What becomes harder or what we lose]

### Neutral
[Other implications]
```

## Numbering

ADRs use **four-digit sequential numbering** (0001, 0002, etc.) to support long-lived projects. Numbers are not reused, even if an ADR is superseded.

**Why four digits?** This project may last 20-30 years, and four digits provide clear ordering without ambiguity.

## Index

### Active ADRs

| ADR | Title | Date | Status |
|-----|-------|------|--------|
| [0001](0001-adversarial-workflow-pattern.md) | Adversarial Workflow Pattern | 2025-10-15 | ✅ Accepted |
| [0002](0002-bash-and-aider-foundation.md) | Bash and Aider Foundation | 2025-10-15 | ✅ Accepted |
| [0003](0003-multi-stage-workflow-design.md) | Multi-Stage Workflow Design | 2025-10-15 | ✅ Accepted |
| [0004](0004-template-based-initialization.md) | Template-Based Initialization | 2025-10-15 | ✅ Accepted |
| [0005](0005-agent-coordination-extension-layer.md) | Agent Coordination Extension Layer | 2025-10-17 | ✅ Accepted |
| [0006](0006-directory-structure-separation.md) | Directory Structure Separation | 2025-10-17 | ✅ Accepted |
| [0007](0007-yaml-env-configuration-pattern.md) | YAML + .env Configuration Pattern | 2025-10-15 | ✅ Accepted |
| [0008](0008-author-evaluator-terminology.md) | Author-Evaluator Terminology | 2025-10-19 | ✅ Accepted |
| [0009](0009-interactive-onboarding.md) | Interactive Onboarding | 2025-10-16 | ✅ Accepted |
| [0010](0010-platform-support-strategy.md) | Platform Support Strategy | 2025-10-15 | ✅ Accepted |
| [0011](0011-non-interactive-execution-support.md) | Non-Interactive Execution Support | 2025-10-30 | ✅ Accepted |

### Planned ADRs

None at this time. All architectural decisions have been documented.

Future ADRs will be added as new significant decisions are made.

### Superseded ADRs

None yet.

## Historical Decision Documents

Prior to adopting ADRs (2025-10-20), architectural decisions were documented in task files and planning documents. These are preserved in [docs/decisions/archive/](../archive/) for historical reference:

- `TASK-PACKAGING-001-PHASE-6-TERMINOLOGY-DECISION.md` - v0.2.0 terminology change to "Author/Reviewer" (superseded by ADR-0008)
- `TASK-TERMINOLOGY-001-REVERT-DECISION.md` - v0.3.2 terminology reversion (converted to ADR-0008)
- Various planning documents from v0.3.0 agent coordination development

## Process

### Creating a New ADR

1. **Identify the decision**: Is this an architectural decision that affects the project's structure, behavior, or future direction?

2. **Assign a number**: Use the next sequential number (check this index)

3. **Draft the ADR**: Use the format above, focusing on:
   - **Context**: What forces led to this decision?
   - **Decision**: What was decided and why?
   - **Consequences**: What are the trade-offs?

4. **Review**: Get feedback from project stakeholders

5. **Accept**: Mark status as "Accepted" and update this index

6. **Commit**: Include the ADR in your commit with appropriate message

### Superseding an ADR

When a decision changes:

1. **Create a new ADR** documenting the new decision
2. **Update the old ADR**: Change status to "Superseded by ADR-XXXX"
3. **Update this index**: Move the old ADR to "Superseded" section
4. **Preserve history**: Never delete or significantly modify accepted ADRs

### Example: ADR-0008 Supersedes v0.2.0 Decision

- v0.2.0 introduced "Author/Reviewer" terminology (documented in archive)
- v0.3.2 reverted to "Author/Evaluator" (documented in ADR-0008)
- Both decisions preserved with full rationale

## When to Write an ADR

**Write an ADR when:**
- ✅ Making architectural choices that affect project structure
- ✅ Choosing between competing technical approaches
- ✅ Establishing patterns or conventions
- ✅ Making trade-offs with significant implications
- ✅ Decisions that future developers will need to understand

**Don't write an ADR for:**
- ❌ Routine bug fixes
- ❌ Feature implementations following established patterns
- ❌ Temporary experimental code
- ❌ Configuration changes without architectural impact

## Related Documentation

- [TERMINOLOGY.md](../../TERMINOLOGY.md) - Official terminology definitions
- [CHANGELOG.md](../../../CHANGELOG.md) - Version history and changes
- [WORKFLOW_PHASES.md](../../WORKFLOW_PHASES.md) - Detailed workflow documentation
- [docs/decisions/archive/](../archive/) - Historical decision documents

## References

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - Michael Nygard
- [ADR GitHub Organization](https://adr.github.io/) - ADR tools and resources
- [Why Write ADRs](https://github.blog/2020-08-13-why-write-adrs/) - GitHub Engineering blog

---

**Maintainer**: planner agent
**Last Updated**: 2025-11-28
**ADR Count**: 11 active, 0 superseded, 0 planned
