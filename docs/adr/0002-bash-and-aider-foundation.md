# ADR-0002: Bash and Aider Foundation

**Status**: Accepted

**Date**: 2025-10-15 (v0.1.0)

**Deciders**: Fredrik Matheson

## Context

The adversarial workflow requires a technical foundation to orchestrate the multi-phase review process (see ADR-0001). This involves:
- Executing AI evaluations with different models
- Parsing git diffs and test results
- Loading configuration and managing state
- Invoking external tools (git, test runners, AI APIs)
- Generating logs and audit trails

### Forces at Play

**Implementation Language Options:**

Several approaches were possible:

1. **Pure Python package** with direct API calls to OpenAI/Anthropic
2. **Node.js/TypeScript** with AI SDK integration
3. **Bash scripts** calling existing AI CLI tools
4. **Language-agnostic scripts** (shell scripts usable from any environment)

**AI Interaction Options:**

1. **Direct API calls** to OpenAI and Anthropic (custom HTTP client)
2. **AI SDKs** (openai-python, anthropic-python)
3. **Existing AI CLI tools** (aider, sgpt, claude-cli, etc.)
4. **Custom AI wrapper** built specifically for this workflow

### Key Requirements

**Git Integration:**
- Must parse git diffs efficiently
- Need to check git status, branch info
- Should work seamlessly with git workflows
- Standard Unix text processing tools ideal

**Configuration Management:**
- Simple YAML parsing
- Environment variable loading (.env files)
- No complex dependency requirements
- Easy for users to debug and modify

**AI Provider Flexibility:**
- Support multiple AI providers (OpenAI, Anthropic, others)
- Handle API authentication, rate limits, retries
- Manage conversation context appropriately
- Allow different models for different phases

**Developer Experience:**
- Scripts should be readable and modifiable
- Users can understand what's happening
- Debugging should be straightforward
- Minimal dependencies to install

**Platform Support:**
- Works on macOS, Linux, WSL
- Leverages existing Unix tooling
- No need for native Windows support (see ADR-0010)

### Problem Statement

What technical foundation provides:
1. **Simplicity**: Easy to install, understand, and modify
2. **Flexibility**: Works with multiple AI providers and development workflows
3. **Transparency**: Users can see exactly what's happening
4. **Reliability**: Mature tools with proven track records
5. **Git-native**: Seamless integration with git-based workflows

## Decision

Use **Bash scripts** as the orchestration layer and **aider-chat** as the AI interaction layer.

### Architecture

**Layer 1: Python CLI (adversarial_workflow/cli.py)**
- Installation and setup (`adversarial init`)
- Configuration management
- Template rendering
- Health checks and validation
- Command routing

**Layer 2: Bash Scripts (workflow orchestration)**
- Phase 1: `evaluate_plan.sh` - Plan evaluation
- Phase 3: `review_implementation.sh` - Code review
- Phase 4: `validate_tests.sh` - Test validation
- Configuration parsing (grep/awk for YAML)
- Environment loading (.env files)
- Git operations (diff, status)
- Logging and audit trails

**Layer 3: Aider (AI interaction)**
- Handles OpenAI, Anthropic, and other AI provider APIs
- Manages context windows and token limits
- Provides retry logic and rate limiting
- Supports fresh context per invocation (critical for adversarial separation)

### Why Bash Scripts

1. **Git-Native Operations**
   ```bash
   # Natural git integration
   git diff HEAD > implementation.diff
   git status --porcelain
   git log --oneline -1
   ```

2. **Unix Text Processing**
   ```bash
   # Simple YAML parsing without external libraries
   EVALUATOR_MODEL=$(grep 'evaluator_model:' config.yml | awk '{print $2}')

   # Environment variable loading
   export $(grep -v '^#' .env | xargs)
   ```

3. **Transparency**: Users can read and understand the scripts
   - No compiled code or hidden behavior
   - Easy to debug with standard tools (bash -x)
   - Modifications don't require rebuilding

4. **Simplicity**: Minimal dependencies
   - Standard Unix tools (grep, awk, cat)
   - Git (already required for workflow)
   - Bash 3.2+ (ships with macOS, Linux)

5. **Reliability**: Battle-tested Unix tools
   - grep, awk, bash have decades of maturity
   - Predictable behavior across systems
   - Well-documented and widely understood

### Why Aider-Chat

