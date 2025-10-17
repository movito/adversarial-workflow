# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-10-17

### Added
- **Agent Coordination System**: New `adversarial agent onboard` command for multi-agent workflow management
  - Optional extension layer on top of core adversarial-workflow
  - Creates `.agent-context/` directory with agent-handoffs.json, current-state.json, README.md
  - Initializes 7 specialized agent roles (coordinator, api-developer, format-developer, media-processor, test-runner, document-reviewer, feature-developer)
  - Safe task migration from `tasks/` → `delegation/tasks/active/` with automatic backup
  - Interactive questionnaire for delegation structure and documentation organization
  - Template rendering with variable substitution (PROJECT_NAME, DATE, PYTHON_VERSION)
  - JSON validation and comprehensive verification
  - Integration with adversarial-workflow config.yml (task_directory update)
- **Health Check Command**: Comprehensive `adversarial health` command for system diagnostics
  - 7 check categories: Configuration, Dependencies, API Keys, Agent Coordination, Scripts, Tasks, Permissions
  - Health scoring system: (passed/total)*100 with 3-tier classification (>90% healthy, 70-90% degraded, <70% critical)
  - Color-coded output: ✅ (pass), ⚠️ (warn), ❌ (fail), ℹ️ (info)
  - `--verbose` flag for detailed diagnostics with fix recommendations
  - `--json` flag for machine-readable output (CI/CD integration)
  - Git status integration showing modified/untracked file counts
  - Exit codes: 0 (healthy), 1 (errors present)
  - Performance: <2 seconds execution, no network calls
- **AGENT-SYSTEM-GUIDE.md Packaging**: Comprehensive agent coordination guide now packaged with distribution
  - Automatically copied to `.agent-context/` during `adversarial init`
  - 34KB guide covering agent roles, task management, coordination patterns
  - Fully offline-capable, no network dependency
- **Pre-flight Check Script**: Optional `agents/tools/preflight-check.sh` for project validation (Bash 3.2+ compatible)
  - 4 scan categories: Project Structure, Prerequisites, Configuration, Active Work
  - Validates Git, Python, Aider, Bash, jq versions
  - Checks YAML configuration validity and .env security
  - Prioritized recommendations (HIGH > MEDIUM > LOW > INFO)
  - Exit codes: 0 (pass), 1 (critical errors), 2 (major issues)
  - Completes in <5 seconds

### Changed
- **Documentation Structure**: All root-level markdown files organized into `docs/` directory
  - `docs/project-history/` for historical completion summaries
  - Cleaner root directory focused on essential files (README, CHANGELOG, LICENSE)
- **README.md**: Added "Quick Setup for AI Agents" section and updated Commands reference
  - Explains when to use agent coordination (optional extension)
  - Integration benefits and setup workflow documented
- **EXAMPLES.md**: Added Example 11: Multi-Agent Workflows (~250 lines)
  - Comprehensive guide for agent coordination setup
  - 7 agent roles explained with real-world usage patterns
  - Health monitoring and troubleshooting examples
  - Integration patterns between adversarial workflow and agent coordination
- **QUICK_START.md**: Added sections for health check and agent coordination
  - Health check usage examples with verbose and JSON modes
  - Agent onboard setup workflow documentation
  - Pre-flight check script usage (optional)
