#!/bin/bash

# Universal Agent Launcher v1.0.0
# Reusable across all projects with JSON-driven configuration

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$AGENTS_DIR")"
CONFIG_DIR="$AGENTS_DIR/config"
CONTEXT_DIR="$PROJECT_ROOT/.agent-context"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load agent roles configuration
ROLES_FILE="$CONFIG_DIR/agent-roles.json"
if [[ ! -f "$ROLES_FILE" ]]; then
    echo -e "${RED}Error: Agent roles configuration not found: $ROLES_FILE${NC}"
    exit 1
fi

# Load project context (optional)
PROJECT_BRIEF=""
PROJECT_STATE=""
if [[ -f "$CONTEXT_DIR/project-brief.md" ]]; then
    PROJECT_BRIEF=$(cat "$CONTEXT_DIR/project-brief.md")
fi
if [[ -f "$CONTEXT_DIR/current-state.json" ]]; then
    PROJECT_STATE=$(cat "$CONTEXT_DIR/current-state.json")
fi

# Function to extract JSON values (simple parser for our use case)
get_json_value() {
    local json="$1"
    local key="$2"
    echo "$json" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | cut -d'"' -f4
}

get_json_object() {
    local json="$1"
    local key="$2"
    echo "$json" | sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*{\\([^}]*\\)}.*/\\1/p"
}

# Get available roles for this project type
get_project_roles() {
    local roles_config=$(cat "$ROLES_FILE")
    local all_roles=$(echo "$roles_config" | grep -o '"[^"]*"[[:space:]]*:[[:space:]]*{' | grep -v '"roles"' | grep -v '"project_types"' | cut -d'"' -f2)

    if [[ -n "$PROJECT_STATE" ]]; then
        local project_type=$(get_json_value "$PROJECT_STATE" "project_type")
        if [[ -n "$project_type" ]]; then
            # For now, return all available roles - could be filtered by project type
            echo "$all_roles"
            return
        fi
    fi
    # Default: all available roles
    echo "$all_roles"
}

# Display header
display_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   Universal Agent System v1.0.0      ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo

    if [[ -n "$PROJECT_BRIEF" ]]; then
        echo -e "${GREEN}Project Context:${NC}"
        echo "$PROJECT_BRIEF" | head -2
        echo
    fi
}

