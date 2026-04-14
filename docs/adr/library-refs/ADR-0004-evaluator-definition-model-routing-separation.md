# ADR-0004: Evaluator Definition and Model Routing Separation

**Status**: Proposed

**Date**: 2026-02-03

**Deciders**: planner, adversarial-workflow team, project maintainers

## Context

### Problem Statement

The adversarial-evaluator-library was created to decouple evaluator definitions from the execution engine (adversarial-workflow) and the consuming projects (agentive-starter-kit). However, the current design couples evaluator definitions to specific API access methods:

```yaml
# Current: WHAT and HOW are coupled
name: claude-adversarial
model: claude-4-opus-20260115      # ← Specific endpoint (HOW)
api_key_env: ANTHROPIC_API_KEY     # ← Specific auth method (HOW)
prompt: |                          # ← Evaluation logic (WHAT)
  You are a senior analyst...
```

This creates problems when users want to access the same models through different providers:

1. **Direct API users**: Want fine-grained control, direct billing relationships
2. **Vertex AI users**: Want unified GCP billing, simplified operations
3. **OpenRouter users**: Want single API key for multiple providers
4. **Corporate users**: May require specific routing for compliance

With the current design, we would need to duplicate evaluators for each access method (e.g., `claude-adversarial`, `vertex-claude-adversarial`, `openrouter-claude-adversarial`), which is unsustainable.

### Forces at Play

**Technical Requirements:**
- Evaluator definitions should be reusable across access methods
- Users should be able to choose their preferred provider routing
- The library should remain a "catalog" of evaluation logic, not API integration code

**Constraints:**
- Backwards compatibility with existing evaluator configs
- adversarial-workflow must be able to resolve definitions to actual API calls
- Different users have different provider relationships and preferences

**Assumptions:**
- adversarial-evaluator-library is a dependency of adversarial-workflow
- Users configure their provider preferences in their own projects
- The same evaluation logic (prompt, criteria) is valid regardless of how the model is accessed

## Decision

We adopt a **Layered Architecture** that separates evaluator definitions (WHAT) from model routing (HOW):

### Layer 1: Evaluator Definitions (This Library)

Evaluators define **requirements**, not implementations:

```yaml
# evaluators/claude-adversarial/evaluator.yml
name: claude-adversarial
description: Adversarial review using Claude Opus
category: adversarial

# Model REQUIREMENT (not endpoint)
model:
  family: claude           # Model family
  tier: opus               # Capability tier within family
  min_version: "4"         # Minimum model generation
  min_context: 128000      # Minimum context window (tokens)

# Evaluation logic (the actual value of this library)
timeout: 180
output_format: markdown
prompt: |
  You are a senior analyst conducting a rigorous adversarial review.
  Challenge every claim and identify weaknesses.
  ...
```

### Layer 2: Provider Registry (This Library)

A registry mapping model families to available models:

```yaml
# providers/registry.yml
providers:
  claude:
    vendor: Anthropic
    tiers:
      opus:
        - id: claude-4-opus-20260115
          version: "4"
          context: 200000
          released: 2026-01-15
        - id: claude-opus-4-5-20251101
          version: "4.5"
          context: 200000
          released: 2025-11-01
      sonnet:
        - id: claude-4-sonnet-20260115
          version: "4"
          context: 200000
      haiku:
        - id: claude-4-haiku-20260115
          version: "4"
          context: 200000

  llama:
    vendor: Meta
    tiers:
      large:
        - id: llama-4-maverick-17b-128e
          version: "4"
          context: 1000000
      medium:
        - id: llama-4-scout-17b-16e
          version: "4"
          context: 10000000

  # ... other families
```

### Layer 3: User Routing Config (User's Project)

Users configure how to access each model family:

```yaml
# .adversarial/config.yml (in user's project)

routing:
  # Power user: direct access where it matters
  claude:
    method: direct
    api_key_env: ANTHROPIC_API_KEY
  openai:
    method: direct
    api_key_env: OPENAI_API_KEY
  llama:
    method: vertex_ai
    project: my-gcp-project

  # Or: corporate user, everything via Vertex
  default:
    method: vertex_ai
    project: corp-gcp-project
    region: us-central1
```

### Layer 4: Resolution Engine (adversarial-workflow)

