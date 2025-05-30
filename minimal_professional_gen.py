#!/usr/bin/env python3
"""
Minimal Professional Resume Generator
Uses only standard LaTeX - guaranteed to work with BasicTeX
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

def simple_yaml_parse(content):
    """Simple YAML parser"""
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
            
        indent = len(line) - len(line.lstrip())
        
        if ':' in stripped and not stripped.startswith('-'):
            if indent == 0:
                current_list = None
                current_item = None
            
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                parsed_items = [item.strip().strip('"\'') for item in items if item.strip()]
                
                if current_item and indent > indent_level:
                    current_item[key] = parsed_items
                else:
                    result[key] = parsed_items
            elif value:
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                if current_item and indent > indent_level:
                    current_item[key] = value
                else:
                    result[key] = value
            else:
                if indent == 0:
                    result[key] = []
                    current_key = key
                    current_list = result[key]
                    current_item = None
                    indent_level = indent
                elif current_item:
                    current_item[key] = []
        
        elif stripped.startswith('-'):
            item_content = stripped[1:].strip()
            
            if current_list is not None:
                if ':' in item_content:
                    item_dict = {}
                    current_item = item_dict
                    current_list.append(item_dict)
                    
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
                    if item_content.startswith('"') and item_content.endswith('"'):
                        item_content = item_content[1:-1]
                    
                    if current_item and 'details' in current_item:
                        if isinstance(current_item['details'], list):
                            current_item['details'].append(item_content)
                        else:
                            current_item['details'] = [item_content]
                    elif current_item:
                        current_item['details'] = [item_content]
                    else:
                        current_list.append(item_content)
        
        elif current_item is not None and indent > indent_level:
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
        print("Usage: python3 minimal_professional_gen.py <data_dir> <output_pdf> <focus_tag>")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    output_pdf = Path(sys.argv[2])
    focus_tag = sys.argv[3]
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="minimal_resume_"))
    print(f"Working directory: {temp_dir}")
    
    try:
        # Load all data
        print("Loading resume data...")
        meta = load_resume_data(data_dir / "meta.md")
        work_exp = load_resume_data(data_dir / "work_experience.md")
        projects = load_resume_data(data_dir / "projects.md")
        education = load_resume_data(data_dir / "education.md")
        skills = load_resume_data(data_dir / "skills.md")
        
        print(f"Generating resume with focus: {focus_tag}")
        
        # Create main LaTeX file with everything inline
        with open(temp_dir / "resume.tex", 'w') as f:
            # Document setup
            f.write(r"""\documentclass[11pt, letterpaper]{article}

% Minimal page setup  
\setlength{\textwidth}{6.5in}
\setlength{\textheight}{9in}
\setlength{\oddsidemargin}{0in}
\setlength{\evensidemargin}{0in}
\setlength{\topmargin}{-0.5in}
\setlength{\headheight}{0in}
\setlength{\headsep}{0in}
\setlength{\footskip}{0.5in}

% Remove paragraph indentation
\setlength{\parindent}{0pt}

