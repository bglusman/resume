#!/usr/bin/env python3
"""
Quick Resume Generator - No external dependencies
Generates a stylish CV directly from the data files
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

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 quick_resume_gen.py <data_dir> <output_pdf> <template_dir> [focus_tag]")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    output_pdf = Path(sys.argv[2])
    template_dir = Path(sys.argv[3])
    focus_tag = sys.argv[4] if len(sys.argv) > 4 else "core"
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="resume_"))
    print(f"Working directory: {temp_dir}")
    
    try:
        # Load data
        print("Loading resume data...")
        meta = load_resume_data(data_dir / "meta.md")
        work_exp = load_resume_data(data_dir / "work_experience.md")
        projects = load_resume_data(data_dir / "projects.md")
        education = load_resume_data(data_dir / "education.md")
        skills = load_resume_data(data_dir / "skills.md")
        
        print(f"Generating resume with focus: {focus_tag}")
        
        # Generate meta info
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
        
        # Generate work experience
        work_items = work_exp.get('work_experience', [])
        filtered_work = filter_by_tag(work_items, focus_tag)
        
        with open(temp_dir / "generated_work_experience.tex", 'w') as f:
            for item in filtered_work:
                role = latex_escape(item.get('role', ''))
                company = latex_escape(item.get('company_name', ''))
                period = latex_escape(item.get('period', ''))
                location = latex_escape(item.get('location', ''))
                
                f.write(f"\\datedsubsection{{\\textbf{{{role}}}, {company}}}{{\\textbf{{{period}}}}}\n")
                f.write(f"{{\\hfill \\textbf{{{location}}}}}\n")
                
                details = item.get('details', [])
                if details:
                    f.write("\\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]\n")
                    for detail in details:
                        f.write(f"    \\item {latex_escape(detail)}\n")
                    f.write("\\end{itemize}\n")
                f.write("\\vspace{0.5em}\n\n")
        
        # Generate projects
        project_items = projects.get('projects', [])
        filtered_projects = filter_by_tag(project_items, focus_tag)
        
        with open(temp_dir / "generated_projects.tex", 'w') as f:
            for item in filtered_projects:
                name = latex_escape(item.get('name', ''))
                period = latex_escape(item.get('period', ''))
                technologies = latex_escape(item.get('technologies', ''))
                description = latex_escape(item.get('description', ''))
                
                f.write(f"\\subsection{{\\textbf{{{name}}}}}\n")
                if technologies:
                    f.write(f"\\textit{{{technologies}}} \\hfill \\textit{{{period}}}\n")
                else:
                    f.write(f"\\hfill \\textit{{{period}}}\n")
                
                details = item.get('details', [])
                if description or details:
                    f.write("\\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]\n")
                    if description:
                        f.write(f"    \\item {description}\n")
                    for detail in details:
                        f.write(f"    \\item {latex_escape(detail)}\n")
                    f.write("\\end{itemize}\n")
                f.write("\\vspace{0.5em}\n\n")
        
        # Generate education
        education_items = education.get('education', [])
        
        with open(temp_dir / "generated_education.tex", 'w') as f:
            for item in education_items:
                degree = latex_escape(item.get('degree', ''))
                institution = latex_escape(item.get('institution', ''))
                period = latex_escape(item.get('period', ''))
                location = latex_escape(item.get('location', ''))
                
                f.write(f"\\datedsubsection{{\\textbf{{{degree}}}, \\textit{{{institution}}}}}{{\\textbf{{{period}}}}}\n")
                f.write(f"{{\\hfill \\textit{{{location}}}}}\n")
                
                details = item.get('details', [])
                if details:
                    f.write("\\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]\n")
                    for detail in details:
                        f.write(f"    \\item {latex_escape(detail)}\n")
                    f.write("\\end{itemize}\n")
                f.write("\\vspace{0.5em}\n\n")
        
        # Generate skills
        skills_items = skills.get('skills', [])
        
        with open(temp_dir / "generated_skills.tex", 'w') as f:
            for item in skills_items:
                if isinstance(item, dict):
                    category = latex_escape(item.get('category', ''))
                    f.write(f"\\cvsubsection{{{category}}}\n")
                    f.write("\\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]\n")
                    
                    skill_items = item.get('skills', [])
                    for skill in skill_items:
                        f.write(f"    \\item {latex_escape(skill)}\n")
                    
                    f.write("\\end{itemize}\n")
                    f.write("\\vspace{0.5em}\n\n")
                else:
                    print(f"Warning: Unexpected skills item format: {item}")
        
        # Copy template files - try basic template first for maximum compatibility
        basic_template = template_dir / "basic_cv_template.tex"
        simple_template = template_dir / "simple_cv_template.tex"
        stylish_template = template_dir / "stylish_cv_template.tex"
        
        if basic_template.exists():
            template_file = basic_template
            template_name = "basic_cv_template.tex"
            print("Using basic template (no packages required)")
        elif simple_template.exists():
            template_file = simple_template
            template_name = "simple_cv_template.tex"
            print("Using simple template")
        elif stylish_template.exists():
            template_file = stylish_template
            template_name = "stylish_cv_template.tex"
            print("Using stylish template")
        else:
            print(f"Error: No template file found in {template_dir}")
            sys.exit(1)
        
        shutil.copy(template_file, temp_dir / template_name)
        
        # Check for class file
        class_file = template_dir / "stylishcv.cls"
        if class_file.exists():
            shutil.copy(class_file, temp_dir / "stylishcv.cls")
            print("Copied stylishcv.cls")
        else:
            print("Warning: stylishcv.cls not found - trying without it")
        
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
        
        xelatex_available = xelatex_cmd is not None
        
        if xelatex_available:
            print("Compiling with XeLaTeX...")
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            # Run xelatex twice for proper formatting
            result1 = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', template_name], 
                                   capture_output=True, text=True)
            result2 = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', template_name], 
                                   capture_output=True, text=True)
            
            os.chdir(old_cwd)
            
            pdf_file = temp_dir / template_name.replace('.tex', '.pdf')
            if pdf_file.exists():
                shutil.copy(pdf_file, output_pdf)
                print(f"✅ Resume generated successfully: {output_pdf}")
                print(f"📁 Temp files kept in: {temp_dir}")
            else:
                print("❌ LaTeX compilation failed")
                print("STDERR from first run:")
                print(result1.stderr)
                print(f"Check temp directory: {temp_dir}")
        else:
            print("⚠️  XeLaTeX not found - LaTeX files generated but PDF compilation skipped")
            print(f"✅ Generated LaTeX files in: {temp_dir}")
            print(f"📄 Main template: {temp_dir}/{template_name}")
            print("")
            print("To complete PDF generation:")
            print("1. Install XeLaTeX: brew install --cask basictex")
            print("2. Run this command again")
            print("")
            print("Or compile manually:")
            print(f"cd {temp_dir} && xelatex {template_name}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()