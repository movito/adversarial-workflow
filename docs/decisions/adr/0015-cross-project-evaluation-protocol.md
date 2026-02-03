# ADR-0015: Cross-Project Evaluation Protocol

**Status**: Proposed

**Date**: 2026-02-03

**Deciders**: planner, project maintainers

## Context

### Problem Statement

As the adversarial-workflow ecosystem grows (adversarial-workflow, adversarial-evaluator-library, consuming projects like agentive-starter-kit), cross-project coordination becomes increasingly important. Currently, this coordination happens through:

1. Manual discussion and back-and-forth
2. ADR documents copied between repositories
3. Informal proposals and responses

This ad-hoc approach worked for ADR-0004/0005 (model routing layer), but has limitations:

- No structured format for questions and responses
- No automated validation of interface compliance
- Coordination relies on human memory and attention
- No audit trail of decisions and their rationale

### Observation

The core of adversarial-workflow is **document evaluation with structured verdicts**:
- Input: Document
- Process: AI review against criteria
- Output: Structured verdict (APPROVED / NEEDS_REVISION / REJECTED) + feedback

This pattern could extend beyond task plans to **cross-project communication**.

### Forces at Play

**Technical Requirements:**
- Projects need to propose changes that affect other projects
- Interface contracts need validation against implementations
- Questions need structured responses with clear ownership
- Decisions need audit trails

**Constraints:**
- Projects are in separate repositories
- Teams may work asynchronously
- Not all communication needs formalization (overhead concern)
- Must integrate with existing planner agents

**Assumptions:**
- Each project has a planner agent that coordinates work
- Projects share the adversarial-workflow tooling
- Cross-project changes are infrequent but high-impact

## Decision

We propose a **Cross-Project Evaluation Protocol** that formalizes inter-project communication using the adversarial-workflow evaluation pattern.

### Protocol Overview

```
┌─────────────────────┐         ┌─────────────────────┐
│  Project A          │         │  Project B          │
│  (e.g., library)    │         │  (e.g., workflow)   │
│                     │         │                     │
│  ┌───────────────┐  │         │  ┌───────────────┐  │
│  │ Planner Agent │  │         │  │ Planner Agent │  │
│  └───────┬───────┘  │         │  └───────┬───────┘  │
│          │          │         │          │          │
│          ▼          │         │          ▼          │
│  .cross-project/    │ ◄─────► │  .cross-project/    │
│  └── outbound/      │  sync   │  └── inbound/       │
│  └── inbound/       │         │  └── outbound/      │
│  └── contracts/     │         │  └── contracts/     │
└─────────────────────┘         └─────────────────────┘
```

### 1. Directory Structure

Each participating project maintains a `.cross-project/` directory:

```
.cross-project/
├── README.md                    # Protocol documentation
├── outbound/                    # Requests TO other projects
│   └── 2026-02-03-routing-proposal.yml
├── inbound/                     # Requests FROM other projects
│   └── 2026-02-03-routing-proposal.yml
├── responses/                   # Responses to requests
│   └── 2026-02-03-routing-proposal-response.yml
├── contracts/                   # Active interface contracts
│   └── library-workflow-v1.yml
└── archive/                     # Completed exchanges
```

### 2. Request Format

```yaml
# .cross-project/outbound/2026-02-03-routing-proposal.yml
schema_version: "1.0"
type: architecture-proposal      # proposal | question | review-request | contract-update

metadata:
  id: "AEL-2026-02-03-001"
  from: adversarial-evaluator-library
  to: adversarial-workflow
  created: 2026-02-03T10:00:00Z
  priority: medium               # low | medium | high | critical
  deadline: 2026-02-10           # Optional response deadline

subject: "Model Routing Layer Architecture"

# Reference to detailed document
document:
  path: docs/decisions/adr/ADR-0004.md
  commit: abc1234

# Specific questions/requests
questions:
  - id: q1
    question: "Does adversarial-workflow currently have any model routing logic?"
    context: "Need to understand current state before proposing changes"

  - id: q2
    question: "What is the current configuration mechanism for users?"
    context: "Proposed routing config needs to fit existing patterns"

  - id: q3
    question: "Are there existing abstractions we should align with?"
    context: "Want to avoid duplicate/conflicting patterns"

# What you're proposing (if type: proposal)
proposal:
  summary: "Separate evaluator definitions from model routing"
  impact: "Requires new resolution engine in workflow"
  breaking_changes: false
```

### 3. Response Format

```yaml
# .cross-project/responses/2026-02-03-routing-proposal-response.yml
schema_version: "1.0"

metadata:
  request_id: "AEL-2026-02-03-001"
  from: adversarial-workflow
  responded: 2026-02-03T15:30:00Z
  responder: planner

verdict: APPROVED                 # APPROVED | NEEDS_REVISION | BLOCKED | DEFERRED

summary: "Architecture aligned. Ready for Phase 1 implementation."

answers:
  - question_id: q1
    answer: |
      No routing logic exists. Model field passes directly to aider --model flag.
      Aider/litellm handles provider routing internally.

  - question_id: q2
    answer: |
      .adversarial/config.yml exists with simple key-value pairs.
      Proposed routing: section fits naturally.

  - question_id: q3
    answer: |
      Greenfield - no existing provider classes or model resolvers.
      EvaluatorConfig dataclass is the only relevant abstraction.

# Counter-proposals or conditions
conditions:
  - "Add litellm_prefix to registry schema for direct passthrough support"
  - "Phase 1 must maintain backwards compatibility with legacy model field"

# Resulting action items
action_items:
  - owner: adversarial-workflow
    task: "ADV-0015: Implement Phase 1 resolution engine"
    target: v0.8.0

  - owner: adversarial-evaluator-library
    task: "Publish providers/registry.yml"
    target: immediate

# Reference to interface contract if established
contract:
  path: .cross-project/contracts/library-workflow-v1.yml
  version: "1.0"
```

