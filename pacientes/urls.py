"""
URL Configuration para la aplicación pacientes.
"""

from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.PatientListView.as_view(), name='list'),
    path('buscar/', views.PatientSearchView.as_view(), name='search'),
    path('<int:pk>/', views.PatientDetailView.as_view(), name='detail'),
]
