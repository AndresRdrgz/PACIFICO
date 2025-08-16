#!/usr/bin/env python3
"""
Simple validation script for the bandeja_comite.html template modal implementation
"""

import re

def check_modal_implementation():
    """Check if modal implementation is complete in the template"""
    
    template_file = "/Users/andresrdrgz_/Documents/GitHub/PACIFICO/workflow/templates/workflow/bandeja_comite.html"
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🚀 Validating Modal Implementation in Bandeja Comité")
        print("=" * 60)
        
        # Check for modal structure
        checks = [
            # Modal HTML structure
            ('Modal container', r'id="modalSolicitudesProcesadas"'),
            ('Modal dialog', r'class="modal-dialog modal-xl"'),
            ('Modal title', r'Historial de Solicitudes Procesadas'),
            
            # Modal trigger
            ('Trigger button', r'data-bs-toggle="modal".*data-bs-target="#modalSolicitudesProcesadas"'),
            # Header button
            ('Header button', r'<i class="fas fa-history"></i>.*Historial'),
            
            # Search and controls
            ('Search input', r'id="searchInputProcesadas"'),
            ('Refresh button', r'id="btnRefrescarProcesadas"'),
            
            # Table structure
            ('Desktop table', r'id="tableProcesadasDesktop"'),
            ('Table body', r'id="tableProcesadasBody"'),
            ('Mobile cards', r'id="cardsProcesadasMobile"'),
            
            # States
            ('Loading state', r'id="loadingStateProcesadas"'),
            ('Empty state', r'id="emptyStateProcesadas"'),
            
            # Pagination
            ('Pagination container', r'id="paginationContainerProcesadas"'),
            ('Pagination', r'id="paginationProcesadas"'),
            
            # JavaScript functions
            ('Load function', r'function cargarSolicitudesProcesadas'),
            ('Render function', r'function renderizarSolicitudesProcesadas'),
            ('Pagination function', r'function renderizarPaginacionProcesadas'),
            
            # Event listeners
            ('Modal show event', r'shown\.bs\.modal'),
            ('Modal hide event', r'hidden\.bs\.modal'),
            ('Search event', r'searchInputProcesadas.*addEventListener'),
            
            # API integration
            ('API URL', r"api_solicitudes_procesadas_comite"),
            ('PDF URL', r"download_pdf_resultado_consulta"),
            
            # Lazy loading
            ('Lazy loading flag', r'modalProcesadasLoaded'),
            ('Lazy loading logic', r'if \(!modalProcesadasLoaded\)'),
        ]
        
        passed = 0
        total = len(checks)
        
        print("\n📋 Component Validation:")
        for check_name, pattern in checks:
            if re.search(pattern, content, re.DOTALL):
                print(f"   ✅ {check_name}")
                passed += 1
            else:
                print(f"   ❌ {check_name}")
        
        # Check for old section-based code (should be removed)
        print("\n🧹 Cleanup Validation:")
        old_patterns = [
            ('Old section ID', r'id="solicitudesProcesadasSection"'),
            ('Old page load call', r'^\s*cargarSolicitudesProcesadas\(\);.*//.*page.*load'),
        ]
        
        cleanup_passed = 0
        for check_name, pattern in old_patterns:
            if not re.search(pattern, content, re.MULTILINE):
                print(f"   ✅ {check_name}: Properly removed")
                cleanup_passed += 1
            else:
                print(f"   ❌ {check_name}: Still present")
        
        # Template structure validation
        print("\n🏗️  Template Structure:")
        structure_checks = [
            ('Extends block', r'{% extends'),
            ('Content block', r'{% block content %}'),
            ('JavaScript block', r'{% block (extra_js|javascript) %}'),
            ('CSRF token', r'{{ csrf_token }}'),
            ('URL tags', r'{% url'),
        ]
        
        structure_passed = 0
        for check_name, pattern in structure_checks:
            if re.search(pattern, content):
                print(f"   ✅ {check_name}")
                structure_passed += 1
            else:
                print(f"   ❌ {check_name}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Validation Summary:")
        print(f"   Modal components: {passed}/{total} ({'✅' if passed == total else '❌'})")
        print(f"   Cleanup: {cleanup_passed}/{len(old_patterns)} ({'✅' if cleanup_passed == len(old_patterns) else '❌'})")
        print(f"   Template structure: {structure_passed}/{len(structure_checks)} ({'✅' if structure_passed == len(structure_checks) else '❌'})")
        
        overall_success = (passed == total and cleanup_passed == len(old_patterns) and structure_passed == len(structure_checks))
        
        if overall_success:
            print("\n🎉 SUCCESS: Modal implementation is complete and ready!")
        else:
            print("\n⚠️  WARNING: Some issues found. Please review the template.")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Error reading template file: {e}")
        return False

def check_file_size():
    """Check template file size to ensure it's reasonable"""
    template_file = "/Users/andresrdrgz_/Documents/GitHub/PACIFICO/workflow/templates/workflow/bandeja_comite.html"
    
    try:
        import os
        size = os.path.getsize(template_file)
        print(f"\n📏 File Size: {size:,} bytes ({size/1024:.1f} KB)")
        
        if size > 500 * 1024:  # 500KB
            print("   ⚠️  Large file size - consider splitting")
        else:
            print("   ✅ Reasonable file size")
            
    except Exception as e:
        print(f"   ❌ Error checking file size: {e}")

if __name__ == "__main__":
    success = check_modal_implementation()
    check_file_size()
    
    print(f"\n🏁 Final Result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
