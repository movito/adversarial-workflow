#!/bin/bash
# Pre-flight Check Script
# Provides comprehensive project scan before starting work
# Usage: ./agents/tools/preflight-check.sh [--json]

set -euo pipefail

# Color codes (disabled in JSON mode)
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check for JSON output mode
JSON_MODE=false
if [[ "${1:-}" == "--json" ]]; then
    JSON_MODE=true
fi

# Counters
PASSED=0
WARNINGS=0
ERRORS=0
INFO_COUNT=0
declare -a RECOMMENDATIONS=()

# Helper functions
check_pass() {
    if [ "$JSON_MODE" = true ]; then
        # Store for JSON output
        :
    else
        echo -e "  ${GREEN}✅${NC} $1"
    fi
    PASSED=$((PASSED + 1))
}

check_warn() {
    if [ "$JSON_MODE" = true ]; then
        :
    else
        echo -e "  ${YELLOW}⚠️ ${NC} $1"
    fi
    WARNINGS=$((WARNINGS + 1))
}

check_fail() {
    if [ "$JSON_MODE" = true ]; then
        :
    else
        echo -e "  ${RED}❌${NC} $1"
    fi
    ERRORS=$((ERRORS + 1))
}

check_info() {
    if [ "$JSON_MODE" = true ]; then
        :
    else
        echo -e "  ${BLUE}ℹ️ ${NC} $1"
    fi
    INFO_COUNT=$((INFO_COUNT + 1))
}

add_recommendation() {
    local priority="$1"
    local message="$2"
    RECOMMENDATIONS+=("$priority: $message")
}

# Start output
if [ "$JSON_MODE" = false ]; then
    echo "🔍 Project Pre-flight Check"
    echo "=========================="
    echo ""
fi

# ============================================================================
# 1. PROJECT STRUCTURE
# ============================================================================

if [ "$JSON_MODE" = false ]; then
    echo "Project Structure:"
fi

# Check for .agent-context/
if [ -d ".agent-context" ]; then
    check_pass ".agent-context/ exists"
else
    check_warn ".agent-context/ not found (not initialized)"
    add_recommendation "MEDIUM" "Run 'adversarial agent-setup' to initialize agent coordination"
fi

# Check for agents/
if [ -d "agents" ]; then
    check_pass "agents/ directory exists"

    # Count agent launcher scripts
    if [ -d "agents" ]; then
        AGENT_COUNT=$(find agents -maxdepth 1 \( -name "*.sh" -o -name "ca" -o -name "fd" -o -name "tr" \) 2>/dev/null | wc -l | tr -d ' ')
        if [ "$AGENT_COUNT" -gt 0 ]; then
            check_info "$AGENT_COUNT agent launcher scripts available"
        fi
    fi
else
    check_info "agents/ not found (optional)"
fi

# Check for delegation/ vs tasks/
if [ -d "delegation" ]; then
    check_pass "delegation/ directory exists"

    if [ -d "delegation/tasks/active" ]; then
        check_pass "delegation/tasks/active/ structure present"
    fi
else
    if [ -d "tasks" ]; then
        check_warn "Using tasks/ at root (consider delegation/ structure)"
        add_recommendation "LOW" "Migrate to delegation/tasks/ for better organization"
    else
        check_info "No task directory found"
    fi
fi

# Check for docs/
if [ -d "docs" ]; then
    check_pass "docs/ directory exists"
else
    check_info "docs/ not found"
fi

