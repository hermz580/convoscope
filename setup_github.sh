#!/bin/bash
# ConvoScope - Automated GitHub Setup Script
# This script will guide you through pushing to GitHub

set -e

echo "🔍 ConvoScope - GitHub Setup Wizard"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "src" ]; then
    echo "❌ Error: Please run this script from the convoscope directory"
    echo "   cd /path/to/convoscope"
    echo "   ./setup_github.sh"
    exit 1
fi

echo "✓ Repository structure verified"
echo ""

# Check git status
if [ ! -d ".git" ]; then
    echo "❌ Error: Git repository not initialized"
    echo "   This shouldn't happen - please check the repository"
    exit 1
fi

echo "✓ Git repository found"
echo ""

# Get GitHub username
echo "📝 GitHub Setup"
echo "---------------"
echo ""
read -p "Enter your GitHub username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "❌ Username required"
    exit 1
fi

echo ""
echo "🌐 Next Steps:"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: convoscope"
echo "3. Description: Privacy-first conversation analytics for Claude AI"
echo "4. Select 'Public' (or 'Private' if you prefer)"
echo "5. ⚠️  IMPORTANT: Leave all checkboxes UNCHECKED"
echo "   - [ ] Add a README file"
echo "   - [ ] Add .gitignore"
echo "   - [ ] Choose a license"
echo "6. Click 'Create repository'"
echo ""
read -p "Press ENTER when you've created the repository..."

# Add remote
echo ""
echo "🔗 Configuring remote..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$GITHUB_USER/convoscope.git"
echo "✓ Remote configured: https://github.com/$GITHUB_USER/convoscope.git"

# Check branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 Renaming branch to 'main'..."
    git branch -M main
fi

echo ""
echo "🚀 Ready to push!"
echo ""
echo "Attempting to push to GitHub..."
echo "You may be prompted for your GitHub credentials."
echo ""
echo "If you have 2FA enabled, you'll need a Personal Access Token instead of password:"
echo "  1. Go to: https://github.com/settings/tokens"
echo "  2. Generate new token (classic)"
echo "  3. Select 'repo' scope"
echo "  4. Use the token as your password when prompted"
echo ""
read -p "Press ENTER to push..."

# Push to GitHub
if git push -u origin main; then
    echo ""
    echo "✅ SUCCESS! Repository pushed to GitHub!"
    echo ""
    echo "🎉 Your repository is live at:"
    echo "   https://github.com/$GITHUB_USER/convoscope"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Visit your repo and add topics/tags"
    echo "   2. Create a release (v2.0.0)"
    echo "   3. Share with the community!"
    echo ""
    echo "📚 See GITHUB_SETUP.md for detailed next steps"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo ""
    echo "1. Authentication Error:"
    echo "   - Make sure username/password are correct"
    echo "   - If 2FA enabled, use Personal Access Token as password"
    echo "   - Token URL: https://github.com/settings/tokens"
    echo ""
    echo "2. Repository Already Exists:"
    echo "   - Delete the existing repo on GitHub"
    echo "   - Or use a different name"
    echo ""
    echo "3. Permission Denied:"
    echo "   - Check that you own the repository"
    echo "   - Verify token has 'repo' scope"
    echo ""
    echo "To retry manually:"
    echo "   git push -u origin main"
    echo ""
    exit 1
fi

# Offer to open browser
echo ""
read -p "Open repository in browser? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "https://github.com/$GITHUB_USER/convoscope"
    elif command -v open &> /dev/null; then
        open "https://github.com/$GITHUB_USER/convoscope"
    else
        echo "Visit: https://github.com/$GITHUB_USER/convoscope"
    fi
fi

echo ""
echo "🎊 Setup complete!"
