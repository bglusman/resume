#!/usr/bin/env python3
"""
Resume Generator - Robust, dependency-free resume generation
Supports both full-length and one-page resumes
"""

import os
import sys
import tempfile
import shutil
import subprocess
import argparse
from pathlib import Path


def check_dependencies():
    """Check for required dependencies and provide helpful error messages"""
    errors = []
    
    # Check for XeLaTeX
    xelatex_paths = [
        '/Library/TeX/texbin/xelatex',
        '/usr/local/texlive/2025basic/bin/universal-darwin/xelatex',
        '/usr/local/texlive/2024basic/bin/universal-darwin/xelatex',
        '/usr/local/texlive/2023basic/bin/universal-darwin/xelatex',
        '/opt/homebrew/texlive/bin/xelatex',
    ]
    
    xelatex_cmd = shutil.which('xelatex')
    if not xelatex_cmd:
        for path in xelatex_paths:
            if os.path.exists(path):
                xelatex_cmd = path
                break
    
    if not xelatex_cmd:
        errors.append("XeLaTeX not found. Install with: brew install --cask basictex")
        errors.append("Then restart your terminal or run: export PATH=\"/usr/local/texlive/*/bin/*:$PATH\"")
    
    return errors, xelatex_cmd


def simple_yaml_parse(content):
    """Simple YAML parser for resume data files"""
    lines = content.strip().split('\n')
    result = {}
    current_key = None
    current_list = None
    current_item = None
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('---'):
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
                # Parse inline list
                items = value[1:-1].split(',')
                parsed_items = [item.strip().strip('"\'') for item in items if item.strip()]
                
                if current_item and indent > indent_level:
                    current_item[key] = parsed_items
                else:
                    result[key] = parsed_items
            elif value:
                # Remove quotes
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
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
            item_content = stripped[1:].strip()
            
            if current_list is not None:
                if ':' in item_content:
                    # Dictionary item
                    item_dict = {}
                    current_item = item_dict
                    current_list.append(item_dict)
                    
                    if item_content:
                        key, value = item_content.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if value:
                            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            elif value.startswith('[') and value.endswith(']'):
                                items = value[1:-1].split(',')
                                value = [item.strip().strip('"\'') for item in items if item.strip()]
                            current_item[key] = value
                else:
                    # Simple list item
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
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    elif value.startswith('[') and value.endswith(']'):
                        items = value[1:-1].split(',')
                        value = [item.strip().strip('"\'') for item in items if item.strip()]
                    current_item[key] = value
    
    return result


