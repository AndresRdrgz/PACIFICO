"""
Simple debug script to test cotizaciones API endpoint directly
"""

import requests
import json

def test_cotizaciones_api():
    print("=" * 60)
    print("TESTING COTIZACIONES API DIRECTLY")
    print("=" * 60)
    
    # Test with a real solicitud ID (you'll need to replace this)
    test_solicitud_id = 1  # Replace with actual solicitud ID
    test_url = f"http://localhost:8000/workflow/api/cotizaciones-cliente/{test_solicitud_id}/"
    
    print(f"🔍 Testing URL: {test_url}")
    print()
    
    try:
        # Make the request (assuming you're logged in or have session)
        response = requests.get(test_url)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if 'cotizaciones' in data:
                print(f"\n📋 Found {len(data['cotizaciones'])} cotizaciones")
                print(f"📋 Cliente cedula: {data.get('cliente_cedula', 'N/A')}")
                
                for i, cot in enumerate(data['cotizaciones'][:3]):  # Show first 3
                    print(f"\n  Cotización {i+1}:")
                    print(f"    ID: {cot.get('id')}")
                    print(f"    Cedula: {cot.get('cedulaCliente')}")
                    print(f"    Cliente: {cot.get('nombreCliente')}")
                    print(f"    Monto: {cot.get('monto')}")
                    
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_cotizaciones_api()
