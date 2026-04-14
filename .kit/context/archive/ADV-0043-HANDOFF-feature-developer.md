# ADV-0043 Handoff: Sync Agent Definitions from Upstream

## Task

Replace 11 agent definition files in `.claude/agents/` with their upstream versions from agentive-starter-kit.

## Source

Copy from: `/Users/broadcaster_three/Github/agentive-starter-kit/.claude/agents/`

## Files to Replace (verbatim copy, no modifications)

1. `AGENT-TEMPLATE.md`
2. `OPERATIONAL-RULES.md`
3. `TASK-STARTER-TEMPLATE.md`
4. `agent-creator.md`
5. `ci-checker.md`
6. `document-reviewer.md`
7. `feature-developer.md` (v1 — distinct from feature-developer-v3 which we keep)
8. `onboarding.md`
9. `planner.md` (v1 — distinct from planner2 which we keep)
10. `security-reviewer.md`
11. `test-runner.md`

## Files to NOT Touch

These are our custom agents — do NOT overwrite:
- `code-reviewer.md` (custom PR integration)
- `feature-developer-v3.md` (our active implementation agent)
- `planner2.md` (our active coordinator)
- `pypi-publisher.md` (ADW-specific)

## Implementation

```bash
# 1. Create branch
git checkout -b feature/ADV-0043-sync-agents-upstream

# 2. Start task
./scripts/core/project start ADV-0043

# 3. Copy files
SRC=/Users/broadcaster_three/Github/agentive-starter-kit/.claude/agents
for f in AGENT-TEMPLATE.md OPERATIONAL-RULES.md TASK-STARTER-TEMPLATE.md \
         agent-creator.md ci-checker.md document-reviewer.md \
         feature-developer.md onboarding.md planner.md \
         security-reviewer.md test-runner.md; do
  cp "$SRC/$f" .claude/agents/
done

# 4. Verify no protected files were touched
git diff --name-only | grep -E '(code-reviewer|feature-developer-v3|planner2|pypi-publisher)' && echo "ERROR: Protected file modified!" || echo "OK: Protected files untouched"

# 5. Run CI check
./scripts/core/ci-check.sh

# 6. Commit, push, create PR
```

## PR Details

**Title**: `sync: Update 11 agent definitions from upstream (ADV-0043)`

**Body**: Upstream sync — copied verbatim from agentive-starter-kit. These are template/reference agents. Bot findings about markdown formatting in these files are upstream's concern.

## Bot Review Strategy

These files are copied verbatim from upstream. For bot findings:
- **Dismiss** any formatting/style issues — they're upstream's responsibility
- **Fix** only if a finding reveals an actual integration issue in our repo
