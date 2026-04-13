# Architectural Brief: Agent-Generated Content and Evolving Schema in a Sanity + Astro Pipeline

This document describes an emerging design problem at the intersection of AI-assisted content production and structured content management. It is intended as a brief for expert review. The context is a teaching and research workflow where a conversational agent (running in Anthropic's Cowork environment) produces analytical documents — overviews, annotated reference lists, regulatory surveys — which need to flow into a Sanity CMS instance and render via an Astro frontend. The central tension is between the agent's capacity to invent novel, situation-appropriate content structures and the CMS's need for a stable, maintainable schema.

*Compiled: March 2026*

---

## 1. The Problem in Concrete Terms

### What we have today

A Cowork agent researches a topic (e.g., global social media regulation), synthesises findings, and produces a standalone HTML file. The file contains structured sections — prose introductions, timelines, jurisdiction profiles, trend analyses, annotated reference tables — but this structure is implicit in the HTML. The file is a one-off deliverable: useful, but not maintainable, not queryable, not composable with other content.

### What we want

The agent pushes structured content to Sanity via its MCP connector. Astro renders it. The content becomes part of a larger, maintained corpus — a teaching site with multiple projects, modules, and deliverables. It can be edited in Sanity Studio, queried via GROQ, cross-referenced with other documents, and rebuilt by the Astro pipeline without manual intervention.

### Why this is harder than it sounds

The agent does not know, at the start of a session, what content structures it will need. A regulatory overview requires timelines and jurisdiction profiles. A literature review requires thematic sections and cross-reference tables. A case study requires a different anatomy entirely. The agent discovers the appropriate structure *during* the research process, not before it. This is a feature, not a bug — it is precisely what makes the agent useful. But it creates a fundamental mismatch with a CMS schema, which must exist *before* content can be written to it.

---

## 2. The Two Extremes

### Extreme A: Fully constrained schema

Define a fixed set of document types and block types in Sanity. The agent must compose within these types, always. If a session produces content that does not fit, the agent flattens it into the nearest available type (e.g., converting a structured timeline into a portable text block).

**Advantages:** Schema stability. Predictable Astro templates. No schema drift. Low maintenance burden.

**Costs:** The agent's output is limited to what the schema anticipated. Novel structures — which may be the most valuable part of the agent's work — are either lost or degraded. Over time, the system converges on a least-common-denominator output format that underutilises the agent's analytical capabilities.

### Extreme B: Fully generative schema

The agent creates new document types and block types on the fly, deploying schema changes via the Sanity MCP's `deploy_schema` tool whenever it encounters a content structure that does not fit. Every session can invent new types.

**Advantages:** No creative constraint. The agent can always express its findings in the most appropriate structure. The CMS faithfully represents whatever the agent produces.

**Costs:** Schema proliferation. Astro templates cannot anticipate new types, so rendering breaks or falls back to generic layouts. Sanity Studio becomes cluttered with one-off types. The schema becomes a geological record of every session's improvisation, with no guarantee that similar concepts were modelled consistently across sessions. Maintenance becomes increasingly expensive.

---

## 3. The Morphogenetic Middle Path

The approach under discussion sits between these extremes. It works as follows:

### 3.1 A stable shared layer

The Sanity instance has a set of common, well-defined document types and block types that serve the entire teaching site. These are the institutional constants: page structures, module containers, reference entries, common metadata fields (author, date, course, tags). These types are designed deliberately, maintained in the Astro codebase, and deployed through the normal development workflow.

The shared layer also includes a standard **reference table** format — a reusable pattern for annotated source lists that follows consistent column definitions and thematic grouping conventions. This is already codified as a Cowork skill and would map to a Sanity schema type.

### 3.2 Per-project custom extensions

When a session produces content that requires structure beyond the shared layer — a timeline with jurisdiction tags, a trend card grid, a comparative matrix — the agent creates a *local schema extension*. This is a new block type or document type, namespaced or tagged to the specific project, deployed via the Sanity MCP.

The agent also produces a corresponding Astro component suggestion or specification — not necessarily executable code, but a description of what the component should render and what props it expects. This bridges the gap between schema creation (which happens here) and frontend rendering (which happens in a separate development environment).

### 3.3 Periodic consolidation

Over time, a separate process — a Claude Code agent, a human review, or both — inspects the accumulated custom extensions. It asks: Which of these have been used more than once? Which are structurally similar and could be merged? Which are true one-offs that should be archived or removed?

Extensions that prove reusable are promoted to the shared layer: the schema type is generalised, an Astro component is built for it, and it becomes available to future sessions without re-invention. Extensions that remain one-offs are either left in place (if harmless) or refactored into the nearest shared type (if the maintenance cost exceeds their value).

Sanity's own content AI agent could assist in this consolidation by restructuring existing documents when a custom type is promoted or retired — transforming content from the old shape to the new one.

---

## 4. What the Agent Gains

### 4.1 Expressive freedom where it matters

The agent can invent structures that serve the material. A regulatory survey is not the same shape as a literature review, which is not the same shape as a design critique. Forcing them into the same schema flattens the analytical work. The morphogenetic approach lets each project find its natural form while still anchoring common elements (references, metadata, page structure) in shared types.

### 4.2 Incremental schema learning

The system gets smarter over time. The first time the agent creates a timeline block, it is a custom one-off. The second time, consolidation recognises the pattern. The third time, there is a shared `timeline` type ready to use. The schema evolves toward the content the agent actually produces, rather than being designed speculatively in advance.

### 4.3 Separation of concerns

Cowork handles research, analysis, and structured content creation. The Sanity MCP handles persistence. Astro and its development agents handle rendering. Each layer operates with its own tools and can be improved independently. The schema is the contract between them, and the morphogenetic approach lets that contract evolve without requiring all parties to coordinate synchronously.

---

## 5. What the Gain Costs

### 5.1 Schema undergrowth

The most immediate risk. Every custom extension is a small liability: a type that Astro may not know how to render, that Sanity Studio displays without a custom input component, that future agents may not recognise. Even with periodic consolidation, there will always be a long tail of project-specific types. The question is whether this tail is a manageable garden or an unmanageable forest.

Mitigation factors: Sanity's schema is code, so it can be linted and audited. A consolidation agent can track type usage and flag unused types. A convention of namespacing custom types (e.g., `project.socialMediaReg.timeline` vs. `shared.timeline`) makes it possible to distinguish institutional types from experimental ones.

### 5.2 The Astro rendering gap

When the agent creates a new block type in Sanity, Astro does not automatically know how to render it. Until a corresponding component exists, the content is structured in the CMS but invisible (or ugly) on the frontend. This creates a temporal gap: content is pushed immediately, but rendering may lag by hours or days until a development agent or human builds the component.

Possible approaches: A generic fallback renderer in Astro that can display any unknown block type in a reasonable (if unstyled) way. A queue of "component needed" requests that the consolidation process works through. Or acceptance of the gap as a feature — content lives in Sanity as structured data first, and frontend rendering is a second-pass concern.

### 5.3 Consistency drift

Two sessions might model the same concept differently. One session creates a `jurisdictionProfile` block with fields for `name`, `status`, and `summary`. Another creates a `countryOverview` block with fields for `country`, `regulatoryStatus`, and `description`. These are the same thing, but the schema does not know that. Consolidation can catch this, but only after the fact — and merging two divergent types that already have content is more work than getting it right the first time.

Mitigation: The Cowork skill that governs content creation should query existing custom types before creating new ones, and prefer reuse over invention. This is a heuristic, not a guarantee — but it shifts the default from "create new" to "reuse existing."

### 5.4 Governance complexity

Who decides when a custom type is promoted to the shared layer? Who decides when one is retired? In a solo practitioner setup (one teacher, one site), this is manageable. In a team or institutional context, it requires a governance process that adds overhead. The morphogenetic metaphor is appealing — organic growth, natural selection — but biological evolution does not have a deployment pipeline or a breaking-changes policy.

### 5.5 Testing surface area

Every new block type is a new thing that can break. Schema migrations, GROQ queries, Astro builds, and Sanity Studio all need to handle types they have not seen before. The more types exist, the larger the testing surface. Automated schema validation and build-time type checking (via Sanity's TypeGen or similar) help, but they do not eliminate the cost.

---

## 6. The Deeper Tension

The morphogenetic approach is, at its core, a bet on a specific trade-off: that the value of letting an agent explore an open opportunity landscape for content presentation outweighs the cost of subsequently imposing structure on what it finds.

This tension is not unique to this architecture. It appears wherever creative or exploratory work meets institutional infrastructure:

- A research group that lets postdocs define their own data schemas versus one that enforces a lab-wide standard
- A design system that allows component variants versus one that restricts to a fixed kit
- A wiki that lets anyone create page types versus one with enforced templates

In each case, the permissive approach generates more diverse and locally appropriate output, but at the cost of global coherence. The restrictive approach maintains coherence, but at the cost of forcing everything into shapes that may not fit.

The morphogenetic path attempts to have both, but it is honest about the mechanism: it relies on a *consolidation loop* that runs after the fact, inspecting what has grown and deciding what to keep, merge, or prune. The quality of the outcome depends almost entirely on the quality of this loop.

If consolidation is frequent, informed, and automated (or agent-assisted), the schema stays healthy: common patterns are recognised and promoted, one-offs are tolerated or retired, and the shared layer gradually becomes richer and more expressive. If consolidation is neglected, the schema accumulates debt: redundant types, orphaned structures, and inconsistencies that make every future session harder.

---

## 7. Open Questions for Expert Review

1. **Consolidation frequency and trigger.** Should consolidation run on a schedule (e.g., monthly), on a threshold (e.g., after N new custom types are created), or be triggered manually? What is the right balance between letting the garden grow and pruning it?

2. **The fallback renderer problem.** Is a generic Astro component that can render any unknown Sanity block type feasible in practice? What are the limits of such a component — can it handle nested structures, references, images? Or is a "component request queue" more realistic?

3. **Agent memory across sessions.** The Cowork agent currently has no persistent memory of previous sessions' schema decisions. Should it? A skill can encode conventions, but awareness of "I created a `jurisdictionProfile` type last week" requires either querying Sanity's schema at session start (feasible via MCP) or maintaining a separate memory store. Which is more reliable?

4. **Schema namespace conventions.** What naming convention best supports the shared/custom distinction? Prefixing (`custom.timeline` vs. `shared.timeline`)? Tagging (a `_schemaStatus` field on each type)? A separate dataset for experimental types?

5. **Adversarial review.** The user mentioned an adversarial-workflow pattern where one agent challenges another's output. Could a "schema critic" agent review proposed custom types before deployment — checking for redundancy with existing types, consistency with naming conventions, and renderability by the current Astro setup? What would this agent need access to?

6. **When not to push to Sanity.** Not every piece of agent output needs to enter the CMS. Some deliverables are genuinely one-off (a quick briefing document, an email draft, a slide deck). The system needs a clear heuristic for when content should be pushed to Sanity and when it should remain a standalone file. Who decides — the user, the agent, or the skill?

7. **Content migration cost.** When a custom type is promoted to the shared layer, existing documents of the old type need to be migrated. How expensive is this in practice? Can Sanity's content AI or a migration script handle it reliably, or does it require manual review?

---

## 8. Recommendation

The morphogenetic approach is the right direction for this use case. The alternative — a fully constrained schema designed in advance — would neuter the agent's most valuable capability: its ability to discover and express the structure that best fits the material. But the approach is only sustainable if the consolidation loop is treated as a first-class concern, not an afterthought.

Concretely, the next steps would be:

1. **Connect the Sanity MCP** and audit the existing schema to establish the current shared layer.
2. **Design the `sanity-content` skill** for Cowork, encoding shared conventions and the logic for querying existing types before creating new ones.
3. **Build a minimal fallback renderer** in Astro that can display unknown block types in a basic but functional way.
4. **Establish a consolidation cadence** — initially manual, potentially agent-assisted — for reviewing and promoting custom types.
5. **Test the loop end-to-end** with a single project (e.g., the social media regulation overview) before scaling to the full teaching site.

The costs are real but manageable. The gain — a teaching corpus that is both structurally sound and analytically rich, maintained through natural agent-human collaboration — is worth the investment.
