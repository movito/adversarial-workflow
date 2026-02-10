# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Nested evaluator discovery** - Discovery now supports nested library structure (`{provider}/{name}/evaluator.yml`) in addition to flat files. Users who manually copy from the library repo no longer need to flatten files. Flat files take precedence on name conflicts.

### Fixed

- **Script version headers injected during init** - `adversarial init` now dynamically injects `# SCRIPT_VERSION: {version}` into all scripts. This ensures `adversarial check` can verify script versions after upgrade. Previously, templates lacked version headers causing "(no version)" warnings.

## [0.9.6] - 2026-02-09

### Added
- **`--force` flag for init** - `adversarial init --force` now skips confirmation prompts for automated upgrades

### Documentation
- **Python 3.13 incompatibility** - Documented that aider-chat requires Python <3.13
- Updated prerequisites to recommend Python 3.10-3.12
- Added uv instructions for managing Python versions
- Updated UPGRADE.md with complete upgrade path

## [0.9.5] - 2026-02-09

### Fixed
- **Version mismatch** - `__version__` now uses `importlib.metadata.version()` as single source of truth, matching pip metadata

### Technical
- Removed hardcoded version strings from `__init__.py` and `cli.py`
- Version is now derived from `pyproject.toml` via pip metadata

## [0.9.4] - 2026-02-08

### Fixed
- **Suppress browser opening** - Added `--no-browser` flag to all aider invocations to prevent browser from opening to `platform.openai.com/api-keys` during evaluations (ADV-0037)

### Added
- **Script version checking** - `adversarial check` now warns if local `.adversarial/scripts/` are outdated compared to installed package version

### Documentation
- Added upgrade instructions: run `adversarial init --force` after `pip install --upgrade` to update local scripts

## [0.9.3] - 2026-02-07

### Fixed
- **Model field priority** - Explicit `model` field now takes priority over `model_requirement` in evaluator configs (ADV-0032)
- Enables library team to update model IDs without requiring workflow package releases

### Technical
- Updated ModelResolver to check `config.model` before resolving `model_requirement`
- Updated ADR-0005 resolution algorithm documentation

## [0.9.2] - 2026-02-06

### Fixed
- **Lenient output validation** - Evaluations no longer fail when output doesn't contain specific markers (verdict:, approved, etc.). Library evaluators with varied output formats now return exit code 0 when they produce valid content.

### Technical
- Removed strict marker requirement in `validate_evaluation_output()`
- File existence + minimum size (500 bytes) = valid evaluation
- Verdict extraction still attempted but not required

## [0.9.1] - 2026-02-06

### Fixed
- **Suppress `_meta` warnings** - Underscore-prefixed fields (e.g., `_meta` from library install) are now silently ignored instead of triggering "unknown fields" warnings

### Technical
- Follows Python convention: underscore prefix indicates metadata/private fields
- Enables library provenance tracking without parser noise

## [0.9.0] - 2026-02-06

### Added
- **ADV-0031: Library Evaluator Execution** - Run installed evaluators with `--evaluator` flag
  - `adversarial evaluate --evaluator <name> task.md` - Run any installed evaluator
  - `-e` short form for convenience
  - Automatic model resolution via `model_requirement` field
  - Graceful fallback to legacy `model` field if resolution fails
  - Support for evaluator aliases
  - Helpful error messages listing available evaluators
  - Full backward compatibility - no flag uses existing shell script behavior

### Technical
- 388 tests passing (+9 new tests for evaluator execution)
- Reuses existing `run_evaluator()` and `ModelResolver` infrastructure
- Clean separation between CLI parsing and evaluator execution

### Documentation
- Updated README with v0.9.0 features and --evaluator usage
- Added "Running Installed Evaluators" section to Evaluator Library docs

## [0.8.1] - 2026-02-05

### Fixed
- **Category confirmation in CI/CD** - `--category --dry-run` no longer hangs in non-TTY environments
- **Dry-run exit codes** - Dry-run now returns exit code 1 when all evaluator previews fail
- **Config robustness** - Non-dict YAML config files (lists, scalars) no longer crash the library client
- **Library URL configuration** - `ADVERSARIAL_LIBRARY_REF` environment variable now properly configures git ref for library access

### Technical
- 379 tests passing (+5 new tests for BugBot fixes)
- Addresses Cursor BugBot findings from PR #22

## [0.8.0] - 2026-02-05

### Added
- **ADV-0013: Evaluator Library CLI Core** - Full integration with shared evaluator library
  - `adversarial library list` - Browse available evaluators with provider/category filtering
  - `adversarial library install <provider/name>` - Install evaluators from library
  - `adversarial library check-updates` - Check for newer versions of installed evaluators
  - `adversarial library update` - Update installed evaluators to latest versions
  - Provenance tracking header in installed evaluator files
  - Smart caching with configurable TTL (default 1 hour)

