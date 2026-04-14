# TASK-AGENT-TEMPLATE-INTEGRATION

**Created**: 2025-10-17
**Status**: PHASE_1_COMPLETE
**Priority**: HIGH
**Assigned**: Feature Developer + Coordinator
**Estimated Effort**: 8-10 hours total
**Phase**: 1 (Template Repo) + 2 (Integration)

---

## Overview

Create a portable agent-roles-template repository and integrate template selection into `adversarial agent onboard` command.

**Goal**: Make agent role definitions reusable across projects via GitHub template repository with minimal friction.

---

## Context

**User Need**: "How can we make a more robust setup for agent roles (feature-developer, test-engineer, etc.), one that can be transported across projects?"

**Reviewer Recommendation**: Ultra-minimal template repository (5 hours) over full package extraction (80-90 hours)

**Current State**:
- `adversarial agent onboard` creates 7 hardcoded agent roles
- Templates embedded in adversarial-workflow package
- No way to customize roles without modifying package

**Desired State**:
- GitHub template repository with standard agent roles
- Users can use standard, minimal, or custom templates
- `adversarial agent onboard` asks which template to use
- Easy to reuse across projects (copy-paste or GitHub template)

---

## Objectives

### Phase 1: Create Template Repository (3-5 hours)
1. Create `github.com/movito/agent-roles-template` repository
2. Extract minimal agent role definitions
3. Write clear README with usage examples
4. Provide 2-3 template variants (standard, minimal)

### Phase 2: Integrate Template Selection (3-5 hours)
5. Update `adversarial agent onboard` to ask for template choice
6. Support built-in, minimal, and custom URL templates
7. Test integration with actual template repository
8. Update documentation

---

## Success Criteria

**Phase 1 (Template Repository)**:
- ✅ Repository created and public
- ✅ `agent-handoffs.json` template with standard 7 roles
- ✅ `agent-handoffs-minimal.json` template with 3 roles
- ✅ README explains usage (under 500 lines)
- ✅ 2 example projects showing usage
- ✅ Can copy-paste template and use immediately

**Phase 2 (Integration)**:
- ✅ `adversarial agent onboard` asks "Customize agent roles?" (optional)
- ✅ Supports 4 choices: Standard (default), Minimal, Custom URL, Skip
- ✅ Fetches template from GitHub if custom URL provided
- ✅ Falls back to built-in templates if fetch fails
- ✅ Documentation updated in README.md + QUICK_START.md

---

## Design: Template Selection Flow

### User Experience

```bash
$ adversarial agent onboard

🤖 Agent Coordination System Setup
ℹ️  Extends adversarial-workflow with agent coordination

Agent Roles:
  Standard setup includes 7 agent roles (coordinator, feature-developer,
  test-runner, document-reviewer, api-developer, format-developer, media-processor)

Customize agent roles? [n]: _

# If user presses Enter or types 'n':
→ Uses built-in standard 7-role template

# If user types 'y':

  1. Minimal (3 roles: coordinator, developer, reviewer)
  2. Custom URL (your own agent-roles-template repository)
  3. Skip agent roles (manual setup later)

Choice [1]: _

# Choice 1: Uses built-in minimal template
# Choice 2: Prompts for URL, fetches from GitHub
# Choice 3: Skips agent-handoffs.json creation
```

### Implementation Logic

```python
def agent_onboard(project_path: str = ".") -> int:
    # ... prerequisite checks ...

    # NEW: Template selection
    template_config = select_agent_template()
    # Returns: {'type': 'standard'|'minimal'|'custom'|'skip', 'url': None|str}

    # ... existing setup flow ...

    # MODIFIED: Render templates based on selection
    if template_config['type'] != 'skip':
        render_agent_template(template_config)

    # ... rest of setup ...
```

---

## Phase 1: Template Repository Structure

### Repository: `github.com/movito/agent-roles-template`

