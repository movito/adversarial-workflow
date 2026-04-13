# TASK-SETUP-001: Create Interactive Setup Wizard

**Task ID**: TASK-SETUP-001
**Assigned Agent**: feature-developer
**Reviewer Role**: Pre-implementation plan review + Post-implementation code review
**Created**: 2025-10-16
**Updated**: 2025-10-16
**Status**: revised-and-approved
**Priority**: HIGH
**Impact**: 90% friction reduction in setup experience
**Reviewer Verdict**: NEEDS_REVISION (2025-10-16) → APPROVED (2025-10-16 after revision)

---

## Objective

Create `adversarial-workflow agent onboard` command that sets up agent coordination infrastructure as an extension layer on top of the core adversarial-workflow system. Reduce agent coordination setup time from 3 hours with 8 user interventions to 5 minutes with 4 questions through better automation.

**Architecture**: Extension layer pattern - agent coordination extends adversarial-workflow core (not parallel system).

---

## Background

**Context**: During universal agent system integration session (2025-10-16), the manual setup process took ~3 hours with multiple back-and-forth interactions:
- User had to manually specify directory structure preferences
- Agent discovered issues reactively rather than proactively
- Multiple commits needed due to missed organizational steps
- Aider installation and API key setup required separate steps

**Current Pain Points**:
1. No single entry point for setup
2. Agent makes assumptions instead of asking upfront questions
3. Multiple manual steps (directory creation, file organization, aider setup, API keys)
4. No clear "done" signal or validation

**Desired Experience**:
User runs one command, answers a few questions interactively, and gets a fully configured system with validation.

---

## Requirements

### Functional Requirements

**✅ REVISED AFTER REVIEWER FEEDBACK** (2025-10-16)

**Critical Issues RESOLVED**:
1. ✅ **CLI Integration**: New command `adversarial-workflow agent onboard` (namespace + verb pattern)
2. ✅ **Code Architecture**: Extension layer pattern - builds on top of adversarial-workflow core (not duplication)
3. ✅ **Template Path**: Use existing `adversarial_workflow/templates/` directory (flat structure)
4. ✅ **Migration Safety**: Detailed backup/confirmation flow with rollback instructions
5. ✅ **Scope**: Phase 1 only (8 hours) - aider/API keys deferred to Phase 2

**Architectural Clarity**:

This command is an **EXTENSION LAYER**, not a parallel system:

```
Layer 1 (Core): adversarial-workflow init
  Creates: .adversarial/, tasks/
  Purpose: Multi-stage AI code review

Layer 2 (Extension): adversarial-workflow agent onboard
  Creates: .agent-context/, agents/, delegation/
  Purpose: Agent coordination infrastructure
  Prerequisite: Layer 1 must exist
  Updates: .adversarial/config.yml (task_directory → delegation/tasks/)
```

**Future Vision** (v0.4.0+): Split into separate packages (`adversarial-workflow`, `agent-coordination`, `delegation-system`)

---

### Revised Requirements

1. **Command**: `adversarial-workflow agent onboard`
   - New CLI command in `adversarial_workflow/cli.py`
   - Entry point in setup.py/pyproject.toml

2. **Pre-flight Discovery**:
   - Scan project structure before asking questions
   - Detect existing directories: `.agent-context/`, `agents/`, `delegation/`, `tasks/`
   - Check prerequisites: git, Python version, aider installation
   - Check existing configuration: `.env`, `.adversarial/config.yml`

3. **Interactive Questionnaire** (4 questions max):
   ```
   Q1: Use delegation/tasks/ structure? (Y/n)
   Q2: Organize root docs into docs/? (Y/n)
   Q3: Install aider-chat if missing? (Y/n)
   Q4: Configure API keys now? (y/N)
   ```

4. **Automated Actions**:
   - Create directory structure based on Q1
   - Migrate existing tasks/ to delegation/tasks/ if applicable
   - Organize documentation files if Q2=Y
   - Install aider-chat via pip if Q3=Y and not installed
   - Prompt for API keys interactively (hidden input) if Q4=Y
   - Initialize .agent-context/ with templates:
     - `agent-handoffs.json` (from template)
     - `current-state.json` (from template)
     - `README.md` (from template)
     - `session-logs/` (empty directory)
   - Update .adversarial/config.yml if needed
   - Add .env to .gitignore if not present

