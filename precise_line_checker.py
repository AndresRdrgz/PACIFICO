#!/usr/bin/env python3
"""
Line-by-line precise Django template analyzer
"""

import re

def analyze_precise_template():
    filepath = "c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO\\workflow\\templates\\workflow\\negocios.html"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("=== PRECISE LINE-BY-LINE ANALYSIS ===")
    
    # Check specific lines mentioned in the error
    check_lines = [588, 589, 590, 594, 595, 602, 606, 612, 616]
    
    for line_num in check_lines:
        if line_num <= len(lines):
            line = lines[line_num - 1].strip()
            
            # Find Django template tags in this line
            tags = re.findall(r'\{%\s*(.*?)\s*%\}', line)
            
            if tags:
                print(f"Line {line_num}: {line}")
                for tag in tags:
                    tag_name = tag.split()[0] if tag.split() else ''
                    print(f"  → Django tag: '{tag_name}' (full: {tag})")
            elif 'if' in line or 'else' in line or 'end' in line:
                print(f"Line {line_num}: {line} (NO DJANGO TAGS)")
            else:
                print(f"Line {line_num}: {line[:50]}...")

if __name__ == "__main__":
    analyze_precise_template()
