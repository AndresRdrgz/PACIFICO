#!/usr/bin/env python3
"""
Comprehensive Template Validation
Performs additional checks beyond basic tag balancing.
"""

import re
import sys

def validate_html_structure(content):
    """Check for unclosed HTML tags and other structural issues."""
    errors = []
    
    # Check for common HTML tag mismatches
    html_patterns = {
        'div': (r'<div\b[^>]*>', r'</div>'),
        'span': (r'<span\b[^>]*>', r'</span>'),
        'table': (r'<table\b[^>]*>', r'</table>'),
        'tr': (r'<tr\b[^>]*>', r'</tr>'),
        'td': (r'<td\b[^>]*>', r'</td>'),
        'th': (r'<th\b[^>]*>', r'</th>'),
        'tbody': (r'<tbody\b[^>]*>', r'</tbody>'),
        'thead': (r'<thead\b[^>]*>', r'</thead>'),
        'form': (r'<form\b[^>]*>', r'</form>'),
        'script': (r'<script\b[^>]*>', r'</script>'),
        'style': (r'<style\b[^>]*>', r'</style>'),
    }
    
    for tag_name, (open_pattern, close_pattern) in html_patterns.items():
        open_tags = re.findall(open_pattern, content, re.IGNORECASE)
        close_tags = re.findall(close_pattern, content, re.IGNORECASE)
        
        # Filter out self-closing tags
        self_closing = re.findall(rf'<{tag_name}\b[^>]*/>', content, re.IGNORECASE)
        open_count = len(open_tags) - len(self_closing)
        close_count = len(close_tags)
        
        if open_count != close_count:
            errors.append(f"HTML tag mismatch: {tag_name} - {open_count} opening tags, {close_count} closing tags")
    
    return errors

def check_string_quotes(content):
    """Check for unmatched quotes in Django template variables."""
    errors = []
    
    # Find all Django template variables and filters
    django_vars = re.findall(r'\{\{.*?\}\}', content, re.DOTALL)
    
    for var in django_vars:
        # Check for unmatched quotes in string literals
        single_quotes = var.count("'") - var.count("\\'")
        double_quotes = var.count('"') - var.count('\\"')
        
        if single_quotes % 2 != 0:
            errors.append(f"Unmatched single quotes in: {var[:50]}...")
        if double_quotes % 2 != 0:
            errors.append(f"Unmatched double quotes in: {var[:50]}...")
    
    return errors

def check_javascript_syntax(content):
    """Basic check for JavaScript syntax issues."""
    errors = []
    
    # Find JavaScript blocks
    js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    
    for i, js_block in enumerate(js_blocks):
        # Check for basic JavaScript syntax issues
        open_braces = js_block.count('{')
        close_braces = js_block.count('}')
        
        if open_braces != close_braces:
            errors.append(f"JavaScript block {i+1}: Mismatched braces - {open_braces} opening, {close_braces} closing")
        
        open_parens = js_block.count('(')
        close_parens = js_block.count(')')
        
        if open_parens != close_parens:
            errors.append(f"JavaScript block {i+1}: Mismatched parentheses - {open_parens} opening, {close_parens} closing")
    
    return errors

def comprehensive_check(filepath):
    """Run comprehensive validation checks."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Running comprehensive validation on: {filepath}")
        print("=" * 80)
        
        all_errors = []
        
        # Check HTML structure
        print("1. Checking HTML tag structure...")
        html_errors = validate_html_structure(content)
        all_errors.extend(html_errors)
        if html_errors:
            for error in html_errors:
                print(f"   ❌ {error}")
        else:
            print("   ✅ HTML tags are properly balanced")
        
        # Check Django template quotes
        print("\n2. Checking Django template string quotes...")
        quote_errors = check_string_quotes(content)
        all_errors.extend(quote_errors)
        if quote_errors:
            for error in quote_errors:
                print(f"   ❌ {error}")
        else:
            print("   ✅ All quotes are properly matched")
        
        # Check JavaScript syntax
        print("\n3. Checking JavaScript syntax...")
        js_errors = check_javascript_syntax(content)
        all_errors.extend(js_errors)
        if js_errors:
            for error in js_errors:
                print(f"   ❌ {error}")
        else:
            print("   ✅ JavaScript syntax appears correct")
        
        print("\n" + "=" * 80)
        
        if all_errors:
            print(f"❌ Found {len(all_errors)} issues:")
            for error in all_errors:
                print(f"   • {error}")
            return False
        else:
            print("✅ All comprehensive checks passed!")
            return True
            
    except Exception as e:
        print(f"Error during validation: {e}")
        return False

if __name__ == "__main__":
    filepath = "c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO\\workflow\\templates\\workflow\\negocios.html"
    success = comprehensive_check(filepath)
    sys.exit(0 if success else 1)
