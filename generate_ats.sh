#!/bin/bash

# ATS-Friendly Resume Generator
# Generates plain text version for Applicant Tracking Systems

set -e

# Default values
DEFAULT_FOCUS_TAG="core"
FOCUS_TAG="$DEFAULT_FOCUS_TAG"
OUTPUT_SUFFIX="$DEFAULT_FOCUS_TAG"
DATA_DIR_ARG=""
OUTPUT_TXT_ARG=""

# Function to display help message
display_help() {
    echo "Usage: $0 [options] <data_dir> <output_txt_file>"
    echo "Options:"
    echo "  --focus <tag>      Focus on a specific tag (default: $DEFAULT_FOCUS_TAG)"
    echo "  -h, --help         Display this help message"
    exit 0
}

# Function to generate ATS-friendly text resume
generate_ats_resume() {
    local data_dir="$1"
    local output_file="$2"
    local focus_tag="$3"
    
    # Read meta information
    local name email phone location summary
    name=$(yq -r 'select(document_index == 0) | .name // "NAME_NOT_FOUND"' "$data_dir/meta.md")
    email=$(yq -r 'select(document_index == 0) | .email // "EMAIL_NOT_FOUND"' "$data_dir/meta.md")
    phone=$(yq -r 'select(document_index == 0) | .phone // "PHONE_NOT_FOUND"' "$data_dir/meta.md")
    location=$(yq -r 'select(document_index == 0) | .location // "LOCATION_NOT_FOUND"' "$data_dir/meta.md")
    summary=$(yq -r 'select(document_index == 0) | .summary // ""' "$data_dir/meta.md")
    
    # Start building the resume
    cat > "$output_file" << EOF
$name
$email | $phone | $location

PROFESSIONAL SUMMARY
$summary

WORK EXPERIENCE
EOF
    
    # Filter and add work experience
    local filtered_work_exp=$(mktemp)
    YQ_TAG="$focus_tag" yq e '.work_experience.items |= map(select(.tags and (.tags | map(. == env(YQ_TAG)) | any))) | .work_experience.items |= (select(. != null) // [])' "$data_dir/work_experience.md" > "$filtered_work_exp"
    
    local experiences_yaml
    experiences_yaml=$(yq -r 'select(document_index == 0) | .work_experience[]? | to_yaml | @base64' "$filtered_work_exp")
    
    echo "$experiences_yaml" | while IFS= read -r item_b64; do
        [[ -z "$item_b64" ]] && continue
        local item_yaml=$(echo "$item_b64" | base64 --decode)
        
        local role company_name dates location description
        role=$(echo "$item_yaml" | yq -r '.role // "ROLE_NOT_FOUND"')
        company_name=$(echo "$item_yaml" | yq -r '.company // "COMPANY_NOT_FOUND"')
        dates=$(echo "$item_yaml" | yq -r '.dates // "DATES_NOT_FOUND"')
        location=$(echo "$item_yaml" | yq -r '.location // "LOCATION_NOT_FOUND"')
        description=$(echo "$item_yaml" | yq -r '.description // ""')
        
        echo "" >> "$output_file"
        echo "$role | $company_name | $dates" >> "$output_file"
        echo "$location" >> "$output_file"
        echo "$description" >> "$output_file"
    done
    
    # Add education
    echo -e "\n\nEDUCATION" >> "$output_file"
    
    local education_yaml
    education_yaml=$(yq -r 'select(document_index == 0) | .education[]? | to_yaml | @base64' "$data_dir/education.md")
    
    echo "$education_yaml" | while IFS= read -r item_b64; do
        [[ -z "$item_b64" ]] && continue
        local item_yaml=$(echo "$item_b64" | base64 --decode)
        
        local degree institution location date
        degree=$(echo "$item_yaml" | yq -r '.degree // "DEGREE_NOT_FOUND"')
        institution=$(echo "$item_yaml" | yq -r '.institution // "INSTITUTION_NOT_FOUND"')
        location=$(echo "$item_yaml" | yq -r '.location // "LOCATION_NOT_FOUND"')
        date=$(echo "$item_yaml" | yq -r '.date // "DATE_NOT_FOUND"')
        
        echo "" >> "$output_file"
        echo "$degree | $institution | $date" >> "$output_file"
        echo "$location" >> "$output_file"
        
        # Add details if they exist
        local details_list_b64=$(echo "$item_yaml" | yq -r '.details[]? | @base64')
        echo "$details_list_b64" | while IFS= read -r detail_b64; do
            if [[ -n "$detail_b64" ]]; then
                local detail_item=$(echo "$detail_b64" | base64 --decode)
                echo "• $detail_item" >> "$output_file"
            fi
        done
    done
    
    # Add projects
    echo -e "\n\nPROJECTS" >> "$output_file"
    
    local filtered_projects=$(mktemp)
    YQ_TAG="$focus_tag" yq e '.projects.items |= map(select(.tags and (.tags | map(. == env(YQ_TAG)) | any))) | .projects.items |= (select(. != null) // [])' "$data_dir/projects.md" > "$filtered_projects"
    
    local projects_yaml
    projects_yaml=$(yq -r 'select(document_index == 0) | .projects[]? | to_yaml | @base64' "$filtered_projects")
    
    echo "$projects_yaml" | while IFS= read -r item_b64; do
        [[ -z "$item_b64" ]] && continue
        local item_yaml=$(echo "$item_b64" | base64 --decode)
        
        local title description link
        title=$(echo "$item_yaml" | yq -r '.title // "TITLE_NOT_FOUND"')
        description=$(echo "$item_yaml" | yq -r '.description // ""')
        link=$(echo "$item_yaml" | yq -r '.link // ""')
        
        echo "" >> "$output_file"
        echo "$title" >> "$output_file"
        echo "$description" >> "$output_file"
        if [[ -n "$link" && "$link" != "null" ]]; then
            echo "$link" >> "$output_file"
        fi
    done
    
    # Add skills
    echo -e "\n\nSKILLS" >> "$output_file"
    
    local skills_yaml
    skills_yaml=$(yq -r 'select(document_index == 0) | .skills.categories[]? | to_yaml | @base64' "$data_dir/skills.md")
    
    echo "$skills_yaml" | while IFS= read -r item_b64; do
        [[ -z "$item_b64" ]] && continue
        local item_yaml=$(echo "$item_b64" | base64 --decode)
        
        local category_name skills_list
        category_name=$(echo "$item_yaml" | yq -r '.name // "CATEGORY_NOT_FOUND"')
        skills_list=$(echo "$item_yaml" | yq -r '.items | join(", ")')
        
        echo "" >> "$output_file"
        echo "$category_name: $skills_list" >> "$output_file"
    done
    
    # Cleanup
    rm -f "$filtered_work_exp" "$filtered_projects"
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --focus)
            FOCUS_TAG="$2"
            OUTPUT_SUFFIX="$2"
            shift 2
            ;;
        --help|-h)
            display_help
            exit 0
            ;;
        --*)
            echo "Unknown option: $1"
            display_help
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Now, assign positional arguments
if [[ "$#" -lt 2 ]]; then
    echo "Error: Missing required positional arguments: <data_dir> <output_txt_file>"
    display_help
    exit 1
