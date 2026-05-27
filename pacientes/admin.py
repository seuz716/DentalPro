"""
Administración de la aplicación pacientes.
"""

from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """
    Administrador personalizado para el modelo Patient.
    Incluye campos de búsqueda, filtros y campos de solo lectura.
    """
    
    list_display = (
        'full_name',
        'document_number',
        'document_type',
        'phone',
        'age',
        'gender',
        'created_at',
    )
    
    search_fields = (
        'first_name',
        'last_name',
        'document_number',
        'email',
        'phone',
    )
    
    list_filter = (
        'gender',
        'document_type',
        'blood_type',
        'created_at',
        'updated_at',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'age',
    )
    
    fieldsets = (
        ('Identificación', {
            'fields': (
                'document_type',
                'document_number',
            )
        }),
        ('Información Personal', {
            'fields': (
                'first_name',
                'last_name',
                'birth_date',
                'gender',
                'age',
            )
        }),
        ('Contacto', {
            'fields': (
                'phone',
                'email',
                'address',
            )
        }),
        ('Información Clínica', {
            'fields': (
                'blood_type',
                'allergies',
                'chronic_conditions',
                'clinical_notes',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
