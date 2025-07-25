#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')

# Setup Django
django.setup()

from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError

try:
    # Try to load the template
    template = get_template('workflow/negocios.html')
    print("✅ Template 'workflow/negocios.html' loaded successfully!")
    print("✅ No syntax errors found in the template.")
    
    # Try to render the template with empty context to check for basic syntax
    context = {}
    try:
        rendered = template.render(context)
        print("✅ Template rendered successfully with empty context.")
    except Exception as e:
        print(f"⚠️  Template loaded but failed to render with empty context: {e}")
        print("This is expected if the template requires specific context variables.")
    
except TemplateDoesNotExist:
    print("❌ Template 'workflow/negocios.html' does not exist!")
    
except TemplateSyntaxError as e:
    print(f"❌ Template syntax error: {e}")
    print(f"❌ Error on line {e.template_debug['line_number']}: {e.template_debug['during']}")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\nTemplate validation complete.")
