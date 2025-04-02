from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
import pytz

# Vista de inicio de sesión
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Obtener la hora actual en la zona horaria local de Venezuela
            venezuela_tz = pytz.timezone('America/Caracas')
            now = timezone.now()
            current_time = now.astimezone(venezuela_tz)

            # Establecer horarios de actividad permitidos (8 AM a 6 PM)
            start_time = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
            end_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)

            # Verificar si la hora actual está dentro del rango permitido
            if start_time <= current_time <= end_time:
                request.session.set_expiry(36000)  # 10 horas en segundos (36000 segundos)
                return redirect('visitor_list')  # Redirige al listado de visitantes
            else:
                messages.error(request, 'Las sesiones solo pueden iniciarse entre las 8 AM y 6 PM.')
                logout(request)
                return redirect('login')

        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

    return render(request, 'login.html')  # Renderiza la plantilla de login

# Vista de cierre de sesión
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    response = redirect('login')
    return response  # Redirige a la página de inicio de sesión