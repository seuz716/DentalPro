"""
URL Configuration para la aplicación core.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    
    # URLs de autenticación tradicional
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # URLs de autenticación WebAuthn/FIDO2
    path('api/webauthn/register/start/', views.WebAuthnRegisterStartView.as_view(), name='webauthn_register_start'),
    path('api/webauthn/register/complete/', views.WebAuthnRegisterCompleteView.as_view(), name='webauthn_register_complete'),
    path('api/webauthn/authenticate/start/', views.WebAuthnAuthenticateStartView.as_view(), name='webauthn_authenticate_start'),
    path('api/webauthn/authenticate/complete/', views.WebAuthnAuthenticateCompleteView.as_view(), name='webauthn_authenticate_complete'),
]
