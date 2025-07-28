#!/usr/bin/env python3
"""
Final verification of the template file
"""

import re

def final_check(content):
    """Final comprehensive check of the template."""
    print("🔍 FINAL COMPREHENSIVE TEMPLATE VERIFICATION")
    print("=" * 60)
    
    # 1. Django Template Tags
    print("1. Django Template Tags Balance:")
    
    tag_patterns = {
        'if': (r'{%\s*if\s+.*?%}', r'{%\s*endif\s*%}'),
        'for': (r'{%\s*for\s+.*?%}', r'{%\s*endfor\s*%}'),
        'block': (r'{%\s*block\s+.*?%}', r'{%\s*endblock\s*%}'),
        'with': (r'{%\s*with\s+.*?%}', r'{%\s*endwith\s*%}'),
    }
    
    django_balanced = True
    for tag_name, (open_pattern, close_pattern) in tag_patterns.items():
        opens = len(re.findall(open_pattern, content))
        closes = len(re.findall(close_pattern, content))
        status = "✅" if opens == closes else "❌"
        print(f"   {status} {tag_name}: {opens} opens, {closes} closes")
        if opens != closes:
            django_balanced = False
    
    # 2. HTML Tags (refined check)
    print("\n2. HTML Tags Balance (Major Tags):")
    
    html_patterns = {
        'div': (r'<div\b[^>]*(?<!/)>', r'</div>'),
        'script': (r'<script\b[^>]*>', r'</script>'),
        'style': (r'<style\b[^>]*>', r'</style>'),
        'table': (r'<table\b[^>]*>', r'</table>'),
        'form': (r'<form\b[^>]*>', r'</form>'),
    }
    
    html_balanced = True
    for tag_name, (open_pattern, close_pattern) in html_patterns.items():
        opens = len(re.findall(open_pattern, content, re.IGNORECASE))
        closes = len(re.findall(close_pattern, content, re.IGNORECASE))
        status = "✅" if opens == closes else "❌"
        print(f"   {status} {tag_name}: {opens} opens, {closes} closes")
        if opens != closes:
            html_balanced = False
    
    # 3. JavaScript Syntax
    print("\n3. JavaScript Syntax:")
    
    js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    js_balanced = True
    
    for i, js_block in enumerate(js_blocks):
        open_braces = js_block.count('{')
        close_braces = js_block.count('}')
        open_parens = js_block.count('(')
        close_parens = js_block.count(')')
        
        brace_status = "✅" if open_braces == close_braces else "❌"
        paren_status = "✅" if open_parens == close_parens else "❌"
        
        print(f"   Block {i+1}: {brace_status} Braces ({open_braces}/{close_braces}), {paren_status} Parens ({open_parens}/{close_parens})")
        
        if open_braces != close_braces or open_parens != close_parens:
            js_balanced = False
    
    # 4. Overall Status
    print("\n" + "=" * 60)
    print("OVERALL STATUS:")
    
    if django_balanced and html_balanced and js_balanced:
        print("🎉 ALL CHECKS PASSED! The template is properly structured.")
        return True
    else:
        print("❌ Some issues remain:")
        if not django_balanced:
            print("   - Django template tags are unbalanced")
        if not html_balanced:
            print("   - HTML tags are unbalanced")
        if not js_balanced:
            print("   - JavaScript syntax has issues")
        return False

if __name__ == "__main__":
    filepath = "c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO\\workflow\\templates\\workflow\\negocios.html"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    success = final_check(content)
    
    if success:
        print("\n✅ TEMPLATE VALIDATION COMPLETE - ALL TESTS PASSED!")
    else:
        print("\n❌ TEMPLATE VALIDATION FAILED - ISSUES FOUND")
