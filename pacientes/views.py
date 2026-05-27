"""
Vistas de la aplicación pacientes.
Implementa listado, búsqueda y detalles de pacientes con HTMX.
"""

from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Patient


class PatientListView(ListView):
    """
    Vista para listar pacientes con paginación.
    Muestra 15 pacientes por página.
    """
    model = Patient
    paginate_by = 15
    template_name = 'pacientes/patient_list.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        """
        Retorna pacientes ordenados por fecha de creación descendente.
        """
        return Patient.objects.all().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """
        Añade contexto adicional para búsqueda.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PatientSearchView(ListView):
    """
    Vista para buscar pacientes por nombre, cédula o teléfono.
    Retorna solo el partial HTML para actualizar con HTMX.
    """
    model = Patient
    paginate_by = 15
    template_name = 'pacientes/partials/_patient_list_results.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        """
        Filtra pacientes por búsqueda de texto en múltiples campos.
        """
        queryset = Patient.objects.all()
        query = self.request.GET.get('q', '')
        
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(document_number__icontains=query) |
                Q(phone__icontains=query) |
                Q(email__icontains=query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """
        Añade la búsqueda al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PatientDetailView(DetailView):
    """
    Vista para ver detalles completos de un paciente.
    Incluye tabs para datos personales, historia clínica y odontograma.
    """
    model = Patient
    template_name = 'pacientes/patient_detail.html'
    context_object_name = 'patient'
    
    def get_context_data(self, **kwargs):
        """
        Añade contexto para tabs (datos personales, HC, odontograma).
        """
        context = super().get_context_data(**kwargs)
        
        # Tab activo (por defecto: personal)
        context['active_tab'] = self.request.GET.get('tab', 'personal')
        
        # Datos para cada tab
        context['tabs'] = {
            'personal': 'Datos Personales',
            'clinical': 'Historia Clínica',
            'odontogram': 'Odontograma',
        }
        
        return context