5. **Template Substitution**:
   - Replace `{{PROJECT_NAME}}` with `$(basename $PWD)`
   - Replace `{{DATE}}` with current date
   - Replace `{{PYTHON_VERSION}}` with detected Python version
   - Detect existing tasks and populate current-state.json

6. **Verification**:
   - Validate JSON files parse correctly
   - Check all 7 agents initialized in agent-handoffs.json
   - Verify scripts are executable
   - Test that .env loads correctly (if created)
   - Show clear success/failure message

7. **Output Messages**:
   - Show progress during setup (with icons/checkmarks)
   - Display summary of what was created/modified
   - Show clear "✅ Setup complete!" message
   - Provide "Next steps" guidance

### Non-Functional Requirements

1. **User Experience**:
   - Total setup time: < 5 minutes
   - Clear, friendly prompts
   - Sensible defaults (Y for most questions)
   - Can be re-run safely (idempotent where possible)

2. **Error Handling**:
   - Graceful failure if git not initialized (suggest `git init`)
   - Clear error if Python < 3.8
   - Handle permission errors (suggest chmod/sudo)
   - Rollback on critical failures

3. **Documentation**:
   - Update README.md with "Quick Setup for AI Agents" section
   - Document command in CLI help text
   - Add examples to EXAMPLES.md

---

## Technical Approach

### Implementation Steps (REVISED - Extension Layer Pattern)

**Phase 1: Core Agent Onboarding** (~8 hours)

1. **Extract Common Helpers** (1 hour)
   ```python
   # In cli.py - extract from init_interactive() for reuse

   def _prompt_user(question: str, default: str = "") -> str:
       """Interactive prompt with default value."""

   def _create_directories(paths: list[str], verbose: bool = True) -> None:
       """Create directory structure safely."""

   def _render_template(template_path: str, output_path: str, context: dict) -> None:
       """Render template file with variable substitution."""

   def _check_adversarial_initialized() -> bool:
       """Check if adversarial-workflow core is initialized."""
       return os.path.exists(".adversarial/config.yml")
   ```

2. **Create Agent Templates** (in existing `adversarial_workflow/templates/`)
   - `agent-handoffs.json.template`
   - `current-state.json.template`
   - `agent-context-README.md.template`
   - Use existing variable pattern: `{{VARIABLE}}`

3. **Implement CLI Command** (`cli.py`) - Extension Layer Pattern
   ```python
   def agent_onboard() -> int:
       """Set up agent coordination system (Extension Layer).

       Prerequisites:
           - adversarial-workflow init must be run first

       Creates:
           - .agent-context/ (agent coordination)
           - agents/ (agent tools and launchers)
           - delegation/ (task management)

       Updates:
           - .adversarial/config.yml (task_directory → delegation/tasks/)

       Returns:
           0 on success, 1 on failure
       """

       # 1. Check prerequisite (Layer 1 must exist)
       if not _check_adversarial_initialized():
           print(f"{RED}✗{RESET} Adversarial workflow not initialized")
           print(f"  Run: adversarial-workflow init")
           return 1

       print(f"\n{BOLD}{CYAN}🤖 Agent Coordination System Setup{RESET}")
       print(f"{INFO} Extends adversarial-workflow with agent coordination")
       print()

       # 2. Pre-flight discovery
       existing_agent_context = os.path.exists(".agent-context")
       existing_delegation = os.path.exists("delegation")
       existing_tasks = os.path.exists("tasks")

       print(f"{BOLD}Current project structure:{RESET}")
       print(f"  {'✓' if existing_agent_context else '○'} .agent-context/")
       print(f"  {'✓' if existing_delegation else '○'} delegation/")
       print(f"  {'✓' if existing_tasks else '○'} tasks/")
       print()

       # 3. Interactive questions (4 max)
       use_delegation = _prompt_user(
           "Use delegation/tasks/ structure? (recommended)", "Y"
       ).lower() in ["y", "yes", ""]

       organize_docs = _prompt_user(
           "Organize root docs into docs/?", "Y"
       ).lower() in ["y", "yes", ""]

       # 4. Create extension structure
       _create_agent_coordination_structure(use_delegation)

       # 5. Migrate tasks if needed
       if use_delegation and existing_tasks:
           _migrate_tasks_to_delegation()

       # 6. Organize documentation
       if organize_docs:
           _organize_documentation()

       # 7. Update core config to use delegation
       if use_delegation:
           _update_adversarial_config("task_directory", "delegation/tasks/")

       # 8. Verify setup
       _verify_agent_setup()

       # 9. Success message
       print(f"\n{GREEN}✅ Agent coordination setup complete!{RESET}")
       print()
       print(f"{BOLD}Next steps:{RESET}")
       print(f"  1. Review: .agent-context/agent-handoffs.json")
       print(f"  2. Assign tasks to agents")
       print(f"  3. Use: adversarial-workflow agent status")

       return 0
   ```

