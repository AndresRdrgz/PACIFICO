#!/usr/bin/env python3
import os
import sys
import django

# Add the project path to sys.path
sys.path.append('/Users/andresrdrgz_/Documents/GitHub/PACIFICO')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.contrib.auth.models import User
from workflow.models import Solicitud
from workflow.modelsWorkflow import NivelComite, UsuarioNivelComite, ParticipacionComite
from django.utils import timezone

def setup_test_committee_data():
    """Set up test committee data for demonstration"""
    try:
        # Get a test solicitud
        solicitud = Solicitud.objects.first()
        if not solicitud:
            print("❌ No hay solicitudes disponibles")
            return
        
        # Get test users
        users = User.objects.all()[:3]  # Get first 3 users
        if len(users) < 2:
            print("❌ No hay suficientes usuarios para crear datos de prueba")
            return
        
        print(f"🔄 Configurando datos de prueba del comité para solicitud {solicitud.codigo}...")
        
        # Create committee levels if they don't exist
        nivel1, created = NivelComite.objects.get_or_create(
            nombre="Nivel 1 - Analista Senior",
            defaults={'orden': 1}
        )
        if created:
            print(f"✅ Creado nivel: {nivel1.nombre}")
        
        nivel2, created = NivelComite.objects.get_or_create(
            nombre="Nivel 2 - Gerente de Crédito",
            defaults={'orden': 2}
        )
        if created:
            print(f"✅ Creado nivel: {nivel2.nombre}")
        
        # Assign users to levels
        for i, user in enumerate(users[:2]):
            nivel = nivel1 if i == 0 else nivel2
            UsuarioNivelComite.objects.get_or_create(
                usuario=user,
                nivel=nivel,
                defaults={'activo': True}
            )
            print(f"✅ Usuario {user.username} asignado a {nivel.nombre}")
        
        # Create test participations
        participaciones_data = [
            {
                'usuario': users[0],
                'nivel': nivel1,
                'resultado': 'APROBADO',
                'comentario': 'Solicitud revisada y aprobada desde el nivel 1. Los documentos están completos y cumplen con todos los requisitos establecidos. El cliente presenta un perfil de riesgo aceptable.'
            },
            {
                'usuario': users[1],
                'nivel': nivel2,
                'resultado': 'OBSERVACIONES',
                'comentario': 'Se requieren aclaraciones adicionales sobre los ingresos del cliente. Recomiendo solicitar estados de cuenta de los últimos 6 meses antes de proceder con la aprobación final.'
            }
        ]
        
        # Delete existing participations for this solicitud to avoid duplicates
        ParticipacionComite.objects.filter(solicitud=solicitud).delete()
        
        for data in participaciones_data:
            participacion = ParticipacionComite.objects.create(
                solicitud=solicitud,
                usuario=data['usuario'],
                nivel=data['nivel'],
                resultado=data['resultado'],
                comentario=data['comentario']
            )
            print(f"✅ Participación creada: {data['usuario'].username} - {data['resultado']}")
        
        print(f"✅ Datos de prueba del comité configurados exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando datos de prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 Configurando datos de prueba del comité...")
    print("=" * 60)
    
    success = setup_test_committee_data()
    
    print("=" * 60)
    
    if success:
        print("✅ Configuración completada exitosamente")
        print("\n📋 Ahora puedes probar el PDF resultado comité con datos reales:")
        print("  1. El PDF incluirá las participaciones del comité")
        print("  2. Cada nivel aparecerá con sus respectivos participantes")
        print("  3. Se mostrarán los resultados y comentarios de cada uno")
        print("\n🧪 Para probar, ejecuta: python3 test_pdf_comite.py")
    else:
        print("❌ Error en la configuración")
