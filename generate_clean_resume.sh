#!/bin/bash

# Clean Resume Generator - Easy wrapper script
# Usage: ./generate_clean_resume.sh [focus_tag]

set -e

FOCUS_TAG=${1:-core}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FILE="brian_glusman_${FOCUS_TAG}.pdf"

echo "🎯 Generating ${FOCUS_TAG}-focused resume..."
echo "📄 Output: ${OUTPUT_FILE}"

cd "$SCRIPT_DIR"
python3 minimal_professional_gen.py data/ "$OUTPUT_FILE" "$FOCUS_TAG"

if [ -f "$OUTPUT_FILE" ]; then
    echo "✅ Resume generated successfully: $OUTPUT_FILE"
    echo "💡 Available focus tags: core, management, elixir, technical, leadership"
    echo ""
    echo "📋 Quick commands:"
    echo "   ./generate_clean_resume.sh core        # Essential experience"
    echo "   ./generate_clean_resume.sh management  # Leadership roles"
    echo "   ./generate_clean_resume.sh elixir      # Elixir/Phoenix focus"
    echo "   ./generate_clean_resume.sh technical   # IC roles"
else
    echo "❌ Resume generation failed"
    exit 1
fi