4. **Implement Migration Safety** - Critical for data operations
   ```python
   def _migrate_tasks_to_delegation() -> bool:
       """Safely migrate tasks/ to delegation/tasks/active/.

       Safety features:
       - Counts files before migrating
       - Creates backup automatically
       - Requires explicit confirmation
       - Preserves backup after migration
       - Provides rollback instructions

       Returns:
           True if migration succeeded, False if skipped/failed
       """
       if not os.path.exists("tasks"):
           print(f"{INFO} No tasks/ directory to migrate")
           return True

       # Count files
       task_files = glob.glob("tasks/**/*.md", recursive=True)

       print(f"\n{BOLD}Migration: tasks/ → delegation/tasks/active/{RESET}")
       print(f"  Found: {len(task_files)} task files")
       print(f"  Backup: tasks.backup/ (auto-created)")
       print()

       migrate = _prompt_user("Proceed with migration?", "Y")
       if migrate.lower() not in ["y", "yes", ""]:
           print(f"{INFO} Skipped - migrate manually later if needed")
           return False

       # Create backup
       print(f"{INFO} Creating backup: tasks.backup/")
       shutil.copytree("tasks", "tasks.backup")
       print(f"{GREEN}✅{RESET} Backup created")

       # Migrate
       print(f"{INFO} Moving tasks/ → delegation/tasks/active/")
       shutil.move("tasks", "delegation/tasks/active-temp")

       # Move contents up one level
       os.makedirs("delegation/tasks/active", exist_ok=True)
       for item in os.listdir("delegation/tasks/active-temp"):
           shutil.move(
               f"delegation/tasks/active-temp/{item}",
               f"delegation/tasks/active/{item}"
           )
       os.rmdir("delegation/tasks/active-temp")

       print(f"{GREEN}✅{RESET} Migration complete")
       print(f"{INFO} Backup preserved at: tasks.backup/")
       print(f"{INFO} Rollback: mv tasks.backup tasks")

       return True
   ```

4. **Template Rendering** (`adversarial_workflow/utils.py`)
   ```python
   def render_template(template_path, context):
       """Replace {{VARIABLES}} with values from context dict."""
       with open(template_path, 'r') as f:
           content = f.read()
       for key, value in context.items():
           content = content.replace(f'{{{{{key}}}}}', value)
       return content
   ```

5. **API Key Handling**
   ```python
   import getpass

   def setup_api_keys():
       """Prompt for API keys with hidden input."""
       openai_key = getpass.getpass('OpenAI API Key (optional, press Enter to skip): ')
       anthropic_key = getpass.getpass('Anthropic API Key (optional, press Enter to skip): ')

       if openai_key or anthropic_key:
           with open('.env', 'w') as f:
               if openai_key:
                   f.write(f'OPENAI_API_KEY={openai_key}\n')
               if anthropic_key:
                   f.write(f'ANTHROPIC_API_KEY={anthropic_key}\n')
           os.chmod('.env', 0o600)  # Secure file permissions
           print('✅ API keys saved securely to .env (permissions: 600)')
   ```

### File Structure

```
adversarial_workflow/
├── cli.py (add agent_setup command)
├── setup_wizard.py (new)
├── templates/
│   └── agent-context/
│       ├── agent-handoffs.json.template
│       ├── current-state.json.template
│       ├── README.md.template
│       └── AGENT-SYSTEM-GUIDE.md
└── utils.py (add render_template)
```

---

## Acceptance Criteria

### Must Have
- [ ] `adversarial agent-setup` command exists and runs
- [ ] Pre-flight check scans project and reports findings
- [ ] Interactive questionnaire asks 4 questions with sensible defaults
- [ ] Creates .agent-context/ with all required files
- [ ] Initializes agent-handoffs.json with 7 agents
- [ ] Handles delegation/ vs tasks/ structure preference
- [ ] Organizes root documentation if requested
- [ ] Installs aider-chat if missing and requested
- [ ] Prompts for API keys with hidden input if requested
- [ ] Verification step validates all created files
- [ ] Shows clear success message with next steps
- [ ] Updates README.md with setup instructions

