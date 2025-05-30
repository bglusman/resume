#!/usr/bin/env python3
"""
Professional Resume Generator - Clean, modern output
Generates beautifully formatted resumes with proper typography
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

def create_professional_template(temp_dir):
    """Create a professional LaTeX template"""
    template_content = r"""
\documentclass[11pt, letterpaper]{article}

% Page setup
\usepackage[margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{titlesec}

% Define colors
\definecolor{sectioncolor}{RGB}{0, 100, 150}
\definecolor{subcolor}{RGB}{100, 100, 100}

% Section formatting
\titleformat{\section}
  {\large\bfseries\color{sectioncolor}}
  {}{0em}
  {}[\titlerule]

\titlespacing*{\section}{0pt}{12pt}{6pt}

% Custom commands
\newcommand{\resumeitem}[1]{\item{#1}}
\newcommand{\resumeitemlist}[1]{\begin{itemize}[leftmargin=0.15in, label={}]{#1}\end{itemize}}

\newcommand{\workentry}[4]{
  \textbf{#1} \hfill \textbf{#2} \\
  \textit{#3} \hfill \textit{#4} \\
  \vspace{2pt}
}

\newcommand{\eduentry}[4]{
  \textbf{#1} \hfill \textbf{#2} \\
  \textit{#3} \hfill \textit{#4} \\
  \vspace{2pt}
}

\newcommand{\projentry}[3]{
  \textbf{#1} \hfill \textbf{#2} \\
  \textit{#3} \\
  \vspace{2pt}
}

% Remove paragraph indentation
\setlength{\parindent}{0pt}

% Input generated files
\input{generated_meta_info.tex}

\begin{document}

% Header
\begin{center}
  {\LARGE\textbf{\MyName}} \\
  \vspace{4pt}
  \MyEmail \quad $\bullet$ \quad \MyPhone \quad $\bullet$ \quad \MyStreetAddress, \MyCity \MyCountryZip
\end{center}

\vspace{8pt}

% Content sections
\section{Experience}
\input{generated_work_experience.tex}

\section{Education}  
\input{generated_education.tex}

\section{Projects}
\input{generated_projects.tex}

\section{Technical Skills}
\input{generated_skills.tex}

\end{document}
"""
    
    with open(temp_dir / "professional_template.tex", 'w') as f:
        f.write(template_content.strip())

def generate_content_files(temp_dir, data, focus_tag):
    """Generate all content files with professional formatting"""
    
    # Meta info
    meta = data['meta']
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
    
    # Work experience
    work_items = data['work_experience'].get('work_experience', [])
    filtered_work = filter_by_tag(work_items, focus_tag)
    
    with open(temp_dir / "generated_work_experience.tex", 'w') as f:
        for item in filtered_work:
            role = latex_escape(item.get('role', ''))
            company = latex_escape(item.get('company_name', ''))
            period = latex_escape(item.get('period', ''))
            location = latex_escape(item.get('location', ''))
            
            f.write(f"\\workentry{{{role}}}{{{period}}}{{{company}}}{{{location}}}\n")
            
            details = item.get('details', [])
            if details:
                f.write("\\resumeitemlist{\n")
                for detail in details:
                    f.write(f"  \\resumeitem{{{latex_escape(detail)}}}\n")
                f.write("}\n")
            f.write("\\vspace{8pt}\n\n")
    
    # Projects
    project_items = data['projects'].get('projects', [])
    filtered_projects = filter_by_tag(project_items, focus_tag)
    
    with open(temp_dir / "generated_projects.tex", 'w') as f:
        for item in filtered_projects:
            name = latex_escape(item.get('name', ''))
            period = latex_escape(item.get('period', ''))
            technologies = latex_escape(item.get('technologies', ''))
            description = latex_escape(item.get('description', ''))
            
            f.write(f"\\projentry{{{name}}}{{{period}}}{{{technologies}}}\n")
            
            if description:
                f.write(f"{description}\n")
            
            details = item.get('details', [])
            if details:
                f.write("\\resumeitemlist{\n")
                for detail in details:
                    f.write(f"  \\resumeitem{{{latex_escape(detail)}}}\n")
                f.write("}\n")
            f.write("\\vspace{8pt}\n\n")
    
    # Education
    education_items = data['education'].get('education', [])
    
    with open(temp_dir / "generated_education.tex", 'w') as f:
        for item in education_items:
            degree = latex_escape(item.get('degree', ''))
            institution = latex_escape(item.get('institution', ''))
            period = latex_escape(item.get('period', ''))
            location = latex_escape(item.get('location', ''))
            
            f.write(f"\\eduentry{{{degree}}}{{{period}}}{{{institution}}}{{{location}}}\n")
            
            details = item.get('details', [])
            if details:
                f.write("\\resumeitemlist{\n")
                for detail in details:
                    f.write(f"  \\resumeitem{{{latex_escape(detail)}}}\n")
                f.write("}\n")
            f.write("\\vspace{8pt}\n\n")
    
    # Skills
    skills_items = data['skills'].get('skills', [])
    
    with open(temp_dir / "generated_skills.tex", 'w') as f:
        for item in skills_items:
            if isinstance(item, dict):
                category = latex_escape(item.get('category', ''))
                skill_items = item.get('skills', [])
                
                skills_text = ", ".join([latex_escape(skill) for skill in skill_items])
                f.write(f"\\textbf{{{category}}}: {skills_text} \\\\\n")
                f.write("\\vspace{3pt}\n")

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 professional_resume_gen.py <data_dir> <output_pdf> <focus_tag>")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    output_pdf = Path(sys.argv[2])
    focus_tag = sys.argv[3] if len(sys.argv) > 3 else "core"
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="professional_resume_"))
    print(f"Working directory: {temp_dir}")
    
    try:
        # Load all data
        print("Loading resume data...")
        data = {
            'meta': load_resume_data(data_dir / "meta.md"),
            'work_experience': load_resume_data(data_dir / "work_experience.md"),
            'projects': load_resume_data(data_dir / "projects.md"),
            'education': load_resume_data(data_dir / "education.md"),
            'skills': load_resume_data(data_dir / "skills.md")
        }
        
        print(f"Generating professional resume with focus: {focus_tag}")
        
        # Create template and content
        create_professional_template(temp_dir)
        generate_content_files(temp_dir, data, focus_tag)
        
        # Find XeLaTeX
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
            result1 = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', 'professional_template.tex'], 
                                   capture_output=True, text=True)
            result2 = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', 'professional_template.tex'], 
                                   capture_output=True, text=True)
            
            os.chdir(old_cwd)
            
            pdf_file = temp_dir / "professional_template.pdf"
            if pdf_file.exists():
                shutil.copy(pdf_file, output_pdf)
                print(f"✅ Professional resume generated: {output_pdf}")
                print(f"📁 Files kept in: {temp_dir}")
            else:
                print("❌ LaTeX compilation failed")
                print("Log file:", temp_dir / "professional_template.log")
                with open(temp_dir / "professional_template.log", 'r') as f:
                    print(f.read()[-1000:])  # Last 1000 chars
        else:
            print("❌ XeLaTeX not found")
            print(f"Generated files in: {temp_dir}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()