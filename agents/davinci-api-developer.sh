#!/bin/bash

# DaVinci API Developer Agent
# Specialized in DaVinci Resolve API automation and timeline manipulation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   DaVinci API Developer Agent v2.0.0  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

echo -e "${GREEN}Specializing in:${NC}"
echo "• DaVinci Resolve Python API integration"
echo "• Timeline manipulation and assembly"
echo "• Media pool management"
echo "• Resolve project operations"
echo "• Direct API method implementation"
echo

echo -e "${BLUE}Launching Claude Code with DaVinci API Developer role...${NC}"
echo

# Change to project directory
cd "$PROJECT_ROOT"

# Launch Claude Code with agent-specific context
exec claude --model claude-3-5-sonnet-20241022 --role "davinci-api-developer" "$@"
