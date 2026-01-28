# Custom Evaluators

This guide explains how to create and use custom evaluators with adversarial-workflow.

## Overview

Custom evaluators allow you to:
- Use different AI models (Gemini, Claude, local models)
- Create domain-specific evaluation criteria
- Share evaluators across projects
- Extend the workflow without modifying the package

## Quick Start

1. Create `.adversarial/evaluators/my-evaluator.yml`
2. Define your evaluator configuration
3. Run: `adversarial my-evaluator file.md`

## Full Schema Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Command name (e.g., "athena", "security-audit") |
| `description` | string | Help text shown in CLI |
| `model` | string | AI model to use (e.g., "gpt-4o", "gemini-2.5-pro", "claude-3-opus-20240229") |
| `api_key_env` | string | Environment variable name for API key |
| `prompt` | string | The evaluation prompt template |
| `output_suffix` | string | Log file suffix (e.g., "SECURITY-AUDIT") |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `aliases` | list | `[]` | Alternative command names |
| `log_prefix` | string | `""` | CLI output prefix (e.g., "ATHENA") |
| `fallback_model` | string | `null` | Fallback model if primary fails |
| `version` | string | `"1.0.0"` | Evaluator version |
| `timeout` | int | `180` | Timeout in seconds (max: 600). CLI `--timeout` overrides this. |

### Complete Example

```yaml
# .adversarial/evaluators/security-audit.yml
name: security-audit
description: Security vulnerability assessment using GPT-4o
version: 1.2.0

model: gpt-4o
fallback_model: gpt-4o-mini
api_key_env: OPENAI_API_KEY
timeout: 300  # 5 minutes for complex security analysis

output_suffix: SECURITY-AUDIT
log_prefix: "SECURITY"

aliases:
  - security
  - audit

prompt: |
  You are a security expert reviewing code for vulnerabilities.

  ## Focus Areas
  1. OWASP Top 10 vulnerabilities
  2. Input validation and sanitization
  3. Authentication and authorization
  4. Data exposure risks
  5. Dependency vulnerabilities

  ## Output Format

  ## Security Audit Summary

  **File**: [filename]
  **Reviewed**: [date]
  **Risk Level**: [CRITICAL / HIGH / MEDIUM / LOW / NONE]

  ## Vulnerabilities Found
  - [CRITICAL] [description]
  - [HIGH] [description]
  ...

  ## Recommendations
  1. [Specific remediation step]
  2. [Alternative approach]

  ## Approval Status
  **Verdict**: [APPROVED / NEEDS_REVISION / REJECT]
```

## Examples

### Legal Document Evaluator

For reviewing contracts, terms of service, and legal documents:

```yaml
# .adversarial/evaluators/legal-review.yml
name: legal-review
description: Legal document review using Claude
model: claude-3-opus-20240229
api_key_env: ANTHROPIC_API_KEY
output_suffix: LEGAL-REVIEW
log_prefix: "LEGAL"

aliases:
  - legal
  - contract

prompt: |
  You are a legal document reviewer.

  ## Review Criteria
  1. Clarity and precision of language
  2. Completeness of terms
  3. Potential ambiguities
  4. Missing standard clauses
  5. Compliance considerations

  ## Output Format

  ## Legal Review Summary

  **Document**: [filename]
  **Reviewed**: [date]
  **Risk Assessment**: [HIGH / MEDIUM / LOW]

  ## Issues Found
  - [CRITICAL] [clause or section with issue]
  - [HIGH] [ambiguous language]
  ...

  ## Recommendations
  1. [Specific revision]

  **Verdict**: [APPROVED / NEEDS_REVISION / REJECT]
```

### Teaching Content Evaluator

For reviewing educational materials:

```yaml
# .adversarial/evaluators/teaching-review.yml
name: teaching-review
description: Educational content review
model: gpt-4o
api_key_env: OPENAI_API_KEY
output_suffix: TEACHING-REVIEW

aliases:
  - teaching
  - edu

prompt: |
  You are an educational content specialist.

  ## Evaluation Criteria
  1. Learning objective clarity
  2. Content accuracy
  3. Appropriate difficulty level
  4. Engagement and interactivity
  5. Assessment alignment

  ## Output Format

  ## Teaching Content Review

  **Material**: [filename]
  **Target Audience**: [identified audience]
  **Verdict**: [APPROVED / NEEDS_REVISION / REJECT]

  ## Strengths
  - [What works well]

  ## Areas for Improvement
  - [Specific suggestions]
```

### Knowledge Evaluation (Athena)

For research and documentation review:

