# Universal Agent System v1.0.0

Reusable agent system that works across multiple projects with minimal token consumption.

## Quick Start

```bash
cd agents/
./ca                          # Interactive agent selection
./universal-agent-launcher.sh # Full launcher with context display
```

## Agent Options

- **🔌 API Developer**: Backend systems, API integration, service connections
- **📝 Format Developer**: File formats, data export, standards compliance
- **🎵 Media Processor**: Media analysis, validation, processing pipelines
- **🧪 Test Runner**: Testing, validation, quality assurance
- **📋 Coordinator**: Task management, project coordination
- **📖 Document Reviewer**: Documentation review and quality assurance

## Architecture

### Reusable Components
```
agents/
├── ca                           # Quick selector (universal)
├── universal-agent-launcher.sh  # Main launcher with context
├── config/
│   └── agent-roles.json        # Role definitions (portable)
├── api-developer.sh            # Generic role launchers
├── format-developer.sh         # (work across projects)
└── media-processor.sh
```

### Project-Specific Context
```
.agent-context/
├── project-brief.md            # 50-100 token summary
├── current-state.json          # Machine-readable status
└── agent-handoffs.json         # Role-specific context
```

## Benefits

✅ **Reusable**: Same agent system works across all projects
✅ **Efficient**: ~50-150 tokens vs 500+ tokens for context loading
✅ **Portable**: Copy `agents/` folder to any project
✅ **Evolutionary**: Role definitions improve over time
✅ **Scalable**: Easy to add new roles and project types

## Token Usage

- **Previous system**: 500+ tokens for project understanding
- **Universal system**: 50-150 tokens with equivalent context
- **Savings**: ~70% reduction in context loading tokens

## Usage Examples

### Interactive Selection
```bash
./ca
# Displays project context and role options
# Select by number (1-5)
```

### Direct Launch
```bash
./api-developer.sh      # Launch API developer with project context
./test-runner.sh        # Launch test runner with current tasks
```

### Project Setup
1. Copy `agents/` folder to new project
2. Create `.agent-context/` with project details
3. Update `agent-handoffs.json` for current tasks
4. Agents automatically detect and load context

## Configuration

### Role Definitions (`config/agent-roles.json`)
- Add new roles for any domain
- Customize system prompts and descriptions
- Define project type associations

### Project Context (`.agent-context/`)
- `project-brief.md`: Human-readable project summary
- `current-state.json`: Machine-readable status and tasks
- `agent-handoffs.json`: Role-specific context and assignments

## Evolution Path

The system improves across projects:
- Role definitions become more refined
- Context patterns get optimized
- New agent types added based on needs
- Token efficiency continues improving

Ready for multi-project deployment and continuous enhancement.
