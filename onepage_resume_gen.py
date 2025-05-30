#!/usr/bin/env python3
"""
One-Page Resume Generator
Generates a condensed, single-page resume perfect for quick handoffs
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

def simple_yaml_parse(content):
    """Improved YAML parser for our specific use case"""
    lines = content.strip().split('\n')
    result = {}
    current_key = None
    current_list = None
    current_item = None
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
            
        # Measure indentation
        indent = len(line) - len(line.lstrip())
        
        if ':' in stripped and not stripped.startswith('-'):
            # Reset context if we're back to top level
            if indent == 0:
                current_list = None
                current_item = None
            
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value.startswith('[') and value.endswith(']'):
                # Parse inline list
                items = value[1:-1].split(',')
                parsed_items = []
                for item in items:
                    item = item.strip().strip('"\'')
                    if item:
                        parsed_items.append(item)
                
                if current_item and indent > indent_level:
                    current_item[key] = parsed_items
                else:
                    result[key] = parsed_items
            elif value:
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                if current_item and indent > indent_level:
                    current_item[key] = value
                else:
                    result[key] = value
            else:
                # Start of nested structure
                if indent == 0:
                    result[key] = []
                    current_key = key
                    current_list = result[key]
                    current_item = None
                    indent_level = indent
                elif current_item:
                    current_item[key] = []
        
        elif stripped.startswith('-'):
            # List item
            item_content = stripped[1:].strip()
            
            if current_list is not None:
                if ':' in item_content:
                    # Dictionary item
                    item_dict = {}
                    current_item = item_dict
                    current_list.append(item_dict)
                    
                    # Parse key-value in this line
                    if item_content:
                        key, value = item_content.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value:
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith('[') and value.endswith(']'):
                                items = value[1:-1].split(',')
                                value = [item.strip().strip('"\'') for item in items if item.strip()]
                            current_item[key] = value
                else:
                    # Simple list item or sub-item
                    if item_content.startswith('"') and item_content.endswith('"'):
                        item_content = item_content[1:-1]
                    
                    if current_item and 'details' in current_item:
                        # This is a detail item
                        if isinstance(current_item['details'], list):
                            current_item['details'].append(item_content)
                        else:
                            current_item['details'] = [item_content]
                    elif current_item:
                        # Start details list
                        current_item['details'] = [item_content]
                    else:
                        current_list.append(item_content)
        
        elif current_item is not None and indent > indent_level:
            # Continuation of previous item
            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                if value:
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith('[') and value.endswith(']'):
                        items = value[1:-1].split(',')
                        value = [item.strip().strip('"\'') for item in items if item.strip()]
                    current_item[key] = value
    
    return result

def load_resume_data(file_path):
    """Load data from markdown file with YAML frontmatter"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 2:
            return simple_yaml_parse(parts[1])
    return {}

def latex_escape(text):
    """Escape text for LaTeX"""
    if not text:
        return ""
    return (str(text).replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
               .replace('_', '\\_').replace('$', '\\$').replace('{', '\\{')
               .replace('}', '\\}').replace('~', '\\textasciitilde{}')
               .replace('^', '\\textasciicircum{}'))

def filter_by_tag(items, focus_tag):
    """Filter items by focus tag"""
    if not items:
        return []
    
    filtered = []
    for item in items:
        tags = item.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        if focus_tag in tags:
            filtered.append(item)
    return filtered

def summarize_text(text, max_words=15):
    """Summarize text to fit in limited space"""
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + "..."

def generate_work_experience_summary(work_items, focus_tag, output_file):
    """Generate condensed work experience for one-page resume"""
    filtered_work = filter_by_tag(work_items, focus_tag)
    
    # Limit to top 3-4 most recent positions
    recent_work = filtered_work[:4]
    
    with open(output_file, 'w') as f:
        for i, item in enumerate(recent_work):
            role = latex_escape(item.get('role', ''))
            company = latex_escape(item.get('company_name', ''))
            period = latex_escape(item.get('period', ''))
            
            f.write(f"\\datedsubsection{{\\textbf{{{role}}}, {company}}}{{\\textbf{{{period}}}}}\n")
            
            # Limit to 2 most impactful details
            details = item.get('details', [])
            if details:
                f.write("\\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]\n")
                for detail in details[:2]:  # Only show top 2 details
                    summarized_detail = summarize_text(detail, 20)
                    f.write(f"    \\item {latex_escape(summarized_detail)}\n")
                f.write("\\end{itemize}\n")
            
            # Reduced spacing between items
            if i < len(recent_work) - 1:
                f.write("\\vspace{0.2em}\n\n")

