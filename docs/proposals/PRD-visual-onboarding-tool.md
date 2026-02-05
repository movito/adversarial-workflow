# Product Requirements Document: Agentive Studio

**Document Version**: 0.1.0
**Status**: Draft
**Author**: Planning Agent
**Created**: 2026-02-05
**Last Updated**: 2026-02-05

---

## Executive Summary

**Agentive Studio** is a browser-based visual tool that enables users to configure and deploy AI agent workflows without touching a terminal. It provides a guided onboarding experience that handles repository creation, agent definition, and project setup—all through an intuitive web interface.

This product addresses the steep learning curve that novice users face when setting up agent-based development workflows, transforming a 15-30 minute terminal-heavy process into a 5-minute visual experience.

---

## Problem Statement

### Current Pain Points

1. **High barrier to entry**: Users must understand Git, CLI tools, YAML syntax, and agent architecture before they can create their first agent workflow.

2. **Intimidating onboarding**: The current flow requires:
   - Reading documentation
   - Installing CLI tools
   - Cloning repositories
   - Understanding file structures
   - Learning agent definition syntax

3. **Agent definition complexity**: Users struggle to understand the relationship between:
   - Step-by-step instructions (what the agent does)
   - Inputs (what the agent reads)
   - Outputs (what the agent produces)
   - Tools (capabilities the agent needs)

4. **No visual feedback**: Users can't see what their agent will look like until they've written the full definition and run it.

### User Quotes (Hypothetical)

> "I just want to set up a code review agent. Why do I need to learn YAML frontmatter?"

> "I spent 2 hours trying to understand the file structure before I could even start."

> "I wish I could just click some boxes and have it generate the config for me."

---

## Goals & Success Metrics

### Primary Goals

1. **Reduce time-to-first-agent** from 30 minutes to under 5 minutes
2. **Enable non-terminal users** to create and deploy agent workflows
3. **Provide visual mental model** for understanding agent architecture
4. **Generate production-ready configurations** that follow best practices

### Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time to first working agent | 30+ min | < 5 min |
| Onboarding completion rate | Unknown | > 80% |
| Users requiring documentation | 100% | < 20% |
| Support requests for setup issues | High | Low |

### Non-Goals (v1)

- Real-time agent execution/testing in browser
- Full IDE functionality
- Team collaboration features
- Self-hosting support (v1 is hosted only)

---

## User Personas

### Persona 1: Alex - The Curious Developer

**Background**: Full-stack developer, comfortable with code, new to AI agents
**Goal**: Quickly set up an agent workflow for a side project
**Pain**: Doesn't want to spend hours learning a new tool's conventions
**Needs**: Fast setup, sensible defaults, ability to customize later

### Persona 2: Sam - The Technical PM

**Background**: Product manager with technical background, writes specs not code
**Goal**: Set up agent workflows for the team to use
**Pain**: Terminal commands are intimidating, YAML syntax is error-prone
**Needs**: Visual interface, clear explanations, export to GitHub for devs

### Persona 3: Jordan - The Team Lead

**Background**: Engineering lead standardizing team workflows
**Goal**: Create consistent agent templates for the team
**Pain**: Every team member sets things up differently
**Needs**: Shareable configurations, best practice defaults, team templates

---

## Feature Requirements

### Phase 1: Core Visual Builder (MVP)

