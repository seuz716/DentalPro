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


class OdontogramConsumer(AsyncWebsocketConsumer):
    """
    Consumidor para la colaboración en tiempo real del Odontograma.
    Broadcastea cambios de estado de dientes a todos los doctores
    conectados al mismo paciente.
    """
    
    async def connect(self):
        self.patient_id = self.scope['url_route']['kwargs']['patient_id']
        self.group_name = f"patient_{self.patient_id}"
        
        # Unirse al grupo del paciente
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket: Doctor unido al grupo colaborativo: {self.group_name}")

    async def disconnect(self, close_code):
        # Abandonar el grupo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket: Doctor abandonó el grupo: {self.group_name}")

    async def receive(self, text_data):
        """Recibe la actualización de estado del diente de un doctor."""
        try:
            data = json.loads(text_data)
            event_type = data.get("type")
            
            if event_type == "tooth_update":
                fdi = data.get("fdi")
                status = data.get("status")
                notes = data.get("notes", "")
                
                # Re-transmitir el cambio a todos los doctores en el grupo
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "broadcast_tooth_update",
                        "fdi": fdi,
                        "status": status,
                        "notes": notes,
                        "sender_channel_name": self.channel_name
                    }
                )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Mensaje WebSocket JSON inválido."
            }))
        except Exception as e:
            logger.error(f"Error en receive de OdontogramConsumer: {str(e)}")

    async def broadcast_tooth_update(self, event):
        """Envía el cambio de diente broadcastado a este WebSocket cliente."""
        # Evitar enviar la actualización de vuelta al mismo cliente emisor
        if self.channel_name != event.get("sender_channel_name"):
            await self.send(text_data=json.dumps({
                "type": "tooth_update",
                "fdi": event["fdi"],
                "status": event["status"],
                "notes": event["notes"]
            }))