### 4. Contract Format

For ongoing interfaces, a contract document captures the agreement:

```yaml
# .cross-project/contracts/library-workflow-v1.yml
schema_version: "1.0"

metadata:
  id: library-workflow-interface
  version: "1.0"
  parties:
    - adversarial-evaluator-library
    - adversarial-workflow
  established: 2026-02-03
  adr_reference: docs/decisions/adr/library-refs/ADR-0005.md

interface:
  name: "Evaluator Library Interface"

  # What library provides
  library_provides:
    - artifact: providers/registry.yml
      schema_version: "1.0"
      update_frequency: "as needed"

    - artifact: evaluators/*/evaluator.yml
      format: "YAML with model_requirement field"
      update_frequency: "per evaluator release"

  # What workflow expects
  workflow_expects:
    - registry_schema_version: "1.x"
    - evaluator_fields: ["name", "model_requirement OR model", "prompt"]

  # Compatibility rules
  compatibility:
    breaking_change_notification: "2 weeks"
    deprecation_period: "1 major version"

validation:
  # How to verify compliance
  library_tests:
    - "Registry validates against schema"
    - "All evaluators have required fields"

  workflow_tests:
    - "Resolution engine handles schema 1.x"
    - "Fallback to legacy model field works"
```

### 5. Planner Integration

Planner agents check for cross-project requests on startup:

```python
# Pseudocode for planner startup
def check_cross_project_requests():
    inbound = glob(".cross-project/inbound/*.yml")
    pending = [r for r in inbound if not has_response(r)]

    if pending:
        print(f"📬 {len(pending)} cross-project request(s) awaiting response:")
        for req in pending:
            print(f"  - {req.subject} from {req.from} (due: {req.deadline})")
```

### 6. Evaluation Integration

Cross-project documents can be evaluated using specialized evaluators:

```bash
# Evaluate a proposal against our codebase
adversarial evaluate --evaluator cross-project-review \
  .cross-project/inbound/2026-02-03-routing-proposal.yml

# Validate implementation against contract
adversarial evaluate --evaluator contract-compliance \
  --contract .cross-project/contracts/library-workflow-v1.yml \
  adversarial_workflow/evaluators/resolver.py
```

### 7. Synchronization

Projects sync their cross-project directories via:

1. **Manual copy**: Copy requests/responses between repos (current approach)
2. **Shared repository**: Dedicated repo for cross-project communication
3. **Automated sync**: GitHub Actions that sync on push (future enhancement)

For now, **manual copy** is sufficient given low volume.

## Consequences

### Positive

- **Structured communication**: Clear format for proposals, questions, responses
- **Audit trail**: All decisions and rationale preserved in version control
- **Planner awareness**: Agents can check for pending requests
- **Evaluation integration**: Use existing evaluation infrastructure
- **Contract validation**: Can verify implementations match agreements

### Negative

- **Overhead for simple questions**: Not everything needs formalization
- **Sync complexity**: Keeping directories in sync across repos
- **Learning curve**: Teams need to learn the protocol
- **Tooling required**: Need evaluators and planner integration

### Neutral

- **Opt-in formality**: Teams choose when to use formal protocol vs informal discussion
- **Evolution**: Protocol can evolve based on actual usage patterns

## Implementation Phases

| Phase | Scope | Effort |
|-------|-------|--------|
| **0** | Document protocol (this ADR) | Done |
| **1** | Create `.cross-project/` structure, manual sync | 1 day |
| **2** | Planner startup check for pending requests | 1 day |
| **3** | `cross-project-review` evaluator | 2-3 days |
| **4** | `contract-compliance` evaluator | 2-3 days |
| **5** | Automated sync (GitHub Actions) | Future |

## When to Use This Protocol

**Use formal protocol for:**
- Architecture changes affecting multiple projects
- Interface contract establishment or changes
- Breaking changes requiring coordination
- Decisions needing permanent record

**Use informal communication for:**
- Quick questions with obvious answers
- Bug reports (use GitHub issues instead)
- Implementation details within agreed contracts
- Exploratory discussions before formal proposals

## Related Decisions

- ADR-0004: Model Routing Layer (example of cross-project coordination)
- ADR-0005: Library-Workflow Interface Contract (example contract)
- ADR-0014: Agent-Evaluator Interaction Patterns (evaluation infrastructure)

## Open Questions

1. **Sync mechanism**: Should we invest in automated sync, or is manual sufficient?
2. **Notification**: How do teams get notified of new requests? (GitHub notifications? Slack?)
3. **Versioning**: How do we handle protocol version evolution?

## References

- Current cross-project artifacts: `docs/decisions/adr/library-refs/`
- Evaluation infrastructure: `adversarial_workflow/evaluators/`

## Revision History

- 2026-02-03: Initial proposal based on ADR-0004/0005 coordination experience

---

**Template Version**: 1.1.0