#### F1.1: Project Setup Wizard

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1 of 3: Project Setup                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Project Name                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ my-agent-workflow                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Description                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ AI-powered code review and documentation system          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Starter Template                                                │
│  ○ Minimal (just the basics)                                    │
│  ● Standard (recommended for most projects)                     │
│  ○ Full (all features enabled)                                  │
│                                                                  │
│  Integrations                                                    │
│  ☑ GitHub Actions (CI/CD)                                       │
│  ☐ Linear (task management)                                     │
│  ☐ Slack notifications                                          │
│                                                                  │
│                                        [Back]  [Next: Agents →] │
└─────────────────────────────────────────────────────────────────┘
```

**Requirements**:
- Text inputs for project name and description
- Template selection (minimal/standard/full)
- Integration toggles
- Validation and helpful error messages

#### F1.2: Visual Agent Builder

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 2 of 3: Define Your Agents                    [+ Add New] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─ code-reviewer ──────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ │   │
│  │  │ Steps           │ │ Input           │ │ Tools       │ │   │
│  │  │                 │ │                 │ │             │ │   │
│  │  │ 1. Read PR diff │ │ ☑ Local files   │ │ ☑ Read      │ │   │
│  │  │ 2. Analyze code │ │ ☑ GitHub PRs    │ │ ☑ Grep      │ │   │
│  │  │ 3. Write review │ │ ☐ Web pages     │ │ ☑ Write     │ │   │
│  │  │                 │ │                 │ │ ☐ Bash      │ │   │
│  │  │ [+ Add step]    │ ├─────────────────┤ │ ☐ WebFetch  │ │   │
│  │  │                 │ │ Output          │ │             │ │   │
│  │  │                 │ │                 │ │             │ │   │
│  │  │                 │ │ ☑ Review file   │ │             │ │   │
│  │  │                 │ │ ☑ PR comments   │ │             │ │   │
│  │  │                 │ │ ☐ Slack msg     │ │             │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────┘ │   │
│  │                                              [Edit] [Delete] │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Suggested Agents:  [+ Code Reviewer] [+ Test Runner] [+ Planner]│
│                                                                  │
│                                        [← Back]  [Next: Deploy →]│
└─────────────────────────────────────────────────────────────────┘
```

**Requirements**:
- Card-based agent display
- Three-panel layout per agent (Steps / Input+Output / Tools)
- Drag-and-drop step reordering
- Tool selection with automatic dependency hints
- Pre-built agent templates ("Suggested Agents")
- Add/edit/delete agents
- Real-time preview of generated markdown

#### F1.3: Deploy & Export

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 3 of 3: Deploy Your Project                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  How would you like to get your project?                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ⭐ Deploy to GitHub (Recommended)                       │    │
│  │                                                          │    │
│  │  Creates a new repository with your configuration.       │    │
│  │  You'll be able to clone it and start working right away.│    │
│  │                                                          │    │
│  │  [Connect GitHub Account]                                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  📦 Download as ZIP                                      │    │
│  │                                                          │    │
│  │  Download the complete project to set up manually.       │    │
│  │                                                          │    │
│  │  [Download project.zip]                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  📋 Copy Configuration                                   │    │
│  │                                                          │    │
│  │  Copy the generated files to paste into existing project.│    │
│  │                                                          │    │
│  │  [View Files] [Copy All]                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│                                              [← Back]  [Finish] │
└─────────────────────────────────────────────────────────────────┘
```

**Requirements**:
- GitHub OAuth integration for direct repo creation
- ZIP download with complete project structure
- Copy-to-clipboard for individual files
- Post-deploy instructions (what to do next)

#### F1.4: Preview Panel

```
┌─────────────────────────────────────────────────────────────────┐
│  Preview: code-reviewer.md                         [Raw] [Formatted]│
├─────────────────────────────────────────────────────────────────┤
│  ---                                                             │
│  name: code-reviewer                                             │
│  description: Reviews PRs for code quality                       │
│  model: claude-sonnet-4-20250514                                       │
│  tools:                                                          │
│    - Read                                                        │
│    - Grep                                                        │
│    - Write                                                       │
│  ---                                                             │
│                                                                  │
│  # Code Reviewer Agent                                           │
│                                                                  │
│  ## Steps                                                        │
│  1. Read the PR diff and understand the changes                  │
│  2. Analyze code for quality issues, bugs, and improvements      │
│  3. Write a comprehensive review with actionable feedback        │
│                                                                  │
│  ## Inputs                                                       │
│  - Local files (source code)                                     │
│  - GitHub PR information                                         │
│                                                                  │
│  ## Outputs                                                      │
│  - Review markdown file                                          │
│  - PR comments                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Requirements**:
- Live preview as user edits
- Toggle between raw markdown and formatted view
- Syntax highlighting for YAML frontmatter
- Copy button for quick export

### Phase 2: Enhanced Features

