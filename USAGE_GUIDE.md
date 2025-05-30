# Professional Resume Generator - Complete Usage Guide

A robust, dependency-light system for generating professional resumes from structured markdown data. Supports both full-length and condensed one-page formats.

## Features

- **📄 Multiple Formats**: Generate full-length or condensed one-page resumes
- **🎯 Tag-based Filtering**: Focus on specific skills or experience (e.g., "elixir", "management", "core")
- **📝 Markdown-based Data**: Easy-to-edit resume data in YAML frontmatter
- **🎨 Professional Templates**: Clean, ATS-friendly LaTeX templates
- **🔧 Robust Error Handling**: Clear error messages and dependency checking
- **⚡ Zero Python Dependencies**: No external Python packages required

## Quick Start

### 1. Setup
```bash
# Run the setup script to install dependencies
./setup.sh
```

### 2. Generate Your Resume
```bash
# Easy way - use the wrapper script
./generate_resume my_resume.pdf

# One-page version
./generate_resume my_resume.pdf --onepage

# Focus on specific experience
./generate_resume my_resume.pdf --focus elixir

# Direct Python usage
python3 resume_generator.py data/ my_resume.pdf templates/
```

## Data Structure

Your resume data lives in the `data/` directory as markdown files with YAML frontmatter:

### `data/meta.md`
Basic contact information and summary:
```yaml
---
name: Your Name
email: your.email@example.com
phone: (555) 123-4567
location: City, State, Country
summary: Brief professional summary
---
```

### `data/work_experience.md`
Employment history with tagging:
```yaml
---
work_experience:
  - role: Senior Software Engineer
    company_name: Company Name
    location: City, State
    period: Jan 2022 – Present
    details:
      - "Built scalable applications using Technology X"
      - "Led team of 5 engineers"
    tags: ["core", "leadership", "technology"]
---
```

### `data/projects.md`
Key projects and achievements:
```yaml
---
projects:
  - name: Project Name
    period: "2022-2023"
    technologies: "Python, Docker, AWS"
    description: Brief project description
    details:
      - "Specific achievement or impact"
      - "Technical details"
    tags: ["core", "python"]
---
```

### `data/skills.md`
Technical skills by category:
```yaml
---
skills:
  - category: Programming Languages
    skills: [Python, JavaScript, Go, Rust]
  - category: Frameworks & Tools
    skills: [Django, React, Docker, Kubernetes]
---
```

### `data/education.md`
Educational background:
```yaml
---
education:
  - institution: University Name
    degree: B.S. Computer Science
    location: City, State
    period: May 2020
    details:
      - "GPA: 3.8/4.0"
      - "Relevant coursework: Data Structures, Algorithms"
---
```

## Tag System

Use tags to create focused resumes for different opportunities:

- **`core`**: Essential experience (always included)
- **`leadership`**: Management and team lead roles
- **`technical`**: Deep technical roles
- **`elixir`**, **`python`**, **`ruby`**: Language-specific experience
- **`startup`**: Startup experience
- **Custom tags**: Create your own for specific use cases

## Templates

### Full Resume Templates
- `stylish_cv_template.tex`: Professional template with clean styling
- `simple_cv_template.tex`: Minimalist template
- `basic_cv_template.tex`: Basic template (no special packages required)

### One-Page Template
- `onepage_cv_template.tex`: Condensed format optimized for single page

## Advanced Usage

### Command Line Options
```bash
python3 resume_generator.py data/ output.pdf templates/ [options]

Options:
  --onepage          Generate condensed one-page resume
  --focus TAG        Filter content by tag (default: core)
  --verbose, -v      Verbose output for debugging
  --help             Show full help message
```

### Examples
```bash
# Standard resume focused on core experience
python3 resume_generator.py data/ john_doe_resume.pdf templates/

# One-page resume for networking events
python3 resume_generator.py data/ john_doe_brief.pdf templates/ --onepage

# Technical resume emphasizing Python experience  
python3 resume_generator.py data/ john_doe_python.pdf templates/ --focus python

# Management-focused resume
python3 resume_generator.py data/ john_doe_leadership.pdf templates/ --focus leadership

# Verbose output for troubleshooting
python3 resume_generator.py data/ output.pdf templates/ --verbose
```

## One-Page Resume Features

When using `--onepage`, the generator automatically:

- **Limits Experience**: Shows top 3-4 most recent positions
- **Condenses Details**: Maximum 2 bullet points per job
- **Summarizes Projects**: Top 2-3 projects with brief descriptions
- **Streamlines Skills**: Key skills in paragraph format
- **Highlights Education**: Only exceptional details (GPA, honors)
- **Optimizes Layout**: Aggressive spacing and margin adjustments

Perfect for:
- Networking events
- Job fairs
- Quick reference
- Initial screening rounds
- When you need to get straight to the point

## Troubleshooting

### Common Issues

**"XeLaTeX not found"**
```bash
# Run setup script
./setup.sh

# Or install manually
brew install --cask basictex

# Add to PATH
export PATH="/usr/local/texlive/*/bin/*:$PATH"
```

**"Template not found"**
- Ensure you're running from the resume directory
- Check that `templates/` directory exists and contains `.tex` files

**"LaTeX compilation failed"**
```bash
# Run with verbose output to see details
python3 resume_generator.py data/ output.pdf templates/ --verbose

# Check for missing LaTeX packages
# BasicTeX has limited packages - some templates may not work
```

**"No matching items for tag"**
- Check your data files have the correct tag in the `tags` array
- Use `--focus core` to see all items tagged as "core"
- Verify YAML syntax in your data files

### File Permissions
```bash
# Make scripts executable
chmod +x setup.sh
chmod +x resume_generator.py
chmod +x generate_resume
```

### Python Environment
The generator uses only Python standard library modules:
- `os`, `sys`, `tempfile`, `shutil`, `subprocess`
- `argparse`, `pathlib`

No `pip install` required!

## File Structure
```
resume/
├── setup.sh                 # Setup script
├── resume_generator.py       # Main generator
├── generate_resume          # Easy wrapper script
├── data/                    # Your resume data
│   ├── meta.md
│   ├── work_experience.md
│   ├── projects.md
│   ├── education.md
│   └── skills.md
├── templates/               # LaTeX templates
│   ├── stylish_cv_template.tex
│   ├── onepage_cv_template.tex
│   └── stylishcv.cls
└── USAGE_GUIDE.md          # This file
```

## Real-World Examples

### Scenario 1: Applying for a Python Backend Role
```bash
# Generate a Python-focused resume
python3 resume_generator.py data/ backend_role.pdf templates/ --focus python

# Your work_experience.md should have Python-related jobs tagged with "python"
# Your projects.md should highlight Python projects with "python" tag
```

### Scenario 2: Networking Event
```bash
# Create a one-page resume for quick handoffs
python3 resume_generator.py data/ networking.pdf templates/ --onepage

# Perfect for business cards, quick introductions, or when space is limited
```

### Scenario 3: Leadership Position
```bash
# Emphasize management experience
python3 resume_generator.py data/ leadership_role.pdf templates/ --focus leadership

# Highlights team management, strategic planning, and leadership achievements
```

### Scenario 4: Startup Application
```bash
# Show entrepreneurial and startup experience
python3 resume_generator.py data/ startup_role.pdf templates/ --focus startup

# Emphasizes agility, wearing multiple hats, and startup experience
```

## Best Practices

### Data Organization
1. **Use descriptive tags**: Be specific about technologies and roles
2. **Keep details action-oriented**: Start bullets with action verbs
3. **Quantify achievements**: Include numbers, percentages, and metrics
4. **Update regularly**: Keep your data current as you gain experience

### Tag Strategy
```yaml
# Good tagging example
tags: ["core", "elixir", "backend", "leadership", "analytics"]

# This allows multiple focused resumes:
# --focus elixir     (Elixir developer role)
# --focus backend    (Backend engineer role)  
# --focus leadership (Engineering manager role)
# --focus analytics  (Data analytics role)
```

### Content Guidelines
- **Be specific**: "Improved performance by 40%" vs "Improved performance"
- **Show impact**: Focus on business outcomes, not just technical tasks
- **Use keywords**: Include technologies and buzzwords from job descriptions
- **Keep current**: Remove outdated technologies and old experience

## Contributing

To add new templates:
1. Create a new `.tex` file in `templates/`
2. Use the same LaTeX input commands:
   - `\input{generated_meta_info.tex}`
   - `\input{generated_work_experience.tex}`
   - `\input{generated_projects.tex}`
   - `\input{generated_education.tex}`
   - `\input{generated_skills.tex}`

For one-page templates, use the `_summary` and `_condensed` variants.

---

**Need help?** Check the troubleshooting section or open an issue with your specific error message and verbose output.

**Made with ❤️ for job seekers everywhere**