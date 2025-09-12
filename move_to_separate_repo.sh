#!/bin/bash
# Script to move AI Context Manager to separate repository

echo "Moving AI Context Manager to separate repository..."

# 1. Create new directory outside current project
cd ..
mkdir ai-context-manager
cd ai-context-manager

# 2. Initialize new git repository
git init
git remote add origin https://github.com/yourusername/ai-context-manager.git

# 3. Copy the package structure
cp -r ../blackblaze2-backup/ai-context-manager/* .

# 4. Copy the current AI context scripts to implement core functionality
mkdir -p ai_context_manager
cp ../blackblaze2-backup/scripts/ai_context_*.py ai_context_manager/
cp ../blackblaze2-backup/scripts/maintain_ai_context.sh ai_context_manager/

# 5. Create initial commit
git add .
git commit -m "Initial commit: AI Context Manager standalone package"

echo "AI Context Manager moved to separate repository:"
echo "Location: $(pwd)"
echo "Next steps:"
echo "1. Push to GitHub: git push -u origin main"
echo "2. Implement CLI interface in ai_context_manager/cli.py"
echo "3. Add tests in tests/"
echo "4. Publish to PyPI: python -m build && twine upload dist/*"
