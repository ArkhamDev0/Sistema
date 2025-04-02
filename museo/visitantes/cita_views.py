from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cita, Visitante
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q

# Función para agregar una cita
@login_required
def agregar_cita(request):
    if request.method == 'POST':
        tipo_cedula = request.POST.get('tipo_cedula')
        cedula = request.POST.get('cedula')
        fecha = request.POST.get('fecha')

        # Verifica si todos los campos requeridos están presentes
        if not tipo_cedula or not cedula or not fecha:
            messages.error(request, "Por favor ingrese todos los campos requeridos.")
            return redirect('agregar_cita')

        fecha_actual = datetime.now().date()
        fecha_solicitada = datetime.strptime(fecha, '%Y-%m-%d').date()

        # Verifica si la fecha de la cita es anterior a la fecha actual
        if fecha_solicitada < fecha_actual:
            messages.error(request, "La fecha de la cita no puede ser anterior a la fecha actual.")
            return redirect('agregar_cita')

        # Formatea la cédula según el tipo
        documento = f"{tipo_cedula}-{cedula}"

        try:
            # Intenta obtener el visitante por documento
            visitante = Visitante.objects.get(documento=documento)

            # Obtiene la hora actual del equipo
            hora_actual = datetime.now().time()

            # Crea la cita
            cita = Cita.objects.create(
                visitante=visitante,
                fecha=fecha,
                hora=hora_actual,  # Usa la hora actual del equipo
                creado_por=request.user
            )

            messages.success(request, f"Cita agendada para {visitante.nombre} {visitante.apellido} el {fecha}.")
            return redirect('agregar_cita')

        except Visitante.DoesNotExist:
            # Maneja el caso en que el visitante no existe
            messages.error(request, "Visitante no registrado. Por favor, registre al visitante antes de agendar la cita.")
            return redirect('agregar_cita')

    else:
        # Renderiza el formulario para agregar cita
        today = datetime.now().date()
        return render(request, 'agendar_cita.html', {'today': today})

# Función para listar todas las citas y filtrarlas por fecha
@login_required
def listar_citas(request):
    citas = Cita.objects.all()
    fecha_filtro = request.GET.get('fecha_filtro')

    # Filtra las citas por fecha si se proporciona una fecha de filtro
    if fecha_filtro:
        citas = citas.filter(fecha=fecha_filtro)

    # Formatea la hora en formato de 12 horas (AM/PM) con minutos
    citas_formateadas = []
    for cita in citas:
        hora = cita.hora.hour
        minuto = cita.hora.minute
        if hora == 0:
            hora_formateada = f"12:{minuto:02} AM"
        elif hora < 12:
            hora_formateada = f"{hora}:{minuto:02} AM"
        elif hora == 12:
            hora_formateada = f"12:{minuto:02} PM"
        else:
            hora_formateada = f"{hora - 12}:{minuto:02} PM"
        citas_formateadas.append({
            'visitante': cita.visitante,
            'fecha': cita.fecha,
            'hora': hora_formateada,
            'pk': cita.pk,  # Agrega la clave primaria para la URL 'reagendar_cita'
        })

    context = {'citas': citas_formateadas, 'fecha_filtro': fecha_filtro}
    return render(request, 'listar_citas.html', context)

# Función para reagendar una cita
@login_required
def reagendar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)

    if request.method == 'POST':
        nueva_fecha = request.POST.get('nueva_fecha')
        fecha_actual = datetime.now().date()
        fecha_solicitada = datetime.strptime(nueva_fecha, '%Y-%m-%d').date()

        # Verifica si la nueva fecha es anterior a la fecha actual
        if fecha_solicitada < fecha_actual:
            messages.error(request, "La nueva fecha de la cita no puede ser anterior a la fecha actual.")
            return redirect('reagendar_cita', pk=pk)

        # Actualiza la fecha de la cita
        cita.fecha = nueva_fecha
        cita.save()
        messages.success(request, f"Cita reagendada para el {nueva_fecha}.")
        return redirect('listar_citas')

    context = {'cita': cita}
    return render(request, 'reagendar_cita.html', context)