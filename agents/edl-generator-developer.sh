#!/bin/bash

# EDL Generator Developer Agent
# Specialized in EDL/XML export format generation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  EDL Generator Developer Agent v2.0.0 ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

echo -e "${GREEN}Specializing in:${NC}"
echo "• CMX 3600 EDL generation"
echo "• FCPXML format creation"
echo "• Industry-standard export formats"
echo "• Import workflow optimization"
echo "• Format compatibility testing"
echo

echo -e "${BLUE}Launching Claude Code with EDL Generator Developer role...${NC}"
echo

# Change to project directory
cd "$PROJECT_ROOT"

# Launch Claude Code with agent-specific context
exec claude --model claude-3-5-sonnet-20241022 --role "edl-generator-developer" "$@"
