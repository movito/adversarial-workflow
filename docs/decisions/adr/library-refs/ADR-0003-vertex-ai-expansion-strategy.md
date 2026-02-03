# ADR-0003: Vertex AI Expansion Strategy

**Status**: Proposed

**Date**: 2026-02-03

**Deciders**: planner, project maintainers

## Context

### Problem Statement

ADR-0002 established a multi-provider expansion strategy with phases for adding evaluators from Cohere, DeepSeek, and other providers. However, practical constraints emerged:

1. **Signup friction**: Each new provider requires separate account creation, billing setup, and API key management
2. **Economic viability**: Some providers (e.g., Cohere) proved not economically feasible
3. **Enterprise requirements**: Some providers require enterprise-tier commitments with sales processes

We need an alternative approach that:
- Minimizes signup friction (easy developer access)
- Provides access to multiple model families
- Maintains pay-as-you-go economics
- Avoids enterprise-tier requirements

### Forces at Play

**Technical Requirements:**
- Access to code-specialized models for code-review diversity
- Access to reasoning models for deep-reasoning gaps
- Unified API pattern for maintainability
- Support for pinned model versions

**Constraints:**
- Single Google Cloud account already exists (for Gemini evaluators)
- Avoid multiple provider signups
- Pay-as-you-go pricing only
- No enterprise sales processes

**Assumptions:**
- Google Cloud access via `GEMINI_API_KEY` is already configured
- Vertex AI Model Garden provides comparable pricing to direct APIs
- Partner models on Vertex AI maintain similar capabilities to direct access

## Decision

We adopt a **Vertex AI Model Garden** strategy for Phase 2/3 expansion, accessing multiple model providers through a single Google Cloud account.

### Principle 1: Single Provider Gateway

Use Vertex AI as a unified gateway to access models from:
- **Google**: Gemini (already using)
- **Meta**: Llama 4 family
- **Mistral**: Codestral 2, Medium 3, Small 3.1
- **Anthropic**: Claude family (optional, for unified billing)

This eliminates the need for separate signups with DeepSeek, Together AI, Groq, or other providers.

### Principle 2: Priority on Code and Reasoning

Focus Phase 2/3 on the identified gaps:

**Code-Review Diversity (Priority 1):**
- Codestral 2 (Mistral's latest code model)
- Llama 4 Maverick (multimodal, strong code reasoning)

**Deep-Reasoning Gaps (Priority 2):**
- Llama 4 Scout (10M context, retrieval + reasoning)
- Mistral Medium 3 (long document analysis, math reasoning)

### Principle 3: Vertex AI API Pattern

All Vertex AI evaluators use a consistent configuration pattern:

```yaml
# Vertex AI evaluator pattern
name: llama4-code
description: Code review using Llama 4 Maverick via Vertex AI
model: vertex_ai/llama-4-maverick-17b-128e-instruct-maas
api_key_env: GOOGLE_APPLICATION_CREDENTIALS
output_suffix: -llama4-code.md
timeout: 180
```

Authentication options:
1. Service account JSON (`GOOGLE_APPLICATION_CREDENTIALS`)
2. Application Default Credentials (`gcloud auth application-default login`)
3. Workload Identity (for cloud deployments)

### Implementation: Target State

**Phase 2: Code-Review & Reasoning via Vertex AI**

| Evaluator | Provider | Model | Category | Rationale |
|-----------|----------|-------|----------|-----------|
| `codestral-v2` | Mistral | codestral-2 | code-review | Latest code-specialized model |
| `llama4-code` | Meta | llama-4-maverick | code-review | Multimodal, 400B MoE |
| `llama4-reasoning` | Meta | llama-4-scout | deep-reasoning | 10M context, retrieval focus |
| `mistral-medium3` | Mistral | mistral-medium-3 | deep-reasoning | Long docs, math reasoning |

**Phase 3: Optional Additions**

| Evaluator | Provider | Model | Category | Rationale |
|-----------|----------|-------|----------|-----------|
| `mistral-small31` | Mistral | mistral-small-3-1-25-03 | quick-check | Fast, multimodal, 128K |
| `vertex-claude` | Anthropic | claude-opus-4-5 | adversarial | Unified billing option |

### Target Coverage Matrix

After Phase 2 implementation:

| Category | Providers | New via Vertex AI |
|----------|-----------|-------------------|
| quick-check | OpenAI, Anthropic, Google, Mistral | (Mistral Small 3.1 optional) |
| code-review | OpenAI, Anthropic, Google, Mistral | +Codestral 2, +Llama 4 Maverick |
| deep-reasoning | OpenAI, Google | +Llama 4 Scout, +Mistral Medium 3 |
| adversarial | OpenAI, Anthropic | (no change) |
| cognitive-diversity | OpenAI, Mistral | (no change) |
| knowledge-synthesis | OpenAI, Google | (no change) |

### Naming Convention

```
{model-family}-{specialty}[-vertex]
```

Examples:
- `llama4-code` (Llama 4 for code review)
- `codestral-v2` (Codestral version 2)
- `mistral-medium3` (Mistral Medium 3)

The `-vertex` suffix is optional since the model field makes the provider clear.

### Acceptance Criteria for Vertex AI Evaluators

Every Vertex AI evaluator MUST meet these criteria:

**Configuration Requirements:**
- [ ] Valid YAML with Vertex AI model path
- [ ] Uses `GOOGLE_APPLICATION_CREDENTIALS` or equivalent auth
- [ ] Pinned model version where available
- [ ] Prompt contains `{content}` placeholder

**Testing Requirements:**
- [ ] Passes config validation tests
- [ ] Successfully evaluates `sample_secure.py`
- [ ] Successfully evaluates `sample_vulnerable.py` (for code-review category)
- [ ] Response time documented

**Documentation Requirements:**
- [ ] README.md with use cases
- [ ] Notes Vertex AI as the access method
- [ ] Comparison with similar evaluators

## Consequences

### Positive

- ✅ **No new signups**: Leverage existing Google Cloud account
- ✅ **Unified billing**: Single invoice for all Vertex AI models
- ✅ **Data privacy**: Prompts not shared with third parties (Google's commitment)
- ✅ **Enterprise security**: SOC 2, HIPAA, FedRAMP compliance available
- ✅ **Simplified API key management**: One auth method for multiple model families
- ✅ **Free tier available**: $300 credits or 90-day Express Mode

### Negative

- ⚠️ **Google Cloud dependency**: All Vertex AI models depend on GCP availability
- ⚠️ **Model availability lag**: New models may appear on direct APIs before Vertex AI
- ⚠️ **Pricing markup**: Vertex AI may have slight markup over direct provider APIs
- ⚠️ **Regional restrictions**: Some models may be limited to specific regions
- ⚠️ **Model retirement**: Vertex AI retires models (e.g., Codestral 25.01 retired Jan 2026)

### Neutral

- 📊 **Different auth pattern**: Vertex AI uses GCP auth vs simple API keys
- 📊 **Model naming differs**: Vertex AI model IDs differ from direct provider IDs
- 📊 **SDK options**: Can use Google Cloud SDK, REST API, or litellm

## Alternatives Considered

### Alternative 1: Direct Multi-Provider Signups

**Description**: Sign up directly with DeepSeek, Groq, Together AI, Cohere, etc.

**Rejected because**:
- ❌ Signup friction for each provider
- ❌ Multiple billing relationships
- ❌ Some providers not economically viable (Cohere)
- ❌ Enterprise requirements for some (Sourcegraph)

### Alternative 2: OpenRouter Aggregator

**Description**: Use OpenRouter as a single API gateway to access multiple models

**Rejected because**:
- ❌ Additional third-party dependency
- ❌ Pricing markup over direct APIs
- ❌ Less enterprise-grade than Vertex AI
- ❌ New signup required (vs existing GCP account)

### Alternative 3: Continue with ADR-0002 Original Plan

**Description**: Proceed with Cohere, DeepSeek direct integration per ADR-0002

**Rejected because**:
- ❌ Cohere not economically feasible (per stakeholder feedback)
- ❌ Each provider requires separate signup
- ❌ Increases operational complexity

## Related Decisions

- ADR-0002: Evaluator Expansion Strategy (original multi-provider approach)
- ADR-0001: Evaluator Testing Strategy (testing requirements apply)

## References

- [Vertex AI Model Garden](https://cloud.google.com/model-garden)
- [Llama 4 GA on Vertex AI](https://developers.googleblog.com/en/llama-4-ga-maas-vertex-ai/)
- [Mistral on Vertex AI](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/partner-models/mistral)
- [Claude on Vertex AI](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/partner-models/claude)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)
- [Vertex AI Express Mode](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)

## Revision History

- 2026-02-03: Initial proposal (Proposed)

---

**Template Version**: 1.1.0
