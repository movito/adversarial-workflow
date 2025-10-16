#!/bin/bash

# Universal Test Runner Agent
# Reusable across all projects

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$AGENTS_DIR")"
CONFIG_DIR="$AGENTS_DIR/config"
CONTEXT_DIR="$PROJECT_ROOT/.agent-context"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load role configuration
ROLES_CONFIG="$CONFIG_DIR/agent-roles.json"
if [[ -f "$ROLES_CONFIG" ]]; then
    ROLE_JSON=$(sed -n '/\"test-runner\":/,/},/p' "$ROLES_CONFIG")
    ROLE_NAME=$(echo "$ROLE_JSON" | grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    ROLE_ICON=$(echo "$ROLE_JSON" | grep -o '"icon"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    SYSTEM_PROMPT=$(echo "$ROLE_JSON" | grep -o '"system_prompt"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
else
    # Fallback if config not found
    ROLE_NAME="Test Runner"
    ROLE_ICON="🧪"
    SYSTEM_PROMPT="You are a test runner agent. Focus on: executing test suites, validation testing, quality assurance, and performance benchmarking."
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      $ROLE_ICON $ROLE_NAME Agent v1.0.0       ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Load and display project context
PROJECT_CONTEXT=""
if [[ -f "$CONTEXT_DIR/project-brief.md" ]]; then
    PROJECT_BRIEF=$(cat "$CONTEXT_DIR/project-brief.md")
    PROJECT_CONTEXT="Project Context: $PROJECT_BRIEF. "

    echo -e "${GREEN}Project Context Loaded${NC}"
    echo "$PROJECT_BRIEF" | head -2
    echo
fi

# Load current state
if [[ -f "$CONTEXT_DIR/current-state.json" ]]; then
    PROJECT_STATE=$(cat "$CONTEXT_DIR/current-state.json")
    PROJECT_CONTEXT+="Current State: $PROJECT_STATE. "
    echo -e "${GREEN}Project State Loaded${NC}"
fi

# Load role-specific handoff
if [[ -f "$CONTEXT_DIR/agent-handoffs.json" ]]; then
    HANDOFFS=$(cat "$CONTEXT_DIR/agent-handoffs.json")
    TEST_HANDOFF=$(echo "$HANDOFFS" | sed -n '/\"test-runner\":/,/},/p')
    if [[ -n "$TEST_HANDOFF" ]]; then
        PROJECT_CONTEXT+="Role Context: $TEST_HANDOFF. "
        echo -e "${GREEN}Role-Specific Context Loaded${NC}"
    fi
fi

echo
echo -e "${BLUE}Launching Claude Code with Test Runner specialization...${NC}"
echo

# Change to project directory
cd "$PROJECT_ROOT"

# Launch Claude with full context
exec claude --append-system-prompt "$PROJECT_CONTEXT $SYSTEM_PROMPT"
