#!/usr/bin/env python3
"""
Debug the API endpoint by creating a simplified test view
"""

def debug_api_solicitudes_procesadas():
    """Debug version of the API to test issues"""
    
    # Simulate request parameters
    page = 1
    per_page = 10
    search = ""
    
    print("🔍 Debugging API Solicitudes Procesadas")
    print("=" * 50)
    
    print(f"📋 Parameters:")
    print(f"   Page: {page}")
    print(f"   Per page: {per_page}")
    print(f"   Search: '{search}'")
    
    try:
        # Test basic imports
        print("\n1️⃣ Testing imports...")
        from workflow.modelsWorkflow import Solicitud, ParticipacionComite
        print("   ✅ Models imported successfully")
        
        # Test query building  
        print("\n2️⃣ Testing query...")
        
        # Basic query test - just get all solicitudes
        print("   Testing basic Solicitud query...")
        total_solicitudes = Solicitud.objects.count()
        print(f"   ✅ Total solicitudes in DB: {total_solicitudes}")
        
        # Test ParticipacionComite query
        print("   Testing ParticipacionComite query...")
        total_participaciones = ParticipacionComite.objects.count()
        print(f"   ✅ Total participaciones in DB: {total_participaciones}")
        
        # Test the filtered query
        print("   Testing filtered query (solicitudes with participaciones)...")
        solicitudes_con_participaciones = Solicitud.objects.filter(
            participaciones_comite__isnull=False
        ).distinct().count()
        print(f"   ✅ Solicitudes with participaciones: {solicitudes_con_participaciones}")
        
        if solicitudes_con_participaciones > 0:
            print("\n3️⃣ Testing detailed query...")
            # Test the full query
            solicitudes_query = Solicitud.objects.filter(
                participaciones_comite__isnull=False
            ).distinct().select_related('cliente', 'cotizacion', 'etapa_actual').order_by('-fecha_ultima_actualizacion')
            
            # Get first few records
            solicitudes = list(solicitudes_query[:3])
            print(f"   ✅ Retrieved {len(solicitudes)} sample solicitudes")
            
            for i, solicitud in enumerate(solicitudes):
                print(f"   📄 Solicitud {i+1}:")
                print(f"      ID: {solicitud.id}")
                print(f"      Codigo: {solicitud.codigo}")
                print(f"      Cliente: {getattr(solicitud.cliente, 'nombreCliente', 'N/A') if solicitud.cliente else 'Sin cliente'}")
                print(f"      Participaciones: {solicitud.participaciones_comite.count()}")
        
        print("\n🎉 All tests passed! API logic should work.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_api_solicitudes_procesadas()
    if success:
        print("\n💡 The API logic is working. The 500 error might be a different issue.")
    else:
        print("\n⚠️ There are issues with the API logic that need to be fixed.")
