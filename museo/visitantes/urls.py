from django.urls import path
from django.views.generic import RedirectView
from .views import (
    login_view,
    logout_view,
)

from .visitor_views import (
    visitor_list,
    visitor_create,
    buscar_visitante,
    crear_visita,  # Importa la nueva función
)

from .cita_views import (
    agregar_cita,
    listar_citas,
    reagendar_cita,
)

from .statistics_views import (
    visitantes_estadisticas,
)

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # URLs originales (se mantienen para compatibilidad)
    path('visitors/', visitor_list, name='visitor_list'),
    path('visitors/new/', visitor_create, name='visitor_create'),
    
    # URLs de citas (se mantienen igual)
    path('agregar_cita/', agregar_cita, name='agregar_cita'),
    path('buscar_visitante/', buscar_visitante, name='buscar_visitante'),
    path('citas/', listar_citas, name='listar_citas'),
    path('citas/reagendar/<int:pk>/', reagendar_cita, name='reagendar_cita'),
    
    # Estadísticas
    path('estadisticas/', visitantes_estadisticas, name='visitantes_estadisticas'),
    
    # URL para crear visita
    path('crear_visita/', crear_visita, name='crear_visita'),
]
