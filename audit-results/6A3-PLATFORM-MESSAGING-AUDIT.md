# Phase 6A.3: Platform Support Messaging Audit

**Date**: 2025-10-15
**Task**: Assess clarity of Windows/WSL platform messaging
**Critical Finding**: Evaluator flagged "Windows/WSL support needs more prominent messaging"

---

## Executive Summary

**Current State**: Platform support IS documented in README.md (lines 210-222) with clear Windows/WSL messaging.

**Problem**: Not prominent enough. Windows users may not see this before attempting installation or during setup.

**Severity**: CRITICAL (per Evaluator findings)

**Required Actions**: 3 enhancements needed

---

## Current Platform Messaging Inventory

### ✅ Exists: README.md Platform Support Section

**Location**: README.md, lines 210-222
**Quality**: GOOD - clear explanation
**Issues**:
- Too far down in document (after Requirements, before Usage Examples)
- No upfront warning in Quick Start
- No runtime detection in CLI

**Current Text**:
```markdown
### Platform Support

**✅ Supported Platforms**:
- **macOS**: Fully supported (tested on macOS 10.15+)
- **Linux**: Fully supported (tested on Ubuntu 22.04, Debian 11+, CentOS 8+)

**⚠️ Windows**:
- **Native Windows**: Not supported (Bash scripts are Unix-specific)
- **WSL (Windows Subsystem for Linux)**: Fully supported
- **Git Bash**: May work but not officially tested

**Why Unix-only?** This package uses Bash scripts for workflow automation.
While Python is cross-platform, the workflow scripts (`.adversarial/scripts/*.sh`)
are designed for Unix-like shells. Windows users should use WSL for a native
Linux environment.
```

**Assessment**:
- ✅ Clear about native Windows not supported
- ✅ WSL mentioned as solution
- ✅ Explains why (Bash scripts)
- ❌ NOT prominent enough (buried in requirements)
- ❌ No runtime warning for Windows users

---

## Missing Platform Messaging

### ❌ Missing #1: Quick Start Warning

**Location**: README.md, "Quick Start" section (lines 19-57)
**Current**: No platform requirements mentioned
**Issue**: Windows users start setup, discover incompatibility too late

**Required Addition**:
```markdown
## Quick Start

**⚠️ Platform Requirements**: This package requires **Unix-like systems**
(macOS or Linux). Windows users need **WSL** (Windows Subsystem for Linux).
[See Platform Support](#platform-support) for details.

### Interactive Setup (Recommended)
```

**Impact**: HIGH - prevents wasted time for Windows users

---

### ❌ Missing #2: CLI Runtime Platform Check

**Location**: `adversarial_workflow/cli.py`
**Current**: No platform detection in `init` or `quickstart`
**Issue**: Windows users can run init, create config, then fail at script execution

**Required Addition**:
```python
import platform

def check_platform_compatibility():
    """Check if platform is supported and warn Windows users."""
    system = platform.system()

    if system == "Windows":
        print("\n" + "="*60)
        print("⚠️  WARNING: Native Windows is NOT Supported")
        print("="*60)
        print("\nThis package requires Unix shell (bash) for workflow scripts.")
        print("\n📍 RECOMMENDED: Use WSL (Windows Subsystem for Linux)")
        print("   Install: https://learn.microsoft.com/windows/wsl/install")
        print("\n⚠️  ALTERNATIVE: Git Bash (not officially supported)")
        print("   Some features may not work correctly")
        print("\n" + "="*60)

        response = input("\n Continue with setup anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("\nSetup cancelled. Please install WSL and try again.")
            return False

    return True

# Call in init_interactive() and quickstart()
```

**Impact**: CRITICAL - prevents user frustration with setup failures

**Location to Add**:
- Line ~50 in `init_interactive()`
- Line ~20 in `quickstart()`

---

### ❌ Missing #3: Installation Documentation Prominence

**Location**: README.md, "Installation" instructions
**Current**: Platform requirements mentioned in separate section
**Issue**: Users follow installation steps without seeing platform warning

**Required Enhancement**:
Move platform requirements ABOVE installation instructions:

```markdown
## Installation

**⚠️ Platform Requirements**:
- ✅ **macOS** and **Linux**: Fully supported
- ❌ **Windows (native)**: Not supported
- ✅ **Windows (WSL)**: Fully supported via [WSL 2](https://learn.microsoft.com/windows/wsl/install)

```bash
pip install adversarial-workflow
```
```

**Impact**: MEDIUM - catches users before pip install

---

## Platform Mentions in Other Files

### docs/TROUBLESHOOTING.md

**Line 48**: Windows-specific venv activation example
```bash
.venv\Scripts\activate     # Windows
```

**Assessment**:
- ✅ Helpful for context
- ⚠️ Could imply Windows is supported (it's showing Windows command)
- Action: Add note: "# Windows (WSL or Git Bash only)"

---

### PHASE-3-COMPLETION-SUMMARY.md

**Line 359**: "Test on Linux, Mac, Windows"

**Assessment**:
- Historical document
- Action: KEEP (documents historical test plan that evolved)

---

## Platform Support Strengths

### ✅ What's Working Well

1. **Clear Documentation**: README Platform Support section is comprehensive
2. **WSL Recommendation**: WSL is prominently mentioned as solution
3. **Rationale Provided**: Explains WHY Unix-only (Bash scripts)
4. **Git Bash Mentioned**: Acknowledges alternative with caveat
5. **Specific OS Versions**: Lists tested versions (macOS 10.15+, Ubuntu 22.04, etc.)

---

## Critical Gaps

### 🔴 Gap #1: Discovery Problem

**Issue**: Users don't see platform requirements until AFTER starting setup.

**User Journey**:
1. Find package on PyPI or GitHub
2. Read Quick Start
3. Run `pip install adversarial-workflow`
4. Run `adversarial init`
5. Fill out interactive prompts
6. Try to run workflow
7. **Scripts fail** (bash not found on native Windows)
8. **THEN** discover Platform Support section

**Fix**: Add warnings at steps 2, 3, and 4

---

### 🔴 Gap #2: No Runtime Protection

**Issue**: CLI doesn't detect Windows and warn user.

**Current Behavior**:
```bash
# On native Windows (PowerShell)
C:\> adversarial init
# Succeeds! Creates .adversarial/ directory
# No warning about incompatibility

C:\> adversarial evaluate task.md
# Fails when trying to execute bash script
# Generic error, not helpful
```

**Fix**: Add platform check in `init_interactive()` and `quickstart()`

---

### 🔴 Gap #3: Documentation Placement

**Issue**: Platform requirements too far down in README (line 210).

**Reading Pattern**:
- Users read: Title (line 1) → Features (line 9) → Quick Start (line 19)
- Many stop there and start trying it
- Platform Support (line 210) is past 3 other sections

**Fix**: Add platform notice in Quick Start AND Requirements sections

---

## Recommended Enhancements

### Enhancement 1: Upfront Platform Notice (CRITICAL)

**Location**: README.md, line ~19 (top of Quick Start)

**Add**:
```markdown
## Quick Start

> **⚠️ Platform Requirements**: This package requires Unix-like systems
> (macOS/Linux) or **WSL** on Windows. Native Windows (PowerShell/CMD) is
> not supported. [Platform details →](#platform-support)
```

**Impact**: Users see warning before attempting anything
**Effort**: 2 minutes

---

### Enhancement 2: Runtime Platform Detection (CRITICAL)

**Location**: `adversarial_workflow/cli.py`

**Add Function** (shown above in Missing #2)

**Call Sites**:
```python
def init_interactive(project_path: str = ".") -> int:
    """Interactive initialization wizard."""
    # ADD THIS AT TOP:
    if not check_platform_compatibility():
        return 1

    # ... rest of function

def quickstart() -> int:
    """Quick start wizard."""
    # ADD THIS AT TOP:
    if not check_platform_compatibility():
        return 1

    # ... rest of function
```

**Impact**: Prevents Windows users from wasting time on incompatible setup
**Effort**: 20 minutes (write + test)

---

### Enhancement 3: Enhanced Platform Section (MEDIUM)

**Location**: README.md, lines 210-222

**Current section is good. Add**:
1. **Visual prominence**: Use colored emoji/icons for clearer scanning
2. **WSL installation link**: Direct link to Microsoft docs
3. **Git Bash warning**: More explicit about limitations

**Enhanced Version**:
```markdown
## Platform Support

### ✅ Fully Supported

**macOS**:
- ✅ macOS 10.15+ (Catalina and later)
- ✅ Native bash 3.2+ support
- ✅ All features work out of the box

**Linux**:
- ✅ Ubuntu 22.04+, Debian 11+, CentOS 8+
- ✅ Any Unix-like system with bash 3.2+
- ✅ All features work out of the box

### ⚠️ Windows

**Native Windows**: ❌ **NOT SUPPORTED**

This package uses Bash shell scripts (`.adversarial/scripts/*.sh`) that
cannot run on native Windows (PowerShell, CMD).

**✅ RECOMMENDED: WSL (Windows Subsystem for Linux)**
- Full support via WSL 2
- All features work as documented
- Setup guide: [Install WSL](https://learn.microsoft.com/windows/wsl/install)
- Takes ~10 minutes to install

**⚠️ Git Bash**: Limited Support
- May work for basic usage
- Some features may fail
- Not officially tested
- Use at your own risk

### Why Unix-Only?

This package uses Bash shell scripting for workflow automation. While
Python itself is cross-platform, the workflow orchestration requires:
- Unix shell (bash 3.2+)
- Standard Unix utilities (grep, sed, etc.)
- Unix-style file paths

**For Windows users**: WSL provides a complete Linux environment and is
the official Microsoft-recommended way to run Linux tools on Windows.
```

**Impact**: Crystal clear for all users, especially Windows
**Effort**: 15 minutes

---

## Validation Checklist

After Phase 6C implements these enhancements:

- [ ] Quick Start has platform warning (visible without scrolling)
- [ ] Installation section mentions platform requirements
- [ ] CLI detects Windows and shows helpful message
- [ ] WSL installation link provided in 3 places
- [ ] Platform Support section enhanced with visuals
- [ ] Git Bash limitations clearly stated
- [ ] No Windows user can miss the requirements

---

## Summary

**Current Score**: 6/10
- ✅ Has good documentation (Platform Support section)
- ❌ Not prominent enough (buried in middle of README)
- ❌ No runtime detection (CLI doesn't warn)
- ❌ Quick Start missing platform notice

**Target Score After Phase 6C**: 10/10
- ✅ Quick Start has upfront warning
- ✅ CLI detects and warns Windows users
- ✅ Enhanced Platform Support section
- ✅ WSL links in multiple places
- ✅ Impossible to miss requirements

---

## Completion Criteria for 6A.3

- [x] Current platform messaging inventoried (README line 210-222)
- [x] Missing messaging identified (3 critical gaps)
- [x] Enhancement recommendations specified (3 enhancements)
- [x] Implementation locations identified (README + cli.py)
- [x] Validation checklist created

**Status**: ✅ COMPLETE

**Time Taken**: ~12 minutes
**Next**: Phase 6A.4 - User Journey Mapping (30 min)

---

**Document Status**: COMPLETE
**Next Document**: 6A4-USER-JOURNEY-ANALYSIS.md
