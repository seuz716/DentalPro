"""
Vistas de la aplicación core.
"""

from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Vista de índice principal."""
    template_name = 'core/index.html'
