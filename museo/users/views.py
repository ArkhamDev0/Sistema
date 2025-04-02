from django.shortcuts import render, redirect, get_object_or_404  
from django.contrib.auth import authenticate, login, logout  
from django.contrib import messages  
from django.contrib.auth.decorators import login_required  
from .models import CustomUser  # Cambiado a CustomUser  

def login_view(request):  
    if request.method == 'POST':  
        username = request.POST['username']  
        password = request.POST['password']  
        user = authenticate(request, username=username, password=password)  
        if user is not None:  
            login(request, user)  
            return redirect('visitor_list')  # Cambiar a la lista de visitantes al inicio  
        else:  
            messages.error(request, "Usuario o contraseña incorrectos.")  
    return render(request, 'login.html')  

def logout_view(request):  
    logout(request)  
    return redirect('login')  # Asegúrate de que 'login' esté definido en tus URLs  

# Vista para el panel de administración  
@login_required  
def admin_dashboard(request):  
    if not request.user.is_admin:  
        messages.error(request, "No tienes permiso para acceder a esta página.")  
        return redirect('visitor_list')  # Redirige a la lista de visitantes si no es admin  

    users = CustomUser.objects.all()  # Obtener todos los usuarios  
    return render(request, 'dj/admin_dashboard.html', {'users': users})  

# Vista para editar un usuario  
@login_required  
def editar_usuario(request, user_id):  
    if not request.user.is_admin:  
        messages.error(request, "No tienes permiso para editar usuarios.")  
        return redirect('visitor_list')  # Redirigir a la lista de visitantes si no es admin  

    user = get_object_or_404(CustomUser, id=user_id)  # Obtener el usuario que se va a editar  

    if request.method == 'POST':  
        new_password = request.POST.get('password', None)  # Obtener la nueva contraseña  
        is_admin = request.POST.get('is_admin') == 'on'  # Cambiar a is_admin, solo se manda si está marcado  

        # Si se proporciona una nueva contraseña, cambiarla  
        if new_password:  
            user.set_password(new_password)  
        
        user.is_admin = is_admin  # Actualizar el estado de admin  
        user.save()  # Guardar cambios en el usuario  

        messages.success(request, "Usuario actualizado exitosamente.")  
        return redirect('admin_dashboard')  # Redirigir de nuevo al dashboard  

    return render(request, 'dj/editar_usuario.html', {'user': user})  # Mostrar el formulario de edición  

@login_required  
def crear_usuario(request):  
    if not request.user.is_admin:  
        messages.error(request, "No tienes permiso para crear usuarios.")  
        return redirect('visitor_list')  # Redirigir si no es admin  

    if request.method == 'POST':  
        username = request.POST['username']  
        password = request.POST['password']  
        
        # Crear el nuevo usuario  
        if username and password:  
            user = CustomUser(username=username)  
            user.set_password(password)  
            user.is_admin = False  # O lo que desees por defecto  
            user.save()  
            messages.success(request, "Usuario creado exitosamente.")  
            return redirect('admin_dashboard')  # Redirigir al dashboard  
        else:  
            messages.error(request, "Por favor, completa todos los campos.")  

    return render(request, 'dj/crear_usuario.html')  # Renderiza el formulario de creación