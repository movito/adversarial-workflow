# Library Reference ADRs

This directory contains copies of Architecture Decision Records from **adversarial-evaluator-library** that are relevant to adversarial-workflow.

## Purpose

These ADRs are copied here for reference because:
1. They document decisions that affect how adversarial-workflow consumes evaluator definitions
2. They propose interfaces between the library and the workflow
3. They contain questions directed to the adversarial-workflow team

## Source Repository

**Repository**: [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library)
**ADR Location**: `docs/decisions/adr/`

## Referenced ADRs

| ADR | Title | Relevance to Workflow |
|-----|-------|----------------------|
| [ADR-0002](ADR-0002-evaluator-expansion-strategy.md) | Evaluator Expansion Strategy | Context for multi-provider support |
| [ADR-0003](ADR-0003-vertex-ai-expansion-strategy.md) | Vertex AI Expansion Strategy | Vertex AI routing requirements |
| [ADR-0004](ADR-0004-evaluator-definition-model-routing-separation.md) | Evaluator Definition / Model Routing Separation | **ACTION REQUIRED** - Proposes resolution layer for workflow |

## Key Decision: ADR-0004

**ADR-0004** proposes a layered architecture where:
- **Library** provides evaluator definitions and provider registry
- **Workflow** implements the resolution engine that maps requirements to API calls
- **Users** configure routing preferences in their projects

### Questions for Workflow Team (from ADR-0004)

1. Does adversarial-workflow currently have any model routing logic, or does it pass through the `model` field directly to litellm/aider?

2. What is the current configuration mechanism for users? Is there a `.adversarial/config.yml` pattern already?

3. Are there existing abstractions we should align with, or is this a greenfield addition?

4. What's the preferred timeline for implementing the resolution layer?

## Keeping in Sync

These copies should be updated when the source ADRs change significantly. Check the source repository for the latest versions.

**Last synced**: 2026-02-03

---

**Note**: These are reference copies. The authoritative versions live in adversarial-evaluator-library.
