"""
Servicio de análisis de radiografías con Google Gemini Flash 2.5.
Proporciona análisis automático de radiografías dentales.
"""

import json
import base64
from pathlib import Path
from django.core.files.storage import default_storage
from core.services.gemini_config import get_gemini_client, GEMINI_PROMPTS, GEMINI_CONFIG


class RadiographAnalysisService:
    """
    Servicio para analizar radiografías dentales con Gemini.
    """
    
    @staticmethod
    def analyze_image(image_path_or_file):
        """
        Analiza una radiografía dental.
        
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
        try:
            genai = get_gemini_client()
            
            # Convertir imagen a base64
            if isinstance(image_path_or_file, str):
                with open(image_path_or_file, 'rb') as f:
                    image_data = base64.standard_b64encode(f.read()).decode()
                mime_type = 'image/jpeg'
            else:
                image_bytes = image_path_or_file.read()
                image_data = base64.standard_b64encode(image_bytes).decode()
                mime_type = image_path_or_file.content_type or 'image/jpeg'
            
            # Crear contenido con imagen
            model = genai.GenerativeModel(GEMINI_CONFIG['model'])
            
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": mime_type, "data": image_data}},
                        {"text": GEMINI_PROMPTS['radiograph_analysis']}
                    ]
                }
            ]
            
            # Generar análisis
            response = model.generate_content(contents)
            
            # Parsear respuesta JSON
            analysis_text = response.text
            
            # Extraer JSON de la respuesta
            try:
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                # Si no está en JSON, retornar en estructura estándar
                analysis = {
                    'findings': analysis_text,
                    'affected_teeth': [],
                    'severity': 'Moderada',
                    'recommendations': ['Consultar con especialista'],
                    'urgency': 'Rutinaria',
                }
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'findings': 'Error al analizar radiografía',
                'affected_teeth': [],
                'severity': 'Desconocida',
                'recommendations': ['Revisión manual necesaria'],
                'urgency': 'Urgente',
            }
    
    @staticmethod
    def translate_clinical_notes(notes_text):
        """
        Traduce notas clínicas técnicas a lenguaje claro para pacientes.
        
        Args:
            notes_text: Notas técnicas
        
        Returns:
            str: Notas traducidas
        """
        try:
            genai = get_gemini_client()
            model = genai.GenerativeModel(GEMINI_CONFIG['model'])
            
            prompt = f"{GEMINI_PROMPTS['clinical_notes_translator']}\n\nNotas: {notes_text}"
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error traduciendo notas: {str(e)}"


class BiometricAuthService:
    """
    Servicio para autenticación biométrica (WebAuthn/FIDO2).
    """
    
    @staticmethod
    def generate_challenge():
        """
        Genera un challenge para autenticación biométrica.
        """
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_credential(credential_data, stored_credential):
        """
        Verifica credencial biométrica (implementación básica).
        En producción, usar librería `webauthn` completa.
        """
        # Comparar credenciales
        return credential_data.get('id') == stored_credential.get('id')
