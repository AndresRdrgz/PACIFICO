from pathlib import Path
import os
import dj_database_url
 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'

# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = False
if DEBUG:
   DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default='postgresql://postgres:FP.h05t1l3@localhost:5432/pacifico',
            conn_max_age=600
        )
    }

'''PARAMETROS POSTGRE
DEBUG = True
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default='postgresql://postgres:FP.h05t1l3@localhost:5432/pacifico',
            conn_max_age=600
        )
    }
'''
'''PARAMETROS POSTGRE
else:
    DATABASES = {
        'default': dj_database_url.config(
            default='postgresql://postgres:FP.h05t1l3@localhost:5432/pacifico',
            conn_max_age=600
        )
    }

'''

''' COMENTARIO ANDRES - UTILIZAR ESTE BLOQUE PARA DESPLIEGUE EN WEBSERVER PACIFICO
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'pacifico',
            'USER': 'pacifico',
            'PASSWORD': 'jKd5sDLNRiHzrPb7',
            'HOST': 'localhost',
            'PORT': '3306'
        }
    }
'''
''' COMENTARIO ANDRES - UTILIZAR ESTE BLOQUE PARA DESPLIEGUE EN RENDER (PRUEBAS)
else:
    DATABASES = {
        'default': dj_database_url.config(
            default='postgresql://postgres:postgres@localhost:5432/pacifico',
            conn_max_age=600
        )
    }
'''

# Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
# and renames the files with unique names for each version to support long-term caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure media directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Media file security settings for production
if not DEBUG:
    # In production, consider additional security for media files
    # Maximum file size for uploads (50MB)
    FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
    DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
    
    # File upload permissions
    #FILE_UPLOAD_PERMISSIONS = 0o644
    #FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

X_FRAME_OPTIONS = 'SAMEORIGIN'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'static/insumos'),
    os.path.join(BASE_DIR, 'static/images'),
]

EXCEL_FILE_PATH = os.path.join(BASE_DIR, 'financiera/pacifico/fideicomiso/patronos.xlsx')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-gy#*57bwnd=06f*jup!b=a15%=3yclx0^x&$+oytscnhs!hf2_"

ALLOWED_HOSTS = ["*"]
# ALLOWED_HOSTS = ['cotfid.fpacifico.com']

'''PARAMETROS SSL
SECURE_SSL_REDIRECT = True  # Comentario o elimina esta línea temporalmente
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = ['cotfid.fpacifico.com', 'www.cotfid.fpacifico.com']

'''

# PWA Configuration
PWA_APP_NAME = 'Pacífico Workflow'
PWA_APP_DESCRIPTION = 'Sistema de Workflow - Financiera Pacífico'
PWA_APP_THEME_COLOR = '#009c3c'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/workflow/'
PWA_APP_START_URL = '/workflow/'
PWA_APP_ICONS = [
    {
        'src': '/static/workflow/icons/icon-72x72.png',
        'sizes': '72x72',
        'type': 'image/png'
    },
    {
        'src': '/static/workflow/icons/icon-96x96.png',
        'sizes': '96x96',
        'type': 'image/png'
    },
    {
        'src': '/static/workflow/icons/icon-128x128.png',
        'sizes': '128x128',
        'type': 'image/png'
    },
    {
        'src': '/static/workflow/icons/icon-144x144.png',
        'sizes': '144x144',
        'type': 'image/png'
    },
    {
        'src': '/static/workflow/icons/icon-152x152.png',
        'sizes': '152x152',
        'type': 'image/png'
    },
    {
        'src': '/static/workflow/icons/icon-192x192.png',
        'sizes': '192x192',
        'type': 'image/png'
    },
    {
        'src': '/static/workflow/icons/icon-384x384.png',
        'sizes': '384x384',
        'type': 'image/png'
    },
    {
        'src': '/static/workflow/icons/icon-512x512.png',
        'sizes': '512x512',
        'type': 'image/png'
    }
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# Session configuration
SESSION_COOKIE_AGE = 60 * 60 * 8  # 8 hours
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on each request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Don't expire when browser closes
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'main_menu'
LOGOUT_REDIRECT_URL = 'login'



# Application definition
CSRF_TRUSTED_ORIGINS = [
    'https://cotfid.fpacifico.com',
    'http://cotfid.fpacifico.com',
    'http://localhost:8000',
    'http://cotfid.fpacifico.com:8000',
]

INSTALLED_APPS = [
    
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pacifico",
    "tombola",
    "capacitaciones_app",
    "nested_admin",
    "mantenimiento",
    "workflow",
    "widget_tweaks",
    "proyectos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "workflow.middleware.APIResponseMiddleware",  # Ensure API endpoints return JSON
    # Middleware personalizado para redirección de usuarios con rol "Usuario"
    "capacitaciones_app.middleware.user_redirect.UserRoleRedirectMiddleware",
    "workflow.middleware.PWAMiddleware",  # PWA-specific headers
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "financiera.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, 'templates'),  # Custom error templates
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "financiera.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases




# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Panama"

USE_I18N = True

USE_TZ = True

#configuracion de correo
EMAIL_BACKEND = 'workflow.email_backend.CustomSMTPEmailBackend'
EMAIL_HOST = 'mail.fpacifico.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'makito@fpacifico.com'  # Cuenta de autenticación que funciona
EMAIL_HOST_PASSWORD = 'aFihr73B'
EMAIL_DEBUG = True
DEFAULT_FROM_EMAIL = 'workflow@fpacifico.com'  # Remitente oficial de la aplicación

# Dynamic SITE_URL based on environment
if DEBUG:
    SITE_URL = 'http://localhost:8000'  # Development
else:
    # Production URLs - customize based on your deployment
    SITE_URL = 'https://cotfid.fpacifico.com'  # Production domain

# Custom error page settings
# In production (DEBUG=False), Django will use custom error templates
ADMINS = [
    ('Admin', 'admin@fpacifico.com'),
]

# Email settings for error notifications in production
if not DEBUG:
    MANAGERS = ADMINS
    # Server email for error notifications
    SERVER_EMAIL = 'noreply@fpacifico.com'

# SSL Context para manejar certificados autofirmados
import ssl
EMAIL_SSL_CONTEXT = ssl.create_default_context()
EMAIL_SSL_CONTEXT.check_hostname = False
EMAIL_SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# Configuración de respaldo para desarrollo (si el correo principal falla)
if DEBUG:
    # Configuración de respaldo para desarrollo
    EMAIL_BACKEND_FALLBACK = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_FROM_FALLBACK = 'workflow@fpacifico.com'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"