#!/bin/bash

echo "🚀 Installing XeLaTeX for resume generation..."

# Check if Homebrew is available
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "📦 Installing BasicTeX (smaller LaTeX distribution)..."
brew install --cask basictex

echo "🔄 Updating PATH for current session..."
export PATH="/usr/local/texlive/2023/bin/universal-darwin:$PATH"

echo "📚 Installing required LaTeX packages..."
sudo tlmgr update --self
sudo tlmgr install collection-fontsrecommended enumitem

echo "✅ XeLaTeX installation complete!"
echo ""
echo "🎯 Now you can generate your resume:"
echo "   python3 quick_resume_gen.py data/ brian_resume.pdf templates/ core"
echo ""
echo "💡 If the command isn't found, restart your terminal or run:"
echo "   export PATH=\"/usr/local/texlive/2023/bin/universal-darwin:\$PATH\""