```
agent-roles-template/
├── README.md                          # Quick start + examples (~500 lines)
├── LICENSE                            # MIT License
├── .github/
│   └── FUNDING.yml                    # Optional sponsorship
│
├── templates/
│   ├── agent-handoffs-standard.json   # 7 roles (current default)
│   ├── agent-handoffs-minimal.json    # 3 roles (coordinator, developer, reviewer)
│   └── agent-handoffs-custom.json     # Example for customization
│
├── examples/
│   ├── basic-usage/
│   │   └── .agent-context/
│   │       └── agent-handoffs.json    # Real-world example
│   └── multi-agent-workflow/
│       └── .agent-context/
│           └── agent-handoffs.json    # Parallel agents example
│
└── docs/
    ├── ROLE-DEFINITIONS.md            # Detailed role descriptions
    └── CUSTOMIZATION-GUIDE.md         # How to create custom roles
```

### Template Content

#### `templates/agent-handoffs-standard.json` (7 roles)
```json
{
  "meta": {
    "version": "1.0.0",
    "template": "standard",
    "project": "{{PROJECT_NAME}}",
    "purpose": "Multi-role agent coordination",
    "last_checked": "{{DATE}}"
  },
  "coordinator": {
    "current_focus": "Available for assignment",
    "task_file": "None",
    "status": "available",
    "priority": "high",
    "dependencies": "None",
    "deliverables": [],
    "technical_notes": "Coordination and planning",
    "coordination_role": "Task management and agent coordination",
    "last_updated": "{{DATE}}"
  },
  "feature-developer": { ... },
  "test-runner": { ... },
  "document-reviewer": { ... },
  "api-developer": { ... },
  "format-developer": { ... },
  "media-processor": { ... }
}
```

#### `templates/agent-handoffs-minimal.json` (3 roles)
```json
{
  "meta": {
    "version": "1.0.0",
    "template": "minimal",
    "project": "{{PROJECT_NAME}}",
    "purpose": "Minimal agent coordination",
    "last_checked": "{{DATE}}"
  },
  "coordinator": {
    "current_focus": "Available for assignment",
    "task_file": "None",
    "status": "available",
    "priority": "high",
    "coordination_role": "Task planning and coordination",
    "last_updated": "{{DATE}}"
  },
  "developer": {
    "current_focus": "Available for assignment",
    "task_file": "None",
    "status": "available",
    "priority": "high",
    "coordination_role": "Code implementation",
    "last_updated": "{{DATE}}"
  },
  "reviewer": {
    "current_focus": "Available for assignment",
    "task_file": "None",
    "status": "available",
    "priority": "medium",
    "coordination_role": "Code and documentation review",
    "last_updated": "{{DATE}}"
  }
}
```

### README.md Structure

```markdown
# Agent Roles Template

Portable agent role definitions for Claude Code multi-agent workflows.

## Quick Start (30 seconds)

### Option 1: Use with adversarial-workflow
```bash
adversarial agent onboard
# Choose "Standard" or "Minimal" when prompted
```

### Option 2: Copy-paste
```bash
# In your project:
mkdir -p .agent-context
curl -o .agent-context/agent-handoffs.json \
  https://raw.githubusercontent.com/movito/agent-roles-template/main/templates/agent-handoffs-standard.json

