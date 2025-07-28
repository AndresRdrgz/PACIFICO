#!/usr/bin/env python3
"""
Precise div tag tracker
"""

import re

def precise_div_check(content):
    """Precisely track div tags and find exactly where the missing ones should be."""
    lines = content.split('\n')
    div_stack = []
    issues = []
    
    for line_num, line in enumerate(lines, 1):
        # Find all opening divs (excluding self-closing ones)
        div_opens = re.finditer(r'<div\b[^>]*(?<!/)>', line, re.IGNORECASE)
        for match in div_opens:
            div_stack.append({
                'line': line_num,
                'column': match.start(),
                'tag': match.group(),
                'context': line.strip()
            })
        
        # Find all closing divs
        div_closes = re.finditer(r'</div>', line, re.IGNORECASE)
        for match in div_closes:
            if div_stack:
                opened = div_stack.pop()
                print(f"✓ Line {line_num}: Closed div (opened at line {opened['line']})")
            else:
                issues.append(f"❌ Line {line_num}: Extra closing </div> with no matching opening tag")
                print(f"❌ Line {line_num}: Extra closing </div>: {line.strip()}")
    
    # Report unclosed divs
    if div_stack:
        print(f"\n❌ Found {len(div_stack)} unclosed div tags:")
        for div_info in div_stack:
            print(f"  Line {div_info['line']}: {div_info['context']}")
        
        # Try to suggest where closing tags should go
        print("\n💡 Suggested locations for missing </div> tags:")
        for div_info in div_stack[-2:]:  # Show last 2 unclosed divs
            # Look for the end of the current block
            start_line = div_info['line']
            for check_line in range(start_line + 1, min(start_line + 50, len(lines))):
                if lines[check_line].strip() and not lines[check_line].strip().startswith('<'):
                    print(f"  Consider adding </div> around line {check_line}")
                    break
    else:
        print("✅ All div tags are properly paired!")
    
    return len(div_stack) == 0 and len(issues) == 0

if __name__ == "__main__":
    filepath = "c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO\\workflow\\templates\\workflow\\negocios.html"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== Precise div tag analysis ===")
    is_balanced = precise_div_check(content)
