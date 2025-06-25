from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView
from django.contrib.auth.forms import PasswordResetForm
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

logger = logging.getLogger(__name__)

# Login view (uses Django's built-in view)
class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'

# Logout view
class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('login')

# Custom Password Reset Form
class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a custom branded email in Spanish
        """
        try:
            # Get user for personalization
            user = User.objects.get(email=to_email)
            
            # Prepare email context
            email_context = {
                'user': user,
                'domain': context['domain'],
                'protocol': context['protocol'],
                'uid': context['uid'],
                'token': context['token'],
                'site_name': 'Aplicación Web',
                'reset_url': f"{context['protocol']}://{context['domain']}/accounts/reset/{context['uid']}/{context['token']}/",
            }
            
            # Create the email content
            subject = '🔐 Solicitud de restablecimiento de contraseña - Aplicación Web'
            
            # HTML email template
            html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restablecimiento de Contraseña - Aplicación Web</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f8f9fa;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #22a650, #1e7e34);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: bold;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #22a650;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .message {{
            font-size: 16px;
            margin-bottom: 30px;
            line-height: 1.7;
        }}
        .reset-button {{
            text-align: center;
            margin: 30px 0;
        }}
        .reset-button a {{
            display: inline-block;
            background: linear-gradient(135deg, #22a650, #1e7e34);
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
        }}
        .info-box {{
            background-color: #e8f5e8;
            border-left: 4px solid #22a650;
            padding: 20px;
            margin: 25px 0;
            border-radius: 0 8px 8px 0;
        }}
        .security-note {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 6px 6px 0;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            border-top: 1px solid #dee2e6;
        }}
        .footer p {{
            margin: 5px 0;
            font-size: 14px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Restablecimiento de Contraseña</h1>
        </div>
        
        <div class="content">
            <div class="greeting">
                ¡Hola {user.get_full_name() or user.username}!
            </div>
            
            <div class="message">
                Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en nuestra aplicación web.
            </div>
            
            <div class="info-box">
                <h3>📋 Tu información de usuario:</h3>
                <p><strong>Usuario:</strong> {user.username}</p>
                <p><strong>Email:</strong> {user.email}</p>
            </div>
            
            <div class="message">
                Para crear una nueva contraseña, haz clic en el siguiente botón:
            </div>
            
            <div class="reset-button">
                <a href="{email_context['reset_url']}" style="color: white; text-decoration: none;">
                    🔑 Restablecer mi contraseña
                </a>
            </div>
            
            <div class="security-note">
                <p><strong>⚠️ Nota de seguridad:</strong> Este enlace expirará en 3 días por motivos de seguridad. Si no solicitaste este cambio, puedes ignorar este correo electrónico.</p>
            </div>
            
            <div class="message">
                Si tienes problemas para hacer clic en el botón, puedes copiar y pegar el siguiente enlace en tu navegador:
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; margin: 20px 0; word-break: break-all; font-family: monospace; font-size: 12px; color: #495057;">
                {email_context['reset_url']}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Equipo de Procesos</strong></p>
            <p>📧 Este correo fue enviado desde: {settings.EMAIL_HOST_USER}</p>
            <p>⚠️ Este es un correo automático, por favor no respondas a este mensaje.</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Send email
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[to_email],
                cc=['arodriguez@fpacifico.com', 'jacastillo@fpacifico.com'],
            )
            email.content_subtype = "html"  # Set email to HTML
            email.send(fail_silently=False)
            
            logger.info(f"Password reset email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False

# Custom Password Reset View
def custom_password_reset_view(request):
    from .ViewsLogin import CustomPasswordResetForm
    
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name=None,  # We handle email in form
                subject_template_name=None,
                html_email_template_name=None
            )
            return redirect('password_reset_done')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})

# Password Reset Done View
class CustomPasswordResetDoneView(TemplateView):
    template_name = 'registration/password_reset_done.html'

# Password Reset Confirm View
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CustomPasswordResetConfirmView(FormView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    
    def get_success_url(self):
        return reverse_lazy('password_reset_complete')
    
    def dispatch(self, *args, **kwargs):
        self.user = self.get_user(kwargs['uidb64'])
        self.token = kwargs['token']
        
        if self.user is not None:
            self.validlink = default_token_generator.check_token(self.user, self.token)
            if self.validlink:
                return super().dispatch(*args, **kwargs)
        
        self.validlink = False
        return self.render_to_response(self.get_context_data())
    
    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, '🎉 ¡Tu contraseña ha sido actualizada exitosamente!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validlink'] = self.validlink
        context['user'] = self.user
        return context

# Password Reset Complete View
class CustomPasswordResetCompleteView(TemplateView):
    template_name = 'registration/password_reset_complete.html'


def login_view(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print('user', user, username, password)
        if user is not None:
            login(request, user)
            return redirect('main_menu')  # Redirect to the main menu after successful login
        else:
            messages.error(request, 'Invalid username or password')
            print('Invalid username or password')
    return render(request, 'registration/login.html')
