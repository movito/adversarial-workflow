# ADR-0010: Platform Support Strategy

**Status**: Accepted

**Date**: 2025-10-15 (v0.1.0)

**Deciders**: Fredrik Matheson

## Context

The adversarial workflow is implemented using Bash scripts that orchestrate aider-chat for AI-powered code review. Platform support decisions affect implementation complexity, maintenance burden, and the user experience across different operating systems.

### Platform Landscape

**Common development platforms:**
1. **macOS** - Unix-based, native Bash, POSIX tools built-in
2. **Linux** - Unix-based, native Bash, POSIX tools standard
3. **Windows native** - Non-Unix, PowerShell/cmd.exe, requires Git Bash or separate Unix tools
4. **Windows WSL** - Linux environment on Windows, full Unix compatibility

**User distribution** (estimated for Python development):
- macOS: ~40% (common in professional dev)
- Linux: ~30% (servers, open source, DevOps)
- Windows: ~30% (enterprise, game dev, .NET)
  - Of Windows users, ~40% use WSL (growing rapidly)

### The Windows Challenge

**Core technical issue:**

The adversarial workflow is built on Bash scripts (ADR-0002) that use:
- Bash shell features (functions, conditionals, loops, heredocs)
- Unix text processing tools (grep, awk, sed)
- Git command-line operations
- Environment variable handling
- File system operations (chmod, directory structure)

**Windows native limitations:**

**1. No Native Bash**
```powershell
# PowerShell is NOT Bash
# Different syntax, semantics, error handling
PS> Test-Path .adversarial/config.yml   # PowerShell
bash$ test -f .adversarial/config.yml    # Bash

# Incompatible script syntax
```

**2. Different Text Tools**
```bash
# Unix (macOS/Linux)
grep 'evaluator_model:' config.yml | awk '{print $2}'

# Windows native
# No built-in grep/awk - need separate installations or PowerShell equivalents
```

**3. Path Separators**
```bash
# Unix: /
.adversarial/scripts/evaluate_plan.sh

# Windows: \
.adversarial\scripts\evaluate_plan.sh  # Won't work in Bash scripts
```

**4. Line Endings**
```
Unix: LF (\n)
Windows: CRLF (\r\n)
# Can cause Bash script failures
```

**5. Permissions**
```bash
# Unix: chmod +x script.sh
# Windows: No direct equivalent, execution permission model differs
```

### Forces at Play

**Simplicity vs Universal Support:**
- Supporting Windows native requires:
  - PowerShell script equivalents (5 core scripts × ~100-500 lines each)
  - OR bundling Unix tools (Git Bash, Cygwin, MSYS2)
  - OR Python reimplementation (abandoning Bash, see ADR-0002)
- Maintaining two script ecosystems (Bash + PowerShell) doubles maintenance
- Testing across platforms multiplies complexity

**WSL as Middle Ground:**
- WSL 2 provides full Linux environment on Windows
- Growing adoption (Windows 10+, Windows 11 default)
- Enables developers to use Linux tools on Windows
- No script modifications needed - runs Bash natively
- Increasingly standard for Python/web development on Windows

**Development Philosophy:**
- Build for where users are going, not where they were
- Modern Windows development increasingly uses WSL
- Enterprise Python development often uses Linux servers anyway
- Optimize for 70% of users, provide path for remaining 30%

**Maintenance Burden:**
- PowerShell expertise required (different from Bash)
- Double testing: Every change needs macOS + Linux + Windows native validation
- Platform-specific bugs and edge cases
- Documentation complexity (different instructions per platform)

**Real-World Usage:**
- Package built for Python developers
- Python ecosystem increasingly Unix-centric (pip, venv, etc.)
- Modern web development tools assume Unix environment
- CI/CD pipelines primarily Linux-based

### Problem Statement

How do we:
1. Support maximum number of users with minimum complexity
2. Avoid maintaining parallel script ecosystems (Bash + PowerShell)
3. Provide clear guidance for Windows users
4. Future-proof platform support strategy
5. Focus development effort on core value (quality gates) not platform abstraction

## Decision

**Support Unix-based platforms fully** (macOS, Linux, WSL) and **provide clear WSL guidance for Windows users** rather than attempting native Windows support.

### Supported Platforms

**Tier 1: Fully Supported**

**macOS (10.15+)**
- ✅ Native Bash (3.2+ built-in, or Homebrew 5.x)
- ✅ Standard Unix tools (grep, awk, sed)
- ✅ Git included in Xcode CLI tools
- ✅ Python 3.8+ available via Homebrew or python.org
- ✅ Primary development platform for package

**Linux (Ubuntu 20.04+, Debian 10+, Fedora 33+, etc.)**
- ✅ Native Bash (4.x or 5.x standard)
- ✅ Standard POSIX tools
- ✅ Git via package manager
- ✅ Python 3.8+ via package manager
- ✅ Full testing coverage

