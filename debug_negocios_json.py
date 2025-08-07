#!/usr/bin/env python3
"""
Detailed debugging script to find the non-serializable User objects
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
sys.path.append('/Users/andresrdrgz_/Documents/GitHub/PACIFICO')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from workflow.views_negocios import get_user_pipeline_access, get_user_solicitudes_queryset, enrich_solicitud_data
import json

def find_non_serializable_objects(obj, path="root"):
    """Recursively find non-JSON-serializable objects"""
    problematic_paths = []
    
    try:
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}"
                try:
                    json.dumps(value)
                except (TypeError, ValueError):
                    problematic_paths.extend(find_non_serializable_objects(value, current_path))
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                current_path = f"{path}[{i}]"
                try:
                    json.dumps(value)
                except (TypeError, ValueError):
                    problematic_paths.extend(find_non_serializable_objects(value, current_path))
        else:
            # Try to serialize the object itself
            try:
                json.dumps(obj)
            except (TypeError, ValueError):
                problematic_paths.append((path, type(obj).__name__, str(obj)[:100]))
                
    except Exception as e:
        problematic_paths.append((path, "Exception", str(e)))
    
    return problematic_paths

def debug_api_data_structure():
    """Debug the exact structure being returned by api_solicitudes_data"""
    print("🔬 Debugging API data structure...")
    
    # Get test user
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    
    if not user:
        print("❌ No test user available")
        return
    
    print(f"✅ Using test user: {user.username}")
    
    # Test individual components
    print("\n1️⃣ Testing access_info...")
    access_info = get_user_pipeline_access(user)
    print(f"   - has_access: {access_info['has_access']}")
    print(f"   - pipelines count: {len(access_info['pipelines'])}")
    print(f"   - pipeline_permissions: {type(access_info['pipeline_permissions'])}")
    
    # Check if pipelines contain User objects
    print("\n2️⃣ Checking pipelines for User objects...")
    for i, pipeline in enumerate(access_info['pipelines']):
        print(f"   Pipeline {i}: {type(pipeline)} - {getattr(pipeline, 'nombre', 'No name')}")
        # Check pipeline attributes for User objects
        for attr_name in dir(pipeline):
            if not attr_name.startswith('_'):
                try:
                    attr_value = getattr(pipeline, attr_name)
                    if isinstance(attr_value, User):
                        print(f"   ⚠️ Found User object: {attr_name} = {attr_value}")
                except:
                    pass
    
    print("\n3️⃣ Testing queryset and enrichment...")
    queryset = get_user_solicitudes_queryset(user, '12')  # Use pipeline 12
    solicitudes = list(queryset[:1])  # Just test with one
    
    if solicitudes:
        solicitud = solicitudes[0]
        print(f"   Original solicitud type: {type(solicitud)}")
        
        # Enrich the data
        enriched = enrich_solicitud_data(solicitud)
        print(f"   Enriched solicitud: {enriched is not None}")
        
        # Check for User objects in enriched solicitud
        print("\n4️⃣ Checking enriched solicitud for User objects...")
        for attr_name in dir(enriched):
            if not attr_name.startswith('_'):
                try:
                    attr_value = getattr(enriched, attr_name)
                    if isinstance(attr_value, User):
                        print(f"   ⚠️ Found User object: {attr_name} = {attr_value}")
                    elif hasattr(attr_value, '__dict__') and any(isinstance(v, User) for v in attr_value.__dict__.values() if hasattr(attr_value, '__dict__')):
                        print(f"   ⚠️ Found object containing User: {attr_name} = {type(attr_value)}")
                except:
                    pass
        
        # Test the actual solicitud_data creation process
        print("\n5️⃣ Testing solicitud_data creation...")
        
        solicitud_data = {
            'id': getattr(solicitud, 'id', getattr(solicitud, 'pk', None)),
            'codigo': getattr(solicitud, 'codigo', '') or f'SOL-{getattr(solicitud, "id", "N/A")}',
            'cliente_nombre': getattr(solicitud, 'cliente_nombre_completo', ''),
            'cliente_cedula': getattr(solicitud, 'cliente_cedula_completa', ''),
            'propietario': getattr(solicitud, 'propietario', ''),
        }
        
        # Test this basic structure
        try:
            json.dumps(solicitud_data)
            print("   ✅ Basic solicitud_data is JSON-safe")
        except Exception as e:
            print(f"   ❌ Basic solicitud_data failed: {e}")
            problems = find_non_serializable_objects(solicitud_data)
            for path, obj_type, obj_str in problems:
                print(f"      - {path}: {obj_type} = {obj_str}")
        
        # Test with all enriched data
        print("\n6️⃣ Testing with enriched data...")
        for key, value in enriched.__dict__.items():
            if key.startswith('enriched_') and value is not None:
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    solicitud_data[key] = value
                else:
                    print(f"   ⚠️ Skipping non-JSON-safe enriched data: {key} = {type(value)}")
        
        try:
            json.dumps(solicitud_data)
            print("   ✅ Full solicitud_data with enriched data is JSON-safe")
        except Exception as e:
            print(f"   ❌ Full solicitud_data failed: {e}")
            problems = find_non_serializable_objects(solicitud_data)
            for path, obj_type, obj_str in problems:
                print(f"      - {path}: {obj_type} = {obj_str}")

def debug_response_structure():
    """Debug the exact response_data structure"""
    print("\n🔍 Debugging full response structure...")
    
    # Create the response data step by step like the API does
    user = User.objects.first()
    if not user:
        print("❌ No test user")
        return
    
    # Test each component of response_data
    print("7️⃣ Testing response components...")
    
    components = {}
    
    # Test basic data
    components['solicitudes'] = []
    components['solicitudes_por_etapa'] = {}
    components['etapas_disponibles'] = []
    components['subestados_disponibles'] = []
    
    # Test pagination
    components['pagination'] = {
        'current_page': 1,
        'total_pages': 1,
        'total_count': 0,
        'has_next': False,
        'has_previous': False,
        'per_page': 15
    }
    
    # Test statistics
    components['statistics'] = {
        'total_solicitudes': 0,
        'solicitudes_pendientes': 0
    }
    
    # Test filters_applied
    components['filters_applied'] = {
        'search': '',
        'pipeline': '12',
        'etapa': '',
        'estado': '',
    }
    
    # Test each component
    for name, component in components.items():
        try:
            json.dumps(component)
            print(f"   ✅ {name} is JSON-safe")
        except Exception as e:
            print(f"   ❌ {name} failed: {e}")
            problems = find_non_serializable_objects(component, name)
            for path, obj_type, obj_str in problems:
                print(f"      - {path}: {obj_type} = {obj_str}")
    
    # Test full response
    response_data = {
        'success': True,
        'data': components
    }
    
    try:
        json.dumps(response_data)
        print("   ✅ Full response_data is JSON-safe")
    except Exception as e:
        print(f"   ❌ Full response_data failed: {e}")
        problems = find_non_serializable_objects(response_data)
        print(f"   Found {len(problems)} problematic objects:")
        for path, obj_type, obj_str in problems[:10]:  # Show first 10
            print(f"      - {path}: {obj_type} = {obj_str}")

if __name__ == "__main__":
    print("=" * 70)
    print("🔬 DETAILED DEBUGGING: JSON SERIALIZATION ISSUES")
    print("=" * 70)
    
    debug_api_data_structure()
    debug_response_structure()
    
    print("\n" + "=" * 70)
    print("🎯 DEBUGGING COMPLETE")
    print("=" * 70)