### Should Have
- [ ] `--yes` flag to accept all defaults (non-interactive mode)
- [ ] `--dry-run` flag to show what would be done
- [ ] Rollback on critical failures
- [ ] Detects and preserves existing .agent-context/ (asks to overwrite)
- [ ] Adds .env and .aider* to .gitignore if not present
- [ ] Colored terminal output (✅ green, ⚠️ yellow, ❌ red)
- [ ] Progress indicators during long operations

### Nice to Have
- [ ] Detects existing tasks/ and offers to migrate
- [ ] Estimates setup time before starting
- [ ] Creates git commit automatically if requested
- [ ] Exports setup log to .agent-context/setup.log

---

## Test Plan

### Unit Tests
1. **T1.1**: `preflight_check()` detects existing directories
2. **T1.2**: `preflight_check()` detects missing prerequisites
3. **T1.3**: `render_template()` substitutes variables correctly
4. **T1.4**: `create_structure()` creates directories correctly
5. **T1.5**: `verify_setup()` validates JSON files

### Integration Tests
1. **T2.1**: Full setup in fresh git repo (happy path)
2. **T2.2**: Setup with existing tasks/ directory (migration)
3. **T2.3**: Setup with existing .agent-context/ (overwrite warning)
4. **T2.4**: Setup with no git repo (error handling)
5. **T2.5**: Setup with --yes flag (non-interactive)
6. **T2.6**: Setup with --dry-run flag (no changes made)

### Manual Testing
1. **T3.1**: Run in real project, verify 5-minute completion time
2. **T3.2**: Verify API key input is hidden (not shown in terminal)
3. **T3.3**: Verify .env file has 600 permissions
4. **T3.4**: Verify success message is clear and helpful

---

## Dependencies

### Code Dependencies
- `click` (CLI framework) - already in requirements
- `PyYAML` (config parsing) - already in requirements
- Standard library: `os`, `shutil`, `json`, `getpass`, `subprocess`

### External Dependencies
- Git (must be available)
- Python 3.8+ (must be installed)
- pip (for aider installation)
- aider-chat (optional, can be installed by wizard)

### Template Dependencies
- AGENT-SYSTEM-GUIDE.md (from universal system - need to package)

---

## Deliverables

1. **Code**:
   - `adversarial_workflow/setup_wizard.py` (new, ~300 lines)
   - `adversarial_workflow/cli.py` (add agent_setup command, +50 lines)
   - `adversarial_workflow/utils.py` (add render_template, +20 lines)

2. **Templates**:
   - `adversarial_workflow/templates/agent-context/agent-handoffs.json.template`
   - `adversarial_workflow/templates/agent-context/current-state.json.template`
   - `adversarial_workflow/templates/agent-context/README.md.template`
   - `adversarial_workflow/templates/agent-context/AGENT-SYSTEM-GUIDE.md`

3. **Tests**:
   - `tests/test_setup_wizard.py` (unit tests, ~200 lines)
   - `tests/test_setup_integration.py` (integration tests, ~150 lines)

4. **Documentation**:
   - Update `README.md` with "Quick Setup for AI Agents" section
   - Update `docs/EXAMPLES.md` with setup examples
   - Update CLI help text

5. **Verification Script**:
   - `agents/tools/verify-integration.sh` (validates setup correctness)

---

## Timeline Estimate (REVISED - Extension Layer Approach)

**Phase 1: Core Agent Onboarding** (v0.3.0)
- **Extract Common Helpers**: 1 hour
- **Create Agent Templates**: 1 hour
- **Implement agent_onboard() Command**: 2 hours
- **Implement Migration Safety**: 1.5 hours
- **Verification & Error Handling**: 1 hour
- **Testing**: 1.5 hours
- **Documentation**: 1 hour
- **Phase 1 Subtotal**: **8 hours** (~1 day)

**Phase 2: Advanced Features** (v0.3.1+ - separate task)
- **Aider Installation Automation**: 1 hour
- **API Key Management Integration**: 1 hour
- **Health Check Integration**: 1 hour
- **Phase 2 Subtotal**: 3 hours