#### F2.1: Agent Templates Library
- Curated collection of production-ready agents
- Community-contributed templates
- One-click import into project
- Categories: Code Review, Testing, Documentation, Planning, etc.

#### F2.2: Workflow Builder
- Visual canvas for connecting agents
- Define handoff points between agents
- Trigger conditions (on PR, on commit, scheduled)
- Export as GitHub Actions workflow

#### F2.3: Configuration Validator
- Real-time validation of agent definitions
- Warnings for common mistakes
- Suggestions for improvements
- Compatibility checks with target tools

### Phase 3: Team & Enterprise

#### F3.1: Team Workspaces
- Shared agent templates
- Role-based access control
- Audit logs
- SSO integration

#### F3.2: Self-Hosting
- Docker deployment option
- Air-gapped installation
- Custom branding

---

## Technical Architecture

### Option A: Hosted SaaS (Recommended for MVP)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vercel)                         │
│                     React/Next.js + TailwindCSS                  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API (Vercel)                        │
│                    Next.js API Routes / Edge                     │
├─────────────────────────────────────────────────────────────────┤
│  • Project generation logic                                      │
│  • Template rendering                                            │
│  • GitHub OAuth flow                                             │
│  • Repository creation via GitHub API                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │  GitHub   │  │ Analytics │  │  Storage  │
        │   API     │  │ (Posthog) │  │ (optional)│
        └───────────┘  └───────────┘  └───────────┘
```

**Tech Stack**:
- **Frontend**: Next.js 14+, React, TailwindCSS, shadcn/ui
- **Backend**: Next.js API routes (serverless)
- **Auth**: NextAuth.js with GitHub OAuth
- **Hosting**: Vercel (free tier sufficient for MVP)
- **Analytics**: PostHog or Plausible

**Why This Stack**:
- Zero infrastructure to manage
- Free hosting for MVP scale
- Fast iteration with hot reload
- Built-in API routes (no separate backend)
- Excellent GitHub integration ecosystem

### Option B: Static Site + GitHub Actions

For maximum simplicity, the tool could be entirely client-side:

```
┌─────────────────────────────────────────────────────────────────┐
│                   Static Frontend (Vercel/Netlify)               │
│                        React + TailwindCSS                       │
├─────────────────────────────────────────────────────────────────┤
│  • All generation happens in browser                             │
│  • Exports ZIP file directly                                     │
│  • GitHub OAuth via client-side flow                             │
│  • No backend required                                           │
└─────────────────────────────────────────────────────────────────┘
```

**Pros**: Simpler, cheaper, no backend security concerns
**Cons**: Limited GitHub integration, larger client bundle

### Data Model

```typescript
interface Project {
  id: string;
  name: string;
  description: string;
  template: 'minimal' | 'standard' | 'full';
  integrations: {
    github_actions: boolean;
    linear: boolean;
    slack: boolean;
  };
  agents: Agent[];
  created_at: string;
  updated_at: string;
}

interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  steps: Step[];
  inputs: Input[];
  outputs: Output[];
  tools: Tool[];
}

interface Step {
  id: string;
  order: number;
  description: string;
  details?: string;
}

interface Input {
  type: 'local_files' | 'github_prs' | 'web_pages' | 'apis' | 'databases';
  enabled: boolean;
  config?: Record<string, unknown>;
}

interface Output {
  type: 'files' | 'pr_comments' | 'slack_messages' | 'api_calls';
  enabled: boolean;
  config?: Record<string, unknown>;
}

type Tool = 'Read' | 'Write' | 'Edit' | 'Grep' | 'Glob' | 'Bash' |
            'WebFetch' | 'WebSearch' | 'TodoWrite';
```

---

## User Flows

### Flow 1: New User Creates First Project

```
1. User lands on starter.agentive.dev
2. Clicks "Create Your First Agent Workflow"
3. Step 1: Enters project name, selects "Standard" template
4. Step 2: Adds a "Code Reviewer" agent from suggestions
   - Customizes steps
   - Selects inputs (Local files, GitHub PRs)
   - Chooses tools (Read, Grep, Write)
