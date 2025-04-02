# usuarios/middleware.py  
from django.http import HttpResponseForbidden  
from django.urls import reverse  

class RestrictAdminMiddleware:  
    def __init__(self, get_response):  
        self.get_response = get_response  

    def __call__(self, request):  
        # Verifica si la ruta es la del admin  
        if request.path.startswith(reverse('admin:index')):  
            # Permite el acceso a los superusuarios  
            if not request.user.is_authenticated or not request.user.is_superuser:  
                return HttpResponseForbidden("Acceso restringido a administradores")  
        return self.get_response(request)  