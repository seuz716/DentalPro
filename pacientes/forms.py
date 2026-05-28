"""
Formularios para la aplicación pacientes.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Patient


class PatientForm(forms.ModelForm):
    """
    Formulario explícito para Patient.
    Ejecuta validaciones del modelo (clean()) antes de guardar.
    Asegura que cédulas inválidas, fechas fuera de rango y datos
    malformados sean rechazados en la interfaz.
    """
    
    # Campo adicional para notas clínicas con placeholder
    clinical_notes = forms.CharField(
        label='Notas Clínicas',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ej: Paciente refiere dolor en molar superior derecho. Sin síntomas sistémicos.'
        })
    )
    
    class Meta:
        model = Patient
        fields = [
            'document_type',
            'document_number',
            'first_name',
            'last_name',
            'birth_date',
            'gender',
            'phone',
            'email',
            'address',
            'blood_type',
            'allergies',
            'chronic_conditions',
            'clinical_notes',
        ]
        
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'document_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
                'placeholder': 'Ej: 1234567890'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'phone': forms.TextInput(attrs={
                'type': 'tel',
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
                'placeholder': '+57 300 123 4567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500',
                'placeholder': 'correo@ejemplo.com'
            }),
            'address': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none'
            }),
            'blood_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500'
            }),
            'allergies': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none',
                'placeholder': 'Ej: Penicilina, látex'
            }),
            'chronic_conditions': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none',
                'placeholder': 'Ej: Diabetes tipo 2, hipertensión'
            }),
            'clinical_notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none'
            }),
        }

    def clean(self):
        """
        Ejecuta las validaciones del modelo Patient antes de guardar.
        Captura errores de ValidationError y los remapea al formulario.
        """
        cleaned_data = super().clean()
        
        try:
            # Triggerea Patient.clean() que valida:
            # - Cédula colombiana (si CC)
            # - Rango de fecha de nacimiento (1900-2099)
            # - Formato de notas clínicas (JSON o texto)
            self.instance.full_clean()
        except ValidationError as e:
            # Remapear errores del modelo al formulario
            if hasattr(e, 'message_dict'):
                for field, messages in e.message_dict.items():
                    self.add_error(field, messages)
            else:
                # Error genérico sin asignación a campo específico
                self.add_error(None, e.message)
        
        return cleaned_data
