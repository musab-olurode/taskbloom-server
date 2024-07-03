#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# python manage.py createsuperuser --no-input

python manage.py createsuperuser --email admin@mail.com --name Admin --title Admin --noinput