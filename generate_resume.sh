#!/bin/bash

# Default focus tag
DEFAULT_FOCUS_TAG="core"
FOCUS_TAG="$DEFAULT_FOCUS_TAG"
OUTPUT_SUFFIX="core"

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --focus) FOCUS_TAG="$2"; OUTPUT_SUFFIX="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "Generating resume with focus: $FOCUS_TAG"

# Define file paths
DATA_DIR="data"
TEMPLATE_DIR="templates"
OUTPUT_DIR="." # Output to current directory

ORIG_WORK_EXP_FILE="$DATA_DIR/work_experience.md"
ORIG_PROJECTS_FILE="$DATA_DIR/projects.md"

FILTERED_WORK_EXP_FILE="$DATA_DIR/filtered_work_experience.md"
FILTERED_PROJECTS_FILE="$DATA_DIR/filtered_projects.md"

# yq commands to filter items
echo "Filtering work experience..."
YQ_TAG="$FOCUS_TAG" yq e '.work_experience.items |= map(select(.tags and (.tags | map(. == env(YQ_TAG)) | any)))' "$ORIG_WORK_EXP_FILE" > "$FILTERED_WORK_EXP_FILE"
if [ $? -ne 0 ]; then
    echo "Error filtering work experience. Aborting."
    exit 1
fi

echo "Filtering projects..."
YQ_TAG="$FOCUS_TAG" yq e '.projects.items |= map(select(.tags and (.tags | map(. == env(YQ_TAG)) | any)))' "$ORIG_PROJECTS_FILE" > "$FILTERED_PROJECTS_FILE"
if [ $? -ne 0 ]; then
    echo "Error filtering projects. Aborting."
    exit 1
fi

# Pandoc command
echo "Running Pandoc..."
pandoc \
    "$DATA_DIR/meta.md" \
    "$DATA_DIR/education.md" \
    "$DATA_DIR/skills.md" \
    "$FILTERED_WORK_EXP_FILE" \
    "$FILTERED_PROJECTS_FILE" \
    --template="$TEMPLATE_DIR/resume.latex" \
    -o "$OUTPUT_DIR/resume_${OUTPUT_SUFFIX}.pdf" \
    --pdf-engine=xelatex

if [ $? -eq 0 ]; then
    echo "Successfully generated resume: $OUTPUT_DIR/resume_${OUTPUT_SUFFIX}.pdf"
else
    echo "Pandoc failed to generate resume."
fi

# Optional: Clean up filtered files
# rm "$FILTERED_WORK_EXP_FILE"
# rm "$FILTERED_PROJECTS_FILE"

echo "Done."