fi

DATA_DIR_ARG="$1"
OUTPUT_TXT_ARG="$2"

# Validate and set global variables from arguments
if [[ "$DATA_DIR_ARG" = /* ]]; then
  DATA_DIR="$DATA_DIR_ARG"
else
  DATA_DIR="$PWD/$DATA_DIR_ARG"
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Data directory '$DATA_DIR_ARG' not found or is not a directory." >&2
    exit 1
fi

if [[ "$OUTPUT_TXT_ARG" = /* ]]; then
  OUTPUT_TXT_FILE="$OUTPUT_TXT_ARG"
else
  OUTPUT_TXT_FILE="$PWD/$OUTPUT_TXT_ARG"
fi

OUTPUT_TXT_DIR=$(dirname "$OUTPUT_TXT_FILE")
if [ ! -d "$OUTPUT_TXT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_TXT_DIR"
    mkdir -p "$OUTPUT_TXT_DIR"
fi

echo "Generating ATS-friendly resume with focus: $FOCUS_TAG"
echo "Data directory: $DATA_DIR"
echo "Output file: $OUTPUT_TXT_FILE"

generate_ats_resume "$DATA_DIR" "$OUTPUT_TXT_FILE" "$FOCUS_TAG"

echo "ATS-friendly resume generated successfully: $OUTPUT_TXT_FILE"