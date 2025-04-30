#!/bin/bash
# Example script for gathering additional context for AI Command Helper
# Copy this file to .aih_context.sh and customize as needed

# Current directory listing
echo "# Directory listing"
ls -la

# Git information (if in a git repository)
if git rev-parse --is-inside-work-tree &>/dev/null; then
  echo -e "\n# Git branch"
  git branch --show-current
  
  echo -e "\n# Git status"
  git status -s
  
  echo -e "\n# Recent commits"
  git log --oneline -n 5
fi

# System information
echo -e "\n# System information"
uname -a

# Disk space
echo -e "\n# Disk space"
df -h .

# Memory usage
echo -e "\n# Memory usage"
free -h

# Running processes (top 5 by CPU)
echo -e "\n# Top processes"
ps aux --sort=-%cpu | head -n 6

# Add your custom commands below
# For example:
# echo -e "\n# Docker containers"
# docker ps

# echo -e "\n# Kubernetes pods"
# kubectl get pods