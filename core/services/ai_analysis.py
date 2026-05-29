"""
Servicio de análisis de radiografías con IA (Anthropic Claude con Fallback a Google Gemini).
Proporciona análisis automático de radiografías dentales y traducción de notas clínicas.
"""

import json
import base64
import logging
from core.services import (
    get_gemini_client,
    get_anthropic_client,
    GEMINI_PROMPTS,
    GEMINI_CONFIG,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GEMINI_API_KEY
)

logger = logging.getLogger(__name__)


class RadiographAnalysisService:
    """
    Servicio premium de análisis con IA para odontología.
    Implementa soporte para Anthropic Claude API como proveedor principal,
    con fallback automático a Google Gemini Flash si no hay API Key de Anthropic
    o si ocurre algún error durante la invocación.
    """
    
    @staticmethod
    def analyze_image(image_path_or_file):
        """
        Analiza una radiografía dental buscando caries, restauraciones, etc.
        
        Args:
            image_path_or_file: Ruta del archivo o FileObject
        
        Returns:
            dict: Análisis estructurado {
                'findings': str,
                'affected_teeth': [11, 12, 36, ...],
                'severity': 'Leve|Moderada|Severa',
                'recommendations': [str],
                'urgency': 'Electiva|Rutinaria|Urgente',
            }
        """
        # 1. Preparar la imagen en base64 y tipo MIME
        try:
            if isinstance(image_path_or_file, str):
                with open(image_path_or_file, 'rb') as f:
                    image_data = base64.standard_b64encode(f.read()).decode()
                mime_type = 'image/jpeg'
            else:
                image_bytes = image_path_or_file.read()
                image_data = base64.standard_b64encode(image_bytes).decode()
                mime_type = getattr(image_path_or_file, 'content_type', 'image/jpeg') or 'image/jpeg'
        except Exception as e:
            logger.error(f"Error procesando la imagen de radiografía: {str(e)}")
            return {
                'error': f"Error al procesar archivo: {str(e)}",
                'findings': 'No se pudo leer la imagen de radiografía.',
                'affected_teeth': [],
                'severity': 'Desconocida',
                'recommendations': ['Verificar formato de imagen', 'Revisión manual necesaria'],
                'urgency': 'Urgente',
            }

        prompt = (
            f"{GEMINI_PROMPTS['radiograph_analysis']}\n\n"
            "IMPORTANTE: Tu respuesta debe ser exclusivamente un objeto JSON válido y legible. "
            "No incluyas explicaciones previas ni posteriores, ni bloques de código markdown como ```json."
        )

        # 2. Intentar con Anthropic Claude (Proveedor Premium Principal)
        if ANTHROPIC_API_KEY:
            try:
                logger.info(f"Iniciando análisis de radiografía con Anthropic Claude ({ANTHROPIC_MODEL})...")
                client = get_anthropic_client()
                
                # Crear el mensaje con imagen usando la API de Anthropic
                response = client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=1024,
                    temperature=0.3,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": mime_type if mime_type in ["image/jpeg", "image/png", "image/gif", "image/webp"] else "image/jpeg",
                                        "data": image_data,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": prompt,
                                }
                            ],
                        }
                    ],
                )
                
                # Extraer texto de la respuesta
                response_text = response.content[0].text
                analysis = RadiographAnalysisService._parse_json_response(response_text)
                logger.info("Análisis de radiografía completado con Anthropic Claude.")
                return analysis
                
            except Exception as anth_err:
                logger.warning(f"Fallo en Anthropic Claude: {str(anth_err)}. Ejecutando fallback a Gemini...")
        else:
            logger.info("Anthropic API Key no configurada. Saltando a Gemini...")

        # 3. Fallback a Google Gemini
        if GEMINI_API_KEY:
            try:
                logger.info("Iniciando análisis de radiografía con Google Gemini...")
                genai = get_gemini_client()
                model = genai.GenerativeModel(GEMINI_CONFIG['model'])
                
                contents = [
                    {
                        "role": "user",
                        "parts": [
                            {"inline_data": {"mime_type": mime_type, "data": image_data}},
                            {"text": prompt}
                        ]
                    }
                ]
                
                response = model.generate_content(contents)
                analysis = RadiographAnalysisService._parse_json_response(response.text)
                logger.info("Análisis de radiografía completado con Google Gemini.")
                return analysis
                
            except Exception as gem_err:
                logger.error(f"Fallo en Google Gemini: {str(gem_err)}.")
        else:
            logger.warning("Gemini API Key no configurada.")

        # 4. Degradación graciosa (Fallback estático si ambos fallan)
        logger.error("No se pudo analizar la radiografía con ningún motor de IA. Retornando respuesta estática segura.")
        return {
            'error': 'Motores de IA no disponibles o credenciales faltantes',
            'findings': 'Se requiere inspección manual de la radiografía debido a que los servicios de análisis automático por IA se encuentran fuera de servicio.',
            'affected_teeth': [],
            'severity': 'Moderada',
            'recommendations': ['Realizar diagnóstico clínico visual', 'Validar API Keys de Anthropic/Gemini en el servidor'],
            'urgency': 'Rutinaria',
        }
    
    @staticmethod
    def translate_clinical_notes(notes_text):
        """
        Traduce notas clínicas técnicas complejas a un lenguaje comprensible para el paciente.
        
        Args:
            notes_text: Texto de la nota clínica
            
        Returns:
            str: Explicación en lenguaje sencillo
        """
        if not notes_text or not notes_text.strip():
            return "No se proporcionaron notas clínicas para traducir."

        prompt = f"{GEMINI_PROMPTS['clinical_notes_translator']}\n\nNotas clínicas técnicas:\n{notes_text}"

        # 1. Intentar con Anthropic Claude
        if ANTHROPIC_API_KEY:
            try:
                logger.info("Traduciendo notas clínicas con Anthropic Claude...")
                client = get_anthropic_client()
                response = client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=1024,
                    temperature=0.3,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )
                logger.info("Traducción completada con Anthropic Claude.")
                return response.content[0].text
            except Exception as anth_err:
                logger.warning(f"Fallo en Anthropic al traducir notas: {str(anth_err)}. Ejecutando fallback a Gemini...")
        
        # 2. Fallback a Google Gemini
        if GEMINI_API_KEY:
            try:
                logger.info("Traduciendo notas clínicas con Google Gemini...")
                genai = get_gemini_client()
                model = genai.GenerativeModel(GEMINI_CONFIG['model'])
                response = model.generate_content(prompt)
                logger.info("Traducción completada con Google Gemini.")
                return response.text
            except Exception as gem_err:
                logger.error(f"Fallo en Gemini al traducir notas: {str(gem_err)}")
        
        # 3. Fallback en caso de desconexión / sin credenciales
        return f"Nota Clínica (Revisión Clínica):\n{notes_text}\n\n[Nota: No se pudo generar la explicación en lenguaje claro debido a que los servicios de IA de traducción no están disponibles]."

    @staticmethod
    def _parse_json_response(response_text):
        """Lógica robusta de parsing de JSON de respuestas de IA."""
        try:
            # Eliminar posibles bloques de markdown ```json o ``` si la IA los puso
            text = response_text.strip()
            if text.startswith("```"):
                # Quitar primera línea de triple comilla
                lines = text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                text = "\n".join(lines).strip()
            
            # Buscar el inicio y fin del objeto JSON real
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No se encontró estructura de objeto {} en la respuesta.")
                
        except (json.JSONDecodeError, ValueError) as err:
            logger.error(f"Error parseando JSON de respuesta IA: {str(err)}. Contenido crudo: {response_text}")
            return {
                'findings': response_text,
                'affected_teeth': [],
                'severity': 'Moderada',
                'recommendations': ['Consultar especialista para revisión de la radiografía'],
                'urgency': 'Rutinaria',
                'parse_error': True
            }
