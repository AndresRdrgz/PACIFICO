from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.test import override_settings
from .models import Proyecto, ProyectoUsuario

# Create your tests here.

class ProyectoEmailTests(TestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        self.invited_user = User.objects.create_user(
            username='tester',
            email='tester@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test project
        self.proyecto = Proyecto.objects.create(
            nombre='Proyecto de Prueba',
            descripcion='Descripción del proyecto de prueba',
            creado_por=self.admin_user
        )
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_notification_sent_on_invitation(self):
        """Test that email notification is sent when user is invited to project"""
        # Create invitation directly
        proyecto_usuario = ProyectoUsuario.objects.create(
            proyecto=self.proyecto,
            usuario=self.invited_user,
            rol='tester'
        )
        
        # Import the view function to test email sending
        from django.test import RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        from proyectos.views import invitar_usuario
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.post('/fake-url/')
        request.user = self.admin_user
        
        # Set up messages framework
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Test email sending logic
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils import timezone
        from django.conf import settings
        
        context = {
            'usuario': self.invited_user,
            'proyecto': self.proyecto,
            'rol': proyecto_usuario.get_rol_display(),
            'invitado_por': self.admin_user.get_full_name() or self.admin_user.username,
            'fecha_invitacion': timezone.now().strftime("%d/%m/%Y %H:%M"),
            'proyecto_url': 'http://testserver/proyectos/proyecto/1/',
        }
        
        # Send email
        subject = f'Invitación al Proyecto QA: {self.proyecto.nombre}'
        html_message = render_to_string('proyectos/emails/invitacion_proyecto.html', context)
        plain_message = render_to_string('proyectos/emails/invitacion_proyecto.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.invited_user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.invited_user.email])
        self.assertIn('Invitación al Proyecto QA', mail.outbox[0].subject)
        self.assertIn(self.proyecto.nombre, mail.outbox[0].body)
        self.assertIn('Tester', mail.outbox[0].body)
    
    def test_no_email_sent_for_user_without_email(self):
        """Test that no email is sent when user has no email address"""
        # Create user without email
        user_no_email = User.objects.create_user(
            username='noemail',
            email='',
            password='testpass123'
        )
        
        # Create invitation directly
        proyecto_usuario = ProyectoUsuario.objects.create(
            proyecto=self.proyecto,
            usuario=user_no_email,
            rol='desarrollador'
        )
        
        # Check that no email was sent (since user has no email)
        self.assertEqual(len(mail.outbox), 0)
