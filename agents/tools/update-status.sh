#!/bin/bash

# Agent Status Update Tool v1.0.0
# Standardized way for agents to update their status

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(dirname "$AGENTS_DIR")"
CONTEXT_DIR="$PROJECT_ROOT/.agent-context"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Usage function
usage() {
    echo "Usage: $0 <agent-role> <status> [task-file] [notes]"
    echo
    echo "Agent Roles: api-developer, format-developer, media-processor, test-runner, coordinator, document-reviewer"
    echo "Status: available, working, blocked, completed"
    echo
    echo "Examples:"
    echo "  $0 api-developer completed TASK-P3-002.md 'API integration finished, all tests passing'"
    echo "  $0 media-processor blocked TASK-P3-001.md 'Waiting for precision requirements clarification'"
    echo "  $0 test-runner working TASK-P3-001.md 'Running precision validation tests'"
}

# Validate inputs
if [[ $# -lt 2 ]]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    usage
    exit 1
fi

AGENT_ROLE="$1"
STATUS="$2"
TASK_FILE="${3:-}"
NOTES="${4:-}"

# Validate agent role
VALID_ROLES="api-developer format-developer media-processor test-runner coordinator document-reviewer"
if [[ ! " $VALID_ROLES " =~ " $AGENT_ROLE " ]]; then
    echo -e "${RED}Error: Invalid agent role: $AGENT_ROLE${NC}"
    echo "Valid roles: $VALID_ROLES"
    exit 1
fi

# Validate status
VALID_STATUSES="available working blocked completed pending coordinating"
if [[ ! " $VALID_STATUSES " =~ " $STATUS " ]]; then
    echo -e "${RED}Error: Invalid status: $STATUS${NC}"
    echo "Valid statuses: $VALID_STATUSES"
    exit 1
fi

# Check if handoffs file exists
HANDOFFS_FILE="$CONTEXT_DIR/agent-handoffs.json"
if [[ ! -f "$HANDOFFS_FILE" ]]; then
    echo -e "${RED}Error: Agent handoffs file not found: $HANDOFFS_FILE${NC}"
    exit 1
fi

# Create session log entry
LOG_DIR="$CONTEXT_DIR/session-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$AGENT_ROLE-$(date +%Y%m%d).log"

echo "[$TIMESTAMP] Status: $STATUS | Task: $TASK_FILE | Notes: $NOTES" >> "$LOG_FILE"

# Interactive prompts for additional details
echo -e "${BLUE}Updating status for: ${YELLOW}$AGENT_ROLE${NC}"
echo -e "Current status: ${GREEN}$STATUS${NC}"
echo

# Get current focus
read -p "Current focus/task description: " CURRENT_FOCUS
if [[ -z "$CURRENT_FOCUS" ]]; then
    CURRENT_FOCUS="Status updated via automation"
fi

# Get dependencies if blocked
DEPENDENCIES=""
if [[ "$STATUS" == "blocked" ]]; then
    read -p "What is blocking this task? " BLOCKING_REASON
    read -p "Dependencies needed: " DEPENDENCIES
    CURRENT_FOCUS="BLOCKED - $CURRENT_FOCUS"
fi

# Backup current handoffs
cp "$HANDOFFS_FILE" "$HANDOFFS_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# Update the JSON file using a temporary Python script
cat > /tmp/update_handoffs.py << EOF
import json
import sys

# Read the current handoffs
with open('$HANDOFFS_FILE', 'r') as f:
    data = json.load(f)

# Update the specific agent
agent_data = data.get('$AGENT_ROLE', {})
agent_data['current_focus'] = '$CURRENT_FOCUS'
agent_data['status'] = '$STATUS'
agent_data['last_updated'] = '$TIMESTAMP'

if '$TASK_FILE':
    agent_data['task_file'] = '$TASK_FILE'

if '$NOTES':
    agent_data['technical_notes'] = '$NOTES'

if '$DEPENDENCIES':
    agent_data['dependencies'] = '$DEPENDENCIES'
    if '$STATUS' == 'blocked':
        agent_data['blocking_reason'] = '${BLOCKING_REASON:-Unknown blocking issue}'

data['$AGENT_ROLE'] = agent_data

# Write back the updated data
with open('$HANDOFFS_FILE', 'w') as f:
    json.dump(data, f, indent=2)

print("Status updated successfully")
EOF

python3 /tmp/update_handoffs.py
rm /tmp/update_handoffs.py

echo -e "${GREEN}✓ Status updated for $AGENT_ROLE${NC}"
echo -e "${GREEN}✓ Session logged to $LOG_FILE${NC}"
echo
echo -e "${BLUE}Updated status:${NC}"
grep -A 8 "\"$AGENT_ROLE\":" "$HANDOFFS_FILE"