```yaml
# .adversarial/evaluators/athena.yml
name: athena
description: Knowledge evaluation using Gemini 2.5 Pro
model: gemini-2.5-pro
api_key_env: GEMINI_API_KEY
output_suffix: KNOWLEDGE-EVALUATION
log_prefix: "ATHENA"

aliases:
  - knowledge
  - research

prompt: |
  You are Athena, a knowledge evaluation specialist.

  ## Evaluation Criteria

  ### 1. SOURCE VALIDITY
  - Are sources authoritative and reliable?
  - Is the source hierarchy correct (primary > secondary > tertiary)?

  ### 2. VERIFIABILITY
  - Can claims be traced to primary sources?
  - Are references complete and correct?

  ### 3. SCOPE AND BOUNDARIES
  - Is the scope realistic?
  - Are boundaries clearly communicated?

  ### 4. MAINTAINABILITY
  - Can content be kept updated over time?
  - Is dating and versioning in place?

  ### 5. AUDIENCE FIT
  - Is content written for the right audience?
  - Is complexity level appropriate?

  ## Output Format

  ## Athena Evaluation Summary

  **Document**: [filename]
  **Evaluated**: [date]
  **Verdict**: [APPROVED / NEEDS_REVISION / REJECT]
  **Confidence**: [HIGH / MEDIUM / LOW]

  ## Strengths
  - [What the document does well]

  ## Concerns
  - [CRITICAL] [Source problems, factual errors]
  - [HIGH] [Missing coverage, unclear scope]

  ## Recommendations
  1. [Concrete improvement]
```

## Listing Evaluators

View all available evaluators (built-in and local):

```bash
adversarial list-evaluators
```

Output:
```
Built-in Evaluators:
  evaluate       Plan evaluation (GPT-4o)
  proofread      Teaching content review (GPT-4o)
  review         Code review (GPT-4o)

Local Evaluators (.adversarial/evaluators/):
  athena         Knowledge evaluation using Gemini 2.5 Pro
    aliases: knowledge, research
    model: gemini-2.5-pro
```

## Troubleshooting

### API Key Issues

**Problem**: "API key not found" error

**Solution**: Ensure the environment variable specified in `api_key_env` is set:
```bash
export GEMINI_API_KEY="your-api-key"
# or
export OPENAI_API_KEY="your-api-key"
```

### Model Compatibility

**Problem**: "Model not supported" error

**Solution**: Check that your model string matches the provider's format:
- OpenAI: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`
- Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- Google: `gemini-2.5-pro`, `gemini-1.5-flash`

### YAML Syntax Errors

**Problem**: Evaluator not appearing in `list-evaluators`

**Solution**: Validate your YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('.adversarial/evaluators/my-eval.yml'))"
```

Common issues:
- Missing required fields (`name`, `description`, `model`, etc.)
- Incorrect indentation
- Missing colon after field names

### Timeout Issues

**Problem**: "Evaluation timed out" error with slow models

**Solution**: Increase the timeout in your evaluator YAML or use the CLI flag:
```yaml
# In your evaluator YAML
timeout: 300  # 5 minutes
```

Or override on the command line:
```bash
adversarial my-evaluator --timeout 400 large-doc.md
```

**Note**: Maximum timeout is 600 seconds (10 minutes). Values above 600 are clamped automatically.

**Timeout precedence**: CLI `--timeout` > YAML `timeout` > default (180s)

### Name Conflicts

**Problem**: "Evaluator 'X' conflicts with CLI command; skipping"

**Solution**: Your evaluator name conflicts with a built-in command. Use a different name or use an alias:
```yaml
name: my-review  # Instead of 'review' which conflicts
aliases:
  - myrev
```

Protected command names:
- `init`, `check`, `doctor`, `health`, `quickstart`
- `agent`, `split`, `validate`, `review`, `list-evaluators`

## Best Practices

1. **Use descriptive names**: Choose clear, memorable command names
2. **Document your prompt**: Include evaluation criteria clearly
3. **Set appropriate output_suffix**: Makes log files easy to identify
4. **Use aliases sparingly**: Too many aliases can cause confusion
5. **Version your evaluators**: Track changes with the `version` field
6. **Test locally first**: Verify the evaluator works before sharing
7. **Configure timeout for slow models**: Set `timeout: 300` (or higher, up to 600) for models like Mistral Large that need more time on large documents. Use `--timeout` CLI flag for one-off overrides.

## Sharing Evaluators

Custom evaluators are stored in `.adversarial/evaluators/`. To share across projects:

1. Copy YAML files to the target project's `.adversarial/evaluators/`
2. Ensure required API keys are documented
3. Consider creating a shared repository of evaluator definitions

## See Also

- [README.md](../README.md) - Main documentation
- [docs/examples/athena.yml](examples/athena.yml) - Complete Athena example
