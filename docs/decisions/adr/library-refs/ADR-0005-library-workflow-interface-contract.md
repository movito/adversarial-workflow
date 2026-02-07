# ADR-0005: Library-Workflow Interface Contract

**Status**: Accepted

**Date**: 2026-02-03

**Deciders**: adversarial-evaluator-library team, adversarial-workflow team

## Context

### Problem Statement

ADR-0004 established a layered architecture separating evaluator definitions (library) from model routing (workflow). This ADR formalizes the interface contract between the two projects to ensure:

1. Compatibility across versions
2. Clear ownership boundaries
3. Predictable behavior for users
4. Graceful migration path

### Cross-Team Agreement

This ADR was developed through cross-team coordination between:
- **adversarial-evaluator-library**: Provides evaluator definitions and provider registry
- **adversarial-workflow**: Implements resolution engine and execution

Both teams have approved this contract.

## Decision

We adopt the following interface contract between the library and workflow.

### 1. Registry Schema Specification

**Schema Version**: 1.0

**Location**: `providers/registry.yml` in adversarial-evaluator-library

```yaml
# providers/registry.yml
schema_version: "1.0"

providers:
  <family_name>:                    # e.g., "claude", "llama", "gpt"
    vendor: <string>                # e.g., "Anthropic", "Meta", "OpenAI"
    vendor_url: <url>               # Official vendor URL
    litellm_prefix: <string>        # Prefix for litellm model strings
    auth_env_default: <string|null> # Default env var for auth
    tiers:
      <tier_name>:                  # e.g., "opus", "sonnet", "haiku"
        capability_level: <int>     # 1-5, higher = more capable
        typical_use: <string>       # Human description
        models:
          - id: <string>            # Canonical model ID
            version: <string>       # Model version/generation
            context_window: <int>   # Max context in tokens
            released: <date>        # YYYY-MM-DD
            status: <enum>          # active | deprecated | sunset
            deprecated_date: <date> # Optional, when deprecated
            sunset_date: <date>     # Optional, when to be removed
            replacement: <string>   # Optional, successor model ID
            # Provider-specific IDs (optional)
            vertex_ai_id: <string>
            bedrock_id: <string>
            azure_id: <string>
            together_ai_id: <string>
            openrouter_id: <string>
```

**Field Requirements**:

| Field | Required | Description |
|-------|----------|-------------|
| `schema_version` | Yes | Registry schema version |
| `vendor` | Yes | Vendor name |
| `litellm_prefix` | Yes | Prefix for litellm (e.g., "anthropic/") |
| `auth_env_default` | No | Default auth env var (null if varies) |
| `capability_level` | Yes | 1-5 integer for tier comparison |
| `id` | Yes | Canonical model identifier |
| `status` | Yes | Lifecycle status |
| Provider IDs | No | Only if model available on that provider |

### 2. Evaluator Definition Schema

**Location**: `evaluators/<provider>/<name>/evaluator.yml`

```yaml
# Phase 2 format (target)
name: <string>                      # Unique evaluator name
description: <string>               # Human description
category: <string>                  # Evaluation category

# Model requirement (Phase 2)
model_requirement:
  family: <string>                  # e.g., "claude"
  tier: <string>                    # e.g., "opus"
  min_version: <string>             # e.g., "4"
  min_context: <int>                # Optional, minimum context needed

# Legacy fields (Phase 1 compatibility)
model: <string>                     # Direct model ID
api_key_env: <string>               # Direct auth env var

# Evaluation logic
timeout: <int>                      # Seconds
output_format: <string>             # e.g., "markdown"
prompt: |
  <evaluation prompt with {content} placeholder>
```

**Dual-Field Support** (Migration Period):

During Phase 1-2 transition, evaluators include BOTH:
- `model` + `api_key_env`: For workflow versions < 0.8.0
- `model_requirement`: For workflow versions >= 0.8.0

### 3. Resolution Algorithm

**Implemented by**: adversarial-workflow

> **Updated (ADV-0032)**: Explicit model field now takes priority over model_requirement.
> This allows library evaluators to specify current model IDs without waiting for
> workflow registry updates.

```
RESOLVE(evaluator, user_config, registry):

  # Step 1: Explicit model field takes priority (ADV-0032)
  # Allows evaluators to specify exact model IDs that stay current
  IF evaluator.model EXISTS:
    RETURN {
      model: evaluator.model,
      auth: evaluator.api_key_env
    }

  # Step 2: Resolve model_requirement via registry
  # Used for portable evaluators without specific model preference
  IF evaluator.model_requirement EXISTS:
    family = evaluator.model_requirement.family
    tier = evaluator.model_requirement.tier
    min_version = evaluator.model_requirement.min_version

    # Find matching model in registry
    model = registry.find(family, tier, min_version, status=active)
    IF model NOT FOUND:
      ERROR "No matching model for {family}/{tier} >= {min_version}"

    # Apply user routing
    routing = user_config.routing[family] OR user_config.routing.default
    IF routing NOT FOUND:
      ERROR "No routing configured for family '{family}'"

    RETURN resolve_endpoint(model, routing)

  # Step 3: Error
  ERROR "Evaluator has neither model nor model_requirement field"
```

