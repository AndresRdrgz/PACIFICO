#!/bin/bash
# production_setup.sh - Setup script for production server

echo "🚀 Setting up PACIFICO production environment..."

# Update system
sudo apt-get update

# Install WeasyPrint system dependencies (optional - for better PDF quality)
echo "📄 Installing PDF generation dependencies..."
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

echo "✅ System dependencies installed"
echo "🔄 Python packages will be installed via requirements.txt"
echo "📄 PDF generation will now use WeasyPrint for best quality"

# Optional: Test PDF generation
echo "🧪 Testing PDF generation..."
cd /path/to/your/app
python manage.py shell -c "
from workflow.views_workflow import generar_pdf_resultado_consulta
print('PDF generation system ready!')
"

echo "🎉 Production setup complete!"
