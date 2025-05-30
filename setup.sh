#!/bin/bash

# Resume Generator Setup Script
# Installs dependencies and prepares the environment

set -e

echo "🚀 Setting up Resume Generator environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This setup script is designed for macOS. For other systems, please install XeLaTeX manually."
    exit 1
fi

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_error "Homebrew is required but not installed."
    print_info "Install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

print_status "Homebrew found"

# Check if XeLaTeX is already available
if command -v xelatex &> /dev/null; then
    print_status "XeLaTeX already installed: $(which xelatex)"
else
    # Check common installation paths
    XELATEX_PATHS=(
        "/Library/TeX/texbin/xelatex"
        "/usr/local/texlive/2025basic/bin/universal-darwin/xelatex"
        "/usr/local/texlive/2024basic/bin/universal-darwin/xelatex"
        "/usr/local/texlive/2023basic/bin/universal-darwin/xelatex"
    )
    
    FOUND_XELATEX=""
    for path in "${XELATEX_PATHS[@]}"; do
        if [[ -f "$path" ]]; then
            FOUND_XELATEX="$path"
            break
        fi
    done
    
    if [[ -n "$FOUND_XELATEX" ]]; then
        print_status "XeLaTeX found at: $FOUND_XELATEX"
        print_info "Adding to PATH in current session..."
        export PATH="$(dirname "$FOUND_XELATEX"):$PATH"
        
        # Add to shell profile
        SHELL_PROFILE=""
        if [[ -n "$ZSH_VERSION" ]]; then
            SHELL_PROFILE="$HOME/.zshrc"
        elif [[ -n "$BASH_VERSION" ]]; then
            SHELL_PROFILE="$HOME/.bash_profile"
        fi
        
        if [[ -n "$SHELL_PROFILE" ]]; then
            if ! grep -q "$(dirname "$FOUND_XELATEX")" "$SHELL_PROFILE" 2>/dev/null; then
                echo "export PATH=\"$(dirname "$FOUND_XELATEX"):\$PATH\"" >> "$SHELL_PROFILE"
                print_status "Added XeLaTeX to $SHELL_PROFILE"
            fi
        fi
    else
        print_warning "XeLaTeX not found. Installing BasicTeX..."
        
        # Install BasicTeX (smaller LaTeX distribution)
        brew install --cask basictex
        
        print_status "BasicTeX installed"
        
        # Update PATH for current session
        export PATH="/usr/local/texlive/2025basic/bin/universal-darwin:/usr/local/texlive/2024basic/bin/universal-darwin:/usr/local/texlive/2023basic/bin/universal-darwin:$PATH"
        
        # Add to shell profile
        SHELL_PROFILE=""
        if [[ -n "$ZSH_VERSION" ]]; then
            SHELL_PROFILE="$HOME/.zshrc"
        elif [[ -n "$BASH_VERSION" ]]; then
            SHELL_PROFILE="$HOME/.bash_profile"
        fi
        
        if [[ -n "$SHELL_PROFILE" ]]; then
            if ! grep -q "texlive" "$SHELL_PROFILE" 2>/dev/null; then
                echo 'export PATH="/usr/local/texlive/*/bin/*:$PATH"' >> "$SHELL_PROFILE"
                print_status "Added LaTeX to $SHELL_PROFILE"
            fi
        fi
    fi
fi

# Verify XeLaTeX is working
if command -v xelatex &> /dev/null; then
    print_status "XeLaTeX is ready: $(which xelatex)"
else
    print_error "XeLaTeX installation may have failed. Please restart your terminal and try again."
    exit 1
fi

# Make resume generator executable
if [[ -f "resume_generator.py" ]]; then
    chmod +x resume_generator.py
    print_status "Made resume_generator.py executable"
fi

# Create a simple wrapper script for easier usage
cat > generate_resume << 'EOF'
#!/bin/bash
# Simple wrapper for resume generation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default paths
DATA_DIR="$SCRIPT_DIR/data"
TEMPLATE_DIR="$SCRIPT_DIR/templates"

# Show usage if no arguments
if [[ $# -eq 0 ]]; then
    echo "Usage: ./generate_resume <output_file> [--onepage] [--focus <tag>]"
    echo ""
    echo "Examples:"
    echo "  ./generate_resume my_resume.pdf"
    echo "  ./generate_resume my_resume.pdf --onepage"
    echo "  ./generate_resume my_resume.pdf --focus elixir"
    echo ""
    exit 1
fi

# Run the Python script
python3 "$SCRIPT_DIR/resume_generator.py" "$DATA_DIR" "$@" "$TEMPLATE_DIR"
EOF

chmod +x generate_resume
print_status "Created easy-to-use generate_resume script"

echo ""
print_status "Setup complete! 🎉"
echo ""
print_info "Quick start:"
echo "  ./generate_resume my_resume.pdf              # Generate full resume"
echo "  ./generate_resume my_resume.pdf --onepage    # Generate one-page resume"
echo ""
print_info "Or use the Python script directly:"
echo "  python3 resume_generator.py data/ output.pdf templates/"
echo ""
print_warning "If you see 'command not found' errors, restart your terminal first."