#!/bin/bash

# StoryGenome Deployment Script
# This script prepares your repository for Streamlit Cloud deployment

echo "🚀 Preparing StoryGenome for Streamlit Cloud deployment..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository. Please initialize git first:"
    echo "   git init"
    echo "   git remote add origin <your-github-repo-url>"
    exit 1
fi

# Check if all required files exist
echo "📋 Checking required files..."

required_files=(
    "streamlit_app.py"
    "requirements.txt"
    "packages.txt"
    ".streamlit/config.toml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Add all files to git
echo "📝 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "Prepare for Streamlit Cloud deployment"
fi

# Check if remote is set
if git remote get-url origin > /dev/null 2>&1; then
    echo "🌐 Pushing to GitHub..."
    git push origin main
    echo ""
    echo "✅ Deployment preparation complete!"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://share.streamlit.io/"
    echo "2. Sign in with your GitHub account"
    echo "3. Click 'New app'"
    echo "4. Select your repository"
    echo "5. Set main file path to: streamlit_app.py"
    echo "6. Add your API keys as secrets"
    echo "7. Click 'Deploy!'"
    echo ""
    echo "Your app will be available at: https://your-app-name-your-username.streamlit.app"
else
    echo "❌ No remote repository set. Please add your GitHub repository:"
    echo "   git remote add origin <your-github-repo-url>"
    echo "   git push -u origin main"
fi