- **API Key Detection**: `adversarial check` command now loads .env before validation
  - Shows API key source: "(from .env)" or "(from environment)"
  - Displays partial API key preview (first 8 + last 4 chars)
  - Properly handles INFO severity level (doesn't cause failures)

### Fixed
- **Workflow Script Safety**: `evaluate_plan.sh` now prevents runaway code implementation
  - Ensures Reviewer stays in planning mode and doesn't implement code
  - Explicit instructions to avoid TodoWrite and Task tools
  - Clearer boundary between plan evaluation and implementation phases

### Documentation
- New: `.agent-context/AGENT-SYSTEM-GUIDE.md` (34KB comprehensive agent guide)
- New: `docs/EXAMPLES.md` Example 11 (Multi-Agent Workflows, ~250 lines)
- Enhanced: `README.md` with agent coordination quick setup section
- Enhanced: `QUICK_START.md` with health check and agent onboard sections
- Enhanced: `TROUBLESHOOTING.md` with .env detection issue and fix
- New: `agents/tools/README.md` with preflight-check.sh documentation

### Quality & Testing
- All 5 setup tasks completed and moved to `delegation/tasks/completed/`
  - TASK-SETUP-001: Agent onboard command (~10h implementation + documentation)
  - TASK-SETUP-002: Pre-flight check script (~4h)
  - TASK-SETUP-003: Fix adversarial check command (1.5h)
  - TASK-SETUP-004: Health check command (~4-5h)
  - TASK-SETUP-005: Package AGENT-SYSTEM-GUIDE.md (~2h)
- Total development effort: ~21.5-22.5 hours
- All acceptance criteria met (Must Have + Should Have)
- Python syntax validation via ast.parse for all new code
- Comprehensive testing in adversarial-workflow v0.2.3 → v0.3.0 transition

### For AI Agents
This release adds an **optional agent coordination system** as an extension layer on top of adversarial-workflow core. Key features:
- **Extension pattern**: Agent coordination extends (not replaces) core workflow
- **Prerequisite check**: Ensures core workflow initialized before agent onboard
- **Safe migration**: Backs up existing tasks/ before moving to delegation/
- **Health monitoring**: `adversarial health` validates both core and agent coordination setup
- **Flexible adoption**: Use agent coordination when managing multi-agent projects, skip it for single-agent workflows
- **Decision guide**: Clear documentation on when to use vs. when to skip agent coordination

## [0.2.3] - 2025-10-16

### Fixed
- **CRITICAL: Workflow scripts now validate API keys before calling aider**
  - Scripts silently fell back to OpenRouter when no API keys were configured
  - Now explicitly check for `.env` file and validate API keys are present
  - Provide clear error messages with ERROR/WHY/FIX/HELP pattern
  - Direct users to `adversarial init --interactive` to set up API keys
  - Prevents unexpected OpenRouter authentication prompts
  - Affects all three workflow scripts: evaluate_plan.sh, review_implementation.sh, validate_tests.sh

### Changed
- Workflow script error messages now use consistent color-coded formatting
- API key validation happens before any aider calls are made
- Error messages clearly distinguish between "no .env file" vs "empty .env file"

### For AI Agents
This release fixes a critical UX issue where workflow scripts would proceed without API keys and fall back to OpenRouter, causing unexpected authentication prompts. Scripts now fail fast with clear error messages directing users to proper setup.

## [0.2.2] - 2025-10-16

### Added
- **Prerequisites Documentation**: Prominent Prerequisites section in README before Quick Start
  - Explicitly lists all required dependencies (Python, Git, aider-chat, API keys)
  - Platform requirements clearly stated (macOS/Linux/WSL)
  - Installation commands and verification steps provided
  - Addresses agent confusion about undocumented aider-chat dependency
- **Python Module Execution**: `__main__.py` enables `python -m adversarial_workflow` execution
  - Provides alternative execution method for agents
  - 5-line module that imports and calls `cli.main()`
- **Pre-flight Template Validation**: Validates package integrity before initialization
  - Checks all 6 required templates exist before attempting to copy
  - Clear error message structure (WHY/MISSING/FIX/WORKAROUND)
  - Distinguishes package bugs from user configuration errors
  - Prevents cryptic "template rendering failed" errors

### Changed
- README.md: Reorganized with Prerequisites section before Quick Start (+28 lines)
- init() function: Added validation logic at start of execution (+39 lines)

### Fixed
- **Agent Experience**: Agents can now discover all prerequisites upfront instead of through trial-and-error
- **Error Messages**: Missing template errors now provide helpful guidance instead of cryptic failures
- **Execution Methods**: Both `adversarial` CLI and `python -m adversarial_workflow` now supported

### Documentation
- Created tasks/agent-experience-improvements.md with full specification
- Addresses issues identified in .agent-context/AGENT_EXPERIENCE_ADVERSARIAL_WORKFLOW.md

### For AI Agents
This release specifically improves the agent integration experience by:
- Making all prerequisites explicit and discoverable upfront
- Providing multiple execution methods (CLI + python -m)
- Catching package integrity issues early with helpful error messages
- Following the ERROR/WHY/FIX/HELP pattern consistently

## [0.2.1] - 2025-10-16

### Fixed
- **CRITICAL: Missing dotfile templates in distribution**: Added `templates/.*` pattern to package-data in pyproject.toml
  - Now includes `.aider.conf.yml.template` and `.env.example.template` in wheel/sdist
  - Fixes BLOCKING issue where `adversarial init` would fail with missing template errors
  - Reported by agent integration testing
- **Version mismatch in CLI**: Updated cli.py `__version__` from 0.1.0 to 0.2.1
  - `adversarial --version` now correctly shows package version
  - All three version declarations now synchronized (pyproject.toml, __init__.py, cli.py)

### Verification
- All 8 template files verified in wheel distribution (including dotfiles)
- Fresh installation test passed with correct version display
- twine check: PASSED for both wheel and source distribution

## [0.2.0] - 2025-10-16

### Added
- **Interactive Onboarding**: New `quickstart` command for guided first-time setup
- **Enhanced Error Messages**: All errors now follow ERROR/WHY/FIX/HELP pattern for better troubleshooting
- **Platform Detection**: Automatic Windows detection with WSL setup guidance
- **Cost Optimization Documentation**: New Example 10 showing how to reduce token costs in large projects
- **Advanced Examples**: 4 new examples covering real-world scenarios:
  - Example 7: Handling review feedback and iteration cycles
  - Example 8: Working with projects without test suites
  - Example 9: Monorepo and multi-package project workflows
  - Example 10: Token cost optimization strategies
- **Terminology Standards**: Official `docs/TERMINOLOGY.md` defining Author/Reviewer concepts
- **Doctor Command**: New `doctor` alias for `check` command
- **API Key Validation**: Interactive setup validates API keys automatically

### Changed
- **Terminology Standardization**: Updated from "Coordinator/Evaluator" to "Author/Reviewer" pattern (73 fixes across 11 files)
  - More intuitive and aligns with industry-standard code review terminology
  - Eliminates confusion about roles and responsibilities
  - Backward compatible - no breaking changes to configuration files
- **Platform Support Documentation**: Expanded from 13 to 64 lines with comprehensive Windows/WSL guidance
- **User Experience Improvements**: Enhanced welcome screen explaining "Why two AI APIs?"
  - Cost estimates per configuration option
  - Clear explanation of adversarial review benefits
  - Guided decision-making for API setup

### Fixed
- Git repository detection error messages now provide clear step-by-step solutions
- Aider installation errors now include helpful troubleshooting steps
- Timeout errors now explain possible causes and fixes
- Windows platform errors now detect platform and suggest WSL installation

### Documentation
- **README.md**: 221 lines added (platform support, examples, terminology)
- **TERMINOLOGY.md**: 560 lines of official terminology standards
- **EXAMPLES.md**: 18 terminology fixes
- **TROUBLESHOOTING.md**: 15 terminology fixes
- **WORKFLOW_PHASES.md**: 12 terminology fixes

### Quality & Testing
- Zero breaking changes - fully backward compatible with v0.1.0
- All validation checks pass via test-runner agent
- User experience score improved from 4.75/10 to 8.5/10 (average across user archetypes)
- Windows users: 2/10 → 8/10 UX score (+6 points)
- First-time users: 4/10 → 8/10 UX score (+4 points)
- macOS/Linux users: 7/10 → 9/10 UX score (+2 points)

### Reference
- See [PHASE-6-COMPLETION-SUMMARY.md](PHASE-6-COMPLETION-SUMMARY.md) for detailed implementation notes
- Total impact: 992 lines added/modified across 9 files
- Development time: 6.5 hours across 7 phases

## [0.1.0] - 2025-10-15

### Added
- Initial release of adversarial-workflow package
- Core CLI commands: `init`, `check`, `evaluate`, `review`, `validate`
- Multi-stage verification workflow (Plan → Implement → Review → Test → Approve)
- Token-efficient design (10-20x reduction vs. standard Aider usage)
- Non-destructive integration into existing projects
- Configuration via YAML and environment variables
- Template scripts for all workflow phases
- Comprehensive documentation and examples
- Support for macOS and Linux platforms
- MIT License

### Features
- **Phase 1**: Plan evaluation with independent AI review
- **Phase 2**: Implementation with any development method
- **Phase 3**: Code review with phantom work detection
- **Phase 4**: Test validation with objective analysis
- **Phase 5**: Final approval with audit trail
- Tool-agnostic design (works with Claude Code, Cursor, Aider, manual coding)
- Configurable AI models (OpenAI GPT-4o, Anthropic Claude)
- Integration with existing task management and test frameworks

### Documentation
- Comprehensive README with quick start guide
- 6 usage examples covering different workflows
- Troubleshooting guide
- Workflow phases documentation
- Token optimization strategies
- Real-world results from thematic-cuts project (85.1% → 96.9% test pass rate)

---

[0.2.0]: https://github.com/movito/adversarial-workflow/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/movito/adversarial-workflow/releases/tag/v0.1.0
