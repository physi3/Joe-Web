from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from ..models import Service, UserServiceAccess

class JoeLoginView(LoginView):
    def get_redirect_url(self):
        next_url = self.request.GET.get('next', None)
        
        if next_url:
            return next_url
        
        return super().get_redirect_url()  # Fallback to default URL

def auth(request, service):
    body = {}

    if request.user.is_authenticated:
        user = request.user
        body["username"] = user.username
    else:
        return JsonResponse({"error": "Not logged in"}, status=401)

    try:
        serviceObject = Service.objects.get(name__iexact=service)
        body["service"] = serviceObject.name
        
    except Service.DoesNotExist:
        return JsonResponse({"error": "Invalid service"}, status=400)

    body["authorized"] = user.is_superuser or UserServiceAccess.objects.filter(user=request.user, service=serviceObject).exists()
    statusCode = 200 if body["authorized"] else 403
    return JsonResponse(body, status = statusCode)
