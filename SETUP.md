# Setup Guide

This guide walks you through setting up adversarial-workflow for development and usage.

---

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+** installed (required for aider compatibility)
   ```bash
   python3 --version  # Should be 3.11 or higher
   ```

2. **Git** installed and configured
   ```bash
   git --version
   ```

3. **API Keys**:
   - **OpenAI API Key** (required for adversarial evaluation)
     - Get at: https://platform.openai.com/api-keys
   - **Anthropic API Key** (for Claude Code)
     - Get at: https://console.anthropic.com/settings/keys

---

## Installation Options

### Option A: Install from PyPI (Recommended for Users)

```bash
pip install adversarial-workflow
```

### Option B: Development Setup

Clone and set up for development:

```bash
# Clone the repository
git clone https://github.com/gmickel/adversarial-workflow.git
cd adversarial-workflow

# Create virtual environment with Python 3.11
python3.11 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

---

## Environment Configuration

### Step 1: Copy Environment Template

```bash
cp .env.template .env
```

### Step 2: Add API Keys

Edit `.env` and add your API keys:

```bash
# Required for evaluation (GPT-4o reviews task specs)
OPENAI_API_KEY=sk-your-openai-key

# Required for Claude operations
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

### Step 3: Verify Configuration

```bash
# Run the check command
adversarial check

# Expected output: All green checkmarks for API keys
```

---

## Serena Setup (Optional)

Serena provides semantic code navigation (go-to-definition, find-references, symbol search).

### Prerequisites

Install `uv` (includes `uvx`):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Run Setup Script

```bash
./.serena/setup-serena.sh adversarial-workflow
```

### Enable Python in Serena

Edit `.serena/project.yml`:

```yaml
project_name: "adversarial-workflow"
languages:
  - python
```

### Verify Serena

```bash
claude mcp list | grep serena
```

---

## API Key Details

### OpenAI API Key

**When needed**: For adversarial evaluation (GPT-4o reviews your task specs).

**Cost**: ~$0.04-0.08 per evaluation. A typical task has 2-3 evaluations.

**To get a key**:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. Add to `.env` as `OPENAI_API_KEY`

### Anthropic API Key

**When needed**: For Claude operations and evaluations.

**To get a key**:
1. Go to https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Copy the key (starts with `sk-ant-`)
4. Add to `.env` as `ANTHROPIC_API_KEY`

---

## Verification Checklist

After setup, verify each component:

### CLI
- [ ] `adversarial --version` shows version
- [ ] `adversarial --help` shows available commands
- [ ] `adversarial check` shows green checkmarks

### Evaluation
- [ ] `.env` contains `OPENAI_API_KEY`
- [ ] `adversarial evaluate <task-file>` runs
- [ ] Results appear in `.adversarial/logs/`

### Development (if applicable)
- [ ] Virtual environment activated
- [ ] `pytest tests/ -v` passes
- [ ] Pre-commit hooks run on commit

### Agents (if using Claude Code)
- [ ] `./agents/launch` shows agent menu
- [ ] `./agents/preflight` runs checks
- [ ] Serena activates (if configured)

---

## Troubleshooting

### Module not found

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall in development mode
pip install -e ".[dev]"
```

### API key not working

```bash
# Verify key is set
echo $OPENAI_API_KEY

# Check .env is loaded
adversarial check
```

### Tests failing

```bash
# Use project's Python
.venv/bin/python -m pytest tests/ -v

# Run specific test
.venv/bin/python -m pytest tests/test_cli.py -v
```

### Pre-commit hooks not running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Quick Start

After setup, try these commands:

```bash
# Check your setup
adversarial check

# See available evaluators
adversarial list-evaluators

# Run an evaluation
adversarial evaluate delegation/tasks/2-todo/<task-file>.md

# Initialize interactive setup (optional)
adversarial init --interactive
```

---

## Getting Help

- **CLI Help**: `adversarial --help`
- **Health Check**: `adversarial health`
- **Documentation**: See `docs/` directory
- **Issues**: https://github.com/gmickel/adversarial-workflow/issues

---

**Setup Guide Version**: 1.0.0