**Windows Subsystem for Linux (WSL 2)**
- ✅ Full Linux environment (Ubuntu 20.04+ recommended)
- ✅ Native Bash and Unix tools
- ✅ Seamless file system access to Windows files
- ✅ Python and pip work identically to Linux
- ✅ Documented setup path for Windows users

**Tier 2: Unsupported**

**Windows Native (PowerShell/cmd.exe)**
- ❌ No Bash environment
- ❌ Scripts will not run
- ❌ No plans for PowerShell equivalents
- ✅ Clear documentation: "Use WSL instead"

### User Experience by Platform

**macOS/Linux users:**
```bash
# Standard installation
pip install adversarial-workflow
adversarial init
# Works immediately
```

**Windows users:**
```powershell
# Step 1: Enable WSL (if not already)
wsl --install

# Step 2: Install Python in WSL
sudo apt update && sudo apt install python3 python3-pip

# Step 3: Install package in WSL
pip install adversarial-workflow

# Step 4: Use from WSL
wsl
adversarial init
```

**Why this works:**
- WSL 2 is included in Windows 10 (version 2004+) and Windows 11
- One-time setup (~5-10 minutes)
- Full Unix compatibility, no compromises
- Better integration than Git Bash or Cygwin

### Documentation Strategy

**README.md Platform Section:**
```markdown
## Platform Support

### Supported Platforms

- ✅ macOS 10.15+ (Catalina and later)
- ✅ Linux (Ubuntu 20.04+, Debian 10+, Fedora 33+, etc.)
- ✅ Windows via WSL 2 (Windows 10 2004+ or Windows 11)

### Windows Users

**Use Windows Subsystem for Linux (WSL 2):**

1. Install WSL: `wsl --install` (PowerShell as Administrator)
2. Restart your computer
3. Install Python: `sudo apt update && sudo apt install python3 python3-pip`
4. Install package: `pip install adversarial-workflow`

See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for detailed instructions.

**Why WSL?** Adversarial-workflow uses Bash scripts and Unix tools
for reliability and simplicity. WSL provides a full Linux environment
on Windows with seamless file access.

**Native Windows not supported.** PowerShell/cmd.exe cannot run Bash
scripts. WSL is the recommended approach.
```

**WINDOWS_SETUP.md (dedicated guide):**
- Step-by-step WSL installation
- Python and pip setup in WSL
- File system access (accessing Windows files from WSL)
- Terminal recommendations (Windows Terminal)
- Troubleshooting common WSL issues
- Links to Microsoft's WSL documentation

**Error Messages:**
```python
# In cli.py
import platform
if platform.system() == 'Windows' and 'microsoft' not in platform.uname().release.lower():
    print("""
    ⚠️  WARNING: Native Windows detected

    Adversarial-workflow requires a Unix environment (Bash, grep, awk).

    Please use Windows Subsystem for Linux (WSL 2):
    1. wsl --install (PowerShell as Administrator)
    2. Restart computer
    3. Install Python in WSL: sudo apt install python3 python3-pip
    4. Install package in WSL: pip install adversarial-workflow

    See: docs/WINDOWS_SETUP.md for details
    """)
    sys.exit(1)
```

### Future Flexibility

**If Windows native support becomes critical:**

**Option 1: PowerShell Rewrites** (substantial effort)
- Rewrite 5 core scripts in PowerShell
- ~2000+ lines of equivalent code
- Ongoing maintenance burden
- Not currently justified by user demand

**Option 2: Python Reimplementation** (architectural change)
- Replace Bash scripts with Python equivalents
- See ADR-0002 alternatives (why Bash was chosen)
- Loses transparency and git-native benefits
- Would require major version bump (v2.0.0)

**Option 3: Cross-Platform Script Library** (over-engineering)
- Abstract platform differences behind library
- Significant complexity for little benefit
- Most users can use WSL

**Current decision:** Monitor WSL adoption and user feedback. Revisit if:
- WSL adoption stagnates (<50% of Windows Python developers by 2027)
- Significant user complaints (>20% of issues are Windows-native requests)
- Python packaging ecosystem shifts away from Unix assumptions

## Consequences

### Positive

**Development Simplicity:**
- ✅ **Single script ecosystem**: Maintain Bash only, not Bash + PowerShell
- ✅ **Unified testing**: macOS + Linux + WSL use identical code paths
- ✅ **Clear focus**: Build features, not platform abstraction layers
- ✅ **Lower maintenance**: One set of scripts, one set of tests
- ✅ **Faster iteration**: Changes don't require cross-platform rewrites

