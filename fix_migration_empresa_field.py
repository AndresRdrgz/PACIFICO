#!/usr/bin/env python3
"""
Script to fix the migration issue with the empresa field in workflow_clienteentrevista table.

The problem: Migration 0031_auto_20250724_2158 is trying to add an 'empresa' field
that already exists in the database, causing a DuplicateColumn error.

Solutions:
1. Mark the migration as applied (fake apply)
2. Or create a custom migration that checks if the column exists before adding it
"""

import os
import sys
import django

# Add the project directory to Python path (adjust for local vs production)
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')

django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table using SQLite-compatible syntax."""
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(%s)" % table_name)
        columns = cursor.fetchall()
        return any(column[1] == column_name for column in columns)

def main():
    print("🔍 Checking if 'empresa' column exists in workflow_clienteentrevista table...")
    
    # Check if the empresa column already exists
    empresa_exists = check_column_exists('workflow_clienteentrevista', 'empresa')
    
    if empresa_exists:
        print("✅ Column 'empresa' already exists in the database.")
        print("🔧 The migration 0031_auto_20250724_2158 is trying to add a field that already exists.")
        print("\n📋 Solutions:")
        print("1. Mark the migration as applied (fake apply)")
        print("2. Skip the problematic operation")
        
        # Option 1: Fake apply the migration
        print("\n🚀 Applying solution 1: Fake apply the migration...")
        print("Command to run on production server:")
        print("python manage.py migrate workflow 0031_auto_20250724_2158 --fake")
        
        # You could also programmatically fake apply it:
        # execute_from_command_line(['manage.py', 'migrate', 'workflow', '0031_auto_20250724_2158', '--fake'])
        
    else:
        print("❌ Column 'empresa' does not exist. The migration should proceed normally.")
        print("This script is not needed in this case.")

if __name__ == "__main__":
    main()
