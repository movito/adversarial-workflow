# TASK-AGENT-COORDINATE-PHASE-0-MINIMAL-EXTRACTION

**Created**: 2025-10-17
**Status**: BLOCKED
**Priority**: HIGH
**Assigned**: Feature Developer
**Estimated Effort**: 15-20 hours
**Timeline**: 2-3 weeks (time-boxed)

---

## BLOCKED BY

**TASK-AGENT-COORDINATE-PHASE-MINUS-1-VALIDATION** (Must pass validation first)

**DO NOT START** until Phase -1 completes with GO decision (5+ interested users validated)

---

## Overview

**Phase 0: Minimal Extraction** - Extract core agent coordination functionality into standalone `agent-coordinate` package.

**Scope**: Minimal viable package with 3 CLI commands only (init, validate, health)

**Time Box**: 20 hours maximum. If exceeded, reassess scope or cancel extraction.

---

## Context

Following successful validation in Phase -1, this phase extracts the minimal core of agent coordination into a standalone package. Focus is on **schemas + validation + health** only. Defer all advanced features to v0.2.0.

**What's INCLUDED in Phase 0**:
- JSON schemas (agent-handoffs.json, current-state.json)
- 3 CLI commands (init, validate, health)
- Basic templates
- Minimal documentation

**What's DEFERRED to Phase 1**:
- Python library API
- Advanced CLI commands
- Comprehensive testing
- Full documentation

---

## Objectives

1. Create standalone GitHub repository
2. Extract JSON schemas from adversarial-workflow
3. Build minimal CLI (3 commands)
4. Test extraction works independently
5. Validate with 2 beta users
6. Make GO/NO-GO decision for Phase 1

---

## Success Criteria

**MUST ACHIEVE ALL**:
- ✅ GitHub repo created and initialized
- ✅ Package installable via `pip install -e .`
- ✅ `agent-coordinate init` creates .agent-context/ with correct structure
- ✅ `agent-coordinate validate` detects schema errors
- ✅ `agent-coordinate health` runs basic checks
- ✅ Works independently (no adversarial-workflow dependency)
- ✅ 2 beta users successfully initialize projects
- ✅ No critical bugs found
- ✅ Stays within 20-hour time box

**DECISION GATE**:
- **If PASS**: Proceed to Phase 1 (Core Features)
- **If FAIL**: Fold back into adversarial-workflow, document lessons learned

---

## Tasks

### 1. Repository Setup (2 hours)

- [ ] Create GitHub repo: `github.com/movito/agent-coordinate`
  ```bash
  gh repo create movito/agent-coordinate --public \
    --description "Structured multi-agent coordination for Claude Code projects"
  ```
- [ ] Initialize package structure
  ```
  agent-coordinate/
  ├── pyproject.toml
  ├── README.md
  ├── LICENSE (MIT)
  ├── .gitignore
  ├── agent_coordinate/
  │   ├── __init__.py
  │   ├── __main__.py
  │   ├── cli.py
  │   ├── core.py
  │   ├── schemas.py
  │   └── templates/
  └── tests/
      └── __init__.py
  ```
- [ ] Set up pyproject.toml
  ```toml
  [project]
  name = "agent-coordinate"
  version = "0.1.0"
  description = "Structured multi-agent coordination for Claude Code"
  requires-python = ">=3.8"
  dependencies = ["jsonschema>=4.0"]

  [project.scripts]
  agent-coordinate = "agent_coordinate.cli:main"
  ```
- [ ] Add .gitignore (Python, venv, .agent-context/)
- [ ] Create minimal README.md

### 2. Extract JSON Schemas (2-3 hours)

- [ ] Copy template files from adversarial-workflow
  ```bash
  # From adversarial-workflow/adversarial_workflow/templates/agent-context/
  cp agent-handoffs.json.template agent-coordinate/agent_coordinate/templates/
  cp current-state.json.template agent-coordinate/agent_coordinate/templates/
  cp README.md.template agent-coordinate/agent_coordinate/templates/
  cp AGENT-SYSTEM-GUIDE.md agent-coordinate/agent_coordinate/templates/
  ```