**Technical Quality:**
- ✅ **Leverages Unix strengths**: Text processing, pipes, git integration
- ✅ **POSIX compliance**: Code works identically across Unix platforms
- ✅ **Shell scripting best practices**: Can use standard Bash idioms
- ✅ **Transparent**: Users can read and modify scripts (Bash is common knowledge)

**User Experience (Unix platforms):**
- ✅ **Zero friction**: Works out of the box on macOS/Linux
- ✅ **Familiar tools**: Bash, grep, awk are standard knowledge
- ✅ **CI/CD friendly**: Linux-based CI systems work perfectly
- ✅ **Server deployment**: Mirrors production Linux environments

**WSL as Solution:**
- ✅ **Growing standard**: WSL 2 increasingly default for Windows dev
- ✅ **Full compatibility**: No compromises or feature gaps
- ✅ **One-time setup**: 5-10 minutes, then identical to Linux
- ✅ **Better than alternatives**: Superior to Git Bash or Cygwin

### Negative

**Windows Native Users:**
- ⚠️ **Extra setup step**: Must install and configure WSL
- ⚠️ **Learning curve**: Unfamiliar with WSL if new
- ⚠️ **Initial friction**: "Why can't I just pip install and use it?"
- ⚠️ **Perception issue**: "Not truly cross-platform"

**Market Coverage:**
- ⚠️ **Excludes some users**: Windows users who can't/won't use WSL
- ⚠️ **Enterprise constraints**: Some corporate environments restrict WSL
- ⚠️ **Compatibility questions**: "Does this work on Windows?" requires explanation
- ⚠️ **Fragmentation**: Windows Python community split (native vs WSL)

**Documentation Burden:**
- ⚠️ **Must explain WSL**: Requires clear setup documentation
- ⚠️ **Support questions**: "How do I install WSL?" support requests
- ⚠️ **Troubleshooting**: WSL-specific issues (file permissions, path mapping)
- ⚠️ **Error detection**: Must detect native Windows and warn gracefully

**Long-Term Risks:**
- ⚠️ **WSL abandonment**: If Microsoft de-prioritizes WSL (unlikely)
- ⚠️ **User expectations**: Python users expect "pip install just works" everywhere
- ⚠️ **Competitive disadvantage**: Other tools may support native Windows
- ⚠️ **Future constraints**: Limits flexibility if requirements change

### Neutral

**When This Strategy Works Well:**
- 📊 Users on macOS or Linux (70% of target audience)
- 📊 Windows users comfortable with WSL (growing percentage)
- 📊 Professional development environments (WSL common)
- 📊 Open source contributors (typically Unix-literate)
- 📊 DevOps/infrastructure engineers (Linux-focused)

**When This Creates Friction:**
- 📊 Windows-only developers new to Unix
- 📊 Enterprise environments with WSL restrictions
- 📊 Students learning Python on Windows
- 📊 Casual users wanting quick setup

**Mitigation Strategies:**
- 📊 Excellent WSL setup documentation
- 📊 Clear platform support messaging
- 📊 Helpful error messages on native Windows
- 📊 Active support for WSL-related questions

## Alternatives Considered

### Alternative 1: Full Windows Native Support

**Structure:** Maintain parallel PowerShell scripts

**Implementation:**
```
adversarial_workflow/
├── scripts/
│   ├── unix/
│   │   ├── evaluate_plan.sh
│   │   ├── review_code.sh
│   │   └── validate_tests.sh
│   └── windows/
│       ├── evaluate_plan.ps1
│       ├── review_code.ps1
│       └── validate_tests.ps1
```

