from django.shortcuts import render
from django.db.models import Count, Q
from .models import Visita
import datetime
from django.core.paginator import Paginator

def visitantes_estadisticas(request):
    """Muestra estadísticas de visitantes con filtros, paginación y reinicio de formularios."""

    # Inicializar filtros
    fecha = request.GET.get('fecha')
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    edad = request.GET.get('edad')
    empresa = request.GET.get('empresa')
    es_extranjero = request.GET.get('es_extranjero')

    # Diccionario para mapear números de mes a nombres
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    # Construir filtros Q para consultas complejas
    filtros = Q()
    if fecha:
        filtros &= Q(fecha_visita=fecha)
    if mes:
        filtros &= Q(fecha_visita__month=mes)
    if anio:
        filtros &= Q(fecha_visita__year=anio)
    if edad:
        filtros &= Q(visitante__edad=edad)
    if empresa:
        filtros &= Q(visitante__empresa=empresa == 'si')  # ajusta segun sea el caso de tu variable empresa
    if es_extranjero:
        filtros &= Q(visitante__es_extranjero=es_extranjero == 'si')  # ajusta segun sea el caso de tu variable es_extranjero

    # Aplicar filtros a las consultas
    visitas = Visita.objects.filter(filtros)

    # Inicializar variables para el contexto
    data = []
    page_obj = None
    venezolanos_count = 0
    extranjeros_count = 0
    total_visitantes = 0
    mensaje = None

    # Solo calcular datos si se aplican filtros
    if filtros != Q():
        # Paginación
        paginator = Paginator(visitas, 10)  # Mostrar 10 visitantes por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Estadísticas por fecha, edad y empresa
        visitantes_unicos = set()
        for v in page_obj:
            if v.visitante not in visitantes_unicos:
                visitantes_unicos.add(v.visitante)

                # Contar el número de visitas por visitante dentro del rango de filtros
                visitas_count = visitas.filter(visitante=v.visitante).count()

                if v.visitante.empresa:
                    empresa_nombre = v.visitante.nombre_empresa
                else:
                    empresa_nombre = "No aplica"
                fecha_formateada = v.fecha_visita.strftime('%d de %B de %Y')
                data.append({
                    'nombre': v.visitante.nombre,
                    'apellido': v.visitante.apellido,
                    'documento': v.visitante.documento,
                    'fecha': fecha_formateada,
                    'edad': v.visitante.edad,
                    'empresa': empresa_nombre,
                })
                if visitas_count > 0:
                    data[-1]['visitas_count'] = visitas_count

        # Estadísticas por tipo de documento (venezolanos y extranjeros)
        venezolanos_count = visitas.filter(visitante__es_extranjero=False).distinct('visitante').count()
        extranjeros_count = visitas.filter(visitante__es_extranjero=True).distinct('visitante').count()
        total_visitantes = venezolanos_count + extranjeros_count

        # Generar mensajes
        if data:
            mensaje = "Se encontraron visitantes con los datos que incluiste en los formularios."
        else:
            if fecha:
                mensaje = "No hay visitantes para mostrar en la fecha especificada."
            elif mes:
                mensaje = "No hay visitantes para mostrar en el mes especificado."
            elif anio:
                mensaje = "No hay visitantes para mostrar en el año especificado."
            elif edad:
                mensaje = "No hay visitantes para mostrar con la edad especificada."
            elif empresa:
                mensaje = "No hay visitantes para mostrar con la empresa especificada."
            elif es_extranjero:
                mensaje = "No hay visitantes para mostrar con el tipo de documento especificado."
            else:
                mensaje = "No se encontraron visitantes con los filtros especificados."
    else:
        mensaje = "Aplica un filtro para ver los resultados."

    context = {
        'data': data,
        'fecha': fecha,
        'mes': mes,
        'anio': anio,
        'edad': edad,
        'empresa': empresa,
        'es_extranjero': es_extranjero,
        'meses': meses,
        'mensaje': mensaje,
        'page_obj': page_obj,
        'venezolanos_count': venezolanos_count,
        'extranjeros_count': extranjeros_count,
        'total_visitantes': total_visitantes,
    }
    return render(request, 'dj/visitantes_estadisticas.html', context)