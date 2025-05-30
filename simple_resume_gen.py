#!/usr/bin/env python3
"""
Simple Resume Generator - Python version
Quick alternative to test resume generation without yq dependency
"""

import yaml
import os
import sys
from pathlib import Path
import argparse

def load_yaml_data(file_path):
    """Load YAML data from markdown file with frontmatter"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 2:
            return yaml.safe_load(parts[1])
    return {}

def filter_by_tags(items, focus_tag):
    """Filter items by focus tag"""
    if not items:
        return []
    
    filtered = []
    for item in items:
        tags = item.get('tags', [])
        if focus_tag in tags:
            filtered.append(item)
    return filtered

def generate_stylish_cv_meta(meta_data, output_file):
    """Generate meta info LaTeX for stylish CV"""
    name = meta_data.get('name', 'Your Name')
    email = meta_data.get('email', 'your.email@example.com')
    phone = meta_data.get('phone', '(000) 000-0000')
    location = meta_data.get('location', '')
    
    # Parse location
    if location and ',' in location:
        parts = location.split(',')
        street = parts[0].strip() if len(parts) > 2 else ""
        city = parts[-2].strip() if len(parts) > 1 else parts[0].strip()
        country_zip = parts[-1].strip()
    else:
        street = ""
        city = location
        country_zip = ""
    
    # LaTeX escaping
    def latex_escape(text):
        return (text.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
                   .replace('_', '\\_').replace('$', '\\$').replace('{', '\\{')
                   .replace('}', '\\}').replace('~', '\\textasciitilde{}')
                   .replace('^', '\\textasciicircum{}').replace('\\', '\\textbackslash{}'))
    
    with open(output_file, 'w') as f:
        f.write(f"\\newcommand{{\\MyName}}{{{latex_escape(name)}}}\n")
        f.write(f"\\newcommand{{\\MyEmail}}{{{latex_escape(email)}}}\n")
        f.write(f"\\newcommand{{\\MyPhone}}{{{latex_escape(phone)}}}\n")
        f.write(f"\\newcommand{{\\MyStreetAddress}}{{{latex_escape(street)}}}\n")
        f.write(f"\\newcommand{{\\MyCity}}{{{latex_escape(city)}}}\n")
        f.write(f"\\newcommand{{\\MyCountryZip}}{{{latex_escape(country_zip)}}}\n")

def generate_work_experience_tex(work_data, focus_tag, output_file):
    """Generate work experience LaTeX"""
    work_items = work_data.get('work_experience', [])
    filtered_work = filter_by_tags(work_items, focus_tag)
    
    def latex_escape(text):
        return (str(text).replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
                   .replace('_', '\\_').replace('$', '\\$').replace('{', '\\{')
                   .replace('}', '\\}').replace('~', '\\textasciitilde{}')
                   .replace('^', '\\textasciicircum{}').replace('\\', '\\textbackslash{}'))
    
    with open(output_file, 'w') as f:
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

def generate_projects_tex(projects_data, focus_tag, output_file):
    """Generate projects LaTeX"""
    project_items = projects_data.get('projects', [])
    filtered_projects = filter_by_tags(project_items, focus_tag)
    
    def latex_escape(text):
        return (str(text).replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
                   .replace('_', '\\_').replace('$', '\\$').replace('{', '\\{')
                   .replace('}', '\\}').replace('~', '\\textasciitilde{}')
                   .replace('^', '\\textasciicircum{}').replace('\\', '\\textbackslash{}'))
    
    with open(output_file, 'w') as f:
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

def generate_education_tex(education_data, output_file):
    """Generate education LaTeX"""
    education_items = education_data.get('education', [])
    
    def latex_escape(text):
        return (str(text).replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
                   .replace('_', '\\_').replace('$', '\\$').replace('{', '\\{')
                   .replace('}', '\\}').replace('~', '\\textasciitilde{}')
                   .replace('^', '\\textasciicircum{}').replace('\\', '\\textbackslash{}'))
    
    with open(output_file, 'w') as f:
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

def generate_skills_tex(skills_data, output_file):
    """Generate skills LaTeX"""
    skills_items = skills_data.get('skills', [])
    
    def latex_escape(text):
        return (str(text).replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
                   .replace('_', '\\_').replace('$', '\\$').replace('{', '\\{')
                   .replace('}', '\\}').replace('~', '\\textasciitilde{}')
                   .replace('^', '\\textasciicircum{}').replace('\\', '\\textbackslash{}'))
    
    with open(output_file, 'w') as f:
        for item in skills_items:
            category = latex_escape(item.get('category', ''))
            f.write(f"\\cvsubsection{{{category}}}\n")
            f.write("\\begin{itemize}[leftmargin=*, itemsep=0pt, parsep=0pt, topsep=0pt]\n")
            
            skills = item.get('skills', [])
            for skill in skills:
                f.write(f"    \\item {latex_escape(skill)}\n")
            
            f.write("\\end{itemize}\n")
            f.write("\\vspace{0.5em}\n\n")

def main():
    parser = argparse.ArgumentParser(description="Simple Python resume generator")
    parser.add_argument("--focus", default="core", help="Focus tag for filtering")
    parser.add_argument("data_dir", help="Directory containing resume data")
    parser.add_argument("output_pdf", help="Output PDF file path")
    parser.add_argument("template_dir", help="Template directory")
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    template_dir = Path(args.template_dir)
    output_pdf = Path(args.output_pdf)
    focus_tag = args.focus
    
    # Create temp directory
    import tempfile
    temp_dir = Path(tempfile.mkdtemp(prefix="resume_gen_"))
    print(f"Working in temp directory: {temp_dir}")
    
    try:
        # Load data
        meta_data = load_yaml_data(data_dir / "meta.md")
        work_data = load_yaml_data(data_dir / "work_experience.md")
        projects_data = load_yaml_data(data_dir / "projects.md")
        education_data = load_yaml_data(data_dir / "education.md")
        skills_data = load_yaml_data(data_dir / "skills.md")
        
        print(f"Generating resume with focus: {focus_tag}")
        
        # Generate LaTeX files
        generate_stylish_cv_meta(meta_data, temp_dir / "generated_meta_info.tex")
        generate_work_experience_tex(work_data, focus_tag, temp_dir / "generated_work_experience.tex")
        generate_projects_tex(projects_data, focus_tag, temp_dir / "generated_projects.tex")
        generate_education_tex(education_data, temp_dir / "generated_education.tex")
        generate_skills_tex(skills_data, temp_dir / "generated_skills.tex")
        
        # Copy template
        import shutil
        template_file = template_dir / "stylish_cv_template.tex"
        if template_file.exists():
            shutil.copy(template_file, temp_dir / "stylish_cv_template.tex")
        else:
            print(f"Template not found: {template_file}")
            return 1
        
        # Copy class file if exists
        class_file = template_dir / "stylishcv.cls"
        if class_file.exists():
            shutil.copy(class_file, temp_dir / "stylishcv.cls")
        
        # Compile with xelatex
        print("Compiling with XeLaTeX...")
        os.chdir(temp_dir)
        result = os.system("xelatex -interaction=nonstopmode stylish_cv_template.tex >/dev/null 2>&1")
        result = os.system("xelatex -interaction=nonstopmode stylish_cv_template.tex >/dev/null 2>&1")  # Run twice
        
        if result == 0 and (temp_dir / "stylish_cv_template.pdf").exists():
            shutil.copy(temp_dir / "stylish_cv_template.pdf", output_pdf)
            print(f"✅ Resume generated successfully: {output_pdf}")
            return 0
        else:
            print("❌ LaTeX compilation failed")
            print("Check temp directory for errors:", temp_dir)
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())