def generate_projects_summary(project_items, focus_tag, output_file):
    """Generate condensed projects for one-page resume"""
    filtered_projects = filter_by_tag(project_items, focus_tag)
    
    # Limit to top 2-3 most impressive projects
    top_projects = filtered_projects[:3]
    
    with open(output_file, 'w') as f:
        for i, item in enumerate(top_projects):
            name = latex_escape(item.get('name', ''))
            technologies = latex_escape(item.get('technologies', ''))
            description = latex_escape(item.get('description', ''))
            
            f.write(f"\\textbf{{{name}}}")
            if technologies:
                # Limit technologies to key ones
                tech_list = technologies.split(',')[:4]  # Show max 4 technologies
                tech_str = ', '.join([t.strip() for t in tech_list])
                f.write(f" \\textit{{({tech_str})}}")
            f.write("\\\\\n")
            
            # Show only description, no detailed bullet points
            if description:
                summarized_desc = summarize_text(description, 25)
                f.write(f"{summarized_desc}\n")
            
            if i < len(top_projects) - 1:
                f.write("\\vspace{0.3em}\n\n")

def generate_skills_condensed(skills_items, output_file):
    """Generate condensed skills in paragraph format"""
    with open(output_file, 'w') as f:
        skill_categories = []
        
        for item in skills_items:
            if isinstance(item, dict):
                category = item.get('category', '')
                skills = item.get('skills', [])
                
                # Show only top 5-6 skills per category
                top_skills = skills[:6]
                skill_str = ', '.join([latex_escape(skill) for skill in top_skills])
                
                if category and skill_str:
                    skill_categories.append(f"\\textbf{{{latex_escape(category)}:}} {skill_str}")
        
        # Format as condensed paragraphs instead of lists
        for i, category_text in enumerate(skill_categories):
            f.write(f"{category_text}")
            if i < len(skill_categories) - 1:
                f.write("\\\\[0.2em]\n")
            else:
                f.write("\n")

