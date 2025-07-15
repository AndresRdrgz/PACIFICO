import re

def find_missing_brace():
    with open('workflow/templates/workflow/detalle_solicitud_analisis.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    script_start = content.find('<script>')
    script_end = content.find('</script>', script_start)
    js_code = content[script_start+8:script_end]
    
    lines = js_code.split('\n')
    brace_count = 0
    
    for i, line in enumerate(lines, 1):
        open_braces = line.count('{')
        close_braces = line.count('}')
        brace_count += open_braces - close_braces
        
        if brace_count < 0:
            print(f"❌ Extra closing brace at line {i}: {line.strip()}")
            break
        elif brace_count > 0 and i == len(lines):
            print(f"❌ Missing {brace_count} closing brace(s) at end of script")
            print(f"Last few lines:")
            for j in range(max(0, len(lines)-5), len(lines)):
                print(f"  {j+1}: {lines[j].strip()}")
    
    print(f"\n📊 Final brace count: {brace_count}")
    return brace_count

if __name__ == "__main__":
    find_missing_brace() 