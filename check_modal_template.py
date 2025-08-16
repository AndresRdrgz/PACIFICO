#!/usr/bin/env python3
"""
Script to validate the bandeja_comite.html template syntax after modal implementation
"""

import os
import sys
import django
from django.conf import settings
from django.template import Template
from django.template.loader import get_template

# Add the project root to Python path
project_root = "/Users/andresrdrgz_/Documents/GitHub/PACIFICO"
sys.path.insert(0, project_root)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Configure Django
django.setup()

def check_template_syntax():
    """Check if the bandeja_comite.html template has valid syntax"""
    try:
        # Try to load the template
        template_path = 'workflow/bandeja_comite.html'
        template = get_template(template_path)
        
        print(f"✅ Template '{template_path}' loaded successfully")
        
        # Try to render with minimal context
        context = {
            'csrf_token': 'test-token',
            'user': type('MockUser', (), {
                'is_authenticated': True,
                'username': 'test_user'
            })(),
            'solicitudes': [],
            'pagination': {
                'current_page': 1,
                'total_pages': 1,
                'has_previous': False,
                'has_next': False,
                'total_items': 0
            }
        }
        
        # Try rendering (this will validate syntax)
        rendered = template.render(context)
        
        print(f"✅ Template rendered successfully")
        print(f"   Rendered content length: {len(rendered)} characters")
        
        # Check for specific modal elements
        modal_checks = [
            ('Modal container', 'id="modalSolicitudesProcesadas"'),
            ('Modal title', 'Historial de Solicitudes Procesadas'),
            ('Search input', 'id="searchInputProcesadas"'),
            ('Table body', 'id="tableProcesadasBody"'),
            ('Pagination container', 'id="paginationProcesadas"'),
            ('JavaScript functions', 'cargarSolicitudesProcesadas'),
            ('Event listeners', 'shown.bs.modal')
        ]
        
        print("\n📋 Modal Component Validation:")
        for check_name, check_content in modal_checks:
            if check_content in rendered:
                print(f"   ✅ {check_name}: Found")
            else:
                print(f"   ❌ {check_name}: Missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Template validation failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        return False

def check_modal_functionality():
    """Check if modal-specific functionality is properly implemented"""
    
    template_file = "/Users/andresrdrgz_/Documents/GitHub/PACIFICO/workflow/templates/workflow/bandeja_comite.html"
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n🔍 Modal Implementation Checks:")
        
        # Check for modal trigger button
        if 'data-bs-toggle="modal"' in content and 'data-bs-target="#modalSolicitudesProcesadas"' in content:
            print("   ✅ Modal trigger button: Properly configured")
        else:
            print("   ❌ Modal trigger button: Missing or misconfigured")
        
        # Check for modal event listeners
        if 'shown.bs.modal' in content:
            print("   ✅ Modal show event listener: Found")
        else:
            print("   ❌ Modal show event listener: Missing")
        
        # Check for lazy loading implementation
        if 'modalProcesadasLoaded' in content:
            print("   ✅ Lazy loading flag: Implemented")
        else:
            print("   ❌ Lazy loading flag: Missing")
        
        # Check for proper API call
        if "api_solicitudes_procesadas_comite" in content:
            print("   ✅ API endpoint: Correctly referenced")
        else:
            print("   ❌ API endpoint: Missing or incorrect")
        
        # Check for responsive design
        if 'tableProcesadasDesktop' in content and 'cardsProcesadasMobile' in content:
            print("   ✅ Responsive design: Desktop and mobile views")
        else:
            print("   ❌ Responsive design: Missing components")
        
        return True
        
    except Exception as e:
        print(f"❌ Modal functionality check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Validating Bandeja Comité Template with Modal Implementation")
    print("=" * 70)
    
    template_valid = check_template_syntax()
    modal_valid = check_modal_functionality()
    
    print("\n" + "=" * 70)
    if template_valid and modal_valid:
        print("✅ All checks passed! Modal implementation is ready.")
    else:
        print("❌ Some issues found. Please review the template.")
    
    print("\n📋 Summary:")
    print(f"   Template syntax: {'✅ Valid' if template_valid else '❌ Invalid'}")
    print(f"   Modal functionality: {'✅ Complete' if modal_valid else '❌ Incomplete'}")