5. Step 3: Clicks "Deploy to GitHub"
   - Authenticates with GitHub
   - Selects organization/account
   - Confirms repository name
6. Repository created with full project structure
7. User shown "Next Steps" with clone command and quick start guide
8. User clones repo and starts using agents
```

### Flow 2: Experienced User Creates Custom Agent

```
1. User lands on starter.agentive.dev
2. Clicks "Create New Agent" (skips project setup)
3. Builds agent visually:
   - Names it "security-auditor"
   - Defines 5 custom steps
   - Selects advanced tools (Bash, WebFetch)
4. Clicks "Copy Configuration"
5. Pastes into existing project's .claude/agents/ directory
6. Agent ready to use
```

### Flow 3: Team Lead Creates Template

```
1. User creates project with multiple agents
2. Before deploying, clicks "Save as Template"
3. Names template "Backend Team Standard"
4. Shares template link with team
5. Team members can one-click deploy the same configuration
```

---

## Design Principles

### 1. Progressive Disclosure
Show simple options first, reveal advanced settings only when needed. A beginner should be able to complete setup without ever seeing "advanced options."

### 2. Sensible Defaults
Every field should have a good default. Users should be able to click "Next" through the entire flow and get a working project.

### 3. Visual Feedback
Show the generated output in real-time. Users should always see what they're creating, not just what they're configuring.

### 4. Escape Hatches
Power users should be able to:
- Edit raw YAML/markdown directly
- Import existing configurations
- Export in multiple formats

### 5. Educational
The tool should teach agent concepts as users build. Tooltips, examples, and contextual help should explain "why" not just "what."

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| GitHub API rate limits | Medium | Medium | Implement caching, show clear errors |
| OAuth token security | High | Low | Use short-lived tokens, secure storage |
| Generated configs don't work | High | Medium | Extensive testing, validation layer |
| Users expect IDE features | Medium | High | Clear positioning as "setup tool, not IDE" |
| Template drift from source | Medium | Medium | Versioned templates, update notifications |

---

## Open Questions

1. **Naming**: "Agentive Studio" vs "Agent Builder" vs "Workflow Studio"?

2. **Pricing model**: Free forever? Freemium with team features? Usage-based?

3. **Template ownership**: Should users be able to publish templates? Marketplace?

4. **Offline support**: Should the tool work offline (PWA)?

5. **IDE extensions**: Should we build VS Code / Cursor extensions that link to this?

6. **Analytics**: What user behavior do we want to track for improvement?

---

## Implementation Roadmap

### Phase 1: MVP (4-6 weeks)
- [ ] Project setup wizard (F1.1)
- [ ] Basic agent builder (F1.2)
- [ ] ZIP download export (F1.3 partial)
- [ ] Preview panel (F1.4)
- [ ] Landing page and basic docs

### Phase 2: GitHub Integration (2-3 weeks)
- [ ] GitHub OAuth flow
- [ ] Direct repository creation
- [ ] Post-deploy instructions

### Phase 3: Polish & Templates (2-3 weeks)
- [ ] Agent templates library (F2.1)
- [ ] Configuration validator (F2.3)
- [ ] Improved UX based on feedback

### Phase 4: Advanced Features (Future)
- [ ] Workflow builder (F2.2)
- [ ] Team workspaces (F3.1)
- [ ] Self-hosting option (F3.2)

---

## Appendix

### A. Competitive Analysis

| Tool | Approach | Pros | Cons |
|------|----------|------|------|
| create-react-app | CLI wizard | Fast, familiar | Terminal required |
| Vercel Templates | Web + GitHub | One-click deploy | Limited customization |
| Retool | Visual builder | Powerful | Complex, enterprise-focused |
| n8n | Workflow canvas | Visual, flexible | Steep learning curve |

### B. Related Documents

- Agentive Starter Kit README
- Agent Definition Format (.claude/agents/*.md)
- Current onboarding documentation

### C. Wireframe Reference

Original wireframe showing the three-panel agent builder concept:
- Left: Step-by-step instructions
- Center: Input (top) and Output (bottom)
- Right: Tools selection

---

*This PRD is a living document. Update as requirements evolve.*
