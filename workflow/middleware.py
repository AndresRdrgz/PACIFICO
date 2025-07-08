class PWAMiddleware:
    """
    Middleware to add PWA-specific headers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add PWA-specific headers
        if request.path.startswith('/workflow/'):
            # Enable service worker for workflow paths
            response['Service-Worker-Allowed'] = '/workflow/'
            
            # Cache control for PWA resources
            if request.path.endswith('sw.js'):
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
            elif request.path.endswith('manifest.json'):
                response['Cache-Control'] = 'public, max-age=86400'
            elif '/static/workflow/icons/' in request.path:
                response['Cache-Control'] = 'public, max-age=31536000'
                
        return response 