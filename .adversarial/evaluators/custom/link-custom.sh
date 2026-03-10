#!/usr/bin/env bash
# Symlink custom evaluators into the evaluators root so the CLI finds them.
# Run after: adversarial init --force or ./scripts/core/project install-evaluators
#
# Usage: .adversarial/evaluators/custom/link-custom.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVALUATORS_DIR="$(dirname "$SCRIPT_DIR")"

cd "$EVALUATORS_DIR"
shopt -s nullglob
for f in custom/*.yml; do
    ln -sf "$f" "$(basename "$f")"
    echo "  Linked: $(basename "$f") -> $f"
done
echo "Custom evaluators linked."