- [ ] Add schema versioning to templates
  ```json
  {
    "schema_version": "1.0",
    ...
  }
  ```
- [ ] Remove adversarial-workflow specific references
- [ ] Test templates render correctly

### 3. Implement Schema Validation (3-4 hours)

**File**: `agent_coordinate/schemas.py`

```python
from jsonschema import validate, ValidationError
from typing import Tuple, List
import json

AGENT_HANDOFFS_SCHEMA = {
    "type": "object",
    "required": ["schema_version"],
    "properties": {
        "schema_version": {"type": "string"},
        # ... define full schema
    }
}

CURRENT_STATE_SCHEMA = {
    "type": "object",
    "required": ["schema_version", "project", "version"],
    "properties": {
        "schema_version": {"type": "string"},
        "project": {"type": "string"},
        "version": {"type": "string"},
        # ... define full schema
    }
}

def validate_agent_handoffs(data: dict) -> Tuple[bool, List[str]]:
    """Validate agent-handoffs.json."""
    try:
        validate(instance=data, schema=AGENT_HANDOFFS_SCHEMA)
        return (True, [])
    except ValidationError as e:
        return (False, [str(e)])

def validate_current_state(data: dict) -> Tuple[bool, List[str]]:
    """Validate current-state.json."""
    try:
        validate(instance=data, schema=CURRENT_STATE_SCHEMA)
        return (True, [])
    except ValidationError as e:
        return (False, [str(e)])
```

- [ ] Define AGENT_HANDOFFS_SCHEMA (based on existing structure)
- [ ] Define CURRENT_STATE_SCHEMA
- [ ] Implement validation functions
- [ ] Add clear error messages
- [ ] Test with valid and invalid JSON

### 4. Implement Core Logic (3-4 hours)

**File**: `agent_coordinate/core.py`

```python
import os
import json
from pathlib import Path
from typing import Optional

class Coordinator:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.context_dir = self.project_path / ".agent-context"

    def init(self, project_name: str = "project") -> None:
        """Initialize agent coordination in project."""
        # Create .agent-context/ directory
        # Render templates
        # Write JSON files
        pass

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate agent coordination setup."""
        # Check .agent-context/ exists
        # Validate JSON schemas
        # Return (is_valid, errors)
        pass

    def health_check(self) -> dict:
        """Run health checks on agent coordination."""
        # Check configuration
        # Check schema validity
        # Check agent status freshness
        # Return health report
        pass
```

- [ ] Implement `Coordinator.init()`
- [ ] Implement `Coordinator.validate()`
- [ ] Implement `Coordinator.health_check()`
- [ ] Add error handling
- [ ] Test each function

### 5. Implement CLI (3-4 hours)

**File**: `agent_coordinate/cli.py`

```python
import argparse
import sys
from .core import Coordinator

def main():
    parser = argparse.ArgumentParser(
        prog="agent-coordinate",
        description="Structured multi-agent coordination for Claude Code"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize agent coordination")
    init_parser.add_argument("--project", default="project", help="Project name")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate setup")

    # health command
    health_parser = subparsers.add_parser("health", help="Run health checks")
    health_parser.add_argument("--verbose", action="store_true", help="Detailed output")

    args = parser.parse_args()

    if args.command == "init":
        # Run init
        pass
    elif args.command == "validate":
        # Run validate
        pass
    elif args.command == "health":
        # Run health
        pass
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

- [ ] Implement `init` command handler
- [ ] Implement `validate` command handler
- [ ] Implement `health` command handler
- [ ] Add help text for each command
- [ ] Test CLI commands manually

### 6. Write Minimal Documentation (1-2 hours)

**README.md**:
```markdown
# agent-coordinate

Structured multi-agent coordination for Claude Code projects.

## Quick Start

Install:
```bash
pip install agent-coordinate
```

Initialize:
```bash
cd your-project
agent-coordinate init
```

Validate:
```bash
agent-coordinate validate
```

Health check:
```bash
agent-coordinate health
```

## Documentation

