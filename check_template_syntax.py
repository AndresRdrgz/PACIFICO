#!/usr/bin/env python
"""
Template syntax checker for Kanban view
"""

def check_template_syntax():
    """Check Django template syntax in negocios.html"""
    
    print("🔍 Checking Kanban Template Syntax")
    print("=" * 50)
    
    template_path = r"c:\Users\arodriguez\Documents\GitHub\PACIFICO\workflow\templates\workflow\negocios.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Template file loaded: {len(content)} characters")
        
        # Check for critical Django template blocks
        syntax_checks = [
            # Basic structure
            ("{% elif view_type == 'kanban' %}", "Kanban view condition"),
            ("{% for etapa in pipeline.etapas.all %}", "Etapas loop"),
            ("{% for s in solicitudes_por_etapa|get_item:etapa.id %}", "Solicitudes loop with filter"),
            ("{% empty %}", "Empty handling"),
            ("{% endfor %}", "Loop closure"),
            
            # Template filters
            ("solicitudes_por_etapa|get_item:etapa.id", "get_item filter usage"),
            ("|length", "Length filter usage"),
            ("|truncatechars:", "Truncate filter usage"),
            
            # Conditional blocks
            ("{% if s.id %}", "Solicitud ID check"),
            ("{% if pipeline %}", "Pipeline check"),
            ("{% else %}", "Else condition"),
            ("{% endif %}", "If closure"),
            
            # URL generation
            ("{% url 'workflow:detalle_solicitud' s.id %}", "URL generation"),
            
            # Template variables
            ("{{ pipeline.nombre }}", "Pipeline name variable"),
            ("{{ etapa.nombre }}", "Etapa name variable"),
            ("{{ s.cliente_nombre }}", "Cliente name variable"),
        ]
        
        print("\n🔍 Django Template Syntax Checks:")
        print("-" * 40)
        
        all_passed = True
        for syntax, description in syntax_checks:
            found = syntax in content
            status = "✅" if found else "❌"
            print(f"{status} {description}: {found}")
            if not found:
                all_passed = False
        
        # Check for potential syntax errors
        print("\n🔍 Potential Syntax Issues:")
        print("-" * 30)
        
        error_patterns = [
            ("{% for", "{% endfor", "Unclosed for loops"),
            ("{% if", "{% endif", "Unclosed if statements"),
            ("{%", "%}", "Unmatched template tags"),
            ("{{", "}}", "Unmatched variables"),
        ]
        
        syntax_issues = []
        for open_tag, close_tag, description in error_patterns:
            open_count = content.count(open_tag)
            close_count = content.count(close_tag)
            
            if open_count != close_count:
                syntax_issues.append(f"{description}: {open_count} open, {close_count} close")
                print(f"⚠️  {description}: {open_count} open vs {close_count} close")
            else:
                print(f"✅ {description}: Balanced ({open_count} pairs)")
        
        # Check for Kanban-specific elements
        print("\n🎯 Kanban-Specific Elements:")
        print("-" * 30)
        
        kanban_elements = [
            ('class="kanban-container"', "Kanban container class"),
            ('class="kanban-board d-flex"', "Kanban board class"),
            ('class="kanban-column"', "Kanban column class"),
            ('class="kanban-card mb-3"', "Kanban card class"),
            ('Debug Information', "Debug section"),
            ('id="kanbanFiltro', "Kanban filters"),
        ]
        
        kanban_issues = []
        for element, description in kanban_elements:
            found = element in content
            status = "✅" if found else "❌"
            print(f"{status} {description}: {found}")
            if not found:
                kanban_issues.append(description)
        
        # Final assessment
        print("\n📋 FINAL ASSESSMENT")
        print("=" * 25)
        
        if all_passed and not syntax_issues and not kanban_issues:
            print("🎉 ALL CHECKS PASSED")
            print("✅ Django template syntax is correct")
            print("✅ Kanban elements are present")
            print("✅ Template should render properly")
            return True
        else:
            print("⚠️  ISSUES FOUND")
            if not all_passed:
                print("❌ Some Django syntax elements missing")
            if syntax_issues:
                print("❌ Template syntax imbalances detected")
            if kanban_issues:
                print("❌ Some Kanban elements missing")
            
            print("\n🔧 RECOMMENDED ACTIONS:")
            print("1. Start Django development server")
            print("2. Access: http://127.0.0.1:8000/workflow/negocios/?pipeline=12&view=kanban")
            print("3. Check browser console for JavaScript errors")
            print("4. Check Django logs for template errors")
            
            return False
    
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        return False
    except Exception as e:
        print(f"❌ Error checking template: {e}")
        return False

if __name__ == '__main__':
    success = check_template_syntax()
    print(f"\nTemplate syntax check: {'PASSED' if success else 'FAILED'}")