def load_resume_data(file_path):
    """Load data from markdown file with YAML frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                return simple_yaml_parse(parts[1])
        return {}
    except FileNotFoundError:
        print(f"Warning: {file_path} not found, skipping...")
        return {}
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
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


def generate_meta_info(meta, output_file):
    """Generate meta info LaTeX file"""
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
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"\\newcommand{{\\MyName}}{{{latex_escape(name)}}}\n")
        f.write(f"\\newcommand{{\\MyEmail}}{{{latex_escape(email)}}}\n")
        f.write(f"\\newcommand{{\\MyPhone}}{{{latex_escape(phone)}}}\n")
        f.write(f"\\newcommand{{\\MyStreetAddress}}{{{latex_escape(street)}}}\n")
        f.write(f"\\newcommand{{\\MyCity}}{{{latex_escape(city)}}}\n")
        f.write(f"\\newcommand{{\\MyCountryZip}}{{{latex_escape(country_zip)}}}\n")


def generate_work_experience(work_exp, focus_tag, output_file, onepage=False):
    """Generate work experience LaTeX"""
    work_items = work_exp.get('work_experience', [])
    filtered_work = filter_by_tag(work_items, focus_tag)
    
    if onepage:
        filtered_work = filtered_work[:4]  # Limit for one-page
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, item in enumerate(filtered_work):
            role = latex_escape(item.get('role', ''))
            company = latex_escape(item.get('company_name', ''))
            period = latex_escape(item.get('period', ''))
            location = latex_escape(item.get('location', ''))
            
            f.write(f"\\datedsubsection{{\\textbf{{{role}}}, {company}}}{{\\textbf{{{period}}}}}\n")
            if location:
                f.write(f"{{\\hfill \\textbf{{{location}}}}}\n")
            
            details = item.get('details', [])
            if details:
                if onepage:
                    details = details[:2]  # Limit details for one-page
                
                f.write("\\begin{itemize}\n")
                for detail in details:
                    if onepage:
                        detail = summarize_text(detail, 20)
                    f.write(f"    \\item {latex_escape(detail)}\n")
                f.write("\\end{itemize}\n")
            
            if i < len(filtered_work) - 1:
                spacing = "0.2em" if onepage else "0.5em"
                f.write(f"\\vspace{{{spacing}}}\n\n")


def generate_projects(projects, focus_tag, output_file, onepage=False):
    """Generate projects LaTeX"""
    project_items = projects.get('projects', [])
    filtered_projects = filter_by_tag(project_items, focus_tag)
    
    if onepage:
        filtered_projects = filtered_projects[:3]  # Limit for one-page
    
    with open(output_file, 'w', encoding='utf-8') as f:
        if onepage:
            # Condensed format for one-page
            for i, item in enumerate(filtered_projects):
                name = latex_escape(item.get('name', ''))
                technologies = latex_escape(item.get('technologies', ''))
                description = latex_escape(item.get('description', ''))
                
                f.write(f"\\textbf{{{name}}}")
                if technologies:
                    tech_list = technologies.split(',')[:4]
                    tech_str = ', '.join([t.strip() for t in tech_list])
                    f.write(f" \\textit{{({tech_str})}}")
                f.write("\\\\\n")
                
                if description:
                    summarized_desc = summarize_text(description, 25)
                    f.write(f"{summarized_desc}\n")
                
                if i < len(filtered_projects) - 1:
                    f.write("\\vspace{0.3em}\n\n")
        else:
            # Full format
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
                    f.write("\\begin{itemize}\n")
                    if description:
                        f.write(f"    \\item {description}\n")
                    for detail in details:
                        f.write(f"    \\item {latex_escape(detail)}\n")
                    f.write("\\end{itemize}\n")
                f.write("\\vspace{0.5em}\n\n")


def generate_education(education, output_file, onepage=False):
    """Generate education LaTeX"""
    education_items = education.get('education', [])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in education_items:
            degree = latex_escape(item.get('degree', ''))
            institution = latex_escape(item.get('institution', ''))
            period = latex_escape(item.get('period', ''))
            location = latex_escape(item.get('location', ''))
            
            if onepage:
                f.write(f"\\textbf{{{degree}}}, \\textit{{{institution}}} \\hfill \\textbf{{{period}}}\\\\\n")
                
                details = item.get('details', [])
                relevant_details = [d for d in details if 'GPA' in d or 'SAT' in d or 'magna' in d.lower() or 'summa' in d.lower()]
                if relevant_details:
                    f.write(f"\\textit{{{latex_escape(relevant_details[0])}}}\\\\\n")
                f.write("\\vspace{0.2em}\n")
            else:
                f.write(f"\\datedsubsection{{\\textbf{{{degree}}}, \\textit{{{institution}}}}}{{\\textbf{{{period}}}}}\n")
                if location:
                    f.write(f"{{\\hfill \\textit{{{location}}}}}\n")
                
                details = item.get('details', [])
                if details:
                    f.write("\\begin{itemize}\n")
                    for detail in details:
                        f.write(f"    \\item {latex_escape(detail)}\n")
                    f.write("\\end{itemize}\n")
                f.write("\\vspace{0.5em}\n\n")


def generate_skills(skills, output_file, onepage=False):
    """Generate skills LaTeX"""
    skills_items = skills.get('skills', [])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        if onepage:
            # Condensed paragraph format
            skill_categories = []
            
            for item in skills_items:
                if isinstance(item, dict):
                    category = item.get('category', '')
                    skill_list = item.get('skills', [])
                    
                    top_skills = skill_list[:6]  # Show only top 6 skills
                    skill_str = ', '.join([latex_escape(skill) for skill in top_skills])
                    
                    if category and skill_str:
                        skill_categories.append(f"\\textbf{{{latex_escape(category)}:}} {skill_str}")
            
            for i, category_text in enumerate(skill_categories):
                f.write(f"{category_text}")
                if i < len(skill_categories) - 1:
                    f.write("\\\\[0.2em]\n")
                else:
                    f.write("\n")
        else:
            # Full format with lists
            for item in skills_items:
                if isinstance(item, dict):
                    category = latex_escape(item.get('category', ''))
                    f.write(f"\\cvsubsection{{{category}}}\n")
                    f.write("\\begin{itemize}\n")
                    
                    skill_items = item.get('skills', [])
                    for skill in skill_items:
                        f.write(f"    \\item {latex_escape(skill)}\n")
                    
                    f.write("\\end{itemize}\n")
                    f.write("\\vspace{0.5em}\n\n")


def compile_latex(temp_dir, template_name, xelatex_cmd):
    """Compile LaTeX to PDF"""
    old_cwd = os.getcwd()
    try:
        os.chdir(temp_dir)
        
        # Run XeLaTeX twice for proper formatting
        for i in range(2):
            result = subprocess.run([xelatex_cmd, '-interaction=nonstopmode', template_name], 
                                   capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                # Read log file for more details
                log_file = template_name.replace('.tex', '.log')
                log_content = ""
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                    except:
                        pass
                
                error_msg = f"LaTeX compilation failed (exit code {result.returncode})\n"
                if result.stderr:
                    error_msg += f"STDERR: {result.stderr}\n"
                if log_content:
                    # Extract key error lines
                    lines = log_content.split('\n')
                    error_lines = [line for line in lines if '!' in line or 'Error' in line or 'error' in line]
                    if error_lines:
                        error_msg += f"Key errors from log:\n" + '\n'.join(error_lines[:5])
                
                return False, error_msg
        
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "LaTeX compilation timed out"
    except Exception as e:
        return False, str(e)
    finally:
        os.chdir(old_cwd)


def main():
    parser = argparse.ArgumentParser(
        description="Generate professional resumes from markdown data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate regular resume
  python3 resume_generator.py data/ output.pdf templates/
  
  # Generate one-page resume  
  python3 resume_generator.py data/ output.pdf templates/ --onepage
  
  # Focus on specific experience
  python3 resume_generator.py data/ output.pdf templates/ --focus elixir
        """
    )
    
    parser.add_argument('data_dir', help='Directory containing resume data files')
    parser.add_argument('output_pdf', help='Output PDF file path')
    parser.add_argument('template_dir', help='Template directory')
    parser.add_argument('--focus', default='core', help='Focus tag for filtering content (default: core)')
    parser.add_argument('--onepage', action='store_true', help='Generate condensed one-page resume')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Convert to Path objects
    data_dir = Path(args.data_dir)
    output_pdf = Path(args.output_pdf)
    template_dir = Path(args.template_dir)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    errors, xelatex_cmd = check_dependencies()
    if errors:
        print("❌ Missing dependencies:")
        for error in errors:
            print(f"   {error}")
        sys.exit(1)
    
    if args.verbose:
        print(f"✅ XeLaTeX found: {xelatex_cmd}")
    
    # Validate input directories
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        sys.exit(1)
    
    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        sys.exit(1)
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix=f"resume_{'onepage_' if args.onepage else ''}"))
    if args.verbose:
        print(f"📁 Working directory: {temp_dir}")
    
    try:
        # Load data
        print("📄 Loading resume data...")
        meta = load_resume_data(data_dir / "meta.md")
        work_exp = load_resume_data(data_dir / "work_experience.md")
        projects = load_resume_data(data_dir / "projects.md")
        education = load_resume_data(data_dir / "education.md")
        skills = load_resume_data(data_dir / "skills.md")
        
        mode = "one-page" if args.onepage else "full-length"
        print(f"🎯 Generating {mode} resume with focus: {args.focus}")
        
        # Generate LaTeX files
        generate_meta_info(meta, temp_dir / "generated_meta_info.tex")
        
        if args.onepage:
            generate_work_experience(work_exp, args.focus, temp_dir / "generated_work_experience_summary.tex", onepage=True)
            generate_projects(projects, args.focus, temp_dir / "generated_projects_summary.tex", onepage=True)
            generate_education(education, temp_dir / "generated_education_condensed.tex", onepage=True)
            generate_skills(skills, temp_dir / "generated_skills_condensed.tex", onepage=True)
        else:
            generate_work_experience(work_exp, args.focus, temp_dir / "generated_work_experience.tex")
            generate_projects(projects, args.focus, temp_dir / "generated_projects.tex")
            generate_education(education, temp_dir / "generated_education.tex")
            generate_skills(skills, temp_dir / "generated_skills.tex")
        
        # Choose template
        if args.onepage:
            template_file = template_dir / "onepage_cv_template.tex"
            template_name = "onepage_cv_template.tex"
        else:
            # Try templates in order of preference
            for template_name in ["basic_cv_template.tex", "simple_cv_template.tex", "stylish_cv_template.tex"]:
                template_file = template_dir / template_name
                if template_file.exists():
                    break
            else:
                print(f"❌ No suitable template found in {template_dir}")
                sys.exit(1)
        
        if not template_file.exists():
            print(f"❌ Template not found: {template_file}")
            sys.exit(1)
        
        # Copy template and class files
        shutil.copy(template_file, temp_dir / template_name)
        
        class_file = template_dir / "stylishcv.cls"
        if class_file.exists():
            shutil.copy(class_file, temp_dir / "stylishcv.cls")
            if args.verbose:
                print("✅ Copied stylishcv.cls")
        
        # Compile LaTeX
        print("🔧 Compiling LaTeX...")
        success, error_msg = compile_latex(temp_dir, template_name, xelatex_cmd)
        
        if success:
            pdf_file = temp_dir / template_name.replace('.tex', '.pdf')
            if pdf_file.exists():
                shutil.copy(pdf_file, output_pdf)
                print(f"✅ Resume generated successfully: {output_pdf}")
                if args.verbose:
                    print(f"📁 Temp files kept in: {temp_dir}")
            else:
                print("❌ PDF file not found after compilation")
                sys.exit(1)
        else:
            print("❌ LaTeX compilation failed")
            if error_msg:
                print(f"Error: {error_msg}")
            print(f"Check temp directory for details: {temp_dir}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()