- **ADV-0014: Evaluator Library CLI Enhancements** - Quality-of-life improvements
  - `adversarial library info <provider/name>` - Show detailed evaluator information
  - `--dry-run` flag for install/update commands - Preview changes without applying
  - `--category` flag for batch installation - Install all evaluators in a category
  - `--yes` flag for non-interactive mode - CI/CD pipeline support
  - Configuration system via `.adversarial/config.yml` and environment variables
  - `ADVERSARIAL_LIBRARY_URL` - Override default library URL
  - `ADVERSARIAL_LIBRARY_NO_CACHE` - Disable caching
  - `ADVERSARIAL_LIBRARY_CACHE_TTL` - Configure cache duration

- **ADV-0015: Model Routing Layer - Phase 1** - Portable model specifications
  - `ModelRequirement` dataclass for structured model requirements (family/tier/constraints)
  - `ModelResolver` with embedded registry matching 7 model families
  - Dual-field support: both `model` and `model_requirement` work in evaluator YAML
  - 5-step resolution order with graceful fallback and warnings
  - Full backwards compatibility - existing evaluators work unchanged
  - Supported families: claude, gpt, o, gemini, mistral, codestral, llama

### Technical
- New `adversarial_workflow/library/` module with client, cache, commands, config, models
- New `adversarial_workflow/evaluators/resolver.py` for model resolution
- Extended `EvaluatorConfig` with `model_requirement` field
- 374 tests passing (264 new tests for library and model routing)

### Documentation
- ADR-0004: Model routing layer architecture
- ADR-0005: Interface contract with evaluator library team

## [0.7.0] - 2026-02-01

### Added
- **Citation Verification Workflow** - New feature to check all URLs in documents before evaluation
  - New `adversarial check-citations` CLI command
  - `--check-citations` flag for evaluators
  - Async parallel URL checking (up to 100 URLs in <30 seconds)
  - 4 status categories: ✅ Available, ⚠️ Blocked, ❌ Broken, 🔄 Redirect
  - 24-hour caching to reduce repeated checks
  - Bot detection (captcha, cloudflare, access denied pages)
  - Task generation for manual verification of blocked URLs
  - `--output-tasks` flag to generate markdown checklists
  - `--mark-inline` flag to annotate URLs with status badges

### Dependencies
- Added `aiohttp>=3.8.0` for async HTTP requests

### Documentation
- Added ADR-0014: Agent-Evaluator Interaction Patterns
- Added URL auto-scraping addendum to ADR-0011

## [0.6.6] - 2026-01-29

### Fixed

- **Custom evaluator runner now includes --no-detect-urls** - Applied the URL auto-scraping fix to `evaluators/runner.py`, completing the fix for custom/YAML-defined evaluators (mistral-fast, codestral-code, etc.)

## [0.6.5] - 2026-01-29

### Fixed
- **Template files now include --no-detect-urls** - Applied the URL auto-scraping fix to distributed template files (`adversarial_workflow/templates/*.sh.template`), completing the fix from v0.6.4 which only updated local scripts

## [0.6.4] - 2026-01-29

### Fixed
- **URL auto-scraping disabled** - Added `--no-detect-urls` flag to prevent aider from scraping URLs in task files during evaluations (evaluate_plan.sh, review_implementation.sh, validate_tests.sh)

## [0.6.3] - 2026-01-28

### Added
- **ADV-0029**: Configurable timeout per evaluator
  - New `timeout` field in evaluator YAML (default: 180s, max: 600s)
  - CLI `--timeout` flag overrides YAML config
  - Timeout source logging shows CLI/YAML/default
  - Solves Mistral Large timeout issues on large documents

### Documentation
- Updated `docs/CUSTOM_EVALUATORS.md` with timeout field, examples, and troubleshooting

## [0.6.2] - 2025-01-25

### Fixed
- **ADV-0022**: `adversarial check` now correctly reports .env variable count (was showing "0 variables")
- **ADV-0024**: Custom evaluators with `api_key_env` now properly load keys from .env files
- **ADV-0025**: Removed false warning "Evaluator 'review' conflicts with CLI command" for built-in evaluators
- **ADV-0026**: Fixed subprocess test environment issues with system pytest

### Added
- **ADV-0027**: Full alignment with agentive-starter-kit conventions
  - Added `scripts/` utilities (validate_task_status.py, verify-setup.sh, ci-check.sh)
  - Added `agents/` launch scripts (launch, onboarding, preflight)
  - Added `.agent-context/templates/` and `workflows/` documentation
  - Updated agent definitions with latest conventions
  - Added SETUP.md for project setup instructions

### Improved
- **ADV-0023**: Better exception handling for .env files with encoding issues
- Exception handling uses specific types (FileNotFoundError, PermissionError, ValueError) instead of generic Exception

## [0.6.1] - 2025-01-24

### Fixed
- **ADV-0021**: .env files are now automatically loaded at CLI startup
  - All commands (evaluate, check, custom evaluators) can access .env variables
  - Explicit path resolution ensures correct .env file is loaded from working directory

## [0.6.0] - 2025-01-22

### Added
- **Plugin Architecture**: Define custom evaluators in `.adversarial/evaluators/*.yml`
  - Support for any AI model (GPT-4o, Gemini, Claude, local models)
  - Create domain-specific evaluation criteria
  - Share evaluators across projects