1. **Multi-Provider Support**
   - OpenAI GPT models (GPT-4, GPT-4 Turbo, GPT-4o)
   - Anthropic Claude models (Claude 3.5 Sonnet, Opus, Haiku)
   - Open-source models (via APIs)
   - Other providers (Azure, AWS Bedrock)

2. **Mature API Handling**
   - Automatic retries on failures
   - Rate limit handling
   - Token counting and context management
   - Error handling and recovery

3. **Fresh Context Per Invocation**
   - Each aider call starts with clean slate
   - No shared context between phases
   - Critical for adversarial independence
   - Simple: just call aider with different prompts

4. **Active Development**
   - Maintained by Paul Gauthier
   - Regular updates and improvements
   - Large user community
   - Comprehensive documentation

5. **CLI-Native Design**
   - Perfect for shell script integration
   - Accepts file inputs and prompts
   - Outputs to stdout (easily captured)
   - Exit codes for success/failure

### Integration Pattern

```bash
# Example from review_implementation.sh
aider \
  --model "$EVALUATOR_MODEL" \
  --no-git \
  --yes \
  --message "$(cat <<'EOF'
Analyze this implementation against the plan.
Check for phantom work (TODOs, incomplete code).
...
EOF
)" \
  implementation.diff \
  "$TASK_FILE" \
  2>&1 | tee "$LOG_FILE"
```

**Key features:**
- `--model`: Configurable AI model selection
- `--no-git`: Doesn't modify repository
- `--yes`: Non-interactive mode
- `--message`: Pass evaluation prompt
- File inputs: diff and plan
- Log capture: Full transcript saved

## Consequences

### Positive

**Simplicity:**
- ✅ **Minimal dependencies**: Just Python, Bash, Git, Aider
- ✅ **Transparent operation**: Users can read scripts and understand behavior
- ✅ **Easy debugging**: Standard Unix tools (bash -x, echo, cat)
- ✅ **Modifiable**: Users can customize scripts without rebuilding

**Flexibility:**
- ✅ **Multi-provider AI**: Works with OpenAI, Anthropic, others via aider
- ✅ **Model selection**: Easy to switch models via configuration
- ✅ **Fresh context**: Each aider call is independent (critical for adversarial pattern)
- ✅ **Git integration**: Native git operations throughout

**Reliability:**
- ✅ **Mature tools**: Bash, grep, awk, git have decades of production use
- ✅ **Aider stability**: Actively maintained, large user base
- ✅ **Error handling**: Clear error messages with structured output
- ✅ **Proven architecture**: Battle-tested in thematic-cuts project

**Developer Experience:**
- ✅ **Installation simplicity**: `pip install aider-chat` is the only extra dependency
- ✅ **Familiar tools**: Most developers know Bash and git
- ✅ **Debugging**: Scripts can be run manually for testing
- ✅ **Extensibility**: Easy to add custom phases or modify behavior

### Negative

**Platform Limitations:**
- ⚠️ **No native Windows**: Requires WSL (Windows Subsystem for Linux)
- ⚠️ **Bash requirement**: Must have Bash 3.2+ (not an issue on macOS/Linux)
- ⚠️ **Unix tooling**: Requires grep, awk (standard on Unix systems)

**Dependency on Aider:**
- ⚠️ **External tool dependency**: Package requires aider-chat installation
- ⚠️ **Aider API changes**: Breaking changes in aider could affect workflow
- ⚠️ **Installation friction**: Users must install additional package
- ⚠️ **Version compatibility**: Must document compatible aider versions

**Bash Script Limitations:**
- ⚠️ **Complex parsing**: YAML parsing via grep/awk is brittle
- ⚠️ **Error handling**: Bash error handling less elegant than Python
- ⚠️ **Testing**: Bash scripts harder to unit test than Python code
- ⚠️ **Cross-platform**: Bash syntax can vary slightly across systems

**Maintenance:**
- ⚠️ **Two languages**: Python (CLI) + Bash (workflow) requires maintaining both
- ⚠️ **Script distribution**: Bash scripts must be templated and installed correctly
- ⚠️ **Version synchronization**: Changes may require updates to both Python and Bash

### Neutral

**Architecture Patterns:**
- 📊 Python handles setup and configuration
- 📊 Bash handles workflow orchestration
- 📊 Aider handles AI interactions
- 📊 Clear separation of concerns

**Alternative Approaches Considered** (see below)

## Alternatives Considered

