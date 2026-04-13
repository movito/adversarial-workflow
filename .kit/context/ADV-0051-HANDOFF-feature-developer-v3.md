# ADV-0051 Handoff: Install Evaluator Library + Custom Evaluators

**Task File**: `delegation/tasks/2-todo/ADV-0051-evaluator-setup-from-dispatch-kit.md`
**Agent**: feature-developer-v3
**Created**: 2026-03-08

## RULES — Read Before Anything Else

1. **Do NOT spawn sub-agents.** Never use the Agent/Task tool. Do all work yourself.
2. **Do NOT modify library-installed evaluator YMLs.** They come from upstream.
3. **Do NOT modify custom evaluator YMLs.** They come from dispatch-kit.
4. **First action**: Create branch and start task (see Step-by-Step below).

## What You're Doing

Three things:
1. Install 22 provider evaluators using `adversarial library install`
2. Copy 5 custom evaluators + link script from dispatch-kit
3. Create an EVALUATION-WORKFLOW.md doc (copy from dispatch-kit, adapt header)

## Current State

- `.adversarial/evaluators/` directory does **not exist** yet
- The project has 3 built-in evaluators (`evaluate`, `proofread`, `review`) — all deprecated
- `adversarial library list` works and shows 22 evaluators available (library v0.5.3)
- No custom evaluators exist in this project

## Step-by-Step Implementation

### Step 1: Create branch and start task

```bash
git checkout -b feature/ADV-0051-evaluator-setup
./scripts/core/project start ADV-0051
```

### Step 2: Create the evaluators directory structure

```bash
mkdir -p .adversarial/evaluators/custom
```

### Step 3: Install 22 provider evaluators via library

```bash
adversarial library install --force --yes \
  google/gemini-flash google/gemini-pro google/gemini-deep google/gemini-code \
  google/code-reviewer-fast google/arch-review-fast \
  openai/arch-review openai/code-reviewer openai/o1-code-review \
  openai/o1-mini-code openai/gpt4o-code openai/fast-check \
  openai/o3-chain openai/gpt5-diversity openai/gpt5-synthesis \
  openai/gpt52-reasoning \
  anthropic/claude-adversarial anthropic/claude-code anthropic/claude-quick \
  mistral/codestral-code mistral/mistral-content mistral/mistral-fast
```

This creates 22 `.yml` files in `.adversarial/evaluators/`.

### Step 4: Copy custom evaluators from dispatch-kit

```bash
cp /Users/broadcaster_three/Github/dispatch-kit/.adversarial/evaluators/custom/*.yml .adversarial/evaluators/custom/
cp /Users/broadcaster_three/Github/dispatch-kit/.adversarial/evaluators/custom/link-custom.sh .adversarial/evaluators/custom/
chmod +x .adversarial/evaluators/custom/link-custom.sh
```

Files you'll get:
1. `architecture-planner.yml` — Forward-looking task plan evaluation (o1)
2. `architecture-planner-fast.yml` — Fast task plan check (Gemini Flash)
3. `architecture-reviewer.yml` — Backward-looking architecture review (o1)
4. `code-reviewer.yml` — Adversarial correctness review (o1)
5. `spec-compliance.yml` — Verify implementation matches spec (Gemini Flash)
6. `link-custom.sh` — Symlinks custom evaluators to evaluators root

### Step 5: Run the link script

```bash
.adversarial/evaluators/custom/link-custom.sh
```

This creates symlinks in `.adversarial/evaluators/` pointing to `custom/*.yml`.

### Step 6: Update .gitignore

Add these lines to `.gitignore` under the existing adversarial section:

```
# Library-installed evaluators (installed per-environment, like node_modules)
.adversarial/evaluators/*.yml
# But DO commit custom evaluators
!.adversarial/evaluators/custom/
```

**Important**: The `!` negation ensures custom evaluators ARE committed even though
`*.yml` in the parent is ignored. The library-installed YMLs should NOT be committed —
they're installed per-environment via `adversarial library install`.

### Step 7: Copy EVALUATION-WORKFLOW.md from dispatch-kit

```bash
cp /Users/broadcaster_three/Github/dispatch-kit/.adversarial/docs/EVALUATION-WORKFLOW.md .adversarial/docs/EVALUATION-WORKFLOW.md
```

This is a 997-line document. Copy it verbatim — do not modify content. It documents:
- Deprecation notice for built-in evaluators
- All available evaluators and their use cases
- Fast/deep pairs pattern
- API key requirements
- Evaluation criteria, verdicts, costs, iteration guidance

### Step 8: Verify

```bash
# Count library-installed evaluators (should be 22 .yml files, not symlinks)
find .adversarial/evaluators -maxdepth 1 -name '*.yml' -not -type l | wc -l

# Count custom evaluators (should be 5 .yml files)
ls .adversarial/evaluators/custom/*.yml | wc -l

# Count symlinks (should be 5, pointing to custom/*.yml)
find .adversarial/evaluators -maxdepth 1 -type l | wc -l

# Verify CLI sees everything
adversarial list-evaluators

# Verify EVALUATION-WORKFLOW.md exists
ls -la .adversarial/docs/EVALUATION-WORKFLOW.md

# Run CI
pytest tests/ -v
```

### Step 9: Commit and PR

**What to commit** (carefully — gitignore should handle this, but verify):
- `.adversarial/evaluators/custom/` (5 YMLs + link script) — YES, commit these
- `.adversarial/docs/EVALUATION-WORKFLOW.md` — YES, commit this
- `.gitignore` changes — YES
- `.adversarial/evaluators/*.yml` (library-installed) — NO, should be gitignored

Check with `git status` that only custom evaluators and docs appear as new files.

## PR Details

- **Branch**: `feature/ADV-0051-evaluator-setup`
- **Title**: `feat: Install evaluator library + custom evaluators (ADV-0051)`
- **Body**:
  ```
  ## Summary
  Installs 22 provider evaluators via `adversarial library install` and adds
  5 custom project evaluators from dispatch-kit v0.4.2.

  Library-installed evaluators are gitignored (installed per-environment).
  Only custom evaluators and the evaluation workflow doc are committed.

  Replaces the file-copy approach from PRs #36/#37 with proper library
  installation. Part of ADV-0039 (upstream sync).
  ```

## Gotchas

- The `link-custom.sh` script uses `cd` internally — run it from any directory,
  it resolves paths relative to itself
- Library evaluators use `_meta:` headers with version info — don't edit these
- The symlinks in `.adversarial/evaluators/` (pointing to `custom/*.yml`) will
  show as untracked — they should be gitignored along with the library YMLs
- Bot reviews may flag the EVALUATION-WORKFLOW.md — dismiss as "upstream sync,
  copied verbatim from dispatch-kit v0.4.2"
