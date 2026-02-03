# ADR-0002: Evaluator Expansion Strategy

**Status**: Proposed

**Date**: 2026-02-01

**Deciders**: planner, project maintainers

## Context

### Problem Statement

The adversarial-evaluator-library provides pre-configured AI evaluators for document and code review. As new models and providers emerge, we need a principled approach to expanding coverage that:

1. Provides meaningful cognitive diversity out of the box
2. Remains a manageable "starter kit" rather than exhaustive catalog
3. Enables projects to extend with their own evaluators
4. Handles model versioning gracefully

### Current State

**12 evaluators** across 3 providers:

| Provider | Count | Categories Covered |
|----------|-------|-------------------|
| OpenAI | 6 | quick-check, code-review, deep-reasoning, adversarial |
| Google | 3 | quick-check, deep-reasoning, knowledge-synthesis |
| Mistral | 3 | quick-check, code-review, cognitive-diversity |

**Coverage gaps:**
- Anthropic/Claude: 0 evaluators (major provider missing)
- adversarial category: 1 evaluator (OpenAI only)
- cognitive-diversity: 1 evaluator (Mistral only)
- knowledge-synthesis: 1 evaluator (Google only)

### Forces at Play

#### Technical Requirements

- Each category should demonstrate cognitive diversity (multiple providers)
- Evaluators must use pinned model versions for reproducibility
- New evaluators should follow established patterns

#### Constraints

- Library should remain a "starter kit", not exhaustive catalog
- Maintenance burden scales with evaluator count
- API costs for testing all evaluators
- Model deprecation requires ongoing updates

#### Assumptions

- Projects will add their own specialized evaluators
- Major providers (OpenAI, Anthropic, Google, Mistral) are essential for broad coverage
- Emerging providers add valuable diversity
- Model behavior drifts; pinned versions provide stability

---

**Definition: Cognitive Diversity**

"Cognitive diversity" means evaluators that produce meaningfully different outputs on the same input—like having multiple reviewers with different expertise examine the same document. A security specialist, a performance engineer, and a UX designer will each catch different issues. Similarly, AI models from different providers have different training data, safety policies, and reasoning patterns, leading them to flag different concerns.

This is measured by:

1. **Disagreement Rate**: On a benchmark set of 20 test documents, evaluators from different providers should disagree on at least 15% of findings (one flags an issue the other doesn't)
2. **Different Failure Modes**: Documented cases where each provider catches issues the other misses
3. **Complementary Strengths**: Each evaluator's README documents its unique strengths vs alternatives

Provider diversity is a *proxy* for cognitive diversity, not a guarantee. Empirical validation (disagreement testing) is required before claiming cognitive diversity benefits.

**Empirical Validation Framework**

Before claiming cognitive diversity benefits for a category, we will:

1. **Run disagreement testing**: Evaluate 20 sample documents with each provider's evaluator
2. **Measure disagreement rate**: Count findings where one evaluator flags an issue the other doesn't
3. **Document failure modes**: Record specific examples where each evaluator caught unique issues
4. **Publish results**: Include disagreement metrics in evaluator README files

Example validation results (to be populated):
```
Category: code-review
Evaluators compared: gpt5-code vs claude-code
Sample size: 20 code files
Disagreement rate: TBD%
Unique findings by gpt5-code: TBD
Unique findings by claude-code: TBD
```

## Decision

We adopt a **Balanced Coverage Model** with the following principles:

### Principle 1: Minimum Viable Diversity

Each category SHOULD have evaluators from **at least 2 different providers** to demonstrate cognitive diversity. Single-provider categories are tracked as gaps but not blockers for Phase 1.

**Priority for multi-provider coverage:**
- **High**: adversarial, code-review (critical evaluation categories)
- **Medium**: deep-reasoning, cognitive-diversity
- **Lower**: knowledge-synthesis, quick-check (less critical or already diverse)

**Current gaps (target for remediation):**
- adversarial: OpenAI only → Add Anthropic or Google
- cognitive-diversity: Mistral only → Add Anthropic or OpenAI
- knowledge-synthesis: Google only → Add OpenAI (Phase 1) or Anthropic (Phase 2)

**Rationale for SHOULD vs MUST**: Strict "MUST" would force low-value evaluator additions or block releases. Categories are prioritized by evaluation criticality, with gaps documented and tracked.

### Principle 2: Provider Tiers

Organize providers into tiers based on selection criteria:

**Selection Criteria:**
1. API stability and uptime (enterprise SLA availability)
2. Model capability benchmarks (MMLU, HumanEval, etc.)
3. Adoption in target user base (developer tools, enterprise)
4. Pricing and availability

**Tier 1 (Essential)** - Must have comprehensive coverage:
- OpenAI: Highest enterprise adoption, stable versioned APIs
- Anthropic: Strong reasoning benchmarks, safety-focused design
- Google: Gemini API, large context windows (1M+ tokens)

**Tier 2 (Important)** - Should have representative coverage:
- Mistral: EU data residency option, competitive pricing
- Cohere: Enterprise RAG focus, embedding integration

**Tier 3 (Emerging)** - May add for specific strengths:
- DeepSeek: Code-specialized models (DeepSeek Coder benchmarks)
- xAI/Grok: Alternative perspective, real-time training
- Meta/Llama via Groq/Together: Open weights baseline for comparison

### Principle 3: Pinned Model Versions

All evaluators MUST use pinned model versions to improve reproducibility:

```yaml
# Good - pinned version
model: gpt-5-turbo-2025-11-01

# Bad - floating reference
model: gpt-5-turbo
```

**Reproducibility Limitations:**
Pinned versions *improve* but do not *guarantee* reproducibility due to:
- Provider-side changes behind the same version label
- Non-determinism in model sampling (mitigated by temperature=0 where supported)
- Changes to safety layers or system prompts by providers

**Mitigation Controls:**
- Use `temperature: 0` in evaluator config when provider supports it
- Store evaluation outputs for comparison
- Document provider deprecation policies in evaluator README
- Monitor for unexpected output changes in CI

**Model Lifecycle Management:**

| Phase | Action | Timeline |
|-------|--------|----------|
| **Active** | Primary recommended evaluator | Until superseded |
| **Deprecated** | New version available, old still works | Target 6 months or provider sunset, whichever is sooner |
| **Sunset** | Model removed by provider | Remove from library within 30 days |

**Timeline Rationale**: 6-month target based on typical provider deprecation windows (OpenAI ~6-12mo, Anthropic ~6mo). If provider announces shorter sunset, we follow their timeline. Exception handling documented in evaluator's CHANGELOG.

**When models are updated:**
1. Create new evaluator with new version (e.g., `gpt5-code-2026-03`)
2. Keep old evaluator marked as `deprecated: true` in YAML
3. Update documentation recommending new version
4. Monitor provider deprecation announcements
5. Remove evaluator when provider sunsets model

**Error Handling for Deprecation:**
- Evaluator YAML includes `deprecated: true` flag when superseded
- Index.json tracks `deprecated_date` and `replacement` fields
- CI warns on deprecated evaluator usage
- Tests continue to run against deprecated evaluators until removal

### Principle 4: Category Cost Ladder

Each category SHOULD have evaluators at different cost points.

**Standard Evaluation Budget** (for cost estimates):
- Input: 2,000 tokens (typical document/code file)
- Output: 500 tokens (evaluation response)
- Prices as of 2026-02-01; verify current rates at provider pricing pages

| Tier | Characteristics | Example Models | Est. Cost/Eval |
|------|-----------------|----------------|----------------|
| **Budget** | Fast, small models | gpt-4o-mini, gemini-1.5-flash | ~$0.001-0.003 |
| **Standard** | Balanced capability | gpt-4o, claude-3-sonnet | ~$0.01-0.04 |
| **Premium** | Maximum capability | gpt-5.2, claude-3-opus, o3 | ~$0.08-0.15 |

**Note**: Costs scale with document size. Large files (10k+ tokens) may cost 5-10x these estimates. Cost calculation script: `scripts/calculate_eval_cost.py` (TODO: create).

### Principle 5: Extensibility First

The library is a **starter kit**. Design for extension:

- Document how to add custom evaluators
- Provide evaluator templates for each category
- Keep core evaluator count manageable (target: 20-30 total)
- Prefer quality over quantity

**Rationale for 20-30 Cap:**
- CI test time: ~30s per evaluator behavioral test = 15-20 min total at 30 evaluators
- Cost: Full test suite at ~$0.05/evaluator = $1-1.50 per CI run
- Maintenance: Each evaluator needs version monitoring, deprecation handling
- Coverage: 6 categories × 4 providers × ~1.2 cost tiers = ~30 evaluators at saturation

### Implementation: Target State

**Phase 1: Fill Critical Gaps** (Priority)

| Evaluator | Provider | Category | Model | Rationale |
|-----------|----------|----------|-------|-----------|
| `claude-adversarial` | Anthropic | adversarial | claude-4-opus-20260115 | Fill single-provider gap, strong reasoning |
| `claude-code` | Anthropic | code-review | claude-4-sonnet-20260115 | Add Tier 1 provider |
| `claude-quick` | Anthropic | quick-check | claude-4-haiku-20260115 | Budget option |
| `gemini-code` | Google | code-review | gemini-3-pro-20260101 | Fill provider gap |
| `gpt5-diversity` | OpenAI | cognitive-diversity | gpt-5-turbo-2025-11-01 | Fill single-provider gap |
| `gpt5-synthesis` | OpenAI | knowledge-synthesis | gpt-5-turbo-2025-11-01 | Fill single-provider gap |

**Phase 2: Expand Tier 2** (Secondary)

| Evaluator | Provider | Category | Model |
|-----------|----------|----------|-------|
| `cohere-reasoning` | Cohere | deep-reasoning | command-r-plus-2025-10 |
| `cohere-synthesis` | Cohere | knowledge-synthesis | command-r-plus-2025-10 |

**Phase 3: Tier 3 Specialists** (Optional)

| Evaluator | Provider | Category | Model |
|-----------|----------|----------|-------|
| `deepseek-code` | DeepSeek | code-review | deepseek-coder-v3-2025-09 |
| `llama-baseline` | Groq | quick-check | llama-4-70b-2025-08 |

### Target Coverage Matrix

After Phase 1:

| Category | OpenAI | Anthropic | Google | Mistral | Total | Multi-Provider? |
|----------|--------|-----------|--------|---------|-------|-----------------|
| quick-check | 1 | 1 | 1 | 1 | 4 | ✅ Yes (4) |
| code-review | 3 | 1 | 1 | 1 | 6 | ✅ Yes (4) |
| deep-reasoning | 1 | 0 | 1 | 0 | 2 | ✅ Yes (2) |
| adversarial | 1 | 1 | 0 | 0 | 2 | ✅ Yes (2) |
| cognitive-diversity | 1 | 0 | 0 | 1 | 2 | ✅ Yes (2) |
| knowledge-synthesis | 1 | 0 | 1 | 0 | 2 | ✅ Yes (2) |
| **Total** | 8 | 3 | 4 | 3 | **18** | **All categories ≥2** |

### Principle 6: Acceptance Criteria for New Evaluators

Every new evaluator MUST meet these criteria before merging:

**Configuration Requirements:**
- [ ] Valid YAML with all required fields (name, description, model, api_key_env, prompt)
- [ ] Pinned model version (not floating reference)
- [ ] Prompt contains `{content}` placeholder
- [ ] README.md documents use cases and expected behavior
- [ ] CHANGELOG.md initialized

**Testing Requirements:**
- [ ] Passes Tier 1 config validation tests
- [ ] Successfully evaluates `sample_secure.py`:
  - Returns non-empty response
  - Response is valid markdown
  - Does not raise false critical issues (low false positive rate)
- [ ] Successfully evaluates `sample_vulnerable.py`:
  - Detects at least 2 of 4 seeded vulnerabilities (SQL injection, XSS, hardcoded secrets, path traversal)
  - Each finding includes: severity level, line reference, remediation suggestion
  - Response includes overall risk assessment
- [ ] Response time documented (avg across 3 runs, must be <120s for standard tier)
- [ ] Cost per evaluation documented (using standard 2k input/500 output budget)

**Output Schema Requirements:**
Evaluator output must be parseable markdown with:
1. Findings section with severity labels (CRITICAL/HIGH/MEDIUM/LOW)
2. Line or code references for each finding
3. Overall assessment or verdict

**Documentation Requirements:**
- [ ] Added to `evaluators/index.json`
- [ ] Category and provider correctly assigned
- [ ] Comparison with similar evaluators noted in README

**Breaking Change Prevention:**
- New evaluators are additive only (no breaking changes to existing evaluator IDs or semantics)
- Existing evaluators may be marked `deprecated: true` and have metadata updated (replacement, deprecated_date)
- Index.json additions use append-only pattern for new evaluators; existing entries may have deprecation fields added
- Existing test fixtures unchanged
- Evaluator prompt content is immutable once released (create new evaluator for prompt changes)

### Naming Convention

```
{model-family}-{category-or-specialty}[-{version-suffix}]
```

Examples:
- `claude-code` (Anthropic code review)
- `gpt5-code-2026-03` (versioned update)
- `deepseek-code` (specialist)
- `llama-baseline` (open source reference)

## Consequences

### Expected Benefits

Adding evaluators following this strategy provides:

- ✅ **Meaningful diversity**: Every category has multiple perspectives, catching issues that single-provider coverage would miss
- ✅ **Reproducible results**: Pinned versions prevent unexpected behavior changes between runs
- ✅ **Clear extension path**: Projects know exactly how to add their own evaluators
- ✅ **Managed scope**: ~20-30 evaluators keeps the library usable without overwhelming users
- ✅ **Cost options**: Budget to premium tiers let users choose based on their needs

### Potential Drawbacks

However, this approach has trade-offs:

- ⚠️ **Version maintenance**: Pinned versions require updates when providers deprecate models
- ⚠️ **API key complexity**: More providers = more API keys to manage and secure
- ⚠️ **Testing cost**: Each new evaluator adds ~$0.05 to the CI test cost and ~30s to runtime
- ⚠️ **Provider dependencies**: Adding Tier 1 providers increases critical external dependencies

### Neutral

- 📊 **Evaluator count grows**: 12 → 18 (Phase 1), potentially ~25 (all phases)
- 📊 **Index structure unchanged**: Same YAML format, same categories

## Alternatives Considered

### Alternative 1: Complete Matrix Coverage

**Description**: Every category has evaluators from every Tier 1 provider (6 categories × 3 providers = 18 minimum)

**Rejected because**:
- ❌ Forces low-value combinations (e.g., Mistral for knowledge-synthesis)
- ❌ Maintenance burden too high
- ❌ Dilutes focus on quality evaluators

### Alternative 2: Curated Minimal Set

**Description**: Only 1-2 best evaluators per category, regardless of provider

**Rejected because**:
- ❌ Loses cognitive diversity benefit
- ❌ Creates provider lock-in risk
- ❌ Doesn't demonstrate multi-model approach

### Alternative 3: Latest Model References

**Description**: Use floating model references (e.g., `gpt-4o` not `gpt-4o-2024-08-06`)

**Rejected because**:
- ❌ Results not reproducible
- ❌ Behavior changes without warning
- ❌ Harder to debug evaluation differences

## Related Decisions

- ADR-0001: Evaluator Testing Strategy (how to test new evaluators)

## References

- `evaluators/index.json` - Current evaluator registry
- `docs/EVALUATOR-TESTING-GUIDE.md` - Testing new evaluators
- [Anthropic API Models](https://docs.anthropic.com/en/docs/models-overview)
- [OpenAI Model Versions](https://platform.openai.com/docs/models)

## Revision History

- 2026-02-01: Initial proposal (Proposed)
- 2026-02-01: Revision based on GPT-5.2 adversarial review:
  - Changed Principle 1 from MUST to SHOULD with priority-based rationale
  - Added operational definition of "cognitive diversity" with measurable criteria
  - Clarified "additive only" to allow deprecation metadata updates
  - Added token budget assumptions and pricing date for cost ladder
  - Specified test pass/fail rubric with output schema requirements
  - Added gpt5-synthesis to Phase 1 (18 total evaluators)
  - Added reproducibility limitations and mitigation controls
  - Added rationale for 20-30 evaluator cap
  - Made provider tier criteria objective (removed marketing language)
  - Clarified lifecycle timeline with provider dependency
- 2026-02-01: Revision based on Gemini 3 Pro synthesis review:
  - Updated Phase 1 model versions to 2025/2026 era (was using deprecated 2024 models)
  - Updated Phase 2/3 model versions for consistency
  - Fixed temporal inconsistency between document date and model versions
- 2026-02-01: Revision based on Mistral Large content review:
  - Added plain-language explanation of "cognitive diversity" concept
  - Restructured "Forces at Play" into clear subsections (Requirements, Constraints, Assumptions)
  - Added empirical validation framework for measuring cognitive diversity
  - Clarified expected benefits and potential drawbacks in Consequences section
- 2026-02-01: Restored Anthropic as Tier 1 provider:
  - Reverted Anthropic exclusion to avoid tight coupling to specific agent implementations
  - Added claude-adversarial, claude-code, claude-quick to Phase 1
  - Restored 4-provider strategy (OpenAI, Anthropic, Google, Mistral)
  - Target: 18 evaluators