### Alternative 1: Pure Python with Direct API Calls

**Considered:** Implement all phases in Python using openai-python and anthropic-python SDKs directly.

**Advantages:**
- Single language (Python)
- More control over API interactions
- Easier unit testing
- No aider dependency

**Rejected because:**
- ❌ **Reinventing the wheel**: Aider already handles multi-provider APIs, retries, rate limits
- ❌ **Maintenance burden**: Would need to maintain API client code, context management
- ❌ **Less flexibility**: Adding new providers requires code changes
- ❌ **Complexity**: API error handling, token management, model selection all custom
- ❌ **Development time**: Significant effort to match aider's capabilities

### Alternative 2: Node.js/TypeScript with Vercel AI SDK

**Considered:** Build workflow in Node.js/TypeScript using Vercel AI SDK or LangChain.

**Advantages:**
- Modern JavaScript ecosystem
- Rich AI SDK options
- Good async/await support
- Type safety with TypeScript

**Rejected because:**
- ❌ **Additional runtime**: Requires Node.js installation
- ❌ **Dependency bloat**: npm packages tend toward large dependency trees
- ❌ **Git integration**: Less natural than Bash for git operations
- ❌ **Development friction**: Many Python developers less familiar with Node.js
- ❌ **Overkill**: Workflow orchestration doesn't need Node's capabilities

### Alternative 3: Pure Bash with Custom AI Wrapper

**Considered:** Write custom Bash/curl-based AI API client instead of using aider.

**Advantages:**
- No external tool dependencies
- Complete control
- Minimal installation

**Rejected because:**
- ❌ **Massive implementation effort**: API clients, retry logic, context management
- ❌ **Error-prone**: Easy to miss edge cases in HTTP/API handling
- ❌ **Limited provider support**: Each provider needs custom implementation
- ❌ **Reinventing aider**: Would essentially recreate what aider already does well
- ❌ **Maintenance nightmare**: API changes require immediate updates

### Alternative 4: Language-Agnostic with JSON API

**Considered:** Create a JSON API that any language can call, make core logic language-agnostic.

**Advantages:**
- Ultimate flexibility
- Language-agnostic
- Potential for web UI

**Rejected because:**
- ❌ **Over-engineering**: Simple workflow doesn't need complex architecture
- ❌ **Deployment complexity**: API server adds installation/maintenance burden
- ❌ **YAGNI**: "You Aren't Gonna Need It" - premature abstraction
- ❌ **Operational overhead**: Running/monitoring a server for local workflow

## Lessons Learned

### What Works Well

- ✅ **Bash for orchestration**: Simple, transparent, git-native
- ✅ **Aider for AI**: Mature, flexible, well-documented
- ✅ **Template approach**: Scripts installed per-project, easily customizable
- ✅ **Clear separation**: Python (setup) + Bash (workflow) + Aider (AI)

### What We'd Change

- 🔄 **YAML parsing**: grep/awk is brittle, could use `yq` or Python helper
- 🔄 **Error handling**: Bash error handling could be more robust
- 🔄 **Testing**: Need better automated testing for Bash scripts

### Future Considerations

- **YAML parsing improvement**: Consider adding `yq` as optional dependency for robust YAML parsing
- **Aider alternatives**: Monitor AI tool ecosystem for alternatives (Claude CLI, OpenAI CLI)
- **Script testing**: Explore Bash testing frameworks (bats-core, shunit2)
- **Windows support**: If demand exists, could add PowerShell versions of scripts

## Related Decisions

- ADR-0001: Adversarial workflow pattern (why we need orchestration scripts)
- ADR-0003: Multi-stage workflow design (phase structure these scripts implement)
- ADR-0004: Template-based initialization (how scripts are installed)
- ADR-0007: YAML + .env configuration (how scripts load configuration)
- ADR-0010: Platform support strategy (why Bash is acceptable)

## References

- [Aider documentation](https://aider.chat/docs/) - AI pair programming tool
- [Aider GitHub](https://github.com/paul-gauthier/aider) - Source code and issues
- [Bash scripting guide](https://www.gnu.org/software/bash/manual/) - Official Bash manual
- [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/) - Comprehensive guide
- [thematic-cuts project](https://github.com/movito/thematic-cuts) - Real-world usage example

## Revision History

- 2025-10-15: Initial decision (v0.1.0)
- 2025-10-20: Documented as ADR-0002
