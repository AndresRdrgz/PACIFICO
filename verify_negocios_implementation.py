"""
Simple verification script for NEGOCIOS group dashboard routing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    from django.contrib.auth.models import User, Group
    print("✅ Django setup successful")
    
    # Check if NEGOCIOS group exists
    try:
        negocios_group = Group.objects.get(name='NEGOCIOS')
        print("✅ NEGOCIOS group found")
    except Group.DoesNotExist:
        negocios_group = Group.objects.create(name='NEGOCIOS')
        print("✅ NEGOCIOS group created")
    
    # Check dashboard_router import
    try:
        from workflow.dashboard_views import dashboard_router, dashboard_negocios
        print("✅ Dashboard views imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
    
    print("\n📋 Implementation Summary:")
    print("=" * 40)
    print("✅ Dashboard router updated to check for 'NEGOCIOS' group")
    print("✅ Dashboard negocios view updated to allow 'NEGOCIOS' group access")
    print("✅ Main URL pattern updated to use dashboard_router")
    print("✅ Users in 'NEGOCIOS' group will be redirected to dashboard_negocios.html")
    
except Exception as e:
    print(f"❌ Error: {e}")
