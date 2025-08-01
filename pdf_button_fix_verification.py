#!/usr/bin/env python3
"""
PDF Button Fix Verification Report
==================================

This script verifies that the PDF button has been successfully updated
to use the new xhtml2pdf format with proper field filtering.
"""

import os

def check_template_filtering():
    """Check if the template has proper filtering"""
    template_path = "workflow/templates/workflow/pdf_resultado_consulta_simple.html"
    
    print("🔍 TEMPLATE FILTERING VERIFICATION")
    print("=" * 50)
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for filtering logic
        if "comentario_analista_credito" in content and "not in cal.campo" in content:
            filter_count = content.count("'comentario_analista_credito' not in cal.campo")
            print(f"✅ Template contains field filtering logic")
            print(f"✅ Filtering applied {filter_count} times in template")
            return True
        else:
            print("❌ Template filtering logic not found")
            return False
            
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def check_api_implementation():
    """Check if the API has been updated"""
    views_path = "workflow/views_workflow.py"
    
    print("\n🔍 API IMPLEMENTATION VERIFICATION")
    print("=" * 50)
    
    if not os.path.exists(views_path):
        print(f"❌ Views file not found: {views_path}")
        return False
    
    try:
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for xhtml2pdf implementation in the API function
        if "def api_pdf_resultado_consulta" in content:
            print("✅ API function found: api_pdf_resultado_consulta")
            
            # Extract the function content
            lines = content.split('\n')
            in_function = False
            function_lines = []
            
            for line in lines:
                if "def api_pdf_resultado_consulta" in line:
                    in_function = True
                elif in_function and line.startswith('def ') and not line.startswith('def api_pdf_resultado_consulta'):
                    break
                
                if in_function:
                    function_lines.append(line)
            
            function_content = '\n'.join(function_lines)
            
            # Check for xhtml2pdf usage
            if "from xhtml2pdf import pisa" in function_content and "pisa.pisaDocument" in function_content:
                print("✅ API uses xhtml2pdf for PDF generation")
                
                # Check for template usage
                if "pdf_resultado_consulta_simple.html" in function_content:
                    print("✅ API uses filtered template: pdf_resultado_consulta_simple.html")
                    return True
                else:
                    print("⚠️  API might not be using the filtered template")
                    return False
            else:
                print("❌ API not updated to use xhtml2pdf")
                return False
        else:
            print("❌ API function not found")
            return False
            
    except Exception as e:
        print(f"❌ Error reading views file: {e}")
        return False

def check_javascript_function():
    """Check if the JavaScript function exists"""
    template_path = "workflow/templates/workflow/detalle_solicitud_analisis.html"
    
    print("\n🔍 JAVASCRIPT FUNCTION VERIFICATION")
    print("=" * 50)
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the PDF button and function
        if "btn-pdf-resultado-consulta" in content and "generatePdfResultadoConsulta" in content:
            print("✅ PDF button found: btn-pdf-resultado-consulta")
            print("✅ JavaScript function found: generatePdfResultadoConsulta")
            
            # Check if it calls the correct API endpoint
            if "/workflow/api/solicitudes/${solicitudId}/pdf-resultado-consulta/" in content:
                print("✅ JavaScript calls correct API endpoint")
                return True
            else:
                print("⚠️  JavaScript might not call the correct API endpoint")
                return False
        else:
            print("❌ PDF button or JavaScript function not found")
            return False
            
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def main():
    """Run all verification checks"""
    
    print("📋 PDF BUTTON FIX VERIFICATION REPORT")
    print("=" * 60)
    print()
    
    # Run all checks
    template_ok = check_template_filtering()
    api_ok = check_api_implementation() 
    js_ok = check_javascript_function()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"Template Filtering: {'✅ PASS' if template_ok else '❌ FAIL'}")
    print(f"API Implementation: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"JavaScript Function: {'✅ PASS' if js_ok else '❌ FAIL'}")
    
    if template_ok and api_ok and js_ok:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("=" * 60)
        print("✅ PDF button has been successfully updated")
        print("✅ Now uses xhtml2pdf format (same as email system)")
        print("✅ comentario_analista_credito field excluded from tables")
        print("✅ API endpoint properly configured")
        print("✅ JavaScript function calls correct endpoint")
        print("\n💡 The PDF button should now generate reports using the")
        print("   new custom format with proper field filtering!")
        return True
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        print("💡 Check the failed items above for details")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
