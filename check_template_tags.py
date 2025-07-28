#!/usr/bin/env python3
"""
Template Tag Balance Checker
Systematically checks that all Django template tags are properly opened and closed.
"""

import re
import sys

def analyze_template_tags(content):
    """Analyze Django template tags in the content and check for proper balancing."""
    
    # Define tag patterns
    patterns = {
        'if': (r'{%\s*if\s+.*?%}', r'{%\s*endif\s*%}'),
        'for': (r'{%\s*for\s+.*?%}', r'{%\s*endfor\s*%}'),
        'block': (r'{%\s*block\s+.*?%}', r'{%\s*endblock\s*%}'),
        'with': (r'{%\s*with\s+.*?%}', r'{%\s*endwith\s*%}'),
        'comment': (r'{%\s*comment\s*%}', r'{%\s*endcomment\s*%}'),
        'load': (r'{%\s*load\s+.*?%}', None),  # No closing tag
        'extends': (r'{%\s*extends\s+.*?%}', None),  # No closing tag
        'include': (r'{%\s*include\s+.*?%}', None),  # No closing tag
        'url': (r'{%\s*url\s+.*?%}', None),  # No closing tag
        'empty': (r'{%\s*empty\s*%}', None),  # Special case - part of for loop
        'else': (r'{%\s*else\s*%}', None),  # Special case - part of if
        'elif': (r'{%\s*elif\s+.*?%}', None),  # Special case - part of if
    }
    
    # Track tag stack for nested tags
    tag_stack = []
    errors = []
    line_number = 0
    
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Find all Django template tags in this line
        all_tags = re.finditer(r'{%\s*(.*?)\s*%}', line)
        
        for match in all_tags:
            tag_content = match.group(1).strip()
            tag_name = tag_content.split()[0] if tag_content.split() else ''
            
            print(f"Line {line_num}: Found tag '{tag_name}' -> {match.group(0)}")
            
            # Handle different tag types
            if tag_name.startswith('end'):
                # This is a closing tag
                closing_tag = tag_name[3:]  # Remove 'end' prefix
                if tag_stack and tag_stack[-1][0] == closing_tag:
                    opened_tag = tag_stack.pop()
                    print(f"  ✓ Closed {closing_tag} (opened at line {opened_tag[1]})")
                else:
                    if tag_stack:
                        errors.append(f"Line {line_num}: Found {tag_name} but expected end{tag_stack[-1][0]} (opened at line {tag_stack[-1][1]})")
                    else:
                        errors.append(f"Line {line_num}: Found {tag_name} but no corresponding opening tag")
                        
            elif tag_name in ['if', 'for', 'block', 'with', 'comment']:
                # These are opening tags that need closing
                tag_stack.append((tag_name, line_num))
                print(f"  → Opened {tag_name}")
                
            elif tag_name in ['else', 'elif', 'empty']:
                # These are intermediate tags - verify they're inside appropriate blocks
                if tag_name in ['else', 'elif'] and tag_stack and tag_stack[-1][0] != 'if':
                    errors.append(f"Line {line_num}: {tag_name} found outside of if block")
                elif tag_name == 'empty' and tag_stack and tag_stack[-1][0] != 'for':
                    errors.append(f"Line {line_num}: empty found outside of for block")
                print(f"  ↔ Intermediate tag {tag_name}")
                
            elif tag_name in ['load', 'extends', 'include', 'url']:
                # These are standalone tags
                print(f"  ○ Standalone tag {tag_name}")
                
            else:
                # Unknown or unhandled tag
                print(f"  ? Unknown tag: {tag_name}")
    
    # Check for unclosed tags
    if tag_stack:
        for tag_name, line_num in tag_stack:
            errors.append(f"Unclosed {tag_name} tag opened at line {line_num}")
    
    return errors

def check_template_file(filepath):
    """Check a template file for tag balance issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Analyzing template file: {filepath}")
        print("=" * 60)
        
        errors = analyze_template_tags(content)
        
        print("\n" + "=" * 60)
        if errors:
            print("ERRORS FOUND:")
            for error in errors:
                print(f"❌ {error}")
            return False
        else:
            print("✅ All template tags are properly balanced!")
            return True
            
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO\\workflow\\templates\\workflow\\negocios.html"
    
    success = check_template_file(filepath)
    sys.exit(0 if success else 1)
