#!/bin/bash
# Script to fix large files in git and push

cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola

echo "=== Current commit history ===" > git_fix_output.txt
git log --oneline -10 >> git_fix_output.txt 2>&1

echo "" >> git_fix_output.txt
echo "=== Removing large files from git ===" >> git_fix_output.txt

# Remove the problematic files from git tracking
git rm --cached "ml_training/external_videos/tier1_ted/The danger of a single story.mp4" >> git_fix_output.txt 2>&1
git rm --cached "ml_training/external_videos/tier1_ted/We should all be feminists.fhls-3768.mp4.part" >> git_fix_output.txt 2>&1

# Remove any other large mp4 files from tracking
git rm --cached -r "ml_training/external_videos/" >> git_fix_output.txt 2>&1

echo "" >> git_fix_output.txt
echo "=== Git status ===" >> git_fix_output.txt
git status >> git_fix_output.txt 2>&1

echo "" >> git_fix_output.txt
echo "=== Committing changes ===" >> git_fix_output.txt
git add .gitignore >> git_fix_output.txt 2>&1
git add .gitattributes >> git_fix_output.txt 2>&1
git commit -m "Remove large video files, add to gitignore" >> git_fix_output.txt 2>&1

echo "" >> git_fix_output.txt
echo "=== Done ===" >> git_fix_output.txt
