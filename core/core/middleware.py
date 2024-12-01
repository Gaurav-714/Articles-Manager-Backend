from django.http import JsonResponse

class CustomTrailingSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.endswith('/') and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return JsonResponse({"error": "URL must end with a trailing slash for this method."}, status=400)
        
        return self.get_response(request)
