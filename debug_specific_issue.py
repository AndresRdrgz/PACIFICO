#!/usr/bin/env python3
"""
Specific Template Issue Debugger
Focus on the specific lines causing the balance issue.
"""

import re

def debug_specific_lines():
    filepath = "c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO\\workflow\\templates\\workflow\\negocios.html"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Focus on the problematic area
    start_line = 560
    end_line = 620
    
    print("=== DEBUGGING LINES 560-620 ===")
    
    tag_stack = []
    
    for i in range(start_line - 1, min(end_line, len(lines))):
        line_num = i + 1
        line = lines[i].strip()
        
        # Find Django template tags
        tags = re.findall(r'\{%\s*(.*?)\s*%\}', line)
        
        if tags:
            print(f"Line {line_num}: {line}")
            
            for tag in tags:
                tag_name = tag.split()[0] if tag.split() else ''
                print(f"  Tag: '{tag_name}' -> {tag}")
                
                if tag_name.startswith('end'):
                    closing_tag = tag_name[3:]
                    if tag_stack and tag_stack[-1][0] == closing_tag:
                        opened = tag_stack.pop()
                        print(f"    ✓ Closed {closing_tag} (opened at line {opened[1]})")
                    else:
                        print(f"    ❌ ERROR: Found {tag_name} but expected end{tag_stack[-1][0] if tag_stack else 'NONE'}")
                        if tag_stack:
                            print(f"       Stack: {[f'{t[0]}@{t[1]}' for t in tag_stack]}")
                        
                elif tag_name in ['if', 'for', 'block', 'with', 'comment']:
                    tag_stack.append((tag_name, line_num))
                    print(f"    → Opened {tag_name}")
                    
                elif tag_name in ['else', 'elif', 'empty']:
                    if tag_name in ['else', 'elif']:
                        if not tag_stack or tag_stack[-1][0] != 'if':
                            print(f"    ❌ ERROR: {tag_name} found but no matching 'if' block")
                            print(f"       Stack: {[f'{t[0]}@{t[1]}' for t in tag_stack]}")
                        else:
                            print(f"    ↔ Valid {tag_name} for if at line {tag_stack[-1][1]}")
                    elif tag_name == 'empty':
                        if not tag_stack or tag_stack[-1][0] != 'for':
                            print(f"    ❌ ERROR: empty found but no matching 'for' block")
                            print(f"       Stack: {[f'{t[0]}@{t[1]}' for t in tag_stack]}")
                        else:
                            print(f"    ↔ Valid empty for for at line {tag_stack[-1][1]}")
    
    print(f"\nFinal stack: {[f'{t[0]}@{t[1]}' for t in tag_stack]}")

if __name__ == "__main__":
    debug_specific_lines()
