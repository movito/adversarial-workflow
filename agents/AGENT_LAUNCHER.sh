#!/bin/bash

# Thematic Cuts Multi-Agent Launcher v2.0.0
# Launch specialized agents for the DaVinci Resolve automation project

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$AGENTS_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Agent configurations
declare -A AGENTS=(
    ["davinci-api-developer"]="DaVinci Resolve API automation and timeline manipulation"
    ["edl-generator-developer"]="EDL/XML generation and export format specialist"
    ["media-processor"]="Audio/video processing and timecode validation"
    ["test-runner"]="Testing and verification"
)

# Display header
display_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   Thematic Cuts Multi-Agent System v2.0.0${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
}

# Display available agents
list_agents() {
    echo -e "${GREEN}Available Agents:${NC}"
    echo
    for agent in "${!AGENTS[@]}"; do
        echo -e "  ${YELLOW}$agent${NC}"
        echo -e "    ${AGENTS[$agent]}"
        echo
    done
}

# Launch specific agent
launch_agent() {
    local agent_name="$1"
    local agent_script="$AGENTS_DIR/${agent_name}.sh"

    if [[ ! -f "$agent_script" ]]; then
        echo -e "${RED}Error: Agent script not found: $agent_script${NC}"
        return 1
    fi

    echo -e "${GREEN}Launching agent: ${YELLOW}$agent_name${NC}"
    echo -e "Description: ${AGENTS[$agent_name]}"
    echo

    # Make script executable if not already
    chmod +x "$agent_script"

    # Launch the agent
    "$agent_script"
}

# Main menu
main_menu() {
    display_header

    if [[ $# -eq 0 ]]; then
        list_agents
        echo -e "${BLUE}Usage:${NC}"
        echo "  $0 <agent-name>    Launch specific agent"
        echo "  $0 all            Launch all agents in sequence"
        echo "  $0 help           Show this help"
        echo
        echo -e "${BLUE}Example:${NC}"
        echo "  $0 security-reviewer"
        echo
        exit 0
    fi

    case "$1" in
        help)
            list_agents
            echo -e "${BLUE}Usage:${NC}"
            echo "  $0 <agent-name>    Launch specific agent"
            echo "  $0 all            Launch all agents in sequence"
            echo
            ;;
        all)
            echo -e "${GREEN}Launching all agents in sequence...${NC}"
            echo
            for agent in davinci-api-developer edl-generator-developer media-processor test-runner; do
                if [[ -n "${AGENTS[$agent]}" ]]; then
                    launch_agent "$agent"
                    echo -e "${BLUE}---${NC}"
                    echo
                fi
            done
            ;;
        *)
            if [[ -n "${AGENTS[$1]}" ]]; then
                launch_agent "$1"
            else
                echo -e "${RED}Error: Unknown agent: $1${NC}"
                echo
                list_agents
                exit 1
            fi
            ;;
    esac
}

# Check if running from correct directory
if [[ ! -f "$PROJECT_ROOT/2025-09-11 Initial conversation.txt" ]] && [[ ! -d "$PROJECT_ROOT/.claude" ]]; then
    echo -e "${RED}Error: This script must be run from the thematic-cuts project${NC}"
    exit 1
fi

# Run main menu
main_menu "$@"
