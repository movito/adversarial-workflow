# ADR-0011: Non-Interactive Execution Support

**Status**: Accepted

**Date**: 2025-10-30 (v0.3.2+)

**Deciders**: Fredrik Matheson, Coordinator Agent

## Context

The adversarial-workflow system is designed to integrate with AI agent coordination systems where agents execute commands in non-interactive shells (background processes, Bash tool contexts, CI/CD pipelines).

During TASK-2025-0037 implementation (file reading investigation and rate limit handling), we added an interactive confirmation prompt for large files (>700 lines) as a safety check to prevent wasted API calls on files that will exceed OpenAI rate limits.

**The Discovery**: This created an unforeseen **hard blocker** for agent automation workflows.

### The Non-Interactive Shell Blocker

When agents execute evaluation commands in non-interactive shells:

1. **The Trigger**: Files >700 lines invoke an interactive confirmation prompt
2. **The Block**: Python's `input()` function waits for user input from stdin
3. **The Problem**: Non-interactive shells have no terminal attached (stdin unavailable)
4. **The Failure**: Process blocks indefinitely - no timeout, no automatic failure
5. **The Impact**: Agent cannot proceed without manual intervention

**Code that blocks**:
```python
# In cli.py evaluate() function (line ~1707)
if line_count > 700:
    print(f"{RED}⚠️  WARNING: File is very large (>{line_count} lines){RESET}")
    print(f"   This will likely fail on Tier 1 OpenAI accounts (30k TPM limit)")
    print(f"   Recommended: Split into files <500 lines each")
    print()
    response = input("Continue anyway? [y/N]: ").strip().lower()  # ← BLOCKS HERE
    if response not in ['y', 'yes']:
        print("Evaluation cancelled.")
        return 0
```

**Why this matters for agents**:
- Agents run in background processes (Bash tool, Task tool)
- CI/CD pipelines are non-interactive by design
- Cron jobs have no terminal
- Batch processing scripts run detached
- No way to provide keyboard input programmatically

This blocking behavior was discovered when the **feature-developer agent** attempted to run file reading investigation tests in TASK-2025-0037 Phase 2B. The agent's execution hung indefinitely, requiring manual intervention.

## Decision

**Support non-interactive execution** through stdin redirection patterns while preserving user safety:

1. **Keep the interactive prompt** (user safety remains important)
2. **Document the stdin bypass pattern** for automation contexts
3. **No --yes flag** (intentional decision - see alternatives)
4. **Stdin redirection as the canonical solution**

### Recommended Pattern

```bash
# Agent/automation execution: pipe "y" to bypass interactive prompts
echo "y" | adversarial evaluate <file>
```

### Why Stdin Redirection Over Flags?

**Stdin redirection chosen because**:

1. **Standard Unix pattern** - Portable and familiar to developers
   ```bash
   # Works everywhere Unix tools work
   echo "y" | command_with_prompt
   yes | command_with_many_prompts
   ```

2. **Works with any interactive prompt** - Not specific to our tool
   - Agents learn one pattern, apply to all tools
   - Future prompts automatically handled
   - No per-tool customization

3. **Explicit in code** - Visible automation intent
   ```bash
   # Clear this is automated/non-interactive
   echo "y" | adversarial evaluate task.md

   # vs hidden flag behavior
   adversarial evaluate --yes task.md
   ```

4. **No flag maintenance burden**
   - No new CLI arguments to document
   - No backward compatibility concerns
   - No flag conflicts with future features

5. **Self-documenting in scripts**
   ```bash
   for task in *.md; do
       echo "y" | adversarial evaluate "$task"  # Clear bypass intent
   done
   ```

## Consequences

### Positive

✅ **Agents can automate large file evaluation**
- Background processes work correctly
- Batch processing scripts run unattended
- CI/CD pipelines function without manual intervention

✅ **Safety prompt preserved for manual execution**
- Interactive users still get confirmation for risky operations
- Prevents accidental waste of API calls on files that will fail
- UX remains protective for human users

✅ **Standard Unix pattern**
- Portable across all Unix-like systems
- Familiar to developers and DevOps engineers
- Works in bash, zsh, sh, and other shells

✅ **No new flags to maintain**
- Simpler CLI interface
- No backward compatibility concerns when adding/removing flags
- Less documentation burden

✅ **Works in multiple contexts**
- CI/CD: GitHub Actions, GitLab CI, Jenkins
- Cron jobs: Scheduled evaluations
- Background jobs: Detached processes
- Batch processing: Multiple file workflows

### Negative

⚠️ **Requires documentation** - Agents/users must learn the pattern
- Added "Bypassing interactive prompts" section to README.md
- Added comprehensive troubleshooting entry to TROUBLESHOOTING.md
- Added "Non-Interactive Execution Patterns" to QUICK-AGENT-SETUP.md
- Created this ADR to preserve decision context

⚠️ **Slightly more verbose than a flag**
```bash
# Stdin redirection (8 characters overhead)
echo "y" | adversarial evaluate task.md

# Hypothetical flag (6 characters overhead)
adversarial evaluate --yes task.md
```
**Verdict**: Verbosity acceptable for clarity and portability

⚠️ **Non-obvious to users unfamiliar with stdin redirection**
- Mitigated through comprehensive documentation
- Standard pattern that generalizes to other tools
- Worth learning for long-term benefit

### Alternatives Considered

