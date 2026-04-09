#!/bin/bash
# scripts/setup/CLEAN_CACHE.sh
# Safely removes local runtime data and logs to keep the repository fresh.

echo "🧹 Starting repository cleanup..."

# Remove temporary data files (but keep the data directory structure)
find data/ -name "*.csv" -delete
find data/ -name "*.json" -not -name "role_profiles.yaml" -delete
find data/ -name "*.jsonl" -delete
find logs/ -name "*.log" -delete

# Remove pycache
find . -name "__pycache__" -type d -exec rm -rf {} +

echo "✅ Cache cleared. Your repository is organized and ready for a fresh run!"
