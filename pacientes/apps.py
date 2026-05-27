"""
Configuración de la aplicación 'pacientes'.
"""

from django.apps import AppConfig


class PacientesConfig(AppConfig):
    """Configuración de la aplicación pacientes."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pacientes'
    verbose_name = 'Pacientes'
