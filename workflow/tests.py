from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
import json
import tempfile
import os

from .modelsWorkflow import (
    Pipeline, Etapa, TransicionEtapa, Solicitud, Requisito, 
    RequisitoPipeline, RequisitoSolicitud, RequisitoTransicion
)


class RequirementValidationSystemTest(TestCase):
    """Test suite for the requirement validation system"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test group
        self.group = Group.objects.create(name='Test Group')
        self.user.groups.add(self.group)
        
        # Create test pipeline
        self.pipeline = Pipeline.objects.create(
            nombre='Consulta de Préstamo',
            descripcion='Pipeline para consultas de préstamo'
        )
        
        # Create test stages
        self.etapa_revision = Etapa.objects.create(
            pipeline=self.pipeline,
            nombre='Revisión de Documentos',
            orden=1,
            sla=timedelta(hours=24),
            es_bandeja_grupal=False
        )
        
        self.etapa_consulta = Etapa.objects.create(
            pipeline=self.pipeline,
            nombre='Enviar a Consulta',
            orden=2,
            sla=timedelta(hours=48),
            es_bandeja_grupal=False
        )
        
        # Create test requirements
        self.requisito_historial = Requisito.objects.create(
            nombre='Historial Crediticio',
            descripcion='Historial crediticio del cliente'
        )
        
        self.requisito_cotizacion = Requisito.objects.create(
            nombre='Cotización',
            descripcion='Cotización del préstamo'
        )
        
        self.requisito_cedula = Requisito.objects.create(
            nombre='Cédula',
            descripcion='Cédula de identidad del cliente'
        )
        
        # Create transition
        self.transicion = TransicionEtapa.objects.create(
            pipeline=self.pipeline,
            etapa_origen=self.etapa_revision,
            etapa_destino=self.etapa_consulta,
            nombre='Enviar a Consulta',
            requiere_permiso=False
        )
        
        # Create requirement transition rules
        self.req_trans_historial = RequisitoTransicion.objects.create(
            transicion=self.transicion,
            requisito=self.requisito_historial,
            obligatorio=True,
            mensaje_personalizado='El historial crediticio es obligatorio para continuar'
        )
        
        self.req_trans_cotizacion = RequisitoTransicion.objects.create(
            transicion=self.transicion,
            requisito=self.requisito_cotizacion,
            obligatorio=True,
            mensaje_personalizado='La cotización es obligatoria para continuar'
        )
        
        self.req_trans_cedula = RequisitoTransicion.objects.create(
            transicion=self.transicion,
            requisito=self.requisito_cedula,
            obligatorio=False,  # Optional requirement
            mensaje_personalizado='La cédula es opcional pero recomendada'
        )
        
        # Create test request
        self.solicitud = Solicitud.objects.create(
            codigo='TEST-001',
            pipeline=self.pipeline,
            etapa_actual=self.etapa_revision,
            creada_por=self.user,
            asignada_a=self.user
        )
        
        # Set up client
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_requirement_transition_model_creation(self):
        """Test that RequisitoTransicion model works correctly"""
        self.assertEqual(self.req_trans_historial.transicion, self.transicion)
        self.assertEqual(self.req_trans_historial.requisito, self.requisito_historial)
        self.assertTrue(self.req_trans_historial.obligatorio)
        self.assertEqual(
            self.req_trans_historial.mensaje_personalizado,
            'El historial crediticio es obligatorio para continuar'
        )
    
    def test_verificar_requisitos_transicion_function(self):
        """Test the verificar_requisitos_transicion function"""
        from .views_workflow import verificar_requisitos_transicion
        
        # Test with no requirements fulfilled
        requisitos_faltantes = verificar_requisitos_transicion(self.solicitud, self.transicion)
        
        # Should return 2 missing requirements (historial and cotizacion are mandatory)
        self.assertEqual(len(requisitos_faltantes), 2)
        
        # Check that mandatory requirements are in the list
        req_names = [req['nombre'] for req in requisitos_faltantes]
        self.assertIn('Historial Crediticio', req_names)
        self.assertIn('Cotización', req_names)
        self.assertNotIn('Cédula', req_names)  # Optional requirement
        
        # Test with some requirements fulfilled
        RequisitoSolicitud.objects.create(
            solicitud=self.solicitud,
            requisito=self.requisito_historial,
            cumplido=True,
            archivo=SimpleUploadedFile("test.pdf", b"file_content")
        )
        
        requisitos_faltantes = verificar_requisitos_transicion(self.solicitud, self.transicion)
        
        # Should return 1 missing requirement (cotizacion)
        self.assertEqual(len(requisitos_faltantes), 1)
        self.assertEqual(requisitos_faltantes[0]['nombre'], 'Cotización')
    
    def test_api_obtener_requisitos_transicion(self):
        """Test the API endpoint for getting transition requirements"""
        url = reverse('workflow:api_obtener_requisitos_transicion', args=[self.solicitud.id])
        response = self.client.get(url, {'nueva_etapa_id': self.etapa_consulta.id})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(len(data['requisitos_faltantes']), 2)
        self.assertEqual(data['total_faltantes'], 2)
        
        # Check transition info
        self.assertEqual(data['transicion']['nombre'], 'Enviar a Consulta')
        self.assertEqual(data['transicion']['etapa_origen'], 'Revisión de Documentos')
        self.assertEqual(data['transicion']['etapa_destino'], 'Enviar a Consulta')
    
    def test_api_subir_requisito_transicion(self):
        """Test the API endpoint for uploading requirement files"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'test file content')
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as file:
                url = reverse('workflow:api_subir_requisito_transicion', args=[self.solicitud.id])
                response = self.client.post(url, {
                    'requisito_id': self.requisito_historial.id,
                    'archivo': file
                })
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            
            self.assertTrue(data['success'])
            self.assertIn('subido exitosamente', data['mensaje'])
            
            # Check that the requirement was created/updated
            req_solicitud = RequisitoSolicitud.objects.get(
                solicitud=self.solicitud,
                requisito=self.requisito_historial
            )
            self.assertTrue(req_solicitud.cumplido)
            self.assertIsNotNone(req_solicitud.archivo)
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_api_validar_requisitos_antes_transicion(self):
        """Test the API endpoint for validating requirements before transition"""
        url = reverse('workflow:api_validar_requisitos_antes_transicion', args=[self.solicitud.id])
        response = self.client.get(url, {'nueva_etapa_id': self.etapa_consulta.id})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertFalse(data['puede_continuar'])  # Should not be able to continue
        self.assertEqual(data['total_faltantes'], 2)
        self.assertIn('Faltan 2 requisito(s)', data['mensaje'])
        
        # Fulfill one requirement
        RequisitoSolicitud.objects.create(
            solicitud=self.solicitud,
            requisito=self.requisito_historial,
            cumplido=True,
            archivo=SimpleUploadedFile("test.pdf", b"file_content")
        )
        
        response = self.client.get(url, {'nueva_etapa_id': self.etapa_consulta.id})
        data = json.loads(response.content)
        
        self.assertFalse(data['puede_continuar'])  # Still missing one requirement
        self.assertEqual(data['total_faltantes'], 1)
        
        # Fulfill all mandatory requirements
        RequisitoSolicitud.objects.create(
            solicitud=self.solicitud,
            requisito=self.requisito_cotizacion,
            cumplido=True,
            archivo=SimpleUploadedFile("test2.pdf", b"file_content")
        )
        
        response = self.client.get(url, {'nueva_etapa_id': self.etapa_consulta.id})
        data = json.loads(response.content)
        
        self.assertTrue(data['puede_continuar'])  # Should be able to continue
        self.assertEqual(data['total_faltantes'], 0)
        self.assertIn('Todos los requisitos están completos', data['mensaje'])
    
    def test_api_cambiar_etapa_with_requirements(self):
        """Test that stage change API respects requirement validation"""
        url = reverse('workflow:api_cambiar_etapa', args=[self.solicitud.id])
        
        # Try to change stage without fulfilling requirements
        response = self.client.post(url, {
            'etapa_id': self.etapa_consulta.id,
            'comentario': 'Intentando cambiar sin requisitos'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('requisitos', data['error'].lower())
        
        # Fulfill requirements and try again
        RequisitoSolicitud.objects.create(
            solicitud=self.solicitud,
            requisito=self.requisito_historial,
            cumplido=True,
            archivo=SimpleUploadedFile("test.pdf", b"file_content")
        )
        
        RequisitoSolicitud.objects.create(
            solicitud=self.solicitud,
            requisito=self.requisito_cotizacion,
            cumplido=True,
            archivo=SimpleUploadedFile("test2.pdf", b"file_content")
        )
        
        response = self.client.post(url, {
            'etapa_id': self.etapa_consulta.id,
            'comentario': 'Cambiando con requisitos cumplidos'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify stage was changed
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.etapa_actual, self.etapa_consulta)
    
    def test_optional_requirements_not_blocking(self):
        """Test that optional requirements don't block transitions"""
        # Fulfill only mandatory requirements
        RequisitoSolicitud.objects.create(
            solicitud=self.solicitud,
            requisito=self.requisito_historial,
            cumplido=True,
            archivo=SimpleUploadedFile("test.pdf", b"file_content")
        )
        
        RequisitoSolicitud.objects.create(
            solicitud=self.solicitud,
            requisito=self.requisito_cotizacion,
            cumplido=True,
            archivo=SimpleUploadedFile("test2.pdf", b"file_content")
        )
        
        # Don't fulfill optional requirement (cedula)
        url = reverse('workflow:api_validar_requisitos_antes_transicion', args=[self.solicitud.id])
        response = self.client.get(url, {'nueva_etapa_id': self.etapa_consulta.id})
        
        data = json.loads(response.content)
        self.assertTrue(data['puede_continuar'])  # Should be able to continue
        self.assertEqual(data['total_faltantes'], 0)
    
    def test_permission_checks(self):
        """Test that permission checks work correctly"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        
        # Try to access with different user
        self.client.login(username='otheruser', password='testpass123')
        
        url = reverse('workflow:api_obtener_requisitos_transicion', args=[self.solicitud.id])
        response = self.client.get(url, {'nueva_etapa_id': self.etapa_consulta.id})
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertIn('permisos', data['error'].lower())
    
    def test_invalid_transition(self):
        """Test behavior when transition doesn't exist"""
        # Create a different stage
        otra_etapa = Etapa.objects.create(
            pipeline=self.pipeline,
            nombre='Otra Etapa',
            orden=3,
            sla=timedelta(hours=12)
        )
        
        url = reverse('workflow:api_obtener_requisitos_transicion', args=[self.solicitud.id])
        response = self.client.get(url, {'nueva_etapa_id': otra_etapa.id})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(len(data['requisitos_faltantes']), 0)
        self.assertIn('No hay requisitos especiales', data['mensaje'])
    
    def test_missing_parameters(self):
        """Test API behavior with missing parameters"""
        url = reverse('workflow:api_obtener_requisitos_transicion', args=[self.solicitud.id])
        response = self.client.get(url)  # Missing nueva_etapa_id
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('ID de nueva etapa requerido', data['error'])
    
    def test_file_upload_validation(self):
        """Test file upload validation"""
        url = reverse('workflow:api_subir_requisito_transicion', args=[self.solicitud.id])
        
        # Try to upload without file
        response = self.client.post(url, {
            'requisito_id': self.requisito_historial.id
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('No se proporcionó ningún archivo', data['error'])
        
        # Try to upload with invalid requisito_id
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'test file content')
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as file:
                response = self.client.post(url, {
                    'requisito_id': 99999,  # Non-existent ID
                    'archivo': file
                })
            
            self.assertEqual(response.status_code, 404)
            
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


class RequirementValidationIntegrationTest(TestCase):
    """Integration tests for the complete requirement validation workflow"""
    
    def setUp(self):
        """Set up integration test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create complete pipeline setup
        self.pipeline = Pipeline.objects.create(
            nombre='Préstamo Personal',
            descripcion='Pipeline completo para préstamos personales'
        )
        
        # Create multiple stages
        self.etapa_inicial = Etapa.objects.create(
            pipeline=self.pipeline,
            nombre='Solicitud Inicial',
            orden=1,
            sla=timedelta(hours=2)
        )
        
        self.etapa_revision = Etapa.objects.create(
            pipeline=self.pipeline,
            nombre='Revisión de Documentos',
            orden=2,
            sla=timedelta(hours=24)
        )
        
        self.etapa_aprobacion = Etapa.objects.create(
            pipeline=self.pipeline,
            nombre='Aprobación',
            orden=3,
            sla=timedelta(hours=48)
        )
        
        self.etapa_final = Etapa.objects.create(
            pipeline=self.pipeline,
            nombre='Finalización',
            orden=4,
            sla=timedelta(hours=12)
        )
        
        # Create requirements
        self.requisitos = {
            'cedula': Requisito.objects.create(nombre='Cédula', descripcion='Cédula de identidad'),
            'ingresos': Requisito.objects.create(nombre='Comprobante de Ingresos', descripcion='Comprobante de ingresos'),
            'referencias': Requisito.objects.create(nombre='Referencias Personales', descripcion='Referencias personales'),
            'garantia': Requisito.objects.create(nombre='Garantía', descripcion='Documento de garantía'),
            'contrato': Requisito.objects.create(nombre='Contrato', descripcion='Contrato de préstamo')
        }
        
        # Create transitions with requirements
        self.transiciones = {}
        
        # Initial to Review
        self.transiciones['inicial_revision'] = TransicionEtapa.objects.create(
            pipeline=self.pipeline,
            etapa_origen=self.etapa_inicial,
            etapa_destino=self.etapa_revision,
            nombre='Enviar a Revisión'
        )
        
        # Review to Approval
        self.transiciones['revision_aprobacion'] = TransicionEtapa.objects.create(
            pipeline=self.pipeline,
            etapa_origen=self.etapa_revision,
            etapa_destino=self.etapa_aprobacion,
            nombre='Enviar a Aprobación'
        )
        
        # Approval to Final
        self.transiciones['aprobacion_final'] = TransicionEtapa.objects.create(
            pipeline=self.pipeline,
            etapa_origen=self.etapa_aprobacion,
            etapa_destino=self.etapa_final,
            nombre='Finalizar'
        )
        
        # Set up requirement rules for each transition
        # Initial to Review: Only cédula required
        RequisitoTransicion.objects.create(
            transicion=self.transiciones['inicial_revision'],
            requisito=self.requisitos['cedula'],
            obligatorio=True
        )
        
        # Review to Approval: cédula, ingresos, referencias required
        for req_name in ['cedula', 'ingresos', 'referencias']:
            RequisitoTransicion.objects.create(
                transicion=self.transiciones['revision_aprobacion'],
                requisito=self.requisitos[req_name],
                obligatorio=True
            )
        
        # Approval to Final: garantia and contrato required
        for req_name in ['garantia', 'contrato']:
            RequisitoTransicion.objects.create(
                transicion=self.transiciones['aprobacion_final'],
                requisito=self.requisitos[req_name],
                obligatorio=True
            )
        
        # Create test request
        self.solicitud = Solicitud.objects.create(
            codigo='INTEGRATION-001',
            pipeline=self.pipeline,
            etapa_actual=self.etapa_inicial,
            creada_por=self.user,
            asignada_a=self.user
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_complete_workflow_with_requirements(self):
        """Test the complete workflow with requirement validation at each step"""
        from .views_workflow import verificar_requisitos_transicion
        
        # Step 1: Initial to Review (only cédula required)
        # Check requirements for this transition
        req_faltantes = verificar_requisitos_transicion(
            self.solicitud, 
            self.transiciones['inicial_revision']
        )
        self.assertEqual(len(req_faltantes), 1)
        self.assertEqual(req_faltantes[0]['nombre'], 'Cédula')
        
        # Upload cédula
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'cedula content')
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as file:
                url = reverse('workflow:api_subir_requisito_transicion', args=[self.solicitud.id])
                response = self.client.post(url, {
                    'requisito_id': self.requisitos['cedula'].id,
                    'archivo': file
                })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify requirement is fulfilled
            req_solicitud = RequisitoSolicitud.objects.get(
                solicitud=self.solicitud,
                requisito=self.requisitos['cedula']
            )
            self.assertTrue(req_solicitud.cumplido)
            
            # Change to review stage
            url = reverse('workflow:api_cambiar_etapa', args=[self.solicitud.id])
            response = self.client.post(url, {
                'etapa_id': self.etapa_revision.id,
                'comentario': 'Avanzando a revisión'
            }, content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            self.solicitud.refresh_from_db()
            self.assertEqual(self.solicitud.etapa_actual, self.etapa_revision)
            
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
        
        # Step 2: Review to Approval (cédula, ingresos, referencias required)
        # Check requirements for this transition
        req_faltantes = verificar_requisitos_transicion(
            self.solicitud, 
            self.transiciones['revision_aprobacion']
        )
        self.assertEqual(len(req_faltantes), 2)  # ingresos and referencias missing
        
        # Upload missing requirements
        for req_name in ['ingresos', 'referencias']:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(f'{req_name} content'.encode())
                tmp_file_path = tmp_file.name
            
            try:
                with open(tmp_file_path, 'rb') as file:
                    url = reverse('workflow:api_subir_requisito_transicion', args=[self.solicitud.id])
                    response = self.client.post(url, {
                        'requisito_id': self.requisitos[req_name].id,
                        'archivo': file
                    })
                
                self.assertEqual(response.status_code, 200)
                
            finally:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
        
        # Verify all requirements are fulfilled
        req_faltantes = verificar_requisitos_transicion(
            self.solicitud, 
            self.transiciones['revision_aprobacion']
        )
        self.assertEqual(len(req_faltantes), 0)
        
        # Change to approval stage
        url = reverse('workflow:api_cambiar_etapa', args=[self.solicitud.id])
        response = self.client.post(url, {
            'etapa_id': self.etapa_aprobacion.id,
            'comentario': 'Avanzando a aprobación'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.etapa_actual, self.etapa_aprobacion)
        
        # Step 3: Approval to Final (garantia and contrato required)
        # Check requirements for this transition
        req_faltantes = verificar_requisitos_transicion(
            self.solicitud, 
            self.transiciones['aprobacion_final']
        )
        self.assertEqual(len(req_faltantes), 2)  # garantia and contrato missing
        
        # Upload missing requirements
        for req_name in ['garantia', 'contrato']:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(f'{req_name} content'.encode())
                tmp_file_path = tmp_file.name
            
            try:
                with open(tmp_file_path, 'rb') as file:
                    url = reverse('workflow:api_subir_requisito_transicion', args=[self.solicitud.id])
                    response = self.client.post(url, {
                        'requisito_id': self.requisitos[req_name].id,
                        'archivo': file
                    })
                
                self.assertEqual(response.status_code, 200)
                
            finally:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
        
        # Verify all requirements are fulfilled
        req_faltantes = verificar_requisitos_transicion(
            self.solicitud, 
            self.transiciones['aprobacion_final']
        )
        self.assertEqual(len(req_faltantes), 0)
        
        # Change to final stage
        url = reverse('workflow:api_cambiar_etapa', args=[self.solicitud.id])
        response = self.client.post(url, {
            'etapa_id': self.etapa_final.id,
            'comentario': 'Finalizando proceso'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.etapa_actual, self.etapa_final)
        
        # Verify all requirements are properly stored
        total_requirements = RequisitoSolicitud.objects.filter(solicitud=self.solicitud).count()
        self.assertEqual(total_requirements, 5)  # All 5 requirements should be stored
        
        fulfilled_requirements = RequisitoSolicitud.objects.filter(
            solicitud=self.solicitud,
            cumplido=True
        ).count()
        self.assertEqual(fulfilled_requirements, 5)  # All should be fulfilled
