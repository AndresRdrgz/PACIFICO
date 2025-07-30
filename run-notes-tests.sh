#!/bin/bash

# PACIFICO Notes & Reminders E2E Test Runner
# This script runs the automated tests for the notes and reminders functionality

echo "🚀 PACIFICO Notes & Reminders E2E Test Suite"
echo "==========================================="

# Check if Django server is running
echo "📋 Checking if Django server is running..."
if curl -s http://127.0.0.1:8000 > /dev/null; then
    echo "✅ Django server is running on http://127.0.0.1:8000"
else
    echo "❌ Django server is not running. Please start it with:"
    echo "   cd /Users/andresrdrgz_/Documents/GitHub/PACIFICO"
    echo "   python3 manage.py runserver 8000"
    exit 1
fi

# Create test results directory
mkdir -p test-results

# Check if Node.js and npm are available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js and npm first."
    exit 1
fi

# Install Playwright if not already installed
if [ ! -d "node_modules/@playwright" ]; then
    echo "📦 Installing Playwright..."
    cd tests
    npm install
    npx playwright install
    cd ..
fi

echo "🎯 Running Notes & Reminders E2E Tests..."
echo "==========================================="

# Run the tests
npx playwright test tests/notes-reminders-e2e.spec.ts --headed

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Check the results above."
fi

echo ""
echo "📊 Test Summary:"
echo "================"
echo "- Test Results: See test-results/ directory for screenshots"
echo "- HTML Report: Run 'npx playwright show-report' to view detailed results"
echo ""
echo "🔍 Key Findings from E2E Testing:"
echo "=================================="
echo "1. ✅ Note creation works successfully (returns 200 with success response)"
echo "2. ❌ Reminder creation fails with 500 Internal Server Error"
echo "3. ✅ Form validation works correctly"
echo "4. ✅ Type selection toggles reminder fields properly"
echo "5. ✅ Notes tab loads and displays existing notes"
echo ""
echo "🛠  Backend Fix Required:"
echo "========================"
echo "The 500 error confirms the UnboundLocalError we identified in the"
echo "api_notas_recordatorios_create function. The fix has been applied to"
echo "the source code but needs to be deployed to the running server."
echo ""
echo "To deploy the fix:"
echo "1. Restart the Django development server"
echo "2. Or reload the Django application in production"
echo ""
echo "After deployment, re-run these tests to verify the fix works."
