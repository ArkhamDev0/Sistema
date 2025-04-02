from django import forms
from django.utils import timezone
from .models import Visitante, Cita
import re

class VisitaForm(forms.ModelForm):
    """
    Formulario para gestionar el modelo 'Visitante' y crear citas.
    """
    TIPO_DOCUMENTO = [
        ('V', 'Cédula Venezolana'),
        ('E', 'Cédula Extranjera'),
        ('P', 'Pasaporte'),
    ]

    tipo_documento = forms.ChoiceField(
        choices=TIPO_DOCUMENTO,
        widget=forms.RadioSelect,
        initial='V'
    )

    fecha_visita = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date(),
        required=False
    )
    visita_hoy = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Visitante
        fields = ['nombre', 'apellido', 'documento', 'telefono', 'correo', 
                  'edad', 'sexo', 'pais', 'empresa', 'nombre_empresa', 'rif_empresa']
        widgets = {
            'empresa': forms.CheckboxInput(),
            'pais': forms.TextInput(attrs={'placeholder': 'Ej: Colombia'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        self.fields['nombre_empresa'].required = False
        self.fields['rif_empresa'].required = False
        self.fields['pais'].required = False
        self.fields['telefono'].required = False
        self.fields['correo'].required = False

        # Inicializar tipo_documento basado en el documento existente
        if self.instance and self.instance.pk:
            doc = self.instance.documento
            if doc.startswith('E-'):
                self.fields['tipo_documento'].initial = 'E'
            elif doc.startswith('P-'):
                self.fields['tipo_documento'].initial = 'P'
            else:
                self.fields['tipo_documento'].initial = 'V'

    def clean(self):
        cleaned_data = super().clean()
        documento = cleaned_data.get('documento', '').strip()
        tipo_documento = cleaned_data.get('tipo_documento')
        pais = cleaned_data.get('pais')
        empresa = cleaned_data.get('empresa', False)
        nombre_empresa = cleaned_data.get('nombre_empresa')
        rif_empresa = cleaned_data.get('rif_empresa')

        # Validación de empresa
        if empresa and (not nombre_empresa or not rif_empresa):
            if not nombre_empresa:
                self.add_error('nombre_empresa', 'Debe proporcionar el nombre de la empresa.')
            if not rif_empresa:
                self.add_error('rif_empresa', 'Debe proporcionar el RIF de la empresa.')

        # Validación de documento según tipo
        if tipo_documento == 'V':
            if not documento.isdigit():
                self.add_error('documento', 'La cédula venezolana debe contener solo números.')
        elif tipo_documento == 'E':
            if not documento.isdigit():
                self.add_error('documento', 'La cédula extranjera debe contener solo números.')
            if not pais:
                self.add_error('pais', 'Debe especificar el país para extranjeros.')
        elif tipo_documento == 'P':
            if not documento:
                self.add_error('documento', 'El pasaporte no puede estar vacío.')
            if not pais:
                self.add_error('pais', 'Debe especificar el país para extranjeros.')

        # Validación de edad
        edad = cleaned_data.get('edad')
        if edad and edad <= 0:
            self.add_error('edad', 'La edad debe ser mayor a 0.')

        return cleaned_data

    def save(self, commit=True):
        visitante = super().save(commit=False)
        tipo_documento = self.cleaned_data['tipo_documento']
        documento = self.cleaned_data['documento'].strip()
        
        # Aplicar prefijo al documento
        prefijos = {'V': 'V-', 'E': 'E-', 'P': 'P-'}
        visitante.documento = prefijos[tipo_documento] + documento
        
        # Asignar es_extranjero
        visitante.es_extranjero = (tipo_documento in ['E', 'P'])
        
        if commit:
            visitante.save()
        return visitante

class CitaForm(forms.Form):
    """
    Formulario para gestionar el modelo 'Cita'.
    Permite registrar citas asociadas a un visitante, validando
    la existencia de este en el sistema mediante su documento.
    """

    # Campo extra para buscar el documento del visitante
    documento = forms.CharField(label="Documento del Visitante", max_length=20)
    fecha = forms.DateField(label="Fecha de la cita")

    nombre = forms.CharField(label="Nombre del Visitante", max_length=100, required=False)
    apellido = forms.CharField(label="Apellido del Visitante", max_length=100, required=False)
    email = forms.EmailField(label="Correo electrónico", max_length=254, required=False)

    def clean_documento(self):
        """
        Valida que el documento del visitante exista en el sistema. Si no existe, lanza una excepción de validación.
        """
        documento = self.cleaned_data['documento']
        try:
            # Verificamos si existe el visitante
            visitante = Visitante.objects.get(documento=documento)
            # Si existe, llenamos los campos con su información
            self.cleaned_data['nombre'] = visitante.nombre
            self.cleaned_data['apellido'] = visitante.apellido
            self.cleaned_data['email'] = visitante.correo
        except Visitante.DoesNotExist:
            # Si no existe, limpiamos los campos
            self.cleaned_data['nombre'] = ''
            self.cleaned_data['apellido'] = ''
            self.cleaned_data['email'] = ''
            raise forms.ValidationError("¡Este visitante no existe! Regístralo primero.")
        return documento

    def save(self, user):
        """
        Guarda la cita en la base de datos. Asocia la cita al visitante correspondiente basado en el documento
        y registra al usuario que está creando la cita.
        """
        documento = self.cleaned_data['documento']
        fecha = self.cleaned_data['fecha']

        try:
            # Si el visitante existe, solo creamos la cita
            visitante = Visitante.objects.get(documento=documento)
            cita = Cita.objects.create(
                visitante=visitante,
                fecha=fecha,
                creado_por=user
            )
            return cita
        except Visitante.DoesNotExist:
            # Si el visitante no existe, lanzamos un error
            raise forms.ValidationError("¡Este visitante no existe! Regístralo primero.")