#!/usr/bin/env python
"""
RPA Test Script - Simulates Makito RPA updating APC status
This script demonstrates how the RPA would interact with the API
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust for your environment
API_ENDPOINT = f"{BASE_URL}/workflow/api/makito/update-status"

def update_apc_status(solicitud_codigo, status, observaciones=""):
    """
    Simulate RPA updating APC status
    
    Args:
        solicitud_codigo (str): Code of the solicitud
        status (str): New status ('in_progress', 'completed', 'error')
        observaciones (str): Optional observations
    """
    
    url = f"{API_ENDPOINT}/{solicitud_codigo}/"
    
    payload = {
        "status": status,
        "observaciones": observaciones
    }
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    try:
        print(f"🤖 Makito RPA: Updating {solicitud_codigo} to {status}")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data['message']}")
            print(f"   📊 Updated Data:")
            for key, value in data['data'].items():
                print(f"      {key}: {value}")
            return True
        else:
            error_data = response.json()
            print(f"   ❌ Error: {error_data.get('error', 'Unknown error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Could not connect to {BASE_URL}")
        print("   Make sure the Django server is running")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected Error: {e}")
        return False

def simulate_complete_workflow():
    """Simulate complete RPA workflow for APC processing"""
    
    print("🚀 Simulating Complete Makito RPA Workflow")
    print("=" * 50)
    
    # Example solicitud code (would come from email parsing in real RPA)
    solicitud_codigo = input("Enter solicitud code (e.g., APC-SAMPLE-001-0721): ").strip()
    
    if not solicitud_codigo:
        print("❌ No solicitud code provided")
        return
    
    print(f"\n📧 Step 1: RPA received workflowAPC email for {solicitud_codigo}")
    print("   - Email parsed successfully")
    print("   - Document type and number extracted")
    print("   - RPA preparing to start process...")
    
    # Step 1: Update to in_progress
    print(f"\n🔄 Step 2: Starting APC process")
    success = update_apc_status(
        solicitud_codigo, 
        "in_progress",
        "Makito RPA iniciando proceso de descarga APC - Conectando a sistemas externos"
    )
    
    if not success:
        print("❌ Failed to update status to in_progress")
        return
    
    input("\n⏸️  Press Enter to continue to completion...")
    
    # Step 2: Update to completed
    print(f"\n✅ Step 3: Completing APC process")
    success = update_apc_status(
        solicitud_codigo,
        "completed", 
        "APC descargado exitosamente por Makito RPA - Archivo guardado en sistema"
    )
    
    if success:
        print(f"\n🎉 Workflow completed successfully!")
        print(f"   Solicitud {solicitud_codigo} processed by Makito RPA")
        print(f"   APC document downloaded and stored")
        print(f"   Status tracking updated in system")
    else:
        print("❌ Failed to update status to completed")

def simulate_error_scenario():
    """Simulate RPA error scenario"""
    
    print("🚨 Simulating RPA Error Scenario")
    print("=" * 40)
    
    solicitud_codigo = input("Enter solicitud code for error test: ").strip()
    
    if not solicitud_codigo:
        print("❌ No solicitud code provided")
        return
    
    # Update to error status
    success = update_apc_status(
        solicitud_codigo,
        "error",
        "Error en proceso Makito RPA - Sistema externo no disponible - Reintento necesario"
    )
    
    if success:
        print("✅ Error status updated successfully")
        print("   User will be notified of the error")
        print("   Manual intervention may be required")

def test_api_connectivity():
    """Test basic API connectivity"""
    
    print("🔗 Testing API Connectivity")
    print("=" * 30)
    
    try:
        # Test with a non-existent code to check API response
        test_url = f"{API_ENDPOINT}/TEST-CONNECTIVITY/"
        response = requests.post(
            test_url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps({"status": "in_progress"})
        )
        
        if response.status_code in [200, 400, 404]:
            print(f"✅ API is accessible at {BASE_URL}")
            print(f"   Response code: {response.status_code}")
            if response.status_code == 404:
                print("   (404 is expected for non-existent solicitud)")
        else:
            print(f"⚠️  Unexpected response code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Make sure Django development server is running:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Error testing connectivity: {e}")

def main():
    """Main menu for RPA simulation"""
    
    print("🤖 Makito RPA Simulation Tool")
    print("=" * 40)
    print("1. Test API Connectivity")
    print("2. Simulate Complete Workflow")
    print("3. Simulate Error Scenario")
    print("4. Manual Status Update")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            test_api_connectivity()
        elif choice == "2":
            simulate_complete_workflow()
        elif choice == "3":
            simulate_error_scenario()
        elif choice == "4":
            codigo = input("Solicitud code: ").strip()
            status = input("New status (pending/in_progress/completed/error): ").strip()
            obs = input("Observations (optional): ").strip()
            update_apc_status(codigo, status, obs)
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
