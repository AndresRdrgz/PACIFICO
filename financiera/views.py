"""
Custom error views for the Pacifico application
"""
from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.utils import timezone
import traceback
import sys


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
