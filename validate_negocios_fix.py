#!/usr/bin/env python
"""
Test script to verify the negocios view fix
"""
import os
import sys
import django

# Add the project directory to the Python path
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')
django.setup()

from django.db.models import Q
from workflow.modelsWorkflow import Pipeline
from django.contrib.auth.models import User

def test_pipeline_query():
    """Test that the pipeline query with permisos_pipeline works correctly"""
    try:
        # Get first user (should be the oficial user or any user)
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
            
        print(f"🔍 Testing with user: {user.username}")
        
        # Test the corrected query
        pipelines = Pipeline.objects.filter(
            Q(permisos_pipeline__usuario=user) |
            Q(etapas__permisos__grupo__user=user)
        ).distinct()
        
        print(f"✅ Query executed successfully")
        print(f"📊 Found {pipelines.count()} pipelines for user {user.username}")
        
        # List the pipelines
        for pipeline in pipelines:
            print(f"   - {pipeline.nombre} (ID: {pipeline.id})")
            
        return True
        
    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")
        return False

def test_superuser_query():
    """Test superuser query"""
    try:
        pipelines = Pipeline.objects.all()
        print(f"✅ Superuser query executed successfully")
        print(f"📊 Total pipelines in system: {pipelines.count()}")
        return True
    except Exception as e:
        print(f"❌ Error in superuser query: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing negocios view fix...")
    print("=" * 50)
    
    # Test regular user query
    print("\n1. Testing regular user pipeline query:")
    test1_result = test_pipeline_query()
    
    # Test superuser query
    print("\n2. Testing superuser pipeline query:")
    test2_result = test_superuser_query()
    
    print("\n" + "=" * 50)
    if test1_result and test2_result:
        print("✅ All tests passed! The fix should work correctly.")
    else:
        print("❌ Some tests failed. Please check the database or model definitions.")
    
    print("\n🔍 Pipeline model fields:")
    try:
        pipeline = Pipeline.objects.first()
        if pipeline:
            print("   Available related fields:")
            for field in pipeline._meta.get_fields():
                if hasattr(field, 'related_name') and field.related_name:
                    print(f"   - {field.related_name} (from {field.name})")
    except Exception as e:
        print(f"   Error getting model fields: {e}")