The workflow resolves evaluator requirements + user routing → actual API calls:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Evaluator     │     │  Provider        │     │  User Routing   │
│   Definition    │  +  │  Registry        │  +  │  Config         │
│   (Layer 1)     │     │  (Layer 2)       │     │  (Layer 3)      │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Resolution Engine    │
                    │   (adversarial-workflow)│
                    │                        │
                    │   Input:               │
                    │   - family: claude     │
                    │   - tier: opus         │
                    │   - min_version: 4     │
                    │                        │
                    │   + routing: vertex_ai │
                    │                        │
                    │   Output:              │
                    │   - endpoint: vertex.. │
                    │   - auth: GCP creds    │
                    └────────────────────────┘
```

### Supported Routing Methods

| Method | Description | Auth |
|--------|-------------|------|
| `direct` | Direct provider API | Provider API key |
| `vertex_ai` | Google Vertex AI Model Garden | GCP credentials |
| `openrouter` | OpenRouter aggregator | OpenRouter API key |
| `bedrock` | AWS Bedrock | AWS credentials |
| `azure` | Azure OpenAI | Azure credentials |

### Migration Path

**Phase 1: Add Model Requirements (Non-Breaking)**

Add `model_requirement` field alongside existing `model` field:

```yaml
# Backwards compatible
model: claude-4-opus-20260115      # Legacy (still works)
model_requirement:                  # New (preferred)
  family: claude
  tier: opus
  min_version: "4"
```

**Phase 2: Update adversarial-workflow**

Add resolution layer that:
1. Reads `model_requirement` if present
2. Falls back to `model` + `api_key_env` if not
3. Applies user routing config

**Phase 3: Deprecate Direct Model References**

Once ecosystem has migrated:
1. New evaluators use only `model_requirement`
2. Document migration guide
3. Eventually remove `model` and `api_key_env` fields

## Consequences

### Positive

- ✅ **Single evaluator definition serves all access methods**: No duplication
- ✅ **User choice**: Power users use direct, corporate users use Vertex AI
- ✅ **Clean separation of concerns**: Library = definitions, Workflow = execution
- ✅ **Future-proof**: New routing methods (Bedrock, Azure) don't require library changes
- ✅ **Loose coupling**: Library and workflow evolve independently

### Negative

- ⚠️ **Migration effort**: Existing evaluators need `model_requirement` added
- ⚠️ **Workflow complexity**: Resolution engine adds code to adversarial-workflow
- ⚠️ **Registry maintenance**: Provider registry needs updates when models change
- ⚠️ **Version sync**: Library and workflow versions must be compatible

### Neutral

- 📊 **ADR-0002/0003 scope change**: These become routing strategy ADRs, belonging more to workflow than library
- 📊 **Testing complexity**: Need to test evaluators against multiple routing methods

## Provider Registry Placement

The provider registry lives in **this library** (adversarial-evaluator-library) because:

1. **Cohesion**: Model metadata is closely related to evaluator definitions
2. **Single source of truth**: One place to update when models change
3. **Dependency direction**: Workflow depends on library, not vice versa

### Drawbacks of Registry in Library

| Drawback | Mitigation |
|----------|------------|
| **Library releases for model updates** | Semantic versioning: model additions are minor versions |
| **Workflow may need newer models** | Workflow can override/extend registry locally |
| **Tight coupling risk** | Registry is data-only (YAML), not code |
| **Stale model versions** | Automated checks for model deprecation |

### Registry Override Pattern

adversarial-workflow or user projects can extend the registry:

```yaml
# .adversarial/registry-overrides.yml
providers:
  claude:
    tiers:
      opus:
        - id: claude-5-opus-20260601    # New model not yet in library
          version: "5"
          context: 500000
```

## Related Decisions

- ADR-0002: Evaluator Expansion Strategy (becomes routing context)
- ADR-0003: Vertex AI Expansion Strategy (becomes routing context)
- ADR-0001: Evaluator Testing Strategy (testing applies to definitions)

## Open Questions (For adversarial-workflow Team)

1. Does adversarial-workflow currently have any model routing logic, or does it pass through the `model` field directly to litellm/aider?

2. What is the current configuration mechanism for users? Is there a `.adversarial/config.yml` pattern already?

3. Are there existing abstractions we should align with, or is this a greenfield addition?

4. What's the preferred timeline for implementing the resolution layer?

## References

- [adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library)
- [adversarial-workflow](https://github.com/movito/adversarial-workflow) (assumed)
- [litellm Provider Documentation](https://docs.litellm.ai/docs/providers)

## Revision History

- 2026-02-03: Initial proposal (Proposed)

---

**Template Version**: 1.1.0
