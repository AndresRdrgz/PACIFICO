#!/usr/bin/env python3
"""
Find unclosed div tags
"""

import re

def find_unclosed_divs(content):
    """Find lines with unclosed div tags."""
    lines = content.split('\n')
    div_stack = []
    
    for line_num, line in enumerate(lines, 1):
        # Find all div tags in this line
        div_opens = re.findall(r'<div\b[^>]*(?<!/)>', line, re.IGNORECASE)
        div_closes = re.findall(r'</div>', line, re.IGNORECASE)
        
        # Track opening divs
        for div_open in div_opens:
            div_stack.append((line_num, div_open))
        
        # Track closing divs
        for _ in div_closes:
            if div_stack:
                div_stack.pop()
            else:
                print(f"Line {line_num}: Extra </div> found: {line.strip()}")
    
    # Report unclosed divs
    if div_stack:
        print(f"Found {len(div_stack)} unclosed div tags:")
        for line_num, div_tag in div_stack:
            print(f"  Line {line_num}: {div_tag}")
    else:
        print("All div tags are properly closed!")

def find_missing_parens(content):
    """Find JavaScript blocks with missing parentheses."""
    js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    
    for i, js_block in enumerate(js_blocks):
        lines = js_block.split('\n')
        paren_count = 0
        
        for line_num, line in enumerate(lines, 1):
            line_open = line.count('(')
            line_close = line.count(')')
            paren_count += line_open - line_close
            
            if ')' in line and paren_count < 0:
                print(f"JavaScript block {i+1}, line {line_num}: Extra closing parenthesis")
                print(f"  {line.strip()}")
        
        if paren_count != 0:
            print(f"JavaScript block {i+1}: Missing {abs(paren_count)} {'opening' if paren_count < 0 else 'closing'} parentheses")

if __name__ == "__main__":
    filepath = "c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO\\workflow\\templates\\workflow\\negocios.html"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== Finding unclosed div tags ===")
    find_unclosed_divs(content)
    
    print("\n=== Finding missing parentheses ===")
    find_missing_parens(content)
