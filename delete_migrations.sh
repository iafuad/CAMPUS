#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Remove migration files but keep __init__.py
echo "Removing Django migration files..."
find apps -path "*/migrations/*.py" ! -name "__init__.py" -delete
find apps -path "*/migrations/*.pyc" -delete
find apps -path "*/migrations/__pycache__" -prune -exec rm -rf {} +

echo "Reset complete. Run 'python manage.py makemigrations && python manage.py migrate'."