**Alternative 1: Add --yes flag**
```bash
adversarial evaluate --yes task.md
```

**Rejected because**:
- Adds maintenance burden (new flag to document, test, maintain)
- Less portable (our flag doesn't work with other tools)
- Hidden behavior (not obvious in script what --yes does)
- Future flag conflicts (what if we need --yes for something else?)

---

**Alternative 2: Auto-detect non-interactive shells**
```python
import sys
if not sys.stdin.isatty():
    # Automatically proceed without prompting
    response = 'y'
else:
    response = input("Continue anyway? [y/N]: ")
```

**Rejected because**:
- Removes safety check exactly when automation needs it most
- Silent failures harder to debug
- Inconsistent behavior (sometimes prompts, sometimes doesn't)
- Agents would proceed with doomed-to-fail operations

---

**Alternative 3: Remove prompt entirely**
```python
# Always proceed, just warn
if line_count > 700:
    print("⚠️  WARNING: File is large, may fail")
# No prompt, continue automatically
```

**Rejected because**:
- Users waste API calls on files that will fail
- No opportunity to cancel before failure
- Removes important safety check

---

**Alternative 4: Environment variable**
```bash
export ADVERSARIAL_AUTO_CONFIRM=1
adversarial evaluate task.md
```

**Rejected because**:
- Hidden behavior (not visible in script what env var does)
- Global state (affects all commands in session)
- Harder to audit (where was this variable set?)
- More complex troubleshooting

---

**Alternative 5: Configuration file option**
```yaml
# .adversarial/config.yml
auto_confirm_large_files: true
```

**Rejected because**:
- Persistent state that might be forgotten
- Not obvious in individual command invocations
- Requires config file management
- Less explicit than per-command decision

## Implementation

### Code Location

**Interactive Prompt**: `adversarial_workflow/cli.py` (lines ~1686-1715)

```python
# Pre-flight check for file size
with open(task_file, 'r') as f:
    line_count = len(f.readlines())

if line_count > 700:
    print(f"{RED}⚠️  WARNING: File is very large (>{line_count} lines){RESET}")
    print(f"   This will likely fail on Tier 1 OpenAI accounts (30k TPM limit)")
    print(f"   Recommended: Split into files <500 lines each")
    print()
    response = input("Continue anyway? [y/N]: ").strip().lower()
    if response not in ['y', 'yes']:
        print("Evaluation cancelled.")
        return 0
```

### Documentation Locations

**User-Facing**:
- `README.md` (File Size Guidelines section, lines 209-217)
- `docs/TROUBLESHOOTING.md` (Large file evaluation entry, lines 385-448)

**Agent-Facing**:
- `docs/QUICK-AGENT-SETUP.md` (Non-Interactive Execution Patterns, lines 229-289)

**Architectural**:
- This ADR (`docs/decisions/adr/0011-non-interactive-execution-support.md`)

### Usage Examples

**Agent Bash Tool Pattern**:
```bash
# Correct - releases blocker
echo "y" | adversarial evaluate delegation/tasks/TASK-2025-0037-*.md

# Incorrect - hangs indefinitely
adversarial evaluate delegation/tasks/TASK-2025-0037-*.md
```

**Batch Processing Script**:
```bash
#!/bin/bash
# Evaluate all active tasks, bypassing prompts

for task in delegation/tasks/active/*.md; do
    echo "Evaluating: $task"
    echo "y" | adversarial evaluate "$task"
    echo "---"
done
```

**CI/CD Example (GitHub Actions)**:
```yaml
- name: Evaluate task specification
  run: echo "y" | adversarial evaluate delegation/tasks/active/TASK-*.md
```

## Related Decisions

- **ADR-0001**: Adversarial Workflow Pattern (why evaluation matters)
- **ADR-0002**: Bash and Aider Foundation (why bash scripts)
- **ADR-0005**: Agent Coordination Extension Layer (agent integration context)
- **TASK-2025-0037**: File reading investigation (why the prompt exists)

## Future Considerations

### Potential Enhancements

1. **Structured output mode**
   ```bash
   # JSON output for programmatic parsing
   adversarial evaluate --json task.md
   ```
   This could bypass prompts automatically (--json implies non-interactive)

2. **Timeout on input()**
   ```python
   # Add timeout to prevent infinite hangs
   response = input_with_timeout("Continue? [y/N]: ", timeout=30)
   ```
   Fallback to default "N" after timeout

3. **Quiet mode**
   ```bash
   # Suppress warnings, proceed automatically
   adversarial evaluate --quiet task.md
   ```
   For environments where warnings create noise

**Note**: None of these are planned currently. Stdin redirection meets all known needs.

## References

**Investigation Context**:
- TASK-2025-0037: File reading investigation and rate limit handling
- OpenAI Rate Limits: 30k TPM for Tier 1 (files <600 lines safe)
- Investigation Results: `delegation/handoffs/TASK-2025-0037-FILE-READING-INVESTIGATION-RESULTS.md`

**User Reports**:
- Feature-developer agent: Discovered blocker during Phase 2B investigation
- Workaround documented: `echo "y" | adversarial evaluate`

**Unix Patterns**:
- Standard input redirection: `echo <input> | <command>`
- Yes command: `yes | <command>` (for multiple prompts)
- Heredoc: `<command> << EOF` (for multi-line input)

---

**Decision Outcome**: Stdin redirection provides a portable, explicit, maintainable solution for non-interactive execution while preserving important user safety checks.
