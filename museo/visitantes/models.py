import datetime
import re
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

# ================================
# Funciones de Validación
# ================================

def validar_solo_letras(value):
    """Valida que el campo contenga solo letras y espacios."""
    if not value.replace(" ", "").isalpha():
        raise ValidationError("Este campo solo debe contener letras.")

def validar_documento(value):
    """Valida que el documento tenga un formato válido."""
    if not re.match(r'^(V|E|P)?-?[\w-]+$', value, re.IGNORECASE):
        raise ValidationError("El documento debe ser alfanumérico y comenzar con V, E, o P, o ser alfanumérico.")

def validar_telefono(value):
    """Valida números de teléfono venezolanos y extranjeros."""
    patrones_venezuela = r'^(0412|0414|0424|0416|0426|0212)-\d{7}$'
    patrones_extranjero = r'^\+\d{1,3}-\d{4,14}$'

    if value and not (re.match(patrones_venezuela, value) or re.match(patrones_extranjero, value)):
        raise ValidationError("El número debe ser venezolano (0412-1234567) o extranjero (+1-5551234567).")

def validar_correo(value):
    """Valida que el correo contenga el carácter '@' solo si se ingresa un valor."""
    if value and '@' not in value:
        raise ValidationError("El correo debe contener '@'.")

def validar_rif(value):
    """Valida el formato del RIF (ej: J-12345678-9 o V123456789)"""
    if not re.match(r'^[A-Za-z]?-?\d{7,9}-?\d?$', value):
        raise ValidationError("Formato de RIF inválido. Ejemplos válidos: J-12345678-9 o V123456789")

# ================================
# Modelo TipoDocumento
# ================================

class TipoDocumento(models.Model):
    """Modelo para los tipos de documento."""
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

# ================================
# Modelo Sexo
# ================================

class Sexo(models.Model):
    """Modelo para las opciones de sexo."""
    descripcion = models.CharField(max_length=20)

    def __str__(self):
        return self.descripcion

# ================================
# Modelo Pais
# ================================

class Pais(models.Model):
    """Modelo para los países."""
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# ================================
# Modelo Empresa (Actualizado)
# ================================

class Empresa(models.Model):
    """Modelo para las empresas relacionadas con Visitantes."""
    visitante = models.OneToOneField(
        'Visitante',
        on_delete=models.CASCADE,
        related_name='empresa_relacionada',
        null=True,
        blank=True,
        help_text="Visitante asociado a esta empresa"
    )
    nombre = models.CharField(max_length=100)
    rif = models.CharField(
        max_length=20, 
        unique=True, 
        validators=[validar_rif],
        help_text="RIF de la empresa (solo números)"
    )

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (RIF: {self.rif})"

    def clean(self):
        """Valida que el RIF sea único."""
        if Empresa.objects.exclude(pk=self.pk).filter(rif=self.rif).exists():
            raise ValidationError({'rif': 'Este RIF ya está registrado en otra empresa'})

# ================================
# Modelo StatusVisita
# ================================

class StatusVisita(models.Model):
    """Modelo para los estados de visita."""
    descripcion = models.CharField(max_length=20)

    def __str__(self):
        return self.descripcion

# ================================
# Modelo StatusCita
# ================================

class StatusCita(models.Model):
    """Modelo para los estados de cita."""
    descripcion = models.CharField(max_length=20)

    def __str__(self):
        return self.descripcion

# ================================
# Modelo Documento
# ================================

class Documento(models.Model):
    """Modelo para los documentos de los visitantes."""
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    valor = models.CharField(max_length=20, unique=True, validators=[validar_documento])

    def __str__(self):
        return f"{self.tipo_documento.descripcion}: {self.valor}"

# ================================
# Modelo Visitante (Actualizado)
# ================================

