"""
URL Configuration para la aplicación pacientes.
"""

from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.PatientListView.as_view(), name='list'),
    path('buscar/', views.PatientSearchView.as_view(), name='search'),
    path('nuevo/', views.PatientCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PatientDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.PatientUpdateView.as_view(), name='update'),
    path('<int:pk>/diente/<int:fdi>/estado/', views.ToothRecordUpdateView.as_view(), name='tooth_status'),
]