# Replace placeholders:
sed -i 's/{{PROJECT_NAME}}/your-project/g' .agent-context/agent-handoffs.json
sed -i 's/{{DATE}}/2025-10-17/g' .agent-context/agent-handoffs.json
```

### Option 3: GitHub Template
Click "Use this template" button above to create your own customized version.

## Templates Available

### Standard (7 roles)
- **coordinator**: Task planning and coordination
- **feature-developer**: Feature implementation
- **test-runner**: Test execution and validation
- **document-reviewer**: Documentation review
- **api-developer**: API integration
- **format-developer**: File format handling
- **media-processor**: Media file processing

[Download standard template](templates/agent-handoffs-standard.json)

### Minimal (3 roles)
- **coordinator**: Task planning
- **developer**: Code implementation
- **reviewer**: Code/doc review

[Download minimal template](templates/agent-handoffs-minimal.json)

## Usage Examples

### Example 1: Basic Project
[See examples/basic-usage/]

### Example 2: Multi-Agent Workflow
[See examples/multi-agent-workflow/]

## Customization

[See docs/CUSTOMIZATION-GUIDE.md]

## Integration

Works with:
- ✅ adversarial-workflow (automatic integration)
- ✅ Any Claude Code project (copy-paste)
- ✅ Custom build systems (parse JSON)

## FAQ

**Q: Do I need adversarial-workflow to use this?**
A: No. These are just JSON templates. Use them however you want.

**Q: Can I add custom roles?**
A: Yes. Copy a template and add your own role definitions.

**Q: Can I use this with other AI tools?**
A: Yes. The JSON schema is tool-agnostic.
```

---

## Phase 2: Integration with adversarial-workflow

### Code Changes in `cli.py`

#### 1. Add Template Selection Function

```python
def select_agent_template() -> Dict[str, str]:
    """
    Prompt user for agent template selection.

    Returns:
        {'type': 'standard'|'minimal'|'custom'|'skip', 'url': None|str}
    """
    print()
    print(f"{BOLD}Agent Roles:{RESET}")
    print("  Standard setup includes 7 agent roles (coordinator, feature-developer,")
    print("  test-runner, document-reviewer, api-developer, format-developer, media-processor)")
    print()

    customize = prompt_user("Customize agent roles?", default="n")

    if customize.lower() not in ["y", "yes"]:
        return {'type': 'standard', 'url': None}

    print()
    print("  1. Minimal (3 roles: coordinator, developer, reviewer)")
    print("  2. Custom URL (your own agent-roles-template repository)")
    print("  3. Skip agent roles (manual setup later)")
    print()

    choice = prompt_user("Choice", default="1")

    if choice == "1":
        return {'type': 'minimal', 'url': None}
    elif choice == "2":
        url = prompt_user("Template repository URL",
                         default="https://github.com/movito/agent-roles-template")
        return {'type': 'custom', 'url': url}
    elif choice == "3":
        return {'type': 'skip', 'url': None}
    else:
        print(f"{YELLOW}Invalid choice, using standard template{RESET}")
        return {'type': 'standard', 'url': None}
```

#### 2. Add Template Fetching Function

```python
def fetch_agent_template(url: str, template_type: str = 'standard') -> Optional[str]:
    """
    Fetch agent template from URL.

    Args:
        url: Base URL of template repository
        template_type: 'standard' or 'minimal'

    Returns:
        Template content as string, or None if fetch fails
    """
    import urllib.request

    # Construct raw URL
    if 'github.com' in url:
        # Convert github.com URL to raw.githubusercontent.com
        raw_url = url.replace('github.com', 'raw.githubusercontent.com')
        if not raw_url.endswith('/'):
            raw_url += '/'
        raw_url += f"main/templates/agent-handoffs-{template_type}.json"
    else:
        # Assume URL already points to template file
        raw_url = url

    try:
        print(f"  {CYAN}Fetching template from {raw_url}{RESET}")
        with urllib.request.urlopen(raw_url, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"  {YELLOW}⚠️  Could not fetch template: {e}{RESET}")
        print(f"  {YELLOW}⚠️  Falling back to built-in template{RESET}")
        return None
```

#### 3. Update `agent_onboard()` Function