% Custom commands for clean formatting
\newcommand{\sectionheading}[1]{
    \vspace{12pt}
    {\large\textbf{#1}}
    \vspace{4pt}
    \hrule
    \vspace{6pt}
}

\begin{document}

""")
            
            # Header
            name = latex_escape(meta.get('name', 'Your Name'))
            email = latex_escape(meta.get('email', 'email@example.com'))
            phone = latex_escape(meta.get('phone', '555-123-4567'))
            location = latex_escape(meta.get('location', ''))
            
            f.write(f"""% Header
\\begin{{center}}
    {{\\LARGE\\textbf{{{name}}}}} \\\\
    \\vspace{{6pt}}
    {email} $\\bullet$ {phone} $\\bullet$ {location}
\\end{{center}}

\\vspace{{12pt}}

""")
            
            # Work Experience
            f.write("\\sectionheading{Experience}\n\n")
            
            work_items = work_exp.get('work_experience', [])
            filtered_work = filter_by_tag(work_items, focus_tag)
            
            for item in filtered_work:
                role = latex_escape(item.get('role', ''))
                company = latex_escape(item.get('company_name', ''))
                period = latex_escape(item.get('period', ''))
                location = latex_escape(item.get('location', ''))
                
                f.write(f"\\textbf{{{role}}} \\hfill \\textbf{{{period}}} \\\\\n")
                f.write(f"\\textit{{{company}}} \\hfill \\textit{{{location}}} \\\\\n")
                f.write("\\vspace{3pt}\n")
                
                details = item.get('details', [])
                if details:
                    f.write("\\begin{itemize}\n")
                    for detail in details:
                        f.write(f"\\item {latex_escape(detail)}\n")
                    f.write("\\end{itemize}\n")
                f.write("\\vspace{8pt}\n\n")
            
            # Education
            f.write("\\sectionheading{Education}\n\n")
            
            education_items = education.get('education', [])
            for item in education_items:
                degree = latex_escape(item.get('degree', ''))
                institution = latex_escape(item.get('institution', ''))
                period = latex_escape(item.get('period', ''))
                location = latex_escape(item.get('location', ''))
                
                f.write(f"\\textbf{{{degree}}} \\hfill \\textbf{{{period}}} \\\\\n")
                f.write(f"\\textit{{{institution}}} \\hfill \\textit{{{location}}} \\\\\n")
                f.write("\\vspace{3pt}\n")
                
                details = item.get('details', [])
                if details:
                    f.write("\\begin{itemize}\n")
                    for detail in details:
                        f.write(f"\\item {latex_escape(detail)}\n")
                    f.write("\\end{itemize}\n")
                f.write("\\vspace{8pt}\n\n")
            
            # Projects
            f.write("\\sectionheading{Projects}\n\n")
            
            project_items = projects.get('projects', [])
            filtered_projects = filter_by_tag(project_items, focus_tag)
            
            for item in filtered_projects:
                name = latex_escape(item.get('name', ''))
                period = latex_escape(item.get('period', ''))
                technologies = latex_escape(item.get('technologies', ''))
                description = latex_escape(item.get('description', ''))
                
                f.write(f"\\textbf{{{name}}} \\hfill \\textbf{{{period}}} \\\\\n")
                if technologies:
                    f.write(f"\\textit{{{technologies}}} \\\\\n")
                
                if description:
                    f.write(f"{description} \\\\\n")
                
                details = item.get('details', [])
                if details:
                    f.write("\\begin{itemize}\n")
                    for detail in details:
                        f.write(f"\\item {latex_escape(detail)}\n")
                    f.write("\\end{itemize}\n")
                f.write("\\vspace{8pt}\n\n")
            
            # Skills
            f.write("\\sectionheading{Technical Skills}\n\n")
            
            skills_items = skills.get('skills', [])
            for item in skills_items:
                if isinstance(item, dict):
                    category = latex_escape(item.get('category', ''))
                    skill_items = item.get('skills', [])
                    
                    skills_text = ", ".join([latex_escape(skill) for skill in skill_items])
                    f.write(f"\\textbf{{{category}}}: {skills_text} \\\\\n")
                    f.write("\\vspace{3pt}\n")
            
            f.write("\n\\end{document}\n")
        
        # Find and run XeLaTeX
        xelatex_paths = [
            '/Library/TeX/texbin/xelatex',
            '/usr/local/texlive/2025basic/bin/universal-darwin/xelatex',
            '/usr/local/texlive/2024basic/bin/universal-darwin/xelatex',
        ]
        
        xelatex_cmd = shutil.which('xelatex')
        if not xelatex_cmd:
            for path in xelatex_paths:
                if os.path.exists(path):
                    xelatex_cmd = path
                    break
        
        if xelatex_cmd:
            print("Compiling with XeLaTeX...")
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            # Compile twice for proper formatting
            result1 = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', 'resume.tex'], 
                                   capture_output=True, text=True)
            result2 = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', 'resume.tex'], 
                                   capture_output=True, text=True)
            
            os.chdir(old_cwd)
            
            pdf_file = temp_dir / "resume.pdf"
            if pdf_file.exists():
                shutil.copy(pdf_file, output_pdf)
                print(f"✅ Professional resume generated: {output_pdf}")
                print(f"📁 Files kept in: {temp_dir}")
                return 0
            else:
                print("❌ LaTeX compilation failed")
                with open(temp_dir / "resume.log", 'r') as log_f:
                    print(log_f.read()[-800:])
                return 1
        else:
            print("❌ XeLaTeX not found")
            print(f"Generated LaTeX file in: {temp_dir}/resume.tex")
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())