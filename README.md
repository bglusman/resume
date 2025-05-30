# AI-Powered Resume Generator

A sophisticated resume generation system that separates data from presentation, supports multiple output formats, and includes AI-powered customization for specific job applications.

## Features

- **Data-driven architecture**: Store resume content in structured YAML files
- **Multiple templates**: Support for LaTeX, plain text, and ATS-friendly formats
- **Tag-based filtering**: Generate different resume versions for specific job types
- **AI customization**: Automatically tailor resumes to specific job descriptions
- **ATS optimization**: Generate plain text versions optimized for Applicant Tracking Systems
- **Flexible output**: PDF, plain text, and future HTML support

## Quick Start

### Basic Resume Generation

```bash
# Generate PDF using default template and "core" tag
./generate_resume.sh data/ resume.pdf templates/

# Generate with specific focus tag
./generate_resume.sh --focus elixir data/ resume_elixir.pdf templates/

# Generate ATS-friendly plain text version
./generate_ats.sh --focus core data/ resume_ats.txt
```

### AI-Powered Job-Specific Customization

```bash
# Set up OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Create job-specific resume variant
python ai_resume_customizer.py data/ job_description.txt acme_backend

# Generate the customized resume
./generate_resume.sh --focus acme_backend data/custom_acme_backend/ resume_acme.pdf templates/
```

## Directory Structure

```
resume/
├── data/                          # Resume data files
│   ├── meta.md                    # Personal info and summary
│   ├── work_experience.md         # Work history with tags
│   ├── projects.md                # Projects with tags  
│   ├── skills.md                  # Skills by category
│   ├── education.md               # Education history
│   └── custom_*/                  # AI-generated custom variants
├── templates/                     # LaTeX and other templates
│   ├── stylish_cv_template.tex
│   ├── ats_friendly.txt
│   └── LaTeXTemplates_*/
├── generate_resume.sh             # Main resume generator
├── generate_ats.sh               # ATS text generator
├── ai_resume_customizer.py       # AI-powered customization
├── config.yaml                   # Configuration settings
└── README.md                     # This file
```

## Data Format

### Meta Information (`data/meta.md`)

```yaml
---
name: "Your Name"
email: "you@example.com"
phone: "555-123-4567"
location: "City, State"
summary: "Professional summary highlighting key skills and experience..."
---
```

### Work Experience (`data/work_experience.md`)

```yaml
---
work_experience:
  items:
  - role: "Engineering Manager"
    company: "Company Name"
    location: "City, State" 
    dates: "Jan 2020 – Present"
    description: |
      Detailed description of role and achievements...
    tags: ["core", "management", "leadership"]
  
  - role: "Senior Developer"
    company: "Previous Company"
    # ... more fields
    tags: ["core", "technical", "elixir"]
---
```

### Projects (`data/projects.md`)

```yaml
---
projects:
  items:
  - title: "Project Name"
    link: "https://github.com/user/project"
    description: "Brief project description..."
    tags: ["core", "elixir", "open-source"]
---
```

### Skills (`data/skills.md`)

```yaml
---
skills:
  categories:
  - name: "Programming Languages"
    items: ["Elixir", "Ruby", "JavaScript", "Python"]
  - name: "Frameworks"
    items: ["Phoenix", "Rails", "React"]
---
```

## Tag System

Use tags to create different resume versions:

- **core**: Essential experience for all resumes
- **elixir**: Elixir/Phoenix specific roles
- **management**: Management and leadership positions
- **technical**: Individual contributor roles
- **consulting**: Client-facing work

### Tag Presets (config.yaml)

```yaml
tag_presets:
  management:
    description: "Management and leadership roles"
    includes: ["core", "management", "leadership"]
  
  technical:
    description: "Technical/IC roles" 
    includes: ["core", "elixir", "technical"]
```

## AI Customization Workflow

1. **Prepare job description**: Save the job posting in a text file

2. **Run AI analysis**:
   ```bash
   python ai_resume_customizer.py data/ job_description.txt company_role
   ```

3. **Review generated customizations**:
   - Check `data/custom_company_role/job_analysis.json` for extracted requirements
   - Review `data/custom_company_role/skill_suggestions.json` for optimization tips
   - Verify customized descriptions in generated files

4. **Generate targeted resume**:
   ```bash
   ./generate_resume.sh --focus company_role data/custom_company_role/ resume_company.pdf templates/
   ./generate_ats.sh --focus company_role data/custom_company_role/ resume_company.txt
   ```

## Templates

### Available Templates

- **stylish_cv_template.tex**: Modern, clean design
- **awesome_cv**: Professional template with excellent typography
- **ats_friendly.txt**: Plain text optimized for ATS systems

### Adding New Templates

1. Create template file in `templates/` directory
2. Add configuration to `config.yaml`
3. Update generation functions if needed for custom template types

## Configuration

Edit `config.yaml` to customize:

- Default templates and tags
- AI model settings
- Output preferences  
- Validation rules
- Build settings

## Requirements

### Basic Generation
- `bash`
- `yq` (YAML processor)
- `xelatex` (for PDF generation)
- LaTeX packages as required by templates

### AI Features
- Python 3.7+
- OpenAI API key
- Required Python packages:
  ```bash
  pip install openai pyyaml
  ```

## Advanced Usage

### Batch Generation

```bash
# Generate multiple formats
for tag in core elixir management; do
  ./generate_resume.sh --focus $tag data/ resume_$tag.pdf templates/
  ./generate_ats.sh --focus $tag data/ resume_$tag.txt
done
```

### Custom Template Development

Templates can use these generated files:
- `generated_meta_info.tex` - Personal information
- `generated_work_experience.tex` - Work history  
- `generated_education.tex` - Education section
- `generated_projects.tex` - Projects section
- `generated_skills.tex` - Skills section

## Tips for Best Results

1. **Tag strategically**: Use specific tags for different job types
2. **Keep descriptions factual**: AI customization enhances but doesn't fabricate
3. **Review AI output**: Always verify AI-generated customizations before using
4. **Maintain data quality**: Well-structured input data produces better results
5. **Test ATS compatibility**: Use online ATS checkers to validate plain text output

## Troubleshooting

### Common Issues

- **LaTeX compilation errors**: Check template requirements and font availability
- **AI customization fails**: Verify OpenAI API key and internet connection
- **Missing data**: Ensure all required YAML fields are present
- **Template not found**: Check file paths and template configuration

### Debug Mode

Enable debug output by setting environment variables:
```bash
export DEBUG=1
./generate_resume.sh --focus core data/ resume.pdf templates/
```

## Contributing

1. Add new templates in `templates/` directory
2. Extend AI customization prompts for better results
3. Add new output formats (HTML, Word, etc.)
4. Improve ATS optimization features
5. Add validation and error handling

## License

This resume generator builds upon various LaTeX templates with their respective licenses. Check individual template directories for specific license information.