- `adversarial list-evaluators` command to show available evaluators (built-in and local)
- Support for evaluator aliases (e.g., `athena`, `knowledge`, `research` for same evaluator)
- Fallback model support for resilient evaluation
- Full documentation for custom evaluator creation:
  - New `docs/CUSTOM_EVALUATORS.md` comprehensive guide
  - New `docs/examples/athena.yml` example evaluator
  - Updated `README.md` with Custom Evaluators section

### Changed
- Refactored evaluator execution into `adversarial_workflow.evaluators` module
- Dynamic CLI subparser registration for custom evaluators

### Technical
- New `EvaluatorConfig` dataclass for evaluator configuration
- Generic `run_evaluator()` function for all evaluator types
- `discover_local_evaluators()` for YAML-based evaluator discovery

### Maintenance
- Updated GitHub Actions: actions/checkout v4 → v6, actions/setup-python v5 → v6, codecov/codecov-action v4 → v5

## [0.5.0] - 2025-11-29

### Added
- New `adversarial split` command for splitting large task files
  - Split by markdown sections (default) or phases (`--strategy phases`)
  - Dry-run preview (`--dry-run`)
  - Configurable line limits (`--max-lines`)
- Comprehensive test suite (72+ tests)
- CI/CD pipeline with GitHub Actions

### Changed
- **BREAKING**: Python 3.10+ required (was 3.8+)
  - Required by aider-chat dependency

### Fixed
- Python 3.10 compatibility (tomllib → tomli fallback)

## [0.3.2] - 2025-10-19

### Changed

**Terminology Reversion: "Reviewer" → "Evaluator"**

Reverted the v0.2.0 terminology change to eliminate ambiguity with agent roles:

- **Author-Evaluator workflow** (was: Author-Reviewer in v0.2.0-v0.3.1)
- Updated ~20-30 occurrences across documentation and user-facing messages
- **Rationale**:
  - "Reviewer" created ambiguity with "document-reviewer" agent role in multi-agent systems
  - "Evaluator" is more precise: evaluates quality and correctness (not generic "review")
  - Aligns with technical naming (`EVALUATOR_MODEL` environment variable)
  - Users naturally refer to it as "Evaluator"

**Files Updated**:
- Core docs: README.md, QUICK_START.md, docs/TERMINOLOGY.md, docs/EXAMPLES.md
- Workflow docs: docs/WORKFLOW_PHASES.md, docs/INTERACTION_PATTERNS.md, docs/TROUBLESHOOTING.md
- Code: adversarial_workflow/__init__.py, adversarial_workflow/cli.py (line 322 output message)
- Templates: README.template, script templates

**Backward Compatibility**: ✅ No breaking changes
- Config keys unchanged (`evaluator_model`)
- Environment variables unchanged (`EVALUATOR_MODEL`)
- Command names unchanged (`adversarial evaluate`)
- Users can upgrade without any configuration changes

### Added

- **New Section in docs/TERMINOLOGY.md**: "Evaluator vs document-reviewer"
  - Clear distinction between Evaluator (aider-powered QA) and document-reviewer (agent role)
  - Explains these are completely separate concepts in different systems
  - Prevents future confusion in multi-agent contexts

- **Decision Document**: `delegation/decisions/TASK-TERMINOLOGY-001-REVERT-DECISION.md`
  - Full rationale for the terminology reversion
  - Lessons learned from v0.2.0 change
  - Migration strategy and success criteria

### Updated

- **docs/TERMINOLOGY.md** to v2.0:
  - Updated version history: v0.1 (Coordinator/Evaluator) → v0.2 (Author/Reviewer) → v0.3.2 (Author/Evaluator)
  - Moved "Reviewer" (for QA role) to deprecated terms
  - Updated all examples and usage patterns
  - Effective date: 2025-10-19

---

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

[0.9.2]: https://github.com/movito/adversarial-workflow/compare/v0.9.1...v0.9.2
[0.9.1]: https://github.com/movito/adversarial-workflow/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/movito/adversarial-workflow/compare/v0.8.1...v0.9.0
[0.8.1]: https://github.com/movito/adversarial-workflow/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/movito/adversarial-workflow/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/movito/adversarial-workflow/compare/v0.6.6...v0.7.0
[0.6.6]: https://github.com/movito/adversarial-workflow/compare/v0.6.5...v0.6.6
[0.6.5]: https://github.com/movito/adversarial-workflow/compare/v0.6.4...v0.6.5
[0.6.4]: https://github.com/movito/adversarial-workflow/compare/v0.6.3...v0.6.4
[0.6.3]: https://github.com/movito/adversarial-workflow/compare/v0.6.2...v0.6.3
[0.6.2]: https://github.com/movito/adversarial-workflow/compare/v0.6.1...v0.6.2
[0.6.1]: https://github.com/movito/adversarial-workflow/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/movito/adversarial-workflow/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/movito/adversarial-workflow/compare/v0.4.0...v0.5.0
[0.2.0]: https://github.com/movito/adversarial-workflow/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/movito/adversarial-workflow/releases/tag/v0.1.0
