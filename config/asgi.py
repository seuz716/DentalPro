"""
Configuración ASGI para el proyecto DentalPro.
Expone la aplicación ASGI como una variable a nivel de módulo llamada 'application'.
Soporta tanto HTTP como WebSockets.
"""

import os
from django.core.asgi import get_asgi_application

# Establecer variable de entorno y cargar aplicación ASGI base de Django
# Esto debe ejecutarse antes de importar cualquier consumer o archivo de enrutamiento
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import config.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            config.routing.websocket_urlpatterns
        )
    ),
})
