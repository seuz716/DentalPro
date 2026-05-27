"""
Vistas de la aplicación pacientes.
Se implementarán en la Fase 3.
"""

from django.views.generic import ListView, DetailView
from .models import Patient


class PatientListView(ListView):
    """
    Vista para listar pacientes con paginación.
    Se implementará en Fase 3.
    """
    model = Patient
    paginate_by = 15


class PatientSearchView(ListView):
    """
    Vista para buscar pacientes.
    Se implementará en Fase 3.
    """
    model = Patient
    paginate_by = 15


class PatientDetailView(DetailView):
    """
    Vista para ver detalles de un paciente.
    Se implementará en Fase 3.
    """
    model = Patient
