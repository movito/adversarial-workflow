# Upgrade Guide

**Python 3.10+ required** (3.13+ supported since v0.9.10)

---

## Upgrading to v1.0.0

### What Changed

v1.0.0 is primarily a reliability release. If you use Gemini-based evaluators
(e.g., `code-reviewer-fast`, `gemini-flash`, `spec-compliance`), verdict
extraction now works correctly. If you only use o1/GPT-4o evaluators, this
release has no user-facing behavior changes.

**Fixed:**
- **Verdict extraction for bold markdown** — Gemini Flash evaluators wrap
  verdicts in `**FAIL**` or `- **FAIL**: ...`. These are now correctly parsed.
  Previously, the CLI reported `verdict: None` for all Gemini-based evaluators.
- **False-positive verdict matching** — All regex patterns are now
  line-anchored, preventing incidental bold text (e.g., `**FAIL**ure modes`)
  from being misread as a verdict.

**Changed:**
- Verdict pattern priority: keyed patterns (`Verdict: FAIL`) match before
  bare-line patterns (`FAIL`), reducing ambiguity in mixed-format outputs.

### Upgrade Steps

```bash
# From PyPI (when published)
pip install --upgrade adversarial-workflow

# Or from git tag
pip install --upgrade git+https://github.com/movito/adversarial-workflow.git@v1.0.0
```

### Verify

```bash
adversarial --version
# Should show: 1.0.0

# Test that Gemini evaluators now report verdicts
adversarial code-reviewer-fast your-task-file.md
# Should show: verdict: FAIL (or PASS, etc.) instead of verdict: None
```

No `adversarial init --force` needed — this is a Python-only fix.

---

## Upgrading to v0.9.11

### What Changed

Major project restructuring. **No breaking changes to the CLI or evaluators.**
These changes only affect contributors or users who reference internal file
paths.

- **`.kit/` directory migration** — builder infrastructure moved from
  `delegation/` to `.kit/` (tasks, context, templates, ADRs)
- **docs/ consolidation** — 9 subdirectories reduced to 4: `adr/`, `archive/`,
  `guides/`, `reference/`
- **Root declutter** — root reduced from 15 to 9 visible files
- **Version management** — `pyproject.toml` is now the single source of truth
  for version numbers

### Upgrade Steps

```bash
pip install --upgrade git+https://github.com/movito/adversarial-workflow.git@v0.9.11
```

**If you reference internal paths** (e.g., `delegation/tasks/`), update them:

| Old Path | New Path |
|----------|----------|
| `delegation/tasks/` | `.kit/tasks/` |
| `delegation/context/` | `.kit/context/` |
| `docs/decisions/` | `docs/adr/` |
| `docs/guides/`, `docs/proposals/`, etc. | `docs/guides/`, `docs/archive/` |

---

## Upgrading to v0.9.10

### What Changed

**Aider dependency completely removed.** All evaluators now use LiteLLM
directly. This is the largest architectural change since the project's
inception.

- No more `pip install aider-chat` requirement
- Python 3.13+ now supported (aider had pinned `<3.13`)
- `adversarial init` no longer creates `.aider.conf.yml`
- `adversarial check` no longer validates aider installation
- ~420 lines of dead code removed from CLI

### Upgrade Steps

```bash
pip install --upgrade adversarial-workflow

# Remove aider if no longer needed by other projects
pip uninstall aider-chat

# Optional: clean up aider config files in your projects
rm -f .aider.conf.yml .aider.model.settings.yml
```

### Verify

```bash
adversarial check
# Should no longer mention aider

adversarial --version
# Should show: 0.9.10
```

### API Key Configuration

Evaluators now use LiteLLM directly. Set the appropriate API key for your
evaluators:

| Provider | Environment Variable | Example Evaluators |
|----------|---------------------|--------------------|
| OpenAI | `OPENAI_API_KEY` | `code-reviewer`, `arch-review`, `o1-code-review` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-code`, `claude-adversarial`, `claude-quick` |
| Google | `GEMINI_API_KEY` | `gemini-flash`, `gemini-deep`, `code-reviewer-fast` |
| Mistral | `MISTRAL_API_KEY` | `mistral-fast`, `mistral-content` |

---

## Upgrading to v0.9.9

### What Changed

- **Double `.md.md` extension bug fixed** — library evaluator outputs were
  getting `.md.md` instead of `.md`. Affected every project using library
  evaluators.

### Upgrade Steps

```bash
pip install --upgrade git+https://github.com/movito/adversarial-workflow.git@v0.9.9
```

No `adversarial init --force` needed.

### Cleaning Up Old `.md.md` Files

Existing outputs in `.adversarial/logs/` may have the double extension:

```bash
cd .adversarial/logs/
for f in *.md.md; do mv "$f" "${f%.md}"; done
```

Or delete them: `rm -f .adversarial/logs/*.md.md`

---

## Upgrading to v0.9.6

### What Changed

- Browser no longer opens during evaluations (no more `platform.openai.com`
  popups)
- Script version checking warns when local scripts are outdated

### Upgrade Steps

```bash
# Both steps required — fix is in Python code AND shell scripts
pip install --upgrade adversarial-workflow
adversarial init --force
```

### Verify

```bash
adversarial check
# Should show: ✅ Scripts up-to-date (v0.9.6)
```

---

## General Upgrade Process

For any version upgrade:

```bash
# 1. Upgrade package
pip install --upgrade adversarial-workflow
# Or pin to a specific version:
pip install --upgrade git+https://github.com/movito/adversarial-workflow.git@v<VERSION>

# 2. Check if local scripts need updating
adversarial check

# 3. If scripts are outdated:
adversarial init --force

# 4. Verify
adversarial --version
adversarial check
```

### When is `adversarial init --force` needed?

| Version | `init --force` needed? | Reason |
|---------|----------------------|--------|
| 1.0.0 | No | Python-only fix |
| 0.9.11 | No | Internal restructuring only |
| 0.9.10 | No | Python-only (aider removal) |
| 0.9.9 | No | Python-only fix |
| 0.9.8 | No | Python-only fix |
| 0.9.7 | No | Python-only (evaluator discovery) |
| 0.9.6 | **Yes** | Shell script changes (no-browser fix) |
| ≤0.9.5 | **Yes** | Shell script changes |

### Library Evaluators

If you use evaluators from the
[adversarial-evaluator-library](https://github.com/movito/adversarial-evaluator-library):

```bash
# Check for updates
adversarial library check-updates

# Update all installed evaluators
adversarial library update --all
```

---

## Version History

See [CHANGELOG.md](../../CHANGELOG.md) for full version history.

Available release tags: https://github.com/movito/adversarial-workflow/tags
