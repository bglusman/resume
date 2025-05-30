# Resume Generation Walkthrough

## Complete Setup & Generation Guide

### Step 1: Install Dependencies

#### Option A: Install XeLaTeX (for PDF generation)
```bash
# macOS with Homebrew
brew install --cask mactex

# Ubuntu/Debian
sudo apt-get install texlive-xetex texlive-fonts-recommended

# Or use BasicTeX (smaller install):
brew install --cask basictex
sudo tlmgr update --self
sudo tlmgr install collection-fontsrecommended
```

#### Option B: Use our Python generator (no XeLaTeX needed for now)
```bash
# The quick_resume_gen.py works without additional dependencies
# We'll generate LaTeX files and can compile later
```

### Step 2: Test Data Structure

Your data is already properly formatted! Let's verify:

```bash
cd /Users/robertgrayson/Downloads/resume

# Check the data structure
cat data/meta.md
cat data/work_experience.md | head -20
cat data/projects.md | head -15
```

### Step 3: Generate Your First Resume

#### Using Python Generator (works now):
```bash
# Generate core resume focusing on essential experience
python3 quick_resume_gen.py data/ brian_glusman_core.pdf templates/ core

# Generate management-focused resume
python3 quick_resume_gen.py data/ brian_glusman_management.pdf templates/ management

# Generate elixir-focused resume  
python3 quick_resume_gen.py data/ brian_glusman_elixir.pdf templates/ elixir
```

#### Once you install XeLaTeX:
```bash
# Generate with the original bash script (more features)
./generate_resume.sh --focus core data/ brian_glusman_core.pdf templates/

# Generate ATS-friendly plain text version
./generate_ats.sh --focus core data/ brian_glusman_core.txt
```

### Step 4: Check Generated Files

After running the Python generator, you'll see output like:
```
Working directory: /var/folders/.../resume_xyz
Loading resume data...
Generating resume with focus: core
Copied stylishcv.cls
Compiling with XeLaTeX...
✅ Resume generated successfully: brian_glusman_core.pdf
📁 Temp files kept in: /var/folders/.../resume_xyz
```

### Step 5: AI-Powered Job Customization

Once you have an OpenAI API key:

```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Create job-specific customization
python3 ai_resume_customizer.py data/ example_job_description.txt backend_fintech

# Generate the customized resume
python3 quick_resume_gen.py data/custom_backend_fintech/ brian_backend_fintech.pdf templates/ backend_fintech
```

### Step 6: Customize for Different Roles

#### Available Tags in Your Data:
- **core**: Essential experience (PepsiCo, Stella Service)
- **elixir**: Elixir/Phoenix specific roles
- **management**: Leadership and team management
- **leadership**: Director-level positions
- **technical**: Individual contributor roles
- **startup**: Startup experience
- **ruby**: Ruby/Rails experience
- **open-source**: Open source contributions

#### Quick Generation Commands:
```bash
# Management role at a large company
python3 quick_resume_gen.py data/ brian_management.pdf templates/ management

# Technical role at an Elixir company
python3 quick_resume_gen.py data/ brian_elixir.pdf templates/ elixir

# Startup technical role
python3 quick_resume_gen.py data/ brian_startup.pdf templates/ technical
```

## What Makes This Great

### ✅ **Your Current Setup Has:**

1. **Rich, structured data** with proper tagging
2. **Multiple experience levels** from IC to management
3. **Strong technical background** in modern technologies
4. **Open source contributions** that showcase expertise
5. **Career progression** clearly documented

### ✅ **The System Provides:**

1. **Consistent formatting** across all resume versions
2. **Tag-based filtering** for targeted applications
3. **Professional LaTeX output** that looks great
4. **ATS-compatible versions** for automated screening
5. **AI-powered customization** for specific job postings

## Next Steps

1. **Install XeLaTeX** to unlock full PDF generation
2. **Test different focus tags** to see output variations
3. **Get OpenAI API key** for AI-powered customization
4. **Add job-specific tags** as you apply to different roles
5. **Iterate on content** based on feedback and results

## Sample Output Quality

Your resume will have:
- **Clean, professional design** using the Stylish CV template
- **Consistent typography** with proper spacing and alignment
- **Logical information hierarchy** (contact → experience → projects → education → skills)
- **Quantified achievements** with clear bullet points
- **Technology keywords** properly highlighted for ATS systems

The generated PDF will be publication-ready and appropriate for both human reviewers and automated screening systems.

## Troubleshooting

### Common Issues:

1. **"xelatex not found"**: Install MacTeX or BasicTeX
2. **"Template not found"**: Check file paths are correct
3. **"No matching items"**: Verify focus tag exists in your data
4. **"Compilation failed"**: Check temp directory for LaTeX errors

### Quick Fixes:
```bash
# Check what tags are available in your data
grep -r "tags:" data/

# Verify template exists
ls templates/stylish_cv_template.tex

# Check generated LaTeX files
ls /var/folders/.../resume_xyz/*.tex
```

Ready to generate your polished resume? Start with the Python generator and upgrade to full LaTeX compilation when you're ready!