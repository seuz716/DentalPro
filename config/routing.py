"""
Configuración de enrutamiento WebSocket para DentalPro.
"""

from django.urls import re_path
from core.consumers import HeartbeatConsumer, OdontogramConsumer

websocket_urlpatterns = [
    re_path(r'^ws/heartbeat/$', HeartbeatConsumer.as_asgi()),
    re_path(r'^ws/odontogram/(?P<patient_id>\d+)/$', OdontogramConsumer.as_asgi()),
]
