#!/bin/bash

# Test script for recordatorio creation API
echo "🧪 Testing Recordatorio Creation API"

# Get CSRF token first
echo "Getting CSRF token..."
CSRF_TOKEN=$(curl -s -c cookies.txt http://127.0.0.1:8000/workflow/negocios/ | grep -o 'csrfmiddlewaretoken.*value="[^"]*"' | sed 's/.*value="//;s/".*//')

if [ -z "$CSRF_TOKEN" ]; then
    echo "❌ Failed to get CSRF token"
    exit 1
fi

echo "✅ Got CSRF token: ${CSRF_TOKEN:0:10}..."

# Test data for recordatorio
FUTURE_DATE=$(date -v+1d '+%Y-%m-%dT%H:%M')
echo "Using future date: $FUTURE_DATE"

# Test creating a recordatorio
echo "Creating recordatorio..."

curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b cookies.txt \
  -d "{
    \"tipo\": \"recordatorio\",
    \"titulo\": \"Test Recordatorio via CURL\",
    \"contenido\": \"This is a test recordatorio created via CURL\",
    \"prioridad\": \"Alta\",
    \"fecha_vencimiento\": \"$FUTURE_DATE\",
    \"estado\": \"pendiente\"
  }" \
  http://127.0.0.1:8000/workflow/api/notas-recordatorios/120/crear/ \
  -v

echo ""
echo "✅ Test completed"

# Clean up
rm -f cookies.txt
