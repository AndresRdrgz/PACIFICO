#!/bin/bash

# PRODUCTION SERVER MIGRATION FIX SCRIPT
# =====================================
# This script fixes the Django migration issue where column 'empresa' already exists

echo "🔧 FIXING DJANGO MIGRATION ISSUE ON PRODUCTION SERVER"
echo "====================================================="
echo ""

# Navigate to project directory
echo "📁 Navigating to project directory..."
cd /www/wwwroot/PACIFICO

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source /PACIFICO/02e43b188e8420e8b9cceda13a53170f_venv/bin/activate

# Check current migration status
echo "📊 Checking current migration status..."
./02e43b188e8420e8b9cceda13a53170f_venv/bin/python3 manage.py showmigrations workflow

echo ""
echo "🎯 APPLYING FIX: Fake apply the problematic migration..."

# Fake apply the problematic migration
./02e43b188e8420e8b9cceda13a53170f_venv/bin/python3 manage.py migrate workflow 0031_auto_20250724_2158 --fake

if [ $? -eq 0 ]; then
    echo "✅ Successfully fake-applied migration 0031_auto_20250724_2158"
    echo ""
    echo "🚀 Continuing with remaining migrations..."
    
    # Apply remaining migrations
    ./02e43b188e8420e8b9cceda13a53170f_venv/bin/python3 manage.py migrate
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 ALL MIGRATIONS COMPLETED SUCCESSFULLY!"
        echo "✅ The migration issue has been resolved."
    else
        echo ""
        echo "❌ Some migrations failed. Please check the output above."
        echo "💡 You may need to fix additional migration issues."
    fi
else
    echo "❌ Failed to fake-apply migration. Trying alternative approach..."
    echo ""
    echo "🔄 Checking if column exists in database..."
    
    # Check if column exists
    COLUMN_EXISTS=$(psql -h localhost -U postgres -d pacifico -t -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'workflow_clienteentrevista' AND column_name = 'empresa';" | grep -c empresa)
    
    if [ "$COLUMN_EXISTS" -gt 0 ]; then
        echo "✅ Column 'empresa' exists in database"
        echo "🔧 Forcing fake application of migration..."
        ./02e43b188e8420e8b9cceda13a53170f_venv/bin/python3 manage.py migrate workflow 0031_auto_20250724_2158 --fake --verbosity=2
        
        # Try migrations again
        ./02e43b188e8420e8b9cceda13a53170f_venv/bin/python3 manage.py migrate
    else
        echo "❌ Column 'empresa' does not exist. This requires manual investigation."
        echo "💡 Please contact the development team for assistance."
    fi
fi

echo ""
echo "📋 Final migration status:"
./02e43b188e8420e8b9cceda13a53170f_venv/bin/python3 manage.py showmigrations workflow

echo ""
echo "📞 If you still have issues, contact the development team with the output above."