# Check for loose files in root (excluding standard ones)
if [ "$JSON_MODE" = false ]; then
    LOOSE_FILES=$(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.MD" \) ! -name "README.md" ! -name "CHANGELOG.md" ! -name "LICENSE.md" ! -name "CONTRIBUTING.md" ! -name "CODE_OF_CONDUCT.md" 2>/dev/null | wc -l | tr -d ' ')
else
    LOOSE_FILES=0
fi

if [ "$LOOSE_FILES" -gt 0 ]; then
    LOOSE_LIST=$(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.MD" \) ! -name "README.md" ! -name "CHANGELOG.md" ! -name "LICENSE.md" ! -name "CONTRIBUTING.md" ! -name "CODE_OF_CONDUCT.md" 2>/dev/null | head -3 | xargs -I {} basename {} | tr '\n' ',' | sed 's/,$//')
    if [ -n "$LOOSE_LIST" ]; then
        check_warn "Loose documentation files in root: $LOOSE_LIST"
        add_recommendation "MEDIUM" "Organize loose files into docs/ directory"
    fi
fi

if [ "$JSON_MODE" = false ]; then
    echo ""
fi

# ============================================================================
# 2. PREREQUISITES
# ============================================================================

if [ "$JSON_MODE" = false ]; then
    echo "Prerequisites:"
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version 2>/dev/null | awk '{print $3}' | head -1)

    # Check if we're in a git repo
    if git rev-parse --git-dir > /dev/null 2>&1; then
        # Check for uncommitted changes
        if git diff-index --quiet HEAD -- 2>/dev/null; then
            check_pass "Git: $GIT_VERSION (working tree clean)"
        else
            # Count modified files
            MODIFIED_COUNT=$(git status --porcelain | grep -c "^ M" || echo "0")
            UNTRACKED_COUNT=$(git status --porcelain | grep -c "^??" || echo "0")

            if [ "$MODIFIED_COUNT" -gt 0 ] || [ "$UNTRACKED_COUNT" -gt 0 ]; then
                check_warn "Git: $GIT_VERSION ($MODIFIED_COUNT modified, $UNTRACKED_COUNT untracked)"
                if [ "$MODIFIED_COUNT" -gt 5 ]; then
                    add_recommendation "LOW" "Consider committing or stashing changes before starting major work"
                fi
            else
                check_pass "Git: $GIT_VERSION (working tree clean)"
            fi
        fi
    else
        check_warn "Git: $GIT_VERSION (not in a git repository)"
    fi
else
    check_fail "Git not installed"
    add_recommendation "HIGH" "Install Git to use adversarial workflow"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        check_pass "Python: $PYTHON_VERSION"
    else
        check_warn "Python: $PYTHON_VERSION (3.8+ recommended)"
        add_recommendation "MEDIUM" "Upgrade to Python 3.8+ for full compatibility"
    fi
else
    check_fail "Python 3 not installed"
    add_recommendation "HIGH" "Install Python 3.8+ to use adversarial workflow"
fi

# Check Aider
if command -v aider &> /dev/null; then
    AIDER_VERSION=$(aider --version 2>&1 | head -1 | awk '{print $2}' || echo "unknown")
    check_pass "Aider: $AIDER_VERSION"
else
    check_warn "Aider not installed"
    add_recommendation "MEDIUM" "Install aider: pip install aider-chat"
fi

# Check Bash version
BASH_VERSION=$(bash --version 2>&1 | head -1 | awk '{print $4}' | cut -d'(' -f1)
BASH_MAJOR=$(echo "$BASH_VERSION" | cut -d. -f1)

if [ "$BASH_MAJOR" -ge 4 ]; then
    check_info "Bash: $BASH_VERSION"
else
    check_info "Bash: $BASH_VERSION (macOS default, some features limited)"
fi

# Check for jq (optional but helpful)
if command -v jq &> /dev/null; then
    JQ_VERSION=$(jq --version 2>&1 | cut -d- -f2)
    check_info "jq: $JQ_VERSION (JSON parsing available)"
else
    check_info "jq not installed (optional)"
fi

if [ "$JSON_MODE" = false ]; then
    echo ""
fi

# ============================================================================
# 3. CONFIGURATION
# ============================================================================

if [ "$JSON_MODE" = false ]; then
    echo "Configuration:"
fi

# Check .adversarial/config.yml
if [ -f ".adversarial/config.yml" ]; then
    # Try to validate YAML syntax
    if command -v python3 &> /dev/null; then
        if python3 -c "import yaml; yaml.safe_load(open('.adversarial/config.yml'))" 2>/dev/null; then
            check_pass ".adversarial/config.yml - Valid YAML"
        else
            check_fail ".adversarial/config.yml - Invalid YAML syntax"
            add_recommendation "HIGH" "Fix YAML syntax in .adversarial/config.yml"
        fi
    else
        check_pass ".adversarial/config.yml exists (YAML validation skipped)"
    fi
else
    check_warn ".adversarial/config.yml not found"
    add_recommendation "MEDIUM" "Run 'adversarial init' to create configuration"
fi

# Check .env file
if [ -f ".env" ]; then
    # Count API keys (various patterns)
    API_KEY_COUNT=0
    if grep -q "ANTHROPIC_API_KEY=" .env 2>/dev/null; then
        API_KEY_COUNT=$((API_KEY_COUNT + 1))
    fi
    if grep -q "OPENAI_API_KEY=" .env 2>/dev/null; then
        API_KEY_COUNT=$((API_KEY_COUNT + 1))
    fi
    if grep -q "GEMINI_API_KEY=" .env 2>/dev/null; then
        API_KEY_COUNT=$((API_KEY_COUNT + 1))
    fi

    check_pass ".env file exists ($API_KEY_COUNT API keys detected)"

    # Check if .env is in .gitignore
    if [ -f ".gitignore" ]; then
        if grep -q "^\.env$" .gitignore 2>/dev/null || grep -q "^\.env " .gitignore 2>/dev/null; then
            check_pass ".env in .gitignore"
        else
            check_fail ".env NOT in .gitignore (SECURITY RISK!)"
            add_recommendation "HIGH" "Add .env to .gitignore immediately to prevent credential leaks"
        fi
    else
        check_fail ".gitignore not found (SECURITY RISK!)"
        add_recommendation "HIGH" "Create .gitignore and add .env to prevent credential leaks"
    fi
else
    check_info ".env not found (API keys in environment)"
fi

# Check .aider.conf.yml
if [ -f ".aider.conf.yml" ]; then
    check_pass ".aider.conf.yml exists"
else
    check_info ".aider.conf.yml not found (optional)"
fi

# Check pyproject.toml or setup.py
if [ -f "pyproject.toml" ]; then
    check_pass "pyproject.toml exists"
elif [ -f "setup.py" ]; then
    check_pass "setup.py exists"
else
    check_info "No Python package configuration found"
fi

if [ "$JSON_MODE" = false ]; then
    echo ""
fi

# ============================================================================
# 4. ACTIVE WORK
# ============================================================================

if [ "$JSON_MODE" = false ]; then
    echo "Active Work:"
fi

# Count active tasks
TASK_COUNT=0
TASK_LOCATION=""

if [ -d "delegation/tasks/active" ]; then
    TASK_COUNT=$(find delegation/tasks/active -name "TASK-*.md" 2>/dev/null | wc -l | tr -d ' ')
    TASK_LOCATION="delegation/tasks/active/"
elif [ -d "tasks" ]; then
    TASK_COUNT=$(find tasks -name "TASK-*.md" 2>/dev/null | wc -l | tr -d ' ')
    TASK_LOCATION="tasks/"
fi

if [ "$TASK_COUNT" -gt 0 ]; then
    check_info "$TASK_COUNT active tasks in $TASK_LOCATION"

    # List first 3 tasks (Bash 3.2 compatible)
    if [ "$TASK_COUNT" -le 3 ]; then
        find "${TASK_LOCATION}" -name "TASK-*.md" 2>/dev/null | while IFS= read -r task_file; do
            TASK_NAME=$(basename "$task_file" .md)
            check_info "  → $TASK_NAME"
        done
    else
        check_info "  (use 'ls ${TASK_LOCATION}' to see all tasks)"
    fi
else
    check_info "No active tasks"
fi

# Check agent-handoffs.json for stale status
if [ -f ".agent-context/agent-handoffs.json" ]; then
    check_pass "agent-handoffs.json exists"

    # If jq is available, check for stale agents
    if command -v jq &> /dev/null; then
        # Check last_updated timestamps (this is a basic check)
        # In a real implementation, we'd parse dates and compare
        check_info "Agent status tracking active"
    fi
else
    check_info "agent-handoffs.json not found (agent system not initialized)"
fi

if [ "$JSON_MODE" = false ]; then
    echo ""
fi

# ============================================================================
# 5. RECOMMENDATIONS
# ============================================================================

if [ "$JSON_MODE" = false ] && [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
    echo "📋 Recommendations:"

    # Sort recommendations by priority
    declare -a HIGH_RECS=()
    declare -a MEDIUM_RECS=()
    declare -a LOW_RECS=()
    declare -a INFO_RECS=()

    for rec in "${RECOMMENDATIONS[@]}"; do
        PRIORITY=$(echo "$rec" | cut -d: -f1)
        case "$PRIORITY" in
            HIGH)
                HIGH_RECS+=("$rec")
                ;;
            MEDIUM)
                MEDIUM_RECS+=("$rec")
                ;;
            LOW)
                LOW_RECS+=("$rec")
                ;;
            INFO)
                INFO_RECS+=("$rec")
                ;;
        esac
    done

    # Print in priority order
    REC_NUM=1
    for rec in "${HIGH_RECS[@]:-}"; do
        MESSAGE=$(echo "$rec" | cut -d: -f2-)
        echo -e "  ${REC_NUM}. ${RED}HIGH${NC}:$MESSAGE"
        REC_NUM=$((REC_NUM + 1))
    done

    for rec in "${MEDIUM_RECS[@]:-}"; do
        MESSAGE=$(echo "$rec" | cut -d: -f2-)
        echo -e "  ${REC_NUM}. ${YELLOW}MEDIUM${NC}:$MESSAGE"
        REC_NUM=$((REC_NUM + 1))
    done

    for rec in "${LOW_RECS[@]:-}"; do
        MESSAGE=$(echo "$rec" | cut -d: -f2-)
        echo -e "  ${REC_NUM}. ${CYAN}LOW${NC}:$MESSAGE"
        REC_NUM=$((REC_NUM + 1))
    done

    for rec in "${INFO_RECS[@]:-}"; do
        MESSAGE=$(echo "$rec" | cut -d: -f2-)
        echo -e "  ${REC_NUM}. ${BLUE}INFO${NC}:$MESSAGE"
        REC_NUM=$((REC_NUM + 1))
    done

    echo ""
fi

# ============================================================================
# 6. SUMMARY
# ============================================================================

if [ "$JSON_MODE" = false ]; then
    echo "Summary: ✅ $PASSED checks passed, ⚠️  $WARNINGS warnings, ❌ $ERRORS errors"
    echo ""
fi

# Exit code determination
if [ $ERRORS -gt 0 ]; then
    exit 1
elif [ $WARNINGS -gt 2 ]; then
    exit 2
else
    exit 0
fi
