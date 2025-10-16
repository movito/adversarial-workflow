#!/bin/bash

# Stale Status Checker v1.0.0
# Detects agents with outdated status information

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(dirname "$AGENTS_DIR")"
CONTEXT_DIR="$PROJECT_ROOT/.agent-context"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

HANDOFFS_FILE="$CONTEXT_DIR/agent-handoffs.json"
CURRENT_TIME=$(date -u +%s)
STALE_THRESHOLD=$((2 * 24 * 60 * 60)) # 2 days in seconds

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Agent Status Staleness Check v1.0.0  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

if [[ ! -f "$HANDOFFS_FILE" ]]; then
    echo -e "${RED}Error: Agent handoffs file not found: $HANDOFFS_FILE${NC}"
    exit 1
fi

# Extract all agent roles from the JSON
AGENTS=$(grep -o '"[^"]*"[[:space:]]*:[[:space:]]*{' "$HANDOFFS_FILE" | cut -d'"' -f2)

STALE_COUNT=0
TOTAL_COUNT=0

for agent in $AGENTS; do
    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    # Extract the last_updated timestamp for this agent
    LAST_UPDATED=$(grep -A 20 "\"$agent\":" "$HANDOFFS_FILE" | grep "last_updated" | head -1 | cut -d'"' -f4)

    if [[ -z "$LAST_UPDATED" ]]; then
        echo -e "${RED}⚠ $agent: No last_updated timestamp found${NC}"
        STALE_COUNT=$((STALE_COUNT + 1))
        continue
    fi

    # Convert timestamp to seconds (handle both formats)
    if [[ "$LAST_UPDATED" =~ [0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        # Date only format, assume end of day
        LAST_UPDATED_SEC=$(date -d "$LAST_UPDATED 23:59:59" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$LAST_UPDATED" +%s 2>/dev/null || echo "0")
    else
        # Full timestamp format
        LAST_UPDATED_SEC=$(date -d "$LAST_UPDATED" +%s 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S UTC" "$LAST_UPDATED" +%s 2>/dev/null || echo "0")
    fi

    if [[ "$LAST_UPDATED_SEC" == "0" ]]; then
        echo -e "${RED}⚠ $agent: Invalid timestamp format: $LAST_UPDATED${NC}"
        STALE_COUNT=$((STALE_COUNT + 1))
        continue
    fi

    AGE_SEC=$((CURRENT_TIME - LAST_UPDATED_SEC))
    AGE_HOURS=$((AGE_SEC / 3600))
    AGE_DAYS=$((AGE_SEC / 86400))

    if [[ $AGE_SEC -gt $STALE_THRESHOLD ]]; then
        echo -e "${RED}🚨 $agent: STALE (${AGE_DAYS}d ${AGE_HOURS}h ago) - $LAST_UPDATED${NC}"
        STALE_COUNT=$((STALE_COUNT + 1))
    else
        if [[ $AGE_SEC -gt 86400 ]]; then
            echo -e "${YELLOW}⚠ $agent: Getting old (${AGE_DAYS}d ${AGE_HOURS}h ago) - $LAST_UPDATED${NC}"
        else
            echo -e "${GREEN}✓ $agent: Current (${AGE_HOURS}h ago) - $LAST_UPDATED${NC}"
        fi
    fi
done

echo
echo -e "${BLUE}Summary:${NC}"
echo -e "Total agents: $TOTAL_COUNT"
echo -e "Stale agents: $STALE_COUNT"
echo -e "Current agents: $((TOTAL_COUNT - STALE_COUNT))"

if [[ $STALE_COUNT -gt 0 ]]; then
    echo
    echo -e "${YELLOW}Recommendation: Request status updates from stale agents${NC}"
    echo "Use: agents/tools/update-status.sh <agent-role> <new-status>"
    exit 1
else
    echo -e "${GREEN}All agents have current status information${NC}"
    exit 0
fi
