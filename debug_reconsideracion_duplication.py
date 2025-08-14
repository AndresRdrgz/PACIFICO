#!/usr/bin/env python3
"""
Quick test to check the reconsideración API response and debug duplication
"""
import os
import sys
import django
import json

# Setup Django
sys.path.append('/Users/andresrdrgz_/Documents/GitHub/PACIFICO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from workflow.modelsWorkflow import Solicitud

def test_reconsideracion_api():
    """Test the reconsideración API directly"""
    print("🧪 Testing Reconsideración API for FLU-156")
    print("=" * 50)
    
    # Get test solicitud
    try:
        solicitud = Solicitud.objects.get(codigo='FLU-156')
        print(f"✅ Found solicitud: {solicitud.codigo} (ID: {solicitud.id})")
    except Solicitud.DoesNotExist:
        print("❌ Solicitud FLU-156 not found")
        return
    
    # Get reconsideraciones directly from model
    reconsideraciones = solicitud.reconsideraciones.all().order_by('-numero_reconsideracion')
    print(f"📊 Direct model query - Total reconsideraciones: {reconsideraciones.count()}")
    
    for recon in reconsideraciones:
        print(f"   - #{recon.numero_reconsideracion}: {recon.estado} (ID: {recon.id})")
    
    # Test API endpoint
    client = Client()
    try:
        user = User.objects.get(username='admin')
        client.login(username='admin', password='admin123')
        print("✅ Logged in as admin")
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        client.login(username='admin', password='admin123')
        print("✅ Created and logged in as admin")
    
    # Call API endpoint
    api_url = f'/workflow/api/solicitud/{solicitud.id}/reconsideracion/historial/'
    print(f"🔗 Testing API: {api_url}")
    
    response = client.get(api_url)
    print(f"📡 API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ API Success: {data.get('success')}")
            print(f"📊 API Response - Total reconsideraciones: {len(data.get('reconsideraciones', []))}")
            
            # Check for duplicates in API response
            api_reconsideraciones = data.get('reconsideraciones', [])
            seen_ids = set()
            seen_numbers = set()
            duplicates_by_id = []
            duplicates_by_number = []
            
            for recon in api_reconsideraciones:
                recon_id = recon.get('id')
                recon_number = recon.get('numero')
                
                if recon_id in seen_ids:
                    duplicates_by_id.append(recon_id)
                seen_ids.add(recon_id)
                
                if recon_number in seen_numbers:
                    duplicates_by_number.append(recon_number)
                seen_numbers.add(recon_number)
                
                print(f"   - API #{recon_number}: {recon.get('estado')} (ID: {recon_id})")
            
            if duplicates_by_id:
                print(f"❌ DUPLICATES BY ID FOUND: {duplicates_by_id}")
            if duplicates_by_number:
                print(f"❌ DUPLICATES BY NUMBER FOUND: {duplicates_by_number}")
            
            if not duplicates_by_id and not duplicates_by_number:
                print("✅ No duplicates found in API response")
                print("🔍 Issue might be in frontend rendering, not backend data")
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON response")
            print(f"Response content: {response.content.decode()[:200]}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.content.decode()[:200]}")

if __name__ == '__main__':
    test_reconsideracion_api()
