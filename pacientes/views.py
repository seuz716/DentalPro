"""
Vistas de la aplicación pacientes.
Implementa listado, búsqueda y detalles de pacientes con HTMX.
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views import View"
from django.views import View
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
import json
import base64

from .models import Patient, ToothRecord
from .forms import PatientForm
from core.services.pdf_generator import PatientReportGenerator


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

        # Estado de dientes (JSON para el odontograma)
        tooth_records = self.object.tooth_records.all()
        context['tooth_status_json'] = json.dumps({r.fdi: r.status for r in tooth_records})

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
    Usa PatientForm que ejecuta validaciones del modelo (clean()).
    Maneja IntegrityError para duplicados de document_number.
    """
    model = Patient
    form_class = PatientForm  # ← AHORA USA FORM EXPLÍCITO
    template_name = 'pacientes/patient_form.html'
    success_url = reverse_lazy('pacientes:list')
    def form_valid(self, form):
        """
        Si el formulario es válido, guarda el paciente y muestra mensaje.
        """
        try:
            response = super().form_valid(form)
            messages.success(
                self.request, 
                f"✓ Paciente {self.object.full_name} creado exitosamente."
            )
            return response
        except IntegrityError:
            # Captura duplicados de document_number a nivel de BD
            form.add_error(
                'document_number', 
                'Este número de documento ya existe en el sistema. '
                'Verifica el número de cédula.'
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Si el formulario es inválido (validaciones fallaron),
        se redisplaya con los errores destacados.
        """
        messages.error(
            self.request,
            'Por favor, corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para actualizar un paciente existente.
    Usa PatientForm que ejecuta validaciones del modelo (clean()).
    """
    model = Patient
    form_class = PatientForm  # ← AHORA USA FORM EXPLÍCITO
    template_name = 'pacientes/patient_form.html'
    
    def get_success_url(self):
        return reverse_lazy('pacientes:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """
        Si el formulario es válido, guarda cambios y muestra mensaje.
        """
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                f"✓ Paciente {self.object.full_name} actualizado exitosamente."
            )
            return response
        except IntegrityError:
            # Captura si otro paciente usa el mismo documento_number
            form.add_error(
                'document_number',
                'Este número de documento está siendo usado por otro paciente. '
                'Elige un número diferente.'
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Si el formulario es inválido, se redisplaya con los errores.
        """
        messages.error(
            self.request,
            'Por favor, corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class ToothRecordUpdateView(LoginRequiredMixin, View):
    """
    Vista para actualizar el estado clínico de un diente individual.
    Retorna un JSON estructurado para el odontograma 3D y 2D.
    """
    def post(self, request, pk, fdi):
        try:
            patient = Patient.objects.get(pk=pk)
            
            # Soportar tanto payload JSON (Three.js) como x-www-form-urlencoded (HTMX)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                status = data.get('status', 'S')
                notes = data.get('notes', '')
            else:
                status = request.POST.get('status', 'S')
                notes = request.POST.get('notes', '')

            # Validar que el estado sea correcto
            valid_statuses = [c[0] for c in ToothRecord.STATUS_CHOICES]
            if status not in valid_statuses:
                return JsonResponse({'success': False, 'error': 'Estado de diente inválido.'}, status=400)

            # Actualizar o crear el registro
            record, created = ToothRecord.objects.update_or_create(
                patient=patient,
                fdi=fdi,
                defaults={'status': status, 'notes': notes}
            )

            return JsonResponse({
                'success': True,
                'fdi': fdi,
                'status': record.status,
                'status_display': record.get_status_display(),
                'notes': record.notes
            })
            
        except Patient.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Paciente no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class PatientReportPDFView(LoginRequiredMixin, View):
    """
    Vista para generar y descargar el reporte PDF de un paciente.
    Acepta un parámetro opcional `canvas_image` (base64) para el odontograma.
    """
    def get(self, request, pk, *args, **kwargs):
        patient = get_object_or_404(Patient, pk=pk)
        canvas_image = request.GET.get('canvas_image', None)

        pdf_generator = PatientReportGenerator(patient, canvas_image=canvas_image)
        pdf_buffer = pdf_generator.generate()

        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_generator.get_filename()}"'
        return response