### 4. User Routing Configuration

**Location**: `.adversarial/config.yml` (in user's project)

```yaml
# .adversarial/config.yml
resolution:
  strict: false                     # true = error if model_requirement fails

routing:
  # Per-family routing
  claude:
    method: direct                  # direct | vertex_ai | bedrock | openrouter
    api_key_env: ANTHROPIC_API_KEY  # Override default

  llama:
    method: vertex_ai
    project: my-gcp-project
    region: us-central1

  # Default for unconfigured families
  default:
    method: direct
```

**Supported Methods**:

| Method | Description | Required Config |
|--------|-------------|-----------------|
| `direct` | Direct vendor API | `api_key_env` |
| `vertex_ai` | Google Vertex AI | `project`, `region` (optional) |
| `bedrock` | AWS Bedrock | AWS credentials |
| `azure` | Azure OpenAI | `deployment`, `api_key_env` |
| `openrouter` | OpenRouter | `api_key_env` |
| `together_ai` | Together AI | `api_key_env` |

### 5. Version Compatibility

**Schema Versioning**: Semantic versioning for registry schema

| Change Type | Schema Version | Example |
|-------------|----------------|---------|
| New provider/model | Patch (1.0.x) | Add gpt-5.1 to registry |
| New optional field | Minor (1.x.0) | Add `cost_per_token` field |
| Breaking change | Major (x.0.0) | Rename `capability_level` |

**Compatibility Matrix**:

| Library Version | Registry Schema | Workflow Min Version |
|-----------------|-----------------|----------------------|
| 0.3.x | 1.0 | 0.8.0 |
| 0.4.x | 1.0 | 0.8.0 |
| 1.0.x | 1.0 | 0.8.0 |

**Handling Version Skew**:

```python
# Workflow implementation
SUPPORTED_SCHEMA_MAJOR = 1

def check_registry_compatibility(registry):
    schema_major = int(registry.schema_version.split('.')[0])

    if schema_major > SUPPORTED_SCHEMA_MAJOR:
        warn(f"Registry schema {registry.schema_version} newer than "
             f"supported ({SUPPORTED_SCHEMA_MAJOR}.x). "
             f"Update adversarial-workflow for full compatibility.")

    # Continue anyway - may still work
```

### 6. Registry Distribution

**Primary**: Bundled with adversarial-workflow at install time

**Updates**: Three mechanisms supported:
1. **Bundled**: Workflow ships with registry snapshot
2. **Fetch**: Optional fetch from library repo (with cache)
3. **Override**: User provides `registry-overrides.yml`

```yaml
# .adversarial/registry-overrides.yml (user's project)
providers:
  claude:
    tiers:
      opus:
        models:
          - id: claude-5-opus-20260601  # Not yet in library
            version: "5"
            context_window: 500000
            status: active
```

**Override Merge Rules**:
- Provider-level: Deep merge
- Model-level: Override by ID, or append if new ID
- User overrides take precedence

### 7. Lifecycle Status Behavior

| Status | Workflow Behavior |
|--------|-------------------|
| `active` | Normal operation |
| `deprecated` | Warn on use, suggest replacement |
| `sunset` | Error, require explicit override |

## Consequences

### Positive

- ✅ **Clear contract**: Both teams know exactly what to implement
- ✅ **Version safety**: Schema versioning prevents silent breakage
- ✅ **User flexibility**: Multiple routing methods supported
- ✅ **Graceful migration**: Dual-field support during transition
- ✅ **Override capability**: Users can extend without library release

### Negative

- ⚠️ **Coordination overhead**: Schema changes require cross-team agreement
- ⚠️ **Dual maintenance**: Migration period has two code paths
- ⚠️ **Registry sync**: Workflow bundled copy may lag behind library

### Neutral

- 📊 **Documentation burden**: Both repos must maintain compatibility docs
- 📊 **Testing complexity**: Integration tests span two repos

## Implementation Timeline

| Phase | Owner | Deliverable | Target |
|-------|-------|-------------|--------|
| 1 | Library | Publish `providers/registry.yml` | 2026-02-03 |
| 2 | Library | Update evaluators with `model_requirement` | 2026-02-05 |
| 3 | Workflow | ADV-0015: Resolution engine (Phase 1) | v0.8.0 |
| 4 | Workflow | Update ADV-0013: Include dual fields | v0.8.0 |
| 5 | Both | Integration testing | v0.8.0 |
| 6 | Library | Deprecate legacy-only evaluators | v1.0.0 |

## Related Decisions

- ADR-0004: Evaluator Definition / Model Routing Separation (architecture)
- ADR-0002: Evaluator Expansion Strategy (context)
- ADR-0003: Vertex AI Expansion Strategy (routing context)

## References

- [litellm Provider Documentation](https://docs.litellm.ai/docs/providers)
- [adversarial-workflow Repository](https://github.com/movito/adversarial-workflow)

## Revision History

- 2026-02-07: ADV-0032 - Updated resolution algorithm: explicit model field now takes priority over model_requirement
- 2026-02-03: Initial contract (Accepted by both teams)

---

**Template Version**: 1.1.0
