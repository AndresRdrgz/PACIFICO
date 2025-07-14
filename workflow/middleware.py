import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class APIResponseMiddleware:
    """
    Middleware to ensure API endpoints return JSON responses
    even for authentication errors
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is an API request
        is_api_request = (
            request.path.startswith('/workflow/api/') or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Content-Type', '').startswith('application/json')
        )
        
        # Process request
        response = self.get_response(request)
        
        # If it's an API request and response is not JSON, try to convert
        if is_api_request and not response.get('Content-Type', '').startswith('application/json'):
            # Check if response is an HTML error page
            if response.status_code >= 400:
                return JsonResponse({
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'code': 'HTTP_ERROR'
                }, status=response.status_code)
        
        return response

class PWAMiddleware:
    """
    Middleware to add PWA-specific headers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add PWA headers
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-Content-Type-Options'] = 'nosniff'
        
        return response 