from django.contrib import admin
from .models import Visitante, Visita, Cita, TipoDocumento, Sexo, Pais, Empresa, StatusVisita, StatusCita, Documento, VisitaHora

class VisitaHoraInline(admin.TabularInline):
    model = VisitaHora
    extra = 1

class VisitaAdmin(admin.ModelAdmin):
    list_display = ('visitante', 'fecha_visita', 'get_horas_visita', 'status')
    inlines = [VisitaHoraInline]

    def get_horas_visita(self, obj):
        return ", ".join([vh.hora_visita.strftime("%H:%M") for vh in obj.visitahora_set.all()])

    get_horas_visita.short_description = "Horas de Visita"

admin.site.register(Visitante)
admin.site.register(Visita, VisitaAdmin)
admin.site.register(Cita)
admin.site.register(TipoDocumento)
admin.site.register(Sexo)
admin.site.register(Pais)
admin.site.register(Empresa)
admin.site.register(StatusVisita)
admin.site.register(StatusCita)
admin.site.register(Documento)
admin.site.register(VisitaHora)