# Display available agents
list_agents() {
    local available_roles=($(get_project_roles))
    local roles_config=$(cat "$ROLES_FILE")

    echo -e "${GREEN}Available Agents:${NC}"
    echo

    local counter=1
    for role in "${available_roles[@]}"; do
        # Extract role info from JSON
        local role_json=$(echo "$roles_config" | sed -n "/\"$role\":/,/},/p")
        local name=$(echo "$role_json" | grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
        local icon=$(echo "$role_json" | grep -o '"icon"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
        local description=$(echo "$role_json" | grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)

        echo -e "  ${YELLOW}$counter${NC}) $icon $name - $description"
        counter=$((counter + 1))
    done
    echo
}

# Launch specific agent
launch_agent() {
    local agent_index="$1"
    local available_roles=($(get_project_roles))
    local roles_config=$(cat "$ROLES_FILE")

    if [[ $agent_index -lt 1 || $agent_index -gt ${#available_roles[@]} ]]; then
        echo -e "${RED}Invalid selection: $agent_index${NC}"
        return 1
    fi

    local role="${available_roles[$((agent_index - 1))]}"
    local role_json=$(echo "$roles_config" | sed -n "/\"$role\":/,/},/p")
    local name=$(echo "$role_json" | grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    local system_prompt=$(echo "$role_json" | grep -o '"system_prompt"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)

    # Build context for agent
    local full_context=""
    if [[ -n "$PROJECT_BRIEF" ]]; then
        full_context="Project Context: $PROJECT_BRIEF. "
    fi
    if [[ -n "$PROJECT_STATE" ]]; then
        full_context+="Current State: $PROJECT_STATE. "
    fi

    # Add role-specific handoff info
    if [[ -f "$CONTEXT_DIR/agent-handoffs.json" ]]; then
        local handoffs=$(cat "$CONTEXT_DIR/agent-handoffs.json")
        local role_handoff=$(echo "$handoffs" | sed -n "/\"$role\":/,/},/p")
        if [[ -n "$role_handoff" ]]; then
            full_context+="Role Context: $role_handoff. "
        fi
    fi

    echo -e "${GREEN}Launching agent: ${YELLOW}$name${NC}"
    echo

    # Change to project directory
    cd "$PROJECT_ROOT"

    # Launch Claude with full context
    exec claude --append-system-prompt "$full_context $system_prompt"
}

# Interactive agent selection
interactive_select() {
    local available_roles=($(get_project_roles))
    local roles_config=$(cat "$ROLES_FILE")

    # Build menu options
    local options=()
    for role in "${available_roles[@]}"; do
        local role_json=$(echo "$roles_config" | sed -n "/\"$role\":/,/},/p")
        local name=$(echo "$role_json" | grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
        local icon=$(echo "$role_json" | grep -o '"icon"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
        options+=("$icon $name")
    done

    echo -e "${GREEN}Select an agent:${NC}"
    echo

    PS3="Choose (number or type name): "
    select opt in "${options[@]}"; do
        if [[ -n "$opt" ]]; then
            # Get the selected index
            local selected_index=$REPLY
            launch_agent "$selected_index"
            break
        elif [[ -n "$REPLY" ]]; then
            # Try to match by name
            local match_found=false
            local counter=1
            for role in "${available_roles[@]}"; do
                local role_json=$(echo "$roles_config" | sed -n "/\"$role\":/,/},/p")
                local name=$(echo "$role_json" | grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
                local name_lower=$(echo "$name" | tr '[:upper:]' '[:lower:]')
                local reply_lower=$(echo "$REPLY" | tr '[:upper:]' '[:lower:]')

                # Match partial names (e.g., "feat" matches "Feature Developer")
                if [[ "$name_lower" == *"$reply_lower"* ]] || [[ "$role" == *"$reply_lower"* ]]; then
                    launch_agent "$counter"
                    match_found=true
                    break
                fi
                counter=$((counter + 1))
            done

            if [[ "$match_found" == false ]]; then
                echo -e "${RED}No agent found matching '$REPLY'. Try again:${NC}"
            fi
        else
            echo -e "${YELLOW}Please select a number or type an agent name.${NC}"
        fi
    done
}

# Main execution
main() {
    display_header

    if [[ $# -eq 0 ]]; then
        interactive_select
        exit 0
    fi

    case "$1" in
        help)
            list_agents
            echo -e "${BLUE}Usage:${NC}"
            echo "  $0                   Interactive selection"
            echo "  $0 <agent-name>      Launch agent by name"
            echo "  $0 <agent-number>    Launch specific agent"
            echo "  $0 help             Show this help"
            ;;
        [1-9])
            launch_agent "$1"
            ;;
        *)
            # Try to match by name
            local available_roles=($(get_project_roles))
            local roles_config=$(cat "$ROLES_FILE")
            local match_found=false
            local counter=1

            for role in "${available_roles[@]}"; do
                local role_json=$(echo "$roles_config" | sed -n "/\"$role\":/,/},/p")
                local name=$(echo "$role_json" | grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
                local name_lower=$(echo "$name" | tr '[:upper:]' '[:lower:]')
                local arg_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')

                # Match partial names or role keys
                if [[ "$name_lower" == *"$arg_lower"* ]] || [[ "$role" == *"$arg_lower"* ]]; then
                    launch_agent "$counter"
                    match_found=true
                    break
                fi
                counter=$((counter + 1))
            done

            if [[ "$match_found" == false ]]; then
                echo -e "${RED}Error: No agent found matching '$1'${NC}"
                echo -e "${YELLOW}Available agents:${NC}"
                list_agents
                exit 1
            fi
            ;;
    esac
}

# Check for project context directory
if [[ ! -d "$CONTEXT_DIR" ]]; then
    echo -e "${YELLOW}Warning: No .agent-context/ directory found${NC}"
    echo "Agents will launch without project context"
    echo
fi

main "$@"
