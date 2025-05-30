# Setup Instructions

## Dependencies Installation

### Required Tools

1. **yq** (YAML processor):
   ```bash
   # macOS with Homebrew
   brew install yq
   
   # Ubuntu/Debian
   sudo apt-get install yq
   
   # Or download from: https://github.com/mikefarah/yq
   ```

2. **XeLaTeX** (for PDF generation):
   ```bash
   # macOS with Homebrew
   brew install --cask mactex
   
   # Ubuntu/Debian
   sudo apt-get install texlive-xetex texlive-fonts-recommended
   ```

3. **Python dependencies** (for AI features):
   ```bash
   pip install openai pyyaml
   ```

### Environment Setup

1. **OpenAI API Key** (for AI customization):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   # Add to ~/.bashrc or ~/.zshrc for persistence
   ```

2. **Make scripts executable**:
   ```bash
   chmod +x generate_resume.sh
   chmod +x generate_ats.sh
   chmod +x ai_resume_customizer.py
   ```

## Quick Test

Once dependencies are installed:

```bash
# Test basic PDF generation
./generate_resume.sh data/ test_resume.pdf templates/

# Test ATS text generation
./generate_ats.sh data/ test_resume.txt

# Test AI customization (requires OpenAI API key)
python ai_resume_customizer.py data/ example_job_description.txt test_job
```

## Troubleshooting

- **yq not found**: Install yq using your package manager
- **XeLaTeX not found**: Install a complete LaTeX distribution
- **OpenAI API errors**: Check your API key and internet connection
- **Permission errors**: Ensure scripts are executable with `chmod +x`