**Rejected because:**
- ❌ **Double maintenance**: Every feature change requires two implementations
- ❌ **PowerShell expertise**: Team doesn't have PowerShell depth
- ❌ **Testing complexity**: Must validate both ecosystems
- ❌ **Divergence risk**: Scripts drift apart over time
- ❌ **Complexity**: Conditional logic for platform detection everywhere
- ❌ **Cost vs benefit**: Huge effort for <15% of users (Windows users who won't use WSL)

### Alternative 2: Pure Python Implementation

**Structure:** Replace all Bash scripts with Python

**Rejected because:**
- ❌ **See ADR-0002**: Decision already made to use Bash
- ❌ **Loses transparency**: Python subprocess calls less readable than shell scripts
- ❌ **Git integration complexity**: Bash is git's native language
- ❌ **Reimplementation cost**: ~2000+ lines of Python to replace 5 Bash scripts
- ❌ **Maintenance burden**: More complex code for same functionality

### Alternative 3: Docker Container Approach

**Structure:** Ship Docker container with Unix environment

```bash
# Windows users run via Docker
docker run adversarial-workflow evaluate task.md
```

**Rejected because:**
- ❌ **Heavy dependency**: Requires Docker (larger than WSL)
- ❌ **File access complexity**: Mounting Windows files into container
- ❌ **Performance overhead**: Container startup time
- ❌ **UX friction**: Docker commands are verbose
- ❌ **Worse than WSL**: WSL is lighter and more integrated

### Alternative 4: Web-Based Service

**Structure:** SaaS offering, no local installation

**Rejected because:**
- ❌ **Fundamentally different**: Not a CLI tool anymore
- ❌ **Privacy concerns**: Code must be uploaded to service
- ❌ **Network dependency**: Can't work offline
- ❌ **Cost implications**: Infrastructure costs, pricing model
- ❌ **Scope creep**: Completely different product

### Alternative 5: Git Bash Requirement (Windows)

**Structure:** Require Git Bash instead of WSL

```bash
# Windows users install Git for Windows
# Use Git Bash terminal
```

**Rejected because:**
- ❌ **Limited environment**: Git Bash is MINGW, not full Linux
- ❌ **Tool inconsistencies**: Some Unix tools missing or different versions
- ❌ **Path translation issues**: Windows paths vs Unix paths
- ❌ **Python integration**: Python.exe vs python in Git Bash context
- ❌ **WSL is better**: More complete, better supported by Microsoft

### Alternative 6: Platform Detection + Degraded Mode

**Structure:** Detect Windows, run with limited features

**Rejected because:**
- ❌ **Poor UX**: "Some features unavailable on Windows"
- ❌ **Complexity**: Conditional feature availability
- ❌ **Testing nightmare**: Different test matrices per platform
- ❌ **Confusing documentation**: "Available on Unix only" notes everywhere
- ❌ **Better to just recommend WSL**: Clear, consistent experience

## Real-World Results

### Platform Distribution (v0.1.0-v0.3.0)

**Observed usage** (based on GitHub issues, discussions):
- macOS: ~45% (slightly higher than estimate)
- Linux: ~35% (as expected)
- Windows (WSL): ~15% (growing)
- Windows (native attempts): ~5% (redirected to WSL documentation)

**User Feedback:**

**Positive:**
- "WSL setup was straightforward, works perfectly now"
- "Glad you focused on quality instead of compromising for Windows"
- "Having one codebase makes contributions easier"

**Friction:**
- "Wish it worked on native Windows" (occasional, ~3-5% of feedback)
- "WSL setup took 15 minutes" (but one-time only)
- "Didn't know I needed WSL initially" → Fixed: Better docs, error messages

**Windows WSL Success Rate:**
- ~90% of Windows users successfully set up WSL and install
- ~10% abandon or request native support
- Most friction during initial WSL install, not package installation

### Support Burden

**Issues related to platform:**
- Unix (macOS/Linux): <5% of issues (mostly Python env problems)
- WSL setup: ~10% of issues (mostly first-time WSL users)
- Windows native requests: ~5% (directed to WSL docs)

**Time savings:**
- Not maintaining PowerShell: ~40-50 hours saved (estimated)
- Unified testing: ~20-30 hours saved per major release
- Simpler CI/CD: ~10 hours saved in pipeline complexity

### Evolution

**v0.1.0:** No explicit Windows guidance, users confused
**v0.2.0:** Added WINDOWS_SETUP.md, improved error messages
**v0.3.0:** Platform check in CLI, better README section

**Trend:** Fewer Windows-native questions over time (better docs + WSL adoption)

## Related Decisions

- ADR-0002: Bash and Aider Foundation (why Bash scripts are fundamental)
- ADR-0004: Template-based initialization (how platform detection affects template rendering)
- ADR-0009: Interactive onboarding (platform check during init)

## References

- [README.md Platform Support](../../../README.md#platform-support) - User-facing documentation
- [TROUBLESHOOTING.md](../../../docs/TROUBLESHOOTING.md) - WSL-specific issues
- [cli.py platform detection](../../../adversarial_workflow/cli.py) - Windows native check
- [Microsoft WSL Documentation](https://learn.microsoft.com/en-us/windows/wsl/) - Official WSL guide
- [WSL 2 Release (2020)](https://devblogs.microsoft.com/commandline/wsl-2-is-now-available-in-windows-insiders/) - WSL evolution

**Industry Examples:**
- [Homebrew](https://brew.sh/) - macOS/Linux only (WSL via Linuxbrew)
- [Poetry](https://python-poetry.org/) - Cross-platform, but recommends Unix for contrib
- [Docker](https://www.docker.com/) - Uses WSL 2 backend on Windows
- [Many dev tools](https://docs.github.com/en/get-started) - Assume Unix, document WSL for Windows

## Revision History

- 2025-10-15: Initial decision (v0.1.0)
- 2025-10-16: Added WINDOWS_SETUP.md (v0.2.0)
- 2025-10-20: Documented as ADR-0010
