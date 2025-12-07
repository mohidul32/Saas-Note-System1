#!/bin/bash

# Backend Setup Script for SaaS Notes System

echo "=== Setting up SaaS Notes Backend ==="

# Create directory structure
echo "Creating directory structure..."
mkdir -p apps/users
mkdir -p apps/companies
mkdir -p apps/workspaces
mkdir -p apps/notes/management/commands
mkdir -p apps/common
mkdir -p scripts

# Create __init__.py files
echo "Creating __init__.py files..."
touch apps/__init__.py
touch apps/users/__init__.py
touch apps/companies/__init__.py
touch apps/workspaces/__init__.py
touch apps/notes/__init__.py
touch apps/common/__init__.py
touch apps/notes/management/__init__.py
touch apps/notes/management/commands/__init__.py

# Create config/__init__.py for Celery
cat > config/__init__.py << 'EOF'
from .celery import app as celery_app

__all__ = ('celery_app',)
EOF

echo "Directory structure created!"
echo ""
echo "Next steps:"
echo "1. Copy all model files to respective apps"
echo "2. Copy serializers, views, permissions to respective apps"
echo "3. Copy settings.py, urls.py, celery.py to config/"
echo "4. Create .env file with database credentials"
echo "5. Run: python manage.py makemigrations"
echo "6. Run: python manage.py migrate"
echo "7. Run: python scripts/seed_data.py"
echo ""
echo "Setup complete!"