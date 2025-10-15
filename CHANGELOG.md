# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
