"""
Configuración de enrutamiento WebSocket para DentalPro.
"""

from django.urls import re_path
from core.consumers import HeartbeatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/heartbeat/$', HeartbeatConsumer.as_asgi()),
]