class Visitante(models.Model):
    """
    Modelo que representa a un visitante único.
    Contiene la información personal del visitante.
    """

    SEXO_OPCIONES = [
        (1, 'Masculino'),
        (2, 'Femenino'),
        (3, 'Otro'),
        (4, 'Prefiero no decirlo')
    ]

    nombre = models.CharField(max_length=100, validators=[validar_solo_letras])
    apellido = models.CharField(max_length=100, validators=[validar_solo_letras])
    documento = models.CharField(max_length=20, unique=True, validators=[validar_documento])
    telefono = models.CharField(max_length=20, blank=True, null=True, validators=[validar_telefono])
    correo = models.EmailField(unique=True, max_length=254, blank=True, null=True)
    edad = models.IntegerField()
    sexo = models.IntegerField(choices=SEXO_OPCIONES)
    pais = models.CharField(max_length=100, blank=True, null=True)
    empresa = models.BooleanField(default=False)
    nombre_empresa = models.CharField(max_length=100, blank=True, null=True)
    rif_empresa = models.CharField(max_length=20, blank=True, null=True, validators=[validar_rif])
    es_extranjero = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Visitante'
        verbose_name_plural = 'Visitantes'
        ordering = ['apellido', 'nombre']

    def clean(self):
        """
        Valida que:
        - Los datos de empresa sean completos si empresa=True
        - El país sea obligatorio para extranjeros
        """
        if self.empresa:
            if not self.nombre_empresa:
                raise ValidationError({'nombre_empresa': "Debe proporcionar el nombre de la empresa."})
            if not self.rif_empresa:
                raise ValidationError({'rif_empresa': "Debe proporcionar el RIF de la empresa."})

        if self.es_extranjero and not self.pais:
            raise ValidationError({'pais': "Debe proporcionar el país si es extranjero."})

    def save(self, *args, **kwargs):
        """
        1. Procesa el formato del documento según nacionalidad
        2. Sincroniza con el modelo Empresa si corresponde
        """
        # Lógica existente para documentos
        if self.es_extranjero:
            if self.documento.startswith('V') or self.documento.startswith('P'):
                if not self.documento.startswith('E-'):
                    self.documento = "E-" + self.documento
        else:
            if self.documento.startswith('E-'):
                self.documento = self.documento[2:]

        # Sincronización con Empresa
        if self.empresa and self.nombre_empresa and self.rif_empresa:
            Empresa.objects.update_or_create(
                rif=self.rif_empresa,
                defaults={
                    'nombre': self.nombre_empresa,
                    'visitante': self
                }
            )
        elif hasattr(self, 'empresa_relacionada'):
            # Si ya no es empresa pero tenía registro anterior
            self.empresa_relacionada.delete()

        super().save(*args, **kwargs)

    def __str__(self):
        """Representación legible del visitante."""
        return f"{self.nombre} {self.apellido}"

# ================================
# Modelo Visita
# ================================

class Visita(models.Model):
    """
    Modelo que representa una visita individual.
    Contiene información sobre la visita y una relación con el visitante.
    """
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE)
    fecha_visita = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=20, default='Pendiente')

    class Meta:
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'
        ordering = ['-fecha_visita']

    def __str__(self):
        return f"Visita de {self.visitante} el {self.fecha_visita}"

# ================================
# Modelo Cita
# ================================

class Cita(models.Model):
    """
    Modelo que representa una cita enlace con un visitante.
    Incluye información sobre la fecha, hora y quién agendó la cita.
    """
    visitante = models.ForeignKey(Visitante, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Agendado')

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"Cita de {self.visitante} el {self.fecha} a las {self.hora}"

# ================================
# Modelo VisitaHora
# ================================

class VisitaHora(models.Model):
    """Modelo para las horas de visita."""
    visita = models.ForeignKey(Visita, on_delete=models.CASCADE)
    hora_visita = models.TimeField()

    class Meta:
        verbose_name = 'Hora de Visita'
        verbose_name_plural = 'Horas de Visita'
        ordering = ['hora_visita']

    def __str__(self):
        return f"Hora de visita: {self.hora_visita}"