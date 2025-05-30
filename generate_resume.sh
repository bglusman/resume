#!/bin/bash

# Default values
DEFAULT_FOCUS_TAG="core"
DEFAULT_TEMPLATE_FILE="resume.latex" # This is our original pandoc template
FOCUS_TAG="$DEFAULT_FOCUS_TAG"
OUTPUT_SUFFIX="$DEFAULT_FOCUS_TAG"
TEMPLATE_FILE="$DEFAULT_TEMPLATE_FILE"
DATA_DIR_ARG=""
OUTPUT_PDF_ARG=""
TEMPLATE_ASSETS_DIR_ARG=""

# Variable to hold the type of template being processed
TEMPLATE_TYPE="stylish_cv" # Default to stylish_cv

# Function to display help message
display_help() {
    echo "Usage: $0 [options] <data_dir> <output_pdf_file> <template_assets_dir>"
    echo "Options:"
    echo "  --focus <tag>      Focus on a specific tag (default: $DEFAULT_FOCUS_TAG)"
    echo "  --template <file>  Use a custom template file (default: $DEFAULT_TEMPLATE_FILE)"
    echo "  -h, --help         Display this help message"
    exit 0
}

# Function to generate meta info for stylish_cv template
# Expects: $1 = input meta_info.md path, $2 = output .tex file path
generate_meta_info_tex_stylish_cv() {
    local meta_file="$1"
    local output_tex_file="$2"

    local name_raw email_raw phone_raw location_full_raw
    name_raw=$(yq -r 'select(document_index == 0) | .name // ""' "$meta_file")
    email_raw=$(yq -r 'select(document_index == 0) | .email // ""' "$meta_file")
    phone_raw=$(yq -r 'select(document_index == 0) | .phone // ""' "$meta_file")
    location_full_raw=$(yq -r 'select(document_index == 0) | .location // ""' "$meta_file")

    local my_name my_email my_phone my_street_address my_city my_country_zip
    my_name=${name_raw:-Your Name}
    my_email=${email_raw:-your.email@example.com}
    my_phone=${phone_raw:-(000) 000-0000}

    if [[ -n "$location_full_raw" && "$location_full_raw" != "null" ]]; then
        IFS=',' read -r -a loc_parts <<< "$location_full_raw"
        local num_loc_parts=${#loc_parts[@]}
        my_street_address=""
        my_city=""
        my_country_zip=""

        if [ "$num_loc_parts" -ge 3 ]; then
            my_country_zip=$(echo "${loc_parts[$num_loc_parts-1]}" | xargs)
            my_city=$(echo "${loc_parts[$num_loc_parts-2]}" | xargs)
            my_street_address=$(IFS=','; echo "${loc_parts[*]:0:$num_loc_parts-2}" | xargs)
        elif [ "$num_loc_parts" -eq 2 ]; then
            my_country_zip=$(echo "${loc_parts[1]}" | xargs)
            my_city=$(echo "${loc_parts[0]}" | xargs)
        elif [ "$num_loc_parts" -eq 1 ]; then
            my_city=$(echo "${loc_parts[0]}" | xargs)
        fi
    else
        my_street_address=""
        my_city=""
        my_country_zip=""
    fi

    # Sanitize for LaTeX
    my_name=$(echo "$my_name" | sed 's/&/\\&/g; s/%/\\%/g; s/#/\\#/g; s/_/\\_/g; s/\$/\\$/g; s/{/\\{/g; s/}/\\}/g; s/~/	extasciitilde{}/g; s/\^/\\textasciicircum{}/g; s/\\/\\textbackslash{}/g')
    my_email=$(echo "$my_email" | sed 's/&/\\&/g; s/%/\\%/g; s/#/\\#/g; s/_/\\_/g; s/\$/\\$/g; s/{/\\{/g; s/}/\\}/g; s/~/	extasciitilde{}/g; s/\^/\\textasciicircum{}/g; s/\\/\\textbackslash{}/g')
    my_phone=$(echo "$my_phone" | sed 's/&/\\&/g; s/%/\\%/g; s/#/\\#/g; s/_/\\_/g; s/\$/\\$/g; s/{/\\{/g; s/}/\\}/g; s/~/	extasciitilde{}/g; s/\^/\\textasciicircum{}/g; s/\\/\\textbackslash{}/g')
    my_street_address=$(echo "$my_street_address" | sed 's/&/\\&/g; s/%/\\%/g; s/#/\\#/g; s/_/\\_/g; s/\$/\\$/g; s/{/\\{/g; s/}/\\}/g; s/~/	extasciitilde{}/g; s/\^/\\textasciicircum{}/g; s/\\/\\textbackslash{}/g')
    my_city=$(echo "$my_city" | sed 's/&/\\&/g; s/%/\\%/g; s/#/\\#/g; s/_/\\_/g; s/\$/\\$/g; s/{/\\{/g; s/}/\\}/g; s/~/	extasciitilde{}/g; s/\^/\\textasciicircum{}/g; s/\\/\\textbackslash{}/g')
    my_country_zip=$(echo "$my_country_zip" | sed 's/&/\\&/g; s/%/\\%/g; s/#/\\#/g; s/_/\\_/g; s/\$/\\$/g; s/{/\\{/g; s/}/\\}/g; s/~/	extasciitilde{}/g; s/\^/\\textasciicircum{}/g; s/\\/\\textbackslash{}/g')

    cat <<EOF > "$output_tex_file"
\newcommand{\MyName}{${my_name}}
\newcommand{\MyEmail}{${my_email}}
\newcommand{\MyPhone}{${my_phone}}
\newcommand{\MyStreetAddress}{${my_street_address}}
\newcommand{\MyCity}{${my_city}}
\newcommand{\MyCountryZip}{${my_country_zip}}
EOF
}

# Function to generate work experience LaTeX
# Expects: $1 = input work_experience.md path, $2 = output .tex file path
generate_work_experience_tex() {
    local input_md_file="$1"
    local output_tex_file="$2"

    # Filter and process work experience data
    local experiences_yaml
    experiences_yaml=$(yq -r 'select(document_index == 0) | .work_experience[]? | to_yaml | @base64' "$input_md_file")

    if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
        echo "\cvsection{Experience}" > "$output_tex_file"
        echo "\begin{cventries}" >> "$output_tex_file"
    fi

    echo "$experiences_yaml" | while IFS= read -r item_b64; do
        [[ -z "$item_b64" ]] && continue
        local item_yaml=$(echo "$item_b64" | base64 --decode)

        local role company_name period location details_list
        role=$(echo "$item_yaml" | yq -r '.role // "ROLE_NOT_FOUND"')
        company_name=$(echo "$item_yaml" | yq -r '.company_name // "COMPANY_NOT_FOUND"')
        period=$(echo "$item_yaml" | yq -r '.period // "PERIOD_NOT_FOUND"')
        location=$(echo "$item_yaml" | yq -r '.location // "LOCATION_NOT_FOUND"')

        # Sanitize for LaTeX
        local role_tex company_name_tex period_tex location_tex
        role_tex=$(echo "$role" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        company_name_tex=$(echo "$company_name" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        period_tex=$(echo "$period" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        location_tex=$(echo "$location" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')

        if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
            echo "\cventry{" >> "$output_tex_file"
            echo "  ${role_tex}" >> "$output_tex_file"
            echo "}{" >> "$output_tex_file"
            echo "  ${company_name_tex}" >> "$output_tex_file"
            echo "}{" >> "$output_tex_file"
            echo "  ${location_tex}" >> "$output_tex_file"
            echo "}{" >> "$output_tex_file"
            echo "  ${period_tex}" >> "$output_tex_file"
            echo "}{%" >> "$output_tex_file"
            echo "  \begin{cvitems}" >> "$output_tex_file"
        else # stylish_cv or default
            echo "\datedsubsection{\textbf{${role_tex}}, ${company_name_tex}}{\textbf{${period_tex}}}" >> "$output_tex_file"
            echo "{\hfill \textbf{${location_tex}}}" >> "$output_tex_file"
            echo "\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]" >> "$output_tex_file"
        fi

        # Process details (list)
        details_list_b64=$(echo "$item_yaml" | yq -r '.details[]? | @base64')
        echo "$details_list_b64" | while IFS= read -r detail_b64; do
            if [[ -n "$detail_b64" ]]; then
                local detail_item=$(echo "$detail_b64" | base64 --decode)
                local detail_item_tex=$(echo "$detail_item" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
                if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
                    echo "    \item{${detail_item_tex}}" >> "$output_tex_file"
                else
                    echo "    \item ${detail_item_tex}" >> "$output_tex_file"
                fi
            fi
        done

        if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
            echo "  \end{cvitems}" >> "$output_tex_file"
            echo "}" >> "$output_tex_file"
            echo "%------------------------------------------------" >> "$output_tex_file"
        else # stylish_cv or default
            echo "\end{itemize}" >> "$output_tex_file"
            echo "\vspace{0.5em}" >> "$output_tex_file"
        fi
    done

    if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
        echo "\end{cventries}" >> "$output_tex_file"
    fi

    echo "Work experience LaTeX generated: $output_tex_file" >&2
}

# Function to generate education LaTeX
# Expects: $1 = input education.md path, $2 = output .tex file path
generate_education_tex() {
    local input_md_file="$1"
    local output_tex_file="$2"

    local education_yaml
    education_yaml=$(yq -r 'select(document_index == 0) | .education[]? | to_yaml | @base64' "$input_md_file")

    if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
        echo "\cvsection{Education}" > "$output_tex_file"
        echo "\begin{cventries}" >> "$output_tex_file"
    fi

    echo "$education_yaml" | while IFS= read -r item_b64; do
        [[ -z "$item_b64" ]] && continue
        local item_yaml=$(echo "$item_b64" | base64 --decode)

        local degree institution location period details_list
        degree=$(echo "$item_yaml" | yq -r '.degree // "DEGREE_NOT_FOUND"')
        institution=$(echo "$item_yaml" | yq -r '.institution // "INSTITUTION_NOT_FOUND"')
        location=$(echo "$item_yaml" | yq -r '.location // "LOCATION_NOT_FOUND"')
        period=$(echo "$item_yaml" | yq -r '.period // "PERIOD_NOT_FOUND"')

        local degree_tex institution_tex location_tex period_tex
        degree_tex=$(echo "$degree" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        institution_tex=$(echo "$institution" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        location_tex=$(echo "$location" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        period_tex=$(echo "$period" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')

        if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
            echo "\cventry{" >> "$output_tex_file"
            echo "  ${degree_tex}" >> "$output_tex_file"
            echo "}{" >> "$output_tex_file"
            echo "  ${institution_tex}" >> "$output_tex_file"
            echo "}{" >> "$output_tex_file"
            echo "  ${location_tex}" >> "$output_tex_file"
            echo "}{" >> "$output_tex_file"
            echo "  ${period_tex}" >> "$output_tex_file"
            echo "}{%" >> "$output_tex_file"
            # Check if details exist for awesome_cv
            local details_present=$(echo "$item_yaml" | yq 'has("details") and (.details | length > 0)')
            if [[ "$details_present" == "true" ]]; then
                echo "  \begin{cvitems}" >> "$output_tex_file"
            fi
        else # stylish_cv or default
            echo "\datedsubsection{\textbf{${degree_tex}}, \textit{${institution_tex}}}{\textbf{${period_tex}}}" >> "$output_tex_file"
            echo "{\hfill \textit{${location_tex}}}" >> "$output_tex_file"
            local details_present_stylish=$(echo "$item_yaml" | yq 'has("details") and (.details | length > 0)')
            if [[ "$details_present_stylish" == "true" ]]; then
                 echo "\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]" >> "$output_tex_file"
            fi
        fi

        details_list_b64=$(echo "$item_yaml" | yq -r '.details[]? | @base64')
        echo "$details_list_b64" | while IFS= read -r detail_b64; do
            if [[ -n "$detail_b64" ]]; then
                local detail_item=$(echo "$detail_b64" | base64 --decode)
                local detail_item_tex=$(echo "$detail_item" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
                if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
                    echo "    \item{${detail_item_tex}}" >> "$output_tex_file"
                else
                    echo "    \item ${detail_item_tex}" >> "$output_tex_file"
                fi
            fi
        done

        if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
            if [[ "$details_present" == "true" ]]; then
                echo "  \end{cvitems}" >> "$output_tex_file"
            fi
            echo "}" >> "$output_tex_file"
            echo "%------------------------------------------------" >> "$output_tex_file"
        else # stylish_cv or default
            if [[ "$details_present_stylish" == "true" ]]; then
                 echo "\end{itemize}" >> "$output_tex_file"
            fi
            echo "\vspace{0.5em}" >> "$output_tex_file"
        fi
    done

    if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
        echo "\end{cventries}" >> "$output_tex_file"
    fi

    echo "Education LaTeX generated: $output_tex_file" >&2
}

# Function to generate projects LaTeX
# Expects: $1 = input projects.md path, $2 = output .tex file path
generate_projects_tex() {
    local input_md_file="$1"
    local output_tex_file="$2"

    local projects_yaml
    projects_yaml=$(yq -r 'select(document_index == 0) | .projects[]? | to_yaml | @base64' "$input_md_file")

    if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
        echo "\cvsection{Projects}" > "$output_tex_file"
        echo "\begin{cventries}" >> "$output_tex_file"
    fi

    echo "$projects_yaml" | while IFS= read -r item_b64; do
        [[ -z "$item_b64" ]] && continue
        local item_yaml=$(echo "$item_b64" | base64 --decode)

        local name period technologies description details_list status
        name=$(echo "$item_yaml" | yq -r '.name // "PROJECT_NAME_NOT_FOUND"')
        period=$(echo "$item_yaml" | yq -r '.period // "PERIOD_NOT_FOUND"')
        technologies=$(echo "$item_yaml" | yq -r '.technologies // ""') # Optional
        description=$(echo "$item_yaml" | yq -r '.description // ""') # Optional
        status=$(echo "$item_yaml" | yq -r '.status // ""') # Optional, for awesome_cv location field

        local name_tex period_tex technologies_tex description_tex status_tex
        name_tex=$(echo "$name" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        period_tex=$(echo "$period" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        technologies_tex=$(echo "$technologies" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        description_tex=$(echo "$description" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
        status_tex=$(echo "$status" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')

        if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
            echo "\cventry{" >> "$output_tex_file"
            echo "  ${name_tex}" >> "$output_tex_file"
            echo "}{" >> "$output_tex_file"
            echo "  ${technologies_tex}" >> "$output_tex_file" # Using technologies as 'organization/subtitle'
            echo "}{" >> "$output_tex_file"
            echo "  ${status_tex}" >> "$output_tex_file" # Using status as 'location'
            echo "}{" >> "$output_tex_file"
            echo "  ${period_tex}" >> "$output_tex_file"
            echo "}{%" >> "$output_tex_file"
            local details_exist_awesome=$(echo "$item_yaml" | yq 'has("details") and (.details | length > 0)')
            local main_desc_exists_awesome=$(echo "$description" | tr -d '[:space:]')

            if [[ -n "$main_desc_exists_awesome" || "$details_exist_awesome" == "true" ]]; then
                echo "  \begin{cvitems}" >> "$output_tex_file"
                if [[ -n "$main_desc_exists_awesome" ]]; then
                    echo "    \item{${description_tex}}" >> "$output_tex_file"
                fi
            fi
        else # stylish_cv or default
            echo "\subsection{\textbf{${name_tex}}}" >> "$output_tex_file"
            if [[ -n "$technologies_tex" ]]; then
              echo "\textit{${technologies_tex}} \hfill \textit{${period_tex}}" >> "$output_tex_file"
            else
              echo "\hfill \textit{${period_tex}}" >> "$output_tex_file"
            fi
            local details_exist_stylish=$(echo "$item_yaml" | yq 'has("details") and (.details | length > 0)')
            local main_desc_exists_stylish=$(echo "$description" | tr -d '[:space:]')

            if [[ -n "$main_desc_exists_stylish" || "$details_exist_stylish" == "true" ]]; then
                echo "\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]" >> "$output_tex_file"
                if [[ -n "$main_desc_exists_stylish" ]]; then
                    echo "    \item ${description_tex}" >> "$output_tex_file"
                fi
            fi
        fi

        details_list_b64=$(echo "$item_yaml" | yq -r '.details[]? | @base64')
        echo "$details_list_b64" | while IFS= read -r detail_b64; do
            if [[ -n "$detail_b64" ]]; then
                local detail_item=$(echo "$detail_b64" | base64 --decode)
                local detail_item_tex=$(echo "$detail_item" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
                if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
                    echo "    \item{${detail_item_tex}}" >> "$output_tex_file"
                else
                    echo "    \item ${detail_item_tex}" >> "$output_tex_file"
                fi
            fi
        done

        if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
            if [[ -n "$main_desc_exists_awesome" || "$details_exist_awesome" == "true" ]]; then
                echo "  \end{cvitems}" >> "$output_tex_file"
            fi
            echo "}" >> "$output_tex_file"
            echo "%------------------------------------------------" >> "$output_tex_file"
        else # stylish_cv or default
            if [[ -n "$main_desc_exists_stylish" || "$details_exist_stylish" == "true" ]]; then
                echo "\end{itemize}" >> "$output_tex_file"
            fi
            echo "\vspace{0.5em}" >> "$output_tex_file"
        fi
    done

    if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
        echo "\end{cventries}" >> "$output_tex_file"
    fi

    echo "Projects LaTeX generated: $output_tex_file" >&2
}

# Function to generate skills LaTeX
# Expects: $1 = input skills.md path, $2 = output .tex file path
generate_skills_tex() {
    local input_md_file="$1"
    local output_tex_file="$2"

    local skills_data_yaml
    skills_data_yaml=$(yq -r 'select(document_index == 0) | .skills[]? | to_yaml | @base64' "$input_md_file")

    if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
        echo "\cvsection{Skills}" > "$output_tex_file"
        echo "\begin{cvskills}" >> "$output_tex_file" # awesome-cv often wraps cvskill in cvskills
    fi

    echo "$skills_data_yaml" | while IFS= read -r item_b64; do
        [[ -z "$item_b64" ]] && continue
        local item_yaml=$(echo "$item_b64" | base64 --decode)

        local category skills_list
        category=$(echo "$item_yaml" | yq -r '.category // "CATEGORY_NOT_FOUND"')

        local category_tex
        category_tex=$(echo "$category" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')

        if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
            skills_list_awesome=$(echo "$item_yaml" | yq -r '(.skills // []) | map(tostring) | join(", ")')
            local skills_list_awesome_tex=$(echo "$skills_list_awesome" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
            echo "  \cvskill{${category_tex}}{${skills_list_awesome_tex}}" >> "$output_tex_file"
        else # stylish_cv or default
            echo "\cvsubsection{${category_tex}}" >> "$output_tex_file"
            echo "\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]" >> "$output_tex_file"
            local skills_items_b64=$(echo "$item_yaml" | yq -r '.skills[]? | @base64')
            echo "$skills_items_b64" | while IFS= read -r skill_b64; do
                if [[ -n "$skill_b64" ]]; then
                    local skill_item=$(echo "$skill_b64" | base64 --decode)
                    local skill_item_tex=$(echo "$skill_item" | sed -e 's/\\/\\textbackslash{}/g' -e 's/&/\\&/g' -e 's/%/\\%/g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g' -e 's/~/	extasciitilde{}/g' -e 's/\^/\\textasciicircum{}/g')
                    echo "    \item ${skill_item_tex}" >> "$output_tex_file"
                fi
            done
            echo "\end{itemize}" >> "$output_tex_file"
            echo "\vspace{0.5em}" >> "$output_tex_file"
        fi
    done

    if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
        echo "\end{cvskills}" >> "$output_tex_file"
        echo "" >> "$output_tex_file" # Add a newline for separation, if needed
    fi

    echo "Skills LaTeX generated: $output_tex_file" >&2
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --focus)
            FOCUS_TAG="$2"
            OUTPUT_SUFFIX="$2"
            shift # past argument
            shift # past value
            ;;
        --template)
            TEMPLATE_FILE="$2"
            shift # past argument
            shift # past value
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
            # Break loop once non-option arguments are encountered
            break
            ;;
    esac
done

# Now, assign positional arguments
if [[ "$#" -lt 3 ]]; then
    echo "Error: Missing required positional arguments: <data_dir> <output_pdf_file> <template_assets_dir>"
    display_help
    exit 1
fi
DATA_DIR_ARG="$1"
OUTPUT_PDF_ARG="$2"
TEMPLATE_ASSETS_DIR_ARG="$3"

# Validate and set global variables from arguments

# Ensure DATA_DIR is an absolute path
if [[ "$DATA_DIR_ARG" = /* ]]; then
  DATA_DIR="$DATA_DIR_ARG"
else
  DATA_DIR="$PWD/$DATA_DIR_ARG"
fi
DATA_DIR=$(cd "$DATA_DIR" && pwd) # Further resolve any relative components like ..
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Data directory '$DATA_DIR_ARG' not found or is not a directory." >&2
    exit 1
fi

# Ensure OUTPUT_PDF_FILE is an absolute path and OUTPUT_DIR is created
if [[ "$OUTPUT_PDF_ARG" = /* ]]; then
  OUTPUT_PDF_FILE="$OUTPUT_PDF_ARG"
else
  OUTPUT_PDF_FILE="$PWD/$OUTPUT_PDF_ARG"
fi
OUTPUT_DIR=$(dirname "$OUTPUT_PDF_FILE")
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Could not create output directory '$OUTPUT_DIR'." >&2
        exit 1
    fi
fi

# Ensure TEMPLATE_ASSETS_DIR is an absolute path
if [[ "$TEMPLATE_ASSETS_DIR_ARG" = /* ]]; then
  TEMPLATE_ASSETS_DIR="$TEMPLATE_ASSETS_DIR_ARG"
else
  TEMPLATE_ASSETS_DIR="$PWD/$TEMPLATE_ASSETS_DIR_ARG"
fi
TEMPLATE_ASSETS_DIR=$(cd "$TEMPLATE_ASSETS_DIR" && pwd)
if [ ! -d "$TEMPLATE_ASSETS_DIR" ]; then
    echo "Error: Template assets directory '$TEMPLATE_ASSETS_DIR_ARG' not found or is not a directory." >&2
    exit 1
fi

echo "Generating resume with focus: $FOCUS_TAG using template: $TEMPLATE_FILE"
echo "Data directory: $DATA_DIR"
echo "Output PDF: $OUTPUT_PDF_FILE"
echo "Template assets directory: $TEMPLATE_ASSETS_DIR"

# Determine TEMPLATE_TYPE based on TEMPLATE_FILE
if [[ "$(basename "$TEMPLATE_FILE")" == "resume_cv.tex" ]]; then
    TEMPLATE_TYPE="awesome_cv"
elif [[ "$(basename "$TEMPLATE_FILE")" == "stylish_cv_template.tex" ]]; then
    TEMPLATE_TYPE="stylish_cv"
else
    echo "Warning: Unknown template file '$TEMPLATE_FILE'. Assuming 'stylish_cv' structure." >&2
    TEMPLATE_TYPE="stylish_cv"
fi
echo "Selected template type: $TEMPLATE_TYPE" >&2

# Define file paths for filtering (common to all templates)
ORIG_WORK_EXP_FILE="$DATA_DIR/work_experience.md"
ORIG_PROJECTS_FILE="$DATA_DIR/projects.md"

# Create temporary names for filtered files within the data directory or a dedicated temp location
# For simplicity, using data dir now, but a script-local temp dir might be cleaner.
FILTERED_WORK_EXP_FILE="$DATA_DIR/filtered_work_experience_${OUTPUT_SUFFIX}.md"
FILTERED_PROJECTS_FILE="$DATA_DIR/filtered_projects_${OUTPUT_SUFFIX}.md"

# Determine template basename for output PDF filename
TEMPLATE_FILENAME_ONLY=$(basename "$TEMPLATE_FILE")
TEMPLATE_BASENAME=${TEMPLATE_FILENAME_ONLY%.*}

# Create TEMP_DIR
TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/resume_build_temp.XXXXXX")
if [ -z "$TEMP_DIR" ] || [ ! -d "$TEMP_DIR" ]; then
  echo "ERROR: Failed to create temporary directory." >&2
  exit 1
fi
echo "Temporary directory created: $TEMP_DIR"

# Define SCRIPT_DIR and validate
SCRIPT_DIR=$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")")
if [ -z "$SCRIPT_DIR" ] || [ "$SCRIPT_DIR" == "/" ]; then
  echo 'ERROR: SCRIPT_DIR is invalid' >&2
  exit 1
fi
echo "DEBUG: SCRIPT_DIR is '$SCRIPT_DIR'"

LAST_TEMP_DIR_FILE="${SCRIPT_DIR}/.last_temp_dir.txt"
if ! echo "$TEMP_DIR" > "$LAST_TEMP_DIR_FILE"; then
  echo "ERROR: Failed to write temp dir path to $LAST_TEMP_DIR_FILE" >&2
  exit 1
fi
echo "Temporary directory path saved to $LAST_TEMP_DIR_FILE"

# yq commands to filter items
echo "Filtering work experience..."
YQ_TAG="$FOCUS_TAG" yq e '.work_experience.items |= map(select(.tags and (.tags | map(. == env(YQ_TAG)) | any))) | .work_experience.items |= (select(. != null) // [])' "$ORIG_WORK_EXP_FILE" > "$FILTERED_WORK_EXP_FILE"
if [ $? -ne 0 ]; then
    echo "Error filtering work experience. Aborting."
    # rm -f "$FILTERED_WORK_EXP_FILE" # Clean up partial file on error
    exit 1
fi
echo "Saving debug filtered work experience to $TEMP_DIR/debug_filtered_work_experience.yml"
cat "$FILTERED_WORK_EXP_FILE" > "$TEMP_DIR/debug_filtered_work_experience.yml"

echo "Filtering projects..."
YQ_TAG="$FOCUS_TAG" yq e '.projects.items |= map(select(.tags and (.tags | map(. == env(YQ_TAG)) | any))) | .projects.items |= (select(. != null) // [])' "$ORIG_PROJECTS_FILE" > "$FILTERED_PROJECTS_FILE"
if [ $? -ne 0 ]; then
    echo "Error filtering projects. Aborting."
    # rm -f "$FILTERED_PROJECTS_FILE" # Clean up partial file on error
    # rm -f "$FILTERED_WORK_EXP_FILE" # Clean up previous success if this one fails
    exit 1
fi
echo "Saving debug filtered projects to $TEMP_DIR/debug_filtered_projects.yml"
cat "$FILTERED_PROJECTS_FILE" > "$TEMP_DIR/debug_filtered_projects.yml"

# Conditional logic for template type
if [[ "$TEMPLATE_TYPE" == "stylish_cv" ]]; then
    echo "Using stylish_cv_template.tex specific generation path..."
    # TEMP_DIR creation is now earlier and global
    # echo "Temporary directory created: $TEMP_DIR"

    # 1. Generate generated_meta_info.tex (Conditionally)
    # This check is actually redundant if TEMPLATE_TYPE is already stylish_cv, but kept for clarity
    if [[ "$TEMPLATE_TYPE" == "stylish_cv" ]]; then
        echo "Generating meta info LaTeX..." >&2
        META_INFO_TEX_FILE="$TEMP_DIR/generated_meta_info.tex"
        generate_meta_info_tex_stylish_cv "$DATA_DIR/meta.md" "$META_INFO_TEX_FILE"
        echo "Meta info LaTeX generated: $META_INFO_TEX_FILE" >&2
    else
        echo "Skipping meta info LaTeX generation for non-stylish_cv type in stylish_cv block. This should not happen." >&2
    fi

    # 2. Generate generated_work_experience.tex
    echo "Generating work experience LaTeX..."
    GENERATED_WORK_EXP_TEX="$TEMP_DIR/generated_work_experience.tex"
    truncate -s 0 "$GENERATED_WORK_EXP_TEX"
    generate_work_experience_tex "$FILTERED_WORK_EXP_FILE" "$GENERATED_WORK_EXP_TEX"

    echo "Work experience LaTeX generated: $GENERATED_WORK_EXP_TEX"
    echo "Saving debug generated work experience to $TEMP_DIR/debug_generated_work_experience.tex"
    cat "$GENERATED_WORK_EXP_TEX" > "$TEMP_DIR/debug_generated_work_experience.tex"

    # 3. Generate generated_education.tex
    echo "Generating education LaTeX..."
    > "$TEMP_DIR/generated_education.tex"
    generate_education_tex "$DATA_DIR/education.md" "$TEMP_DIR/generated_education.tex"
    echo "Saving debug generated education to $TEMP_DIR/debug_generated_education.tex"
    cat "$TEMP_DIR/generated_education.tex" > "$TEMP_DIR/debug_generated_education.tex"
    
    # 4. Generate generated_projects.tex
    echo "Generating projects LaTeX..."
    GENERATED_PROJECTS_TEX="$TEMP_DIR/generated_projects.tex"
    truncate -s 0 "$GENERATED_PROJECTS_TEX"
    generate_projects_tex "$FILTERED_PROJECTS_FILE" "$GENERATED_PROJECTS_TEX"

    echo "Projects LaTeX generated: $GENERATED_PROJECTS_TEX"
    echo "Saving debug generated projects to $TEMP_DIR/debug_generated_projects.tex"
    cat "$GENERATED_PROJECTS_TEX" > "$TEMP_DIR/debug_generated_projects.tex"

    # 5. Generate generated_skills.tex
    echo "Generating skills LaTeX..."
    SKILLS_TEX_FILE="$TEMP_DIR/generated_skills.tex"
    DEBUG_SKILLS_TEX_FILE="$TEMP_DIR/debug_generated_skills.tex"
    generate_skills_tex "$DATA_DIR/skills.md" "$SKILLS_TEX_FILE"
    echo "Saving debug generated skills to $DEBUG_SKILLS_TEX_FILE"
    cat "$SKILLS_TEX_FILE" > "$DEBUG_SKILLS_TEX_FILE"

    # Copy stylishcv.cls to TEMP_DIR if it exists in the script's directory or PWD
    if [[ "$TEMPLATE_FILE" == "stylish_cv_template.tex" ]]; then
        if [ -f "$TEMPLATE_ASSETS_DIR/stylishcv.cls" ]; then
            cp "$TEMPLATE_ASSETS_DIR/stylishcv.cls" "$TEMP_DIR/"
            echo "Copied stylishcv.cls to $TEMP_DIR" >&2
        else
            echo "Warning: stylishcv.cls not found in $TEMPLATE_ASSETS_DIR" >&2
        fi
    fi
    
    # 6. Compile with xelatex
    echo "Compiling LaTeX document with xelatex..."
    cp "$TEMPLATE_ASSETS_DIR/$TEMPLATE_FILE" "$TEMP_DIR/"
    # Ensure stylishcv.cls is available in the temp directory if it's the stylish_cv template
    if [[ "$TEMPLATE_FILE" == "stylish_cv_template.tex" ]]; then
        if [ -f "$TEMPLATE_ASSETS_DIR/stylishcv.cls" ]; then
            cp "$TEMPLATE_ASSETS_DIR/stylishcv.cls" "$TEMP_DIR/"
            echo "Copied stylishcv.cls to $TEMP_DIR" >&2
        else
            echo "Warning: stylishcv.cls not found in $TEMPLATE_ASSETS_DIR. It's required for stylish_cv." >&2
        fi
    fi
    
    (cd "$TEMP_DIR" && xelatex -interaction=nonstopmode "$TEMPLATE_FILENAME_ONLY" && xelatex -interaction=nonstopmode "$TEMPLATE_FILENAME_ONLY")
    XELATEX_EXIT_CODE=$?
    
    if [ $XELATEX_EXIT_CODE -eq 0 ] && [ -f "$TEMP_DIR/$TEMPLATE_BASENAME.pdf" ]; then
        mv "$TEMP_DIR/$TEMPLATE_BASENAME.pdf" "$OUTPUT_PDF_FILE"
        echo "Successfully generated resume: $OUTPUT_PDF_FILE"
    else
        echo "XeLaTeX failed to generate PDF or PDF not found. Check logs in $TEMP_DIR" >&2
        # exit 1 # Optionally exit on failure
    fi

elif [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
    echo "Preparing files for awesome_cv template..."
    # TEMP_DIR is already created

    # Create cv-sections directory in TEMP_DIR
    CV_SECTIONS_DIR="$TEMP_DIR/cv-sections"
    mkdir -p "$CV_SECTIONS_DIR"
    echo "Created $CV_SECTIONS_DIR" >&2

    # Generate section files into CV_SECTIONS_DIR
    echo "Generating work experience LaTeX for awesome_cv..."
    generate_work_experience_tex "$FILTERED_WORK_EXP_FILE" "$CV_SECTIONS_DIR/experience.tex"
    echo "Generating education LaTeX for awesome_cv..."
    generate_education_tex "$DATA_DIR/education.md" "$CV_SECTIONS_DIR/education.tex"
    echo "Generating projects LaTeX for awesome_cv..."
    generate_projects_tex "$FILTERED_PROJECTS_FILE" "$CV_SECTIONS_DIR/projects.tex"
    echo "Generating skills LaTeX for awesome_cv..."
    generate_skills_tex "$DATA_DIR/skills.md" "$CV_SECTIONS_DIR/skills.tex"

    # Copy awesome-cv.cls and fonts directory from TEMPLATE_ASSETS_DIR to TEMP_DIR root
    if [ -f "$TEMPLATE_ASSETS_DIR/awesome-cv.cls" ]; then
        cp "$TEMPLATE_ASSETS_DIR/awesome-cv.cls" "$TEMP_DIR/"
        echo "Copied awesome-cv.cls to $TEMP_DIR" >&2
    else
        echo "Warning: awesome-cv.cls not found in $TEMPLATE_ASSETS_DIR. It's required for awesome_cv." >&2
    fi

    if [ -d "$TEMPLATE_ASSETS_DIR/fonts" ]; then
        cp -R "$TEMPLATE_ASSETS_DIR/fonts" "$TEMP_DIR/"
        echo "Copied fonts/ directory to $TEMP_DIR" >&2
    else
        echo "Warning: fonts/ directory not found in $TEMPLATE_ASSETS_DIR. It might be required for awesome_cv." >&2
    fi
    # No PDF compilation for awesome_cv by this script.
    # Instructions will be printed at the very end.

else # Original Pandoc path for resume.latex or other Pandoc-compatible templates
    echo "Using Pandoc generation path for $TEMPLATE_FILE..."
    # Ensure TEMPLATE_FILE is an absolute path for pandoc's --template
    local absolute_template_path
    if [[ "$TEMPLATE_FILE" = /* ]]; then
        absolute_template_path="$TEMPLATE_FILE"
    else
        # If TEMPLATE_FILE was somehow relative, assume it's relative to TEMPLATE_ASSETS_DIR
        absolute_template_path="$TEMPLATE_ASSETS_DIR/$TEMPLATE_FILE"
    fi     

    pandoc \
        "$DATA_DIR/meta.md" \
        "$DATA_DIR/education.md" \
        "$DATA_DIR/skills.md" \
        "$FILTERED_WORK_EXP_FILE" \
        "$FILTERED_PROJECTS_FILE" \
        --template="$absolute_template_path" \
        -o "$OUTPUT_PDF_FILE" \
        --pdf-engine=xelatex

    if [ $? -eq 0 ]; then
        echo "Successfully generated resume: $OUTPUT_PDF_FILE"
    else
        echo "Pandoc failed to generate resume."
        # exit 1 # Optionally exit on failure
    fi
fi

# Final cleanup of filtered data files (optional)
# echo "Cleaning up filtered data files..."
# rm -f "$FILTERED_WORK_EXP_FILE"
# rm -f "$FILTERED_PROJECTS_FILE"

echo "Done."

# Instructions for awesome_cv
if [[ "$TEMPLATE_TYPE" == "awesome_cv" ]]; then
    echo ""
    echo "IMPORTANT FOR AWESOME_CV TEMPLATE:"
    echo "1. Ensure you have the 'awesome-cv' template files (resume_cv.tex, awesome-cv.cls, fonts/, etc.)."
    echo "2. The generated LaTeX section files are in: $TEMP_DIR/cv-sections/"
    echo "3. Copy these files into your 'awesome-cv/cv-sections/' directory, overwriting existing ones if necessary."
    echo "   - experience.tex"
    echo "   - education.tex"
    echo "   - skills.tex"
    echo "   - projects.tex (you may need to add '\input{cv-sections/projects.tex}' to your resume_cv.tex)"
    echo "4. Manually configure your personal information (name, contact details, etc.) directly in your 'resume_cv.tex' file."
    echo "5. Compile your main 'resume_cv.tex' file using XeLaTeX."
fi
