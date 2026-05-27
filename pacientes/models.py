"""
Modelos de la aplicación pacientes.
Se implementarán completamente en Fase 1.
"""

from django.db import models


class Patient(models.Model):
    """
    Modelo de Paciente.
    Campos completos se implementarán en Fase 1.
    """
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['-id']
    
    def __str__(self):
        """Representación en string del paciente."""
        return f"Paciente {self.pk}"
