#!/usr/bin/env python3
"""
Script to generate Django migration for adding apc_archivo field.
Run this in your Django project root directory.
"""

import os
import django
from django.core.management import call_command

if __name__ == "__main__":
    # Setup Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "financiera.settings")
    django.setup()
    
    print("Generating migration for apc_archivo field...")
    
    try:
        # Generate migration for the workflow app
        call_command('makemigrations', 'workflow', name='add_apc_archivo_field')
        print("✅ Migration generated successfully!")
        print("Next steps:")
        print("1. Review the generated migration file")
        print("2. Run: python manage.py migrate")
        
    except Exception as e:
        print(f"❌ Error generating migration: {e}")
        print("\nManual migration option:")
        print("Run: python manage.py makemigrations workflow --name add_apc_archivo_field")