def generate_education_condensed(education_items, output_file):
    """Generate condensed education"""
    with open(output_file, 'w') as f:
        for item in education_items:
            degree = latex_escape(item.get('degree', ''))
            institution = latex_escape(item.get('institution', ''))
            period = latex_escape(item.get('period', ''))
            
            f.write(f"\\textbf{{{degree}}}, \\textit{{{institution}}} \\hfill \\textbf{{{period}}}\\\\\n")
            
            # Only show most relevant details (like GPA if exceptional)
            details = item.get('details', [])
            relevant_details = [d for d in details if 'GPA' in d or 'SAT' in d or 'magna' in d.lower() or 'summa' in d.lower()]
            if relevant_details:
                f.write(f"\\textit{{{latex_escape(relevant_details[0])}}}\\\\\n")
            
            f.write("\\vspace{0.2em}\n")

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 onepage_resume_gen.py <data_dir> <output_pdf> <template_dir> [focus_tag]")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    output_pdf = Path(sys.argv[2])
    template_dir = Path(sys.argv[3])
    focus_tag = sys.argv[4] if len(sys.argv) > 4 else "core"
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="onepage_resume_"))
    print(f"Working directory: {temp_dir}")
    
    try:
        # Load data
        print("Loading resume data...")
        meta = load_resume_data(data_dir / "meta.md")
        work_exp = load_resume_data(data_dir / "work_experience.md")
        projects = load_resume_data(data_dir / "projects.md")
        education = load_resume_data(data_dir / "education.md")
        skills = load_resume_data(data_dir / "skills.md")
        
        print(f"Generating one-page resume with focus: {focus_tag}")
        
        # Generate meta info (same as regular resume)
        name = meta.get('name', 'Your Name')
        email = meta.get('email', 'email@example.com')
        phone = meta.get('phone', '555-123-4567')
        location = meta.get('location', '')
        
        # Parse location
        if location and ',' in location:
            parts = [p.strip() for p in location.split(',')]
            if len(parts) >= 3:
                street, city, country_zip = parts[0], parts[1], parts[2]
            elif len(parts) == 2:
                street, city, country_zip = "", parts[0], parts[1]
            else:
                street, city, country_zip = "", parts[0], ""
        else:
            street, city, country_zip = "", location, ""
        
        with open(temp_dir / "generated_meta_info.tex", 'w') as f:
            f.write(f"\\newcommand{{\\MyName}}{{{latex_escape(name)}}}\n")
            f.write(f"\\newcommand{{\\MyEmail}}{{{latex_escape(email)}}}\n")
            f.write(f"\\newcommand{{\\MyPhone}}{{{latex_escape(phone)}}}\n")
            f.write(f"\\newcommand{{\\MyStreetAddress}}{{{latex_escape(street)}}}\n")
            f.write(f"\\newcommand{{\\MyCity}}{{{latex_escape(city)}}}\n")
            f.write(f"\\newcommand{{\\MyCountryZip}}{{{latex_escape(country_zip)}}}\n")
        
        # Generate condensed sections
        work_items = work_exp.get('work_experience', [])
        generate_work_experience_summary(work_items, focus_tag, temp_dir / "generated_work_experience_summary.tex")
        
        project_items = projects.get('projects', [])
        generate_projects_summary(project_items, focus_tag, temp_dir / "generated_projects_summary.tex")
        
        education_items = education.get('education', [])
        generate_education_condensed(education_items, temp_dir / "generated_education_condensed.tex")
        
        skills_items = skills.get('skills', [])
        generate_skills_condensed(skills_items, temp_dir / "generated_skills_condensed.tex")
        
        # Copy one-page template
        onepage_template = template_dir / "onepage_cv_template.tex"
        if not onepage_template.exists():
            print(f"Error: One-page template not found: {onepage_template}")
            sys.exit(1)
        
        shutil.copy(onepage_template, temp_dir / "onepage_cv_template.tex")
        
        # Check for class file
        class_file = template_dir / "stylishcv.cls"
        if class_file.exists():
            shutil.copy(class_file, temp_dir / "stylishcv.cls")
            print("Copied stylishcv.cls")
        
        # Try to compile with xelatex
        print("Checking for XeLaTeX...")
        
        # Common XeLaTeX paths on macOS
        xelatex_paths = [
            '/Library/TeX/texbin/xelatex',
            '/usr/local/texlive/2025basic/bin/universal-darwin/xelatex',
            '/usr/local/texlive/2024basic/bin/universal-darwin/xelatex',
            '/usr/local/texlive/2023basic/bin/universal-darwin/xelatex',
        ]
        
        xelatex_cmd = shutil.which('xelatex')
        if not xelatex_cmd:
            for path in xelatex_paths:
                if os.path.exists(path):
                    xelatex_cmd = path
                    break
        
        if xelatex_cmd:
            print("Compiling one-page resume with XeLaTeX...")
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            # Run xelatex twice for proper formatting
            result1 = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', 'onepage_cv_template.tex'], 
                                   capture_output=True, text=True)
            result2 = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', 'onepage_cv_template.tex'], 
                                   capture_output=True, text=True)
            
            os.chdir(old_cwd)
            
            pdf_file = temp_dir / "onepage_cv_template.pdf"
            if pdf_file.exists():
                shutil.copy(pdf_file, output_pdf)
                print(f"✅ One-page resume generated successfully: {output_pdf}")
                print(f"📁 Temp files kept in: {temp_dir}")
            else:
                print("❌ LaTeX compilation failed")
                print("STDERR from first run:")
                print(result1.stderr)
                print(f"Check temp directory: {temp_dir}")
        else:
            print("⚠️  XeLaTeX not found - LaTeX files generated but PDF compilation skipped")
            print(f"✅ Generated LaTeX files in: {temp_dir}")
            print(f"📄 Main template: {temp_dir}/onepage_cv_template.tex")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()