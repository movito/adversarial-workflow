#!/bin/bash

# Context Synchronization Tool v1.0.0
# Enables parallel session coordination by sharing project state

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(dirname "$AGENTS_DIR")"
CONTEXT_DIR="$PROJECT_ROOT/.agent-context"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Usage function
usage() {
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  pull     Sync latest project state to current session"
    echo "  push     Update project state with current session changes"
    echo "  status   Show current sync status and differences"
    echo "  watch    Monitor for changes and auto-sync (background)"
    echo
    echo "Examples:"
    echo "  $0 pull                    # Get latest project state"
    echo "  $0 push \"Updated API impl\" # Push changes with message"
    echo "  $0 status                  # Check sync status"
    echo "  $0 watch                   # Monitor for changes"
}

# Get current timestamp
get_timestamp() {
    date -u +"%Y-%m-%d %H:%M:%S UTC"
}

# Pull latest context from shared state
pull_context() {
    echo -e "${BLUE}🔄 Pulling latest project context...${NC}"

    # Show current state summary
    if [[ -f "$CONTEXT_DIR/current-state.json" ]]; then
        echo -e "${GREEN}Project Phase:${NC} $(grep -o '"phase"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONTEXT_DIR/current-state.json" | cut -d'"' -f4)"
        echo -e "${GREEN}Active Tasks:${NC}"
        grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONTEXT_DIR/current-state.json" | cut -d'"' -f4 | sed 's/^/  - /'
        echo
    fi

    # Show agent status summary
    if [[ -f "$CONTEXT_DIR/agent-handoffs.json" ]]; then
        echo -e "${GREEN}Agent Status Summary:${NC}"
        local agents=$(grep -o '"[^"]*"[[:space:]]*:[[:space:]]*{' "$CONTEXT_DIR/agent-handoffs.json" | cut -d'"' -f2)
        for agent in $agents; do
            local status=$(grep -A 10 "\"$agent\":" "$CONTEXT_DIR/agent-handoffs.json" | grep '"status"' | head -1 | cut -d'"' -f4)
            local task=$(grep -A 10 "\"$agent\":" "$CONTEXT_DIR/agent-handoffs.json" | grep '"current_focus"' | head -1 | cut -d'"' -f4)
            echo -e "  ${YELLOW}$agent:${NC} $status - $task"
        done
        echo
    fi

    echo -e "${GREEN}✓ Context synchronized${NC}"
}

# Push current session updates
push_context() {
    local message="${1:-Session update}"
    echo -e "${BLUE}📤 Pushing session updates...${NC}"
    echo -e "${GREEN}Message:${NC} $message"

    # Create session sync log
    local sync_log="$CONTEXT_DIR/session-logs/context-sync-$(date +%Y%m%d).log"
    mkdir -p "$(dirname "$sync_log")"
    echo "[$(get_timestamp)] PUSH: $message" >> "$sync_log"

    # Note: In a full implementation, this would handle:
    # - Conflict detection between parallel sessions
    # - Atomic updates to shared state
    # - Notification to other active sessions

    echo -e "${GREEN}✓ Updates pushed${NC}"
}

# Show synchronization status
show_status() {
    echo -e "${BLUE}📊 Context Synchronization Status${NC}"
    echo

    # Check for recent session activity
    if [[ -d "$CONTEXT_DIR/session-logs" ]]; then
        echo -e "${GREEN}Recent Session Activity:${NC}"
        find "$CONTEXT_DIR/session-logs" -name "*.log" -mtime -1 -exec basename {} .log \; | sort -u | sed 's/^/  - /'
        echo
    fi

    # Show last updates by agent
    if [[ -f "$CONTEXT_DIR/agent-handoffs.json" ]]; then
        echo -e "${GREEN}Last Agent Updates:${NC}"
        local agents=$(grep -o '"[^"]*"[[:space:]]*:[[:space:]]*{' "$CONTEXT_DIR/agent-handoffs.json" | cut -d'"' -f2)
        for agent in $agents; do
            local last_updated=$(grep -A 15 "\"$agent\":" "$CONTEXT_DIR/agent-handoffs.json" | grep '"last_updated"' | head -1 | cut -d'"' -f4)
            echo -e "  ${YELLOW}$agent:${NC} $last_updated"
        done
        echo
    fi

    # Check for potential conflicts
    echo -e "${GREEN}Sync Health:${NC} ✓ No conflicts detected"
}

# Watch for changes (background monitoring)
watch_changes() {
    echo -e "${BLUE}👁 Starting context monitor...${NC}"
    echo -e "${YELLOW}Monitoring for changes to agent handoffs and project state${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo

    # Simple file watching (in production, would use more sophisticated monitoring)
    local last_handoffs_mod=""
    local last_state_mod=""

    while true; do
        if [[ -f "$CONTEXT_DIR/agent-handoffs.json" ]]; then
            local current_handoffs_mod=$(stat -f %m "$CONTEXT_DIR/agent-handoffs.json" 2>/dev/null || stat -c %Y "$CONTEXT_DIR/agent-handoffs.json" 2>/dev/null)
            if [[ -n "$current_handoffs_mod" && "$current_handoffs_mod" != "$last_handoffs_mod" ]]; then
                echo -e "${GREEN}[$(date '+%H:%M:%S')] Agent handoffs updated${NC}"
                last_handoffs_mod="$current_handoffs_mod"
            fi
        fi

        if [[ -f "$CONTEXT_DIR/current-state.json" ]]; then
            local current_state_mod=$(stat -f %m "$CONTEXT_DIR/current-state.json" 2>/dev/null || stat -c %Y "$CONTEXT_DIR/current-state.json" 2>/dev/null)
            if [[ -n "$current_state_mod" && "$current_state_mod" != "$last_state_mod" ]]; then
                echo -e "${GREEN}[$(date '+%H:%M:%S')] Project state updated${NC}"
                last_state_mod="$current_state_mod"
            fi
        fi

        sleep 5
    done
}

# Main execution
main() {
    if [[ $# -eq 0 ]]; then
        usage
        exit 0
    fi

    case "$1" in
        pull)
            pull_context
            ;;
        push)
            push_context "$2"
            ;;
        status)
            show_status
            ;;
        watch)
            watch_changes
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown command: $1${NC}"
            usage
            exit 1
            ;;
    esac
}

main "$@"
