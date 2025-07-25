#!/bin/bash

# AUTOMATIC DEPLOYMENT SCRIPT FOR PRODUCTION
# ==========================================
# This script should be run after pulling updates from the repository
# It will handle the migration issue automatically

echo "🚀 STARTING DEPLOYMENT WITH MIGRATION FIX"
echo "=========================================="

# Set variables
PROJECT_DIR="/www/wwwroot/PACIFICO"
VENV_PATH="/PACIFICO/02e43b188e8420e8b9cceda13a53170f_venv"
PYTHON_PATH="$VENV_PATH/bin/python3"
MANAGE_PY="$PROJECT_DIR/manage.py"

# Navigate to project directory
cd $PROJECT_DIR

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source $VENV_PATH/bin/activate

# Show current migration status
echo "📊 Current migration status:"
$PYTHON_PATH $MANAGE_PY showmigrations workflow --verbosity=0

# Check if problematic migration exists and is unapplied
MIGRATION_STATUS=$($PYTHON_PATH $MANAGE_PY showmigrations workflow --format=json | grep -c '"workflow", "0031_auto_20250724_2158", false')

if [ "$MIGRATION_STATUS" -gt 0 ]; then
    echo "⚠️  Found unapplied problematic migration 0031_auto_20250724_2158"
    echo "🔧 The migration has been fixed to handle existing 'empresa' column"
fi

# Run migrations normally (the fixed migration will handle the column check)
echo "🔄 Running migrations..."
$PYTHON_PATH $MANAGE_PY migrate

if [ $? -eq 0 ]; then
    echo "✅ All migrations completed successfully!"
    echo "🎉 Deployment completed without issues."
else
    echo "❌ Migration failed. Check the output above for details."
    exit 1
fi

# Collect static files (if needed)
echo "📁 Collecting static files..."
$PYTHON_PATH $MANAGE_PY collectstatic --noinput

# Show final migration status
echo "📋 Final migration status:"
$PYTHON_PATH $MANAGE_PY showmigrations workflow --verbosity=0

echo ""
echo "🏁 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "The migration issue has been automatically resolved."
