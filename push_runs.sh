#!/bin/bash

# Exit on error
set -e

echo "=== Staging files under runs/ and updating .gitignore ==="
git add .gitignore runs/

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "No new runs or changes to commit."
    exit 0
fi

# Get current timestamp for the commit message
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
COMMIT_MESSAGE="feat: add new runs at $TIMESTAMP"

echo "=== Committing changes ==="
git commit -m "$COMMIT_MESSAGE"

echo "=== Pulling latest remote changes to avoid conflicts ==="
git pull --rebase origin main

echo "=== Pushing to remote repository ==="
git push origin main

echo "=== Success! New runs pushed successfully ==="
