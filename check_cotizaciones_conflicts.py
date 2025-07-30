#!/usr/bin/env python3
"""
Simple script to check URL patterns and verify cotizaciones API endpoints
This helps identify if there are multiple conflicting endpoints
"""

import re
import os

def search_cotizaciones_urls():
    print("=" * 60)
    print("SEARCHING FOR COTIZACIONES URL PATTERNS")
    print("=" * 60)
    
    # Files to search
    url_files = [
        'workflow/urls.py',
        'workflow/urls_workflow.py', 
        'pacifico/urls.py',
        'urls.py'
    ]
    
    cotizaciones_patterns = []
    
    for url_file in url_files:
        if os.path.exists(url_file):
            print(f"\n🔍 Searching in {url_file}:")
            print("-" * 40)
            
            try:
                with open(url_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Search for cotizaciones-related URL patterns
                patterns = [
                    r"path\(['\"][^'\"]*cotizaciones[^'\"]*['\"].*?\)",
                    r"url\(['\"][^'\"]*cotizaciones[^'\"]*['\"].*?\)"
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        print(f"  ✅ {match}")
                        cotizaciones_patterns.append((url_file, match))
                        
                # Also search for view function references
                view_patterns = [
                    r"['\"][^'\"]*cotizaciones[^'\"]*['\"],\s*views[^,]*",
                    r"views[^,]*cotizaciones[^,]*"
                ]
                
                for pattern in view_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        print(f"  📋 {match}")
                        
            except Exception as e:
                print(f"  ❌ Error reading {url_file}: {e}")
        else:
            print(f"  ⚠️ {url_file} not found")
    
    print(f"\n📊 Total cotizaciones URL patterns found: {len(cotizaciones_patterns)}")
    
    if len(cotizaciones_patterns) > 1:
        print("\n⚠️ MULTIPLE COTIZACIONES ENDPOINTS DETECTED!")
        print("This could be causing the filtering issue.")
        print("\nEndpoints found:")
        for file, pattern in cotizaciones_patterns:
            print(f"  📁 {file}: {pattern}")
    
    return cotizaciones_patterns

def search_cotizaciones_views():
    print("\n" + "=" * 60)
    print("SEARCHING FOR COTIZACIONES VIEW FUNCTIONS")
    print("=" * 60)
    
    # Files to search
    view_files = [
        'workflow/views.py',
        'workflow/views_workflow.py',
        'workflow/views_reconsideraciones.py',
        'workflow/api.py',
        'pacifico/views.py'
    ]
    
    functions_found = []
    
    for view_file in view_files:
        if os.path.exists(view_file):
            print(f"\n🔍 Searching in {view_file}:")
            print("-" * 40)
            
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Search for cotizaciones-related functions
                pattern = r"def\s+[^(]*cotizaciones[^(]*\([^)]*\):"
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    print(f"  ✅ {match}")
                    functions_found.append((view_file, match))
                    
            except Exception as e:
                print(f"  ❌ Error reading {view_file}: {e}")
        else:
            print(f"  ⚠️ {view_file} not found")
    
    print(f"\n📊 Total cotizaciones functions found: {len(functions_found)}")
    
    return functions_found

def main():
    """Main function to run all checks"""
    print("🔍 COTIZACIONES API CONFLICT DETECTION")
    print("This script helps identify potential conflicts in cotizaciones APIs")
    print()
    
    # Change to the correct directory
    if os.path.basename(os.getcwd()) != 'PACIFICO':
        if os.path.exists('PACIFICO'):
            os.chdir('PACIFICO')
        else:
            print("⚠️ Please run this script from the PACIFICO directory")
            return
    
    url_patterns = search_cotizaciones_urls()
    view_functions = search_cotizaciones_views()
    
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    
    if len(url_patterns) == 0:
        print("❌ No cotizaciones URL patterns found")
    elif len(url_patterns) == 1:
        print("✅ Single cotizaciones URL pattern found (good)")
    else:
        print(f"⚠️ Multiple cotizaciones URL patterns found ({len(url_patterns)})")
        print("   This could cause the wrong API to be called")
    
    if len(view_functions) == 0:
        print("❌ No cotizaciones view functions found")
    elif len(view_functions) == 1:
        print("✅ Single cotizaciones view function found (good)")
    else:
        print(f"⚠️ Multiple cotizaciones view functions found ({len(view_functions)})")
        print("   Make sure the correct one is being used")
    
    print("\n🔍 RECOMMENDATION:")
    print("1. Check server logs when clicking 'Ver todas las cotizaciones del cliente'")
    print("2. Look for the DEBUG messages added to views_reconsideraciones.py")
    print("3. Verify which API endpoint is actually being called")
    print("4. Check browser Network tab to see the actual request URL")

if __name__ == "__main__":
    main()
