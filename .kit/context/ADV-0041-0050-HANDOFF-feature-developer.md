# ADV-0041 + ADV-0050 Handoff: Skills, Workflows, and Patterns

## Task

Add skills, workflow docs, patterns.yml, and powertest-runner agent from upstream. All additive — no existing files to conflict with.

## Part 1: Skills (ADV-0041)

Copy 5 skill directories from `/Users/broadcaster_three/Github/agentive-starter-kit/.claude/skills/` to `.claude/skills/`:

```bash
mkdir -p .claude/skills
SRC=/Users/broadcaster_three/Github/agentive-starter-kit/.claude/skills
cp -r "$SRC/bot-triage" .claude/skills/
cp -r "$SRC/code-review-evaluator" .claude/skills/
cp -r "$SRC/pre-implementation" .claude/skills/
cp -r "$SRC/review-handoff" .claude/skills/
cp -r "$SRC/self-review" .claude/skills/
```

### Required Fix: pre-implementation/SKILL.md

The GitHub Actions conclusion values list is incomplete. Find the line with conclusion values and expand to the full set:

**Before** (4 values):
```
conclusion: "success" | "failure" | "cancelled" | "skipped" | null
```

**After** (8 values):
```
conclusion: "success" | "failure" | "cancelled" | "skipped" | "action_required" | "neutral" | "stale" | "timed_out" | null
```

This was a Critical CodeRabbit finding on PR #34.

## Part 2: Workflows & Patterns (ADV-0050)

Copy 4 workflow docs from `/Users/broadcaster_three/Github/agentive-starter-kit/.agent-context/workflows/` to `.agent-context/workflows/`:

```bash
SRC=/Users/broadcaster_three/Github/agentive-starter-kit/.agent-context
cp "$SRC/workflows/EVALUATOR-LIBRARY-WORKFLOW.md" .agent-context/workflows/
cp "$SRC/workflows/PR-SIZE-WORKFLOW.md" .agent-context/workflows/
cp "$SRC/workflows/RESEARCH-QUALITY-STANDARDS.md" .agent-context/workflows/
cp "$SRC/workflows/WORKFLOW-FREEZE-POLICY.md" .agent-context/workflows/
cp "$SRC/patterns.yml" .agent-context/
```

## Part 3: powertest-runner Agent (from ADV-0044)

Copy and fix powertest-runner.md:

```bash
cp /Users/broadcaster_three/Github/agentive-starter-kit/.claude/agents/powertest-runner.md .claude/agents/
```

### Required Fixes for powertest-runner.md:

1. **Serena project name**: Change `mcp__serena__activate_project("...")` to use `"adversarial-workflow"`
2. **Branch creation step**: Ensure the "Starting a Task" section includes `git checkout -b` as the first step before `./scripts/core/project start`

Do NOT add `bootstrap.md` — it's a kit internal, not useful for downstream projects.

## Implementation Steps

```bash
# 1. Create branch
git checkout -b feature/ADV-0041-skills-workflows-patterns

# 2. Start task
./scripts/core/project start ADV-0041

# 3. Copy all files (see Parts 1-3 above)

# 4. Apply fixes:
#    - pre-implementation/SKILL.md: expand conclusion values
#    - powertest-runner.md: Serena project name + branch creation step

# 5. Run CI check
./scripts/core/ci-check.sh

# 6. Commit, push, create PR
```

## PR Details

**Title**: `sync: Add skills, workflow docs, patterns.yml, and powertest-runner (ADV-0041/0050)`

**Body**:
```
## Summary
Adds 5 skill directories, 4 workflow docs, patterns.yml defensive coding
reference, and powertest-runner agent from agentive-starter-kit.

Integration fixes:
- pre-implementation/SKILL.md: adds 4 missing GitHub Actions conclusion values
- powertest-runner.md: correct Serena project name + branch creation step

Part of ADV-0039 (upstream sync).

## Test plan
- [ ] All 5 skills present in .claude/skills/
- [ ] All 4 workflow docs present in .agent-context/workflows/
- [ ] patterns.yml present in .agent-context/
- [ ] powertest-runner.md present in .claude/agents/
- [ ] CI passes
```

## Bot Review Strategy

Most files are copied verbatim from upstream. For bot findings:
- **Dismiss** formatting/style issues in upstream-authored files
- **Fix** only findings related to our integration fixes (conclusion values, Serena name)