See docs/ for full documentation.
```

- [ ] Write 5-minute quick start
- [ ] Document 3 CLI commands
- [ ] Add installation instructions
- [ ] Link to full documentation (Phase 1)

### 7. Test in Isolated Environment (2-3 hours)

- [ ] Create fresh virtualenv
- [ ] Install package: `pip install -e .`
- [ ] Test in empty directory
  ```bash
  mkdir test-project && cd test-project
  agent-coordinate init
  agent-coordinate validate
  agent-coordinate health
  ```
- [ ] Verify files created correctly
- [ ] Test error scenarios:
  - Missing .agent-context/
  - Corrupt JSON files
  - Invalid schemas
- [ ] Fix any bugs found
- [ ] Document known issues

### 8. Beta Testing (2-3 hours)

- [ ] Identify 2 beta users (from Phase -1 validation)
- [ ] Send installation instructions
- [ ] Ask them to:
  1. Install package
  2. Run `agent-coordinate init` in new project
  3. Run `agent-coordinate validate`
  4. Run `agent-coordinate health`
  5. Report any issues
- [ ] Collect feedback
- [ ] Fix critical bugs
- [ ] Document feedback for Phase 1

### 9. Decision Gate (1 hour)

**Assess Results**:
- [ ] Did extraction work successfully?
- [ ] Did beta users succeed?
- [ ] Are there critical bugs?
- [ ] Is value clear and compelling?
- [ ] Are you still motivated to continue?
- [ ] Did we stay within 20-hour time box?

**Make Decision**:
- **GO**: Proceed to Phase 1 (Core Features) - expect 35-45 hours
- **NO-GO**: Fold back into adversarial-workflow, document lessons

---

## Deliverables

1. **GitHub Repository**: `github.com/movito/agent-coordinate`
2. **Minimal Package**: Installable via pip
3. **CLI Tool**: 3 commands working
4. **Templates**: JSON schemas with versioning
5. **Basic Documentation**: README with quick start
6. **Beta Test Report**: Feedback from 2 users
7. **Decision Document**: GO/NO-GO for Phase 1

---

## Exit Criteria

**If Phase 0 SUCCEEDS**:
- ✅ Create Phase 1 task (Core Features)
- ✅ Set realistic timeline (35-45 hours)
- ✅ Plan testing strategy
- ✅ Update beta users with timeline

**If Phase 0 FAILS**:
- ✅ Document lessons learned
- ✅ Fold extraction back into adversarial-workflow
- ✅ Archive agent-coordinate repo
- ✅ Create "Improve Agent Coordination Docs" task
- ✅ No further extraction work

---

## Time Box Rules

**STRICT 20-HOUR LIMIT**:
- If you hit 20 hours and tasks incomplete → STOP
- Assess: Is scope too large?
- Options:
  1. Scope down further (remove health check?)
  2. Cancel extraction (fold back to adversarial-workflow)
  3. Accept that realistic timeline is 80+ hours (update plan)

**Do NOT continue past 20 hours without reassessing**

---

## Dependencies

**Blocked By**:
- TASK-AGENT-COORDINATE-PHASE-MINUS-1-VALIDATION (must pass)

**Blocks**:
- TASK-AGENT-COORDINATE-PHASE-1-FEATURES
- TASK-AGENT-COORDINATE-PHASE-2-RELEASE

---

## Related Documents

- `PLAN-AGENT-COORDINATION-PACKAGE-v2.md` - Phase 0 details (lines 258-295)
- `TASK-AGENT-COORDINATE-PHASE-MINUS-1-VALIDATION.md` - Prerequisite validation
- `REVIEWER-CRITIQUE-AGENT-COORDINATION-PACKAGE.md` - Critical review

---

## Notes

**Remember**:
- Keep scope MINIMAL (resist feature creep)
- Time-box strictly (20 hours max)
- Beta test with real users (not just you)
- Be okay with cancelling if extraction doesn't work
- Focus on schemas + validation + health ONLY
- Defer everything else to Phase 1

**Questions to Answer**:
- Does extraction work independently?
- Do beta users find value?
- Is it worth continuing to Phase 1?

---

## Status Updates

**2025-10-17**: Task created. BLOCKED by Phase -1 validation. Do not start.

---

**CRITICAL PATH**: This task determines if we proceed with full extraction or fold back into adversarial-workflow.
