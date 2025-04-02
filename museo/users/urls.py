from django.urls import path  
from .views import login_view, logout_view, admin_dashboard, editar_usuario, crear_usuario  # Asegúrate de que crear_usuario esté aquí  

urlpatterns = [  
    path('login/', login_view, name='login'),  
    path('logout/', logout_view, name='logout'),  
    path('admin/', admin_dashboard, name='admin_dashboard'),  
    path('editar_usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),  
    path('crear_usuario/', crear_usuario, name='crear_usuario'),  # Asegúrate que esta línea esté presente  
]  