```python
def agent_onboard(project_path: str = ".") -> int:
    # ... existing prerequisite checks (lines 1715-1728) ...

    # NEW: Add template selection (after line 1732, before pre-flight discovery)
    template_config = select_agent_template()

    # ... existing pre-flight discovery (lines 1734-1745) ...

    # ... existing setup flow (lines 1746-1812) ...

    # MODIFIED: Render agent-handoffs.json based on template selection (around line 1889)
    if template_config['type'] != 'skip':
        agent_handoffs_template = None

        # Fetch custom template if URL provided
        if template_config['type'] == 'custom' and template_config['url']:
            content = fetch_agent_template(template_config['url'], 'standard')
            if content:
                # Write directly without rendering (already contains placeholders)
                # Or render if using template variables
                pass

        # Use built-in template
        if template_config['type'] == 'standard':
            agent_handoffs_template = templates_dir / "agent-handoffs.json.template"
        elif template_config['type'] == 'minimal':
            # Need to create agent-handoffs-minimal.json.template in package
            agent_handoffs_template = templates_dir / "agent-handoffs-minimal.json.template"

        if agent_handoffs_template and agent_handoffs_template.exists():
            render_template(
                str(agent_handoffs_template),
                ".agent-context/agent-handoffs.json",
                template_vars
            )
            role_count = "7 roles" if template_config['type'] == 'standard' else "3 roles"
            print(f"  {GREEN}✅{RESET} Created .agent-context/agent-handoffs.json ({role_count})")
        else:
            print(f"  {YELLOW}⚠️{RESET}  Skipped agent-handoffs.json creation")

    # ... rest of function unchanged ...
```

### Package Changes Required

1. **Add minimal template to package**:
   - Create `adversarial_workflow/templates/agent-context/agent-handoffs-minimal.json.template`
   - 3 roles only: coordinator, developer, reviewer

2. **Update documentation**:
   - `README.md`: Add section on agent template customization
   - `QUICK_START.md`: Explain template choices
   - `docs/EXAMPLES.md`: Add example of custom template usage

---

## Tasks Breakdown

### Phase 1: Template Repository (3-5 hours)

**Task 1.1: Create Repository** (30 min)
- [ ] Create `github.com/movito/agent-roles-template` (public)
- [ ] Add MIT License
- [ ] Create directory structure

**Task 1.2: Extract Templates** (1 hour)
- [ ] Create `agent-handoffs-standard.json` (7 roles, current default)
- [ ] Create `agent-handoffs-minimal.json` (3 roles: coordinator, developer, reviewer)
- [ ] Add template variable placeholders ({{PROJECT_NAME}}, {{DATE}})
- [ ] Validate JSON syntax

**Task 1.3: Write Documentation** (2 hours)
- [ ] Write README.md (quick start, examples, FAQ)
- [ ] Create `docs/ROLE-DEFINITIONS.md` (explain each role)
- [ ] Create `docs/CUSTOMIZATION-GUIDE.md` (how to customize)
- [ ] Add usage examples to README

**Task 1.4: Create Examples** (1 hour)
- [ ] `examples/basic-usage/` - Simple single-agent workflow
- [ ] `examples/multi-agent-workflow/` - Parallel agents
- [ ] Test examples work as documented

**Task 1.5: Test & Validate** (30 min)
- [ ] Test copy-paste workflow from README
- [ ] Validate all JSON files
- [ ] Check GitHub template button works
- [ ] Fix any issues found

---

### Phase 2: Integration (3-5 hours)

**Task 2.1: Add Minimal Template to Package** (30 min)
- [ ] Create `adversarial_workflow/templates/agent-context/agent-handoffs-minimal.json.template`
- [ ] Test template renders correctly
- [ ] Update pyproject.toml if needed (package-data)

**Task 2.2: Implement Template Selection** (2 hours)
- [ ] Add `select_agent_template()` function to cli.py
- [ ] Add `fetch_agent_template()` function
- [ ] Update `agent_onboard()` to use template selection
- [ ] Test all 4 paths: standard, minimal, custom URL, skip
- [ ] Add error handling (network failures, invalid JSON, etc.)

