#!/bin/bash
echo "🛠️ Fixing Large File Push Error..."

# 1. Remove large MMS cache files from the git index
git rm -r --cached data/mms_cache/ 2>/dev/null || echo "Info: MMS cache already removed from index or not found."

# 2. Ensure .gitignore is staged
git add .gitignore

# 3. Amend the previous commit to exclude these files
echo "📝 Amending commit..."
git commit --amend --no-edit

# 4. Attempt to push again
echo "🚀 Attempting push to main..."
git push origin main

echo "✅ Fix attempted. Check output above for success."
