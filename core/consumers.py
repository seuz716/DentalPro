"""
Consumidores de WebSockets de Django Channels para la aplicación core.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class HeartbeatConsumer(AsyncWebsocketConsumer):
    """
    Consumidor básico para monitoreo y pruebas de latido/heartbeat de conexión.
    """
    
    async def connect(self):
        """Maneja el establecimiento de la conexión."""
        await self.accept()
        logger.info("WebSocket: Conexión de latido establecida exitosamente.")
        
        # Enviar mensaje de bienvenida inicial
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "status": "connected",
            "message": "Conexión WebSocket establecida con éxito. Enviando latido..."
        }))

    async def disconnect(self, close_code):
        """Maneja la desconexión del cliente."""
        logger.info(f"WebSocket: Conexión de latido cerrada con código: {close_code}")

    async def receive(self, text_data):
        """Maneja la recepción de datos del cliente."""
        try:
            data = json.loads(text_data)
            event_type = data.get("type")
            
            if event_type == "ping":
                # Responder a la petición ping con pong
                await self.send(text_data=json.dumps({
                    "type": "pong",
                    "status": "alive",
                    "message": "Servidor respondiendo en tiempo real."
                }))
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": f"Tipo de evento no soportado: {event_type}"
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Formato de mensaje JSON inválido."
            }))
        except Exception as e:
            logger.error(f"Error procesando mensaje WebSocket: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"Error interno del servidor WebSocket: {str(e)}"
            }))
