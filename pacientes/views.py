"""
Vistas de la aplicación pacientes.
Implementa listado, búsqueda y detalles de pacientes con HTMX.
"""

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import IntegrityError
from .models import Patient


class PatientListView(LoginRequiredMixin, ListView):
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


class PatientSearchView(LoginRequiredMixin, ListView):
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
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(document_number__icontains=query)
                | Q(phone__icontains=query)
                | Q(email__icontains=query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Añade la búsqueda al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PatientDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para ver detalles completos de un paciente.
    Incluye tabs para datos personales, historia clínica y odontograma.

    Comportamiento HTMX:
        - Petición normal:   devuelve patient_detail.html (página completa).
        - Petición HTMX:     devuelve solo el partial del tab solicitado
                             (detectado por la cabecera HX-Request).
                             Esto evita que la página completa se inserte
                             dentro de #tab-content.
    """
    model = Patient
    template_name = 'pacientes/patient_detail.html'
    context_object_name = 'patient'

    # Mapa de tab → partial template
    TAB_TEMPLATES = {
        'personal':   'pacientes/partials/_tab_personal.html',
        'clinical':   'pacientes/partials/_tab_clinical.html',
        'odontogram': 'pacientes/partials/_tab_odontogram.html',
    }

    def render_to_response(self, context, **response_kwargs):
        """
        Si la petición viene de HTMX (HX-Request header), devuelve el
        partial correspondiente al tab activo en lugar de la página completa.
        """
        if self.request.headers.get('HX-Request'):
            tab = self.request.GET.get('tab', 'personal')
            template = self.TAB_TEMPLATES.get(tab, self.TAB_TEMPLATES['personal'])
            return render(self.request, template, context)

        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        """
        Añade contexto para tabs (datos personales, HC, odontograma).
        """
        context = super().get_context_data(**kwargs)

        # Tab activo (por defecto: personal)
        context['active_tab'] = self.request.GET.get('tab', 'personal')

        # Nombres de tabs para el template
        context['tabs'] = {
            'personal':   'Datos Personales',
            'clinical':   'Historia Clínica',
            'odontogram': 'Odontograma',
        }

        # Estado de dientes (JSON para el odontograma SVG).
        # En producción, cargarlo desde un modelo ToothRecord relacionado:
        #   tooth_records = patient.tooth_records.all()
        #   context['tooth_status_json'] = json.dumps({r.fdi: r.status for r in tooth_records})
        context['tooth_status_json'] = '{}'

        if context['active_tab'] == 'odontogram':
            # Generar datos de los 32 dientes FDI para el loop del template
            teeth = []
            # Cuadrante 1 (18 a 11) - Superior Derecho (pantalla izquierda)
            for i in range(18, 10, -1):
                teeth.append({'id': i, 'x': 392 - (i-11)*50, 'y': 90})
            # Cuadrante 2 (21 a 28) - Superior Izquierdo (pantalla derecha)
            for i in range(21, 29):
                teeth.append({'id': i, 'x': 442 + (i-21)*50, 'y': 90})
            # Cuadrante 4 (48 a 41) - Inferior Derecho (pantalla izquierda)
            for i in range(48, 40, -1):
                teeth.append({'id': i, 'x': 392 - (i-41)*50, 'y': 200})
            # Cuadrante 3 (31 a 38) - Inferior Izquierdo (pantalla derecha)
            for i in range(31, 39):
                teeth.append({'id': i, 'x': 442 + (i-31)*50, 'y': 200})
                
            context['odontogram_teeth'] = teeth
            
        return context

class PatientCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo paciente.
    Implementa manejo de IntegrityError para race conditions.
    """
    model = Patient
    fields = ['document_type', 'document_number', 'first_name', 'last_name', 'birth_date', 'gender', 'phone', 'email', 'address']
    template_name = 'pacientes/patient_form.html'
    success_url = reverse_lazy('pacientes:list')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Paciente creado exitosamente.")
            return response
        except IntegrityError:
            form.add_error('document_number', 'Error de concurrencia: El número de documento ya fue registrado recientemente.')
            return self.form_invalid(form)

class PatientUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para actualizar un paciente existente.
    Implementa manejo de IntegrityError para race conditions.
    """
    model = Patient
    fields = ['document_type', 'document_number', 'first_name', 'last_name', 'birth_date', 'gender', 'phone', 'email', 'address']
    template_name = 'pacientes/patient_form.html'
    
    def get_success_url(self):
        return reverse_lazy('pacientes:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Paciente actualizado exitosamente.")
            return response
        except IntegrityError:
            form.add_error('document_number', 'Error de concurrencia: El número de documento choca con un registro existente.')
            return self.form_invalid(form)
