from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from .models import Cita, Visita, Visitante
from .forms import VisitaForm
import logging
import re
from django.db import IntegrityError  # Importa IntegrityError
import pytz
import datetime  # Importa datetime

logger = logging.getLogger(__name__)

@login_required
def visitor_list(request):
    today = timezone.now().date()

    # Obtener los IDs de los visitantes que tienen citas para hoy
    visitantes_con_cita_ids = Cita.objects.filter(fecha=today).values_list('visitante_id', flat=True)

    # Actualizar el estado de las visitas que tienen visitantes con citas para hoy
    Visita.objects.filter(
        visitante_id__in=visitantes_con_cita_ids,
        fecha_visita=today,
        status='Pendiente'
    ).update(status='Visitante')

    # Obtener todas las visitas del día actual
    visitas = Visita.objects.filter(fecha_visita=today).order_by('fecha_visita')

    # Actualizar el estado de las visitas pendientes si es dentro del horario
    hora_actual = timezone.now().astimezone(pytz.timezone('America/Caracas')).time()  # Reemplaza 'America/Caracas' con tu zona horaria
    hora_inicio = datetime.time(8, 0)
    hora_fin = datetime.time(18, 0)

    if hora_inicio <= hora_actual <= hora_fin:
        Visita.objects.filter(fecha_visita=today, status='Pendiente').update(status='Visitante')

    # Agrupar las visitas por visitante
    visitantes_unicos = []
    visitantes_procesados = set()
    for visita in visitas:
        if visita.visitante not in visitantes_procesados:
            visitantes_unicos.append({
                'visitante': visita.visitante,
                'status': visita.status
            })
            visitantes_procesados.add(visita.visitante)

    # Agrupar las visitas únicas en listas de 10
    visitas_paginadas = [visitantes_unicos[i:i + 10] for i in range(0, len(visitantes_unicos), 10)]

    context = {
        'visitas_paginadas': visitas_paginadas,
    }

    return render(request, 'visitor_list.html', context)

@login_required
def visitor_create(request):
    """
    Crea un nuevo visitante o muestra el formulario para crear uno.
    """
    if request.method == 'POST':
        form = VisitaForm(request.POST)
        if form.is_valid():
            try:
                visitante = form.save(commit=False)
                tipo_documento = form.cleaned_data['tipo_documento']
                documento = form.cleaned_data['documento'].strip()
                
                # Asignar es_extranjero basado en el tipo de documento
                visitante.es_extranjero = (tipo_documento in ['E', 'P'])
                
                # Limpiar y formatear el documento
                if documento.startswith(('V-', 'E-', 'P-')):
                    documento = documento[2:]
                
                # Asignar prefijo según tipo de documento
                prefijos = {'V': 'V-', 'E': 'E-', 'P': 'P-'}
                visitante.documento = prefijos[tipo_documento] + documento
                
                # Debug: imprimir valores importantes
                print(f"Documento final: {visitante.documento}")
                print(f"Es extranjero: {visitante.es_extranjero}")
                print(f"País: {visitante.pais}")
                
                # Validación adicional para extranjeros
                if visitante.es_extranjero and not visitante.pais:
                    messages.error(request, 'Los visitantes extranjeros deben especificar su país.')
                    return render(request, 'visitor_form.html', {'form': form})
                
                # Verificar duplicados
                if Visitante.objects.filter(documento=visitante.documento).exists():
                    messages.error(request, 'Ya existe un visitante con este documento.')
                    return render(request, 'visitor_form.html', {'form': form})
                
                # Guardar el visitante
                visitante.save()
                
                # Crear la visita asociada
                fecha_visita = form.cleaned_data.get('fecha_visita', timezone.now().date())
                Visita.objects.create(
                    visitante=visitante,
                    fecha_visita=fecha_visita,
                    status='Pendiente'
                )
                
                messages.success(request, 'Visitante registrado con éxito!')
                return redirect('visitor_list')
                
            except IntegrityError as e:
                messages.error(request, f'Error al guardar: {str(e)}')
            except Exception as e:
                messages.error(request, f'Ocurrió un error inesperado: {str(e)}')
        else:
            # Debug: mostrar errores de validación
            print("Errores de formulario:", form.errors)
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = VisitaForm()
    
    return render(request, 'visitor_form.html', {'form': form})

