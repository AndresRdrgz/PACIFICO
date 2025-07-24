"""
Custom error views for the Pacifico application
"""
import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError, Http404, HttpResponse
from django.template import loader
from django.utils import timezone
import traceback
import sys
from django.views.static import serve
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View


def custom_404_view(request, exception=None):
    """
    Custom 404 error view
    """
    template = loader.get_template('404.html')
    context = {
        'request': request,
        'exception': exception,
        'timestamp': timezone.now(),
    }
    
    return HttpResponseNotFound(template.render(context, request))


def custom_500_view(request):
    """
    Custom 500 error view with detailed error information for internal use
    """
    template = loader.get_template('500.html')
    
    # Get exception information if available
    exception_type = None
    exception_value = None
    exception_traceback = None
    
    if sys.exc_info()[0] is not None:
        exception_type, exception_value, exception_traceback = sys.exc_info()
    
    # Format traceback for display
    traceback_text = ""
    if exception_traceback:
        traceback_text = ''.join(traceback.format_exception(
            exception_type, exception_value, exception_traceback
        ))
    
    context = {
        'request': request,
        'exception': exception_value,
        'exception_type': exception_type.__name__ if exception_type else None,
        'exception_value': str(exception_value) if exception_value else None,
        'traceback': traceback_text,
        'timestamp': timezone.now(),
    }
    
    return HttpResponseServerError(template.render(context, request))


class SecureMediaView(View):
    """
    Custom view for serving media files with additional security checks
    """
    
    def get(self, request, path):
        # Check if the file exists
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        
        if not os.path.exists(file_path):
            raise Http404("File not found")
        
        # Additional security checks for production
        if not settings.DEBUG:
            # Check file extension
            file_ext = path.split('.')[-1].lower()
            if file_ext not in getattr(settings, 'ALLOWED_MEDIA_EXTENSIONS', []):
                raise Http404("File type not allowed")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > getattr(settings, 'MEDIA_FILES_MAX_SIZE', 50 * 1024 * 1024):
                raise Http404("File too large")
        
        # Serve the file
        return serve(request, path, document_root=settings.MEDIA_ROOT)