**Task 2.3: Update Documentation** (1 hour)
- [ ] Update README.md with template selection section
- [ ] Update QUICK_START.md with template choices
- [ ] Add example to docs/EXAMPLES.md (custom template usage)
- [ ] Update help text in cli.py

**Task 2.4: Testing** (1-1.5 hours)
- [ ] Test standard template (default path)
- [ ] Test minimal template
- [ ] Test custom URL (with actual GitHub template repo)
- [ ] Test skip option
- [ ] Test error handling (invalid URL, network failure)
- [ ] Test on fresh project

**Task 2.5: Update CHANGELOG** (30 min)
- [ ] Document new feature in CHANGELOG.md
- [ ] Note: Agent template selection now available
- [ ] Link to agent-roles-template repository

---

## Timeline

**Phase 1** (Template Repository):
- Week 1, Day 1-2: 3-5 hours
- Can be done independently

**Phase 2** (Integration):
- Week 1, Day 3-4: 3-5 hours
- Depends on Phase 1 completion

**Total**: 6-10 hours over 4 days

---

## Dependencies

**Blocks**:
- None (this is a new feature)

**Depends On**:
- Existing `adversarial agent onboard` implementation (cli.py:1693-2044)
- Template system already in place (render_template function)

**Related**:
- TASK-AGENT-COORDINATE-PHASE-MINUS-1-VALIDATION (cancelled - not extracting full package)

---

## Exit Criteria

**Phase 1 Complete When**:
- ✅ Template repository is public and documented
- ✅ Can copy-paste template into any project
- ✅ README is clear enough for first-time users
- ✅ At least 2 example projects work

**Phase 2 Complete When**:
- ✅ `adversarial agent onboard` asks for template choice
- ✅ All 4 template options work correctly
- ✅ Error handling graceful (falls back to built-in)
- ✅ Documentation updated
- ✅ Feature tested on fresh project

**Overall Success**:
- ✅ User can choose standard, minimal, or custom templates
- ✅ Template can be reused across projects easily
- ✅ Default experience unchanged (press Enter = standard template)
- ✅ No breaking changes to existing users

---

## Notes

**Design Philosophy**:
- **Default = Standard**: 95% of users just press Enter, get 7-role template
- **Non-intrusive**: One optional question, doesn't slow down flow
- **Flexible**: Power users can customize without environment variables
- **Fail-safe**: Custom URL fetch fails → falls back to built-in template

**Alternative Approaches Rejected**:
- ❌ Full package extraction (80-90 hours, premature)
- ❌ Environment variable only (too hidden)
- ❌ Always prompt for each role (too many questions)
- ❌ Git submodule (too complex for users)

**Future Enhancements** (v0.4.0+):
- Agent role marketplace/registry
- More built-in templates (e.g., frontend-focused, backend-focused)
- Template versioning support
- CLI command to list available templates

---

## Related Documents

- `PLAN-AGENT-COORDINATION-PACKAGE-v2.md` - Original extraction plan (superseded by this approach)
- `REVIEWER-CRITIQUE-AGENT-COORDINATION-PACKAGE.md` - Critique that led to minimal approach
- CLI implementation: `adversarial_workflow/cli.py:1693-2044`

---

## Status Updates

**2025-10-17 09:00**: Task created. Ready to start Phase 1 (template repository creation).
**2025-10-17 10:30**: ✅ Phase 1 COMPLETE - Repository created at https://github.com/movito/agent-roles-template
  - Created standard template (7 roles)
  - Created minimal template (3 roles)
  - Wrote comprehensive README with examples
  - Added 2 example projects (basic-usage, multi-agent-workflow)
  - Published to GitHub (988 lines, MIT License)
  - Tested template download - works correctly
  - **Total time**: ~3 hours (estimated 3-5h)

---

**CRITICAL PATH**: This is the practical, minimal solution (6-10 hours) vs. full package extraction (80-90 hours).