@require_GET
def buscar_visitante(request):
    """
    Busca un visitante por número de documento y devuelve sus datos en formato JSON.
    """
    documento = request.GET.get('documento', '').strip()
    tipo_documento = request.GET.get('tipo_documento', '')
    es_extranjero = request.GET.get('es_extranjero', 'false') == 'true'

    # Elimina cualquier prefijo incorrecto del documento de búsqueda
    if documento.startswith('V-') or documento.startswith('E-') or documento.startswith('P-'):
        documento = documento[2:]

    # Agrega el prefijo correcto según el tipo de documento para la búsqueda
    if tipo_documento == 'V':
        documento_completo = 'V-' + documento
    elif tipo_documento == 'E':
        documento_completo = 'E-' + documento
    elif tipo_documento == 'P':
        documento_completo = 'E-P-' + documento
    else:
        documento_completo = documento  # Si no se proporciona tipo_documento, busca sin prefijo

    try:
        # Intenta buscar por el documento completo con prefijo
        visitante = Visitante.objects.get(documento=documento_completo)
        data = {
            'existe': True,
            'nombre': visitante.nombre,
            'apellido': visitante.apellido,
            'edad': visitante.edad,
            'sexo': visitante.sexo,
            'telefono': visitante.telefono,
            'correo': visitante.correo,
            'pais': visitante.pais,
            'empresa': visitante.empresa,
            'nombre_empresa': visitante.nombre_empresa,
            'rif_empresa': visitante.rif_empresa,
            'tipo_documento_real': tipo_documento, #Envía el tipo de documento original.
            'es_extranjero': es_extranjero, #Envia si es extranjero o no.
            'documento_completo': visitante.documento #Envía el documento completo.
        }
        return JsonResponse(data)
    except Visitante.DoesNotExist:
        # Si no se encuentra, intenta buscar por el documento sin prefijo
        try:
            visitante = Visitante.objects.get(documento=documento)
            data = {
                'existe': True,
                'nombre': visitante.nombre,
                'apellido': visitante.apellido,
                'edad': visitante.edad,
                'sexo': visitante.sexo,
                'telefono': visitante.telefono,
                'correo': visitante.correo,
                'pais': visitante.pais,
                'empresa': visitante.empresa,
                'nombre_empresa': visitante.nombre_empresa,
                'rif_empresa': visitante.rif_empresa,
                'tipo_documento_real': tipo_documento, #Envía el tipo de documento original.
                'es_extranjero': es_extranjero, #Envia si es extranjero o no.
                'documento_completo': visitante.documento #Envía el documento completo.
            }
            return JsonResponse(data)
        except Visitante.DoesNotExist:
            mensaje = 'Visitante no encontrado.'
            if tipo_documento == 'E':
                mensaje = 'No se encontró un visitante con ese número de cédula extranjera.'
            elif tipo_documento == 'P':
                mensaje = 'No se encontró un visitante con ese número de pasaporte.'
            return JsonResponse({
                'existe': False,
                'mensaje': mensaje
            })
        except Exception as e:
            logger.error(f"Error al buscar visitante: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:
        logger.error(f"Error al buscar visitante: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
def crear_visita(request):
    if request.method == 'POST':
        documento = request.POST.get('documento')
        tipo_documento = request.POST.get('tipo_documento')

        # Elimina cualquier prefijo incorrecto del documento
        if documento.startswith('V-') or documento.startswith('E-') or documento.startswith('P-'):
            documento = documento[2:]

        # Construye el documento completo con el prefijo correcto
        if tipo_documento == 'V':
            documento_completo = 'V-' + documento
        elif tipo_documento == 'E':
            documento_completo = 'E-' + documento
        elif tipo_documento == 'P':
            documento_completo = 'P-' + documento
        else:
            documento_completo = documento  # Si no se proporciona tipo_documento, busca sin prefijo

        try:
            visitante = Visitante.objects.get(documento=documento_completo)
            Visita.objects.create(visitante=visitante)
            messages.success(request, f"Visita creada para {visitante.nombre} {visitante.apellido} en la fecha actual.")
            return redirect('visitor_list')
        except Visitante.DoesNotExist:
            messages.error(request, "Visitante no encontrado.")
            return redirect('crear_visita')
    else:
        return render(request, 'crear_visita.html')