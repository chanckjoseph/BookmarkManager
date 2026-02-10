#!/bin/bash
# Move to the project root (where the script is located)
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the app from project root
echo "🚀 Launching Bookmark Manager..."
python3 prototype/api.py