**Total (Phase 1 Only)**: **8 hours** (~1 day)
**Total (Both Phases)**: 11 hours (~1.4 days)

**Effort Reduction**: From 12 hours (original) to 8 hours (focused scope with clearer architecture)

---

## Risk Assessment

### High Risk Areas
- API key security (must use hidden input, secure file permissions)
- Migration of existing tasks/ (data loss risk)
- Overwriting existing .agent-context/ (backup needed)

### Medium Risk Areas
- Cross-platform compatibility (macOS vs Linux paths)
- Error handling (many possible failure points)
- Template rendering (complex substitutions)

### Low Risk Areas
- Directory creation (straightforward)
- JSON validation (standard library)
- CLI integration (established pattern)

---

## Success Metrics

1. **Time Reduction**: Setup time reduced from 3 hours to < 5 minutes (95%+ reduction)
2. **User Interventions**: Reduced from 8 manual steps to 4 questions (50% reduction)
3. **Error Rate**: < 5% of users encounter errors during setup
4. **Satisfaction**: Qualitative feedback indicates "easy" or "very easy" experience

---

## Questions for Reviewer

1. **Scope**: Is the 4-question interactive approach the right balance between automation and user control?
2. **Security**: Is the API key handling approach (getpass + 600 permissions) sufficient? (Phase 2)
3. **Migration**: Should the wizard automatically migrate tasks/ to delegation/tasks/, or require explicit confirmation?
4. **Idempotency**: Should the wizard be fully idempotent (can re-run without issues), or warn on existing setup?
5. **Error Recovery**: Should critical failures trigger rollback, or leave partial setup for manual inspection?
6. **Template Packaging**: Should AGENT-SYSTEM-GUIDE.md be packaged with the tool, or downloaded on first run? (See TASK-SETUP-005)

---

## Reviewer Feedback (2025-10-16)

**Initial Verdict**: NEEDS_REVISION (High Confidence)

**Strengths**:
- Excellent problem identification and UX focus
- Clear objective with measurable metrics (3h → 5min)
- Well-structured questionnaire approach
- Good security considerations (deferred to Phase 2)
- Thorough acceptance criteria

**Critical Issues (RESOLVED)**:
1. ✅ CLI integration conflict → **RESOLVED**: `adversarial-workflow agent onboard` (namespace + verb pattern)
2. ✅ Code duplication → **RESOLVED**: Extension layer pattern with shared helpers (not duplication)
3. ✅ Template location mismatch → **RESOLVED**: Use existing `templates/` directory (flat structure)
4. ✅ Migration underspecified → **RESOLVED**: Detailed backup/confirmation flow with rollback instructions
5. ✅ Scope creep → **RESOLVED**: Phase 1 only (8 hours), advanced features deferred to Phase 2

**Architectural Insight** (2025-10-16):
- Clarified that adversarial-workflow is **core layer** (review system)
- Agent coordination is **extension layer** (builds on core)
- This is not duplication, it's **layering** (prerequisite: core must exist first)
- Future vision: Split into modular packages (v0.4.0+)

**Revised Verdict**: **APPROVED** (after architectural clarification and scope refinement)

**Revised Effort**: 8 hours (Phase 1 only, focused scope with clear layering pattern)

---

## Notes

- This task addresses **Critical Improvement #1** from SETUP-EXPERIENCE-LEARNINGS.md
- **Architecture**: Extension layer pattern - agent coordination extends adversarial-workflow core
- Uses shared helpers, does NOT duplicate existing init_interactive() code
- Complements other setup improvements (TASK-SETUP-002: preflight check, TASK-SETUP-004: health check)
- Should be included in v0.3.0 release (Phase 1 only)
- Phase 2 (aider/API keys) deferred to v0.3.1+
- **Future Vision** (v0.4.0+): Split into modular packages (`adversarial-workflow`, `agent-coordination`, `delegation-system`)

---

**Status**: REVISED-AND-APPROVED - Ready for implementation
**Estimated Effort**: 8 hours (Phase 1 - focused scope)
**Impact**: High - Transforms user experience (3 hours → 5 minutes setup)
**Next Action**: Assign to feature-developer for implementation
**Created**: 2025-10-16 by Coordinator
**Reviewed**: 2025-10-16 by Reviewer (NEEDS_REVISION → APPROVED after revisions)
**Revised**: 2025-10-16 by Coordinator (architectural clarification, scope refinement)
